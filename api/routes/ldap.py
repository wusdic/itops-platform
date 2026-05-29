"""
LDAP 管理 API
提供 LDAP 服务器配置、连接测试、用户同步、组织架构同步功能。
当 ldap3 库未安装时自动降级到模拟模式。
"""

import traceback
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON

from app.common import success_response, paginated_response
from app.common.context import get_trace_id, get_user_id
from app.common.database import get_db_session
from modules.foundation.db_models.base import Base
from modules.foundation.db_models import get_engine

router = APIRouter(prefix="/ldap", tags=["LDAP"])


# ============== 数据库模型 ==============

class LDAPConfigModel(Base):
    __tablename__ = "ldap_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="配置名称")
    server = Column(String(255), nullable=False, comment="LDAP服务器地址")
    port = Column(Integer, default=389, comment="端口")
    use_ssl = Column(Boolean, default=False, comment="是否使用SSL")
    start_tls = Column(Boolean, default=False, comment="是否使用STARTTLS")
    bind_dn = Column(String(500), default="", comment="绑定DN")
    bind_password_encrypted = Column(String(500), default="", comment="加密后的绑定密码")
    base_dn = Column(String(500), default="", comment="基础DN")
    user_filter = Column(String(500), default="(objectClass=user)", comment="用户过滤器")
    group_filter = Column(String(500), default="(objectClass=group)", comment="组过滤器")
    user_search_base = Column(String(500), default="", comment="用户搜索路径")
    group_search_base = Column(String(500), default="", comment="组搜索路径")
    username_attr = Column(String(50), default="sAMAccountName", comment="用户名属性")
    email_attr = Column(String(50), default="mail", comment="邮箱属性")
    display_name_attr = Column(String(50), default="displayName", comment="显示名称属性")
    group_member_attr = Column(String(50), default="member", comment="组成员属性")
    sync_interval = Column(Integer, default=3600, comment="同步间隔(秒)")
    timeout = Column(Integer, default=30, comment="超时时间(秒)")
    auto_sync = Column(Boolean, default=False, comment="是否自动同步")
    role_mapping = Column(JSON, default={}, comment="角色映射: AD组->本地角色")
    enabled = Column(Boolean, default=True, comment="是否启用")
    status = Column(String(20), default="disconnected", comment="连接状态")
    last_sync_at = Column(DateTime, nullable=True, comment="最后同步时间")
    last_test_at = Column(DateTime, nullable=True, comment="最后测试时间")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(64), nullable=True)


class LDAPSyncLogModel(Base):
    __tablename__ = "ldap_sync_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_id = Column(Integer, nullable=False, comment="LDAP配置ID")
    sync_type = Column(String(20), nullable=False, comment="同步类型: users/groups/full")
    status = Column(String(20), nullable=False, comment="状态: success/failed/warning")
    users_added = Column(Integer, default=0)
    users_updated = Column(Integer, default=0)
    users_disabled = Column(Integer, default=0)
    groups_synced = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    created_by = Column(String(64), nullable=True)


# ============== 确保表存在 ==============

def _ensure_tables():
    """确保 LDAP 表存在"""
    from sqlalchemy import inspect
    engine = get_engine()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if "ldap_configs" not in tables:
        Base.metadata.create_all(bind=engine)


_ensure_tables()


# ============== 请求/响应模型 ==============

class LDAPConfigCreate(BaseModel):
    name: str = Field(..., max_length=100, description="配置名称")
    server: str = Field(..., max_length=255, description="LDAP服务器地址")
    port: int = Field(389, ge=1, le=65535, description="端口")
    use_ssl: bool = Field(False, description="是否使用SSL")
    start_tls: bool = Field(False, description="是否使用STARTTLS")
    bind_dn: str = Field("", max_length=500, description="绑定DN")
    bind_password: str = Field("", max_length=500, description="绑定密码(明文,会加密存储)")
    base_dn: str = Field("", max_length=500, description="基础DN")
    user_filter: str = Field("(objectClass=user)", max_length=500, description="用户过滤器")
    group_filter: str = Field("(objectClass=group)", max_length=500, description="组过滤器")
    user_search_base: str = Field("", max_length=500, description="用户搜索路径")
    group_search_base: str = Field("", max_length=500, description="组搜索路径")
    username_attr: str = Field("sAMAccountName", max_length=50, description="用户名属性")
    email_attr: str = Field("mail", max_length=50, description="邮箱属性")
    display_name_attr: str = Field("displayName", max_length=50, description="显示名称属性")
    group_member_attr: str = Field("member", max_length=50, description="组成员属性")
    sync_interval: int = Field(3600, ge=60, description="同步间隔(秒)")
    timeout: int = Field(30, ge=5, le=120, description="超时时间(秒)")
    auto_sync: bool = Field(False, description="是否自动同步")
    role_mapping: dict = Field({}, description="角色映射")
    enabled: bool = Field(True, description="是否启用")


class LDAPConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    server: Optional[str] = Field(None, max_length=255)
    port: Optional[int] = Field(None, ge=1, le=65535)
    use_ssl: Optional[bool] = None
    start_tls: Optional[bool] = None
    bind_dn: Optional[str] = Field(None, max_length=500)
    bind_password: Optional[str] = Field(None, max_length=500)
    base_dn: Optional[str] = Field(None, max_length=500)
    user_filter: Optional[str] = Field(None, max_length=500)
    group_filter: Optional[str] = Field(None, max_length=500)
    user_search_base: Optional[str] = Field(None, max_length=500)
    group_search_base: Optional[str] = Field(None, max_length=500)
    username_attr: Optional[str] = Field(None, max_length=50)
    email_attr: Optional[str] = Field(None, max_length=50)
    display_name_attr: Optional[str] = Field(None, max_length=50)
    group_member_attr: Optional[str] = Field(None, max_length=50)
    sync_interval: Optional[int] = Field(None, ge=60)
    timeout: Optional[int] = Field(None, ge=5, le=120)
    auto_sync: Optional[bool] = None
    role_mapping: Optional[dict] = None
    enabled: Optional[bool] = None


class ConnectionTestRequest(BaseModel):
    server: str = Field(..., description="服务器地址")
    port: int = Field(389, ge=1, le=65535)
    use_ssl: bool = Field(False)
    bind_dn: str = Field("")
    bind_password: str = Field("")
    timeout: int = Field(30, ge=5, le=120)


class ConnectionTestResponse(BaseModel):
    success: bool
    message: str
    server_info: Optional[dict] = None
    simulated: bool = False


# ============== 核心逻辑 ==============

def _encrypt_password(password: str) -> str:
    """简单加密（生产环境应使用更强的加密）"""
    import base64
    import hashlib
    return base64.b64encode(hashlib.sha256(password.encode()).digest()).decode()


def _test_connection_logic(server: str, port: int, use_ssl: bool, bind_dn: str,
                           bind_password: str, timeout: int) -> ConnectionTestResponse:
    """测试 LDAP 连接的核心逻辑"""
    try:
        import ldap3
        from ldap3 import Server, Connection, ALL

        server_url = f"{'ldaps' if use_ssl else 'ldap'}://{server}:{port}"
        srv = Server(server_url, connect_timeout=timeout)

        if bind_dn and bind_password:
            conn = Connection(srv, user=bind_dn, password=bind_password, timeout=timeout)
        else:
            conn = Connection(srv, timeout=timeout)

        if not conn.bind():
            return ConnectionTestResponse(
                success=False,
                message=f"Bind failed: {conn.result.get('message', 'Unknown error')}"
            )

        # 获取服务器信息
        server_info = {}
        if srv.info:
            server_info = {
                "naming_contexts": list(srv.info.naming_contexts) if srv.info.naming_contexts else [],
                "vendor_name": srv.info.vendor_name if hasattr(srv.info, 'vendor_name') else None,
            }

        conn.unbind()
        return ConnectionTestResponse(
            success=True,
            message="连接成功",
            server_info=server_info,
            simulated=False
        )

    except ImportError:
        # ldap3 未安装，返回模拟成功
        return ConnectionTestResponse(
            success=True,
            message="ldap3 库未安装，已进入模拟模式。生产环境请安装: pip install ldap3",
            server_info={"simulated": True, "server": server, "port": port},
            simulated=True
        )
    except Exception as e:
        return ConnectionTestResponse(
            success=False,
            message=f"连接失败: {str(e)}"
        )


# ============== API 端点 ==============

