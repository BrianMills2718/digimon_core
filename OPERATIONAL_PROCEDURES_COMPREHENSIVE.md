# KGAS Operational Procedures - Comprehensive Guide

**Date**: 2025-07-25  
**Version**: 1.0  
**Status**: 🟢 **PRODUCTION READY**  
**Scope**: Complete operational procedures for KGAS GraphRAG system

---

## 🎯 **OPERATIONAL OVERVIEW**

This document provides comprehensive operational procedures for the KGAS (Knowledge Graph Analysis System) GraphRAG production environment, covering deployment, monitoring, troubleshooting, backup/restore, and maintenance procedures.

### **System Architecture Summary**
- **Core Services**: QualityService, ProvenanceService, IdentityService  
- **Infrastructure**: Kubernetes-based deployment with monitoring and backup
- **Monitoring**: Prometheus/Grafana stack with comprehensive alerting
- **Backup**: Automated daily backups with S3 integration
- **Deployment**: One-command automated deployment with validation

---

## 📋 **1. DEPLOYMENT PROCEDURES**

### **1.1 Pre-Deployment Checklist**

#### **Infrastructure Requirements**
```bash
# Verify Kubernetes cluster
kubectl cluster-info
kubectl get nodes

# Check Prometheus Operator
kubectl get pods -n monitoring | grep prometheus

# Verify storage classes
kubectl get storageclass

# Check resource quotas
kubectl describe quota -n kgas-production
```

#### **Environment Variables Setup**
```bash
# Core Configuration
export NAMESPACE="kgas-production"
export IMAGE_TAG="v1.0.0"
export REGISTRY="your-registry.com/kgas"

# Database Configuration
export NEO4J_URI="bolt://neo4j.production:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your-secure-password"

# Backup Configuration
export BACKUP_STORAGE_URI="s3://kgas-backups/"
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"

# LLM API Keys (Optional)
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### **1.2 Standard Deployment Process**

#### **Step 1: Secrets Management**
```bash
# Create namespace
kubectl create namespace $NAMESPACE

# Database secrets
kubectl create secret generic kgas-db-credentials \
  --from-literal=neo4j-uri="$NEO4J_URI" \
  --from-literal=neo4j-user="$NEO4J_USER" \
  --from-literal=neo4j-password="$NEO4J_PASSWORD" \
  -n $NAMESPACE

# Backup secrets
kubectl create secret generic kgas-backup-credentials \
  --from-literal=backup-storage-uri="$BACKUP_STORAGE_URI" \
  --from-literal=aws-access-key-id="$AWS_ACCESS_KEY_ID" \
  --from-literal=aws-secret-access-key="$AWS_SECRET_ACCESS_KEY" \
  -n $NAMESPACE

# LLM API keys (if needed)
kubectl create secret generic kgas-api-keys \
  --from-literal=openai-api-key="$OPENAI_API_KEY" \
  --from-literal=anthropic-api-key="$ANTHROPIC_API_KEY" \
  -n $NAMESPACE
```

#### **Step 2: Automated Deployment**
```bash
# Execute comprehensive deployment
chmod +x deploy.sh
./deploy.sh deploy

# Monitor deployment progress
kubectl rollout status deployment/kgas-api -n $NAMESPACE

# Verify deployment
./deploy.sh status
```

#### **Step 3: Post-Deployment Validation**
```bash
# Health checks
kubectl port-forward svc/kgas-api 8000:8000 -n $NAMESPACE &
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/metrics

# Service validation
kubectl get pods -n $NAMESPACE -l app=kgas
kubectl get services -n $NAMESPACE
kubectl get ingress -n $NAMESPACE

# Monitoring validation
kubectl get servicemonitor kgas-metrics -n $NAMESPACE
kubectl get prometheusrules -n $NAMESPACE
```

### **1.3 Emergency Deployment Procedures**

#### **Hotfix Deployment**
```bash
# Build and deploy hotfix
export IMAGE_TAG="v1.0.1-hotfix"
./deploy.sh update-image

# Verify hotfix deployment
kubectl describe deployment/kgas-api -n $NAMESPACE
kubectl logs -f deployment/kgas-api -n $NAMESPACE
```

#### **Rollback Procedures**
```bash
# Quick rollback to previous version
kubectl rollout undo deployment/kgas-api -n $NAMESPACE

