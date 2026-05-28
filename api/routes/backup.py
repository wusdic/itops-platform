"""
备份恢复管理 API 路由
P1-12 系统备份恢复
提供备份配置CRUD、备份执行、历史查询、恢复操作等接口
"""

import logging
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from pydantic import field_validator

from modules.business.backup_manager import (
    BackupManager,
    BackupConfig,
    BackupRecord,
    BackupType,
    BackupTarget,
    BackupStatus,
    RestoreStatus,
    RestoreRecord,
    get_backup_manager,
    init_backup_manager,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["备份恢复"])


# ============== 内存存储的备份配置列表 ==============

_backup_configs: dict[str, dict] = {}


# ============== 请求/响应模型 ==============

class BackupConfigCreate(BaseModel):
    """创建备份配置"""
    name: str = Field(..., description="配置名称")
    backup_type: str = Field(..., description="备份类型: full/incremental/differential")
    targets: List[str] = Field(default_factory=lambda: ["all"], description="备份目标: database/config/files/all")
    retention_days: int = Field(30, description="保留天数")
    max_backups: int = Field(10, description="最大备份数量")
    compression_enabled: bool = Field(True, description="是否启用压缩")
    compression_level: int = Field(9, ge=0, le=9, description="压缩级别 0-9")
    backup_dir: Optional[str] = Field(None, description="备份存储路径")
    db_backup_tables: List[str] = Field(default_factory=list, description="数据库备份表，空表示全部")
    file_backup_paths: List[str] = Field(default_factory=list, description="文件备份路径列表")
    file_exclude_patterns: List[str] = Field(
        default_factory=lambda: ["*.pyc", "__pycache__", ".git", "*.log"],
        description="文件排除模式"
    )
    auto_backup_enabled: bool = Field(True, description="是否启用自动备份")
    backup_schedule: str = Field("0 2 * * *", description="备份调度表达式")
    notify_on_success: bool = Field(True, description="成功时通知")
    notify_on_failure: bool = Field(True, description="失败时通知")

    @field_validator('backup_type')
    @classmethod
    def validate_backup_type(cls, v):
        valid_types = ['full', 'incremental', 'differential']
        if v not in valid_types:
            raise ValueError(f"backup_type must be one of {valid_types}")
        return v

    @field_validator('targets')
    @classmethod
    def validate_targets(cls, v):
        valid_targets = ['database', 'config', 'files', 'all']
        for target in v:
            if target not in valid_targets:
                raise ValueError(f"target must be one of {valid_targets}")
        return v


class BackupConfigUpdate(BaseModel):
    """更新备份配置"""
    name: Optional[str] = None
    backup_type: Optional[str] = None
    targets: Optional[List[str]] = None
    retention_days: Optional[int] = None
    max_backups: Optional[int] = None
    compression_enabled: Optional[bool] = None
    compression_level: Optional[int] = Field(None, ge=0, le=9)
    backup_dir: Optional[str] = None
    db_backup_tables: Optional[List[str]] = None
    file_backup_paths: Optional[List[str]] = None
    file_exclude_patterns: Optional[List[str]] = None
    auto_backup_enabled: Optional[bool] = None
    backup_schedule: Optional[str] = None
    notify_on_success: Optional[bool] = None
    notify_on_failure: Optional[bool] = None

    @field_validator('backup_type')
    @classmethod
    def validate_backup_type(cls, v):
        if v is None:
            return v
        valid_types = ['full', 'incremental', 'differential']
        if v not in valid_types:
            raise ValueError(f"backup_type must be one of {valid_types}")
        return v


