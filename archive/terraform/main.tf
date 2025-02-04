provider "aws" {
    region = var.REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_ACCESS_KEY
}

resource "aws_s3_bucket" "cacareco-plants" {
    bucket = "c15-cacareco-archive"
    force_destroy = true
}

resource "aws_iam_policy" "s3_access_policy" {
    name        = "s3-read-write-access"
    description = "Policy granting read and write access to the S3 bucket"

    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
        {
            Effect   = "Allow"
            Action   = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
            Resource = [
            "arn:aws:s3:::cacareco_plants",
            "arn:aws:s3:::cacareco_plants/*"
            ]
        }
        ]
    })
}

resource "aws_iam_group" "s3_access_group" {
    name = "s3-read-write-cacareco-group"
}

resource "aws_iam_group_policy_attachment" "cacareco_policy_attachment" {
    group      = aws_iam_group.s3_access_group.name
    policy_arn = aws_iam_policy.s3_access_policy.arn
}

resource "aws_iam_user_group_membership" "user_group_membership" {
    for_each = toset([
    "c15-trainee-abdulrahman-dahir", 
    "c15-trainee-benjamin-smith", 
    "c15-trainee-tess-piastra", 
    "c15-trainee-zander-rackevic"
  ])

  user   = each.value
  groups = [aws_iam_group.s3_access_group.name]
}

# Lambda build

data "aws_ecr_repository" "lambda-repo" {
  name = "c15-cacareco-lmnh-plants-archive"
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
    name = "c15-cacareco-archive-role"
    assume_role_policy = data.aws_iam_policy_document.lambda-role-trust-policy-doc.json
}

# Permissions policy
resource "aws_iam_policy" "lambda-role-permissions-policy" {
    name = "c15-cacareco-lambda-permissions-policy"
    policy = data.aws_iam_policy_document.lambda-role-permissions-policy-doc.json
}

# Connect the policy to the role
resource "aws_iam_role_policy_attachment" "lambda-role-policy-connection" {
  role = aws_iam_role.lambda-role.name
  policy_arn = aws_iam_policy.lambda-role-permissions-policy.arn
}

resource "aws_lambda_function" "lambda-report" {
  function_name = "c15-cacareco-archive-lambda"
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
    DB_HOST=var.DB_HOST
    DB_PORT=var.DB_PORT
    DB_NAME=var.DB_NAME
    DB_USER=var.DB_USER
    DB_PASSWORD=var.DB_PASSWORD
    SCHEMA_NAME=var.SCHEMA_NAME
    }
  }
  
}