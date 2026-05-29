"""知识中心服务"""
import uuid
import logging
from typing import Optional, List, Dict, Any

from app.common.database import get_db_session

logger = logging.getLogger(__name__)


class KnowledgeService:
    """知识中心服务"""

    @staticmethod
    def create_article(article_data: Dict[str, Any], author: str = None) -> str:
        """创建知识文章"""
        with get_db_session() as db:
            from app.domains.knowledge.models import KnowledgeArticle
            article_id = f"kb-{uuid.uuid4().hex[:16]}"
            tags = ",".join(article_data.get("tags", [])) if article_data.get("tags") else None
            asset_types = ",".join(article_data.get("asset_types", [])) if article_data.get("asset_types") else None
            article = KnowledgeArticle(
                article_id=article_id,
                title=article_data["title"],
                content=article_data.get("content"),
                tags=tags,
                category=article_data.get("category"),
                asset_types=asset_types,
                alert_types=",".join(article_data["alert_types"]) if article_data.get("alert_types") else None,
                source_type=article_data.get("source_type"),
                source_id=article_data.get("source_id"),
                author=author,
                status="draft",
            )
            db.add(article)
            db.commit()
            return article_id

    @staticmethod
    def search_articles(
        keyword: Optional[str] = None,
        category: Optional[str] = None,
        status: str = "published",
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """搜索知识文章"""
        with get_db_session() as db:
            from app.domains.knowledge.models import KnowledgeArticle
            query = db.query(KnowledgeArticle)
            if status:
                query = query.filter(KnowledgeArticle.status == status)
            if category:
                query = query.filter(KnowledgeArticle.category == category)
            if keyword:
                query = query.filter(KnowledgeArticle.title.contains(keyword))
            records = query.order_by(KnowledgeArticle.created_at.desc()).limit(limit).all()
            return [
                {
                    "id": r.id,
                    "article_id": r.article_id,
                    "title": r.title,
                    "tags": r.tags,
                    "category": r.category,
                    "status": r.status,
                    "review_status": r.review_status,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in records
            ]

    @staticmethod
    def list_articles(status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """列出知识文章"""
        with get_db_session() as db:
            from app.domains.knowledge.models import KnowledgeArticle
            query = db.query(KnowledgeArticle)
            if status:
                query = query.filter(KnowledgeArticle.status == status)
            records = query.order_by(KnowledgeArticle.created_at.desc()).limit(limit).all()
            return [
                {
                    "id": r.id,
                    "article_id": r.article_id,
                    "title": r.title,
                    "tags": r.tags,
                    "category": r.category,
                    "status": r.status,
                    "source_type": r.source_type,
                    "review_status": r.review_status,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in records
            ]
