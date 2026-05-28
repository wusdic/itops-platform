"""
自动化领域 - API 路由
"""

from fastapi import APIRouter, Request, HTTPException
from typing import Optional
from app.common import success_response, paginated_response, get_trace_id
from app.common.database import get_db_session
from app.domains.automation.service import AutomationService
from app.domains.automation.schemas import CreateScriptRequest, UpdateScriptRequest

router = APIRouter(prefix="/api/v1/automation", tags=["自动化"])


@router.get("/scripts")
async def list_scripts(
    request: Request,
    page: int = 1,
    page_size: int = 20,
    name: Optional[str] = None,
    script_type: Optional[str] = None,
):
    with get_db_session() as db:
        svc = AutomationService(db)
        items, total = svc.list_scripts(page, page_size, name, script_type)
        return paginated_response(
            items=[{"id": i.id, "name": i.name, "script_type": i.script_type,
                    "description": i.description} for i in items],
            total=total, page=page, page_size=page_size, trace_id=get_trace_id(),
        )


@router.get("/scripts/{script_id}")
async def get_script(request: Request, script_id: int):
    with get_db_session() as db:
        svc = AutomationService(db)
        script = svc.get_script(script_id)
        if not script:
            raise HTTPException(status_code=404, detail="Script not found")
        return success_response(data={"id": script.id, "name": script.name,
                                      "script_type": script.script_type,
                                      "description": script.description}, trace_id=get_trace_id())


@router.post("/scripts")
async def create_script(request: Request):
    with get_db_session() as db:
        body = await request.json()
        req = CreateScriptRequest(**body)
        svc = AutomationService(db)
        script = svc.create_script(req)
        return success_response(data={"id": script.id, "name": script.name}, trace_id=get_trace_id())


@router.put("/scripts/{script_id}")
async def update_script(request: Request, script_id: int):
    with get_db_session() as db:
        body = await request.json()
        req = UpdateScriptRequest(**body)
        svc = AutomationService(db)
        script = svc.update_script(script_id, req)
        if not script:
            raise HTTPException(status_code=404, detail="Script not found")
        return success_response(data={"id": script.id}, trace_id=get_trace_id())


@router.delete("/scripts/{script_id}")
async def delete_script(request: Request, script_id: int):
    with get_db_session() as db:
        svc = AutomationService(db)
        ok = svc.delete_script(script_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Script not found")
        return success_response(message="Script deleted", trace_id=get_trace_id())


@router.post("/scripts/{script_id}/execute")
async def execute_script(request: Request, script_id: int):
    with get_db_session() as db:
        svc = AutomationService(db)
        body = await request.json()
        target = body.get("target")
        result = svc.execute_script(script_id, target)
        return success_response(data=result, trace_id=get_trace_id())
