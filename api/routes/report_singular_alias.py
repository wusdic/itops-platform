"""
报表单数别名路由
提供 GET /api/v1/report → /api/v1/reports 的别名
"""

from fastapi import APIRouter, Depends, Query
from datetime import datetime
from api.dependencies import get_current_user, CurrentUser, get_db
from api.routes.report import PaginationParams

router = APIRouter(prefix="/api/v1/report", tags=["报表别名"])


@router.get("", summary="获取报表列表(单数别名)")
async def get_reports_singular(
    pagination: PaginationParams = Depends(PaginationParams),
    report_type: str = Query(None),
    status: str = Query(None),
    start_date: datetime = Query(None),
    end_date: datetime = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db=Depends(get_db),
):
    """GET /api/v1/report 别名到 GET /api/v1/reports"""
    from api.routes.report import get_reports
    return await get_reports(
        pagination=pagination,
        report_type=report_type,
        status=status,
        start_date=start_date,
        end_date=end_date,
        current_user=current_user,
        db=db,
    )
