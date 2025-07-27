from flask import Flask, request
import requests, json
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

app = Flask(__name__)
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint="http://44.202.146.252:4317", insecure=True)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route("/login")
def login():
    span = trace.get_current_span()
    trace_id = format(span.get_span_context().trace_id, "032x")
    print(json.dumps({
        "service": "auth-service",
        "message": "Login requested",
        "trace_id": trace_id
    }))
    requests.get("http://orders-service:5001/process")
    return "Login processed!"

app.run(host="0.0.0.0", port=5000)