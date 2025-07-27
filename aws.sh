# Update with your bucket name
export BUCKET_NAME=otel-emr-bucket-example
export REGION=us-east-1

# Create bucket
aws s3 mb s3://$BUCKET_NAME

# Upload OTEL config and bootstrap script
aws s3 cp otel-config.yaml s3://$BUCKET_NAME/
aws s3 cp emr-bootstrap.sh s3://$BUCKET_NAME/
