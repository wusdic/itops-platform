"""知识中心数据模型"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func
from modules.foundation.db_models.base import Base


class KnowledgeArticle(Base):
    """知识文章"""
    __tablename__ = "knowledge_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(String(64), unique=True, nullable=False, index=True)
    title = Column(String(256), nullable=False)
    content = Column(Text)
    tags = Column(String(512))  # 逗号分隔
    category = Column(String(64))
    asset_types = Column(String(256))  # 适用的资产类型，逗号分隔
    alert_types = Column(String(256))  # 适用的告警类型
    status = Column(String(16), default="draft")  # draft/published/archived
    source_type = Column(String(32))  # manual/alert/execution/ticket/ai
    source_id = Column(String(64))
    author = Column(String(64))
    review_status = Column(String(16), default="pending")  # pending/approved/rejected
    reviewed_by = Column(String(64))
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("idx_kb_status", "status", "category"),
        Index("idx_kb_tags", "tags"),
    )
