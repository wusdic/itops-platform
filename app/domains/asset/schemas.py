"""
资产领域 - Pydantic Schemas

定义资产相关的数据模型，对应 app/domains/asset/models.py。
文档依据: docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md §8.1
"""

from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict


# ============== IP 相关 ==============

class IPAddressBase(BaseModel):
    """IP地址基础模型"""
    ip_address: str = Field(..., description="IP地址")
    ip_type: str = Field(default='ipv4', description="ipv4/ipv6")
    mac_address: Optional[str] = Field(None, description="MAC地址")
    hostname: Optional[str] = Field(None, description="主机名")
    interface_name: Optional[str] = Field(None, description="网卡名称")
    interface_type: Optional[str] = Field(default='physical', description="网卡类型")
    is_management: bool = Field(default=False, description="是否管理接口")
    is_primary: bool = Field(default=False, description="是否主IP")
    is_public: bool = Field(default=False, description="是否公网IP")
    vlan_id: Optional[int] = Field(None, description="VLAN ID")
    subnet_mask: Optional[str] = Field(None, description="子网掩码")
    gateway: Optional[str] = Field(None, description="网关")


class CreateIPAddressRequest(IPAddressBase):
    """添加IP请求"""
    pass


# ============== 资产主表 ==============

class AssetBase(BaseModel):
    """资产基础模型"""
    name: str = Field(..., min_length=1, max_length=128, description="资产名称")
    asset_type: str = Field(..., description="资产类型: server/network/storage/security/middleware/database/app")
    sub_type: Optional[str] = Field(None, description="子类型")
    status: str = Field(default='active', description="状态: active/inactive/maintenance/decommissioned")
    hostname: Optional[str] = Field(None, max_length=128, description="主机名")
    ip_address: Optional[str] = Field(None, max_length=64, description="主IP地址")
    mac_address: Optional[str] = Field(None, max_length=64, description="主MAC地址")

    # 位置
    location: Optional[str] = Field(None, max_length=256, description="位置")
    idc: Optional[str] = Field(None, max_length=128, description="机房")
    building: Optional[str] = Field(None, max_length=64, description="楼宇")
    floor: Optional[str] = Field(None, max_length=32, description="楼层")
    rack: Optional[str] = Field(None, max_length=64, description="机柜")
    rack_position: Optional[str] = Field(None, max_length=32, description="机柜位置")

    # 厂商
    vendor: Optional[str] = Field(None, max_length=128, description="厂商")
    model: Optional[str] = Field(None, max_length=128, description="型号")
    serial_number: Optional[str] = Field(None, max_length=128, description="序列号")
    manufacturer: Optional[str] = Field(None, max_length=128, description="制造商")
    purchase_date: Optional[date] = Field(None, description="采购日期")
    warranty_end: Optional[date] = Field(None, description="保修结束")
    cost: Optional[float] = Field(None, description="成本")

    # 系统
    os_type: Optional[str] = Field(None, max_length=64, description="操作系统类型")
    os_version: Optional[str] = Field(None, max_length=128, description="操作系统版本")
    kernel_version: Optional[str] = Field(None, max_length=128, description="内核版本")
    cpu: Optional[str] = Field(None, max_length=128, description="CPU信息")
    memory: Optional[str] = Field(None, max_length=64, description="内存")
    disk: Optional[str] = Field(None, max_length=256, description="磁盘")

    # 管理接口
    ssh_port: int = Field(default=22, description="SSH端口")
    ssh_username: Optional[str] = Field(None, max_length=64, description="SSH用户名")
    web_url: Optional[str] = Field(None, max_length=256, description="Web管理URL")

    # 元数据
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")
    custom_fields: Optional[dict] = Field(default_factory=dict, description="自定义字段")

    # 业务关联
    business_id: Optional[int] = Field(None, description="业务系统ID")
    business_name: Optional[str] = Field(None, max_length=128, description="业务系统名称")
    group_id: Optional[int] = Field(None, description="资产组ID")

    # 责任人
    owner: Optional[str] = Field(None, max_length=64, description="责任人")
    owner_email: Optional[str] = Field(None, max_length=128, description="责任人邮箱")

    # 备注
    remark: Optional[str] = Field(None, description="备注")


class CreateAssetRequest(AssetBase):
    """创建资产请求"""
    created_by: Optional[str] = Field(None, max_length=64, description="创建人")
    model_config = ConfigDict(str_strip_whitespace=True)


