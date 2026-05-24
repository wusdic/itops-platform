"""
字典管理数据库模型
存储系统数据字典和字典项
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func

from .base import Base


class DictType(Base):
    """
    字典类型模型
    """
    __tablename__ = "dict_types"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 字典类型信息
    name = Column(String(100), nullable=False, comment="字典类型名称")
    code = Column(String(64), unique=True, index=True, nullable=False, comment="字典类型代码")
    description = Column(String(256), nullable=True, comment="描述")
    status = Column(String(20), default="active")  # active/inactive

    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_code', 'code'),
        Index('idx_status', 'status'),
    )

    def __repr__(self):
        return f"<DictType(id={self.id}, name='{self.name}', code='{self.code}')>"


class DictItem(Base):
    """
    字典项模型
    存储具体字典值
    """
    __tablename__ = "dict_items"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 字典项信息
    type_id = Column(Integer, nullable=False, index=True, comment="所属字典类型ID")
    label = Column(String(100), nullable=False, comment="显示文本")
    value = Column(String(256), nullable=False, comment="字典值")
    sort_order = Column(Integer, default=0, comment="排序序号")

    # 扩展属性
    color = Column(String(32), nullable=True, comment="颜色标签")
    css_class = Column(String(64), nullable=True, comment="CSS样式类")
    extra_data = Column(Text, nullable=True, comment="扩展数据JSON")

    # 状态
    status = Column(String(20), default="active")  # active/inactive

    # 元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_type_id', 'type_id'),
        Index('idx_value', 'value'),
        Index('idx_sort_order', 'sort_order'),
    )

    def __repr__(self):
        return f"<DictItem(id={self.id}, label='{self.label}', value='{self.value}')>"
