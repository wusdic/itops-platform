"""
资产领域 - Pydantic Schemas

定义资产相关的数据模型，对齐 modules.foundation.db_models.device.Device 模型。
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class DeviceBase(BaseModel):
    """设备基础模型"""
    name: str = Field(..., min_length=1, max_length=128, description="设备名称")
    hostname: Optional[str] = Field(None, max_length=128, description="主机名")
    device_type: str = Field(..., description="设备类型")
    ip_address: Optional[str] = Field(None, max_length=64, description="IP地址")
    status: str = Field(default="unknown", description="设备状态")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")
    location: Optional[str] = Field(None, max_length=256, description="位置")
    idc: Optional[str] = Field(None, max_length=128, description="机房")
    rack: Optional[str] = Field(None, max_length=64, description="机柜")
    rack_position: Optional[str] = Field(None, max_length=32, description="机柜位置")
    vendor: Optional[str] = Field(None, max_length=128, description="厂商")
    model: Optional[str] = Field(None, max_length=128, description="型号")
    manufacturer: Optional[str] = Field(None, max_length=128, description="制造商")
    serial_number: Optional[str] = Field(None, max_length=128, description="序列号")
    os_type: Optional[str] = Field(None, max_length=64, description="操作系统类型")
    os_version: Optional[str] = Field(None, max_length=64, description="操作系统版本")
    cpu: Optional[str] = Field(None, max_length=128, description="CPU信息")
    memory: Optional[str] = Field(None, max_length=64, description="内存信息")
    disk: Optional[str] = Field(None, max_length=128, description="磁盘信息")
    owner: Optional[str] = Field(None, max_length=64, description="责任人")
    owner_email: Optional[str] = Field(None, max_length=128, description="责任人邮箱")
    remark: Optional[str] = Field(None, description="备注")


class CreateDeviceRequest(DeviceBase):
    """创建设备请求"""
    mac_address: Optional[str] = Field(None, max_length=64, description="MAC地址")
    monitor_enabled: bool = Field(default=True, description="是否启用监控")
    snmp_enabled: bool = Field(default=True, description="是否启用SNMP")
    snmp_community: Optional[str] = Field(None, max_length=64, description="SNMP Community")
    ssh_port: int = Field(default=22, description="SSH端口")
    business_id: Optional[int] = Field(None, description="业务系统ID")
    group_id: Optional[int] = Field(None, description="设备组ID")
    metadata: Optional[dict] = Field(default_factory=dict, description="元数据")


class UpdateDeviceRequest(BaseModel):
    """更新设备请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    hostname: Optional[str] = Field(None, max_length=128)
    device_type: Optional[str] = None
    ip_address: Optional[str] = Field(None, max_length=64)
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    location: Optional[str] = Field(None, max_length=256)
    idc: Optional[str] = Field(None, max_length=128)
    rack: Optional[str] = Field(None, max_length=64)
    rack_position: Optional[str] = Field(None, max_length=32)
    vendor: Optional[str] = Field(None, max_length=128)
    model: Optional[str] = Field(None, max_length=128)
    manufacturer: Optional[str] = Field(None, max_length=128)
    serial_number: Optional[str] = Field(None, max_length=128)
    os_type: Optional[str] = Field(None, max_length=64)
    os_version: Optional[str] = Field(None, max_length=64)
    cpu: Optional[str] = Field(None, max_length=128)
    memory: Optional[str] = Field(None, max_length=64)
    disk: Optional[str] = Field(None, max_length=128)
    owner: Optional[str] = Field(None, max_length=64)
    owner_email: Optional[str] = Field(None, max_length=128)
    remark: Optional[str] = None
    mac_address: Optional[str] = Field(None, max_length=64)
    monitor_enabled: Optional[bool] = None
    snmp_enabled: Optional[bool] = None
    snmp_community: Optional[str] = Field(None, max_length=64)
    ssh_port: Optional[int] = None
    business_id: Optional[int] = None
    group_id: Optional[int] = None


