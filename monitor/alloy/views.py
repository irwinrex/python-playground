
from django.http import JsonResponse
import time
import logging
from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


def health(request):
    """Simple health endpoint with trace context."""
    with tracer.start_as_current_span("health_check"):
        logger.info("Health check endpoint hit")
        return JsonResponse({"status": "ok"})


def slow_api(request):
    """Example API with simulated latency for tracing."""
    with tracer.start_as_current_span("slow_api"):
        logger.info("Slow API called, simulating latency")
        time.sleep(0.5)
        return JsonResponse({"message": "Response after delay"})
