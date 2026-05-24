"""
租户管理 API 路由 (P2-23 多租户隔离)
提供租户的 CRUD、用户分配、配额管理等接口
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.dependencies import get_db, get_current_user, CurrentUser
from modules.foundation.db_models.system import Tenant, TenantConfig, SystemUser
from modules.foundation.db_models.tenant import set_tenant_context, TenantContextManager

router = APIRouter(prefix="/tenants", tags=["租户管理"])


# ============== 请求/响应模型 ==============

class TenantCreate(BaseModel):
    """创建租户"""
    name: str = Field(..., max_length=128, description="租户名称")
    code: str = Field(..., max_length=64, description="租户代码（唯一）")
    plan: str = Field("basic", description="套餐: basic/standard/premium/enterprise")
    contact_name: Optional[str] = Field(None, description="联系人姓名")
    contact_email: Optional[str] = Field(None, description="联系人邮箱")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    max_devices: int = Field(100, description="最大设备数")
    max_users: int = Field(20, description="最大用户数")
    max_storage_gb: int = Field(50, description="最大存储GB")
    expires_at: Optional[datetime] = Field(None, description="过期时间")


class TenantUpdate(BaseModel):
    """更新租户"""
    name: Optional[str] = None
    code: Optional[str] = None
    status: Optional[str] = Field(None, description="active/suspended/trial")
    plan: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    max_devices: Optional[int] = None
    max_users: Optional[int] = None
    max_storage_gb: Optional[int] = None
    expires_at: Optional[datetime] = None


class TenantUserAssign(BaseModel):
    """分配用户到租户"""
    user_id: str = Field(..., description="用户ID")
    tenant_id: str = Field(..., description="租户ID")


# ============== 租户 CRUD ==============

@router.get("", summary="获取租户列表")
async def list_tenants(
    status: Optional[str] = Query(None, description="状态过滤"),
    plan: Optional[str] = Query(None, description="套餐过滤"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取租户列表（超级管理员专用）"""
    # 检查超级管理员权限
    if "super_admin" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="需要超级管理员权限")

    query = db.query(Tenant)
    if status:
        query = query.filter(Tenant.status == status)
    if plan:
        query = query.filter(Tenant.plan == plan)

    total = query.count()
    items = query.order_by(Tenant.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [_t_to_dict(t) for t in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("", summary="创建租户")
async def create_tenant(
    tenant: TenantCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建新租户（超级管理员专用）"""
    if "super_admin" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="需要超级管理员权限")

    # 检查 code 唯一性
    existing = db.query(Tenant).filter(Tenant.code == tenant.code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"租户代码 {tenant.code} 已存在")

    # 生成租户 ID
    tenant_id = f"t{datetime.now().strftime('%Y%m%d')}{abs(hash(tenant.code)) % 10000:04d}"

    db_tenant = Tenant(
        id=tenant_id,
        name=tenant.name,
        code=tenant.code,
        plan=tenant.plan,
        contact_name=tenant.contact_name,
        contact_email=tenant.contact_email,
        contact_phone=tenant.contact_phone,
        max_devices=tenant.max_devices,
        max_users=tenant.max_users,
        max_storage_gb=tenant.max_storage_gb,
        expires_at=tenant.expires_at,
        status="active",
    )
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)

    return {"tenant": _t_to_dict(db_tenant), "message": "租户创建成功"}


@router.get("/{tenant_id}", summary="获取租户详情")
async def get_tenant(
    tenant_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取指定租户详情"""
    # 租户用户只能查看自己的租户
    if "super_admin" not in current_user.roles and "admin" not in current_user.roles and current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="无权访问该租户")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")

    # 统计该租户的用户数和设备数
    user_count = db.query(SystemUser).filter(SystemUser.tenant_id == tenant_id).count()

    result = _t_to_dict(tenant)
    result["user_count"] = user_count
    return result


@router.put("/{tenant_id}", summary="更新租户")
async def update_tenant(
    tenant_id: str,
    updates: TenantUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新租户信息（超级管理员专用）"""
    if "super_admin" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="需要超级管理员权限")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")

    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tenant, key, value)

    db.commit()
    db.refresh(tenant)
    return {"tenant": _t_to_dict(tenant), "message": "更新成功"}


@router.delete("/{tenant_id}", summary="删除租户")
async def delete_tenant(
    tenant_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除租户（管理员可用）"""
    if "super_admin" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="需要管理员或超级管理员权限")

    if tenant_id == "t0001":  # 保护默认租户
        raise HTTPException(status_code=400, detail="不能删除系统默认租户")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")

    # 检查是否还有用户
    user_count = db.query(SystemUser).filter(SystemUser.tenant_id == tenant_id).count()
    if user_count > 0:
        raise HTTPException(status_code=400, detail=f"该租户下还有 {user_count} 个用户，请先迁移或删除")

    db.delete(tenant)
    db.commit()
    return {"message": "删除成功"}


# ============== 租户用户管理 ==============

@router.get("/{tenant_id}/users", summary="获取租户下的用户列表")
async def list_tenant_users(
    tenant_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取指定租户下的所有用户"""
    if "super_admin" not in current_user.roles and "admin" not in current_user.roles and current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="无权访问该租户")

    query = db.query(SystemUser).filter(SystemUser.tenant_id == tenant_id)
    total = query.count()
    users = query.order_by(SystemUser.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [{"id": u.id, "username": u.username, "email": u.email, "status": u.status, "roles": u.roles} for u in users],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/{tenant_id}/users", summary="将用户分配到租户")
async def assign_user_to_tenant(
    tenant_id: str,
    assignment: TenantUserAssign,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """将已有用户分配到指定租户"""
    if "super_admin" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    # 验证租户存在
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")

    # 验证用户存在
    user = db.query(SystemUser).filter(SystemUser.id == assignment.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 检查配额
    current_users = db.query(SystemUser).filter(SystemUser.tenant_id == tenant_id).count()
    if current_users >= tenant.max_users:
        raise HTTPException(status_code=400, detail=f"租户用户配额已达上限（{tenant.max_users}）")

    user.tenant_id = tenant_id
    db.commit()

    return {"message": f"用户 {user.username} 已分配到租户 {tenant.name}"}


@router.delete("/{tenant_id}/users/{user_id}", summary="将用户从租户移除")
async def remove_user_from_tenant(
    tenant_id: str,
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """将用户从租户移除（不会删除用户）"""
    if "super_admin" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    user = db.query(SystemUser).filter(SystemUser.id == user_id, SystemUser.tenant_id == tenant_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不在该租户下")

    user.tenant_id = None
    db.commit()
    return {"message": f"用户 {user.username} 已从租户移除"}


# ============== 租户配额 ==============

@router.get("/{tenant_id}/quota", summary="获取租户配额使用情况")
async def get_tenant_quota(
    tenant_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取租户配额使用情况"""
    if "super_admin" not in current_user.roles and "admin" not in current_user.roles and current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="无权访问该租户")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="租户不存在")

    user_count = db.query(SystemUser).filter(SystemUser.tenant_id == tenant_id).count()
    # 设备数量需要从 device 表统计，这里返回 0 表示未实现
    device_count = 0

    return {
        "tenant_id": tenant_id,
        "tenant_name": tenant.name,
        "plan": tenant.plan,
        "quota": {
            "max_devices": tenant.max_devices,
            "max_users": tenant.max_users,
            "max_storage_gb": tenant.max_storage_gb,
        },
        "usage": {
            "devices": device_count,
            "users": user_count,
            "storage_gb": 0,
        },
        "utilization": {
            "devices_pct": round(device_count / tenant.max_devices * 100, 1) if tenant.max_devices > 0 else 0,
            "users_pct": round(user_count / tenant.max_users * 100, 1) if tenant.max_users > 0 else 0,
        },
    }


# ============== 辅助函数 ==============

def _t_to_dict(t: Tenant) -> dict:
    return {
        "id": t.id,
        "name": t.name,
        "code": t.code,
        "status": t.status,
        "plan": t.plan,
        "contact_name": t.contact_name,
        "contact_email": t.contact_email,
        "contact_phone": t.contact_phone,
        "max_devices": t.max_devices,
        "max_users": t.max_users,
        "max_storage_gb": t.max_storage_gb,
        "expires_at": t.expires_at.isoformat() if t.expires_at else None,
        "is_master": bool(t.is_master),
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
    }
