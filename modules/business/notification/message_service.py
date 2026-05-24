"""
BM-06 站内消息服务
提供站内信（通知消息）的CRUD操作
"""

import logging
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from modules.foundation.db_models.notification.notification_message_model import NotificationMessageModel

logger = logging.getLogger(__name__)


class NotificationMessageService:
    """站内消息服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_message(
        self,
        user_id: str,
        title: str,
        content: str,
        msg_type: str = "system",
        username: Optional[str] = None,
        related_object: Optional[Dict] = None,
        priority: str = "normal",
    ) -> NotificationMessageModel:
        """创建站内消息"""
        message = NotificationMessageModel(
            user_id=user_id,
            username=username,
            title=title,
            content=content,
            type=msg_type,
            related_object=json.dumps(related_object) if related_object else None,
            priority=priority,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_message(self, message_id: int, user_id: str) -> Optional[NotificationMessageModel]:
        """获取单条消息"""
        return self.db.query(NotificationMessageModel).filter(
            and_(
                NotificationMessageModel.id == message_id,
                NotificationMessageModel.user_id == user_id,
                NotificationMessageModel.is_deleted == False
            )
        ).first()
    
    def list_messages(
        self,
        user_id: str,
        msg_type: Optional[str] = None,
        is_read: Optional[bool] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[NotificationMessageModel]:
        """获取消息列表"""
        query = self.db.query(NotificationMessageModel).filter(
            and_(
                NotificationMessageModel.user_id == user_id,
                NotificationMessageModel.is_deleted == False
            )
        )
        
        if msg_type:
            query = query.filter(NotificationMessageModel.type == msg_type)
        
        if is_read is not None:
            query = query.filter(NotificationMessageModel.is_read == is_read)
        
        if keyword:
            query = query.filter(
                or_(
                    NotificationMessageModel.title.ilike(f"%{keyword}%"),
                    NotificationMessageModel.content.ilike(f"%{keyword}%")
                )
            )
        
        return query.order_by(desc(NotificationMessageModel.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    
    def count_messages(
        self,
        user_id: str,
        msg_type: Optional[str] = None,
        is_read: Optional[bool] = None,
    ) -> int:
        """统计消息数量"""
        query = self.db.query(NotificationMessageModel).filter(
            and_(
                NotificationMessageModel.user_id == user_id,
                NotificationMessageModel.is_deleted == False
            )
        )
        
        if msg_type:
            query = query.filter(NotificationMessageModel.type == msg_type)
        
        if is_read is not None:
            query = query.filter(NotificationMessageModel.is_read == is_read)
        
        return query.count()
    
    def count_unread(self, user_id: str) -> int:
        """统计未读消息数量"""
        return self.db.query(NotificationMessageModel).filter(
            and_(
                NotificationMessageModel.user_id == user_id,
                NotificationMessageModel.is_deleted == False,
                NotificationMessageModel.is_read == False
            )
        ).count()
    
    def mark_read(self, message_id: int, user_id: str) -> bool:
        """标记单条消息为已读"""
        message = self.get_message(message_id, user_id)
        if not message:
            return False
        
        message.is_read = True
        message.read_at = datetime.now()
        self.db.commit()
        return True
    
    def mark_all_read(self, user_id: str) -> int:
        """标记所有消息为已读，返回已读数量"""
        now = datetime.now()
        count = self.db.query(NotificationMessageModel).filter(
            and_(
                NotificationMessageModel.user_id == user_id,
                NotificationMessageModel.is_deleted == False,
                NotificationMessageModel.is_read == False
            )
        ).update({
            NotificationMessageModel.is_read: True,
            NotificationMessageModel.read_at: now
        })
        self.db.commit()
        return count
    
    def delete_message(self, message_id: int, user_id: str) -> bool:
        """删除单条消息（软删除）"""
        message = self.get_message(message_id, user_id)
        if not message:
            return False
        
        message.is_deleted = True
        message.deleted_at = datetime.now()
        self.db.commit()
        return True
    
    def delete_all(self, user_id: str) -> int:
        """删除所有消息（软删除），返回删除数量"""
        now = datetime.now()
        count = self.db.query(NotificationMessageModel).filter(
            and_(
                NotificationMessageModel.user_id == user_id,
                NotificationMessageModel.is_deleted == False
            )
        ).update({
            NotificationMessageModel.is_deleted: True,
            NotificationMessageModel.deleted_at: now
        })
        self.db.commit()
        return count
