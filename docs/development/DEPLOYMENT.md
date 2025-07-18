**Doc status**: Living – auto-checked by doc-governance CI

# KGAS Deployment Guide

**Document Version**: 1.0  
**Created**: 2025-01-27  
**Purpose**: Deployment procedures and container configuration for KGAS

---

## Container Configuration

### Docker Compose Services
```yaml
services:
  neo4j:
    image: neo4j:5.15.0-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_PLUGINS=["apoc"]
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_import:/var/lib/neo4j/import
      - neo4j_plugins:/plugins

  qdrant:
    image: qdrant/qdrant:v1.7.0
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334

  kgas-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
    depends_on:
      - neo4j
      - qdrant
    volumes:
      - ./data:/app/data
      - ./config:/app/config

volumes:
  neo4j_data:
  neo4j_logs:
  neo4j_import:
  neo4j_plugins:
  qdrant_data:
```

---

## Quick Start Deployment

### Prerequisites
- Docker and Docker Compose installed
- At least 16GB RAM available
- 100GB free disk space

### Deployment Steps
```bash
# Clone the repository
git clone https://github.com/your-org/kgas.git
cd kgas

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration

# Start services
docker compose up -d

# Verify deployment
docker compose ps
curl http://localhost:8000/health

# Access services
# Neo4j Browser: http://localhost:7474
# Qdrant Dashboard: http://localhost:6333/dashboard
# KGAS API: http://localhost:8000
```

---

## Production Deployment

### Environment Configuration
```bash
# Production environment variables
export NODE_ENV=production
export LOG_LEVEL=INFO
export METRICS_PORT=9102
export PII_SALT_FILE=/etc/kgas/pii_salt
export PII_VAULT_PATH=/var/lib/kgas/pii_vault.sqlite
```

### Security Configuration
```bash
# Set up PII salt
sudo mkdir -p /etc/kgas
sudo openssl rand -hex 32 > /etc/kgas/pii_salt
sudo chmod 600 /etc/kgas/pii_salt

# Set up PII vault
mkdir -p /var/lib/kgas
touch /var/lib/kgas/pii_vault.sqlite
chmod 600 /var/lib/kgas/pii_vault.sqlite
```

### Monitoring Setup
```bash
# Start monitoring stack
docker compose -f docker-compose.monitoring.yml up -d

# Configure alerts
python scripts/configure_monitoring.py
```

---

## Scaling Configuration

### Horizontal Scaling
```yaml
# docker-compose.scale.yml
services:
  kgas-app:
    deploy:
      replicas: 3
    environment:
      - NODE_ID=${HOSTNAME}
      - CLUSTER_MODE=true

  neo4j:
    image: neo4j:5.15.0-enterprise
    environment:
      - NEO4J_dbms_mode=CLUSTER
      - NEO4J_causal__clustering_initial__discovery__members=neo4j-1:5000,neo4j-2:5000,neo4j-3:5000
```

### Load Balancing
```yaml
# nginx.conf
upstream kgas_backend {
    server kgas-app-1:8000;
    server kgas-app-2:8000;
    server kgas-app-3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://kgas_backend;
    }
}
```

---

## Backup and Recovery

### Backup Procedures
```bash
# Database backup
docker exec neo4j neo4j-admin dump --database=neo4j --to=/backups/

# Vector database backup
curl -X POST "http://localhost:6333/collections/entities/snapshots"

# Configuration backup
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/
```

### Recovery Procedures
```bash
# Database recovery
docker exec neo4j neo4j-admin load --from=/backups/neo4j.dump --database=neo4j --force

# Vector database recovery
curl -X POST "http://localhost:6333/collections/entities/snapshots/restore"

# Configuration recovery
tar -xzf config_backup_20250127.tar.gz
```

---

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker compose logs

# Check resource usage
docker stats

# Restart services
docker compose restart
```

#### Performance Issues
```bash
# Check resource limits
docker compose exec neo4j neo4j-admin memrec

# Optimize Neo4j
docker compose exec neo4j cypher-shell "CALL dbms.listConfig()"

# Check Qdrant performance
curl "http://localhost:6333/collections/entities"
```

#### Connection Issues
```bash
# Test Neo4j connection
docker compose exec kgas-app python -c "from neo4j import GraphDatabase; print(GraphDatabase.driver('bolt://neo4j:7687', auth=('neo4j', 'password')).verify_connectivity())"

# Test Qdrant connection
curl "http://localhost:6333/collections"
```

---

## Monitoring and Logging

### Metrics Endpoints
- **Application Metrics**: http://localhost:8000/metrics
- **Neo4j Metrics**: http://localhost:7474/browser/
- **Qdrant Metrics**: http://localhost:6333/metrics

### Log Aggregation
```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f kgas-app

# Export logs
docker compose logs > kgas_logs_$(date +%Y%m%d).log
```

---

**Note**: This deployment guide provides the essential information for deploying KGAS in various environments. Always test deployment procedures in a staging environment before production deployment. -e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>
