variable "aws_region" {
  default = "us-east-1"
}

variable "app_image" {
  description = "ECR image for the application"
}

variable "vpc_id" {
  description = "VPC ID"
}

variable "subnet_ids" {
  type = list(string)
  description = "List of public subnet IDs"
}
