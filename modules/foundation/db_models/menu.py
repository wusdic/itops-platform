"""
菜单管理数据库模型
存储系统菜单和导航结构
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func

from .base import Base


class Menu(Base):
    """
    菜单模型
    支持树形结构的菜单管理
    """
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 菜单基本信息
    name = Column(String(100), nullable=False, comment="菜单名称")
    code = Column(String(64), unique=True, index=True, comment="菜单代码")
    icon = Column(String(128), nullable=True, comment="菜单图标")
    path = Column(String(256), nullable=True, comment="路由路径")
    component = Column(String(256), nullable=True, comment="组件路径")
    redirect = Column(String(256), nullable=True, comment="重定向路径")

    # 层级关系
    parent_id = Column(Integer, nullable=True, index=True, comment="父菜单ID")
    sort_order = Column(Integer, default=0, comment="排序序号")

    # 菜单类型
    menu_type = Column(String(20), default="menu")  # menu/directory/button
    visible = Column(Integer, default=1)  # 1=显示, 0=隐藏
    is_frame = Column(Integer, default=1)  # 1=外部 frame, 0=内部页面
    cache = Column(Integer, default=0)  # 1=缓存, 0=不缓存

    # 权限
    permission = Column(String(100), nullable=True, comment="权限标识")
    description = Column(String(256), nullable=True, comment="描述")

    # 状态
    status = Column(String(20), default="active")  # active/inactive

    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_parent_id', 'parent_id'),
        Index('idx_status', 'status'),
        Index('idx_sort_order', 'sort_order'),
    )

    def __repr__(self):
        return f"<Menu(id={self.id}, name='{self.name}', code='{self.code}')>"
