# OpenTelemetry AWS Example

This example demonstrates tracing and logging for two Python microservices using OpenTelemetry, with export to AWS X-Ray and CloudWatch Logs. It includes local Docker setup and EMR deployment support.

---

## ✅ Components

- **auth-service** and **orders-service** (Flask apps)
- **OpenTelemetry SDK** for Python
- **OpenTelemetry Collector** (local and EMR)
- **AWS Exporters**:
  - Traces → X-Ray
  - Logs → CloudWatch Logs

---

## 🚀 Local Setup

```bash
docker-compose up --build
```

Test endpoint:
```bash
curl http://localhost:5000/login
```

---

## 📦 EMR Setup

### Step 1: Create an S3 bucket and upload these files:
- `otel-config.yaml`
- `emr-bootstrap.sh`

Update the `emr-bootstrap.sh` script to download these files from S3 and configure the collector.

### Step 2: Launch EMR Cluster with Bootstrap Action

Use the AWS Console or CLI:

```bash
aws emr create-cluster   --name "EMRWithOtel"   --release-label emr-6.14.0   --applications Name=Spark   --instance-type m5.xlarge   --instance-count 3   --use-default-roles   --ec2-attributes KeyName=myKey   --bootstrap-actions Path=s3://your-bucket/emr-bootstrap.sh
```

---

## 🛠 Terraform/CloudFormation (Coming Soon)

You can use the following starter modules:
- EMR cluster with bootstrap action
- IAM role with access to X-Ray and CloudWatch Logs
- S3 bucket with `otel-config.yaml` and bootstrap script

Let me know if you want the full Terraform or CloudFormation templates added to this repo.