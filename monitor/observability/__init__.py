# observability/__init__.py
from .otel_logs import setup_logging
from .otel_traces import setup_tracing

__all__ = ['setup_logging', 'setup_tracing']
