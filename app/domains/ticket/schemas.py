"""工单中心 Schema"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class TicketCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    source_type: Optional[str] = None
    source_id: Optional[str] = None
    assigned_to: Optional[str] = None


class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    review: Optional[str] = None


class TicketResponse(BaseModel):
    id: int
    ticket_id: str
    title: str
    priority: str
    status: str
    source_type: Optional[str] = None
    assigned_to: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
