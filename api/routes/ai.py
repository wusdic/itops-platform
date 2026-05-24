"""
AI Assistant API Router
Provides intelligent Q&A, fault diagnosis, and suggestion generation
"""

from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
import json
import logging

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.dependencies import get_db, get_current_user, CurrentUser, PaginationParams
from modules.business.knowledge_base.models import (
    SOPDocument, FaultCase, Category, Tag,
    DocumentStatus, FaultLevel, FaultStatus, ReviewStatus
)
from modules.collection.device_manager import DeviceManager


router = APIRouter()
logger = logging.getLogger(__name__)


# ============== Message persistence helper functions ==============

def _save_chat_messages(
    db: Session,
    current_user: CurrentUser,
    conversation_id: str,
    user_message: str,
    assistant_message: str,
    model: Optional[str],
    suggestions: Optional[List[str]],
    mode: str,
    error_message: Optional[str] = None,
):
    """
    Save dialog messages to database (user messages and AI responses)
    Create session if not exists
    """
    from modules.foundation.db_models.ai import AIConversation, AIMessage
    
    # Find or create session
    conversation = db.query(AIConversation).filter(
        AIConversation.conversation_id == conversation_id
    ).first()
    
    if not conversation:
        # Create new session
        conversation = AIConversation(
            conversation_id=conversation_id,
            user_id=current_user.user_id,
            username=current_user.username,
            conversation_type="chat",
            message_count=0,
        )
        db.add(conversation)
    
    now = datetime.now()
    
    # Save user message
    user_msg = AIMessage(
        conversation_id=conversation_id,
        user_id=current_user.user_id,
        role="user",
        content=user_message,
        created_at=now,
    )
    db.add(user_msg)
    
    # Save AI reply
    assistant_msg = AIMessage(
        conversation_id=conversation_id,
        user_id=current_user.user_id,
        role="assistant",
        content=assistant_message,
        model=model,
        suggestions=json.dumps(suggestions) if suggestions else None,
        error_message=error_message,
        created_at=now,
    )
    db.add(assistant_msg)
    
    # Update session stats
    conversation.message_count = (conversation.message_count or 0) + 2
    conversation.last_message_at = now
    conversation.updated_at = now
    
    # Set title if first user message
    if conversation.message_count <= 2 and user_message:
        conversation.title = user_message[:50] + ("..." if len(user_message) > 50 else "")
    
    db.commit()


# ============== Platform context fetch ==============

async def _fetch_platform_context(db: Session) -> str:
    """
    Get ITOps platform real-time context for LLM system prompt.
    Uses raw SQL to avoid broken module import chains.
    """
    try:
        from sqlalchemy import text

        # Device stats
        stats_row = db.execute(text(""" 
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'ONLINE' THEN 1 ELSE 0 END) as online_count,
                SUM(CASE WHEN status = 'OFFLINE' THEN 1 ELSE 0 END) as offline_count,
                SUM(CASE WHEN status = 'MAINTENANCE' THEN 1 ELSE 0 END) as maint_count
            FROM devices
        """)).fetchone()
        total_devices = stats_row.total if stats_row and stats_row.total else 0
        online_count = stats_row.online_count if stats_row and stats_row.online_count else 0
        offline_count = stats_row.offline_count if stats_row and stats_row.offline_count else 0
        maint_count = stats_row.maint_count if stats_row and stats_row.maint_count else 0

        # Active alerts
        alert_row = db.execute(text("SELECT COUNT(*) FROM alerts WHERE status = 'active'")).scalar()
        active_alerts = alert_row or 0

        ctx = (
            f"Platform data: {total_devices} devices total, "
            f"{online_count} online, {offline_count} offline, {maint_count} maintenance. "
            f"{active_alerts} active alerts. "
            f"You are an IT operations assistant. Answer in Chinese. "
            f"For questions about platform devices, alerts, and monitoring, "
            f"answer directly based on the data above. Do not say you cannot provide information."
        )
        return ctx
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.warning(f"Failed to fetch platform context: {e}")
        return "You are an IT operations assistant. Answer in Chinese."


# ============== Module-level streaming generator ==============

async def _llm_stream_generator(
    base_url: str,
    model: str,
    messages: List[dict],
    conversation_id: str,
    timeout: float = 300.0,
):
    """
    Module-level streaming response generator.
    Used for LLM CPU inference at approximately 4 tokens per second.
    """
    import httpx
    import asyncio

    payload = {
        "messages": messages,
        "model": model,
        "stream": True,
        "temperature": 0.0,
        "max_tokens": 100,
    }

    full_content = ""
    try:
        # connect=10s (jointimeout), read=300s (streaming读timeout足够大), default=300s兜底
        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0)) as client:
            async with client.stream("POST", f"{base_url}/v1/chat/completions", json=payload) as resp:
                buffer = ""
                depth = 0
                in_string = False
                escape = False
                async for raw in resp.aiter_text():
                    for ch in raw:
                        buffer += ch
                        if escape:
                            escape = False
                            continue
                        if ch == "\\" and in_string:
                            escape = True
                            continue
                        if ch == '"':
                            in_string = not in_string
                        if not in_string:
                            if ch == "{":
                                depth += 1
                            elif ch == "}":
                                depth -= 1
                                if depth == 0 and buffer.lstrip().startswith("data: "):
                                    json_str = buffer.lstrip()[6:]
                                    buffer = ""
                                    try:
                                        data = json.loads(json_str)
                                        # llama.cpp / Qwen format: choices[0].delta.content
                                        if "choices" in data and len(data["choices"]) > 0:
                                            delta = data["choices"][0].get("delta", {})
                                            content = delta.get("content", "")
                                            if content:
                                                full_content += content
                                                yield f"data: {json.dumps({'type': 'content', 'content': content}, ensure_ascii=False)}\n\n"
                                        # Legacy format compatibility: message.content
                                        elif "message" in data:
                                            content = data["message"].get("content", "")
                                            if content:
                                                full_content += content
                                                yield f"data: {json.dumps({'type': 'content', 'content': content}, ensure_ascii=False)}\n\n"
                                        if data.get("done", False) or data.get("choices", [{}])[0].get("finish_reason"):
                                            # Exit both loops: return from generator
                                            return
                                    except json.JSONDecodeError:
                                        pass
        # Stream completed normally (llama.cpp sends done, we exit via return above)
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Stream error: {e}")
        yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"


