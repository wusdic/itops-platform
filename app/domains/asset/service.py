"""
资产领域 - Service 层

业务逻辑层，处理资产相关的核心业务逻辑。
复用现有的 modules.foundation.db_models Device 模型。
"""

from typing import List, Optional, Tuple
from datetime import datetime
import json

from sqlalchemy.orm import Session
from sqlalchemy import or_, func


class AssetService:
    """资产服务"""

    def __init__(self, db: Session):
        self.db = db

    def _to_device_dict(self, device) -> dict:
        """将Device模型转换为字典"""
        tags = device.tags
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',') if t.strip()]
        elif tags is None:
            tags = []

        return {
            "id": device.id,
            "name": device.name,
            "hostname": device.hostname,
            "device_type": str(device.device_type) if device.device_type else None,
            "ip_address": device.ip_address,
            "mac_address": device.mac_address,
            "status": str(device.status) if device.status else "unknown",
            "tags": tags,
            "location": device.location,
            "idc": device.idc,
            "rack": device.rack,
            "rack_position": device.rack_position,
            "vendor": device.vendor,
            "model": device.model,
            "manufacturer": device.manufacturer,
            "serial_number": device.serial_number,
            "os_type": device.os_type,
            "os_version": device.os_version,
            "cpu": device.cpu,
            "memory": device.memory,
            "disk": device.disk,
            "owner": device.owner,
            "owner_email": device.owner_email,
            "remark": device.remark,
            "monitor_enabled": device.monitor_enabled if device.monitor_enabled is not None else True,
            "snmp_enabled": device.snmp_enabled if device.snmp_enabled is not None else True,
            "ssh_port": device.ssh_port or 22,
            "business_id": device.business_id,
            "business_name": device.business_name,
            "group_id": device.group_id,
            "created_at": device.created_at.isoformat() if device.created_at else None,
            "updated_at": device.updated_at.isoformat() if device.updated_at else None,
            "created_by": device.created_by,
            "updated_by": device.updated_by,
        }

    def list_assets(
        self,
        page: int = 1,
        page_size: int = 20,
        name: Optional[str] = None,
        device_type: Optional[str] = None,
        status: Optional[str] = None,
        vendor: Optional[str] = None,
        idc: Optional[str] = None,
        tag: Optional[str] = None,
        group_id: Optional[int] = None,
        business_id: Optional[int] = None,
    ) -> Tuple[List[dict], int]:
        """获取资产列表"""
        from modules.foundation.db_models.device import Device

        query = self.db.query(Device)

        if name:
            query = query.filter(Device.name.ilike(f"%{name}%"))
        if device_type:
            query = query.filter(Device.device_type == device_type)
        if status:
            query = query.filter(Device.status == status)
        if vendor:
            query = query.filter(Device.vendor.ilike(f"%{vendor}%"))
        if idc:
            query = query.filter(Device.idc.ilike(f"%{idc}%"))
        if tag:
            query = query.filter(Device.tags.ilike(f"%{tag}%"))
        if group_id:
            query = query.filter(Device.group_id == group_id)
        if business_id:
            query = query.filter(Device.business_id == business_id)

        total = query.count()
        offset = (page - 1) * page_size
        devices = query.order_by(Device.id.desc()).offset(offset).limit(page_size).all()

        return [self._to_device_dict(d) for d in devices], total

    def get_asset(self, asset_id: int) -> Optional[dict]:
        """获取单个资产"""
        from modules.foundation.db_models.device import Device

        device = self.db.query(Device).filter(Device.id == asset_id).first()
        if not device:
            return None
        return self._to_device_dict(device)

    def get_asset_by_name(self, name: str) -> Optional[dict]:
        """通过名称获取资产"""
        from modules.foundation.db_models.device import Device

        device = self.db.query(Device).filter(
            or_(Device.name == name, Device.hostname == name)
        ).first()
        if not device:
            return None
        return self._to_device_dict(device)

    def create_asset(self, req) -> dict:
        """创建资产"""
        from modules.foundation.db_models.device import Device

        tags_str = ','.join(req.tags) if req.tags else ''

        device = Device(
            name=req.name,
            hostname=req.hostname,
            device_type=req.device_type.upper() if hasattr(req, 'device_type') and req.device_type else 'SERVER_LINUX',
            ip_address=req.ip_address,
            mac_address=req.mac_address,
            status=(req.status or 'unknown').lower(),
            tags=tags_str,
            location=req.location,
            idc=req.idc,
            rack=req.rack,
            rack_position=req.rack_position,
            vendor=req.vendor,
            model=req.model,
            manufacturer=req.manufacturer,
            serial_number=req.serial_number,
            os_type=req.os_type,
            os_version=req.os_version,
            cpu=req.cpu,
            memory=req.memory,
            disk=req.disk,
            owner=req.owner,
            owner_email=req.owner_email,
            remark=req.remark,
            monitor_enabled=req.monitor_enabled if hasattr(req, 'monitor_enabled') else True,
            snmp_enabled=req.snmp_enabled if hasattr(req, 'snmp_enabled') else True,
            snmp_community=req.snmp_community if hasattr(req, 'snmp_community') else None,
            ssh_port=req.ssh_port if hasattr(req, 'ssh_port') else 22,
            business_id=req.business_id if hasattr(req, 'business_id') else None,
            group_id=req.group_id if hasattr(req, 'group_id') else None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        return self._to_device_dict(device)

    def update_asset(self, asset_id: int, req) -> Optional[dict]:
        """更新资产"""
        from modules.foundation.db_models.device import Device

        device = self.db.query(Device).filter(Device.id == asset_id).first()
        if not device:
            return None

        update_data = req.model_dump(exclude_unset=True)

        # 处理 tags 列表转字符串
        if 'tags' in update_data and update_data['tags'] is not None:
            update_data['tags'] = ','.join(update_data['tags'])

        # 处理枚举字段大写
        for key, value in update_data.items():
            if value is not None and key in ['status', 'device_type']:
                if isinstance(value, str):
                    value = value.upper()
                setattr(device, key, value)
            elif value is not None:
                setattr(device, key, value)

        device.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(device)
        return self._to_device_dict(device)

    def delete_asset(self, asset_id: int) -> bool:
        """删除资产"""
        from modules.foundation.db_models.device import Device

        device = self.db.query(Device).filter(Device.id == asset_id).first()
        if not device:
            return False
        self.db.delete(device)
        self.db.commit()
        return True

    def update_tags(self, asset_id: int, tags: List[str]) -> Optional[dict]:
        """更新资产标签"""
        from modules.foundation.db_models.device import Device

        device = self.db.query(Device).filter(Device.id == asset_id).first()
        if not device:
            return None

        device.tags = ','.join(tags) if tags else ''
        device.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(device)
        return self._to_device_dict(device)

    def get_stats(self) -> dict:
        """获取设备统计"""
        from modules.foundation.db_models.device import Device, DeviceStatus, DeviceType

        total = self.db.query(Device).count()

        status_counts = {
            "online": self.db.query(Device).filter(Device.status == DeviceStatus.ONLINE).count(),
            "offline": self.db.query(Device).filter(Device.status == DeviceStatus.OFFLINE).count(),
            "warning": self.db.query(Device).filter(Device.status == DeviceStatus.WARNING).count(),
            "critical": self.db.query(Device).filter(Device.status == DeviceStatus.CRITICAL).count(),
            "maintenance": self.db.query(Device).filter(Device.status == DeviceStatus.MAINTENANCE).count(),
            "unknown": self.db.query(Device).filter(
                or_(Device.status == None, Device.status == DeviceStatus.UNKNOWN)
            ).count(),
        }

        by_type = {}
        for dt in DeviceType:
            count = self.db.query(Device).filter(Device.device_type == dt).count()
            if count > 0:
                by_type[dt.value] = count

        by_vendor = {}
        vendor_results = self.db.query(
            Device.vendor, func.count(Device.id)
        ).filter(Device.vendor.isnot(None)).group_by(Device.vendor).all()
        for vendor, count in vendor_results:
            by_vendor[vendor] = count

        by_idc = {}
        idc_results = self.db.query(
            Device.idc, func.count(Device.id)
        ).filter(Device.idc.isnot(None)).group_by(Device.idc).all()
        for idc_name, count in idc_results:
            by_idc[idc_name] = count

        return {
            "total": total,
            "online": status_counts["online"],
            "offline": status_counts["offline"],
            "warning": status_counts["warning"],
            "critical": status_counts["critical"],
            "maintenance": status_counts["maintenance"],
            "unknown": status_counts["unknown"],
            "by_type": by_type,
            "by_vendor": by_vendor,
            "by_idc": by_idc,
        }


# ========== 设备分组服务 ==========

class DeviceGroupService:
    """设备分组服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_groups(
        self,
        page: int = 1,
        page_size: int = 50,
        name: Optional[str] = None,
        parent_id: Optional[int] = None,
    ) -> Tuple[List[dict], int]:
        """获取分组列表"""
        from modules.foundation.db_models.device import DeviceGroup, Device

        query = self.db.query(DeviceGroup)

        if name:
            query = query.filter(DeviceGroup.name.ilike(f"%{name}%"))
        if parent_id is not None:
            query = query.filter(DeviceGroup.parent_id == parent_id)

        total = query.count()
        offset = (page - 1) * page_size
        groups = query.order_by(DeviceGroup.id).offset(offset).limit(page_size).all()

        result = []
        for g in groups:
            device_count = self.db.query(Device).filter(Device.group_id == g.id).count()
            result.append({
                "id": g.id,
                "name": g.name,
                "parent_id": g.parent_id,
                "description": g.description,
                "is_public": g.is_public,
                "device_count": device_count,
                "created_at": g.created_at.isoformat() if g.created_at else None,
                "updated_at": g.updated_at.isoformat() if g.updated_at else None,
            })

        return result, total

    def get_group(self, group_id: int) -> Optional[dict]:
        """获取分组详情"""
        from modules.foundation.db_models.device import DeviceGroup, Device

        group = self.db.query(DeviceGroup).filter(DeviceGroup.id == group_id).first()
        if not group:
            return None

        device_count = self.db.query(Device).filter(Device.group_id == group.id).count()

        return {
            "id": group.id,
            "name": group.name,
            "parent_id": group.parent_id,
            "description": group.description,
            "is_public": group.is_public,
            "device_count": device_count,
            "created_at": group.created_at.isoformat() if group.created_at else None,
            "updated_at": group.updated_at.isoformat() if group.updated_at else None,
        }

    def create_group(self, req) -> dict:
        """创建分组"""
        from modules.foundation.db_models.device import DeviceGroup

        group = DeviceGroup(
            name=req.name,
            parent_id=req.parent_id,
            description=req.description,
            is_public=req.is_public if hasattr(req, 'is_public') else True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)

        return {
            "id": group.id,
            "name": group.name,
            "parent_id": group.parent_id,
            "description": group.description,
            "is_public": group.is_public,
            "device_count": 0,
            "created_at": group.created_at.isoformat() if group.created_at else None,
            "updated_at": group.updated_at.isoformat() if group.updated_at else None,
        }

    def update_group(self, group_id: int, req) -> Optional[dict]:
        """更新分组"""
        from modules.foundation.db_models.device import DeviceGroup

        group = self.db.query(DeviceGroup).filter(DeviceGroup.id == group_id).first()
        if not group:
            return None

        update_data = req.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(group, key, value)

        group.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(group)

        from modules.foundation.db_models.device import Device
        device_count = self.db.query(Device).filter(Device.group_id == group.id).count()

        return {
            "id": group.id,
            "name": group.name,
            "parent_id": group.parent_id,
            "description": group.description,
            "is_public": group.is_public,
            "device_count": device_count,
            "created_at": group.created_at.isoformat() if group.created_at else None,
            "updated_at": group.updated_at.isoformat() if group.updated_at else None,
        }

    def delete_group(self, group_id: int) -> bool:
        """删除分组"""
        from modules.foundation.db_models.device import DeviceGroup, Device

        # 检查是否有子分组
        child_count = self.db.query(DeviceGroup).filter(DeviceGroup.parent_id == group_id).count()
        if child_count > 0:
            raise ValueError("Cannot delete group with child groups")

        # 检查是否有设备
        device_count = self.db.query(Device).filter(Device.group_id == group_id).count()
        if device_count > 0:
            raise ValueError("Cannot delete group with devices, please move or delete devices first")

        group = self.db.query(DeviceGroup).filter(DeviceGroup.id == group_id).first()
        if not group:
            return False

        self.db.delete(group)
        self.db.commit()
        return True

    def get_group_devices(self, group_id: int, page: int = 1, page_size: int = 50) -> Tuple[List[dict], int]:
        """获取分组下的设备"""
        from modules.foundation.db_models.device import Device

        query = self.db.query(Device).filter(Device.group_id == group_id)
        total = query.count()
        offset = (page - 1) * page_size
        devices = query.order_by(Device.id.desc()).offset(offset).limit(page_size).all()

        asset_svc = AssetService(self.db)
        return [asset_svc._to_device_dict(d) for d in devices], total


# ========== 业务系统服务 ==========

class BusinessSystemService:
    """业务系统服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_systems(
        self,
        page: int = 1,
        page_size: int = 50,
        name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[dict], int]:
        """获取业务系统列表"""
        from modules.foundation.db_models.device import BusinessSystem, Device

        query = self.db.query(BusinessSystem)

        if name:
            query = query.filter(BusinessSystem.name.ilike(f"%{name}%"))
        if status:
            query = query.filter(BusinessSystem.status == status)

        total = query.count()
        offset = (page - 1) * page_size
        systems = query.order_by(BusinessSystem.id).offset(offset).limit(page_size).all()

        result = []
        for s in systems:
            device_count = self.db.query(Device).filter(Device.business_id == s.id).count()
            result.append({
                "id": s.id,
                "name": s.name,
                "code": s.code,
                "description": s.description,
                "sla_level": s.sla_level,
                "availability_target": s.availability_target,
                "owner": s.owner,
                "owner_email": s.owner_email,
                "status": s.status,
                "device_count": device_count,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            })

        return result, total

    def get_system(self, system_id: int) -> Optional[dict]:
        """获取业务系统详情"""
        from modules.foundation.db_models.device import BusinessSystem, Device

        system = self.db.query(BusinessSystem).filter(BusinessSystem.id == system_id).first()
        if not system:
            return None

        device_count = self.db.query(Device).filter(Device.business_id == system.id).count()

        return {
            "id": system.id,
            "name": system.name,
            "code": system.code,
            "description": system.description,
            "sla_level": system.sla_level,
            "availability_target": system.availability_target,
            "owner": system.owner,
            "owner_email": system.owner_email,
            "status": system.status,
            "device_count": device_count,
            "created_at": system.created_at.isoformat() if system.created_at else None,
            "updated_at": system.updated_at.isoformat() if system.updated_at else None,
        }

    def create_system(self, req) -> dict:
        """创建业务系统"""
        from modules.foundation.db_models.device import BusinessSystem

        system = BusinessSystem(
            name=req.name,
            code=req.code,
            description=req.description,
            sla_level=req.sla_level,
            availability_target=req.availability_target,
            owner=req.owner,
            owner_email=req.owner_email,
            status=req.status if hasattr(req, 'status') else 'active',
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.db.add(system)
        self.db.commit()
        self.db.refresh(system)

        return {
            "id": system.id,
            "name": system.name,
            "code": system.code,
            "description": system.description,
            "sla_level": system.sla_level,
            "availability_target": system.availability_target,
            "owner": system.owner,
            "owner_email": system.owner_email,
            "status": system.status,
            "device_count": 0,
            "created_at": system.created_at.isoformat() if system.created_at else None,
            "updated_at": system.updated_at.isoformat() if system.updated_at else None,
        }

    def update_system(self, system_id: int, req) -> Optional[dict]:
        """更新业务系统"""
        from modules.foundation.db_models.device import BusinessSystem

        system = self.db.query(BusinessSystem).filter(BusinessSystem.id == system_id).first()
        if not system:
            return None

        update_data = req.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(system, key, value)

        system.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(system)

        from modules.foundation.db_models.device import Device
        device_count = self.db.query(Device).filter(Device.business_id == system.id).count()

        return {
            "id": system.id,
            "name": system.name,
            "code": system.code,
            "description": system.description,
            "sla_level": system.sla_level,
            "availability_target": system.availability_target,
            "owner": system.owner,
            "owner_email": system.owner_email,
            "status": system.status,
            "device_count": device_count,
            "created_at": system.created_at.isoformat() if system.created_at else None,
            "updated_at": system.updated_at.isoformat() if system.updated_at else None,
        }

    def delete_system(self, system_id: int) -> bool:
        """删除业务系统"""
        from modules.foundation.db_models.device import BusinessSystem

        system = self.db.query(BusinessSystem).filter(BusinessSystem.id == system_id).first()
        if not system:
            return False

        self.db.delete(system)
        self.db.commit()
        return True

    def get_system_devices(self, system_id: int, page: int = 1, page_size: int = 50) -> Tuple[List[dict], int]:
        """获取业务系统下的设备"""
        from modules.foundation.db_models.device import Device

        query = self.db.query(Device).filter(Device.business_id == system_id)
        total = query.count()
        offset = (page - 1) * page_size
        devices = query.order_by(Device.id.desc()).offset(offset).limit(page_size).all()

        asset_svc = AssetService(self.db)
        return [asset_svc._to_device_dict(d) for d in devices], total


# ========== 标签服务 ==========

class TagService:
    """标签服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_tags(self) -> List[dict]:
        """获取所有标签及计数"""
        from modules.foundation.db_models.device import Device

        # 获取所有设备的所有标签
        devices = self.db.query(Device.tags).filter(Device.tags.isnot(None)).all()

        tag_counts = {}
        for (tags_str,) in devices:
            if tags_str:
                for tag in tags_str.split(','):
                    tag = tag.strip()
                    if tag:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1

        return [
            {"name": name, "count": count}
            for name, count in sorted(tag_counts.items(), key=lambda x: -x[1])
        ]

    def get_tag_devices(self, tag: str, page: int = 1, page_size: int = 50) -> Tuple[List[dict], int]:
        """获取指定标签下的所有设备"""
        from modules.foundation.db_models.device import Device

        query = self.db.query(Device).filter(Device.tags.ilike(f"%{tag}%"))
        total = query.count()
        offset = (page - 1) * page_size
        devices = query.order_by(Device.id.desc()).offset(offset).limit(page_size).all()

        asset_svc = AssetService(self.db)
        return [asset_svc._to_device_dict(d) for d in devices], total
