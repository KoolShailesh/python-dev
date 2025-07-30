from flask import Flask,request 
from opentelemetry import baggage, trace
from otel_setup import configure_otel
import logging

app = Flask(__name__)
# Configure OpenTelemetry for App B.
# The `otel_setup.py` will set up the X-Ray propagator to extract
# trace context and baggage from incoming requests.
configure_otel("app-b", app)
logger = logging.getLogger("app-b") # Get a named logger for App B

@app.route("/data")
def data():
    """
    Endpoint for App B to receive requests from App A.
    It retrieves the correlation_id from baggage and adds it as a span attribute.
    """

    # --- ADD THIS FOR DEBUGGING ---
    logger.info(f"App B: Incoming headers: {request.headers}")
    # --- END DEBUGGING ADDITION ---

    # Retrieve correlation_id from baggage.
    # The AWSXRayPropagator configured in otel_setup.py will
    # automatically extract this from the incoming X-Amzn-Trace-Id header if present.
    correlation_id = baggage.get_baggage("correlation_id")

    # Get the current span and set the correlation_id as an attribute.
    # This ensures the correlation_id appears in the trace for App B.
    span = trace.get_current_span()
    if span and correlation_id:
        span.set_attribute("correlation_id", correlation_id)

    # Log the activity in App B.
    # The OTELFormatter in otel_setup.py will pick up the correlation_id from baggage
    # and include it in the console log output.
    logger.info("App B: /data endpoint called")
    return "Hello from App B"

if __name__ == "__main__":
    logger.info("App B starting on port 5001")
    app.run(host="0.0.0.0", port=5001)