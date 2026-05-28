"""
API路由模块
"""

from fastapi import APIRouter

from .monitoring import router as monitoring_router
from .workorder import router as workorder_router
from .knowledge import router as knowledge_router
from .report import router as report_router
from .inspection import router as inspection_router
from .asset import router as asset_router
from .ai import router as ai_router
from .admin import router as admin_router
from .system import router as system_router
from .notification import router as notification_router
from .device_api import router as device_router
from .device_metrics import router as device_metrics_router
from .device_import import router as device_import_router
from .auth import router as auth_router
from .discovery import router as discovery_router
from .automation import router as automation_router
from .adapters import router as adapters_router
from .sharding import router as sharding_router
from .deploy import router as deploy_router
from .watermark import router as watermark_router
from .api_keys import router as api_keys_router
from .log_service import router as log_service_router
from .report_singular_alias import router as report_singular_alias_router
from .backup import router as backup_router

__all__ = [
    "monitoring_router",
    "workorder_router",
    "knowledge_router",
    "report_router",
    "inspection_router",
    "asset_router",
    "ai_router",
    "admin_router",
    "system_router",
    "notification_router",
    "device_router",
    "device_metrics_router",
    "device_import_router",
    "auth_router",
    "discovery_router",
    "automation_router",
    "adapters_router",
    "sharding_router",
    "deploy_router",
    "watermark_router",
    "api_keys_router",
    "log_service_router",
    "report_singular_alias_router",
    "backup_router",
]
