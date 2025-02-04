provider "aws" {
    region = "eu-west-2"
}

data "aws_ecr_repository" "image-repo" {
    name = "c15-cacareco-lmnh-plants-dashboard"
}

data "aws_ecr_image" "image-version" {
    repository_name = data.aws_ecr_repository.image-repo.name
    image_tag = "latest"
}

data "aws_iam_role" "execution-role" {
  name = "ecsTaskExecutionRole"
}

resource "aws_ecs_task_definition" "c15-cacareco-plants-dashboard-td" {
    family = "c15-cacareco-lmnh-plants"
    container_definitions = jsonencode([
        {
            name      = "c15-cacareco-plants-dashboard-td"
            image     = data.aws_ecr_image.image-version.image_uri
            essential = true
            memory = 512
            environment = [
                {
                    name = "AWS_ACCESS_KEY",
                    value = var.AWS_ACCESS_KEY
                },
                {
                    name = "AWS_SECRET_ACCESS_KEY",
                    value = var.AWS_SECRET_ACCESS_KEY
                },
                {
                    name = "DB_HOST",
                    value = var.DB_HOST
                },
                {
                    name = "DB_PORT",
                    value = var.DB_PORT
                },
                {
                    name = "DB_NAME",
                    value = var.DB_NAME
                },
                {
                    name = "DB_USER",
                    value = var.DB_USER
                },
                {
                    name = "DB_PASSWORD",
                    value = var.DB_PASSWORD
                },
                {
                    name = "SCHEMA_NAME",
                    value = var.SCHEMA_NAME
                }
            ]
            logConfiguration = {
                logDriver = "awslogs"
                "options": {
                    awslogs-group = "/ecs/c15-cacareco-lmnh-plants"
                    awslogs-stream-prefix = "ecs"
                    awslogs-create-group = "true"
                    awslogs-stream-prefix = "ecs"
                    awslogs-region = "eu-west-2"
                }
            }
        }])
    requires_compatibilities = ["FARGATE"]
    network_mode             = "awsvpc"
    cpu                      = "256"
    memory                   = "512"
    execution_role_arn = data.aws_iam_role.execution-role.arn
}