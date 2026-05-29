"""工单中心数据模型"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func
from modules.foundation.db_models.base import Base


class Ticket(Base):
    """工单"""
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(64), unique=True, nullable=False, index=True)
    title = Column(String(256), nullable=False)
    description = Column(Text)
    priority = Column(String(16), default="medium")  # low/medium/high/critical
    status = Column(String(16), default="open")  # open/acknowledged/processing/resolved/closed
    source_type = Column(String(32))  # alert/execution/manual
    source_id = Column(String(64))
    assigned_to = Column(String(64))
    created_by = Column(String(64))
    closed_at = Column(DateTime(timezone=True))
    resolution = Column(Text)  # 关闭原因/解决方案
    review = Column(Text)  # 复盘内容
    related_logs = Column(Text)  # JSON array
    related_executions = Column(Text)  # JSON array
    trace_id = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("idx_ticket_status", "status", "priority"),
        Index("idx_ticket_source", "source_type", "source_id"),
    )
