#!/bin/bash


# # Use contrib version for aws exporters (awsemf, awsxray)
# wget -L https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.99.0/otelcol-contrib_0.99.0_linux_amd64.rpm -O otelcol.rpm
# sudo rpm -ivh otelcol.rpm

# Download and install OpenTelemetry Collector Contrib RPM
curl -L https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.99.0/otelcol-contrib_0.99.0_linux_amd64.rpm -o otelcol.rpm

sudo rpm -ivh otelcol.rpm


# Create OTEL config file
cat <<EOF | sudo tee /etc/otel-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
      http:

processors:
  batch:
  resource:
    attributes:
      - key: service.namespace
        value: otel-example

exporters:
  awsxray:
    region: us-east-1
  awsemf:
    namespace: OtelExampleApp
    log_group_name: /otel/example/logs
  logging:
    loglevel: debug

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch, resource]
      exporters: [awsxray, logging]

    logs:
      receivers: [otlp]
      processors: [batch, resource]
      exporters: [awsemf, logging]

EOF

# Enable and start OTEL Collector
sudo systemctl enable otelcol-contrib
sudo systemctl start otelcol-contrib