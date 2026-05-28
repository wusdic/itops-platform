"""
BM-028 告警领域 - API 路由

统一告警管理 API，包含告警 CRUD、触发规则、抑制、收敛、升级等功能。
遵循统一响应格式 + ErrorCode + get_db_session() 规范。
"""

from fastapi import APIRouter, HTTPException, Query, status, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Any

from app.common import success_response, error_response, paginated_response, ErrorCode, get_http_status
from app.common.context import get_trace_id
from app.common.database import get_db_session

router = APIRouter(prefix="/alerts", tags=["告警管理"])


# ============== 请求模型 ==============

class TriggerRuleCreateRequest(BaseModel):
    """创建触发规则请求"""
    name: str = Field(..., description="规则名称")
    condition_type: str = Field("threshold", description="条件类型: threshold, change, rate, constant, expression")
    match_conditions: dict = Field(..., description="匹配条件")
    alert_level: str = Field("warning", description="告警级别")
    description: str = Field("", description="规则描述")
    enabled: bool = Field(True, description="是否启用")
    suppress_enabled: bool = Field(False, description="是否启用抑制")
    suppress_duration: int = Field(300, description="抑制时间(秒)")
    trigger_interval: int = Field(60, description="触发间隔(秒)")


# ============== 告警基础接口 ==============

@router.get("/", summary="获取告警列表")
async def list_alerts(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=200, description="每页数量"),
    status: Optional[str] = Query(None, description="状态过滤: active, acknowledged, resolved, closed, suppressed"),
    level: Optional[str] = Query(None, description="级别过滤: critical, high, medium, low, info"),
    device_id: Optional[int] = Query(None, description="设备ID"),
    host: Optional[str] = Query(None, description="主机名/IP"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
):
    """获取告警列表，支持分页和多种过滤条件"""
    with get_db_session() as db:
        from modules.foundation.db_models.alert import Alert, AlertStatus, AlertLevel
        from modules.business.monitoring.alert_service import AlertService
        from sqlalchemy import or_
        
        svc = AlertService(db)
        
        # 构建过滤条件
        status_filter = None
        if status:
            try:
                status_filter = AlertStatus(status)
            except ValueError:
                pass
        
        level_filter = None
        if level:
            try:
                level_filter = AlertLevel(level)
            except ValueError:
                pass
        
        alerts, total = svc.list_alerts(
            status=status_filter,
            level=level_filter,
            device_id=device_id,
            host=host,
            page=page,
            page_size=page_size,
        )
        
        items = [alert.to_dict() for alert in alerts]
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            trace_id=get_trace_id(),
        )


@router.get("/stats", summary="获取告警统计")
async def get_alert_stats():
    """获取告警统计信息"""
    with get_db_session() as db:
        from modules.foundation.db_models.alert import Alert, AlertStatus, AlertLevel
        from modules.business.monitoring.alert_service import AlertService
        
        svc = AlertService(db)
        stats = svc.get_statistics()
        
        return success_response(data=stats, trace_id=get_trace_id())


@router.get("/{alert_id}", summary="获取告警详情")
async def get_alert(alert_id: int):
    """获取单个告警详情"""
    with get_db_session() as db:
        from modules.foundation.db_models.alert import Alert
        from modules.business.monitoring.alert_service import AlertService
        
        svc = AlertService(db)
        alert = svc.get_alert(alert_id)
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found",
            )
        
        return success_response(data=alert.to_dict(), trace_id=get_trace_id())


