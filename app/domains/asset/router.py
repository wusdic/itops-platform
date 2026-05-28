"""
资产领域 - API 路由

参考实现：展示如何在新架构下定义 API 路由。
"""

from fastapi import APIRouter, Request, Depends, HTTPException, status
from typing import Optional

from app.common import (
    success_response,
    error_response,
    paginated_response,
    get_http_status,
    ErrorCode,
    Permission,
    require_permission,
)
from app.common.context import get_trace_id

router = APIRouter(prefix="/api/v1/assets", tags=["资产管理"])


@router.get("/")
async def list_assets(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    name: Optional[str] = None,
    device_type: Optional[str] = None,
):
    """获取资产列表"""
    with get_db_session() as db:
        # 调用 service 层
        from app.domains.asset.service import AssetService
        svc = AssetService(db)
        items, total = svc.list_assets(
            page=page,
            page_size=page_size,
            name=name,
            device_type=device_type,
        )
        return paginated_response(
            items=[i.model_dump() for i in items],
            total=total,
            page=page,
            page_size=page_size,
            trace_id=get_trace_id(),
        )


@router.get("/{asset_id}")
async def get_asset(request: Request, asset_id: int):
    """获取单个资产"""
    with get_db_session() as db:
        from app.domains.asset.service import AssetService
        svc = AssetService(db)
        asset = svc.get_asset(asset_id)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found",
            )
        return success_response(data=asset.model_dump(), trace_id=get_trace_id())


@router.post("/")
async def create_asset(request: Request):
    """创建资产"""
    with get_db_session() as db:
        from app.domains.asset.service import AssetService
        from app.domains.asset.schemas import CreateAssetRequest
        body = await request.json()
        req = CreateAssetRequest(**body)
        svc = AssetService(db)
        asset = svc.create_asset(req)
        return success_response(data=asset.model_dump(), trace_id=get_trace_id())


@router.put("/{asset_id}")
async def update_asset(request: Request, asset_id: int):
    """更新资产"""
    with get_db_session() as db:
        from app.domains.asset.service import AssetService
        from app.domains.asset.schemas import UpdateAssetRequest
        body = await request.json()
        req = UpdateAssetRequest(**body)
        svc = AssetService(db)
        asset = svc.update_asset(asset_id, req)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        return success_response(data=asset.model_dump(), trace_id=get_trace_id())


@router.delete("/{asset_id}")
async def delete_asset(request: Request, asset_id: int):
    """删除资产"""
    with get_db_session() as db:
        from app.domains.asset.service import AssetService
        svc = AssetService(db)
        ok = svc.delete_asset(asset_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Asset not found")
        return success_response(message="Asset deleted", trace_id=get_trace_id())


# Import at bottom to avoid circular import
from app.common.database import get_db_session