# Rollback to specific revision
kubectl rollout history deployment/kgas-api -n $NAMESPACE
kubectl rollout undo deployment/kgas-api --to-revision=3 -n $NAMESPACE

# Complete environment rollback
./deploy.sh rollback
```

---

## 📊 **2. MONITORING AND ALERTING PROCEDURES**

### **2.1 Health Monitoring Dashboard**

#### **Key Performance Indicators (KPIs)**
- **Application Health**: Health endpoint response rate (>99.9%)
- **Request Throughput**: Requests per second (baseline: 100 RPS)
- **Response Latency**: 95th percentile response time (<2 seconds)
- **Error Rate**: HTTP 5xx errors (<0.5%)
- **Resource Utilization**: CPU (<70%), Memory (<80%)
- **Database Connectivity**: Neo4j connection status (100% uptime)

#### **Grafana Dashboard Access**
```bash
# Access Grafana dashboard
kubectl port-forward svc/grafana 3000:3000 -n monitoring

# Dashboard URLs:
# - KGAS System Overview: http://localhost:3000/d/kgas-overview
# - Performance Metrics: http://localhost:3000/d/kgas-performance  
# - Error Analysis: http://localhost:3000/d/kgas-errors
```

#### **Prometheus Metrics Queries**
```promql
# Request rate
rate(kgas_requests_total[5m])

# Error rate
rate(kgas_requests_total{status=~"5.."}[5m]) / rate(kgas_requests_total[5m])

# Response time percentiles
histogram_quantile(0.95, rate(kgas_request_duration_seconds_bucket[5m]))

# System health
kgas_system_health

# Active connections
kgas_active_connections
```

### **2.2 Alert Management**

#### **Critical Alerts (Immediate Response)**
- **KGASDown**: Application completely unavailable
- **KGASHighErrorRate**: Error rate >5% for 2+ minutes
- **KGASHighMemoryUsage**: Memory usage >90% for 5+ minutes
- **KGASBackupFailed**: Daily backup job failed

#### **Warning Alerts (Next Business Day)**
- **KGASHighResponseTime**: 95th percentile >5 seconds for 3+ minutes
- **KGASHighActiveConnections**: >1000 concurrent connections
- **KGASQualityServiceDegraded**: Quality assessment errors increasing

#### **Alert Response Procedures**
```bash
# Check alert status
kubectl get prometheusrules -n $NAMESPACE
kubectl describe prometheusrule kgas-alerts -n $NAMESPACE

# View active alerts
curl http://prometheus:9090/api/v1/alerts

# Silence alerts during maintenance
curl -X POST http://alertmanager:9093/api/v1/silences \
  -d '{"matchers":[{"name":"alertname","value":"KGASHighResponseTime"}],"startsAt":"2023-07-25T10:00:00Z","endsAt":"2023-07-25T12:00:00Z","comment":"Maintenance window"}'
```

### **2.3 Log Analysis**

#### **Log Aggregation**
```bash
# Application logs
kubectl logs -f deployment/kgas-api -n $NAMESPACE

# Filter by log level
kubectl logs deployment/kgas-api -n $NAMESPACE | grep "ERROR"
kubectl logs deployment/kgas-api -n $NAMESPACE | grep "exception"

# Multi-pod log streaming
kubectl logs -f -l app=kgas -n $NAMESPACE --all-containers
```

#### **Log Analysis Queries**
```bash
# Error pattern analysis
kubectl logs deployment/kgas-api -n $NAMESPACE --since=1h | grep -E "(ERROR|EXCEPTION|Failed)" | sort | uniq -c

# Performance issue analysis
kubectl logs deployment/kgas-api -n $NAMESPACE | grep "duration" | awk '{print $NF}' | sort -n

# Quality service error analysis
kubectl logs deployment/kgas-api -n $NAMESPACE | grep "QualityService" | grep "error"
```

---

## 🛠️ **3. TROUBLESHOOTING PROCEDURES**

### **3.1 Common Issues and Solutions**

#### **Application Startup Issues**
```bash
# Check pod status and events
kubectl get pods -n $NAMESPACE -l app=kgas
kubectl describe pod <pod-name> -n $NAMESPACE

# Common fixes:
# 1. Secret missing or incorrect
kubectl get secrets -n $NAMESPACE
kubectl describe secret kgas-db-credentials -n $NAMESPACE