@router.post("/", summary="创建告警")
async def create_alert(
    title: str = Query(..., description="告警标题"),
    level: str = Query(..., description="告警级别: critical, high, medium, low, info"),
    message: str = Query("", description="告警消息"),
    device_id: Optional[int] = Query(None, description="设备ID"),
    device_name: Optional[str] = Query(None, description="设备名称"),
    device_ip: Optional[str] = Query(None, description="设备IP"),
    metric_name: Optional[str] = Query(None, description="指标名称"),
    metric_value: Optional[float] = Query(None, description="指标值"),
    threshold: Optional[float] = Query(None, description="阈值"),
    category: Optional[str] = Query(None, description="分类"),
):
    """创建新告警"""
    with get_db_session() as db:
        from modules.foundation.db_models.alert import AlertLevel, AlertCategory
        from modules.business.monitoring.alert_service import AlertService
        
        svc = AlertService(db)
        
        # 转换级别
        try:
            alert_level = AlertLevel(level)
        except ValueError:
            alert_level = AlertLevel.INFO
        
        # 转换分类
        alert_category = None
        if category:
            try:
                alert_category = AlertCategory(category)
            except ValueError:
                alert_category = AlertCategory.OTHER
        
        alert = svc.create_alert(
            title=title,
            level=alert_level,
            message=message,
            device_id=device_id,
            device_name=device_name,
            device_ip=device_ip,
            metric_name=metric_name,
            metric_value=metric_value,
            threshold=threshold,
            category=alert_category,
        )
        
        return success_response(
            data=alert.to_dict(),
            message="Alert created successfully",
            trace_id=get_trace_id(),
        )


@router.put("/{alert_id}/acknowledge", summary="确认告警")
async def acknowledge_alert(alert_id: int):
    """确认告警"""
    with get_db_session() as db:
        from modules.business.monitoring.alert_service import AlertService
        from app.common.context import get_username
        
        svc = AlertService(db)
        username = get_username() or "system"
        
        if not svc.acknowledge_alert(alert_id, username):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found",
            )
        
        return success_response(
            data={"id": alert_id, "status": "acknowledged"},
            message="Alert acknowledged",
            trace_id=get_trace_id(),
        )


@router.put("/{alert_id}/resolve", summary="解决告警")
async def resolve_alert(
    alert_id: int,
    resolution: str = Query("", description="解决方案"),
):
    """解决告警"""
    with get_db_session() as db:
        from modules.business.monitoring.alert_service import AlertService
        from app.common.context import get_username
        
        svc = AlertService(db)
        username = get_username() or "system"
        
        if not svc.resolve_alert(alert_id, username, resolution):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found",
            )
        
        return success_response(
            data={"id": alert_id, "status": "resolved"},
            message="Alert resolved",
            trace_id=get_trace_id(),
        )


@router.put("/{alert_id}/close", summary="关闭告警")
async def close_alert(alert_id: int):
    """关闭告警"""
    with get_db_session() as db:
        from modules.business.monitoring.alert_service import AlertService
        from app.common.context import get_username
        
        svc = AlertService(db)
        username = get_username() or "system"
        
        if not svc.close_alert(alert_id, username):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found",
            )
        
        return success_response(
            data={"id": alert_id, "status": "closed"},
            message="Alert closed",
            trace_id=get_trace_id(),
        )


@router.put("/{alert_id}/suppress", summary="抑制告警")
async def suppress_alert(
    alert_id: int,
    reason: str = Query("", description="抑制原因"),
):
    """抑制告警"""
    with get_db_session() as db:
        from modules.foundation.db_models.alert import Alert, AlertStatus
        from modules.business.monitoring.alert_service import AlertService
        from app.common.context import get_username
        
        svc = AlertService(db)
        username = get_username() or "system"
        
        alert = svc.get_alert(alert_id)
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found",
            )
        
        if alert.status == AlertStatus.SUPPRESSED:
            return error_response(
                code=ErrorCode.ALERT_SUPPRESSED,
                message="Alert already suppressed",
                trace_id=get_trace_id(),
            )
        
        if not svc.suppress_alert(alert_id, username, reason):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found",
            )
        
        return success_response(
            data={"id": alert_id, "status": "suppressed"},
            message="Alert suppressed",
            trace_id=get_trace_id(),
        )


