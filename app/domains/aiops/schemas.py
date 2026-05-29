"""AIops Schema"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class AIAnalysisRequest(BaseModel):
    source_type: str  # alert/event/ticket
    source_id: str
    context: Dict[str, Any]  # 资产+指标+日志+事件+告警+执行历史


class AIAnalysisResponse(BaseModel):
    analysis_id: str
    summary: str
    impact: str
    probable_causes: List[Dict[str, Any]]  # [{"cause": "...", "confidence": "高"}]
    recommended_actions: List[Dict[str, Any]]  # [{"action": "...", "risk": "低"}]
    verification_plan: Optional[str] = None
    confidence: str  # 高/中/低


class AIAnalysisRecordResponse(BaseModel):
    id: int
    analysis_id: str
    source_type: str
    source_id: str
    confidence: str
    created_at: datetime

    class Config:
        from_attributes = True
