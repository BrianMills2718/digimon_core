# Kubernetes Deployment - CLAUDE.md

## Overview
The `k8s/` directory contains Kubernetes deployment manifests for running KGAS in production environments. These manifests provide a complete production-ready deployment with proper resource management, security, and observability.

## Directory Structure

### Deployment Manifests
- **`deployment.yaml`**: Main application deployment with containers, resource limits, and health checks
- **`service.yaml`**: Service definitions for internal and external access
- **`configmap.yaml`**: Configuration data for the application
- **`secret.yaml`**: Secure storage for sensitive configuration (API keys, passwords)

## Deployment Architecture

### Container Strategy
```yaml
# Production deployment uses multi-container pod:
- kgas-app:     Main application container
- neo4j:        Graph database sidecar
- prometheus:   Metrics collection sidecar
```

### Resource Management
- **CPU Limits**: Optimized for research workloads with burst capability
- **Memory Limits**: Configured for graph processing and vector operations
- **Storage**: Persistent volumes for database and application data
- **Networking**: Secure internal communication with external access points

### Security Configuration
- **Non-root containers**: All containers run with unprivileged users
- **Security contexts**: Minimal privileges and read-only root filesystems
- **Network policies**: Restricted inter-pod communication
- **Secret management**: Kubernetes secrets for sensitive data

## Key Configuration Areas

### Application Configuration (ConfigMap)
```yaml
# Environment-specific settings
database:
  neo4j_uri: "bolt://neo4j:7687"
  connection_pool_size: 50
  query_timeout: 30

llm_services:
  timeout: 60
  retry_attempts: 3
  rate_limits:
    openai: 100
    anthropic: 50

monitoring:
  metrics_enabled: true
  health_check_interval: 30
  log_level: "INFO"
```

### Security Secrets
```yaml
# Sensitive configuration (base64 encoded)
api_keys:
  openai_api_key: <base64-encoded-key>
  anthropic_api_key: <base64-encoded-key>
  google_api_key: <base64-encoded-key>

database:
  neo4j_password: <base64-encoded-password>
  
security:
  jwt_secret: <base64-encoded-secret>
  encryption_key: <base64-encoded-key>
```

## Deployment Commands

### Initial Deployment
```bash
# Create namespace (if needed)
kubectl create namespace kgas-production

# Apply configurations in order
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Verify deployment
kubectl get pods -n kgas-production
kubectl get services -n kgas-production
```

### Update Deployment
```bash
# Update configuration
kubectl apply -f k8s/configmap.yaml

# Rolling update deployment
kubectl rollout restart deployment/kgas-app -n kgas-production

# Monitor rollout
kubectl rollout status deployment/kgas-app -n kgas-production
```

### Scaling Operations
```bash
# Scale application pods
kubectl scale deployment kgas-app --replicas=3 -n kgas-production

# Horizontal pod autoscaling
kubectl autoscale deployment kgas-app --cpu-percent=70 --min=2 --max=10 -n kgas-production
```

## Health Monitoring

### Health Check Endpoints
```yaml
# Configured in deployment.yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Monitoring Commands
```bash
# Check pod health
kubectl get pods -n kgas-production -o wide

# View application logs
kubectl logs -f deployment/kgas-app -n kgas-production

# Check resource usage
kubectl top pods -n kgas-production
kubectl top nodes

# Monitor events
kubectl get events -n kgas-production --sort-by='.lastTimestamp'
```

## Troubleshooting

### Common Issues

#### **Pod Startup Issues**
```bash
# Check pod status
kubectl describe pod <pod-name> -n kgas-production

# Check configuration
kubectl get configmap kgas-config -o yaml -n kgas-production
kubectl get secret kgas-secrets -n kgas-production

# Check resource availability
kubectl describe nodes
```

#### **Database Connection Issues**
```bash
# Test Neo4j connectivity
kubectl exec -it <kgas-pod> -n kgas-production -- python -c "
from src.core.neo4j_manager import Neo4jManager
manager = Neo4jManager()
print(manager.health_check())
"

# Check Neo4j pod status
kubectl get pods -l app=neo4j -n kgas-production
kubectl logs -f <neo4j-pod> -n kgas-production
```

#### **Resource Constraints**
```bash
# Check resource limits
kubectl describe pod <pod-name> -n kgas-production | grep -A 5 "Limits"

# Monitor resource usage
kubectl top pod <pod-name> -n kgas-production --containers

# Check for resource pressure
kubectl describe node <node-name> | grep -A 5 "Allocated"
```

#### **Network Issues**
```bash
# Test service connectivity
kubectl get svc -n kgas-production
kubectl describe svc kgas-service -n kgas-production

# Test internal connectivity
kubectl exec -it <pod-name> -n kgas-production -- curl http://kgas-service:8000/health

