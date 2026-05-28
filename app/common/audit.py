"""
审计日志工具

记录关键操作（创建/删除/执行/审批）到审计日志表。
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from app.common.context import get_trace_id, get_user_id, get_username

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    审计日志记录器

    用法:
        audit = AuditLogger(db)
        audit.log(
            action="asset.create",
            resource="asset",
            resource_id="123",
            details={"name": "server-01"}
        )
    """

    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> None:
        """
        记录审计日志

        Args:
            action: 操作类型，如 asset.create, asset.delete, automation.execute
            resource: 资源类型，如 asset, config, automation
            resource_id: 资源 ID
            details: 操作详情（JSON 格式）
            status: 操作状态 success/failed
            error_message: 错误信息
        """
        try:
            from modules.foundation.db_models import operation_logs

            log_entry = operation_logs.OperationLog(
                username=get_username() or "system",
                action=action,
                resource=resource,
                resource_id=str(resource_id) if resource_id else None,
                watermark_id=None,
                method="API",
                path=f"/{resource}",
                ip_address=None,
                user_agent=None,
                request_body=None,
                response_status=0 if status == "success" else 1,
                error_message=error_message,
                duration_ms=0,
                timestamp=datetime.now(),
            )
            self.db.add(log_entry)
            self.db.commit()
            logger.info(
                f"Audit: {action} {resource}/{resource_id} by {get_username()} - {status}"
            )
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
            self.db.rollback()


def log_audit(
    db: Session,
    action: str,
    resource: str,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    status: str = "success",
    error_message: Optional[str] = None,
) -> None:
    """便捷函数：记录审计日志"""
    AuditLogger(db).log(action, resource, resource_id, details, status, error_message)
