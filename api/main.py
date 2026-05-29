"""
FastAPI应用入口
API网关层主入口
"""

import os
import logging
from fastapi import FastAPI, Request
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
    asset_domain_router,
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
    report_singular_alias_router,
    backup_router,
    ldap_router,
)
from app.domains.collector.router import router as collector_router
from app.domains.config.router import router as config_router
from app.domains.alert.router import router as alert_router
from app.domains.strategy.router import router as strategy_router
from api.dependencies import get_settings
from api.middleware.logging import LoggingMiddleware
from api.middleware.error_handler import ErrorHandlerMiddleware
from api.middleware.performance import PerformanceMiddleware
from api.middleware.request_id import RequestIDMiddleware
from api.lifespan import lifespan
from api.exception_handlers import register_exception_handlers

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


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

    # 新版资产中心路由（app/domains/asset/router.py）
    app.include_router(
        asset_domain_router,
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
        prefix="/api/v1/devices",
        tags=["设备管理"],
    )

    app.include_router(
        device_metrics_router,
        prefix="/api/v1",
        tags=["采集精细化开关"],
    )

    app.include_router(device_import_router, prefix="/api/v1", tags=["设备批量导入"])

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

    app.include_router(
        report_singular_alias_router,
        prefix="",
        tags=["报表别名"],
    )

    app.include_router(
        backup_router,
        prefix="/api/v1/backup",
        tags=["备份恢复"],
    )

    app.include_router(
        collector_router,
        prefix="/api/v1/collectors",
        tags=["采集器管理"],
    )

    app.include_router(
        config_router,
        prefix="/api/v1",
        tags=["配置与凭证管理"],
    )

    app.include_router(
        alert_router,
        prefix="/api/v1",
        tags=["告警管理"],
    )

    app.include_router(
        strategy_router,
        prefix="/api/v1",
        tags=["策略中心"],
    )

    app.include_router(
        ldap_router,
        prefix="/api/v1",
        tags=["LDAP管理"],
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

    # 注册全局异常处理器（生产环境不返回 traceback）
    register_exception_handlers(app)

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
