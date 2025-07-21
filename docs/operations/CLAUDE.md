# Operations Documentation - CLAUDE.md

## Overview
The `docs/operations/` directory contains operational documentation for deploying, maintaining, and monitoring KGAS in production environments. This documentation covers hardware requirements, deployment procedures, monitoring setup, and operational best practices.

## Directory Structure

### Current Documentation
- **`HARDWARE.md`**: Hardware requirements and system specifications
- **`OPERATIONS.md`**: Operational procedures and maintenance guides
- **`governance/`**: Governance documentation including license compliance

### Expected Operations Documentation
- **`deployment/`**: Deployment guides for different environments
- **`monitoring/`**: Monitoring setup and alerting configuration
- **`backup/`**: Backup and recovery procedures
- **`security/`**: Security operations and incident response
- **`troubleshooting/`**: Common issues and resolution procedures

## Key Operational Areas

### 1. Deployment Operations
KGAS supports multiple deployment scenarios:

#### **Local Development**
```bash
# Quick local setup
git clone https://github.com/your-org/KGAS.git
cd KGAS
python -m venv venv
source venv/bin/activate
pip install -e .
docker-compose up -d neo4j
python main.py
```

#### **Docker Deployment**
```bash
# Production Docker deployment
docker build -f docker/Dockerfile -t kgas:latest .
docker-compose -f docker/docker-compose.production.yml up -d
```

#### **Kubernetes Deployment**
```bash
# Production Kubernetes deployment
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 2. System Requirements

#### **Minimum Hardware Requirements**
- **CPU**: 4 cores (Intel i5 or AMD Ryzen 5 equivalent)
- **Memory**: 8GB RAM (16GB recommended for large datasets)
- **Storage**: 50GB SSD storage minimum
- **Network**: Stable internet connection for LLM API access

#### **Recommended Production Hardware**
- **CPU**: 8+ cores (Intel i7/Xeon or AMD Ryzen 7/EPYC)
- **Memory**: 32GB+ RAM for enterprise workloads
- **Storage**: 500GB+ NVMe SSD with regular backup
- **Network**: High-speed connection with redundancy

#### **Database Requirements**
- **Neo4j**: Version 5.13+ with vector indexing support
- **SQLite**: Built into Python, no separate installation needed
- **Docker**: For containerized Neo4j deployment

### 3. Monitoring and Observability

#### **Health Check Endpoints**
```bash
# Check system health
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/metrics
curl http://localhost:8000/status
```

#### **Prometheus Metrics**
KGAS exposes comprehensive metrics for monitoring:
- Document processing rates and success/failure counts
- Entity extraction performance and quality metrics
- Graph construction times and node/edge counts
- Database query performance and connection health
- Memory usage, CPU utilization, and system resources

#### **Grafana Dashboards**
Pre-configured dashboards provide visualization for:
- **System Overview**: High-level system health and performance
- **Document Processing**: Processing pipeline metrics and throughput
- **Entity Analysis**: Entity extraction quality and performance
- **Graph Metrics**: Graph size, growth, and analysis performance
- **Database Performance**: Query times and resource utilization
- **Error Tracking**: Error rates, types, and recovery metrics

### 4. Security Operations

#### **Authentication and Authorization**
- **JWT Tokens**: Secure API access with configurable expiration
- **API Keys**: Secure external LLM API access
- **Rate Limiting**: Prevent abuse and ensure fair resource usage
- **Request Validation**: Input sanitization and validation

#### **Data Protection**
- **PII Encryption**: AES-GCM encryption for sensitive data
- **Secure Storage**: Encrypted databases and secure file handling
- **Audit Logging**: Comprehensive audit trail for all operations
- **Data Retention**: Configurable data retention policies

#### **Network Security**
- **HTTPS**: All external communications over encrypted channels
- **Firewall Rules**: Appropriate network access controls
- **Container Security**: Non-root containers with minimal privileges
- **Secret Management**: Secure handling of API keys and credentials

### 5. Backup and Recovery

#### **Database Backup**
```bash
# Neo4j backup
docker exec neo4j-container neo4j-admin database backup --to-path=/backups neo4j

