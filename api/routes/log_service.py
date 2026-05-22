"""
日志配置与归集服务
管理日志配置、写入日志记录、归集分组
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy import func, text
from sqlalchemy.orm import Session

logger = logging.getLogger("logs")

# 日志分类定义：category -> sub_category -> (enabled, min_level, description)
DEFAULT_LOG_CONFIG = {
    "operation": {
        "login": {"enabled": True, "min_level": "INFO", "description": "登录/登出"},
        "device_crud": {"enabled": True, "min_level": "INFO", "description": "设备增删改查"},
        "alert_action": {"enabled": True, "min_level": "INFO", "description": "告警状态变更"},
        "workorder_crud": {"enabled": True, "min_level": "INFO", "description": "工单增删改"},
        "adapter_credential": {"enabled": False, "min_level": "INFO", "description": "适配器/凭证变更"},
    },
    "system": {
        "error": {"enabled": True, "min_level": "ERROR", "description": "ERROR 及以上"},
        "warning": {"enabled": True, "min_level": "WARNING", "description": "WARNING 及以上"},
        "info": {"enabled": False, "min_level": "INFO", "description": "INFO 记录（量大）"},
        "debug": {"enabled": False, "min_level": "DEBUG", "description": "DEBUG 记录（最大量）"},
    },
    "collection": {
        "success": {"enabled": False, "min_level": "INFO", "description": "采集成功（量大）"},
        "failed": {"enabled": True, "min_level": "ERROR", "description": "采集失败"},
        "offline": {"enabled": True, "min_level": "WARNING", "description": "设备离线"},
    },
    "audit": {
        "all": {"enabled": True, "min_level": "INFO", "description": "全部告警操作"},
    },
}

LEVEL_PRIORITY = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}


def _should_record(config: dict, level: str) -> bool:
    """判断某级别的日志是否应该记录"""
    if not config.get("enabled", 0):
        return False
    config_level = config.get("min_level", "INFO")
    return LEVEL_PRIORITY.get(level, 0) >= LEVEL_PRIORITY.get(config_level, 1)


def _get_sub_category(action: str, resource: str, category: str) -> str:
    """根据操作推断子分类"""
    if category == "operation":
        if action in ("login", "logout"):
            return "login"
        if action in ("create", "update", "delete") and resource:
            if resource in ("device", "devices"):
                return "device_crud"
            if resource in ("workorder", "workorders"):
                return "workorder_crud"
            if resource in ("alert", "alerts"):
                return "alert_action"
            if resource in ("adapter", "credential", "credentials", "adapters"):
                return "adapter_credential"
        return "login"  # 默认归为 login
    if category == "system":
        return "error"  # 系统日志按 ERROR 级别归入 error
    if category == "collection":
        return action  # action 就是 success/failed/offline
    return "all"


class LogConfigService:
    """日志配置服务"""

    @staticmethod
    def init_defaults(db: Session):
        """初始化默认配置（仅插入未存在的记录）"""
        from modules.foundation.db_models.system import LogConfig

        existing = db.query(LogConfig).first()
        if existing:
            return  # 已有配置，跳过

        for category, subs in DEFAULT_LOG_CONFIG.items():
            for sub, cfg in subs.items():
                db.add(LogConfig(
                    category=category,
                    sub_category=sub,
                    enabled=1 if cfg["enabled"] else 0,
                    min_level=cfg["min_level"],
                    description=cfg["description"],
                    retention_days=7,
                    aggregation_enabled=1,
                ))
        db.commit()
        logger.info("日志配置已初始化")

    @staticmethod
    def get_all(db: Session) -> list:
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
    def update_all(db: Session, configs: list) -> list:
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
                results.append({"category": row.category, "sub_category": "updated"})
        db.commit()
        return results

    @staticmethod
    def is_enabled(db: Session, category: str, sub_category: str, level: str = "INFO") -> bool:
        from modules.foundation.db_models.system import LogConfig

        cfg = db.query(LogConfig).filter(
            LogConfig.category == category,
            LogConfig.sub_category == sub_category,
        ).first()
        if not cfg:
            # 无配置时默认开启
            return True
        return _should_record({
            "enabled": cfg.enabled,
            "min_level": cfg.min_level,
        }, level)


class LogAggregationService:
    """日志归集服务"""

    @staticmethod
    def _make_group_key(category: str, dimensions: dict) -> str:
        """生成归集键"""
        key_data = json.dumps(dimensions, sort_keys=True, ensure_ascii=True)
        return hashlib.md5(key_data.encode()).hexdigest()

    @staticmethod
    def _get_or_create_group(db: Session, category: str, dimensions: dict,
                              now: datetime) -> tuple:
        from modules.foundation.db_models.system import LogGroup

        group_key = LogAggregationService._make_group_key(category, dimensions)
        group = db.query(LogGroup).filter(
            LogGroup.category == category,
            LogGroup.group_key == group_key,
        ).first()

        if group:
            return group, False

        group = LogGroup(
            category=category,
            group_key=group_key,
            dimension_summary=json.dumps(dimensions, ensure_ascii=True),
            first_seen=now,
            last_seen=now,
            total_count=0,
            level_distribution=json.dumps({}),
        )
        db.add(group)
        db.flush()
        return group, True

    @staticmethod
    def write_operation_log(db: Session, record: dict, config: dict):
        """写入操作日志（归集模式）"""
        from modules.foundation.db_models.system import LogGroup, LogItem

        sub_cat = _get_sub_category(
            record.get("action", ""),
            record.get("resource", ""),
            "operation"
        )

        if not _should_record(config.get(sub_cat, {}), record.get("level", "INFO")):
            return

        now = datetime.now()
        # 归集维度：action + resource + 10分钟时间桶
        bucket = now.replace(minute=now.minute // 10 * 10, second=0, microsecond=0)
        dimensions = {
            "action": record.get("action", ""),
            "resource": record.get("resource", ""),
            "username": record.get("username", ""),
            "ip": record.get("ip_address", ""),
            "bucket": bucket.isoformat(),
        }
        group, is_new = LogAggregationService._get_or_create_group(db, "operation", dimensions, now)

        # 更新组统计
        group.total_count += 1
        group.last_seen = now
        if is_new:
            group.sample_log = record.get("path", "")

        # 写入明细
        item = LogItem(
            group_id=group.id,
            category="operation",
            raw_content=json.dumps(record, ensure_ascii=True),
            level=record.get("level", "INFO"),
            message=f"{record.get('username', '')} {record.get('action', '')} {record.get('resource', '')}",
            detail=json.dumps({
                "method": record.get("method"),
                "path": record.get("path"),
                "resource_id": record.get("resource_id"),
                "status": record.get("response_status"),
            }, ensure_ascii=True),
            duration_ms=record.get("duration_ms"),
            username=record.get("username"),
            ip_address=record.get("ip_address"),
            resource_type=record.get("resource"),
            resource_id=record.get("resource_id"),
            created_at=now,
        )
        db.add(item)

    @staticmethod
    def write_system_log(db: Session, level: str, source: str, message: str, raw: str):
        """写入系统日志（归集模式）"""
        from modules.foundation.db_models.system import LogGroup, LogItem

        sub_cat = "error" if level in ("ERROR", "CRITICAL") else "warning" if level == "WARNING" else "info"
        cfg = {"enabled": 1, "min_level": "WARNING"}  # 从 DB 读

        # 简化：系统日志总是归集（按 level + source + 5分钟桶）
        now = datetime.now()
        bucket = now.replace(minute=now.minute // 5 * 5, second=0, microsecond=0)
        dimensions = {
            "level": level,
            "source": source,
            "bucket": bucket.isoformat(),
        }
        group, is_new = LogAggregationService._get_or_create_group(db, "system", dimensions, now)

        group.total_count += 1
        group.last_seen = now
        if is_new:
            group.sample_log = message[:200]

        # 更新 level 分布
        dist = json.loads(group.level_distribution or "{}")
        dist[level] = dist.get(level, 0) + 1
        group.level_distribution = json.dumps(dist)

        item = LogItem(
            group_id=group.id,
            category="system",
            raw_content=raw,
            level=level,
            source=source,
            message=message,
            created_at=now,
        )
        db.add(item)

    @staticmethod
    def write_collection_log(db: Session, status: str, device_name: str, device_ip: str,
                              message: str, duration_ms: int, config: dict):
        """写入采集日志（归集模式）"""
        from modules.foundation.db_models.system import LogGroup, LogItem

        if not _should_record(config.get(status, {}), "ERROR" if status == "failed" else "INFO"):
            return

        now = datetime.now()
        bucket = now.replace(second=0, microsecond=0)
        dimensions = {
            "status": status,
            "device_name": device_name,
            "device_ip": device_ip,
            "bucket": bucket.isoformat(),
        }
        group, is_new = LogAggregationService._get_or_create_group(db, "collection", dimensions, now)

        group.total_count += 1
        group.last_seen = now
        if is_new:
            group.sample_log = message[:200]

        dist = json.loads(group.level_distribution or "{}")
        dist[status] = dist.get(status, 0) + 1
        group.level_distribution = json.dumps(dist)

        item = LogItem(
            group_id=group.id,
            category="collection",
            raw_content=message,
            level="ERROR" if status == "failed" else "INFO",
            source="collector",
            message=message,
            duration_ms=duration_ms,
            resource_type="device",
            resource_id=device_ip,
            created_at=now,
        )
        db.add(item)

    @staticmethod
    def get_groups(db: Session, category: str, keyword: str = None,
                   start_date: datetime = None, end_date: datetime = None,
                   page: int = 1, page_size: int = 20) -> tuple:
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
            dim = json.loads(g.dimension_summary or "{}")
            # 隐藏 bucket 字段（太细节）
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

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    def get_group_items(db: Session, group_id: int, page: int = 1, page_size: int = 50) -> dict:
        from modules.foundation.db_models.system import LogItem

        query = db.query(LogItem).filter(LogItem.group_id == group_id)
        total = query.count()
        items_db = query.order_by(LogItem.created_at.desc()) \
            .offset((page - 1) * page_size).limit(page_size).all()

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
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    def cleanup_old_logs(db: Session):
        """清理过期日志（按 retention_days）"""
        from modules.foundation.db_models.system import LogConfig, LogGroup, LogItem

        configs = db.query(LogConfig).all()
        for cfg in configs:
            cutoff = datetime.now() - timedelta(days=cfg.retention_days)
            # 删除归集组（级联删除明细）
            groups = db.query(LogGroup).filter(
                LogGroup.category == cfg.category,
                LogGroup.last_seen < cutoff,
            ).all()
            group_ids = [g.id for g in groups]
            if group_ids:
                db.query(LogItem).filter(LogItem.group_id.in_(group_ids)).delete(synchronize_session=False)
                db.query(LogGroup).filter(LogGroup.id.in_(group_ids)).delete(synchronize_session=False)
        db.commit()
        logger.info("日志清理完成")

    @staticmethod
    def get_stats(db: Session) -> dict:
        """获取各分类实时统计"""
        from modules.foundation.db_models.system import LogGroup, LogItem

        stats = {}
        for cat in ("operation", "system", "collection", "audit"):
            total_items = db.query(func.sum(LogGroup.total_count)).filter(
                LogGroup.category == cat
            ).scalar() or 0
            total_groups = db.query(LogGroup.id).filter(
                LogGroup.category == cat
            ).count()
            stats[cat] = {
                "total_items": int(total_items),
                "total_groups": total_groups,
            }
        return stats