class BackupConfigResponse(BaseModel):
    """备份配置响应"""
    id: str
    name: str
    backup_type: str
    targets: List[str]
    retention_days: int
    max_backups: int
    compression_enabled: bool
    compression_level: int
    backup_dir: str
    db_backup_tables: List[str]
    file_backup_paths: List[str]
    file_exclude_patterns: List[str]
    auto_backup_enabled: bool
    backup_schedule: str
    notify_on_success: bool
    notify_on_failure: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class BackupExecuteRequest(BaseModel):
    """执行备份请求"""
    name: str = Field(..., description="备份名称")
    backup_type: str = Field("full", description="备份类型: full/incremental/differential")
    targets: List[str] = Field(default_factory=lambda: ["all"], description="备份目标")
    description: str = Field("", description="备份描述")

    @field_validator('backup_type')
    @classmethod
    def validate_backup_type(cls, v):
        valid_types = ['full', 'incremental', 'differential']
        if v not in valid_types:
            raise ValueError(f"backup_type must be one of {valid_types}")
        return v


class BackupHistoryQuery(BaseModel):
    """备份历史查询参数"""
    status: Optional[str] = Field(None, description="备份状态: pending/running/success/failed/cancelled")
    backup_type: Optional[str] = Field(None, description="备份类型")
    limit: int = Field(100, ge=1, le=1000, description="返回数量")
    offset: int = Field(0, ge=0, description="偏移量")


class RestoreRequest(BaseModel):
    """恢复请求"""
    target: str = Field("all", description="恢复目标: database/config/files/all")
    target_path: Optional[str] = Field(None, description="恢复路径")
    create_pre_backup: bool = Field(True, description="恢复前是否创建备份")


class BackupStatusResponse(BaseModel):
    """备份状态响应"""
    running_backups: int = 0
    pending_backups: int = 0
    last_backup_id: Optional[str] = None
    last_backup_status: Optional[str] = None
    last_backup_time: Optional[str] = None


# ============== 辅助函数 ==============

def _backup_config_to_response(config_id: str, config: dict) -> BackupConfigResponse:
    """将备份配置字典转换为响应模型"""
    return BackupConfigResponse(
        id=config_id,
        name=config['name'],
        backup_type=config['backup_type'],
        targets=config['targets'],
        retention_days=config['retention_days'],
        max_backups=config['max_backups'],
        compression_enabled=config['compression_enabled'],
        compression_level=config['compression_level'],
        backup_dir=config['backup_dir'],
        db_backup_tables=config['db_backup_tables'],
        file_backup_paths=config['file_backup_paths'],
        file_exclude_patterns=config['file_exclude_patterns'],
        auto_backup_enabled=config['auto_backup_enabled'],
        backup_schedule=config['backup_schedule'],
        notify_on_success=config['notify_on_success'],
        notify_on_failure=config['notify_on_failure'],
        created_at=config.get('created_at'),
        updated_at=config.get('updated_at'),
    )


def _backup_record_to_response(record: BackupRecord) -> dict:
    """将备份记录转换为响应字典"""
    return record.to_dict()


def _restore_record_to_response(record: RestoreRecord) -> dict:
    """将恢复记录转换为响应字典"""
    return record.to_dict()


# ============== 路由接口 ==============

@router.get("/configs")
async def get_backup_configs():
    """
    获取备份配置列表
    
    Returns:
        备份配置列表
    """
    configs = []
    for config_id, config in _backup_configs.items():
        configs.append(_backup_config_to_response(config_id, config))
    return {"code": 0, "message": "success", "data": configs}


@router.post("/configs")
async def create_backup_config(config: BackupConfigCreate):
    """
    创建备份配置
    
    Args:
        config: 备份配置信息
    
    Returns:
        创建的备份配置
    """
    import uuid
    
    config_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    config_dict = {
        "name": config.name,
        "backup_type": config.backup_type,
        "targets": config.targets,
        "retention_days": config.retention_days,
        "max_backups": config.max_backups,
        "compression_enabled": config.compression_enabled,
        "compression_level": config.compression_level,
        "backup_dir": config.backup_dir or "/data/backup",
        "db_backup_tables": config.db_backup_tables,
        "file_backup_paths": config.file_backup_paths,
        "file_exclude_patterns": config.file_exclude_patterns,
        "auto_backup_enabled": config.auto_backup_enabled,
        "backup_schedule": config.backup_schedule,
        "notify_on_success": config.notify_on_success,
        "notify_on_failure": config.notify_on_failure,
        "created_at": now,
        "updated_at": now,
    }
    
    _backup_configs[config_id] = config_dict
    
    return {"code": 0, "message": "success", "data": _backup_config_to_response(config_id, config_dict)}


