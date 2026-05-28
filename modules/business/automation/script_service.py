# -*- coding: utf-8 -*-
"""
脚本管理服务
提供脚本的创建、更新、版本管理、参数校验等功能
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from sqlalchemy.orm import Session

from modules.foundation.db_models.automation import (
    AutomationScript,
    AutomationScriptVersion,
)
from modules.foundation.db_models.base import DatabaseManager
from app.common.error_codes import ErrorCode

logger = logging.getLogger(__name__)


class ScriptManagementService:
    """
    脚本管理服务
    
    功能：
    - 脚本 CRUD 操作
    - 版本管理（自动保存版本历史）
    - 参数校验
    - 风险等级评估
    - 标签管理
    """

    # 风险等级定义
    RISK_LEVELS = ['low', 'medium', 'high', 'critical']
    
    # 支持的脚本类型
    SCRIPT_TYPES = ['shell', 'python', 'ansible', 'powershell']
    
    # 高危关键词（用于风险评估）
    DANGEROUS_KEYWORDS = [
        r'rm -rf', r'drop table', r'delete from', r'truncate',
        r'shutdown', r'reboot', r'init 0', r'init 6',
        r'format', r'fdisk', r'mkfs',
        r'passwd', r'chpasswd', r'su root',
        r'chmod 777', r'chmod -R 777',
        r'wget.*\| sh', r'curl.*\| sh',
    ]

    def __init__(self, db_session: Optional[Session] = None):
        """
        初始化脚本管理服务
        
        Args:
            db_session: 数据库会话，如果为None则使用 db_manager 获取
        """
        self._db = db_session
        self._db_manager = DatabaseManager()

    @property
    def db(self) -> Session:
        """获取数据库会话"""
        if self._db is None:
            self._db = self._db_manager.get_session()
        return self._db

    def list_scripts(
        self,
        page: int = 1,
        page_size: int = 20,
        script_type: Optional[str] = None,
        risk_level: Optional[str] = None,
        keyword: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Tuple[List[Dict], int]:
        """
        获取脚本列表（分页）
        
        Args:
            page: 页码
            page_size: 每页数量
            script_type: 脚本类型过滤
            risk_level: 风险等级过滤
            keyword: 关键词搜索
            tags: 标签过滤
            
        Returns:
            (脚本列表, 总数)
        """
        query = self.db.query(AutomationScript)

        if script_type:
            query = query.filter(AutomationScript.script_type == script_type)
        if risk_level:
            query = query.filter(AutomationScript.risk_level == risk_level)
        if keyword:
            query = query.filter(
                (AutomationScript.name.contains(keyword)) |
                (AutomationScript.description.contains(keyword))
            )
        if tags:
            # JSON 数组包含所有指定标签
            for tag in tags:
                query = query.filter(AutomationScript.tags.contains(tag))

        total = query.count()
        items = query.order_by(AutomationScript.updated_at.desc()) \
            .offset((page - 1) * page_size).limit(page_size).all()

        return [self._to_dict(s) for s in items], total

    def get_script(self, script_id: str) -> Optional[Dict]:
        """
        获取脚本详情
        
        Args:
            script_id: 脚本ID
            
        Returns:
            脚本详情字典，不存在返回 None
        """
        script = self.db.query(AutomationScript).filter(
            AutomationScript.id == script_id
        ).first()
        return self._to_dict(script) if script else None

    def create_script(
        self,
        name: str,
        script_type: str,
        content: str,
        description: str = "",
        risk_level: str = "medium",
        params_schema: Optional[List[Dict]] = None,
        tags: Optional[List[str]] = None,
        created_by: str = "system",
    ) -> Tuple[Dict, Optional[str]]:
        """
        创建新脚本
        
        Args:
            name: 脚本名称
            script_type: 脚本类型
            content: 脚本内容
            description: 脚本描述
            risk_level: 风险等级
            params_schema: 参数定义
            tags: 标签
            created_by: 创建者
            
        Returns:
            (创建的脚本字典, 错误码)
        """
        # 参数校验
        if script_type not in self.SCRIPT_TYPES:
            return {}, f"INVALID_SCRIPT_TYPE: 支持的类型: {', '.join(self.SCRIPT_TYPES)}"
        
        if risk_level not in self.RISK_LEVELS:
            return {}, f"INVALID_RISK_LEVEL: 支持的等级: {', '.join(self.RISK_LEVELS)}"

        if not name or not name.strip():
            return {}, "INVALID_NAME: 脚本名称不能为空"

        if not content or not content.strip():
            return {}, "INVALID_CONTENT: 脚本内容不能为空"

        # 检查名称重复
        existing = self.db.query(AutomationScript).filter(
            AutomationScript.name == name.strip()
        ).first()
        if existing:
            return {}, f"DUPLICATE_NAME: 脚本名称 '{name}' 已存在"

        script_id = str(uuid.uuid4())

        # 自动评估风险等级
        assessed_risk = self._assess_risk_level(content, risk_level)

        # 保存第一个版本
        version = AutomationScriptVersion(
            id=str(uuid.uuid4()),
            script_id=script_id,
            version=1,
            content=content,
            change_summary="Initial version",
            created_by=created_by,
        )
        self.db.add(version)

        # 创建脚本
        script = AutomationScript(
            id=script_id,
            name=name.strip(),
            description=description,
            script_type=script_type,
            content=content,
            risk_level=assessed_risk,
            params_schema=params_schema or [],
            tags=tags or [],
            source="manual",
            created_by=created_by,
            updated_by=created_by,
        )
        self.db.add(script)

        try:
            self.db.commit()
            logger.info(f"Created script {script_id} by {created_by}")
            return self._to_dict(script), None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create script: {e}")
            return {}, f"CREATE_FAILED: {str(e)}"

    def update_script(
        self,
        script_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        script_type: Optional[str] = None,
        content: Optional[str] = None,
        risk_level: Optional[str] = None,
        params_schema: Optional[List[Dict]] = None,
        tags: Optional[List[str]] = None,
        updated_by: str = "system",
        change_summary: Optional[str] = None,
    ) -> Tuple[Dict, Optional[str]]:
        """
        更新脚本（自动保存版本）
        
        Args:
            script_id: 脚本ID
            name: 脚本名称
            description: 脚本描述
            script_type: 脚本类型
            content: 脚本内容
            risk_level: 风险等级
            params_schema: 参数定义
            tags: 标签
            updated_by: 更新者
            change_summary: 变更说明
            
        Returns:
            (更新的脚本字典, 错误码)
        """
        script = self.db.query(AutomationScript).filter(
            AutomationScript.id == script_id
        ).first()
        
        if not script:
            return {}, f"NOT_FOUND: 脚本 {script_id} 不存在"

        # 参数校验
        if name is not None and not name.strip():
            return {}, "INVALID_NAME: 脚本名称不能为空"
        
        if script_type is not None and script_type not in self.SCRIPT_TYPES:
            return {}, f"INVALID_SCRIPT_TYPE: 支持的类型: {', '.join(self.SCRIPT_TYPES)}"
        
        if risk_level is not None and risk_level not in self.RISK_LEVELS:
            return {}, f"INVALID_RISK_LEVEL: 支持的等级: {', '.join(self.RISK_LEVELS)}"

        # 检查名称重复（排除自己）
        if name is not None and name.strip() != script.name:
            existing = self.db.query(AutomationScript).filter(
                AutomationScript.name == name.strip(),
                AutomationScript.id != script_id
            ).first()
            if existing:
                return {}, f"DUPLICATE_NAME: 脚本名称 '{name}' 已存在"

        # 保存当前内容为新版本
        last_version = self.db.query(AutomationScriptVersion) \
            .filter(AutomationScriptVersion.script_id == script_id) \
            .order_by(AutomationScriptVersion.version.desc()).first()
        new_version_num = (last_version.version + 1) if last_version else 1

        version = AutomationScriptVersion(
            id=str(uuid.uuid4()),
            script_id=script_id,
            version=new_version_num,
            content=script.content,
            change_summary=change_summary or f"Before update to v{new_version_num}",
            created_by=updated_by,
        )
        self.db.add(version)

        # 更新字段
        if name is not None:
            script.name = name.strip()
        if description is not None:
            script.description = description
        if script_type is not None:
            script.script_type = script_type
        if content is not None:
            script.content = content
            # 重新评估风险
            script.risk_level = self._assess_risk_level(content, risk_level or script.risk_level)
        elif risk_level is not None:
            script.risk_level = risk_level
        if params_schema is not None:
            script.params_schema = params_schema
        if tags is not None:
            script.tags = tags

        script.updated_by = updated_by
        script.updated_at = datetime.now()

        try:
            self.db.commit()
            logger.info(f"Updated script {script_id} by {updated_by}")
            return self._to_dict(script), None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update script: {e}")
            return {}, f"UPDATE_FAILED: {str(e)}"

    def delete_script(self, script_id: str) -> Tuple[bool, Optional[str]]:
        """
        删除脚本
        
        Args:
            script_id: 脚本ID
            
        Returns:
            (是否成功, 错误码)
        """
        script = self.db.query(AutomationScript).filter(
            AutomationScript.id == script_id
        ).first()
        
        if not script:
            return False, f"NOT_FOUND: 脚本 {script_id} 不存在"

        # 删除版本记录（级联会自动处理，但显式删除更安全）
        self.db.query(AutomationScriptVersion).filter(
            AutomationScriptVersion.script_id == script_id
        ).delete()

        # 删除脚本
        self.db.delete(script)

        try:
            self.db.commit()
            logger.info(f"Deleted script {script_id}")
            return True, None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete script: {e}")
            return False, f"DELETE_FAILED: {str(e)}"

    def get_versions(self, script_id: str) -> List[Dict]:
        """
        获取脚本版本历史
        
        Args:
            script_id: 脚本ID
            
        Returns:
            版本列表
        """
        versions = self.db.query(AutomationScriptVersion) \
            .filter(AutomationScriptVersion.script_id == script_id) \
            .order_by(AutomationScriptVersion.version.desc()).all()

        return [
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

    def get_version(self, script_id: str, version: int) -> Optional[Dict]:
        """
        获取指定版本
        
        Args:
            script_id: 脚本ID
            version: 版本号
            
        Returns:
            版本详情
        """
        v = self.db.query(AutomationScriptVersion) \
            .filter(
                AutomationScriptVersion.script_id == script_id,
                AutomationScriptVersion.version == version
            ).first()
        
        if not v:
            return None
        
        return {
            "id": v.id,
            "version": v.version,
            "content": v.content,
            "change_summary": v.change_summary,
            "created_by": v.created_by,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }

    def rollback_version(
        self,
        script_id: str,
        version: int,
        updated_by: str = "system"
    ) -> Tuple[Dict, Optional[str]]:
        """
        回滚到指定版本
        
        Args:
            script_id: 脚本ID
            version: 版本号
            updated_by: 更新者
            
        Returns:
            (回滚后的脚本字典, 错误码)
        """
        target_version = self.get_version(script_id, version)
        if not target_version:
            return {}, f"NOT_FOUND: 版本 {version} 不存在"

        return self.update_script(
            script_id=script_id,
            content=target_version["content"],
            updated_by=updated_by,
            change_summary=f"Rollback to v{version}"
        )

    def validate_params(
        self,
        script_id: str,
        params: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], List[Dict]]:
        """
        校验脚本参数
        
        Args:
            script_id: 脚本ID
            params: 待校验的参数
            
        Returns:
            (是否通过, 错误信息, 缺失/错误的参数列表)
        """
        script = self.db.query(AutomationScript).filter(
            AutomationScript.id == script_id
        ).first()
        
        if not script:
            return False, f"Script {script_id} not found", []

        schema = script.params_schema or []
        errors = []

        for param_def in schema:
            param_name = param_def.get("name")
            param_type = param_def.get("type", "string")
            required = param_def.get("required", False)
            default = param_def.get("default")

            # 检查必填参数
            if required and param_name not in params:
                if default is None:
                    errors.append({
                        "name": param_name,
                        "error": "missing_required",
                        "message": f"Required parameter '{param_name}' is missing"
                    })
                    continue

            # 检查类型
            if param_name in params:
                value = params[param_name]
                if not self._validate_param_type(value, param_type):
                    errors.append({
                        "name": param_name,
                        "error": "invalid_type",
                        "message": f"Parameter '{param_name}' must be of type {param_type}"
                    })

        return len(errors) == 0, None if errors else "Invalid parameters", errors

    def _validate_param_type(self, value: Any, param_type: str) -> bool:
        """校验参数类型"""
        if value is None:
            return True
        
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        
        expected_type = type_map.get(param_type)
        if expected_type is None:
            return True  # 未知类型不校验
        
        return isinstance(value, expected_type)

    def _assess_risk_level(
        self,
        content: str,
        declared_level: str
    ) -> str:
        """
        自动评估风险等级
        
        Args:
            content: 脚本内容
            declared_level: 声明的风险等级
            
        Returns:
            评估后的风险等级
        """
        import re
        
        content_lower = content.lower()
        
        # 检查高危关键词
        for keyword in self.DANGEROUS_KEYWORDS:
            if re.search(keyword, content_lower, re.IGNORECASE):
                # 如果声明的是 low，但检测到高危操作，提升为 critical
                if declared_level == "low":
                    return "critical"
                # 如果声明的是 medium/high，但检测到高危操作，提升为 critical
                return "critical"
        
        # 检查敏感操作数量
        sensitive_count = sum(1 for kw in [
            'sudo', 'chown', 'chgrp', 'rm ', 'del ', 'delete',
            'kill', 'pkill', 'killall',
        ] if kw in content_lower)
        
        if sensitive_count >= 3 and declared_level in ['low', 'medium']:
            return "high"
        
        return declared_level

    def _to_dict(self, script: AutomationScript) -> Dict:
        """将脚本对象转换为字典"""
        return {
            "id": script.id,
            "name": script.name,
            "description": script.description,
            "script_type": script.script_type,
            "content": script.content,
            "risk_level": script.risk_level,
            "params_schema": script.params_schema or [],
            "tags": script.tags or [],
            "source": script.source,
            "created_by": script.created_by,
            "updated_by": script.updated_by,
            "created_at": script.created_at.isoformat() if script.created_at else None,
            "updated_at": script.updated_at.isoformat() if script.updated_at else None,
        }