class DeviceResponse(DeviceBase):
    """设备响应"""
    id: int
    mac_address: Optional[str] = None
    monitor_enabled: bool = True
    snmp_enabled: bool = True
    snmp_community: Optional[str] = None
    ssh_port: int = 22
    business_id: Optional[int] = None
    business_name: Optional[str] = None
    group_id: Optional[int] = None
    group_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DeviceListResponse(BaseModel):
    """设备列表响应（简化版）"""
    id: int
    name: str
    device_type: str
    ip_address: Optional[str] = None
    status: str
    tags: List[str] = Field(default_factory=list)
    vendor: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    idc: Optional[str] = None
    owner: Optional[str] = None
    monitor_enabled: bool = True
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ========== 设备分组 ==========

class DeviceGroupBase(BaseModel):
    """设备分组基础模型"""
    name: str = Field(..., min_length=1, max_length=128, description="分组名称")
    parent_id: Optional[int] = Field(None, description="父分组ID")
    description: Optional[str] = Field(None, max_length=256, description="描述")
    is_public: bool = Field(default=True, description="是否公开")


class CreateDeviceGroupRequest(DeviceGroupBase):
    """创建设备分组请求"""
    pass


class UpdateDeviceGroupRequest(BaseModel):
    """更新设备分组请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    parent_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=256)
    is_public: Optional[bool] = None


class DeviceGroupResponse(DeviceGroupBase):
    """设备分组响应"""
    id: int
    device_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ========== 业务系统 ==========

class BusinessSystemBase(BaseModel):
    """业务系统基础模型"""
    name: str = Field(..., min_length=1, max_length=128, description="系统名称")
    code: Optional[str] = Field(None, max_length=64, description="系统代码")
    description: Optional[str] = Field(None, max_length=512, description="描述")
    sla_level: Optional[str] = Field(None, max_length=32, description="SLA级别")
    availability_target: Optional[float] = Field(99.9, description="可用性目标(%)")
    owner: Optional[str] = Field(None, max_length=64, description="负责人")
    owner_email: Optional[str] = Field(None, max_length=128, description="负责人邮箱")
    status: str = Field(default="active", description="状态")


class CreateBusinessSystemRequest(BusinessSystemBase):
    """创建业务系统请求"""
    pass


class UpdateBusinessSystemRequest(BaseModel):
    """更新业务系统请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    code: Optional[str] = Field(None, max_length=64)
    description: Optional[str] = Field(None, max_length=512)
    sla_level: Optional[str] = Field(None, max_length=32)
    availability_target: Optional[float] = None
    owner: Optional[str] = Field(None, max_length=64)
    owner_email: Optional[str] = Field(None, max_length=128)
    status: Optional[str] = None


class BusinessSystemResponse(BusinessSystemBase):
    """业务系统响应"""
    id: int
    device_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ========== 设备统计 ==========

class DeviceStatsResponse(BaseModel):
    """设备统计响应"""
    total: int = 0
    online: int = 0
    offline: int = 0
    warning: int = 0
    critical: int = 0
    maintenance: int = 0
    unknown: int = 0
    by_type: dict = Field(default_factory=dict)
    by_vendor: dict = Field(default_factory=dict)
    by_idc: dict = Field(default_factory=dict)


# ========== 标签管理 ==========

class TagInfo(BaseModel):
    """标签信息"""
    name: str
    count: int = 0
    devices: List[int] = Field(default_factory=list)


class TagUpdateRequest(BaseModel):
    """标签更新请求"""
    tags: List[str] = Field(..., description="标签列表")


# ========== 设备关联 ==========

class DeviceBindingRequest(BaseModel):
    """设备关联请求"""
    group_id: Optional[int] = Field(None, description="设备组ID")
    business_id: Optional[int] = Field(None, description="业务系统ID")
    tags: Optional[List[str]] = Field(None, description="标签列表")
