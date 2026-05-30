# -*- coding: utf-8 -*-
"""
审批流服务
为自动化脚本执行提供审批流程管理，包括：
- 审批规则定义
- 多级审批支持
- 审批状态跟踪
- 审批与执行联动
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

from sqlalchemy.orm import Session

from modules.foundation.db_models.base import Base, DatabaseManager

logger = logging.getLogger(__name__)


class ApprovalStatus(str):
    """审批状态"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ApprovalLevel:
    """审批等级定义"""
    LEVEL_1 = 1  # 初级审批（组长）
    LEVEL_2 = 2  # 中级审批（经理）
    LEVEL_3 = 3  # 高级审批（总监）


# 风险等级与审批等级映射
RISK_APPROVAL_LEVEL_MAP = {
    "critical": ApprovalLevel.LEVEL_3,
    "high": ApprovalLevel.LEVEL_2,
    "medium": ApprovalLevel.LEVEL_1,
    "low": 0,  # 不需要审批
}


def get_approval_table_definition():
    """获取审批表定义（用于延迟创建）"""
    from sqlalchemy import Column, String, Text, Integer, BigInteger, DateTime, JSON, Boolean, ForeignKey, Index
    
    class AutomationApprovalRequest(Base):
        """自动化执行审批请求表"""
        __tablename__ = "automation_approval_requests"

        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        
        # 关联执行
        execution_id = Column(String(36), ForeignKey("automation_executions.id"), nullable=False)
        script_id = Column(String(36), ForeignKey("automation_scripts.id"), nullable=False)
        
        # 审批配置
        risk_level = Column(String(16), nullable=False)
        required_approval_level = Column(Integer, nullable=False, default=0)
        current_approval_level = Column(Integer, default=0)
        
        # 状态
        status = Column(String(32), default=ApprovalStatus.PENDING, nullable=False)
        
        # 审批人配置（JSON格式，支持多级审批）
        # [{"level": 1, "approvers": ["user1", "user2"], "mode": "one"}, ...]
        approval_config = Column(JSON, default=list)
        
        # 审批记录
        approval_records = Column(JSON, default=list)
        # [{"level": 1, "approver": "user1", "action": "approve", "comment": "...", "time": "..."}, ...]
        
        # 原因
        reason = Column(Text)
        
        # 时间
        created_by = Column(String(64))
        created_at = Column(DateTime, default=datetime.now)
        updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
        expires_at = Column(DateTime)
        completed_at = Column(DateTime)
        
        __table_args__ = (
            Index("idx_approval_execution", "execution_id"),
            Index("idx_approval_status", "status"),
            Index("idx_approval_script", "script_id"),
        )

    return AutomationApprovalRequest


# 延迟获取模型类（带缓存）
_approval_model_cache = None

def get_approval_model():
    """获取审批模型类（延迟加载，缓存结果）"""
    global _approval_model_cache
    if _approval_model_cache is None:
        _approval_model_cache = get_approval_table_definition()
    return _approval_model_cache


