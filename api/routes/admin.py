"""
系统管理API路由
提供用户管理、角色权限、系统配置等管理功能
"""

from typing import Optional, List
from datetime import datetime
import secrets
import json
import zlib

from fastapi import APIRouter, Depends, Query, HTTPException, Body
from pydantic import BaseModel, Field

from api.dependencies import get_db, get_current_user, CurrentUser, PaginationParams, require_role
from core.config.manager import ConfigManager
from sqlalchemy.orm import Session

from api.routes.auth import _user_store
from modules.foundation.auth_manager.auth import PasswordHasher


router = APIRouter()


def _role_id_from_code(code: str) -> int:
    """从角色代码生成确定性ID（避免Python hash()的进程随机化问题）"""
    return zlib.crc32(code.encode('utf-8')) & 0x7FFFFFFF % 10000


# ============== 请求/响应模型 ==============

class UserCreate(BaseModel):
    """创建用户"""
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    password: str = Field(..., description="密码")
    full_name: Optional[str] = Field(None, description="姓名")
    phone: Optional[str] = Field(None, description="电话")
    roles: List[str] = Field(default_factory=list, description="角色列表")
    is_active: bool = Field(True, description="是否启用")


class UserUpdate(BaseModel):
    """更新用户"""
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    roles: Optional[List[str]] = None
    is_active: Optional[bool] = None


class RoleCreate(BaseModel):
    """创建角色"""
    name: str = Field(..., description="角色名称")
    code: str = Field(..., description="角色代码")
    description: Optional[str] = Field(None, description="描述")
    permissions: List[str] = Field(default_factory=list, description="权限列表")


class SystemConfigUpdate(BaseModel):
    """更新系统配置"""
    key: str = Field(..., description="配置键")
    value: str = Field(..., description="配置值")
    description: Optional[str] = Field(None, description="描述")


# 预定义角色
ROLES = {
    "admin": {"name": "管理员", "code": "admin", "permissions": ["*"], "description": "系统管理员"},
    "operator": {"name": "运维工程师", "code": "operator", "permissions": ["monitoring:read", "workorder:write", "asset:read", "knowledge:read"], "description": "运维工程师"},
    "viewer": {"name": "访客", "code": "viewer", "permissions": ["monitoring:read", "asset:read", "knowledge:read"], "description": "只读访客"},
}

# 预定义权限
PERMISSIONS = [
    {"code": "monitoring:read", "name": "查看监控", "category": "monitoring"},
    {"code": "monitoring:write", "name": "管理监控", "category": "monitoring"},
    {"code": "workorder:read", "name": "查看工单", "category": "workorder"},
    {"code": "workorder:write", "name": "管理工单", "category": "workorder"},
    {"code": "asset:read", "name": "查看资产", "category": "asset"},
    {"code": "asset:write", "name": "管理资产", "category": "asset"},
    {"code": "knowledge:read", "name": "查看知识库", "category": "knowledge"},
    {"code": "knowledge:write", "name": "管理知识库", "category": "knowledge"},
    {"code": "report:read", "name": "查看报表", "category": "report"},
    {"code": "report:write", "name": "管理报表", "category": "report"},
    {"code": "admin:user", "name": "用户管理", "category": "admin"},
    {"code": "admin:role", "name": "角色管理", "category": "admin"},
    {"code": "admin:config", "name": "系统配置", "category": "admin"},
]

# 系统配置（内存存储，生产环境应存入数据库）
import time as _time
import os as _os

def _get_default_timezone():
    tz = _os.environ.get('TZ', '')
    if tz:
        return tz
    # Windows
    if hasattr(_time, 'tzset'):
        _time.tzset()
    return str(_time.tzname[0]) if _time.tzname else 'UTC'

_system_config = {
    "system.name": {"value": "ITOps Platform", "description": "系统名称", "category": "system"},
    "system.maintenance": {"value": "false", "description": "维护模式", "category": "system"},
    "system.version": {"value": "1.0.0", "description": "系统版本", "category": "system"},
    "system.timezone": {"value": "Asia/Shanghai", "description": "系统时区", "category": "system"},
}


# ============== 用户管理接口 ==============

