"""
策略中心 - 数据库模型

定义策略模板、策略规则和策略版本的数据库模型。
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    JSON, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from modules.foundation.db_models.base import Base, db_session
import enum


class StrategyStatus(str, enum.Enum):
    """策略状态"""
    DRAFT = "draft"           # 草稿
    ACTIVE = "active"         # 生效中
    SUSPENDED = "suspended"    # 已挂起
    ARCHIVED = "archived"     # 已归档


class StrategyPriority(str, enum.Enum):
    """策略优先级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RuleConditionType(str, enum.Enum):
    """规则条件类型"""
    THRESHOLD = "threshold"        # 阈值条件
    TIME_RANGE = "time_range"      # 时间范围
    DEVICE_TYPE = "device_type"    # 设备类型
    METRIC = "metric"             # 指标条件
    EVENT = "event"                # 事件条件
    CUSTOM = "custom"             # 自定义条件


class RuleActionType(str, enum.Enum):
    """规则动作类型"""
    ALERT = "alert"               # 告警
    NOTIFY = "notify"             # 通知
    WEBHOOK = "webhook"           # Webhook调用
    AUTO_FIX = "auto_fix"         # 自动修复
    ESCALATE = "escalate"         # 升级
    TICKET = "ticket"            # 创建工单


class ChangeType(str, enum.Enum):
    """变更类型"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    PUBLISH = "publish"
    SUSPEND = "suspend"
    ACTIVATE = "activate"
    ROLLBACK = "rollback"
    CLONE = "clone"


class StrategyTemplate(Base):
    """策略模板"""
    __tablename__ = "strategy_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, comment="模板名称")
    description = Column(Text, nullable=True, comment="模板描述")
    category = Column(String(64), nullable=True, comment="模板分类")
    strategy_type = Column(String(64), nullable=True, comment="策略类型")
    template_content = Column(JSON, nullable=False, comment="模板内容（规则骨架）")
    variables = Column(JSON, nullable=True, comment="模板变量定义")
    default_values = Column(JSON, nullable=True, comment="默认变量值")
    tags = Column(JSON, nullable=True, comment="标签列表")
    is_active = Column(Boolean, default=True, comment="是否启用")
    use_count = Column(Integer, default=0, comment="使用次数")
    created_by = Column(String(64), nullable=True, comment="创建人")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class Strategy(Base):
    """策略主表"""
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, comment="策略名称")
    description = Column(Text, nullable=True, comment="策略描述")
    template_id = Column(Integer, ForeignKey("strategy_templates.id"), nullable=True, comment="关联模板ID")
    strategy_type = Column(String(64), nullable=False, comment="策略类型")
    category = Column(String(64), nullable=True, comment="策略分类")
    priority = Column(SQLEnum(StrategyPriority), default=StrategyPriority.MEDIUM, comment="优先级")
    status = Column(SQLEnum(StrategyStatus), default=StrategyStatus.DRAFT, comment="状态")
    scope = Column(JSON, nullable=True, comment="策略范围（设备/分组/标签）")
    conditions = Column(JSON, nullable=False, comment="触发条件")
    actions = Column(JSON, nullable=False, comment="执行动作")
    config = Column(JSON, nullable=True, comment="策略配置")
    tags = Column(JSON, nullable=True, comment="标签列表")
    version = Column(Integer, default=1, comment="当前版本号")
    is_locked = Column(Boolean, default=False, comment="是否锁定")
    locked_by = Column(String(64), nullable=True, comment="锁定人")
    locked_at = Column(DateTime, nullable=True, comment="锁定时间")
    published_at = Column(DateTime, nullable=True, comment="发布时间")
    published_by = Column(String(64), nullable=True, comment="发布人")
    tenant_id = Column(String(64), nullable=True, comment="租户ID")
    created_by = Column(String(64), nullable=True, comment="创建人")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    template = relationship("StrategyTemplate", backref="strategies")
    versions = relationship("StrategyVersion", back_populates="strategy", order_by="StrategyVersion.version.desc()")


class StrategyVersion(Base):
    """策略版本历史"""
    __tablename__ = "strategy_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False, comment="策略ID")
    version = Column(Integer, nullable=False, comment="版本号")
    name = Column(String(128), nullable=False, comment="策略名称")
    description = Column(Text, nullable=True, comment="策略描述")
    strategy_type = Column(String(64), nullable=False, comment="策略类型")
    category = Column(String(64), nullable=True, comment="策略分类")
    priority = Column(SQLEnum(StrategyPriority), comment="优先级")
    status = Column(SQLEnum(StrategyStatus), comment="状态")
    scope = Column(JSON, nullable=True, comment="策略范围")
    conditions = Column(JSON, nullable=False, comment="触发条件")
    actions = Column(JSON, nullable=False, comment="执行动作")
    config = Column(JSON, nullable=True, comment="策略配置")
    change_type = Column(SQLEnum(ChangeType), nullable=False, comment="变更类型")
    change_summary = Column(Text, nullable=True, comment="变更摘要")
    previous_version_id = Column(Integer, nullable=True, comment="前一版本ID")
    previous_values = Column(JSON, nullable=True, comment="变更前的值")
    operator = Column(String(64), nullable=True, comment="操作人")
    operator_ip = Column(String(64), nullable=True, comment="操作人IP")
    approved_by = Column(String(64), nullable=True, comment="审批人")
    approved_at = Column(DateTime, nullable=True, comment="审批时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关联关系
    strategy = relationship("Strategy", back_populates="versions")


class StrategyRule(Base):
    """策略规则库"""
    __tablename__ = "strategy_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, comment="规则名称")
    description = Column(Text, nullable=True, comment="规则描述")
    rule_type = Column(String(64), nullable=False, comment="规则类型")
    condition_type = Column(SQLEnum(RuleConditionType), comment="条件类型")
    conditions = Column(JSON, nullable=False, comment="条件表达式")
    condition_logic = Column(String(16), default="AND", comment="条件逻辑 AND/OR")
    action_type = Column(SQLEnum(RuleActionType), nullable=False, comment="动作类型")
    action_config = Column(JSON, nullable=False, comment="动作配置")
    priority = Column(Integer, default=100, comment="优先级（数字越小优先级越高）")
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_system = Column(Boolean, default=False, comment="是否系统规则")
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True, comment="关联策略ID")
    tags = Column(JSON, nullable=True, comment="标签列表")
    test_data = Column(JSON, nullable=True, comment="测试数据")
    created_by = Column(String(64), nullable=True, comment="创建人")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    strategy = relationship("Strategy", backref="rules")


class EvaluationResult(Base):
    """评估结果记录"""
    __tablename__ = "evaluation_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False, comment="策略ID")
    strategy_version = Column(Integer, nullable=False, comment="策略版本")
    evaluation_context = Column(JSON, nullable=False, comment="评估上下文")
    triggered_conditions = Column(JSON, nullable=True, comment="触发的条件")
    matched_rules = Column(JSON, nullable=True, comment="匹配到的规则")
    actions_triggered = Column(JSON, nullable=True, comment="触发的动作")
    action_results = Column(JSON, nullable=True, comment="动作执行结果")
    evaluation_time_ms = Column(Integer, nullable=True, comment="评估耗时(毫秒)")
    status = Column(String(32), nullable=False, comment="评估状态: success, partial, failed")
    error_message = Column(Text, nullable=True, comment="错误信息")
    evaluated_by = Column(String(64), nullable=True, comment="评估人")
    tenant_id = Column(String(64), nullable=True, comment="租户ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
