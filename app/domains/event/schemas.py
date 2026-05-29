"""事件中心 Schema"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class EventCreate(BaseModel):
    event_type: str
    source: str = "system"
    asset_id: Optional[str] = None
    severity: str = "info"
    payload: Optional[Dict[str, Any]] = None
    correlation_key: Optional[str] = None


class EventResponse(BaseModel):
    id: int
    event_id: str
    event_type: str
    source: Optional[str] = None
    asset_id: Optional[str] = None
    severity: str
    timestamp: datetime
    payload: Optional[Dict[str, Any]] = None
    correlation_key: Optional[str] = None
    status: str

    class Config:
        from_attributes = True
