"""
资产领域 - API 路由

统一设备管理 API，包含设备 CRUD、分组管理、标签管理、业务系统关联。
遵循统一响应格式 + ErrorCode + get_db_session() 规范。
"""

from fastapi import APIRouter, Request, Depends, HTTPException, Query, status

from app.common import (
    success_response,
    error_response,
    paginated_response,
    get_http_status,
    ErrorCode,
)
from app.common.context import get_trace_id
from app.common.database import get_db_session

router = APIRouter(prefix="/api/v1/assets", tags=["资产管理"])


# ============== 设备接口 ==============

@router.get("/", summary="获取设备列表")
async def list_assets(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=200, description="每页数量"),
    name: str = Query(None, description="设备名称过滤"),
    device_type: str = Query(None, description="设备类型过滤"),
    status: str = Query(None, description="设备状态过滤"),
    vendor: str = Query(None, description="厂商过滤"),
    idc: str = Query(None, description="机房过滤"),
    tag: str = Query(None, description="标签过滤"),
    group_id: int = Query(None, description="设备组ID过滤"),
    business_id: int = Query(None, description="业务系统ID过滤"),
):
    """获取资产列表，支持分页和多种过滤条件"""
    with get_db_session() as db:
        from app.domains.asset.service import AssetService
        svc = AssetService(db)
        items, total = svc.list_assets(
            page=page,
            page_size=page_size,
            name=name,
            device_type=device_type,
            status=status,
            vendor=vendor,
            idc=idc,
            tag=tag,
            group_id=group_id,
            business_id=business_id,
        )
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            trace_id=get_trace_id(),
        )


@router.get("/stats", summary="获取设备统计")
async def get_asset_stats():
    """获取设备统计信息"""
    with get_db_session() as db:
        from app.domains.asset.service import AssetService
        svc = AssetService(db)
        stats = svc.get_stats()
        return success_response(data=stats, trace_id=get_trace_id())


@router.get("/{asset_id}", summary="获取设备详情")
async def get_asset(asset_id: int):
    """获取单个资产详情"""
    with get_db_session() as db:
        from app.domains.asset.service import AssetService
        svc = AssetService(db)
        asset = svc.get_asset(asset_id)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found",
            )
        return success_response(data=asset, trace_id=get_trace_id())


@router.get("/name/{name}", summary="通过名称获取设备")
async def get_asset_by_name(name: str):
    """通过名称获取资产"""
    with get_db_session() as db:
        from app.domains.asset.service import AssetService
        svc = AssetService(db)
        asset = svc.get_asset_by_name(name)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found",
            )
        return success_response(data=asset, trace_id=get_trace_id())


@router.post("/", summary="创建设备", status_code=status.HTTP_201_CREATED)
async def create_asset(request: Request):
    """创建设备"""
    with get_db_session() as db:
        from app.domains.asset.service import AssetService
        from app.domains.asset.schemas import CreateDeviceRequest
        body = await request.json()
        req = CreateDeviceRequest(**body)
        svc = AssetService(db)
        asset = svc.create_asset(req)
        return success_response(data=asset, trace_id=get_trace_id(), message="Asset created")


@router.put("/{asset_id}", summary="更新设备")
async def update_asset(asset_id: int, request: Request):
    """更新设备"""
    with get_db_session() as db:
        from app.domains.asset.service import AssetService
        from app.domains.asset.schemas import UpdateDeviceRequest
        body = await request.json()
        req = UpdateDeviceRequest(**body)
        svc = AssetService(db)
        asset = svc.update_asset(asset_id, req)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        return success_response(data=asset, trace_id=get_trace_id(), message="Asset updated")


