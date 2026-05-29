"""日志中心 Schema"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class ExecutionLogResponse(BaseModel):
    id: int
    execution_id: str
    step_name: Optional[str] = None
    level: str
    message: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: int
    action: str
    resource: str
    resource_id: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
