"""
配置领域 - API 路由

提供配置管理和凭证管理 API，支持：
- 配置 CRUD 操作
- 配置版本管理和发布流程
- 凭证安全存储（加密）和轮换
"""

import json
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, status, Header

from app.common import (
    success_response,
    error_response,
    paginated_response,
    get_http_status,
    ErrorCode,
    get_trace_id,
    get_username,
)
from app.common.database import get_db_session
from app.domains.config.service import ConfigService, CredentialService
from app.domains.config.schemas import (
    CreateConfigRequest,
    UpdateConfigRequest,
    PublishConfigRequest,
    RollbackConfigRequest,
    CreateCredentialRequest,
    UpdateCredentialRequest,
)

router = APIRouter(tags=["配置与凭证管理"])

# ========== 配置管理 API ==========


@router.get("/configs")
async def list_configs(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    x_tenant_id: Optional[str] = Header(None),
):
    """获取配置列表"""
    with get_db_session() as db:
        svc = ConfigService(db)
        items, total = svc.list_configs(
            page=page,
            page_size=page_size,
            category=category,
            keyword=keyword,
            tenant_id=x_tenant_id,
        )
        return paginated_response(
            items=[{
                "id": i.id,
                "key": i.config_key,
                "category": i.category,
                "data_type": i.data_type,
                "description": i.description,
                "version": i.version,
                "is_published": i.isPublished,
                "is_locked": i.isLocked,
                "updated_at": i.updated_at.isoformat() if i.updated_at else None,
            } for i in items],
            total=total,
            page=page,
            page_size=page_size,
            trace_id=get_trace_id(),
        )


@router.get("/configs/{config_id}")
async def get_config(
    request: Request,
    config_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """获取单个配置"""
    with get_db_session() as db:
        svc = ConfigService(db)
        cfg = svc.get_config(config_id, tenant_id=x_tenant_id)
        if not cfg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Config not found",
            )
        return success_response(
            data={
                "id": cfg.id,
                "key": cfg.config_key,
                "value": cfg.config_value,
                "category": cfg.category,
                "data_type": cfg.data_type,
                "description": cfg.description,
                "version": cfg.version,
                "is_published": cfg.isPublished,
                "is_locked": cfg.isLocked,
                "tags": json.loads(cfg.tags) if cfg.tags else [],
                "created_at": cfg.created_at.isoformat() if cfg.created_at else None,
                "updated_at": cfg.updated_at.isoformat() if cfg.updated_at else None,
                "created_by": cfg.created_by,
                "updated_by": cfg.updated_by,
            },
            trace_id=get_trace_id(),
        )


@router.post("/configs")
async def create_config(
    request: Request,
    x_tenant_id: Optional[str] = Header(None),
):
    """创建配置"""
    with get_db_session() as db:
        body = await request.json()
        req = CreateConfigRequest(**body)
        svc = ConfigService(db)
        try:
            operator = get_username()
            cfg = svc.create_config(req, operator=operator, tenant_id=x_tenant_id)
            return success_response(
                data={
                    "id": cfg.id,
                    "key": cfg.config_key,
                    "version": cfg.version,
                },
                trace_id=get_trace_id(),
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )


