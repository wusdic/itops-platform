"""事件中心路由"""
from fastapi import APIRouter, Query, Body
from typing import Optional, List

from app.domains.event.service import EventService
from app.domains.event.schemas import EventCreate

router = APIRouter(prefix="/events", tags=["事件中心"])


@router.post("")
def create_event(event: EventCreate):
    """创建事件"""
    event_id = EventService.create_event(
        event_type=event.event_type,
        source=event.source,
        asset_id=event.asset_id,
        severity=event.severity,
        payload=event.payload,
        correlation_key=event.correlation_key,
    )
    return {"code": 0, "message": "success", "data": {"event_id": event_id}}


@router.get("")
def list_events(
    asset_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=200),
    offset: int = Query(0),
):
    """查询事件列表"""
    result = EventService.get_events(asset_id, event_type, severity, status, limit, offset)
    return {"code": 0, "message": "success", "data": result["items"], "total": result["total"]}
