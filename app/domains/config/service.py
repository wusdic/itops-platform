"""
配置领域 - Service 层

业务逻辑层，处理配置和凭证相关的核心业务逻辑。
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session


class ConfigService:
    """配置服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_configs(self, page=1, page_size=20, category=None, name=None) -> Tuple[List, int]:
        """获取配置列表"""
        from modules.foundation.db_models.system_configs import SystemConfig
        query = self.db.query(SystemConfig)
        if category:
            query = query.filter(SystemConfig.category == category)
        if name:
            query = query.filter(SystemConfig.config_key.like(f"%{name}%"))
        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(SystemConfig.id.desc()).offset(offset).limit(page_size).all()
        return items, total

    def get_config(self, config_id: int) -> Optional[object]:
        from modules.foundation.db_models.system_configs import SystemConfig
        return self.db.query(SystemConfig).filter(SystemConfig.id == config_id).first()

    def create_config(self, req) -> object:
        from modules.foundation.db_models.system_configs import SystemConfig
        from datetime import datetime
        cfg = SystemConfig(
            config_key=req.key,
            config_value=req.value,
            category=req.category,
            description=req.description or "",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.db.add(cfg)
        self.db.commit()
        self.db.refresh(cfg)
        return cfg

    def update_config(self, config_id: int, req) -> Optional[object]:
        from modules.foundation.db_models.system_configs import SystemConfig
        from datetime import datetime
        cfg = self.db.query(SystemConfig).filter(SystemConfig.id == config_id).first()
        if not cfg:
            return None
        if req.value is not None:
            cfg.config_value = req.value
        if req.description is not None:
            cfg.description = req.description
        cfg.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(cfg)
        return cfg

    def delete_config(self, config_id: int) -> bool:
        from modules.foundation.db_models.system_configs import SystemConfig
        cfg = self.db.query(SystemConfig).filter(SystemConfig.id == config_id).first()
        if not cfg:
            return False
        self.db.delete(cfg)
        self.db.commit()
        return True
