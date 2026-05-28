"""
资产领域 - Service 层

业务逻辑层，处理资产相关的核心业务逻辑。
复用现有的 modules.foundation.db_models Device 模型。
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_


class AssetService:
    """资产服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_assets(
        self,
        page: int = 1,
        page_size: int = 20,
        name: Optional[str] = None,
        device_type: Optional[str] = None,
    ) -> Tuple[List, int]:
        """获取资产列表"""
        from modules.foundation.db_models.devices import Device

        query = self.db.query(Device)

        if name:
            query = query.filter(Device.name.like(f"%{name}%"))
        if device_type:
            query = query.filter(Device.device_type == device_type)

        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(Device.id.desc()).offset(offset).limit(page_size).all()

        return items, total

    def get_asset(self, asset_id: int) -> Optional[object]:
        """获取单个资产"""
        from modules.foundation.db_models.devices import Device
        return self.db.query(Device).filter(Device.id == asset_id).first()

    def create_asset(self, req) -> object:
        """创建资产"""
        from modules.foundation.db_models.devices import Device
        from datetime import datetime

        device = Device(
            name=req.name,
            device_type=req.device_type.upper() if hasattr(req, 'device_type') else 'SERVER_LINUX',
            ip_address=req.ip_address,
            status=req.status.upper() if hasattr(req, 'status') else 'UNKNOWN',
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        return device

    def update_asset(self, asset_id: int, req) -> Optional[object]:
        """更新资产"""
        from modules.foundation.db_models.devices import Device
        from datetime import datetime

        device = self.db.query(Device).filter(Device.id == asset_id).first()
        if not device:
            return None

        update_data = req.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None and key in ['status', 'device_type']:
                value = value.upper()
            setattr(device, key, value)
        device.updated_at = datetime.now()

        self.db.commit()
        self.db.refresh(device)
        return device

    def delete_asset(self, asset_id: int) -> bool:
        """删除资产"""
        from modules.foundation.db_models.devices import Device

        device = self.db.query(Device).filter(Device.id == asset_id).first()
        if not device:
            return False
        self.db.delete(device)
        self.db.commit()
        return True
