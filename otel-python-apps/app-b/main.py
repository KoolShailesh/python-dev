from flask import Flask
import logging

from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor  # NEW
from otel_setup import configure_tracer

# Standard Python logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app-b")

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
LoggingInstrumentor().instrument(set_logging_format=True)  # NEW

configure_tracer("app-b")

@app.route("/data")
def data():
    logger.info("App B: /data endpoint called")
    return "Hello from App B"

if __name__ == "__main__":
    logger.info("App B starting on port 5001")
    app.run(port=5001)
