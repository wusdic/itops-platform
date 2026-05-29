"""治理中心数据模型"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func
from modules.foundation.db_models.base import Base


class UserRole(Base):
    """用户角色"""
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(String(64), unique=True, nullable=False, index=True)
    role_name = Column(String(64), nullable=False)
    description = Column(Text)
    permissions = Column(Text)  # JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PermissionRecord(Base):
    """权限记录"""
    __tablename__ = "permission_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), index=True)
    resource = Column(String(64), nullable=False)
    action = Column(String(32), nullable=False)
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    granted_by = Column(String(64))
    trace_id = Column(String(64))

    __table_args__ = (
        Index("idx_perm_user", "user_id", "resource"),
    )
