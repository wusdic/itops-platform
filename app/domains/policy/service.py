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

    # ==================== Phase 7-2: 策略版本管理 ====================

    @staticmethod
    def _policy_to_dict(p: "Policy") -> Dict[str, Any]:
        """将 Policy 模型转为字典"""
        return {
            "id": p.id,
            "policy_id": p.policy_id,
            "name": p.name,
            "description": p.description,
            "trigger_source": p.trigger_source,
            "trigger_type": p.trigger_type,
            "condition": json.loads(p.condition) if p.condition else None,
            "scope": json.loads(p.scope) if p.scope else None,
            "risk_level": p.risk_level,
            "require_approval": p.require_approval,
            "actions": json.loads(p.actions) if p.actions else [],
            "verification": json.loads(p.verification) if p.verification else None,
            "version": p.version,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }

    @staticmethod
    def create_version(policy_id: str, change_summary: str = "", created_by: str = "system") -> Optional[str]:
        """
        Phase 7-2: 为策略创建一个新版本快照。

        发布策略时自动创建版本快照，保存完整策略内容。
        """
        with get_db_session() as db:
            from app.domains.policy.models import Policy, PolicyVersion

            policy = db.query(Policy).filter(Policy.policy_id == policy_id).first()
            if not policy:
                return None

            # 获取当前最新版本号
            latest = db.query(PolicyVersion).filter(
                PolicyVersion.policy_id == policy_id
            ).order_by(PolicyVersion.version.desc()).first()
            next_version = (latest.version + 1) if latest else 1

            version_id = f"pv-{uuid.uuid4().hex[:16]}"
            version = PolicyVersion(
                version_id=version_id,
                policy_id=policy_id,
                version=next_version,
                content_snapshot=json.dumps(PolicyService._policy_to_dict(policy)),
                change_summary=change_summary or f"版本 {next_version} 发布",
                created_by=created_by,
                is_active=False,
            )
            db.add(version)

            # 将之前的版本标记为非激活
            db.query(PolicyVersion).filter(
                PolicyVersion.policy_id == policy_id,
                PolicyVersion.version < next_version,
            ).update({"is_active": False})

            db.commit()
            return version_id

    @staticmethod
    def list_versions(policy_id: str) -> List[Dict[str, Any]]:
        """Phase 7-2: 列出策略的所有版本"""
        with get_db_session() as db:
            from app.domains.policy.models import PolicyVersion
            records = db.query(PolicyVersion).filter(
                PolicyVersion.policy_id == policy_id
            ).order_by(PolicyVersion.version.desc()).all()
            return [
                {
                    "version_id": r.version_id,
                    "policy_id": r.policy_id,
                    "version": r.version,
                    "change_summary": r.change_summary,
                    "created_by": r.created_by,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                    "is_active": r.is_active,
                }
                for r in records
            ]

    @staticmethod
    def get_version(version_id: str) -> Optional[Dict[str, Any]]:
        """Phase 7-2: 获取指定版本的完整快照"""
        with get_db_session() as db:
            from app.domains.policy.models import PolicyVersion
            record = db.query(PolicyVersion).filter(
                PolicyVersion.version_id == version_id
            ).first()
            if not record:
                return None
            return {
                "version_id": record.version_id,
                "policy_id": record.policy_id,
                "version": record.version,
                "change_summary": record.change_summary,
                "created_by": record.created_by,
                "created_at": record.created_at.isoformat() if record.created_at else None,
                "is_active": record.is_active,
                "content": json.loads(record.content_snapshot),
            }

    @staticmethod
    def rollback_version(version_id: str) -> Optional[str]:
        """
        Phase 7-2: 回滚策略到指定版本。

        将指定版本的内容恢复到策略主表，并创建新版本快照记录这次回滚。
        注意：本方法在单个事务内完成策略恢复+版本记录，版本ID从本方法内生成。
        """
        with get_db_session() as db:
            from app.domains.policy.models import Policy, PolicyVersion

            version_record = db.query(PolicyVersion).filter(
                PolicyVersion.version_id == version_id
            ).first()
            if not version_record:
                return None

            policy = db.query(Policy).filter(
                Policy.policy_id == version_record.policy_id
            ).first()
            if not policy:
                return None

            # 获取当前最新版本号，准备创建新版本记录
            latest = db.query(PolicyVersion).filter(
                PolicyVersion.policy_id == version_record.policy_id
            ).order_by(PolicyVersion.version.desc()).first()
            next_version = (latest.version + 1) if latest else 1

            # 恢复策略内容
            content = json.loads(version_record.content_snapshot)
            policy.name = content.get("name", policy.name)
            policy.description = content.get("description")
            policy.trigger_source = content.get("trigger_source")
            policy.trigger_type = content.get("trigger_type")
            policy.condition = json.dumps(content["condition"]) if content.get("condition") else None
            policy.scope = json.dumps(content["scope"]) if content.get("scope") else None
            policy.risk_level = content.get("risk_level", policy.risk_level)
            policy.require_approval = content.get("require_approval", 0)
            policy.actions = json.dumps(content["actions"]) if content.get("actions") else None
            policy.verification = json.dumps(content["verification"]) if content.get("verification") else None
            policy.version = version_record.version
            policy.status = "published"

            # 在同一事务内创建新版本快照（记录这次回滚）
            import uuid as _uuid
            new_version_id = f"pv-{_uuid.uuid4().hex[:16]}"
            new_pv = PolicyVersion(
                version_id=new_version_id,
                policy_id=policy.policy_id,
                version=next_version,
                content_snapshot=json.dumps(PolicyService._policy_to_dict(policy)),
                change_summary=f"回滚到版本 {version_record.version}",
                created_by="system",
                is_active=False,
            )
            db.add(new_pv)

            # 将旧版本标记为非激活
            db.query(PolicyVersion).filter(
                PolicyVersion.policy_id == policy.policy_id,
                PolicyVersion.version < next_version,
            ).update({"is_active": False})

            db.commit()
            return new_version_id