@router.put("/{alert_id}/restore", summary="恢复告警")
async def restore_alert(alert_id: int):
    """恢复已抑制的告警"""
    with get_db_session() as db:
        from modules.foundation.db_models.alert import AlertStatus
        from modules.business.monitoring.alert_service import AlertService
        from app.common.context import get_username
        
        svc = AlertService(db)
        username = get_username() or "system"
        
        if not svc.restore_alert(alert_id, username):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found or not suppressed",
            )
        
        return success_response(
            data={"id": alert_id, "status": "active"},
            message="Alert restored",
            trace_id=get_trace_id(),
        )


@router.put("/{alert_id}/transfer", summary="转派告警")
async def transfer_alert(
    alert_id: int,
    assignee: str = Query(..., description="接收人"),
):
    """转派告警给其他处理人"""
    with get_db_session() as db:
        from modules.business.monitoring.alert_service import AlertService
        from app.common.context import get_username
        
        svc = AlertService(db)
        username = get_username() or "system"
        
        if not svc.transfer_alert(alert_id, assignee, username):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found",
            )
        
        return success_response(
            data={"id": alert_id, "assignee": assignee},
            message=f"Alert transferred to {assignee}",
            trace_id=get_trace_id(),
        )


# ============== 告警规则接口 ==============

@router.get("/rules/", summary="获取告警规则列表")
async def list_alert_rules():
    """获取告警触发规则列表"""
    with get_db_session() as db:
        from modules.foundation.db_models.alert import AlertRule
        from sqlalchemy import desc
        
        rules = db.query(AlertRule).order_by(desc(AlertRule.created_at)).all()
        
        items = [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "category": r.category.value if r.category else None,
                "level": r.level.value if r.level else "medium",
                "enabled": r.enabled,
                "expression": r.expression,
                "threshold_value": r.threshold_value,
                "comparison": r.comparison,
                "duration_seconds": r.duration_seconds,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rules
        ]
        
        return success_response(data={"items": items, "total": len(items)}, trace_id=get_trace_id())


@router.get("/rules/{rule_id}", summary="获取告警规则详情")
async def get_alert_rule(rule_id: int):
    """获取告警规则详情"""
    with get_db_session() as db:
        from modules.foundation.db_models.alert import AlertRule
        
        rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert rule not found",
            )
        
        return success_response(
            data={
                "id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "category": rule.category.value if rule.category else None,
                "level": rule.level.value if rule.level else "medium",
                "enabled": rule.enabled,
                "expression": rule.expression,
                "threshold_value": rule.threshold_value,
                "comparison": rule.comparison,
                "duration_seconds": rule.duration_seconds,
                "metric_name": rule.metric_name,
                "metric_source": rule.metric_source,
                "device_type_filter": rule.device_type_filter,
                "device_id_filter": rule.device_id_filter,
                "tags_filter": rule.tags_filter,
                "auto_acknowledge": rule.auto_acknowledge,
                "auto_resolve": rule.auto_resolve,
                "create_workorder": rule.create_workorder,
                "notify_enabled": rule.notify_enabled,
                "notify_channels": rule.notify_channels,
                "notify_receivers": rule.notify_receivers,
                "notify_interval": rule.notify_interval,
                "suppress_enabled": rule.suppress_enabled,
                "suppress_duration": rule.suppress_duration,
                "suppress_key": rule.suppress_key,
                "created_at": rule.created_at.isoformat() if rule.created_at else None,
                "updated_at": rule.updated_at.isoformat() if rule.updated_at else None,
            },
            trace_id=get_trace_id(),
        )


# ============== 告警收敛接口 ==============

@router.get("/consolidation/groups", summary="获取收敛组列表")
async def get_consolidation_groups():
    """获取告警收敛组列表"""
    from modules.business.monitoring.alert_consolidation import get_alert_consolidator
    
    consolidator = get_alert_consolidator()
    groups = consolidator.get_all_groups()
    
    items = [g.to_dict() for g in groups]
    
    return success_response(
        data={"items": items, "total": len(items)},
        trace_id=get_trace_id(),
    )


