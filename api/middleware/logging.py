"""
请求日志中间件
记录所有请求的详细信息到数据库 operation_logs 表
"""

import json
import logging
import time
import re
from datetime import datetime
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("access")


# 需要记录到操作日志的请求路径（不含需要过滤的路径）
LOGGED_PATHS_PREFIX = ("/api",)
# 不记录到操作日志的路径（精确匹配）
LOGGED_PATHS_EXACT = (
    "/api/v1/health",
    "/api/v1/metrics",
    "/docs",
    "/openapi.json",
    "/redoc",
)
# 登录路径 - 用于识别需要从请求体提取用户名的请求
LOGIN_PATHS = ("/api/v1/auth/login", "/api/v1/auth/login/")
# 不记录请求体的路径（但登录特殊处理：提取用户名）
NO_BODY_PATHS = ("/api/v1/health", "/api/v1/metrics", "/docs", "/openapi.json", "/redoc")


def _extract_resource(path: str) -> tuple[Optional[str], Optional[str]]:
    """从请求路径提取 resource 和 resource_id"""
    # /api/v1/devices/123 → resource=devices, resource_id=123
    parts = [p for p in path.strip("/").split("/") if p]
    if len(parts) >= 3 and parts[0] == "api" and parts[1] == "v1":
        resource = parts[2] if len(parts) > 2 else None
        resource_id = parts[3] if len(parts) > 3 else None
        return resource, resource_id
    return None, None


def _extract_action(method: str, path: str) -> str:
    """从 HTTP 方法和路径推断操作类型"""
    action_map = {
        "GET": "read",
        "POST": "create",
        "PUT": "update",
        "PATCH": "update",
        "DELETE": "delete",
    }
    return action_map.get(method.upper(), method.lower())


def _safe_get_body(request: Request) -> Optional[str]:
    """安全获取请求体（仅用于非登录请求）"""
    if any(path in request.url.path for path in NO_BODY_PATHS):
        return None
    try:
        body = request._body  # noqa: access private attribute
        if body:
            try:
                text = body.decode("utf-8", errors="replace")
                # 截断过长 body
                if len(text) > 1000:
                    text = text[:1000] + "...[truncated]"
                return text
            except Exception:
                return None
    except Exception:
        pass
    return None


def _get_user_from_token(request: Request) -> str:
    """从请求中提取用户名（通过 Authorization header）"""
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            import base64
            import json as _json
            # JWT payload is second part
            payload_b64 = token.split(".")[1]
            # Add padding
            padding = 4 - len(payload_b64) % 4
            if padding < 4:
                payload_b64 += "=" * padding
            payload = _json.loads(base64.urlsafe_b64decode(payload_b64))
            return payload.get("username", payload.get("sub", "anonymous"))
        except Exception:
            pass
    return "anonymous"


def _write_log_to_db(record: dict):
    """在新线程中写入数据库，避免阻塞事件循环"""
    import threading

    def _do_insert():
        try:
            from modules.foundation.db_models.base import DatabaseManager
            from modules.foundation.db_models.system import OperationLog

            with DatabaseManager().session_scope() as db:
                try:
                    log = OperationLog(
                        username=record.get("username", "anonymous"),
                        action=record.get("action", "unknown"),
                        resource=record.get("resource"),
                        resource_id=record.get("resource_id"),
                        method=record.get("method"),
                        path=record.get("path"),
                        ip_address=record.get("ip_address"),
                        user_agent=record.get("user_agent", "")[:256],
                        request_body=record.get("request_body"),
                        response_status=record.get("response_status"),
                        error_message=record.get("error_message"),
                        duration_ms=record.get("duration_ms", 0),
                        timestamp=datetime.fromisoformat(record["timestamp"]),
                    )
                    db.add(log)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    logger.warning(f"Failed to write operation log: {e}")
        except Exception as e:
            logger.warning(f"Failed to write operation log (import error): {e}")

    t = threading.Thread(target=_do_insert, daemon=True)
    t.start()


class LoggingMiddleware(BaseHTTPMiddleware):
    """记录每个请求的详细信息到数据库"""

    async def dispatch(self, request: Request, call_next):
        # 跳过不需要记录的路径
        path = request.url.path
        if not path.startswith(LOGGED_PATHS_PREFIX) or path in LOGGED_PATHS_EXACT:
            return await call_next(request)

        start_time = time.perf_counter()
        client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        if not client_ip:
            client_ip = request.client.host if request.client else "-"
        user_agent = request.headers.get("user-agent", "")[:256]

        # 提取资源信息
        resource, resource_id = _extract_resource(path)
        action = _extract_action(request.method, path)

        # 特殊处理登录：从请求体中提取用户名（call_next 执行前就知道）
        _username_from_body = None
        request_body = None
        if path in LOGIN_PATHS and request.method == "POST":
            try:
                body = await request.body()
                if body:
                    try:
                        body_data = json.loads(body.decode("utf-8"))
                        _username_from_body = body_data.get("username", "")
                        # 截断过长的 body
                        body_text = body.decode("utf-8", errors="replace")
                        if len(body_text) > 1000:
                            body_text = body_text[:1000] + "...[truncated]"
                        request_body = body_text
                    except Exception:
                        pass
                    # 重新构建请求体以便后续 handler 能继续读取
                    async def receive():
                        return {"type": "http.request", "body": body}
                    request._receive = receive  # noqa: access private attribute
            except Exception:
                pass
        elif path not in NO_BODY_PATHS and request.method in ("POST", "PUT", "PATCH"):
            body = await request.body()
            if body:
                try:
                    text = body.decode("utf-8", errors="replace")
                    if len(text) > 1000:
                        text = text[:1000] + "...[truncated]"
                    request_body = text
                except Exception:
                    pass
                # 重新构建请求体以便后续 handler 能继续读取
                async def receive():
                    return {"type": "http.request", "body": body}
                request._receive = receive  # noqa: access private attribute

        username = _get_user_from_token(request)
        # 如果从 token 解析不出用户名（返回默认的 "anonymous"），用登录请求体中的用户名
        if _username_from_body and username == "anonymous":
            username = _username_from_body

        # 打印请求开始
        logger.info(
            json.dumps(
                {
                    "type": "request_start",
                    "method": request.method,
                    "path": path,
                    "client_ip": client_ip,
                    "user": username,
                },
                ensure_ascii=False,
            )
        )

        # 执行请求
        error_message = None
        response_status = 500
        try:
            response = await call_next(request)
            response_status = response.status_code
            return response
        except Exception as e:
            error_message = str(e)[:500]
            response_status = 500
            raise
        finally:
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            timestamp = datetime.now().astimezone().isoformat()

            # 打印请求完成
            logger.info(
                json.dumps(
                    {
                        "type": "request_end",
                        "method": request.method,
                        "path": path,
                        "status": response_status,
                        "duration_ms": duration_ms,
                        "client_ip": client_ip,
                        "user": username,
                    },
                    ensure_ascii=False,
                )
            )

            # 写入数据库
            _write_log_to_db(
                {
                    "username": username,
                    "action": action,
                    "resource": resource,
                    "resource_id": resource_id,
                    "method": request.method,
                    "path": path,
                    "ip_address": client_ip,
                    "user_agent": user_agent,
                    "request_body": request_body,
                    "response_status": response_status,
                    "error_message": error_message,
                    "duration_ms": duration_ms,
                    "timestamp": timestamp,
                }
            )
