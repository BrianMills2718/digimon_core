# Task TD.5: Scaling and Backup Automation

## Overview
Implement production scaling capabilities and automated backup strategies for high availability and disaster recovery.

**Duration**: Weeks 9-10  
**Priority**: MEDIUM  
**Prerequisites**: Task TD.4 (Testing Infrastructure) complete  

## Current State Analysis

### Scaling Limitations
- **Manual scaling only**: No auto-scaling configuration
- **Single instance**: No load balancing setup
- **Fixed resources**: No dynamic resource allocation
- **No horizontal scaling**: Database and application monolithic

### Backup Gaps
- **Manual backups**: No automated backup schedule
- **No versioning**: Configuration changes not tracked
- **Limited recovery**: No automated recovery procedures
- **No validation**: Backups not tested for restoration

## Implementation Plan

### Step 1: Kubernetes Deployment Configuration (Day 1-3)

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: kgas-production

---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kgas-app
  namespace: kgas-production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kgas
  template:
    metadata:
      labels:
        app: kgas
    spec:
      containers:
      - name: kgas
        image: kgas:latest
        ports:
        - containerPort: 8000
        env:
        - name: NEO4J_URI
          valueFrom:
            secretKeyRef:
              name: kgas-secrets
              key: neo4j-uri
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
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

---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: kgas-service
  namespace: kgas-production
spec:
  selector:
    app: kgas
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer

---
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: kgas-hpa
  namespace: kgas-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: kgas-app
  minReplicas: 2
  maxReplicas: 20
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
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
      - type: Pods
        value: 4
        periodSeconds: 60
```

### Step 2: Database Scaling Configuration (Day 4-5)

```yaml
# k8s/neo4j-cluster.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: neo4j-cluster
  namespace: kgas-production
spec:
  serviceName: neo4j
  replicas: 3
  selector:
    matchLabels:
      app: neo4j
  template:
    metadata:
      labels:
        app: neo4j
    spec:
      containers:
      - name: neo4j
        image: neo4j:enterprise
        env:
        - name: NEO4J_ACCEPT_LICENSE_AGREEMENT
          value: "yes"
        - name: NEO4J_dbms_mode
          value: "CORE"
        - name: NEO4J_causal__clustering_minimum__core__cluster__size__at__formation
          value: "3"
        - name: NEO4J_causal__clustering_discovery__type
          value: "K8S"
        - name: NEO4J_causal__clustering_kubernetes_service__name
          value: "neo4j"
        volumeClaimTemplates:
        - metadata:
            name: data
          spec:
            accessModes: ["ReadWriteOnce"]
            resources:
              requests:
                storage: 100Gi

# src/core/neo4j_cluster_manager.py
class Neo4jClusterManager:
    """Manage Neo4j cluster connections with read replicas"""
    
    def __init__(self, core_servers: List[str], read_replicas: List[str]):
        self.core_servers = core_servers
        self.read_replicas = read_replicas
        self._core_drivers = []
        self._replica_drivers = []
        self._init_drivers()
    
    def _init_drivers(self):
        """Initialize drivers for all servers"""
        for server in self.core_servers:
            driver = GraphDatabase.driver(
                server,
                auth=self._get_auth(),
                max_connection_pool_size=10
            )
            self._core_drivers.append(driver)
        
        for server in self.read_replicas:
            driver = GraphDatabase.driver(
                server,
                auth=self._get_auth(),
                max_connection_pool_size=20
            )
            self._replica_drivers.append(driver)
    
    async def execute_write(self, query: str, params: Dict = None):
        """Execute write query on core server"""
        driver = self._get_healthy_core_driver()
        async with driver.session(default_access_mode=WRITE_ACCESS) as session:
            return await session.run(query, params)
    
    async def execute_read(self, query: str, params: Dict = None):
        """Execute read query on replica"""
        driver = self._get_healthy_replica_driver()
        async with driver.session(default_access_mode=READ_ACCESS) as session:
            return await session.run(query, params)
```

### Step 3: Automated Backup System (Day 6-7)

```python
# src/core/backup_automation.py
import asyncio
import aioboto3
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