@router.delete("/{asset_id}", summary="删除设备")
async def delete_asset(asset_id: int):
    """删除设备"""
    with get_db_session() as db:
        from app.domains.asset.service import AssetService
        svc = AssetService(db)
        ok = svc.delete_asset(asset_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Asset not found")
        return success_response(message="Asset deleted", trace_id=get_trace_id())


@router.patch("/{asset_id}/tags", summary="更新设备标签")
async def update_asset_tags(asset_id: int, request: Request):
    """更新设备标签"""
    with get_db_session() as db:
        from app.domains.asset.service import AssetService
        from app.domains.asset.schemas import TagUpdateRequest
        body = await request.json()
        req = TagUpdateRequest(**body)
        svc = AssetService(db)
        asset = svc.update_tags(asset_id, req.tags)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        return success_response(data=asset, trace_id=get_trace_id(), message="Tags updated")


# ============== 设备分组接口 ==============

@router.get("/groups/", summary="获取设备分组列表")
async def list_device_groups(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    name: str = Query(None, description="分组名称过滤"),
    parent_id: int = Query(None, description="父分组ID"),
):
    """获取设备分组列表"""
    with get_db_session() as db:
        from app.domains.asset.service import DeviceGroupService
        svc = DeviceGroupService(db)
        items, total = svc.list_groups(page=page, page_size=page_size, name=name, parent_id=parent_id)
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            trace_id=get_trace_id(),
        )


@router.get("/groups/{group_id}", summary="获取设备分组详情")
async def get_device_group(group_id: int):
    """获取设备分组详情"""
    with get_db_session() as db:
        from app.domains.asset.service import DeviceGroupService
        svc = DeviceGroupService(db)
        group = svc.get_group(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Device group not found")
        return success_response(data=group, trace_id=get_trace_id())


@router.post("/groups/", summary="创建设备分组", status_code=status.HTTP_201_CREATED)
async def create_device_group(request: Request):
    """创建设备分组"""
    with get_db_session() as db:
        from app.domains.asset.service import DeviceGroupService
        from app.domains.asset.schemas import CreateDeviceGroupRequest
        body = await request.json()
        req = CreateDeviceGroupRequest(**body)
        svc = DeviceGroupService(db)
        group = svc.create_group(req)
        return success_response(data=group, trace_id=get_trace_id(), message="Device group created")


@router.put("/groups/{group_id}", summary="更新设备分组")
async def update_device_group(group_id: int, request: Request):
    """更新设备分组"""
    with get_db_session() as db:
        from app.domains.asset.service import DeviceGroupService
        from app.domains.asset.schemas import UpdateDeviceGroupRequest
        body = await request.json()
        req = UpdateDeviceGroupRequest(**body)
        svc = DeviceGroupService(db)
        group = svc.update_group(group_id, req)
        if not group:
            raise HTTPException(status_code=404, detail="Device group not found")
        return success_response(data=group, trace_id=get_trace_id(), message="Device group updated")


@router.delete("/groups/{group_id}", summary="删除设备分组")
async def delete_device_group(group_id: int):
    """删除设备分组"""
    with get_db_session() as db:
        from app.domains.asset.service import DeviceGroupService
        svc = DeviceGroupService(db)
        try:
            ok = svc.delete_group(group_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        if not ok:
            raise HTTPException(status_code=404, detail="Device group not found")
        return success_response(message="Device group deleted", trace_id=get_trace_id())


@router.get("/groups/{group_id}/devices", summary="获取分组下的设备")
async def get_group_devices(
    group_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
):
    """获取设备分组下的所有设备"""
    with get_db_session() as db:
        from app.domains.asset.service import DeviceGroupService
        svc = DeviceGroupService(db)
        items, total = svc.get_group_devices(group_id, page=page, page_size=page_size)
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            trace_id=get_trace_id(),
        )


# ============== 业务系统接口 ==============

@router.get("/business-systems/", summary="获取业务系统列表")
async def list_business_systems(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    name: str = Query(None, description="业务系统名称过滤"),
    status: str = Query(None, description="业务系统状态过滤"),
):
    """获取业务系统列表"""
    with get_db_session() as db:
        from app.domains.asset.service import BusinessSystemService
        svc = BusinessSystemService(db)
        items, total = svc.list_systems(page=page, page_size=page_size, name=name, status=status)
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            trace_id=get_trace_id(),
        )


