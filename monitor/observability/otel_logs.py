# observability/otel_logs.py
import logging
import os
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry._logs import LogRecord

class CleanLogRecordProcessor(BatchLogRecordProcessor):
    def emit(self, log_record: LogRecord):
        # Remove instrumentation scope completely
        log_record.instrumentation_scope = None
        
        # Remove auto-added code context attributes
        if hasattr(log_record, 'attributes') and log_record.attributes:
            # Keep only custom attributes, remove auto code context
            filtered_attrs = {
                k: v for k, v in log_record.attributes.items()
                if not k.startswith('code.')
            }
            log_record.attributes = filtered_attrs
        
        # Create a clean resource without SDK metadata
        clean_resource = Resource.create({
            "service.name": os.getenv("OTEL_SERVICE_NAME", "django-app"),
            "service.namespace": os.getenv("OTEL_SERVICE_NAMESPACE", "backend"),
            "deployment.environment": os.getenv("OTEL_ENVIRONMENT", "development")
        })
        
        # Replace the resource with our clean version
        log_record.resource = clean_resource
        
        # Call the original emit method
        super().emit(log_record)

def setup_logging():
    """Setup OpenTelemetry logging only"""
    try:
        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://grafana-alloy:4317")
        if not endpoint:
            print("OTEL_EXPORTER_OTLP_ENDPOINT not set, skipping OpenTelemetry logging")
            return

        # Create clean resource
        resource = Resource.create({
            "service.name": os.getenv("OTEL_SERVICE_NAME", "django-app"),
            "service.namespace": os.getenv("OTEL_SERVICE_NAMESPACE", "backend"),
            "deployment.environment": os.getenv("OTEL_ENVIRONMENT", "development")
        })

        provider = LoggerProvider(resource=resource)
        exporter = OTLPLogExporter(
            endpoint=endpoint,
            insecure=os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "true").lower() == "true",
        )

        # Use the clean processor
        processor = CleanLogRecordProcessor(
            exporter,
            max_export_batch_size=512,
            schedule_delay_millis=5000,
        )
        
        provider.add_log_record_processor(processor)
        
        # Use the standard LoggingHandler
        handler = LoggingHandler(logger_provider=provider)
        
        # Set log level
        log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, log_level_name, logging.INFO)
        handler.setLevel(log_level)

        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(log_level)

        print(f"OpenTelemetry logging configured for {endpoint}")
        return provider

    except Exception as e:
        print(f"Failed to setup OpenTelemetry logging: {e}")
        return None
