provider "aws" {
  access_key = var.AWS_ACCESS_KEY
  secret_key = var.AWS_SECRET_ACCESS_KEY
  region = var.REGION
}


resource "aws_s3_bucket" "archive_bucket" {
  bucket = "c15-cacareco-archive"
  force_destroy = true
}