@router.get("/business-systems/{system_id}", summary="获取业务系统详情")
async def get_business_system(system_id: int):
    """获取业务系统详情"""
    with get_db_session() as db:
        from app.domains.asset.service import BusinessSystemService
        svc = BusinessSystemService(db)
        system = svc.get_system(system_id)
        if not system:
            raise HTTPException(status_code=404, detail="Business system not found")
        return success_response(data=system, trace_id=get_trace_id())


@router.post("/business-systems/", summary="创建业务系统", status_code=status.HTTP_201_CREATED)
async def create_business_system(request: Request):
    """创建业务系统"""
    with get_db_session() as db:
        from app.domains.asset.service import BusinessSystemService
        from app.domains.asset.schemas import CreateBusinessSystemRequest
        body = await request.json()
        req = CreateBusinessSystemRequest(**body)
        svc = BusinessSystemService(db)
        system = svc.create_system(req)
        return success_response(data=system, trace_id=get_trace_id(), message="Business system created")


@router.put("/business-systems/{system_id}", summary="更新业务系统")
async def update_business_system(system_id: int, request: Request):
    """更新业务系统"""
    with get_db_session() as db:
        from app.domains.asset.service import BusinessSystemService
        from app.domains.asset.schemas import UpdateBusinessSystemRequest
        body = await request.json()
        req = UpdateBusinessSystemRequest(**body)
        svc = BusinessSystemService(db)
        system = svc.update_system(system_id, req)
        if not system:
            raise HTTPException(status_code=404, detail="Business system not found")
        return success_response(data=system, trace_id=get_trace_id(), message="Business system updated")


@router.delete("/business-systems/{system_id}", summary="删除业务系统")
async def delete_business_system(system_id: int):
    """删除业务系统"""
    with get_db_session() as db:
        from app.domains.asset.service import BusinessSystemService
        svc = BusinessSystemService(db)
        ok = svc.delete_system(system_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Business system not found")
        return success_response(message="Business system deleted", trace_id=get_trace_id())


@router.get("/business-systems/{system_id}/devices", summary="获取业务系统下的设备")
async def get_system_devices(
    system_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
):
    """获取业务系统下的所有设备"""
    with get_db_session() as db:
        from app.domains.asset.service import BusinessSystemService
        svc = BusinessSystemService(db)
        items, total = svc.get_system_devices(system_id, page=page, page_size=page_size)
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            trace_id=get_trace_id(),
        )


# ============== 标签接口 ==============

@router.get("/tags/", summary="获取所有标签")
async def list_tags():
    """获取所有标签列表及计数"""
    with get_db_session() as db:
        from app.domains.asset.service import TagService
        svc = TagService(db)
        tags = svc.list_tags()
        return success_response(data=tags, trace_id=get_trace_id())


@router.get("/tags/{tag}/devices", summary="获取指定标签下的设备")
async def get_tag_devices(
    tag: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
):
    """获取指定标签下的所有设备"""
    with get_db_session() as db:
        from app.domains.asset.service import TagService
        svc = TagService(db)
        items, total = svc.get_tag_devices(tag, page=page, page_size=page_size)
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            trace_id=get_trace_id(),
        )


# ============== 设备关联接口 ==============

@router.patch("/{asset_id}/binding", summary="更新设备关联")
async def update_device_binding(asset_id: int, request: Request):
    """更新设备分组、业务系统、标签等关联"""
    with get_db_session() as db:
        from app.domains.asset.service import AssetService
        from app.domains.asset.schemas import DeviceBindingRequest
        body = await request.json()
        req = DeviceBindingRequest(**body)

        svc = AssetService(db)
        device = svc.get_asset(asset_id)
        if not device:
            raise HTTPException(status_code=404, detail="Asset not found")

        # 构建更新请求
        from app.domains.asset.schemas import UpdateDeviceRequest
        update_data = {}
        if req.group_id is not None:
            update_data['group_id'] = req.group_id
        if req.business_id is not None:
            update_data['business_id'] = req.business_id
        if req.tags is not None:
            update_data['tags'] = req.tags

        if update_data:
            update_req = UpdateDeviceRequest(**update_data)
            device = svc.update_asset(asset_id, update_req)

        return success_response(data=device, trace_id=get_trace_id(), message="Binding updated")
