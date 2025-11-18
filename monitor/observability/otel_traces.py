# observability/otel_traces.py
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.django import DjangoInstrumentor

def setup_tracing():
    """Setup OpenTelemetry tracing only"""
    try:
        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://grafana-alloy:4317")
        if not endpoint:
            print("OTEL_EXPORTER_OTLP_ENDPOINT not set, skipping OpenTelemetry tracing")
            return

        resource = Resource.create({
            "service.name": os.getenv("OTEL_SERVICE_NAME", "django-app"),
            "service.namespace": os.getenv("OTEL_SERVICE_NAMESPACE", "backend"),
            "deployment.environment": os.getenv("OTEL_ENVIRONMENT", "development")
        })

        trace.set_tracer_provider(TracerProvider(resource=resource))
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(
                    endpoint=endpoint,
                    insecure=os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "true").lower() == "true",
                )
            )
        )

        # Instrument Django
        DjangoInstrumentor().instrument(
            excluded_urls="^/admin/.*|^/static/.*",
            request_hook=lambda span, request: (
                span.set_attribute("user.id", getattr(request.user, 'id', None)) if hasattr(request, 'user') and request.user else None
            )
        )

        print("OpenTelemetry tracing configured successfully")
        
    except Exception as e:
        print(f"Failed to setup OpenTelemetry tracing: {e}")
