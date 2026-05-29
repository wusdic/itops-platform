"""日志中心数据模型"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func
from modules.foundation.db_models.base import Base


class ExecutionLog(Base):
    """执行日志"""
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(String(64), nullable=False, index=True)
    step_name = Column(String(128))
    level = Column(String(16), default="INFO")  # DEBUG/INFO/WARN/ERROR
    message = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    trace_id = Column(String(64))

    __table_args__ = (
        Index("idx_exec_log", "execution_id", "timestamp"),
    )


class AuditLogRecord(Base):
    """审计日志"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(64), nullable=False)
    resource = Column(String(64), nullable=False)
    resource_id = Column(String(64))
    user_id = Column(String(64))
    username = Column(String(128))
    details = Column(Text)  # JSON
    ip_address = Column(String(64))
    trace_id = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_audit_resource", "resource", "resource_id"),
        Index("idx_audit_user", "user_id", "created_at"),
    )
