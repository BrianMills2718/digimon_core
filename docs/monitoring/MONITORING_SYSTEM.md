# KGAS Integration Monitoring System

## Overview

The KGAS Integration Monitoring System provides comprehensive real-time validation, health checking, performance monitoring, and alerting for the entire KGAS infrastructure and tools ecosystem.

## Features

### 🔍 **Comprehensive Health Monitoring**
- **Infrastructure Integration**: Monitor all infrastructure components (database optimizer, memory manager, LLM cache, etc.)
- **Core Services**: Track health of identity, provenance, quality, and workflow services
- **Tool Registry**: Monitor tool implementation status and health
- **Workflow Execution**: Validate end-to-end workflow functionality
- **System Performance**: Track CPU, memory, disk usage and application-specific metrics

### 🚨 **Intelligent Alerting**
- **Configurable Alert Rules**: Define custom alert conditions using Python expressions
- **Severity Levels**: Info, Warning, Error, and Critical alert classifications
- **Cooldown Periods**: Prevent alert spam with configurable cooldown periods
- **Multiple Notification Channels**: Webhook, email, and Slack integration support

### 📊 **Real-time Dashboard**
- **Web-based Interface**: Modern, responsive dashboard accessible via browser
- **Live Status Updates**: Real-time component status indicators
- **Performance Metrics**: Visual displays of system and infrastructure metrics
- **Alert History**: View and filter recent alerts
- **Data Export**: Export monitoring data for analysis

### 📈 **Performance Analytics**
- **Response Time Tracking**: Monitor API and tool execution times
- **Resource Usage Analysis**: Track memory, CPU, and disk utilization patterns
- **Cache Performance**: Monitor cache hit rates and effectiveness
- **Error Rate Monitoring**: Track error rates across all components

## Architecture

### Core Components

```
Integration Validator
├── Health Check Engine
│   ├── Infrastructure Checker
│   ├── Services Checker
│   ├── Tools Checker
│   ├── Workflows Checker
│   └── Performance Checker
├── Alert Engine
│   ├── Rule Evaluator
│   ├── Alert Generator
│   ├── Notification Manager
│   └── Cooldown Controller
├── Metrics Collector
│   ├── System Metrics
│   ├── Infrastructure Metrics
│   ├── Performance Metrics
│   └── Error Metrics
└── Data Manager
    ├── History Storage
    ├── Export Manager
    └── Cleanup Controller
```

### Integration Points

- **Infrastructure Integration**: Monitors all infrastructure components via `InfrastructureIntegrator`
- **Service Manager**: Health checks for all core services
- **Tool Registry**: Implementation status and health monitoring
- **Workflow Tester**: End-to-end workflow validation
- **Performance Benchmarker**: Performance metrics collection

## Installation and Setup

### Prerequisites

```bash
# Core dependencies
pip install asyncio aiofiles psutil

# Dashboard dependencies (optional)
pip install aiohttp aiohttp-cors

# Testing dependencies (optional)
pip install pytest pytest-asyncio
```

### Configuration

Create a monitoring configuration file:

```bash
cp config/monitoring/integration_monitoring.json config/monitoring/my_monitoring.json
# Edit configuration as needed
```

Key configuration sections:

#### Health Check Configuration
```json
{
  "health_checks": {
    "infrastructure": {
      "enabled": true,
      "interval_seconds": 30,
      "timeout_seconds": 30,
      "retry_count": 3,
      "failure_threshold": 3,
      "recovery_threshold": 2
    }
  }
}
```

#### Performance Thresholds
```json
{
  "performance": {
    "cpu_threshold": 80.0,
    "memory_threshold": 85.0,
    "response_time_threshold": 5.0,
    "error_rate_threshold": 0.05
  }
}
```

#### Alert Rules
```json
{
  "alert_rules": [
    {
      "name": "high_memory_usage",
      "condition": "memory_percent > 85",
      "severity": "warning",
      "message_template": "High memory usage: {memory_percent:.1f}%",
      "cooldown_minutes": 5,
      "enabled": true
    }
  ]
}
```

## Usage

### Starting the Monitoring Service

