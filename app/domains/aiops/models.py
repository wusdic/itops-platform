"""AIops 数据模型"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func
from modules.foundation.db_models.base import Base


class AIAnalysisRecord(Base):
    """AI 分析记录"""
    __tablename__ = "ai_analysis_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(64), unique=True, nullable=False, index=True)
    source_type = Column(String(32))  # alert/event/ticket/execution
    source_id = Column(String(64))
    input_context = Column(Text)  # JSON
    output_result = Column(Text)  # JSON 结构化输出
    confidence = Column(String(8))  # 高/中/低
    user_feedback = Column(String(16))  # correct/incorrect/partially_correct
    feedback_comment = Column(Text)
    trace_id = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_ai_source", "source_type", "source_id"),
    )
