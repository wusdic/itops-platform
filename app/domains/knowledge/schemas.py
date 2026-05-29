"""知识中心 Schema"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class KnowledgeArticleCreate(BaseModel):
    title: str
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    asset_types: Optional[List[str]] = None
    alert_types: Optional[List[str]] = None
    source_type: Optional[str] = None
    source_id: Optional[str] = None


class KnowledgeArticleResponse(BaseModel):
    id: int
    article_id: str
    title: str
    tags: Optional[str] = None
    category: Optional[str] = None
    status: str
    source_type: Optional[str] = None
    review_status: str
    created_at: datetime

    class Config:
        from_attributes = True
