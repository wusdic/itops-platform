"""治理中心服务"""
import logging
from typing import Optional, List, Dict, Any

from app.common.database import get_db_session

logger = logging.getLogger(__name__)


class GovernanceService:
    """治理中心服务"""

    @staticmethod
    def get_user_permissions(user_id: str) -> List[str]:
        """获取用户权限列表"""
        with get_db_session() as db:
            from app.domains.governance.models import PermissionRecord
            records = db.query(PermissionRecord).filter(
                PermissionRecord.user_id == user_id
            ).all()
            return list(set(f"{r.resource}.{r.action}" for r in records))

    @staticmethod
    def grant_permission(user_id: str, resource: str, action: str, granted_by: str = None) -> bool:
        """授予权限"""
        with get_db_session() as db:
            from app.domains.governance.models import PermissionRecord
            existing = db.query(PermissionRecord).filter(
                PermissionRecord.user_id == user_id,
                PermissionRecord.resource == resource,
                PermissionRecord.action == action,
            ).first()
            if existing:
                return True
            record = PermissionRecord(
                user_id=user_id,
                resource=resource,
                action=action,
                granted_by=granted_by,
            )
            db.add(record)
            db.commit()
            return True
