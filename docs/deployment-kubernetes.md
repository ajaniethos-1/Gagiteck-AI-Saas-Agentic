# Kubernetes Deployment Guide

This guide covers deploying the Gagiteck AI SaaS Platform to Kubernetes.

## Prerequisites

- Kubernetes cluster (1.28+)
- kubectl configured
- Helm 3.x
- Docker registry access (Docker Hub, ECR, GCR)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                        │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Ingress Controller                    │   │
│  │              (nginx / traefik / istio)                   │   │
│  └───────────────────────┬─────────────────────────────────┘   │
│                          │                                       │
│         ┌────────────────┴────────────────┐                    │
│         ▼                                  ▼                    │
│  ┌─────────────────┐              ┌─────────────────┐          │
│  │   Dashboard     │              │      API        │          │
│  │   Deployment    │              │   Deployment    │          │
│  │   (2 replicas)  │              │   (3 replicas)  │          │
│  └────────┬────────┘              └────────┬────────┘          │
│           │                                 │                    │
│           └─────────────┬──────────────────┘                    │
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Services                              │   │
│  │   PostgreSQL │ Redis │ ConfigMaps │ Secrets             │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Create Namespace

```bash
kubectl create namespace gagiteck
kubectl config set-context --current --namespace=gagiteck
```

### 2. Create Secrets

```bash
# Create secrets for sensitive data
kubectl create secret generic gagiteck-secrets \
  --from-literal=database-url='postgresql://user:pass@postgres:5432/gagiteck' \
  --from-literal=redis-url='redis://redis:6379' \
  --from-literal=openai-api-key='sk-...' \
  --from-literal=anthropic-api-key='sk-ant-...' \
  --from-literal=nextauth-secret='your-secret-here'
```

### 3. Apply Manifests

```bash
kubectl apply -f k8s/
```

## Kubernetes Manifests

### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: gagiteck
  labels:
    app: gagiteck
```

### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: gagiteck-config
  namespace: gagiteck
data:
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  NODE_ENV: "production"
  NEXT_PUBLIC_API_URL: "http://api:8000"
```

### API Deployment

```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: gagiteck
  labels:
    app: gagiteck
    component: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gagiteck
      component: api
  template:
    metadata:
      labels:
        app: gagiteck
        component: api
    spec:
      containers:
        - name: api
          image: your-registry/gagiteck-api:latest
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: gagiteck-config
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: gagiteck-secrets
                  key: database-url
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: gagiteck-secrets
                  key: redis-url
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: gagiteck-secrets
                  key: openai-api-key
          resources:
            requests:
              cpu: "250m"
              memory: "512Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: gagiteck
spec:
  selector:
    app: gagiteck
    component: api
  ports:
    - port: 8000
      targetPort: 8000
  type: ClusterIP
```

### Dashboard Deployment

```yaml
# k8s/dashboard-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dashboard
  namespace: gagiteck
  labels:
    app: gagiteck
    component: dashboard
spec:
  replicas: 2
  selector:
    matchLabels:
      app: gagiteck
      component: dashboard
  template:
    metadata:
      labels:
        app: gagiteck
        component: dashboard
    spec:
      containers:
        - name: dashboard
          image: your-registry/gagiteck-dashboard:latest
          ports:
            - containerPort: 3000
          envFrom:
            - configMapRef:
                name: gagiteck-config
          env:
            - name: NEXTAUTH_SECRET
              valueFrom:
                secretKeyRef:
                  name: gagiteck-secrets
                  key: nextauth-secret
          resources:
            requests:
              cpu: "100m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
          readinessProbe:
            httpGet:
              path: /api/health
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: dashboard
  namespace: gagiteck
spec:
  selector:
    app: gagiteck
    component: dashboard
  ports:
    - port: 3000
      targetPort: 3000
  type: ClusterIP
```

### PostgreSQL StatefulSet

```yaml
# k8s/postgres.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: gagiteck
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:15-alpine
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_USER
              value: gagiteck
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: gagiteck-secrets
                  key: postgres-password
            - name: POSTGRES_DB
              value: gagiteck
          volumeMounts:
            - name: postgres-data
              mountPath: /var/lib/postgresql/data
          resources:
            requests:
              cpu: "250m"
              memory: "512Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"
  volumeClaimTemplates:
    - metadata:
        name: postgres-data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: standard
        resources:
          requests:
            storage: 20Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: gagiteck
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
  clusterIP: None
```

### Redis Deployment

