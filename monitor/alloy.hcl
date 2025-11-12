discovery.docker "containers" {
  host = "unix:///var/run/docker.sock"
}

discovery.relabel "filter" {
  targets = discovery.docker.containers.targets

  rule {
    source_labels = ["__meta_docker_container_name"]
    regex         = "^(django.*|myapp.*)$"
    action        = "keep"
  }

  rule {
    source_labels = ["__meta_docker_container_id"]
    regex         = "(.*)"
    target_label  = "__path__"
    replacement   = "/var/lib/docker/containers/$1/$1-json.log"
    action        = "replace"
  }
}

loki.source.file "docker_logs" {
  targets    = discovery.relabel.filter.targets
  forward_to = [loki.write.alloy_logs.receiver]
}

otelcol.receiver.otlp "django_app" {
  grpc {
    endpoint = "0.0.0.0:4317"
  }

  http {
    endpoint = "0.0.0.0:4318"
  }

  output {
    logs    = [otelcol.processor.batch.alloy_batch.input]
    metrics = [otelcol.processor.batch.alloy_batch.input]
    traces  = [otelcol.processor.batch.alloy_batch.input]
  }
}

otelcol.processor.batch "alloy_batch" {
  timeout         = "5s"
  send_batch_size = 2000

  output {
    logs    = [otelcol.exporter.loki.alloy_loki_exporter.input]
    metrics = [otelcol.exporter.otlp.metrics_exporter.input]
    traces  = [otelcol.exporter.otlp.traces_exporter.input]
  }
}

otelcol.exporter.loki "alloy_loki_exporter" {
  forward_to = [loki.write.alloy_logs.receiver]
}

loki.write "alloy_logs" {
  endpoint {
    url = env("ALLOY_BASE_URL") + "/v1/logs"
  }

  headers = {
    "Authorization" = env("ALLOY_AUTH_HEADER"),
  }

  tls {
    insecure = (env("ALLOY_TLS_INSECURE") == "true")
  }
}

otelcol.exporter.otlp "metrics_exporter" {
  client {
    endpoint = env("ALLOY_BASE_URL") + "/v1/metrics"

    headers = {
      "Authorization" = env("ALLOY_AUTH_HEADER"),
    }

    tls {
      insecure = (env("ALLOY_TLS_INSECURE") == "true")
    }
  }

  sending_queue {
    enabled       = true
    queue_size    = 20000
    num_consumers = 4
    storage       = "persistent"
  }

  retry_on_failure {
    enabled          = true
    initial_interval = "5s"
    max_interval     = "30s"
    max_elapsed_time = "15m"
  }
}

otelcol.exporter.otlp "traces_exporter" {
  client {
    endpoint = env("ALLOY_BASE_URL") + "/v1/traces"

    headers = {
      "Authorization" = env("ALLOY_AUTH_HEADER"),
    }

    tls {
      insecure = (env("ALLOY_TLS_INSECURE") == "true")
    }
  }

  sending_queue {
    enabled       = true
    queue_size    = 20000
    num_consumers = 4
    storage       = "persistent"
  }

  retry_on_failure {
    enabled          = true
    initial_interval = "5s"
    max_interval     = "30s"
    max_elapsed_time = "15m"
  }
}
