resource "aws_s3_bucket" "logs_bucket" {
  bucket = "infra-ops-logs-2026-secure"
  
  tags = {
    Environment = "Production"
    Purpose     = "Audit Logs"
  }
}

resource "aws_s3_bucket_versioning" "logs_ver" {
  bucket = aws_s3_bucket.logs_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}