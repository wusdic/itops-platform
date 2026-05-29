"""
策略中心 - API 路由

提供策略模板、策略规则、评估引擎的 API 接口：
- 策略模板 CRUD
- 策略 CRUD 及版本管理
- 策略规则管理
- 策略评估引擎
"""

from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Header, status


async def safe_json_body(request: Request) -> dict:
    """安全解析 JSON body，空 body 返回空字典而不抛 StopIteration 异常"""
    try:
        body = await request.json()
        return body if isinstance(body, dict) else {}
    except Exception:
        return {}

from app.common import (
    success_response,
    error_response,
    paginated_response,
    get_trace_id,
    get_username,
)
from app.common.database import get_db_session
from app.domains.strategy.service import (
    StrategyTemplateService,
    StrategyService,
    StrategyRuleService,
    EvaluationEngine,
)
from app.domains.strategy.schemas import (
    CreateTemplateRequest,
    UpdateTemplateRequest,
    CreateStrategyRequest,
    UpdateStrategyRequest,
    PublishStrategyRequest,
    RollbackStrategyRequest,
    CreateRuleRequest,
    UpdateRuleRequest,
    EvaluateRequest,
    EvaluationContext,
    CloneStrategyRequest,
)

router = APIRouter(prefix="/strategy", tags=["策略中心"])


# ========== 策略模板 API ==========