@router.get("/consolidation/rules", summary="获取收敛规则列表")
async def get_consolidation_rules():
    """获取告警收敛规则列表"""
    from modules.business.monitoring.alert_consolidation import get_alert_consolidator
    
    consolidator = get_alert_consolidator()
    rules = consolidator.list_rules()
    
    items = [r.to_dict() for r in rules]
    
    return success_response(
        data={"items": items, "total": len(items)},
        trace_id=get_trace_id(),
    )


@router.post("/consolidation/evaluate", summary="评估告警收敛")
async def evaluate_consolidation(alert_id: int):
    """对指定告警进行收敛评估"""
    with get_db_session() as db:
        from modules.business.monitoring.alert_service import AlertService
        
        svc = AlertService(db)
        group = svc.consolidate_alert(alert_id)
        
        if not group:
            return error_response(
                code=ErrorCode.ALERT_CONSOLIDATION_FAILED,
                message="Consolidation failed or alert not found",
                trace_id=get_trace_id(),
            )
        
        return success_response(
            data=group.to_dict(),
            message=f"Alert consolidated into group with {group.count} alerts",
            trace_id=get_trace_id(),
        )


# ============== 告警触发接口 ==============

@router.post("/trigger/evaluate", summary="评估指标触发条件")
async def evaluate_trigger(
    metric_name: str = Query(..., description="指标名称"),
    value: float = Query(..., description="指标值"),
    device_id: int = Query(..., description="设备ID"),
    device_name: str = Query(..., description="设备名称"),
    device_ip: str = Query(..., description="设备IP"),
    previous_value: Optional[float] = Query(None, description="前一个值"),
    duration_seconds: Optional[int] = Query(None, description="持续秒数"),
):
    """评估指标是否触发告警"""
    with get_db_session() as db:
        from modules.business.monitoring.alert_service import AlertService
        
        svc = AlertService(db)
        
        events = await svc.evaluate_and_trigger(
            metric_name=metric_name,
            value=value,
            device_id=device_id,
            device_name=device_name,
            device_ip=device_ip,
            previous_value=previous_value,
            duration_seconds=duration_seconds,
        )
        
        return success_response(
            data={
                "triggered": len(events) > 0,
                "events": [e.to_dict() for e in events],
                "count": len(events),
            },
            trace_id=get_trace_id(),
        )


@router.get("/trigger/events", summary="获取触发事件列表")
async def get_trigger_events(
    rule_id: Optional[str] = Query(None, description="规则ID"),
    status: Optional[str] = Query(None, description="状态"),
    limit: int = Query(100, le=1000, description="返回数量"),
):
    """获取触发事件历史"""
    from modules.business.monitoring.alert_trigger import get_trigger_engine, TriggerStatus
    
    engine = get_trigger_engine()
    
    status_enum = None
    if status:
        try:
            status_enum = TriggerStatus(status)
        except ValueError:
            pass
    
    events = engine.list_events(
        rule_id=rule_id,
        status=status_enum,
        limit=limit,
    )
    
    return success_response(
        data={"items": [e.to_dict() for e in events], "total": len(events)},
        trace_id=get_trace_id(),
    )


@router.get("/trigger/rules", summary="获取触发规则列表")
async def get_trigger_rules(enabled: Optional[bool] = Query(None, description="启用状态")):
    """获取告警触发规则列表"""
    from modules.business.monitoring.alert_trigger import get_trigger_engine, TriggerCondition
    
    engine = get_trigger_engine()
    rules = engine.list_rules(enabled_only=False)
    
    if enabled is not None:
        rules = [r for r in rules if r.enabled == enabled]
    
    items = [r.to_dict() for r in rules]
    
    return success_response(
        data={"items": items, "total": len(items)},
        trace_id=get_trace_id(),
    )