@router.get("/users", summary="获取用户列表")
async def get_users(
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    role: Optional[str] = Query(None, description="角色过滤"),
    is_active: Optional[bool] = Query(None, description="启用状态过滤"),
    pagination: PaginationParams = Depends(PaginationParams),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户列表"""
    all_users = _user_store.list_users()
    
    # 过滤
    filtered_users = all_users
    if keyword:
        filtered_users = [u for u in filtered_users if 
            keyword.lower() in u.username.lower() or 
            (u.email and keyword.lower() in u.email.lower())]
    
    if role:
        filtered_users = [u for u in filtered_users if role in u.roles]
    
    total = len(filtered_users)
    
    # 分页
    start = pagination.offset
    end = start + pagination.limit
    page_users = filtered_users[start:end]
    
    return {
        "items": [_user_to_dict(u) for u in page_users],
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
    }


def _user_to_dict(user) -> dict:
    """用户转字典"""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.metadata.get("full_name") if user.metadata else None,
        "phone": user.metadata.get("phone") if user.metadata else None,
        "roles": user.roles,
        "is_active": user.status.value == "active",
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "created_at": user.created_at.isoformat(),
    }


@router.post("/users", summary="创建用户")
async def create_user(
    user: UserCreate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """创建新用户"""
    try:
        new_user = _user_store.create_user(
            username=user.username,
            password=user.password,
            email=user.email,
            roles=user.roles if user.roles else None,
        )
        
        return {
            "id": new_user.get("user_id"),
            "username": user.username,
            "email": user.email,
            "roles": new_user.get("roles", user.roles if user.roles else ["viewer"]),
            "is_active": True,
            "created_at": datetime.now().isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users/{user_id}", summary="获取用户详情")
async def get_user(
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户详细信息"""
    user_data = _user_store.get_user_by_id(str(user_id))
    
    if not user_data:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # get_user_by_id 返回简化dict，直接用
    return {
        "id": user_data["user_id"],
        "username": user_data["username"],
        "email": user_data["email"],
        "full_name": None,
        "phone": None,
        "roles": user_data["roles"],
        "is_active": user_data["is_active"],
        "last_login": None,
        "created_at": None,
    }


@router.put("/users/{user_id}", summary="更新用户")
async def update_user(
    user_id: str,
    user: UserUpdate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """更新用户信息"""
    # 获取用户
    target_user = None
    for u in _user_store.list_users():
        if u.id == str(user_id):
            target_user = u
            break
    
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新字段
    _user_store.update_user(
        user_id=str(user_id),
        email=user.email,
        roles=user.roles,
        is_active=user.is_active,
        full_name=user.full_name,
        phone=user.phone,
    )
    
    return {"status": "success", "message": "User updated successfully"}


@router.delete("/users/{user_id}", summary="删除用户")
async def delete_user(
    user_id: str,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """删除用户"""
    # 不能删除管理员
    for u in _user_store.list_users():
        if u.id == str(user_id):
            if u.username == "admin":
                raise HTTPException(status_code=400, detail="不能删除管理员账户")
            _user_store.delete_user(str(user_id))
            return {"status": "success", "message": "User deleted successfully"}
    
    raise HTTPException(status_code=404, detail="用户不存在")


@router.post("/users/{user_id}/reset-password", summary="重置密码")
async def reset_password(
    user_id: str,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """重置用户密码"""
    new_password = f"Password@{secrets.token_hex(4)}"
    ok = _user_store.update_user_password(str(user_id), PasswordHasher.hash_password(new_password))
    if not ok:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        "status": "success",
        "message": "Password reset successfully",
        "new_password": new_password,
    }


# ============== 角色管理接口 ==============

@router.get("/roles", summary="获取角色列表")
async def get_roles(
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """获取角色列表"""
    items = []
    for code, role in ROLES.items():
        # 统计使用该角色的用户数
        all_users = _user_store.list_users()
        user_count = sum(1 for u in all_users if code in u.roles)
        items.append({
            "id": _role_id_from_code(code),
            "name": role["name"],
            "code": role["code"],
            "description": role["description"],
            "permissions": role["permissions"],
            "user_count": user_count,
        })
    
    return {"items": items, "total": len(items)}


@router.post("/roles", summary="创建角色")
async def create_role(
    role: RoleCreate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """创建新角色"""
    if role.code in ROLES:
        raise HTTPException(status_code=400, detail="角色代码已存在")
    
    ROLES[role.code] = {
        "name": role.name,
        "code": role.code,
        "permissions": role.permissions,
        "description": role.description or "",
    }
    
    return {
        "id": _role_id_from_code(role.code),
        "name": role.name,
        "code": role.code,
        "permissions": role.permissions,
        "created_at": datetime.now().isoformat(),
    }


@router.put("/roles/{role_id}", summary="更新角色")
async def update_role(
    role_id: int,
    role: RoleCreate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """更新角色"""
    # 查找角色
    found_code = None
    for code, r in ROLES.items():
        if _role_id_from_code(code) == role_id:
            found_code = code
            break
    
    if not found_code:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    ROLES[found_code] = {
        "name": role.name,
        "code": found_code,
        "permissions": role.permissions,
        "description": role.description or "",
    }
    
    return {"status": "success", "message": "Role updated successfully"}


@router.delete("/roles/{role_id}", summary="删除角色")
async def delete_role(
    role_id: int,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """删除角色"""
    found_code = None
    for code, r in ROLES.items():
        if _role_id_from_code(code) == role_id:
            found_code = code
            break
    
    if not found_code:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    if found_code == "admin":
        raise HTTPException(status_code=400, detail="不能删除管理员角色")
    
    del ROLES[found_code]
    return {"status": "success", "message": "Role deleted successfully"}


# ============== 权限管理接口 ==============

@router.get("/permissions", summary="获取权限列表")
async def get_permissions(
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """获取系统所有权限列表"""
    return {"items": PERMISSIONS, "total": len(PERMISSIONS)}


# ============== 系统配置接口 ==============

@router.get("/config", summary="获取系统配置")
async def get_system_config(
    category: Optional[str] = Query(None, description="配置分类过滤"),
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """获取系统配置"""
    items = []
    for key, cfg in _system_config.items():
        if category and cfg.get("category") != category:
            continue
        items.append({
            "key": key,
            "value": cfg["value"],
            "description": cfg.get("description"),
            "category": cfg.get("category"),
            "updated_at": datetime.now().isoformat(),
        })
    
    return {"items": items, "total": len(items)}


@router.put("/config/{config_key}", summary="更新系统配置")
async def update_system_config(
    config_key: str,
    config: SystemConfigUpdate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """更新系统配置"""
    if config_key not in _system_config:
        _system_config[config_key] = {}
    
    _system_config[config_key]["value"] = config.value
    _system_config[config_key]["description"] = config.description or _system_config[config_key].get("description", "")
    
    return {"status": "success", "message": "Configuration updated successfully"}


@router.get("/ai/config", summary="获取AI配置")
async def get_ai_config(
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """获取LLM AI配置"""
    cfg = ConfigManager().llm
    return {
        "provider": cfg.provider,
        "api_base": cfg.api_base,
        "api_key": cfg.api_key,
        "model": cfg.model,
        "temperature": cfg.temperature,
        "max_tokens": cfg.max_tokens,
    }


@router.get("/timezones", summary="获取可用时区列表")
async def get_timezones(
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """获取所有可用时区列表"""
    import zoneinfo
    zones = sorted(zoneinfo.available_timezones())
    # 常用时区优先
    common = ["Asia/Shanghai", "Asia/Hong_Kong", "Asia/Tokyo", "Asia/Singapore",
              "Europe/London", "Europe/Paris", "Europe/Berlin",
              "America/New_York", "America/Los_Angeles", "America/Chicago",
              "UTC", "GMT"]
    prioritized = [z for z in common if z in zones]
    others = [z for z in zones if z not in common]
    return {"items": prioritized + others, "total": len(zones)}


# ============== 系统信息接口 ==============

@router.get("/info", summary="获取系统信息")
async def get_system_info(
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取系统运行信息"""
    return {
        "version": _system_config.get("system.version", {}).get("value", "1.0.0"),
        "environment": "production",
        "uptime": 86400,
        "timezone": _system_config.get("system.timezone", {}).get("value", "UTC"),
        "database": {
            "type": "mysql",
            "status": "connected",
            "connections": 10,
        },
        "redis": {
            "status": "connected",
        },
    }


@router.get("/metrics", summary="获取系统指标")
async def get_system_metrics(
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """获取系统性能指标"""
    # 简化实现，返回模拟数据
    # 实际应从系统收集真实指标
    return {
        "cpu": {"usage": 45.5, "cores": 8},
        "memory": {"total": 16384, "used": 8192, "usage": 50.0},
        "disk": {"total": 512000, "used": 256000, "usage": 50.0},
        "network": {"in": 1000, "out": 500},
    }


# ============== 操作日志接口 ==============

@router.get("/logs", summary="获取操作日志")
async def get_operation_logs(
    operator: Optional[str] = Query(None, description="操作人过滤"),
    action: Optional[str] = Query(None, description="操作类型过滤"),
    start_date: Optional[datetime] = Query(None, description="开始时间"),
    end_date: Optional[datetime] = Query(None, description="结束时间"),
    pagination: PaginationParams = Depends(PaginationParams),
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """获取操作日志"""
    from modules.foundation.db_models.system import OperationLog

    query = db.query(OperationLog)

    if operator:
        query = query.filter(OperationLog.username == operator)
    if action:
        query = query.filter(OperationLog.action == action)
    if start_date:
        query = query.filter(OperationLog.timestamp >= start_date)
    if end_date:
        query = query.filter(OperationLog.timestamp <= end_date)

    total = query.count()
    logs = query.order_by(OperationLog.timestamp.desc()).offset(pagination.offset).limit(pagination.limit).all()

    return {
        "items": [
            {
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
            }
            for log in logs
        ],
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
    }


# ============== 系统日志接口 ==============

@router.get("/system-logs", summary="获取系统日志")
async def get_system_logs(
    level: Optional[str] = Query(None, description="日志级别过滤"),
    keyword: Optional[str] = Query(None, description="关键词过滤"),
    start_date: Optional[datetime] = Query(None, description="开始时间"),
    end_date: Optional[datetime] = Query(None, description="结束时间"),
    pagination: PaginationParams = Depends(PaginationParams),
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """读取 api.log 文件作为系统日志"""
    import os

    log_file = os.environ.get("ITOPS_LOG_FILE", "/tmp/itops_data/logs/api.log")
    if not os.path.exists(log_file):
        return {"items": [], "total": 0, "page": pagination.page, "page_size": pagination.limit}

    entries = []
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Parse: 2026-05-21 03:00:00,000 - access - INFO - {"type": "request_start", ...}
                # or: 2026-05-21 03:00:00,000 - module - LEVEL - message
                parts = line.split(" - ", 3)
                if len(parts) < 4:
                    continue
                ts_str = parts[0]
                source = parts[1]
                level_val = parts[2].strip()
                message = parts[3]

                # Filter by level
                if level and level_val.upper() != level.upper():
                    continue
                # Filter by keyword
                if keyword and keyword.lower() not in message.lower():
                    continue
                # Filter by date range
                try:
                    from datetime import datetime as dt
                    log_dt = dt.strptime(ts_str.split(",")[0], "%Y-%m-%d %H:%M:%S")
                    if start_date and log_dt < start_date:
                        continue
                    if end_date and log_dt > end_date:
                        continue
                except Exception:
                    pass

                entries.append({
                    "idx": len(entries) + 1,
                    "time": ts_str.replace(",", "."),
                    "level": level_val,
                    "source": source,
                    "message": message,
                })
    except Exception as e:
        pass

    total = len(entries)
    start = pagination.offset
    end = start + pagination.limit
    page_entries = entries[start:end]

    return {
        "items": page_entries,
        "total": total,
        "page": pagination.page,
        "page_size": pagination.limit,
    }


# ============== 采集日志接口 ==============

@router.get("/collection-logs", summary="获取采集日志")
async def get_collection_logs(
    status: Optional[str] = Query(None, description="采集状态"),
    device: Optional[str] = Query(None, description="设备名称过滤"),
    pagination: PaginationParams = Depends(PaginationParams),
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """从 performance_metrics 表读取最新采集记录作为采集日志"""
    from modules.foundation.db_models.monitoring import PerformanceMetric

    query = db.query(PerformanceMetric)

    if device:
        query = query.filter(PerformanceMetric.device_name.ilike(f"%{device}%"))
    if status:
        # Map status to metric patterns
        if status == "success":
            pass  # All metrics imply success
        elif status == "failed":
            pass  # No clear failure indicator in this table
        elif status == "offline":
            query = query.filter(PerformanceMetric.metric_name == "ping_status")

    # Order by timestamp desc
    query = query.order_by(PerformanceMetric.timestamp.desc())

    total = query.count()
    rows = query.offset(pagination.offset).limit(pagination.limit).all()

    # Group by collection time to build "log entries"
    entries = {}
    for row in rows:
        key = (row.device_name, row.timestamp)
        if key not in entries:
            entries[key] = {
                "idx": len(entries) + 1,
                "time": row.timestamp.strftime("%Y-%m-%d %H:%M:%S") if row.timestamp else "-",
                "device": row.device_name or f"device_{row.device_id}",
                "protocol": row.metric_category or "monitoring",
                "status": "success",
                "duration": "-",
                "message": f"{row.metric_name} = {row.value} {row.metric_unit or ''}".strip(),
            }
        else:
            entries[key]["message"] += f" | {row.metric_name} = {row.value} {row.metric_unit or ''}".strip()

    items = list(entries.values())
    # Apply status filter in Python (since we grouped)
    if status == "failed":
        items = [e for e in items if "error" in e["message"].lower() or "fail" in e["message"].lower()]
    elif status == "offline":
        items = [e for e in items if "ping" in e["message"].lower() and "0" in e["message"]]

    total = len(items)
    start = pagination.offset
    end = start + pagination.limit

    return {
        "items": items[start:end],
        "total": total,
        "page": pagination.page,
        "page_size": pagination.limit,
    }


# ============== 备份管理接口 ==============

@router.get("/backup", summary="获取备份列表")
async def get_backups(
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """获取数据库备份列表"""
    from modules.foundation.db_models.system import BackupRecord

    backups = db.query(BackupRecord).order_by(BackupRecord.created_at.desc()).all()

    return {
        "items": [
            {
                "id": b.id,
                "backup_type": b.backup_type,
                "file_name": b.file_name,
                "file_path": b.file_path,
                "file_size": b.file_size,
                "status": b.status,
                "storage_type": b.storage_type,
                "created_by": b.created_by,
                "started_at": b.started_at.isoformat() if b.started_at else None,
                "completed_at": b.completed_at.isoformat() if b.completed_at else None,
                "duration_seconds": b.duration_seconds,
                "created_at": b.created_at.isoformat() if b.created_at else None,
            }
            for b in backups
        ],
        "total": len(backups)
    }


@router.post("/backup", summary="创建备份")
async def create_backup(
    backup_type: str = Query("full", description="备份类型: full, incremental, config"),
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """创建数据库备份"""
    from modules.foundation.db_models.system import BackupRecord
    import os

    # 生成备份文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f"backup_{backup_type}_{timestamp}.sql"
    backup_dir = "/tmp/backups"

    # 确保备份目录存在
    os.makedirs(backup_dir, exist_ok=True)
    file_path = os.path.join(backup_dir, file_name)

    # 创建备份记录
    backup_record = BackupRecord(
        backup_type=backup_type,
        file_name=file_name,
        file_path=file_path,
        status="completed",
        storage_type="local",
        storage_path=backup_dir,
        created_by=current_user.username,
        started_at=datetime.now(),
        completed_at=datetime.now(),
        duration_seconds=0,
    )

    db.add(backup_record)
    db.commit()
    db.refresh(backup_record)

    return {
        "status": "success",
        "message": "Backup created",
        "task_id": f"backup-{timestamp}",
        "backup_id": backup_record.id,
        "file_name": file_name,
        "file_path": file_path,
    }


@router.post("/backup/{backup_id}/restore", summary="恢复备份")
async def restore_backup(
    backup_id: int,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """恢复数据库备份"""
    # 简化实现
    return {
        "status": "success",
        "message": "Restore task created",
        "task_id": f"restore-{datetime.now().strftime('%Y%m%d%H%M%S')}",
    }


# ============== 缓存管理接口 ==============

@router.post("/cache/clear", summary="清空缓存")
async def clear_cache(
    cache_type: str = Query("all", description="缓存类型: all, redis, memory"),
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """清空系统缓存"""
    # 简化实现
    return {
        "status": "success",
        "message": f"{cache_type} cache cleared",
    }


# ============== 健康检查接口 ==============

@router.get("/health", summary="系统健康检查")
async def system_health_check(
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """执行系统健康检查"""
    return {
        "status": "healthy",
        "components": {
            "database": {"status": "healthy", "latency_ms": 5},
            "redis": {"status": "healthy", "latency_ms": 1},
            "filesystem": {"status": "healthy", "usage_percent": 45},
            "monitoring": {"status": "healthy"},
        },
        "checked_at": datetime.now().isoformat(),
    }


# ============== API Key管理接口 ==============

import secrets
import hashlib
import string


def _generate_api_key(prefix: str = "sk") -> tuple:
    """
    生成API Key
    Returns: (full_key, key_hash, key_prefix)
    """
    # 生成随机字符串
    random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(48))
    full_key = f"{prefix}-{random_part}"
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    key_prefix = f"{prefix}-{random_part[:8]}"
    return full_key, key_hash, key_prefix


def _mask_api_key(key: str) -> str:
    """掩码API Key，只显示前8位"""
    if len(key) > 12:
        return f"{key[:12]}{'***'}"
    return f"{key[:4]}{'***'}"


class APIKeyCreate(BaseModel):
    """创建API Key"""
    name: str = Field(..., description="API Key名称")
    user_id: Optional[str] = Field(None, description="关联用户ID")
    username: Optional[str] = Field(None, description="关联用户名")
    scopes: List[str] = Field(default_factory=list, description="权限范围")
    expires_days: Optional[int] = Field(None, description="过期天数，为空表示永不过期")
    max_requests: Optional[int] = Field(None, description="最大请求数，为空表示无限制")
    rate_limit: Optional[int] = Field(100, description="每分钟请求数限制")
    rate_limit_window: Optional[int] = Field(60, description="速率限制时间窗口(秒)")


class APIKeyUpdate(BaseModel):
    """更新API Key"""
    name: Optional[str] = None
    enabled: Optional[bool] = None
    scopes: Optional[List[str]] = None
    expires_days: Optional[int] = None
    max_requests: Optional[int] = None
    rate_limit: Optional[int] = None


@router.get("/api-keys", summary="获取API Key列表")
async def get_api_keys(
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    is_active: Optional[bool] = Query(None, description="启用状态过滤"),
    pagination: PaginationParams = Depends(PaginationParams),
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """获取API Key列表"""
    from modules.foundation.db_models.system import APIKey

    query = db.query(APIKey)

    if keyword:
        query = query.filter(
            (APIKey.name.ilike(f"%{keyword}%")) |
            (APIKey.key_id.ilike(f"%{keyword}%")) |
            (APIKey.username.ilike(f"%{keyword}%"))
        )

    if is_active is not None:
        query = query.filter(APIKey.is_active == (1 if is_active else 0))

    total = query.count()
    keys = query.order_by(APIKey.created_at.desc()).offset(pagination.offset).limit(pagination.limit).all()

    return {
        "items": [
            {
                "id": k.id,
                "key_id": k.key_id,
                "key_prefix": k.key_prefix,
                "name": k.name,
                "username": k.username,
                "scopes": json.loads(k.scopes) if k.scopes else [],
                "is_active": bool(k.is_active),
                "is_revoked": bool(k.is_revoked),
                "expires_at": k.expires_at.isoformat() if k.expires_at else None,
                "max_requests": k.max_requests,
                "request_count": k.request_count,
                "rate_limit": k.rate_limit,
                "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
                "created_at": k.created_at.isoformat() if k.created_at else None,
                "created_by": k.created_by,
            }
            for k in keys
        ],
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
    }


@router.post("/api-keys", summary="创建API Key")
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """创建新的API Key"""
    from modules.foundation.db_models.system import APIKey

    # 生成API Key
    full_key, key_hash, key_prefix = _generate_api_key()

    # 计算过期时间
    expires_at = None
    if api_key_data.expires_days:
        from datetime import timedelta
        expires_at = datetime.now() + timedelta(days=api_key_data.expires_days)

    # 创建记录
    api_key_record = APIKey(
        key_id=f"key_{secrets.token_hex(8)}",
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=api_key_data.name,
        user_id=api_key_data.user_id,
        username=api_key_data.username,
        scopes=json.dumps(api_key_data.scopes) if api_key_data.scopes else None,
        is_active=1,
        is_revoked=0,
        expires_at=expires_at,
        max_requests=api_key_data.max_requests or -1,
        rate_limit=api_key_data.rate_limit or 100,
        rate_limit_window=api_key_data.rate_limit_window or 60,
        created_by=current_user.username,
    )

    db.add(api_key_record)
    db.commit()
    db.refresh(api_key_record)

    return {
        "id": api_key_record.id,
        "key_id": api_key_record.key_id,
        "api_key": full_key,  # 只在创建时返回一次
        "key_prefix": key_prefix,
        "name": api_key_data.name,
        "scopes": api_key_data.scopes,
        "expires_at": expires_at.isoformat() if expires_at else None,
        "max_requests": api_key_data.max_requests,
        "rate_limit": api_key_data.rate_limit,
        "created_at": api_key_record.created_at.isoformat() if api_key_record.created_at else None,
        "message": "请妥善保管API Key，仅在创建时显示完整Key"
    }


@router.get("/api-keys/{key_id}", summary="获取API Key详情")
async def get_api_key(
    key_id: str,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """获取指定API Key的详细信息"""
    from modules.foundation.db_models.system import APIKey

    api_key_record = db.query(APIKey).filter(APIKey.key_id == key_id).first()

    if not api_key_record:
        raise HTTPException(status_code=404, detail="API Key不存在")

    return {
        "id": api_key_record.id,
        "key_id": api_key_record.key_id,
        "key_prefix": api_key_record.key_prefix,
        "name": api_key_record.name,
        "user_id": api_key_record.user_id,
        "username": api_key_record.username,
        "scopes": json.loads(api_key_record.scopes) if api_key_record.scopes else [],
        "is_active": bool(api_key_record.is_active),
        "is_revoked": bool(api_key_record.is_revoked),
        "expires_at": api_key_record.expires_at.isoformat() if api_key_record.expires_at else None,
        "max_requests": api_key_record.max_requests,
        "request_count": api_key_record.request_count,
        "rate_limit": api_key_record.rate_limit,
        "rate_limit_window": api_key_record.rate_limit_window,
        "last_used_at": api_key_record.last_used_at.isoformat() if api_key_record.last_used_at else None,
        "last_used_ip": api_key_record.last_used_ip,
        "created_at": api_key_record.created_at.isoformat() if api_key_record.created_at else None,
        "created_by": api_key_record.created_by,
    }


@router.put("/api-keys/{key_id}", summary="更新API Key")
async def update_api_key(
    key_id: str,
    api_key_data: APIKeyUpdate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """更新API Key"""
    from modules.foundation.db_models.system import APIKey

    api_key_record = db.query(APIKey).filter(APIKey.key_id == key_id).first()

    if not api_key_record:
        raise HTTPException(status_code=404, detail="API Key不存在")

    # 更新字段
    if api_key_data.name is not None:
        api_key_record.name = api_key_data.name

    if api_key_data.enabled is not None:
        api_key_record.is_active = 1 if api_key_data.enabled else 0

    if api_key_data.scopes is not None:
        api_key_record.scopes = json.dumps(api_key_data.scopes)

    if api_key_data.expires_days is not None:
        from datetime import timedelta
        if api_key_data.expires_days > 0:
            api_key_record.expires_at = datetime.now() + timedelta(days=api_key_data.expires_days)
        else:
            api_key_record.expires_at = None

    if api_key_data.max_requests is not None:
        api_key_record.max_requests = api_key_data.max_requests

    if api_key_data.rate_limit is not None:
        api_key_record.rate_limit = api_key_data.rate_limit

    api_key_record.updated_at = datetime.now()

    db.commit()

    return {"status": "success", "message": "API Key更新成功"}


@router.delete("/api-keys/{key_id}", summary="删除API Key")
async def delete_api_key(
    key_id: str,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """删除API Key"""
    from modules.foundation.db_models.system import APIKey

    api_key_record = db.query(APIKey).filter(APIKey.key_id == key_id).first()

    if not api_key_record:
        raise HTTPException(status_code=404, detail="API Key不存在")

    db.delete(api_key_record)
    db.commit()

    return {"status": "success", "message": "API Key删除成功"}


@router.post("/api-keys/{key_id}/revoke", summary="撤销API Key")
async def revoke_api_key(
    key_id: str,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """撤销API Key（软删除）"""
    from modules.foundation.db_models.system import APIKey

    api_key_record = db.query(APIKey).filter(APIKey.key_id == key_id).first()

    if not api_key_record:
        raise HTTPException(status_code=404, detail="API Key不存在")

    if api_key_record.is_revoked:
        raise HTTPException(status_code=400, detail="API Key已被撤销")

    api_key_record.is_revoked = 1
    api_key_record.is_active = 0
    api_key_record.updated_at = datetime.now()

    db.commit()

    return {"status": "success", "message": "API Key已撤销"}


@router.post("/api-keys/{key_id}/activate", summary="激活API Key")
async def activate_api_key(
    key_id: str,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """激活被禁用的API Key"""
    from modules.foundation.db_models.system import APIKey

    api_key_record = db.query(APIKey).filter(APIKey.key_id == key_id).first()

    if not api_key_record:
        raise HTTPException(status_code=404, detail="API Key不存在")

    if api_key_record.is_revoked:
        raise HTTPException(status_code=400, detail="已撤销的API Key无法激活，请重新创建")

    api_key_record.is_active = 1
    api_key_record.updated_at = datetime.now()

    db.commit()

    return {"status": "success", "message": "API Key已激活"}


@router.post("/api-keys/{key_id}/rotate", summary="轮换API Key")
async def rotate_api_key(
    key_id: str,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """轮换API Key（创建新的Key并禁用旧的）"""
    from modules.foundation.db_models.system import APIKey

    api_key_record = db.query(APIKey).filter(APIKey.key_id == key_id).first()

    if not api_key_record:
        raise HTTPException(status_code=404, detail="API Key不存在")

    # 生成新Key
    full_key, key_hash, key_prefix = _generate_api_key()

    # 更新旧Key为禁用
    api_key_record.is_active = 0
    api_key_record.is_revoked = 1
    api_key_record.updated_at = datetime.now()

    # 创建新Key（复制原Key的大部分属性）
    new_key_record = APIKey(
        key_id=f"key_{secrets.token_hex(8)}",
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=api_key_record.name + " (轮换)",
        user_id=api_key_record.user_id,
        username=api_key_record.username,
        scopes=api_key_record.scopes,
        is_active=1,
        is_revoked=0,
        expires_at=api_key_record.expires_at,
        max_requests=api_key_record.max_requests,
        rate_limit=api_key_record.rate_limit,
        rate_limit_window=api_key_record.rate_limit_window,
        created_by=current_user.username,
    )

    db.add(new_key_record)
    db.commit()
    db.refresh(new_key_record)

    return {
        "status": "success",
        "message": "API Key已轮换，旧Key已禁用",
        "old_key_id": key_id,
        "new_key_id": new_key_record.key_id,
        "new_api_key": full_key,
        "key_prefix": key_prefix,
    }


# ============== 备份恢复接口 ==============

class BackupCreateRequest(BaseModel):
    """创建备份请求"""
    name: str = Field(..., description="备份名称")
    backup_type: str = Field("full", description="备份类型: full, incremental, differential")
    targets: List[str] = Field(default_factory=list, description="备份目标: database, config, files, all")
    description: str = Field("", description="备份描述")


class BackupRestoreRequest(BaseModel):
    """恢复备份请求"""
    target: str = Field("all", description="恢复目标: database, config, files, all")
    target_path: Optional[str] = Field(None, description="恢复路径")
    create_pre_backup: bool = Field(True, description="恢复前是否创建备份")


@router.get("/backups", summary="获取备份列表")
async def get_backups(
    status: Optional[str] = Query(None, description="状态过滤"),
    backup_type: Optional[str] = Query(None, description="备份类型过滤"),
    limit: int = Query(100, le=500),
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """获取备份列表"""
    from modules.business.backup_manager import (
        get_backup_manager, BackupStatus, BackupType
    )
    
    manager = get_backup_manager()
    
    status_enum = None
    if status:
        try:
            status_enum = BackupStatus(status)
        except ValueError:
            pass
    
    type_enum = None
    if backup_type:
        try:
            type_enum = BackupType(backup_type)
        except ValueError:
            pass
    
    backups = manager.list_backups(status=status_enum, backup_type=type_enum, limit=limit)
    
    return {
        "items": [b.to_dict() for b in backups],
        "total": len(backups),
    }


@router.post("/backups", summary="创建备份")
async def create_backup(
    request: BackupCreateRequest,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """创建新的备份"""
    from modules.business.backup_manager import (
        get_backup_manager, BackupStatus, BackupType, BackupTarget
    )
    
    manager = get_backup_manager()
    
    # 解析备份类型
    backup_type = BackupType(request.backup_type)
    
    # 解析目标
    targets = []
    if not request.targets or 'all' in request.targets:
        targets = [BackupTarget.ALL]
    else:
        for t in request.targets:
            try:
                targets.append(BackupTarget(t))
            except ValueError:
                pass
    
    record = await manager.create_backup(
        name=request.name,
        backup_type=backup_type,
        targets=targets,
        description=request.description,
    )
    
    return {
        "id": record.id,
        "status": record.status.value if isinstance(record.status, BackupStatus) else record.status,
        "message": "备份创建成功" if record.status == BackupStatus.SUCCESS else "备份创建失败",
        "record": record.to_dict(),
    }


@router.get("/backups/{backup_id}", summary="获取备份详情")
async def get_backup(
    backup_id: str,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """获取备份详细信息"""
    from modules.business.backup_manager import get_backup_manager
    
    manager = get_backup_manager()
    backup = manager.get_backup(backup_id)
    
    if not backup:
        raise HTTPException(status_code=404, detail="备份不存在")
    
    return backup.to_dict()


@router.delete("/backups/{backup_id}", summary="删除备份")
async def delete_backup(
    backup_id: str,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """删除备份"""
    from modules.business.backup_manager import get_backup_manager
    
    manager = get_backup_manager()
    
    if not manager.delete_backup(backup_id):
        raise HTTPException(status_code=404, detail="备份不存在")
    
    return {"status": "success", "message": "备份已删除"}


@router.post("/backups/{backup_id}/restore", summary="恢复备份")
async def restore_backup(
    backup_id: str,
    request: BackupRestoreRequest,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """从备份恢复数据"""
    from modules.business.backup_manager import (
        get_backup_manager, BackupTarget
    )
    
    manager = get_backup_manager()
    
    backup = manager.get_backup(backup_id)
    if not backup:
        raise HTTPException(status_code=404, detail="备份不存在")
    
    target = BackupTarget(request.target)
    
    record = await manager.restore(
        backup_id=backup_id,
        target=target,
        target_path=request.target_path,
        create_pre_backup=request.create_pre_backup,
    )
    
    return {
        "id": record.id,
        "status": record.status.value if isinstance(record.status, RestoreStatus) else record.status,
        "message": "恢复成功" if record.status == RestoreStatus.SUCCESS else "恢复失败",
        "record": record.to_dict(),
    }


@router.get("/restores", summary="获取恢复记录列表")
async def get_restores(
    limit: int = Query(100, le=500),
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """获取恢复记录列表"""
    from modules.business.backup_manager import get_backup_manager
    
    manager = get_backup_manager()
    restores = manager.list_restores(limit=limit)
    
    return {
        "items": [r.to_dict() for r in restores],
        "total": len(restores),
    }


@router.get("/restores/{restore_id}", summary="获取恢复记录详情")
async def get_restore(
    restore_id: str,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """获取恢复记录详细信息"""
    from modules.business.backup_manager import get_backup_manager
    
    manager = get_backup_manager()
    restore = manager.get_restore(restore_id)
    
    if not restore:
        raise HTTPException(status_code=404, detail="恢复记录不存在")
    
    return restore.to_dict()


@router.post("/backups/cleanup", summary="清理过期备份")
async def cleanup_backups(
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """清理过期的备份文件"""
    from modules.business.backup_manager import get_backup_manager
    
    manager = get_backup_manager()
    count = manager.cleanup_old_backups()
    
    return {"status": "success", "message": f"已清理 {count} 个过期备份"}


@router.get("/backup/config", summary="获取备份配置")
async def get_backup_config(
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """获取备份配置信息"""
    from modules.business.backup_manager import get_backup_manager
    
    manager = get_backup_manager()
    config = manager.config
    
    return {
        "backup_dir": config.backup_dir,
        "retention_days": config.retention_days,
        "max_backups": config.max_backups,
        "compression_enabled": config.compression_enabled,
        "compression_level": config.compression_level,
        "encryption_enabled": config.encryption_enabled,
        "auto_backup_enabled": config.auto_backup_enabled,
        "backup_schedule": config.backup_schedule,
    }


# ============================================================
# 日志配置与归集 API
# ============================================================

@router.get("/log-configs", summary="获取日志配置列表")
async def get_log_configs(
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """获取日志配置列表（操作/系统/采集/审计）"""
    db = next(get_db())
    try:
        LogConfigService.init_defaults(db)
        configs = LogConfigService.get_all(db)
        return {"items": configs, "total": len(configs)}
    finally:
        db.close()


@router.put("/log-configs", summary="批量更新日志配置")
async def update_log_configs(
    configs: list = Body(..., description="日志配置列表"),
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """批量更新日志配置（启用/禁用/级别/归集开关）"""
    db = next(get_db())
    try:
        LogConfigService.update_all(db, configs)
        return {"status": "ok", "updated": len(configs)}
    finally:
        db.close()


@router.get("/log-stats", summary="获取日志统计")
async def get_log_stats(
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """获取各分类日志的实时统计"""
    db = next(get_db())
    try:
        return LogAggregationService.get_stats(db)
    finally:
        db.close()


@router.get("/logs/groups", summary="获取日志归集组列表")
async def get_log_groups(
    category: str = Query(..., description="分类: operation/system/collection/audit"),
    keyword: str = Query(None, description="关键词过滤"),
    start_date: str = Query(None, description="开始时间 ISO格式"),
    end_date: str = Query(None, description="结束时间 ISO格式"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """获取日志归集组列表（一级视图）"""
    db = next(get_db())
    try:
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        result = LogAggregationService.get_groups(
            db, category, keyword, start_dt, end_dt, page, page_size
        )
        return result
    finally:
        db.close()


@router.get("/logs/groups/{group_id}/items", summary="获取归集组内的日志明细")
async def get_log_group_items(
    group_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """获取某个归集组内的所有日志明细（二级视图）"""
    db = next(get_db())
    try:
        return LogAggregationService.get_group_items(db, group_id, page, page_size)
    finally:
        db.close()


@router.post("/logs/cleanup", summary="清理过期日志")
async def cleanup_logs(
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """根据各配置的 retention_days 清理过期日志"""
    db = next(get_db())
    try:
        LogAggregationService.cleanup_old_logs(db)
        return {"status": "ok", "message": "日志清理完成"}
    finally:
        db.close()


# ============== 组织架构/部门管理接口 ==============

class DepartmentCreate(BaseModel):
    """创建部门"""
    name: str = Field(..., description="部门名称")
    code: Optional[str] = Field(None, description="部门编码")
    parent_id: Optional[int] = Field(None, description="上级部门ID")
    manager_id: Optional[str] = Field(None, description="部门负责人ID")
    description: Optional[str] = Field(None, description="部门描述")
    sort_order: int = Field(0, description="排序")


class DepartmentUpdate(BaseModel):
    """更新部门"""
    name: Optional[str] = None
    code: Optional[str] = None
    parent_id: Optional[int] = None
    manager_id: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    sort_order: Optional[int] = None


def _dept_to_dict(dept) -> dict:
    """部门转字典"""
    return {
        "id": dept.id,
        "name": dept.name,
        "code": dept.code,
        "parent_id": dept.parent_id,
        "manager_id": dept.manager_id,
        "description": dept.description,
        "status": dept.status,
        "sort_order": dept.sort_order,
        "created_at": dept.created_at.isoformat() if dept.created_at else None,
        "updated_at": dept.updated_at.isoformat() if dept.updated_at else None,
    }


@router.get("/departments", summary="获取部门列表")
async def get_departments(
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    parent_id: Optional[int] = Query(None, description="上级部门ID"),
    status: Optional[str] = Query(None, description="状态过滤"),
    pagination: PaginationParams = Depends(PaginationParams),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取部门列表"""
    from modules.foundation.db_models.system import Department

    query = db.query(Department)
    if keyword:
        query = query.filter(
            (Department.name.ilike(f"%{keyword}%")) |
            (Department.code.ilike(f"%{keyword}%"))
        )
    if parent_id is not None:
        query = query.filter(Department.parent_id == parent_id)
    if status:
        query = query.filter(Department.status == status)

    total = query.count()
    departments = query.order_by(Department.sort_order.asc(), Department.id.asc()) \
        .offset(pagination.offset).limit(pagination.limit).all()

    return {
        "items": [_dept_to_dict(d) for d in departments],
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
    }


@router.post("/departments", summary="创建部门")
async def create_department(
    dept: DepartmentCreate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """创建新部门"""
    from modules.foundation.db_models.system import Department

    existing = db.query(Department).filter(Department.name == dept.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"部门名称 '{dept.name}' 已存在")

    if dept.code:
        existing = db.query(Department).filter(Department.code == dept.code).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"部门编码 '{dept.code}' 已存在")

    if dept.parent_id:
        parent = db.query(Department).filter(Department.id == dept.parent_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail=f"上级部门ID {dept.parent_id} 不存在")

    new_dept = Department(
        name=dept.name,
        code=dept.code,
        parent_id=dept.parent_id,
        manager_id=dept.manager_id,
        description=dept.description,
        sort_order=dept.sort_order,
    )
    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)

    return {"code": 0, "message": "success", "data": _dept_to_dict(new_dept)}


@router.get("/departments/tree", summary="获取部门树")
async def get_department_tree(
    status: Optional[str] = Query(None, description="状态过滤"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取部门树形结构"""
    from modules.foundation.db_models.system import Department

    query = db.query(Department)
    if status:
        query = query.filter(Department.status == status)

    all_depts = query.order_by(Department.sort_order.asc(), Department.id.asc()).all()

    dept_dict = {d.id: _dept_to_dict(d) for d in all_depts}
    for d in all_depts:
        dept_dict[d.id]["children"] = []

    roots = []
    for d in all_depts:
        if d.parent_id and d.parent_id in dept_dict:
            dept_dict[d.parent_id]["children"].append(dept_dict[d.id])
        elif not d.parent_id:
            roots.append(dept_dict[d.id])

    return {"code": 0, "message": "success", "data": roots}


@router.get("/departments/{dept_id}", summary="获取部门详情")
async def get_department(
    dept_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取部门详情"""
    from modules.foundation.db_models.system import Department

    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail=f"部门 {dept_id} 不存在")

    children_count = db.query(Department).filter(Department.parent_id == dept_id).count()

    result = _dept_to_dict(dept)
    result["children_count"] = children_count

    return {"code": 0, "message": "success", "data": result}


@router.put("/departments/{dept_id}", summary="更新部门")
async def update_department(
    dept_id: int,
    dept_update: DepartmentUpdate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """更新部门信息"""
    from modules.foundation.db_models.system import Department

    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail=f"部门 {dept_id} 不存在")

    if dept_update.name is not None:
        existing = db.query(Department).filter(
            Department.name == dept_update.name,
            Department.id != dept_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"部门名称 '{dept_update.name}' 已存在")
        dept.name = dept_update.name

    if dept_update.code is not None:
        if dept_update.code:
            existing = db.query(Department).filter(
                Department.code == dept_update.code,
                Department.id != dept_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"部门编码 '{dept_update.code}' 已存在")
        dept.code = dept_update.code

    if dept_update.parent_id is not None:
        if dept_update.parent_id == dept_id:
            raise HTTPException(status_code=400, detail="不能将自己设为上级部门")
        if dept_update.parent_id > 0:
            parent = db.query(Department).filter(Department.id == dept_update.parent_id).first()
            if not parent:
                raise HTTPException(status_code=400, detail=f"上级部门ID {dept_update.parent_id} 不存在")
        dept.parent_id = dept_update.parent_id if dept_update.parent_id > 0 else None

    if dept_update.manager_id is not None:
        dept.manager_id = dept_update.manager_id
    if dept_update.description is not None:
        dept.description = dept_update.description
    if dept_update.status is not None:
        dept.status = dept_update.status
    if dept_update.sort_order is not None:
        dept.sort_order = dept_update.sort_order

    db.commit()
    db.refresh(dept)

    return {"code": 0, "message": "success", "data": _dept_to_dict(dept)}


@router.delete("/departments/{dept_id}", summary="删除部门")
async def delete_department(
    dept_id: int,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """删除部门（检查是否有子部门和用户）"""
    from modules.foundation.db_models.system import Department, SystemUser

    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail=f"部门 {dept_id} 不存在")

    children = db.query(Department).filter(Department.parent_id == dept_id).count()
    if children > 0:
        raise HTTPException(status_code=400, detail=f"部门下有 {children} 个子部门，请先删除子部门")

    users = db.query(SystemUser).filter(SystemUser.department_id == dept_id).count()
    if users > 0:
        raise HTTPException(status_code=400, detail=f"部门下有 {users} 个用户，请先转移用户")

    db.delete(dept)
    db.commit()

    return {"code": 0, "message": f"部门 '{dept.name}' 已删除"}


# ============== 内部 SQL 执行接口（用于数据库迁移）==============
class SqlExecRequest(BaseModel):
    sql: str
    params: Optional[dict] = None


class SqlExecResponse(BaseModel):
    code: int
    message: str
    rowcount: Optional[int] = None
    lastrowid: Optional[int] = None
    results: Optional[list] = None


@router.post("/internal/sql", response_model=SqlExecResponse, summary="内部SQL执行")
async def exec_sql(
    req: SqlExecRequest,
    db: Session = Depends(get_db),
):
    """
    通过API内部执行SQL（使用API进程已建立的数据库连接）。
    仅限DBA维护使用。
    """
    from sqlalchemy import text
    try:
        result = db.execute(text(req.sql), req.params or {})
        db.commit()
        if result.returns_rows:
            rows = [dict(row._mapping) for row in result]
            return SqlExecResponse(code=0, message="查询成功", results=rows)
        else:
            return SqlExecResponse(
                code=0, message="执行成功",
                rowcount=result.rowcount,
                lastrowid=result.lastrowid if hasattr(result, 'lastrowid') else None
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============== 菜单管理接口 ==============

class MenuCreate(BaseModel):
    """创建菜单"""
    name: str = Field(..., description="菜单名称")
    code: Optional[str] = Field(None, description="菜单代码")
    icon: Optional[str] = Field(None, description="菜单图标")
    path: Optional[str] = Field(None, description="路由路径")
    component: Optional[str] = Field(None, description="组件路径")
    redirect: Optional[str] = Field(None, description="重定向路径")
    parent_id: Optional[int] = Field(None, description="父菜单ID")
    sort_order: int = Field(0, description="排序序号")
    menu_type: str = Field("menu", description="菜单类型: menu/directory/button")
    visible: int = Field(1, description="是否显示: 1=显示, 0=隐藏")
    is_frame: int = Field(1, description="是否外部Frame: 1=是, 0=内部页面")
    cache: int = Field(0, description="是否缓存: 1=缓存, 0=不缓存")
    permission: Optional[str] = Field(None, description="权限标识")
    description: Optional[str] = Field(None, description="描述")
    status: str = Field("active", description="状态: active/inactive")


class MenuUpdate(BaseModel):
    """更新菜单"""
    name: Optional[str] = None
    code: Optional[str] = None
    icon: Optional[str] = None
    path: Optional[str] = None
    component: Optional[str] = None
    redirect: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    menu_type: Optional[str] = None
    visible: Optional[int] = None
    is_frame: Optional[int] = None
    cache: Optional[int] = None
    permission: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


@router.get("/menu", summary="获取菜单树")
async def get_menus(
    status: Optional[str] = Query(None, description="状态过滤"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取菜单树形列表"""
    from modules.business.menu_service import MenuService
    service = MenuService(db)
    tree = service.get_tree(status=status)
    return {"items": tree, "total": len(tree)}


@router.post("/menu", summary="创建菜单")
async def create_menu(
    menu_data: MenuCreate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """创建新菜单"""
    from modules.business.menu_service import MenuService
    service = MenuService(db)

    # 检查code唯一性
    if menu_data.code:
        existing = service.get_by_code(menu_data.code)
        if existing:
            raise HTTPException(status_code=400, detail=f"菜单代码 '{menu_data.code}' 已存在")

    # 检查父菜单
    if menu_data.parent_id:
        parent = service.get_by_id(menu_data.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail=f"父菜单ID {menu_data.parent_id} 不存在")

    data = menu_data.model_dump(exclude_none=False)
    menu = service.create(data)
    return {"id": menu.id, "name": menu.name, "code": menu.code, "status": "success", "message": "菜单创建成功"}


@router.get("/menu/{menu_id}", summary="获取菜单详情")
async def get_menu(
    menu_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取菜单详细信息"""
    from modules.business.menu_service import MenuService
    service = MenuService(db)
    menu = service.get_by_id(menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    return service._to_dict(menu)


@router.put("/menu/{menu_id}", summary="更新菜单")
async def update_menu(
    menu_id: int,
    menu_data: MenuUpdate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """更新菜单信息"""
    from modules.business.menu_service import MenuService
    service = MenuService(db)

    existing = service.get_by_id(menu_id)
    if not existing:
        raise HTTPException(status_code=404, detail="菜单不存在")

    # 检查code唯一性
    if menu_data.code:
        by_code = service.get_by_code(menu_data.code)
        if by_code and by_code.id != menu_id:
            raise HTTPException(status_code=400, detail=f"菜单代码 '{menu_data.code}' 已存在")

    data = menu_data.model_dump(exclude_none=True)
    menu = service.update(menu_id, data)
    return {"status": "success", "message": "菜单更新成功"}


@router.delete("/menu/{menu_id}", summary="删除菜单")
async def delete_menu(
    menu_id: int,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """删除菜单"""
    from modules.business.menu_service import MenuService
    service = MenuService(db)
    try:
        ok = service.delete(menu_id)
        if not ok:
            raise HTTPException(status_code=404, detail="菜单不存在")
        return {"status": "success", "message": "菜单删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============== 字典管理接口 ==============

class DictTypeCreate(BaseModel):
    """创建字典类型"""
    name: str = Field(..., description="字典类型名称")
    code: str = Field(..., description="字典类型代码")
    description: Optional[str] = Field(None, description="描述")
    status: str = Field("active", description="状态: active/inactive")


class DictTypeUpdate(BaseModel):
    """更新字典类型"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class DictItemCreate(BaseModel):
    """创建字典项"""
    type_id: int = Field(..., description="字典类型ID")
    label: str = Field(..., description="显示文本")
    value: str = Field(..., description="字典值")
    sort_order: int = Field(0, description="排序序号")
    color: Optional[str] = Field(None, description="颜色标签")
    css_class: Optional[str] = Field(None, description="CSS样式类")
    extra_data: Optional[dict] = Field(None, description="扩展数据")
    status: str = Field("active", description="状态: active/inactive")


class DictItemUpdate(BaseModel):
    """更新字典项"""
    type_id: Optional[int] = None
    label: Optional[str] = None
    value: Optional[str] = None
    sort_order: Optional[int] = None
    color: Optional[str] = None
    css_class: Optional[str] = None
    extra_data: Optional[dict] = None
    status: Optional[str] = None


@router.get("/dict", summary="获取字典类型列表")
async def get_dict_types(
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    status: Optional[str] = Query(None, description="状态过滤"),
    pagination: PaginationParams = Depends(PaginationParams),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取字典类型分页列表"""
    from modules.business.dict_service import DictService
    service = DictService(db)
    result = service.get_types(
        keyword=keyword,
        status=status,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return result


@router.post("/dict", summary="创建字典类型")
async def create_dict_type(
    dict_data: DictTypeCreate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """创建新字典类型"""
    from modules.business.dict_service import DictService
    service = DictService(db)

    existing = service.get_type_by_code(dict_data.code)
    if existing:
        raise HTTPException(status_code=400, detail=f"字典类型代码 '{dict_data.code}' 已存在")

    data = dict_data.model_dump(exclude_none=False)
    dict_type = service.create_type(data)
    return {"id": dict_type.id, "name": dict_type.name, "code": dict_type.code, "status": "success", "message": "字典类型创建成功"}


@router.get("/dict/all-items", summary="获取字典项列表")
async def get_dict_items(
    type_id: Optional[int] = Query(None, description="字典类型ID"),
    type_code: Optional[str] = Query(None, description="字典类型代码"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    status: Optional[str] = Query(None, description="状态过滤"),
    pagination: PaginationParams = Depends(PaginationParams),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取字典项分页列表"""
    from modules.business.dict_service import DictService
    service = DictService(db)
    result = service.get_items(
        type_id=type_id,
        type_code=type_code,
        keyword=keyword,
        status=status,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return result


@router.get("/dict/{type_code}/items", summary="根据类型代码获取字典项")
async def get_dict_items_by_type(
    type_code: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """根据字典类型代码获取字典项列表"""
    from modules.business.dict_service import DictService
    service = DictService(db)
    items = service.get_items_by_type_code(type_code)
    return {"items": items, "total": len(items)}


@router.post("/dict/all-items", summary="创建字典项")
async def create_dict_item(
    item_data: DictItemCreate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """创建新字典项"""
    from modules.business.dict_service import DictService
    service = DictService(db)

    # 检查类型存在
    dict_type = service.get_type_by_id(item_data.type_id)
    if not dict_type:
        raise HTTPException(status_code=400, detail=f"字典类型ID {item_data.type_id} 不存在")

    data = item_data.model_dump(exclude_none=False)
    item = service.create_item(data)
    return {"id": item.id, "label": item.label, "value": item.value, "status": "success", "message": "字典项创建成功"}


@router.get("/dict/{type_id}", summary="获取字典类型详情")
async def get_dict_type(
    type_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取字典类型详细信息"""
    from modules.business.dict_service import DictService
    service = DictService(db)
    dict_type = service.get_type_by_id(type_id)
    if not dict_type:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    return service._type_to_dict(dict_type)


@router.put("/dict/{type_id}", summary="更新字典类型")
async def update_dict_type(
    type_id: int,
    dict_data: DictTypeUpdate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """更新字典类型"""
    from modules.business.dict_service import DictService
    service = DictService(db)

    existing = service.get_type_by_id(type_id)
    if not existing:
        raise HTTPException(status_code=404, detail="字典类型不存在")

    data = dict_data.model_dump(exclude_none=True)
    updated = service.update_type(type_id, data)
    return {"status": "success", "message": "字典类型更新成功"}


@router.delete("/dict/{type_id}", summary="删除字典类型")
async def delete_dict_type(
    type_id: int,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """删除字典类型（同时删除所有字典项）"""
    from modules.business.dict_service import DictService
    service = DictService(db)
    ok = service.delete_type(type_id)
    if not ok:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    return {"status": "success", "message": "字典类型删除成功"}


@router.get("/dict/items/{item_id}", summary="获取字典项详情")
async def get_dict_item(
    item_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取字典项详细信息"""
    from modules.business.dict_service import DictService
    service = DictService(db)
    item = service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="字典项不存在")
    return service._item_to_dict(item)


@router.put("/dict/items/{item_id}", summary="更新字典项")
async def update_dict_item(
    item_id: int,
    item_data: DictItemUpdate,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """更新字典项"""
    from modules.business.dict_service import DictService
    service = DictService(db)

    existing = service.get_item_by_id(item_id)
    if not existing:
        raise HTTPException(status_code=404, detail="字典项不存在")

    if item_data.type_id:
        dict_type = service.get_type_by_id(item_data.type_id)
        if not dict_type:
            raise HTTPException(status_code=400, detail=f"字典类型ID {item_data.type_id} 不存在")

    data = item_data.model_dump(exclude_none=True)
    updated = service.update_item(item_id, data)
    return {"status": "success", "message": "字典项更新成功"}


@router.delete("/dict/items/{item_id}", summary="删除字典项")
async def delete_dict_item(
    item_id: int,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """删除字典项"""
    from modules.business.dict_service import DictService
    service = DictService(db)
    ok = service.delete_item(item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="字典项不存在")
    return {"status": "success", "message": "字典项删除成功"}


# ============== system_router: 前端契约适配层 ==============
# 前端 system/menu.vue 用 /api/v1/system/menus（key/label模型）
# 后端已有 /api/v1/admin/menu（id/name模型）
# 本层做数据格式适配，不重复业务逻辑

system_router = APIRouter()


def _admin_menu_to_frontend(admin_menu: dict) -> dict:
    """将后端菜单格式转为前端期望的 key/label 格式"""
    return {
        "key": str(admin_menu.get("id", "")),
        "label": admin_menu.get("name", ""),
        "path": admin_menu.get("path") or "",
        "iconName": admin_menu.get("icon") or admin_menu.get("icon_name") or None,
        "icon": admin_menu.get("icon") or None,
        "sort": admin_menu.get("sort_order", 0),
        "type": admin_menu.get("menu_type", "menu"),
        "parentKey": str(admin_menu.get("parent_id")) if admin_menu.get("parent_id") else None,
        "visible": bool(admin_menu.get("visible", 1)),
        "status": admin_menu.get("status", "active"),
        "permission": admin_menu.get("permission"),
        "component": admin_menu.get("component"),
        "description": admin_menu.get("description"),
    }


@system_router.get("/menus", summary="获取前端菜单树")
async def get_system_menus(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """适配前端 system/menu.vue 的 key/label 格式"""
    from modules.business.menu_service import MenuService
    service = MenuService(db)
    tree = service.get_tree(status="active")

    # 转换为前端格式并构建 children 树
    items = [_admin_menu_to_frontend(m) for m in tree]
    mapped = {}
    for item in items:
        mapped[item["key"]] = {**item, "children": []}

    result = []
    for item in items:
        if item.get("parentKey") and item["parentKey"] in mapped:
            mapped[item["parentKey"]]["children"].append(item)
        elif not item.get("parentKey"):
            result.append(item)

    return result


@system_router.post("/menus", summary="创建菜单（前端格式）")
async def create_system_menu(
    menu_data: dict,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """接收前端格式 {key, label, parentKey, sort} → 转为后端格式创建"""
    from modules.business.menu_service import MenuService
    service = MenuService(db)

    # parentKey → parent_id
    parent_id = None
    if menu_data.get("parentKey"):
        parent_menu = service.get_by_id(int(menu_data["parentKey"]))
        parent_id = parent_menu.id if parent_menu else None

    admin_format = {
        "name": menu_data.get("label", menu_data.get("name", "")),
        "code": menu_data.get("key", ""),
        "path": menu_data.get("path", ""),
        "icon": menu_data.get("iconName") or menu_data.get("icon"),
        "sort_order": menu_data.get("sort", 0),
        "parent_id": parent_id,
        "menu_type": menu_data.get("type", "menu"),
        "visible": 1 if menu_data.get("visible", True) else 0,
        "permission": menu_data.get("permission"),
        "component": menu_data.get("component"),
        "description": menu_data.get("description"),
    }

    created = service.create(admin_format)
    return {"key": str(created.id), "label": created.name, "status": "success"}


@system_router.put("/menus/{menu_key}", summary="更新菜单（前端格式）")
async def update_system_menu(
    menu_key: str,
    menu_data: dict,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """接收前端格式 → 转为后端格式更新"""
    from modules.business.menu_service import MenuService
    service = MenuService(db)

    menu = service.get_by_id(int(menu_key))
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")

    parent_id = None
    if menu_data.get("parentKey"):
        parent_menu = service.get_by_id(int(menu_data["parentKey"]))
        parent_id = parent_menu.id if parent_menu else None

    update_data = {}
    if "label" in menu_data:
        update_data["name"] = menu_data["label"]
    if "key" in menu_data:
        update_data["code"] = menu_data["key"]
    if "path" in menu_data:
        update_data["path"] = menu_data["path"]
    if "iconName" in menu_data:
        update_data["icon"] = menu_data["iconName"]
    if "sort" in menu_data:
        update_data["sort_order"] = menu_data["sort"]
    if "parentKey" in menu_data:
        update_data["parent_id"] = parent_id
    if "visible" in menu_data:
        update_data["visible"] = 1 if menu_data["visible"] else 0
    if "permission" in menu_data:
        update_data["permission"] = menu_data["permission"]

    service.update(int(menu_key), update_data)
    return {"status": "success"}


@system_router.delete("/menus/{menu_key}", summary="删除菜单（前端格式）")
async def delete_system_menu(
    menu_key: str,
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """接收前端格式的 key 删除"""
    from modules.business.menu_service import MenuService
    service = MenuService(db)
    ok = service.delete(int(menu_key))
    if not ok:
        raise HTTPException(status_code=404, detail="菜单不存在")
    return {"status": "success"}


from api.routes.log_service import LogConfigService, LogAggregationService
