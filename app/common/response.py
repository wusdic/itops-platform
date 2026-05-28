"""
统一响应结构

标准响应格式：
{
    "success": true,
    "code": "OK",
    "message": "success",
    "data": {...},
    "trace_id": "uuid"
}
"""

from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class UnifiedResponse(BaseModel, Generic[T]):
    """统一响应模型"""
    success: bool = True
    code: str = "OK"
    message: str = "success"
    data: Optional[T] = None
    trace_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "code": "OK",
                "message": "success",
                "data": {},
                "trace_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class PageData(BaseModel, Generic[T]):
    """分页数据"""
    items: list[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    pages: int = 0


def success_response(
    data: Any = None,
    message: str = "success",
    code: str = "OK",
    trace_id: Optional[str] = None
) -> dict:
    """成功响应"""
    return {
        "success": True,
        "code": code,
        "message": message,
        "data": data,
        "trace_id": trace_id
    }


def error_response(
    code: str,
    message: str,
    trace_id: Optional[str] = None,
    details: Optional[Any] = None
) -> dict:
    """错误响应"""
    return {
        "success": False,
        "code": code,
        "message": message,
        "data": details,
        "trace_id": trace_id
    }


def paginated_response(
    items: list,
    total: int,
    page: int = 1,
    page_size: int = 20,
    **kwargs
) -> dict:
    """分页响应"""
    pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return success_response(data={
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
        **kwargs
    })
