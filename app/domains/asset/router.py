"""
资产领域 - API 路由

统一资产管理 API，包含资产 CRUD、IP 管理、分组、标签、关系。
遵循统一响应格式 + ErrorCode + get_db_session() 规范。
文档依据: docs/01-architecture/AUTONOMOUS_ITOPS_TARGET_ARCHITECTURE.md §8.1

重要: FastAPI 按定义顺序匹配路由。固定路径(如 /groups, /tags) 必须定义在 /{id} 之前。
"""

from fastapi import APIRouter, Query, status, HTTPException
from fastapi.responses import JSONResponse

from app.common import success_response, paginated_response
from app.common.context import get_trace_id, get_user_id
from app.common.database import get_db_session

from app.domains.asset.schemas import (
    CreateAssetRequest, UpdateAssetRequest,
    CreateIPAddressRequest, CreateRelationRequest,
    CreateGroupRequest, CreateTagRequest,
    CreateBusinessSystemRequest,
)
from app.domains.asset.service import AssetService, AssetGroupService, AssetTagService, BusinessSystemService

router = APIRouter(prefix="", tags=["资产管理"])


# ============================================================
# 固定路径路由（必须在 /{id} 之前定义）
# ============================================================

# ============== 资产列表/统计/搜索 ==============

@router.get("/", summary="获取资产列表")
async def list_assets(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=200, description="每页数量"),
    name: str = Query(None, description="资产名称过滤"),
    asset_type: str = Query(None, description="资产类型过滤"),
    sub_type: str = Query(None, description="子类型过滤"),
    status: str = Query(None, description="状态过滤"),
    vendor: str = Query(None, description="厂商过滤"),
    idc: str = Query(None, description="机房过滤"),
    tag: str = Query(None, description="标签过滤"),
    group_id: int = Query(None, description="资产组ID过滤"),
    business_id: int = Query(None, description="业务系统ID过滤"),
):
    """获取资产列表，支持分页和多种过滤条件"""
    with get_db_session() as db:
        svc = AssetService(db)
        items, total = svc.list_assets(
            page=page, page_size=page_size,
            name=name, asset_type=asset_type, sub_type=sub_type,
            status=status, vendor=vendor, idc=idc,
            tag=tag, group_id=group_id, business_id=business_id,
        )
        return paginated_response(
            items=items, total=total,
            page=page, page_size=page_size,
            trace_id=get_trace_id(),
        )


@router.post("/", summary="创建资产", status_code=status.HTTP_201_CREATED)
async def create_asset(req: CreateAssetRequest):
    """创建新资产，自动生成业务ID（AST-XXXXXX）"""
    with get_db_session() as db:
        svc = AssetService(db)
        try:
            req.created_by = get_user_id()
            asset = svc.create_asset(req)
            return success_response(data=asset, trace_id=get_trace_id())
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={"success": False, "code": "BAD_REQUEST", "message": str(e), "trace_id": get_trace_id()}
            )


@router.get("/stats", summary="获取资产统计")
async def get_asset_stats():
    """获取资产统计信息"""
    with get_db_session() as db:
        svc = AssetService(db)
        stats = svc.get_stats()
        return success_response(data=stats, trace_id=get_trace_id())


@router.get("/search", summary="搜索资产")
async def search_assets(
    q: str = None, asset_type: str = None, status: str = None,
    vendor: str = None, idc: str = None, tag: str = None,
    page: int = 1, page_size: int = 20
):
    """全局搜索资产"""
    with get_db_session() as db:
        svc = AssetService(db)
        assets, total = svc.list_assets(
            page=page, page_size=page_size, name=q, asset_type=asset_type,
            status=status, vendor=vendor, idc=idc, tag=tag
        )
        return success_response(data={"items": assets, "total": total, "page": page, "page_size": page_size}, trace_id=get_trace_id())


# ============== 资产分组 ==============