#### Command Line Interface
```bash
# Start monitoring service
python scripts/monitoring/start_integration_monitoring.py --config config/monitoring/my_monitoring.json

# Start in development mode
python scripts/monitoring/start_integration_monitoring.py --mode development

# Get status
python scripts/monitoring/start_integration_monitoring.py --command status

# Export monitoring data
python scripts/monitoring/start_integration_monitoring.py --command export --output monitoring_report.json
```

#### Programmatic Usage
```python
from src.monitoring.integration_validator import create_production_validator

async def start_monitoring():
    # Create validator
    validator = create_production_validator("config/monitoring/my_monitoring.json")
    
    # Initialize components
    await validator.initialize_components()
    
    # Start monitoring
    await validator.start_monitoring()
    
    # Get health status
    health = await validator.get_health_status()
    print(f"Overall status: {health['overall_status']}")
    
    # Export data
    await validator.export_monitoring_data("report.json")
    
    # Cleanup
    await validator.cleanup()
```

### Web Dashboard

Start the web dashboard for real-time monitoring:

```bash
# Start dashboard on default port 8080
python scripts/monitoring/monitoring_dashboard.py

# Start on custom port
python scripts/monitoring/monitoring_dashboard.py --port 9000

# With custom config
python scripts/monitoring/monitoring_dashboard.py --config config/monitoring/my_monitoring.json
```

Access the dashboard at `http://localhost:8080`

### Dashboard Features

#### Status Overview
- **Component Health**: Real-time status of all monitored components
- **Status Indicators**: Color-coded status indicators (Green=Healthy, Yellow=Warning, Red=Critical)
- **Last Check Time**: Timestamp of last health check for each component

#### Performance Metrics
- **CPU Usage**: Current CPU utilization with visual progress bar
- **Memory Usage**: RAM utilization with threshold indicators
- **Disk Usage**: Storage utilization monitoring
- **Cache Performance**: Cache hit rates and effectiveness metrics
- **Response Times**: Average response times for operations

#### Alert Management
- **Recent Alerts**: List of alerts from configurable time period
- **Alert Details**: Full alert information including severity, component, and timestamp
- **Alert Filtering**: Filter alerts by severity, component, or time range

#### Data Export
- **JSON Export**: Export complete monitoring data in JSON format
- **Automated Reports**: Scheduled daily and weekly reports
- **Historical Data**: Access to historical performance and health data

## Health Check Types

### Infrastructure Health Checks
- **Component Availability**: Verify all infrastructure components are initialized and operational
- **Performance Metrics**: Check cache hit rates, operation counts, and speedup metrics
- **Resource Usage**: Monitor memory and CPU usage of infrastructure components

### Service Health Checks
- **Service Availability**: Verify all core services (identity, provenance, quality, workflow) are responsive
- **API Functionality**: Test basic service operations
- **Database Connectivity**: Verify database connections for services that require them

### Tool Health Checks
- **Implementation Status**: Track tool implementation progress across all 121 tools
- **Tool Availability**: Verify implemented tools are functional
- **Contract Compliance**: Validate tools implement required interfaces

### Workflow Health Checks
- **Basic Workflow**: Execute simple document processing workflow
- **Enhanced Workflow**: Test infrastructure-enhanced workflow execution
- **Parallel Workflow**: Validate parallel processing capabilities
- **Performance Workflow**: Measure workflow execution performance

### Performance Health Checks
- **System Resources**: Monitor CPU, memory, and disk usage
- **Response Times**: Track operation response times
- **Error Rates**: Monitor error frequencies across components
- **Throughput**: Measure system throughput and capacity

## Alert System

### Alert Rules

Alert rules are defined using Python expressions evaluated against current metrics:

```json
{
  "name": "high_cpu_usage",
  "condition": "cpu_percent > 80",
  "severity": "warning",
  "message_template": "High CPU usage detected: {cpu_percent:.1f}%",
  "cooldown_minutes": 5,
  "enabled": true
}
```

#### Available Metrics
- `cpu_percent`: Current CPU usage percentage
- `memory_percent`: Current memory usage percentage
- `memory_available_gb`: Available memory in GB
- `failed_services`: Number of failed services
- `cache_hit_rate`: Infrastructure cache hit rate (0.0-1.0)
- `error_rate`: Recent error rate (0.0-1.0)
- `avg_response_time`: Average response time in seconds
- `infrastructure_status`: Infrastructure status ('HEALTHY' or 'CRITICAL')