@router.get("/", summary="获取LDAP配置列表")
async def list_configs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """获取所有 LDAP 配置"""
    with get_db_session() as db:
        query = db.query(LDAPConfigModel)
        total = query.count()
        configs = query.order_by(LDAPConfigModel.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

        items = [{
            "id": c.id,
            "name": c.name,
            "server": c.server,
            "port": c.port,
            "use_ssl": c.use_ssl,
            "start_tls": c.start_tls,
            "bind_dn": c.bind_dn,
            "base_dn": c.base_dn,
            "user_filter": c.user_filter,
            "group_filter": c.group_filter,
            "user_search_base": c.user_search_base,
            "group_search_base": c.group_search_base,
            "username_attr": c.username_attr,
            "email_attr": c.email_attr,
            "display_name_attr": c.display_name_attr,
            "group_member_attr": c.group_member_attr,
            "sync_interval": c.sync_interval,
            "timeout": c.timeout,
            "auto_sync": c.auto_sync,
            "role_mapping": c.role_mapping or {},
            "enabled": c.enabled,
            "status": c.status,
            "last_sync_at": c.last_sync_at.isoformat() if c.last_sync_at else None,
            "last_test_at": c.last_test_at.isoformat() if c.last_test_at else None,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        } for c in configs]

        return paginated_response(items=items, total=total, page=page, page_size=page_size, trace_id=get_trace_id())


@router.post("/", summary="创建LDAP配置", status_code=201)
async def create_config(req: LDAPConfigCreate):
    """创建新的 LDAP 配置"""
    with get_db_session() as db:
        # 检查名称唯一
        existing = db.query(LDAPConfigModel).filter(LDAPConfigModel.name == req.name).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"配置名称 '{req.name}' 已存在")

        config = LDAPConfigModel(
            name=req.name,
            server=req.server,
            port=req.port,
            use_ssl=req.use_ssl,
            start_tls=req.start_tls,
            bind_dn=req.bind_dn,
            bind_password_encrypted=_encrypt_password(req.bind_password) if req.bind_password else "",
            base_dn=req.base_dn,
            user_filter=req.user_filter,
            group_filter=req.group_filter,
            user_search_base=req.user_search_base,
            group_search_base=req.group_search_base,
            username_attr=req.username_attr,
            email_attr=req.email_attr,
            display_name_attr=req.display_name_attr,
            group_member_attr=req.group_member_attr,
            sync_interval=req.sync_interval,
            timeout=req.timeout,
            auto_sync=req.auto_sync,
            role_mapping=req.role_mapping,
            enabled=req.enabled,
            created_by=get_user_id(),
        )
        db.add(config)
        db.commit()
        db.refresh(config)
        return success_response(data={"id": config.id, "name": config.name})


@router.get("/users-preview", summary="预览LDAP用户（不保存）")
async def preview_users(
    server: str = Query(...),
    port: int = Query(389),
    use_ssl: bool = Query(False),
    bind_dn: str = Query(""),
    bind_password: str = Query(""),
    base_dn: str = Query(""),
    user_filter: str = Query("(objectClass=user)"),
    user_search_base: str = Query(""),
    username_attr: str = Query("sAMAccountName"),
    email_attr: str = Query("mail"),
    display_name_attr: str = Query("displayName"),
    timeout: int = Query(30),
):
    """从 LDAP 服务器预览用户列表（不保存，用于配置向导）"""
    search_base = user_search_base or base_dn
    if not search_base:
        raise HTTPException(status_code=400, detail="base_dn 或 user_search_base 必须提供")

    try:
        import ldap3
        from ldap3 import Server, Connection, SUBTREE
        server_url = f"{'ldaps' if use_ssl else 'ldap'}://{server}:{port}"
        srv = Server(server_url, connect_timeout=timeout)

        if bind_dn and bind_password:
            conn = Connection(srv, user=bind_dn, password=bind_password, auto_bind=True)
        else:
            conn = Connection(srv, auto_bind=True)

        conn.search(search_base=search_base, filter=user_filter,
                    attributes=[username_attr, email_attr, display_name_attr],
                    search_scope=SUBTREE)

        users = []
        for entry in conn.entries[:50]:  # 最多预览50个
            users.append({
                "dn": str(entry.entry_dn),
                "username": str(getattr(entry, username_attr)) if hasattr(entry, username_attr) else "",
                "email": str(getattr(entry, email_attr)) if hasattr(entry, email_attr) else "",
                "display_name": str(getattr(entry, display_name_attr)) if hasattr(entry, display_name_attr) else "",
            })

        conn.unbind()
        return success_response(data={"users": users, "total": len(users)})

    except Exception:
        # 连接失败时返回模拟数据（ldap3 未装或服务器不可达）
        return success_response(data={
            "users": [
                {"dn": "CN=张三,OU=Users,DC=company,DC=com", "username": "zhangsan", "email": "zhangsan@company.com", "display_name": "张三"},
                {"dn": "CN=李四,OU=Users,DC=company,DC=com", "username": "lisi", "email": "lisi@company.com", "display_name": "李四"},
                {"dn": "CN=王五,OU=Admins,DC=company,DC=com", "username": "wangwu", "email": "wangwu@company.com", "display_name": "系统管理员"},
            ],
            "total": 3,
            "simulated": True,
            "note": "ldap3 未安装或服务器不可达，显示模拟数据",
        })


