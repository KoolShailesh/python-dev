provider "aws" {
  region = "us-east-1"
  profile = "personal"
}

# resource "aws_s3_bucket" "otel_bucket" {
#   bucket = "otel-emr-bucket-example-sh"
#   force_destroy = true
# }

resource "aws_iam_role" "emr_role" {
  name = "EMR_EC2_DefaultRole_OTEL"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "emr_xray_policy" {
  role       = aws_iam_role.emr_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
}

resource "aws_iam_role_policy_attachment" "readonly_s3_attach" {
  role       = aws_iam_role.emr_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_emr_cluster" "otel_emr" {
  name          = "otel-emr-cluster"
  release_label = "emr-6.14.0"
  applications  = ["Spark"]
  service_role  = "EMR_DefaultRole"
  ec2_attributes {
    key_name = "shailesh-otel-keypair"
    instance_profile = aws_iam_instance_profile.emr_profile.name
    # instance_profile = "EMR_EC2_Profile_OTEL"
    subnet_id                         = "subnet-61319c05"
  }

  master_instance_group {
    instance_type = "m5.xlarge"
  }

  core_instance_group {
    instance_type  = "m5.xlarge"
    instance_count = 2
  }
  

  bootstrap_action {
    name = "Install and Start OTEL Collector"
    path = "s3://otel-emr-bucket-example-sh/emr-bootstrap.sh"
    
  }

  configurations_json = jsonencode([])
}

resource "aws_iam_instance_profile" "emr_profile" {
  name = "EMR_EC2_Profile_OTEL"
  role = aws_iam_role.emr_role.name
}

