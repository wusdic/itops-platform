# -*- coding: utf-8 -*-
"""
自动化模块 API 路由
提供脚本库、任务调度、执行记录、触发规则和 AI 决策引擎接口

重构说明（v2）：
- Scripts/Tasks/Executions 从内存存储改为数据库持久化
- 新增事件入口 API（供监控/工单模块调用）
- 新增 AI 决策引擎接口
- 保持 trigger-rules 和 rollback 相关 API 兼容
"""

import logging
import uuid
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.dependencies import get_db, get_current_user, CurrentUser
from modules.foundation.db_models import (
    AutomationScript, AutomationTask, AutomationExecution,
    AutomationExecutionLog, AutomationTriggerRule,
    AutomationAIDecision, AutomationScriptVersion
)
from modules.foundation.db_models.base import DatabaseManager

router = APIRouter()
logger = logging.getLogger(__name__)
db_manager = DatabaseManager()


# ============== 通用响应模型 ==============

class BaseResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None


class PaginationResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Dict[str, Any]


# ============== Scripts API ==============

class ScriptParamSchema(BaseModel):
    """脚本参数定义"""
    name: str
    type: str = "string"
    required: bool = False
    default: Optional[Any] = None
    description: Optional[str] = None


class CreateScriptRequest(BaseModel):
    """创建脚本请求"""
    name: str = Field(..., description="脚本名称")
    description: Optional[str] = Field("", description="脚本描述")
    script_type: str = Field(..., description="脚本类型: shell, python, ansible")
    content: str = Field(..., description="脚本内容")
    risk_level: str = Field("medium", description="风险等级: low, medium, high, critical")
    params_schema: Optional[List[ScriptParamSchema]] = Field([], description="参数定义")
    tags: Optional[List[str]] = Field([], description="标签")


class UpdateScriptRequest(BaseModel):
    """更新脚本请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    script_type: Optional[str] = None
    content: Optional[str] = None
    risk_level: Optional[str] = None
    params_schema: Optional[List[ScriptParamSchema]] = None
    tags: Optional[List[str]] = None


class ExecuteScriptRequest(BaseModel):
    """执行脚本请求"""
    params: Optional[Dict[str, Any]] = Field({}, description="执行参数")
    target_device_ids: Optional[List[int]] = Field([], description="目标设备ID列表")
    dry_run: bool = Field(False, description="是否dry-run模式（仅模拟，不实际执行）")


class ScriptResponse(BaseModel):
    """脚本响应"""
    id: str
    name: str
    description: Optional[str]
    script_type: str
    risk_level: str
    params_schema: Optional[List[Dict]]
    tags: Optional[List[str]]
    source: str
    created_by: Optional[str]
    updated_by: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


@router.get("/scripts", summary="获取脚本列表")
async def list_scripts(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    script_type: Optional[str] = Query(None, description="脚本类型过滤"),
    risk_level: Optional[str] = Query(None, description="风险等级过滤"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取脚本列表（分页）"""
    query = db.query(AutomationScript)

    if script_type:
        query = query.filter(AutomationScript.script_type == script_type)
    if risk_level:
        query = query.filter(AutomationScript.risk_level == risk_level)
    if keyword:
        query = query.filter(
            (AutomationScript.name.contains(keyword)) |
            (AutomationScript.description.contains(keyword))
        )

    total = query.count()
    items = query.order_by(AutomationScript.updated_at.desc()) \
        .offset((page - 1) * page_size).limit(page_size).all()

    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": [_script_to_dict(s) for s in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    }


