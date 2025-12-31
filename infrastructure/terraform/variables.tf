# Gagiteck Terraform Variables

# General
variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

# Networking
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.20.0/24"]
}

# Domain & SSL
variable "domain_name" {
  description = "Domain name for the application (e.g., gagiteck.com)"
  type        = string
  default     = ""
}

variable "certificate_arn" {
  description = "ARN of ACM certificate for HTTPS"
  type        = string
  default     = ""
}

# Database (RDS)
variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "gagiteck"
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "gagiteck_admin"
  sensitive   = true
}

variable "db_password" {
  description = "PostgreSQL master password"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

# Redis (ElastiCache)
variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

# ECS - API Service
variable "api_cpu" {
  description = "CPU units for API service (1024 = 1 vCPU)"
  type        = number
  default     = 256
}

variable "api_memory" {
  description = "Memory for API service in MB"
  type        = number
  default     = 512
}

variable "api_count" {
  description = "Number of API tasks to run"
  type        = number
  default     = 1
}

# ECS - Dashboard Service
variable "dashboard_cpu" {
  description = "CPU units for Dashboard service"
  type        = number
  default     = 256
}

variable "dashboard_memory" {
  description = "Memory for Dashboard service in MB"
  type        = number
  default     = 512
}

variable "dashboard_count" {
  description = "Number of Dashboard tasks to run"
  type        = number
  default     = 1
}

# Authentication
variable "nextauth_secret" {
  description = "NextAuth.js secret for session encryption"
  type        = string
  sensitive   = true
  default     = ""
}

variable "github_oauth_id" {
  description = "GitHub OAuth App Client ID"
  type        = string
  default     = ""
}

variable "github_oauth_secret" {
  description = "GitHub OAuth App Client Secret"
  type        = string
  sensitive   = true
  default     = ""
}
