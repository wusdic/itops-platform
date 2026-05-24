"""
多租户隔离核心模块
实现请求级租户上下文，确保所有数据库操作自动带上 tenant_id 过滤
"""

import threading
from contextvars import ContextVar
from typing import Optional, Callable, Any
from dataclasses import dataclass

# 请求级租户上下文（协程安全）
_tenant_context: ContextVar[Optional[str]] = ContextVar("tenant_id", default=None)
_thread_local = threading.local()


@dataclass
class TenantContext:
    """租户上下文信息"""
    tenant_id: str
    user_id: str
    username: str
    roles: list[str]
    is_super_admin: bool = False  # 超级管理员可访问所有租户


def set_tenant_context(tenant_id: Optional[str]) -> None:
    """设置当前线程/协程的租户ID"""
    _tenant_context.set(tenant_id)


def get_tenant_id() -> Optional[str]:
    """获取当前租户ID"""
    return _tenant_context.get()


def clear_tenant_context() -> None:
    """清除租户上下文"""
    _tenant_context.reset(None)


class TenantContextManager:
    """
    租户上下文管理器
    
    用法:
        with TenantContextManager(tenant_id="t001"):
            # 这里面所有查询自动带上 tenant_id 过滤
            devices = session.query(Device).all()
    """

    def __init__(self, tenant_id: Optional[str]):
        self.tenant_id = tenant_id
        self._token = None

    def __enter__(self):
        self._token = _tenant_context.set(self.tenant_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _tenant_context.reset(self._token)
        return False


def require_tenant(f: Callable) -> Callable:
    """
    装饰器：确保函数在租户上下文中执行
    如果没有设置租户ID，抛出异常
    """
    def wrapper(*args, **kwargs):
        if get_tenant_id() is None:
            raise RuntimeError(
                "Tenant context not set. Use TenantContextManager or set_tenant_context() first."
            )
        return f(*args, **kwargs)
    return wrapper


def get_tenant_filter(model_class, alias=None):
    """
    获取当前租户的过滤条件
    
    Args:
        model_class: SQLAlchemy 模型类
        alias: 可选的查询别名
    
    Returns:
        SQLAlchemy filter 条件，或 None（超级管理员无限制）
    
    用法:
        query = session.query(Device)
        tenant_filter = get_tenant_filter(Device)
        if tenant_filter:
            query = query.filter(tenant_filter)
    """
    tenant_id = get_tenant_id()
    if tenant_id is None:
        return None
    
    column_name = "tenant_id"
    if alias is not None:
        column = getattr(alias.c, column_name, None)
    else:
        column = getattr(model_class, column_name, None)
    
    if column is None:
        return None
    
    return column == tenant_id


class TenantAwareQuery:
    """
    租户感知的查询构建器
    自动注入 tenant_id 过滤条件
    
    用法:
        results = TenantAwareQuery(session, Device).filter_by(status='online').all()
    """
    
    def __init__(self, session, model_class):
        self.session = session
        self.model_class = model_class
        self._query = session.query(model_class)
        self._apply_tenant_filter()
    
    def _apply_tenant_filter(self):
        """自动应用租户过滤"""
        tenant_id = get_tenant_id()
        if tenant_id is None:
            return  # 超级管理员不限制
        
        column = getattr(self.model_class, "tenant_id", None)
        if column is not None:
            self._query = self._query.filter(column == tenant_id)
    
    def filter_by(self, **kwargs):
        """过滤，自动保留租户条件"""
        self._query = self._query.filter_by(**kwargs)
        return self
    
    def filter(self, *args, **kwargs):
        """高级过滤"""
        self._query = self._query.filter(*args, **kwargs)
        return self
    
    def all(self):
        return self._query.all()
    
    def first(self):
        return self._query.first()
    
    def count(self):
        return self._query.count()
    
    def paginate(self, page=1, page_size=20):
        offset = (page - 1) * page_size
        return self._query.offset(offset).limit(page_size).all()
    
    @property
    def query(self):
        """获取底层 query 对象（用于不支持链式调用的场景）"""
        return self._query
