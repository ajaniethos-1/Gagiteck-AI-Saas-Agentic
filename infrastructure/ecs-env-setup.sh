#!/bin/bash
# Gagiteck ECS Environment Setup Script
# Run this script to configure environment variables for the API

set -e

echo "=== Gagiteck ECS Environment Setup ==="

# Configuration
CLUSTER_NAME="gagiteck-dev-cluster"
API_SERVICE="gagiteck-dev-api"
AWS_REGION="${AWS_REGION:-us-east-1}"
SECRET_NAME="gagiteck/prod/api-config"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Get existing infrastructure endpoints
echo ""
echo "Step 1: Fetching infrastructure endpoints..."

# Get RDS endpoint
RDS_ENDPOINT=$(aws rds describe-db-instances \
  --query 'DBInstances[?contains(DBInstanceIdentifier, `gagiteck`)].Endpoint.Address' \
  --output text --region $AWS_REGION 2>/dev/null || echo "")

if [ -n "$RDS_ENDPOINT" ]; then
  echo -e "${GREEN}✓ RDS Endpoint: $RDS_ENDPOINT${NC}"
else
  echo -e "${YELLOW}! RDS not found. Enter manually or set DATABASE_URL later.${NC}"
  RDS_ENDPOINT="your-rds-endpoint.amazonaws.com"
fi

# Get ElastiCache endpoint
REDIS_ENDPOINT=$(aws elasticache describe-cache-clusters \
  --query 'CacheClusters[?contains(CacheClusterId, `gagiteck`)].CacheNodes[0].Endpoint.Address' \
  --output text --region $AWS_REGION 2>/dev/null || echo "")

if [ -n "$REDIS_ENDPOINT" ]; then
  echo -e "${GREEN}✓ Redis Endpoint: $REDIS_ENDPOINT${NC}"
else
  echo -e "${YELLOW}! ElastiCache not found. Enter manually or set REDIS_URL later.${NC}"
  REDIS_ENDPOINT="your-elasticache-endpoint.cache.amazonaws.com"
fi

# Step 2: Create/Update Secrets Manager secret
echo ""
echo "Step 2: Creating secrets in AWS Secrets Manager..."

# Generate JWT secret
JWT_SECRET=$(openssl rand -hex 32)

# Create secret JSON
SECRET_JSON=$(cat <<EOF
{
  "JWT_SECRET": "$JWT_SECRET",
  "DATABASE_URL": "postgresql://gagiteck:YOUR_DB_PASSWORD@$RDS_ENDPOINT:5432/gagiteck",
  "REDIS_URL": "redis://$REDIS_ENDPOINT:6379",
  "SENTRY_DSN": "",
  "OPENAI_API_KEY": "",
  "ANTHROPIC_API_KEY": ""
}
EOF
)

# Check if secret exists
if aws secretsmanager describe-secret --secret-id "$SECRET_NAME" --region $AWS_REGION >/dev/null 2>&1; then
  echo "Secret exists, updating..."
  aws secretsmanager update-secret \
    --secret-id "$SECRET_NAME" \
    --secret-string "$SECRET_JSON" \
    --region $AWS_REGION
else
  echo "Creating new secret..."
  aws secretsmanager create-secret \
    --name "$SECRET_NAME" \
    --description "Gagiteck API configuration secrets" \
    --secret-string "$SECRET_JSON" \
    --region $AWS_REGION
fi

SECRET_ARN=$(aws secretsmanager describe-secret --secret-id "$SECRET_NAME" --query 'ARN' --output text --region $AWS_REGION)
echo -e "${GREEN}✓ Secret ARN: $SECRET_ARN${NC}"

# Step 3: Get current task definition
echo ""
echo "Step 3: Updating ECS Task Definition..."

TASK_DEF=$(aws ecs describe-task-definition --task-definition $API_SERVICE --region $AWS_REGION 2>/dev/null)

if [ -z "$TASK_DEF" ]; then
  echo -e "${RED}✗ Task definition not found. Please create it first.${NC}"
  exit 1
fi

# Create new task definition with environment variables
EXECUTION_ROLE_ARN=$(echo $TASK_DEF | jq -r '.taskDefinition.executionRoleArn')
TASK_ROLE_ARN=$(echo $TASK_DEF | jq -r '.taskDefinition.taskRoleArn')

