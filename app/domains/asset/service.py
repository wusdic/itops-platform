"""
资产领域 - Service 层

业务逻辑层，处理资产相关的核心业务逻辑。
使用新的 Asset 模型（app/domains/asset/models.py）。
文档依据: docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md §8.1
"""

from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.domains.asset.models import (
    Asset, AssetIP, AssetTag, AssetTagBinding,
    AssetGroup, AssetRelation, AssetCredentialBinding,
    AssetCollectionProfile, AssetLifecycleEvent,
)


class AssetService:
    """资产服务 - 基于新资产模型"""

    def __init__(self, db: Session):
        self.db = db

    def _to_asset_dict(self, asset: Asset, include_ips: bool = False) -> dict:
        """将 Asset 模型转换为字典"""
        result = asset.to_dict()
        if include_ips:
            ips = self.db.query(AssetIP).filter(AssetIP.asset_id == asset.id).all()
            result['_ips'] = [ip.to_dict() if hasattr(ip, 'to_dict') else {
                'id': ip.id,
                'ip_address': ip.ip_address,
                'mac_address': ip.mac_address,
                'interface_name': ip.interface_name,
                'is_management': ip.is_management,
                'is_primary': ip.is_primary,
            } for ip in ips]
        return result

    def list_assets(
        self,
        page: int = 1,
        page_size: int = 20,
        name: Optional[str] = None,
        asset_type: Optional[str] = None,
        sub_type: Optional[str] = None,
        status: Optional[str] = None,
        vendor: Optional[str] = None,
        idc: Optional[str] = None,
        tag: Optional[str] = None,
        group_id: Optional[int] = None,
        business_id: Optional[int] = None,
    ) -> Tuple[List[dict], int]:
        """获取资产列表"""
        query = self.db.query(Asset)

        if name:
            query = query.filter(Asset.name.ilike(f"%{name}%"))
        if asset_type:
            query = query.filter(Asset.asset_type == asset_type)
        if sub_type:
            query = query.filter(Asset.sub_type == sub_type)
        if status:
            query = query.filter(Asset.status == status)
        if vendor:
            query = query.filter(Asset.vendor.ilike(f"%{vendor}%"))
        if idc:
            query = query.filter(Asset.idc.ilike(f"%{idc}%"))
        if group_id:
            query = query.filter(Asset.group_id == group_id)
        if business_id:
            query = query.filter(Asset.business_id == business_id)
        if tag:
            # 标签过滤：通过 tag_bindings join
            query = query.join(AssetTagBinding).join(AssetTag).filter(
                or_(
                    AssetTag.tag_key.ilike(f"%{tag}%"),
                    AssetTag.tag_value.ilike(f"%{tag}%"),
                )
            )

        total = query.count()
        offset = (page - 1) * page_size
        assets = query.order_by(Asset.id.desc()).offset(offset).limit(page_size).all()

        return [self._to_asset_dict(a) for a in assets], total

    def get_asset(self, asset_id: int) -> Optional[dict]:
        """获取单个资产（包含IP列表）"""
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            return None
        return self._to_asset_dict(asset, include_ips=True)

    def get_asset_by_asset_id(self, business_asset_id: str) -> Optional[dict]:
        """通过业务ID（如 AST-000001）获取资产"""
        asset = self.db.query(Asset).filter(Asset.asset_id == business_asset_id).first()
        if not asset:
            return None
        return self._to_asset_dict(asset, include_ips=True)

    def create_asset(self, req) -> dict:
        """创建资产（自动生成业务ID）"""
        # 生成资产业务ID
        last_asset = self.db.query(Asset).order_by(Asset.id.desc()).first()
        next_num = (last_asset.id + 1) if last_asset else 1
        asset_id_str = f"AST-{next_num:06d}"

        asset = Asset(
            asset_id=asset_id_str,
            name=req.name,
            asset_type=req.asset_type,
            sub_type=req.sub_type,
            status=req.status or 'active',
            hostname=req.hostname,
            ip_address=req.ip_address,
            mac_address=req.mac_address,
            location=req.location,
            idc=req.idc,
            building=req.building,
            floor=req.floor,
            rack=req.rack,
            rack_position=req.rack_position,
            vendor=req.vendor,
            model=req.model,
            serial_number=req.serial_number,
            manufacturer=req.manufacturer,
            purchase_date=req.purchase_date,
            warranty_end=req.warranty_end,
            os_type=req.os_type,
            os_version=req.os_version,
            cpu=req.cpu,
            memory=req.memory,
            disk=req.disk,
            ssh_port=req.ssh_port or 22,
            ssh_username=req.ssh_username,
            web_url=req.web_url,
            owner=req.owner,
            owner_email=req.owner_email,
            remark=req.remark,
            tags=req.tags,
            business_id=req.business_id,
            business_name=req.business_name,
            group_id=req.group_id,
            first_discovered_at=datetime.now(),
            last_seen_at=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=getattr(req, 'created_by', None),
        )
        self.db.add(asset)
        self.db.flush()

        # 如果提供了IP，创建主IP记录
        if req.ip_address:
            primary_ip = AssetIP(
                asset_id=asset.id,
                ip_address=req.ip_address,
                mac_address=req.mac_address,
                hostname=req.hostname,
                interface_type='physical',
                is_primary=True,
                is_management=True,
            )
            self.db.add(primary_ip)

        self.db.commit()
        self.db.refresh(asset)

        # 记录生命周期事件
        self._log_lifecycle_event(
            asset.id, "registered", "asset.registered",
            "info", f"资产 {asset.name} 登记注册", "system"
        )

        return self._to_asset_dict(asset, include_ips=True)

    def update_asset(self, asset_id: int, req) -> Optional[dict]:
        """更新资产"""
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            return None

        update_data = req.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(asset, key):
                setattr(asset, key, value)

        asset.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(asset)
        return self._to_asset_dict(asset, include_ips=True)

    def delete_asset(self, asset_id: int) -> bool:
        """删除资产"""
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            return False
        self.db.delete(asset)
        self.db.commit()
        return True

    def get_stats(self) -> dict:
        """获取资产统计"""
        total = self.db.query(Asset).count()

        status_counts = {}
        for status_val in ['active', 'inactive', 'maintenance', 'decommissioned']:
            status_counts[status_val] = self.db.query(Asset).filter(
                Asset.status == status_val
            ).count()

        by_type = {}
        type_results = self.db.query(
            Asset.asset_type, func.count(Asset.id)
        ).group_by(Asset.asset_type).all()
        for t, cnt in type_results:
            by_type[t] = cnt

        by_vendor = {}
        vendor_results = self.db.query(
            Asset.vendor, func.count(Asset.id)
        ).filter(Asset.vendor.isnot(None)).group_by(Asset.vendor).all()
        for v, cnt in vendor_results:
            by_vendor[v] = cnt

        by_idc = {}
        idc_results = self.db.query(
            Asset.idc, func.count(Asset.id)
        ).filter(Asset.idc.isnot(None)).group_by(Asset.idc).all()
        for i, cnt in idc_results:
            by_idc[i] = cnt

        return {
            "total": total,
            "active": status_counts.get('active', 0),
            "inactive": status_counts.get('inactive', 0),
            "maintenance": status_counts.get('maintenance', 0),
            "decommissioned": status_counts.get('decommissioned', 0),
            "by_type": by_type,
            "by_vendor": by_vendor,
            "by_idc": by_idc,
        }

    def add_ip(self, asset_id: int, ip_data: dict) -> dict:
        """为资产添加IP地址"""
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        ip_record = AssetIP(
            asset_id=asset_id,
            ip_address=ip_data['ip_address'],
            ip_type=ip_data.get('ip_type', 'ipv4'),
            mac_address=ip_data.get('mac_address'),
            hostname=ip_data.get('hostname'),
            interface_name=ip_data.get('interface_name'),
            interface_type=ip_data.get('interface_type', 'physical'),
            is_management=ip_data.get('is_management', False),
            is_primary=ip_data.get('is_primary', False),
            is_public=ip_data.get('is_public', False),
            vlan_id=ip_data.get('vlan_id'),
            subnet_mask=ip_data.get('subnet_mask'),
            gateway=ip_data.get('gateway'),
        )
        self.db.add(ip_record)
        self.db.commit()
        self.db.refresh(ip_record)
        return ip_record.to_dict() if hasattr(ip_record, 'to_dict') else {
            'id': ip_record.id, 'ip_address': ip_record.ip_address
        }

    def get_relations(self, asset_id: int, relation_type: Optional[str] = None) -> List[dict]:
        """获取资产关系"""
        query = self.db.query(AssetRelation).filter(
            or_(
                AssetRelation.source_asset_id == asset_id,
                AssetRelation.target_asset_id == asset_id,
            )
        )
        if relation_type:
            query = query.filter(AssetRelation.relation_type == relation_type)

        relations = query.all()
        result = []
        for r in relations:
            source = self.db.query(Asset).filter(Asset.id == r.source_asset_id).first()
            target = self.db.query(Asset).filter(Asset.id == r.target_asset_id).first()
            result.append({
                'id': r.id,
                'source_asset_id': r.source_asset_id,
                'source_asset_name': source.name if source else None,
                'target_asset_id': r.target_asset_id,
                'target_asset_name': target.name if target else None,
                'relation_type': r.relation_type,
                'relation_label': r.relation_label,
                'bidirectional': r.bidirectional,
                'metadata': r.extra_data,
                'created_at': r.created_at.isoformat() if r.created_at else None,
            })
        return result

    def add_relation(self, source_asset_id: int, target_asset_id: int,
                     relation_type: str, relation_label: str = None,
                     bidirectional: bool = False, metadata: dict = None) -> dict:
        """添加资产关系"""
        relation = AssetRelation(
            source_asset_id=source_asset_id,
            target_asset_id=target_asset_id,
            relation_type=relation_type,
            relation_label=relation_label,
            bidirectional=bidirectional,
            extra_data=metadata,
            created_at=datetime.now(),
        )
        self.db.add(relation)
        self.db.commit()
        self.db.refresh(relation)

        # 如果是双向关系，同时创建反向
        if bidirectional:
            reverse = AssetRelation(
                source_asset_id=target_asset_id,
                target_asset_id=source_asset_id,
                relation_type=relation_type,
                relation_label=relation_label,
                bidirectional=True,
                extra_data=metadata,
                created_at=datetime.now(),
            )
            self.db.add(reverse)
            self.db.commit()

        return {
            'id': relation.id,
            'source_asset_id': relation.source_asset_id,
            'target_asset_id': relation.target_asset_id,
            'relation_type': relation.relation_type,
        }

    def _log_lifecycle_event(
        self, asset_id: int, event_type: str, event_subtype: str,
        severity: str, description: str, actor: str,
        metadata: dict = None, trace_id: str = None
    ):
        """记录资产生命周期事件"""
        from app.common.context import get_trace_id
        event = AssetLifecycleEvent(
            asset_id=asset_id,
            event_type=event_type,
            event_subtype=event_subtype,
            severity=severity,
            description=description,
            actor=actor,
            actor_name=actor,
            extra_data=metadata,
            occurred_at=datetime.now(),
            trace_id=trace_id or get_trace_id(),
        )
        self.db.add(event)
        self.db.commit()


