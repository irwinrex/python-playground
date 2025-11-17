// -------------------------------------------------------------
// OTLP RECEIVER (Django logs + traces)
// -------------------------------------------------------------
otelcol.receiver.otlp "django_otel" {
  grpc { endpoint = "0.0.0.0:4317" }
  http { endpoint = "0.0.0.0:4318" }

  // Send logs + traces into the batch processors
  output {
    logs   = [otelcol.processor.batch.logs_batch.input]
    traces = [otelcol.processor.batch.traces_batch.input]
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
// otelcol.auth.basic "tempo_auth" {
//   username = env("ALLOY_AUTH_USERNAME")
//   password = env("ALLOY_AUTH_PASSWORD")
// }

// -------------------------------------------------------------
// EXPORT TRACES → TEMPO
// -------------------------------------------------------------
otelcol.exporter.otlp "tempo" {
  client {
    endpoint = env("ALLOY_TEMPO_URL")

    // auth = tempo_auth

    tls {
      insecure_skip_verify = env("ALLOY_TLS_INSECURE") == "false"
    }
  }
}

// -------------------------------------------------------------
// LOKI SOURCE (Docker logs)
// -------------------------------------------------------------
loki.source.docker "docker_logs" {
  host = "unix:///var/run/docker.sock"
  targets = discovery.docker.all.targets

  forward_to = [loki.process.enrich_labels.receiver]
}

// -------------------------------------------------------------
// DISCOVERY
// -------------------------------------------------------------
discovery.docker "all" {
  host = "unix:///var/run/docker.sock"
}

// -------------------------------------------------------------
// PROCESS LOGS
// -------------------------------------------------------------
loki.process "enrich_labels" {
  // stage.match {
  //   selector = "{job=\"docker\"}"
  //   stage.label_drop {
  //     values = ["filename"]
  //   }
  // }

  // stage.match {
  //   selector = "{job=\"docker\"}"
  //   stage.labels {
  //     values = {
  //       local_service = "django-app",
  //     }
  //   }
  // }

  forward_to = [loki.write.loki_push.receiver]
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
