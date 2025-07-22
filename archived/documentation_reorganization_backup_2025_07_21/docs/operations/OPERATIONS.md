---
status: living
---

# KGAS Operations Guide

**Document Version**: 1.0  
**Created**: 2025-01-27  
**Purpose**: Operational procedures and maintenance for the Knowledge Graph Analysis System

---

## System Administration

### Service Management
```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart specific service
docker compose restart neo4j

# View service logs
docker compose logs -f neo4j
```

### Health Monitoring
```bash
# Check service health
docker compose ps

# Monitor resource usage
docker stats

# Check disk space
df -h

# Monitor memory usage
free -h
```

---

## Backup and Recovery

### Backup Procedures
```bash
# Full system backup
make full-backup

# This command dumps:
# - Neo4j database
# - Redis cache
# - PII vault
# - Configuration files
# - Log files
```

### Recovery Procedures
```bash
# Restore from backup
make restore-backup

# Target restore time on clean hardware: ≤ 60 minutes

# Verify restoration
make verify-restore
```

### Backup Schedule
- **Daily**: Full system backups
- **Weekly**: Incremental backups
- **Monthly**: Offsite backup copies
- **Quarterly**: Disaster recovery testing

---

## Performance Monitoring

### Key Metrics
- **CPU Usage**: Target <80%
- **Memory Usage**: Target <85%
- **Disk Usage**: Target <90%
- **Response Time**: Target <5s for queries
- **Throughput**: Target >100 documents/hour

### Monitoring Tools
```bash
# System monitoring
htop
iotop
nethogs

# Application monitoring
python scripts/monitor_performance.py

# Database monitoring
cypher-shell "CALL dbms.listConnections()"
```

---

## Security Operations

### Access Management
```bash
# Rotate API keys
python scripts/rotate_api_keys.py

# Update passwords
python scripts/update_passwords.py

# Audit access logs
python scripts/audit_access.py
```

### PII Management
```bash
# Rotate salt quarterly
scripts/rotate_salt.sh

# Audit PII vault
python scripts/audit_pii_vault.py

# Export PII for compliance
python scripts/export_pii_report.py
```

#### Salt location
```bash
cat /etc/kgas/pii_salt            # read-only mount
# Annual rotation (run by cron)
scripts/rotate_salt.sh --vault ~/.kgas/pii_vault.sqlite --salt-file /etc/kgas/pii_salt
```

---

## Maintenance Procedures

### Regular Maintenance
```bash
# Daily tasks
python scripts/daily_maintenance.py

# Weekly tasks
python scripts/weekly_maintenance.py

# Monthly tasks
python scripts/monthly_maintenance.py
```

### Reloading Policies Without Downtime

To reload OPA/Rego policies without downtime:

1. Update policy files in the `policies/` directory.
2. Send a SIGHUP or use the OPA API to trigger a policy reload:
   ```bash
   curl -X POST http://localhost:8181/v1/policies/reload
   ```
3. OPA will reload all policies in place; no service restart required.

- Always validate policies with `opa test` before reloading in production.

### Database Maintenance
```bash
# Neo4j maintenance
cypher-shell "CALL dbms.listConnections()"
cypher-shell "CALL dbms.listTransactions()"

# Redis maintenance
sqlite3 metadata.db "VACUUM;"
```

---

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker compose logs service_name

# Check resources
docker system df

# Restart Docker
sudo systemctl restart docker
```

#### High Memory Usage
```bash
# Check memory usage
docker stats

# Restart memory-intensive services
docker compose restart neo4j

# Increase memory limits in docker-compose.yml
```

#### Slow Performance
```bash
# Check CPU usage
htop

# Check disk I/O
iotop

# Check network
nethogs

# Optimize database
python scripts/optimize_databases.py
```

---

## Disaster Recovery

### Recovery Procedures
1. **Assess Damage**: Determine scope of failure
2. **Stop Services**: Halt all affected services
3. **Restore Data**: Restore from latest backup
4. **Verify Integrity**: Run integrity checks
5. **Restart Services**: Start services in order
6. **Test Functionality**: Verify system operation

### Recovery Time Objectives
- **RTO**: 60 minutes for full system recovery
- **RPO**: 24 hours maximum data loss
- **MTTR**: 30 minutes mean time to repair

---

## Compliance and Auditing

### Audit Procedures
```bash
# Security audit
python scripts/security_audit.py

# Compliance check
python scripts/compliance_check.py

# Data audit
python scripts/data_audit.py
```

### Reporting
- **Monthly**: Security and compliance reports
- **Quarterly**: Performance and capacity reports
- **Annually**: Full system audit reports

---

## Scaling Operations

### Vertical Scaling
```bash
# Increase memory limits
# Edit docker-compose.yml
# Increase memory: 16g -> 32g

# Increase CPU limits
# Edit docker-compose.yml
# Increase cpus: 4 -> 8
```

### Horizontal Scaling
```bash
# To be added: Neo4j cluster scaling instructions

# Add Neo4j instances
docker compose up -d neo4j-2 neo4j-3

# Configure load balancing
python scripts/configure_load_balancer.py
```

### Helm Chart Deployment
```bash
# Deploy to Kubernetes cluster
helm install kgas ./helm/kgas

# Scale horizontally
kubectl scale statefulset kgas-neo4j --replicas=3

# Monitor deployment
kubectl get pods -l app=kgas
kubectl logs -f deployment/kgas-api
```

---

## Monitoring and Alerting

### Alert Configuration
```bash
# Set up monitoring
python scripts/setup_monitoring.py

# Configure alerts
python scripts/configure_alerts.py

# Test alerting
python scripts/test_alerts.py
```

### Alert Channels
- **Email**: Critical system alerts
- **Slack**: Operational notifications
- **SMS**: Emergency alerts
- **Webhook**: Integration with external systems

---

## Monitoring Stack Setup

To enable observability, deploy the open-source monitoring stack:

```yaml
docker-compose:
  services:
    otel-collector:
      image: otel/opentelemetry-collector:latest
      ports:
        - "4317:4317"  # OTLP gRPC
        - "4318:4318"  # OTLP HTTP
      volumes:
        - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
      command: ["--config=/etc/otel-collector-config.yaml"]

    grafana:
      image: grafana/grafana:latest
      ports:
        - "3000:3000"
      environment:
        - GF_SECURITY_ADMIN_PASSWORD=admin
      depends_on:
        - tempo

    tempo:
      image: grafana/tempo:latest
      ports:
        - "3200:3200"
      command: ["-config.file=/etc/tempo.yaml"]
      volumes:
        - ./tempo.yaml:/etc/tempo.yaml
```

- **otel-collector**: Receives spans from KGAS services
- **grafana**: Visualizes traces and metrics
- **tempo**: Stores distributed traces

See the official OTel and Grafana docs for advanced configuration.

---

**Note**: This operations guide should be updated as the system evolves and new operational procedures are developed. -e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>
