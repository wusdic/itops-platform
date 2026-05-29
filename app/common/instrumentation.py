"""
OpenTelemetry instrumentation for ITOps Platform.
Provides trace/span decorators for API requests, worker tasks, and AI calls.

Usage:
    from app.common.instrumentation import trace_span, init_telemetry

    # Initialize once at startup
    init_telemetry(service_name="itops-api")

    # Wrap any function
    @trace_span("ai.analyze")
    async def analyze_alert(alert_id: int):
        ...
"""
import os
import time
import logging
from functools import wraps
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)

# ─── No-op fallbacks ──────────────────────────────────────────
class _NoOpSpan:
    """No-op span when OpenTelemetry is not installed."""
    def set_attribute(self, key: str, value: Any) -> None: pass
    def set_status(self, status: Any) -> None: pass
    def record_exception(self, exc: Exception) -> None: pass
    def end(self) -> None: pass
    def add_event(self, name: str, attributes: dict = None) -> None: pass

class _NoOpTracer:
    """No-op tracer when OpenTelemetry is not installed."""
    def start_span(self, name: str, **kwargs) -> _NoOpSpan:
        return _NoOpSpan()
    def start_as_current_span(self, name: str, **kwargs):
        return _NoOpSpan()

_tracer: Any = _NoOpTracer()
_telemetry_initialized = False


def init_telemetry(
    service_name: str = "itops-platform",
    otlp_endpoint: Optional[str] = None,
) -> None:
    """
    Initialize OpenTelemetry tracing.
    Safe to call even if opentelemetry is not installed.

    Args:
        service_name: Name of this service (e.g., "itops-api", "itops-worker")
        otlp_endpoint: OTLP collector endpoint (e.g., "http://localhost:4317").
                       If None, traces are logged only (no export).
    """
    global _tracer, _telemetry_initialized
    if _telemetry_initialized:
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
        from opentelemetry.sdk.resources import Resource, SERVICE_NAME
        from opentelemetry.trace import Status, StatusCode

        resource = Resource(attributes={
            SERVICE_NAME: service_name,
            "service.version": os.getenv("APP_VERSION", "1.0.0"),
            "deployment.environment": os.getenv("ENVIRONMENT", "development"),
        })

        provider = TracerProvider(resource=resource)

        # Export to OTLP collector if configured
        if otlp_endpoint:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
                processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
                provider.add_span_processor(processor)
            except ImportError:
                logger.warning("OTLP exporter not available, falling back to console")
                provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        else:
            # Console exporter for development
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer(service_name)
        _telemetry_initialized = True
        logger.info(f"OpenTelemetry initialized for service={service_name}, endpoint={otlp_endpoint}")
    except ImportError as e:
        logger.warning(f"OpenTelemetry not installed: {e}. Tracing disabled.")
        _telemetry_initialized = True  # Mark as initialized (with no-op)


def trace_span(
    name: str,
    attributes: Optional[dict] = None,
    record_exception: bool = True,
) -> Callable:
    """
    Decorator to trace a function as a span.

    Usage:
        @trace_span("ai.analyze_alert", attributes={"alert.severity": "critical"})
        async def analyze_alert(alert_id: int):
            ...

    Args:
        name: Span name (e.g., "ai.analyze", "db.query", "automation.execute")
        attributes: Fixed attributes for this span
        record_exception: Whether to record exceptions automatically
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            span_name = f"{name}"
            with _tracer.start_as_current_span(span_name) as span:
                if attributes:
                    for k, v in attributes.items():
                        span.set_attribute(k, v)
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as exc:
                    if record_exception:
                        span.record_exception(exc)
                    span.set_status(Status(StatusCode.ERROR, str(exc)))
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            span_name = f"{name}"
            with _tracer.start_as_current_span(span_name) as span:
                if attributes:
                    for k, v in attributes.items():
                        span.set_attribute(k, v)
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as exc:
                    if record_exception:
                        span.record_exception(exc)
                    span.set_status(Status(StatusCode.ERROR, str(exc)))
                    raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def add_span_attribute(key: str, value: Any) -> None:
    """Add attribute to current span (no-op if no active span)."""
    try:
        from opentelemetry import trace
        span = trace.get_current_span()
        span.set_attribute(key, value)
    except Exception:
        pass


def record_event(name: str, attributes: Optional[dict] = None) -> None:
    """Record an event in the current span."""
    try:
        from opentelemetry import trace
        span = trace.get_current_span()
        span.add_event(name, attributes=attributes or {})
    except Exception:
        pass


def get_trace_id() -> Optional[str]:
    """Get current trace ID as hex string, or None if no active span."""
    try:
        from opentelemetry import trace
        span = trace.get_current_span()
        ctx = span.get_span_context()
        if ctx.is_valid:
            return format(ctx.trace_id, '032x')
    except Exception:
        pass
    return None
