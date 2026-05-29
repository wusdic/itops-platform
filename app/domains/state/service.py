"""状态中心服务"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.common.database import get_db_session
from app.common.context import get_trace_id

logger = logging.getLogger(__name__)


class StateService:
    """状态中心服务"""

    @staticmethod
    def get_latest_state(asset_id: str, state_type: str = "health") -> Optional[Dict[str, Any]]:
        """获取资产最新状态"""
        with get_db_session() as db:
            from app.domains.state.models import AssetStateSnapshot
            record = db.query(AssetStateSnapshot).filter(
                AssetStateSnapshot.asset_id == asset_id,
                AssetStateSnapshot.state_type == state_type
            ).order_by(AssetStateSnapshot.reached_at.desc()).first()
            if record:
                return {
                    "id": record.id,
                    "asset_id": record.asset_id,
                    "state_type": record.state_type,
                    "state_value": record.state_value,
                    "collection_status": record.collection_status,
                    "reached_at": record.reached_at.isoformat() if record.reached_at else None,
                }
            return None

    @staticmethod
    def record_state_change(asset_id: str, from_state: str, to_state: str, reason: str = None) -> int:
        """记录状态变更"""
        with get_db_session() as db:
            from app.domains.state.models import AssetStateChange, AssetStateSnapshot
            change = AssetStateChange(
                asset_id=asset_id,
                from_state=from_state,
                to_state=to_state,
                reason=reason,
                trace_id=get_trace_id(),
            )
            db.add(change)
            db.commit()
            return change.id

    @staticmethod
    def get_state_history(asset_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取状态变更历史"""
        with get_db_session() as db:
            from app.domains.state.models import AssetStateChange
            records = db.query(AssetStateChange).filter(
                AssetStateChange.asset_id == asset_id
            ).order_by(AssetStateChange.changed_at.desc()).limit(limit).all()
            return [
                {
                    "id": r.id,
                    "asset_id": r.asset_id,
                    "from_state": r.from_state,
                    "to_state": r.to_state,
                    "changed_at": r.changed_at.isoformat() if r.changed_at else None,
                    "reason": r.reason,
                }
                for r in records
            ]