### Alert Severities

1. **INFO**: Informational messages, no action required
2. **WARNING**: Potential issues that should be monitored
3. **ERROR**: Issues that need attention but don't affect core functionality
4. **CRITICAL**: Severe issues that require immediate attention

### Notification Channels

#### Webhook Notifications
```json
{
  "notification": {
    "webhook": {
      "enabled": true,
      "url": "https://your-webhook-url.com/alerts",
      "timeout_seconds": 10,
      "retry_count": 3
    }
  }
}
```

#### Email Notifications
```json
{
  "notification": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your-email@gmail.com",
      "password": "your-app-password",
      "from_address": "monitoring@kgas.com",
      "to_addresses": ["admin@kgas.com", "team@kgas.com"]
    }
  }
}
```

#### Slack Notifications
```json
{
  "notification": {
    "slack": {
      "enabled": true,
      "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
      "channel": "#alerts"
    }
  }
}
```

## Performance Monitoring

### Metrics Collection

The monitoring system automatically collects:

#### System Metrics
- CPU utilization (per core and overall)
- Memory usage (used, available, swap)
- Disk usage (used space, I/O rates)
- Network statistics (if applicable)

#### Infrastructure Metrics
- Cache hit rates and miss rates
- Operation counts and frequencies
- Performance speedup measurements
- Resource utilization by component

#### Application Metrics
- Tool execution times
- Workflow completion rates
- Service response times
- Error frequencies and types

### Performance Thresholds

Configure thresholds to trigger alerts when performance degrades:

```json
{
  "performance": {
    "cpu_threshold": 80.0,        // CPU usage %
    "memory_threshold": 85.0,     // Memory usage %
    "disk_threshold": 90.0,       // Disk usage %
    "response_time_threshold": 5.0,    // Seconds
    "error_rate_threshold": 0.05,      // 5% error rate
    "cache_hit_rate_threshold": 0.30   // 30% cache hit rate
  }
}
```

## Data Management

### Historical Data

The monitoring system maintains historical data for:
- Health check results
- Performance metrics
- Alert history
- System events

### Data Retention

Configure data retention policies:

```json
{
  "monitoring": {
    "history_retention_days": 7,
    "max_history_entries": 10000,
    "cleanup_interval_hours": 24
  }
}
```

### Data Export

Export monitoring data in various formats:

#### JSON Export
```python
await validator.export_monitoring_data("monitoring_report.json")
```

#### Automated Reports
- **Daily Reports**: Summary of previous day's performance and alerts
- **Weekly Reports**: Comprehensive weekly analysis
- **Custom Reports**: On-demand detailed analysis

### Database Integration

For production environments, integrate with time-series databases:

#### InfluxDB Integration
```python
# Example InfluxDB integration
from influxdb_client import InfluxDBClient

client = InfluxDBClient(url="http://localhost:8086", token="your-token")
# Write metrics to InfluxDB
```

#### Prometheus Integration
```python
# Example Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

health_check_counter = Counter('health_checks_total', 'Total health checks')
response_time_histogram = Histogram('response_time_seconds', 'Response times')
```

## Testing

### Running Tests

```bash
# Run all monitoring tests
python -m pytest tests/monitoring/ -v

# Run specific test
python -m pytest tests/monitoring/test_integration_validator.py::TestIntegrationValidator::test_monitoring_lifecycle -v

# Run with coverage
python -m pytest tests/monitoring/ --cov=src/monitoring --cov-report=html
```

### Test Coverage

The test suite covers:
- Validator initialization and configuration
- Health check functionality for all component types
- Alert rule evaluation and generation
- Data export and cleanup
- Dashboard API endpoints
- Error handling and edge cases

### Integration Testing

```python
# Full integration test
async def test_full_monitoring_cycle():
    validator = create_production_validator()
    await validator.initialize_components()
    await validator.start_monitoring()
    
    # Wait for health checks
    await asyncio.sleep(30)
    
    # Verify results
    health = await validator.get_health_status()
    assert health['overall_status'] in ['healthy', 'warning', 'critical']
    
    await validator.cleanup()
```

