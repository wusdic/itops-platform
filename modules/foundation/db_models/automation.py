# -*- coding: utf-8 -*-
"""
自动化模块数据库模型
对应表：automation_scripts, automation_tasks, automation_executions,
       automation_execution_logs, automation_trigger_rules,
       automation_ai_decisions, automation_script_versions
"""

import uuid
from datetime import datetime
from typing import Optional, List, Any

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, DateTime, JSON, BigInteger,
    ForeignKey, Index, Float
)
from sqlalchemy.orm import relationship

from .base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class AutomationScript(Base):
    """自动化脚本库"""
    __tablename__ = "automation_scripts"

    id = Column(String(36), primary_key=True, default=generate_uuid)

    # 租户隔离
    tenant_id = Column(String(64), index=True)  # 租户ID

    name = Column(String(100), nullable=False)
    description = Column(Text)
    script_type = Column(String(32), nullable=False, comment="shell, python, ansible")
    content = Column(Text, nullable=False)
    risk_level = Column(String(16), default="medium", comment="low, medium, high, critical")
    params_schema = Column(JSON, comment="[{name, type, required, default, description}]")
    tags = Column(JSON, comment='["nginx", "backup"]')
    source = Column(String(32), default="manual", comment="manual, ai_generated")
    created_by = Column(String(64))
    updated_by = Column(String(64))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    tasks = relationship("AutomationTask", back_populates="script")
    executions = relationship("AutomationExecution", back_populates="script")
    versions = relationship("AutomationScriptVersion", back_populates="script", order_by="desc(AutomationScriptVersion.version)")

    __table_args__ = (
        Index("idx_script_type", "script_type"),
        Index("idx_risk_level", "risk_level"),
        Index("idx_source", "source"),
    )


class AutomationTask(Base):
    """自动化任务调度"""
    __tablename__ = "automation_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    script_id = Column(String(36), ForeignKey("automation_scripts.id", ondelete="RESTRICT"), nullable=False)
    trigger_type = Column(String(32), nullable=False, comment="cron, interval, manual")
    trigger_config = Column(JSON, comment='{"cron": "0 2 * * *"} or {"interval_seconds": 300}')
    target_device_ids = Column(JSON, comment="[1, 2, 3]，空表示所有")
    enabled = Column(Boolean, default=True)
    next_run_time = Column(DateTime)
    last_run_time = Column(DateTime)
    last_execution_id = Column(String(36))
    status = Column(String(32), default="idle", comment="idle, running, error")
    created_by = Column(String(64))
    updated_by = Column(String(64))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    script = relationship("AutomationScript", back_populates="tasks")
    executions = relationship("AutomationExecution", back_populates="task")

    __table_args__ = (
        Index("idx_task_script_id", "script_id"),
        Index("idx_task_trigger_type", "trigger_type"),
        Index("idx_task_enabled", "enabled"),
        Index("idx_task_status", "status"),
    )


class AutomationExecution(Base):
    """自动化执行记录"""
    __tablename__ = "automation_executions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("automation_tasks.id", ondelete="SET NULL"))
    script_id = Column(String(36), ForeignKey("automation_scripts.id", ondelete="RESTRICT"), nullable=False)
    trigger_type = Column(String(32), nullable=False, comment="manual, scheduled, api, alert")
    trigger_params = Column(JSON, comment="触发时传入的参数")
    status = Column(String(32), nullable=False, comment="pending, running, success, failed, cancelled, rolled_back")
    started_at = Column(DateTime, nullable=False, default=datetime.now)
    completed_at = Column(DateTime)
    duration_ms = Column(Integer, comment="毫秒")
    target_devices = Column(JSON, comment="本次执行的目标设备")
    result_summary = Column(JSON, comment='{"exit_code": 0, "stdout": "...", "stderr": "..."}')
    error_message = Column(Text)
    triggered_by = Column(String(64), comment='用户名或"scheduler"')
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    task = relationship("AutomationTask", back_populates="executions")
    script = relationship("AutomationScript", back_populates="executions")
    logs = relationship("AutomationExecutionLog", back_populates="execution", order_by="AutomationExecutionLog.timestamp")

    __table_args__ = (
        Index("idx_exec_task_id", "task_id"),
        Index("idx_exec_script_id", "script_id"),
        Index("idx_exec_status", "status"),
        Index("idx_exec_started_at", "started_at"),
        Index("idx_exec_trigger_type", "trigger_type"),
    )


