"""
自动化领域 - Pydantic Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field


class CreateScriptRequest(BaseModel):
    name: str = Field(..., min_length=1)
    script_type: str = "shell"
    content: str = ""
    description: Optional[str] = None


class UpdateScriptRequest(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None


class ScriptResponse(BaseModel):
    id: int
    name: str
    script_type: str
    description: str

    class Config:
        from_attributes = True
