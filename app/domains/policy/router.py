"""策略中心路由"""
from fastapi import APIRouter, Query
from typing import Optional

from app.domains.policy.service import PolicyService
from app.domains.policy.schemas import PolicyCreate

router = APIRouter(prefix="/policies", tags=["策略中心"])


@router.post("")
def create_policy(policy: PolicyCreate):
    """创建策略"""
    policy_id = PolicyService.create_policy(policy.model_dump())
    return {"code": 0, "message": "success", "data": {"policy_id": policy_id}}


@router.get("")
def list_policies(status: Optional[str] = Query(None), limit: int = Query(100, le=200)):
    """列出策略"""
    policies = PolicyService.list_policies(status, limit)
    return {"code": 0, "message": "success", "data": policies}


@router.get("/match/{trigger_type}")
def match_policies(trigger_type: str, asset_id: Optional[str] = Query(None)):
    """匹配适用的策略"""
    policies = PolicyService.match_policies(trigger_type, asset_id)
    return {"code": 0, "message": "success", "data": policies}
