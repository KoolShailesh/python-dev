from flask import Flask, request
import requests
import logging

from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor  # NEW
from otel_setup import configure_tracer

# Standard Python logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app-a")

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
LoggingInstrumentor().instrument(set_logging_format=True)  # NEW

configure_tracer("app-a")

@app.route("/")
def index():
    logger.info("App A: Received request to /")
    response = requests.get("http://localhost:5001/data")
    logger.info("App A: Received response from App B")
    return f"App A called App B: {response.text}"

if __name__ == "__main__":
    logger.info("App A starting on port 5000")
    app.run(port=5000)
