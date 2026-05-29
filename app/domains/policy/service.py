"""策略中心服务"""
import uuid
import json
import logging
from typing import Optional, List, Dict, Any

from app.common.database import get_db_session

logger = logging.getLogger(__name__)


class PolicyService:
    """策略中心服务"""

    @staticmethod
    def create_policy(policy_data: Dict[str, Any]) -> str:
        """创建策略"""
        with get_db_session() as db:
            from app.domains.policy.models import Policy
            policy_id = f"pol-{uuid.uuid4().hex[:16]}"
            policy = Policy(
                policy_id=policy_id,
                name=policy_data["name"],
                description=policy_data.get("description"),
                trigger_source=policy_data.get("trigger_source", "event"),
                trigger_type=policy_data.get("trigger_type"),
                condition=json.dumps(policy_data.get("condition")) if policy_data.get("condition") else None,
                scope=json.dumps(policy_data.get("scope")) if policy_data.get("scope") else None,
                risk_level=policy_data.get("risk_level", "medium"),
                require_approval=policy_data.get("require_approval", 0),
                actions=json.dumps(policy_data.get("actions")) if policy_data.get("actions") else None,
                verification=json.dumps(policy_data.get("verification")) if policy_data.get("verification") else None,
                status="draft",
            )
            db.add(policy)
            db.commit()
            return policy_id

    @staticmethod
    def match_policies(trigger_type: str, asset_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """匹配适用的策略"""
        with get_db_session() as db:
            from app.domains.policy.models import Policy
            records = db.query(Policy).filter(
                Policy.trigger_type == trigger_type,
                Policy.status == "published"
            ).all()
            return [
                {
                    "policy_id": r.policy_id,
                    "name": r.name,
                    "trigger_source": r.trigger_source,
                    "trigger_type": r.trigger_type,
                    "risk_level": r.risk_level,
                    "require_approval": r.require_approval,
                    "actions": json.loads(r.actions) if r.actions else [],
                    "verification": json.loads(r.verification) if r.verification else None,
                }
                for r in records
            ]

    @staticmethod
    def list_policies(status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """列出策略"""
        with get_db_session() as db:
            from app.domains.policy.models import Policy
            query = db.query(Policy)
            if status:
                query = query.filter(Policy.status == status)
            records = query.order_by(Policy.created_at.desc()).limit(limit).all()
            return [
                {
                    "id": r.id,
                    "policy_id": r.policy_id,
                    "name": r.name,
                    "trigger_source": r.trigger_source,
                    "trigger_type": r.trigger_type,
                    "risk_level": r.risk_level,
                    "require_approval": r.require_approval,
                    "version": r.version,
                    "status": r.status,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in records
            ]
