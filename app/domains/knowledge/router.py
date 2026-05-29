"""知识中心路由"""
from fastapi import APIRouter, Query
from typing import Optional

from app.domains.knowledge.service import KnowledgeService
from app.domains.knowledge.schemas import KnowledgeArticleCreate

router = APIRouter(prefix="/knowledge", tags=["知识中心"])


@router.post("/articles")
def create_article(article: KnowledgeArticleCreate):
    """创建知识文章"""
    article_id = KnowledgeService.create_article(article.model_dump())
    return {"code": 0, "message": "success", "data": {"article_id": article_id}}


@router.get("/articles")
def list_articles(status: Optional[str] = Query(None), limit: int = Query(100, le=200)):
    """列出知识文章"""
    articles = KnowledgeService.list_articles(status, limit)
    return {"code": 0, "message": "success", "data": articles}


@router.get("/articles/search")
def search_articles(
    keyword: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
):
    """搜索知识文章"""
    articles = KnowledgeService.search_articles(keyword, category)
    return {"code": 0, "message": "success", "data": articles}