# ============== Enum definitions ==============

class ConversationType(str, Enum):
    """Dialog type"""
    CHAT = "chat"
    TROUBLESHOOTING = "troubleshooting"
    SUGGESTION = "suggestion"
    ANALYSIS = "analysis"


class MessageRole(str, Enum):
    """Message role"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# ============== Request/Response models ==============

class ChatMessage(BaseModel):
    """Chat message"""
    role: str = Field(..., description="角色: user, assistant, system")
    content: str = Field(..., description="message内容")
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Chat request"""
    message: str = Field(..., description="usermessage")
    conversation_id: Optional[str] = Field(None, description="sessionID")
    conversation_type: str = Field("chat", description="Dialog type")
    context: Optional[dict] = Field(None, description="contextinformation")
    stream: bool = Field(False, description="是否启用streaming输出")


class ChatResponse(BaseModel):
    """Chat response"""
    conversation_id: str
    message: str
    suggestions: Optional[List[str]] = None
    related_docs: Optional[List[dict]] = None
    metadata: Optional[dict] = None


class TroubleshootingRequest(BaseModel):
    """Troubleshooting request"""
    symptom: str = Field(..., description="fault现象")
    device_id: Optional[int] = Field(None, description="deviceID")
    device_name: Optional[str] = Field(None, description="device名称")
    device_ip: Optional[str] = Field(None, description="deviceIP")
    error_logs: Optional[str] = Field(None, description="errorlog")
    metrics: Optional[dict] = Field(None, description="相关metric")


class TroubleshootingResponse(BaseModel):
    """fault排查response"""
    diagnosis: str = Field(..., description="诊断结果")
    confidence: float = Field(..., description="置信度 0-1")
    possible_causes: List[str] = Field(..., description="可能原因")
    suggested_steps: List[dict] = Field(..., description="建议step")
    related_cases: Optional[List[dict]] = Field(None, description="相关案例")
    related_docs: Optional[List[dict]] = Field(None, description="相关文档")


class SuggestionRequest(BaseModel):
    """建议生成request"""
    type: str = Field(..., description="建议class型: performance, security, capacity, optimization")
    target: str = Field(..., description="目标: host, service, system")
    target_id: Optional[int] = Field(None, description="目标ID")
    metrics: Optional[dict] = Field(None, description="currentmetricdata")


# ============== fault案例query ==============

def _find_related_cases(symptom: str, keyword: str = None, limit: int = 5) -> List[dict]:
    """Find related fault cases from database"""
    from api.dependencies import get_db
    
    # 这个function需要db session,We return a query builder approach
    # 实际调用h传入db
    return []


# ============== 对话接口 ==============

@router.post("/chat/_debug", summary="debugstreaming接口")
async def chat_debug(
    request: ChatRequest,
):
    """Minimal streaming test endpoint without dependencies"""
    import httpx
    import json

    async def stream_generator():
        payload = {
            "messages": [{"role": "user", "content": request.message}],
            "model": "qwen3.5-9b-deepseek-v4-flash-q8_0",
            "stream": True,
            "temperature": 0.0,
            "max_tokens": 100,
        }
        base_url = os.getenv("AI_BASE_URL", "http://localhost:11435")
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0)) as client:
                async with client.stream("POST", f"{base_url}/v1/chat/completions", json=payload) as resp:
                    async for line in resp.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                # llama.cpp / Qwen format: choices[0].delta.content
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                                    if data["choices"][0].get("finish_reason"):
                                        break
                                elif "message" in data:
                                    content = data.get("message", {}).get("content", "")
                                    if content:
                                        yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                                if data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/chat", summary="发送message")
