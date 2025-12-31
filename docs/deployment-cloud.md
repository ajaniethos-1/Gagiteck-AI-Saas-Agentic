# AWS Cloud Deployment Guide

This guide covers deploying the Gagiteck AI SaaS Platform to AWS using Terraform and ECS Fargate.

## Architecture Overview

```
                         ┌─────────────────┐
                         │    Route 53     │
                         └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │       ALB       │
                         │   (Public LB)   │
                         └────────┬────────┘
                    ┌─────────────┴─────────────┐
                    │                           │
           ┌────────▼────────┐        ┌─────────▼────────┐
           │   Dashboard     │        │       API        │
           │   (Fargate)     │        │   (Fargate)      │
           └────────┬────────┘        └─────────┬────────┘
                    │                           │
        ┌───────────┴───────────────────────────┴───────────┐
        │                Private Subnets                     │
        │    ┌──────────┐  ┌──────────┐  ┌──────────┐      │
        │    │   RDS    │  │  Redis   │  │   S3     │      │
        │    │PostgreSQL│  │ElastiCache│ │ Assets   │      │
        │    └──────────┘  └──────────┘  └──────────┘      │
        └────────────────────────────────────────────────────┘
```

## AWS Services Used

| Service | Purpose |
|---------|---------|
| **VPC** | Network isolation with public/private subnets |
| **ECS Fargate** | Serverless container orchestration |
| **ECR** | Docker image registry |
| **ALB** | Application load balancer with health checks |
| **RDS PostgreSQL** | Managed database |
| **ElastiCache Redis** | In-memory cache and queues |
| **S3** | Static assets and file storage |
| **Secrets Manager** | Secure credential storage |
| **CloudWatch** | Logging and monitoring |

## Prerequisites

### 1. Install Required Tools

```bash
# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Terraform
brew install terraform  # macOS
# Or download from https://terraform.io/downloads

# Docker
# Install Docker Desktop or Docker Engine
```

### 2. Configure AWS Credentials

```bash
# Create IAM user with programmatic access
# Required permissions: AdministratorAccess or custom policy

aws configure
# AWS Access Key ID: your-access-key
# AWS Secret Access Key: your-secret-key
# Default region: us-east-1
# Default output format: json

# Verify configuration
aws sts get-caller-identity
```

## Deployment Steps

### Step 1: Clone Repository

```bash
git clone https://github.com/ajaniethos-1/gagiteck-AI-SaaS-Agentic.git
cd gagiteck-AI-SaaS-Agentic/infrastructure/terraform
```

### Step 2: Configure Variables

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
# General
aws_region  = "us-east-1"
environment = "dev"  # dev, staging, or prod

# Networking
vpc_cidr             = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs = ["10.0.10.0/24", "10.0.20.0/24"]

# Domain & SSL (optional)
domain_name     = ""  # e.g., "gagiteck.com"
certificate_arn = ""  # ACM certificate ARN

# Database
db_name           = "gagiteck"
db_username       = "gagiteck_admin"
db_password       = "YourSecurePassword123!"
db_instance_class = "db.t3.micro"

# Redis
redis_node_type = "cache.t3.micro"

# ECS - API Service
api_cpu    = 256
api_memory = 512
api_count  = 1

# ECS - Dashboard Service
dashboard_cpu    = 256
dashboard_memory = 512
dashboard_count  = 1
```

### Step 3: Initialize Terraform

```bash
terraform init
```

### Step 4: Plan Infrastructure

```bash
terraform plan
```

Review the planned resources before applying.

### Step 5: Apply Infrastructure

```bash
terraform apply
```

Type `yes` to confirm. This creates ~50 AWS resources and takes 10-15 minutes.

### Step 6: Build and Push Docker Images

```bash
# Get ECR registry URL
ECR_REGISTRY=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ECR_REGISTRY

# Build and push API
cd ../../api
docker build -t $ECR_REGISTRY/gagiteck-dev-api:latest .
docker push $ECR_REGISTRY/gagiteck-dev-api:latest

# Build and push Dashboard
cd ../dashboard
docker build -t $ECR_REGISTRY/gagiteck-dev-dashboard:latest .
docker push $ECR_REGISTRY/gagiteck-dev-dashboard:latest
```

### Step 7: Update ECS Services

```bash
# Force new deployment to pull latest images
aws ecs update-service \
  --cluster gagiteck-dev-cluster \
  --service gagiteck-dev-api \
  --force-new-deployment

aws ecs update-service \
  --cluster gagiteck-dev-cluster \
  --service gagiteck-dev-dashboard \
  --force-new-deployment
```

### Step 8: Verify Deployment

```bash
# Get ALB DNS name
terraform output alb_dns_name

# Test API health
curl http://<alb-dns-name>:8000/health

