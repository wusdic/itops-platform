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

    @staticmethod
    def explain_match(policy: Dict[str, Any], event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 7-5: 策略命中解释。

        解释为什么某个策略被命中，返回：
        - match_reason: 命中原因
        - affected_assets: 受影响的资产列表
        - action_plan: 将要执行的动作计划
        - risk_assessment: 风险评估
        - verification_plan: 如何验证执行结果
        """
        policy_name = policy.get("name", "未知策略")
        trigger_type = policy.get("trigger_type", "")
        scope = policy.get("scope", {})
        actions = policy.get("actions", [])
        verification = policy.get("verification", {})
        risk_level = policy.get("risk_level", "medium")

        # 构建命中原因
        match_reasons = []
        if event_data.get("trigger_type"):
            match_reasons.append(f"触发类型匹配: {event_data['trigger_type']}")
        if event_data.get("asset_id"):
            match_reasons.append(f"资产ID: {event_data['asset_id']}")
        if event_data.get("metric_value") is not None:
            match_reasons.append(f"指标值: {event_data['metric_value']}（触发阈值: {trigger_type}）")
        if event_data.get("severity"):
            match_reasons.append(f"事件严重度: {event_data['severity']}")

        # 受影响资产
        affected_assets = []
        scope_type = scope.get("scope_type", "all")
        if scope_type == "all":
            affected_assets = [{"scope": "all", "description": "所有资产"}]
        elif scope_type == "tags":
            affected_assets = [{"type": "tags", "tags": scope.get("tags", []), "description": "按标签筛选"}]
        elif scope_type == "device_ids":
            device_ids = scope.get("device_ids", [])
            affected_assets = [{"type": "device_ids", "count": len(device_ids), "ids": device_ids[:10], "description": f"指定 {len(device_ids)} 台设备"}]

        # 动作计划
        action_plan = []
        for action in (actions if isinstance(actions, list) else []):
            action_desc = action if isinstance(action, str) else action.get("type", "unknown")
            action_plan.append({
                "action": action_desc,
                "description": f"执行动作: {action_desc}",
                "estimated_duration_ms": 5000,
            })

        # 风险评估
        risk_colors = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}
        risk_assessment = {
            "level": risk_level,
            "icon": risk_colors.get(risk_level, "⚪️"),
            "warnings": [],
        }
        if risk_level in ("high", "critical"):
            risk_assessment["warnings"].append(f"⚠️ {policy_name} 为 {risk_level} 风险等级，需要审批")
        if scope_type == "all":
            risk_assessment["warnings"].append("⚠️ 影响范围为全量资产，请谨慎操作")

        # 验证计划
        verification_plan = []
        if verification:
            verification_plan.append({
                "step": "指标复查",
                "description": f"执行后检查指标是否恢复: {verification.get('metric_name', 'unknown')}",
                "expected_value": verification.get("expected_value", "normal"),
                "tolerance": verification.get("tolerance", 0.05),
            })
        else:
            verification_plan.append({
                "step": "指标复查",
                "description": "执行后检查指标是否恢复到正常范围",
                "expected_value": "低于阈值",
            })

        return {
            "policy_id": policy.get("policy_id"),
            "policy_name": policy_name,
            "trigger_type": trigger_type,
            "match_reasons": match_reasons,
            "affected_assets": affected_assets,
            "action_plan": action_plan,
            "risk_assessment": risk_assessment,
            "verification_plan": verification_plan,
            "require_approval": bool(policy.get("require_approval")),
        }