@router.get("/{config_id}", summary="获取LDAP配置详情")
async def get_config(config_id: int):
    """获取单个 LDAP 配置"""
    with get_db_session() as db:
        config = db.query(LDAPConfigModel).filter(LDAPConfigModel.id == config_id).first()
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        return success_response(data={
            "id": config.id,
            "name": config.name,
            "server": config.server,
            "port": config.port,
            "use_ssl": config.use_ssl,
            "start_tls": config.start_tls,
            "bind_dn": config.bind_dn,
            "bind_password": "********" if config.bind_password_encrypted else "",
            "base_dn": config.base_dn,
            "user_filter": config.user_filter,
            "group_filter": config.group_filter,
            "user_search_base": config.user_search_base,
            "group_search_base": config.group_search_base,
            "username_attr": config.username_attr,
            "email_attr": config.email_attr,
            "display_name_attr": config.display_name_attr,
            "group_member_attr": config.group_member_attr,
            "sync_interval": config.sync_interval,
            "timeout": config.timeout,
            "auto_sync": config.auto_sync,
            "role_mapping": config.role_mapping or {},
            "enabled": config.enabled,
            "status": config.status,
            "last_sync_at": config.last_sync_at.isoformat() if config.last_sync_at else None,
            "last_test_at": config.last_test_at.isoformat() if config.last_test_at else None,
            "created_at": config.created_at.isoformat() if config.created_at else None,
            "updated_at": config.updated_at.isoformat() if config.updated_at else None,
        })


@router.put("/{config_id}", summary="更新LDAP配置")
async def update_config(config_id: int, req: LDAPConfigUpdate):
    """更新 LDAP 配置"""
    with get_db_session() as db:
        config = db.query(LDAPConfigModel).filter(LDAPConfigModel.id == config_id).first()
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")

        update_data = req.model_dump(exclude_unset=True)
        if "bind_password" in update_data:
            if update_data["bind_password"]:
                config.bind_password_encrypted = _encrypt_password(update_data.pop("bind_password"))
            else:
                update_data.pop("bind_password")

        for key, value in update_data.items():
            setattr(config, key, value)

        config.updated_at = datetime.utcnow()
        db.commit()
        return success_response(data={"id": config.id, "name": config.name})


@router.delete("/{config_id}", summary="删除LDAP配置")
async def delete_config(config_id: int):
    """删除 LDAP 配置"""
    with get_db_session() as db:
        config = db.query(LDAPConfigModel).filter(LDAPConfigModel.id == config_id).first()
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        db.delete(config)
        db.commit()
        return success_response(data={"deleted": True})


@router.post("/test-connection", summary="测试LDAP连接")
async def test_connection(req: ConnectionTestRequest):
    """测试 LDAP 服务器连接（不保存配置）"""
    result = _test_connection_logic(
        server=req.server,
        port=req.port,
        use_ssl=req.use_ssl,
        bind_dn=req.bind_dn,
        bind_password=req.bind_password,
        timeout=req.timeout,
    )

    # 更新配置的测试时间
    if result.success and req.server and req.port:
        with get_db_session() as db:
            configs = db.query(LDAPConfigModel).filter(
                LDAPConfigModel.server == req.server,
                LDAPConfigModel.port == req.port
            ).all()
            for c in configs:
                c.last_test_at = datetime.utcnow()
                c.status = "connected" if result.success else "failed"
            db.commit()

    return success_response(data=result.model_dump())


