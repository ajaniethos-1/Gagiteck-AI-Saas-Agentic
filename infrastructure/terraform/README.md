# Gagiteck AWS Infrastructure

Terraform configuration for deploying the Gagiteck AI SaaS Platform on AWS.

## Architecture

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

## Prerequisites

1. **AWS CLI** installed and configured
   ```bash
   aws configure
   ```

2. **Terraform** v1.0+
   ```bash
   brew install terraform  # macOS
   ```

3. **Docker** for building images

## Quick Start

### 1. Initialize Terraform

```bash
cd infrastructure/terraform
terraform init
```

### 2. Configure Variables

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

### 3. Plan and Apply

```bash
# Preview changes
terraform plan

# Apply infrastructure
terraform apply
```

### 4. Build and Push Docker Images

```bash
# Get ECR login
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $(terraform output -raw api_ecr_repository_url | cut -d'/' -f1)

# Build and push API
docker build -t gagiteck-api ../api
docker tag gagiteck-api:latest $(terraform output -raw api_ecr_repository_url):latest
docker push $(terraform output -raw api_ecr_repository_url):latest

# Build and push Dashboard
docker build -t gagiteck-dashboard ../dashboard
docker tag gagiteck-dashboard:latest $(terraform output -raw dashboard_ecr_repository_url):latest
docker push $(terraform output -raw dashboard_ecr_repository_url):latest
```

### 5. Update ECS Services

```bash
aws ecs update-service \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --service $(terraform output -raw api_service_name) \
  --force-new-deployment

aws ecs update-service \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --service $(terraform output -raw dashboard_service_name) \
  --force-new-deployment
```

## Configuration

### Environment Tiers

| Variable | Dev | Staging | Production |
|----------|-----|---------|------------|
| `db_instance_class` | db.t3.micro | db.t3.small | db.t3.medium+ |
| `redis_node_type` | cache.t3.micro | cache.t3.small | cache.t3.medium+ |
| `api_count` | 1 | 2 | 2+ |
| `dashboard_count` | 1 | 2 | 2+ |
| `api_cpu` | 256 | 512 | 1024+ |
| `api_memory` | 512 | 1024 | 2048+ |

### Estimated Costs

| Tier | Monthly Cost |
|------|-------------|
| Dev | ~$50-100 |
| Staging | ~$150-250 |
| Production | ~$400+ |

## SSL/HTTPS Setup

1. **Request Certificate in ACM**
   ```bash
   aws acm request-certificate \
     --domain-name gagiteck.com \
     --subject-alternative-names "*.gagiteck.com" \
     --validation-method DNS
   ```

2. **Add DNS Validation Records** in Route 53

3. **Update terraform.tfvars**
   ```hcl
   domain_name     = "gagiteck.com"
   certificate_arn = "arn:aws:acm:us-east-1:123456789:certificate/abc-123"
   ```

## Outputs

After `terraform apply`, you'll get:

| Output | Description |
|--------|-------------|
| `api_url` | API endpoint URL |
| `dashboard_url` | Dashboard URL |
| `alb_dns_name` | Load balancer DNS |
| `rds_endpoint` | Database connection string |
| `redis_endpoint` | Redis connection string |

## Destroy Infrastructure

```bash
terraform destroy
```

## Troubleshooting

### ECS Tasks Not Starting
```bash
# Check task logs
aws logs tail /ecs/gagiteck-dev-api --follow

# Describe service
aws ecs describe-services \
  --cluster gagiteck-dev-cluster \
  --services gagiteck-dev-api
```

### Database Connection Issues
```bash
# Test from bastion/VPN
psql -h <rds-endpoint> -U gagiteck_admin -d gagiteck
```

### ALB Health Check Failures
- Verify security groups allow traffic
- Check target group health in AWS Console
- Ensure health check path returns 200

## Security Considerations

- All resources in private subnets (except ALB)
- RDS and Redis only accessible from ECS
- Secrets stored in AWS Secrets Manager
- S3 bucket blocks public access
- Storage encryption enabled
