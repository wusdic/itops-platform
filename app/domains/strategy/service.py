"""
策略中心 - Service 层

业务逻辑层，处理策略模板、策略规则、评估引擎的核心业务逻辑。
"""

import json
import re
import time
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.domains.strategy.schemas import (
    CreateTemplateRequest, UpdateTemplateRequest,
    CreateStrategyRequest, UpdateStrategyRequest,
    CreateRuleRequest, UpdateRuleRequest,
    EvaluateRequest, EvaluationContext,
)


class StrategyTemplateService:
    """策略模板服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_templates(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        keyword: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List, int]:
        """获取模板列表"""
        from app.domains.strategy.models import StrategyTemplate

        query = self.db.query(StrategyTemplate)
        if category:
            query = query.filter(StrategyTemplate.category == category)
        if keyword:
            query = query.filter(
                or_(
                    StrategyTemplate.name.like(f"%{keyword}%"),
                    StrategyTemplate.description.like(f"%{keyword}%")
                )
            )
        if is_active is not None:
            query = query.filter(StrategyTemplate.is_active == is_active)

        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(StrategyTemplate.updated_at.desc()).offset(offset).limit(page_size).all()
        return items, total

    def get_template(self, template_id: int) -> Optional[object]:
        """获取单个模板"""
        from app.domains.strategy.models import StrategyTemplate
        return self.db.query(StrategyTemplate).filter(StrategyTemplate.id == template_id).first()

    def create_template(self, req: CreateTemplateRequest, operator: str = None) -> object:
        """创建模板"""
        from app.domains.strategy.models import StrategyTemplate

        template = StrategyTemplate(
            name=req.name,
            description=req.description or "",
            category=req.category,
            strategy_type=req.strategy_type,
            template_content=json.dumps(req.template_content),
            variables=json.dumps([v.model_dump() for v in req.variables]) if req.variables else None,
            default_values=json.dumps(req.default_values) if req.default_values else None,
            tags=json.dumps(req.tags) if req.tags else None,
            created_by=operator,
        )
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def update_template(self, template_id: int, req: UpdateTemplateRequest) -> Optional[object]:
        """更新模板"""
        from app.domains.strategy.models import StrategyTemplate

        template = self.get_template(template_id)
        if not template:
            return None

        if req.name is not None:
            template.name = req.name
        if req.description is not None:
            template.description = req.description
        if req.category is not None:
            template.category = req.category
        if req.strategy_type is not None:
            template.strategy_type = req.strategy_type
        if req.template_content is not None:
            template.template_content = json.dumps(req.template_content)
        if req.variables is not None:
            template.variables = json.dumps([v.model_dump() for v in req.variables])
        if req.default_values is not None:
            template.default_values = json.dumps(req.default_values)
        if req.tags is not None:
            template.tags = json.dumps(req.tags)
        if req.is_active is not None:
            template.is_active = req.is_active

        template.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(template)
        return template

    def delete_template(self, template_id: int) -> bool:
        """删除模板"""
        from app.domains.strategy.models import StrategyTemplate

        template = self.get_template(template_id)
        if not template:
            return False

        # 检查是否有策略关联
        if template.strategies and len(template.strategies) > 0:
            raise ValueError("Cannot delete template that is in use by strategies")

        self.db.delete(template)
        self.db.commit()
        return True

    def clone_template(self, template_id: int, new_name: str, operator: str = None) -> object:
        """克隆模板"""
        from app.domains.strategy.models import StrategyTemplate

        original = self.get_template(template_id)
        if not original:
            raise ValueError("Template not found")

        cloned = StrategyTemplate(
            name=new_name,
            description=original.description,
            category=original.category,
            strategy_type=original.strategy_type,
            template_content=original.template_content,
            variables=original.variables,
            default_values=original.default_values,
            tags=original.tags,
            created_by=operator,
        )
        self.db.add(cloned)
        self.db.commit()
        self.db.refresh(cloned)
        return cloned


class StrategyService:
    """策略服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_strategies(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        strategy_type: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> Tuple[List, int]:
        """获取策略列表"""
        from app.domains.strategy.models import Strategy

        query = self.db.query(Strategy)
        if category:
            query = query.filter(Strategy.category == category)
        if strategy_type:
            query = query.filter(Strategy.strategy_type == strategy_type)
        if status:
            query = query.filter(Strategy.status == status)
        if keyword:
            query = query.filter(
                or_(
                    Strategy.name.like(f"%{keyword}%"),
                    Strategy.description.like(f"%{keyword}%")
                )
            )
        if tenant_id:
            query = query.filter(Strategy.tenant_id == tenant_id)

        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(Strategy.updated_at.desc()).offset(offset).limit(page_size).all()
        return items, total

    def get_strategy(self, strategy_id: int, tenant_id: Optional[str] = None) -> Optional[object]:
        """获取单个策略"""
        from app.domains.strategy.models import Strategy

        query = self.db.query(Strategy).filter(Strategy.id == strategy_id)
        if tenant_id:
            query = query.filter(Strategy.tenant_id == tenant_id)
        return query.first()

    def create_strategy(self, req: CreateStrategyRequest, operator: str = None, tenant_id: Optional[str] = None) -> object:
        """创建策略"""
        from app.domains.strategy.models import Strategy, StrategyVersion, ChangeType

        strategy = Strategy(
            name=req.name,
            description=req.description or "",
            template_id=req.template_id,
            strategy_type=req.strategy_type,
            category=req.category,
            priority=req.priority,
            status="draft",
            scope=json.dumps(req.scope) if req.scope else None,
            conditions=json.dumps([c.model_dump() for c in req.conditions]),
            actions=json.dumps([a.model_dump() for a in req.actions]),
            config=json.dumps(req.config) if req.config else None,
            tags=json.dumps(req.tags) if req.tags else None,
            tenant_id=tenant_id,
            created_by=operator,
        )
        self.db.add(strategy)
        self.db.flush()

        # 创建初始版本记录
        version = StrategyVersion(
            strategy_id=strategy.id,
            version=1,
            name=strategy.name,
            description=strategy.description,
            strategy_type=strategy.strategy_type,
            category=strategy.category,
            priority=strategy.priority,
            status=strategy.status,
            scope=strategy.scope,
            conditions=strategy.conditions,
            actions=strategy.actions,
            config=strategy.config,
            change_type=ChangeType.CREATE,
            change_summary="Initial creation",
            previous_values={},
            operator=operator,
        )
        self.db.add(version)

        # 更新模板使用次数
        if req.template_id:
            from app.domains.strategy.models import StrategyTemplate
            template = self.db.query(StrategyTemplate).filter(StrategyTemplate.id == req.template_id).first()
            if template:
                template.use_count += 1

        self.db.commit()
        self.db.refresh(strategy)
        return strategy

    def update_strategy(
        self,
        strategy_id: int,
        req: UpdateStrategyRequest,
        operator: str = None,
        operator_ip: str = None,
        tenant_id: Optional[str] = None,
    ) -> Optional[object]:
        """更新策略"""
        from app.domains.strategy.models import Strategy, StrategyVersion, ChangeType

        strategy = self.get_strategy(strategy_id, tenant_id)
        if not strategy:
            raise ValueError("Strategy not found")

        if strategy.is_locked:
            raise ValueError("Strategy is locked, cannot update")

        # 记录旧值
        old_values = {
            "name": strategy.name,
            "description": strategy.description,
            "priority": strategy.priority,
            "scope": strategy.scope,
            "conditions": strategy.conditions,
            "actions": strategy.actions,
            "config": strategy.config,
        }

        # 更新字段
        if req.name is not None:
            strategy.name = req.name
        if req.description is not None:
            strategy.description = req.description
        if req.strategy_type is not None:
            strategy.strategy_type = req.strategy_type
        if req.category is not None:
            strategy.category = req.category
        if req.priority is not None:
            strategy.priority = req.priority
        if req.scope is not None:
            strategy.scope = json.dumps(req.scope)
        if req.conditions is not None:
            strategy.conditions = json.dumps([c.model_dump() for c in req.conditions])
        if req.actions is not None:
            strategy.actions = json.dumps([a.model_dump() for a in req.actions])
        if req.config is not None:
            strategy.config = json.dumps(req.config)
        if req.tags is not None:
            strategy.tags = json.dumps(req.tags)

        strategy.version += 1
        strategy.updated_at = datetime.now()

        # 创建版本记录
        version = StrategyVersion(
            strategy_id=strategy.id,
            version=strategy.version,
            name=strategy.name,
            description=strategy.description,
            strategy_type=strategy.strategy_type,
            category=strategy.category,
            priority=strategy.priority,
            status=strategy.status,
            scope=strategy.scope,
            conditions=strategy.conditions,
            actions=strategy.actions,
            config=strategy.config,
            change_type=ChangeType.UPDATE,
            change_summary=req.change_summary or f"Updated to version {strategy.version}",
            previous_values=old_values,
            operator=operator,
            operator_ip=operator_ip,
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(strategy)
        return strategy

    def delete_strategy(self, strategy_id: int, tenant_id: Optional[str] = None) -> bool:
        """删除策略"""
        from app.domains.strategy.models import Strategy

        strategy = self.get_strategy(strategy_id, tenant_id)
        if not strategy:
            return False

        if strategy.is_locked:
            raise ValueError("Strategy is locked, cannot delete")

        if strategy.status == "active":
            raise ValueError("Cannot delete active strategy, please suspend it first")

        self.db.delete(strategy)
        self.db.commit()
        return True

    def publish_strategy(
        self,
        strategy_id: int,
        operator: str = None,
        operator_ip: str = None,
        tenant_id: Optional[str] = None,
    ) -> object:
        """发布策略"""
        from app.domains.strategy.models import Strategy, StrategyVersion, ChangeType

        strategy = self.get_strategy(strategy_id, tenant_id)
        if not strategy:
            raise ValueError("Strategy not found")

        if strategy.status == "active":
            raise ValueError("Strategy is already active")

        old_status = strategy.status
        strategy.status = "active"
        strategy.published_at = datetime.now()
        strategy.published_by = operator
        strategy.version += 1

        # 创建版本记录
        version = StrategyVersion(
            strategy_id=strategy.id,
            version=strategy.version,
            name=strategy.name,
            description=strategy.description,
            strategy_type=strategy.strategy_type,
            category=strategy.category,
            priority=strategy.priority,
            status=strategy.status,
            scope=strategy.scope,
            conditions=strategy.conditions,
            actions=strategy.actions,
            config=strategy.config,
            change_type=ChangeType.PUBLISH,
            change_summary=f"Published version {strategy.version}",
            previous_values={"status": old_status},
            operator=operator,
            operator_ip=operator_ip,
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(strategy)
        return strategy

    def suspend_strategy(
        self,
        strategy_id: int,
        operator: str = None,
        operator_ip: str = None,
        tenant_id: Optional[str] = None,
    ) -> object:
        """挂起策略"""
        from app.domains.strategy.models import Strategy, StrategyVersion, ChangeType

        strategy = self.get_strategy(strategy_id, tenant_id)
        if not strategy:
            raise ValueError("Strategy not found")

        if strategy.status != "active":
            raise ValueError("Only active strategy can be suspended")

        old_status = strategy.status
        strategy.status = "suspended"
        strategy.version += 1

        # 创建版本记录
        version = StrategyVersion(
            strategy_id=strategy.id,
            version=strategy.version,
            name=strategy.name,
            description=strategy.description,
            strategy_type=strategy.strategy_type,
            category=strategy.category,
            priority=strategy.priority,
            status=strategy.status,
            scope=strategy.scope,
            conditions=strategy.conditions,
            actions=strategy.actions,
            config=strategy.config,
            change_type=ChangeType.SUSPEND,
            change_summary="Strategy suspended",
            previous_values={"status": old_status},
            operator=operator,
            operator_ip=operator_ip,
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(strategy)
        return strategy

    def activate_strategy(
        self,
        strategy_id: int,
        operator: str = None,
        operator_ip: str = None,
        tenant_id: Optional[str] = None,
    ) -> object:
        """激活策略（从挂起状态恢复）"""
        from app.domains.strategy.models import Strategy, StrategyVersion, ChangeType

        strategy = self.get_strategy(strategy_id, tenant_id)
        if not strategy:
            raise ValueError("Strategy not found")

        if strategy.status != "suspended":
            raise ValueError("Only suspended strategy can be activated")

        old_status = strategy.status
        strategy.status = "active"
        strategy.version += 1

        # 创建版本记录
        version = StrategyVersion(
            strategy_id=strategy.id,
            version=strategy.version,
            name=strategy.name,
            description=strategy.description,
            strategy_type=strategy.strategy_type,
            category=strategy.category,
            priority=strategy.priority,
            status=strategy.status,
            scope=strategy.scope,
            conditions=strategy.conditions,
            actions=strategy.actions,
            config=strategy.config,
            change_type=ChangeType.ACTIVATE,
            change_summary="Strategy activated",
            previous_values={"status": old_status},
            operator=operator,
            operator_ip=operator_ip,
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(strategy)
        return strategy

    def rollback_strategy(
        self,
        strategy_id: int,
        target_version: int = None,
        operator: str = None,
        operator_ip: str = None,
        tenant_id: Optional[str] = None,
    ) -> object:
        """回滚策略"""
        from app.domains.strategy.models import Strategy, StrategyVersion, ChangeType

        strategy = self.get_strategy(strategy_id, tenant_id)
        if not strategy:
            raise ValueError("Strategy not found")

        # 获取历史版本
        versions = (
            self.db.query(StrategyVersion)
            .filter(StrategyVersion.strategy_id == strategy_id)
            .order_by(StrategyVersion.version.desc())
            .all()
        )

        if not versions:
            raise ValueError("No version history found")

        if target_version is None:
            # 回滚到上一版本
            target = versions[1] if len(versions) > 1 else versions[0]
        else:
            target = next((v for v in versions if v.version == target_version), None)

        if not target:
            raise ValueError(f"Target version {target_version} not found")

        # 记录当前值
        old_values = {
            "name": strategy.name,
            "description": strategy.description,
            "priority": strategy.priority,
            "scope": strategy.scope,
            "conditions": strategy.conditions,
            "actions": strategy.actions,
            "config": strategy.config,
        }

        # 执行回滚
        strategy.name = target.name
        strategy.description = target.description
        strategy.priority = target.priority
        strategy.scope = target.scope
        strategy.conditions = target.conditions
        strategy.actions = target.actions
        strategy.config = target.config
        strategy.version += 1

        # 创建回滚版本记录
        version = StrategyVersion(
            strategy_id=strategy.id,
            version=strategy.version,
            name=strategy.name,
            description=strategy.description,
            strategy_type=strategy.strategy_type,
            category=strategy.category,
            priority=strategy.priority,
            status=strategy.status,
            scope=strategy.scope,
            conditions=strategy.conditions,
            actions=strategy.actions,
            config=strategy.config,
            change_type=ChangeType.ROLLBACK,
            change_summary=f"Rolled back to version {target.version}",
            previous_values=old_values,
            operator=operator,
            operator_ip=operator_ip,
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(strategy)
        return strategy

    def get_strategy_versions(
        self,
        strategy_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List, int]:
        """获取策略版本历史"""
        from app.domains.strategy.models import StrategyVersion

        query = self.db.query(StrategyVersion).filter(StrategyVersion.strategy_id == strategy_id)
        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(StrategyVersion.version.desc()).offset(offset).limit(page_size).all()
        return items, total

    def lock_strategy(self, strategy_id: int, operator: str = None, tenant_id: Optional[str] = None) -> object:
        """锁定策略"""
        from app.domains.strategy.models import Strategy

        strategy = self.get_strategy(strategy_id, tenant_id)
        if not strategy:
            raise ValueError("Strategy not found")

        strategy.is_locked = True
        strategy.locked_by = operator
        strategy.locked_at = datetime.now()
        self.db.commit()
        self.db.refresh(strategy)
        return strategy

    def unlock_strategy(self, strategy_id: int, tenant_id: Optional[str] = None) -> object:
        """解锁策略"""
        from app.domains.strategy.models import Strategy

        strategy = self.get_strategy(strategy_id, tenant_id)
        if not strategy:
            raise ValueError("Strategy not found")

        strategy.is_locked = False
        strategy.locked_by = None
        strategy.locked_at = None
        self.db.commit()
        self.db.refresh(strategy)
        return strategy

    def clone_strategy(
        self,
        strategy_id: int,
        new_name: str,
        operator: str = None,
        tenant_id: Optional[str] = None,
        clone_rules: bool = True,
    ) -> object:
        """克隆策略"""
        from app.domains.strategy.models import Strategy, StrategyVersion, StrategyRule, ChangeType

        original = self.get_strategy(strategy_id, tenant_id)
        if not original:
            raise ValueError("Strategy not found")

        # 创建新策略
        cloned = Strategy(
            name=new_name,
            description=original.description,
            template_id=original.template_id,
            strategy_type=original.strategy_type,
            category=original.category,
            priority=original.priority,
            status="draft",
            scope=original.scope,
            conditions=original.conditions,
            actions=original.actions,
            config=original.config,
            tags=original.tags,
            tenant_id=tenant_id,
            created_by=operator,
        )
        self.db.add(cloned)
        self.db.flush()

        # 创建初始版本记录
        version = StrategyVersion(
            strategy_id=cloned.id,
            version=1,
            name=cloned.name,
            description=cloned.description,
            strategy_type=cloned.strategy_type,
            category=cloned.category,
            priority=cloned.priority,
            status=cloned.status,
            scope=cloned.scope,
            conditions=cloned.conditions,
            actions=cloned.actions,
            config=cloned.config,
            change_type=ChangeType.CLONE,
            change_summary=f"Cloned from strategy {strategy_id}",
            previous_values={},
            operator=operator,
        )
        self.db.add(version)

        # 克隆规则
        if clone_rules:
            rules = self.db.query(StrategyRule).filter(StrategyRule.strategy_id == strategy_id).all()
            for rule in rules:
                cloned_rule = StrategyRule(
                    name=rule.name,
                    description=rule.description,
                    rule_type=rule.rule_type,
                    condition_type=rule.condition_type,
                    conditions=rule.conditions,
                    condition_logic=rule.condition_logic,
                    action_type=rule.action_type,
                    action_config=rule.action_config,
                    priority=rule.priority,
                    strategy_id=cloned.id,
                    tags=rule.tags,
                    created_by=operator,
                )
                self.db.add(cloned_rule)

        self.db.commit()
        self.db.refresh(cloned)
        return cloned


class StrategyRuleService:
    """策略规则服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_rules(
        self,
        page: int = 1,
        page_size: int = 20,
        rule_type: Optional[str] = None,
        condition_type: Optional[str] = None,
        action_type: Optional[str] = None,
        strategy_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        keyword: Optional[str] = None,
    ) -> Tuple[List, int]:
        """获取规则列表"""
        from app.domains.strategy.models import StrategyRule

        query = self.db.query(StrategyRule)
        if rule_type:
            query = query.filter(StrategyRule.rule_type == rule_type)
        if condition_type:
            query = query.filter(StrategyRule.condition_type == condition_type)
        if action_type:
            query = query.filter(StrategyRule.action_type == action_type)
        if strategy_id:
            query = query.filter(StrategyRule.strategy_id == strategy_id)
        if is_active is not None:
            query = query.filter(StrategyRule.is_active == is_active)
        if keyword:
            query = query.filter(
                or_(
                    StrategyRule.name.like(f"%{keyword}%"),
                    StrategyRule.description.like(f"%{keyword}%")
                )
            )

        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(StrategyRule.priority.asc(), StrategyRule.id.desc()).offset(offset).limit(page_size).all()
        return items, total

    def get_rule(self, rule_id: int) -> Optional[object]:
        """获取单个规则"""
        from app.domains.strategy.models import StrategyRule
        return self.db.query(StrategyRule).filter(StrategyRule.id == rule_id).first()

    def create_rule(self, req: CreateRuleRequest, operator: str = None) -> object:
        """创建规则"""
        from app.domains.strategy.models import StrategyRule

        rule = StrategyRule(
            name=req.name,
            description=req.description or "",
            rule_type=req.rule_type,
            condition_type=req.condition_type,
            conditions=json.dumps([c.model_dump() for c in req.conditions]),
            condition_logic=req.condition_logic,
            action_type=req.action_type,
            action_config=json.dumps(req.action_config),
            priority=req.priority,
            strategy_id=req.strategy_id,
            tags=json.dumps(req.tags) if req.tags else None,
            created_by=operator,
        )
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def update_rule(self, rule_id: int, req: UpdateRuleRequest) -> Optional[object]:
        """更新规则"""
        from app.domains.strategy.models import StrategyRule

        rule = self.get_rule(rule_id)
        if not rule:
            return None

        if req.name is not None:
            rule.name = req.name
        if req.description is not None:
            rule.description = req.description
        if req.rule_type is not None:
            rule.rule_type = req.rule_type
        if req.condition_type is not None:
            rule.condition_type = req.condition_type
        if req.conditions is not None:
            rule.conditions = json.dumps([c.model_dump() for c in req.conditions])
        if req.condition_logic is not None:
            rule.condition_logic = req.condition_logic
        if req.action_type is not None:
            rule.action_type = req.action_type
        if req.action_config is not None:
            rule.action_config = json.dumps(req.action_config)
        if req.priority is not None:
            rule.priority = req.priority
        if req.is_active is not None:
            rule.is_active = req.is_active
        if req.tags is not None:
            rule.tags = json.dumps(req.tags)

        rule.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete_rule(self, rule_id: int) -> bool:
        """删除规则"""
        from app.domains.strategy.models import StrategyRule

        rule = self.get_rule(rule_id)
        if not rule:
            return False

        self.db.delete(rule)
        self.db.commit()
        return True

    def test_rule(self, rule_id: int, test_context: Dict[str, Any]) -> Dict[str, Any]:
        """测试规则"""
        from app.domains.strategy.models import StrategyRule

        rule = self.get_rule(rule_id)
        if not rule:
            return {"success": False, "error": "Rule not found"}

        # 使用评估引擎测试
        evaluator = EvaluationEngine(self.db)
        result = evaluator.evaluate_rule(rule, test_context)
        return result


class EvaluationEngine:
    """评估引擎"""

    OPERATORS = {
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
        ">": lambda a, b: float(a) > float(b),
        "<": lambda a, b: float(a) < float(b),
        ">=": lambda a, b: float(a) >= float(b),
        "<=": lambda a, b: float(a) <= float(b),
        "in": lambda a, b: a in b,
        "not_in": lambda a, b: a not in b,
        "contains": lambda a, b: b in str(a),
        "regex": lambda a, b: bool(re.match(b, str(a))),
    }

    def __init__(self, db: Session):
        self.db = db

    def evaluate(self, req: EvaluateRequest, operator: str = None) -> Dict[str, Any]:
        """评估策略"""
        from app.domains.strategy.models import Strategy, EvaluationResult

        strategy_ids = req.strategy_ids or ([req.strategy_id] if req.strategy_id else [])
        
        if not strategy_ids:
            return {
                "success": False,
                "error": "No strategy specified",
                "results": []
            }

        results = []
        for strategy_id in strategy_ids:
            strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                results.append({
                    "strategy_id": strategy_id,
                    "success": False,
                    "error": "Strategy not found"
                })
                continue

            if strategy.status != "active":
                results.append({
                    "strategy_id": strategy_id,
                    "strategy_version": strategy.version,
                    "success": True,
                    "triggered": False,
                    "message": f"Strategy is {strategy.status}, not evaluated"
                })
                continue

            start_time = time.time()
            try:
                # 解析条件和动作
                conditions = json.loads(strategy.conditions) if isinstance(strategy.conditions, str) else strategy.conditions
                actions = json.loads(strategy.actions) if isinstance(strategy.actions, str) else strategy.actions

                # 执行评估
                result = self._evaluate_conditions(conditions, req.context)

                evaluation_time_ms = int((time.time() - start_time) * 1000)

                if result["triggered"]:
                    # 触发动作
                    action_results = self._execute_actions(actions, req.context, simulate=req.simulate)

                    evaluation_record = EvaluationResult(
                        strategy_id=strategy.id,
                        strategy_version=strategy.version,
                        evaluation_context=req.context.model_dump(),
                        triggered_conditions=json.dumps(result["matched"]),
                        matched_rules=json.dumps([]),
                        actions_triggered=json.dumps(actions) if req.simulate else None,
                        action_results=json.dumps(action_results) if req.simulate else None,
                        evaluation_time_ms=evaluation_time_ms,
                        status="success" if all(r.get("success", False) for r in action_results) else "partial",
                        evaluated_by=operator,
                    )
                    self.db.add(evaluation_record)
                    self.db.commit()

                    results.append({
                        "strategy_id": strategy.id,
                        "strategy_version": strategy.version,
                        "success": True,
                        "triggered": True,
                        "matched_conditions": result["matched"],
                        "triggered_actions": actions,
                        "action_results": action_results,
                        "evaluation_time_ms": evaluation_time_ms,
                        "message": "Strategy triggered successfully"
                    })
                else:
                    results.append({
                        "strategy_id": strategy.id,
                        "strategy_version": strategy.version,
                        "success": True,
                        "triggered": False,
                        "matched_conditions": [],
                        "evaluation_time_ms": evaluation_time_ms,
                        "message": "No conditions matched"
                    })

            except Exception as e:
                evaluation_time_ms = int((time.time() - start_time) * 1000)
                
                # 记录失败评估
                evaluation_record = EvaluationResult(
                    strategy_id=strategy.id,
                    strategy_version=strategy.version,
                    evaluation_context=req.context.model_dump(),
                    evaluation_time_ms=evaluation_time_ms,
                    status="failed",
                    error_message=str(e),
                    evaluated_by=operator,
                )
                self.db.add(evaluation_record)
                self.db.commit()

                results.append({
                    "strategy_id": strategy.id,
                    "success": False,
                    "error": str(e),
                    "evaluation_time_ms": evaluation_time_ms
                })

        return {
            "success": True,
            "results": results,
            "total": len(results)
        }

    def _evaluate_conditions(self, conditions: List[Dict], context: EvaluationContext) -> Dict[str, Any]:
        """评估条件"""
        matched = []
        all_matched = True

        for condition in conditions:
            cond_result = self._evaluate_single_condition(condition, context)
            if cond_result:
                matched.append(condition.get("description") or condition.get("field"))
            else:
                all_matched = False

        return {
            "triggered": all_matched and len(conditions) > 0,
            "matched": matched
        }

    def _evaluate_single_condition(self, condition: Dict, context: EvaluationContext) -> bool:
        """评估单个条件"""
        cond_type = condition.get("type")
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")

        # 获取字段值
        field_value = self._get_field_value(field, context)

        # 执行比较
        op_func = self.OPERATORS.get(operator)
        if not op_func:
            return False

        try:
            return op_func(field_value, value)
        except (ValueError, TypeError):
            return False

    def _get_field_value(self, field: str, context: EvaluationContext) -> Any:
        """获取字段值"""
        context_dict = context.model_dump()

        # 支持嵌套字段访问 (e.g., "metrics.cpu_usage")
        parts = field.split(".")
        value = context_dict

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return None

        return value

    def _execute_actions(self, actions: List[Dict], context: EvaluationContext, simulate: bool = False) -> List[Dict[str, Any]]:
        """执行动作"""
        results = []

        for action in actions:
            action_type = action.get("type")
            action_config = action.get("config", {})

            if simulate:
                results.append({
                    "action_type": action_type,
                    "success": True,
                    "simulated": True,
                    "message": f"Action {action_type} would be executed"
                })
            else:
                # 根据动作类型执行
                try:
                    result = self._execute_single_action(action_type, action_config, context)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "action_type": action_type,
                        "success": False,
                        "error": str(e)
                    })

        return results

    def _execute_single_action(self, action_type: str, config: Dict, context: EvaluationContext) -> Dict[str, Any]:
        """执行单个动作"""
        if action_type == "alert":
            return self._execute_alert_action(config, context)
        elif action_type == "notify":
            return self._execute_notify_action(config, context)
        elif action_type == "webhook":
            return self._execute_webhook_action(config, context)
        elif action_type == "ticket":
            return self._execute_ticket_action(config, context)
        elif action_type == "escalate":
            return self._execute_escalate_action(config, context)
        elif action_type == "auto_fix":
            return self._execute_auto_fix_action(config, context)
        else:
            return {"action_type": action_type, "success": False, "error": f"Unknown action type: {action_type}"}

    def _execute_alert_action(self, config: Dict, context: EvaluationContext) -> Dict[str, Any]:
        """执行告警动作"""
        # 实际实现会调用告警服务
        return {
            "action_type": "alert",
            "success": True,
            "alert_id": f"alert-{datetime.now().timestamp()}",
            "message": "Alert created"
        }

    def _execute_notify_action(self, config: Dict, context: EvaluationContext) -> Dict[str, Any]:
        """执行通知动作"""
        # 实际实现会调用通知服务
        return {
            "action_type": "notify",
            "success": True,
            "notification_id": f"notify-{datetime.now().timestamp()}",
            "message": "Notification sent"
        }

    def _execute_webhook_action(self, config: Dict, context: EvaluationContext) -> Dict[str, Any]:
        """执行Webhook动作"""
        url = config.get("url")
        method = config.get("method", "POST")
        # 实际实现会发送HTTP请求
        return {
            "action_type": "webhook",
            "success": True,
            "url": url,
            "method": method,
            "message": "Webhook called"
        }

    def _execute_ticket_action(self, config: Dict, context: EvaluationContext) -> Dict[str, Any]:
        """执行工单动作"""
        # 实际实现会创建工单
        return {
            "action_type": "ticket",
            "success": True,
            "ticket_id": f"ticket-{datetime.now().timestamp()}",
            "message": "Ticket created"
        }

    def _execute_escalate_action(self, config: Dict, context: EvaluationContext) -> Dict[str, Any]:
        """执行升级动作"""
        level = config.get("level", "high")
        return {
            "action_type": "escalate",
            "success": True,
            "level": level,
            "message": f"Escalated to {level}"
        }

    def _execute_auto_fix_action(self, config: Dict, context: EvaluationContext) -> Dict[str, Any]:
        """执行自动修复动作"""
        fix_type = config.get("fix_type", "default")
        return {
            "action_type": "auto_fix",
            "success": True,
            "fix_type": fix_type,
            "message": f"Auto fix {fix_type} executed"
        }

    def evaluate_rule(self, rule, test_context: Dict[str, Any]) -> Dict[str, Any]:
        """测试规则"""
        conditions = json.loads(rule.conditions) if isinstance(rule.conditions, str) else rule.conditions

        # 转换为EvaluationContext
        context = EvaluationContext(**test_context)

        # 评估条件
        result = self._evaluate_conditions(conditions, context)

        return {
            "success": True,
            "rule_id": rule.id,
            "rule_name": rule.name,
            "matched": result["matched"],
            "triggered": result["triggered"],
            "action_type": rule.action_type,
            "action_config": json.loads(rule.action_config) if isinstance(rule.action_config, str) else rule.action_config
        }

    def get_evaluation_history(
        self,
        strategy_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List, int]:
        """获取评估历史"""
        from app.domains.strategy.models import EvaluationResult

        query = self.db.query(EvaluationResult).filter(EvaluationResult.strategy_id == strategy_id)
        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(EvaluationResult.created_at.desc()).offset(offset).limit(page_size).all()
        return items, total
