# Monitoring Configuration - CLAUDE.md

## Overview
The `config/monitoring/` directory contains configuration files for the comprehensive monitoring stack that provides observability, metrics collection, alerting, and performance tracking for KGAS across all environments.

## Directory Structure

### Current Files
- **`docker-compose.monitoring.yml`**: Complete monitoring stack deployment
- **`prometheus.yml`**: Prometheus metrics collection configuration
- **`grafana-datasources.yml`**: Grafana data source configuration

### Monitoring Architecture
```yaml
# Complete monitoring stack
monitoring_stack:
  metrics_collection:   # Prometheus
  visualization:        # Grafana
  log_aggregation:     # Elasticsearch/Fluentd (planned)
  alerting:            # AlertManager
  uptime_monitoring:   # Custom health checks
  performance:         # APM integration
```

## Monitoring Stack Components

### Prometheus Configuration (`prometheus.yml`)

#### Core Metrics Collection
```yaml
# Prometheus scraping configuration
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'kgas-production'
    environment: '${ENVIRONMENT:-production}'

rule_files:
  - "alert_rules.yml"
  - "recording_rules.yml"

scrape_configs:
  # KGAS Application Metrics
  - job_name: 'kgas-app'
    static_configs:
      - targets: ['kgas-app:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
    honor_labels: true
    
  # Neo4j Database Metrics
  - job_name: 'neo4j'
    static_configs:
      - targets: ['neo4j:2004']
    metrics_path: '/metrics'
    scrape_interval: 60s
    
  # System Metrics (Node Exporter)
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 30s
    
  # Container Metrics (cAdvisor)
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
    scrape_interval: 30s
```

#### KGAS-Specific Metrics
```yaml
# Custom KGAS metrics configuration
kgas_metrics:
  application_metrics:
    - kgas_documents_processed_total
    - kgas_entities_extracted_total
    - kgas_relationships_extracted_total
    - kgas_graph_query_duration_seconds
    - kgas_api_request_duration_seconds
    - kgas_error_rate
    - kgas_active_workflows
    
  database_metrics:
    - kgas_neo4j_query_duration_seconds
    - kgas_neo4j_connection_pool_active
    - kgas_neo4j_transaction_duration_seconds
    - kgas_sqlite_query_duration_seconds
    
  business_metrics:
    - kgas_research_workflows_completed
    - kgas_cross_modal_conversions_total
    - kgas_theory_applications_total
    - kgas_quality_scores_distribution
```

### Grafana Configuration (`grafana-datasources.yml`)

#### Data Source Configuration
```yaml
# Grafana data sources
apiVersion: 1

datasources:
  # Prometheus for metrics
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    basicAuth: false
    editable: true
    jsonData:
      timeInterval: "30s"
      queryTimeout: "60s"
      httpMethod: "POST"
    
  # Neo4j for graph data
  - name: Neo4j
    type: neo4j-datasource
    access: proxy
    url: bolt://neo4j:7687
    basicAuth: true
    basicAuthUser: neo4j
    secureJsonData:
      basicAuthPassword: ${NEO4J_PASSWORD}
    jsonData:
      database: "neo4j"
      encrypted: false
      
  # Elasticsearch for logs (when available)
  - name: Elasticsearch
    type: elasticsearch
    access: proxy
    url: http://elasticsearch:9200
    database: "kgas-logs-*"
    jsonData:
      timeField: "@timestamp"
      esVersion: "8.0.0"
      logMessageField: "message"
      logLevelField: "level"
```

### Docker Monitoring Stack (`docker-compose.monitoring.yml`)

#### Complete Monitoring Deployment
```yaml
# Comprehensive monitoring stack
version: '3.8'

services:
  # Prometheus - Metrics Collection
  prometheus:
    image: prom/prometheus:v2.40.0
    container_name: kgas-prometheus
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
      - '--storage.tsdb.retention.time=30d'
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./alert_rules.yml:/etc/prometheus/alert_rules.yml:ro
      - prometheus_data:/prometheus
    networks:
      - monitoring
    
  # Grafana - Visualization
  grafana:
    image: grafana/grafana:9.3.0
    container_name: kgas-grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
      - GF_INSTALL_PLUGINS=neo4j-datasource
      - GF_FEATURE_TOGGLES_ENABLE=ngalert
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml:ro
      - ./grafana-dashboards:/etc/grafana/provisioning/dashboards:ro
    networks:
      - monitoring
    depends_on:
      - prometheus
      
  # AlertManager - Alert Management
  alertmanager:
    image: prom/alertmanager:v0.25.0
    container_name: kgas-alertmanager
    restart: unless-stopped
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
      - '--web.external-url=http://localhost:9093'
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
      - alertmanager_data:/alertmanager
    networks:
      - monitoring
      
  # Node Exporter - System Metrics
  node-exporter:
    image: prom/node-exporter:v1.5.0
    container_name: kgas-node-exporter
    restart: unless-stopped
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    networks:
      - monitoring
      
  # cAdvisor - Container Metrics
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.46.0
    container_name: kgas-cadvisor
    restart: unless-stopped
    privileged: true
    devices:
      - /dev/kmsg
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - monitoring

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:

networks:
  monitoring:
    driver: bridge
```

