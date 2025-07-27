FROM python:3.10-slim
WORKDIR /app
COPY main.py .
RUN pip install flask opentelemetry-sdk opentelemetry-exporter-otlp opentelemetry-instrumentation-flask
EXPOSE 5000
CMD ["python", "main.py"]
