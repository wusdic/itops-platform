"""
策略中心 - Pydantic Schemas

提供策略模板、策略规则、评估引擎的请求/响应模型。
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class StrategyStatus(str, Enum):
    """策略状态"""
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class StrategyPriority(str, Enum):
    """策略优先级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RuleConditionType(str, Enum):
    """规则条件类型"""
    THRESHOLD = "threshold"
    TIME_RANGE = "time_range"
    DEVICE_TYPE = "device_type"
    METRIC = "metric"
    EVENT = "event"
    CUSTOM = "custom"


class RuleActionType(str, Enum):
    """规则动作类型"""
    ALERT = "alert"
    NOTIFY = "notify"
    WEBHOOK = "webhook"
    AUTO_FIX = "auto_fix"
    ESCALATE = "escalate"
    TICKET = "ticket"


class ChangeType(str, Enum):
    """变更类型"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    PUBLISH = "publish"
    SUSPEND = "suspend"
    ACTIVATE = "activate"
    ROLLBACK = "rollback"
    CLONE = "clone"


# ========== 策略模板 Schema ==========

class ConditionExpression(BaseModel):
    """条件表达式"""
    type: str = Field(..., description="条件类型: threshold, time_range, device_type, metric, event, custom")
    field: str = Field(..., description="字段名")
    operator: str = Field(..., description="操作符: ==, !=, >, <, >=, <=, in, not_in, contains, regex")
    value: Any = Field(..., description="比较值")
    description: Optional[str] = Field(None, description="条件描述")


class ActionConfig(BaseModel):
    """动作配置"""
    type: str = Field(..., description="动作类型: alert, notify, webhook, auto_fix, escalate, ticket")
    config: Dict[str, Any] = Field(default_factory=dict, description="动作配置参数")
    order: int = Field(default=1, description="执行顺序")


class TemplateVariable(BaseModel):
    """模板变量定义"""
    name: str = Field(..., description="变量名")
    type: str = Field(default="string", description="变量类型")
    description: Optional[str] = Field(None, description="变量描述")
    default: Any = Field(None, description="默认值")
    options: Optional[List[Any]] = Field(None, description="可选值列表")
    required: bool = Field(default=True, description="是否必填")


class CreateTemplateRequest(BaseModel):
    """创建策略模板请求"""
    name: str = Field(..., min_length=1, max_length=128, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    category: Optional[str] = Field(None, description="模板分类")
    strategy_type: Optional[str] = Field(None, description="策略类型")
    template_content: Dict[str, Any] = Field(..., description="模板内容")
    variables: Optional[List[TemplateVariable]] = Field(None, description="模板变量")
    default_values: Optional[Dict[str, Any]] = Field(None, description="默认变量值")
    tags: Optional[List[str]] = Field(None, description="标签")


class UpdateTemplateRequest(BaseModel):
    """更新策略模板请求"""
    name: Optional[str] = Field(None, max_length=128, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    category: Optional[str] = Field(None, description="模板分类")
    strategy_type: Optional[str] = Field(None, description="策略类型")
    template_content: Optional[Dict[str, Any]] = Field(None, description="模板内容")
    variables: Optional[List[TemplateVariable]] = Field(None, description="模板变量")
    default_values: Optional[Dict[str, Any]] = Field(None, description="默认变量值")
    tags: Optional[List[str]] = Field(None, description="标签")
    is_active: Optional[bool] = Field(None, description="是否启用")


class TemplateResponse(BaseModel):
    """模板响应"""
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    strategy_type: Optional[str] = None
    template_content: Dict[str, Any] = Field(default_factory=dict)
    variables: Optional[List[Dict[str, Any]]] = None
    default_values: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_active: bool = True
    use_count: int = 0
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TemplateListItem(BaseModel):
    """模板列表项"""
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    strategy_type: Optional[str] = None
    is_active: bool
    use_count: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== 策略 Schema ==========

class CreateStrategyRequest(BaseModel):
    """创建策略请求"""
    name: str = Field(..., min_length=1, max_length=128, description="策略名称")
    description: Optional[str] = Field(None, description="策略描述")
    template_id: Optional[int] = Field(None, description="关联模板ID")
    strategy_type: str = Field(..., description="策略类型")
    category: Optional[str] = Field(None, description="策略分类")
    priority: str = Field(default="medium", description="优先级: critical, high, medium, low")
    scope: Optional[Dict[str, Any]] = Field(None, description="策略范围")
    conditions: List[ConditionExpression] = Field(..., description="触发条件")
    actions: List[ActionConfig] = Field(..., description="执行动作")
    config: Optional[Dict[str, Any]] = Field(None, description="策略配置")
    tags: Optional[List[str]] = Field(None, description="标签")


class UpdateStrategyRequest(BaseModel):
    """更新策略请求"""
    name: Optional[str] = Field(None, max_length=128, description="策略名称")
    description: Optional[str] = Field(None, description="策略描述")
    strategy_type: Optional[str] = Field(None, description="策略类型")
    category: Optional[str] = Field(None, description="策略分类")
    priority: Optional[str] = Field(None, description="优先级")
    scope: Optional[Dict[str, Any]] = Field(None, description="策略范围")
    conditions: Optional[List[ConditionExpression]] = Field(None, description="触发条件")
    actions: Optional[List[ActionConfig]] = Field(None, description="执行动作")
    config: Optional[Dict[str, Any]] = Field(None, description="策略配置")
    tags: Optional[List[str]] = Field(None, description="标签")
    change_summary: Optional[str] = Field(None, description="变更摘要")


class PublishStrategyRequest(BaseModel):
    """发布策略请求"""
    change_summary: Optional[str] = Field(None, description="发布说明")


class RollbackStrategyRequest(BaseModel):
    """回滚策略请求"""
    target_version: Optional[int] = Field(None, description="目标版本号")


class StrategyResponse(BaseModel):
    """策略响应"""
    id: int
    name: str
    description: Optional[str] = None
    template_id: Optional[int] = None
    strategy_type: str
    category: Optional[str] = None
    priority: str
    status: str
    scope: Optional[Dict[str, Any]] = None
    conditions: List[Dict[str, Any]] = Field(default_factory=list)
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    config: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    version: int
    is_locked: bool
    locked_by: Optional[str] = None
    locked_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    published_by: Optional[str] = None
    tenant_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StrategyListItem(BaseModel):
    """策略列表项"""
    id: int
    name: str
    description: Optional[str] = None
    strategy_type: str
    category: Optional[str] = None
    priority: str
    status: str
    version: int
    is_locked: bool
    template_id: Optional[int] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StrategyVersionResponse(BaseModel):
    """策略版本响应"""
    id: int
    strategy_id: int
    version: int
    name: str
    description: Optional[str] = None
    strategy_type: str
    category: Optional[str] = None
    priority: str
    status: str
    scope: Optional[Dict[str, Any]] = None
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    config: Optional[Dict[str, Any]] = None
    change_type: str
    change_summary: Optional[str] = None
    previous_version_id: Optional[int] = None
    operator: Optional[str] = None
    operator_ip: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== 策略规则 Schema ==========

class CreateRuleRequest(BaseModel):
    """创建规则请求"""
    name: str = Field(..., min_length=1, max_length=128, description="规则名称")
    description: Optional[str] = Field(None, description="规则描述")
    rule_type: str = Field(..., description="规则类型")
    condition_type: str = Field(..., description="条件类型")
    conditions: List[ConditionExpression] = Field(..., description="条件表达式")
    condition_logic: str = Field(default="AND", description="条件逻辑 AND/OR")
    action_type: str = Field(..., description="动作类型")
    action_config: Dict[str, Any] = Field(..., description="动作配置")
    priority: int = Field(default=100, description="优先级")
    strategy_id: Optional[int] = Field(None, description="关联策略ID")
    tags: Optional[List[str]] = Field(None, description="标签")


class UpdateRuleRequest(BaseModel):
    """更新规则请求"""
    name: Optional[str] = Field(None, description="规则名称")
    description: Optional[str] = Field(None, description="规则描述")
    rule_type: Optional[str] = Field(None, description="规则类型")
    condition_type: Optional[str] = Field(None, description="条件类型")
    conditions: Optional[List[ConditionExpression]] = Field(None, description="条件表达式")
    condition_logic: Optional[str] = Field(None, description="条件逻辑 AND/OR")
    action_type: Optional[str] = Field(None, description="动作类型")
    action_config: Optional[Dict[str, Any]] = Field(None, description="动作配置")
    priority: Optional[int] = Field(None, description="优先级")
    is_active: Optional[bool] = Field(None, description="是否启用")
    tags: Optional[List[str]] = Field(None, description="标签")


class RuleResponse(BaseModel):
    """规则响应"""
    id: int
    name: str
    description: Optional[str] = None
    rule_type: str
    condition_type: str
    conditions: List[Dict[str, Any]]
    condition_logic: str
    action_type: str
    action_config: Dict[str, Any]
    priority: int
    is_active: bool
    is_system: bool
    strategy_id: Optional[int] = None
    tags: Optional[List[str]] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== 评估引擎 Schema ==========

class EvaluationContext(BaseModel):
    """评估上下文"""
    device_id: Optional[int] = Field(None, description="设备ID")
    device_name: Optional[str] = Field(None, description="设备名称")
    device_type: Optional[str] = Field(None, description="设备类型")
    host: Optional[str] = Field(None, description="主机名/IP")
    metrics: Optional[Dict[str, float]] = Field(None, description="指标数据")
    events: Optional[List[Dict[str, Any]]] = Field(None, description="事件列表")
    timestamp: Optional[datetime] = Field(None, description="评估时间")
    custom_data: Optional[Dict[str, Any]] = Field(None, description="自定义数据")


class EvaluateRequest(BaseModel):
    """评估请求"""
    strategy_id: Optional[int] = Field(None, description="策略ID")
    strategy_ids: Optional[List[int]] = Field(None, description="策略ID列表")
    context: EvaluationContext = Field(..., description="评估上下文")
    simulate: bool = Field(default=False, description="是否模拟执行")


class EvaluateResponse(BaseModel):
    """评估响应"""
    success: bool
    strategy_id: int
    strategy_version: int
    triggered: bool
    matched_conditions: List[str] = Field(default_factory=list)
    triggered_actions: List[Dict[str, Any]] = Field(default_factory=list)
    action_results: Dict[str, Any] = Field(default_factory=dict)
    evaluation_time_ms: int
    message: str
    error: Optional[str] = None

    class Config:
        from_attributes = True


class EvaluationHistoryResponse(BaseModel):
    """评估历史响应"""
    id: int
    strategy_id: int
    strategy_version: int
    evaluation_context: Dict[str, Any]
    triggered_conditions: Optional[List[str]] = None
    matched_rules: Optional[List[str]] = None
    actions_triggered: Optional[List[Dict[str, Any]]] = None
    action_results: Optional[Dict[str, Any]] = None
    evaluation_time_ms: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    evaluated_by: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== 批量操作 Schema ==========

class CloneStrategyRequest(BaseModel):
    """克隆策略请求"""
    strategy_id: int = Field(..., description="源策略ID")
    new_name: str = Field(..., description="新策略名称")
    clone_rules: bool = Field(default=True, description="是否克隆关联规则")