## Alert Configuration

### Alert Rules (`alert_rules.yml`)
```yaml
# Prometheus alerting rules
groups:
  - name: kgas_application_alerts
    rules:
      # High Error Rate
      - alert: KGASHighErrorRate
        expr: rate(kgas_error_rate[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
          component: application
        annotations:
          summary: "KGAS error rate is high"
          description: "Error rate is {{ $value }} errors per second"
          
      # Document Processing Failure
      - alert: KGASDocumentProcessingFailure
        expr: increase(kgas_documents_failed_total[10m]) > 5
        for: 1m
        labels:
          severity: critical
          component: processing
        annotations:
          summary: "Multiple document processing failures"
          description: "{{ $value }} documents failed to process in the last 10 minutes"
          
      # Database Connection Issues
      - alert: KGASNeo4jDown
        expr: up{job="neo4j"} == 0
        for: 30s
        labels:
          severity: critical
          component: database
        annotations:
          summary: "Neo4j database is down"
          description: "Neo4j database connection is not responding"
          
      # High Memory Usage
      - alert: KGASHighMemoryUsage
        expr: process_resident_memory_bytes{job="kgas-app"} / (1024^3) > 6
        for: 5m
        labels:
          severity: warning
          component: system
        annotations:
          summary: "KGAS memory usage is high"
          description: "Memory usage is {{ $value }}GB"
          
      # Slow Query Performance
      - alert: KGASSlowQueries
        expr: rate(kgas_graph_query_duration_seconds_sum[5m]) / rate(kgas_graph_query_duration_seconds_count[5m]) > 10
        for: 3m
        labels:
          severity: warning
          component: performance
        annotations:
          summary: "KGAS queries are running slowly"
          description: "Average query time is {{ $value }} seconds"

  - name: kgas_business_alerts
    rules:
      # Low Quality Extraction
      - alert: KGASLowQualityExtraction
        expr: rate(kgas_low_quality_entities_total[30m]) / rate(kgas_entities_extracted_total[30m]) > 0.3
        for: 5m
        labels:
          severity: warning
          component: quality
        annotations:
          summary: "High rate of low-quality entity extraction"
          description: "{{ $value | humanizePercentage }} of extracted entities are low quality"
          
      # Theory Application Failures
      - alert: KGASTheoryApplicationFailures
        expr: increase(kgas_theory_application_failures_total[1h]) > 10
        for: 2m
        labels:
          severity: warning
          component: theory
        annotations:
          summary: "Multiple theory application failures"
          description: "{{ $value }} theory applications failed in the last hour"
```

### AlertManager Configuration (`alertmanager.yml`)
```yaml
# Alert routing and notification configuration
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@kgas.example.com'

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  routes:
    # Critical alerts go to multiple channels
    - match:
        severity: critical
      receiver: 'critical-alerts'
      
    # Application alerts to development team
    - match:
        component: application
      receiver: 'dev-team'
      
    # Database alerts to infrastructure team
    - match:
        component: database
      receiver: 'infra-team'

receivers:
  - name: 'default'
    email_configs:
      - to: 'admin@kgas.example.com'
        subject: 'KGAS Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
          
  - name: 'critical-alerts'
    email_configs:
      - to: 'admin@kgas.example.com,oncall@kgas.example.com'
        subject: 'CRITICAL KGAS Alert: {{ .GroupLabels.alertname }}'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#kgas-alerts'
        title: 'Critical KGAS Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
        
  - name: 'dev-team'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#kgas-dev'
        title: 'KGAS Development Alert'
        
  - name: 'infra-team'
    email_configs:
      - to: 'infrastructure@kgas.example.com'
        subject: 'KGAS Infrastructure Alert'
```

## Grafana Dashboards

### System Overview Dashboard
```json
{
  "dashboard": {
    "title": "KGAS System Overview",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(kgas_api_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(kgas_error_rate[5m])",
            "legendFormat": "Errors/sec"
          }
        ]
      },
      {
        "title": "Document Processing",
        "type": "stat",
        "targets": [
          {
            "expr": "increase(kgas_documents_processed_total[1h])",
            "legendFormat": "Documents Processed (1h)"
          }
        ]
      },
      {
        "title": "Active Workflows",
        "type": "gauge",
        "targets": [
          {
            "expr": "kgas_active_workflows",
            "legendFormat": "Active Workflows"
          }
        ]
      }
    ]
  }
}
```

