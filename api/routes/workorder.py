"""
工单管理API路由
提供工单创建、查询、审批、处理等接口
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.dependencies import get_db, get_current_user, CurrentUser, PaginationParams, require_role
from modules.foundation.db_models.workorder import (
    WorkOrder, WorkOrderFlow, WorkOrderType, WorkOrderStatus, WorkOrderPriority
)
from modules.business.workorder.workorder import WorkOrderCore
from modules.business.report_generator.excel_exporter import WorkOrderExporter, ExportFormat
from core.config.constants import MAX_EXPORT_RECORDS

router = APIRouter()


# ============== 请求/响应模型 ==============

class WorkOrderCreate(BaseModel):
    """创建工单请求"""
    order_type: str = Field("fault", description="工单类型: fault, change, inspection, security, demand, question")
    title: str = Field(..., max_length=256, description="工单标题")
    description: Optional[str] = Field(None, description="工单描述")
    priority: str = Field("P3", description="优先级: P1, P2, P3, P4")
    device_id: Optional[int] = Field(None, description="关联设备ID")
    device_name: Optional[str] = Field(None, description="关联设备名称")
    device_ip: Optional[str] = Field(None, description="关联设备IP")
    assignee: Optional[str] = Field(None, description="处理人")
    expected_end: Optional[datetime] = Field(None, description="期望完成时间")
    impact: Optional[str] = Field(None, description="影响范围")
    tags: Optional[str] = Field(None, description="标签")
    attachments: Optional[List[dict]] = Field(None, description="附件列表")


class WorkOrderUpdate(BaseModel):
    """更新工单请求"""
    title: Optional[str] = Field(None, max_length=256)
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assignee: Optional[str] = None
    expected_end: Optional[datetime] = None
    tags: Optional[str] = None
    resolution: Optional[str] = None
    root_cause: Optional[str] = None
    improvement: Optional[str] = None


class WorkOrderFlowCreate(BaseModel):
    """创建工单流程记录"""
    action: str = Field(..., description="操作: assign, approve, reject, resolve, close, cancel")
    comment: Optional[str] = Field(None, description="意见/备注")
    to_status: Optional[str] = Field(None, description="新状态")


class WorkOrderDraftSave(BaseModel):
    """保存工单草稿请求"""
    draft_id: Optional[str] = Field(None, description="草稿ID(更新时传入)")
    order_type: Optional[str] = Field(None, description="工单类型")
    title: Optional[str] = Field(None, description="标题")
    description: Optional[str] = Field(None, description="描述")
    priority: Optional[str] = Field("P3", description="优先级")
    device_id: Optional[int] = Field(None, description="设备ID")
    device_name: Optional[str] = Field(None, description="设备名称")
    device_ip: Optional[str] = Field(None, description="设备IP")
    assignee: Optional[str] = Field(None, description="处理人")
    expected_end: Optional[datetime] = Field(None, description="期望完成时间")
    impact: Optional[str] = Field(None, description="影响范围")
    tags: Optional[List[str]] = Field(None, description="标签")
    attachments: Optional[List[dict]] = Field(None, description="附件")
    is_auto_save: bool = Field(False, description="是否自动保存")


class WorkOrderResponse(BaseModel):
    """工单响应"""
    id: int
    order_no: str
    order_type: str
    priority: str
    title: str
    description: Optional[str] = None
    status: str
    device_name: Optional[str] = None
    device_ip: Optional[str] = None
    creator: str
    assignee: Optional[str] = None
    created_at: datetime
    updated_at: datetime


def _build_workorder_core(db: Session) -> WorkOrderCore:
    """构建工单核心实例"""
    return WorkOrderCore(db)


def _map_order_type(order_type: str) -> WorkOrderType:
    """映射工单类型字符串到枚举"""
    mapping = {
        'fault': WorkOrderType.FAULT,
        'change': WorkOrderType.CHANGE,
        'inspection': WorkOrderType.INSPECTION,
        'security': WorkOrderType.SECURITY,
        'demand': WorkOrderType.DEMAND,
        'question': WorkOrderType.QUESTION,
        'other': WorkOrderType.OTHER,
    }
    return mapping.get(order_type, WorkOrderType.OTHER)


def _map_priority(priority: str) -> WorkOrderPriority:
    """映射优先级字符串到枚举"""
    mapping = {
        'P1': WorkOrderPriority.P1,
        'P2': WorkOrderPriority.P2,
        'P3': WorkOrderPriority.P3,
        'P4': WorkOrderPriority.P4,
    }
    return mapping.get(priority, WorkOrderPriority.P3)


def _map_status(status: str) -> WorkOrderStatus:
    """映射状态字符串到枚举"""
    mapping = {
        'pending': WorkOrderStatus.PENDING,
        'processing': WorkOrderStatus.PROCESSING,
        'pending_approval': WorkOrderStatus.PENDING_APPROVAL,
        'approved': WorkOrderStatus.APPROVED,
        'rejected': WorkOrderStatus.REJECTED,
        'resolved': WorkOrderStatus.RESOLVED,
        'closed': WorkOrderStatus.CLOSED,
        'cancelled': WorkOrderStatus.CANCELLED,
    }
    return mapping.get(status, WorkOrderStatus.PENDING)


def _workorder_to_dict(wo: WorkOrder) -> dict:
    """工单模型转字典"""
    return {
        'id': wo.id,
        'order_no': wo.order_no,
        'order_type': wo.order_type.value if wo.order_type else None,
        'priority': wo.priority.value if wo.priority else None,
        'title': wo.title,
        'description': wo.description,
        'status': wo.status.value if wo.status else None,
        'device_id': wo.device_id,
        'device_name': wo.device_name,
        'device_ip': wo.device_ip,
        'creator': wo.creator,
        'assignee': wo.assignee,
        'created_at': wo.created_at.isoformat() if wo.created_at else None,
        'updated_at': wo.updated_at.isoformat() if wo.updated_at else None,
    }


# ============== 工单接口 ==============

@router.get("", summary="获取工单列表")
@router.get("/", summary="获取工单列表")
async def get_workorders(
    status_filter: Optional[str] = Query(None, alias="status", description="状态过滤"),
    order_type: Optional[str] = Query(None, description="工单类型过滤"),
    priority: Optional[str] = Query(None, description="优先级过滤"),
    assignee: Optional[str] = Query(None, description="处理人过滤"),
    creator: Optional[str] = Query(None, description="创建人过滤"),
    device_id: Optional[int] = Query(None, description="设备ID过滤"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    start_date: Optional[datetime] = Query(None, description="创建时间开始"),
    end_date: Optional[datetime] = Query(None, description="创建时间结束"),
    pagination: PaginationParams = Depends(PaginationParams),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取工单列表
    支持多条件过滤和分页
    """
    core = _build_workorder_core(db)
    
    # 映射过滤参数
    status_enum = _map_status(status_filter) if status_filter else None
    type_enum = _map_order_type(order_type) if order_type else None
    priority_enum = _map_priority(priority) if priority else None
    
    # 查询工单列表
    workorders, total = core.list(
        status=status_enum,
        order_type=type_enum,
        priority=priority_enum,
        creator=creator,
        assignee=assignee,
        start_time=start_date,
        end_time=end_date,
        page=pagination.page,
        page_size=pagination.page_size
    )
    
    return {
        "items": [_workorder_to_dict(wo) for wo in workorders],
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
    }


