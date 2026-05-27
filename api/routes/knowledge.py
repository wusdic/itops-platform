"""
知识库API路由
提供SOP文档、故障案例、文档管理等接口
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_

from api.dependencies import get_db, get_current_user, CurrentUser, PaginationParams
from modules.business.knowledge_base.models import (
    SOPDocument, FaultCase, Category, Tag,
    DocumentStatus, FaultLevel, FaultStatus, ReviewStatus
)
from modules.business.knowledge.knowledge_graph import get_knowledge_graph


router = APIRouter()


# ============== 请求/响应模型 ==============

class SOPDocumentCreate(BaseModel):
    """创建SOP文档请求"""
    title: str = Field(..., max_length=200, description="文档标题")
    content: str = Field(..., description="文档内容(Markdown)")
    category_id: Optional[int] = Field(None, description="分类ID")
    tags: Optional[str] = Field(None, description="标签，逗号分隔")
    author: Optional[str] = Field(None, description="作者")


class SOPDocumentUpdate(BaseModel):
    """更新SOP文档请求"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[str] = None
    status: Optional[str] = None


class FaultCaseCreate(BaseModel):
    """创建故障案例请求"""
    title: str = Field(..., max_length=200, description="案例标题")
    fault_level: str = Field("P3", description="故障级别: p1, p2, p3, p4")
    fault_category: Optional[str] = Field(None, description="故障分类")
    symptom: str = Field(..., description="故障现象")
    root_cause: Optional[str] = Field(None, description="根本原因")
    solution: Optional[str] = Field(None, description="解决方案")
    prevention: Optional[str] = Field(None, description="预防措施")
    tags: Optional[str] = Field(None, description="标签")
    category_id: Optional[int] = Field(None, description="分类ID")


class FaultCaseUpdate(BaseModel):
    """更新故障案例请求"""
    title: Optional[str] = Field(None, max_length=200)
    fault_level: Optional[str] = None
    fault_status: Optional[str] = None
    fault_category: Optional[str] = None
    symptom: Optional[str] = None
    root_cause: Optional[str] = None
    solution: Optional[str] = None
    prevention: Optional[str] = None
    tags: Optional[str] = None


class CategoryCreate(BaseModel):
    """创建分类请求"""
    name: str = Field(..., max_length=100, description="分类名称")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    code: Optional[str] = Field(None, max_length=50, description="分类编码")
    doc_type: Optional[str] = Field(None, description="文档类型")
    description: Optional[str] = Field(None, description="描述")


class TagCreate(BaseModel):
    """创建标签请求"""
    name: str = Field(..., max_length=50, description="标签名称")
    color: Optional[str] = Field(None, max_length=20, description="标签颜色")
    category_id: Optional[int] = Field(None, description="分类ID")
    description: Optional[str] = Field(None, description="描述")


def _sop_to_dict(sop: SOPDocument) -> dict:
    """SOP文档转字典"""
    return {
        'id': sop.id,
        'doc_no': sop.doc_no,
        'title': sop.title,
        'content': sop.content,
        'category_id': sop.category_id,
        'tags': sop.tags.split(',') if sop.tags else [],
        'version': sop.version,
        'status': str(sop.status) if sop.status else 'DRAFT',
        'author': sop.author,
        'reviewer': sop.reviewer,
        'approver': sop.approver,
        'review_status': str(sop.review_status) if sop.review_status else None,
        'effective_date': sop.effective_date.isoformat() if sop.effective_date else None,
        'view_count': sop.view_count,
        'like_count': sop.like_count,
        'created_at': sop.created_at.isoformat() if sop.created_at else None,
        'updated_at': sop.updated_at.isoformat() if sop.updated_at else None,
    }


def _case_to_dict(case: FaultCase) -> dict:
    """故障案例转字典"""
    return {
        'id': case.id,
        'case_no': case.case_no,
        'title': case.title,
        'fault_level': str(case.fault_level) if case.fault_level else None,
        'fault_status': str(case.fault_status) if case.fault_status else None,
        'fault_category': case.fault_category,
        'symptom': case.symptom,
        'root_cause': case.root_cause,
        'solution': case.solution,
        'prevention': case.prevention,
        'affected_systems': case.affected_systems or [],
        'user_impact': case.user_impact,
        'business_impact': case.business_impact,
        'duration': case.duration,
        'tags': case.tags.split(',') if case.tags else [],
        'occurrence_time': case.occurrence_time.isoformat() if case.occurrence_time else None,
        'resolution_time': case.resolution_time.isoformat() if case.resolution_time else None,
        'author': case.author,
        'view_count': case.view_count,
        'created_at': case.created_at.isoformat() if case.created_at else None,
        'updated_at': case.updated_at.isoformat() if case.updated_at else None,
    }