# 2. Resource constraints
kubectl top pods -n $NAMESPACE
kubectl describe nodes

# 3. Image pull issues
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp'
```

#### **Database Connection Issues**
```bash
# Test database connectivity
kubectl exec -it deployment/kgas-api -n $NAMESPACE -- \
  python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('$NEO4J_URI', auth=('$NEO4J_USER', '$NEO4J_PASSWORD'))
print('Connected!' if driver.verify_connectivity() else 'Failed!')
driver.close()
"

# Check database pod (if Neo4j in cluster)
kubectl get pods -l app=neo4j -n $NAMESPACE
kubectl logs -f deployment/neo4j -n $NAMESPACE

# Network connectivity test
kubectl exec -it deployment/kgas-api -n $NAMESPACE -- nslookup neo4j.production
kubectl exec -it deployment/kgas-api -n $NAMESPACE -- telnet neo4j.production 7687
```

#### **Performance Issues**
```bash
# Resource utilization analysis
kubectl top pods -n $NAMESPACE
kubectl top nodes

# Memory and CPU profiling
kubectl exec -it deployment/kgas-api -n $NAMESPACE -- \
  python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'Disk: {psutil.disk_usage(\"/\").percent}%')
"

# Application performance metrics
curl http://localhost:8000/metrics | grep kgas_request_duration
```

#### **Quality Service Issues**
```bash
# Quality service health check
kubectl exec -it deployment/kgas-api -n $NAMESPACE -- \
  python -c "
from src.core.quality_service import QualityService
qs = QualityService()
print('QualityService health:', qs.health_check())
print('Advanced analytics:', qs.get_advanced_analytics())
"

# Error pattern analysis
kubectl logs deployment/kgas-api -n $NAMESPACE | grep "QualityService" | tail -20
```

### **3.2 Advanced Troubleshooting**

#### **Performance Bottleneck Analysis**
```bash
# Identify slow operations
kubectl exec -it deployment/kgas-api -n $NAMESPACE -- \
  python -c "
from src.core.provenance_service import ProvenanceService
ps = ProvenanceService()
bottlenecks = ps.detect_bottlenecks()
print('Detected bottlenecks:', bottlenecks)
"

# Memory leak detection
kubectl exec -it deployment/kgas-api -n $NAMESPACE -- \
  python -c "
import gc
import psutil
print('Memory before GC:', psutil.virtual_memory().percent)
gc.collect()
print('Memory after GC:', psutil.virtual_memory().percent)
print('Unreachable objects:', gc.garbage)
"
```

#### **Data Integrity Validation**
```bash
# Validate provenance data
kubectl exec -it deployment/kgas-api -n $NAMESPACE -- \
  python -c "
from src.core.provenance_service import ProvenanceService
ps = ProvenanceService()
compliance = ps.generate_compliance_report()
print('Compliance report:', compliance)
"

# Quality data validation
kubectl exec -it deployment/kgas-api -n $NAMESPACE -- \
  python -c "
from src.core.quality_service import QualityService
qs = QualityService()
anomalies = qs.detect_quality_anomalies()
print('Quality anomalies:', anomalies)
"
```

---

## 🔄 **4. BACKUP AND RECOVERY PROCEDURES**

### **4.1 Backup Management**

#### **Automated Backup Verification**
```bash
# Check backup CronJob status
kubectl get cronjobs kgas-backup -n $NAMESPACE
kubectl describe cronjob kgas-backup -n $NAMESPACE

# View recent backup jobs
kubectl get jobs -n $NAMESPACE | grep backup

# Check backup logs
kubectl logs job/kgas-backup-$(date +%Y%m%d) -n $NAMESPACE

# Verify S3 backup files
aws s3 ls $BACKUP_STORAGE_URI | grep kgas_backup | tail -10
```

#### **Manual Backup Procedures**
```bash
# Trigger manual backup
kubectl create job --from=cronjob/kgas-backup kgas-manual-backup-$(date +%Y%m%d%H%M) -n $NAMESPACE

# Monitor manual backup
kubectl logs -f job/kgas-manual-backup-$(date +%Y%m%d%H%M) -n $NAMESPACE

