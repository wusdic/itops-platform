"""
字典管理服务
提供字典类型和字典项的 CRUD 操作
"""

import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from modules.foundation.db_models.dict_model import DictType, DictItem


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