@router.get("/export", summary="导出工单")
async def export_workorders(
    status: Optional[str] = Query(None, description="状态过滤"),
    priority: Optional[str] = Query(None, description="优先级过滤"),
    start_date: Optional[datetime] = Query(None, description="创建时间开始"),
    end_date: Optional[datetime] = Query(None, description="创建时间结束"),
    format: Optional[str] = Query("excel", description="导出格式: excel/csv"),
    current_user: CurrentUser = Depends(require_role("admin", "operator")),
    db: Session = Depends(get_db),
):
    """
    导出工单到Excel或CSV文件
    支持按状态、优先级、时间范围过滤
    仅限 admin 和 operator 角色
    """
    core = _build_workorder_core(db)
    
    # 映射过滤参数
    status_enum = _map_status(status) if status else None
    priority_enum = _map_priority(priority) if priority else None
    
    # 查询工单列表 (不分页，获取所有)
    workorders, total = core.list(
        status=status_enum,
        priority=priority_enum,
        start_time=start_date,
        end_time=end_date,
        page=1,
        page_size=MAX_EXPORT_RECORDS  # 最大导出条数
    )
    
    if not workorders:
        return {"data": [], "code": 0, "message": "没有可导出的工单"}
    
    # 转换为字典
    workorder_dicts = [_workorder_to_dict(wo) for wo in workorders]
    
    # 导出
    exporter = WorkOrderExporter()
    export_format = ExportFormat.CSV if format == 'csv' else ExportFormat.XLSX
    
    file_bytes, content_type = exporter.export(workorder_dicts, format=export_format)
    
    from fastapi.responses import StreamingResponse
    import io
    
    filename = f"workorders_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if format == 'csv':
        filename += ".csv"
        media_type = "text/csv; charset=utf-8-sig"
    else:
        filename += ".xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )


@router.get("/export/{workorder_id}", summary="导出单个工单")
async def export_single_workorder(
    workorder_id: int,
    format: Optional[str] = Query("excel", description="导出格式: excel/csv"),
    current_user: CurrentUser = Depends(require_role("admin", "operator")),
    db: Session = Depends(get_db),
):
    """
    导出单个工单到Excel或CSV文件
    仅限 admin 和 operator 角色
    """
    core = _build_workorder_core(db)
    
    # 获取工单
    wo = core.get_by_id(workorder_id)
    if not wo:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    # 转换为字典
    wo_dict = _workorder_to_dict(wo)
    
    # 导出
    exporter = WorkOrderExporter()
    export_format = ExportFormat.CSV if format == 'csv' else ExportFormat.XLSX
    
    file_bytes, content_type = exporter.export_single(wo_dict, format=export_format)
    
    from fastapi.responses import StreamingResponse
    import io
    
    filename = f"workorder_{wo.order_no}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if format == 'csv':
        filename += ".csv"
        media_type = "text/csv; charset=utf-8-sig"
    else:
        filename += ".xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )


