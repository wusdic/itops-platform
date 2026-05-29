"""日志中心路由"""
from fastapi import APIRouter, Query
from typing import Optional

from app.domains.log.service import LogService

router = APIRouter(prefix="/logs", tags=["日志中心"])


@router.get("/executions/{execution_id}")
def get_execution_logs(execution_id: str, level: Optional[str] = Query(None)):
    """获取执行日志"""
    logs = LogService.get_execution_logs(execution_id, level)
    return {"code": 0, "message": "success", "data": logs}


@router.get("/audit")
def get_audit_logs(
    resource: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    limit: int = Query(100, le=200),
):
    """获取审计日志"""
    logs = LogService.get_audit_logs(resource, user_id, limit)
    return {"code": 0, "message": "success", "data": logs}
