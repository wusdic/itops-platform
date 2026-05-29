"""日志中心服务"""
import json
import logging
from typing import Optional, List, Dict, Any

from app.common.database import get_db_session

logger = logging.getLogger(__name__)


class LogService:
    """日志中心服务"""

    @staticmethod
    def log_execution(
        execution_id: str,
        step_name: str,
        level: str = "INFO",
        message: str = "",
        trace_id: str = None,
    ) -> int:
        """记录执行日志"""
        with get_db_session() as db:
            from app.domains.log.models import ExecutionLog
            log = ExecutionLog(
                execution_id=execution_id,
                step_name=step_name,
                level=level,
                message=message,
                trace_id=trace_id,
            )
            db.add(log)
            db.commit()
            return log.id

    @staticmethod
    def get_execution_logs(execution_id: str, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取执行日志"""
        with get_db_session() as db:
            from app.domains.log.models import ExecutionLog
            query = db.query(ExecutionLog).filter(ExecutionLog.execution_id == execution_id)
            if level:
                query = query.filter(ExecutionLog.level == level)
            records = query.order_by(ExecutionLog.timestamp.asc()).all()
            return [
                {
                    "id": r.id,
                    "execution_id": r.execution_id,
                    "step_name": r.step_name,
                    "level": r.level,
                    "message": r.message,
                    "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                }
                for r in records
            ]

    @staticmethod
    def get_audit_logs(
        resource: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """获取审计日志"""
        with get_db_session() as db:
            from app.domains.log.models import AuditLogRecord
            query = db.query(AuditLogRecord)
            if resource:
                query = query.filter(AuditLogRecord.resource == resource)
            if user_id:
                query = query.filter(AuditLogRecord.user_id == user_id)
            records = query.order_by(AuditLogRecord.created_at.desc()).limit(limit).all()
            return [
                {
                    "id": r.id,
                    "action": r.action,
                    "resource": r.resource,
                    "resource_id": r.resource_id,
                    "user_id": r.user_id,
                    "username": r.username,
                    "details": json.loads(r.details) if r.details else None,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in records
            ]
