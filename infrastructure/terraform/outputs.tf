# Gagiteck Terraform Outputs

# VPC
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

# ECR
output "api_ecr_repository_url" {
  description = "ECR repository URL for API"
  value       = aws_ecr_repository.api.repository_url
}

output "dashboard_ecr_repository_url" {
  description = "ECR repository URL for Dashboard"
  value       = aws_ecr_repository.dashboard.repository_url
}

# ALB
output "alb_dns_name" {
  description = "ALB DNS name"
  value       = module.alb.alb_dns_name
}

output "alb_zone_id" {
  description = "ALB hosted zone ID for Route53"
  value       = module.alb.alb_zone_id
}

# Database
output "rds_endpoint" {
  description = "RDS endpoint"
  value       = module.rds.endpoint
  sensitive   = true
}

output "rds_port" {
  description = "RDS port"
  value       = module.rds.port
}

# Redis
output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = module.elasticache.endpoint
  sensitive   = true
}

# ECS
output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "api_service_name" {
  description = "API ECS service name"
  value       = module.ecs.api_service_name
}

output "dashboard_service_name" {
  description = "Dashboard ECS service name"
  value       = module.ecs.dashboard_service_name
}

# S3
output "assets_bucket_name" {
  description = "S3 assets bucket name"
  value       = aws_s3_bucket.assets.id
}

# Secrets
output "secrets_arn" {
  description = "Secrets Manager ARN"
  value       = aws_secretsmanager_secret.app_secrets.arn
}

# Deployment URLs
output "api_url" {
  description = "API URL"
  value       = var.domain_name != "" ? "https://api.${var.domain_name}" : "http://${module.alb.alb_dns_name}:8000"
}

output "dashboard_url" {
  description = "Dashboard URL"
  value       = var.domain_name != "" ? "https://${var.domain_name}" : "http://${module.alb.alb_dns_name}"
}
