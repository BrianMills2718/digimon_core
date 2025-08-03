"""
Health Monitoring Data Models

Data structures for health checks, metrics, and alerts.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class HealthMetrics:
    """Health metrics for service monitoring"""
    timestamp: datetime
    response_time_ms: float
    status_code: Optional[int] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class MetricType(Enum):
    """Types of metrics collected"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    service_name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    response_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "service_name": self.service_name,
            "status": self.status.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "response_time": self.response_time,
            "metadata": self.metadata,
            "dependencies": self.dependencies
        }

    def is_healthy(self) -> bool:
        """Check if the result indicates a healthy status"""
        return self.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]

    def is_critical(self) -> bool:
        """Check if the result indicates a critical status"""
        return self.status == HealthStatus.CRITICAL


@dataclass
class SystemMetric:
    """System metric data point"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "name": self.name,
            "value": self.value,
            "metric_type": self.metric_type.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "unit": self.unit
        }

    def with_tags(self, **tags) -> "SystemMetric":
        """Create a new metric with additional tags"""
        new_tags = self.tags.copy()
        new_tags.update(tags)
        return SystemMetric(
            name=self.name,
            value=self.value,
            metric_type=self.metric_type,
            timestamp=self.timestamp,
            tags=new_tags,
            unit=self.unit
        )


@dataclass
class Alert:
    """System alert"""
    alert_id: str
    severity: str
    title: str
    message: str
    timestamp: datetime
    service_name: str
    metric_name: Optional[str] = None
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "alert_id": self.alert_id,
            "severity": self.severity,
            "title": self.title,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "service_name": self.service_name,
            "metric_name": self.metric_name,
            "threshold_value": self.threshold_value,
            "actual_value": self.actual_value,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }

    def resolve(self, resolved_at: Optional[datetime] = None) -> None:
        """Mark alert as resolved"""
        self.resolved = True
        self.resolved_at = resolved_at or datetime.now()

    def is_critical(self) -> bool:
        """Check if alert is critical severity"""
        return self.severity.lower() == "critical"

    def is_active(self) -> bool:
        """Check if alert is still active (not resolved)"""
        return not self.resolved


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration for health monitoring"""
    name: str
    url: str
    method: str = "GET"
    timeout: float = 30.0
    expected_status: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    check_interval: int = 60  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "name": self.name,
            "url": self.url,
            "method": self.method,
            "timeout": self.timeout,
            "expected_status": self.expected_status,
            "headers": self.headers,
            "check_interval": self.check_interval
        }


@dataclass
class ServiceStatus:
    """Current status of a monitored service"""
    service_name: str
    status: HealthStatus
    last_check: datetime
    last_healthy: Optional[datetime] = None
    consecutive_failures: int = 0
    total_checks: int = 0
    uptime_percentage: float = 0.0
    average_response_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "service_name": self.service_name,
            "status": self.status.value,
            "last_check": self.last_check.isoformat(),
            "last_healthy": self.last_healthy.isoformat() if self.last_healthy else None,
            "consecutive_failures": self.consecutive_failures,
            "total_checks": self.total_checks,
            "uptime_percentage": self.uptime_percentage,
            "average_response_time": self.average_response_time
        }

    def update_from_check(self, check_result: HealthCheckResult) -> None:
        """Update status from a health check result"""
        self.last_check = check_result.timestamp
        self.total_checks += 1
        
        if check_result.is_healthy():
            self.last_healthy = check_result.timestamp
            self.consecutive_failures = 0
            self.status = check_result.status
        else:
            self.consecutive_failures += 1
            self.status = check_result.status

        # Update average response time (simple moving average)
        if self.average_response_time == 0.0:
            self.average_response_time = check_result.response_time
        else:
            self.average_response_time = (
                (self.average_response_time * (self.total_checks - 1) + check_result.response_time) 
                / self.total_checks
            )


@dataclass
class HealthThresholds:
    """Threshold configuration for health monitoring"""
    cpu_warning: float = 70.0
    cpu_critical: float = 90.0
    memory_warning: float = 80.0
    memory_critical: float = 95.0
    disk_warning: float = 85.0
    disk_critical: float = 95.0
    response_time_warning: float = 1000.0  # milliseconds
    response_time_critical: float = 5000.0  # milliseconds
    consecutive_failures_critical: int = 3

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary representation"""
        return {
            "cpu_warning": self.cpu_warning,
            "cpu_critical": self.cpu_critical,
            "memory_warning": self.memory_warning,
            "memory_critical": self.memory_critical,
            "disk_warning": self.disk_warning,
            "disk_critical": self.disk_critical,
            "response_time_warning": self.response_time_warning,
            "response_time_critical": self.response_time_critical,
            "consecutive_failures_critical": self.consecutive_failures_critical
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "HealthThresholds":
        """Create instance from dictionary"""
        return cls(**data)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"