"""
系统管理 API 路由
包含: 字典管理、菜单管理、系统设置、系统日志
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.dependencies import get_db, get_current_user, CurrentUser, require_role
from modules.business.dict_service import DictService
from modules.business.menu_service import MenuService
from modules.foundation.db_models.system import LogConfig, LogGroup, LogItem

router = APIRouter(tags=["系统管理"])


# ============== 系统配置（内存存储，与 admin.py 保持一致） =============

_system_config = {
    "site_name": {"value": "ITOps Platform", "description": "站点名称", "category": "basic"},
    "site_logo": {"value": "", "description": "站点Logo URL", "category": "basic"},
    "timezone": {"value": "Asia/Shanghai", "description": "系统时区", "category": "basic"},
    "date_format": {"value": "YYYY-MM-DD", "description": "日期格式", "category": "basic"},
    "page_size": {"value": "20", "description": "默认分页大小", "category": "basic"},
    "session_timeout": {"value": "3600", "description": "会话超时时间(秒)", "category": "security"},
    "password_min_length": {"value": "8", "description": "密码最小长度", "category": "security"},
    "allow_register": {"value": "false", "description": "是否允许自助注册", "category": "security"},
    "log_level": {"value": "INFO", "description": "系统日志级别", "category": "system"},
    "log_retention_days": {"value": "30", "description": "日志保留天数", "category": "system"},
    "max_login_attempts": {"value": "5", "description": "最大登录失败次数", "category": "security"},
    "lockout_duration": {"value": "300", "description": "账户锁定时长(秒)", "category": "security"},
    "smtp_host": {"value": "", "description": "SMTP服务器地址", "category": "notification"},
    "smtp_port": {"value": "587", "description": "SMTP端口", "category": "notification"},
    "smtp_from": {"value": "", "description": "发件人邮箱", "category": "notification"},
    "dingtalk_webhook": {"value": "", "description": "钉钉群机器人WebHook", "category": "notification"},
    "wecom_webhook": {"value": "", "description": "企业微信群机器人WebHook", "category": "notification"},
    "feishu_webhook": {"value": "", "description": "飞书群机器人WebHook", "category": "notification"},
    "ai_provider": {"value": "openai", "description": "AI服务提供商", "category": "ai"},
    "ai_model": {"value": "gpt-4", "description": "AI模型", "category": "ai"},
    "ai_api_key": {"value": "", "description": "AI API Key", "category": "ai"},
    "ai_base_url": {"value": "https://api.openai.com", "description": "AI API Base URL", "category": "ai"},
}


# ============== 请求/响应模型 ==============

class DictTypeCreate(BaseModel):
    """创建字典类型"""
    name: str = Field(..., description="字典名称")
    code: str = Field(..., description="字典编码")
    description: Optional[str] = Field(None, description="描述")
    status: str = Field("active", description="状态")


class DictTypeUpdate(BaseModel):
    """更新字典类型"""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class DictItemCreate(BaseModel):
    """创建字典项"""
    type_id: int = Field(..., description="字典类型ID")
    label: str = Field(..., description="标签")
    value: str = Field(..., description="值")
    sort_order: int = Field(0, description="排序")
    color: Optional[str] = Field(None, description="颜色")
    css_class: Optional[str] = Field(None, description="CSS类")
    extra_data: Optional[dict] = Field(None, description="扩展数据")
    status: str = Field("active", description="状态")


class DictItemUpdate(BaseModel):
    """更新字典项"""
    type_id: Optional[int] = None
    label: Optional[str] = None
    value: Optional[str] = None
    sort_order: Optional[int] = None
    color: Optional[str] = None
    css_class: Optional[str] = None
    extra_data: Optional[dict] = None
    status: Optional[str] = None


class MenuCreate(BaseModel):
    """创建菜单"""
    name: str = Field(..., description="菜单名称")
    code: Optional[str] = Field(None, description="菜单编码")
    icon: Optional[str] = Field(None, description="图标")
    path: Optional[str] = Field(None, description="路径")
    component: Optional[str] = Field(None, description="组件")
    redirect: Optional[str] = Field(None, description="重定向")
    parent_id: Optional[int] = Field(None, description="父菜单ID")
    sort_order: int = Field(0, description="排序")
    menu_type: str = Field("menu", description="菜单类型: menu/btn")
    visible: int = Field(1, description="是否可见: 0/1")
    is_frame: int = Field(1, description="是否外链: 0/1")
    cache: int = Field(0, description="是否缓存: 0/1")
    permission: Optional[str] = Field(None, description="权限标识")
    description: Optional[str] = Field(None, description="描述")
    status: str = Field("active", description="状态")


class MenuUpdate(BaseModel):
    """更新菜单"""
    name: Optional[str] = None
    code: Optional[str] = None
    icon: Optional[str] = None
    path: Optional[str] = None
    component: Optional[str] = None
    redirect: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    menu_type: Optional[str] = None
    visible: Optional[int] = None
    is_frame: Optional[int] = None
    cache: Optional[int] = None
    permission: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class SystemConfigUpdate(BaseModel):
    """更新系统配置"""
    value: str = Field(..., description="配置值")
    description: Optional[str] = Field(None, description="描述")


# ============== 辅助函数 ==============

def _format_dict_type(t) -> dict:
    """字典类型转字典"""
    return {
        "id": t.id,
        "name": t.name,
        "code": t.code,
        "description": t.description,
        "status": t.status,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
    }


def _format_dict_item(i) -> dict:
    """字典项转字典"""
    from json import loads
    extra = None
    if i.extra_data:
        try:
            extra = loads(i.extra_data)
        except Exception:
            extra = i.extra_data
    return {
        "id": i.id,
        "type_id": i.type_id,
        "label": i.label,
        "value": i.value,
        "sort_order": i.sort_order,
        "color": i.color,
        "css_class": i.css_class,
        "extra_data": extra,
        "status": i.status,
        "created_at": i.created_at.isoformat() if i.created_at else None,
        "updated_at": i.updated_at.isoformat() if i.updated_at else None,
    }


def _format_menu(m) -> dict:
    """菜单转字典，支持 dict 或 Menu ORM 对象"""
    if isinstance(m, dict):
        return m
    result = {
        "id": m.id,
        "name": m.name,
        "code": m.code,
        "icon": m.icon,
        "path": m.path,
        "component": m.component,
        "redirect": m.redirect,
        "parent_id": m.parent_id,
        "sort_order": m.sort_order,
        "menu_type": m.menu_type,
        "visible": m.visible,
        "is_frame": m.is_frame,
        "cache": m.cache,
        "permission": m.permission,
        "description": m.description,
        "status": m.status,
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "updated_at": m.updated_at.isoformat() if m.updated_at else None,
    }
    # Preserve children set by _build_tree
    if hasattr(m, "children"):
        result["children"] = m.children
    return result


def _frontend_menu(m) -> dict:
    """后端菜单格式转前端 key/label 格式，支持 dict 或 Menu ORM 对象"""
    if not isinstance(m, dict):
        m = _format_menu(m)
    result = {
        "key": str(m.get("id", "")),
        "label": m.get("name", ""),
        "path": m.get("path") or "",
        "iconName": m.get("icon") or None,
        "icon": m.get("icon") or None,
        "sort": m.get("sort_order", 0),
        "type": m.get("menu_type", "menu"),
        "parentKey": str(m.get("parent_id")) if m.get("parent_id") else None,
        "visible": bool(m.get("visible", 1)),
        "status": m.get("status", "active"),
        "permission": m.get("permission"),
        "component": m.get("component"),
        "description": m.get("description"),
    }
    # Include children if present (set by _build_tree on Menu objects)
    if isinstance(m, dict) and m.get("children"):
        result["children"] = [_frontend_menu(c) for c in m["children"]]
    return result


# ============== 字典管理 =============

@router.get("/dict", summary="获取字典类型列表")
async def get_dict_types(
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    status: Optional[str] = Query(None, description="状态过滤"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取字典类型分页列表"""
    service = DictService(db)
    result = service.get_types(keyword=keyword, status=status, page=page, page_size=page_size)
    return {"code": 0, "message": "success", "data": result}