@router.post("/trigger/rules", summary="创建触发规则")
async def create_trigger_rule(request: TriggerRuleCreateRequest):
    """创建新的触发规则"""
    with get_db_session() as db:
        from modules.business.monitoring.alert_service import AlertService
        
        svc = AlertService(db)
        
        rule_id = svc.create_trigger_rule(
            name=request.name,
            condition_type=request.condition_type,
            match_conditions=request.match_conditions,
            alert_level=request.alert_level,
            description=request.description,
            enabled=request.enabled,
            suppress_enabled=request.suppress_enabled,
            suppress_duration=request.suppress_duration,
            trigger_interval=request.trigger_interval,
        )
        
        return success_response(
            data={"id": rule_id},
            message="Trigger rule created successfully",
            trace_id=get_trace_id(),
        )


@router.delete("/trigger/rules/{rule_id}", summary="删除触发规则")
async def delete_trigger_rule(rule_id: str):
    """删除触发规则"""
    from modules.business.monitoring.alert_trigger import get_trigger_engine
    
    engine = get_trigger_engine()
    
    if not engine.delete_rule(rule_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trigger rule not found",
        )
    
    return success_response(
        message="Trigger rule deleted",
        trace_id=get_trace_id(),
    )


@router.post("/trigger/rules/{rule_id}/test", summary="测试触发规则")
async def test_trigger_rule(rule_id: str):
    """测试触发规则"""
    from modules.business.monitoring.alert_trigger import get_trigger_engine
    
    engine = get_trigger_engine()
    rule = engine.get_rule(rule_id)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trigger rule not found",
        )
    
    # 模拟测试数据
    import asyncio
    conditions = rule.match_conditions
    test_value = conditions.get('value', 90) + 10
    
    async def run_test():
        return await engine.evaluate_and_trigger(
            metric_name=conditions.get('metric', 'cpu_usage'),
            value=test_value,
            device_id=1,
            device_name='test-server',
            device_ip='192.168.1.1',
        )
    
    events = asyncio.run(run_test())
    
    return success_response(
        data={
            "success": len(events) > 0,
            "triggered": len(events) > 0,
            "events": [e.to_dict() for e in events],
            "message": f"Test {'triggered successfully' if events else 'did not trigger'}",
        },
        trace_id=get_trace_id(),
    )


# ============== 告警升级接口 ==============

@router.post("/{alert_id}/escalate", summary="手动升级告警")
async def escalate_alert(alert_id: int):
    """手动升级告警"""
    with get_db_session() as db:
        from modules.foundation.db_models.alert import Alert
        from modules.business.monitoring.alert_audit_service import AlertAuditService, AuditAction
        
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found",
            )
        
        # 创建升级审计日志
        audit_service = AlertAuditService(db)
        try:
            audit_service.create_log(
                alert_id=alert_id,
                action=AuditAction.ESCALATE,
                alert_key=alert.alert_key,
                operator="system",
                reason="Manual escalation",
            )
        except Exception as e:
            pass  # 审计日志失败不影响主流程
        
        return success_response(
            data={"id": alert_id, "escalated": True},
            message="Alert escalated",
            trace_id=get_trace_id(),
        )


@router.get("/escalation/policies", summary="获取升级策略列表")
async def get_escalation_policies():
    """获取告警升级策略列表"""
    from modules.business.monitoring.alerter import get_alert_trigger, EscalationPolicy
    
    trigger = get_alert_trigger()
    
    # 返回默认升级策略
    policies = [
        {
            "level": 1,
            "wait_seconds": 300,
            "notify_channels": ["email"],
            "description": "Level 1: 通知值班人员",
        },
        {
            "level": 2,
            "wait_seconds": 600,
            "notify_channels": ["email", "sms"],
            "assignees": ["on_call_manager"],
            "description": "Level 2: 通知运维经理",
        },
        {
            "level": 3,
            "wait_seconds": 900,
            "notify_channels": ["email", "sms", "phone"],
            "assignees": ["team_lead"],
            "description": "Level 3: 升级到团队负责人",
        },
    ]
    
    return success_response(data={"items": policies, "total": len(policies)}, trace_id=get_trace_id())