### Database Performance Dashboard
```json
{
  "dashboard": {
    "title": "KGAS Database Performance",
    "panels": [
      {
        "title": "Neo4j Query Duration",
        "type": "heatmap",
        "targets": [
          {
            "expr": "rate(kgas_neo4j_query_duration_seconds_bucket[5m])",
            "format": "heatmap"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "kgas_neo4j_connection_pool_active",
            "legendFormat": "Active Connections"
          },
          {
            "expr": "kgas_neo4j_connection_pool_idle",
            "legendFormat": "Idle Connections"
          }
        ]
      },
      {
        "title": "Graph Size",
        "type": "stat",
        "targets": [
          {
            "expr": "kgas_graph_nodes_total",
            "legendFormat": "Total Nodes"
          },
          {
            "expr": "kgas_graph_relationships_total",
            "legendFormat": "Total Relationships"
          }
        ]
      }
    ]
  }
}
```

### Research Analytics Dashboard
```json
{
  "dashboard": {
    "title": "KGAS Research Analytics",
    "panels": [
      {
        "title": "Entity Extraction Quality",
        "type": "pie",
        "targets": [
          {
            "expr": "kgas_entities_high_quality_total",
            "legendFormat": "High Quality"
          },
          {
            "expr": "kgas_entities_medium_quality_total",
            "legendFormat": "Medium Quality"
          },
          {
            "expr": "kgas_entities_low_quality_total",
            "legendFormat": "Low Quality"
          }
        ]
      },
      {
        "title": "Cross-Modal Conversions",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(kgas_cross_modal_conversions_total[1h])",
            "legendFormat": "Conversions/hour"
          }
        ]
      },
      {
        "title": "Theory Applications",
        "type": "table",
        "targets": [
          {
            "expr": "kgas_theory_applications_total by (theory_id)",
            "format": "table"
          }
        ]
      }
    ]
  }
}
```

## Monitoring Commands

### Start Monitoring Stack
```bash
# Start complete monitoring stack
cd config/monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Verify all services
docker-compose -f docker-compose.monitoring.yml ps

# Check logs
docker-compose -f docker-compose.monitoring.yml logs -f prometheus
docker-compose -f docker-compose.monitoring.yml logs -f grafana
```

### Access Monitoring Services
```bash
# Prometheus metrics and rules
curl http://localhost:9090/metrics
curl http://localhost:9090/api/v1/rules

# Grafana dashboards
open http://localhost:3000
# Default login: admin/admin (change in production)

# AlertManager status
curl http://localhost:9093/api/v1/status
curl http://localhost:9093/api/v1/alerts
```

### Configuration Management
```bash
# Reload Prometheus configuration
curl -X POST http://localhost:9090/-/reload

# Test alert rules
promtool check rules config/monitoring/alert_rules.yml

# Validate Prometheus config
promtool check config config/monitoring/prometheus.yml

# Test alert notifications
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[{"labels":{"alertname":"test"}}]'
```

## Troubleshooting

### Common Issues

#### **Prometheus Not Scraping Targets**
```bash
# Check target status
curl http://localhost:9090/api/v1/targets

# Check service discovery
curl http://localhost:9090/api/v1/targets/metadata

# Test connectivity to target
docker-compose exec prometheus wget -O- http://kgas-app:8000/metrics
```

#### **Grafana Dashboard Issues**
```bash
# Check Grafana logs
docker-compose logs grafana

# Test data source connectivity
curl -X GET http://admin:admin@localhost:3000/api/datasources/1/health

# Refresh dashboard
curl -X POST http://admin:admin@localhost:3000/api/admin/provisioning/dashboards/reload
```

#### **Alert Not Firing**
```bash
# Check alert rule evaluation
curl http://localhost:9090/api/v1/rules

# Check alertmanager configuration
curl http://localhost:9093/api/v1/status

# Test alert routing
amtool config routes test --config.file=alertmanager.yml
```

## Best Practices

### Monitoring Strategy
1. **Layered Monitoring**: System, application, and business metrics
2. **Proactive Alerting**: Alert on leading indicators, not just failures
3. **Alert Fatigue Prevention**: Tune alerts to minimize false positives
4. **Comprehensive Coverage**: Monitor all critical system components
5. **Performance Baseline**: Establish and monitor performance baselines

### Dashboard Design
1. **User-Focused**: Design dashboards for specific user needs
2. **Hierarchical**: Start with high-level overview, drill down to details
3. **Actionable**: Include information needed for troubleshooting
4. **Consistent**: Use consistent visualization and color schemes
5. **Automated**: Automate dashboard provisioning and updates

### Alert Management
1. **Severity Classification**: Clear severity levels with appropriate responses
2. **Escalation Procedures**: Define clear escalation paths
3. **Documentation**: Include runbooks for common alerts
4. **Testing**: Regularly test alert delivery and response procedures
5. **Continuous Improvement**: Regular review and tuning of alerts

The monitoring configuration provides comprehensive observability into KGAS performance, health, and business metrics, enabling proactive issue detection and resolution.