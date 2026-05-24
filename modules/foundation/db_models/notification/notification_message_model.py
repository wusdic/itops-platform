"""
站内消息数据库模型
用于存储用户收到的通知消息（站内信）
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Index
from sqlalchemy.sql import func
from modules.foundation.db_models.base import Base


class NotificationMessageModel(Base):
    """站内消息模型"""
    __tablename__ = "notification_message"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 用户信息
    user_id = Column(String(64), nullable=False, index=True)
    username = Column(String(128))
    
    # 消息内容
    title = Column(String(200), nullable=False)
    content = Column(Text)
    
    # 消息类型: system, alert, workorder, device, knowledge, ai
    type = Column(String(32), nullable=False, index=True, default="system")
    
    # 关联对象 (JSON格式)
    # 例如: {"object_type": "alert", "object_id": "123"}
    related_object = Column(Text)
    
    # 状态
    is_read = Column(Boolean, default=False, index=True)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # 优先级: low, normal, high, urgent
    priority = Column(String(16), default="normal")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    read_at = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))
    
    # 索引
    __table_args__ = (
        Index('idx_msg_user_read', 'user_id', 'is_read'),
        Index('idx_msg_user_created', 'user_id', 'created_at'),
        Index('idx_msg_user_type', 'user_id', 'type'),
    )
    
    def to_dict(self):
        """转换为字典"""
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'title': self.title,
            'content': self.content,
            'type': self.type,
            'related_object': json.loads(self.related_object) if self.related_object else None,
            'is_read': self.is_read,
            'is_deleted': self.is_deleted,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
        }
