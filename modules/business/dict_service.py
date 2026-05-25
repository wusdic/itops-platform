"""
字典管理服务
提供字典类型和字典项的 CRUD 操作
"""

import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from modules.foundation.db_models.dict_model import DictType, DictItem

# 默认字典数据
DEFAULT_DICTS = {
    "device_type": {
        "name": "设备类型",
        "code": "device_type",
        "items": [
            {"label": "服务器", "value": "server", "color": "#409EFF", "sort_order": 1},
            {"label": "网络设备", "value": "network", "color": "#67C23A", "sort_order": 2},
            {"label": "安全设备", "value": "security", "color": "#E6A23C", "sort_order": 3},
            {"label": "存储设备", "value": "storage", "color": "#909399", "sort_order": 4},
            {"label": "容器", "value": "container", "color": "#F56C6C", "sort_order": 5},
            {"label": "云资源", "value": "cloud", "color": "#9B59B6", "sort_order": 6},
            {"label": "其他", "value": "other", "color": "#C0C4CC", "sort_order": 99},
        ],
    },
    "alert_level": {
        "name": "告警级别",
        "code": "alert_level",
        "items": [
            {"label": "紧急", "value": "critical", "color": "#F56C6C", "sort_order": 1},
            {"label": "重要", "value": "high", "color": "#E6A23C", "sort_order": 2},
            {"label": "一般", "value": "medium", "color": "#409EFF", "sort_order": 3},
            {"label": "提示", "value": "low", "color": "#909399", "sort_order": 4},
            {"label": "信息", "value": "info", "color": "#67C23A", "sort_order": 5},
        ],
    },
    "alert_status": {
        "name": "告警状态",
        "code": "alert_status",
        "items": [
            {"label": "活跃", "value": "active", "color": "#F56C6C", "sort_order": 1},
            {"label": "已确认", "value": "acknowledged", "color": "#E6A23C", "sort_order": 2},
            {"label": "已解决", "value": "resolved", "color": "#67C23A", "sort_order": 3},
            {"label": "已关闭", "value": "closed", "color": "#909399", "sort_order": 4},
            {"label": "已抑制", "value": "suppressed", "color": "#C0C4CC", "sort_order": 5},
        ],
    },
    "workorder_status": {
        "name": "工单状态",
        "code": "workorder_status",
        "items": [
            {"label": "待处理", "value": "pending", "color": "#409EFF", "sort_order": 1},
            {"label": "处理中", "value": "processing", "color": "#E6A23C", "sort_order": 2},
            {"label": "已解决", "value": "resolved", "color": "#67C23A", "sort_order": 3},
            {"label": "已关闭", "value": "closed", "color": "#909399", "sort_order": 4},
            {"label": "已取消", "value": "cancelled", "color": "#C0C4CC", "sort_order": 5},
        ],
    },
    "workorder_priority": {
        "name": "工单优先级",
        "code": "workorder_priority",
        "items": [
            {"label": "P1 - 紧急", "value": "P1", "color": "#F56C6C", "sort_order": 1},
            {"label": "P2 - 高", "value": "P2", "color": "#E6A23C", "sort_order": 2},
            {"label": "P3 - 中", "value": "P3", "color": "#409EFF", "sort_order": 3},
            {"label": "P4 - 低", "value": "P4", "color": "#909399", "sort_order": 4},
        ],
    },
    "workorder_type": {
        "name": "工单类型",
        "code": "workorder_type",
        "items": [
            {"label": "故障", "value": "fault", "color": "#F56C6C", "sort_order": 1},
            {"label": "变更", "value": "change", "color": "#E6A23C", "sort_order": 2},
            {"label": "巡检", "value": "inspection", "color": "#67C23A", "sort_order": 3},
            {"label": "发布", "value": "release", "color": "#409EFF", "sort_order": 4},
            {"label": "其他", "value": "other", "color": "#909399", "sort_order": 99},
        ],
    },
    "vendor_type": {
        "name": "厂商类型",
        "code": "vendor_type",
        "items": [
            {"label": "服务器", "value": "server", "color": "#409EFF", "sort_order": 1},
            {"label": "网络", "value": "network", "color": "#67C23A", "sort_order": 2},
            {"label": "安全", "value": "security", "color": "#E6A23C", "sort_order": 3},
            {"label": "存储", "value": "storage", "color": "#909399", "sort_order": 4},
            {"label": "云服务", "value": "cloud", "color": "#9B59B6", "sort_order": 5},
        ],
    },
    "notification_type": {
        "name": "通知类型",
        "code": "notification_type",
        "items": [
            {"label": "邮件", "value": "email", "color": "#409EFF", "sort_order": 1},
            {"label": "短信", "value": "sms", "color": "#67C23A", "sort_order": 2},
            {"label": "钉钉", "value": "dingtalk", "color": "#1677FF", "sort_order": 3},
            {"label": "企业微信", "value": "wecom", "color": "#2EABFF", "sort_order": 4},
            {"label": "飞书", "value": "feishu", "color": "#2EABFF", "sort_order": 5},
            {"label": "Webhook", "value": "webhook", "color": "#909399", "sort_order": 6},
        ],
    },
}


