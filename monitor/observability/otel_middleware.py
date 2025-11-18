# observability/otel_middleware.py
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class OpenTelemetryLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log all HTTP requests and responses
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def should_log_request(self, path):
        """Determine if we should log this request"""
        excluded_paths = [
            '/favicon.ico',
            '/static/',
            '/admin/',
            '/health',
            '/health/'
        ]
        return not any(path.startswith(excluded) for excluded in excluded_paths)

    def process_request(self, request):
        # Skip logging for excluded paths
        if not self.should_log_request(request.path):
            return None
            
        # Start timer when request comes in
        request.start_time = time.time()
        
        # Get client IP
        client_ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:200]
        
        # Log request details
        logger.info(
            f"Request: {request.method} {request.path}",
            extra={
                "http.method": request.method,
                "http.route": request.path,
                "http.url": request.build_absolute_uri()[:500],
                "http.user_agent": user_agent,
                "http.client_ip": client_ip,
                "log.source": "middleware"
            }
        )
        return None

    def process_response(self, request, response):
        # Skip logging for excluded paths
        if not self.should_log_request(request.path):
            return response
            
        # Calculate request duration
        duration = 0
        if hasattr(request, 'start_time'):
            duration = (time.time() - request.start_time) * 1000

        # Log response details
        logger.info(
            f"Response: {request.method} {request.path} - {response.status_code}",
            extra={
                "http.method": request.method,
                "http.route": request.path,
                "http.status_code": response.status_code,
                "http.duration_ms": round(duration, 2),
                "log.source": "middleware"
            }
        )
        return response

    def process_exception(self, request, exception):
        # Skip logging for excluded paths
        if not self.should_log_request(request.path):
            return None
            
        # Log exceptions
        logger.error(
            f"Error: {request.method} {request.path} - {str(exception)}",
            extra={
                "http.method": request.method,
                "http.route": request.path,
                "error.message": str(exception)[:500],
                "error.type": type(exception).__name__,
                "log.source": "middleware"
            },
            exc_info=True
        )
        return None

    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip
