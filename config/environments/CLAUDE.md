# Environment Configurations - CLAUDE.md

## Overview
The `config/environments/` directory contains environment-specific configuration files for different deployment scenarios of KGAS. These configurations ensure appropriate settings for development, testing, staging, and production environments.

## Directory Structure

### Current Files
- **`docker-compose.yml`**: Default development environment configuration
- **`docker-compose.prod.yml`**: Production environment configuration with optimized settings

### Expected Environment Files
- **`development.yml`**: Local development environment settings
- **`testing.yml`**: CI/CD testing environment configuration
- **`staging.yml`**: Pre-production staging environment
- **`production.yml`**: Production environment with full security and monitoring

## Environment Strategy

### Multi-Environment Architecture
```yaml
# Environment progression strategy
Development → Testing → Staging → Production
     ↓           ↓         ↓          ↓
  Local Dev   CI/CD     Pre-prod   Live System
  Fast/Debug  Reliable  Realistic  Optimized
  Mock APIs   Test APIs Prod APIs  Prod APIs
  SQLite      SQLite    Neo4j      Neo4j+HA
```

### Configuration Inheritance
```yaml
# Configuration layering approach
base_config:          # Common settings across all environments
  ↓
environment_config:   # Environment-specific overrides
  ↓
local_overrides:      # Developer/deployment specific settings
```

## Environment Configurations

### Development Environment (`docker-compose.yml`)

#### Purpose
Local development environment optimized for developer productivity and fast iteration.

#### Key Features
```yaml
services:
  kgas-app:
    build: 
      context: ../..
      dockerfile: Dockerfile.dev  # Development dockerfile
    environment:
      - LOG_LEVEL=DEBUG
      - RELOAD_ON_CHANGE=true
      - MOCK_EXTERNAL_APIS=true
      - DATABASE_TIMEOUT=10
    ports:
      - "8000:8000"    # Main application
      - "8501:8501"    # Streamlit UI
    volumes:
      - ../../src:/app/src:delegated  # Live code reload
      - ../../tests:/app/tests:ro
      - dev_data:/app/data
    depends_on:
      - neo4j-dev
      
  neo4j-dev:
    image: neo4j:5.13-community
    environment:
      - NEO4J_AUTH=neo4j/devpassword
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_dbms_memory_heap_max__size=1G
      - NEO4J_dbms_memory_pagecache_size=512M
    ports:
      - "7474:7474"    # Browser interface
      - "7687:7687"    # Bolt protocol
    volumes:
      - neo4j_dev_data:/data
      - neo4j_dev_logs:/logs
```

#### Development Optimizations
- **Fast startup**: Minimal resource allocation for quick container startup
- **Live reload**: Source code changes reflected immediately
- **Debug logging**: Verbose logging for development debugging
- **Mock services**: External API mocking to avoid rate limits and costs
- **Port exposure**: All ports exposed for easy access and debugging

### Production Environment (`docker-compose.prod.yml`)

#### Purpose
Production-ready configuration with security, performance, and reliability optimizations.

#### Key Features
```yaml
services:
  kgas-app:
    image: kgas:${VERSION:-latest}
    restart: unless-stopped
    environment:
      - LOG_LEVEL=INFO
      - DATABASE_POOL_SIZE=20
      - METRICS_ENABLED=true
      - SECURITY_ENHANCED=true
      - PERFORMANCE_MODE=production
    ports:
      - "8000:8000"    # Only necessary ports exposed
    volumes:
      - prod_data:/app/data:rw
      - prod_logs:/app/logs:rw
      - /etc/ssl/certs:/etc/ssl/certs:ro  # SSL certificates
    depends_on:
      - neo4j-prod
      - redis-cache
      - monitoring
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G
      
  neo4j-prod:
    image: neo4j:5.13-enterprise
    restart: unless-stopped
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
      - NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
      - NEO4J_dbms_memory_heap_max__size=4G
      - NEO4J_dbms_memory_pagecache_size=2G
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*
      - NEO4J_dbms_backup_enabled=true
    volumes:
      - neo4j_prod_data:/data
      - neo4j_prod_logs:/logs
      - neo4j_prod_backups:/backups
    ports:
      - "127.0.0.1:7687:7687"  # Only local access
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G
          
  redis-cache:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "127.0.0.1:6379:6379"
      
  monitoring:
    image: prom/prometheus:latest
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    volumes:
      - ../monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "127.0.0.1:9090:9090"
```

#### Production Optimizations
- **Resource limits**: Proper CPU and memory allocation
- **Health checks**: Comprehensive health monitoring
- **Security**: Minimal port exposure and enhanced security
- **Performance**: Optimized database and cache configuration
- **Monitoring**: Built-in Prometheus monitoring
- **Backup**: Automated backup configuration

## Environment-Specific Settings

### Database Configuration

#### Development Database
```yaml
# Optimized for fast development cycles
neo4j_dev_config:
  memory:
    heap_size: "1G"
    page_cache: "512M"
  performance:
    query_timeout: "10s"
    transaction_timeout: "30s"
  features:
    apoc_enabled: true
    debug_logging: true
    query_logging: true
```

#### Production Database
```yaml
# Optimized for performance and reliability
neo4j_prod_config:
  memory:
    heap_size: "4G"
    page_cache: "2G"
  performance:
    query_timeout: "60s"
    transaction_timeout: "300s"
  security:
    auth_enabled: true
    ssl_enabled: true
    backup_enabled: true
  monitoring:
    metrics_enabled: true
    slow_query_logging: true
```

### Application Configuration

