"""
配置领域 - API 路由
"""

from fastapi import APIRouter, Request, HTTPException, status
from typing import Optional
from app.common import success_response, paginated_response, get_trace_id
from app.common.database import get_db_session
from app.domains.config.service import ConfigService
from app.domains.config.schemas import CreateConfigRequest, UpdateConfigRequest

router = APIRouter(prefix="/api/v1/configs", tags=["配置管理"])


@router.get("/")
async def list_configs(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    name: Optional[str] = None,
):
    with get_db_session() as db:
        svc = ConfigService(db)
        items, total = svc.list_configs(page, page_size, category, name)
        return paginated_response(
            items=[{"id": i.id, "key": i.config_key, "value": i.config_value,
                    "category": i.category, "description": i.description} for i in items],
            total=total, page=page, page_size=page_size, trace_id=get_trace_id(),
        )


@router.get("/{config_id}")
async def get_config(request: Request, config_id: int):
    with get_db_session() as db:
        svc = ConfigService(db)
        cfg = svc.get_config(config_id)
        if not cfg:
            raise HTTPException(status_code=404, detail="Config not found")
        return success_response(data={"id": cfg.id, "key": cfg.config_key,
                                      "value": cfg.config_value, "category": cfg.category,
                                      "description": cfg.description}, trace_id=get_trace_id())


@router.post("/")
async def create_config(request: Request):
    with get_db_session() as db:
        body = await request.json()
        req = CreateConfigRequest(**body)
        svc = ConfigService(db)
        cfg = svc.create_config(req)
        return success_response(data={"id": cfg.id, "key": cfg.config_key}, trace_id=get_trace_id())


@router.put("/{config_id}")
async def update_config(request: Request, config_id: int):
    with get_db_session() as db:
        body = await request.json()
        req = UpdateConfigRequest(**body)
        svc = ConfigService(db)
        cfg = svc.update_config(config_id, req)
        if not cfg:
            raise HTTPException(status_code=404, detail="Config not found")
        return success_response(data={"id": cfg.id}, trace_id=get_trace_id())


@router.delete("/{config_id}")
async def delete_config(request: Request, config_id: int):
    with get_db_session() as db:
        svc = ConfigService(db)
        ok = svc.delete_config(config_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Config not found")
        return success_response(message="Config deleted", trace_id=get_trace_id())
