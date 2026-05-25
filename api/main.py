"""
FastAPI应用入口
API网关层主入口
"""

import os
import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from api.routes import (
    monitoring_router,
    workorder_router,
    knowledge_router,
    report_router,
    inspection_router,
    asset_router,
    ai_router,
    admin_router,
    system_router,
    notification_router,
    device_router,
    device_metrics_router,
    device_import_router,
    auth_router,
    discovery_router,
    automation_router,
    adapters_router,
    sharding_router,
    api_keys_router,
    log_service_router,
)
from api.dependencies import get_settings
from api.middleware.logging import LoggingMiddleware
from api.middleware.error_handler import ErrorHandlerMiddleware
from api.middleware.performance import PerformanceMiddleware
from api.middleware.request_id import RequestIDMiddleware

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
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

    # 启动告警升级定时任务
    import asyncio as _asyncio_alt
    _bg_tasks: list = []

    try:
        from modules.business.monitoring.alerter import get_alert_trigger
        alert_trigger = get_alert_trigger()
        _bg_tasks.append(_asyncio_alt.create_task(alert_trigger.start()))
        logger.info("AlertTrigger escalation task started")
    except Exception as e:
        logger.warning(f"AlertTrigger initialization skipped: {e}")

    # 启动设备定时采集任务
    periodic_collect_task = None
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


def create_app() -> FastAPI:
    """
    创建FastAPI应用实例
    """
    app = FastAPI(
        title="ITOps Platform API",
        description="智能化运维平台API网关",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # 添加CORS中间件
    # CORS配置从环境变量读取，支持环境变量覆盖
    settings = get_settings()
    cors_origins_env = os.getenv("CORS_ORIGINS", "")
    cors_origins = cors_origins_env.split(",") if cors_origins_env else settings.CORS_ORIGINS
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # 添加GZip压缩中间件
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 添加自定义中间件
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(PerformanceMiddleware)
    app.add_middleware(ErrorHandlerMiddleware)

    # 健康检查端点（必须在路由注册之前，确保 /health 优先级高于 /{path:path}）
    @app.get("/health", tags=["系统"])
    async def health_check():
        """健康检查接口"""
        return {
            "status": "healthy",
            "service": "itops-platform-api",
            "version": "1.0.0",
        }

    @app.get("/ready", tags=["系统"])
    async def readiness_check():
        """就绪检查接口"""
        return {
            "status": "ready",
            "service": "itops-platform-api",
        }

    # 注册路由
    app.include_router(
        monitoring_router,
        prefix="/api/v1/monitoring",
        tags=["监控管理"],
    )
    
    app.include_router(
        workorder_router,
        prefix="/api/v1/workorders",
        tags=["工单管理"],
    )
    
    app.include_router(
        knowledge_router,
        prefix="/api/v1/knowledge",
        tags=["知识库"],
    )
    
    app.include_router(
        report_router,
        prefix="/api/v1/reports",
        tags=["报表管理"],
    )
    
    app.include_router(
        inspection_router,
        prefix="/api/v1/inspection",
        tags=["巡检管理"],
    )
    
    app.include_router(
        asset_router,
        prefix="/api/v1/assets",
        tags=["资产管理"],
    )
    
    app.include_router(
        ai_router,
        prefix="/api/v1/ai",
        tags=["AI助手"],
    )
    
    app.include_router(
        admin_router,
        prefix="/api/v1/admin",
        tags=["系统管理"],
    )

    app.include_router(
        system_router,
        prefix="/api/v1/system",
        tags=["系统适配"],
    )

    app.include_router(
        adapters_router,
        prefix="/api/v1/admin",
        tags=["适配器管理"],
    )
    
    app.include_router(
        notification_router,
        prefix="/api/v1/notifications",
        tags=["通知渠道"],
    )

    app.include_router(
        device_router,
        prefix="",
        tags=["设备管理"],
    )

    app.include_router(
        device_metrics_router,
        prefix="",
        tags=["采集精细化开关"],
    )

    app.include_router(
        device_import_router,
        prefix="",
        tags=["设备批量导入"],
    )

    app.include_router(
        auth_router,
        prefix="/api/v1/auth",
        tags=["认证"],
    )

    app.include_router(
        discovery_router,
        prefix="/api/v1/discovery",
        tags=["设备发现"],
    )

    app.include_router(
        automation_router,
        prefix="/api/v1/automation",
        tags=["自动化触发"],
    )

    from api.routes.tenant import router as tenant_router
    app.include_router(
        tenant_router,
        prefix="/api/v1",
        tags=["租户管理"],
    )

    app.include_router(
        sharding_router,
        prefix="/api/v1",
        tags=["分片管理"],
    )

    from api.routes.deploy import router as deploy_router
    app.include_router(
        deploy_router,
        tags=["部署管理"],
    )

    from api.routes.watermark import router as watermark_router
    app.include_router(
        watermark_router,
        tags=["操作水印"],
    )

    from api.routes.vendor_credentials import router as vendor_credentials_router
    app.include_router(
        vendor_credentials_router,
        prefix="/api/v1/credentials",
        tags=["厂商账密管理"],
    )

    app.include_router(
        api_keys_router,
        prefix="/api/v1/api-keys",
        tags=["API密钥管理"],
    )

    app.include_router(
        log_service_router,
        prefix="/api/v1/logs",
        tags=["日志服务"],
    )

    # 前端静态文件服务 - 使用中间件方式避免路由冲突
    dist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
    if os.path.exists(dist_path):
        @app.middleware("static_files")
        async def static_files_middleware(request: Request, call_next):
            path = request.url.path
            
            # 拦截 /assets/* 请求
            if path.startswith("/assets/"):
                file_path = os.path.join(dist_path, path.lstrip("/"))
                if os.path.isfile(file_path):
                    return FileResponse(file_path)
            
            response = await call_next(request)
            return response
        
        @app.get("/")
        async def serve_index():
            return FileResponse(os.path.join(dist_path, "index.html"))
        
        # SPA fallback路由 - 仅处理 GET 请求的静态文件路由
        @app.get("/{path:path}")
        async def serve_spa(path: str):
            if path.startswith("api/"):
                return JSONResponse(status_code=404, content={"detail": "Not Found"})
            return FileResponse(os.path.join(dist_path, "index.html"))
        
        logger.info(f"Frontend static files enabled at /assets/ from: {dist_path}")

    # 全局异常处理 - 必须在最后添加，覆盖所有其他处理器
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """全局异常处理器"""
        import traceback
        tb = traceback.format_exc()
        print(f"EXCEPTION: {exc}\n{tb}", flush=True)
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": str(exc),
                "detail": tb,
                "path": str(request.url),
            },
        )

    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
