# Health Monitoring System

## Overview

The Health Monitoring System provides comprehensive real-time health checks, metrics collection, and alerting for all KGAS services. It addresses the critical need for operational visibility identified in the Phase RELIABILITY audit.

## Key Components

### 1. System Health Monitor

The main monitoring class that orchestrates all health checks:

```python
from src.core.health_monitor import SystemHealthMonitor, get_global_health_monitor

monitor = get_global_health_monitor()
await monitor.start_monitoring()
```

### 2. Health Check Results

Standardized health check format:

```python
@dataclass
class HealthCheckResult:
    service_name: str
    status: HealthStatus  # HEALTHY, DEGRADED, UNHEALTHY, CRITICAL, UNKNOWN
    message: str
    timestamp: datetime
    response_time: float
    metadata: Dict[str, Any]
    dependencies: List[str]
```

### 3. Metrics Collection

System and application metrics tracking:

```python
collector = MetricsCollector()
collector.record_metric("app.requests", 100, MetricType.COUNTER)
collector.record_metric("app.latency", 250, MetricType.GAUGE, unit="ms")
```

### 4. Alert Management

Threshold-based alerting system:

```python
alert_manager = AlertManager()
alert_manager.set_threshold("system.cpu.usage", "warning", 80.0)
alert_manager.set_threshold("system.cpu.usage", "critical", 95.0)
```

## Health Check Implementation

### Using the Decorator

The easiest way to add health checks:

```python
from src.core.health_monitor import health_check_endpoint

@health_check_endpoint("my_service")
async def my_service_health():
    # Check service health
    is_healthy = await check_database_connection()
    
    return HealthCheckResult(
        service_name="my_service",
        status=HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY,
        message="Service operational" if is_healthy else "Database connection failed",
        timestamp=datetime.now(),
        response_time=0.05,
        metadata={
            "version": "1.0.0",
            "connections": get_active_connections()
        }
    )
```

### Manual Registration

For more control:

```python
async def custom_health_check():
    # Custom health check logic
    return HealthCheckResult(...)

monitor.register_health_check("custom_service", custom_health_check)
```

## Built-in Health Checks

The system includes automatic checks for:

1. **CPU Usage**
   - Healthy: < 80%
   - Degraded: 80-90%
   - Critical: > 90%

2. **Memory Usage**
   - Healthy: < 80%
   - Degraded: 80-90%
   - Critical: > 90%

3. **Disk Usage**
   - Healthy: < 80%
   - Degraded: 80-90%
   - Critical: > 90%

4. **System Resources**
   - Combined check of CPU, memory, and disk
   - Overall system health assessment

## Metrics Collection

### Recording Metrics

```python
# Counter - cumulative values
collector.record_metric("requests.total", 1000, MetricType.COUNTER)

# Gauge - point-in-time values
collector.record_metric("connections.active", 25, MetricType.GAUGE)

# Histogram - distribution of values
collector.record_metric("response.time", 150, MetricType.HISTOGRAM, unit="ms")

# Timer - duration measurements
collector.record_metric("operation.duration", 2.5, MetricType.TIMER, unit="s")
```

### Accessing Metrics

```python
# Current values
current = collector.get_current_metrics()

# Historical data
history = collector.get_metric_history("requests.total", minutes=60)
```

## Alert Configuration

### Setting Thresholds

```python
# Warning at 80%, critical at 95%
alert_manager.set_threshold("system.memory.percent", "warning", 80.0)
alert_manager.set_threshold("system.memory.percent", "critical", 95.0)

# Custom application thresholds
alert_manager.set_threshold("app.error_rate", "warning", 0.05)
alert_manager.set_threshold("app.error_rate", "critical", 0.10)
```

### Handling Alerts

```python
async def handle_alert(alert: Alert):
    if alert.severity == "critical":
        # Page on-call engineer
        await send_page(alert)
    elif alert.severity == "warning":
        # Send to monitoring channel
        await send_slack_notification(alert)
    
    # Log all alerts
    logger.warning(f"[{alert.severity}] {alert.title}: {alert.message}")

alert_manager.register_alert_handler(handle_alert)
```

## System Health API

### Get Overall Health

```python
health = await monitor.check_system_health()

# Returns:
{
    "overall_status": "healthy",  # or degraded, unhealthy, critical
    "services": {
        "api": {
            "status": "healthy",
            "message": "API operational",
            "response_time": 0.05,
            "timestamp": "2025-01-23T10:00:00"
        },
        # ... other services
    },
    "metrics": {
        "system.cpu.usage": {"value": 45.2, "unit": "%"},
        "system.memory.percent": {"value": 72.1, "unit": "%"}
    },
    "active_alerts": [
        {
            "severity": "warning",
            "title": "High memory usage",
            "message": "Memory usage at 85%"
        }
    ]
}
```

### Health Endpoints

For HTTP services:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    monitor = get_global_health_monitor()
    health_status = await monitor.check_system_health()
    
    # Return appropriate HTTP status
    if health_status["overall_status"] == "unhealthy":
        status_code = 503  # Service Unavailable
    elif health_status["overall_status"] == "degraded":
        status_code = 200  # OK but degraded
    else:
        status_code = 200  # OK
    
    return health_status, status_code