class AutomatedBackupManager:
    """Automated backup system with validation"""
    
    def __init__(self, config: BackupConfig):
        self.config = config
        self.s3_client = None
        self._init_s3()
    
    async def schedule_backups(self):
        """Schedule automated backups"""
        while True:
            try:
                # Hourly incremental
                await self.incremental_backup()
                await asyncio.sleep(3600)  # 1 hour
                
                # Daily full backup at 2 AM
                if datetime.now().hour == 2:
                    await self.full_backup()
                
                # Weekly backup validation
                if datetime.now().weekday() == 0:  # Monday
                    await self.validate_backups()
                    
            except Exception as e:
                logger.error(f"Backup failed: {e}")
                await self.alert_backup_failure(e)
    
    async def incremental_backup(self):
        """Perform incremental backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Neo4j incremental backup
        neo4j_backup = await self._backup_neo4j_incremental(timestamp)
        
        # Application state backup
        app_backup = await self._backup_application_state(timestamp)
        
        # Upload to S3
        await self._upload_to_s3(neo4j_backup, f"incremental/neo4j/{timestamp}")
        await self._upload_to_s3(app_backup, f"incremental/app/{timestamp}")
        
        # Cleanup old incremental backups (keep 24 hours)
        await self._cleanup_old_backups("incremental", timedelta(days=1))
    
    async def full_backup(self):
        """Perform full system backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Stop writes temporarily
        async with self.maintenance_mode():
            # Neo4j full backup
            neo4j_backup = await self._backup_neo4j_full(timestamp)
            
            # PostgreSQL backup (checkpoints, config)
            pg_backup = await self._backup_postgresql(timestamp)
            
            # Configuration backup
            config_backup = await self._backup_configuration(timestamp)
        
        # Upload to S3 with redundancy
        for backup, path in [
            (neo4j_backup, f"full/neo4j/{timestamp}"),
            (pg_backup, f"full/postgresql/{timestamp}"),
            (config_backup, f"full/config/{timestamp}")
        ]:
            await self._upload_to_s3(backup, path)
            await self._upload_to_glacier(backup, path)  # Long-term storage
        
        # Keep 30 days of full backups
        await self._cleanup_old_backups("full", timedelta(days=30))
    
    async def _backup_neo4j_incremental(self, timestamp: str) -> Path:
        """Incremental Neo4j backup using transaction logs"""
        backup_path = Path(f"/tmp/neo4j_incremental_{timestamp}")
        
        cmd = [
            "neo4j-admin", "backup",
            "--incremental",
            "--from", self.config.neo4j_uri,
            "--to", str(backup_path)
        ]
        
        await asyncio.create_subprocess_exec(*cmd)
        return backup_path
    
    async def validate_backups(self):
        """Validate backup integrity"""
        # Get latest backup
        latest_backup = await self._get_latest_backup()
        
        # Test restoration in isolated environment
        test_env = await self._create_test_environment()
        
        try:
            # Restore backup
            await self._restore_backup(latest_backup, test_env)
            
            # Run validation queries
            validation_passed = await self._run_validation_suite(test_env)
            
            if not validation_passed:
                await self.alert_validation_failure()
            
        finally:
            await self._cleanup_test_environment(test_env)

# scripts/backup_automation.sh
#!/bin/bash
# Automated backup script with monitoring

set -euo pipefail

BACKUP_DIR="/var/backups/kgas"
S3_BUCKET="s3://kgas-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Function to send alerts
alert() {
    local message="$1"
    curl -X POST "$SLACK_WEBHOOK" \
        -H 'Content-Type: application/json' \
        -d "{\"text\": \"Backup Alert: $message\"}"
}

# Neo4j backup
echo "Starting Neo4j backup..."
neo4j-admin backup \
    --database=neo4j \
    --to="$BACKUP_DIR/neo4j_$TIMESTAMP" || {
        alert "Neo4j backup failed"
        exit 1
    }

# Compress backup
tar -czf "$BACKUP_DIR/neo4j_$TIMESTAMP.tar.gz" \
    "$BACKUP_DIR/neo4j_$TIMESTAMP"

# Upload to S3
aws s3 cp "$BACKUP_DIR/neo4j_$TIMESTAMP.tar.gz" \
    "$S3_BUCKET/neo4j/" \
    --storage-class STANDARD_IA

# Verify upload
aws s3api head-object \
    --bucket "${S3_BUCKET#s3://}" \
    --key "neo4j/neo4j_$TIMESTAMP.tar.gz" || {
        alert "S3 upload verification failed"
        exit 1
    }

# Cleanup local files older than 7 days
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed successfully"
```

### Step 4: Disaster Recovery Procedures (Day 8-9)

```python
# src/core/disaster_recovery.py
class DisasterRecoveryManager:
    """Automated disaster recovery procedures"""
    
    def __init__(self, config: DRConfig):
        self.config = config
        self.health_monitor = HealthMonitor()
    
    async def monitor_and_recover(self):
        """Monitor system health and trigger recovery"""
        while True:
            health_status = await self.health_monitor.check_all()
            
            if not health_status.healthy:
                await self.initiate_recovery(health_status)
            
            await asyncio.sleep(30)  # Check every 30 seconds
    
    async def initiate_recovery(self, health_status: HealthStatus):
        """Initiate appropriate recovery procedure"""
        if health_status.database_down:
            await self.recover_database()
        
        if health_status.service_degraded:
            await self.recover_services()
        
        if health_status.total_failure:
            await self.full_disaster_recovery()
    
    async def recover_database(self):
        """Recover database from backup"""
        logger.warning("Database failure detected, initiating recovery")
        
        # 1. Stop dependent services
        await self.stop_services()
        
        # 2. Get latest valid backup
        backup = await self.get_latest_valid_backup()
        
        # 3. Restore database
        await self.restore_database(backup)
        
        # 4. Validate restoration
        if await self.validate_database():
            await self.start_services()
            logger.info("Database recovery successful")
        else:
            await self.escalate_to_manual_intervention()
    
    async def full_disaster_recovery(self):
        """Complete system recovery procedure"""
        logger.critical("Total system failure, initiating full DR")
        
        # 1. Switch to DR site
        await self.activate_dr_site()
        
        # 2. Restore from latest backup
        await self.restore_full_system()
        
        # 3. Verify system integrity
        await self.run_integrity_checks()
        
        # 4. Switch traffic to DR site
        await self.update_dns_to_dr()
        
        # 5. Notify stakeholders
        await self.send_dr_notifications()

