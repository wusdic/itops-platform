"""
配置领域 - Service 层

业务逻辑层，处理配置和凭证相关的核心业务逻辑。
支持配置版本管理、发布流程和凭证安全存储。
"""

import json
import base64
import hashlib
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_

from core.utils.helpers import hash_password, generate_token


class ConfigService:
    """配置服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_configs(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        keyword: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> Tuple[List, int]:
        """获取配置列表"""
        from modules.foundation.db_models.system_configs import SystemConfig

        query = self.db.query(SystemConfig)
        if category:
            query = query.filter(SystemConfig.category == category)
        if keyword:
            query = query.filter(
                or_(
                    SystemConfig.config_key.like(f"%{keyword}%"),
                    SystemConfig.description.like(f"%{keyword}%")
                )
            )
        if tenant_id:
            query = query.filter(SystemConfig.tenant_id == tenant_id)

        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(SystemConfig.updated_at.desc()).offset(offset).limit(page_size).all()
        return items, total

    def get_config(self, config_id: int, tenant_id: Optional[str] = None) -> Optional[object]:
        """获取单个配置"""
        from modules.foundation.db_models.system_configs import SystemConfig

        query = self.db.query(SystemConfig).filter(SystemConfig.id == config_id)
        if tenant_id:
            query = query.filter(SystemConfig.tenant_id == tenant_id)
        return query.first()

    def get_config_by_key(self, config_key: str, tenant_id: Optional[str] = None) -> Optional[object]:
        """根据key获取配置"""
        from modules.foundation.db_models.system_configs import SystemConfig

        query = self.db.query(SystemConfig).filter(SystemConfig.config_key == config_key)
        if tenant_id:
            query = query.filter(SystemConfig.tenant_id == tenant_id)
        return query.first()

    def create_config(self, req, operator: str = None, tenant_id: Optional[str] = None) -> object:
        """创建配置"""
        from modules.foundation.db_models.system_configs import SystemConfig, ConfigVersion

        # 检查key是否已存在
        existing = self.get_config_by_key(req.key, tenant_id)
        if existing:
            raise ValueError(f"Config key '{req.key}' already exists")

        # 解析tags
        tags_json = json.dumps(req.tags) if req.tags else None

        cfg = SystemConfig(
            config_key=req.key,
            config_value=req.value,
            category=req.category,
            data_type=req.data_type,
            description=req.description or "",
            version=1,
            isPublished=False,
            tags=tags_json,
            tenant_id=tenant_id,
            created_by=operator,
            updated_by=operator,
        )
        self.db.add(cfg)
        self.db.flush()

        # 创建初始版本记录
        version_record = ConfigVersion(
            config_id=cfg.id,
            version=1,
            config_value=req.value,
            change_type="create",
            change_summary="Initial creation",
            operator=operator,
            previous_value="",
        )
        self.db.add(version_record)
        self.db.commit()
        self.db.refresh(cfg)
        return cfg

    def update_config(
        self,
        config_id: int,
        req,
        operator: str = None,
        operator_ip: str = None,
        tenant_id: Optional[str] = None,
    ) -> object:
        """更新配置"""
        from modules.foundation.db_models.system_configs import SystemConfig, ConfigVersion

        cfg = self.get_config(config_id, tenant_id)
        if not cfg:
            raise ValueError("Config not found")

        if cfg.isLocked:
            raise ValueError("Config is locked, cannot update")

        # 记录旧值
        old_value = cfg.config_value

        # 更新字段
        if req.value is not None:
            cfg.config_value = req.value
        if req.category is not None:
            cfg.category = req.category
        if req.data_type is not None:
            cfg.data_type = req.data_type
        if req.description is not None:
            cfg.description = req.description
        if req.tags is not None:
            cfg.tags = json.dumps(req.tags) if req.tags else None

        cfg.version += 1
        cfg.updated_by = operator
        cfg.change_summary = req.change_summary or f"Updated to version {cfg.version}"

        # 创建版本记录
        version_record = ConfigVersion(
            config_id=cfg.id,
            version=cfg.version,
            config_value=cfg.config_value,
            change_type="update",
            change_summary=cfg.change_summary,
            operator=operator,
            operator_ip=operator_ip,
            previous_value=old_value,
        )
        self.db.add(version_record)
        self.db.commit()
        self.db.refresh(cfg)
        return cfg

    def delete_config(self, config_id: int, tenant_id: Optional[str] = None) -> bool:
        """删除配置"""
        from modules.foundation.db_models.system_configs import SystemConfig

        cfg = self.get_config(config_id, tenant_id)
        if not cfg:
            return False

        if cfg.isLocked:
            raise ValueError("Config is locked, cannot delete")

        self.db.delete(cfg)
        self.db.commit()
        return True

    def publish_config(
        self,
        config_id: int,
        operator: str = None,
        operator_ip: str = None,
        tenant_id: Optional[str] = None,
    ) -> object:
        """发布配置"""
        from modules.foundation.db_models.system_configs import SystemConfig, ConfigVersion

        cfg = self.get_config(config_id, tenant_id)
        if not cfg:
            raise ValueError("Config not found")

        old_version = cfg.version
        old_published = cfg.isPublished

        cfg.isPublished = True
        cfg.published_at = datetime.now()
        cfg.published_by = operator

        # 创建发布版本记录
        version_record = ConfigVersion(
            config_id=cfg.id,
            version=cfg.version,
            config_value=cfg.config_value,
            change_type="publish",
            change_summary=f"Published version {cfg.version}",
            operator=operator,
            operator_ip=operator_ip,
        )
        self.db.add(version_record)
        self.db.commit()
        self.db.refresh(cfg)
        return cfg

    def rollback_config(
        self,
        config_id: int,
        target_version: int = None,
        operator: str = None,
        operator_ip: str = None,
        tenant_id: Optional[str] = None,
    ) -> object:
        """回滚配置"""
        from modules.foundation.db_models.system_configs import SystemConfig, ConfigVersion

        cfg = self.get_config(config_id, tenant_id)
        if not cfg:
            raise ValueError("Config not found")

        # 获取历史版本
        versions = (
            self.db.query(ConfigVersion)
            .filter(ConfigVersion.config_id == config_id)
            .order_by(ConfigVersion.version.desc())
            .all()
        )

        if not versions:
            raise ValueError("No version history found")

        if target_version is None:
            # 回滚到上一版本（跳过当前版本）
            target = versions[1] if len(versions) > 1 else versions[0]
        else:
            target = next((v for v in versions if v.version == target_version), None)

        if not target:
            raise ValueError(f"Target version {target_version} not found")

        # 记录当前值用于回滚记录
        old_value = cfg.config_value

        # 执行回滚
        cfg.config_value = target.config_value
        cfg.version += 1
        cfg.updated_by = operator

        # 创建回滚版本记录
        version_record = ConfigVersion(
            config_id=cfg.id,
            version=cfg.version,
            config_value=cfg.config_value,
            change_type="rollback",
            change_summary=f"Rolled back to version {target.version}",
            operator=operator,
            operator_ip=operator_ip,
            previous_value=old_value,
        )
        self.db.add(version_record)
        self.db.commit()
        self.db.refresh(cfg)
        return cfg

    def lock_config(
        self,
        config_id: int,
        operator: str = None,
        tenant_id: Optional[str] = None,
    ) -> object:
        """锁定配置"""
        from modules.foundation.db_models.system_configs import SystemConfig

        cfg = self.get_config(config_id, tenant_id)
        if not cfg:
            raise ValueError("Config not found")

        cfg.isLocked = True
        cfg.locked_by = operator
        cfg.locked_at = datetime.now()
        self.db.commit()
        self.db.refresh(cfg)
        return cfg

    def unlock_config(
        self,
        config_id: int,
        tenant_id: Optional[str] = None,
    ) -> object:
        """解锁配置"""
        from modules.foundation.db_models.system_configs import SystemConfig

        cfg = self.get_config(config_id, tenant_id)
        if not cfg:
            raise ValueError("Config not found")

        cfg.isLocked = False
        cfg.locked_by = None
        cfg.locked_at = None
        self.db.commit()
        self.db.refresh(cfg)
        return cfg

    def get_config_versions(
        self,
        config_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List, int]:
        """获取配置版本历史"""
        from modules.foundation.db_models.system_configs import ConfigVersion

        query = self.db.query(ConfigVersion).filter(ConfigVersion.config_id == config_id)
        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(ConfigVersion.version.desc()).offset(offset).limit(page_size).all()
        return items, total


class CredentialService:
    """凭证服务"""

    # 简单的加密密钥（生产环境应使用更安全的方式管理）
    _ENCRYPTION_KEY = None

    @classmethod
    def _get_encryption_key(cls) -> bytes:
        """获取加密密钥"""
        if cls._ENCRYPTION_KEY is None:
            import os
            key_path = "/home/zcxx/.hermes/projects/itops_platform/.credential_key"
            if os.path.exists(key_path):
                with open(key_path, 'rb') as f:
                    cls._ENCRYPTION_KEY = f.read()
            else:
                # 生成随机密钥
                cls._ENCRYPTION_KEY = os.urandom(32)
                os.makedirs(os.path.dirname(key_path), exist_ok=True)
                with open(key_path, 'wb') as f:
                    f.write(cls._ENCRYPTION_KEY)
        return cls._ENCRYPTION_KEY

    @classmethod
    def encrypt_value(cls, value: str) -> str:
        """加密凭证值"""
        import os
        from cryptography.fernet import Fernet

        key = cls._get_encryption_key()
        f = Fernet(base64.urlsafe_b64encode(key[:32]))
        encrypted = f.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()

    @classmethod
    def decrypt_value(cls, encrypted_value: str) -> str:
        """解密凭证值"""
        from cryptography.fernet import Fernet

        key = cls._get_encryption_key()
        f = Fernet(base64.urlsafe_b64encode(key[:32]))
        decrypted = f.decrypt(base64.b64decode(encrypted_value.encode()))
        return decrypted.decode()

    def __init__(self, db: Session):
        self.db = db

    def list_credentials(
        self,
        page: int = 1,
        page_size: int = 20,
        credential_type: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        keyword: Optional[str] = None,
        is_active: Optional[bool] = None,
        tenant_id: Optional[str] = None,
    ) -> Tuple[List, int]:
        """获取凭证列表"""
        from modules.foundation.db_models.system_configs import Credential

        query = self.db.query(Credential)
        if credential_type:
            query = query.filter(Credential.credential_type == credential_type)
        if resource_type:
            query = query.filter(Credential.resource_type == resource_type)
        if resource_id:
            query = query.filter(Credential.resource_id == resource_id)
        if keyword:
            query = query.filter(
                or_(
                    Credential.name.like(f"%{keyword}%"),
                    Credential.description.like(f"%{keyword}%")
                )
            )
        if is_active is not None:
            query = query.filter(Credential.is_active == is_active)
        if tenant_id:
            query = query.filter(Credential.tenant_id == tenant_id)

        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(Credential.updated_at.desc()).offset(offset).limit(page_size).all()
        return items, total

    def get_credential(self, credential_id: int, tenant_id: Optional[str] = None) -> Optional[object]:
        """获取单个凭证"""
        from modules.foundation.db_models.system_configs import Credential

        query = self.db.query(Credential).filter(Credential.id == credential_id)
        if tenant_id:
            query = query.filter(Credential.tenant_id == tenant_id)
        return query.first()

    def create_credential(
        self,
        req,
        operator: str = None,
        tenant_id: Optional[str] = None,
    ) -> object:
        """创建凭证"""
        from modules.foundation.db_models.system_configs import Credential

        # 加密凭证值
        encrypted_value = self.encrypt_value(req.credential_value)

        # 创建hash用于校验（可选）
        value_hash = hashlib.sha256(req.credential_value.encode()).hexdigest()

        # 解析tags
        tags_json = json.dumps(req.tags) if req.tags else None

        # 解析allowed_ips
        allowed_ips_json = json.dumps(req.allowed_ips) if req.allowed_ips else None

        cred = Credential(
            name=req.name,
            credential_type=req.credential_type,
            username=req.username,
            credential_value_encrypted=encrypted_value,
            credential_value_hash=value_hash,
            resource_type=req.resource_type,
            resource_id=req.resource_id,
            resource_name=req.resource_name,
            expires_at=req.expires_at,
            rotation_interval_days=req.rotation_interval_days,
            allowed_ips=allowed_ips_json,
            max_usage_count=req.max_usage_count,
            description=req.description or "",
            tags=tags_json,
            tenant_id=tenant_id,
            created_by=operator,
            updated_by=operator,
            is_active=True,
        )
        self.db.add(cred)
        self.db.commit()
        self.db.refresh(cred)
        return cred

    def update_credential(
        self,
        credential_id: int,
        req,
        operator: str = None,
        tenant_id: Optional[str] = None,
    ) -> object:
        """更新凭证"""
        from modules.foundation.db_models.system_configs import Credential

        cred = self.get_credential(credential_id, tenant_id)
        if not cred:
            raise ValueError("Credential not found")

        if req.name is not None:
            cred.name = req.name
        if req.credential_value is not None:
            cred.credential_value_encrypted = self.encrypt_value(req.credential_value)
            cred.credential_value_hash = hashlib.sha256(req.credential_value.encode()).hexdigest()
            cred.last_rotated_at = datetime.now()
        if req.resource_type is not None:
            cred.resource_type = req.resource_type
        if req.resource_id is not None:
            cred.resource_id = req.resource_id
        if req.resource_name is not None:
            cred.resource_name = req.resource_name
        if req.expires_at is not None:
            cred.expires_at = req.expires_at
        if req.rotation_interval_days is not None:
            cred.rotation_interval_days = req.rotation_interval_days
        if req.allowed_ips is not None:
            cred.allowed_ips = json.dumps(req.allowed_ips) if req.allowed_ips else None
        if req.max_usage_count is not None:
            cred.max_usage_count = req.max_usage_count
        if req.is_active is not None:
            cred.is_active = req.is_active
        if req.description is not None:
            cred.description = req.description
        if req.tags is not None:
            cred.tags = json.dumps(req.tags) if req.tags else None

        cred.updated_by = operator
        self.db.commit()
        self.db.refresh(cred)
        return cred

    def delete_credential(self, credential_id: int, tenant_id: Optional[str] = None) -> bool:
        """删除凭证"""
        from modules.foundation.db_models.system_configs import Credential

        cred = self.get_credential(credential_id, tenant_id)
        if not cred:
            return False

        self.db.delete(cred)
        self.db.commit()
        return True

    def get_credential_value(
        self,
        credential_id: int,
        operator: str = None,
        tenant_id: Optional[str] = None,
    ) -> str:
        """获取凭证解密后的值"""
        from modules.foundation.db_models.system_configs import Credential

        cred = self.get_credential(credential_id, tenant_id)
        if not cred:
            raise ValueError("Credential not found")

        if not cred.is_active_and_valid():
            raise ValueError("Credential is not active or has expired")

        # 更新使用统计
        cred.usage_count += 1
        cred.last_used_at = datetime.now()
        cred.last_used_by = operator
        self.db.commit()

        return self.decrypt_value(cred.credential_value_encrypted)

    def rotate_credential(
        self,
        credential_id: int,
        new_value: str,
        operator: str = None,
        tenant_id: Optional[str] = None,
    ) -> object:
        """轮换凭证"""
        from modules.foundation.db_models.system_configs import Credential

        cred = self.get_credential(credential_id, tenant_id)
        if not cred:
            raise ValueError("Credential not found")

        cred.credential_value_encrypted = self.encrypt_value(new_value)
        cred.credential_value_hash = hashlib.sha256(new_value.encode()).hexdigest()
        cred.last_rotated_at = datetime.now()
        cred.updated_by = operator
        cred.usage_count = 0  # 重置使用计数

        self.db.commit()
        self.db.refresh(cred)
        return cred

    def validate_credential(self, credential_id: int, value: str) -> bool:
        """验证凭证值"""
        from modules.foundation.db_models.system_configs import Credential

        cred = self.get_credential(credential_id)
        if not cred:
            return False

        expected_hash = hashlib.sha256(value.encode()).hexdigest()
        return cred.credential_value_hash == expected_hash

    def get_credentials_by_resource(
        self,
        resource_type: str,
        resource_id: str,
        tenant_id: Optional[str] = None,
    ) -> List:
        """获取指定资源的所有凭证"""
        from modules.foundation.db_models.system_configs import Credential

        query = self.db.query(Credential).filter(
            Credential.resource_type == resource_type,
            Credential.resource_id == resource_id,
        )
        if tenant_id:
            query = query.filter(Credential.tenant_id == tenant_id)
        return query.all()
