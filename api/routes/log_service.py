"""
日志配置与归集服务
管理日志配置、写入日志记录、归集分组
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from api.dependencies import get_db, get_current_user, CurrentUser

logger = logging.getLogger("logs")

router = APIRouter(tags=["日志服务"])

# 日志分类定义：category -> sub_category -> (enabled, min_level, description)
DEFAULT_LOG_CONFIG = {
    "operation": {
        "login": {"enabled": True, "min_level": "INFO", "description": "登录/登出"},
        "device_crud": {"enabled": True, "min_level": "INFO", "description": "设备增删改查"},
        "alert_action": {"enabled": True, "min_level": "INFO", "description": "告警状态变更"},
        "workorder_crud": {"enabled": True, "min_level": "INFO", "description": "工单增删改"},
        "adapter_credential": {"enabled": False, "min_level": "INFO", "description": "适配器/凭证变更"},
    },
    "system": {
        "error": {"enabled": True, "min_level": "ERROR", "description": "ERROR 及以上"},
        "warning": {"enabled": True, "min_level": "WARNING", "description": "WARNING 及以上"},
        "info": {"enabled": False, "min_level": "INFO", "description": "INFO 记录（量大）"},
        "debug": {"enabled": False, "min_level": "DEBUG", "description": "DEBUG 记录（最大量）"},
    },
    "collection": {
        "success": {"enabled": False, "min_level": "INFO", "description": "采集成功（量大）"},
        "failed": {"enabled": True, "min_level": "ERROR", "description": "采集失败"},
        "offline": {"enabled": True, "min_level": "WARNING", "description": "设备离线"},
    },
    "audit": {
        "all": {"enabled": True, "min_level": "INFO", "description": "全部告警操作"},
    },
}

LEVEL_PRIORITY = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}


def _should_record(config: dict, level: str) -> bool:
    """判断某级别的日志是否应该记录"""
    if not config.get("enabled", 0):
        return False
    config_level = config.get("min_level", "INFO")
    return LEVEL_PRIORITY.get(level, 0) >= LEVEL_PRIORITY.get(config_level, 1)


def _get_sub_category(action: str, resource: str, category: str) -> str:
    """根据操作推断子分类"""
    if category == "operation":
        if action in ("login", "logout"):
            return "login"
        if action in ("create", "update", "delete") and resource:
            if resource in ("device", "devices"):
                return "device_crud"
            if resource in ("workorder", "workorders"):
                return "workorder_crud"
            if resource in ("alert", "alerts"):
                return "alert_action"
            if resource in ("adapter", "credential", "credentials", "adapters"):
                return "adapter_credential"
        return "login"  # 默认归为 login
    if category == "system":
        return "error"  # 系统日志按 ERROR 级别归入 error
    if category == "collection":
        return action  # action 就是 success/failed/offline
    return "all"


class LogConfigService:
    """日志配置服务"""

    @staticmethod
    def init_defaults(db: Session):
        """初始化默认配置（仅插入未存在的记录）"""
        from modules.foundation.db_models.system import LogConfig

        existing = db.query(LogConfig).first()
        if existing:
            return  # 已有配置，跳过

        for category, subs in DEFAULT_LOG_CONFIG.items():
            for sub, cfg in subs.items():
                db.add(LogConfig(
                    category=category,
                    sub_category=sub,
                    enabled=1 if cfg["enabled"] else 0,
                    min_level=cfg["min_level"],
                    description=cfg["description"],
                    retention_days=7,
                    aggregation_enabled=1,
                ))
        db.commit()
        logger.info("日志配置已初始化")

    @staticmethod
    def get_all(db: Session) -> list:
        from modules.foundation.db_models.system import LogConfig

        configs = db.query(LogConfig).order_by(LogConfig.category, LogConfig.id).all()
        return [
            {
                "id": c.id,
                "category": c.category,
                "sub_category": c.sub_category,
                "enabled": bool(c.enabled),
                "min_level": c.min_level,
                "aggregation_enabled": bool(c.aggregation_enabled),
                "retention_days": c.retention_days,
                "description": c.description,
            }
            for c in configs
        ]

    @staticmethod
    def update_all(db: Session, configs: list) -> list:
        from modules.foundation.db_models.system import LogConfig

        results = []
        for cfg in configs:
            row = db.query(LogConfig).filter(
                LogConfig.category == cfg["category"],
                LogConfig.sub_category == cfg["sub_category"],
            ).first()
            if row:
                if "enabled" in cfg:
                    row.enabled = 1 if cfg["enabled"] else 0
                if "min_level" in cfg:
                    row.min_level = cfg["min_level"]
                if "retention_days" in cfg:
                    row.retention_days = cfg["retention_days"]
                if "aggregation_enabled" in cfg:
                    row.aggregation_enabled = 1 if cfg["aggregation_enabled"] else 0
                results.append({"category": row.category, "sub_category": "updated"})
        db.commit()
        return results

    @staticmethod
    def is_enabled(db: Session, category: str, sub_category: str, level: str = "INFO") -> bool:
        from modules.foundation.db_models.system import LogConfig

        cfg = db.query(LogConfig).filter(
            LogConfig.category == category,
            LogConfig.sub_category == sub_category,
        ).first()
        if not cfg:
            # 无配置时默认开启
            return True
        return _should_record({
            "enabled": cfg.enabled,
            "min_level": cfg.min_level,
        }, level)


class LogAggregationService:
    """日志归集服务"""

    @staticmethod
    def _make_group_key(category: str, dimensions: dict) -> str:
        """生成归集键"""
        key_data = json.dumps(dimensions, sort_keys=True, ensure_ascii=True)
        return hashlib.md5(key_data.encode()).hexdigest()

    @staticmethod
    def _get_or_create_group(db: Session, category: str, dimensions: dict,
                              now: datetime) -> tuple:
        from modules.foundation.db_models.system import LogGroup

        group_key = LogAggregationService._make_group_key(category, dimensions)
        group = db.query(LogGroup).filter(
            LogGroup.category == category,
            LogGroup.group_key == group_key,
        ).first()

        if group:
            return group, False

        group = LogGroup(
            category=category,
            group_key=group_key,
            dimension_summary=json.dumps(dimensions, ensure_ascii=True),
            first_seen=now,
            last_seen=now,
            total_count=0,
            level_distribution=json.dumps({}),
        )
        db.add(group)
        db.flush()
        return group, True

    @staticmethod
    def write_operation_log(db: Session, record: dict, config: dict):
        """写入操作日志（归集模式）"""
        from modules.foundation.db_models.system import LogGroup, LogItem

        sub_cat = _get_sub_category(
            record.get("action", ""),
            record.get("resource", ""),
            "operation"
        )

        if not _should_record(config.get(sub_cat, {}), record.get("level", "INFO")):
            return

        now = datetime.now()
        # 归集维度：action + resource + 10分钟时间桶
        bucket = now.replace(minute=now.minute // 10 * 10, second=0, microsecond=0)
        dimensions = {
            "action": record.get("action", ""),
            "resource": record.get("resource", ""),
            "username": record.get("username", ""),
            "ip": record.get("ip_address", ""),
            "bucket": bucket.isoformat(),
        }
        group, is_new = LogAggregationService._get_or_create_group(db, "operation", dimensions, now)

        # 更新组统计
        group.total_count += 1
        group.last_seen = now
        if is_new:
            group.sample_log = record.get("path", "")

        # 写入明细
        item = LogItem(
            group_id=group.id,
            category="operation",
            raw_content=json.dumps(record, ensure_ascii=True),
            level=record.get("level", "INFO"),
            message=f"{record.get('username', '')} {record.get('action', '')} {record.get('resource', '')}",
            detail=json.dumps({
                "method": record.get("method"),
                "path": record.get("path"),
                "resource_id": record.get("resource_id"),
                "status": record.get("response_status"),
            }, ensure_ascii=True),
            duration_ms=record.get("duration_ms"),
            username=record.get("username"),
            ip_address=record.get("ip_address"),
            resource_type=record.get("resource"),
            resource_id=record.get("resource_id"),
            created_at=now,
        )
        db.add(item)

    @staticmethod
    def write_system_log(db: Session, level: str, source: str, message: str, raw: str):
        """写入系统日志（归集模式）"""
        from modules.foundation.db_models.system import LogGroup, LogItem

        sub_cat = "error" if level in ("ERROR", "CRITICAL") else "warning" if level == "WARNING" else "info"
        cfg = {"enabled": 1, "min_level": "WARNING"}  # 从 DB 读

        # 简化：系统日志总是归集（按 level + source + 5分钟桶）
        now = datetime.now()
        bucket = now.replace(minute=now.minute // 5 * 5, second=0, microsecond=0)
        dimensions = {
            "level": level,
            "source": source,
            "bucket": bucket.isoformat(),
        }
        group, is_new = LogAggregationService._get_or_create_group(db, "system", dimensions, now)

        group.total_count += 1
        group.last_seen = now
        if is_new:
            group.sample_log = message[:200]

        # 更新 level 分布
        dist = json.loads(group.level_distribution or "{}")
        dist[level] = dist.get(level, 0) + 1
        group.level_distribution = json.dumps(dist)

        item = LogItem(
            group_id=group.id,
            category="system",
            raw_content=raw,
            level=level,
            source=source,
            message=message,
            created_at=now,
        )
        db.add(item)

    @staticmethod
    def write_collection_log(db: Session, status: str, device_name: str, device_ip: str,
                              message: str, duration_ms: int, config: dict):
        """写入采集日志（归集模式）"""
        from modules.foundation.db_models.system import LogGroup, LogItem

        if not _should_record(config.get(status, {}), "ERROR" if status == "failed" else "INFO"):
            return

        now = datetime.now()
        bucket = now.replace(second=0, microsecond=0)
        dimensions = {
            "status": status,
            "device_name": device_name,
            "device_ip": device_ip,
            "bucket": bucket.isoformat(),
        }
        group, is_new = LogAggregationService._get_or_create_group(db, "collection", dimensions, now)

        group.total_count += 1
        group.last_seen = now
        if is_new:
            group.sample_log = message[:200]

        dist = json.loads(group.level_distribution or "{}")
        dist[status] = dist.get(status, 0) + 1
        group.level_distribution = json.dumps(dist)

        item = LogItem(
            group_id=group.id,
            category="collection",
            raw_content=message,
            level="ERROR" if status == "failed" else "INFO",
            source="collector",
            message=message,
            duration_ms=duration_ms,
            resource_type="device",
            resource_id=device_ip,
            created_at=now,
        )
        db.add(item)

    @staticmethod
    def get_groups(db: Session, category: str, keyword: str = None,
                   start_date: datetime = None, end_date: datetime = None,
                   page: int = 1, page_size: int = 20) -> tuple:
        from modules.foundation.db_models.system import LogGroup

        query = db.query(LogGroup).filter(LogGroup.category == category)

        if start_date:
            query = query.filter(LogGroup.last_seen >= start_date)
        if end_date:
            query = query.filter(LogGroup.last_seen <= end_date)

        total = query.count()
        groups = query.order_by(LogGroup.last_seen.desc()) \
            .offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for g in groups:
            dim = json.loads(g.dimension_summary or "{}")
            # 隐藏 bucket 字段（太细节）
            dim.pop("bucket", None)
            items.append({
                "id": g.id,
                "category": g.category,
                "group_key": g.group_key,
                "dimension": dim,
                "first_seen": g.first_seen.isoformat() if g.first_seen else None,
                "last_seen": g.last_seen.isoformat() if g.last_seen else None,
                "total_count": g.total_count,
                "level_distribution": json.loads(g.level_distribution or "{}"),
                "sample_log": g.sample_log,
            })

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    def get_group_items(db: Session, group_id: int, page: int = 1, page_size: int = 50) -> dict:
        from modules.foundation.db_models.system import LogItem

        query = db.query(LogItem).filter(LogItem.group_id == group_id)
        total = query.count()
        items_db = query.order_by(LogItem.created_at.desc()) \
            .offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for it in items_db:
            items.append({
                "id": it.id,
                "group_id": it.group_id,
                "category": it.category,
                "level": it.level,
                "source": it.source,
                "message": it.message,
                "detail": json.loads(it.detail) if it.detail else None,
                "duration_ms": it.duration_ms,
                "username": it.username,
                "ip_address": it.ip_address,
                "resource_type": it.resource_type,
                "resource_id": it.resource_id,
                "raw_content": it.raw_content,
                "created_at": it.created_at.isoformat() if it.created_at else None,
            })
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    def cleanup_old_logs(db: Session):
        """清理过期日志（按 retention_days）"""
        from modules.foundation.db_models.system import LogConfig, LogGroup, LogItem

        configs = db.query(LogConfig).all()
        for cfg in configs:
            cutoff = datetime.now() - timedelta(days=cfg.retention_days)
            # 删除归集组（级联删除明细）
            groups = db.query(LogGroup).filter(
                LogGroup.category == cfg.category,
                LogGroup.last_seen < cutoff,
            ).all()
            group_ids = [g.id for g in groups]
            if group_ids:
                db.query(LogItem).filter(LogItem.group_id.in_(group_ids)).delete(synchronize_session=False)
                db.query(LogGroup).filter(LogGroup.id.in_(group_ids)).delete(synchronize_session=False)
        db.commit()
        logger.info("日志清理完成")

    @staticmethod
    def get_stats(db: Session) -> dict:
        """获取各分类实时统计"""
        from modules.foundation.db_models.system import LogGroup, LogItem

        stats = {}
        for cat in ("operation", "system", "collection", "audit"):
            total_items = db.query(func.sum(LogGroup.total_count)).filter(
                LogGroup.category == cat
            ).scalar() or 0
            total_groups = db.query(LogGroup.id).filter(
                LogGroup.category == cat
            ).count()
            stats[cat] = {
                "total_items": int(total_items),
                "total_groups": total_groups,
            }
        return stats


# ============== API Routes ==============

from app.common.response import success_response, error_response, paginated_response
from app.common.error_codes import ErrorCode
from pydantic import BaseModel, Field
from typing import List, Optional


class LogConfigUpdateItem(BaseModel):
    """日志配置项更新"""
    category: str
    sub_category: str
    enabled: Optional[bool] = None
    min_level: Optional[str] = None
    retention_days: Optional[int] = None
    aggregation_enabled: Optional[bool] = None


class LogConfigUpdateRequest(BaseModel):
    """批量更新日志配置请求"""
    configs: List[LogConfigUpdateItem]


class LogIndexConfig(BaseModel):
    """日志接入配置"""
    id: Optional[int] = None
    name: str
    index_pattern: str  # like: nginx-access-*
    log_type: str  # nginx, system, application, custom
    enabled: bool = True
    retention_days: int = 7
    description: Optional[str] = None


class LogIndexCreateRequest(BaseModel):
    """创建日志接入配置请求"""
    name: str = Field(..., description="配置名称")
    index_pattern: str = Field(..., description="索引模式，如 nginx-access-*")
    log_type: str = Field(..., description="日志类型: nginx, system, application, custom")
    enabled: bool = Field(True, description="是否启用")
    retention_days: int = Field(7, description="保留天数")
    description: Optional[str] = Field(None, description="描述")


class LogAccessConfig(BaseModel):
    """日志接入凭证配置"""
    id: Optional[int] = None
    name: str
    backend: str  # elasticsearch, loki, splunk
    host: str
    port: int = 9200
    username: Optional[str] = None
    password: Optional[str] = None
    index_pattern: Optional[str] = None
    enabled: bool = True


class LogAccessConfigCreateRequest(BaseModel):
    """创建日志接入凭证配置请求"""
    name: str = Field(..., description="配置名称")
    backend: str = Field(..., description="后端类型: elasticsearch, loki, splunk")
    host: str = Field(..., description="主机地址")
    port: int = Field(9200, description="端口")
    username: Optional[str] = Field(None, description="用户名")
    password: Optional[str] = Field(None, description="密码")
    index_pattern: Optional[str] = Field(None, description="索引模式")
    enabled: bool = Field(True, description="是否启用")


# ---- 日志配置管理 ----

@router.get("/config", summary="获取日志配置列表")
async def get_log_configs(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取所有日志配置项"""
    try:
        configs = LogConfigService.get_all(db)
        return success_response(data=configs, message="获取日志配置成功")
    except Exception as e:
        logger.error(f"获取日志配置失败: {e}")
        return error_response(code=ErrorCode.LOG_QUERY_FAILED, message=f"获取日志配置失败: {str(e)}")