class AssetGroupService:
    """资产分组服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_groups(
        self,
        page: int = 1,
        page_size: int = 50,
        name: Optional[str] = None,
        parent_id: Optional[int] = None,
        group_type: Optional[str] = None,
    ) -> Tuple[List[dict], int]:
        """获取分组列表"""
        query = self.db.query(AssetGroup)

        if name:
            query = query.filter(AssetGroup.group_name.ilike(f"%{name}%"))
        if parent_id is not None:
            query = query.filter(AssetGroup.parent_id == parent_id)
        if group_type:
            query = query.filter(AssetGroup.group_type == group_type)

        total = query.count()
        offset = (page - 1) * page_size
        groups = query.order_by(AssetGroup.display_order, AssetGroup.id).offset(offset).limit(page_size).all()

        result = []
        for g in groups:
            asset_count = self.db.query(Asset).filter(Asset.group_id == g.id).count()
            result.append({
                "id": g.id,
                "group_code": g.group_code,
                "group_name": g.group_name,
                "parent_id": g.parent_id,
                "group_type": g.group_type,
                "description": g.description,
                "is_public": g.is_public,
                "display_order": g.display_order,
                "asset_count": asset_count,
                "created_at": g.created_at.isoformat() if g.created_at else None,
                "updated_at": g.updated_at.isoformat() if g.updated_at else None,
            })

        return result, total

    def create_group(self, req) -> dict:
        """创建分组"""
        # 生成 group_code
        last = self.db.query(AssetGroup).order_by(AssetGroup.id.desc()).first()
        next_num = (last.id + 1) if last else 1
        group_code = f"GRP-{next_num:04d}"

        group = AssetGroup(
            group_code=group_code,
            group_name=req.group_name,
            parent_id=req.parent_id,
            group_type=req.group_type,
            description=req.description,
            display_order=req.display_order or 0,
            is_public=req.is_public if hasattr(req, 'is_public') else True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=getattr(req, 'created_by', None),
        )
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)

        return {
            "id": group.id,
            "group_code": group.group_code,
            "group_name": group.group_name,
            "parent_id": group.parent_id,
            "group_type": group.group_type,
            "description": group.description,
            "is_public": group.is_public,
            "display_order": group.display_order,
            "asset_count": 0,
            "created_at": group.created_at.isoformat() if group.created_at else None,
        }


class AssetTagService:
    """资产标签服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_tags(self, category: Optional[str] = None) -> List[dict]:
        """获取所有标签（含使用计数）"""
        query = self.db.query(AssetTag)
        if category:
            query = query.filter(AssetTag.tag_category == category)

        tags = query.all()
        result = []
        for t in tags:
            count = self.db.query(AssetTagBinding).filter(
                AssetTagBinding.tag_id == t.id
            ).count()
            result.append({
                'id': t.id,
                'tag_key': t.tag_key,
                'tag_value': t.tag_value,
                'tag_color': t.tag_color,
                'tag_category': t.tag_category,
                'description': t.description,
                'asset_count': count,
            })
        return result

    def create_tag(self, req) -> dict:
        """创建标签"""
        tag = AssetTag(
            tag_key=req.tag_key,
            tag_value=req.tag_value,
            tag_color=req.tag_color or '#1890ff',
            tag_category=req.tag_category,
            description=req.description,
            created_at=datetime.now(),
        )
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return {
            'id': tag.id,
            'tag_key': tag.tag_key,
            'tag_value': tag.tag_value,
            'tag_color': tag.tag_color,
            'tag_category': tag.tag_category,
            'description': tag.description,
            'asset_count': 0,
        }

    def bind_tag(self, asset_id: int, tag_id: int, created_by: str = None) -> dict:
        """绑定标签到资产"""
        # 检查是否已绑定
        existing = self.db.query(AssetTagBinding).filter(
            AssetTagBinding.asset_id == asset_id,
            AssetTagBinding.tag_id == tag_id,
        ).first()
        if existing:
            return {'id': existing.id, 'asset_id': existing.asset_id, 'tag_id': existing.tag_id}

        binding = AssetTagBinding(
            asset_id=asset_id,
            tag_id=tag_id,
            created_at=datetime.now(),
            created_by=created_by,
        )
        self.db.add(binding)
        self.db.commit()
        self.db.refresh(binding)
        return {'id': binding.id, 'asset_id': binding.asset_id, 'tag_id': binding.tag_id}

    def unbind_tag(self, asset_id: int, tag_id: int) -> bool:
        """解除资产标签绑定"""
        binding = self.db.query(AssetTagBinding).filter(
            AssetTagBinding.asset_id == asset_id,
            AssetTagBinding.tag_id == tag_id,
        ).first()
        if not binding:
            return False
        self.db.delete(binding)
        self.db.commit()
        return True


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
        from modules.foundation.db_models.device import BusinessSystem as LegacyBusinessSystem

        query = self.db.query(LegacyBusinessSystem)

        if name:
            query = query.filter(LegacyBusinessSystem.name.ilike(f"%{name}%"))
        if status:
            query = query.filter(LegacyBusinessSystem.status == status)

        total = query.count()
        offset = (page - 1) * page_size
        systems = query.order_by(LegacyBusinessSystem.id).offset(offset).limit(page_size).all()

        result = []
        for s in systems:
            device_count = self.db.query(Asset).filter(Asset.business_id == s.id).count()
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
            })

        return result, total
