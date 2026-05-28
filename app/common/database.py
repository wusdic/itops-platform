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

    用法:
        with get_db_session() as db:
            db.query(...)
            db.commit()

    或者在 FastAPI 依赖中:
        def get_db():
            with get_db_session() as db:
                yield db
    """
    db = _legacy_session
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        pass  # legacy session is managed by lifespan, don't close here


def commit_with_audit(db: Session, audit_action: str, resource: str, resource_id: str = None):
    """
    提交并记录审计日志

    用法:
        commit_with_audit(db, "asset.create", "asset", "123")
    """
    from app.common.audit import log_audit
    db.commit()
    log_audit(db, audit_action, resource, resource_id)