@router.get("/templates")
async def list_templates(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    """获取策略模板列表"""
    with get_db_session() as db:
        svc = StrategyTemplateService(db)
        items, total = svc.list_templates(
            page=page,
            page_size=page_size,
            category=category,
            keyword=keyword,
            is_active=is_active,
        )
        return paginated_response(
            items=[{
                "id": i.id,
                "name": i.name,
                "description": i.description,
                "category": i.category,
                "strategy_type": i.strategy_type,
                "is_active": i.is_active,
                "use_count": i.use_count,
                "created_at": i.created_at.isoformat() if i.created_at else None,
                "updated_at": i.updated_at.isoformat() if i.updated_at else None,
            } for i in items],
            total=total,
            page=page,
            page_size=page_size,
            trace_id=get_trace_id(),
        )


@router.get("/templates/{template_id}")
async def get_template(request: Request, template_id: int):
    """获取单个策略模板"""
    with get_db_session() as db:
        svc = StrategyTemplateService(db)
        template = svc.get_template(template_id)
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        return success_response(
            data={
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "strategy_type": template.strategy_type,
                "template_content": template.template_content,
                "variables": template.variables,
                "default_values": template.default_values,
                "tags": template.tags,
                "is_active": template.is_active,
                "use_count": template.use_count,
                "created_by": template.created_by,
                "created_at": template.created_at.isoformat() if template.created_at else None,
                "updated_at": template.updated_at.isoformat() if template.updated_at else None,
            },
            trace_id=get_trace_id(),
        )


@router.post("/templates")
async def create_template(request: Request):
    """创建策略模板"""
    with get_db_session() as db:
        body = await safe_json_body(request)
        req = CreateTemplateRequest(**body)
        operator = get_username()
        svc = StrategyTemplateService(db)
        try:
            template = svc.create_template(req, operator=operator)
            return success_response(
                data={"id": template.id, "name": template.name},
                trace_id=get_trace_id(),
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/templates/{template_id}")
async def update_template(request: Request, template_id: int):
    """更新策略模板"""
    with get_db_session() as db:
        body = await safe_json_body(request)
        req = UpdateTemplateRequest(**body)
        svc = StrategyTemplateService(db)
        template = svc.update_template(template_id, req)
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        return success_response(data={"id": template.id}, trace_id=get_trace_id())


@router.delete("/templates/{template_id}")
async def delete_template(request: Request, template_id: int):
    """删除策略模板"""
    with get_db_session() as db:
        svc = StrategyTemplateService(db)
        try:
            ok = svc.delete_template(template_id)
            if not ok:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
            return success_response(message="Template deleted", trace_id=get_trace_id())
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/templates/{template_id}/clone")
async def clone_template(request: Request, template_id: int):
    """克隆策略模板"""
    with get_db_session() as db:
        body = await safe_json_body(request)
        new_name = body.get("new_name")
        if not new_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="new_name is required")
        operator = get_username()
        svc = StrategyTemplateService(db)
        try:
            template = svc.clone_template(template_id, new_name, operator=operator)
            return success_response(data={"id": template.id, "name": template.name}, trace_id=get_trace_id())
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ========== 策略 API ==========

@router.get("/strategies")
async def list_strategies(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    strategy_type: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    x_tenant_id: Optional[str] = Header(None),
):
    """获取策略列表"""
    with get_db_session() as db:
        svc = StrategyService(db)
        items, total = svc.list_strategies(
            page=page,
            page_size=page_size,
            category=category,
            strategy_type=strategy_type,
            status=status,
            keyword=keyword,
            tenant_id=x_tenant_id,
        )
        return paginated_response(
            items=[{
                "id": i.id,
                "name": i.name,
                "description": i.description,
                "strategy_type": i.strategy_type,
                "category": i.category,
                "priority": i.priority,
                "status": i.status,
                "version": i.version,
                "is_locked": i.is_locked,
                "template_id": i.template_id,
                "created_by": i.created_by,
                "created_at": i.created_at.isoformat() if i.created_at else None,
                "updated_at": i.updated_at.isoformat() if i.updated_at else None,
            } for i in items],
            total=total,
            page=page,
            page_size=page_size,
            trace_id=get_trace_id(),
        )


@router.get("/strategies/{strategy_id}")
async def get_strategy(
    request: Request,
    strategy_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """获取单个策略"""
    with get_db_session() as db:
        svc = StrategyService(db)
        strategy = svc.get_strategy(strategy_id, tenant_id=x_tenant_id)
        if not strategy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
        return success_response(
            data={
                "id": strategy.id,
                "name": strategy.name,
                "description": strategy.description,
                "template_id": strategy.template_id,
                "strategy_type": strategy.strategy_type,
                "category": strategy.category,
                "priority": strategy.priority,
                "status": strategy.status,
                "scope": strategy.scope,
                "conditions": strategy.conditions,
                "actions": strategy.actions,
                "config": strategy.config,
                "tags": strategy.tags,
                "version": strategy.version,
                "is_locked": strategy.is_locked,
                "locked_by": strategy.locked_by,
                "locked_at": strategy.locked_at.isoformat() if strategy.locked_at else None,
                "published_at": strategy.published_at.isoformat() if strategy.published_at else None,
                "published_by": strategy.published_by,
                "tenant_id": strategy.tenant_id,
                "created_by": strategy.created_by,
                "created_at": strategy.created_at.isoformat() if strategy.created_at else None,
                "updated_at": strategy.updated_at.isoformat() if strategy.updated_at else None,
            },
            trace_id=get_trace_id(),
        )


@router.post("/strategies")
async def create_strategy(
    request: Request,
    x_tenant_id: Optional[str] = Header(None),
):
    """创建策略"""
    with get_db_session() as db:
        body = await safe_json_body(request)
        req = CreateStrategyRequest(**body)
        operator = get_username()
        svc = StrategyService(db)
        try:
            strategy = svc.create_strategy(req, operator=operator, tenant_id=x_tenant_id)
            return success_response(
                data={"id": strategy.id, "name": strategy.name, "version": strategy.version},
                trace_id=get_trace_id(),
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/strategies/{strategy_id}")
async def update_strategy(
    request: Request,
    strategy_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """更新策略"""
    with get_db_session() as db:
        body = await safe_json_body(request)
        req = UpdateStrategyRequest(**body)
        operator = get_username()
        operator_ip = request.client.host if request.client else None
        svc = StrategyService(db)
        try:
            strategy = svc.update_strategy(
                strategy_id, req,
                operator=operator,
                operator_ip=operator_ip,
                tenant_id=x_tenant_id,
            )
            return success_response(data={"id": strategy.id, "version": strategy.version}, trace_id=get_trace_id())
        except ValueError as e:
            if "not found" in str(e).lower():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
            if "locked" in str(e).lower():
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/strategies/{strategy_id}")
async def delete_strategy(
    request: Request,
    strategy_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """删除策略"""
    with get_db_session() as db:
        svc = StrategyService(db)
        try:
            ok = svc.delete_strategy(strategy_id, tenant_id=x_tenant_id)
            if not ok:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
            return success_response(message="Strategy deleted", trace_id=get_trace_id())
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/strategies/{strategy_id}/publish")
async def publish_strategy(
    request: Request,
    strategy_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """发布策略"""
    body = await safe_json_body(request) if request.method == "POST" else {}
    req = PublishStrategyRequest(**body) if body else PublishStrategyRequest()
    operator = get_username()
    operator_ip = request.client.host if request.client else None
    with get_db_session() as db:
        svc = StrategyService(db)
        try:
            strategy = svc.publish_strategy(
                strategy_id,
                operator=operator,
                operator_ip=operator_ip,
                tenant_id=x_tenant_id,
            )
            return success_response(
                data={"id": strategy.id, "version": strategy.version, "status": strategy.status},
                trace_id=get_trace_id(),
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/strategies/{strategy_id}/suspend")
async def suspend_strategy(
    request: Request,
    strategy_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """挂起策略"""
    operator = get_username()
    operator_ip = request.client.host if request.client else None
    with get_db_session() as db:
        svc = StrategyService(db)
        try:
            strategy = svc.suspend_strategy(
                strategy_id,
                operator=operator,
                operator_ip=operator_ip,
                tenant_id=x_tenant_id,
            )
            return success_response(
                data={"id": strategy.id, "status": strategy.status},
                trace_id=get_trace_id(),
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/strategies/{strategy_id}/activate")
async def activate_strategy(
    request: Request,
    strategy_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """激活策略（从挂起状态恢复）"""
    operator = get_username()
    operator_ip = request.client.host if request.client else None
    with get_db_session() as db:
        svc = StrategyService(db)
        try:
            strategy = svc.activate_strategy(
                strategy_id,
                operator=operator,
                operator_ip=operator_ip,
                tenant_id=x_tenant_id,
            )
            return success_response(
                data={"id": strategy.id, "status": strategy.status},
                trace_id=get_trace_id(),
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/strategies/{strategy_id}/rollback")
async def rollback_strategy(
    request: Request,
    strategy_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """回滚策略"""
    body = await safe_json_body(request) if request.method == "POST" else {}
    target_version = body.get("target_version")
    operator = get_username()
    operator_ip = request.client.host if request.client else None
    with get_db_session() as db:
        svc = StrategyService(db)
        try:
            strategy = svc.rollback_strategy(
                strategy_id,
                target_version=target_version,
                operator=operator,
                operator_ip=operator_ip,
                tenant_id=x_tenant_id,
            )
            return success_response(
                data={"id": strategy.id, "version": strategy.version},
                trace_id=get_trace_id(),
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/strategies/{strategy_id}/versions")
async def get_strategy_versions(
    request: Request,
    strategy_id: int,
    page: int = 1,
    page_size: int = 20,
    x_tenant_id: Optional[str] = Header(None),
):
    """获取策略版本历史"""
    with get_db_session() as db:
        svc = StrategyService(db)
        # 先检查策略是否存在
        strategy = svc.get_strategy(strategy_id, tenant_id=x_tenant_id)
        if not strategy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
        items, total = svc.get_strategy_versions(strategy_id, page=page, page_size=page_size)
        import json as _json
        def _parse_version(v):
            cfg = {}
            try:
                if v.config:
                    cfg = _json.loads(v.config) if isinstance(v.config, str) else v.config
            except Exception:
                pass
            return {
                "id": v.id,
                "strategy_id": v.strategy_id,
                "version": v.version,
                "name": cfg.get("name"),
                "description": cfg.get("description"),
                "strategy_type": cfg.get("strategy_type"),
                "category": cfg.get("category"),
                "priority": cfg.get("priority"),
                "status": cfg.get("status"),
                "change_type": v.change_type,
                "change_summary": v.change_summary,
                "operator": v.operator,
                "created_at": v.created_at.isoformat() if v.created_at else None,
            }
        return paginated_response(
            items=[_parse_version(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
            trace_id=get_trace_id(),
        )


@router.post("/strategies/{strategy_id}/lock")
async def lock_strategy(
    request: Request,
    strategy_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """锁定策略"""
    operator = get_username()
    with get_db_session() as db:
        svc = StrategyService(db)
        try:
            strategy = svc.lock_strategy(strategy_id, operator=operator, tenant_id=x_tenant_id)
            return success_response(
                data={"id": strategy.id, "is_locked": strategy.is_locked},
                trace_id=get_trace_id(),
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/strategies/{strategy_id}/unlock")
async def unlock_strategy(
    request: Request,
    strategy_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """解锁策略"""
    with get_db_session() as db:
        svc = StrategyService(db)
        try:
            strategy = svc.unlock_strategy(strategy_id, tenant_id=x_tenant_id)
            return success_response(
                data={"id": strategy.id, "is_locked": strategy.is_locked},
                trace_id=get_trace_id(),
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/strategies/{strategy_id}/clone")
async def clone_strategy(
    request: Request,
    strategy_id: int,
    x_tenant_id: Optional[str] = Header(None),
):
    """克隆策略"""
    body = await safe_json_body(request)
    req = CloneStrategyRequest(**body)
    operator = get_username()
    with get_db_session() as db:
        svc = StrategyService(db)
        try:
            strategy = svc.clone_strategy(
                strategy_id,
                new_name=req.new_name,
                operator=operator,
                tenant_id=x_tenant_id,
                clone_rules=req.clone_rules,
            )
            return success_response(
                data={"id": strategy.id, "name": strategy.name},
                trace_id=get_trace_id(),
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ========== 策略规则 API ==========

@router.get("/rules")
async def list_rules(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    rule_type: Optional[str] = None,
    condition_type: Optional[str] = None,
    action_type: Optional[str] = None,
    strategy_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    keyword: Optional[str] = None,
):
    """获取策略规则列表"""
    with get_db_session() as db:
        svc = StrategyRuleService(db)
        items, total = svc.list_rules(
            page=page,
            page_size=page_size,
            rule_type=rule_type,
            condition_type=condition_type,
            action_type=action_type,
            strategy_id=strategy_id,
            is_active=is_active,
            keyword=keyword,
        )
        return paginated_response(
            items=[{
                "id": i.id,
                "name": i.name,
                "description": i.description,
                "rule_type": i.rule_type,
                "condition_type": i.condition_type,
                "action_type": i.action_type,
                "priority": i.priority,
                "is_active": i.is_active,
                "is_system": i.is_system,
                "strategy_id": i.strategy_id,
                "created_by": i.created_by,
                "created_at": i.created_at.isoformat() if i.created_at else None,
                "updated_at": i.updated_at.isoformat() if i.updated_at else None,
            } for i in items],
            total=total,
            page=page,
            page_size=page_size,
            trace_id=get_trace_id(),
        )


@router.get("/rules/{rule_id}")
async def get_rule(request: Request, rule_id: int):
    """获取单个规则"""
    with get_db_session() as db:
        svc = StrategyRuleService(db)
        rule = svc.get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
        return success_response(
            data={
                "id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "rule_type": rule.rule_type,
                "condition_type": rule.condition_type,
                "conditions": rule.conditions,
                "condition_logic": rule.condition_logic,
                "action_type": rule.action_type,
                "action_config": rule.action_config,
                "priority": rule.priority,
                "is_active": rule.is_active,
                "is_system": rule.is_system,
                "strategy_id": rule.strategy_id,
                "tags": rule.tags,
                "created_by": rule.created_by,
                "created_at": rule.created_at.isoformat() if rule.created_at else None,
                "updated_at": rule.updated_at.isoformat() if rule.updated_at else None,
            },
            trace_id=get_trace_id(),
        )


@router.post("/rules")
async def create_rule(request: Request):
    """创建规则"""
    with get_db_session() as db:
        body = await safe_json_body(request)
        req = CreateRuleRequest(**body)
        operator = get_username()
        svc = StrategyRuleService(db)
        try:
            rule = svc.create_rule(req, operator=operator)
            return success_response(
                data={"id": rule.id, "name": rule.name},
                trace_id=get_trace_id(),
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/rules/{rule_id}")
async def update_rule(request: Request, rule_id: int):
    """更新规则"""
    with get_db_session() as db:
        body = await safe_json_body(request)
        req = UpdateRuleRequest(**body)
        svc = StrategyRuleService(db)
        rule = svc.update_rule(rule_id, req)
        if not rule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
        return success_response(data={"id": rule.id}, trace_id=get_trace_id())


@router.delete("/rules/{rule_id}")
async def delete_rule(request: Request, rule_id: int):
    """删除规则"""
    with get_db_session() as db:
        svc = StrategyRuleService(db)
        ok = svc.delete_rule(rule_id)
        if not ok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
        return success_response(message="Rule deleted", trace_id=get_trace_id())


@router.post("/rules/{rule_id}/test")
async def test_rule(request: Request, rule_id: int):
    """测试规则"""
    with get_db_session() as db:
        body = await safe_json_body(request)
        test_context = body.get("context", {})
        svc = StrategyRuleService(db)
        result = svc.test_rule(rule_id, test_context)
        return success_response(data=result, trace_id=get_trace_id())


# ========== 评估引擎 API ==========

@router.post("/evaluate")
async def evaluate_strategy(request: Request):
    """评估策略"""
    with get_db_session() as db:
        body = await safe_json_body(request)
        req = EvaluateRequest(**body)
        operator = get_username()
        evaluator = EvaluationEngine(db)
        result = evaluator.evaluate(req, operator=operator)
        return success_response(data=result, trace_id=get_trace_id())


@router.post("/evaluate/simulate")
async def simulate_strategy(request: Request):
    """模拟评估策略（不实际执行动作）"""
    with get_db_session() as db:
        body = await safe_json_body(request)
        req = EvaluateRequest(**body, simulate=True)
        operator = get_username()
        evaluator = EvaluationEngine(db)
        result = evaluator.evaluate(req, operator=operator)
        return success_response(data=result, trace_id=get_trace_id())


@router.get("/strategies/{strategy_id}/evaluations")
async def get_evaluation_history(
    request: Request,
    strategy_id: int,
    page: int = 1,
    page_size: int = 20,
    x_tenant_id: Optional[str] = Header(None),
):
    """获取评估历史"""
    with get_db_session() as db:
        svc = StrategyService(db)
        # 检查策略是否存在
        strategy = svc.get_strategy(strategy_id, tenant_id=x_tenant_id)
        if not strategy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
        evaluator = EvaluationEngine(db)
        items, total = evaluator.get_evaluation_history(strategy_id, page=page, page_size=page_size)
        return paginated_response(
            items=[{
                "id": i.id,
                "strategy_id": i.strategy_id,
                "strategy_version": i.strategy_version,
                "evaluation_context": i.evaluation_context,
                "triggered_conditions": i.triggered_conditions,
                "matched_rules": i.matched_rules,
                "actions_triggered": i.actions_triggered,
                "action_results": i.action_results,
                "evaluation_time_ms": i.evaluation_time_ms,
                "status": i.status,
                "error_message": i.error_message,
                "evaluated_by": i.evaluated_by,
                "created_at": i.created_at.isoformat() if i.created_at else None,
            } for i in items],
            total=total,
            page=page,
            page_size=page_size,
            trace_id=get_trace_id(),
        )
