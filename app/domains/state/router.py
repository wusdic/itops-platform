"""状态中心路由"""
from fastapi import APIRouter, Depends
from typing import Optional, List

from app.domains.state.service import StateService

router = APIRouter(prefix="/state", tags=["状态中心"])


@router.get("/assets/{asset_id}/state")
def get_asset_state(asset_id: str, state_type: Optional[str] = "health"):
    """获取资产最新状态"""
    state = StateService.get_latest_state(asset_id, state_type)
    return {"code": 0, "message": "success", "data": state}


@router.get("/assets/{asset_id}/state/history")
def get_state_history(asset_id: str, limit: int = 100):
    """获取状态变更历史"""
    history = StateService.get_state_history(asset_id, limit)
    return {"code": 0, "message": "success", "data": history}