@router.get("/groups/list", summary="获取资产分组列表（分页）")
async def list_groups_paginated(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    name: str = Query(None),
    parent_id: int = Query(None),
    group_type: str = Query(None),
):
    """获取资产分组列表（分页）"""
    with get_db_session() as db:
        svc = AssetGroupService(db)
        items, total = svc.list_groups(
            page=page, page_size=page_size,
            name=name, parent_id=parent_id, group_type=group_type,
        )
        return paginated_response(
            items=items, total=total,
            page=page, page_size=page_size,
            trace_id=get_trace_id(),
        )


@router.get("/groups", summary="获取所有资产分组")
async def get_groups():
    """获取所有资产分组（不分页）"""
    with get_db_session() as db:
        svc = AssetGroupService(db)
        groups = svc.list_groups()
        return success_response(data=groups, trace_id=get_trace_id())


@router.post("/groups", summary="创建资产分组", status_code=status.HTTP_201_CREATED)
async def create_group(req: CreateGroupRequest):
    """创建资产分组"""
    with get_db_session() as db:
        svc = AssetGroupService(db)
        group = svc.create_group(req)
        return success_response(data=group, trace_id=get_trace_id())


# ============== 资产标签 ==============

@router.get("/tags/list", summary="获取资产标签列表（分页）")
async def list_tags_paginated(category: str = Query(None)):
    """获取资产标签列表（分页）"""
    with get_db_session() as db:
        svc = AssetTagService(db)
        tags = svc.list_tags(category)
        return success_response(data={"items": tags, "total": len(tags)}, trace_id=get_trace_id())


@router.get("/tags", summary="获取所有资产标签")
async def get_tags(category: str = Query(None)):
    """获取所有资产标签（不分页）"""
    with get_db_session() as db:
        svc = AssetTagService(db)
        tags = svc.list_tags(category)
        return success_response(data=tags, trace_id=get_trace_id())


@router.post("/tags", summary="创建资产标签", status_code=status.HTTP_201_CREATED)
async def create_tag(req: CreateTagRequest):
    """创建资产标签"""
    with get_db_session() as db:
        svc = AssetTagService(db)
        tag = svc.create_tag(req)
        return success_response(data=tag, trace_id=get_trace_id())


# ============== 业务系统 ==============

@router.get("/business/list", summary="获取业务系统列表")
async def list_business_systems(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    name: str = Query(None),
    status: str = Query(None),
):
    """获取业务系统列表"""
    with get_db_session() as db:
        svc = BusinessSystemService(db)
        items, total = svc.list_systems(
            page=page, page_size=page_size,
            name=name, status=status,
        )
        return paginated_response(
            items=items, total=total,
            page=page, page_size=page_size,
            trace_id=get_trace_id(),
        )


@router.post("/business", summary="创建业务系统", status_code=status.HTTP_201_CREATED)
async def create_business_system(req: CreateBusinessSystemRequest):
    """创建业务系统"""
    from modules.foundation.db_models.device import BusinessSystem as LegacyBusinessSystem
    with get_db_session() as db:
        system = LegacyBusinessSystem(
            name=req.name,
            code=req.code,
            description=req.description,
            sla_level=req.sla_level,
            availability_target=req.availability_target,
            owner=req.owner,
            owner_email=req.owner_email,
            status=req.status or "active",
            tenant_id=None,
            created_by=get_user_id(),
        )
        db.add(system)
        db.commit()
        db.refresh(system)
        return success_response(data={"id": system.id, "name": system.name}, trace_id=get_trace_id())