class DictService:
    """字典服务类"""

    def __init__(self, db: Session):
        self.db = db

    # ============== 字典类型管理 ==============

    def get_types(
        self,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        获取字典类型分页列表

        Args:
            keyword: 关键词搜索
            status: 状态过滤
            page: 页码
            page_size: 每页数量

        Returns:
            分页结果
        """
        query = self.db.query(DictType)

        if keyword:
            query = query.filter(
                or_(
                    DictType.name.ilike(f"%{keyword}%"),
                    DictType.code.ilike(f"%{keyword}%"),
                )
            )
        if status:
            query = query.filter(DictType.status == status)

        total = query.count()
        items = (
            query.order_by(DictType.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {
            "items": [self._type_to_dict(t) for t in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_all_types(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取所有字典类型"""
        query = self.db.query(DictType)
        if status:
            query = query.filter(DictType.status == status)
        items = query.order_by(DictType.sort_order.asc(), DictType.id.asc()).all()
        return [self._type_to_dict(t) for t in items]

    def get_type_by_id(self, type_id: int) -> Optional[DictType]:
        """根据ID获取字典类型"""
        return self.db.query(DictType).filter(DictType.id == type_id).first()

    def get_type_by_code(self, code: str) -> Optional[DictType]:
        """根据代码获取字典类型"""
        return self.db.query(DictType).filter(DictType.code == code).first()

    @staticmethod
    def init_defaults(db: Session):
        """初始化默认字典数据（幂等，仅在字典类型为空时插入）"""
        existing = db.query(DictType).first()
        if existing:
            return  # 已有字典类型，跳过

        for code, type_data in DEFAULT_DICTS.items():
            dict_type = DictType(
                name=type_data["name"],
                code=type_data["code"],
                description=type_data.get("description", ""),
                status="active",
            )
            db.add(dict_type)
            db.flush()

            for item_data in type_data.get("items", []):
                dict_item = DictItem(
                    type_id=dict_type.id,
                    label=item_data["label"],
                    value=item_data["value"],
                    sort_order=item_data.get("sort_order", 0),
                    color=item_data.get("color"),
                    css_class=item_data.get("css_class"),
                    status="active",
                )
                db.add(dict_item)

        db.commit()

    def create_type(self, data: Dict[str, Any]) -> DictType:
        """
        创建字典类型

        Args:
            data: 字典类型数据

        Returns:
            创建的字典类型对象
        """
        dict_type = DictType(
            name=data["name"],
            code=data["code"],
            description=data.get("description"),
            status=data.get("status", "active"),
        )
        self.db.add(dict_type)
        self.db.commit()
        self.db.refresh(dict_type)
        return dict_type

    def update_type(self, type_id: int, data: Dict[str, Any]) -> Optional[DictType]:
        """
        更新字典类型

        Args:
            type_id: 字典类型ID
            data: 更新数据

        Returns:
            更新后的字典类型对象
        """
        dict_type = self.get_type_by_id(type_id)
        if not dict_type:
            return None

        if "name" in data:
            dict_type.name = data["name"]
        if "description" in data:
            dict_type.description = data["description"]
        if "status" in data:
            dict_type.status = data["status"]

        self.db.commit()
        self.db.refresh(dict_type)
        return dict_type

    def delete_type(self, type_id: int) -> bool:
        """
        删除字典类型

        Args:
            type_id: 字典类型ID

        Returns:
            是否删除成功
        """
        dict_type = self.get_type_by_id(type_id)
        if not dict_type:
            return False

        # 删除所有关联的字典项
        self.db.query(DictItem).filter(DictItem.type_id == type_id).delete()
        self.db.delete(dict_type)
        self.db.commit()
        return True

    # ============== 字典项管理 ==============

    def get_items(
        self,
        type_id: Optional[int] = None,
        type_code: Optional[str] = None,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        获取字典项分页列表

        Args:
            type_id: 字典类型ID
            type_code: 字典类型代码
            keyword: 关键词搜索
            status: 状态过滤
            page: 页码
            page_size: 每页数量

        Returns:
            分页结果
        """
        query = self.db.query(DictItem)

        if type_id:
            query = query.filter(DictItem.type_id == type_id)
        elif type_code:
            dict_type = self.get_type_by_code(type_code)
            if dict_type:
                query = query.filter(DictItem.type_id == dict_type.id)

        if keyword:
            query = query.filter(
                or_(
                    DictItem.label.ilike(f"%{keyword}%"),
                    DictItem.value.ilike(f"%{keyword}%"),
                )
            )
        if status:
            query = query.filter(DictItem.status == status)

        total = query.count()
        items = (
            query.order_by(DictItem.sort_order.asc(), DictItem.id.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {
            "items": [self._item_to_dict(i) for i in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_items_by_type_code(self, type_code: str) -> List[Dict[str, Any]]:
        """
        根据字典类型代码获取字典项列表

        Args:
            type_code: 字典类型代码

        Returns:
            字典项列表
        """
        dict_type = self.get_type_by_code(type_code)
        if not dict_type:
            return []

        items = (
            self.db.query(DictItem)
            .filter(DictItem.type_id == dict_type.id, DictItem.status == "active")
            .order_by(DictItem.sort_order.asc(), DictItem.id.asc())
            .all()
        )
        return [self._item_to_dict(i) for i in items]

    def get_item_by_id(self, item_id: int) -> Optional[DictItem]:
        """根据ID获取字典项"""
        return self.db.query(DictItem).filter(DictItem.id == item_id).first()

    def create_item(self, data: Dict[str, Any]) -> DictItem:
        """
        创建字典项

        Args:
            data: 字典项数据

        Returns:
            创建的字典项对象
        """
        item = DictItem(
            type_id=data["type_id"],
            label=data["label"],
            value=data["value"],
            sort_order=data.get("sort_order", 0),
            color=data.get("color"),
            css_class=data.get("css_class"),
            extra_data=json.dumps(data["extra_data"]) if data.get("extra_data") else None,
            status=data.get("status", "active"),
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_item(self, item_id: int, data: Dict[str, Any]) -> Optional[DictItem]:
        """
        更新字典项

        Args:
            item_id: 字典项ID
            data: 更新数据

        Returns:
            更新后的字典项对象
        """
        item = self.get_item_by_id(item_id)
        if not item:
            return None

        update_fields = ["type_id", "label", "value", "sort_order", "color", "css_class", "status"]
        for field in update_fields:
            if field in data:
                setattr(item, field, data[field])

        if "extra_data" in data:
            item.extra_data = json.dumps(data["extra_data"]) if data["extra_data"] else None

        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_item(self, item_id: int) -> bool:
        """
        删除字典项

        Args:
            item_id: 字典项ID

        Returns:
            是否删除成功
        """
        item = self.get_item_by_id(item_id)
        if not item:
            return False

        self.db.delete(item)
        self.db.commit()
        return True

    def _type_to_dict(self, dict_type: DictType) -> Dict[str, Any]:
        """字典类型转字典"""
        return {
            "id": dict_type.id,
            "name": dict_type.name,
            "code": dict_type.code,
            "description": dict_type.description,
            "status": dict_type.status,
            "created_at": dict_type.created_at.isoformat() if dict_type.created_at else None,
            "updated_at": dict_type.updated_at.isoformat() if dict_type.updated_at else None,
        }

    def _item_to_dict(self, item: DictItem) -> Dict[str, Any]:
        """字典项转字典"""
        extra = None
        if item.extra_data:
            try:
                extra = json.loads(item.extra_data)
            except Exception:
                extra = item.extra_data

        return {
            "id": item.id,
            "type_id": item.type_id,
            "label": item.label,
            "value": item.value,
            "sort_order": item.sort_order,
            "color": item.color,
            "css_class": item.css_class,
            "extra_data": extra,
            "status": item.status,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        }
