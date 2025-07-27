provider "aws" {
  region = var.aws_region
}

resource "aws_iam_role" "task_execution_role" {
  name = "otel_task_execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "execution_role_policy" {
  role       = aws_iam_role.task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "task_role" {
  name = "otel_task_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "otel_policy" {
  name        = "otel-trace-policy"
  description = "Policy for X-Ray and CloudWatch"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:CreateLogGroup"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "task_role_attach" {
  role       = aws_iam_role.task_role.name
  policy_arn = aws_iam_policy.otel_policy.arn
}

resource "aws_cloudwatch_log_group" "app" {
  name = "/ecs/otel-app"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "collector" {
  name = "/ecs/otel-collector"
  retention_in_days = 7
}

resource "aws_ecs_cluster" "otel_cluster" {
  name = "otel-cluster"
}

resource "aws_ecs_task_definition" "otel_task" {
  family                   = "otel-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.task_execution_role.arn
  task_role_arn            = aws_iam_role.task_role.arn

  container_definitions = jsonencode([
    {
      name      = "app",
      image     = var.app_image,
      essential = true,
      portMappings = [{ containerPort = 5000 }],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = aws_cloudwatch_log_group.app.name,
          awslogs-region        = var.aws_region,
          awslogs-stream-prefix = "ecs"
        }
      },
      environment = [
        {
          name  = "OTEL_EXPORTER_OTLP_ENDPOINT",
          value = "http://localhost:4318"
        },
        {
          name  = "OTEL_TRACES_EXPORTER",
          value = "otlp"
        }
      ]
    },
    {
      name      = "otel-collector",
      image     = "public.ecr.aws/aws-observability/aws-otel-collector:latest",
      essential = true,
      portMappings = [{ containerPort = 4318 }],
      command   = ["--config=/etc/otel-config/otel-config.yaml"],
      mountPoints = [{
        sourceVolume  = "otel-config",
        containerPath = "/etc/otel-config",
        readOnly      = true
      }],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = aws_cloudwatch_log_group.collector.name,
          awslogs-region        = var.aws_region,
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  volume {
    name = "otel-config"
    host_path = null
  }
}

resource "aws_ecs_service" "otel_service" {
  name            = "otel-service"
  cluster         = aws_ecs_cluster.otel_cluster.id
  task_definition = aws_ecs_task_definition.otel_task.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets         = var.subnet_ids
    assign_public_ip = true
    security_groups = [aws_security_group.allow_http.id]
  }
}

resource "aws_security_group" "allow_http" {
  name        = "allow_http"
  description = "Allow HTTP"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