def _category_to_dict(cat: Category, include_children: bool = False) -> dict:
    """分类转字典"""
    result = {
        'id': cat.id,
        'name': cat.name,
        'parent_id': cat.parent_id,
        'code': cat.code,
        'doc_type': cat.doc_type.value if cat.doc_type else None,
        'description': cat.description,
        'sort_order': cat.sort_order,
        'icon': cat.icon,
        'is_active': cat.is_active,
    }
    if include_children:
        result['children'] = [_category_to_dict(c, True) for c in cat.children if c.is_active]
    return result


def _tag_to_dict(tag: Tag) -> dict:
    """标签转字典"""
    return {
        'id': tag.id,
        'name': tag.name,
        'color': tag.color,
        'category_id': tag.category_id,
        'description': tag.description,
        'usage_count': tag.usage_count,
    }


# ============== 搜索接口 ==============

@router.get("/search", summary="知识库搜索")
async def search_knowledge(
    query: Optional[str] = Query(None, description="搜索关键词(query的别名)"),
    keyword: Optional[str] = Query(None, description="搜索关键词(keyword)"),
    search_type: str = Query("hybrid", description="搜索类型: fulltext, semantic, hybrid"),
    doc_type: Optional[str] = Query(None, description="文档类型过滤"),
    category_id: Optional[int] = Query(None, description="分类ID过滤"),
    tags: Optional[str] = Query(None, description="标签过滤"),
    limit: int = Query(20, le=100, description="返回数量限制"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    知识库全文/向量搜索
    支持关键词搜索和语义搜索
    """
    search_query = keyword or query or ""
    
    if not search_query:
        return {"query": "", "items": [], "total": 0}
    
    results = []
    
    # 搜索SOP文档
    if not doc_type or doc_type == "sop":
        sop_query = db.query(SOPDocument).filter(
            SOPDocument.is_deleted == False,
            SOPDocument.status == DocumentStatus.APPROVED
        )
        if search_query:
            sop_query = sop_query.filter(
                or_(
                    SOPDocument.title.ilike(f"%{search_query}%"),
                    SOPDocument.content.ilike(f"%{search_query}%"),
                )
            )
        if category_id:
            sop_query = sop_query.filter(SOPDocument.category_id == category_id)
        sops = sop_query.limit(limit).all()
        for sop in sops:
            results.append({
                "id": sop.id,
                "type": "sop",
                "title": sop.title,
                "snippet": (sop.content[:200] + "...") if sop.content and len(sop.content) > 200 else (sop.content or ""),
                "score": 1.0,
            })
    
    # 搜索故障案例
    if not doc_type or doc_type == "fault_case":
        case_query = db.query(FaultCase).filter(FaultCase.is_deleted == False)
        if search_query:
            case_query = case_query.filter(
                or_(
                    FaultCase.title.ilike(f"%{search_query}%"),
                    FaultCase.symptom.ilike(f"%{search_query}%"),
                    FaultCase.root_cause.ilike(f"%{search_query}%"),
                )
            )
        if category_id:
            case_query = case_query.filter(FaultCase.category_id == category_id)
        cases = case_query.limit(limit).all()
        for case in cases:
            results.append({
                "id": case.id,
                "type": "fault_case",
                "title": case.title,
                "snippet": (case.symptom[:200] + "...") if case.symptom and len(case.symptom) > 200 else (case.symptom or ""),
                "score": 1.0,
            })
    
    return {
        "query": search_query,
        "search_type": search_type,
        "items": results[:limit],
        "total": len(results),
    }


# ============== SOP文档接口 ==============

@router.get("/sop", summary="获取SOP文档列表")
async def get_sop_documents(
    status: Optional[str] = Query(None, description="状态过滤"),
    category_id: Optional[int] = Query(None, description="分类ID过滤"),
    tags: Optional[str] = Query(None, description="标签过滤"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    pagination: PaginationParams = Depends(PaginationParams),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取SOP文档列表"""
    query = db.query(SOPDocument).filter(SOPDocument.is_deleted == False)
    
    if status:
        try:
            status_enum = DocumentStatus(status)
            query = query.filter(SOPDocument.status == status_enum)
        except ValueError:
            pass
    
    if category_id:
        query = query.filter(SOPDocument.category_id == category_id)
    
    if tags:
        tag_list = [t.strip() for t in tags.split(',')]
        for tag in tag_list:
            query = query.filter(SOPDocument.tags.ilike(f"%{tag}%"))
    
    if keyword:
        query = query.filter(
            or_(
                SOPDocument.title.ilike(f"%{keyword}%"),
                SOPDocument.content.ilike(f"%{keyword}%"),
            )
        )
    
    total = query.count()
    sops = query.order_by(SOPDocument.updated_at.desc()).offset(pagination.offset).limit(pagination.limit).all()
    
    return {
        "items": [_sop_to_dict(s) for s in sops],
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
    }


@router.post("/sop", summary="创建SOP文档")
async def create_sop_document(
    document: SOPDocumentCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建新的SOP文档"""
    doc_no = f"SOP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{datetime.now().microsecond:04d}"
    
    db_sop = SOPDocument(
        doc_no=doc_no,
        title=document.title,
        content=document.content,
        category_id=document.category_id,
        tags=document.tags,
        author=document.author or current_user.username,
        status=DocumentStatus.DRAFT,
    )
    
    db.add(db_sop)
    db.commit()
    db.refresh(db_sop)
    
    return _sop_to_dict(db_sop)


@router.get("/sop/{doc_id}", summary="获取SOP文档详情")
async def get_sop_document(
    doc_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取SOP文档的详细信息"""
    sop = db.query(SOPDocument).filter(SOPDocument.id == doc_id, SOPDocument.is_deleted == False).first()
    
    if not sop:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 增加查看次数
    sop.view_count += 1
    db.commit()
    
    return _sop_to_dict(sop)


@router.put("/sop/{doc_id}", summary="更新SOP文档")
async def update_sop_document(
    doc_id: int,
    document: SOPDocumentUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新SOP文档"""
    sop = db.query(SOPDocument).filter(SOPDocument.id == doc_id, SOPDocument.is_deleted == False).first()
    
    if not sop:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    update_data = document.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == 'status' and value:
            setattr(sop, key, DocumentStatus(value))
        else:
            setattr(sop, key, value)
    
    sop.updated_at = datetime.now()
    db.commit()
    db.refresh(sop)
    
    return _sop_to_dict(sop)


@router.delete("/sop/{doc_id}", summary="删除SOP文档")
async def delete_sop_document(
    doc_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除SOP文档（软删除）"""
    sop = db.query(SOPDocument).filter(SOPDocument.id == doc_id, SOPDocument.is_deleted == False).first()
    
    if not sop:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    sop.is_deleted = True
    sop.updated_at = datetime.now()
    db.commit()
    
    return {"status": "success", "message": "Document deleted successfully"}


@router.post("/sop/{doc_id}/review", summary="提交SOP文档审核")
async def submit_sop_review(
    doc_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """提交SOP文档进行审核"""
    sop = db.query(SOPDocument).filter(SOPDocument.id == doc_id, SOPDocument.is_deleted == False).first()
    
    if not sop:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    sop.status = DocumentStatus.PENDING_REVIEW
    sop.review_status = ReviewStatus.PENDING
    sop.updated_at = datetime.now()
    db.commit()
    
    return {"status": "success", "message": "Document submitted for review"}


@router.post("/sop/{doc_id}/approve", summary="批准SOP文档")
async def approve_sop_document(
    doc_id: int,
    comment: Optional[str] = Query(None, description="审核意见"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """批准SOP文档"""
    sop = db.query(SOPDocument).filter(SOPDocument.id == doc_id, SOPDocument.is_deleted == False).first()
    
    if not sop:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    sop.status = DocumentStatus.APPROVED
    sop.review_status = ReviewStatus.APPROVED
    sop.review_comment = comment
    sop.approver = current_user.username
    sop.approval_date = datetime.now()
    sop.effective_date = datetime.now()
    sop.updated_at = datetime.now()
    db.commit()
    
    return {"status": "success", "message": "Document approved"}


# ============== 故障案例接口 ==============

@router.get("/fault-case", summary="获取故障案例列表")
async def get_fault_cases(
    fault_level: Optional[str] = Query(None, description="故障级别过滤"),
    fault_status: Optional[str] = Query(None, description="故障状态过滤"),
    fault_category: Optional[str] = Query(None, description="故障分类过滤"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    pagination: PaginationParams = Depends(PaginationParams),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取故障案例列表"""
    query = db.query(FaultCase).filter(FaultCase.is_deleted == False)
    
    if fault_level:
        try:
            level_enum = FaultLevel(fault_level.lower())
            query = query.filter(FaultCase.fault_level == level_enum)
        except ValueError:
            pass
    
    if fault_status:
        try:
            status_enum = FaultStatus(fault_status)
            query = query.filter(FaultCase.fault_status == status_enum)
        except ValueError:
            pass
    
    if fault_category:
        query = query.filter(FaultCase.fault_category == fault_category)
    
    if keyword:
        query = query.filter(
            or_(
                FaultCase.title.ilike(f"%{keyword}%"),
                FaultCase.symptom.ilike(f"%{keyword}%"),
                FaultCase.root_cause.ilike(f"%{keyword}%"),
            )
        )
    
    total = query.count()
    cases = query.order_by(FaultCase.updated_at.desc()).offset(pagination.offset).limit(pagination.limit).all()
    
    return {
        "items": [_case_to_dict(c) for c in cases],
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
    }


@router.post("/fault-case", summary="创建故障案例")
async def create_fault_case(
    case: FaultCaseCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建新的故障案例"""
    case_no = f"CASE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{datetime.now().microsecond:04d}"
    
    try:
        level_enum = FaultLevel(case.fault_level.lower())
    except ValueError:
        level_enum = FaultLevel.P3
    
    db_case = FaultCase(
        case_no=case_no,
        title=case.title,
        fault_level=level_enum,
        fault_status=FaultStatus.OPEN,
        fault_category=case.fault_category,
        symptom=case.symptom,
        root_cause=case.root_cause,
        solution=case.solution,
        prevention=case.prevention,
        tags=case.tags,
        category_id=case.category_id,
        author=current_user.username,
    )
    
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    
    return _case_to_dict(db_case)


@router.get("/fault-case/{case_id}", summary="获取故障案例详情")
async def get_fault_case(
    case_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取故障案例的详细信息"""
    case = db.query(FaultCase).filter(FaultCase.id == case_id, FaultCase.is_deleted == False).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")
    
    # 增加查看次数
    case.view_count += 1
    db.commit()
    
    return _case_to_dict(case)


@router.put("/fault-case/{case_id}", summary="更新故障案例")
async def update_fault_case(
    case_id: int,
    case: FaultCaseUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新故障案例"""
    db_case = db.query(FaultCase).filter(FaultCase.id == case_id, FaultCase.is_deleted == False).first()
    
    if not db_case:
        raise HTTPException(status_code=404, detail="案例不存在")
    
    update_data = case.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == 'fault_level' and value:
            try:
                setattr(db_case, key, FaultLevel(value.lower()))
            except ValueError:
                pass
        elif key == 'fault_status' and value:
            try:
                setattr(db_case, key, FaultStatus(value))
            except ValueError:
                pass
        else:
            setattr(db_case, key, value)
    
    db_case.updated_at = datetime.now()
    db.commit()
    db.refresh(db_case)
    
    return _case_to_dict(db_case)


# ============== AI 案例推荐接口 ==============

# 模块级同步 LLM 客户端（避免在 async context 中创建 event loop）
_sync_llm_client = None

def _get_sync_llm_client():
    global _sync_llm_client
    if _sync_llm_client is None:
        from modules.business.ai_copilot.llm_client import SyncLLMClient
        from api.start import get_config_manager
        cm = get_config_manager()
        ai_config = cm.get("ai_copilot", {}) if cm else {}
        _sync_llm_client = SyncLLMClient(ai_config)
    return _sync_llm_client


class SimilarCaseRecommendRequest(BaseModel):
    """推荐请求模型"""
    top_n: int = Field(default=5, ge=1, le=20, description="推荐数量")
    min_score: float = Field(default=0.3, ge=0.0, le=1.0, description="最低相似度阈值")


@router.post("/fault-case/{case_id}/recommend-similar", summary="AI推荐相似故障案例")
async def recommend_similar_cases(
    case_id: int,
    body: SimilarCaseRecommendRequest = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    基于 LLM 语义分析，推荐与指定故障案例相似的历史案例。

    - 阶段1：基于关键词 + 分类 + 级别初筛候选案例
    - 阶段2：调用 LLM 对候选案例进行语义相似度评分
    - 返回 Top 推荐，按相似度降序排列
    """
    from modules.business.knowledge_base.case import CaseRecommender

    top_n = body.top_n if body else 5
    min_score = body.min_score if body else 0.3

    from modules.business.knowledge_base.case import CaseRecommender

    # CaseRecommender 需要同步 db，LLM 调用在外部通过 executor 执行
    # 先创建无 llm_client 的 recommender 来获取候选
    recommender_no_llm = CaseRecommender(db, llm_client=None)
    candidates_result = recommender_no_llm._get_candidates(case_id, top_n=top_n)

    if not candidates_result.get("success"):
        raise HTTPException(status_code=400, detail=candidates_result.get("error", "获取候选失败"))

    candidate_cases = candidates_result.get("candidate_cases", [])
    query_dict = candidates_result.get("query_dict", {})

    if not candidate_cases:
        return {
            "success": True, "case_id": case_id, "recommendations": [],
            "analysis_summary": "候选案例库为空", "total_candidates": 0
        }

    # 构建 prompt
    prompt = recommender_no_llm._build_similarity_prompt(query_dict, candidate_cases)

    # 通过线程池执行同步 LLM 调用
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FUTimeoutError
    _llm_executor = ThreadPoolExecutor(max_workers=2)

    def _do_chat():
        client = _get_sync_llm_client()
        return client.chat([{"role": "user", "content": prompt}])

    future = _llm_executor.submit(_do_chat)
    try:
        response = future.result(timeout=60)
    except FUTimeoutError:
        response = {"content": "", "error": "LLM调用超时"}

    response_text = response.get("content", "") if isinstance(response, dict) else str(response)
    llm_result = recommender_no_llm._parse_llm_response(response_text)

    recommendations = []
    for rec in llm_result.get("recommendations", []):
        if rec.get("similarity_score", 0) < min_score:
            continue
        matched = next((c for c in candidate_cases if c["id"] == rec["id"]), None)
        if matched:
            recommendations.append({
                "id": rec["id"],
                "similarity_score": round(rec.get("similarity_score", 0), 3),
                "match_reason": rec.get("match_reason", ""),
                "title": matched["title"],
                "symptom": matched["symptom"],
                "root_cause": matched["root_cause"],
                "solution": matched["solution"],
            })

    return {
        "success": True,
        "case_id": case_id,
        "recommendations": sorted(recommendations, key=lambda x: x["similarity_score"], reverse=True),
        "analysis_summary": llm_result.get("analysis_summary", ""),
        "total_candidates": len(candidate_cases),
        "llm_fallback": False,
    }


# ============== 分类接口 ==============

@router.get("/category", summary="获取分类列表")
async def get_categories(
    doc_type: Optional[str] = Query(None, description="文档类型过滤"),
    parent_id: Optional[int] = Query(None, description="父分类ID"),
    include_children: bool = Query(False, description="是否包含子分类"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取文档分类列表"""
    query = db.query(Category).filter(Category.is_active == True)
    
    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    else:
        query = query.filter(Category.parent_id == None)
    
    categories = query.all()
    
    return {
        "items": [_category_to_dict(c, include_children) for c in categories],
        "total": len(categories),
    }


@router.post("/category", summary="创建分类")
async def create_category(
    category: CategoryCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建新的分类"""
    db_category = Category(
        name=category.name,
        parent_id=category.parent_id,
        code=category.code,
        description=category.description,
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return _category_to_dict(db_category)


@router.put("/category/{category_id}", summary="更新分类")
async def update_category(
    category_id: int,
    category: CategoryCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新指定分类"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="分类不存在")
    if category.name:
        db_category.name = category.name
    if category.parent_id is not None:
        db_category.parent_id = category.parent_id
    if category.code is not None:
        db_category.code = category.code
    if category.description is not None:
        db_category.description = category.description
    db.commit()
    return _category_to_dict(db_category)


@router.delete("/category/{category_id}", summary="删除分类")
async def delete_category(
    category_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除指定分类"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="分类不存在")
    db.delete(db_category)
    db.commit()
    return {"status": "success", "message": "分类已删除"}


@router.delete("/fault-case/{case_id}", summary="删除故障案例")
async def delete_fault_case(
    case_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除指定故障案例"""
    db_case = db.query(FaultCase).filter(FaultCase.id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="故障案例不存在")
    db_case.is_deleted = True
    db.commit()
    return {"status": "success", "message": "故障案例已删除"}


# ============== 标签接口 ==============

@router.get("/tag", summary="获取标签列表")
async def get_tags(
    category_id: Optional[int] = Query(None, description="分类ID"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    limit: int = Query(50, le=200, description="返回数量限制"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取标签列表"""
    query = db.query(Tag)
    
    if category_id:
        query = query.filter(Tag.category_id == category_id)
    
    if keyword:
        query = query.filter(Tag.name.ilike(f"%{keyword}%"))
    
    tags = query.order_by(Tag.usage_count.desc()).limit(limit).all()
    
    return {
        "items": [_tag_to_dict(t) for t in tags],
        "total": len(tags),
    }


@router.post("/tag", summary="创建标签")
async def create_tag(
    tag: TagCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建新的标签"""
    existing = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="标签已存在")

    db_tag = Tag(
        name=tag.name,
        color=tag.color,
        category_id=tag.category_id,
        description=tag.description,
    )
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag.to_dict()


# ============== 统计接口 ==============

@router.get("/stats", summary="获取知识库统计")
async def get_knowledge_stats(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取知识库统计信息"""
    total_sops = db.query(SOPDocument).filter(SOPDocument.is_deleted == False).count()
    approved_sops = db.query(SOPDocument).filter(
        SOPDocument.is_deleted == False,
        SOPDocument.status == DocumentStatus.APPROVED
    ).count()
    
    total_cases = db.query(FaultCase).filter(FaultCase.is_deleted == False).count()
    
    total_categories = db.query(Category).filter(Category.is_active == True).count()
    total_tags = db.query(Tag).count()
    
    # 获取查看次数最高的标签
    top_tags = db.query(Tag).order_by(Tag.usage_count.desc()).limit(10).all()
    
    return {
        "total_documents": total_sops + total_cases,
        "sop_count": total_sops,
        "approved_sop_count": approved_sops,
        "fault_case_count": total_cases,
        "category_count": total_categories,
        "tag_count": total_tags,
        "top_tags": [{"name": t.name, "count": t.usage_count} for t in top_tags],
    }


# ============== 文档多级审核接口 ==============

class ReviewFlowCreate(BaseModel):
    """创建审核流程请求"""
    name: str = Field(..., description="流程名称")
    description: str = Field("", description="流程描述")
    levels: List[dict] = Field(..., description="审核级别配置列表")
    enable_timeout_notification: bool = True
    timeout_notification_interval: int = 24
    allow_withdraw_after_approve: bool = False
    applicable_doc_types: List[str] = Field(default_factory=list, description="适用文档类型")
    applicable_categories: List[int] = Field(default_factory=list, description="适用分类")


class ReviewFlowUpdate(BaseModel):
    """更新审核流程请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    levels: Optional[List[dict]] = None
    enable_timeout_notification: Optional[bool] = None
    timeout_notification_interval: Optional[int] = None
    allow_withdraw_after_approve: Optional[bool] = None
    applicable_doc_types: Optional[List[str]] = None
    applicable_categories: Optional[List[int]] = None


class ReviewSubmitRequest(BaseModel):
    """提交审核请求"""
    flow_id: str = Field(..., description="审核流程ID")
    document_id: int = Field(..., description="文档ID")
    document_type: str = Field(..., description="文档类型")
    document_title: str = Field(..., description="文档标题")
    comment: str = Field("", description="提交说明")


@router.get("/review-flows", summary="获取审核流程列表")
async def get_review_flows(
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取文档审核流程列表"""
    from modules.business.knowledge_base.document_review import get_review_flow
    
    flow_manager = get_review_flow()
    flows = flow_manager.list_flows()
    
    return {
        "items": [f.to_dict() for f in flows],
        "total": len(flows),
    }


@router.post("/review-flows", summary="创建审核流程")
async def create_review_flow(
    flow: ReviewFlowCreate,
    current_user: CurrentUser = Depends(get_current_user),
):
    """创建新的文档审核流程"""
    from modules.business.knowledge_base.document_review import (
        get_review_flow, ReviewFlowConfig, ReviewLevelConfig, ReviewLevel
    )
    
    flow_manager = get_review_flow()
    
    import uuid
    levels = []
    for i, level_config in enumerate(flow.levels):
        levels.append(ReviewLevelConfig(
            level=ReviewLevel(f"level_{i+1}"),
            name=level_config.get('name', f'Level {i+1}'),
            description=level_config.get('description', ''),
            reviewer_role=level_config.get('reviewer_role', ''),
            specific_reviewers=level_config.get('specific_reviewers', []),
            require_all_approved=level_config.get('require_all_approved', True),
            auto_assign=level_config.get('auto_assign', True),
            allow_skip=level_config.get('allow_skip', False),
            timeout_hours=level_config.get('timeout_hours', 48),
        ))
    
    flow_config = ReviewFlowConfig(
        id=str(uuid.uuid4()),
        name=flow.name,
        description=flow.description,
        levels=levels,
        enable_timeout_notification=flow.enable_timeout_notification,
        timeout_notification_interval=flow.timeout_notification_interval,
        allow_withdraw_after_approve=flow.allow_withdraw_after_approve,
        applicable_doc_types=flow.applicable_doc_types,
        applicable_categories=flow.applicable_categories,
        created_by=current_user.username,
    )
    
    flow_manager.add_flow(flow_config)
    
    return {"id": flow_config.id, "message": "创建成功"}


@router.get("/review-flows/{flow_id}", summary="获取审核流程详情")
async def get_review_flow_detail(
    flow_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取审核流程详细信息"""
    from modules.business.knowledge_base.document_review import get_review_flow
    
    flow_manager = get_review_flow()
    flow = flow_manager.get_flow(flow_id)
    
    if not flow:
        raise HTTPException(status_code=404, detail="审核流程不存在")
    
    return flow.to_dict()


@router.put("/review-flows/{flow_id}", summary="更新审核流程")
async def update_review_flow(
    flow_id: str,
    flow_update: ReviewFlowUpdate,
    current_user: CurrentUser = Depends(get_current_user),
):
    """更新审核流程"""
    from modules.business.knowledge_base.document_review import (
        get_review_flow, ReviewLevelConfig, ReviewLevel
    )
    
    flow_manager = get_review_flow()
    flow = flow_manager.get_flow(flow_id)
    
    if not flow:
        raise HTTPException(status_code=404, detail="审核流程不存在")
    
    update_data = flow_update.model_dump(exclude_unset=True)
    
    if 'levels' in update_data and update_data['levels']:
        levels = []
        for i, level_config in enumerate(update_data['levels']):
            levels.append(ReviewLevelConfig(
                level=ReviewLevel(f"level_{i+1}"),
                name=level_config.get('name', f'Level {i+1}'),
                description=level_config.get('description', ''),
                reviewer_role=level_config.get('reviewer_role', ''),
                specific_reviewers=level_config.get('specific_reviewers', []),
                require_all_approved=level_config.get('require_all_approved', True),
                auto_assign=level_config.get('auto_assign', True),
                allow_skip=level_config.get('allow_skip', False),
                timeout_hours=level_config.get('timeout_hours', 48),
            ))
        flow.levels = levels
    
    for key, value in update_data.items():
        if key != 'levels' and value is not None and hasattr(flow, key):
            setattr(flow, key, value)
    
    flow_manager.update_flow(flow)
    
    return {"message": "更新成功"}


@router.delete("/review-flows/{flow_id}", summary="删除审核流程")
async def delete_review_flow(
    flow_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """删除审核流程"""
    from modules.business.knowledge_base.document_review import get_review_flow
    
    flow_manager = get_review_flow()
    
    if not flow_manager.delete_flow(flow_id):
        raise HTTPException(status_code=404, detail="审核流程不存在")
    
    return {"message": "删除成功"}


@router.post("/reviews/submit", summary="提交文档审核")
async def submit_document_review(
    request: ReviewSubmitRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """提交文档进行多级审核"""
    from modules.business.knowledge_base.document_review import get_review_flow
    
    flow_manager = get_review_flow()
    
    record = flow_manager.submit_for_review(
        flow_id=request.flow_id,
        document_id=request.document_id,
        document_type=request.document_type,
        document_title=request.document_title,
        submitter=current_user.username,
        comment=request.comment,
    )
    
    if not record:
        raise HTTPException(status_code=400, detail="提交审核失败，可能已有活跃审核")
    
    return {"id": record.id, "message": "提交成功"}


@router.get("/reviews", summary="获取审核记录列表")
async def get_reviews(
    status: Optional[str] = Query(None, description="状态过滤"),
    flow_id: Optional[str] = Query(None, description="流程ID过滤"),
    submitted_by: Optional[str] = Query(None, description="提交人过滤"),
    document_type: Optional[str] = Query(None, description="文档类型过滤"),
    limit: int = Query(100, le=1000),
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取审核记录列表"""
    from modules.business.knowledge_base.document_review import get_review_flow, ReviewStatus
    
    flow_manager = get_review_flow()
    
    status_enum = None
    if status:
        try:
            status_enum = ReviewStatus(status)
        except ValueError:
            pass
    
    reviews = flow_manager.list_reviews(
        status=status_enum,
        flow_id=flow_id,
        submitted_by=submitted_by,
        document_type=document_type,
        limit=limit,
    )
    
    return {
        "items": [r.to_dict() for r in reviews],
        "total": len(reviews),
    }


@router.get("/reviews/{review_id}", summary="获取审核记录详情")
async def get_review_detail(
    review_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取审核记录详情"""
    from modules.business.knowledge_base.document_review import get_review_flow
    
    flow_manager = get_review_flow()
    record = flow_manager.get_review(review_id)
    
    if not record:
        raise HTTPException(status_code=404, detail="审核记录不存在")
    
    return record.to_dict()


@router.post("/reviews/{review_id}/approve", summary="批准审核")
async def approve_review(
    review_id: str,
    comment: str = Query("", description="审核意见"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """批准当前审核级别或完成审核"""
    from modules.business.knowledge_base.document_review import get_review_flow
    
    flow_manager = get_review_flow()
    
    if not flow_manager.approve(review_id, current_user.username, comment):
        raise HTTPException(status_code=400, detail="批准失败")
    
    return {"message": "批准成功"}


@router.post("/reviews/{review_id}/reject", summary="拒绝审核")
async def reject_review(
    review_id: str,
    comment: str = Query("", description="拒绝原因"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """拒绝审核"""
    from modules.business.knowledge_base.document_review import get_review_flow
    
    flow_manager = get_review_flow()
    
    if not flow_manager.reject(review_id, current_user.username, comment):
        raise HTTPException(status_code=400, detail="拒绝失败")
    
    return {"message": "拒绝成功"}


@router.post("/reviews/{review_id}/request-revision", summary="要求修订")
async def request_revision(
    review_id: str,
    comment: str = Query("", description="修订说明"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """要求提交人修订文档"""
    from modules.business.knowledge_base.document_review import get_review_flow
    
    flow_manager = get_review_flow()
    
    if not flow_manager.request_revision(review_id, current_user.username, comment):
        raise HTTPException(status_code=400, detail="操作失败")
    
    return {"message": "已要求修订"}


@router.post("/reviews/{review_id}/withdraw", summary="撤回审核")
async def withdraw_review(
    review_id: str,
    comment: str = Query("", description="撤回说明"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """撤回审核提交"""
    from modules.business.knowledge_base.document_review import get_review_flow
    
    flow_manager = get_review_flow()
    
    if not flow_manager.withdraw(review_id, current_user.username, comment):
        raise HTTPException(status_code=400, detail="撤回失败")
    
    return {"message": "撤回成功"}


@router.post("/reviews/{review_id}/resubmit", summary="重新提交审核")
async def resubmit_review(
    review_id: str,
    comment: str = Query("", description="重新提交说明"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """修订后重新提交审核"""
    from modules.business.knowledge_base.document_review import get_review_flow
    
    flow_manager = get_review_flow()
    
    if not flow_manager.resubmit(review_id, current_user.username, comment):
        raise HTTPException(status_code=400, detail="重新提交失败")
    
    return {"message": "重新提交成功"}


@router.get("/reviews/pending", summary="获取待审核列表")
async def get_pending_reviews(
    reviewer_role: Optional[str] = Query(None, description="审核人角色"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取当前用户待审核的文档列表"""
    from modules.business.knowledge_base.document_review import get_review_flow
    
    flow_manager = get_review_flow()
    pending = flow_manager.get_pending_reviews(reviewer_role)
    
    return {
        "items": [r.to_dict() for r in pending],
        "total": len(pending),
    }


# ============== 知识图谱接口 (P2-20) ==============

class GraphNodeCreate(BaseModel):
    """创建图节点"""
    label: str = Field(..., description="节点标签")
    properties: dict = Field(default_factory=dict, description="节点属性")


class GraphRelCreate(BaseModel):
    """创建图关系"""
    start_node_id: str = Field(..., description="起始节点ID")
    end_node_id: str = Field(..., description="终止节点ID")
    rel_type: str = Field(..., description="关系类型")
    properties: dict = Field(default_factory=dict, description="关系属性")
    weight: float = Field(1.0, description="关系权重")


class GraphSimilarityQuery(BaseModel):
    """图谱相似度查询"""
    case_id: int = Field(..., description="故障案例ID")
    max_depth: int = Field(3, description="最大遍历深度")
    limit: int = Field(10, description="返回结果数量")


@router.get("/graph/stats", summary="图谱统计")
async def get_graph_stats(
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取知识图谱统计信息"""
    kg = get_knowledge_graph()
    return kg.stats()


@router.post("/graph/build", summary="构建筑识图谱")
async def build_graph(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    从数据库中的故障案例、告警等数据构建筑识图谱
    节点：故障案例、设备、告警
    关系：案例-设备、案例-告警、案例-相似案例
    """
    kg = get_knowledge_graph()
    result = kg.build_graph_from_cases(db)
    return {
        "message": "图谱构建完成",
        **result,
        "graph_stats": kg.stats(),
    }


@router.post("/graph/nodes", summary="创建图节点")
async def create_graph_node(
    node: GraphNodeCreate,
    current_user: CurrentUser = Depends(get_current_user),
):
    """创建知识图谱节点"""
    kg = get_knowledge_graph()
    created = kg.graph.create_node(label=node.label, properties=node.properties)
    return {"node": created.to_dict()}


@router.get("/graph/nodes", summary="查询图节点")
async def query_graph_nodes(
    label: Optional[str] = Query(None, description="节点标签过滤"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """按标签查询图节点"""
    kg = get_knowledge_graph()
    nodes = kg.graph.find_nodes(label=label or "FaultCase", limit=100)
    return {"nodes": [n.to_dict() for n in nodes], "total": len(nodes)}


@router.post("/graph/relationships", summary="创建图关系")
async def create_graph_relationship(
    rel: GraphRelCreate,
    current_user: CurrentUser = Depends(get_current_user),
):
    """创建知识图谱关系"""
    kg = get_knowledge_graph()
    created = kg.graph.create_relationship(
        start_node_id=rel.start_node_id,
        end_node_id=rel.end_node_id,
        rel_type=rel.rel_type,
        properties=rel.properties,
        weight=rel.weight,
    )
    if not created:
        raise HTTPException(status_code=400, detail="创建关系失败，节点可能不存在")
    return {"relationship": created.to_dict()}


@router.get("/graph/case/{case_id}/similar", summary="图谱相似案例查询")
async def get_graph_similar_cases(
    case_id: int,
    max_depth: int = Query(3, description="遍历深度"),
    limit: int = Query(10, description="返回数量"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    基于知识图谱查找与指定案例相似的其他案例
    使用 BFS 遍历 + 相似度传播算法
    """
    kg = get_knowledge_graph()
    similar = kg.find_similar_cases(
        case_id=case_id,
        max_depth=max_depth,
        limit=limit,
    )
    return {
        "case_id": case_id,
        "similar_cases": similar,
        "total": len(similar),
    }


@router.get("/graph/case/{case_id}/context", summary="案例图谱上下文")
async def get_case_graph_context(
    case_id: int,
    depth: int = Query(2, description="查询深度"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取案例的完整图谱上下文（周围节点和关系）"""
    kg = get_knowledge_graph()
    context = kg.get_case_graph_context(case_id=case_id, depth=depth)
    return context


@router.get("/graph/path/{case_a_id}/{case_b_id}", summary="两案例关联路径")
async def get_path_between_cases(
    case_a_id: int,
    case_b_id: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    """查找两个故障案例之间的关联路径"""
    kg = get_knowledge_graph()
    path = kg.find_path_between_cases(case_a_id, case_b_id)
    if path is None:
        return {"path": None, "message": "两点之间无关联路径"}
    return {"path": path}
