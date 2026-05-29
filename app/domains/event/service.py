"""事件中心服务"""
import uuid
import json
import logging
from typing import Optional, List, Dict, Any

from app.common.database import get_db_session
from app.common.context import get_trace_id

logger = logging.getLogger(__name__)


class EventService:
    """事件中心服务"""

    @staticmethod
    def create_event(
        event_type: str,
        source: str = "system",
        asset_id: Optional[str] = None,
        severity: str = "info",
        payload: Optional[Dict[str, Any]] = None,
        correlation_key: Optional[str] = None,
    ) -> str:
        """创建事件"""
        with get_db_session() as db:
            from app.domains.event.models import Event
            event_id = f"evt-{uuid.uuid4().hex[:16]}"
            event = Event(
                event_id=event_id,
                event_type=event_type,
                source=source,
                asset_id=asset_id,
                severity=severity,
                payload=json.dumps(payload) if payload else None,
                correlation_key=correlation_key,
                trace_id=get_trace_id(),
            )
            db.add(event)
            db.commit()
            logger.info(f"Event created: {event_id} type={event_type} asset={asset_id}")
            return event_id

    @staticmethod
    def get_events(
        asset_id: Optional[str] = None,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """查询事件列表"""
        with get_db_session() as db:
            from app.domains.event.models import Event
            query = db.query(Event)
            if asset_id:
                query = query.filter(Event.asset_id == asset_id)
            if event_type:
                query = query.filter(Event.event_type == event_type)
            if severity:
                query = query.filter(Event.severity == severity)
            if status:
                query = query.filter(Event.status == status)
            total = query.count()
            records = query.order_by(Event.timestamp.desc()).offset(offset).limit(limit).all()
            return {
                "total": total,
                "items": [
                    {
                        "id": r.id,
                        "event_id": r.event_id,
                        "event_type": r.event_type,
                        "source": r.source,
                        "asset_id": r.asset_id,
                        "severity": r.severity,
                        "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                        "payload": json.loads(r.payload) if r.payload else None,
                        "correlation_key": r.correlation_key,
                        "status": r.status,
                    }
                    for r in records
                ],
            }