async def chat(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    发送message给AI助手
    """
    conversation_id = request.conversation_id or f"conv-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # 尝试get全局 LLM client
    from api.start import get_llm_client
    llm_client = get_llm_client()

    if llm_client is None:
        # LLM 未initialize,degradation到意graph检测
        suggestions = ["进行fault排查", "生成优化建议", "searchknowledge_base", "analysislog"]
        response_message = "AIservice暂不可用,请检查LLMservice是否start."
        
        # Save user and AI messages (fallback mode)
        _save_chat_messages(
            db=db,
            current_user=current_user,
            conversation_id=conversation_id,
            user_message=request.message,
            assistant_message=response_message,
            model=None,
            suggestions=suggestions,
            mode="llm_unavailable"
        )
        
        return {
            "conversation_id": conversation_id,
            "message": response_message,
            "suggestions": suggestions,
            "metadata": {
                "mode": "llm_unavailable",
                "timestamp": datetime.now().isoformat()
            },
        }

    # Get platform real-time context,注入 system prompt
    platform_context = await _fetch_platform_context(db)

    messages = [
        {"role": "system", "content": platform_context},
        {"role": "user", "content": request.message},
    ]

    if request.stream:
        # Streaming response: use module-level generator (avoid Python 3.13 nested async def closure bug)
        base_url = os.getenv("AI_BASE_URL", llm_client.base_url or "http://localhost:11435")
        model = llm_client._default_model or "qwen3.5-9b-deepseek-v4-flash-q8_0"
        return StreamingResponse(
            _llm_stream_generator(base_url, model, messages, conversation_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Conversation-ID": conversation_id,
            }
        )

    # 非streamingresponse
    # Qwen 0.8B 模型太小，temperature=0.7 容易产生幻觉（编造数字）
    # temperature=0.0 保证确定性输出，max_tokens=100 防止模型生成时"走神"
    result = await llm_client.chat(
        messages=messages,
        model=None,
        temperature=0.0,
        max_tokens=100,
    )

    if result.get("done") and result.get("content"):
        response_message = result["content"]
        model_name = result.get("model", "qwen3.5-9b-deepseek-v4-flash-q8_0")
        suggestions = ["resume对话", "进入fault排查", "生成优化建议"]
        
        # Save user message和ai_reply
        _save_chat_messages(
            db=db,
            current_user=current_user,
            conversation_id=conversation_id,
            user_message=request.message,
            assistant_message=response_message,
            model=model_name,
            suggestions=suggestions,
            mode="llm"
        )
        
        return {
            "conversation_id": conversation_id,
            "message": response_message,
            "suggestions": suggestions,
            "metadata": {
                "mode": "llm",
                "model": model_name,
                "eval_count": result.get("eval_count", 0),
                "timestamp": datetime.now().isoformat()
            },
        }
    else:
        error_message = "ai_reply生成failed,请retry."
        suggestions = ["retry", "进入fault排查", "生成优化建议"]
        
        # saveerrorinformation
        _save_chat_messages(
            db=db,
            current_user=current_user,
            conversation_id=conversation_id,
            user_message=request.message,
            assistant_message=error_message,
            model=None,
            suggestions=suggestions,
            mode="llm_error",
            error_message=error_message
        )
        
        return {
            "conversation_id": conversation_id,
            "message": error_message,
            "suggestions": suggestions,
            "metadata": {"mode": "llm_error", "timestamp": datetime.now().isoformat()},
        }


@router.get("/conversations/{conversation_id}", summary="Get conversation history")
async def get_conversation(
    conversation_id: str,
    limit: int = Query(50, le=100, description="返回message数量"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get messages for a specific conversation
    """
    from modules.foundation.db_models.ai import AIConversation, AIMessage

    # findsession
    conversation = db.query(AIConversation).filter(
        AIConversation.conversation_id == conversation_id,
        AIConversation.is_deleted == False
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="session不存在")

    # getmessagelist
    messages = db.query(AIMessage).filter(
        AIMessage.conversation_id == conversation_id
    ).order_by(AIMessage.created_at.asc()).limit(limit).all()

    return {
        "conversation_id": conversation_id,
        "title": conversation.title,
        "conversation_type": conversation.conversation_type,
        "message_count": len(messages),
        "messages": [msg.to_dict() for msg in messages],
        "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
        "last_message_at": conversation.last_message_at.isoformat() if conversation.last_message_at else None,
    }


@router.get("/conversations", summary="Get conversation list")
async def get_conversations(
    conversation_type: Optional[str] = Query(None, description="Dialog typefilter"),
    is_pinned: Optional[bool] = Query(None, description="置顶statefilter"),
    keyword: Optional[str] = Query(None, description="关键词search"),
    limit: int = Query(20, le=50, description="返回数量限制"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """getuser的sessionlist"""
    from modules.foundation.db_models.ai import AIConversation

    query = db.query(AIConversation).filter(
        AIConversation.user_id == current_user.user_id,
        AIConversation.is_deleted == False
    )

    if conversation_type:
        query = query.filter(AIConversation.conversation_type == conversation_type)

    if is_pinned is not None:
        query = query.filter(AIConversation.is_pinned == is_pinned)

    if keyword:
        query = query.filter(
            (AIConversation.title.ilike(f"%{keyword}%")) |
            (AIConversation.summary.ilike(f"%{keyword}%"))
        )

    total = query.count()
    conversations = query.order_by(AIConversation.is_pinned.desc(), AIConversation.last_message_at.desc()).limit(limit).all()

    return {
        "items": [
            {
                "conversation_id": conv.conversation_id,
                "title": conv.title,
                "summary": conv.summary,
                "conversation_type": conv.conversation_type,
                "message_count": conv.message_count,
                "is_pinned": conv.is_pinned,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
            }
            for conv in conversations
        ],
        "total": total,
    }


@router.delete("/conversations/{conversation_id}", summary="Delete conversation")
async def delete_conversation(
    conversation_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete specified conversation (soft delete)"""
    from modules.foundation.db_models.ai import AIConversation, AIMessage

    conversation = db.query(AIConversation).filter(
        AIConversation.conversation_id == conversation_id,
        AIConversation.is_deleted == False
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="session不存在")

    # 软Delete conversation
    conversation.is_deleted = True
    conversation.updated_at = datetime.now()

    db.commit()

    return {
        "status": "success",
        "message": "Conversation deleted"
    }


@router.put("/conversations/{conversation_id}/pin", summary="置顶/cancel置顶session")
async def pin_conversation(
    conversation_id: str,
    is_pinned: bool = Query(..., description="是否置顶"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """置顶或cancel置顶session"""
    from modules.foundation.db_models.ai import AIConversation

    conversation = db.query(AIConversation).filter(
        AIConversation.conversation_id == conversation_id,
        AIConversation.is_deleted == False
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="session不存在")

    conversation.is_pinned = is_pinned
    conversation.updated_at = datetime.now()

    db.commit()

    return {
        "status": "success",
        "message": f"session已{'置顶' if is_pinned else 'cancel置顶'}"
    }


@router.post("/conversations/{conversation_id}/messages", summary="savemessage到session")
async def save_message_to_conversation(
    conversation_id: str,
    role: str = Query(..., description="Message role: user, assistant, system"),
    content: str = Query(..., description="message内容"),
    model: Optional[str] = Query(None, description="使用的模型"),
    suggestions: Optional[List[str]] = Query(None, description="建议list"),
    references: Optional[str] = Query(None, description="参考资料(JSON)"),
    token_count: Optional[int] = Query(None, description="Token数量"),
    error_message: Optional[str] = Query(None, description="errorinformation"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save message to specified session(For dialog history persistence)"""
    from modules.foundation.db_models.ai import AIConversation, AIMessage
    import json

    # Find or create session
    conversation = db.query(AIConversation).filter(
        AIConversation.conversation_id == conversation_id
    ).first()

    if not conversation:
        # Create new session
        conversation = AIConversation(
            conversation_id=conversation_id,
            user_id=current_user.user_id,
            username=current_user.username,
            conversation_type="chat",
            message_count=0,
        )
        db.add(conversation)

    # createmessage
    message = AIMessage(
        conversation_id=conversation_id,
        user_id=current_user.user_id,
        role=role,
        content=content,
        model=model,
        suggestions=json.dumps(suggestions) if suggestions else None,
        references=json.dumps(references) if references else None,
        token_count=token_count,
        error_message=error_message,
    )
    db.add(message)

    # Update session stats
    conversation.message_count = (conversation.message_count or 0) + 1
    conversation.last_message_at = datetime.now()
    conversation.updated_at = datetime.now()

    # Set title if first user message
    if conversation.message_count == 1 and role == "user":
        conversation.title = content[:50] + ("..." if len(content) > 50 else "")

    db.commit()
    db.refresh(message)

    return {
        "status": "success",
        "message_id": message.id,
        "conversation_id": conversation_id,
        "message_count": conversation.message_count,
    }


# ============== fault排查接口 ==============

@router.post("/troubleshoot", summary="智能fault排查")
async def troubleshoot(
    request: TroubleshootingRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    智能fault排查
    Analyze possible causes based on fault symptoms and provide handling suggestions
    """
    # Find related fault cases from database
    related_cases_query = db.query(FaultCase).filter(
        FaultCase.is_deleted == False,
        FaultCase.fault_status.in_([FaultStatus.RESOLVED, FaultStatus.CLOSED])
    )
    
    # 按关键词match
    search_term = request.symptom
    related_cases_query = related_cases_query.filter(
        (FaultCase.title.ilike(f"%{search_term}%")) |
        (FaultCase.symptom.ilike(f"%{search_term}%")) |
        (FaultCase.root_cause.ilike(f"%{search_term}%"))
    )
    
    related_cases_db = related_cases_query.order_by(FaultCase.view_count.desc()).limit(5).all()
    related_cases = [
        {
            "id": c.id,
            "case_no": c.case_no,
            "title": c.title,
            "fault_level": c.fault_level.value if c.fault_level else None,
            "symptom": c.symptom[:200] + "..." if c.symptom and len(c.symptom) > 200 else c.symptom,
            "root_cause": c.root_cause,
            "resolution": c.solution,
            "similarity": 0.8
        }
        for c in related_cases_db
    ]
    
    # Analyze possible causes by keywords
    symptom_lower = request.symptom.lower()
    possible_causes = []
    suggested_steps = []
    
    # 关键词matchanalysis
    if any(kw in symptom_lower for kw in ['cpu', '负载', 'load', '占用高']):
        possible_causes.extend([
            "CPU密集型task占用资源",
            "恶意软件或挖矿程序",
            "系统update或后台task",
            "exceptionprocess或死iteration"
        ])
        suggested_steps.append({
            "order": 1,
            "action": "viewCPU使用情况",
            "command": "top -bn1 | head -20",
            "description": "检查currentCPU占用最高的process"
        })
        suggested_steps.append({
            "order": 2,
            "action": "检查定htask",
            "command": "crontab -l",
            "description": "Check for abnormal scheduled tasks"
        })
        suggested_steps.append({
            "order": 3,
            "action": "view系统负载",
            "command": "uptime",
            "description": "检查系统1/5/15min钟average负载"
        })
    
    if any(kw in symptom_lower for kw in ['memory', 'memory', 'oom', '溢出']):
        possible_causes.extend([
            "Memory leak causes insufficient available memory",
            "大memoryoperation导致OOM",
            "cache未释放"
        ])
        suggested_steps.append({
            "order": 1,
            "action": "viewmemory使用",
            "command": "free -h",
            "description": "Check memory usage and available space"
        })
        suggested_steps.append({
            "order": 2,
            "action": "View processes with highest memory usage",
            "command": "ps aux --sort=-%mem | head -10",
            "description": "Find process consuming most memory"
        })
    
    if any(kw in symptom_lower for kw in ['disk', 'disk', 'null间', '满']):
        possible_causes.extend([
            "disknull间不足",
            "log文件过大",
            "临h文件未清理",
            "大文件占用null间"
        ])
        suggested_steps.append({
            "order": 1,
            "action": "viewdisk使用",
            "command": "df -h",
            "description": "Check disk usage of each partition"
        })
        suggested_steps.append({
            "order": 2,
            "action": "find大文件",
            "command": "du -sh /* | sort -rh | head -10",
            "description": "Find directory consuming most space"
        })
    
    if any(kw in symptom_lower for kw in ['network', 'network', 'join', '不通']):
        possible_causes.extend([
            "networkjoinfault",
            "防火墙阻断",
            "DNS解析问题",
            "port不通"
        ])
        suggested_steps.append({
            "order": 1,
            "action": "检查network连通性",
            "command": "ping -c 4 8.8.8.8",
            "description": "testnetworkjoin"
        })
        suggested_steps.append({
            "order": 2,
            "action": "检查port监听",
            "command": "ss -tlnp",
            "description": "view监听portstate"
        })
    
    if any(kw in symptom_lower for kw in ['service', 'service', 'start', 'run']):
        possible_causes.extend([
            "service未start",
            "serviceconfigurationerror",
            "依赖serviceexception",
            "port被占用"
        ])
        suggested_steps.append({
            "order": 1,
            "action": "检查servicestate",
            "command": "systemctl status <service_name>",
            "description": "viewservicerunstate"
        })
        suggested_steps.append({
            "order": 2,
            "action": "viewservicelog",
            "command": "journalctl -u <service_name> -n 50",
            "description": "viewservicelog"
        })
    
    # 如果没有match到关键词,返回通用analysis
    if not possible_causes:
        possible_causes = [
            "系统资源不足",
            "应用程序exception",
            "configurationerror",
            "外部依赖fault"
        ]
        suggested_steps = [
            {"order": 1, "action": "检查系统资源", "command": "top -bn1 && free -h && df -h", "description": "viewCPU,memory,disk使用情况"},
            {"order": 2, "action": "检查系统log", "command": "tail -100 /var/log/messages", "description": "view系统log"},
            {"order": 3, "action": "viewservicestate", "command": "systemctl status <service>", "description": "检查相关servicestate"}
        ]
    
    # find相关文档
    related_docs = []
    if related_cases:
        # Use fault cases as reference document
        for case in related_cases[:2]:
            related_docs.append({
                "id": case['id'],
                "title": case['title'],
                "type": "fault_case",
                "relevance": 0.85
            })
    
    return {
        "diagnosis": f"根据您描述的「{request.symptom}」,可能由以下原因导致",
        "confidence": 0.75 if related_cases else 0.6,
        "possible_causes": possible_causes[:5],
        "suggested_steps": suggested_steps[:5],
        "related_cases": related_cases,
        "related_docs": related_docs,
    }


@router.post("/troubleshoot/auto", summary="自动fault诊断")
async def auto_troubleshoot(
    device_id: int = Query(..., description="deviceID"),
    symptom: str = Query(..., description="fault现象描述"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    自动fault诊断
    采集devicemetric和log,综合analysisfault原因
    """
    from modules.foundation.db_models.device import Device
    
    # getdeviceinformation
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="device不存在")
    
    try:
        # 采集devicemetric
        manager = DeviceManager()
        result = await manager.collect_device(device.hostname or device.name)
        
        if result and result.status.value == 'online':
            metrics = result.metrics
            
            # Further analysis based on metric data
            diagnosis_points = []
            
            if 'cpu' in metrics:
                cpu = metrics.get('cpu', {})
                usage = cpu.get('usage', 0)
                if usage > 80:
                    diagnosis_points.append(f"CPUusage过高: {usage}%")
                if cpu.get('load_avg_1m', 0) > cpu.get('cores', 8):
                    diagnosis_points.append(f"系统负载过高: {cpu.get('load_avg_1m')}")
            
            if 'memory' in metrics:
                mem = metrics.get('memory', {})
                usage = mem.get('usage_percent', 0)
                if usage > 85:
                    diagnosis_points.append(f"memoryusage过高: {usage}%")
            
            if 'disks' in metrics:
                for disk in metrics.get('disks', []):
                    if float(disk.get('usage_percent', 0)) > 90:
                        diagnosis_points.append(f"disk {disk.get('mounted_on')} usage超过90%")
            
            return {
                "status": "completed",
                "task_id": f"task-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "device_id": device_id,
                "device_name": device.name,
                "symptom": symptom,
                "metrics_collected": True,
                "diagnosis_points": diagnosis_points if diagnosis_points else ["未发现明显exception"],
                "message": "fault诊断完成"
            }
        else:
            return {
                "status": "error",
                "task_id": f"task-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "message": f"device采集failed: {result.error if result else 'unknownerror'}"
            }
    except Exception as e:
        return {
            "status": "error",
            "task_id": f"task-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "message": f"诊断exception: {str(e)}"
        }


# ============== 建议生成接口 ==============

@router.post("/suggest", summary="生成优化建议")
async def generate_suggestion(
    request: SuggestionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    生成优化建议
    根据currentstate生成performance,安全,capacity等优化建议
    """
    suggestions = []
    summary = ""
    
    if request.type == "performance":
        # 基于metric的优化建议
        if request.metrics:
            metrics = request.metrics
            
            if 'cpu_usage' in metrics and metrics['cpu_usage'] > 80:
                suggestions.append({
                    "priority": "high",
                    "title": "CPUusage过高",
                    "description": f"currentCPUusage{metrics['cpu_usage']}%,建议优化或扩容",
                    "impact": "提高系统response速度",
                    "effort": "medium"
                })
            
            if 'memory_usage' in metrics and metrics['memory_usage'] > 85:
                suggestions.append({
                    "priority": "high",
                    "title": "memoryusage过高",
                    "description": f"currentmemoryusage{metrics['memory_usage']}%,建议扩容或优化",
                    "impact": "避免OOM和提高stable性",
                    "effort": "medium"
                })
            
            if 'disk_usage' in metrics and metrics['disk_usage'] > 90:
                suggestions.append({
                    "priority": "critical",
                    "title": "disknull间不足",
                    "description": f"currentdiskusage{metrics['disk_usage']}%,需要立即清理",
                    "impact": "避免service中断",
                    "effort": "low"
                })
        
        # 通用performance优化建议
        if not suggestions:
            suggestions.extend([
                {
                    "priority": "medium",
                    "title": "启用cache",
                    "description": "使用Redis等cache减少data库压力",
                    "impact": "提高response速度",
                    "effort": "medium"
                },
                {
                    "priority": "medium",
                    "title": "优化data库index",
                    "description": "Check and optimize slow queries and missing indexes",
                    "impact": "提高queryperformance",
                    "effort": "medium"
                }
            ])
        
        summary = f"基于{request.target}的performanceanalysis,生成了{len(suggestions)}条优化建议"
    
    elif request.type == "security":
        suggestions = [
            {
                "priority": "high",
                "title": "update系统补丁",
                "description": "定期update系统安全补丁",
                "impact": "减少安全漏洞",
                "effort": "low"
            },
            {
                "priority": "high",
                "title": "configuration防火墙",
                "description": "仅开放必要的port",
                "impact": "减少攻击面",
                "effort": "medium"
            },
            {
                "priority": "medium",
                "title": "启用log审计",
                "description": "开启login和operation审计",
                "impact": "提高安全可追溯性",
                "effort": "low"
            }
        ]
        summary = "安全加固建议已完成"
    
    elif request.type == "capacity":
        suggestions = [
            {
                "priority": "medium",
                "title": "monitoringcapacity趋势",
                "description": "Establish capacity monitoring and prediction model",
                "impact": "提前规划扩容",
                "effort": "medium"
            },
            {
                "priority": "low",
                "title": "archive历史data",
                "description": "Archive historical data to reduce storage pressure",
                "impact": "降低storage成本",
                "effort": "low"
            }
        ]
        summary = "capacity规划建议已完成"
    
    else:  # optimization
        suggestions = [
            {
                "priority": "medium",
                "title": "定期巡检",
                "description": "建立定期巡检机制",
                "impact": "及h发现问题",
                "effort": "low"
            },
            {
                "priority": "medium",
                "title": "自动化运维",
                "description": "Use scripts to automate common operations",
                "impact": "提高运维效率",
                "effort": "medium"
            }
        ]
        summary = f"针对{request.target}的优化建议已完成"
    
    return {
        "type": request.type,
        "suggestions": suggestions,
        "summary": summary,
    }


# ============== report解读接口 ==============

@router.post("/interpret/report", summary="解读报表")
async def interpret_report(
    report_id: int = Query(..., description="报表ID"),
    focus_areas: Optional[List[str]] = Query(None, description="关注领域"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    解读报表
    AI自动analysis报表内容,提取关键information和exception
    """
    from modules.foundation.db_models.report_template import Report
    
    # get报表data
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="报表不存在")
    
    # 简化实现:基于报表data进行analysis
    findings = []
    recommendations = []
    
    if report.report_data:
        try:
            data = json.loads(report.report_data) if isinstance(report.report_data, str) else report.report_data
            
            # analysis报表data中的exception
            if 'alerts' in data:
                alert_count = len(data['alerts'])
                if alert_count > 0:
                    findings.append({
                        "area": "alert",
                        "status": "warning",
                        "detail": f"Total: {alert_count}条alertrecord"
                    })
            
            if 'availability' in data:
                avail = data.get('availability', 0)
                if avail < 99.9:
                    findings.append({
                        "area": "可用性",
                        "status": "warning",
                        "detail": f"系统可用性{avail}%,未达到99.9%目标"
                    })
                else:
                    findings.append({
                        "area": "可用性",
                        "status": "normal",
                        "detail": f"系统可用性{avail}%,符合SLA要求"
                    })
        except Exception:
            pass
    
    if not findings:
        findings.append({
            "area": "总体",
            "status": "normal",
            "detail": "未发现重大exception"
        })
        recommendations.append("resume保持current运维state")
        recommendations.append("建议定期进行系统巡检")
    
    return {
        "report_id": report_id,
        "report_name": report.name,
        "summary": f"报表解读完成,Total: 发现{len(findings)}个关注点",
        "key_findings": findings,
        "recommendations": recommendations,
    }


# ============== loganalysis接口 ==============

@router.post("/analyze/logs", summary="analysislog")
async def analyze_logs(
    logs: str = Query(..., description="log内容"),
    context: Optional[str] = Query(None, description="contextinformation"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    智能loganalysis
    analysislog内容,提取error,exception和关键event
    """
    lines = logs.strip().split('\n') if logs else []
    
    errors = []
    warnings = []
    timeline = []
    
    error_keywords = ['error', 'exception', 'fatal', 'failed', 'failure']
    warning_keywords = ['warning', 'warn', 'timeout']
    
    for line in lines:
        line_lower = line.lower()
        
        if any(kw in line_lower for kw in error_keywords):
            errors.append({
                "line": line[:200],
                "possible_cause": "需要Check service status and network connections"
            })
        
        if any(kw in line_lower for kw in warning_keywords):
            warnings.append({
                "line": line[:200]
            })
        
        # 尝试提取time戳
        import re
        time_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', line)
        if time_match:
            timeline.append({
                "time": time_match.group(1),
                "event": line[:100]
            })
    
    # 去重
    seen_errors = set()
    unique_errors = []
    for e in errors:
        key = e['line'][:50]
        if key not in seen_errors:
            seen_errors.add(key)
            unique_errors.append(e)
    
    seen_warnings = set()
    unique_warnings = []
    for w in warnings:
        key = w['line'][:50]
        if key not in seen_warnings:
            seen_warnings.add(key)
            unique_warnings.append(w)
    
    # 生成analysisdigest
    summary = f"Total: analysis了{len(lines)}行log,发现{len(unique_errors)}个error,{len(unique_warnings)}个warning"
    
    return {
        "summary": summary,
        "errors": unique_errors[:10],
        "warnings": unique_warnings[:10],
        "timeline": timeline[:20],
        "error_count": len(unique_errors),
        "warning_count": len(unique_warnings),
    }


# ============== 知识问答接口 ==============

@router.post("/qa", summary="知识问答")
async def question_answer(
    question: str = Query(..., description="问题"),
    category: Optional[str] = Query(None, description="问题class别"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    知识问答
    Answer O&M related questions based on knowledge base
    """
    # Search relevant content from knowledge base
    from modules.business.knowledge_base.models import SOPDocument
    
    # searchSOP文档
    query = db.query(SOPDocument).filter(
        SOPDocument.is_deleted == False,
        SOPDocument.status == 'approved'
    )
    
    if question:
        query = query.filter(
            (SOPDocument.title.ilike(f"%{question}%")) |
            (SOPDocument.content.ilike(f"%{question}%"))
        )
    
    docs = query.limit(5).all()
    
    sources = []
    answer_parts = []
    
    if docs:
        for doc in docs:
            sources.append({
                "id": doc.id,
                "title": doc.title,
                "type": "sop",
                "relevance": 0.9
            })
            # 提取相关内容作为答案
            content_preview = doc.content[:300] if doc.content else ""
            answer_parts.append(f"[{doc.title}]\n{content_preview}...")
    
    if answer_parts:
        answer = "\n\n".join(answer_parts[:2])
        confidence = 0.85
    else:
        # 通用回答
        answer = "抱歉,No relevant content found in knowledge base.建议您:\n1. view系统operation手册\n2. 咨询技术supported人员\n3. commit工单gethelp"
        confidence = 0.3
    
    return {
        "answer": answer,
        "sources": sources,
        "confidence": confidence,
        "question": question
    }


# ============== sessionstatistics接口 ==============

@router.get("/stats", summary="getAI助手statistics")
async def get_ai_stats(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """getAI助手使用statistics"""
    # Get statistics from fault cases
    total_cases = db.query(FaultCase).filter(FaultCase.is_deleted == False).count()
    
    # 从SOP文档getstatisticsdata
    from modules.business.knowledge_base.models import SOPDocument
    total_sops = db.query(SOPDocument).filter(
        SOPDocument.is_deleted == False,
        SOPDocument.status == 'approved'
    ).count()
    
    return {
        "total_conversations": 0,  # 需要sessionstorage
        "total_messages": 0,
        "today_conversations": 0,
        "today_messages": 0,
        "knowledge_base_size": {
            "fault_cases": total_cases,
            "sop_documents": total_sops,
        },
        "avg_response_time_ms": 0,  # 需要LLMservice
    }


# ============== alert根因analysis接口 ==============

class RootCauseAnalyzeRequest(BaseModel):
    """根因analysisrequest"""
    include_llm: bool = Field(True, description="是否使用LLM深度analysis")
    include_history: bool = Field(True, description="是否包含关联alert")
    include_cases: bool = Field(True, description="是否包含相似案例")


class RootCauseAnalyzeResponse(BaseModel):
    """根因analysisresponse"""
    alert_id: int
    success: bool
    root_cause: str
    confidence: float
    possible_causes: List[Dict]
    related_alerts: List[Dict]
    analysis_steps: List[Dict]
    evidence: Dict
    recommendations: List[str]
    metadata: Dict
    error: Optional[str] = None


@router.post(
    "/analyze/{alert_id}/root-cause",
    summary="alert根因analysis",
    response_model=RootCauseAnalyzeResponse
)
async def analyze_root_cause(
    alert_id: int,
    request: RootCauseAnalyzeRequest = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    AIalert根因analysis
    
    Based on alert info and historical data,使用AIanalysisalert的根本原因.
    supported:
    - 基于模式的初步analysis
    - 关联alertfind
    - 相似案例match
    - LLM深度analysis(可选)
    """
    # 如果没有request体,使用defaultparameter
    if request is None:
        request = RootCauseAnalyzeRequest()
    
    # get根因analysis器
    analyzer = get_root_cause_analyzer()
    
    # 尝试getLLMclient(如果可用)
    try:
        from api.start import get_llm_client
        llm_client = get_llm_client()
        if llm_client:
            analyzer.llm_client = llm_client
    except Exception:
        pass  # LLM不可用h使用无LLM模式
    
    # 执行analysis
    result = await analyzer.analyze(
        alert_id=alert_id,
        db=db,
        include_llm=request.include_llm,
        include_history=request.include_history,
        include_cases=request.include_cases
    )
    
    # 返回结果
    return RootCauseAnalyzeResponse(
        alert_id=result.alert_id,
        success=result.success,
        root_cause=result.root_cause,
        confidence=result.confidence,
        possible_causes=result.possible_causes,
        related_alerts=result.related_alerts,
        analysis_steps=result.analysis_steps,
        evidence=result.evidence,
        recommendations=result.recommendations,
        metadata=result.metadata,
        error=result.error if not result.success else None
    )


# ============== C3: alert处置(Remediation)接口 ==============

from modules.business.ai_copilot.remediation import RemediationEngine, RemediationPlan


class RemediationRequest(BaseModel):
    """alert处置request"""
    alert_id: int = Field(..., description="alertID")
    include_auto_executable: bool = Field(False, description="Only return auto-executable steps")


class RemediationStepResponse(BaseModel):
    """处置stepresponse"""
    step_id: int
    action: str
    description: str
    command: Optional[str] = None
    rationale: Optional[str] = None
    estimated_duration: Optional[str] = None
    auto_executable: bool = False


class SOPMatchResponse(BaseModel):
    """match的SOPresponse"""
    sop_id: str
    sop_name: str
    match_score: float
    matched_keywords: List[str] = []
    prerequisites: List[str] = []


class RemediationResponse(BaseModel):
    """alert处置response"""
    plan_id: str
    alert_id: str
    alert_type: str
    alert_level: str
    matched_sop: Optional[SOPMatchResponse] = None
    steps: List[RemediationStepResponse]
    risk_level: str
    estimated_time: Optional[str] = None
    summary: str


def get_remediation_engine() -> RemediationEngine:
    """
    get RemediationEngine instance
    """
    return RemediationEngine()


@router.post(
    "/analyze/{alert_id}/remediation",
    summary="alert智能处置",
    response_model=RemediationResponse
)
async def get_remediation(
    alert_id: int,
    request: Optional[RemediationRequest] = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Alert remediation endpoint"""
    # 如果没有request体,使用defaultparameter
    if request is None:
        request = RemediationRequest(alert_id=alert_id)
    
    # get RemediationEngine
    engine = get_remediation_engine()
    
    # 从data库getalertinformation
    from modules.foundation.db_models.monitoring import Alert
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail=f"alert {alert_id} 不存在")
    
    # 构造alertdata
    alert_data = {
        "alert_id": str(alert_id),
        "alert_type": alert.alert_type or "unknown",
        "name": alert.name or "",
        "message": alert.message or "",
        "level": alert.level or "medium",
    }
    
    # 生成处置方案
    plan: RemediationPlan = engine.generate_remediation_plan(alert_id, alert_data)
    
    # Filter auto-executable steps (if requested)
    steps = plan.generated_steps
    if request.include_auto_executable:
        steps = [s for s in steps if s.auto_executable]
    
    # buildmatch的SOPresponse
    matched_sop = None
    if plan.matched_sops:
        best_match = plan.matched_sops[0]
        matched_sop = SOPMatchResponse(
            sop_id=best_match.sop_id,
            sop_name=best_match.sop_name,
            match_score=best_match.match_score,
            matched_keywords=best_match.matched_keywords,
            prerequisites=best_match.prerequisites,
        )
    
    return RemediationResponse(
        plan_id=f"plan_{alert_id}_{int(datetime.now().timestamp())}",
        alert_id=str(alert_id),
        alert_type=plan.alert_type,
        alert_level=plan.alert_level,
        matched_sop=matched_sop,
        steps=[
            RemediationStepResponse(
                step_id=s.step_id,
                action=s.action,
                description=s.description,
                command=s.command,
                rationale=s.rationale,
                estimated_duration=s.estimated_duration,
                auto_executable=s.auto_executable,
            )
            for s in steps
        ],
        risk_level=plan.risk_level,
        estimated_time=plan.estimated_total_time,
        summary=plan.summary,
    )
