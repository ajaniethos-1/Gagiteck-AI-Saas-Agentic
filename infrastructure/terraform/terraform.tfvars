# Gagiteck Terraform Variables Example
# Copy this file to terraform.tfvars and fill in your values

# General
aws_region  = "us-east-1"
environment = "dev"  # dev, staging, or prod

# Networking
vpc_cidr             = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs = ["10.0.10.0/24", "10.0.20.0/24"]

# Domain & SSL (optional - leave empty for dev)
domain_name     = ""  # e.g., "gagiteck.com"
certificate_arn = ""  # ARN from ACM

# Database
db_name           = "gagiteck"
db_username       = "gagiteck_admin"
db_password       = "GagiteckDB2024Secure!"  # Use a strong password!
db_instance_class = "db.t3.micro"  # db.t3.small for production

# Redis
redis_node_type = "cache.t3.micro"  # cache.t3.small for production

# ECS - API Service
api_cpu    = 256   # 256, 512, 1024, 2048, 4096
api_memory = 512   # Depends on CPU
api_count  = 1     # 2+ for production

# ECS - Dashboard Service
dashboard_cpu    = 256
dashboard_memory = 512
dashboard_count  = 1

# Authentication (optional)
nextauth_secret     = ""  # Generate with: openssl rand -base64 32
github_oauth_id     = ""
github_oauth_secret = ""