class AutomationExecutionLog(Base):
    """自动化执行日志（流式输出）"""
    __tablename__ = "automation_execution_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    execution_id = Column(String(36), ForeignKey("automation_executions.id", ondelete="CASCADE"), nullable=False)
    stream = Column(String(16), comment="stdout, stderr, info")
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)

    # 关系
    execution = relationship("AutomationExecution", back_populates="logs")

    __table_args__ = (
        Index("idx_log_execution_id", "execution_id"),
    )


class AutomationTriggerRule(Base):
    """告警触发规则"""
    __tablename__ = "automation_trigger_rules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=True)
    condition = Column(JSON, nullable=False, comment="{condition_type, metric_name, operator, threshold_value}")
    alert_level = Column(String(16), default="medium")
    device_ids = Column(JSON)
    device_tags = Column(JSON)
    trigger_interval = Column(Integer, default=300, comment="秒")
    suppress_enabled = Column(Boolean, default=False)
    suppress_duration = Column(Integer, default=300, comment="秒")
    suppress_key = Column(String(128))
    time_windows = Column(JSON, comment="[{start: '00:00', end: '06:00', days: [1,2,3,4,5]}]")
    actions = Column(JSON, nullable=False, comment="[{action_type, enabled, script_id, params}]")
    trigger_count = Column(Integer, default=0)
    last_triggered_at = Column(DateTime)
    created_by = Column(String(64))
    updated_by = Column(String(64))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        Index("idx_rule_enabled", "enabled"),
        Index("idx_rule_alert_level", "alert_level"),
    )


class AutomationAIDecision(Base):
    """AI 执行决策记录"""
    __tablename__ = "automation_ai_decisions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_type = Column(String(32), nullable=False, comment="alert, workorder, manual")
    event_id = Column(String(36), nullable=False)
    event_context = Column(JSON, nullable=False, comment="原始事件数据")
    llm_model = Column(String(64), comment="使用的模型")
    llm_prompt = Column(Text)
    llm_response = Column(Text)
    decision = Column(String(32), nullable=False, comment="use_script, generate_script, escalate, human")
    script_id = Column(String(36), comment="使用的脚本（如果有）")
    generated_script_id = Column(String(36), comment="AI 生成的脚本（如果有）")
    execution_id = Column(String(36), comment="关联的执行记录")
    confidence = Column(Float, comment="决策置信度 0-1")
    reason = Column(Text)
    status = Column(String(32), nullable=False, comment="pending, success, failed, escalated")
    created_at = Column(DateTime, default=datetime.now)

    # 关系（execution_id 不做外键约束，仅通过 execution_id 关联）
    # execution = relationship("AutomationExecution", back_populates="ai_decision")  # 暂不关联，避免循环

    __table_args__ = (
        Index("idx_ai_event_type", "event_type"),
        Index("idx_ai_event_id", "event_id"),
        Index("idx_ai_decision", "decision"),
        Index("idx_ai_status", "status"),
        Index("idx_ai_created_at", "created_at"),
    )


class AutomationScriptVersion(Base):
    """脚本版本管理"""
    __tablename__ = "automation_script_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    script_id = Column(String(36), ForeignKey("automation_scripts.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    change_summary = Column(Text)
    created_by = Column(String(64), comment="'AI' 或用户名")
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    script = relationship("AutomationScript", back_populates="versions")

    __table_args__ = (
        Index("idx_ver_script_id", "script_id"),
        Index("idx_ver_version", "script_id", "version"),
    )
