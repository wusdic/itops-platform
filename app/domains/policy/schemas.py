"""策略中心 Schema"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class PolicyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_source: str = "event"
    trigger_type: str
    condition: Optional[Dict[str, Any]] = None
    scope: Optional[Dict[str, Any]] = None
    risk_level: str = "medium"
    require_approval: int = 0
    actions: Optional[List[Dict[str, Any]]] = None
    verification: Optional[Dict[str, Any]] = None


class PolicyResponse(BaseModel):
    id: int
    policy_id: str
    name: str
    description: Optional[str] = None
    trigger_source: str
    trigger_type: str
    risk_level: str
    require_approval: int
    version: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
