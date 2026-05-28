"""
采集器运行时与状态中心 - API 路由

提供采集器注册、心跳、状态追踪的 REST API
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Query

from app.common import success_response, paginated_response, get_trace_id
from app.common.database import get_db_session
from app.common.error_codes import ErrorCode, get_http_status
from app.domains.collector.service import CollectorService, CollectorTaskService
from app.domains.collector.schemas import (
    CollectorRegisterRequest, CollectorRegisterResponse,
    CollectorHeartbeatRequest, CollectorHeartbeatResponse,
    CollectorStateInfo, CollectorStateResponse,
    CollectorTaskSubmitRequest, CollectorTaskSubmitResponse,
    CollectorTaskResultRequest,
    CollectorConfigUpdateRequest, CollectorConfigResponse,
    CollectorDeregisterRequest,
    CollectorListRequest, CollectorStatsResponse,
    CollectorStatus, TaskStatus
)

router = APIRouter(tags=["采集器管理"])


# ========== 采集器注册与注销 ==========

@router.post("/register", response_model=CollectorRegisterResponse)
async def register_collector(request: Request, req: CollectorRegisterRequest):
    """
    注册采集器
    
    采集器启动时调用此接口注册到状态中心
    """
    with get_db_session() as db:
        svc = CollectorService(db)
        result = svc.register_collector(req)
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Failed to register collector"
            )
        
        return CollectorRegisterResponse(**result)


@router.post("/deregister")
async def deregister_collector(request: Request, req: CollectorDeregisterRequest):
    """
    注销采集器
    
    采集器关闭时调用此接口注销
    """
    with get_db_session() as db:
        svc = CollectorService(db)
        ok = svc.deregister_collector(req.collector_id, req.reason)
        
        if not ok:
            raise HTTPException(
                status_code=404,
                detail="Collector not found"
            )
        
        return success_response(message="Collector deregistered", trace_id=get_trace_id())


# ========== 心跳 ==========

@router.post("/heartbeat", response_model=CollectorHeartbeatResponse)
async def heartbeat(request: Request, req: CollectorHeartbeatRequest):
    """
    采集器心跳
    
    采集器定期调用此接口保持在线状态，同时上报资源使用情况
    """
    with get_db_session() as db:
        svc = CollectorService(db)
        result = svc.heartbeat(req)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Collector not found"
            )
        
        return CollectorHeartbeatResponse(**result)


# ========== 状态查询 ==========

@router.get("/state/{collector_id}", response_model=CollectorStateInfo)
async def get_collector_state(request: Request, collector_id: str):
    """
    获取采集器状态
    
    查看指定采集器的当前状态和统计信息
    """
    with get_db_session() as db:
        svc = CollectorService(db)
        state = svc.get_collector_state(collector_id)
        
        if not state:
            raise HTTPException(
                status_code=404,
                detail="Collector not found"
            )
        
        return state


@router.get("/states", response_model=CollectorStateResponse)
async def get_all_states(request: Request):
    """
    获取所有采集器状态
    
    查看所有已注册采集器的状态概览
    """
    with get_db_session() as db:
        svc = CollectorService(db)
        result = svc.get_all_states()
        
        return CollectorStateResponse(**result)


@router.get("/list")
async def list_collectors(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = None,
    protocol: Optional[str] = None,
    collector_id: Optional[str] = None,
    collector_name: Optional[str] = None
):
    """
    获取采集器列表
    
    分页查询采集器，支持按状态、协议、ID、名称过滤
    """
    with get_db_session() as db:
        svc = CollectorService(db)
        collectors, total = svc.list_collectors(
            page=page,
            page_size=page_size,
            status=status,
            protocol=protocol,
            collector_id=collector_id,
            collector_name=collector_name
        )
        
        items = [CollectorStateInfo(**c) for c in collectors]
        
        return paginated_response(
            items=[i.model_dump() for i in items],
            total=total,
            page=page,
            page_size=page_size,
            trace_id=get_trace_id()
        )


@router.get("/stats", response_model=CollectorStatsResponse)
async def get_stats(request: Request):
    """
    获取采集器统计信息
    
    查看采集器的整体运行统计
    """
    with get_db_session() as db:
        svc = CollectorService(db)
        stats = svc.get_stats()
        
        return CollectorStatsResponse(**stats)


# ========== 配置管理 ==========

@router.post("/config", response_model=CollectorConfigResponse)
async def update_config(request: Request, req: CollectorConfigUpdateRequest):
    """
    更新采集器配置
    
    下发新的配置给指定采集器
    """
    with get_db_session() as db:
        svc = CollectorService(db)
        config_hash = svc.update_config(req.collector_id, req.config, req.config_hash)
        
        if not config_hash:
            raise HTTPException(
                status_code=404,
                detail="Collector not found"
            )
        
        return CollectorConfigResponse(
            collector_id=req.collector_id,
            config=req.config,
            config_hash=config_hash,
            updated_at=datetime.now()
        )


# ========== 任务管理 ==========

@router.post("/tasks/submit", response_model=CollectorTaskSubmitResponse)
async def submit_task(request: Request, req: CollectorTaskSubmitRequest):
    """
    提交采集任务
    
    向指定采集器下发采集任务
    """
    with get_db_session() as db:
        svc = CollectorTaskService(db)
        result = svc.submit_task(req)
        
        if not result.get("success", True):
            error_code = result.get("error", "SYSTEM_INTERNAL_ERROR")
            raise HTTPException(
                status_code=get_http_status(error_code),
                detail=error_code
            )
        
        return CollectorTaskSubmitResponse(**result)


@router.post("/tasks/result")
async def report_task_result(request: Request, req: CollectorTaskResultRequest):
    """
    上报任务结果
    
    采集器完成采集任务后上报结果
    """
    with get_db_session() as db:
        svc = CollectorTaskService(db)
        ok = svc.report_result(req)
        
        return success_response(message="Result reported", trace_id=get_trace_id())


# ========== 健康检查 ==========

@router.get("/health")
async def health_check(request: Request):
    """
    采集器健康检查
    
    用于负载均衡器探测采集器健康状态
    """
    return success_response(
        data={"status": "healthy", "timestamp": datetime.now().isoformat()},
        trace_id=get_trace_id()
    )
