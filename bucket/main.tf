provider "aws" {
    region = "eu-west-2"
}

resource "aws_s3_bucket" "cacareco-plants" {
    bucket = "cacareco-plants"
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