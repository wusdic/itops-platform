"""
资产领域 - Pydantic Schemas

定义资产相关的数据模型。
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class DeviceBase(BaseModel):
    """设备基础模型"""
    name: str
    device_type: str
    ip_address: Optional[str] = None
    status: str = "UNKNOWN"
    tags: Optional[List[str]] = []


class CreateAssetRequest(BaseModel):
    """创建资产请求"""
    name: str = Field(..., min_length=1, max_length=255)
    device_type: str
    ip_address: Optional[str] = None
    status: str = "UNKNOWN"
    tags: Optional[List[str]] = []
    metadata: Optional[dict] = {}


class UpdateAssetRequest(BaseModel):
    """更新资产请求"""
    name: Optional[str] = None
    device_type: Optional[str] = None
    ip_address: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class AssetResponse(BaseModel):
    """资产响应"""
    id: int
    name: str
    device_type: str
    ip_address: Optional[str]
    status: str
    tags: List[str]
    metadata: dict
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