@router.get("/configs/{config_id}")
async def get_backup_config(config_id: str):
    """
    获取单个备份配置
    
    Args:
        config_id: 配置ID
    
    Returns:
        备份配置详情
    """
    config = _backup_configs.get(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return {"code": 0, "message": "success", "data": _backup_config_to_response(config_id, config)}


@router.put("/configs/{config_id}")
async def update_backup_config(config_id: str, config: BackupConfigUpdate):
    """
    更新备份配置
    
    Args:
        config_id: 配置ID
        config: 更新后的配置信息
    
    Returns:
        更新后的备份配置
    """
    existing = _backup_configs.get(config_id)
    if not existing:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    update_data = config.model_dump(exclude_unset=True)
    
    # 验证 backup_type
    if 'backup_type' in update_data and update_data['backup_type'] is not None:
        valid_types = ['full', 'incremental', 'differential']
        if update_data['backup_type'] not in valid_types:
            raise HTTPException(status_code=400, detail=f"backup_type must be one of {valid_types}")
    
    # 验证 targets
    if 'targets' in update_data and update_data['targets'] is not None:
        valid_targets = ['database', 'config', 'files', 'all']
        for target in update_data['targets']:
            if target not in valid_targets:
                raise HTTPException(status_code=400, detail=f"target must be one of {valid_targets}")
    
    # 更新字段
    for key, value in update_data.items():
        if value is not None:
            existing[key] = value
    
    existing['updated_at'] = datetime.now().isoformat()
    
    return {"code": 0, "message": "success", "data": _backup_config_to_response(config_id, existing)}


@router.delete("/configs/{config_id}")
async def delete_backup_config(config_id: str):
    """
    删除备份配置
    
    Args:
        config_id: 配置ID
    
    Returns:
        删除结果
    """
    if config_id not in _backup_configs:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    del _backup_configs[config_id]
    
    return {"code": 0, "message": "success", "data": {"deleted": True}}


@router.post("/execute")
async def execute_backup(request: BackupExecuteRequest, background_tasks: BackgroundTasks):
    """
    执行备份
    
    Args:
        request: 备份执行参数
        background_tasks: 后台任务
    
    Returns:
        备份记录
    """
    manager = get_backup_manager()
    
    # 转换类型
    backup_type = BackupType(request.backup_type)
    targets = [BackupTarget(t) for t in request.targets]
    
    # 创建备份
    record = await manager.create_backup(
        name=request.name,
        backup_type=backup_type,
        targets=targets,
        description=request.description,
    )
    
    return {"code": 0, "message": "success", "data": _backup_record_to_response(record)}


@router.get("/history")
async def get_backup_history(
    status: Optional[str] = Query(None, description="备份状态"),
    backup_type: Optional[str] = Query(None, description="备份类型"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
):
    """
    获取备份历史
    
    Args:
        status: 备份状态过滤
        backup_type: 备份类型过滤
        limit: 返回数量
        offset: 偏移量
    
    Returns:
        备份历史列表
    """
    manager = get_backup_manager()
    
    # 转换过滤参数
    status_filter = BackupStatus(status) if status else None
    type_filter = BackupType(backup_type) if backup_type else None
    
    # 获取备份列表
    backups = manager.list_backups(
        status=status_filter,
        backup_type=type_filter,
        limit=limit + offset,
    )
    
    # 应用分页
    total = len(backups)
    backups = backups[offset:offset + limit]
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": [_backup_record_to_response(b) for b in backups],
            "total": total,
            "offset": offset,
            "limit": limit,
        }
    }


