"""状态中心 Schema"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class AssetStateSnapshotResponse(BaseModel):
    id: int
    asset_id: str
    state_type: str
    state_value: Optional[Dict[str, Any]] = None
    collection_status: str = "success"
    reached_at: datetime

    class Config:
        from_attributes = True


class AssetStateChangeResponse(BaseModel):
    id: int
    asset_id: str
    from_state: Optional[str] = None
    to_state: str
    changed_at: datetime
    reason: Optional[str] = None

    class Config:
        from_attributes = True
