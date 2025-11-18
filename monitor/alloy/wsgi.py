# wsgi.py
import os
from django.core.wsgi import get_wsgi_application

# Setup OpenTelemetry
try:
    from observability.otel_logs import setup_logging
    from observability.otel_traces import setup_tracing
    
    setup_logging()  # Setup logging first
    setup_tracing()  # Then setup tracing
    
except ImportError as e:
    print(f"OpenTelemetry setup skipped: {e}")
except Exception as e:
    print(f"OpenTelemetry setup failed: {e}")

# Now setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alloy.settings')
application = get_wsgi_application()
