"""治理中心路由"""
from fastapi import APIRouter, Query

from app.domains.governance.service import GovernanceService

router = APIRouter(prefix="/governance", tags=["治理中心"])


@router.get("/users/{user_id}/permissions")
def get_user_permissions(user_id: str):
    """获取用户权限"""
    permissions = GovernanceService.get_user_permissions(user_id)
    return {"code": 0, "message": "success", "data": permissions}


@router.post("/users/{user_id}/permissions")
def grant_permission(user_id: str, resource: str, action: str):
    """授予权限"""
    ok = GovernanceService.grant_permission(user_id, resource, action)
    return {"code": 0 if ok else 1, "message": "success" if ok else "failed"}
