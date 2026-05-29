"""策略中心数据模型"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Index, Boolean, ForeignKey
from sqlalchemy.sql import func
from modules.foundation.db_models.base import Base


class Policy(Base):
    """策略"""
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    trigger_source = Column(String(64))  # event/alert/manual
    trigger_type = Column(String(64))  # disk_usage_high/cpu_high/...
    condition = Column(Text)  # JSON 条件表达式
    scope = Column(Text)  # JSON 适用范围
    risk_level = Column(String(16), default="medium")  # low/medium/high/critical
    require_approval = Column(Integer, default=0)  # 0=不需要 1=需要
    actions = Column(Text)  # JSON 动作链
    verification = Column(Text)  # JSON 验证条件
    version = Column(Integer, default=1)
    status = Column(String(16), default="draft")  # draft/published/disabled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("idx_policy_trigger", "trigger_source", "trigger_type"),
    )


class PolicyVersion(Base):
    """策略版本表"""
    __tablename__ = "policy_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version_id = Column(String(64), unique=True, nullable=False, index=True)
    policy_id = Column(String(64), nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    content_snapshot = Column(Text, nullable=False)  # JSON 完整策略快照
    change_summary = Column(Text)  # 版本变更说明
    created_by = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=False)  # 是否为当前激活版本

    __table_args__ = (
        Index("idx_policy_version_policy", "policy_id", "version"),
    )