## Troubleshooting

### Common Issues

#### Monitor Not Starting
```bash
# Check configuration
python -c "import json; print(json.load(open('config/monitoring/integration_monitoring.json')))"

# Check dependencies
python -c "import psutil, asyncio; print('Dependencies OK')"

# Check log files
tail -f logs/integration_monitoring.log
```

#### High Resource Usage
```bash
# Reduce monitoring frequency
# Edit config: increase interval_seconds for health checks

# Disable expensive checks
# Set enabled: false for workflow health checks in development
```

#### Missing Alerts
```bash
# Check alert rule conditions
# Verify metrics are being collected
# Check cooldown periods aren't blocking alerts
```

### Debug Mode

Enable debug logging for troubleshooting:

```json
{
  "monitoring": {
    "log_level": "DEBUG",
    "enable_detailed_logging": true
  }
}
```

### Health Check Failures

Common causes and solutions:

1. **Infrastructure Component Failure**
   - Check if infrastructure integrator is properly initialized
   - Verify Neo4j database connectivity
   - Check memory manager configuration

2. **Service Health Check Failure**
   - Verify service manager initialization
   - Check individual service health
   - Review service dependencies

3. **Performance Health Check Failure**
   - Check system resource availability
   - Review performance thresholds
   - Monitor for resource-intensive processes

## Best Practices

### Production Deployment

1. **Configuration Management**
   - Use environment-specific configuration files
   - Store sensitive credentials in environment variables
   - Version control configuration templates

2. **Resource Planning**
   - Monitor monitoring system resource usage
   - Scale monitoring infrastructure with system growth
   - Implement monitoring data archival strategy

3. **Alert Management**
   - Define clear escalation procedures
   - Implement alert routing based on severity
   - Regular review and tuning of alert rules

4. **Performance Optimization**
   - Tune health check intervals based on system requirements
   - Optimize database queries for historical data
   - Implement caching for dashboard queries

### Development Environment

1. **Reduced Monitoring**
   - Use development validator with reduced checks
   - Disable expensive workflow health checks
   - Increase monitoring intervals

2. **Testing Integration**
   - Include monitoring health in CI/CD pipelines
   - Test alert rules with synthetic data
   - Validate dashboard functionality

## API Reference

### IntegrationValidator Class

#### Methods

##### `initialize_components() -> bool`
Initialize all monitoring components.

##### `start_monitoring() -> bool`
Start continuous monitoring loop.

##### `stop_monitoring()`
Stop monitoring and cleanup tasks.

##### `get_health_status() -> Dict[str, Any]`
Get current health status for all components.

##### `get_recent_alerts(hours: int = 24) -> List[Dict[str, Any]]`
Get alerts from specified time period.

##### `export_monitoring_data(output_path: str) -> bool`
Export monitoring data to file.

### Factory Functions

##### `create_production_validator(config_path: Optional[str] = None) -> IntegrationValidator`
Create validator optimized for production monitoring.

##### `create_development_validator(config_path: Optional[str] = None) -> IntegrationValidator`
Create validator optimized for development environment.

### Configuration Schema

See `config/monitoring/integration_monitoring.json` for complete configuration schema and examples.

## Roadmap

### Future Enhancements

1. **Advanced Analytics**
   - Machine learning-based anomaly detection
   - Predictive performance analysis
   - Automated root cause analysis

2. **Enhanced Visualization**
   - Time-series performance charts
   - Component dependency graphs
   - Interactive alert correlation

3. **Integration Expansion**
   - Kubernetes monitoring integration
   - Cloud provider metrics integration
   - External monitoring system connectors

4. **Automation Features**
   - Automated performance optimization
   - Self-healing capabilities
   - Dynamic threshold adjustment

## Support and Contributing

### Reporting Issues
- Create issues in the project repository
- Include monitoring logs and configuration
- Provide steps to reproduce problems

### Contributing
- Follow project coding standards
- Add tests for new monitoring features
- Update documentation for configuration changes

### Contact
- Project maintainers: [Contact Information]
- Documentation: [Documentation Links]
- Community: [Community Channels]