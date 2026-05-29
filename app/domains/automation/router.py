"""
自动化领域 - API 路由
"""

from fastapi import APIRouter, Request, HTTPException
from typing import Optional


async def safe_json_body(req: Request) -> dict:
    """安全解析 JSON body，空 body 返回空字典"""
    try:
        body = await req.json()
        return body if isinstance(body, dict) else {}
    except Exception:
        return {}


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
    """查询脚本列表"""
    with get_db_session() as db:
        svc = AutomationService(db)
        items, total = svc.list_scripts(page=page, page_size=page_size, name=name, script_type=script_type)
        return paginated_response(items=items, total=total, page=page, page_size=page_size)


@router.post("/scripts")
async def create_script(request: Request):
    with get_db_session() as db:
        body = await safe_json_body(request)
        req = CreateScriptRequest(**body)
        svc = AutomationService(db)
        script = svc.create_script(req)
        return success_response(data={"id": str(script.id), "name": script.name}, trace_id=get_trace_id())


@router.get("/scripts/{script_id}")
async def get_script(script_id: int):
    with get_db_session() as db:
        svc = AutomationService(db)
        script = svc.get_script(script_id)
        if not script:
            raise HTTPException(status_code=404, detail="Script not found")
        return success_response(data=script, trace_id=get_trace_id())


@router.put("/scripts/{script_id}")
async def update_script(request: Request, script_id: int):
    with get_db_session() as db:
        body = await safe_json_body(request)
        req = UpdateScriptRequest(**body)
        svc = AutomationService(db)
        script = svc.update_script(script_id, req)
        return success_response(data={"id": str(script.id)}, trace_id=get_trace_id())


@router.delete("/scripts/{script_id}")
async def delete_script(script_id: int):
    with get_db_session() as db:
        svc = AutomationService(db)
        svc.delete_script(script_id)
        return success_response(data={"id": str(script_id)}, trace_id=get_trace_id())


@router.post("/scripts/{script_id}/execute")
async def execute_script(request: Request, script_id: int):
    with get_db_session() as db:
        svc = AutomationService(db)
        body = await safe_json_body(request)
        target = body.get("target")
        result = svc.execute_script(script_id, target)
        return success_response(data=result, trace_id=get_trace_id())