# Check network policies
kubectl get networkpolicies -n kgas-production
```

## Security Best Practices

### Secret Management
```bash
# Create secrets securely
kubectl create secret generic kgas-secrets \
  --from-literal=openai-api-key=$OPENAI_API_KEY \
  --from-literal=neo4j-password=$NEO4J_PASSWORD \
  -n kgas-production

# Rotate secrets
kubectl delete secret kgas-secrets -n kgas-production
kubectl create secret generic kgas-secrets \
  --from-literal=openai-api-key=$NEW_OPENAI_API_KEY \
  --from-literal=neo4j-password=$NEW_NEO4J_PASSWORD \
  -n kgas-production

# Update deployment to use new secrets
kubectl rollout restart deployment/kgas-app -n kgas-production
```

### RBAC Configuration
```yaml
# Minimal RBAC for KGAS service account
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: kgas-role
rules:
- apiGroups: [""]
  resources: ["pods", "configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
```

### Network Security
```yaml
# Network policy for KGAS namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: kgas-network-policy
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 8000
```

## Performance Optimization

### Resource Tuning
```yaml
# Optimized resource requests and limits
resources:
  requests:
    memory: "2Gi"
    cpu: "1000m"
  limits:
    memory: "8Gi"
    cpu: "4000m"
```

### Storage Optimization
```yaml
# High-performance storage for Neo4j
volumeClaimTemplates:
- metadata:
    name: neo4j-data
  spec:
    accessModes: ["ReadWriteOnce"]
    storageClassName: "ssd-fast"
    resources:
      requests:
        storage: 100Gi
```

### Auto-scaling Configuration
```yaml
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: kgas-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: kgas-app
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

## Backup and Recovery

### Database Backup
```bash
# Create Neo4j backup job
kubectl create job neo4j-backup-$(date +%Y%m%d) \
  --image=neo4j:5.13 \
  --dry-run=client -o yaml | \
  kubectl apply -f -

# Verify backup completion
kubectl logs job/neo4j-backup-$(date +%Y%m%d) -n kgas-production
```

### Configuration Backup
```bash
# Backup all configurations
kubectl get configmap kgas-config -o yaml > backup/configmap-$(date +%Y%m%d).yaml
kubectl get secret kgas-secrets -o yaml > backup/secrets-$(date +%Y%m%d).yaml
kubectl get deployment kgas-app -o yaml > backup/deployment-$(date +%Y%m%d).yaml
```

### Disaster Recovery
```bash
# Emergency scale-down
kubectl scale deployment kgas-app --replicas=0 -n kgas-production

# Restore from backup
kubectl apply -f backup/configmap-latest.yaml
kubectl apply -f backup/deployment-latest.yaml

# Scale back up
kubectl scale deployment kgas-app --replicas=2 -n kgas-production
```

## Monitoring and Observability

### Prometheus Integration
```yaml
# Service monitor for Prometheus
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: kgas-metrics
spec:
  selector:
    matchLabels:
      app: kgas
  endpoints:
  - port: metrics
    path: /metrics
    interval: 30s
```

### Grafana Dashboards
```bash
# Apply Grafana dashboard ConfigMap
kubectl apply -f monitoring/grafana-dashboard-configmap.yaml

# Verify dashboard availability
kubectl get configmap -l grafana_dashboard=1 -n monitoring
```

### Log Aggregation
```yaml
# Fluentd configuration for log collection
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/kgas-*.log
      pos_file /var/log/fluentd-kgas.log.pos
      tag kubernetes.kgas
      format json
    </source>
```

## Environment Management

### Development Environment
```bash
# Deploy to development namespace
kubectl apply -f k8s/ -n kgas-development

# Use development-specific configuration
kubectl patch configmap kgas-config -n kgas-development \
  --patch '{"data":{"LOG_LEVEL":"DEBUG","METRICS_ENABLED":"true"}}'
```

### Staging Environment
```bash
# Deploy to staging with production-like settings
kubectl apply -f k8s/ -n kgas-staging

# Run integration tests
kubectl run integration-tests --image=kgas:test-latest \
  --env="TARGET_NAMESPACE=kgas-staging" \
  --rm -i --tty
```

### Production Environment
```bash
# Production deployment with all security measures
kubectl apply -f k8s/ -n kgas-production

# Enable monitoring and alerting
kubectl apply -f monitoring/ -n kgas-production

# Verify all components
kubectl get all -n kgas-production
```

## CI/CD Integration

### GitOps Workflow
```yaml
# ArgoCD application for automated deployment
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: kgas-production
spec:
  source:
    repoURL: https://github.com/your-org/kgas
    path: k8s/
    targetRevision: main
  destination:
    server: https://kubernetes.default.svc
    namespace: kgas-production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Deployment Validation
```bash
# Pre-deployment validation
kubectl apply --dry-run=client -f k8s/

# Post-deployment verification
kubectl rollout status deployment/kgas-app -n kgas-production
curl -f http://kgas-service/health
```

The Kubernetes deployment provides a robust, scalable, and secure foundation for running KGAS in production environments with proper observability and operational excellence.