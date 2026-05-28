"""
数据库 Session 管理

提供统一风格的 session 获取和会话关闭。
使用 contextmanager 确保 session 在请求结束时正确关闭。
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from modules.foundation.db_models.base import db_session as _legacy_session


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    获取数据库 session 的标准方式

    _legacy_session() 是一个 @contextmanager 装饰的生成器函数，
    调用 db_session() 返回一个生成器，需用 next() 取出 session。

    用法:
        with get_db_session() as db:
            db.query(...)
            db.commit()
    """
    gen = _legacy_session()
    try:
        session = next(gen)  # 取出 @contextmanager yield 的 session
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        try:
            next(gen)  # 驱动生成器结束（触发 StopIteration）
        except StopIteration:
            pass
        session.close()


def commit_with_audit(db: Session, audit_action: str, resource: str, resource_id: str = None):
    """
    提交并记录审计日志

    用法:
        commit_with_audit(db, "asset.create", "asset", "123")
    """
    from app.common.audit import log_audit
    db.commit()
    log_audit(db, audit_action, resource, resource_id)
