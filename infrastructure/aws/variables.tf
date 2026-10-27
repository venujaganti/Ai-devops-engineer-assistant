variable "aws_region" {
  description = "AWS region for the deployment."
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Environment label applied to AWS resources."
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "environment must be dev, staging, or production."
  }
}

variable "app_image" {
  description = "Fully qualified, published OCI image URI for the assistant."
  type        = string
  validation {
    condition     = length(trimspace(var.app_image)) > 0 && can(regex(":", var.app_image))
    error_message = "app_image must be a fully qualified image URI with a tag or digest."
  }
}

variable "instance_type" {
  description = "EC2 instance type; choose a size appropriate for your load."
  type        = string
  default     = "t3.small"
}

variable "vpc_cidr" {
  description = "CIDR for the dedicated VPC."
  type        = string
  default     = "10.42.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR for the public application subnet."
  type        = string
  default     = "10.42.1.0/24"
}

variable "grafana_allowed_cidr" {
  description = "Optional trusted CIDR allowed to reach Grafana on TCP/3000. Leave empty to keep Grafana private and use SSM port forwarding."
  type        = string
  default     = ""
  validation {
    condition     = var.grafana_allowed_cidr == "" || can(cidrhost(var.grafana_allowed_cidr, 0))
    error_message = "grafana_allowed_cidr must be a valid CIDR or an empty string."
  }
}

variable "grafana_admin_password" {
  description = "Initial Grafana admin password. Stored in Terraform state and EC2 user data; use a secret backend for production."
  type        = string
  sensitive   = true
  validation {
    condition     = length(var.grafana_admin_password) >= 16
    error_message = "grafana_admin_password must be at least 16 characters long."
  }
}

variable "ssh_allowed_cidr" {
  description = "Optional trusted CIDR allowed SSH access. Keep empty and use AWS Systems Manager by default."
  type        = string
  default     = ""
  validation {
    condition     = var.ssh_allowed_cidr == "" || can(cidrhost(var.ssh_allowed_cidr, 0))
    error_message = "ssh_allowed_cidr must be a valid CIDR or an empty string."
  }
}

variable "gemini_secret_arn" {
  description = "Optional ARN of a Secrets Manager secret whose SecretString contains the Gemini API key."
  type        = string
  default     = ""
  validation {
    condition     = var.gemini_secret_arn == "" || can(regex("^arn:[^:]+:secretsmanager:[^:]+:[0-9]{12}:secret:.+$", var.gemini_secret_arn))
    error_message = "gemini_secret_arn must be a Secrets Manager secret ARN or an empty string."
  }
}
