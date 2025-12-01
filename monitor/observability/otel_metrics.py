# observability/otel_metrics.py

import os
import time
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource

def setup_metrics():
    """Setup OpenTelemetry metrics for API: counters and duration histogram with service.name tagging."""
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "grafana-alloy:4317")
    insecure = os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "true").lower() == "true"
    export_interval = int(os.getenv("OTEL_METRICS_EXPORT_INTERVAL", "30000"))

    exporter = OTLPMetricExporter(
        endpoint=endpoint,
        insecure=insecure
    )

    reader = PeriodicExportingMetricReader(
        exporter,
        export_interval_millis=export_interval
    )

    resource = Resource.create({
        "service.name": os.getenv("OTEL_SERVICE_NAME", "django-app"),
        "service.namespace": os.getenv("OTEL_SERVICE_NAMESPACE", "backend"),
        "deployment.environment": os.getenv("OTEL_ENVIRONMENT", "development")
    })
    provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(provider)

    meter = metrics.get_meter(__name__, version="1.0.0")

    request_counter = meter.create_counter(
        name="http.server.requests_total",
        description="Total HTTP server requests by status code class",
        unit="1"
    )

    request_latency = meter.create_histogram(
        name="http.server.duration_seconds",
        description="HTTP server request processing duration in seconds",
        unit="s"
    )

    return {
        "meter": meter,
        "counter": request_counter,
        "histogram": request_latency
    }

def record_request(counter, histogram, *, status_code, method, route, duration_s):
    """Record a request: increment counter and record latency with service attribute."""
    service_name = os.getenv("OTEL_SERVICE_NAME", "django-app")
    status_class = f"{status_code // 100}xx"
    attributes = {
        "service.name": service_name,
        "http.method": method,
        "http.route": route,
        "http.status_code_class": status_class
    }

    counter.add(1, attributes)
    histogram.record(duration_s, attributes)