# Verify backup completion
aws s3 ls $BACKUP_STORAGE_URI | grep $(date +%Y%m%d)
```

### **4.2 Recovery Procedures**

#### **Database Recovery**
```bash
# List available backups
aws s3 ls $BACKUP_STORAGE_URI | grep kgas_backup

# Download specific backup
aws s3 cp $BACKUP_STORAGE_URI/kgas_backup_20250725_020000.dump ./kgas_backup.dump

# Restore database (coordinate with database team)
# Note: This requires stopping the application first
kubectl scale deployment/kgas-api --replicas=0 -n $NAMESPACE

# Restore Neo4j database
neo4j-admin database load neo4j --from-path=./kgas_backup.dump --overwrite-destination

# Restart application
kubectl scale deployment/kgas-api --replicas=3 -n $NAMESPACE
```

#### **Application State Recovery**
```bash
# Recover application configuration
kubectl get configmaps -n $NAMESPACE
kubectl describe configmap kgas-config -n $NAMESPACE

# Restore secrets if corrupted
kubectl delete secret kgas-db-credentials -n $NAMESPACE
# Recreate secrets using deployment procedures above

# Validate recovery
./deploy.sh status
curl http://localhost:8000/health
```

### **4.3 Disaster Recovery**

#### **Complete Environment Recreation**
```bash
# Create new namespace
kubectl create namespace kgas-disaster-recovery

# Restore from backup
export NAMESPACE="kgas-disaster-recovery"
export RECOVERY_MODE="true"

# Execute deployment with recovery flag
./deploy.sh deploy --recovery

# Restore data from most recent backup
# Follow database recovery procedures above

# Validate disaster recovery
./deploy.sh status
curl http://localhost:8000/health
```

---

## ⚙️ **5. MAINTENANCE PROCEDURES**

### **5.1 Routine Maintenance**

#### **Daily Tasks**
```bash
# Health check validation
curl http://localhost:8000/health
curl http://localhost:8000/ready

# Resource utilization check
kubectl top pods -n $NAMESPACE
kubectl top nodes

# Backup verification
kubectl get jobs -n $NAMESPACE | grep backup | tail -1
```

#### **Weekly Tasks**
```bash
# Performance analysis
kubectl exec -it deployment/kgas-api -n $NAMESPACE -- \
  python -c "
from src.core.quality_service import QualityService
from src.core.provenance_service import ProvenanceService
qs = QualityService()
ps = ProvenanceService()
print('Quality analytics:', qs.get_advanced_analytics())
print('Provenance analytics:', ps.get_advanced_analytics())
"

# Log rotation and cleanup
kubectl exec -it deployment/kgas-api -n $NAMESPACE -- \
  find /var/log -name "*.log" -mtime +7 -exec rm {} \;

# Update monitoring dashboards
kubectl apply -f k8s/monitoring.yaml -n $NAMESPACE
```

#### **Monthly Tasks**
```bash
# Security updates
kubectl get pods -n $NAMESPACE -o jsonpath="{.items[*].spec.containers[*].image}"

# Performance optimization review
kubectl exec -it deployment/kgas-api -n $NAMESPACE -- \
  python -c "
from src.core.quality_service import QualityService
qs = QualityService()
recommendations = qs.generate_optimization_recommendations()
print('Optimization recommendations:', recommendations)
"

# Capacity planning analysis
kubectl describe nodes | grep -A5 "Allocated resources"
```

### **5.2 Scaling Operations**

#### **Horizontal Scaling**
```bash
# Scale up for high load
kubectl scale deployment/kgas-api --replicas=5 -n $NAMESPACE

# Monitor scaling
kubectl rollout status deployment/kgas-api -n $NAMESPACE
kubectl get pods -n $NAMESPACE -l app=kgas

# Configure Horizontal Pod Autoscaler
kubectl autoscale deployment/kgas-api --cpu-percent=70 --min=3 --max=10 -n $NAMESPACE
```

#### **Vertical Scaling**
```bash
# Update resource limits
kubectl patch deployment/kgas-api -n $NAMESPACE -p '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "kgas-api",
          "resources": {
            "requests": {"memory": "2Gi", "cpu": "1000m"},
            "limits": {"memory": "4Gi", "cpu": "2000m"}
          }
        }]
      }
    }
  }
}'

