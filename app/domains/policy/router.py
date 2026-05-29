"""策略中心路由"""
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.domains.policy.service import PolicyService
from app.domains.policy.schemas import PolicyCreate

router = APIRouter(prefix="/policies", tags=["策略中心"])


class PolicyConflictCheckRequest(BaseModel):
    """策略冲突检测请求"""
    policies: List[Dict[str, Any]] = Field(..., description="待检测的策略列表（可以是新建策略或已有策略）")


class PolicyConflict(BaseModel):
    """策略冲突"""
    conflict_type: str = Field(..., description="冲突类型: overlapping_scope / same_trigger / conflicting_actions")
    severity: str = Field(..., description="严重程度: high / medium / low")
    policy_a: Dict[str, Any] = Field(..., description="冲突策略A")
    policy_b: Dict[str, Any] = Field(..., description="冲突策略B")
    description: str = Field(..., description="冲突描述")
    resolution: str = Field(..., description="解决建议")


@router.post("/check-conflicts", summary="检测策略冲突")
def check_policy_conflicts(request: PolicyConflictCheckRequest):
    """
    检测策略之间的冲突。
    
    检测以下冲突类型：
    - overlapping_scope: 两个策略触发条件重叠（同类型+同范围）
    - same_trigger: 两个策略触发同一事件
    - conflicting_actions: 两个策略执行的动作互相冲突
    """
    conflicts: List[Dict[str, Any]] = []

    policies = request.policies
    n = len(policies)

    for i in range(n):
        for j in range(i + 1, n):
            pA = policies[i]
            pB = policies[j]

            # 跳过禁用或草稿策略
            if pA.get("status") in ("disabled", "draft") and pB.get("status") in ("disabled", "draft"):
                continue

            # 检测1：相同触发类型 + 重叠范围 = 冲突
            if pA.get("trigger_type") and pA["trigger_type"] == pB.get("trigger_type"):
                scope_a = pA.get("scope", {})
                scope_b = pB.get("scope", {})

                # 解析 scope 中的 device_ids 和 tags
                devices_a = set(scope_a.get("device_ids", []))
                devices_b = set(scope_b.get("device_ids", []))
                tags_a = set(scope_a.get("tags", []))
                tags_b = set(scope_b.get("tags", []))

                has_overlap = (
                    (devices_a and devices_b and devices_a & devices_b) or
                    (tags_a and tags_b and tags_a & tags_b)
                )

                if has_overlap:
                    conflicts.append({
                        "conflict_type": "overlapping_scope",
                        "severity": "high" if (pA.get("risk_level") == "critical" or pB.get("risk_level") == "critical") else "medium",
                        "policy_a": {"policy_id": pA.get("policy_id") or pA.get("id"), "name": pA.get("name")},
                        "policy_b": {"policy_id": pB.get("policy_id") or pB.get("id"), "name": pB.get("name")},
                        "description": (
                            f"策略「{pA.get('name')}」和「{pB.get('name')}」"
                            f"同为 {pA['trigger_type']} 触发且作用范围重叠，"
                            f"可能导致同一个事件触发多个策略。"
                        ),
                        "resolution": "使用策略优先级或时间窗口区分，或合并为同一策略。",
                    })

            # 检测2：相同触发类型 + 不同范围但都是全范围 = 冲突
            if (pA.get("trigger_type") and pA["trigger_type"] == pB.get("trigger_type") and
                scope_a.get("scope_type") == "all" and scope_b.get("scope_type") == "all"):
                conflicts.append({
                    "conflict_type": "overlapping_scope",
                    "severity": "high",
                    "policy_a": {"policy_id": pA.get("policy_id") or pA.get("id"), "name": pA.get("name")},
                    "policy_b": {"policy_id": pB.get("policy_id") or pB.get("id"), "name": pB.get("name")},
                    "description": (
                        f"策略「{pA.get('name')}」和「{pB.get('name')}」"
                        f"同为全范围 {pA['trigger_type']} 触发，必然冲突。"
                    ),
                    "resolution": "只保留一个全范围策略，或限制其中一个的范围。",
                })

    return {
        "code": 0,
        "message": "success",
        "data": {
            "total_policies": n,
            "conflict_count": len(conflicts),
            "has_conflicts": len(conflicts) > 0,
            "conflicts": conflicts,
        }
    }


class PolicySimulateRequest(BaseModel):
    """策略模拟请求"""
    trigger_type: str = Field(..., description="触发类型: disk_usage_high/cpu_high/memory_high/...")
    asset_id: Optional[str] = Field(None, description="资产ID")
    device_id: Optional[int] = Field(None, description="设备ID")
    event_data: Optional[Dict[str, Any]] = Field({}, description="事件数据（如指标值）")