class ApprovalService:
    """
    审批流服务
    
    功能：
    - 评估脚本执行是否需要审批
    - 创建审批请求
    - 处理审批（通过/拒绝）
    - 查询审批状态
    - 审批与执行联动
    """

    # 审批超时时间（小时）
    DEFAULT_TIMEOUT_HOURS = 24

    # 审批模式
    APPROVAL_MODE_ONE = "one"      # 或签（任一审批人通过即可）
    APPROVAL_MODE_ALL = "all"       # 会签（所有审批人必须通过）

    def __init__(self, db_session: Optional[Session] = None):
        """
        初始化审批服务
        
        Args:
            db_session: 数据库会话
        """
        self._db = db_session
        self._db_manager = DatabaseManager()

    @property
    def db(self) -> Session:
        """获取数据库会话"""
        if self._db is None:
            self._db = self._db_manager.get_session()
        return self._db

    def evaluate_approval_required(
        self,
        script_id: str,
        risk_level: str,
        execution_context: Optional[Dict] = None,
    ) -> Tuple[bool, int, Dict]:
        """
        评估是否需要审批
        
        Args:
            script_id: 脚本ID
            risk_level: 风险等级 (low, medium, high, critical)
            execution_context: 执行上下文（包含目标设备、参数等信息）
            
        Returns:
            (是否需要审批, 需要审批等级, 评估详情)
        """
        required_level = RISK_APPROVAL_LEVEL_MAP.get(risk_level, 0)
        needs_approval = required_level > 0

        details = {
            "risk_level": risk_level,
            "required_approval_level": required_level,
            "approval_mode": self.APPROVAL_MODE_ONE if required_level > 0 else None,
            "estimated_wait_time_hours": self.DEFAULT_TIMEOUT_HOURS,
        }

        # 如果是高风险脚本，检查目标设备
        if needs_approval and execution_context:
            target_devices = execution_context.get("target_devices", [])
            if len(target_devices) > 10:
                # 目标设备超过10台，提升审批等级
                details["target_device_count"] = len(target_devices)
                details["approval_note"] = "Multiple targets, may require higher approval"

        return needs_approval, required_level, details

    def create_approval_request(
        self,
        execution_id: str,
        script_id: str,
        risk_level: str,
        required_approval_level: int,
        created_by: str,
        reason: str = "",
        approval_config: Optional[List[Dict]] = None,
        timeout_hours: int = None,
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        创建审批请求
        
        Args:
            execution_id: 执行ID
            script_id: 脚本ID
            risk_level: 风险等级
            required_approval_level: 需要审批等级
            created_by: 创建者
            reason: 审批原因
            approval_config: 审批配置
            timeout_hours: 超时时间（小时）
            
        Returns:
            (审批请求字典, 错误码)
        """
        ApprovalModel = get_approval_model()

        # 检查是否已有待处理的审批请求
        existing = self.db.query(ApprovalModel).filter(
            ApprovalModel.execution_id == execution_id,
            ApprovalModel.status == ApprovalStatus.PENDING
        ).first()
        if existing:
            return None, "APPROVAL_ALREADY_EXISTS: 该执行已有待处理的审批请求"

        approval_id = str(uuid.uuid4())
        timeout = timeout_hours or self.DEFAULT_TIMEOUT_HOURS

        # 构建默认审批配置
        if approval_config is None:
            approval_config = self._build_default_approval_config(required_approval_level)

        request = ApprovalModel(
            id=approval_id,
            execution_id=execution_id,
            script_id=script_id,
            risk_level=risk_level,
            required_approval_level=required_approval_level,
            current_approval_level=0,
            status=ApprovalStatus.PENDING,
            approval_config=approval_config,
            approval_records=[],
            reason=reason,
            created_by=created_by,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=timeout),
        )
        self.db.add(request)

        try:
            self.db.commit()
            logger.info(f"Created approval request {approval_id} for execution {execution_id}")
            return self._to_dict(request), None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create approval request: {e}")
            return None, f"CREATE_FAILED: {str(e)}"

    def get_approval_request(self, approval_id: str) -> Optional[Dict]:
        """
        获取审批请求详情
        
        Args:
            approval_id: 审批请求ID
            
        Returns:
            审批请求详情
        """
        ApprovalModel = get_approval_model()
        request = self.db.query(ApprovalModel).filter(
            ApprovalModel.id == approval_id
        ).first()
        return self._to_dict(request) if request else None

    def get_approval_request_by_execution(self, execution_id: str) -> Optional[Dict]:
        """
        根据执行ID获取审批请求
        
        Args:
            execution_id: 执行ID
            
        Returns:
            审批请求详情
        """
        ApprovalModel = get_approval_model()
        request = self.db.query(ApprovalModel).filter(
            ApprovalModel.execution_id == execution_id
        ).first()
        return self._to_dict(request) if request else None

    def list_pending_approvals(
        self,
        approver: str,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Dict], int]:
        """
        获取待我审批的列表
        
        Args:
            approver: 审批人
            page: 页码
            page_size: 每页数量
            
        Returns:
            (审批请求列表, 总数)
        """
        ApprovalModel = get_approval_model()
        
        # 获取所有待审批请求
        query = self.db.query(ApprovalModel).filter(
            ApprovalModel.status == ApprovalStatus.PENDING
        )
        
        # 过滤出当前审批人可以审批的
        all_requests = query.all()
        filtered = []
        for req in all_requests:
            config = req.approval_config or []
            current_level = req.current_approval_level + 1
            
            # 查找当前级别是否有该审批人
            level_config = next(
                (c for c in config if c.get("level") == current_level),
                None
            )
            if level_config and approver in level_config.get("approvers", []):
                filtered.append(req)

        # 分页
        total = len(filtered)
        start = (page - 1) * page_size
        end = start + page_size
        items = filtered[start:end]

        return [self._to_dict(r) for r in items], total

    def approve(
        self,
        approval_id: str,
        approver: str,
        comment: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        审批通过
        
        Args:
            approval_id: 审批请求ID
            approver: 审批人
            comment: 审批意见
            
        Returns:
            (是否成功, 错误码)
        """
        ApprovalModel = get_approval_model()
        request = self.db.query(ApprovalModel).filter(
            ApprovalModel.id == approval_id
        ).first()
        
        if not request:
            return False, "NOT_FOUND: 审批请求不存在"
        
        if request.status != ApprovalStatus.PENDING:
            return False, f"INVALID_STATUS: 当前状态为 {request.status}"
        
        # 检查审批人是否有权限
        current_level = request.current_approval_level + 1
        level_config = None
        for config in (request.approval_config or []):
            if config.get("level") == current_level:
                level_config = config
                break
        
        if not level_config:
            return False, "INVALID_STATE: 当前没有需要审批的级别"
        
        if approver not in level_config.get("approvers", []):
            return False, "PERMISSION_DENIED: 您没有审批权限"
        
        # 记录审批
        record = {
            "level": current_level,
            "approver": approver,
            "action": "approve",
            "comment": comment or "",
            "time": datetime.now().isoformat(),
        }
        
        records = list(request.approval_records or [])
        records.append(record)
        request.approval_records = records
        
        # 检查是否完成当前级别
        mode = level_config.get("mode", self.APPROVAL_MODE_ONE)
        
        if mode == self.APPROVAL_MODE_ONE:
            # 或签模式：当前级别一人通过即可
            request.current_approval_level = current_level
        else:
            # 会签模式：需要所有当前级别审批人都通过
            all_approvers = level_config.get("approvers", [])
            approved_approvers = [
                r["approver"] for r in records 
                if r.get("level") == current_level and r.get("action") == "approve"
            ]
            if set(approved_approvers) >= set(all_approvers):
                request.current_approval_level = current_level
        
        # 检查是否全部审批完成
        if request.current_approval_level >= request.required_approval_level:
            request.status = ApprovalStatus.APPROVED
            request.completed_at = datetime.now()
            
            # 触发执行
            self._trigger_execution(request.execution_id)
        else:
            request.updated_at = datetime.now()
        
        try:
            self.db.commit()
            logger.info(f"Approval {approval_id} approved by {approver} at level {current_level}")
            return True, None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to approve: {e}")
            return False, f"APPROVE_FAILED: {str(e)}"

    def reject(
        self,
        approval_id: str,
        approver: str,
        comment: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        审批拒绝
        
        Args:
            approval_id: 审批请求ID
            approver: 审批人
            comment: 拒绝原因
            
        Returns:
            (是否成功, 错误码)
        """
        ApprovalModel = get_approval_model()
        request = self.db.query(ApprovalModel).filter(
            ApprovalModel.id == approval_id
        ).first()
        
        if not request:
            return False, "NOT_FOUND: 审批请求不存在"
        
        if request.status != ApprovalStatus.PENDING:
            return False, f"INVALID_STATUS: 当前状态为 {request.status}"
        
        # 检查审批人是否有权限
        current_level = request.current_approval_level + 1
        level_config = None
        for config in (request.approval_config or []):
            if config.get("level") == current_level:
                level_config = config
                break
        
        if level_config and approver not in level_config.get("approvers", []):
            return False, "PERMISSION_DENIED: 您没有审批权限"
        
        # 记录拒绝
        record = {
            "level": current_level,
            "approver": approver,
            "action": "reject",
            "comment": comment or "",
            "time": datetime.now().isoformat(),
        }
        
        records = list(request.approval_records or [])
        records.append(record)
        request.approval_records = records
        
        # 拒绝即终止整个审批流程
        request.status = ApprovalStatus.REJECTED
        request.completed_at = datetime.now()
        
        # 取消关联的执行
        self._cancel_execution(request.execution_id, reason=f"Rejected by {approver}")
        
        try:
            self.db.commit()
            logger.info(f"Approval {approval_id} rejected by {approver}")
            return True, None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to reject: {e}")
            return False, f"REJECT_FAILED: {str(e)}"

    def cancel_approval(
        self,
        approval_id: str,
        cancelled_by: str,
        reason: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        取消审批请求
        
        Args:
            approval_id: 审批请求ID
            cancelled_by: 取消者
            reason: 取消原因
            
        Returns:
            (是否成功, 错误码)
        """
        ApprovalModel = get_approval_model()
        request = self.db.query(ApprovalModel).filter(
            ApprovalModel.id == approval_id
        ).first()
        
        if not request:
            return False, "NOT_FOUND: 审批请求不存在"
        
        if request.status != ApprovalStatus.PENDING:
            return False, f"INVALID_STATUS: 当前状态为 {request.status}"
        
        request.status = ApprovalStatus.CANCELLED
        request.completed_at = datetime.now()
        
        # 取消关联的执行
        self._cancel_execution(request.execution_id, reason=f"Cancelled by {cancelled_by}")
        
        try:
            self.db.commit()
            logger.info(f"Approval {approval_id} cancelled by {cancelled_by}")
            return True, None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to cancel approval: {e}")
            return False, f"CANCEL_FAILED: {str(e)}"

    def check_timeout(self) -> List[Dict]:
        """
        检查并处理超时的审批请求
        
        Returns:
            超时的审批请求列表
        """
        ApprovalModel = get_approval_model()
        now = datetime.now()
        
        timed_out = self.db.query(ApprovalModel).filter(
            ApprovalModel.status == ApprovalStatus.PENDING,
            ApprovalModel.expires_at < now
        ).all()
        
        for request in timed_out:
            request.status = ApprovalStatus.TIMEOUT
            request.completed_at = now
            
            # 取消关联的执行
            self._cancel_execution(request.execution_id, reason="Approval timeout")
        
        if timed_out:
            self.db.commit()
            logger.info(f"Marked {len(timed_out)} approval requests as timeout")
        
        return [self._to_dict(r) for r in timed_out]

    def _build_default_approval_config(self, required_level: int) -> List[Dict]:
        """
        构建默认审批配置
        
        Args:
            required_level: 需要审批等级
            
        Returns:
            审批配置列表
        """
        config = []
        
        if required_level >= ApprovalLevel.LEVEL_1:
            config.append({
                "level": ApprovalLevel.LEVEL_1,
                "approvers": ["组长"],  # 默认审批人，实际应从组织架构获取
                "mode": self.APPROVAL_MODE_ONE,
            })
        
        if required_level >= ApprovalLevel.LEVEL_2:
            config.append({
                "level": ApprovalLevel.LEVEL_2,
                "approvers": ["经理"],
                "mode": self.APPROVAL_MODE_ONE,
            })
        
        if required_level >= ApprovalLevel.LEVEL_3:
            config.append({
                "level": ApprovalLevel.LEVEL_3,
                "approvers": ["总监"],
                "mode": self.APPROVAL_MODE_ONE,
            })
        
        return config

    def _trigger_execution(self, execution_id: str):
        """
        触发执行（审批通过后）
        
        Args:
            execution_id: 执行ID
        """
        try:
            from modules.foundation.db_models.automation import AutomationExecution
            execution = self.db.query(AutomationExecution).filter(
                AutomationExecution.id == execution_id
            ).first()
            
            if execution and execution.status == "pending_approval":
                execution.status = "pending"
                logger.info(f"Execution {execution_id} approved, now pending")
        except Exception as e:
            logger.error(f"Failed to trigger execution: {e}")

    def _cancel_execution(self, execution_id: str, reason: str):
        """
        取消执行（审批拒绝后）
        
        Args:
            execution_id: 执行ID
            reason: 取消原因
        """
        try:
            from modules.foundation.db_models.automation import AutomationExecution
            execution = self.db.query(AutomationExecution).filter(
                AutomationExecution.id == execution_id
            ).first()
            
            if execution and execution.status in ["pending", "pending_approval"]:
                execution.status = "cancelled"
                execution.error_message = reason
                logger.info(f"Execution {execution_id} cancelled: {reason}")
        except Exception as e:
            logger.error(f"Failed to cancel execution: {e}")

    def _to_dict(self, request) -> Dict:
        """将审批请求转换为字典"""
        return {
            "id": request.id,
            "execution_id": request.execution_id,
            "script_id": request.script_id,
            "risk_level": request.risk_level,
            "required_approval_level": request.required_approval_level,
            "current_approval_level": request.current_approval_level,
            "status": request.status,
            "approval_config": request.approval_config or [],
            "approval_records": request.approval_records or [],
            "reason": request.reason,
            "created_by": request.created_by,
            "created_at": request.created_at.isoformat() if request.created_at else None,
            "updated_at": request.updated_at.isoformat() if request.updated_at else None,
            "expires_at": request.expires_at.isoformat() if request.expires_at else None,
            "completed_at": request.completed_at.isoformat() if request.completed_at else None,
        }
