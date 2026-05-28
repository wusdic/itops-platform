"""
配置领域 - Pydantic Schemas
"""

from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ConfigCategory(str, Enum):
    """配置分类"""
    GENERAL = "general"
    SECURITY = "security"
    NETWORK = "network"
    DATABASE = "database"
    MONITORING = "monitoring"
    NOTIFICATION = "notification"
    AUTOMATION = "automation"
    INTEGRATION = "integration"


class ConfigDataType(str, Enum):
    """配置数据类型"""
    STRING = "string"
    INT = "int"
    BOOL = "bool"
    JSON = "json"
    LIST = "list"


# ========== 配置请求/响应模型 ==========

class CreateConfigRequest(BaseModel):
    key: str = Field(..., min_length=1, max_length=128, description="配置键")
    value: str = Field(default="", description="配置值")
    category: str = Field(default="general", description="配置分类")
    data_type: str = Field(default="string", description="数据类型")
    description: Optional[str] = Field(None, description="配置描述")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")


class UpdateConfigRequest(BaseModel):
    value: Optional[str] = Field(None, description="配置值")
    category: Optional[str] = Field(None, description="配置分类")
    data_type: Optional[str] = Field(None, description="数据类型")
    description: Optional[str] = Field(None, description="配置描述")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    change_summary: Optional[str] = Field(None, description="变更摘要")


class PublishConfigRequest(BaseModel):
    change_summary: Optional[str] = Field(None, description="发布说明")


class RollbackConfigRequest(BaseModel):
    target_version: Optional[int] = Field(None, description="回滚目标版本，默认回滚到上一版本")


class ConfigResponse(BaseModel):
    id: int
    key: str
    value: str
    category: str
    data_type: str
    description: str
    version: int
    is_published: bool
    is_locked: bool
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


class ConfigListItem(BaseModel):
    id: int
    key: str
    category: str
    data_type: str
    description: str
    version: int
    is_published: bool
    is_locked: bool
    updated_at: datetime

    class Config:
        from_attributes = True


class ConfigVersionResponse(BaseModel):
    id: int
    config_id: int
    version: int
    config_value: str
    change_summary: str
    change_type: str
    operator: Optional[str] = None
    operator_ip: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 凭证请求/响应模型 ==========

class CredentialType(str, Enum):
    """凭证类型"""
    PASSWORD = "password"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"
    TOKEN = "token"
    SSH_KEY = "ssh_key"


class CreateCredentialRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128, description="凭证名称")
    credential_type: str = Field(..., description="凭证类型")
    username: Optional[str] = Field(None, max_length=128, description="关联用户名")
    credential_value: str = Field(..., description="凭证值（将加密存储）")
    resource_type: Optional[str] = Field(None, description="关联资源类型")
    resource_id: Optional[str] = Field(None, description="关联资源ID")
    resource_name: Optional[str] = Field(None, max_length=256, description="关联资源名称")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    rotation_interval_days: Optional[int] = Field(None, ge=1, description="轮换周期（天）")
    allowed_ips: Optional[List[str]] = Field(default_factory=list, description="允许访问的IP列表")
    max_usage_count: int = Field(default=-1, ge=-1, description="最大使用次数，-1表示无限制")
    description: Optional[str] = Field(None, description="描述")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")


class UpdateCredentialRequest(BaseModel):
    name: Optional[str] = Field(None, description="凭证名称")
    credential_value: Optional[str] = Field(None, description="新凭证值（将加密存储）")
    resource_type: Optional[str] = Field(None, description="关联资源类型")
    resource_id: Optional[str] = Field(None, description="关联资源ID")
    resource_name: Optional[str] = Field(None, description="关联资源名称")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    rotation_interval_days: Optional[int] = Field(None, ge=1, description="轮换周期（天）")
    allowed_ips: Optional[List[str]] = Field(None, description="允许访问的IP列表")
    max_usage_count: Optional[int] = Field(None, ge=-1, description="最大使用次数")
    is_active: Optional[bool] = Field(None, description="是否启用")
    description: Optional[str] = Field(None, description="描述")
    tags: Optional[List[str]] = Field(None, description="标签列表")


class CredentialResponse(BaseModel):
    id: int
    name: str
    credential_type: str
    username: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    is_active: bool
    expires_at: Optional[datetime] = None
    last_rotated_at: Optional[datetime] = None
    rotation_interval_days: Optional[int] = None
    max_usage_count: int
    usage_count: int
    description: str
    tags: List[str]
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    last_used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CredentialListItem(BaseModel):
    id: int
    name: str
    credential_type: str
    username: Optional[str] = None
    resource_type: Optional[str] = None
    resource_name: Optional[str] = None
    is_active: bool
    expires_at: Optional[datetime] = None
    last_rotated_at: Optional[datetime] = None
    is_expired: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class CredentialValueResponse(BaseModel):
    """凭证值响应（解密后的值，仅在明确请求时返回）"""
    credential_value: str
    expires_at: Optional[datetime] = None