@router.put("/configs/{config_id}")
async def update_config(
    request: Request,
    config_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """更新配置"""
    with get_db_session() as db:
        body = await request.json()
        req = UpdateConfigRequest(**body)
        svc = ConfigService(db)
        try:
            operator = get_username()
            operator_ip = request.client.host if request.client else None
            cfg = svc.update_config(
                config_id, req,
                operator=operator,
                operator_ip=operator_ip,
                tenant_id=x_tenant_id,
            )
            return success_response(
                data={"id": cfg.id, "version": cfg.version},
                trace_id=get_trace_id(),
            )
        except ValueError as e:
            if "not found" in str(e).lower():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
            if "locked" in str(e).lower():
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/configs/{config_id}")
async def delete_config(
    request: Request,
    config_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """删除配置"""
    with get_db_session() as db:
        svc = ConfigService(db)
        try:
            ok = svc.delete_config(config_id, tenant_id=x_tenant_id)
            if not ok:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
            return success_response(message="Config deleted", trace_id=get_trace_id())
        except ValueError as e:
            if "locked" in str(e).lower():
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/configs/{config_id}/publish")
async def publish_config(
    request: Request,
    config_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """发布配置"""
    try:
        body = await request.json() if request.method == "POST" else {}
    except Exception:
        body = {}
    with get_db_session() as db:
        svc = ConfigService(db)
        try:
            operator = get_username()
            operator_ip = request.client.host if request.client else None
            cfg = svc.publish_config(
                config_id,
                operator=operator,
                operator_ip=operator_ip,
                tenant_id=x_tenant_id,
            )
            return success_response(
                data={"id": cfg.id, "version": cfg.version, "is_published": cfg.isPublished},
                trace_id=get_trace_id(),
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/configs/{config_id}/rollback")
async def rollback_config(
    request: Request,
    config_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """回滚配置"""
    try:
        body = await request.json() if request.method == "POST" else {}
    except Exception:
        body = {}
    target_version = body.get("target_version")
    with get_db_session() as db:
        svc = ConfigService(db)
        try:
            operator = get_username()
            operator_ip = request.client.host if request.client else None
            cfg = svc.rollback_config(
                config_id,
                target_version=target_version,
                operator=operator,
                operator_ip=operator_ip,
                tenant_id=x_tenant_id,
            )
            return success_response(
                data={"id": cfg.id, "version": cfg.version},
                trace_id=get_trace_id(),
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/configs/{config_id}/lock")
async def lock_config(
    request: Request,
    config_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """锁定配置"""
    with get_db_session() as db:
        svc = ConfigService(db)
        try:
            operator = get_username()
            cfg = svc.lock_config(config_id, operator=operator, tenant_id=x_tenant_id)
            return success_response(data={"id": cfg.id, "is_locked": cfg.isLocked}, trace_id=get_trace_id())
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/configs/{config_id}/unlock")
async def unlock_config(
    request: Request,
    config_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """解锁配置"""
    with get_db_session() as db:
        svc = ConfigService(db)
        try:
            cfg = svc.unlock_config(config_id, tenant_id=x_tenant_id)
            return success_response(data={"id": cfg.id, "is_locked": cfg.isLocked}, trace_id=get_trace_id())
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/configs/{config_id}/versions")
async def get_config_versions(
    request: Request,
    config_id: int,
    page: int = 1,
    page_size: int = 20,
    x_tenant_id: Optional[str] = Header(None),
):
    """获取配置版本历史"""
    with get_db_session() as db:
        svc = ConfigService(db)
        # 先检查配置是否存在
        cfg = svc.get_config(config_id, tenant_id=x_tenant_id)
        if not cfg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
        items, total = svc.get_config_versions(config_id, page=page, page_size=page_size)
        return paginated_response(
            items=[{
                "id": i.id,
                "config_id": i.config_id,
                "version": i.version,
                "config_value": i.config_value,
                "change_summary": i.change_summary,
                "change_type": i.change_type,
                "operator": i.operator,
                "operator_ip": i.operator_ip,
                "approved_by": i.approved_by,
                "approved_at": i.approved_at.isoformat() if i.approved_at else None,
                "created_at": i.created_at.isoformat() if i.created_at else None,
            } for i in items],
            total=total,
            page=page,
            page_size=page_size,
            trace_id=get_trace_id(),
        )


# ========== 凭证管理 API ==========


@router.get("/credentials")
async def list_credentials(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    credential_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    keyword: Optional[str] = None,
    is_active: Optional[bool] = None,
    x_tenant_id: Optional[str] = Header(None),
):
    """获取凭证列表（不返回敏感值）"""
    with get_db_session() as db:
        svc = CredentialService(db)
        items, total = svc.list_credentials(
            page=page,
            page_size=page_size,
            credential_type=credential_type,
            resource_type=resource_type,
            resource_id=resource_id,
            keyword=keyword,
            is_active=is_active,
            tenant_id=x_tenant_id,
        )
        from datetime import datetime
        return paginated_response(
            items=[{
                "id": i.id,
                "name": i.name,
                "credential_type": i.credential_type,
                "username": i.username,
                "resource_type": i.resource_type,
                "resource_id": i.resource_id,
                "resource_name": i.resource_name,
                "is_active": i.is_active,
                "expires_at": i.expires_at.isoformat() if i.expires_at else None,
                "last_rotated_at": i.last_rotated_at.isoformat() if i.last_rotated_at else None,
                "rotation_interval_days": i.rotation_interval_days,
                "max_usage_count": i.max_usage_count,
                "usage_count": i.usage_count,
                "description": i.description,
                "tags": json.loads(i.tags) if i.tags else [],
                "created_at": i.created_at.isoformat() if i.created_at else None,
            } for i in items],
            total=total,
            page=page,
            page_size=page_size,
            trace_id=get_trace_id(),
        )


@router.get("/credentials/{credential_id}")
async def get_credential(
    request: Request,
    credential_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """获取单个凭证（不返回敏感值）"""
    with get_db_session() as db:
        svc = CredentialService(db)
        cred = svc.get_credential(credential_id, tenant_id=x_tenant_id)
        if not cred:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")
        return success_response(
            data={
                "id": cred.id,
                "name": cred.name,
                "credential_type": cred.credential_type,
                "username": cred.username,
                "resource_type": cred.resource_type,
                "resource_id": cred.resource_id,
                "resource_name": cred.resource_name,
                "is_active": cred.is_active,
                "expires_at": cred.expires_at.isoformat() if cred.expires_at else None,
                "last_rotated_at": cred.last_rotated_at.isoformat() if cred.last_rotated_at else None,
                "rotation_interval_days": cred.rotation_interval_days,
                "max_usage_count": cred.max_usage_count,
                "usage_count": cred.usage_count,
                "description": cred.description,
                "tags": json.loads(cred.tags) if cred.tags else [],
                "created_by": cred.created_by,
                "updated_by": cred.updated_by,
                "last_used_at": cred.last_used_at.isoformat() if cred.last_used_at else None,
                "created_at": cred.created_at.isoformat() if cred.created_at else None,
                "updated_at": cred.updated_at.isoformat() if cred.updated_at else None,
            },
            trace_id=get_trace_id(),
        )


@router.post("/credentials")
async def create_credential(
    request: Request,
    x_tenant_id: Optional[str] = Header(None),
):
    """创建凭证"""
    with get_db_session() as db:
        body = await request.json()
        req = CreateCredentialRequest(**body)
        svc = CredentialService(db)
        try:
            operator = get_username()
            cred = svc.create_credential(req, operator=operator, tenant_id=x_tenant_id)
            return success_response(
                data={"id": cred.id, "name": cred.name, "credential_type": cred.credential_type},
                trace_id=get_trace_id(),
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/credentials/{credential_id}")
async def update_credential(
    request: Request,
    credential_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """更新凭证"""
    with get_db_session() as db:
        body = await request.json()
        req = UpdateCredentialRequest(**body)
        svc = CredentialService(db)
        try:
            operator = get_username()
            cred = svc.update_credential(credential_id, req, operator=operator, tenant_id=x_tenant_id)
            return success_response(data={"id": cred.id}, trace_id=get_trace_id())
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/credentials/{credential_id}")
async def delete_credential(
    request: Request,
    credential_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """删除凭证"""
    with get_db_session() as db:
        svc = CredentialService(db)
        ok = svc.delete_credential(credential_id, tenant_id=x_tenant_id)
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")
        return success_response(message="Credential deleted", trace_id=get_trace_id())


@router.get("/credentials/{credential_id}/value")
async def get_credential_value(
    request: Request,
    credential_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """获取凭证解密后的值（敏感操作）"""
    with get_db_session() as db:
        svc = CredentialService(db)
        try:
            operator = get_username()
            value = svc.get_credential_value(credential_id, operator=operator, tenant_id=x_tenant_id)
            return success_response(data={"credential_value": value}, trace_id=get_trace_id())
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/credentials/{credential_id}/rotate")
async def rotate_credential(
    request: Request,
    credential_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """轮换凭证"""
    body = await request.json()
    new_value = body.get("new_value")
    if not new_value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="new_value is required")
    with get_db_session() as db:
        svc = CredentialService(db)
        try:
            operator = get_username()
            cred = svc.rotate_credential(credential_id, new_value, operator=operator, tenant_id=x_tenant_id)
            return success_response(
                data={"id": cred.id, "last_rotated_at": cred.last_rotated_at.isoformat() if cred.last_rotated_at else None},
                trace_id=get_trace_id(),
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/credentials/{credential_id}/validate")
async def validate_credential(
    request: Request,
    credential_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """验证凭证值"""
    body = await request.json()
    value = body.get("value")
    if not value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="value is required")
    with get_db_session() as db:
        svc = CredentialService(db)
        is_valid = svc.validate_credential(credential_id, value)
        return success_response(data={"valid": is_valid}, trace_id=get_trace_id())


@router.get("/resources/{resource_type}/{resource_id}/credentials")
async def get_resource_credentials(
    request: Request,
    resource_type: str,
    resource_id: str,
    x_tenant_id: Optional[str] = Header(None),
):
    """获取指定资源的所有凭证"""
    with get_db_session() as db:
        svc = CredentialService(db)
        creds = svc.get_credentials_by_resource(resource_type, resource_id, tenant_id=x_tenant_id)
        return success_response(
            data=[{
                "id": c.id,
                "name": c.name,
                "credential_type": c.credential_type,
                "username": c.username,
                "is_active": c.is_active,
                "expires_at": c.expires_at.isoformat() if c.expires_at else None,
            } for c in creds],
            trace_id=get_trace_id(),
        )
