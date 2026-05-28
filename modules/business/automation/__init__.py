# -*- coding: utf-8 -*-
"""
自动化执行中心业务模块
包含：脚本管理服务、执行引擎服务、审批流服务
"""

from .script_service import ScriptManagementService
from .execution_service import ExecutionService
from .approval_service import ApprovalService

__all__ = [
    'ScriptManagementService',
    'ExecutionService',
    'ApprovalService',
]

__version__ = '1.0.0'
