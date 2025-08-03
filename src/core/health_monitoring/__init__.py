"""
Health Monitoring Module

Decomposed health monitoring components for comprehensive system monitoring.
Provides real-time health checks, metrics collection, and operational visibility.
"""

from .data_models import (
    HealthMetrics,
    HealthStatus,
    MetricType,
    HealthCheckResult,
    SystemMetric,
    Alert,
    ServiceEndpoint,
    ServiceStatus,
    HealthThresholds,
    AlertSeverity
)

from .metrics_collector import MetricsCollector, MetricTimer
from .alert_manager import (
    AlertManager,
    AlertRule,
    console_notification_handler,
    log_notification_handler,
    webhook_notification_handler
)
from .service_health_monitor import (
    ServiceHealthMonitor,
    neo4j_health_check,
    sqlite_health_check
)
from .system_health_monitor import (
    SystemHealthMonitor,
    get_global_health_monitor,
    health_check_endpoint,
    timed_operation
)

__all__ = [
    # Data models
    "HealthMetrics",
    "HealthStatus",
    "MetricType", 
    "HealthCheckResult",
    "SystemMetric",
    "Alert",
    "ServiceEndpoint",
    "ServiceStatus",
    "HealthThresholds",
    "AlertSeverity",
    
    # Core components
    "MetricsCollector",
    "MetricTimer",
    "AlertManager",
    "AlertRule", 
    "ServiceHealthMonitor",
    "SystemHealthMonitor",
    
    # Notification handlers
    "console_notification_handler",
    "log_notification_handler", 
    "webhook_notification_handler",
    
    # Built-in health checks
    "neo4j_health_check",
    "sqlite_health_check",
    
    # Utilities
    "get_global_health_monitor",
    "health_check_endpoint",
    "timed_operation"
]