"""
系统配置数据库模型
用于存储系统配置和配置版本历史
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Index, Boolean
from sqlalchemy.sql import func

from .base import Base


class SystemConfig(Base):
    """
    系统配置模型
    支持配置版本管理和发布流程
    """
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 配置信息
    config_key = Column(String(128), unique=True, nullable=False, index=True)
    config_value = Column(Text, nullable=False, default="")
    category = Column(String(64), nullable=False, index=True, default="general")
    data_type = Column(String(32), nullable=False, default="string")  # string/int/bool/json/list

    # 描述
    description = Column(String(512))

    # 版本管理
    version = Column(Integer, nullable=False, default=1)
    isPublished = Column(Boolean, nullable=False, default=False)
    published_at = Column(DateTime)
    published_by = Column(String(64))

    # 锁定状态
    isLocked = Column(Boolean, nullable=False, default=False)
    locked_by = Column(String(64))
    locked_at = Column(DateTime)

    # 变更历史
    change_summary = Column(String(256))  # 变更摘要

    # 标签
    tags = Column(String(256))  # JSON数组格式

    # 租户隔离
    tenant_id = Column(String(64), index=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(64))
    updated_by = Column(String(64))

    # 索引
    __table_args__ = (
        Index('idx_category_key', 'category', 'config_key'),
        Index('idx_tenant_category', 'tenant_id', 'category'),
    )

    def __repr__(self):
        return f"<SystemConfig(id={self.id}, key='{self.config_key}', version={self.version})>"


class ConfigVersion(Base):
    """
    配置版本历史模型
    记录配置的每次变更历史
    """
    __tablename__ = "config_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_id = Column(Integer, nullable=False, index=True)

    # 版本信息
    version = Column(Integer, nullable=False)
    config_value = Column(Text, nullable=False)
    change_summary = Column(String(256))

    # 变更详情
    change_type = Column(String(32))  # create/update/delete/publish/rollback
    previous_value = Column(Text)  # 变更前的值
    diff = Column(Text)  # JSON格式的差异

    # 操作信息
    operation_type = Column(String(16))  # manual/auto/system
    operator = Column(String(64))
    operator_ip = Column(String(64))

    # 审批信息
    approved_by = Column(String(64))
    approved_at = Column(DateTime)
    approval_comment = Column(String(256))

    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 索引
    __table_args__ = (
        Index('idx_config_version', 'config_id', 'version', unique=True),
        Index('idx_config_time', 'config_id', 'created_at'),
    )

    def __repr__(self):
        return f"<ConfigVersion(config_id={self.config_id}, version={self.version})>"


class Credential(Base):
    """
    凭证模型
    用于安全存储敏感信息（密码、API密钥、证书等）
    """
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 凭证信息
    name = Column(String(128), nullable=False, index=True)
    credential_type = Column(String(64), nullable=False, index=True)  # password/api_key/certificate/token/ssh_key
    username = Column(String(128))  # 常与credential一起存储的用户名
    credential_value_encrypted = Column(Text, nullable=False)  # 加密后的凭证值
    credential_value_hash = Column(String(256))  # 用于校验的hash值（可选）

    # 关联资源
    resource_type = Column(String(64), index=True)  # device/adapter/system/user
    resource_id = Column(String(64), index=True)  # 关联资源ID
    resource_name = Column(String(256))  # 关联资源名称（冗余存储便于显示）

    # 安全设置
    is_active = Column(Boolean, nullable=False, default=True)
    expires_at = Column(DateTime)  # 过期时间
    last_rotated_at = Column(DateTime)  # 最近一次轮换时间
    rotation_interval_days = Column(Integer)  # 轮换周期（天）

    # 使用限制
    allowed_ips = Column(String(256))  # 允许访问的IP列表，JSON格式
    max_usage_count = Column(Integer)  # 最大使用次数，-1表示无限制
    usage_count = Column(Integer, default=0)  # 当前使用次数

    # 描述和标签
    description = Column(String(512))
    tags = Column(String(256))  # JSON数组格式

    # 审计信息
    created_by = Column(String(64))
    updated_by = Column(String(64))
    last_used_at = Column(DateTime)
    last_used_by = Column(String(64))

    # 租户隔离
    tenant_id = Column(String(64), index=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 索引
    __table_args__ = (
        Index('idx_resource', 'resource_type', 'resource_id'),
        Index('idx_tenant_type', 'tenant_id', 'credential_type'),
        Index('idx_name_active', 'name', 'is_active'),
    )

    def __repr__(self):
        return f"<Credential(id={self.id}, name='{self.name}', type='{self.credential_type}')>"

    def is_expired(self) -> bool:
        """检查凭证是否已过期"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def is_active_and_valid(self) -> bool:
        """检查凭证是否可用"""
        if not self.is_active:
            return False
        if self.is_expired():
            return False
        if self.max_usage_count > 0 and self.usage_count >= self.max_usage_count:
            return False
        return True
