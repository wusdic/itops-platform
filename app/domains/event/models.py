"""事件中心数据模型"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func
from modules.foundation.db_models.base import Base


class Event(Base):
    """事件记录"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), unique=True, nullable=False, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    source = Column(String(64))  # collector/alert/system/manual
    asset_id = Column(String(64), index=True)
    severity = Column(String(16))  # critical/high/medium/low/info
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    payload = Column(Text)  # JSON
    correlation_key = Column(String(128), index=True)
    trace_id = Column(String(64))
    status = Column(String(16), default="active")  # active/corrlated/suppressed/cleared
    related_event_ids = Column(Text)  # JSON array

    __table_args__ = (
        Index("idx_event_asset_time", "asset_id", "timestamp"),
        Index("idx_event_corr", "correlation_key", "timestamp"),
    )
