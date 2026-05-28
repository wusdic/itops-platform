"""
Trace ID 中间件

为每个请求生成唯一 trace_id，设置到请求上下文和响应头中。
"""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.common.context import set_trace_id


class TraceIDMiddleware(BaseHTTPMiddleware):
    """
    Trace ID 中间件
    为每个请求生成唯一的 X-Trace-ID
    """
    HEADER_NAME = "X-Trace-ID"

    async def dispatch(self, request: Request, call_next) -> Response:
        # 获取或生成 trace_id
        trace_id = request.headers.get(self.HEADER_NAME)
        if not trace_id:
            trace_id = str(uuid.uuid4())

        # 设置到上下文
        set_trace_id(trace_id)
        request.state.trace_id = trace_id

        # 处理请求
        response = await call_next(request)

        # 在响应头中添加 trace_id
        response.headers[self.HEADER_NAME] = trace_id

        return response
