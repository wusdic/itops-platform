"""
日志业务服务
提供日志查询、配置管理、接入配置的业务逻辑
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session

logger = logging.getLogger("logs")


class LogQueryService:
    """日志查询服务"""

    @staticmethod
    def query_logs(
        db: Session,
        category: str,
        keyword: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        level: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """查询日志（归集组级别）"""
        from modules.foundation.db_models.system import LogGroup

        query = db.query(LogGroup).filter(LogGroup.category == category)

        if start_date:
            query = query.filter(LogGroup.last_seen >= start_date)
        if end_date:
            query = query.filter(LogGroup.last_seen <= end_date)

        total = query.count()
        groups = query.order_by(LogGroup.last_seen.desc()) \
            .offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for g in groups:
            import json
            dim = json.loads(g.dimension_summary or "{}")
            dim.pop("bucket", None)
            items.append({
                "id": g.id,
                "category": g.category,
                "group_key": g.group_key,
                "dimension": dim,
                "first_seen": g.first_seen.isoformat() if g.first_seen else None,
                "last_seen": g.last_seen.isoformat() if g.last_seen else None,
                "total_count": g.total_count,
                "level_distribution": json.loads(g.level_distribution or "{}"),
                "sample_log": g.sample_log,
            })

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    def query_log_items(
        db: Session,
        group_id: int,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """查询日志明细"""
        from modules.foundation.db_models.system import LogItem

        query = db.query(LogItem).filter(LogItem.group_id == group_id)
        total = query.count()
        items_db = query.order_by(LogItem.created_at.desc()) \
            .offset((page - 1) * page_size).limit(page_size).all()

        import json
        items = []
        for it in items_db:
            items.append({
                "id": it.id,
                "group_id": it.group_id,
                "category": it.category,
                "level": it.level,
                "source": it.source,
                "message": it.message,
                "detail": json.loads(it.detail) if it.detail else None,
                "duration_ms": it.duration_ms,
                "username": it.username,
                "ip_address": it.ip_address,
                "resource_type": it.resource_type,
                "resource_id": it.resource_id,
                "raw_content": it.raw_content,
                "created_at": it.created_at.isoformat() if it.created_at else None,
            })
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }


class LogConfigManagementService:
    """日志配置管理服务"""

    @staticmethod
    def get_configs(db: Session) -> List[Dict[str, Any]]:
        """获取所有日志配置"""
        from modules.foundation.db_models.system import LogConfig

        configs = db.query(LogConfig).order_by(LogConfig.category, LogConfig.id).all()
        return [
            {
                "id": c.id,
                "category": c.category,
                "sub_category": c.sub_category,
                "enabled": bool(c.enabled),
                "min_level": c.min_level,
                "aggregation_enabled": bool(c.aggregation_enabled),
                "retention_days": c.retention_days,
                "description": c.description,
            }
            for c in configs
        ]

    @staticmethod
    def update_configs(db: Session, configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量更新日志配置"""
        from modules.foundation.db_models.system import LogConfig

        results = []
        for cfg in configs:
            row = db.query(LogConfig).filter(
                LogConfig.category == cfg["category"],
                LogConfig.sub_category == cfg["sub_category"],
            ).first()
            if row:
                if "enabled" in cfg:
                    row.enabled = 1 if cfg["enabled"] else 0
                if "min_level" in cfg:
                    row.min_level = cfg["min_level"]
                if "retention_days" in cfg:
                    row.retention_days = cfg["retention_days"]
                if "aggregation_enabled" in cfg:
                    row.aggregation_enabled = 1 if cfg["aggregation_enabled"] else 0
                results.append({"category": row.category, "sub_category": row.sub_category, "status": "updated"})
        db.commit()
        return results


class LogAccessConfigService:
    """日志接入配置服务"""

    @staticmethod
    def get_all(db: Session) -> List[Dict[str, Any]]:
        """获取所有日志接入配置"""
        from modules.foundation.db_models.system import LogAccessConfig

        configs = db.query(LogAccessConfig).all()
        return [
            {
                "id": c.id,
                "name": c.name,
                "backend": c.backend,
                "host": c.host,
                "port": c.port,
                "username": c.username,
                "index_pattern": c.index_pattern,
                "log_type": c.log_type,
                "enabled": bool(c.enabled),
                "retention_days": c.retention_days,
                "description": c.description,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in configs
        ]

    @staticmethod
    def create(
        db: Session,
        name: str,
        backend: str,
        host: str,
        port: int,
        index_pattern: Optional[str] = None,
        log_type: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        enabled: bool = True,
        retention_days: int = 7,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """创建日志接入配置"""
        from modules.foundation.db_models.system import LogAccessConfig

        config = LogAccessConfig(
            name=name,
            backend=backend,
            host=host,
            port=port,
            username=username,
            password=password,
            index_pattern=index_pattern,
            log_type=log_type,
            enabled=1 if enabled else 0,
            retention_days=retention_days,
            description=description,
        )
        db.add(config)
        db.commit()
        db.refresh(config)
        return {
            "id": config.id,
            "name": config.name,
            "backend": config.backend,
            "host": config.host,
            "port": config.port,
            "enabled": bool(config.enabled),
        }

    @staticmethod
    def delete(db: Session, config_id: int) -> bool:
        """删除日志接入配置"""
        from modules.foundation.db_models.system import LogAccessConfig

        config = db.query(LogAccessConfig).filter(LogAccessConfig.id == config_id).first()
        if not config:
            return False
        db.delete(config)
        db.commit()
        return True


class LogIndexService:
    """日志索引服务（简化版，实际生产可能需要连接ES/Loki等）"""

    @staticmethod
    def list_indexes(db: Session) -> List[Dict[str, Any]]:
        """列出已配置的日志索引"""
        from modules.foundation.db_models.system import LogAccessConfig

        configs = db.query(LogAccessConfig).filter(
            LogAccessConfig.index_pattern.isnot(None)
        ).all()
        return [
            {
                "id": c.id,
                "name": c.name,
                "index_pattern": c.index_pattern,
                "log_type": c.log_type,
                "backend": c.backend,
                "enabled": bool(c.enabled),
                "retention_days": c.retention_days,
            }
            for c in configs
        ]

    @staticmethod
    def create_index(
        db: Session,
        name: str,
        index_pattern: str,
        log_type: str,
        retention_days: int = 7,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """创建索引配置"""
        from modules.foundation.db_models.system import LogAccessConfig

        config = LogAccessConfig(
            name=name,
            index_pattern=index_pattern,
            log_type=log_type,
            backend="elasticsearch",  # 默认后端
            host="localhost",
            port=9200,
            enabled=1,
            retention_days=retention_days,
            description=description,
        )
        db.add(config)
        db.commit()
        db.refresh(config)
        return {
            "id": config.id,
            "name": config.name,
            "index_pattern": config.index_pattern,
            "log_type": config.log_type,
            "enabled": bool(config.enabled),
        }