# scripts/dr_test.sh
#!/bin/bash
# Monthly disaster recovery test

echo "Starting DR test at $(date)"

# 1. Create test environment
kubectl create namespace dr-test

# 2. Deploy test instance
kubectl apply -f k8s/dr-test-deployment.yaml -n dr-test

# 3. Restore latest backup
./scripts/restore_backup.sh --target dr-test

# 4. Run validation suite
python scripts/validate_dr_restoration.py

# 5. Cleanup
kubectl delete namespace dr-test

echo "DR test completed"
```

### Step 5: Monitoring and Alerting (Day 10)

```yaml
# k8s/monitoring.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: kgas-production
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    
    rule_files:
      - 'alerts.yml'
    
    scrape_configs:
      - job_name: 'kgas-apps'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names:
                - kgas-production
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_app]
            action: keep
            regex: kgas

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: alert-rules
  namespace: kgas-production
data:
  alerts.yml: |
    groups:
      - name: kgas_alerts
        rules:
          - alert: HighMemoryUsage
            expr: container_memory_usage_bytes{pod=~"kgas-.*"} > 1.5e9
            for: 5m
            labels:
              severity: warning
            annotations:
              summary: "High memory usage in {{ $labels.pod }}"
          
          - alert: PodCrashLooping
            expr: rate(kube_pod_container_status_restarts_total{namespace="kgas-production"}[15m]) > 0
            for: 5m
            labels:
              severity: critical
            annotations:
              summary: "Pod {{ $labels.pod }} is crash looping"
          
          - alert: BackupFailed
            expr: backup_last_success_timestamp_seconds < (time() - 7200)
            for: 10m
            labels:
              severity: critical
            annotations:
              summary: "Backup hasn't succeeded in 2 hours"
```

## Implementation Checklist

### Kubernetes Deployment
- [ ] Create namespace and secrets
- [ ] Deploy application with HPA
- [ ] Configure service and ingress
- [ ] Set up Neo4j cluster
- [ ] Test auto-scaling behavior

### Backup Automation
- [ ] Implement backup manager
- [ ] Schedule automated backups
- [ ] Configure S3 storage
- [ ] Set up backup validation
- [ ] Test restoration procedures

### Disaster Recovery
- [ ] Document DR procedures
- [ ] Automate recovery scripts
- [ ] Set up DR site
- [ ] Test failover process
- [ ] Create runbooks

### Monitoring
- [ ] Deploy Prometheus
- [ ] Configure alerts
- [ ] Set up Grafana dashboards
- [ ] Integrate with PagerDuty
- [ ] Test alert routing

## Success Criteria

### Week 9 Completion
- [ ] Kubernetes deployment working
- [ ] Auto-scaling configured and tested
- [ ] Database clustering operational
- [ ] Basic backup automation

### Week 10 Completion
- [ ] Full backup system automated
- [ ] DR procedures documented
- [ ] Monitoring and alerting active
- [ ] Recovery procedures tested
- [ ] Documentation complete

## Testing Procedures

### Scaling Tests
```bash
# Generate load to test auto-scaling
kubectl run -i --tty load-generator --rm --image=busybox -- /bin/sh
while true; do wget -q -O- http://kgas-service/heavy-endpoint; done

# Monitor scaling
kubectl get hpa -w
kubectl get pods -w
```

### Backup Tests
```bash
# Test backup creation
./scripts/backup_automation.sh

# Test restoration
./scripts/restore_backup.sh --backup backup_20240124_120000.tar.gz --target test-env

# Validate restoration
python scripts/validate_restoration.py --target test-env
```

### DR Tests
```bash
# Simulate failure
kubectl delete deployment kgas-app -n kgas-production

# Monitor recovery
watch kubectl get pods -n kgas-production

# Test DR site activation
./scripts/activate_dr_site.sh
```

## Production Readiness

### Pre-Production Checklist
- [ ] All automated tests passing
- [ ] Backup/restore verified
- [ ] DR procedures tested
- [ ] Monitoring alerts working
- [ ] Runbooks documented
- [ ] Team trained on procedures

### Go-Live Requirements
- [ ] 99.9% uptime SLA defined
- [ ] RTO < 4 hours documented
- [ ] RPO < 1 hour achieved
- [ ] On-call rotation established
- [ ] Incident response procedures