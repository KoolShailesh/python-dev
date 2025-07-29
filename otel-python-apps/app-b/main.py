from flask import Flask
import logging

from opentelemetry import baggage, trace
from otel_setup import configure_otel

# Standard logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app-b")

# Create Flask app
app = Flask(__name__)

# Configure OpenTelemetry tracing, logging, instrumentation
configure_otel("app-b", app)

@app.route("/data")
def data():
    # Enrich span with correlation ID from baggage (for trace observability)
    correlation_id = baggage.get_baggage("correlation.id")
    span = trace.get_current_span()
    if span and correlation_id:
        span.set_attribute("correlation.id", correlation_id)

    logger.info("App B: /data endpoint called")
    return "Hello from App B"

if __name__ == "__main__":
    logger.info("App B starting on port 5001")
    app.run(host="0.0.0.0", port=5001)