@router.get("/dict/all", summary="获取所有字典类型")
async def get_all_dict_types(
    status: Optional[str] = Query(None, description="状态过滤"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取所有字典类型（不分页）"""
    service = DictService(db)
    items = service.get_all_types(status=status)
    return {"code": 0, "message": "success", "data": items}


@router.get("/dict/{dict_id}", summary="获取字典类型详情")
async def get_dict_type(
    dict_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """根据ID获取字典类型"""
    service = DictService(db)
    dict_type = service.get_type_by_id(dict_id)
    if not dict_type:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    return {"code": 0, "message": "success", "data": _format_dict_type(dict_type)}


@router.post("/dict", summary="创建字典类型")
async def create_dict_type(
    data: DictTypeCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """创建字典类型"""
    service = DictService(db)
    existing = service.get_type_by_code(data.code)
    if existing:
        raise HTTPException(status_code=400, detail="字典编码已存在")
    dict_type = service.create_type(data.model_dump())
    return {"code": 0, "message": "success", "data": _format_dict_type(dict_type)}


@router.put("/dict/{dict_id}", summary="更新字典类型")
async def update_dict_type(
    dict_id: int,
    data: DictTypeUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """更新字典类型"""
    service = DictService(db)
    dict_type = service.update_type(dict_id, data.model_dump(exclude_unset=True))
    if not dict_type:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    return {"code": 0, "message": "success", "data": _format_dict_type(dict_type)}


@router.delete("/dict/{dict_id}", summary="删除字典类型")
async def delete_dict_type(
    dict_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """删除字典类型"""
    service = DictService(db)
    ok = service.delete_type(dict_id)
    if not ok:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    return {"code": 0, "message": "success"}


# ============== 字典项管理 =============

@router.get("/dict/items", summary="获取字典项列表")
async def get_dict_items(
    type_id: Optional[int] = Query(None, description="字典类型ID"),
    type_code: Optional[str] = Query(None, description="字典类型编码"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    status: Optional[str] = Query(None, description="状态过滤"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取字典项分页列表"""
    service = DictService(db)
    result = service.get_items(
        type_id=type_id, type_code=type_code,
        keyword=keyword, status=status,
        page=page, page_size=page_size
    )
    return {"code": 0, "message": "success", "data": result}


@router.get("/dict/items/by-code/{type_code}", summary="根据类型编码获取字典项")
async def get_dict_items_by_code(
    type_code: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """根据字典类型编码获取字典项列表"""
    service = DictService(db)
    items = service.get_items_by_type_code(type_code)
    return {"code": 0, "message": "success", "data": items}


@router.get("/dict/items/{item_id}", summary="获取字典项详情")
async def get_dict_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """根据ID获取字典项"""
    service = DictService(db)
    item = service.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="字典项不存在")
    return {"code": 0, "message": "success", "data": _format_dict_item(item)}


@router.post("/dict/items", summary="创建字典项")
async def create_dict_item(
    data: DictItemCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """创建字典项"""
    service = DictService(db)
    dict_type = service.get_type_by_id(data.type_id)
    if not dict_type:
        raise HTTPException(status_code=404, detail="字典类型不存在")
    item = service.create_item(data.model_dump())
    return {"code": 0, "message": "success", "data": _format_dict_item(item)}


@router.put("/dict/items/{item_id}", summary="更新字典项")
async def update_dict_item(
    item_id: int,
    data: DictItemUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """更新字典项"""
    service = DictService(db)
    item = service.update_item(item_id, data.model_dump(exclude_unset=True))
    if not item:
        raise HTTPException(status_code=404, detail="字典项不存在")
    return {"code": 0, "message": "success", "data": _format_dict_item(item)}


@router.delete("/dict/items/{item_id}", summary="删除字典项")
async def delete_dict_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """删除字典项"""
    service = DictService(db)
    ok = service.delete_item(item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="字典项不存在")
    return {"code": 0, "message": "success"}


# ============== 菜单管理 =============

@router.get("/menu", summary="获取菜单列表")
async def get_menus(
    status: Optional[str] = Query(None, description="状态过滤"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取菜单树形列表"""
    service = MenuService(db)
    tree = service.get_tree(status=status)
    return {"code": 0, "message": "success", "data": [_format_menu(m) for m in tree]}


@router.get("/menus", summary="获取前端格式菜单树")
async def get_frontend_menus(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取前端格式（key/label）的菜单树"""
    service = MenuService(db)
    tree = service.get_tree(status="active")
    items = [_frontend_menu(m) for m in tree]
    mapped = {}
    for item in items:
        mapped[item["key"]] = {**item, "children": []}
    result = []
    for item in items:
        if item.get("parentKey") and item["parentKey"] in mapped:
            mapped[item["parentKey"]]["children"].append(item)
        elif not item.get("parentKey"):
            result.append(item)
    return {"code": 0, "message": "success", "data": result}


@router.get("/menu/{menu_id}", summary="获取菜单详情")
async def get_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """根据ID获取菜单"""
    service = MenuService(db)
    menu = service.get_by_id(menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    return {"code": 0, "message": "success", "data": _format_menu(menu)}


@router.post("/menu", summary="创建菜单")
async def create_menu(
    data: MenuCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """创建菜单"""
    service = MenuService(db)
    menu = service.create(data.model_dump())
    return {"code": 0, "message": "success", "data": _format_menu(menu)}


@router.put("/menu/{menu_id}", summary="更新菜单")
async def update_menu(
    menu_id: int,
    data: MenuUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """更新菜单"""
    service = MenuService(db)
    menu = service.update(menu_id, data.model_dump(exclude_unset=True))
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    return {"code": 0, "message": "success", "data": _format_menu(menu)}


@router.delete("/menu/{menu_id}", summary="删除菜单")
async def delete_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """删除菜单"""
    service = MenuService(db)
    try:
        ok = service.delete(menu_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not ok:
        raise HTTPException(status_code=404, detail="菜单不存在")
    return {"code": 0, "message": "success"}


# ============== 系统设置 =============

@router.get("/settings", summary="获取系统配置列表")
async def get_settings(
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    category: Optional[str] = Query(None, description="配置分类过滤"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=100, description="每页数量"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取系统配置列表"""
    items = []
    for key, cfg in _system_config.items():
        if keyword and keyword.lower() not in key.lower() and keyword.lower() not in cfg.get("description", "").lower():
            continue
        if category and cfg.get("category") != category:
            continue
        items.append({
            "key": key,
            "value": cfg["value"],
            "description": cfg.get("description"),
            "category": cfg.get("category"),
            "updated_at": datetime.now().isoformat(),
        })
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": items[start:end],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    }


@router.get("/settings/{key}", summary="获取单个系统配置")
async def get_setting(
    key: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """根据key获取系统配置"""
    if key not in _system_config:
        raise HTTPException(status_code=404, detail="配置不存在")
    cfg = _system_config[key]
    return {
        "code": 0,
        "message": "success",
        "data": {
            "key": key,
            "value": cfg["value"],
            "description": cfg.get("description"),
            "category": cfg.get("category"),
            "updated_at": datetime.now().isoformat(),
        }
    }


@router.put("/settings/{key}", summary="更新系统配置")
async def update_setting(
    key: str,
    data: SystemConfigUpdate,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    """更新系统配置"""
    if key not in _system_config:
        raise HTTPException(status_code=404, detail="配置不存在")
    _system_config[key]["value"] = data.value
    if data.description is not None:
        _system_config[key]["description"] = data.description
    return {
        "code": 0,
        "message": "success",
        "data": {
            "key": key,
            "value": _system_config[key]["value"],
            "description": _system_config[key].get("description"),
            "updated_at": datetime.now().isoformat(),
        }
    }


# ============== 系统日志 =============

@router.get("/logs", summary="获取日志归集组列表")
async def get_log_groups(
    category: Optional[str] = Query(None, description="日志分类: operation,system,collection,audit"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取日志归集组分页列表"""
    query = db.query(LogGroup)
    if category:
        query = query.filter(LogGroup.category == category)
    if start_date:
        query = query.filter(LogGroup.first_seen >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(LogGroup.last_seen <= datetime.fromisoformat(end_date + " 23:59:59"))
    if keyword:
        query = query.filter(LogGroup.group_key.ilike(f"%{keyword}%"))

    total = query.count()
    items = (
        query.order_by(LogGroup.last_seen.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    result = []
    for g in items:
        from json import loads
        dim = {}
        level_dist = {}
        try:
            dim = loads(g.dimension_summary) if g.dimension_summary else {}
        except Exception:
            pass
        try:
            level_dist = loads(g.level_distribution) if g.level_distribution else {}
        except Exception:
            pass
        result.append({
            "id": g.id,
            "category": g.category,
            "group_key": g.group_key,
            "dimension": dim,
            "first_seen": g.first_seen.isoformat() if g.first_seen else None,
            "last_seen": g.last_seen.isoformat() if g.last_seen else None,
            "total_count": g.total_count,
            "level_distribution": level_dist,
            "sample_log": g.sample_log,
        })

    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": result,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    }


@router.get("/logs/groups/{group_id}/items", summary="获取归集组内的日志明细")
async def get_log_group_items(
    group_id: int,
    level: Optional[str] = Query(None, description="日志级别过滤"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取归集组内的单条日志明细"""
    query = db.query(LogItem).filter(LogItem.group_id == group_id)
    if level:
        query = query.filter(LogItem.level == level)

    total = query.count()
    items = (
        query.order_by(LogItem.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    result = []
    for item in items:
        from json import loads
        detail = None
        if item.detail:
            try:
                detail = loads(item.detail)
            except Exception:
                detail = item.detail
        result.append({
            "id": item.id,
            "category": item.category,
            "level": item.level,
            "source": item.source,
            "message": item.message,
            "detail": detail,
            "duration_ms": item.duration_ms,
            "username": item.username,
            "ip_address": item.ip_address,
            "resource_type": item.resource_type,
            "resource_id": item.resource_id,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        })

    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": result,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    }


@router.get("/log-stats", summary="获取日志统计")
async def get_log_stats(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取各分类日志统计"""
    stats = {}
    categories = ["operation", "system", "collection", "audit"]
    for cat in categories:
        total = db.query(func.count(LogGroup.id)).filter(LogGroup.category == cat).scalar()
        groups = db.query(
            LogItem.level, func.count(LogItem.id)
        ).join(LogGroup, LogItem.group_id == LogGroup.id).filter(LogGroup.category == cat).group_by(LogItem.level).all()
        level_dist = {row[0]: row[1] for row in groups}
        stats[cat] = {
            "total_items": total or 0,
            "total_groups": len(groups) if total else 0,
            "level_distribution": level_dist,
        }
    return {"code": 0, "message": "success", "data": stats}


@router.get("/log-configs", summary="获取日志配置")
async def get_log_configs(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取日志记录配置列表"""
    configs = db.query(LogConfig).all()
    return {
        "code": 0,
        "message": "success",
        "data": [
            {
                "id": c.id,
                "category": c.category,
                "sub_category": c.sub_category,
                "enabled": bool(c.enabled),
                "min_level": c.min_level,
                "aggregation_enabled": bool(c.aggregation_enabled),
                "retention_days": c.retention_days,
                "description": c.description,
            }
            for c in configs
        ]
    }


@router.put("/log-configs", summary="批量更新日志配置")
async def update_log_configs(
    configs: List[dict],
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """批量更新日志配置"""
    for cfg in configs:
        record = db.query(LogConfig).filter(
            LogConfig.category == cfg["category"],
            LogConfig.sub_category == cfg["sub_category"]
        ).first()
        if record:
            if "enabled" in cfg:
                record.enabled = 1 if cfg["enabled"] else 0
            if "min_level" in cfg:
                record.min_level = cfg["min_level"]
            if "aggregation_enabled" in cfg:
                record.aggregation_enabled = 1 if cfg["aggregation_enabled"] else 0
            if "retention_days" in cfg:
                record.retention_days = cfg["retention_days"]
    db.commit()
    return {"code": 0, "message": "success"}


@router.post("/logs/cleanup", summary="清理过期日志")
async def cleanup_logs(
    days: int = Query(30, ge=1, description="保留天数"),
    category: Optional[str] = Query(None, description="日志分类"),
    current_user: CurrentUser = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """清理过期日志"""
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=days)
    # 删除旧的 LogItem
    item_query = db.query(LogItem).filter(LogItem.created_at < cutoff)
    if category:
        item_query = item_query.filter(LogItem.category == category)
    deleted_items = item_query.delete()

    # 删除不再有子项的 LogGroup
    group_query = db.query(LogGroup).filter(LogGroup.last_seen < cutoff)
    if category:
        group_query = group_query.filter(LogGroup.category == category)
    deleted_groups = group_query.delete()

    db.commit()
    return {
        "code": 0,
        "message": f"成功清理 {deleted_items} 条日志明细和 {deleted_groups} 个归集组",
        "data": {"deleted_items": deleted_items, "deleted_groups": deleted_groups}
    }