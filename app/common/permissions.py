"""
权限校验装饰器

提供基于角色的权限校验装饰器：
- @require_permission(resource, action)
- @require_role(role_name)
"""

import functools
from typing import List, Optional, Callable

from fastapi import HTTPException, status
from starlette.requests import Request


class Permission:
    """权限定义"""
    # 资源
    ASSET = "asset"
    CONFIG = "config"
    COLLECTOR = "collector"
    STATE = "state"
    EVENT = "event"
    ALERT = "alert"
    LOG = "log"
    POLICY = "policy"
    AUTOMATION = "automation"
    AIOPS = "aiops"
    TICKET = "ticket"
    KNOWLEDGE = "knowledge"
    SYSTEM = "system"
    USER = "user"
    ROLE = "role"

    # 操作
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    ADMIN = "admin"


class RBAC:
    """角色权限映射"""

    ROLE_PERMISSIONS = {
        "admin": ["*"],  # 管理员拥有所有权限
        "operator": [
            "asset.create", "asset.read", "asset.update",
            "config.read", "config.update",
            "collector.read", "collector.execute",
            "state.read",
            "event.read", "event.update",
            "alert.read", "alert.update",
            "log.read",
            "policy.read",
            "automation.create", "automation.read", "automation.update", "automation.execute",
            "ticket.create", "ticket.read", "ticket.update",
            "knowledge.read", "knowledge.create",
        ],
        "readonly": [
            "asset.read",
            "config.read",
            "collector.read",
            "state.read",
            "event.read",
            "alert.read",
            "log.read",
            "policy.read",
            "automation.read",
            "ticket.read",
            "knowledge.read",
        ],
    }

    @classmethod
    def has_permission(cls, role: str, resource: str, action: str) -> bool:
        """检查角色是否有指定资源的操作权限"""
        perms = cls.ROLE_PERMISSIONS.get(role, [])
        if "*" in perms:
            return True
        return f"{resource}.{action}" in perms

    @classmethod
    def get_user_permissions(cls, role: str) -> List[str]:
        """获取角色的所有权限"""
        return cls.ROLE_PERMISSIONS.get(role, [])


def get_user_role(request: Request) -> str:
    """从请求中获取用户角色"""
    # 优先从 request.state 获取（已由 auth 中间件设置）
    if hasattr(request.state, "user_role"):
        return request.state.user_role
    # 备用：从 request.state.user 推断
    if hasattr(request.state, "user"):
        return getattr(request.state.user, "role", "readonly")
    return "readonly"


def require_permission(resource: str, action: str) -> Callable:
    """
    权限校验装饰器

    用法:
        @router.get("/assets")
        @require_permission("asset", "read")
        async def list_assets(request: Request):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            role = get_user_role(request)
            if not RBAC.has_permission(role, resource, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {resource}.{action}"
                )
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_role(role_name: str) -> Callable:
    """
    角色校验装饰器

    用法:
        @router.get("/admin")
        @require_role("admin")
        async def admin_only(request: Request):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            role = get_user_role(request)
            if role != role_name and role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: {role_name}"
                )
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
