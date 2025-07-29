from flask import Flask, request
import requests
import logging
import datetime
import time

from opentelemetry import trace
from opentelemetry.baggage import set_baggage
from opentelemetry.context import attach, detach
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from otel_setup import configure_otel  #  updated import

# Setup standard logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app-a")

# Setup Flask app
app = Flask(__name__)

# Configure OpenTelemetry (tracing + logging)
tracer = configure_otel("app-a", app)  #  updated function call

# Generate correlation ID: DDMMYYHHMMSS.nnn
def generate_correlation_id():
    now = datetime.datetime.now()
    nanosec = int(time.time_ns() % 1_000_000_000)
    return now.strftime("%d%m%y%H%M%S") + f".{nanosec:03d}"[:3]  # Keep 3 digits

@app.route("/")
def index():
    correlation_id = generate_correlation_id()

    # Inject correlation ID into context baggage
    token = attach(set_baggage("correlation.id", correlation_id))

    # Add correlation ID to current span
    span = trace.get_current_span()
    span.set_attribute("correlation.id", correlation_id)

    # Log correlation ID and make downstream call
    app.logger.info(f"Calling App B with correlation ID: {correlation_id}")
    response = requests.get("http://localhost:5001/data")

    # Detach context after request
    detach(token)

    return f"App A called App B: {response.text}"

if __name__ == "__main__":
    logger.info("App A starting on port 5000")
    app.run(host="0.0.0.0", port=5000)
