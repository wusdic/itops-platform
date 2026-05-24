# -*- coding: utf-8 -*-
"""
指纹模板版本管理 - 数据库模型
"""

from .base import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from datetime import datetime


class FingerprintTemplateVersion(Base):
    """
    指纹模板版本快照
    每次模板变更前保存当前完整状态，支持回滚
    """
    __tablename__ = "fingerprint_template_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(64), nullable=False, unique=True, index=True, comment="版本号")
    description = Column(String(255), nullable=True, comment="版本描述")
    content = Column(Text, nullable=False, comment="完整模板内容(JSON)")
    operator = Column(String(64), nullable=True, comment="操作人")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_fingerprint_template_versions_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<FingerprintTemplateVersion(version={self.version}, created_at={self.created_at})>"