@router.get("/business/{business_id}/devices", summary="获取业务系统下的设备")
async def get_business_devices(
    business_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """获取业务系统关联的设备"""
    with get_db_session() as db:
        svc = AssetService(db)
        assets, total = svc.list_assets(page=page, page_size=page_size, business_id=business_id)
        return paginated_response(items=assets, total=total, page=page, page_size=page_size, trace_id=get_trace_id())


# ============================================================
# 动态 ID 路由（必须在所有固定路径之后）
# ============================================================

@router.get("/{asset_id}", summary="获取资产详情")
async def get_asset(asset_id: int):
    """获取单个资产详情（包含IP列表）"""
    with get_db_session() as db:
        svc = AssetService(db)
        asset = svc.get_asset(asset_id)
        if not asset:
            return JSONResponse(
                status_code=404,
                content={"success": False, "code": "NOT_FOUND", "message": "Asset not found", "trace_id": get_trace_id()}
            )
        return success_response(data=asset, trace_id=get_trace_id())


@router.put("/{asset_id}", summary="更新资产")
async def update_asset(asset_id: int, req: UpdateAssetRequest):
    """更新资产信息"""
    with get_db_session() as db:
        svc = AssetService(db)
        asset = svc.update_asset(asset_id, req)
        if not asset:
            return JSONResponse(
                status_code=404,
                content={"success": False, "code": "NOT_FOUND", "message": "Asset not found", "trace_id": get_trace_id()}
            )
        return success_response(data=asset, trace_id=get_trace_id())


@router.delete("/{asset_id}", summary="删除资产")
async def delete_asset(asset_id: int):
    """删除资产"""
    with get_db_session() as db:
        svc = AssetService(db)
        ok = svc.delete_asset(asset_id)
        if not ok:
            return JSONResponse(
                status_code=404,
                content={"success": False, "code": "NOT_FOUND", "message": "Asset not found", "trace_id": get_trace_id()}
            )
        return success_response(data={"deleted": True}, trace_id=get_trace_id())


# ============== IP 地址管理 ==============

@router.post("/{asset_id}/ips", summary="添加资产IP", status_code=status.HTTP_201_CREATED)
async def add_asset_ip(asset_id: int, req: CreateIPAddressRequest):
    """为资产添加IP地址"""
    with get_db_session() as db:
        svc = AssetService(db)
        try:
            ip_record = svc.add_ip(asset_id, req.model_dump())
            return success_response(data=ip_record, trace_id=get_trace_id())
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))


# ============== 资产关系 ==============

@router.get("/{asset_id}/relations", summary="获取资产关系")
async def get_asset_relations(asset_id: int, relation_type: str = Query(None)):
    """获取资产的所有关联关系"""
    with get_db_session() as db:
        svc = AssetService(db)
        relations = svc.get_relations(asset_id, relation_type)
        return success_response(data=relations, trace_id=get_trace_id())


@router.post("/{asset_id}/relations", summary="添加资产关系", status_code=status.HTTP_201_CREATED)
async def add_asset_relation(asset_id: int, req: CreateRelationRequest):
    """添加资产之间的关系（网络拓扑、依赖关系等）"""
    with get_db_session() as db:
        svc = AssetService(db)
        relation = svc.add_relation(
            source_asset_id=asset_id,
            target_asset_id=req.target_asset_id,
            relation_type=req.relation_type,
            relation_label=req.relation_label,
            bidirectional=req.bidirectional,
            metadata=req.metadata,
        )
        return success_response(data=relation, trace_id=get_trace_id())


# ============== 标签绑定 ==============

@router.post("/{asset_id}/tags/{tag_id}", summary="绑定标签到资产", status_code=status.HTTP_201_CREATED)
async def bind_tag(asset_id: int, tag_id: int):
    """将标签绑定到资产"""
    with get_db_session() as db:
        svc = AssetTagService(db)
        binding = svc.bind_tag(asset_id, tag_id, created_by=get_user_id())
        return success_response(data=binding, trace_id=get_trace_id())


@router.delete("/{asset_id}/tags/{tag_id}", summary="解除资产标签绑定")
async def unbind_tag(asset_id: int, tag_id: int):
    """解除资产的标签绑定"""
    with get_db_session() as db:
        svc = AssetTagService(db)
        ok = svc.unbind_tag(asset_id, tag_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Binding not found")
        return success_response(data={"unbound": True}, trace_id=get_trace_id())


# ============== 资产配置快照 ==============

@router.get("/config/snapshot", summary="获取资产配置快照")
async def get_config_snapshot():
    """获取所有资产的最新配置快照"""
    with get_db_session() as db:
        svc = AssetService(db)
        snapshots = svc.get_config_snapshots()
        return success_response(data=snapshots, trace_id=get_trace_id())
