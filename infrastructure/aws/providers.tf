provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "ai-devops-engineer-assistant"
      ManagedBy   = "Terraform"
      Environment = var.environment
    }
  }
}
