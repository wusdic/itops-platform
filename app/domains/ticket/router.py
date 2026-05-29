"""工单中心路由"""
from fastapi import APIRouter, Query, Path
from typing import Optional

from app.domains.ticket.service import TicketService
from app.domains.ticket.schemas import TicketCreate, TicketUpdate

router = APIRouter(prefix="/tickets", tags=["工单中心"])


@router.post("")
def create_ticket(ticket: TicketCreate):
    """创建工单"""
    ticket_id = TicketService.create_ticket(ticket.model_dump())
    return {"code": 0, "message": "success", "data": {"ticket_id": ticket_id}}


@router.get("/{ticket_id}")
def get_ticket(ticket_id: str = Path(...)):
    """获取工单详情"""
    ticket = TicketService.get_ticket(ticket_id)
    if not ticket:
        return {"code": 1, "message": "工单不存在"}
    return {"code": 0, "message": "success", "data": ticket}


@router.put("/{ticket_id}")
def update_ticket(ticket_id: str = Path(...), update: TicketUpdate = ...):
    """更新工单"""
    ok = TicketService.update_ticket(ticket_id, update.model_dump(exclude_none=True))
    return {"code": 0 if ok else 1, "message": "success" if ok else "工单不存在"}


@router.get("")
def list_tickets(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    limit: int = Query(100, le=200),
    offset: int = Query(0),
):
    """列出工单"""
    result = TicketService.list_tickets(status, priority, assigned_to, limit, offset)
    return {"code": 0, "message": "success", "data": result["items"], "total": result["total"]}
