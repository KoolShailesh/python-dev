import os
import logging
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# -------- HARDCODE OTEL COLLECTOR CONFIG --------
OTEL_COLLECTOR_HOST = "44.202.25.247"
OTEL_COLLECTOR_PORT = "4318"
OTEL_COLLECTOR_BASE_URL = f"http://{OTEL_COLLECTOR_HOST}:{OTEL_COLLECTOR_PORT}"
# -------------------------------------


def configure_otel(service_name: str, app=None):
    resource = Resource.create({SERVICE_NAME: service_name})

    # -------- Tracing Setup --------
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer_provider = trace.get_tracer_provider()

    trace_exporter = OTLPSpanExporter(endpoint=f"{OTEL_COLLECTOR_BASE_URL}/v1/traces")
    tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))

    # -------- Logging Setup --------
    LoggingInstrumentor().instrument(set_logging_format=True)

    log_provider = LoggerProvider(resource=resource)
    log_exporter = OTLPLogExporter(endpoint=f"{OTEL_COLLECTOR_BASE_URL}/v1/logs")
    log_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

    handler = LoggingHandler(level=logging.INFO, logger_provider=log_provider)
    logging.getLogger().addHandler(handler)

    # -------- Instrumentations --------
    if app:
        FlaskInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()

    return trace.get_tracer(service_name)
