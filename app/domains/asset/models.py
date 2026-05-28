"""
资产中心 - SQLAlchemy Models

对应数据库迁移脚本: scripts/migration/013_asset_center.sql
文档依据: docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md §8.1
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Boolean, 
    ForeignKey, JSON, DECIMAL, Date, Index
)
from sqlalchemy.orm import relationship
from modules.foundation.db_models.base import Base


class Asset(Base):
    """
    资产主表

    平台所有可观测、可配置、可告警、可执行对象的统一账本。
    替代旧的 devices 表。
    """
    __tablename__ = 'assets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(String(64), unique=True, nullable=False, comment='业务ID，如 AST-000001')
    name = Column(String(128), nullable=False, comment='资产名称')
    asset_type = Column(String(64), nullable=False, comment='类型: server/network/storage/security/middleware/database/app')
    sub_type = Column(String(64), comment='子类型')

    status = Column(String(32), default='active', comment='状态: active/inactive/maintenance/decommissioned')

    # 位置
    idc = Column(String(128), comment='机房')
    building = Column(String(64), comment='楼宇')
    floor = Column(String(32), comment='楼层')
    rack = Column(String(64), comment='机柜')
    rack_position = Column(String(32), comment='机柜位置')

    # 厂商
    vendor = Column(String(128), comment='厂商')
    model = Column(String(128), comment='型号')
    serial_number = Column(String(128), comment='序列号')
    manufacturer = Column(String(128), comment='制造商')
    purchase_date = Column(Date, comment='采购日期')
    warranty_end = Column(Date, comment='保修结束')
    cost = Column(DECIMAL(12, 2), comment='成本')

    # 操作系统/软件
    os_type = Column(String(64), comment='操作系统类型')
    os_version = Column(String(128), comment='操作系统版本')
    kernel_version = Column(String(128), comment='内核版本')
    cpu = Column(String(128), comment='CPU信息')
    memory = Column(String(64), comment='内存')
    disk = Column(String(256), comment='磁盘')
    network_interfaces = Column(JSON, comment='网络接口列表')

    # 管理接口
    ssh_port = Column(Integer, default=22, comment='SSH端口')
    ssh_username = Column(String(64), comment='SSH用户名')
    web_url = Column(String(256), comment='Web管理URL')
    web_port = Column(Integer, comment='Web管理端口')

    # 元数据
    tags = Column(JSON, comment='标签列表')
    custom_fields = Column(JSON, comment='自定义字段')
    extra_data = Column(JSON, comment='扩展元数据')

    # 业务关联
    business_id = Column(Integer, comment='所属业务系统ID')
    business_name = Column(String(128), comment='所属业务系统名称')
    group_id = Column(Integer, comment='所属资产组ID')

    # 生命周期
    first_discovered_at = Column(DateTime, comment='首次发现时间')
    last_seen_at = Column(DateTime, comment='最后在线时间')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(64))
    updated_by = Column(String(64))

    # 主机名（DNS hostname）
    hostname = Column(String(128), comment='主机名')
    # 主IP地址（兼容字段，实际IP在 asset_ips 表）
    ip_address = Column(String(64), comment='主IP地址')
    mac_address = Column(String(64), comment='主MAC地址')

    # 位置信息（兼容字段）
    location = Column(String(256), comment='位置（兼容）')

    # 责任人（冗余存储，方便查询）
    owner = Column(String(64), comment='责任人')
    owner_email = Column(String(128), comment='责任人邮箱')

    # SSH 明文参考（仅指纹引用，实际密码在 credentials 表）
    ssh_password_fingerprint = Column(String(256), comment='SSH密码指纹')

    # 备注
    remark = Column(Text, comment='备注')

    # 管理接口（兼容）
    web_username = Column(String(64), comment='Web管理用户名')
    web_password_fingerprint = Column(String(256), comment='Web密码指纹')

    # 租户隔离
    tenant_id = Column(String(64), index=True)

    # 关系
    ips = relationship('AssetIP', back_populates='asset', cascade='all, delete-orphan', lazy='dynamic')
    tag_bindings = relationship('AssetTagBinding', back_populates='asset', cascade='all, delete-orphan')
    credentials_bindings = relationship('AssetCredentialBinding', back_populates='asset', cascade='all, delete-orphan')
    collection_profiles = relationship('AssetCollectionProfile', back_populates='asset', cascade='all, delete-orphan')
    lifecycle_events = relationship('AssetLifecycleEvent', back_populates='asset', cascade='all, delete-orphan')

    __table_args__ = (
        Index('idx_asset_type', 'asset_type'),
        Index('idx_sub_type', 'sub_type'),
        Index('idx_status', 'status'),
        Index('idx_first_discovered', 'first_discovered_at'),
        Index('idx_last_seen', 'last_seen_at'),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'name': self.name,
            'asset_type': self.asset_type,
            'sub_type': self.sub_type,
            'status': self.status,
            'idc': self.idc,
            'building': self.building,
            'floor': self.floor,
            'rack': self.rack,
            'rack_position': self.rack_position,
            'vendor': self.vendor,
            'model': self.model,
            'serial_number': self.serial_number,
            'manufacturer': self.manufacturer,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'warranty_end': self.warranty_end.isoformat() if self.warranty_end else None,
            'cost': float(self.cost) if self.cost else None,
            'os_type': self.os_type,
            'os_version': self.os_version,
            'kernel_version': self.kernel_version,
            'cpu': self.cpu,
            'memory': self.memory,
            'disk': self.disk,
            'network_interfaces': self.network_interfaces,
            'ssh_port': self.ssh_port,
            'ssh_username': self.ssh_username,
            'web_url': self.web_url,
            'web_port': self.web_port,
            'tags': self.tags or [],
            'custom_fields': self.custom_fields,
            'extra_data': self.extra_data,
            'business_id': self.business_id,
            'business_name': self.business_name,
            'group_id': self.group_id,
            'first_discovered_at': self.first_discovered_at.isoformat() if self.first_discovered_at else None,
            'last_seen_at': self.last_seen_at.isoformat() if self.last_seen_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'tenant_id': self.tenant_id,
        }


class AssetIP(Base):
    """资产IP地址表"""
    __tablename__ = 'asset_ips'

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey('assets.id', ondelete='CASCADE'), nullable=False)
    ip_address = Column(String(64), nullable=False)
    ip_type = Column(String(8), default='ipv4')
    mac_address = Column(String(64))
    hostname = Column(String(128))
    interface_name = Column(String(64))
    interface_type = Column(String(32))
    is_management = Column(Boolean, default=False)
    is_primary = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    vlan_id = Column(Integer)
    subnet_mask = Column(String(64))
    gateway = Column(String(64))
    dns_servers = Column(JSON)
    bandwidth = Column(String(32))
    nat_ip = Column(String(64))
    nat_port = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    asset = relationship('Asset', back_populates='ips')

    __table_args__ = (
        Index('uk_asset_ip_interface', 'asset_id', 'ip_address', 'interface_name', unique=True),
        Index('idx_ip_address', 'ip_address'),
    )


class AssetTag(Base):
    """资产标签定义表"""
    __tablename__ = 'asset_tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag_key = Column(String(64), nullable=False)
    tag_value = Column(String(256))
    tag_color = Column(String(16), default='#1890ff')
    tag_category = Column(String(64))
    description = Column(String(256))
    created_at = Column(DateTime, default=datetime.now)

    bindings = relationship('AssetTagBinding', back_populates='tag', cascade='all, delete-orphan')

    __table_args__ = (
        Index('uk_tag_key_value', 'tag_key', 'tag_value', unique=True),
    )


class AssetTagBinding(Base):
    """资产标签绑定表"""
    __tablename__ = 'asset_tag_bindings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey('assets.id', ondelete='CASCADE'), nullable=False)
    tag_id = Column(Integer, ForeignKey('asset_tags.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    created_by = Column(String(64))

    asset = relationship('Asset', back_populates='tag_bindings')
    tag = relationship('AssetTag', back_populates='bindings')

    __table_args__ = (
        Index('uk_asset_tag', 'asset_id', 'tag_id', unique=True),
    )


class AssetGroup(Base):
    """资产分组表"""
    __tablename__ = 'asset_groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_code = Column(String(64), unique=True, nullable=False)
    group_name = Column(String(128), nullable=False)
    parent_id = Column(Integer)
    group_type = Column(String(32))
    description = Column(String(256))
    display_order = Column(Integer, default=0)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(64))
    tenant_id = Column(String(64))

    __table_args__ = (
        Index('idx_parent_id', 'parent_id'),
    )


class AssetRelation(Base):
    """资产关系表"""
    __tablename__ = 'asset_relations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_asset_id = Column(Integer, ForeignKey('assets.id', ondelete='CASCADE'), nullable=False)
    target_asset_id = Column(Integer, ForeignKey('assets.id', ondelete='CASCADE'), nullable=False)
    relation_type = Column(String(32), nullable=False)
    relation_label = Column(String(128))
    bidirectional = Column(Boolean, default=False)
    extra_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    created_by = Column(String(64))

    __table_args__ = (
        Index('uk_relation', 'source_asset_id', 'target_asset_id', 'relation_type', unique=True),
        Index('idx_relation_type', 'relation_type'),
    )


class AssetCredentialBinding(Base):
    """资产凭证绑定表"""
    __tablename__ = 'asset_credentials'

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey('assets.id', ondelete='CASCADE'), nullable=False)
    credential_id = Column(Integer, nullable=False)  # 引用 credentials 表（Phase 3）
    credential_type = Column(String(32), nullable=False)
    interface_name = Column(String(64))
    is_primary = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    description = Column(String(256))
    enabled = Column(Boolean, default=True)
    last_verified_at = Column(DateTime)
    last_success_at = Column(DateTime)
    last_failure_at = Column(DateTime)
    last_failure_reason = Column(String(256))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(64))

    asset = relationship('Asset', back_populates='credentials_bindings')

    __table_args__ = (
        Index('uk_asset_credential', 'asset_id', 'credential_id', 'interface_name', unique=True),
        Index('idx_credential_type', 'credential_type'),
        Index('idx_is_primary', 'is_primary'),
    )


class AssetCollectionProfile(Base):
    """资产采集配置表"""
    __tablename__ = 'asset_collection_profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey('assets.id', ondelete='CASCADE'), nullable=False)
    profile_name = Column(String(128), nullable=False)
    collector_type = Column(String(64), nullable=False)
    collection_interval = Column(Integer, default=60)
    enabled = Column(Boolean, default=True)
    config = Column(JSON)
    metrics = Column(JSON)
    status = Column(String(32), default='active')
    last_collection_at = Column(DateTime)
    last_success_at = Column(DateTime)
    last_failure_at = Column(DateTime)
    last_failure_reason = Column(String(256))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(64))

    asset = relationship('Asset', back_populates='collection_profiles')

    __table_args__ = (
        Index('idx_collector_type', 'collector_type'),
        Index('idx_status', 'status'),
    )


class AssetLifecycleEvent(Base):
    """资产生命周期事件表"""
    __tablename__ = 'asset_lifecycle_events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey('assets.id', ondelete='CASCADE'), nullable=False)
    event_type = Column(String(64), nullable=False)
    event_subtype = Column(String(64))
    severity = Column(String(16), default='info')
    description = Column(Text)
    actor = Column(String(64))
    actor_name = Column(String(128))
    extra_data = Column(JSON)
    occurred_at = Column(DateTime, default=datetime.now)
    trace_id = Column(String(64))

    asset = relationship('Asset', back_populates='lifecycle_events')

    __table_args__ = (
        Index('idx_occurred_at', 'occurred_at'),
        Index('idx_trace_id', 'trace_id'),
    )
