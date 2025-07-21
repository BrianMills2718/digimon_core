# Monitoring Module - CLAUDE.md

## Overview
The `src/monitoring/` directory contains **Grafana dashboard management** and monitoring infrastructure for the GraphRAG system. This module provides comprehensive monitoring dashboards for system performance, database metrics, API monitoring, and error tracking.

## Monitoring Architecture

### Dashboard Management Pattern
The monitoring module follows a structured dashboard management pattern:
- **GrafanaDashboardManager**: Main dashboard creation and management
- **Dashboard Templates**: Pre-defined dashboard configurations
- **Metric Integration**: Integration with Prometheus metrics
- **Real-time Monitoring**: Real-time system monitoring and alerting

### Dashboard Organization Pattern
All dashboards are organized by monitoring domain:
- **System Overview**: Overall system health and performance
- **Performance Monitoring**: Detailed performance metrics
- **Database Monitoring**: Graph database metrics and health
- **API Monitoring**: API performance and usage metrics
- **Entity Processing**: Entity extraction and processing metrics
- **Error Tracking**: Error rates and failure analysis

## Individual Component Patterns

### GrafanaDashboardManager (`grafana_dashboards.py`)
**Purpose**: Grafana dashboard creation and management for GraphRAG system

**Key Patterns**:
- **Dashboard Creation**: Create comprehensive monitoring dashboards
- **Metric Integration**: Integrate with Prometheus metrics
- **Real-time Updates**: Provide real-time monitoring updates
- **Alerting Integration**: Integrate with alerting systems

**Usage**:
```python
from src.monitoring.grafana_dashboards import GrafanaDashboardManager

# Initialize dashboard manager
manager = GrafanaDashboardManager(
    grafana_url="http://localhost:3000",
    api_key="your-grafana-api-key"
)

# Create system overview dashboard
overview_dashboard = manager.create_system_overview_dashboard()

# Create performance dashboard
performance_dashboard = manager.create_performance_dashboard()

# Provision all dashboards
results = manager.provision_all_dashboards()
print(f"Provisioned {len(results)} dashboards")
```

**Core Components**:

#### System Overview Dashboard
```python
def create_system_overview_dashboard(self) -> Dict[str, Any]:
    """Create system overview dashboard"""
```

**Overview Features**:
- **CPU Usage**: Monitor system CPU usage with thresholds
- **Memory Usage**: Monitor system memory usage with thresholds
- **Documents Processed**: Track document processing rates
- **Health Check Status**: Monitor service health status
- **System Load**: Monitor system load with gauge visualization

**Metrics**:
- `kgas_system_cpu_usage_percent`: System CPU usage percentage
- `kgas_system_memory_usage_percent`: System memory usage percentage
- `kgas_documents_processed_total`: Total documents processed
- `kgas_health_check_status`: Service health check status

#### Performance Dashboard
```python
def create_performance_dashboard(self) -> Dict[str, Any]:
    """Create performance monitoring dashboard"""
```

**Performance Features**:
- **Document Processing Time**: 95th percentile processing time
- **API Response Time**: API response time by provider
- **Throughput**: Documents processed per second
- **Error Rate**: Error rate monitoring

**Metrics**:
- `kgas_document_processing_duration_seconds`: Document processing duration
- `kgas_api_response_duration_seconds`: API response duration
- `kgas_documents_processed_total`: Document processing throughput
- `kgas_documents_processed_total{status="error"}`: Error rate

#### Database Dashboard
```python
def create_database_dashboard(self) -> Dict[str, Any]:
    """Create database monitoring dashboard"""
```

**Database Features**:
- **Graph Nodes**: Total number of graph nodes
- **Graph Edges**: Total number of graph edges
- **Database Connections**: Active database connections
- **Query Performance**: Database query performance metrics

**Metrics**:
- `kgas_graph_nodes_total`: Total graph nodes
- `kgas_graph_edges_total`: Total graph edges
- `kgas_database_connections_active`: Active database connections
- `kgas_database_query_duration_seconds`: Database query duration

#### API Monitoring Dashboard
```python
def create_api_monitoring_dashboard(self) -> Dict[str, Any]:
    """Create API monitoring dashboard"""
```

**API Features**:
- **API Response Times**: Response times by API endpoint
- **API Error Rates**: Error rates by API endpoint
- **API Usage**: API usage patterns and trends
- **Rate Limiting**: Rate limiting and throttling metrics

