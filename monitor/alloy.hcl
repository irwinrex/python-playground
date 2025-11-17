// -------------------------------------------------------------
// OTLP RECEIVER (Django logs + traces)
// -------------------------------------------------------------
otelcol.receiver.otlp "django_otel" {
  grpc { endpoint = "0.0.0.0:4317" }
  http { endpoint = "0.0.0.0:4318" }

  // Send logs + traces into the batch processors
  output {
    logs   = [otelcol.processor.resourcedetection.add_env_label.input]
    traces = [otelcol.processor.batch.traces_batch.input]
  }
}

// -------------------------------------------------------------
// RESOURCE PROCESSOR (Add static labels/attributes)
// -------------------------------------------------------------
otelcol.processor.resourcedetection "add_env_label" {
  detectors = ["static"]
  static_resource {
    attributes = {
      "app_env" = "local",
    }
  }
  output {
    logs = [otelcol.processor.batch.logs_batch.input]
  }
}

// -------------------------------------------------------------
// BATCH PROCESSORS
// -------------------------------------------------------------
otelcol.processor.batch "logs_batch" {
  output {
    logs = [otelcol.exporter.loki.django_loki.input]
  }
}

otelcol.processor.batch "traces_batch" {
  output {
    traces = [otelcol.exporter.otlp.tempo.input]
  }
}

// -------------------------------------------------------------
// EXPORT LOGS → LOKI
// -------------------------------------------------------------
otelcol.exporter.loki "django_loki" {
  forward_to = [loki.write.loki_push.receiver]
}

// -------------------------------------------------------------
// AUTH
// -------------------------------------------------------------
otelcol.auth.basic "tempo_auth" {
  username = env("ALLOY_AUTH_USERNAME")
  password = env("ALLOY_AUTH_PASSWORD")
}

// -------------------------------------------------------------
// EXPORT TRACES → TEMPO
// -------------------------------------------------------------
otelcol.exporter.otlp "tempo" {
  client {
    endpoint = env("ALLOY_TEMPO_URL")

    auth = otelcol.auth.basic.tempo_auth.handler

    tls {
      insecure_skip_verify = env("ALLOY_TLS_INSECURE") == "false"
    }
  }
}



// -------------------------------------------------------------
// LOKI WRITE ENDPOINT
// -------------------------------------------------------------
loki.write "loki_push" {
  endpoint {
    url = env("ALLOY_LOKI_URL")

    basic_auth {
      username = env("ALLOY_AUTH_USERNAME")
      password = env("ALLOY_AUTH_PASSWORD")
    }

    tls_config {
      insecure_skip_verify = true
    }
  }
}
