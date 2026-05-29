"""
菜单管理服务
提供菜单的 CRUD 和树形结构查询
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from modules.foundation.db_models.menu import Menu


class MenuService:
    """菜单服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_tree(self, status: Optional[str] = None) -> List[Menu]:
        """
        获取菜单树形列表

        Args:
            status: 状态过滤 (active/inactive)

        Returns:
            树形结构的菜单列表（Menu 对象，包含 children 属性）
        """
        query = self.db.query(Menu)
        if status:
            query = query.filter(Menu.status == status)

        all_menus = query.order_by(Menu.sort_order.asc(), Menu.id.asc()).all()
        return self._build_tree(all_menus, parent_id=None)

    def _build_tree(self, menus: List[Menu], parent_id: Optional[int]) -> List[Menu]:
        """递归构建树形结构，返回 Menu 对象列表"""
        tree = []
        for menu in menus:
            if menu.parent_id == parent_id:
                children = self._build_tree(menus, menu.id)
                if children:
                    menu.children = children  # type: ignore[attr-defined]
                tree.append(menu)
        return tree

    def get_by_id(self, menu_id: int) -> Optional[Menu]:
        """根据ID获取菜单"""
        return self.db.query(Menu).filter(Menu.id == menu_id).first()

    def get_by_code(self, code: str) -> Optional[Menu]:
        """根据代码获取菜单"""
        return self.db.query(Menu).filter(Menu.code == code).first()

    def create(self, data: Dict[str, Any]) -> Menu:
        """
        创建菜单

        Args:
            data: 菜单数据，包含 name, code, path, parent_id 等字段

        Returns:
            创建的菜单对象
        """
        menu = Menu(
            name=data["name"],
            code=data.get("code"),
            icon=data.get("icon"),
            path=data.get("path"),
            component=data.get("component"),
            redirect=data.get("redirect"),
            parent_id=data.get("parent_id"),
            sort_order=data.get("sort_order", 0),
            menu_type=data.get("menu_type", "menu"),
            visible=data.get("visible", 1),
            is_frame=data.get("is_frame", 1),
            cache=data.get("cache", 0),
            permission=data.get("permission"),
            description=data.get("description"),
            status=data.get("status", "active"),
        )
        self.db.add(menu)
        self.db.commit()
        self.db.refresh(menu)
        return menu

    def update(self, menu_id: int, data: Dict[str, Any]) -> Optional[Menu]:
        """
        更新菜单

        Args:
            menu_id: 菜单ID
            data: 更新数据

        Returns:
            更新后的菜单对象，如果不存在返回None
        """
        menu = self.get_by_id(menu_id)
        if not menu:
            return None

        update_fields = [
            "name", "code", "icon", "path", "component", "redirect",
            "parent_id", "sort_order", "menu_type", "visible", "is_frame",
            "cache", "permission", "description", "status"
        ]
        for field in update_fields:
            if field in data:
                setattr(menu, field, data[field])

        self.db.commit()
        self.db.refresh(menu)
        return menu

    def delete(self, menu_id: int) -> bool:
        """
        删除菜单

        Args:
            menu_id: 菜单ID

        Returns:
            是否删除成功
        """
        menu = self.get_by_id(menu_id)
        if not menu:
            return False

        # 检查是否有子菜单
        children = self.db.query(Menu).filter(Menu.parent_id == menu_id).count()
        if children > 0:
            raise ValueError("Cannot delete menu with children")

        self.db.delete(menu)
        self.db.commit()
        return True

    def _to_dict(self, menu: Menu) -> Dict[str, Any]:
        """菜单对象转字典"""
        return {
            "id": menu.id,
            "name": menu.name,
            "code": menu.code,
            "icon": menu.icon,
            "path": menu.path,
            "component": menu.component,
            "redirect": menu.redirect,
            "parent_id": menu.parent_id,
            "sort_order": menu.sort_order,
            "menu_type": menu.menu_type,
            "visible": menu.visible,
            "is_frame": menu.is_frame,
            "cache": menu.cache,
            "permission": menu.permission,
            "description": menu.description,
            "status": menu.status,
            "created_at": menu.created_at.isoformat() if menu.created_at else None,
            "updated_at": menu.updated_at.isoformat() if menu.updated_at else None,
        }
