"""治理中心 Schema"""
from pydantic import BaseModel
from typing import Optional, List


class RoleResponse(BaseModel):
    id: int
    role_id: str
    role_name: str
    description: Optional[str] = None
    permissions: Optional[List[str]] = None

    class Config:
        from_attributes = True
