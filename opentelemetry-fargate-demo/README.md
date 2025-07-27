# OpenTelemetry on AWS Fargate

This project deploys a Python Flask application with OpenTelemetry SDK to AWS Fargate using the AWS Distro for OpenTelemetry (ADOT) Collector as a sidecar. It exports traces to AWS X-Ray and metrics to CloudWatch.

## Contents
- Python app with OTLP exporter
- ADOT Collector config for X-Ray and CloudWatch
- Terraform infra: ECS Fargate + IAM + CloudWatch

## Steps to Run

1. **Build and Push Docker Image**:
   ```bash
   docker build -t my-otel-app ./app
   aws ecr create-repository --repository-name my-otel-app
   docker tag my-otel-app:latest <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/my-otel-app
   aws ecr get-login-password | docker login --username AWS --password-stdin <your-registry>
   docker push <your-repo-url>
   ```

2. **Configure and Apply Terraform**:
   ```bash
   cd terraform
   terraform init
   terraform apply
   ```

3. **Test the App**:
   Visit `http://<ECS-Service-Public-IP>:5000/` or use:
   ```bash
   curl http://<public-ip>:5000/
   ```

4. **View Traces & Logs**:
   - **X-Ray Console** → Service Map & Traces
   - **CloudWatch Logs** → `/ecs/otel-app`, `/ecs/otel-collector`

## Cleanup
```bash
terraform destroy
```