# SQLite backup
cp data/kgas.db backups/kgas_$(date +%Y%m%d_%H%M%S).db
```

#### **Configuration Backup**
```bash
# Backup configuration files
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
    .env \
    docker-compose.*.yml \
    k8s/*.yaml \
    contracts/
```

#### **Recovery Procedures**
1. **Database Recovery**: Restore from most recent backup
2. **Configuration Recovery**: Restore configuration files
3. **Service Restart**: Restart services with restored configuration
4. **Validation**: Run health checks to verify recovery

### 6. Performance Tuning

#### **Database Optimization**
```cypher
// Neo4j performance tuning
// Create appropriate indexes
CREATE INDEX entity_id_index FOR (e:Entity) ON (e.id);
CREATE VECTOR INDEX entity_embedding_index FOR (e:Entity) ON (e.embedding);

// Configure memory settings in neo4j.conf
dbms.memory.heap.initial_size=2g
dbms.memory.heap.max_size=4g
dbms.memory.pagecache.size=2g
```

#### **Application Performance**
- **Connection Pooling**: Optimize database connection usage
- **Async Processing**: Use async operations for I/O bound tasks
- **Caching**: Cache frequently accessed data and computations
- **Resource Monitoring**: Track memory and CPU usage patterns

### 7. Troubleshooting

#### **Common Issues**

**Database Connection Problems**
```bash
# Check Neo4j status
docker ps | grep neo4j
docker logs neo4j-container

# Test connection
python -c "
from src.core.neo4j_manager import Neo4jManager
manager = Neo4jManager()
print(manager.health_check())
"
```

**Memory Issues**
```bash
# Check memory usage
free -h
docker stats

# Monitor Python memory usage
python -c "
import psutil
process = psutil.Process()
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

**API Authentication Errors**
```bash
# Verify API keys are set
python -c "
import os
print('OpenAI:', bool(os.getenv('OPENAI_API_KEY')))
print('Anthropic:', bool(os.getenv('ANTHROPIC_API_KEY')))
print('Google:', bool(os.getenv('GOOGLE_API_KEY')))
"
```

#### **Log Analysis**
```bash
# View application logs
tail -f logs/kgas.log

# Search for errors
grep -i error logs/kgas.log | tail -20

# Monitor real-time logs
docker logs -f kgas-container
```

### 8. Maintenance Procedures

#### **Regular Maintenance**
- **Daily**: Monitor system health and error rates
- **Weekly**: Review performance metrics and resource usage
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Full system backup and disaster recovery testing

#### **Update Procedures**
```bash
# Update KGAS
git pull origin main
pip install -e .
docker-compose down
docker-compose up -d

# Update dependencies
pip install --upgrade -r requirements.txt
```

#### **Database Maintenance**
```bash
# Neo4j maintenance
docker exec neo4j-container cypher-shell -u neo4j -p password \
    "CALL db.index.fulltext.listAvailableAnalyzers();"

# SQLite maintenance
python -c "
import sqlite3
conn = sqlite3.connect('data/kgas.db')
conn.execute('VACUUM;')
conn.close()
"
```

## Environment-Specific Operations

### Development Environment
- **Local Setup**: Quick development environment setup
- **Testing**: Automated testing and validation procedures
- **Debugging**: Debug configuration and troubleshooting

### Staging Environment
- **Pre-production Testing**: Full system validation before production
- **Load Testing**: Performance testing with realistic workloads
- **Integration Testing**: End-to-end system integration validation

### Production Environment
- **High Availability**: Redundancy and failover procedures
- **Monitoring**: Comprehensive monitoring and alerting
- **Security**: Enhanced security measures and compliance
- **Backup**: Regular backup and disaster recovery procedures

## Compliance and Governance

### License Compliance
- **Third-party Licenses**: Track and comply with all third-party licenses
- **License Compatibility**: Ensure license compatibility across dependencies
- **Attribution**: Proper attribution for open source components

### Data Governance
- **Data Handling**: Proper handling of research data and PII
- **Retention Policies**: Data retention and deletion procedures
- **Audit Requirements**: Audit trail and compliance reporting

### Security Compliance
- **Security Standards**: Adherence to security best practices
- **Vulnerability Management**: Regular security assessments and updates
- **Incident Response**: Security incident response procedures

## Performance Monitoring

### Key Performance Indicators (KPIs)
- **Processing Throughput**: Documents processed per hour
- **Entity Extraction Quality**: Confidence scores and accuracy metrics
- **System Availability**: Uptime and service availability
- **Response Times**: API response times and query performance
- **Resource Utilization**: CPU, memory, and storage usage

### Alerting Configuration
```yaml
# Example Prometheus alerting rules
groups:
  - name: kgas_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(kgas_errors_total[5m]) > 0.1
        annotations:
          summary: "KGAS error rate is high"
      
      - alert: DatabaseConnectionFailure
        expr: kgas_database_health == 0
        annotations:
          summary: "Database connection failed"
      
      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes > 2e9
        annotations:
          summary: "Memory usage is high"
```

## Operational Best Practices

### Deployment Best Practices
- **Blue-Green Deployment**: Zero-downtime deployments
- **Health Checks**: Comprehensive health validation
- **Rollback Procedures**: Quick rollback capabilities
- **Configuration Management**: Secure configuration handling

### Monitoring Best Practices
- **Proactive Monitoring**: Monitor leading indicators
- **Comprehensive Metrics**: Track all critical system components
- **Alert Tuning**: Minimize false positives while catching real issues
- **Dashboard Design**: Clear, actionable dashboards

### Security Best Practices
- **Principle of Least Privilege**: Minimal necessary permissions
- **Defense in Depth**: Multiple security layers
- **Regular Updates**: Keep all components updated
- **Incident Response**: Clear incident response procedures

The operations documentation ensures reliable, secure, and maintainable deployment of KGAS across different environments, supporting both research and production use cases.