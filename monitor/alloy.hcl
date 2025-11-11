// ==========================================
// Grafana Alloy v1.11.0
// Django → Local Alloy → Remote Alloy / LGTM
// ==========================================

// --- Receivers ---
// Accepts OTLP data (gRPC and HTTP) from Django OpenTelemetry SDK
otelcol.receiver.otlp "from_django" {
  grpc {
    endpoint = "0.0.0.0:4317"
  }
  http {
    endpoint = "0.0.0.0:4318"
  }
}

// Collect logs from Django containers via Docker socket
loki.source.docker "django_logs" {
  docker_url         = "unix:///var/run/docker.sock"
  containers         = ["django*"]
  labels             = { job = "django_logs" }
  forward_to         = [loki.write.alloy_logs.receiver]
}

// --- Processors ---
otelcol.processor.batch "default" {
  timeout = "5s"
  send_batch_size = 2000
}

// --- Exporters (HTTP/Protobuf over HTTPS) ---
// 1️⃣ Traces
otelcol.exporter.otlphttp "alloy_traces" {
  client {
    endpoint = "${env("ALLOY_BASE_URL")}/v1/traces"
    headers = {
      "Authorization" = "Bearer ${env("ALLOY_AUTH_TOKEN")}"
    }
    tls {
      insecure = env("ALLOY_TLS_INSECURE") == "true"
    }
  }
}

// 2️⃣ Metrics
otelcol.exporter.otlphttp "alloy_metrics" {
  client {
    endpoint = "${env("ALLOY_BASE_URL")}/v1/metrics"
    headers = {
      "Authorization" = "Bearer ${env("ALLOY_AUTH_TOKEN")}"
    }
    tls {
      insecure = env("ALLOY_TLS_INSECURE") == "true"
    }
  }
}

// 3️⃣ Logs
loki.write "alloy_logs" {
  endpoint {
    url = "${env("ALLOY_BASE_URL")}/v1/logs"
  }
  headers = {
    "Authorization" = "Bearer ${env("ALLOY_AUTH_TOKEN")}"
  }
  tls {
    insecure = env("ALLOY_TLS_INSECURE") == "true"
  }
}

// --- Pipelines ---
otelcol.service "main" {
  pipelines = {
    traces = [
      otelcol.receiver.otlp.from_django,
      otelcol.processor.batch.default,
      otelcol.exporter.otlphttp.alloy_traces,
    ]
    metrics = [
      otelcol.receiver.otlp.from_django,
      otelcol.processor.batch.default,
      otelcol.exporter.otlphttp.alloy_metrics,
    ]
  }
}
