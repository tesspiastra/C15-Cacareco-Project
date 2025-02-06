provider "aws" {
  region = "eu-west-2"
  secret_key = var.AWS_SECRET_ACCESS_KEY
  access_key = var.AWS_ACCESS_KEY
}

# ECR

data "aws_ecr_repository" "lambda-image-repo" {
  name = "c15-cacareco-lmnh-plants-etl"
}

data "aws_ecr_image" "lambda-image-version" {
  repository_name = data.aws_ecr_repository.lambda-image-repo.name
  image_tag = "latest"
}

# Permissions for the lambda

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
  name ="c15-cacareco-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda-role-trust-policy-doc.json
}

resource "aws_iam_policy" "lambda-role-permissions-policy" {
  name = "c15-cacareco-lambda-pipeline-policy"
  policy = data.aws_iam_policy_document.lambda-role-permissions-policy-doc.json
}

resource "aws_iam_role_policy_attachment" "lambda-role-policy-attachment" {
  role = aws_iam_role.lambda-role.name
  policy_arn = aws_iam_policy.lambda-role-permissions-policy.arn
}

# Lambda

resource "aws_lambda_function" "pipeline-lambda" {
  function_name = "c15-cacareco-pipeline-lambda"
  role = aws_iam_role.lambda-role.arn
  package_type = "Image"
  image_uri = data.aws_ecr_image.lambda-image-version.image_uri
  environment { 
    variables = {
        DB_HOST = var.DB_HOST
        DB_NAME = var.DB_NAME
        DB_USER = var.DB_USER
        DB_PASSWORD = var.DB_PASSWORD
        DB_PORT = var.DB_PORT
        }
    }
}