@router.post("/", summary="创建工单")
async def create_workorder(
    workorder: WorkOrderCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    创建新的工单
    自动生成工单编号
    """
    core = _build_workorder_core(db)
    
    # 创建工单
    wo = core.create(
        title=workorder.title,
        order_type=_map_order_type(workorder.order_type),
        creator=current_user.username,
        description=workorder.description,
        priority=_map_priority(workorder.priority),
        device_id=workorder.device_id,
        device_name=workorder.device_name,
        device_ip=workorder.device_ip,
        assignee=workorder.assignee,
        expected_end=workorder.expected_end,
        impact=workorder.impact,
        tags=workorder.tags.split(',') if workorder.tags else None,
        attachments=workorder.attachments,
    )
    
    return _workorder_to_dict(wo)


# ============== 工单辅助接口（必须在 /{workorder_id} 之前定义）==============

@router.get("/categories", summary="获取工单分类列表")
async def get_workorder_categories(
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取工单分类列表"""
    return {
        "items": [
            {"id": 1, "name": "故障处理", "code": "fault", "count": 0},
            {"id": 2, "name": "变更申请", "code": "change", "count": 0},
            {"id": 3, "name": "数据处理", "code": "data", "count": 0},
            {"id": 4, "name": "权限申请", "code": "permission", "count": 0},
            {"id": 5, "name": "其他", "code": "other", "count": 0},
        ]
    }


@router.get("/priorities", summary="获取工单优先级列表")
async def get_workorder_priorities(
    current_user: CurrentUser = Depends(get_current_user),
):
    """获取工单优先级列表"""
    return {
        "items": [
            {"id": 1, "name": "P1 - 紧急", "code": "P1", "level": 1, "color": "red"},
            {"id": 2, "name": "P2 - 高", "code": "P2", "level": 2, "color": "orange"},
            {"id": 3, "name": "P3 - 中", "code": "P3", "level": 3, "color": "blue"},
            {"id": 4, "name": "P4 - 低", "code": "P4", "level": 4, "color": "green"},
        ]
    }


@router.get("/stats/summary", summary="获取工单统计摘要")
async def get_workorder_stats(
    start_date: Optional[datetime] = Query(None, description="统计开始日期"),
    end_date: Optional[datetime] = Query(None, description="统计结束日期"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取工单统计摘要"""
    core = _build_workorder_core(db)
    
    # 统计各状态工单数量
    workorders, total = core.list(page=1, page_size=MAX_EXPORT_RECORDS)
    
    stats = {
        'total': total,
        'pending': 0,
        'processing': 0,
        'resolved': 0,
        'closed': 0,
        'by_priority': {'P1': 0, 'P2': 0, 'P3': 0, 'P4': 0},
        'by_type': {'fault': 0, 'change': 0, 'inspection': 0, 'security': 0, 'demand': 0, 'question': 0, 'other': 0},
    }
    
    for wo in workorders:
        if wo.status == WorkOrderStatus.PENDING:
            stats['pending'] += 1
        elif wo.status == WorkOrderStatus.PROCESSING:
            stats['processing'] += 1
        elif wo.status == WorkOrderStatus.RESOLVED:
            stats['resolved'] += 1
        elif wo.status == WorkOrderStatus.CLOSED:
            stats['closed'] += 1
            
        if wo.priority:
            stats['by_priority'][wo.priority.value] = stats['by_priority'].get(wo.priority.value, 0) + 1
        
        if wo.order_type:
            stats['by_type'][wo.order_type.value] = stats['by_type'].get(wo.order_type.value, 0) + 1
    
    return stats


@router.get("/stats/trend", summary="获取工单趋势")
async def get_workorder_trend(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取工单趋势数据"""
    from datetime import timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    core = _build_workorder_core(db)
    workorders, _ = core.list(start_time=start_date, end_time=end_date, page=1, page_size=MAX_EXPORT_RECORDS)
    
    # 按日期分组
    dates_set = set()
    created_dict = {}
    resolved_dict = {}
    
    for wo in workorders:
        if wo.created_at:
            date_str = wo.created_at.strftime('%Y-%m-%d')
            dates_set.add(date_str)
            created_dict[date_str] = created_dict.get(date_str, 0) + 1
        
        if wo.status == WorkOrderStatus.RESOLVED and wo.updated_at:
            date_str = wo.updated_at.strftime('%Y-%m-%d')
            dates_set.add(date_str)
            resolved_dict[date_str] = resolved_dict.get(date_str, 0) + 1
        elif wo.status == WorkOrderStatus.CLOSED and wo.updated_at:
            date_str = wo.updated_at.strftime('%Y-%m-%d')
            dates_set.add(date_str)
            resolved_dict[date_str] = resolved_dict.get(date_str, 0) + 1
    
    dates = sorted(list(dates_set))
    created = [created_dict.get(d, 0) for d in dates]
    resolved = [resolved_dict.get(d, 0) for d in dates]
    
    return {
        "dates": dates,
        "created": created,
        "resolved": resolved,
    }


# ============== 工单详情接口 ==============

@router.get("/{workorder_id}", summary="获取工单详情")
async def get_workorder(
    workorder_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取工单的详细信息"""
    core = _build_workorder_core(db)
    wo = core.get_by_id(workorder_id)
    
    if not wo:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    return _workorder_to_dict(wo)


@router.put("/{workorder_id}/draft", summary="保存工单草稿")
async def save_workorder_draft(
    workorder_id: int,
    draft: WorkOrderDraftSave,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    保存工单草稿(WKO-008)
    
    - 不更新updated_at
    - 不记录操作历史
    - 状态保持draft
    - 只更新: title, description, priority, draft_data, draft_saved_at
    """
    core = _build_workorder_core(db)
    
    # 获取工单
    wo = core.get_by_id(workorder_id)
    if not wo:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    # 草稿保存只更新指定字段
    if draft.title is not None:
        wo.title = draft.title
    if draft.description is not None:
        wo.description = draft.description
    if draft.priority is not None:
        wo.priority = _map_priority(draft.priority)
    
    # 构建草稿数据快照
    draft_data = {
        'order_type': draft.order_type or (wo.order_type.value if wo.order_type else None),
        'title': draft.title if draft.title is not None else wo.title,
        'description': draft.description if draft.description is not None else wo.description,
        'priority': draft.priority if draft.priority is not None else (wo.priority.value if wo.priority else 'P3'),
        'device_id': draft.device_id if draft.device_id is not None else wo.device_id,
        'device_name': draft.device_name if draft.device_name is not None else wo.device_name,
        'device_ip': draft.device_ip if draft.device_ip is not None else wo.device_ip,
        'assignee': draft.assignee if draft.assignee is not None else wo.assignee,
        'expected_end': draft.expected_end.isoformat() if draft.expected_end else (wo.expected_end.isoformat() if wo.expected_end else None),
        'impact': draft.impact if draft.impact is not None else wo.impact,
        'tags': draft.tags if draft.tags is not None else (wo.tags.split(',') if wo.tags else []),
        'attachments': draft.attachments if draft.attachments is not None else [],
    }
    
    wo.draft_data = draft_data
    wo.draft_saved_at = datetime.now()
    
    # 注意：不更新updated_at，不记录操作历史
    
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="草稿保存失败")
    
    return {
        "code": 0,
        "message": "草稿保存成功",
        "data": _workorder_to_dict(wo)
    }


@router.put("/{workorder_id}", summary="更新工单")
async def update_workorder(
    workorder_id: int,
    workorder: WorkOrderUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新工单信息"""
    core = _build_workorder_core(db)
    
    # 构建更新数据
    update_data = {}
    if workorder.title is not None:
        update_data['title'] = workorder.title
    if workorder.description is not None:
        update_data['description'] = workorder.description
    if workorder.priority is not None:
        update_data['priority'] = _map_priority(workorder.priority)
    if workorder.status is not None:
        update_data['status'] = _map_status(workorder.status)
    if workorder.assignee is not None:
        update_data['assignee'] = workorder.assignee
    if workorder.expected_end is not None:
        update_data['expected_end'] = workorder.expected_end
    if workorder.tags is not None:
        update_data['tags'] = workorder.tags
    if workorder.resolution is not None:
        update_data['resolution'] = workorder.resolution
    if workorder.root_cause is not None:
        update_data['root_cause'] = workorder.root_cause
    if workorder.improvement is not None:
        update_data['improvement'] = workorder.improvement
    
    if not update_data:
        raise HTTPException(status_code=400, detail="没有需要更新的字段")
    
    success = core.update(workorder_id, operator=current_user.username, **update_data)
    
    if not success:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    return {"status": "success", "message": "工单更新成功"}


@router.delete("/{workorder_id}", summary="删除工单")
async def delete_workorder(
    workorder_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    删除工单（软删除）
    仅管理员或创建人可以删除
    """
    core = _build_workorder_core(db)
    
    # 获取工单检查权限
    wo = core.get_by_id(workorder_id)
    if not wo:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    # 只有管理员或创建人可以删除
    if not current_user.is_admin() and wo.creator != current_user.username:
        raise HTTPException(status_code=403, detail="无权限删除此工单")
    
    success = core.delete(workorder_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    return {"status": "success", "message": "工单删除成功"}


# ============== 工单流程接口 ==============

@router.get("/{workorder_id}/approval-flow", summary="获取工单审批流程图")
async def get_workorder_approval_flow(
    workorder_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取工单审批流程图数据
    返回按时间排序的审批节点列表，包含状态、审批人、操作、意见等
    """
    # 验证工单存在
    core = _build_workorder_core(db)
    wo = core.get_by_id(workorder_id)
    if not wo:
        raise HTTPException(status_code=404, detail="工单不存在")

    # 获取所有流程记录（WorkOrderFlow）
    flows = db.query(WorkOrderFlow).filter(
        WorkOrderFlow.work_order_id == workorder_id
    ).order_by(WorkOrderFlow.created_at.asc()).all()

    # 状态到中文的映射
    status_labels = {
        'pending': '待处理',
        'processing': '处理中',
        'pending_approval': '待审批',
        'approved': '已批准',
        'rejected': '已拒绝',
        'resolved': '已解决',
        'closed': '已关闭',
        'cancelled': '已取消',
    }

    # 操作到图标的映射
    action_icons = {
        'assign': '👤',
        'approve': '✅',
        'reject': '❌',
        'resolve': '🔧',
        'close': '🔒',
        'cancel': '🚫',
        'submit': '📤',
        'create': '🆕',
    }

    # 构建节点列表
    nodes = []

    # 起始节点：工单创建
    wo_order_type = wo.order_type.value if hasattr(wo.order_type, 'value') else (wo.order_type or 'fault')
    wo_status = wo.status.value if hasattr(wo.status, 'value') else (wo.status or 'pending')
    nodes.append({
        'node_id': 'start',
        'type': 'start',
        'title': '工单创建',
        'status': 'pending',
        'status_label': '已创建',
        'operator': wo.creator or '系统',
        'action': 'create',
        'action_icon': '🆕',
        'comment': (wo.description or '')[:200],
        'created_at': wo.created_at.isoformat() if wo.created_at else None,
        'is_current': False,
    })

    # 合并 flows 和 approval_records
    approval_records = []
    try:
        from modules.business.workorder.approval import ApprovalRecord
        approval_records = db.query(ApprovalRecord).filter(
            ApprovalRecord.work_order_id == workorder_id
        ).order_by(ApprovalRecord.created_at.asc()).all()
    except Exception:
        pass  # 表可能不存在

    # 用字典按时间线合并
    timeline = []
    for f in flows:
        timeline.append({
            'ts': f.created_at,
            'source': 'flow',
            'data': f,
        })
    for ar in approval_records:
        timeline.append({
            'ts': ar.created_at,
            'source': 'approval',
            'data': ar,
        })

    # 按时间排序
    timeline.sort(key=lambda x: x['ts'] or 0)

    current_status = wo_status
    current_node_id = None

    for item in timeline:
        d = item['data']
        if item['source'] == 'flow':
            action = d.action or ''
            from_s = d.from_status or ''
            to_s = d.to_status or ''
            operator = d.operator or '系统'
            comment = d.comment or ''
            ts = d.created_at

            node_type = 'process'
            if action in ('approve', 'reject'):
                node_type = 'approval'
            elif action in ('resolve', 'close'):
                node_type = 'complete'

            nodes.append({
                'node_id': f'flow_{d.id}',
                'type': node_type,
                'title': d.step_name or f'流程节点 #{d.id}',
                'status': to_s,
                'status_label': status_labels.get(to_s, to_s),
                'operator': operator,
                'action': action,
                'action_icon': action_icons.get(action, '➡️'),
                'comment': comment[:200] if comment else '',
                'from_status': from_s,
                'to_status': to_s,
                'created_at': ts.isoformat() if ts else None,
                'is_current': to_s == current_status,
            })

            if to_s == current_status:
                current_node_id = f'flow_{d.id}'

        elif item['source'] == 'approval':
            node_type = 'approval'
            if d.status == 'approved':
                node_type = 'approval_done'
            elif d.status == 'rejected':
                node_type = 'approval_rejected'

            nodes.append({
                'node_id': f'approval_{d.id}',
                'type': node_type,
                'title': f'审批节点 #{d.id}',
                'status': d.status,
                'status_label': {'pending': '待审批', 'approved': '已批准', 'rejected': '已拒绝',
                                 'cancelled': '已取消', 'timeout': '已超时', 'delegated': '已委托'}.get(d.status, d.status),
                'operator': d.approver or '未知',
                'approver_role': d.approver_role or '',
                'action': d.action or 'approve',
                'action_icon': '✅' if d.status == 'approved' else ('❌' if d.status == 'rejected' else '⏳'),
                'comment': d.comment or '',
                'mode': d.mode or '',
                'created_at': d.created_at.isoformat() if d.created_at else None,
                'completed_at': d.completed_at.isoformat() if d.completed_at else None,
                'expires_at': d.expires_at.isoformat() if d.expires_at else None,
                'is_current': d.status == 'pending',
            })

            if d.status == 'pending':
                current_node_id = f'approval_{d.id}'

    # 终止节点
    end_status = wo_status
    end_types = {
        'closed': 'end_resolved',
        'cancelled': 'end_cancelled',
        'rejected': 'end_rejected',
    }
    nodes.append({
        'node_id': 'end',
        'type': end_types.get(end_status, 'end'),
        'title': '流程结束',
        'status': end_status,
        'status_label': status_labels.get(end_status, end_status),
        'operator': '',
        'action': 'end',
        'action_icon': '🏁',
        'comment': '',
        'created_at': wo.updated_at.isoformat() if wo.updated_at else None,
        'is_current': end_status in ('closed', 'cancelled', 'rejected'),
    })

    # 找出当前节点
    for node in nodes:
        if node['is_current'] and node['node_id'] != 'start' and node['node_id'] != 'end':
            current_node_id = node['node_id']

    # 工作流配置（从工单类型获取默认步骤）
    workflow_steps = {
        'fault': ['创建', '处理中', '待审批', '已批准', '已解决', '已关闭'],
        'change': ['创建', '评估', '待审批', '已批准', '实施', '已关闭'],
        'inspection': ['创建', '处理中', '待审批', '已批准', '已解决', '已关闭'],
        'security': ['创建', '评估', '待审批', '已批准', '处理', '已关闭'],
    }

    return {
        'workorder_id': workorder_id,
        'workorder_no': wo.order_no or '',
        'current_status': current_status,
        'current_node_id': current_node_id,
        'workorder_type': wo_order_type,
        'workflow_steps': workflow_steps.get(wo_order_type, workflow_steps['fault']),
        'nodes': nodes,
    }


@router.get("/{workorder_id}/flows", summary="获取工单流程历史")
async def get_workorder_flows(
    workorder_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取工单的处理流程历史"""
    flows = db.query(WorkOrderFlow).filter(
        WorkOrderFlow.work_order_id == workorder_id
    ).order_by(WorkOrderFlow.created_at.asc()).all()
    
    return {
        "items": [
            {
                "id": f.id,
                "step_name": f.step_name,
                "action": f.action,
                "from_status": f.from_status,
                "to_status": f.to_status,
                "operator": f.operator,
                "comment": f.comment,
                "created_at": f.created_at.isoformat() if f.created_at else None,
            }
            for f in flows
        ]
    }


@router.post("/{workorder_id}/flows", summary="添加工单流程记录")
async def create_workorder_flow(
    workorder_id: int,
    flow: WorkOrderFlowCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    添加工单流程记录
    包括状态变更、审批、操作等
    """
    # 验证工单存在
    core = _build_workorder_core(db)
    wo = core.get_by_id(workorder_id)
    if not wo:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    # 映射action到状态
    action_to_status = {
        'assign': WorkOrderStatus.PROCESSING,
        'approve': WorkOrderStatus.APPROVED,
        'reject': WorkOrderStatus.REJECTED,
        'resolve': WorkOrderStatus.RESOLVED,
        'close': WorkOrderStatus.CLOSED,
        'cancel': WorkOrderStatus.CANCELLED,
    }
    
    new_status = action_to_status.get(flow.action, flow.to_status)
    
    # 创建流程记录
    wo_flow = WorkOrderFlow(
        work_order_id=workorder_id,
        step_name=_get_step_name(flow.action),
        action=flow.action,
        from_status=wo.status.value if wo.status else None,
        to_status=new_status.value if isinstance(new_status, WorkOrderStatus) else new_status,
        operator=current_user.username,
        comment=flow.comment,
    )
    
    db.add(wo_flow)
    
    # 更新工单状态
    if new_status:
        wo.status = new_status if isinstance(new_status, WorkOrderStatus) else _map_status(new_status)
    
    db.commit()
    
    return {
        "id": wo_flow.id,
        "workorder_id": workorder_id,
        "action": flow.action,
        "operator": current_user.username,
        "created_at": wo_flow.created_at.isoformat() if wo_flow.created_at else None,
    }


def _get_step_name(action: str) -> str:
    """获取步骤名称"""
    names = {
        'create': '创建工单',
        'assign': '分配处理人',
        'approve': '审批通过',
        'reject': '审批拒绝',
        'resolve': '解决工单',
        'close': '关闭工单',
        'cancel': '取消工单',
    }
    return names.get(action, action)


# ============== AI分析接口 ==============

@router.post("/analyze/root-cause", summary="AI根因分析")
async def analyze_root_cause(
    title: str = Query(..., description="工单标题"),
    description: Optional[str] = Query(None, description="工单描述"),
    device_info: Optional[str] = Query(None, description="设备信息(JSON)"),
    alert_info: Optional[str] = Query(None, description="告警信息(JSON)"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    AI根因分析
    根据工单信息分析并返回可能的根本原因
    """
    from modules.business.workorder.root_cause import RootCauseAnalyzer
    
    analyzer = RootCauseAnalyzer()
    result = analyzer.analyze(
        title=title,
        description=description or "",
        device_info=device_info,
        alert_info=alert_info
    )
    
    return result.to_dict()


@router.post("/analyze/remediation", summary="AI修复建议")
async def suggest_remediation(
    title: str = Query(..., description="工单标题"),
    description: Optional[str] = Query(None, description="工单描述"),
    root_cause: Optional[str] = Query(None, description="根本原因"),
    category: Optional[str] = Query(None, description="原因分类"),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    AI修复建议
    根据工单信息和根因分析返回修复建议
    """
    from modules.business.workorder.remediation import RemediationAdvisor
    
    advisor = RemediationAdvisor()
    result = advisor.suggest(
        title=title,
        description=description or "",
        root_cause=root_cause,
        category=category
    )
    
    return result.to_dict()


# ============== 工单草稿接口 ==============

class WorkOrderDraftResponse(BaseModel):
    """工单草稿响应"""
    draft_id: str
    user_id: str
    username: str
    order_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    priority: str
    status: str
    created_at: str
    updated_at: str


@router.post("/draft/save", summary="保存工单草稿")
async def save_draft(
    draft: WorkOrderDraftSave,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    保存工单草稿
    支持手动保存和自动保存
    """
    from modules.business.workorder.workorder_draft import WorkOrderDraftManager
    
    draft_manager = WorkOrderDraftManager()
    
    draft_data = draft.dict(exclude_none=True) if draft else {}
    if draft_data.get('is_auto_save'):
        # Auto-save doesn't include certain fields
        draft_data.pop('is_auto_save', None)
    
    draft_id, saved_draft = draft_manager.save_draft(
        user_id=str(current_user.user_id),
        username=current_user.username,
        draft_id=draft.draft_id,
        draft_data=draft_data,
        is_auto_save=draft.is_auto_save
    )
    
    return {
        "status": "success",
        "draft_id": draft_id,
        "message": "草稿保存成功" if not draft.is_auto_save else "自动保存成功",
        "is_auto_save": draft.is_auto_save
    }


@router.get("/draft/list", summary="获取草稿列表")
async def list_drafts(
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    获取当前用户的草稿列表
    """
    from modules.business.workorder.workorder_draft import WorkOrderDraftManager
    
    draft_manager = WorkOrderDraftManager()
    drafts = draft_manager.list_drafts(str(current_user.user_id))
    
    return {
        "items": [d.to_dict() for d in drafts],
        "total": len(drafts)
    }


@router.get("/draft/{draft_id}", summary="获取草稿详情")
async def get_draft(
    draft_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    获取指定草稿的详细信息
    """
    from modules.business.workorder.workorder_draft import WorkOrderDraftManager
    
    draft_manager = WorkOrderDraftManager()
    draft = draft_manager.get_draft(str(current_user.user_id), draft_id)
    
    if not draft:
        raise HTTPException(status_code=404, detail="草稿不存在")
    
    return draft.to_dict()


@router.delete("/draft/{draft_id}", summary="删除草稿")
async def delete_draft(
    draft_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    删除指定的草稿
    """
    from modules.business.workorder.workorder_draft import WorkOrderDraftManager
    
    draft_manager = WorkOrderDraftManager()
    success = draft_manager.delete_draft(str(current_user.user_id), draft_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="草稿不存在")
    
    return {"status": "success", "message": "草稿已删除"}


# ============== SLA管理接口 (WKO-021/022) ==============

@router.get("/{workorder_id}/sla", summary="获取工单SLA状态")
async def get_workorder_sla_status(
    workorder_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取工单的SLA状态(WKO-021)
    
    返回:
    - remaining_seconds: 剩余秒数(负数表示已超时)
    - deadline: 截止时间
    - sla_level: SLA级别(P1-P4)
    - breach_warning: 是否警告
    - is_breached: 是否已超时
    - escalation_level: 当前升级级别(0-4)
    """
    from modules.business.workorder.sla_manager import SLAManager
    
    # 构建SLAManager
    sla_manager = SLAManager(db_session=db)
    
    # 获取工单信息验证存在
    core = _build_workorder_core(db)
    wo = core.get_by_id(workorder_id)
    if not wo:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    # 计算SLA状态
    status = sla_manager.compute_sla_status(workorder_id)
    
    return {"code": 0, "data": status}


@router.post("/{workorder_id}/sla/refresh", summary="刷新SLA状态")
async def refresh_sla_status(
    workorder_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    重新计算SLA状态(WKO-021)
    
    重新计算工单的SLA状态并检查是否需要升级
    """
    from modules.business.workorder.sla_manager import SLAManager
    
    # 构建SLAManager
    sla_manager = SLAManager(db_session=db)
    
    # 获取工单信息验证存在
    core = _build_workorder_core(db)
    wo = core.get_by_id(workorder_id)
    if not wo:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    # 重新计算SLA状态
    status = sla_manager.compute_sla_status(workorder_id)
    
    # 检查并触发升级
    escalations = sla_manager.check_escalation(workorder_id)
    
    return {
        "code": 0,
        "data": {
            "sla_status": status,
            "escalations": escalations
        }
    }


@router.get("/{workorder_id}/sla/history", summary="获取SLA升级历史")
async def get_sla_escalation_history(
    workorder_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取工单的SLA升级历史记录
    """
    from modules.business.workorder.sla_manager import SLAManager
    
    sla_manager = SLAManager(db_session=db)
    
    # 验证工单存在
    core = _build_workorder_core(db)
    wo = core.get_by_id(workorder_id)
    if not wo:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    history = sla_manager.get_escalation_history(workorder_id)
    
    return {"code": 0, "data": history}


@router.post("/{workorder_id}/sla/timer/start", summary="启动SLA计时器")
async def start_sla_timer(
    workorder_id: int,
    sla_type: str = Query("response", description="SLA类型: response/resolve"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    启动SLA计时器(WKO-021)
    
    为工单启动响应或解决SLA计时
    """
    from modules.business.workorder.sla_manager import SLAManager
    
    core = _build_workorder_core(db)
    wo = core.get_by_id(workorder_id)
    
    if not wo:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    sla_manager = SLAManager(db_session=db)
    timer_info = sla_manager.start_sla_timer(
        workorder_id=workorder_id,
        priority=wo.priority.value if wo.priority else 'P3',
        sla_type=sla_type
    )
    
    return {"code": 0, "data": timer_info}


# ============== 旧的SLA接口(兼容) ==============

@router.get("/sla/{workorder_id}", summary="[兼容]获取SLA状态")
async def get_sla_status_old(
    workorder_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    [兼容接口]获取工单的SLA状态
    """
    from modules.business.workorder.sla_manager import SLAManager
    
    sla_manager = SLAManager(db_session=db)
    core = _build_workorder_core(db)
    wo = core.get_by_id(workorder_id)
    
    if not wo:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    status = sla_manager.compute_sla_status(workorder_id)
    
    return {
        "workorder_id": workorder_id,
        "priority": wo.priority.value if wo.priority else 'P3',
        "response": status.get('response_timer'),
        "resolve": status.get('resolve_timer')
    }


@router.get("/sla/summary", summary="[兼容]获取SLA汇总")
async def get_sla_summary_old(
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    [兼容接口]获取SLA状态汇总
    """
    from modules.business.workorder.workorder_draft import SLATracker
    
    sla_tracker = SLATracker()
    summary = sla_tracker.get_sla_summary()
    
    return summary


@router.post("/sla/{workorder_id}/start", summary="[兼容]启动SLA计时")
async def start_sla_timer_old(
    workorder_id: int,
    sla_type: str = Query("response", description="SLA类型: response/resolve"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    [兼容接口]启动SLA计时器
    """
    from modules.business.workorder.workorder_draft import SLATracker
    
    core = _build_workorder_core(db)
    wo = core.get_by_id(workorder_id)
    
    if not wo:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    sla_tracker = SLATracker()
    timer_info = sla_tracker.start_sla_timer(
        workorder_id=workorder_id,
        priority=wo.priority.value if wo.priority else 'P3',
        sla_type=sla_type
    )
    
    return {"status": "success", "timer": timer_info}


# ============== 工单导出接口 ==============

@router.get("/export", summary="导出工单")
async def export_workorders(
    status: Optional[str] = Query(None, description="状态过滤"),
    order_type: Optional[str] = Query(None, description="工单类型"),
    priority: Optional[str] = Query(None, description="优先级"),
    start_date: Optional[datetime] = Query(None, description="创建时间开始"),
    end_date: Optional[datetime] = Query(None, description="创建时间结束"),
    format: Optional[str] = Query("xlsx", description="导出格式: xlsx, csv"),
    current_user: CurrentUser = Depends(require_role("admin", "operator")),
    db: Session = Depends(get_db),
):
    """
    导出工单列表到Excel或CSV
    仅限 admin 和 operator 角色
    """
    from fastapi.responses import Response
    from modules.business.workorder.workorder_export import WorkOrderExporter, ExportFormat
    
    # Query work orders
    core = _build_workorder_core(db)
    
    status_enum = _map_status(status) if status else None
    type_enum = _map_order_type(order_type) if order_type else None
    priority_enum = _map_priority(priority) if priority else None
    
    workorders, total = core.list(
        status=status_enum,
        order_type=type_enum,
        priority=priority_enum,
        start_time=start_date,
        end_time=end_date,
        page=1,
        page_size=10000
    )
    
    # Convert to dict format
    wo_list = []
    for wo in workorders:
        wo_dict = {
            'order_no': wo.order_no,
            'order_type': wo.order_type.value if wo.order_type else None,
            'title': wo.title,
            'priority': wo.priority.value if wo.priority else None,
            'status': wo.status.value if wo.status else None,
            'creator': wo.creator,
            'assignee': wo.assignee,
            'device_name': wo.device_name,
            'device_ip': wo.device_ip,
            'created_at': wo.created_at,
            'updated_at': wo.updated_at,
            'expected_end': wo.expected_end,
            'actual_end': wo.actual_end,
            'sla_response_time': wo.sla_response_time,
            'sla_resolve_time': wo.sla_resolve_time,
            'description': wo.description,
            'resolution': wo.resolution,
            'root_cause': wo.root_cause,
            'improvement': wo.improvement,
            'impact': wo.impact,
            'tags': wo.tags.split(',') if wo.tags else [],
            'closed_at': wo.closed_at,
        }
        
        # Calculate SLA breach
        if wo.sla_resolve_time and wo.created_at:
            resolve_deadline = wo.created_at + timedelta(minutes=wo.sla_resolve_time)
            if wo.status not in [WorkOrderStatus.RESOLVED, WorkOrderStatus.CLOSED]:
                wo_dict['sla_breached'] = datetime.now() > resolve_deadline
            else:
                wo_dict['sla_breached'] = wo.sla_resolved_at and wo.sla_resolved_at > resolve_deadline
        else:
            wo_dict['sla_breached'] = False
        
        wo_list.append(wo_dict)
    
    # Export
    exporter = WorkOrderExporter()
    export_format = ExportFormat.CSV if format == 'csv' else ExportFormat.XLSX
    
    filename = f"workorders_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    file_bytes, content_type = exporter.export(wo_list, filename, export_format)
    
    return Response(
        content=file_bytes,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}.{format}"
        }
    )


# ============== 工单操作接口 ==============

@router.post("/{workorder_id}/assign", summary="分配工单")
async def assign_workorder(
    workorder_id: int,
    assignee: str = Query(..., description="处理人"),
    comment: Optional[str] = Query(None, description="分配说明"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """分配工单给指定处理人"""
    core = _build_workorder_core(db)
    success = core.assign(workorder_id, assignee, current_user.username, comment)
    
    if not success:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    return {"status": "success", "message": f"工单已分配给 {assignee}"}


@router.post("/{workorder_id}/approve", summary="审批工单")
async def approve_workorder(
    workorder_id: int,
    approved: bool = Query(..., description="是否批准"),
    comment: Optional[str] = Query(None, description="审批意见"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """审批工单"""
    core = _build_workorder_core(db)
    
    if approved:
        success = core.approve(workorder_id, current_user.username, comment)
    else:
        success = core.reject(workorder_id, current_user.username, comment)
    
    if not success:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    action = "审批通过" if approved else "审批拒绝"
    return {"status": "success", "message": f"工单{action}"}


@router.post("/{workorder_id}/resolve", summary="解决工单")
async def resolve_workorder(
    workorder_id: int,
    resolution: str = Query(..., description="解决方案"),
    root_cause: Optional[str] = Query(None, description="根本原因"),
    improvement: Optional[str] = Query(None, description="改进措施"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """解决工单"""
    core = _build_workorder_core(db)
    workorder = core.update(
        workorder_id,
        operator=current_user.username,
        status=WorkOrderStatus.RESOLVED,
        resolution=resolution,
        root_cause=root_cause,
        improvement=improvement,
    )

    if not workorder:
        raise HTTPException(status_code=404, detail="工单不存在")

    return {"status": "success", "message": "工单已解决"}


@router.post("/{workorder_id}/close", summary="关闭工单")
async def close_workorder(
    workorder_id: int,
    satisfaction: Optional[int] = Query(None, ge=1, le=5, description="满意度评分"),
    feedback: Optional[str] = Query(None, description="反馈意见"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """关闭工单"""
    core = _build_workorder_core(db)
    success = core.close(workorder_id, current_user.username, satisfaction, feedback)
    
    if not success:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    return {"status": "success", "message": "工单已关闭"}


@router.post("/{workorder_id}/cancel", summary="取消工单")
async def cancel_workorder(
    workorder_id: int,
    reason: str = Query(..., description="取消原因"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """取消工单"""
    core = _build_workorder_core(db)
    success = core.cancel(workorder_id, reason, current_user.username)
    
    if not success:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    return {"status": "success", "message": "工单已取消"}


# ============== 告警转工单接口 =============

class AlertToWorkOrderRequest(BaseModel):
    """告警转工单请求"""
    alert_id: int = Field(..., description="关联的告警ID")
    title: Optional[str] = Field(None, description="工单标题，不填则自动生成")
    priority: Optional[str] = Field("P3", description="优先级: P1, P2, P3, P4")
    order_type: Optional[str] = Field("fault", description="工单类型: fault, change, inspection")


@router.post("/convert-to-workorder", summary="告警转工单")
async def convert_alert_to_workorder(
    request: AlertToWorkOrderRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    将告警转换为工单。
    从告警中提取设备信息、告警级别、描述作为工单初始内容。
    """
    from modules.foundation.db_models.alert import Alert, AlertLevel, AlertStatus

    alert = db.query(Alert).filter(Alert.id == request.alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"告警 {request.alert_id} 不存在")

    # 自动生成标题
    title = request.title or f"[告警转工单] {alert.title or '未知告警'} (ID:{alert.id})"

    # 根据告警级别映射优先级
    priority_map = {"critical": "P1", "high": "P1", "medium": "P2", "low": "P3", "info": "P4"}
    alert_level_str = str(alert.level.value) if hasattr(alert.level, 'value') else str(alert.level or 'medium')
    priority = request.priority or priority_map.get(alert_level_str.lower(), "P3")

    # 构建工单描述
    description = (
        f"## 来源告警信息\n"
        f"- 告警ID: {alert.id}\n"
        f"- 告警名称: {alert.title or '未知'}\n"
        f"- 告警级别: {alert_level_str}\n"
        f"- 告警状态: {alert.status or '未知'}\n"
        f"- 告警时间: {alert.created_at or '未知'}\n"
        f"- 设备名称: {getattr(alert, 'device_name', '未知') or '未知'}\n"
        f"- 设备IP: {getattr(alert, 'device_ip', '未知') or '未知'}\n"
        f"\n## 告警详情\n{alert.message or '无详细描述'}\n"
    )

    wo_create = WorkOrderCreate(
        order_type=request.order_type or "fault",
        title=title,
        description=description,
        priority=priority,
        device_name=getattr(alert, 'device_name', None),
        device_ip=getattr(alert, 'device_ip', None),
    )

    wo = _build_workorder_core(db).create(
        title=title,
        order_type=_map_order_type(request.order_type or "fault"),
        creator=current_user.username,
        description=description,
        priority=_map_priority(priority),
        device_name=getattr(alert, 'device_name', None),
        device_ip=getattr(alert, 'device_ip', None),
    )

    # 将告警状态更新为已转工单
    try:
        alert.status = AlertStatus.ACKNOWLEDGED
        db.commit()
    except Exception:
        db.rollback()

    return {
        "status": "success",
        "message": "已从告警创建工单",
        "workorder_id": wo.id,
        "alert_id": alert.id,
    }


# ============== 工单转知识接口 =============

class GenerateKnowledgeRequest(BaseModel):
    """工单转知识请求"""
    doc_type: str = Field("sop", description="知识类型: sop（默认SOP文档）")
    category_id: Optional[int] = Field(None, description="分类ID")
    tags: Optional[str] = Field(None, description="标签，逗号分隔")
    content_template: Optional[str] = Field(
        None,
        description="内容模板: full（完整，包含所有字段）、summary（仅包含解决步骤）、root_cause（包含根因分析）"
    )


@router.post("/tickets/{workorder_id}/generate-knowledge", summary="工单转知识")
async def generate_knowledge_from_workorder(
    workorder_id: int,
    request: GenerateKnowledgeRequest = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    将已解决的工单转化为知识文档草稿（SOP文档）。
    生成的文档默认状态为 DRAFT，需经审核后才可发布。
    """
    import traceback
    try:
        # 获取工单
        wo = db.query(WorkOrder).filter(WorkOrder.id == workorder_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail="工单不存在")

        # 获取工单关联的设备信息
        device_info = ""
        if wo.device_name or wo.device_ip:
            device_info = f"\n\n**关联设备**: {wo.device_name or ''} ({wo.device_ip or 'N/A'})"

        # 根据模板决定内容
        template = request.content_template if (request and hasattr(request, 'content_template') and request.content_template) else "full"

        if template == "summary":
            content = f"""# {wo.title}

## 问题概述
{wo.description or '无描述'}

## 解决步骤
{wo.resolution or '无解决方案记录'}

## 标签
{wo.tags or ''}
"""
        elif template == "root_cause":
            content = f"""# {wo.title}

## 问题描述
{wo.description or '无描述'}{device_info}

## 根因分析
{wo.root_cause or '未填写'}

## 解决方案
{wo.resolution or '无解决方案记录'}
"""
        else:  # full
            content = f"""# {wo.title}

## 问题描述
{wo.description or '无描述'}{device_info}

## 根因分析
{wo.root_cause or '未填写'}

## 解决方案
{wo.resolution or '无解决方案记录'}

## 改进措施
{wo.improvement or '无改进措施'}

## 工单信息
- 工单ID: {wo.id}
- 优先级: {wo.priority}
- 创建时间: {wo.created_at}
- 关联标签: {wo.tags or '无'}
"""

        # 使用 SOPKnowledgeBase 创建知识文档草稿
        from modules.business.knowledge_base.sop import SOPKnowledgeBase
        sop_service = SOPKnowledgeBase(db)
        tags_str = request.tags if (request and hasattr(request, 'tags') and request.tags) else ''
        tags_list = [t.strip() for t in tags_str.split(',')] if tags_str else []
        doc = sop_service.create(
            title=f"[工单#{wo.id}] {wo.title}",
            content=content,
            author=current_user.username,
            category_id=request.category_id if (request and hasattr(request, 'category_id') and request.category_id) else None,
            tags=tags_list if tags_list else None,
            metadata={
                "source_workorder_id": wo.id,
                "source_type": "workorder",
            }
        )

        return {
            "status": "success",
            "message": "知识文档草稿已创建",
            "document_id": doc.id,
            "doc_no": doc.doc_no,
            "title": doc.title,
            "review_status": doc.review_status.value if hasattr(doc.review_status, 'value') else str(doc.review_status),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建知识文档失败: {type(e).__name__}: {str(e)}\n{traceback.format_exc()}")
