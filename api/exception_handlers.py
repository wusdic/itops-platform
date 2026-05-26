"""
全局异常处理器
在生产环境中不返回 traceback，仅记录到日志
"""

import logging
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def register_exception_handlers(app):
    """向 FastAPI app 注册全局异常处理器"""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """
        全局异常处理器
        生产环境不返回 traceback，只返回通用错误信息，详细信息写入日志
        """
        import traceback
        tb = traceback.format_exc()
        print(f"EXCEPTION: {exc}\n{tb}", flush=True)
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An internal error occurred",
                "detail": None,  # 不在响应中返回 traceback，防止信息泄露
                "path": str(request.url),
            },
        )

    return app
