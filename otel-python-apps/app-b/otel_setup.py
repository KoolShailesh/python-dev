# otel_setup.py

import os
import sys
import logging
from opentelemetry import trace, baggage
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

# OTEL Collector endpoint
OTEL_COLLECTOR_HOST = "3.82.145.211"
OTEL_COLLECTOR_PORT = "4318"
OTEL_COLLECTOR_BASE_URL = f"http://{OTEL_COLLECTOR_HOST}:{OTEL_COLLECTOR_PORT}"


class OTELFormatter(logging.Formatter):
    def format(self, record):
        try:
            span = trace.get_current_span()
            ctx = span.get_span_context() if span else None

            trace_id = format(ctx.trace_id, "032x") if ctx and ctx.trace_id else "-"
            span_id = format(ctx.span_id, "016x") if ctx and ctx.span_id else "-"
            correlation_id = baggage.get_baggage("correlation_id") or "-"

            record.trace_id = trace_id
            record.span_id = span_id
            record.correlation_id = correlation_id

            # Get base message
            msg = record.getMessage()

            # Append exception info if present and safely convertible
            if record.exc_info:
                try:
                    msg += "\n" + self.formatException(record.exc_info)
                except Exception:
                    pass

            return (
                f"[{self.formatTime(record)}] "
                f"[{record.levelname}] "
                f"trace_id={trace_id} "
                f"span_id={span_id} "
                f"correlation_id={correlation_id} - "
                f"{msg}"
            )
        except Exception:
            return super().format(record)


def configure_otel(service_name: str, app=None):
    resource = Resource.create({SERVICE_NAME: service_name})

    # -------- Tracing --------
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    trace_exporter = OTLPSpanExporter(endpoint=f"{OTEL_COLLECTOR_BASE_URL}/v1/traces")
    tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))

    # -------- Logging --------
    LoggingInstrumentor().instrument(set_logging_format=False)

    log_provider = LoggerProvider(resource=resource)
    log_exporter = OTLPLogExporter(endpoint=f"{OTEL_COLLECTOR_BASE_URL}/v1/logs")
    log_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

    otel_handler = LoggingHandler(level=logging.INFO, logger_provider=log_provider)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(OTELFormatter(fmt="%(message)s"))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = []  # Clear existing
    root_logger.addHandler(console_handler)
    root_logger.addHandler(otel_handler)

    # -------- Instrument Flask and Requests --------
    if app:
        FlaskInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()

    return trace.get_tracer(service_name)
