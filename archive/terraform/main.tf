provider "aws" {
    region = var.REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_ACCESS_KEY
}

resource "aws_s3_bucket" "cacareco-plants" {
    bucket = "c15-cacareco-archive"
    force_destroy = true
}


data "aws_ecr_repository" "lambda-repo" {
  name = "c15/abdul-report-handler"
}

data "aws_ecr_image" "lambda-image" {
  repository_name = data.aws_ecr_repository.lambda-repo.name
  image_tag = "latest"
}

# Trust doc
data "aws_iam_policy_document" "lambda-role-trust-policy-doc" {
    statement {
      effect = "Allow"
      principals {
        type = "Service"
        identifiers = [ "lambda.amazonaws.com" ]
      }
      actions = [
        "sts:AssumeRole"
      ]
    }
}

# Permissions doc
data "aws_iam_policy_document" "lambda-role-permissions-policy-doc" {
    statement {
      effect = "Allow"
      actions = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ]
      resources = [ "arn:aws:logs:eu-west-2:129033205317:*" ]
    }
}

# Role
resource "aws_iam_role" "lambda-role" {
    name = "c15-abdul-lambda-email-terraform-role"
    assume_role_policy = data.aws_iam_policy_document.lambda-role-trust-policy-doc.json
}

# Permissions policy
resource "aws_iam_policy" "lambda-role-permissions-policy" {
    name = "c15-abdul-lambda-email-permissions-policy"
    policy = data.aws_iam_policy_document.lambda-role-permissions-policy-doc.json
}

# Connect the policy to the role
resource "aws_iam_role_policy_attachment" "lambda-role-policy-connection" {
  role = aws_iam_role.lambda-role.name
  policy_arn = aws_iam_policy.lambda-role-permissions-policy.arn
}

resource "aws_lambda_function" "lambda-report" {
  function_name = "c15-abdul-lambda-report"
  timeout = 10
  image_uri = data.aws_ecr_image.lambda-image.image_uri
  package_type = "Image"

  memory_size = 512
  ephemeral_storage {
    size = 512
  }

  role = aws_iam_role.lambda-role.arn

  environment {
    variables = {
    DB_HOST="c15-truck-db.c57vkec7dkkx.eu-west-2.rds.amazonaws.com"
    DB_PORT="3306"
    DB_NAME="abdulrahman_dahir"
    DB_USER="abdulrahman_dahir"
    DB_PASSWORD="Rihad_Namharludba10"
    }
  }
  
}