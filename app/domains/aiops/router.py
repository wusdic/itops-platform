"""AIops 路由"""
from fastapi import APIRouter, Query
from typing import Optional

from app.domains.aiops.service import AIopsService
from app.domains.aiops.schemas import AIAnalysisRequest

router = APIRouter(prefix="/aiops", tags=["AIops"])


@router.post("/analyze")
def analyze(request: AIAnalysisRequest):
    """AI 结构化分析"""
    result = AIopsService.analyze(request.source_type, request.source_id, request.context)
    return {"code": 0, "message": "success", "data": result}


@router.get("/analysis/history")
def get_analysis_history(
    source_type: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
):
    """获取 AI 分析历史"""
    history = AIopsService.get_analysis_history(source_type, limit)
    return {"code": 0, "message": "success", "data": history}
