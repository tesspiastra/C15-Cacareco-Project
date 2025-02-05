provider "aws" {
    region = var.REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_ACCESS_KEY
}

resource "aws_s3_bucket" "cacareco-plants" {
    bucket = "c15-cacareco-archive"
    force_destroy = true
}