@router.put("/config", summary="批量更新日志配置")
async def update_log_configs(
    req: LogConfigUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """批量更新日志配置项"""
    try:
        configs = LogConfigService.update_all(db, req.configs)
        return success_response(data={"updated": configs}, message="更新日志配置成功")
    except Exception as e:
        logger.error(f"更新日志配置失败: {e}")
        return error_response(code=ErrorCode.LOG_CONFIG_UPDATE_FAILED, message=f"更新日志配置失败: {str(e)}")


@router.get("/config/init", summary="初始化日志配置")
async def init_log_config(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """初始化默认日志配置（仅在数据库为空时插入）"""
    try:
        LogConfigService.init_defaults(db)
        return success_response(message="日志配置初始化成功")
    except Exception as e:
        logger.error(f"初始化日志配置失败: {e}")
        return error_response(code=ErrorCode.LOG_CONFIG_UPDATE_FAILED, message=f"初始化日志配置失败: {str(e)}")


# ---- 日志接入配置（索引管理） ----

@router.get("/indexes", summary="获取日志接入配置列表")
async def get_log_indexes(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取日志接入配置列表（索引模式配置）"""
    from modules.foundation.db_models.system import LogAccessConfig
    try:
        configs = db.query(LogAccessConfig).all()
        items = [{
            "id": c.id,
            "name": c.name,
            "backend": c.backend,
            "host": c.host,
            "port": c.port,
            "username": c.username,
            "index_pattern": c.index_pattern,
            "enabled": bool(c.enabled),
            "created_at": c.created_at.isoformat() if c.created_at else None,
        } for c in configs]
        return success_response(data={"items": items, "total": len(items)}, message="获取日志接入配置成功")
    except Exception as e:
        logger.error(f"获取日志接入配置失败: {e}")
        return error_response(code=ErrorCode.LOG_QUERY_FAILED, message=f"获取日志接入配置失败: {str(e)}")


@router.post("/indexes", summary="创建日志接入配置")
async def create_log_index(
    req: LogIndexCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建日志接入配置（索引模式）"""
    from modules.foundation.db_models.system import LogAccessConfig
    try:
        config = LogAccessConfig(
            name=req.name,
            index_pattern=req.index_pattern,
            log_type=req.log_type,
            enabled=1 if req.enabled else 0,
            retention_days=req.retention_days,
            description=req.description,
        )
        db.add(config)
        db.commit()
        db.refresh(config)
        return success_response(data={
            "id": config.id,
            "name": config.name,
            "index_pattern": config.index_pattern,
            "log_type": config.log_type,
            "enabled": bool(config.enabled),
        }, message="创建日志接入配置成功", code="OK")
    except Exception as e:
        logger.error(f"创建日志接入配置失败: {e}")
        db.rollback()
        return error_response(code=ErrorCode.LOG_INDEX_CREATE_FAILED, message=f"创建日志接入配置失败: {str(e)}")


@router.delete("/indexes/{index_id}", summary="删除日志接入配置")
async def delete_log_index(
    index_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除指定的日志接入配置"""
    from modules.foundation.db_models.system import LogAccessConfig
    try:
        config = db.query(LogAccessConfig).filter(LogAccessConfig.id == index_id).first()
        if not config:
            return error_response(code=ErrorCode.LOG_INDEX_NOT_FOUND, message="日志接入配置不存在")
        db.delete(config)
        db.commit()
        return success_response(message="删除日志接入配置成功")
    except Exception as e:
        logger.error(f"删除日志接入配置失败: {e}")
        db.rollback()
        return error_response(code=ErrorCode.LOG_INDEX_DELETE_FAILED, message=f"删除日志接入配置失败: {str(e)}")


# ---- 日志接入凭证管理 ----

@router.get("/access-configs", summary="获取日志接入凭证列表")
async def get_access_configs(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取日志后端接入凭证配置列表"""
    from modules.foundation.db_models.system import LogAccessConfig
    try:
        configs = db.query(LogAccessConfig).all()
        items = [{
            "id": c.id,
            "name": c.name,
            "backend": c.backend,
            "host": c.host,
            "port": c.port,
            "username": c.username,
            "index_pattern": c.index_pattern,
            "enabled": bool(c.enabled),
            "created_at": c.created_at.isoformat() if c.created_at else None,
        } for c in configs]
        return success_response(data={"items": items, "total": len(items)}, message="获取接入凭证成功")
    except Exception as e:
        logger.error(f"获取接入凭证失败: {e}")
        return error_response(code=ErrorCode.LOG_QUERY_FAILED, message=f"获取接入凭证失败: {str(e)}")


@router.post("/access-configs", summary="创建日志接入凭证")
async def create_access_config(
    req: LogAccessConfigCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建日志接入凭证配置"""
    from modules.foundation.db_models.system import LogAccessConfig
    try:
        config = LogAccessConfig(
            name=req.name,
            backend=req.backend,
            host=req.host,
            port=req.port,
            username=req.username,
            password=req.password,
            index_pattern=req.index_pattern,
            enabled=1 if req.enabled else 0,
        )
        db.add(config)
        db.commit()
        db.refresh(config)
        return success_response(data={
            "id": config.id,
            "name": config.name,
            "backend": config.backend,
            "host": config.host,
            "port": config.port,
            "enabled": bool(config.enabled),
        }, message="创建接入凭证成功", code="OK")
    except Exception as e:
        logger.error(f"创建接入凭证失败: {e}")
        db.rollback()
        return error_response(code=ErrorCode.LOG_ACCESS_CONFIG_UPDATE_FAILED, message=f"创建接入凭证失败: {str(e)}")


@router.delete("/access-configs/{config_id}", summary="删除日志接入凭证")
async def delete_access_config(
    config_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除指定的日志接入凭证"""
    from modules.foundation.db_models.system import LogAccessConfig
    try:
        config = db.query(LogAccessConfig).filter(LogAccessConfig.id == config_id).first()
        if not config:
            return error_response(code=ErrorCode.LOG_ACCESS_CONFIG_NOT_FOUND, message="接入凭证不存在")
        db.delete(config)
        db.commit()
        return success_response(message="删除接入凭证成功")
    except Exception as e:
        logger.error(f"删除接入凭证失败: {e}")
        db.rollback()
        return error_response(code=ErrorCode.LOG_ACCESS_CONFIG_UPDATE_FAILED, message=f"删除接入凭证失败: {str(e)}")


# ---- 日志查询 ----

@router.get("/groups", summary="获取日志归集组列表")
async def get_log_groups(
    category: str = Query(..., description="日志分类: operation/system/collection/audit"),
    keyword: Optional[str] = Query(None, description="关键词过滤"),
    start_date: Optional[datetime] = Query(None, description="开始时间"),
    end_date: Optional[datetime] = Query(None, description="结束时间"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取指定分类的日志归集组列表"""
    try:
        result = LogAggregationService.get_groups(
            db, category, keyword, start_date, end_date, page, page_size
        )
        return success_response(data=result, message="获取日志归集组成功")
    except Exception as e:
        logger.error(f"获取日志归集组失败: {e}")
        return error_response(code=ErrorCode.LOG_QUERY_FAILED, message=f"获取日志归集组失败: {str(e)}")


@router.get("/groups/{group_id}/items", summary="获取日志归集组明细")
async def get_group_items(
    group_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取指定归集组内的日志明细"""
    try:
        result = LogAggregationService.get_group_items(db, group_id, page, page_size)
        return success_response(data=result, message="获取日志明细成功")
    except Exception as e:
        logger.error(f"获取日志明细失败: {e}")
        return error_response(code=ErrorCode.LOG_QUERY_FAILED, message=f"获取日志明细失败: {str(e)}")


@router.get("/stats", summary="获取日志统计")
async def get_log_stats(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取各分类日志实时统计"""
    try:
        stats = LogAggregationService.get_stats(db)
        return success_response(data=stats, message="获取日志统计成功")
    except Exception as e:
        logger.error(f"获取日志统计失败: {e}")
        return error_response(code=ErrorCode.LOG_QUERY_FAILED, message=f"获取日志统计失败: {str(e)}")


@router.post("/cleanup", summary="清理过期日志")
async def cleanup_logs(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """触发过期日志清理"""
    try:
        LogAggregationService.cleanup_old_logs(db)
        return success_response(message="日志清理完成")
    except Exception as e:
        logger.error(f"日志清理失败: {e}")
        return error_response(code=ErrorCode.LOG_QUERY_FAILED, message=f"日志清理失败: {str(e)}")


# ---- 操作日志查询（兼容旧接口） ----

@router.get("/operation", summary="查询操作日志")
async def query_operation_logs(
    username: Optional[str] = Query(None, description="用户名"),
    action: Optional[str] = Query(None, description="操作类型"),
    resource: Optional[str] = Query(None, description="资源类型"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查询操作日志（从 operation_logs 表）"""
    from modules.foundation.db_models.system import OperationLog
    try:
        query = db.query(OperationLog)
        if username:
            query = query.filter(OperationLog.username.ilike(f"%{username}%"))
        if action:
            query = query.filter(OperationLog.action == action)
        if resource:
            query = query.filter(OperationLog.resource == resource)
        if start_time:
            query = query.filter(OperationLog.timestamp >= start_time)
        if end_time:
            query = query.filter(OperationLog.timestamp <= end_time)

        total = query.count()
        logs = query.order_by(OperationLog.timestamp.desc()) \
            .offset((page - 1) * page_size).limit(page_size).all()

        items = [{
            "id": log.id,
            "username": log.username,
            "action": log.action,
            "resource": log.resource,
            "resource_id": log.resource_id,
            "method": log.method,
            "path": log.path,
            "ip_address": log.ip_address,
            "response_status": log.response_status,
            "duration_ms": log.duration_ms,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
        } for log in logs]

        return success_response(data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }, message="查询操作日志成功")
    except Exception as e:
        logger.error(f"查询操作日志失败: {e}")
        return error_response(code=ErrorCode.LOG_QUERY_FAILED, message=f"查询操作日志失败: {str(e)}")
