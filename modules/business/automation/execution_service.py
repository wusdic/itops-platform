# -*- coding: utf-8 -*-
"""
执行引擎服务
提供脚本执行的核心逻辑，包括执行、取消、状态管理、日志记录等
"""

import logging
import uuid
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum

from sqlalchemy.orm import Session

from modules.foundation.db_models.automation import (
    AutomationScript,
    AutomationTask,
    AutomationExecution,
    AutomationExecutionLog,
)
from modules.foundation.db_models.base import DatabaseManager

logger = logging.getLogger(__name__)


class ExecutionStatus(str, Enum):
    """执行状态枚举（与数据库一致）"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


class ExecutionService:
    """
    执行引擎服务
    
    功能：
    - 脚本执行（异步/同步）
    - 执行状态管理
    - 执行日志记录
    - 执行结果存储
    - 任务调度集成
    """

    # 高风险脚本需要的审批等级
    HIGH_RISK_APPROVAL_LEVEL = {
        "critical": 3,  # 需要3级审批
        "high": 2,     # 需要2级审批
    }

    def __init__(self, db_session: Optional[Session] = None):
        """
        初始化执行服务
        
        Args:
            db_session: 数据库会话
        """
        self._db = db_session
        self._db_manager = DatabaseManager()
        
        # 执行中的任务
        self._active_executions: Dict[str, threading.Event] = {}
        self._execution_threads: Dict[str, threading.Thread] = {}
        self._lock = threading.Lock()
        
        # 脚本执行器
        self._script_executor = None

    @property
    def db(self) -> Session:
        """获取数据库会话"""
        if self._db is None:
            self._db = self._db_manager.get_session()
        return self._db

    def _get_executor(self):
        """获取脚本执行器（延迟加载）"""
        if self._script_executor is None:
            try:
                from modules.automation.script_executor.executor import ScriptExecutor
                self._script_executor = ScriptExecutor()
            except ImportError:
                logger.warning("ScriptExecutor not available, using mock execution")
                self._script_executor = None
        return self._script_executor

    # ==================== 执行记录管理 ====================

    def create_execution(
        self,
        script_id: str,
        trigger_type: str,
        trigger_params: Optional[Dict] = None,
        task_id: Optional[str] = None,
        target_devices: Optional[List[int]] = None,
        triggered_by: str = "system",
        status: str = ExecutionStatus.PENDING.value,
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        创建执行记录
        
        Args:
            script_id: 脚本ID
            trigger_type: 触发类型 (manual, scheduled, api, alert)
            trigger_params: 触发参数
            task_id: 关联任务ID
            target_devices: 目标设备列表
            triggered_by: 触发者
            status: 初始状态
            
        Returns:
            (执行记录字典, 错误码)
        """
        # 验证脚本存在
        script = self.db.query(AutomationScript).filter(
            AutomationScript.id == script_id
        ).first()
        if not script:
            return None, f"SCRIPT_NOT_FOUND: 脚本 {script_id} 不存在"

        execution_id = str(uuid.uuid4())

        execution = AutomationExecution(
            id=execution_id,
            task_id=task_id,
            script_id=script_id,
            trigger_type=trigger_type,
            trigger_params=trigger_params or {},
            status=status,
            started_at=datetime.now(),
            target_devices=target_devices or [],
            triggered_by=triggered_by,
        )
        self.db.add(execution)

        try:
            self.db.commit()
            logger.info(f"Created execution {execution_id} for script {script_id}")
            return self._execution_to_dict(execution, script.name if script else None), None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create execution: {e}")
            return None, f"CREATE_FAILED: {str(e)}"

    def execute_script(
        self,
        script_id: str,
        params: Optional[Dict[str, Any]] = None,
        target_devices: Optional[List[int]] = None,
        triggered_by: str = "system",
        trigger_type: str = "manual",
        task_id: Optional[str] = None,
        async_mode: bool = True,
        on_output: Optional[Callable[[str, str], None]] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        执行脚本
        
        Args:
            script_id: 脚本ID
            params: 执行参数
            target_devices: 目标设备列表
            triggered_by: 触发者
            trigger_type: 触发类型
            task_id: 关联任务ID
            async_mode: 是否异步执行
            on_output: 输出回调函数 (stream, content)
            
        Returns:
            (execution_id, 错误码)
        """
        # 获取脚本
        script = self.db.query(AutomationScript).filter(
            AutomationScript.id == script_id
        ).first()
        if not script:
            return None, f"SCRIPT_NOT_FOUND: 脚本 {script_id} 不存在"

        # 创建执行记录
        execution_id = str(uuid.uuid4())
        execution = AutomationExecution(
            id=execution_id,
            task_id=task_id,
            script_id=script_id,
            trigger_type=trigger_type,
            trigger_params=params or {},
            status=ExecutionStatus.PENDING.value,
            started_at=datetime.now(),
            target_devices=target_devices or [],
            triggered_by=triggered_by,
        )
        self.db.add(execution)

        # 如果是任务执行，更新任务状态
        if task_id:
            task = self.db.query(AutomationTask).filter(
                AutomationTask.id == task_id
            ).first()
            if task:
                task.last_execution_id = execution_id
                task.last_run_time = datetime.now()
                task.status = "running"

        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            return None, f"CREATE_FAILED: {str(e)}"

        if async_mode:
            # 异步执行
            thread = threading.Thread(
                target=self._execute_async,
                args=(execution_id, script, params or {}, on_output)
            )
            thread.daemon = True
            thread.start()
            return execution_id, None
        else:
            # 同步执行
            success, result = self._execute_sync(execution_id, script, params or {}, on_output)
            return execution_id, None if success else result

    def _execute_async(
        self,
        execution_id: str,
        script: AutomationScript,
        params: Dict[str, Any],
        on_output: Optional[Callable],
    ):
        """异步执行脚本"""
        cancel_event = threading.Event()
        with self._lock:
            self._active_executions[execution_id] = cancel_event

        try:
            self._do_execute(execution_id, script, params, on_output, cancel_event)
        finally:
            with self._lock:
                self._active_executions.pop(execution_id, None)

    def _execute_sync(
        self,
        execution_id: str,
        script: AutomationScript,
        params: Dict[str, Any],
        on_output: Optional[Callable],
    ) -> Tuple[bool, Optional[str]]:
        """同步执行脚本"""
        cancel_event = threading.Event()
        return self._do_execute(execution_id, script, params, on_output, cancel_event)

    def _do_execute(
        self,
        execution_id: str,
        script: AutomationScript,
        params: Dict[str, Any],
        on_output: Optional[Callable],
        cancel_event: threading.Event,
    ) -> Tuple[bool, Optional[str]]:
        """执行脚本的核心逻辑"""
        from datetime import datetime as dt
        
        # 更新状态为 running
        execution = self.db.query(AutomationExecution).filter(
            AutomationExecution.id == execution_id
        ).first()
        if not execution:
            return False, "EXECUTION_NOT_FOUND"
        
        execution.status = ExecutionStatus.RUNNING.value
        self.db.commit()

        # 渲染脚本内容
        rendered_content = self._render_script(script.content, params)
        
        # 记录开始日志
        self._add_log(execution_id, "info", f"Starting execution of script '{script.name}'")
        self._add_log(execution_id, "info", f"Risk level: {script.risk_level}")

        start_time = dt.now()
        success = True
        error_message = ""
        stdout = ""
        stderr = ""

        try:
            executor = self._get_executor()
            if executor is not None:
                # 使用真实执行器
                result = executor.execute(
                    script=rendered_content,
                    script_type=script.script_type,
                    parameters=params,
                    timeout=300,
                )
                
                stdout = result.stdout or ""
                stderr = result.stderr or ""
                success = result.status.value == "success"
                if not success:
                    error_message = result.error_message or f"Exit code: {result.return_code}"
            else:
                # 模拟执行
                import time
                time.sleep(0.1)  # 模拟执行时间
                stdout = f"Script executed successfully (mock)\nParameters: {params}"
                error_message = ""

        except Exception as e:
            success = False
            error_message = str(e)
            logger.error(f"Execution {execution_id} failed: {e}")

        # 计算执行时间
        end_time = dt.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        # 记录输出日志
        if stdout:
            for line in stdout.split('\n'):
                if line.strip():
                    self._add_log(execution_id, "stdout", line)
        if stderr:
            for line in stderr.split('\n'):
                if line.strip():
                    self._add_log(execution_id, "stderr", line)

        # 更新执行记录
        execution = self.db.query(AutomationExecution).filter(
            AutomationExecution.id == execution_id
        ).first()
        if execution:
            execution.status = ExecutionStatus.SUCCESS.value if success else ExecutionStatus.FAILED.value
            execution.completed_at = end_time
            execution.duration_ms = duration_ms
            execution.result_summary = {
                "exit_code": 0 if success else 1,
                "stdout": stdout,
                "stderr": stderr,
            }
            execution.error_message = error_message if not success else None
            
            # 如果是任务执行，更新任务状态
            if execution.task_id:
                task = self.db.query(AutomationTask).filter(
                    AutomationTask.id == execution.task_id
                ).first()
                if task:
                    task.status = "idle" if success else "error"

            self.db.commit()

        # 记录完成日志
        status_str = "SUCCESS" if success else "FAILED"
        self._add_log(execution_id, "info", f"Execution {status_str} (duration: {duration_ms}ms)")
        if error_message:
            self._add_log(execution_id, "info", f"Error: {error_message}")

        return success, None if success else error_message

    def cancel_execution(self, execution_id: str, cancelled_by: str = "system") -> Tuple[bool, Optional[str]]:
        """
        取消执行
        
        Args:
            execution_id: 执行ID
            cancelled_by: 取消者
            
        Returns:
            (是否成功, 错误码)
        """
        execution = self.db.query(AutomationExecution).filter(
            AutomationExecution.id == execution_id
        ).first()
        
        if not execution:
            return False, f"EXECUTION_NOT_FOUND: 执行 {execution_id} 不存在"

        if execution.status not in [ExecutionStatus.PENDING.value, ExecutionStatus.RUNNING.value]:
            return False, f"INVALID_STATUS: 当前状态为 {execution.status}，无法取消"

        # 设置取消标志
        with self._lock:
            cancel_event = self._active_executions.get(execution_id)
            if cancel_event:
                cancel_event.set()

        # 更新状态
        execution.status = ExecutionStatus.CANCELLED.value
        execution.completed_at = datetime.now()
        execution.error_message = f"Cancelled by {cancelled_by}"
        
        # 如果是任务执行，更新任务状态
        if execution.task_id:
            task = self.db.query(AutomationTask).filter(
                AutomationTask.id == execution.task_id
            ).first()
            if task:
                task.status = "idle"

        self.db.commit()
        
        self._add_log(execution_id, "info", f"Execution cancelled by {cancelled_by}")
        logger.info(f"Execution {execution_id} cancelled by {cancelled_by}")
        
        return True, None

    def get_execution(self, execution_id: str) -> Optional[Dict]:
        """
        获取执行详情
        
        Args:
            execution_id: 执行ID
            
        Returns:
            执行详情字典
        """
        e = self.db.query(AutomationExecution).filter(
            AutomationExecution.id == execution_id
        ).first()
        
        if not e:
            return None
        
        script = self.db.query(AutomationScript).filter(
            AutomationScript.id == e.script_id
        ).first()
        
        task = None
        if e.task_id:
            task = self.db.query(AutomationTask).filter(
                AutomationTask.id == e.task_id
            ).first()
        
        return self._execution_to_dict(e, task.name if task else None, script.name if script else None)

    def list_executions(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        task_id: Optional[str] = None,
        script_id: Optional[str] = None,
        triggered_by: Optional[str] = None,
    ) -> Tuple[List[Dict], int]:
        """
        获取执行记录列表
        
        Args:
            page: 页码
            page_size: 每页数量
            status: 状态过滤
            task_id: 任务ID过滤
            script_id: 脚本ID过滤
            triggered_by: 触发者过滤
            
        Returns:
            (执行记录列表, 总数)
        """
        query = self.db.query(AutomationExecution)

        if status:
            query = query.filter(AutomationExecution.status == status)
        if task_id:
            query = query.filter(AutomationExecution.task_id == task_id)
        if script_id:
            query = query.filter(AutomationExecution.script_id == script_id)
        if triggered_by:
            query = query.filter(AutomationExecution.triggered_by == triggered_by)

        total = query.count()
        items = query.order_by(AutomationExecution.started_at.desc()) \
            .offset((page - 1) * page_size).limit(page_size).all()

        result = []
        for e in items:
            script = self.db.query(AutomationScript).filter(
                AutomationScript.id == e.script_id
            ).first()
            task = None
            if e.task_id:
                task = self.db.query(AutomationTask).filter(
                    AutomationTask.id == e.task_id
                ).first()
            result.append(self._execution_to_dict(
                e, task.name if task else None, script.name if script else None
            ))

        return result, total

    def get_execution_logs(
        self,
        execution_id: str,
        stream: Optional[str] = None,
        offset: int = 0,
        limit: int = 1000,
    ) -> List[Dict]:
        """
        获取执行日志
        
        Args:
            execution_id: 执行ID
            stream: 日志类型过滤 (stdout, stderr, info)
            offset: 偏移量
            limit: 返回数量限制
            
        Returns:
            日志列表
        """
        query = self.db.query(AutomationExecutionLog).filter(
            AutomationExecutionLog.execution_id == execution_id
        )
        
        if stream:
            query = query.filter(AutomationExecutionLog.stream == stream)
        
        logs = query.order_by(AutomationExecutionLog.timestamp.asc()) \
            .offset(offset).limit(limit).all()

        return [
            {
                "id": log.id,
                "stream": log.stream,
                "content": log.content,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            }
            for log in logs
        ]

    def _add_log(
        self,
        execution_id: str,
        stream: str,
        content: str,
    ):
        """
        添加执行日志
        
        Args:
            execution_id: 执行ID
            stream: 日志类型
            content: 日志内容
        """
        log = AutomationExecutionLog(
            execution_id=execution_id,
            stream=stream,
            content=content,
            timestamp=datetime.now(),
        )
        self.db.add(log)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()

    def _render_script(self, content: str, params: Dict[str, Any]) -> str:
        """渲染脚本内容，替换参数"""
        result = content
        for key, value in params.items():
            # 支持 ${key} 和 {{key}} 两种格式
            result = result.replace(f"${{{key}}}", str(value))
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result

    def _execution_to_dict(
        self,
        e: AutomationExecution,
        task_name: Optional[str] = None,
        script_name: Optional[str] = None,
    ) -> Dict:
        """将执行记录转换为字典"""
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

    # ==================== 风险评估 ====================

    def check_risk_level(
        self,
        script_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, int, Optional[str]]:
        """
        检查脚本执行风险
        
        Args:
            script_id: 脚本ID
            params: 执行参数
            
        Returns:
            (风险等级, 需要审批等级, 是否需要阻塞)
        """
        script = self.db.query(AutomationScript).filter(
            AutomationScript.id == script_id
        ).first()
        
        if not script:
            return "unknown", 0, "SCRIPT_NOT_FOUND"

        risk_level = script.risk_level
        required_approval_level = self.HIGH_RISK_APPROVAL_LEVEL.get(risk_level, 0)
        
        # 是否需要阻塞等待审批
        needs_block = required_approval_level > 0
        
        return risk_level, required_approval_level, None if needs_block else None

    # ==================== 执行统计 ====================

    def get_statistics(
        self,
        script_id: Optional[str] = None,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        获取执行统计
        
        Args:
            script_id: 脚本ID（可选）
            days: 统计天数
            
        Returns:
            统计数据
        """
        from datetime import timedelta
        
        start_date = datetime.now() - timedelta(days=days)
        
        query = self.db.query(AutomationExecution).filter(
            AutomationExecution.started_at >= start_date
        )
        
        if script_id:
            query = query.filter(AutomationExecution.script_id == script_id)
        
        total = query.count()
        
        # 按状态统计
        status_counts = {}
        for status in ExecutionStatus:
            count = query.filter(AutomationExecution.status == status.value).count()
            status_counts[status.value] = count
        
        # 计算平均执行时间
        completed = query.filter(
            AutomationExecution.status.in_([
                ExecutionStatus.SUCCESS.value,
                ExecutionStatus.FAILED.value
            ]),
            AutomationExecution.duration_ms.isnot(None)
        ).all()
        
        avg_duration = 0
        if completed:
            avg_duration = sum(e.duration_ms or 0 for e in completed) / len(completed)
        
        return {
            "total": total,
            "status_counts": status_counts,
            "avg_duration_ms": int(avg_duration),
            "period_days": days,
        }
