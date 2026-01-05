variable "region" {
  description = "AWS Region to deploy resources"
  type        = string
  default     = "eu-west-1"
}

variable "db_username" {
  description = "Database administrator username"
  type        = string
  default     = "admin"
}

variable "db_password" {
  description = "Database administrator password"
  type        = string
  sensitive   = true
  # In production, this should come from AWS Secrets Manager, not a variable default!
}