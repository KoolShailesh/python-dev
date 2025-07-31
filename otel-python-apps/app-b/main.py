from flask import Flask, request
from opentelemetry import baggage, trace
from otel_setup import configure_otel
import logging
from kafka import KafkaProducer
import json
from datetime import datetime

app = Flask(__name__)
configure_otel("app-b", app)
logger = logging.getLogger("app-b")

# Kafka setup
KAFKA_BROKER = "34.238.44.149:9092"
KAFKA_TOPIC = "my-topic-redshift"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=str.encode
)

@app.route("/data")
def data():
    correlation_id = baggage.get_baggage("correlation_id")
    logger.info(f"Extracted correlation_id: {correlation_id}")

    # Add correlation_id to span
    span = trace.get_current_span()
    if span and correlation_id:
        span.set_attribute("correlation_id", correlation_id)

    # Format message with timestamp included
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
    message_text = f"Hello from App B at {current_time} IST"

    message = {
        "message": message_text,
        "correlation_id": correlation_id
    }

    # Kafka headers
    # Kafka headers
    kafka_headers = []
    try:
        if correlation_id and isinstance(correlation_id, str):
            kafka_headers.append(("correlation_id", str(correlation_id).encode("utf-8")))
        logger.info(f"Kafka headers: {kafka_headers}")
    except Exception as e:
        logger.error(f"Failed to encode correlation_id header: {e}")

    try:
        producer.send(
            KAFKA_TOPIC,
            key=correlation_id or "unknown",
            value=message,
            headers=kafka_headers
        )
        producer.flush()
        logger.info(f"Kafka message sent with timestamp in message field {current_time}")
    except Exception as e:
         logger.error(f"Failed to send Kafka message: {e}", exc_info=True)


    return "Message sent to Kafka"

if __name__ == "__main__":
    logger.info("App B starting on port 5001")
    app.run(host="0.0.0.0", port=5001)
