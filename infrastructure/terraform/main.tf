# Gagiteck AWS Infrastructure
# Terraform configuration for deploying the full platform

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment for remote state storage
  # backend "s3" {
  #   bucket         = "gagiteck-terraform-state"
  #   key            = "infrastructure/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "gagiteck-terraform-locks"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "Gagiteck"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# Local values
locals {
  name_prefix = "gagiteck-${var.environment}"
  azs         = slice(data.aws_availability_zones.available.names, 0, 2)

  common_tags = {
    Project     = "Gagiteck"
    Environment = var.environment
  }
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  name_prefix         = local.name_prefix
  vpc_cidr            = var.vpc_cidr
  availability_zones  = local.azs
  public_subnet_cidrs = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs

  tags = local.common_tags
}

# ECR Repositories
resource "aws_ecr_repository" "api" {
  name                 = "${local.name_prefix}-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}

resource "aws_ecr_repository" "dashboard" {
  name                 = "${local.name_prefix}-dashboard"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}

# ECR Lifecycle Policy
resource "aws_ecr_lifecycle_policy" "api" {
  repository = aws_ecr_repository.api.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 10 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 10
      }
      action = {
        type = "expire"
      }
    }]
  })
}

resource "aws_ecr_lifecycle_policy" "dashboard" {
  repository = aws_ecr_repository.dashboard.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 10 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 10
      }
      action = {
        type = "expire"
      }
    }]
  })
}

# ALB Module
module "alb" {
  source = "./modules/alb"

  name_prefix        = local.name_prefix
  vpc_id             = module.vpc.vpc_id
  public_subnet_ids  = module.vpc.public_subnet_ids
  certificate_arn    = var.certificate_arn
  domain_name        = var.domain_name

  tags = local.common_tags
}

# RDS Module
module "rds" {
  source = "./modules/rds"

  name_prefix        = local.name_prefix
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids

  db_name            = var.db_name
  db_username        = var.db_username
  db_password        = var.db_password
  db_instance_class  = var.db_instance_class

  allowed_security_groups = [module.ecs.ecs_security_group_id]

  tags = local.common_tags
}

# ElastiCache Module
module "elasticache" {
  source = "./modules/elasticache"

  name_prefix        = local.name_prefix
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  node_type          = var.redis_node_type

  allowed_security_groups = [module.ecs.ecs_security_group_id]

  tags = local.common_tags
}

# ECS Module
module "ecs" {
  source = "./modules/ecs"

  name_prefix        = local.name_prefix
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids

  # Container images
  api_image       = "${aws_ecr_repository.api.repository_url}:latest"
  dashboard_image = "${aws_ecr_repository.dashboard.repository_url}:latest"

  # Target groups from ALB
  api_target_group_arn       = module.alb.api_target_group_arn
  dashboard_target_group_arn = module.alb.dashboard_target_group_arn

  # Environment variables
  database_url = "postgresql://${var.db_username}:${var.db_password}@${module.rds.endpoint}/${var.db_name}"
  redis_url    = "redis://${module.elasticache.endpoint}:6379"

  api_cpu       = var.api_cpu
  api_memory    = var.api_memory
  api_count     = var.api_count

  dashboard_cpu    = var.dashboard_cpu
  dashboard_memory = var.dashboard_memory
  dashboard_count  = var.dashboard_count

  tags = local.common_tags
}

# Secrets Manager for sensitive data
resource "aws_secretsmanager_secret" "app_secrets" {
  name        = "${local.name_prefix}-secrets"
  description = "Gagiteck application secrets"
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    DATABASE_URL     = "postgresql://${var.db_username}:${var.db_password}@${module.rds.endpoint}/${var.db_name}"
    REDIS_URL        = "redis://${module.elasticache.endpoint}:6379"
    NEXTAUTH_SECRET  = var.nextauth_secret
    GITHUB_ID        = var.github_oauth_id
    GITHUB_SECRET    = var.github_oauth_secret
  })
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${local.name_prefix}-api"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "dashboard" {
  name              = "/ecs/${local.name_prefix}-dashboard"
  retention_in_days = 30
}

# S3 Bucket for static assets
resource "aws_s3_bucket" "assets" {
  bucket = "${local.name_prefix}-assets-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_versioning" "assets" {
  bucket = aws_s3_bucket.assets.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "assets" {
  bucket = aws_s3_bucket.assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "assets" {
  bucket = aws_s3_bucket.assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