#### Development Settings
```yaml
# Development-optimized application settings
dev_app_config:
  logging:
    level: "DEBUG"
    format: "detailed"
    console_output: true
  
  apis:
    mock_external: true
    rate_limits: false
    timeout: 10
  
  database:
    pool_size: 5
    connection_timeout: 5
    retry_attempts: 3
  
  features:
    auto_reload: true
    debug_mode: true
    profiling: true
```

#### Production Settings
```yaml
# Production-optimized application settings
prod_app_config:
  logging:
    level: "INFO"
    format: "json"
    file_output: true
    rotation: "daily"
  
  apis:
    mock_external: false
    rate_limits: true
    timeout: 60
    retry_backoff: "exponential"
  
  database:
    pool_size: 20
    connection_timeout: 30
    retry_attempts: 5
    health_check_interval: 60
  
  security:
    jwt_expiration: 3600
    api_key_rotation: true
    audit_logging: true
  
  performance:
    cache_enabled: true
    compression: true
    optimization_level: "high"
```

## Security Configurations

### Development Security
```yaml
# Relaxed security for development ease
dev_security:
  authentication:
    required: false
    mock_users: true
  
  api_keys:
    validation: "basic"
    test_keys: true
  
  encryption:
    level: "basic"
    test_data: true
  
  network:
    all_ports_exposed: true
    cors_permissive: true
```

### Production Security
```yaml
# Enhanced security for production
prod_security:
  authentication:
    required: true
    jwt_validation: "strict"
    session_timeout: 3600
  
  api_keys:
    validation: "comprehensive"
    rotation_enabled: true
    audit_trail: true
  
  encryption:
    level: "enterprise"
    key_management: "external"
    data_at_rest: true
    data_in_transit: true
  
  network:
    minimal_ports: true
    firewall_rules: "strict"
    intrusion_detection: true
    ddos_protection: true
```

## Monitoring and Observability

### Development Monitoring
```yaml
# Basic monitoring for development
dev_monitoring:
  metrics:
    enabled: true
    detailed_debug: true
    local_dashboard: true
  
  logging:
    level: "DEBUG"
    console_output: true
    file_retention: "7 days"
  
  alerts:
    enabled: false
    notification_channels: ["console"]
```

### Production Monitoring
```yaml
# Comprehensive production monitoring
prod_monitoring:
  metrics:
    prometheus: true
    grafana_dashboards: true
    custom_metrics: true
    sla_monitoring: true
  
  logging:
    centralized: true
    structured_logs: true
    log_aggregation: "elasticsearch"
    retention: "90 days"
  
  alerts:
    multi_channel: true
    escalation_policies: true
    incident_management: true
    notification_channels: ["email", "slack", "pagerduty"]
  
  tracing:
    distributed_tracing: true
    performance_profiling: true
    request_tracking: true
```

## Environment Management Commands

### Development Environment
```bash
# Start development environment
cd config/environments
docker-compose up -d

# View logs
docker-compose logs -f kgas-app

# Connect to development database
docker-compose exec neo4j-dev cypher-shell -u neo4j -p devpassword

# Restart with new code
docker-compose restart kgas-app

# Clean development environment
docker-compose down -v
```

### Production Environment
```bash
# Start production environment
cd config/environments
docker-compose -f docker-compose.prod.yml up -d

# Health check
curl http://localhost:8000/health

# Monitor performance
docker-compose -f docker-compose.prod.yml exec monitoring curl http://localhost:9090/metrics

# Backup database
docker-compose -f docker-compose.prod.yml exec neo4j-prod neo4j-admin database backup --to-path=/backups neo4j

# Rolling restart
docker-compose -f docker-compose.prod.yml restart kgas-app
```

### Environment Switching
```bash
# Switch from dev to production
docker-compose down
docker-compose -f docker-compose.prod.yml up -d

# Switch with data migration
./scripts/migrate_environment.sh dev prod

# Validate environment
./scripts/validate_environment.sh prod
```

## Configuration Validation

### Environment Validation Scripts
```bash
# Validate environment configuration
python scripts/validate_config.py config/environments/docker-compose.prod.yml

# Test environment connectivity
python scripts/test_environment.py --env production

# Security audit
python scripts/security_audit.py --env production

# Performance baseline
python scripts/performance_baseline.py --env production
```

### Health Checks
```bash
# Comprehensive environment health check
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/metrics

# Database connectivity
python -c "
from src.core.neo4j_manager import Neo4jManager
manager = Neo4jManager()
print(manager.health_check())
"

# External service connectivity
python scripts/test_external_apis.py
```

## Best Practices

### Environment Design
1. **Separation of Concerns**: Clear separation between environment types
2. **Configuration as Code**: All environment settings in version control
3. **Secret Management**: Proper secret handling for each environment
4. **Resource Optimization**: Appropriate resource allocation per environment
5. **Security Gradation**: Security measures appropriate to environment risk

### Environment Management
1. **Automated Deployment**: Use CI/CD for environment provisioning
2. **Configuration Validation**: Validate configurations before deployment
3. **Monitoring**: Comprehensive monitoring for all environments
4. **Backup and Recovery**: Appropriate backup strategies per environment
5. **Documentation**: Clear documentation for environment procedures

### Development Workflow
1. **Local Development**: Easy local environment setup and teardown
2. **Feature Testing**: Isolated testing environments for feature development
3. **Integration Testing**: Staging environment for integration validation
4. **Production Deployment**: Safe and reliable production deployment
5. **Rollback Capability**: Quick rollback procedures for all environments

The environment configurations provide a robust foundation for running KGAS across different deployment scenarios while maintaining appropriate security, performance, and operational characteristics for each use case.