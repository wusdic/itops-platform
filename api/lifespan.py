"""
应用生命周期管理
启动时初始化服务（DB/AI/配置热更新/后台任务），关闭时清理资源
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, List

from fastapi import FastAPI

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    应用生命周期管理
    启动时初始化服务，关闭时清理资源
    """
    logger.info("Starting ITOps Platform API Gateway...")

    # 初始化数据库
    try:
        from modules.foundation.db_models.base import init_db
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")

    # 初始化其他服务
    try:
        from api.dependencies import get_settings
        settings = get_settings()
        logger.info(f"Environment: {settings.ENVIRONMENT}")
    except Exception as e:
        logger.warning(f"Settings initialization skipped: {e}")

    # 初始化AI（LLM客户端）
    try:
        from api.start import init_ai
        ai_result = init_ai({})
        if ai_result:
            logger.info("AI (LLM) initialized successfully")
        else:
            logger.warning("AI initialization returned None (disabled or failed)")
    except Exception as e:
        logger.warning(f"AI initialization skipped: {e}")

    # 初始化配置热更新
    try:
        from api.start import init_config_hot_reload
        init_config_hot_reload({})
    except Exception as e:
        logger.warning(f"Config hot reload initialization skipped: {e}")

    # 初始化 OpenTelemetry（可选，OTEL_ENDPOINT 环境变量配置 OTLP 收集器）
    try:
        from app.common.instrumentation import init_telemetry
        otlp_endpoint = os.getenv("OTEL_ENDPOINT")
        init_telemetry(
            service_name="itops-api",
            otlp_endpoint=otlp_endpoint,
        )
    except Exception as e:
        logger.warning(f"OpenTelemetry initialization skipped: {e}")

    # 启动后台任务
    import asyncio as _asyncio_alt
    _bg_tasks: list = []
    periodic_collect_task = None

    # 启动告警升级定时任务
    try:
        from modules.business.monitoring.alerter import get_alert_trigger
        alert_trigger = get_alert_trigger()
        _bg_tasks.append(_asyncio_alt.create_task(alert_trigger.start()))
        logger.info("AlertTrigger escalation task started")
    except Exception as e:
        logger.warning(f"AlertTrigger initialization skipped: {e}")

    # 启动设备定时采集任务
    try:
        from modules.collection.device_manager import get_device_manager

        manager = get_device_manager()
        # 从配置获取采集间隔，默认60秒
        interval = 60
        try:
            from modules.collection.config_loader import get_config_loader
            loader = get_config_loader()
            interval = loader.get_global_config('collect.default_interval') or 60
        except Exception:
            pass

        # 启动定时采集为后台任务，并捕获句柄以便优雅关闭
        periodic_collect_task = _asyncio_alt.create_task(
            manager.start_periodic_collect(interval=interval)
        )
        _bg_tasks.append(periodic_collect_task)
        logger.info(f"设备定时采集任务已启动 (间隔: {interval}秒)")

        # 注册自动化触发回调 - 每个设备采集完都会触发
        from modules.automation.auto_trigger_service import get_trigger_service
        trigger_service = get_trigger_service()
        manager.register_callback(trigger_service.on_device_metrics)
        logger.info("自动化触发服务已注册到设备采集回调")

        # 启动自动化触发评估循环
        _bg_tasks.append(_asyncio_alt.create_task(trigger_service.start()))
        logger.info("自动化触发服务已启动")
    except Exception as e:
        logger.warning(f"设备定时采集任务启动失败: {e}")

    logger.info("ITOps Platform API Gateway started successfully")

    yield

    # 关闭时清理资源
    logger.info("Shutting down ITOps Platform API Gateway...")

    # 停止自动化触发服务
    try:
        from modules.automation.auto_trigger_service import get_trigger_service
        trigger_service = get_trigger_service()
        await trigger_service.stop()
        logger.info("自动化触发服务已停止")
    except Exception as e:
        logger.warning(f"停止自动化触发服务失败: {e}")

    # 停止定时采集任务并取消所有后台任务
    if periodic_collect_task:
        try:
            from modules.collection.device_manager import get_device_manager
            manager = get_device_manager()
            manager.stop()
            periodic_collect_task.cancel()
            logger.info("设备定时采集任务已停止")
        except Exception as e:
            logger.warning(f"停止设备定时采集任务失败: {e}")

    # 取消所有捕获的后台任务
    for t in _bg_tasks:
        if not t.done():
            t.cancel()
    if _bg_tasks:
        await _asyncio_alt.gather(*_bg_tasks, return_exceptions=True)

    try:
        from modules.foundation.db_models.base import close_db
        close_db()
    except Exception as e:
        logger.warning(f"Database cleanup skipped: {e}")

    # 停止配置热更新轮询
    try:
        from api.start import get_config_manager
        cm = get_config_manager()
        if cm:
            cm.stop_watching()
            logger.info("Config hot reload stopped")
    except Exception as e:
        logger.warning(f"Config hot reload cleanup skipped: {e}")

    # 停止告警升级定时任务
    try:
        from modules.business.monitoring.alerter import get_alert_trigger
        alert_trigger = get_alert_trigger()
        await alert_trigger.stop()
        logger.info("AlertTrigger stopped")
    except Exception as e:
        logger.warning(f"AlertTrigger cleanup skipped: {e}")

    logger.info("ITOps Platform API Gateway stopped")