```yaml
# k8s/redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: gagiteck
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          ports:
            - containerPort: 6379
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: gagiteck
spec:
  selector:
    app: redis
  ports:
    - port: 6379
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: gagiteck-ingress
  namespace: gagiteck
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - gagiteck.com
        - api.gagiteck.com
      secretName: gagiteck-tls
  rules:
    - host: gagiteck.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: dashboard
                port:
                  number: 3000
    - host: api.gagiteck.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api
                port:
                  number: 8000
```

## Helm Chart

For more complex deployments, use the Helm chart:

### Install with Helm

```bash
# Add repository
helm repo add gagiteck https://charts.gagiteck.com
helm repo update

# Install
helm install gagiteck gagiteck/gagiteck \
  --namespace gagiteck \
  --create-namespace \
  --values values.yaml
```

### values.yaml

```yaml
# values.yaml
global:
  imageRegistry: your-registry

api:
  replicaCount: 3
  image:
    repository: gagiteck-api
    tag: latest
  resources:
    requests:
      cpu: 250m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1Gi

dashboard:
  replicaCount: 2
  image:
    repository: gagiteck-dashboard
    tag: latest

postgresql:
  enabled: true
  auth:
    username: gagiteck
    password: ""  # Use existingSecret
    database: gagiteck
  primary:
    persistence:
      size: 20Gi

redis:
  enabled: true
  architecture: standalone

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: gagiteck.com
      paths:
        - path: /
          service: dashboard
    - host: api.gagiteck.com
      paths:
        - path: /
          service: api
  tls:
    - secretName: gagiteck-tls
      hosts:
        - gagiteck.com
        - api.gagiteck.com
```

## Scaling

### Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
  namespace: gagiteck
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### Manual Scaling

```bash
# Scale API deployment
kubectl scale deployment api --replicas=5 -n gagiteck

# Scale Dashboard deployment
kubectl scale deployment dashboard --replicas=3 -n gagiteck
```

## Monitoring

### Install Prometheus Stack

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

### ServiceMonitor

```yaml
# k8s/servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: api-monitor
  namespace: gagiteck
spec:
  selector:
    matchLabels:
      app: gagiteck
      component: api
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```

## Troubleshooting

### Check Pod Status

```bash
# List all pods
kubectl get pods -n gagiteck

# Describe a pod
kubectl describe pod <pod-name> -n gagiteck

# View logs
kubectl logs <pod-name> -n gagiteck -f

# Previous container logs
kubectl logs <pod-name> -n gagiteck --previous
```

### Debug Containers

```bash
# Execute shell in container
kubectl exec -it <pod-name> -n gagiteck -- /bin/sh

# Port forward for local debugging
kubectl port-forward svc/api 8000:8000 -n gagiteck
```

### Common Issues

#### Pods in CrashLoopBackOff

```bash
# Check container logs
kubectl logs <pod-name> -n gagiteck

# Check events
kubectl get events -n gagiteck --sort-by='.lastTimestamp'
```

#### ImagePullBackOff

```bash
# Verify image exists
docker pull your-registry/gagiteck-api:latest

# Check image pull secrets
kubectl get secrets -n gagiteck
```

#### Database Connection Failures

```bash
# Test connection from pod
kubectl exec -it <api-pod> -n gagiteck -- \
  psql $DATABASE_URL -c "SELECT 1"
```

## Backup & Restore

### Database Backup

```bash
# Create backup job
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: postgres-backup
  namespace: gagiteck
spec:
  template:
    spec:
      containers:
        - name: backup
          image: postgres:15-alpine
          command: ["pg_dump"]
          args: ["-h", "postgres", "-U", "gagiteck", "-d", "gagiteck", "-f", "/backup/dump.sql"]
          volumeMounts:
            - name: backup
              mountPath: /backup
      volumes:
        - name: backup
          persistentVolumeClaim:
            claimName: backup-pvc
      restartPolicy: Never
EOF
```

## Security Best Practices

1. **Network Policies**: Restrict pod-to-pod communication
2. **Pod Security Standards**: Use restricted policies
3. **RBAC**: Minimal service account permissions
4. **Secrets**: Use external secrets operator
5. **Image Security**: Scan images with Trivy

### Network Policy Example

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
  namespace: gagiteck
spec:
  podSelector:
    matchLabels:
      component: api
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              component: dashboard
      ports:
        - port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - port: 5432
    - to:
        - podSelector:
            matchLabels:
              app: redis
      ports:
        - port: 6379
```

## Next Steps

- [Docker Deployment](deployment-docker.md) - Local Docker setup
- [AWS Deployment](deployment-cloud.md) - AWS ECS deployment
- [Configuration Guide](configuration.md) - Environment configuration