**Metrics**:
- `kgas_api_response_duration_seconds`: API response duration
- `kgas_api_requests_total`: Total API requests
- `kgas_api_errors_total`: Total API errors
- `kgas_api_rate_limit_hits_total`: Rate limit hits

#### Entity Processing Dashboard
```python
def create_entity_processing_dashboard(self) -> Dict[str, Any]:
    """Create entity processing monitoring dashboard"""
```

**Entity Features**:
- **Entity Extraction Rate**: Entities extracted per document
- **Entity Processing Time**: Entity processing duration
- **Entity Quality Metrics**: Entity quality and confidence scores
- **Entity Type Distribution**: Distribution of entity types

**Metrics**:
- `kgas_entities_extracted_total`: Total entities extracted
- `kgas_entity_processing_duration_seconds`: Entity processing duration
- `kgas_entity_confidence_score`: Entity confidence scores
- `kgas_entity_types_total`: Entity type distribution

#### Error Tracking Dashboard
```python
def create_error_tracking_dashboard(self) -> Dict[str, Any]:
    """Create error tracking dashboard"""
```

**Error Features**:
- **Error Rates**: Error rates by component and type
- **Error Trends**: Error trend analysis over time
- **Error Distribution**: Distribution of error types
- **Recovery Metrics**: Error recovery and resolution metrics

**Metrics**:
- `kgas_errors_total`: Total errors by type
- `kgas_error_recovery_time_seconds`: Error recovery time
- `kgas_errors_by_component_total`: Errors by component
- `kgas_error_resolution_rate`: Error resolution rate

#### Dashboard Provisioning
```python
def provision_all_dashboards(self) -> Dict[str, Any]:
    """Provision all monitoring dashboards"""
```

**Provisioning Features**:
- **Batch Creation**: Create all dashboards in batch
- **Status Tracking**: Track provisioning status for each dashboard
- **Error Handling**: Handle provisioning errors gracefully
- **Result Reporting**: Report provisioning results

## Dashboard Templates

### System Overview Dashboard (`system_overview_dashboard.json`)
**Purpose**: Overall system health and performance monitoring

**Key Panels**:
- **System CPU Usage**: CPU usage with color-coded thresholds
- **System Memory Usage**: Memory usage with color-coded thresholds
- **Documents Processed**: Document processing rate over time
- **Health Check Status**: Service health status indicators
- **System Load**: System load gauge visualization

### Performance Dashboard (`document_processing_dashboard.json`)
**Purpose**: Detailed performance monitoring and analysis

**Key Panels**:
- **Document Processing Time**: Processing time percentiles
- **API Response Time**: API response time by provider
- **Throughput**: Documents processed per second
- **Error Rate**: Error rate monitoring and trends

### Database Dashboard (`database_monitoring_dashboard.json`)
**Purpose**: Graph database monitoring and health

**Key Panels**:
- **Graph Nodes**: Total number of graph nodes
- **Graph Edges**: Total number of graph edges
- **Database Connections**: Active connection monitoring
- **Query Performance**: Query duration and performance

### API Dashboard (`api_performance_dashboard.json`)
**Purpose**: API performance and usage monitoring

**Key Panels**:
- **API Response Times**: Response time by endpoint
- **API Error Rates**: Error rates by endpoint
- **API Usage**: Usage patterns and trends
- **Rate Limiting**: Rate limiting metrics

### Error Dashboard (`error_tracking_dashboard.json`)
**Purpose**: Error tracking and analysis

**Key Panels**:
- **Error Rates**: Error rates by component
- **Error Trends**: Error trends over time
- **Error Distribution**: Error type distribution
- **Recovery Metrics**: Error recovery metrics

### Workflow Dashboard (`workflow_execution_dashboard.json`)
**Purpose**: Workflow execution monitoring

**Key Panels**:
- **Workflow Execution Time**: Workflow duration metrics
- **Workflow Success Rate**: Success rate by workflow type
- **Workflow Queue**: Workflow queue monitoring
- **Resource Usage**: Resource usage by workflow

## Common Commands & Workflows

