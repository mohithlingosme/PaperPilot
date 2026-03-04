import os
import logging
import structlog
import uuid
from typing import Optional
from contextvars import ContextVar
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Optional observability deps
try:  # pragma: no cover - defensive import
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    OTEL_AVAILABLE = True
except ImportError:  # pragma: no cover
    OTEL_AVAILABLE = False

try:  # pragma: no cover
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastAPIIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    SENTRY_AVAILABLE = True
except ImportError:  # pragma: no cover
    SENTRY_AVAILABLE = False

# Context variables for correlation IDs
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)
span_id_var: ContextVar[Optional[str]] = ContextVar('span_id', default=None)

# Prometheus metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)
http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation']
)
external_api_duration = Histogram(
    'external_api_duration_seconds',
    'External API call duration in seconds',
    ['service', 'method']
)

# PII redaction helper
def redact_pii(data: dict) -> dict:
    """Redact sensitive information from logs"""
    sensitive_keys = ['password', 'token', 'secret', 'key', 'authorization']
    redacted = {}
    for k, v in data.items():
        if any(sensitive in k.lower() for sensitive in sensitive_keys):
            redacted[k] = '[REDACTED]'
        elif isinstance(v, dict):
            redacted[k] = redact_pii(v)
        else:
            redacted[k] = v
    return redacted

# Structured logging setup
def setup_logging(service_name: str):
    """Setup structured JSON logging"""
    shared_processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        lambda _, __, event_dict: redact_pii(event_dict),
        structlog.processors.JSONRenderer()
    ]

    structlog.configure(
        processors=shared_processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Set up standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
        handlers=[logging.StreamHandler()]
    )

    # Add service and env to all logs
    structlog.contextvars.bind_contextvars(
        service=service_name,
        env=os.getenv('ENV', 'dev')
    )

# Correlation ID middleware
async def correlation_middleware(request: Request, call_next):
    """Middleware to handle correlation IDs"""
    # Get or generate request_id
    request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
    request_id_var.set(request_id)

    # Get trace/span IDs from headers or generate
    trace_id = request.headers.get('X-Trace-ID') or str(uuid.uuid4())
    span_id = request.headers.get('X-Span-ID') or str(uuid.uuid4())
    trace_id_var.set(trace_id)
    span_id_var.set(span_id)

    # Bind to structlog context
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        trace_id=trace_id,
        span_id=span_id
    )

    response = await call_next(request)

    # Add correlation IDs to response headers
    response.headers['X-Request-ID'] = request_id
    response.headers['X-Trace-ID'] = trace_id
    response.headers['X-Span-ID'] = span_id

    return response

# Metrics endpoint
def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Health endpoints
def health_endpoint():
    """Liveness probe"""
    return JSONResponse({"status": "healthy"})

def ready_endpoint():
    """Readiness probe - check dependencies"""
    # TODO: Add actual dependency checks (DB, queue, etc.)
    return JSONResponse({
        "status": "ready",
        "dependencies": {
            "database": "ok",
            "queue": "ok",
            "storage": "ok"
        }
    })

# Tracing setup
def setup_tracing(service_name: str):
    """Setup OpenTelemetry tracing"""
    if os.getenv('OBS_ENABLED', 'false').lower() == 'true' and OTEL_AVAILABLE:
        trace.set_tracer_provider(TracerProvider())
        tracer_provider = trace.get_tracer_provider()

        otlp_exporter = OTLPSpanExporter(
            endpoint=os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4317'),
            insecure=True,
        )
        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider.add_span_processor(span_processor)

        # Instrument FastAPI and SQLAlchemy
        FastAPIInstrumentor.instrument()
        SQLAlchemyInstrumentor.instrument()

# Sentry setup
def setup_sentry():
    """Setup Sentry error tracking"""
    if os.getenv('SENTRY_DSN') and SENTRY_AVAILABLE:
        sentry_sdk.init(
            dsn=os.getenv('SENTRY_DSN'),
            integrations=[
                FastAPIIntegration(),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=1.0,
            environment=os.getenv('ENV', 'dev'),
            release=os.getenv('RELEASE_VERSION', 'dev'),
        )

# Initialize observability
def init_observability(app, service_name: str):
    """Initialize all observability components"""
    setup_logging(service_name)
    setup_tracing(service_name)
    setup_sentry()

    # Add middleware
    app.middleware("http")(correlation_middleware)

    # Add routes
    app.get("/metrics")(metrics_endpoint)
    app.get("/health")(health_endpoint)
    app.get("/ready")(ready_endpoint)

    logger = structlog.get_logger()
    logger.info("Observability initialized", service=service_name)