# Create container definition with secrets
CONTAINER_DEF=$(cat <<EOF
[
  {
    "name": "api",
    "image": "$(echo $TASK_DEF | jq -r '.taskDefinition.containerDefinitions[0].image')",
    "essential": true,
    "portMappings": [
      {
        "containerPort": 8000,
        "hostPort": 8000,
        "protocol": "tcp"
      }
    ],
    "environment": [
      {"name": "ENVIRONMENT", "value": "production"},
      {"name": "DEBUG", "value": "false"},
      {"name": "HOST", "value": "0.0.0.0"},
      {"name": "PORT", "value": "8000"},
      {"name": "AWS_REGION", "value": "$AWS_REGION"},
      {"name": "SES_SENDER_EMAIL", "value": "noreply@mimoai.co"},
      {"name": "CORS_ORIGINS", "value": "https://app.mimoai.co,https://mimoai.co"}
    ],
    "secrets": [
      {"name": "JWT_SECRET", "valueFrom": "$SECRET_ARN:JWT_SECRET::"},
      {"name": "DATABASE_URL", "valueFrom": "$SECRET_ARN:DATABASE_URL::"},
      {"name": "REDIS_URL", "valueFrom": "$SECRET_ARN:REDIS_URL::"},
      {"name": "SENTRY_DSN", "valueFrom": "$SECRET_ARN:SENTRY_DSN::"},
      {"name": "OPENAI_API_KEY", "valueFrom": "$SECRET_ARN:OPENAI_API_KEY::"},
      {"name": "ANTHROPIC_API_KEY", "valueFrom": "$SECRET_ARN:ANTHROPIC_API_KEY::"}
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/gagiteck-api",
        "awslogs-region": "$AWS_REGION",
        "awslogs-stream-prefix": "api"
      }
    },
    "healthCheck": {
      "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
      "interval": 30,
      "timeout": 5,
      "retries": 3,
      "startPeriod": 60
    }
  }
]
EOF
)

# Register new task definition
echo "Registering updated task definition..."
aws ecs register-task-definition \
  --family $API_SERVICE \
  --container-definitions "$CONTAINER_DEF" \
  --requires-compatibilities FARGATE \
  --network-mode awsvpc \
  --cpu "256" \
  --memory "512" \
  --execution-role-arn "$EXECUTION_ROLE_ARN" \
  --task-role-arn "$TASK_ROLE_ARN" \
  --region $AWS_REGION

echo -e "${GREEN}✓ Task definition updated${NC}"

# Step 4: Update ECS service to use new task definition
echo ""
echo "Step 4: Updating ECS Service..."

aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service $API_SERVICE \
  --force-new-deployment \
  --region $AWS_REGION >/dev/null

echo -e "${GREEN}✓ Service update triggered${NC}"

# Step 5: Add Secrets Manager permissions to execution role
echo ""
echo "Step 5: Ensuring IAM permissions..."

ROLE_NAME=$(echo $EXECUTION_ROLE_ARN | sed 's/.*role\///')

# Create policy for Secrets Manager access
POLICY_JSON=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "$SECRET_ARN"
    }
  ]
}
EOF
)

aws iam put-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-name "GagiteckSecretsAccess" \
  --policy-document "$POLICY_JSON" \
  --region $AWS_REGION 2>/dev/null || echo "Policy may already exist"

echo -e "${GREEN}✓ IAM permissions configured${NC}"

echo ""
echo "=== Setup Complete ==="
echo ""
echo -e "${YELLOW}Important: Update the following values in Secrets Manager:${NC}"
echo "  1. DATABASE_URL - Update with your actual RDS password"
echo "  2. SENTRY_DSN - Add your Sentry project DSN (optional)"
echo "  3. OPENAI_API_KEY - Add if using OpenAI"
echo "  4. ANTHROPIC_API_KEY - Add if using Anthropic"
echo ""
echo "To update secrets:"
echo "  aws secretsmanager update-secret --secret-id $SECRET_NAME --secret-string 'JSON'"
echo ""
echo "Monitor deployment:"
echo "  aws ecs describe-services --cluster $CLUSTER_NAME --services $API_SERVICE"