### Development Commands
```bash
# Test dashboard manager
python -c "from src.monitoring.grafana_dashboards import GrafanaDashboardManager; manager = GrafanaDashboardManager(); print('Dashboard manager created successfully')"

# Test dashboard creation
python -c "from src.monitoring.grafana_dashboards import GrafanaDashboardManager; manager = GrafanaDashboardManager(); dashboard = manager.create_system_overview_dashboard(); print(f'Dashboard: {dashboard[\"dashboard\"][\"title\"]}')"

# Test performance dashboard
python -c "from src.monitoring.grafana_dashboards import GrafanaDashboardManager; manager = GrafanaDashboardManager(); dashboard = manager.create_performance_dashboard(); print(f'Performance dashboard: {dashboard[\"dashboard\"][\"title\"]}')"

# Test database dashboard
python -c "from src.monitoring.grafana_dashboards import GrafanaDashboardManager; manager = GrafanaDashboardManager(); dashboard = manager.create_database_dashboard(); print(f'Database dashboard: {dashboard[\"dashboard\"][\"title\"]}')"
```

### Testing Commands
```bash
# Test API monitoring dashboard
python -c "from src.monitoring.grafana_dashboards import GrafanaDashboardManager; manager = GrafanaDashboardManager(); dashboard = manager.create_api_monitoring_dashboard(); print(f'API dashboard: {dashboard[\"dashboard\"][\"title\"]}')"

# Test entity processing dashboard
python -c "from src.monitoring.grafana_dashboards import GrafanaDashboardManager; manager = GrafanaDashboardManager(); dashboard = manager.create_entity_processing_dashboard(); print(f'Entity dashboard: {dashboard[\"dashboard\"][\"title\"]}')"

# Test error tracking dashboard
python -c "from src.monitoring.grafana_dashboards import GrafanaDashboardManager; manager = GrafanaDashboardManager(); dashboard = manager.create_error_tracking_dashboard(); print(f'Error dashboard: {dashboard[\"dashboard\"][\"title\"]}')"

# Test dashboard provisioning
python -c "from src.monitoring.grafana_dashboards import GrafanaDashboardManager; manager = GrafanaDashboardManager(); print(manager.provision_all_dashboards.__doc__)"
```

### Debugging Commands
```bash
# Check Grafana configuration
python -c "from src.monitoring.grafana_dashboards import GrafanaDashboardManager; manager = GrafanaDashboardManager(); print(f'Grafana URL: {manager.grafana_url}')"

# Check dashboard templates
python -c "import json; from pathlib import Path; dashboard_file = Path('src/monitoring/dashboards/system_overview_dashboard.json'); print(json.load(open(dashboard_file))['dashboard']['title'])"

# Test dashboard structure
python -c "from src.monitoring.grafana_dashboards import GrafanaDashboardManager; manager = GrafanaDashboardManager(); dashboard = manager.create_system_overview_dashboard(); print(f'Panels: {len(dashboard[\"dashboard\"][\"panels\"])}')"

# Check metric expressions
python -c "from src.monitoring.grafana_dashboards import GrafanaDashboardManager; manager = GrafanaDashboardManager(); dashboard = manager.create_system_overview_dashboard(); panel = dashboard['dashboard']['panels'][0]; print(f'Metric: {panel[\"targets\"][0][\"expr\"]}')"
```

## Code Style & Conventions

### Dashboard Design Patterns
- **Comprehensive Coverage**: Monitor all system components
- **Real-time Updates**: Provide real-time monitoring updates
- **Threshold Alerts**: Use color-coded thresholds for alerts
- **Metric Integration**: Integrate with Prometheus metrics

### Naming Conventions
- **Manager Classes**: Use `Manager` suffix for management classes
- **Dashboard Names**: Use descriptive dashboard names
- **Metric Names**: Use consistent metric naming conventions
- **Panel Names**: Use descriptive panel names

### Error Handling Patterns
- **Graceful Failures**: Handle dashboard creation failures gracefully
- **Error Reporting**: Report detailed error information
- **Fallback Mechanisms**: Provide fallback dashboard configurations
- **Status Tracking**: Track dashboard provisioning status

### Logging Patterns
- **Dashboard Logging**: Log dashboard creation and updates
- **Error Logging**: Log dashboard creation errors
- **Performance Logging**: Log dashboard performance metrics
- **Provisioning Logging**: Log dashboard provisioning status

## Integration Points

### Grafana Integration
- **Dashboard API**: Integration with Grafana dashboard API
- **Metric Queries**: Integration with Prometheus metric queries
- **Alerting**: Integration with Grafana alerting
- **Authentication**: Integration with Grafana authentication

