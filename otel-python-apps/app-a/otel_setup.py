import logging
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

from opentelemetry.instrumentation.logging import LoggingInstrumentor

def configure_tracer(service_name: str):
    resource = Resource.create({SERVICE_NAME: service_name})

    # Setup tracing
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer_provider = trace.get_tracer_provider()
    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint="http://54.174.162.54:4318/v1/traces")
        )
    )

    # Setup logging
    LoggingInstrumentor().instrument(set_logging_format=True)

    log_provider = LoggerProvider(resource=resource)
    handler = LoggingHandler(level=logging.INFO, logger_provider=log_provider)
    logging.getLogger().addHandler(handler)

    log_exporter = OTLPLogExporter(endpoint="http://54.174.162.54:4318/v1/logs")
    log_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
