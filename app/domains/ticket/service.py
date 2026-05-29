"""工单中心服务"""
import uuid
import json
import logging
from typing import Optional, List, Dict, Any

from app.common.database import get_db_session

logger = logging.getLogger(__name__)


class TicketService:
    """工单中心服务"""

    @staticmethod
    def create_ticket(ticket_data: Dict[str, Any], created_by: str = None) -> str:
        """创建工单"""
        with get_db_session() as db:
            from app.domains.ticket.models import Ticket
            ticket_id = f"tkt-{uuid.uuid4().hex[:16]}"
            ticket = Ticket(
                ticket_id=ticket_id,
                title=ticket_data["title"],
                description=ticket_data.get("description"),
                priority=ticket_data.get("priority", "medium"),
                source_type=ticket_data.get("source_type"),
                source_id=ticket_data.get("source_id"),
                assigned_to=ticket_data.get("assigned_to"),
                created_by=created_by,
            )
            db.add(ticket)
            db.commit()
            logger.info(f"Ticket created: {ticket_id}")
            return ticket_id

    @staticmethod
    def get_ticket(ticket_id: str) -> Optional[Dict[str, Any]]:
        """获取工单详情"""
        with get_db_session() as db:
            from app.domains.ticket.models import Ticket
            record = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
            if record:
                return {
                    "id": record.id,
                    "ticket_id": record.ticket_id,
                    "title": record.title,
                    "description": record.description,
                    "priority": record.priority,
                    "status": record.status,
                    "source_type": record.source_type,
                    "source_id": record.source_id,
                    "assigned_to": record.assigned_to,
                    "created_by": record.created_by,
                    "resolution": record.resolution,
                    "review": record.review,
                    "created_at": record.created_at.isoformat() if record.created_at else None,
                    "closed_at": record.closed_at.isoformat() if record.closed_at else None,
                }
            return None

    @staticmethod
    def update_ticket(ticket_id: str, update_data: Dict[str, Any]) -> bool:
        """更新工单"""
        with get_db_session() as db:
            from app.domains.ticket.models import Ticket
            from datetime import datetime
            record = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
            if not record:
                return False
            for key, value in update_data.items():
                if value is not None and hasattr(record, key):
                    setattr(record, key, value)
            if update_data.get("status") == "closed":
                record.closed_at = datetime.now()
            db.commit()
            return True

    @staticmethod
    def list_tickets(
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """列出工单"""
        with get_db_session() as db:
            from app.domains.ticket.models import Ticket
            query = db.query(Ticket)
            if status:
                query = query.filter(Ticket.status == status)
            if priority:
                query = query.filter(Ticket.priority == priority)
            if assigned_to:
                query = query.filter(Ticket.assigned_to == assigned_to)
            total = query.count()
            records = query.order_by(Ticket.created_at.desc()).offset(offset).limit(limit).all()
            return {
                "total": total,
                "items": [
                    {
                        "id": r.id,
                        "ticket_id": r.ticket_id,
                        "title": r.title,
                        "priority": r.priority,
                        "status": r.status,
                        "source_type": r.source_type,
                        "assigned_to": r.assigned_to,
                        "created_at": r.created_at.isoformat() if r.created_at else None,
                    }
                    for r in records
                ],
            }