# Access Dashboard
open http://<alb-dns-name>
```

## CI/CD with GitHub Actions

The repository includes a GitHub Actions workflow for automated deployments.

### Configure GitHub Secrets

Add these secrets to your GitHub repository:

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |

### Workflow Triggers

The deploy workflow runs on:
- Push to `main` branch
- Changes to `api/**`, `dashboard/**`, or `.github/workflows/deploy.yml`
- Manual trigger via GitHub Actions UI

### Workflow File

`.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]
    paths:
      - 'api/**'
      - 'dashboard/**'
      - '.github/workflows/deploy.yml'
  workflow_dispatch:

env:
  AWS_REGION: us-east-1
  ECS_CLUSTER: gagiteck-dev-cluster

jobs:
  deploy-api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - uses: aws-actions/amazon-ecr-login@v2
        id: login-ecr

      - name: Build and push API
        run: |
          cd api
          docker build -t ${{ steps.login-ecr.outputs.registry }}/gagiteck-dev-api:${{ github.sha }} .
          docker push ${{ steps.login-ecr.outputs.registry }}/gagiteck-dev-api:${{ github.sha }}

      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster ${{ env.ECS_CLUSTER }} \
            --service gagiteck-dev-api \
            --force-new-deployment
```

## Environment Tiers

### Development

```hcl
environment       = "dev"
db_instance_class = "db.t3.micro"
redis_node_type   = "cache.t3.micro"
api_count         = 1
api_cpu           = 256
api_memory        = 512
```

Estimated cost: ~$50-100/month

### Staging

```hcl
environment       = "staging"
db_instance_class = "db.t3.small"
redis_node_type   = "cache.t3.small"
api_count         = 2
api_cpu           = 512
api_memory        = 1024
```

Estimated cost: ~$150-250/month

### Production

```hcl
environment       = "prod"
db_instance_class = "db.t3.medium"
redis_node_type   = "cache.t3.medium"
api_count         = 3
api_cpu           = 1024
api_memory        = 2048
```

Estimated cost: ~$400+/month

## SSL/HTTPS Setup

### 1. Request ACM Certificate

```bash
aws acm request-certificate \
  --domain-name gagiteck.com \
  --subject-alternative-names "*.gagiteck.com" \
  --validation-method DNS
```

### 2. Add DNS Validation Records

Add the CNAME records provided by ACM to your DNS provider.

### 3. Update Terraform Variables

```hcl
domain_name     = "gagiteck.com"
certificate_arn = "arn:aws:acm:us-east-1:123456789:certificate/abc-123"
```

### 4. Apply Changes

```bash
terraform apply
```

## Monitoring & Logs

### CloudWatch Logs

```bash
# View API logs
aws logs tail /ecs/gagiteck-dev-api --follow

# View Dashboard logs
aws logs tail /ecs/gagiteck-dev-dashboard --follow

# Search logs
aws logs filter-log-events \
  --log-group-name /ecs/gagiteck-dev-api \
  --filter-pattern "ERROR"
```

### ECS Service Status

```bash
# Describe services
aws ecs describe-services \
  --cluster gagiteck-dev-cluster \
  --services gagiteck-dev-api gagiteck-dev-dashboard

# List running tasks
aws ecs list-tasks \
  --cluster gagiteck-dev-cluster \
  --service-name gagiteck-dev-api
```

## Troubleshooting

### ECS Tasks Not Starting

```bash
# Check service events
aws ecs describe-services \
  --cluster gagiteck-dev-cluster \
  --services gagiteck-dev-api \
  --query 'services[0].events[:5]'

# Check task failures
aws ecs describe-tasks \
  --cluster gagiteck-dev-cluster \
  --tasks $(aws ecs list-tasks --cluster gagiteck-dev-cluster --desired-status STOPPED --query 'taskArns[0]' --output text)
```

### Health Check Failures

1. Verify the health check endpoint returns 200:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check security groups allow ALB traffic to ECS tasks

3. Verify container port matches task definition

### Database Connection Issues

```bash
# Test from bastion or VPN
psql -h <rds-endpoint> -U gagiteck_admin -d gagiteck

# Check security group rules
aws ec2 describe-security-groups \
  --group-ids <rds-security-group-id>
```

### Image Pull Errors

```bash
# Verify image exists in ECR
aws ecr describe-images \
  --repository-name gagiteck-dev-api

# Check ECS task execution role has ECR permissions
```

## Scaling

### Manual Scaling

```bash
# Scale API to 3 instances
aws ecs update-service \
  --cluster gagiteck-dev-cluster \
  --service gagiteck-dev-api \
  --desired-count 3
```

### Auto Scaling

Add to Terraform:

```hcl
resource "aws_appautoscaling_target" "api" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.api.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "api_cpu" {
  name               = "api-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.api.resource_id
  scalable_dimension = aws_appautoscaling_target.api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.api.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 70.0
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }
}
```

## Destroy Infrastructure

```bash
# Destroy all resources
terraform destroy

# Type 'yes' to confirm
```

**Warning**: This deletes all data including databases. Create backups first.

## Terraform Outputs

After deployment, get these values:

```bash
terraform output api_url
terraform output dashboard_url
terraform output alb_dns_name
terraform output rds_endpoint
terraform output redis_endpoint
terraform output api_ecr_repository_url
terraform output dashboard_ecr_repository_url
```

## Security Best Practices

1. **Network Isolation**: All resources in private subnets except ALB
2. **Secrets Management**: Use AWS Secrets Manager for credentials
3. **Encryption**: Enable encryption for RDS, S3, and Redis
4. **IAM Roles**: Use least-privilege task execution roles
5. **Security Groups**: Restrict traffic to only required ports
6. **WAF**: Consider adding AWS WAF for production

## Next Steps

- [Docker Deployment](deployment-docker.md) - Local Docker setup
- [Configuration Guide](configuration.md) - Environment configuration
- [Monitoring Setup](monitoring.md) - CloudWatch dashboards
