"""
app.common - 统一基础设施层

提供所有领域共享的基础设施：
- response: 统一响应结构
- error_codes: 统一错误码体系
- context: 请求上下文
- audit: 审计日志
- permissions: 权限校验
- database: 数据库会话管理
- redis_client: Redis 缓存和锁
- message_queue: 消息队列
- background_task: 后台任务
"""

from app.common.response import UnifiedResponse, success_response, error_response, paginated_response
from app.common.error_codes import ErrorCode, get_http_status
from app.common.context import (
    RequestContext,
    get_trace_id,
    get_user_id,
    get_tenant_id,
    get_username,
    set_request_context,
    set_trace_id,
    set_user_context,
)
from app.common.permissions import Permission, RBAC, require_permission, require_role
from app.common.database import get_db_session, commit_with_audit
from app.common.redis_client import RedisCache, RedisLock, cache
from app.common.message_queue import MessageQueue, Channels, mq
from app.common.background_task import BackgroundTask, run_in_background

__all__ = [
    # response
    "UnifiedResponse",
    "success_response",
    "error_response",
    "paginated_response",
    # error_codes
    "ErrorCode",
    "get_http_status",
    # context
    "RequestContext",
    "get_trace_id",
    "get_user_id",
    "get_tenant_id",
    "get_username",
    "set_request_context",
    "set_trace_id",
    "set_user_context",
    # permissions
    "Permission",
    "RBAC",
    "require_permission",
    "require_role",
    # database
    "get_db_session",
    "commit_with_audit",
    # redis
    "RedisCache",
    "RedisLock",
    "cache",
    # message_queue
    "MessageQueue",
    "Channels",
    "mq",
    # background_task
    "BackgroundTask",
    "run_in_background",
]
