# api/routes/watermark.py — 操作水印 API
"""
为敏感操作生成可验证水印并写入 operation_logs

端点:
  POST /api/v1/watermark/generate    生成水印
  POST /api/v1/watermark/verify     验证水印
  POST /api/v1/watermark/log        记录带水印的操作
  GET  /api/v1/watermark/track/{id}  溯源查询
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List

from api.dependencies import get_current_user, require_role, CurrentUser, get_db
from modules.business.watermark_service import (
    generate_watermark,
    verify_watermark,
    parse_watermark,
)

router = APIRouter(prefix="/api/v1/watermark", tags=["操作水印"])


# ─── Request / Response 模型 ──────────────────────────────────────────────────

class WatermarkGenerateRequest(BaseModel):
    action: str = Field(..., description="操作类型 create/update/delete/export")
    resource: str = Field(..., description="资源类型 device/workorder/alert/script/config")
    resource_id: str = Field(..., description="资源 ID")
    operator: Optional[str] = Field(None, description="操作人（默认当前用户）")


class WatermarkLogRequest(BaseModel):
    action: str
    resource: str
    resource_id: str
    request_params: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class WatermarkVerifyRequest(BaseModel):
    watermark_id: str


class WatermarkResponse(BaseModel):
    watermark_id: str
    action: str
    resource: str
    resource_id: str
    operator: str
    timestamp: float


# ─── API ─────────────────────────────────────────────────────────────────────

@router.post("/generate", response_model=WatermarkResponse)
def make_watermark(
    payload: WatermarkGenerateRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """为指定操作生成防篡改水印"""
    operator = payload.operator or current_user.username
    wm = generate_watermark(
        action=payload.action,
        resource=payload.resource,
        resource_id=payload.resource_id,
        operator=operator,
    )
    info = parse_watermark(wm)
    return {
        "watermark_id": wm,
        "action": info["action"],
        "resource": info["resource"],
        "resource_id": info["resource_id"],
        "operator": info["operator"],
        "timestamp": float(info["timestamp"]),
    }


@router.post("/verify")
def check_watermark(payload: WatermarkVerifyRequest):
    """验证水印是否有效"""
    result = verify_watermark(payload.watermark_id)
    return result


@router.post("/log")
def log_watermarked_operation(
    payload: WatermarkLogRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    记录一条带水印的操作到 operation_logs
    （敏感操作如删除/导出/配置变更应在业务逻辑中调用此接口）
    """
    import time
    from modules.foundation.db_models.system import OperationLog

    wm = generate_watermark(
        action=payload.action,
        resource=payload.resource,
        resource_id=payload.resource_id,
        operator=current_user.username,
    )

    log = OperationLog(
        username=current_user.username,
        action=payload.action,
        resource=payload.resource,
        resource_id=payload.resource_id,
        watermark_id=wm,
        method="WATERMARKED",  # 标识为水印操作
        path=f"/watermark/{payload.action}/{payload.resource_id}",
        ip_address=payload.ip_address or "unknown",
        user_agent=payload.user_agent or "",
        request_body=str(payload.request_params or {}),
        response_status=200,
        duration_ms=0,
        timestamp=datetime.now(),
    )
    db.add(log)
    db.commit()

    return {
        "message": "操作已记录",
        "watermark_id": wm,
        "log_time": time.time(),
    }


@router.get("/track/{watermark_id}")
def track_watermark(
    watermark_id: str,
    current_user: CurrentUser = Depends(require_role("admin")),
    db = Depends(get_db),
):
    """根据水印 ID 溯源查询（需要 admin）"""
    # 先解析水印
    info = parse_watermark(watermark_id)
    if not info:
        raise HTTPException(400, "水印格式错误")

    # 验证水印有效性
    verify_result = verify_watermark(watermark_id)

    # 从 operation_logs 查找对应记录
    from modules.foundation.db_models.system import OperationLog

    logs = db.query(OperationLog).filter(
        OperationLog.username == info["operator"],
        OperationLog.action == info["action"],
        OperationLog.resource == info["resource"],
        OperationLog.resource_id == info["resource_id"],
    ).order_by(OperationLog.timestamp.desc()).limit(10).all()

    log_records = []
    for log in logs:
        log_records.append({
            "id": log.id,
            "username": log.username,
            "action": log.action,
            "resource": log.resource,
            "resource_id": log.resource_id,
            "method": log.method,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
        })

    return {
        "watermark": {
            "id": watermark_id,
            "parsed": info,
            "verified": verify_result["valid"],
        },
        "matched_logs": log_records,
    }


# 需要 datetime
from datetime import datetime