@router.post("/simulate", summary="模拟策略触发")
def simulate_policies(request: PolicySimulateRequest):
    """
    模拟给定事件会命中哪些策略（dry-run 模式）。
    
    用于在创建/修改策略前测试策略是否会按预期触发。
    返回会命中的策略列表及触发原因。
    """
    # 获取所有启用的策略
    all_policies = PolicyService.list_policies(status="published", limit=500)

    matched_policies = []
    for policy in all_policies:
        # 检查触发类型是否匹配
        if policy.get("trigger_type") != request.trigger_type:
            continue

        # 检查适用范围
        scope = policy.get("scope", {})
        scope_type = scope.get("scope_type", "all")

        if scope_type == "all":
            # 全范围策略，直接命中
            matched_policies.append({
                "policy_id": policy.get("policy_id"),
                "name": policy.get("name"),
                "trigger_type": policy.get("trigger_type"),
                "risk_level": policy.get("risk_level"),
                "matched": True,
                "match_reason": "全范围策略，匹配所有触发事件",
                "actions": policy.get("actions"),
                "require_approval": bool(policy.get("require_approval")),
            })
        elif scope_type == "tags" and request.asset_id:
            # 按标签匹配
            asset_tags = scope.get("tags", [])
            # 简化：假设 asset_id 包含标签信息，这里用 asset_id 前缀模拟
            if any(tag.lower() in request.asset_id.lower() for tag in asset_tags):
                matched_policies.append({
                    "policy_id": policy.get("policy_id"),
                    "name": policy.get("name"),
                    "trigger_type": policy.get("trigger_type"),
                    "risk_level": policy.get("risk_level"),
                    "matched": True,
                    "match_reason": f"资产标签匹配: {asset_tags}",
                    "actions": policy.get("actions"),
                    "require_approval": bool(policy.get("require_approval")),
                })
        elif scope_type == "device_ids" and request.device_id:
            # 按设备ID匹配
            device_ids = scope.get("device_ids", [])
            if request.device_id in device_ids:
                matched_policies.append({
                    "policy_id": policy.get("policy_id"),
                    "name": policy.get("name"),
                    "trigger_type": policy.get("trigger_type"),
                    "risk_level": policy.get("risk_level"),
                    "matched": True,
                    "match_reason": f"设备ID {request.device_id} 在策略范围内",
                    "actions": policy.get("actions"),
                    "require_approval": bool(policy.get("require_approval")),
                })

    return {
        "code": 0,
        "message": "success",
        "data": {
            "trigger_type": request.trigger_type,
            "asset_id": request.asset_id,
            "device_id": request.device_id,
            "total_policies_checked": len(all_policies),
            "matched_count": len(matched_policies),
            "matched_policies": matched_policies,
        }
    }


@router.post("")
def create_policy(policy: PolicyCreate):
    """创建策略"""
    policy_id = PolicyService.create_policy(policy.model_dump())
    return {"code": 0, "message": "success", "data": {"policy_id": policy_id}}


@router.get("")
def list_policies(status: Optional[str] = Query(None), limit: int = Query(100, le=200)):
    """列出策略"""
    policies = PolicyService.list_policies(status, limit)
    return {"code": 0, "message": "success", "data": policies}


@router.get("/match/{trigger_type}")
def match_policies(trigger_type: str, asset_id: Optional[str] = Query(None)):
    """匹配适用的策略"""
    policies = PolicyService.match_policies(trigger_type, asset_id)
    return {"code": 0, "message": "success", "data": policies}


@router.post("/match/{trigger_type}/explain", summary="策略命中解释")
def explain_policy_match(
    trigger_type: str,
    event_data: Dict[str, Any],
):
    """
    Phase 7-5: 策略命中解释。

    给定触发类型和事件数据，返回命中的策略及其命中原因、影响资产、动作计划和验证方案。
    用于用户在策略触发后，看到"为什么触发这个策略"的解释。
    """
    # 匹配所有 published 策略
    matched = PolicyService.match_policies(trigger_type=trigger_type, asset_id=event_data.get("asset_id"))

    explanations = []
    for policy in matched:
        explanation = PolicyService.explain_match(policy, event_data)
        explanations.append(explanation)

    return {
        "code": 0,
        "message": "success",
        "data": {
            "trigger_type": trigger_type,
            "event_data": event_data,
            "matched_count": len(explanations),
            "explanations": explanations,
        }
    }
