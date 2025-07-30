from flask import Flask
from opentelemetry import baggage, trace
from otel_setup import configure_otel
import logging

app = Flask(__name__)
configure_otel("app-b", app)
logger = logging.getLogger("app-b")

@app.route("/data")
def data():
    correlation_id = baggage.get_baggage("correlation_id")
    span = trace.get_current_span()
    if span and correlation_id:
        span.set_attribute("correlation_id", correlation_id)

    logger.info("App B: /data endpoint called")
    return "Hello from App B"

if __name__ == "__main__":
    logger.info("App B starting on port 5001")
    app.run(host="0.0.0.0", port=5001)
