import os
import logging
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor


def setup_telemetry():
    """
    Configure tracing and metrics to export via OTLP/gRPC to local Alloy agent.
    Logs are collected via Docker logs receiver (not OTLP).
    """
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "grpc://alloy-agent:4317")
    insecure = os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "true").lower() == "true"

    resource = Resource.create({
        "service.name": os.getenv("OTEL_SERVICE_NAME", "django-app"),
        "service.version": os.getenv("SERVICE_VERSION", "1.0.0"),
        "deployment.environment": os.getenv("DEPLOYMENT_ENV", "production"),
        "host.name": os.getenv("HOSTNAME", "unknown"),
    })

    # === TRACING ===
    trace_provider = TracerProvider(resource=resource)
    trace_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=insecure)
    trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    trace.set_tracer_provider(trace_provider)

    # === METRICS ===
    metric_exporter = OTLPMetricExporter(endpoint=endpoint, insecure=insecure)
    metric_reader = PeriodicExportingMetricReader(metric_exporter)
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))

    # === LOGGING TO STDOUT (for Docker logs collection) ===
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Add stdout handler if not already present
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        stdout_handler.setFormatter(formatter)
        root_logger.addHandler(stdout_handler)

    # === AUTO-INSTRUMENTATION ===
    DjangoInstrumentor().instrument()
    RequestsInstrumentor().instrument()

    logging.getLogger(__name__).info(
        "OpenTelemetry initialized: Traces & Metrics via gRPC to %s | Logs via Docker", 
        endpoint
    )
