from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
import os

reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="http://grafana-alloy:4317", insecure=True),
    export_interval_millis=30000)
metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))