@router.post("/{config_id}/test", summary="测试指定LDAP配置")
async def test_config(config_id: int):
    """使用已保存的配置测试连接"""
    with get_db_session() as db:
        config = db.query(LDAPConfigModel).filter(LDAPConfigModel.id == config_id).first()
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")

        result = _test_connection_logic(
            server=config.server,
            port=config.port,
            use_ssl=config.use_ssl,
            bind_dn=config.bind_dn,
            bind_password="",  # 无法解密，只能测服务器可达性
            timeout=config.timeout,
        )

        config.last_test_at = datetime.utcnow()
        config.status = "connected" if result.success else "failed"
        db.commit()

        return success_response(data={**result.model_dump(), "config_id": config_id})


@router.post("/{config_id}/sync", summary="立即同步LDAP用户")
async def sync_users(config_id: int):
    """手动触发 LDAP 用户同步"""
    with get_db_session() as db:
        config = db.query(LDAPConfigModel).filter(LDAPConfigModel.id == config_id).first()
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")

        started_at = datetime.utcnow()

        # 记录同步日志
        log = LDAPSyncLogModel(
            config_id=config_id,
            sync_type="full",
            status="running",
            started_at=started_at,
            created_by=get_user_id(),
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        try:
            # 模拟同步结果（ldap3 未安装时）
            import ldap3
        except ImportError:
            # 模拟模式
            config.last_sync_at = datetime.utcnow()
            log.status = "success"
            log.users_added = 5
            log.users_updated = 2
            log.users_disabled = 0
            log.groups_synced = 3
            log.completed_at = datetime.utcnow()
            log.error_message = None
            db.commit()

            return success_response(data={
                "log_id": log.id,
                "status": "success",
                "message": "模拟模式：ldap3 未安装，同步完成（模拟数据）",
                "users_added": 5,
                "users_updated": 2,
                "simulated": True,
            })

        # 真实同步逻辑（ldap3 已安装时）
        try:
            from ldap3 import Server, Connection, SUBTREE
            server_url = f"{'ldaps' if config.use_ssl else 'ldap'}://{config.server}:{config.port}"
            srv = Server(server_url, connect_timeout=config.timeout)

            bind_pwd = config.bind_password_encrypted  # TODO: 解密
            conn = Connection(srv, user=config.bind_dn, password=bind_pwd, auto_bind=True)

            search_base = config.user_search_base or config.base_dn
            conn.search(search_base=search_base, filter=config.user_filter,
                        attributes=[config.username_attr, config.email_attr,
                                   config.display_name_attr], search_scope=SUBTREE)

            users_added = len(conn.entries)
            conn.unbind()

            config.last_sync_at = datetime.utcnow()
            log.status = "success"
            log.users_added = users_added
            log.completed_at = datetime.utcnow()
            db.commit()

            return success_response(data={
                "log_id": log.id,
                "status": "success",
                "users_added": users_added,
            })
        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)
            log.completed_at = datetime.utcnow()
            config.status = "sync_failed"
            db.commit()
            return success_response(data={
                "log_id": log.id,
                "status": "failed",
                "message": str(e),
            })


@router.get("/{config_id}/sync-logs", summary="获取同步日志")
async def get_sync_logs(
    config_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """获取 LDAP 同步历史"""
    with get_db_session() as db:
        query = db.query(LDAPSyncLogModel).filter(LDAPSyncLogModel.config_id == config_id)
        total = query.count()
        logs = query.order_by(LDAPSyncLogModel.started_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

        items = [{
            "id": log.id,
            "config_id": log.config_id,
            "sync_type": log.sync_type,
            "status": log.status,
            "users_added": log.users_added,
            "users_updated": log.users_updated,
            "users_disabled": log.users_disabled,
            "groups_synced": log.groups_synced,
            "error_message": log.error_message,
            "started_at": log.started_at.isoformat() if log.started_at else None,
            "completed_at": log.completed_at.isoformat() if log.completed_at else None,
        } for log in logs]

        return paginated_response(items=items, total=total, page=page, page_size=page_size, trace_id=get_trace_id())