@router.get("/history/{backup_id}")
async def get_backup_detail(backup_id: str):
    """
    获取单个备份详情
    
    Args:
        backup_id: 备份ID
    
    Returns:
        备份详情
    """
    manager = get_backup_manager()
    
    record = manager.get_backup(backup_id)
    if not record:
        raise HTTPException(status_code=404, detail="备份不存在")
    
    return {"code": 0, "message": "success", "data": _backup_record_to_response(record)}


@router.post("/restore/{backup_id}")
async def restore_backup(backup_id: str, request: RestoreRequest):
    """
    执行恢复
    
    Args:
        backup_id: 备份ID
        request: 恢复参数
    
    Returns:
        恢复记录
    """
    manager = get_backup_manager()
    
    # 检查备份是否存在
    backup = manager.get_backup(backup_id)
    if not backup:
        raise HTTPException(status_code=404, detail="备份不存在")
    
    # 执行恢复
    target = BackupTarget(request.target)
    record = await manager.restore(
        backup_id=backup_id,
        target=target,
        target_path=request.target_path,
        create_pre_backup=request.create_pre_backup,
    )
    
    return {"code": 0, "message": "success", "data": _restore_record_to_response(record)}


@router.get("/status")
async def get_backup_status():
    """
    获取备份任务状态
    
    Returns:
        备份状态信息
    """
    manager = get_backup_manager()
    
    backups = manager.list_backups(limit=1000)
    
    running = [b for b in backups if b.status == BackupStatus.RUNNING]
    pending = [b for b in backups if b.status == BackupStatus.PENDING]
    
    # 找到最近一次备份
    last_backup = backups[0] if backups else None
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "running_backups": len(running),
            "pending_backups": len(pending),
            "last_backup_id": last_backup.id if last_backup else None,
            "last_backup_status": last_backup.status.value if last_backup else None,
            "last_backup_time": last_backup.started_at.isoformat() if last_backup else None,
        }
    }


@router.delete("/history/{backup_id}")
async def delete_backup(backup_id: str):
    """
    删除备份
    
    Args:
        backup_id: 备份ID
    
    Returns:
        删除结果
    """
    manager = get_backup_manager()
    
    success = manager.delete_backup(backup_id)
    if not success:
        raise HTTPException(status_code=404, detail="备份不存在")
    
    return {"code": 0, "message": "success", "data": {"deleted": True}}


@router.post("/cleanup")
async def cleanup_old_backups():
    """
    清理过期备份
    
    Returns:
        清理结果
    """
    manager = get_backup_manager()
    
    count = manager.cleanup_old_backups()
    
    return {"code": 0, "message": "success", "data": {"cleaned_count": count}}


@router.get("/restores")
async def get_restore_history(
    limit: int = Query(100, ge=1, le=1000, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
):
    """
    获取恢复历史
    
    Args:
        limit: 返回数量
        offset: 偏移量
    
    Returns:
        恢复历史列表
    """
    manager = get_backup_manager()
    
    restores = manager.list_restores(limit=limit + offset)
    
    # 应用分页
    total = len(restores)
    restores = restores[offset:offset + limit]
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": [_restore_record_to_response(r) for r in restores],
            "total": total,
            "offset": offset,
            "limit": limit,
        }
    }


@router.get("/restores/{restore_id}")
async def get_restore_detail(restore_id: str):
    """
    获取恢复详情
    
    Args:
        restore_id: 恢复ID
    
    Returns:
        恢复详情
    """
    manager = get_backup_manager()
    
    record = manager.get_restore(restore_id)
    if not record:
        raise HTTPException(status_code=404, detail="恢复记录不存在")
    
    return {"code": 0, "message": "success", "data": _restore_record_to_response(record)}
