"""AIops 服务"""
import uuid
import json
import logging
from typing import Optional, Dict, Any, List

from app.common.database import get_db_session

logger = logging.getLogger(__name__)


class AIopsService:
    """AIops 服务"""

    @staticmethod
    def analyze(source_type: str, source_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI 结构化分析
        实际调用本地 LLM（Qwen3.5），返回结构化 JSON
        """
        # TODO: 实际调用本地 LLM
        # 目前返回模拟结果
        result = {
            "analysis_id": f"ana-{uuid.uuid4().hex[:16]}",
            "summary": f"基于 {source_type} {source_id} 的分析",
            "impact": "影响范围：局部",
            "probable_causes": [
                {"cause": "磁盘空间不足", "confidence": "高"},
                {"cause": "日志文件过多", "confidence": "中"},
            ],
            "recommended_actions": [
                {"action": "清理 /var/log 目录", "risk": "低"},
                {"action": "扩展磁盘容量", "risk": "中"},
            ],
            "verification_plan": "执行 df -h 确认磁盘使用率下降",
            "confidence": "中",
        }

        # 记录分析结果
        with get_db_session() as db:
            from app.domains.aiops.models import AIAnalysisRecord
            record = AIAnalysisRecord(
                analysis_id=result["analysis_id"],
                source_type=source_type,
                source_id=source_id,
                input_context=json.dumps(context),
                output_result=json.dumps(result),
                confidence=result["confidence"],
            )
            db.add(record)
            db.commit()

        return result

    @staticmethod
    def get_analysis_history(source_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """获取分析历史"""
        with get_db_session() as db:
            from app.domains.aiops.models import AIAnalysisRecord
            query = db.query(AIAnalysisRecord)
            if source_type:
                query = query.filter(AIAnalysisRecord.source_type == source_type)
            records = query.order_by(AIAnalysisRecord.created_at.desc()).limit(limit).all()
            return [
                {
                    "id": r.id,
                    "analysis_id": r.analysis_id,
                    "source_type": r.source_type,
                    "source_id": r.source_id,
                    "confidence": r.confidence,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in records
            ]