```

## Background Monitoring

### Starting Continuous Monitoring

```python
monitor = get_global_health_monitor()

# Configure check interval (default: 60 seconds)
monitor.health_check_interval = 30

# Start background monitoring
await monitor.start_monitoring()

# ... application runs ...

# Stop when shutting down
await monitor.stop_monitoring()
```

### Integration with Application Lifecycle

```python
async def startup():
    """Application startup tasks."""
    monitor = get_global_health_monitor()
    
    # Register service health checks
    monitor.register_health_check("database", check_database_health)
    monitor.register_health_check("cache", check_cache_health)
    monitor.register_health_check("api", check_api_health)
    
    # Start monitoring
    await monitor.start_monitoring()

async def shutdown():
    """Application shutdown tasks."""
    monitor = get_global_health_monitor()
    await monitor.stop_monitoring()
```

## Dashboard Integration

The health monitoring system provides data suitable for dashboards:

```python
# Prometheus-style metrics export
@app.get("/metrics")
async def metrics():
    monitor = get_global_health_monitor()
    metrics = monitor.metrics_collector.get_current_metrics()
    
    # Format as Prometheus metrics
    output = []
    for name, metric in metrics.items():
        output.append(f"# TYPE {name} {metric.metric_type.value}")
        output.append(f"{name} {metric.value}")
    
    return "\n".join(output)
```

## Best Practices

### 1. Health Check Implementation

- Keep health checks fast (< 5 seconds)
- Include meaningful metadata
- Check actual functionality, not just connectivity
- Include dependency checks

### 2. Metric Naming

Follow consistent naming conventions:
- `service.component.metric`
- Use lowercase with dots
- Include units in metric name or metadata

### 3. Alert Thresholds

- Start with conservative thresholds
- Adjust based on actual patterns
- Different thresholds for different times of day
- Consider rate of change, not just absolute values

### 4. Error Handling

```python
async def safe_health_check():
    try:
        # Actual health check
        result = await perform_check()
        return HealthCheckResult(
            status=HealthStatus.HEALTHY,
            message="Check passed"
        )
    except Exception as e:
        # Don't let health check crash
        return HealthCheckResult(
            status=HealthStatus.UNHEALTHY,
            message=f"Health check failed: {str(e)}"
        )
```

## Monitoring Checklist

- [ ] All services have health check endpoints
- [ ] Critical metrics have thresholds set
- [ ] Alert handlers are configured
- [ ] Background monitoring is started on app startup
- [ ] Health endpoints return appropriate HTTP status codes
- [ ] Metrics are exported for dashboard consumption
- [ ] Health checks include dependency validation
- [ ] Response times are tracked for all checks

## Example: Complete Service Setup

```python
from src.core.health_monitor import get_global_health_monitor, health_check_endpoint

class MyService:
    def __init__(self):
        self.monitor = get_global_health_monitor()
        self.setup_monitoring()
    
    def setup_monitoring(self):
        """Configure monitoring for this service."""
        # Set metric thresholds
        self.monitor.alert_manager.set_threshold(
            "myservice.error_rate", "warning", 0.01
        )
        self.monitor.alert_manager.set_threshold(
            "myservice.response_time", "warning", 1000.0
        )
    
    @health_check_endpoint("myservice")
    async def health_check(self):
        """Service health check."""
        checks = {
            "database": await self.check_database(),
            "cache": await self.check_cache(),
            "upstream": await self.check_upstream_service()
        }
        
        # Overall health based on dependencies
        if all(checks.values()):
            status = HealthStatus.HEALTHY
            message = "All systems operational"
        elif any(checks.values()):
            status = HealthStatus.DEGRADED
            message = f"Degraded: {[k for k,v in checks.items() if not v]}"
        else:
            status = HealthStatus.UNHEALTHY
            message = "Service unavailable"
        
        return HealthCheckResult(
            service_name="myservice",
            status=status,
            message=message,
            timestamp=datetime.now(),
            response_time=0.05,
            metadata={"checks": checks}
        )
    
    async def record_request(self, duration: float, error: bool = False):
        """Record request metrics."""
        self.monitor.metrics_collector.record_metric(
            "myservice.requests.total",
            1,
            MetricType.COUNTER
        )
        
        if error:
            self.monitor.metrics_collector.record_metric(
                "myservice.errors.total",
                1,
                MetricType.COUNTER
            )
        
        self.monitor.metrics_collector.record_metric(
            "myservice.response_time",
            duration * 1000,
            MetricType.HISTOGRAM,
            unit="ms"
        )
```

## Conclusion

The health monitoring system provides:

- ✅ Real-time health checks for all services
- ✅ Comprehensive metrics collection
- ✅ Threshold-based alerting
- ✅ System resource monitoring
- ✅ Background monitoring capabilities
- ✅ Dashboard-ready data export
- ✅ Easy integration via decorators

This ensures operational visibility and enables proactive issue detection throughout the KGAS system.