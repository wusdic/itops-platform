"""
请求上下文

在请求生命周期内传递 trace_id、user_id、tenant_id 等上下文信息。
通过 contextvars 实现线程安全的上下文传递。
"""

import contextvars
from contextlib import contextmanager
from typing import Optional
from dataclasses import dataclass


# Context variables
_trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="")
_user_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("user_id", default="")
_tenant_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("tenant_id", default="")
_username_var: contextvars.ContextVar[str] = contextvars.ContextVar("username", default="")


@dataclass
class RequestContext:
    """请求上下文"""
    trace_id: str = ""
    user_id: str = ""
    tenant_id: str = ""
    username: str = ""

    @classmethod
    def get_current(cls) -> "RequestContext":
        """获取当前上下文"""
        return cls(
            trace_id=_trace_id_var.get(),
            user_id=_user_id_var.get(),
            tenant_id=_tenant_id_var.get(),
            username=_username_var.get(),
        )


def get_trace_id() -> str:
    """获取当前 trace_id"""
    return _trace_id_var.get("")


def get_user_id() -> str:
    """获取当前用户 ID"""
    return _user_id_var.get("")


def get_tenant_id() -> str:
    """获取当前租户 ID"""
    return _tenant_id_var.get("")


def get_username() -> str:
    """获取当前用户名"""
    return _username_var.get("")


@contextmanager
def set_request_context(
    trace_id: str = "",
    user_id: str = "",
    tenant_id: str = "",
    username: str = "",
):
    """设置请求上下文"""
    token1 = _trace_id_var.set(trace_id)
    token2 = _user_id_var.set(user_id)
    token3 = _tenant_id_var.set(tenant_id)
    token4 = _username_var.set(username)
    try:
        yield
    finally:
        _trace_id_var.reset(token1)
        _user_id_var.reset(token2)
        _tenant_id_var.reset(token3)
        _username_var.reset(token4)


def set_trace_id(trace_id: str) -> None:
    """设置 trace_id"""
    _trace_id_var.set(trace_id)


def set_user_context(user_id: str, username: str = "", tenant_id: str = "") -> None:
    """设置用户上下文"""
    _user_id_var.set(user_id)
    _username_var.set(username)
    _tenant_id_var.set(tenant_id)
