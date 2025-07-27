from flask import Flask
import json
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor

app = Flask(__name__)
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317", insecure=True)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))
FlaskInstrumentor().instrument_app(app)

@app.route("/process")
def process():
    span = trace.get_current_span()
    trace_id = format(span.get_span_context().trace_id, "032x")
    print(json.dumps({
        "service": "orders-service",
        "message": "Order processed",
        "trace_id": trace_id
    }))
    return "Order done!"

app.run(host="0.0.0.0", port=5001)