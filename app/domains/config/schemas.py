"""
配置领域 - Pydantic Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field


class CreateConfigRequest(BaseModel):
    key: str = Field(..., min_length=1)
    value: str = ""
    category: str = "general"
    description: Optional[str] = None


class UpdateConfigRequest(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None


class ConfigResponse(BaseModel):
    id: int
    config_key: str
    config_value: str
    category: str
    description: str

    class Config:
        from_attributes = True