# Monitor resource changes
kubectl rollout status deployment/kgas-api -n $NAMESPACE
kubectl top pods -n $NAMESPACE
```

---

## 📞 **6. SUPPORT AND ESCALATION**

### **6.1 Support Tiers**

#### **Tier 1: Application Support**
- **Scope**: Application errors, configuration issues, basic troubleshooting
- **Response Time**: 4 hours (business), 1 hour (critical)
- **Contacts**: Platform Team
- **Tools**: kubectl, application logs, health endpoints

#### **Tier 2: Infrastructure Support**
- **Scope**: Kubernetes issues, networking, storage, monitoring
- **Response Time**: 2 hours (business), 30 minutes (critical)
- **Contacts**: DevOps/SRE Team
- **Tools**: Kubernetes, Prometheus, Grafana, AWS

#### **Tier 3: Database Support**
- **Scope**: Neo4j issues, backup/restore, data integrity
- **Response Time**: 1 hour (business), 15 minutes (critical)
- **Contacts**: Database Team
- **Tools**: Neo4j Admin, Cypher queries, backup tools

### **6.2 Incident Response**

#### **Critical Incident (P1)**
```bash
# Immediate actions
1. Check system status: ./deploy.sh status
2. Verify monitoring: Check Grafana dashboards
3. Application logs: kubectl logs -f deployment/kgas-api -n $NAMESPACE
4. Contact on-call engineer
5. Create incident ticket

# Communication
- Slack: #kgas-incidents
- Email: kgas-ops@company.com
- Phone: On-call rotation
```

#### **High Priority Incident (P2)**
```bash
# Response actions
1. Assess impact and scope
2. Review recent changes
3. Check resource utilization
4. Engage appropriate support tier
5. Document troubleshooting steps
```

### **6.3 Knowledge Base**

#### **Common Solutions**
- **Pod CrashLoopBackOff**: Check resource limits, secrets, database connectivity
- **High Memory Usage**: Review application metrics, check for memory leaks
- **Slow Response Times**: Analyze performance metrics, check database queries
- **Backup Failures**: Verify S3 credentials, check storage quotas

#### **Useful Commands Reference**
```bash
# Quick health check
kubectl get pods -n $NAMESPACE && curl http://localhost:8000/health

# Resource status
kubectl top pods -n $NAMESPACE && kubectl top nodes

# Recent events
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10

# Service status
kubectl get svc,ingress -n $NAMESPACE
```

---

## ✅ **7. OPERATIONAL CHECKLIST**

### **Pre-Deployment Checklist**
- [ ] Environment variables configured
- [ ] Secrets created and validated
- [ ] Kubernetes cluster accessible
- [ ] Monitoring stack operational
- [ ] Backup storage accessible
- [ ] Team notifications sent

### **Post-Deployment Checklist**
- [ ] All pods running and healthy
- [ ] Health endpoints responding
- [ ] Monitoring metrics appearing
- [ ] Backup job scheduled
- [ ] Ingress/Load balancer configured
- [ ] Documentation updated

### **Weekly Operations Checklist**
- [ ] Performance metrics reviewed
- [ ] Backup status verified
- [ ] Security updates checked
- [ ] Resource utilization analyzed
- [ ] Logs reviewed for errors
- [ ] Monitoring dashboards updated

### **Monthly Operations Checklist**
- [ ] Capacity planning review
- [ ] Security audit completed
- [ ] Performance optimization applied
- [ ] Disaster recovery tested
- [ ] Documentation updated
- [ ] Team training conducted

---

## 📊 **8. PERFORMANCE BASELINES**

### **Application Performance Targets**
- **Availability**: 99.9% uptime
- **Response Time**: <2s (95th percentile)
- **Throughput**: 100+ requests/second
- **Error Rate**: <0.5%
- **Memory Usage**: <80% of allocated
- **CPU Usage**: <70% of allocated

### **Resource Utilization Baselines**
- **Pod Memory**: 1-2GB per replica
- **Pod CPU**: 0.5-1.0 cores per replica
- **Storage**: 10GB+ for logs and temp data
- **Network**: 100Mbps+ bandwidth
- **Database**: <100ms query response time

---

**Document Version**: 1.0  
**Last Updated**: 2025-07-25  
**Next Review**: 2025-08-25  
**Owner**: KGAS Operations Team

---

*This comprehensive operational guide ensures reliable, maintainable, and scalable operation of the KGAS GraphRAG system in production environments.*