class UpdateAssetRequest(BaseModel):
    """更新资产请求（全部字段可选）"""
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    asset_type: Optional[str] = None
    sub_type: Optional[str] = None
    status: Optional[str] = None
    hostname: Optional[str] = Field(None, max_length=128)
    ip_address: Optional[str] = Field(None, max_length=64)
    mac_address: Optional[str] = Field(None, max_length=64)
    location: Optional[str] = Field(None, max_length=256)
    idc: Optional[str] = Field(None, max_length=128)
    building: Optional[str] = Field(None, max_length=64)
    floor: Optional[str] = Field(None, max_length=32)
    rack: Optional[str] = Field(None, max_length=64)
    rack_position: Optional[str] = Field(None, max_length=32)
    vendor: Optional[str] = Field(None, max_length=128)
    model: Optional[str] = Field(None, max_length=128)
    serial_number: Optional[str] = Field(None, max_length=128)
    manufacturer: Optional[str] = Field(None, max_length=128)
    purchase_date: Optional[date] = None
    warranty_end: Optional[date] = None
    cost: Optional[float] = None
    os_type: Optional[str] = Field(None, max_length=64)
    os_version: Optional[str] = Field(None, max_length=128)
    kernel_version: Optional[str] = Field(None, max_length=128)
    cpu: Optional[str] = Field(None, max_length=128)
    memory: Optional[str] = Field(None, max_length=64)
    disk: Optional[str] = Field(None, max_length=256)
    ssh_port: Optional[int] = None
    ssh_username: Optional[str] = Field(None, max_length=64)
    web_url: Optional[str] = Field(None, max_length=256)
    tags: Optional[List[str]] = None
    custom_fields: Optional[dict] = None
    business_id: Optional[int] = None
    business_name: Optional[str] = Field(None, max_length=128)
    group_id: Optional[int] = None
    owner: Optional[str] = Field(None, max_length=64)
    owner_email: Optional[str] = Field(None, max_length=128)
    remark: Optional[str] = None


# ============== 资产响应 ==============

class AssetResponse(AssetBase):
    """资产响应模型"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: str
    first_discovered_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    tenant_id: Optional[str] = None


# ============== 资产关系 ==============

class CreateRelationRequest(BaseModel):
    """创建资产关系请求"""
    target_asset_id: int = Field(..., description="目标资产ID")
    relation_type: str = Field(..., description="关系类型: network/depends_on/contains/runs_on/connects_to")
    relation_label: Optional[str] = Field(None, description="关系标签")
    bidirectional: bool = Field(default=False, description="是否双向关系")
    metadata: Optional[dict] = Field(None, description="扩展属性")


# ============== 分组 ==============

class CreateGroupRequest(BaseModel):
    """创建分组请求"""
    group_name: str = Field(..., min_length=1, max_length=128, description="分组名称")
    parent_id: Optional[int] = Field(None, description="父分组ID")
    group_type: Optional[str] = Field(None, description="分组类型: idc/business/role/custom")
    description: Optional[str] = Field(None, description="描述")
    display_order: int = Field(default=0, description="排序")
    is_public: bool = Field(default=True, description="是否公开")


# ============== 标签 ==============

class CreateTagRequest(BaseModel):
    """创建标签请求"""
    tag_key: str = Field(..., min_length=1, max_length=64, description="标签键")
    tag_value: Optional[str] = Field(None, max_length=256, description="标签值")
    tag_color: str = Field(default='#1890ff', description="标签颜色")
    tag_category: Optional[str] = Field(None, description="标签分类: env/role/owner/business")
    description: Optional[str] = Field(None, description="描述")


# ============== 业务系统 ==============

class CreateBusinessSystemRequest(BaseModel):
    """创建业务系统请求"""
    name: str = Field(..., min_length=1, max_length=128, description="系统名称")
    code: Optional[str] = Field(None, max_length=64, description="系统代码")
    description: Optional[str] = Field(None, description="描述")
    sla_level: Optional[str] = Field(None, description="SLA级别")
    availability_target: Optional[float] = Field(None, description="可用性目标(%)")
    owner: Optional[str] = Field(None, max_length=64, description="负责人")
    owner_email: Optional[str] = Field(None, max_length=128, description="负责人邮箱")