### Prometheus Integration
- **Metric Collection**: Integration with Prometheus metric collection
- **Query Language**: Integration with PromQL query language
- **Time Series**: Integration with time series data
- **Alerting Rules**: Integration with Prometheus alerting rules

### Core Integration
- **Configuration**: Integration with configuration system
- **Logging**: Integration with logging system
- **Metrics**: Integration with metrics collection
- **Health Checks**: Integration with health check system

### External Dependencies
- **Requests**: HTTP requests for Grafana API
- **JSON**: JSON serialization and deserialization
- **Datetime**: Time tracking and formatting
- **Pathlib**: File path handling

## Performance Considerations

### Dashboard Performance
- **Panel Optimization**: Optimize dashboard panels for performance
- **Query Optimization**: Optimize Prometheus queries
- **Refresh Rates**: Set appropriate refresh rates
- **Caching**: Use Grafana caching for performance

### Metric Performance
- **Metric Collection**: Optimize metric collection frequency
- **Query Performance**: Optimize Prometheus query performance
- **Storage Optimization**: Optimize metric storage
- **Retention Policies**: Set appropriate retention policies

### Resource Management
- **Memory Usage**: Monitor dashboard memory usage
- **CPU Usage**: Monitor dashboard CPU usage
- **Network Usage**: Monitor dashboard network usage
- **Storage Usage**: Monitor dashboard storage usage

## Monitoring Patterns

### System Monitoring
- **Health Checks**: Monitor system health status
- **Resource Usage**: Monitor system resource usage
- **Performance Metrics**: Monitor system performance
- **Availability**: Monitor system availability

### Application Monitoring
- **API Performance**: Monitor API performance metrics
- **Error Rates**: Monitor application error rates
- **Throughput**: Monitor application throughput
- **Response Times**: Monitor response times

### Database Monitoring
- **Connection Pool**: Monitor database connection pool
- **Query Performance**: Monitor query performance
- **Storage Usage**: Monitor database storage usage
- **Replication**: Monitor database replication

### Business Metrics
- **Document Processing**: Monitor document processing metrics
- **Entity Extraction**: Monitor entity extraction metrics
- **User Activity**: Monitor user activity metrics
- **Quality Metrics**: Monitor quality metrics

## Troubleshooting

### Common Issues
1. **Grafana Connection Issues**: Check Grafana URL and API key
2. **Metric Collection Issues**: Check Prometheus metric collection
3. **Dashboard Creation Issues**: Check dashboard configuration
4. **Performance Issues**: Check dashboard and query performance

### Debug Commands
```bash
# Check Grafana connectivity
python -c "import requests; response = requests.get('http://localhost:3000/api/health'); print(f'Grafana health: {response.status_code}')"

# Check Prometheus metrics
python -c "import requests; response = requests.get('http://localhost:9090/api/v1/query?query=up'); print(f'Prometheus query: {response.status_code}')"

# Test dashboard creation
python -c "from src.monitoring.grafana_dashboards import GrafanaDashboardManager; manager = GrafanaDashboardManager(); print('Dashboard manager test successful')"

# Check configuration
python -c "from src.core.unified_config import get_config; config = get_config(); print(f'Grafana API key: {config.get(\"grafana.api_key\", \"Not set\")[:10]}...' if config.get(\"grafana.api_key\") else 'Not set')"
```

## Migration & Upgrades

### Dashboard Migration
- **Dashboard Updates**: Update dashboard configurations
- **Metric Migration**: Migrate metrics to new naming conventions
- **Panel Migration**: Migrate dashboard panels
- **Template Migration**: Migrate dashboard templates

### Grafana Migration
- **Version Updates**: Update Grafana version compatibility
- **API Changes**: Handle Grafana API changes
- **Configuration Updates**: Update Grafana configuration
- **Plugin Updates**: Update Grafana plugins

### Metric Migration
- **Metric Names**: Migrate metric names and labels
- **Query Language**: Update PromQL queries
- **Alerting Rules**: Migrate alerting rules
- **Retention Policies**: Update retention policies

### Configuration Updates
- **Dashboard Configuration**: Update dashboard configuration
- **Metric Configuration**: Update metric configuration
- **Alerting Configuration**: Update alerting configuration
- **Performance Configuration**: Update performance settings 