"""状态中心数据模型"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func
from modules.foundation.db_models.base import Base


class AssetStateSnapshot(Base):
    """资产状态快照"""
    __tablename__ = "asset_state_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(String(64), nullable=False, index=True)
    state_type = Column(String(32), nullable=False)  # healthy/warning/critical/maintenance
    state_value = Column(Text)  # JSON 格式的详细状态
    collection_status = Column(String(32), default="success")  # success/failed/partial_success/timeout
    reached_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_asset_state", "asset_id", "state_type"),
    )


class AssetStateChange(Base):
    """资产状态变更记录"""
    __tablename__ = "asset_state_changes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(String(64), nullable=False, index=True)
    from_state = Column(String(32))
    to_state = Column(String(32), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(String(256))
    trace_id = Column(String(64))

    __table_args__ = (
        Index("idx_asset_change", "asset_id", "changed_at"),
    )