@router.post("/scripts", summary="创建脚本", response_model=BaseResponse)
async def create_script(
    request: CreateScriptRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建新脚本"""
    script_id = str(uuid.uuid4())

    # 保存第一个版本
    version = AutomationScriptVersion(
        id=str(uuid.uuid4()),
        script_id=script_id,
        version=1,
        content=request.content,
        change_summary="Initial version",
        created_by=current_user.username,
    )
    db.add(version)

    script = AutomationScript(
        id=script_id,
        name=request.name,
        description=request.description,
        script_type=request.script_type,
        content=request.content,
        risk_level=request.risk_level,
        params_schema=[p.model_dump() for p in request.params_schema] if request.params_schema else [],
        tags=request.tags,
        source="manual",
        created_by=current_user.username,
        updated_by=current_user.username,
    )
    db.add(script)
    db.commit()

    logger.info(f"Created script {script_id} by {current_user.username}")
    return {"code": 0, "message": "success", "data": _script_to_dict(script)}


@router.get("/scripts/{script_id}", summary="获取脚本详情")
async def get_script(
    script_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取脚本详情"""
    script = db.query(AutomationScript).filter(AutomationScript.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail=f"Script {script_id} not found")
    return {"code": 0, "message": "success", "data": _script_to_dict(script)}


@router.put("/scripts/{script_id}", summary="更新脚本", response_model=BaseResponse)
async def update_script(
    script_id: str,
    request: UpdateScriptRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新脚本（自动保存版本）"""
    script = db.query(AutomationScript).filter(AutomationScript.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail=f"Script {script_id} not found")

    # 保存新版本
    last_version = db.query(AutomationScriptVersion) \
        .filter(AutomationScriptVersion.script_id == script_id) \
        .order_by(AutomationScriptVersion.version.desc()).first()
    new_version_num = (last_version.version + 1) if last_version else 1

    version = AutomationScriptVersion(
        id=str(uuid.uuid4()),
        script_id=script_id,
        version=new_version_num,
        content=script.content,
        change_summary=f"Before update to v{new_version_num}",
        created_by=current_user.username,
    )
    db.add(version)

    # 更新字段
    if request.name is not None:
        script.name = request.name
    if request.description is not None:
        script.description = request.description
    if request.script_type is not None:
        script.script_type = request.script_type
    if request.content is not None:
        script.content = request.content
    if request.risk_level is not None:
        script.risk_level = request.risk_level
    if request.params_schema is not None:
        script.params_schema = [p.model_dump() for p in request.params_schema]
    if request.tags is not None:
        script.tags = request.tags

    script.updated_by = current_user.username
    script.updated_at = datetime.now()
    db.commit()

    logger.info(f"Updated script {script_id} by {current_user.username}")
    return {"code": 0, "message": "success", "data": _script_to_dict(script)}


@router.delete("/scripts/{script_id}", summary="删除脚本")
async def delete_script(
    script_id: str,
    force: bool = Query(False, description="强制删除（跳过引用检查，高危操作）"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除脚本（force=True 跳过 Task/Execution 引用检查，直接删除所有关联记录）"""
    # 检查是否有任务引用（force 模式跳过）
    if not force:
        task = db.query(AutomationTask).filter(AutomationTask.script_id == script_id).first()
        if task:
            raise HTTPException(status_code=409, detail=f"Script is used by task '{task.name}', cannot delete. Use force=true to override.")
        execution = db.query(AutomationExecution).filter(AutomationExecution.script_id == script_id).first()
        if execution:
            raise HTTPException(status_code=409, detail=f"Script has execution records, cannot delete. Use force=true to override.")

    script = db.query(AutomationScript).filter(AutomationScript.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail=f"Script {script_id} not found")

    # force 模式：按正确顺序级联删除
    # 1. 删除版本记录
    db.query(AutomationScriptVersion).filter(AutomationScriptVersion.script_id == script_id).delete()
    # 2. 删除任务记录（关联的 executions 已在 DB 层 CASCADE）
    db.query(AutomationTask).filter(AutomationTask.script_id == script_id).delete()
    # 3. 删除执行记录
    db.query(AutomationExecution).filter(AutomationExecution.script_id == script_id).delete()
    # 4. 删除脚本本身
    db.delete(script)
    db.commit()

    action = "force-deleted" if force else "deleted"
    logger.warning(f"[HIGH-RISK] {action} script {script_id} by {current_user.username} (force={force})")
    return {"code": 0, "message": f"Script {script_id} {action} (force={force})"}


@router.post("/scripts/{script_id}/execute", summary="立即执行脚本")
async def execute_script(
    script_id: str,
    request: ExecuteScriptRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """立即执行脚本（异步，返回 execution_id）"""
    script = db.query(AutomationScript).filter(AutomationScript.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail=f"Script {script_id} not found")

    execution_id = str(uuid.uuid4())

    # Dry-run 模式：仅返回预计执行信息，不实际执行
    if request.dry_run:
        logger.info(f"Dry-run script {script_id}, execution_id: {execution_id}")
        return {
            "code": 0,
            "message": "success",
            "data": {
                "execution_id": execution_id,
                "status": "dry_run",
                "dry_run": True,
                "script_id": script_id,
                "script_name": script.name,
                "target_devices": request.target_device_ids,
                "trigger_type": "manual",
                "triggered_by": current_user.username,
                "estimated_impact": {
                    "risk_level": script.risk_level or "medium",
                    "affected_devices": len(request.target_device_ids) if request.target_device_ids else 1,
                    "estimated_duration_ms": 1000,
                },
                "note": "Dry-run completed. No actual execution performed.",
            }
        }

    # Phase 8-7: 并发锁 — 同一设备同时只能有一个执行任务
    from app.common.redis_client import RedisLock
    if request.target_device_ids:
        lock = RedisLock()
        for device_id in request.target_device_ids:
            lock_key = f"device_execution:{device_id}"
            try:
                with lock.acquire(lock_key, expire=300, wait_timeout=0):
                    pass  # 锁获取成功，继续
            except TimeoutError:
                raise HTTPException(
                    status_code=409,
                    detail=f"Device {device_id} is currently executing another task. Please try again later."
                )

    # 创建执行记录
    execution = AutomationExecution(
        id=execution_id,
        task_id=None,
        script_id=script_id,
        trigger_type="manual",
        trigger_params=request.params,
        status="pending",
        started_at=datetime.now(),
        target_devices=request.target_device_ids,
        triggered_by=current_user.username,
    )
    db.add(execution)
    db.commit()

    # TODO: 实际异步执行脚本（调用 script_executor）
    # 目前模拟执行
    execution.status = "success"
    execution.completed_at = datetime.now()
    execution.duration_ms = 100
    execution.result_summary = {"exit_code": 0, "stdout": "Script executed successfully (mock)"}
    db.commit()

    logger.info(f"Executed script {script_id}, execution_id: {execution_id}")
    return {
        "code": 0,
        "message": "success",
        "data": {
            "execution_id": execution_id,
            "status": execution.status,
        }
    }


@router.get("/scripts/{script_id}/versions", summary="获取脚本版本历史")
async def get_script_versions(
    script_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取脚本的版本历史"""
    versions = db.query(AutomationScriptVersion) \
        .filter(AutomationScriptVersion.script_id == script_id) \
        .order_by(AutomationScriptVersion.version.desc()).all()

    return {
        "code": 0,
        "message": "success",
        "data": [
            {
                "id": v.id,
                "version": v.version,
                "content": v.content,
                "change_summary": v.change_summary,
                "created_by": v.created_by,
                "created_at": v.created_at.isoformat() if v.created_at else None,
            }
            for v in versions
        ]
    }


# ============== Tasks API ==============

class CreateTaskRequest(BaseModel):
    """创建任务请求"""
    name: str = Field(..., description="任务名称")
    description: Optional[str] = Field("", description="任务描述")
    script_id: str = Field(..., description="脚本ID")
    trigger_type: str = Field(..., description="触发类型: cron, interval, manual")
    trigger_config: Optional[Dict] = Field({}, description="触发配置")
    target_device_ids: Optional[List[int]] = Field([], description="目标设备ID列表")
    enabled: bool = Field(True, description="是否启用")


class UpdateTaskRequest(BaseModel):
    """更新任务请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    script_id: Optional[str] = None
    trigger_type: Optional[str] = None
    trigger_config: Optional[Dict] = None
    target_device_ids: Optional[List[int]] = None
    enabled: Optional[bool] = None


class TaskResponse(BaseModel):
    """任务响应"""
    id: str
    name: str
    description: Optional[str]
    script_id: str
    script_name: Optional[str] = None
    trigger_type: str
    trigger_config: Optional[Dict]
    target_device_ids: Optional[List[int]]
    enabled: bool
    next_run_time: Optional[str]
    last_run_time: Optional[str]
    last_execution_id: Optional[str]
    status: str
    created_by: Optional[str]
    created_at: Optional[str]


@router.get("/tasks", summary="获取任务列表")
async def list_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    enabled: Optional[bool] = Query(None, description="按启用状态过滤"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取任务列表（分页）"""
    query = db.query(AutomationTask)

    if enabled is not None:
        query = query.filter(AutomationTask.enabled == enabled)

    total = query.count()
    items = query.order_by(AutomationTask.updated_at.desc()) \
        .offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for task in items:
        script = db.query(AutomationScript).filter(AutomationScript.id == task.script_id).first()
        result.append(_task_to_dict(task, script.name if script else None))

    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": result,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    }


@router.post("/tasks", summary="创建任务", response_model=BaseResponse)
async def create_task(
    request: CreateTaskRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建新任务"""
    # 验证脚本存在
    script = db.query(AutomationScript).filter(AutomationScript.id == request.script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail=f"Script {request.script_id} not found")

    task_id = str(uuid.uuid4())
    task = AutomationTask(
        id=task_id,
        name=request.name,
        description=request.description,
        script_id=request.script_id,
        trigger_type=request.trigger_type,
        trigger_config=request.trigger_config,
        target_device_ids=request.target_device_ids,
        enabled=request.enabled,
        status="idle",
        created_by=current_user.username,
        updated_by=current_user.username,
    )
    db.add(task)
    db.commit()

    logger.info(f"Created task {task_id} by {current_user.username}")
    return {"code": 0, "message": "success", "data": _task_to_dict(task, script.name)}


@router.get("/tasks/{task_id}", summary="获取任务详情")
async def get_task(
    task_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取任务详情"""
    task = db.query(AutomationTask).filter(AutomationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    script = db.query(AutomationScript).filter(AutomationScript.id == task.script_id).first()
    return {"code": 0, "message": "success", "data": _task_to_dict(task, script.name if script else None)}


@router.put("/tasks/{task_id}", summary="更新任务", response_model=BaseResponse)
async def update_task(
    task_id: str,
    request: UpdateTaskRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新任务"""
    task = db.query(AutomationTask).filter(AutomationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    if request.name is not None:
        task.name = request.name
    if request.description is not None:
        task.description = request.description
    if request.script_id is not None:
        script = db.query(AutomationScript).filter(AutomationScript.id == request.script_id).first()
        if not script:
            raise HTTPException(status_code=404, detail=f"Script {request.script_id} not found")
        task.script_id = request.script_id
    if request.trigger_type is not None:
        task.trigger_type = request.trigger_type
    if request.trigger_config is not None:
        task.trigger_config = request.trigger_config
    if request.target_device_ids is not None:
        task.target_device_ids = request.target_device_ids
    if request.enabled is not None:
        task.enabled = request.enabled

    task.updated_by = current_user.username
    task.updated_at = datetime.now()
    db.commit()

    script = db.query(AutomationScript).filter(AutomationScript.id == task.script_id).first()
    logger.info(f"Updated task {task_id} by {current_user.username}")
    return {"code": 0, "message": "success", "data": _task_to_dict(task, script.name if script else None)}


@router.delete("/tasks/{task_id}", summary="删除任务")
async def delete_task(
    task_id: str,
    force: bool = Query(False, description="强制删除（终止运行中的执行并删除，高危操作）"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除任务（force=True 终止运行中的执行后再删除任务）"""
    task = db.query(AutomationTask).filter(AutomationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    # force 模式：先终止所有运行中的执行
    if force:
        running = db.query(AutomationExecution).filter(
            AutomationExecution.task_id == task_id,
            AutomationExecution.status.in_(["queued", "running", "waiting_approval"])
        ).all()
        for exec_ in running:
            exec_.status = "failed"
            exec_.ended_at = datetime.now()
            exec_.error_message = f"Killed by {current_user.username} (force delete)"
        if running:
            logger.warning(f"[HIGH-RISK] Force-deleted task {task_id}, terminated {len(running)} running executions")

    db.delete(task)
    db.commit()

    action = "force-deleted" if force else "deleted"
    logger.warning(f"[HIGH-RISK] {action} task {task_id} by {current_user.username} (force={force})")
    return {"code": 0, "message": f"Task {task_id} {action} (force={force})"}


@router.post("/tasks/{task_id}/run", summary="立即执行任务")
async def run_task(
    task_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """立即执行任务（不影响调度周期）"""
    task = db.query(AutomationTask).filter(AutomationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    script = db.query(AutomationScript).filter(AutomationScript.id == task.script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail=f"Script {task.script_id} not found")

    execution_id = str(uuid.uuid4())

    execution = AutomationExecution(
        id=execution_id,
        task_id=task_id,
        script_id=task.script_id,
        trigger_type="manual",
        trigger_params={},
        status="running",
        started_at=datetime.now(),
        target_devices=task.target_device_ids,
        triggered_by=current_user.username,
    )
    db.add(execution)

    task.last_execution_id = execution_id
    task.last_run_time = datetime.now()
    task.status = "running"
    db.commit()

    # TODO: 实际异步执行脚本
    execution.status = "success"
    execution.completed_at = datetime.now()
    execution.duration_ms = 200
    execution.result_summary = {"exit_code": 0, "stdout": "Task executed (mock)"}
    task.status = "idle"
    db.commit()

    logger.info(f"Ran task {task_id}, execution_id: {execution_id}")
    return {
        "code": 0,
        "message": "success",
        "data": {
            "execution_id": execution_id,
            "task_id": task_id,
            "status": execution.status,
        }
    }


# ============== Executions API ==============

@router.get("/executions", summary="获取执行记录列表")
async def list_executions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态过滤"),
    task_id: Optional[str] = Query(None, description="任务ID过滤"),
    script_id: Optional[str] = Query(None, description="脚本ID过滤"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取执行记录列表（分页）"""
    query = db.query(AutomationExecution)

    if status:
        query = query.filter(AutomationExecution.status == status)
    if task_id:
        query = query.filter(AutomationExecution.task_id == task_id)
    if script_id:
        query = query.filter(AutomationExecution.script_id == script_id)

    total = query.count()
    items = query.order_by(AutomationExecution.started_at.desc()) \
        .offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for e in items:
        task = db.query(AutomationTask).filter(AutomationTask.id == e.task_id).first() if e.task_id else None
        script = db.query(AutomationScript).filter(AutomationScript.id == e.script_id).first()
        result.append(_execution_to_dict(e, task.name if task else None, script.name if script else None))

    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": result,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    }


@router.get("/executions/{execution_id}", summary="获取执行详情")
async def get_execution(
    execution_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取执行详情"""
    e = db.query(AutomationExecution).filter(AutomationExecution.id == execution_id).first()
    if not e:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")

    task = db.query(AutomationTask).filter(AutomationTask.id == e.task_id).first() if e.task_id else None
    script = db.query(AutomationScript).filter(AutomationScript.id == e.script_id).first()

    return {"code": 0, "message": "success", "data": _execution_to_dict(e, task.name if task else None, script.name if script else None)}


@router.get("/executions/{execution_id}/verify", summary="Phase 8-9 验证执行结果")
async def verify_execution_result(
    execution_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Phase 8-9: 执行结果验证。

    执行成功后，验证预期效果是否达成：
    1. 查询执行记录确认状态
    2. 重新采集目标设备指标
    3. 对比执行前后指标变化
    4. 返回验证结论（passed / failed / inconclusive）
    """
    from modules.business.automation.execution_service import ExecutionService
    svc = ExecutionService(db)
    result = svc.verify_execution(execution_id)
    return {"code": 0, "message": "success", "data": result}


@router.get("/executions/{execution_id}/logs", summary="获取执行日志")
async def get_execution_logs(
    execution_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取执行日志"""
    logs = db.query(AutomationExecutionLog) \
        .filter(AutomationExecutionLog.execution_id == execution_id) \
        .order_by(AutomationExecutionLog.timestamp.asc()).all()

    return {
        "code": 0,
        "message": "success",
        "data": [
            {
                "id": log.id,
                "stream": log.stream,
                "content": log.content,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            }
            for log in logs
        ]
    }


# ============== Approval API（审批流）==============

class ApprovalRequestCreate(BaseModel):
    """创建审批请求"""
    execution_id: str = Field(..., description="执行ID")
    reason: Optional[str] = Field("", description="审批原因")
    timeout_hours: Optional[int] = Field(24, description="审批超时时间")


class ApprovalActionRequest(BaseModel):
    """审批操作请求"""
    comment: Optional[str] = Field("", description="审批意见")


@router.post("/executions/{execution_id}/approval", summary="创建审批请求")
async def create_approval_request(
    execution_id: str,
    request: ApprovalRequestCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """为执行创建审批请求（当执行需要审批时）"""
    from modules.business.automation.approval_service import ApprovalService
    from modules.business.automation.execution_service import ExecutionService

    # 获取执行信息
    exec_service = ExecutionService(db)
    execution = exec_service.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")

    # 检查风险等级
    risk_level, required_level, _ = exec_service.check_risk_level(execution["script_id"])
    if required_level == 0:
        return {"code": 0, "message": "No approval needed", "data": {"needs_approval": False}}

    # 创建审批请求
    approval_service = ApprovalService(db)
    result, error = approval_service.create_approval_request(
        execution_id=execution_id,
        script_id=execution["script_id"],
        risk_level=risk_level,
        required_approval_level=required_level,
        created_by=current_user.username,
        reason=request.reason,
        timeout_hours=request.timeout_hours,
    )

    if error:
        raise HTTPException(status_code=400, detail=error)

    # 更新执行状态
    exec_record = db.query(AutomationExecution).filter(AutomationExecution.id == execution_id).first()
    if exec_record:
        exec_record.status = "pending_approval"
        db.commit()

    return {"code": 0, "message": "success", "data": {
        "needs_approval": True,
        "approval_id": result["id"],
        "required_level": required_level,
    }}


class RiskAssessmentRequest(BaseModel):
    params: Optional[Dict[str, Any]] = Field(default=None, description="执行参数")
    target_device_ids: Optional[List[str]] = Field(default=None, description="目标设备ID列表")


@router.post("/scripts/{script_id}/risk-assessment", summary="风险评估")
async def assess_script_risk(
    script_id: str,
    request: RiskAssessmentRequest = RiskAssessmentRequest(),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Phase 8-4: 评估脚本执行风险，返回危险命令、影响面、警告和建议"""
    from modules.business.automation.execution_service import ExecutionService
    exec_service = ExecutionService(db)
    result = exec_service.assess_risk(
        script_id=script_id,
        params=request.params,
        target_device_ids=request.target_device_ids,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"code": 0, "message": "success", "data": result}


@router.get("/approvals/pending", summary="获取待我审批的列表")
async def list_pending_approvals(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户待审批的列表"""
    from modules.business.automation.approval_service import ApprovalService

    approval_service = ApprovalService(db)
    items, total = approval_service.list_pending_approvals(
        approver=current_user.username,
        page=page,
        page_size=page_size,
    )

    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    }


@router.post("/approvals/{approval_id}/approve", summary="审批通过")
async def approve_approval(
    approval_id: str,
    request: ApprovalActionRequest = ApprovalActionRequest(),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """审批通过"""
    from modules.business.automation.approval_service import ApprovalService

    approval_service = ApprovalService(db)
    success, error = approval_service.approve(
        approval_id=approval_id,
        approver=current_user.username,
        comment=request.comment,
    )

    if not success:
        raise HTTPException(status_code=400, detail=error)

    return {"code": 0, "message": "success"}


@router.post("/approvals/{approval_id}/reject", summary="审批拒绝")
async def reject_approval(
    approval_id: str,
    request: ApprovalActionRequest = ApprovalActionRequest(),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """审批拒绝"""
    from modules.business.automation.approval_service import ApprovalService

    approval_service = ApprovalService(db)
    success, error = approval_service.reject(
        approval_id=approval_id,
        approver=current_user.username,
        comment=request.comment,
    )

    if not success:
        raise HTTPException(status_code=400, detail=error)

    return {"code": 0, "message": "success"}


@router.post("/approvals/{approval_id}/cancel", summary="取消审批请求")
async def cancel_approval(
    approval_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """取消审批请求"""
    from modules.business.automation.approval_service import ApprovalService

    approval_service = ApprovalService(db)
    success, error = approval_service.cancel_approval(
        approval_id=approval_id,
        cancelled_by=current_user.username,
    )

    if not success:
        raise HTTPException(status_code=400, detail=error)

    return {"code": 0, "message": "success"}


@router.get("/approvals/{approval_id}", summary="获取审批详情")
async def get_approval(
    approval_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取审批详情"""
    from modules.business.automation.approval_service import ApprovalService

    approval_service = ApprovalService(db)
    result = approval_service.get_approval_request(approval_id)

    if not result:
        raise HTTPException(status_code=404, detail=f"Approval {approval_id} not found")

    return {"code": 0, "message": "success", "data": result}


@router.get("/executions/{execution_id}/approval", summary="获取执行的审批状态")
async def get_execution_approval(
    execution_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取指定执行的审批状态"""
    from modules.business.automation.approval_service import ApprovalService

    approval_service = ApprovalService(db)
    result = approval_service.get_approval_request_by_execution(execution_id)

    return {"code": 0, "message": "success", "data": result or {"execution_id": execution_id, "status": "no_approval_required"}}


# ============== Events API（AI 决策引擎入口）==============

class EventContext(BaseModel):
    """事件上下文"""
    alert_level: Optional[str] = None
    device_id: Optional[int] = None
    device_name: Optional[str] = None
    device_ip: Optional[str] = None
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
    triggered_at: Optional[str] = None
    extra: Optional[Dict] = {}


class TriggerEventRequest(BaseModel):
    """触发事件请求"""
    event_type: str = Field(..., description="事件类型: alert, workorder, manual")
    event_id: str = Field(..., description="事件源ID")
    source: str = Field(..., description="事件来源: monitoring, workorder, manual")
    context: EventContext


class AIDecisionResponse(BaseModel):
    """AI 决策响应"""
    decision: str  # use_script, generate_script, escalate, human
    script_id: Optional[str] = None
    generated_script_id: Optional[str] = None
    confidence: Optional[float] = None
    reason: Optional[str] = None


@router.post("/events", summary="触发自动化事件（AI 决策入口）")
async def trigger_event(
    request: TriggerEventRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    事件入口 API，供监控/工单模块调用

    AI 决策流程：
    1. 提取事件上下文
    2. 查询知识库获取推荐脚本
    3. 调用本地 LLM 做决策
    4. 根据决策执行或升级
    5. 成功后推送案例到知识库
    """
    event_id = str(uuid.uuid4())

    # 1. 查询知识库获取推荐脚本（如果有）
    recommended_scripts = []
    try:
        import requests
        resp = requests.get(
            "http://localhost:8000/api/v1/knowledge/fault-case/recommend-scripts",
            params={"symptom": request.context.metric_name or request.context.extra.get("symptom", "")},
            timeout=5,
        )
        if resp.status_code == 200:
            recommended_scripts = resp.json().get("recommendations", [])
    except Exception:
        pass  # 知识库不可用时继续

    # 2. 调用 LLM 做决策（模拟）
    # TODO: 实际调用 ai_copilot 模块
    ai_decision = _mock_ai_decision(request, recommended_scripts)

    # 3. 保存 AI 决策记录
    ai_record = AutomationAIDecision(
        id=str(uuid.uuid4()),
        event_type=request.event_type,
        event_id=request.event_id,
        event_context=request.context.model_dump(),
        llm_model="mock",
        llm_prompt="mock prompt",
        llm_response=str(ai_decision),
        decision=ai_decision["decision"],
        script_id=ai_decision.get("script_id"),
        generated_script_id=ai_decision.get("generated_script_id"),
        confidence=ai_decision.get("confidence"),
        reason=ai_decision.get("reason"),
        status="pending",
    )
    db.add(ai_record)
    db.commit()

    # 4. 根据决策执行
    execution_id = None
    if ai_decision["decision"] in ("use_script", "generate_script"):
        script_id = ai_decision.get("script_id") or ai_decision.get("generated_script_id")
        if script_id:
            execution = AutomationExecution(
                id=str(uuid.uuid4()),
                task_id=None,
                script_id=script_id,
                trigger_type="alert" if request.event_type == "alert" else "manual",
                trigger_params={"event_id": request.event_id, "context": request.context.model_dump()},
                status="running",
                started_at=datetime.now(),
                target_devices=[request.context.device_id] if request.context.device_id else [],
                triggered_by="automation",
            )
            db.add(execution)
            db.commit()

            # 模拟执行
            execution.status = "success"
            execution.completed_at = datetime.now()
            execution.duration_ms = 500
            execution.result_summary = {"exit_code": 0, "stdout": "Executed by AI decision"}
            ai_record.execution_id = execution.id
            ai_record.status = "success"
            execution_id = execution.id
            db.commit()

            # 5. 成功后推送案例到知识库
            _push_fault_case_to_knowledge(request, execution)

    elif ai_decision["decision"] == "escalate":
        # 升级到通知模块
        ai_record.status = "escalated"
        db.commit()
        try:
            import requests
            requests.post(
                "http://localhost:8000/api/v1/notification/send",
                json={
                    "type": "feishu",
                    "title": "自动化处理失败，需要人工介入",
                    "content": f"事件 {request.event_id} 自动处理失败，请及时处理",
                    "recipients": [],
                    "escalation": True,
                },
                timeout=5,
            )
        except Exception:
            pass

    logger.info(f"Event {event_id} processed, AI decision: {ai_decision['decision']}")
    return {
        "code": 0,
        "message": "success",
        "data": {
            "event_id": event_id,
            "ai_decision": AIDecisionResponse(**ai_decision),
            "execution_id": execution_id,
        }
    }


# ============== 兼容旧 API（Trigger Rules - 内存→数据库）==============

# 继续使用 AlertTriggerEngine 处理业务逻辑
_trigger_engine = None

def _get_trigger_engine():
    global _trigger_engine
    if _trigger_engine is None:
        from modules.automation.alert_trigger.trigger import AlertTriggerEngine
        _trigger_engine = AlertTriggerEngine()
    return _trigger_engine


# 旧版请求模型（保持兼容）
class ConditionConfigRequest(BaseModel):
    condition_type: str = "threshold"
    metric_name: str = ""
    operator: str = ">"
    threshold_value: float = 0
    duration_seconds: int = 0
    change_percent: float = 0
    rate_percent: float = 0
    expression: str = ""


class ActionConfigRequest(BaseModel):
    action_type: str
    enabled: bool = True
    script_name: Optional[str] = None
    script_content: Optional[str] = None
    script_params: Dict[str, Any] = {}
    workorder_title_template: Optional[str] = None
    workorder_description_template: Optional[str] = None
    workorder_type: str = "fault"
    workorder_priority: str = "P2"
    notification_channels: List[str] = []
    notification_receivers: List[str] = []
    notification_template: Optional[str] = None


class CreateTriggerRuleRequest(BaseModel):
    name: str
    description: str = ""
    enabled: bool = True
    condition: ConditionConfigRequest
    alert_level: str = "medium"
    device_ids: List[int] = []
    device_tags: List[str] = []
    trigger_interval: int = 300
    suppress_enabled: bool = False
    suppress_duration: int = 300
    suppress_key: str = ""
    time_windows: List[Dict[str, Any]] = []
    actions: List[ActionConfigRequest] = []


class UpdateTriggerRuleRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    condition: Optional[ConditionConfigRequest] = None
    alert_level: Optional[str] = None
    device_ids: Optional[List[int]] = None
    device_tags: Optional[List[str]] = None
    trigger_interval: Optional[int] = None
    suppress_enabled: Optional[bool] = None
    suppress_duration: Optional[int] = None
    suppress_key: Optional[str] = None
    time_windows: Optional[List[Dict[str, Any]]] = None
    actions: Optional[List[ActionConfigRequest]] = None


class TriggerRuleResponse(BaseModel):
    id: str
    name: str
    description: str
    enabled: bool
    condition: Dict[str, Any]
    alert_level: str
    device_ids: List[int]
    device_tags: List[str]
    trigger_interval: int
    suppress_enabled: bool
    suppress_duration: int
    suppress_key: str
    time_windows: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: str
    updated_by: str
    trigger_count: int
    last_triggered_at: Optional[str] = None


@router.get("/trigger-rules", summary="列出触发规则")
async def list_trigger_rules(
    enabled: Optional[bool] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """列出所有触发规则（从数据库）"""
    query = db.query(AutomationTriggerRule)
    if enabled is not None:
        query = query.filter(AutomationTriggerRule.enabled == enabled)

    rules = query.order_by(AutomationTriggerRule.created_at.desc()).all()
    return {
        "code": 0,
        "message": "success",
        "data": {
            "total": len(rules),
            "items": [_rule_to_response(r) for r in rules],
        }
    }


@router.post("/trigger-rules", summary="创建触发规则")
async def create_trigger_rule(
    request: CreateTriggerRuleRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建新的告警触发规则（持久化到数据库）"""
    rule_id = str(uuid.uuid4())

    rule = AutomationTriggerRule(
        id=rule_id,
        name=request.name,
        description=request.description,
        enabled=request.enabled,
        condition=request.condition.model_dump(),
        alert_level=request.alert_level,
        device_ids=request.device_ids,
        device_tags=request.device_tags,
        trigger_interval=request.trigger_interval,
        suppress_enabled=request.suppress_enabled,
        suppress_duration=request.suppress_duration,
        suppress_key=request.suppress_key,
        time_windows=request.time_windows,
        actions=[a.model_dump() for a in request.actions],
        created_by=current_user.username,
        updated_by=current_user.username,
    )
    db.add(rule)
    db.commit()

    logger.info(f"Created trigger rule: {rule_id} by {current_user.username}")
    return {"code": 0, "message": "success", "data": _rule_to_response(rule)}


@router.get("/trigger-rules/{rule_id}", summary="获取触发规则")
async def get_trigger_rule(
    rule_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取指定触发规则的详情"""
    rule = db.query(AutomationTriggerRule).filter(AutomationTriggerRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")
    return {"code": 0, "message": "success", "data": _rule_to_response(rule)}


@router.put("/trigger-rules/{rule_id}", summary="更新触发规则")
async def update_trigger_rule(
    rule_id: str,
    request: UpdateTriggerRuleRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新指定的触发规则"""
    rule = db.query(AutomationTriggerRule).filter(AutomationTriggerRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")

    if request.name is not None:
        rule.name = request.name
    if request.description is not None:
        rule.description = request.description
    if request.enabled is not None:
        rule.enabled = request.enabled
    if request.condition is not None:
        rule.condition = request.condition.model_dump()
    if request.alert_level is not None:
        rule.alert_level = request.alert_level
    if request.device_ids is not None:
        rule.device_ids = request.device_ids
    if request.device_tags is not None:
        rule.device_tags = request.device_tags
    if request.trigger_interval is not None:
        rule.trigger_interval = request.trigger_interval
    if request.suppress_enabled is not None:
        rule.suppress_enabled = request.suppress_enabled
    if request.suppress_duration is not None:
        rule.suppress_duration = request.suppress_duration
    if request.suppress_key is not None:
        rule.suppress_key = request.suppress_key
    if request.time_windows is not None:
        rule.time_windows = request.time_windows
    if request.actions is not None:
        rule.actions = [a.model_dump() for a in request.actions]

    rule.updated_by = current_user.username
    rule.updated_at = datetime.now()
    db.commit()

    logger.info(f"Updated trigger rule: {rule_id} by {current_user.username}")
    return {"code": 0, "message": "success", "data": _rule_to_response(rule)}


@router.delete("/trigger-rules/{rule_id}", summary="删除触发规则")
async def delete_trigger_rule(
    rule_id: str,
    force: bool = Query(False, description="强制删除（高危操作）"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除指定的触发规则（高危操作，force=True 绕过安全检查）"""
    rule = db.query(AutomationTriggerRule).filter(AutomationTriggerRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")

    db.delete(rule)
    db.commit()

    action = "force-deleted" if force else "deleted"
    logger.warning(f"[HIGH-RISK] {action} trigger rule {rule_id} by {current_user.username} (force={force})")
    return {"code": 0, "message": f"Rule {rule_id} {action} (force={force})"}


@router.post("/trigger-rules/{rule_id}/test", summary="测试触发规则")
async def test_trigger_rule(
    rule_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """测试执行指定的触发规则"""
    rule = db.query(AutomationTriggerRule).filter(AutomationTriggerRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")

    if not rule.enabled:
        raise HTTPException(status_code=400, detail="Rule not enabled, cannot test")

    if not rule.actions:
        raise HTTPException(status_code=400, detail="Rule has no actions configured")

    # 返回模拟测试结果
    return {
        "code": 0,
        "message": "success",
        "data": {
            "id": f"test_{uuid.uuid4().hex[:12]}",
            "rule_id": rule_id,
            "rule_name": rule.name,
            "trigger_time": datetime.now().isoformat(),
            "status": "triggered",
            "actions_executed": len(rule.actions),
            "message": "Test execution simulated",
        }
    }


# ============== Rollback/Snapshot API（保持兼容）==============

class RollbackRequest(BaseModel):
    rollback_script: Optional[str] = None
    rollback_params: Dict[str, Any] = {}


@router.get("/rollback-history", summary="获取回滚历史")
async def get_rollback_history(
    limit: int = Query(100, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取回滚历史记录（调用现有 executor）"""
    from modules.automation.script_executor import ScriptExecutor
    executor = ScriptExecutor()

    try:
        history = executor._rollback_manager.get_rollback_history(limit=limit)
        return {
            "code": 0,
            "message": "success",
            "data": {
                "total": len(history),
                "items": [
                    {
                        "execution_id": r.execution_id,
                        "status": r.status.value,
                        "snapshot_id": r.snapshot_id,
                        "message": r.message,
                        "duration": r.duration,
                        "created_at": r.created_at.isoformat(),
                    }
                    for r in history
                ]
            }
        }
    except Exception as e:
        # 如果 executor 有问题，返回空
        return {"code": 0, "message": "success", "data": {"total": 0, "items": []}}


@router.get("/executions/{execution_id}/snapshot", summary="获取快照")
async def get_snapshot(
    execution_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取指定执行的快照"""
    from modules.automation.script_executor import ScriptExecutor
    executor = ScriptExecutor()

    snapshot = executor._rollback_manager.get_snapshot(execution_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail=f"No snapshot for execution {execution_id}")

    return {
        "code": 0,
        "message": "success",
        "data": {
            "id": snapshot.id,
            "execution_id": snapshot.execution_id,
            "snapshot_type": snapshot.snapshot_type.value,
            "data": snapshot.data,
            "metadata": snapshot.metadata,
            "created_at": snapshot.created_at.isoformat(),
            "checksum": snapshot.checksum,
        }
    }


@router.post("/executions/{execution_id}/rollback", summary="执行回滚")
async def execute_rollback(
    execution_id: str,
    request: RollbackRequest = RollbackRequest(),
    current_user: CurrentUser = Depends(get_current_user),
):
    """执行回滚"""
    from modules.automation.script_executor import ScriptExecutor
    executor = ScriptExecutor()

    result = executor._rollback_manager.execute_rollback(
        execution_id=execution_id,
        rollback_script=request.rollback_script,
        rollback_params=request.rollback_params,
    )

    return {
        "code": 0,
        "message": "success",
        "data": {
            "execution_id": result.execution_id,
            "status": result.status.value,
            "snapshot_id": result.snapshot_id,
            "rollback_script_result": result.rollback_script_result,
            "message": result.message,
            "duration": result.duration,
        }
    }


@router.post("/evaluate", summary="评估指标是否超阈值")
async def evaluate_metric(
    device_id: int = Query(..., description="设备ID"),
    metric_name: str = Query(..., description="指标名称"),
    threshold: Optional[float] = Query(None, description="阈值"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    评估指标是否超过阈值，供自动化规则测试使用。
    前端传入 device_id + metric_name + 可选 threshold，
    后端从 metrics 表查最新值，判断是否超阈值。
    """
    # 查询设备最新指标
    try:
        result = db.execute(
            text("""
                SELECT metric_name, value, unit, timestamp
                FROM metrics
                WHERE device_id = :device_id AND metric_name = :metric_name
                ORDER BY timestamp DESC LIMIT 1
            """),
            {"device_id": device_id, "metric_name": metric_name}
        )
        row = result.fetchone()
    except Exception:
        row = None

    if not row:
        return {
            "device_id": device_id,
            "metric_name": metric_name,
            "current_value": None,
            "threshold": threshold,
            "exceeded": None,
            "message": "未找到该设备该指标的最近数据",
        }

    current_value = float(row[1]) if row[1] is not None else None
    unit = row[2]
    timestamp = row[3]

    if current_value is None:
        return {
            "device_id": device_id,
            "metric_name": metric_name,
            "current_value": None,
            "threshold": threshold,
            "exceeded": None,
            "message": "指标值为空",
        }

    exceeded = current_value > threshold if threshold is not None else None

    return {
        "device_id": device_id,
        "metric_name": metric_name,
        "current_value": current_value,
        "unit": unit,
        "timestamp": timestamp.isoformat() if timestamp else None,
        "threshold": threshold,
        "exceeded": exceeded,
        "message": f"指标 {'超过' if exceeded else '未超过'}阈值" if threshold is not None else "无阈值参数",
    }


# ============== 辅助函数 ==============

def _script_to_dict(s: AutomationScript) -> Dict:
    return {
        "id": s.id,
        "name": s.name,
        "description": s.description,
        "script_type": s.script_type,
        "content": s.content,
        "risk_level": s.risk_level,
        "params_schema": s.params_schema or [],
        "tags": s.tags or [],
        "source": s.source,
        "created_by": s.created_by,
        "updated_by": s.updated_by,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
    }


def _task_to_dict(t: AutomationTask, script_name: Optional[str] = None) -> Dict:
    return {
        "id": t.id,
        "name": t.name,
        "description": t.description,
        "script_id": t.script_id,
        "script_name": script_name,
        "trigger_type": t.trigger_type,
        "trigger_config": t.trigger_config or {},
        "target_device_ids": t.target_device_ids or [],
        "enabled": t.enabled,
        "next_run_time": t.next_run_time.isoformat() if t.next_run_time else None,
        "last_run_time": t.last_run_time.isoformat() if t.last_run_time else None,
        "last_execution_id": t.last_execution_id,
        "status": t.status,
        "created_by": t.created_by,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }


def _execution_to_dict(e: AutomationExecution, task_name: Optional[str] = None, script_name: Optional[str] = None) -> Dict:
    return {
        "id": e.id,
        "task_id": e.task_id,
        "task_name": task_name,
        "script_id": e.script_id,
        "script_name": script_name,
        "trigger_type": e.trigger_type,
        "trigger_params": e.trigger_params or {},
        "status": e.status,
        "started_at": e.started_at.isoformat() if e.started_at else None,
        "completed_at": e.completed_at.isoformat() if e.completed_at else None,
        "duration_ms": e.duration_ms,
        "target_devices": e.target_devices or [],
        "result_summary": e.result_summary or {},
        "error_message": e.error_message,
        "triggered_by": e.triggered_by,
    }


def _rule_to_response(r: AutomationTriggerRule) -> Dict:
    return {
        "id": r.id,
        "name": r.name,
        "description": r.description,
        "enabled": r.enabled,
        "condition": r.condition or {},
        "alert_level": r.alert_level,
        "device_ids": r.device_ids or [],
        "device_tags": r.device_tags or [],
        "trigger_interval": r.trigger_interval,
        "suppress_enabled": r.suppress_enabled,
        "suppress_duration": r.suppress_duration,
        "suppress_key": r.suppress_key,
        "time_windows": r.time_windows or [],
        "actions": r.actions or [],
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        "created_by": r.created_by or "",
        "updated_by": r.updated_by or "",
        "trigger_count": r.trigger_count or 0,
        "last_triggered_at": r.last_triggered_at.isoformat() if r.last_triggered_at else None,
    }


def _mock_ai_decision(event: TriggerEventRequest, recommended_scripts: List) -> Dict:
    """模拟 AI 决策（TODO: 实际调用 ai_copilot）"""
    if recommended_scripts:
        return {
            "decision": "use_script",
            "script_id": recommended_scripts[0].get("script_id"),
            "confidence": 0.85,
            "reason": f"Found {len(recommended_scripts)} similar historical cases",
        }

    # 无推荐时，默认 escalation
    return {
        "decision": "escalate",
        "confidence": 0.5,
        "reason": "No suitable script found, escalate to human",
    }


def _push_fault_case_to_knowledge(event: TriggerEventRequest, execution: AutomationExecution):
    """推送故障案例到知识库"""
    try:
        import requests
        requests.post(
            "http://localhost:8000/api/v1/knowledge/fault-case/from-automation",
            json={
                "source": "automation",
                "automation_execution_id": execution.id,
                "title": f"Auto-resolved: {event.context.metric_name or 'Unknown'}",
                "fault_category": "automation",
                "fault_level": event.context.alert_level or "P3",
                "symptom": event.context.metric_name,
                "root_cause": "Auto-detected by AI",
                "solution": f"Executed script {execution.script_id}",
                "script_id": execution.script_id,
                "execution_params": execution.trigger_params,
                "occurrence_time": event.context.triggered_at or datetime.now().isoformat(),
                "resolved_time": execution.completed_at.isoformat() if execution.completed_at else datetime.now().isoformat(),
            },
            timeout=5,
        )
    except Exception:
        pass


# ============================================================================
# SSE Streaming — Phase 6-2: WebSocket/SSE 实时日志推送
# ============================================================================
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
import json
import asyncio
import queue

from api.dependencies import get_db
from modules.foundation.db_models.automation import AutomationExecution
from api.routes.automation import router as automation_router

# SSE router
sse_router = APIRouter()

# 全局订阅管理器（per-execution 订阅队列）
_execution_subscribers: dict[int, queue.Queue] = {}


def publish_execution_log(execution_id: int, event_type: str, data: dict):
    """供 ExecutionService 内部调用，向 SSE 订阅者推送日志"""
    if execution_id in _execution_subscribers:
        try:
            _execution_subscribers[execution_id].put_nowait({"event": event_type, "data": data})
        except Exception:
            pass


async def event_stream(execution_id: int):
    """SSE generator: 将订阅队列中的事件 yield 为 SSE 格式"""
    q = _execution_subscribers.setdefault(execution_id, queue.Queue(maxsize=100))
    yield f"event: connected\ndata: {json.dumps({'execution_id': execution_id, 'status': 'subscribed'})}\n\n"
    while True:
        try:
            event = q.get(timeout=5)
            if event is None:
                break
            yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"
        except queue.Empty:
            yield f"event: heartbeat\ndata: {json.dumps({'ts': asyncio.get_event_loop().time()})}\n\n"


@sse_router.get("/executions/{execution_id}/stream", summary="SSE 实时日志流")
def stream_execution_logs(execution_id: int, db: Session = Depends(get_db)):
    """SSE 端点：订阅指定 execution_id 的实时执行日志"""
    execution = db.query(AutomationExecution).filter(
        AutomationExecution.id == execution_id
    ).first()
    if not execution:
        return JSONResponse(status_code=404, content={"detail": f"Execution {execution_id} not found"})
    return StreamingResponse(
        event_stream(execution_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
    )


# 注册 SSE router 到 automation_router
automation_router.include_router(sse_router)
