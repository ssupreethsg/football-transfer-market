resource "aws_s3_bucket" "staging" {
  bucket = "${var.project_name}-staging-bucket"
}

resource "aws_s3_bucket_public_access_block" "staging" {
  bucket = aws_s3_bucket.staging.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
