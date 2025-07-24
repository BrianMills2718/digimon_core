#!/usr/bin/env python3
"""
Comprehensive System Health Monitoring

Provides real-time health checks, metrics collection, and operational 
visibility for all KGAS services. Critical architectural fix for 
Phase RELIABILITY.

Replaces the current lack of operational visibility with comprehensive
monitoring, alerting, and debugging capabilities.
"""

import asyncio
import logging
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import uuid

logger = logging.getLogger(__name__)


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


@dataclass
class SystemMetric:
    """System metric data point"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""


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


class MetricsCollector:
    """Collect and store system metrics"""
    
    def __init__(self, max_history=10000):
        self.metrics_history = deque(maxlen=max_history)
        self.current_metrics: Dict[str, SystemMetric] = {}
        self._lock = threading.Lock()
        
        # Start background metric collection
        self.collection_task = None
        self.collection_interval = 30  # seconds
        
    async def start_collection(self):
        """Start background metrics collection"""
        if self.collection_task is None:
            self.collection_task = asyncio.create_task(self._collect_system_metrics())
            logger.info("Started metrics collection")
    
    async def stop_collection(self):
        """Stop background metrics collection"""
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
            self.collection_task = None
            logger.info("Stopped metrics collection")
    
    async def _collect_system_metrics(self):
        """Background task to collect system metrics"""
        while True:
            try:
                await self._collect_cpu_metrics()
                await self._collect_memory_metrics()
                await self._collect_disk_metrics()
                await self._collect_network_metrics()
                
                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_cpu_metrics(self):
        """Collect CPU metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        self.record_metric("system.cpu.usage", cpu_percent, MetricType.GAUGE, unit="%")
        
        cpu_count = psutil.cpu_count()
        self.record_metric("system.cpu.count", cpu_count, MetricType.GAUGE)
        
        load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
        self.record_metric("system.load.1min", load_avg[0], MetricType.GAUGE)
        self.record_metric("system.load.5min", load_avg[1], MetricType.GAUGE)
        self.record_metric("system.load.15min", load_avg[2], MetricType.GAUGE)
    
    async def _collect_memory_metrics(self):
        """Collect memory metrics"""
        memory = psutil.virtual_memory()
        self.record_metric("system.memory.total", memory.total, MetricType.GAUGE, unit="bytes")
        self.record_metric("system.memory.available", memory.available, MetricType.GAUGE, unit="bytes")
        self.record_metric("system.memory.used", memory.used, MetricType.GAUGE, unit="bytes")
        self.record_metric("system.memory.percent", memory.percent, MetricType.GAUGE, unit="%")
        
        swap = psutil.swap_memory()
        self.record_metric("system.swap.total", swap.total, MetricType.GAUGE, unit="bytes")
        self.record_metric("system.swap.used", swap.used, MetricType.GAUGE, unit="bytes")
        self.record_metric("system.swap.percent", swap.percent, MetricType.GAUGE, unit="%")
    
    async def _collect_disk_metrics(self):
        """Collect disk metrics"""
        disk_usage = psutil.disk_usage('/')
        self.record_metric("system.disk.total", disk_usage.total, MetricType.GAUGE, unit="bytes")
        self.record_metric("system.disk.used", disk_usage.used, MetricType.GAUGE, unit="bytes")
        self.record_metric("system.disk.free", disk_usage.free, MetricType.GAUGE, unit="bytes")
        self.record_metric("system.disk.percent", (disk_usage.used / disk_usage.total) * 100, MetricType.GAUGE, unit="%")
        
        disk_io = psutil.disk_io_counters()
        if disk_io:
            self.record_metric("system.disk.read_bytes", disk_io.read_bytes, MetricType.COUNTER, unit="bytes")
            self.record_metric("system.disk.write_bytes", disk_io.write_bytes, MetricType.COUNTER, unit="bytes")
    
    async def _collect_network_metrics(self):
        """Collect network metrics"""
        net_io = psutil.net_io_counters()
        if net_io:
            self.record_metric("system.network.bytes_sent", net_io.bytes_sent, MetricType.COUNTER, unit="bytes")
            self.record_metric("system.network.bytes_recv", net_io.bytes_recv, MetricType.COUNTER, unit="bytes")
            self.record_metric("system.network.packets_sent", net_io.packets_sent, MetricType.COUNTER)
            self.record_metric("system.network.packets_recv", net_io.packets_recv, MetricType.COUNTER)
    
    def record_metric(self, name: str, value: float, metric_type: MetricType, 
                     tags: Dict[str, str] = None, unit: str = ""):
        """Record a metric value"""
        metric = SystemMetric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.now(),
            tags=tags or {},
            unit=unit
        )
        
        with self._lock:
            self.current_metrics[name] = metric
            self.metrics_history.append(metric)
    
    def get_current_metrics(self) -> Dict[str, SystemMetric]:
        """Get current metric values"""
        with self._lock:
            return self.current_metrics.copy()
    
    def get_metric_history(self, name: str, minutes: int = 60) -> List[SystemMetric]:
        """Get metric history for specified time period"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self._lock:
            return [
                metric for metric in self.metrics_history
                if metric.name == name and metric.timestamp >= cutoff_time
            ]


class AlertManager:
    """Manage system alerts and notifications"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_handlers: List[Callable] = []
        self.thresholds: Dict[str, Dict[str, float]] = {}
        self._lock = threading.Lock()
        
        # Setup default thresholds
        self._setup_default_thresholds()
    
    def _setup_default_thresholds(self):
        """Setup default alert thresholds"""
        self.thresholds = {
            "system.cpu.usage": {"warning": 80.0, "critical": 95.0},
            "system.memory.percent": {"warning": 80.0, "critical": 95.0},
            "system.disk.percent": {"warning": 80.0, "critical": 95.0},
            "service.response_time": {"warning": 5.0, "critical": 10.0},
            "service.error_rate": {"warning": 0.05, "critical": 0.10},
        }
    
    def register_alert_handler(self, handler: Callable):
        """Register alert handler for notifications"""
        self.alert_handlers.append(handler)
        logger.info("Registered alert handler")
    
    def set_threshold(self, metric_name: str, level: str, value: float):
        """Set alert threshold for metric"""
        if metric_name not in self.thresholds:
            self.thresholds[metric_name] = {}
        self.thresholds[metric_name][level] = value
        logger.info(f"Set {level} threshold for {metric_name}: {value}")
    
    async def check_metric_thresholds(self, metric: SystemMetric):
        """Check if metric exceeds thresholds and create alerts"""
        thresholds = self.thresholds.get(metric.name)
        if not thresholds:
            return
        
        # Check critical threshold first
        if "critical" in thresholds and metric.value >= thresholds["critical"]:
            await self._create_alert(
                "critical",
                f"Critical threshold exceeded: {metric.name}",
                f"Metric {metric.name} value {metric.value} exceeds critical threshold {thresholds['critical']}",
                metric.name,
                thresholds["critical"],
                metric.value
            )
        elif "warning" in thresholds and metric.value >= thresholds["warning"]:
            await self._create_alert(
                "warning",
                f"Warning threshold exceeded: {metric.name}",
                f"Metric {metric.name} value {metric.value} exceeds warning threshold {thresholds['warning']}",
                metric.name,
                thresholds["warning"],
                metric.value
            )
    
    async def _create_alert(self, severity: str, title: str, message: str,
                          metric_name: str = None, threshold_value: float = None,
                          actual_value: float = None):
        """Create new alert"""
        alert_id = str(uuid.uuid4())
        
        alert = Alert(
            alert_id=alert_id,
            severity=severity,
            title=title,
            message=message,
            timestamp=datetime.now(),
            service_name="system",
            metric_name=metric_name,
            threshold_value=threshold_value,
            actual_value=actual_value
        )
        
        with self._lock:
            self.alerts[alert_id] = alert
        
        # Send alert to handlers
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
        
        logger.warning(f"[{severity.upper()}] {title}: {message}")
    
    def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        with self._lock:
            if alert_id in self.alerts:
                self.alerts[alert_id].resolved = True
                self.alerts[alert_id].resolved_at = datetime.now()
                logger.info(f"Resolved alert {alert_id}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts"""
        with self._lock:
            return [alert for alert in self.alerts.values() if not alert.resolved]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary statistics"""
        with self._lock:
            active_alerts = [alert for alert in self.alerts.values() if not alert.resolved]
            
            summary = {
                "total_alerts": len(self.alerts),
                "active_alerts": len(active_alerts),
                "alert_breakdown": defaultdict(int)
            }
            
            for alert in active_alerts:
                summary["alert_breakdown"][alert.severity] += 1
            
            return dict(summary)


class SystemHealthMonitor:
    """
    Comprehensive system health monitoring with real-time checks,
    metrics collection, and alerting.
    """
    
    def __init__(self):
        self.health_checks: Dict[str, Callable] = {}
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.last_health_check: Dict[str, HealthCheckResult] = {}
        self._lock = asyncio.Lock()
        
        # Monitoring configuration
        self.health_check_interval = 60  # seconds
        self.monitoring_enabled = False
        self.monitoring_task = None
        
        # Register default health checks
        self._register_default_health_checks()
        
        logger.info("SystemHealthMonitor initialized")
    
    def _register_default_health_checks(self):
        """Register default health checks for core services"""
        self.register_health_check("system", self._check_system_health)
        self.register_health_check("memory", self._check_memory_health)
        self.register_health_check("disk", self._check_disk_health)
        self.register_health_check("cpu", self._check_cpu_health)
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        if self.monitoring_enabled:
            return
        
        self.monitoring_enabled = True
        
        # Start metrics collection
        await self.metrics_collector.start_collection()
        
        # Start health check loop
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("Started system health monitoring")
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        if not self.monitoring_enabled:
            return
        
        self.monitoring_enabled = False
        
        # Stop metrics collection
        await self.metrics_collector.stop_collection()
        
        # Stop monitoring task
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped system health monitoring")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_enabled:
            try:
                # Run all health checks
                await self._run_all_health_checks()
                
                # Check metric thresholds
                await self._check_all_thresholds()
                
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def _run_all_health_checks(self):
        """Run all registered health checks"""
        for service_name, check_func in self.health_checks.items():
            try:
                result = await self._run_health_check(service_name, check_func)
                self.last_health_check[service_name] = result
                
                # Create alerts for unhealthy services
                if result.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                    await self.alert_manager._create_alert(
                        "critical" if result.status == HealthStatus.CRITICAL else "warning",
                        f"Service {service_name} is {result.status.value}",
                        result.message,
                        service_name=service_name
                    )
                
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                
                # Create failure result
                failure_result = HealthCheckResult(
                    service_name=service_name,
                    status=HealthStatus.UNKNOWN,
                    message=f"Health check failed: {str(e)}",
                    timestamp=datetime.now(),
                    response_time=0.0
                )
                self.last_health_check[service_name] = failure_result
    
    async def _run_health_check(self, service_name: str, check_func: Callable) -> HealthCheckResult:
        """Run individual health check with timing"""
        start_time = time.time()
        
        try:
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            
            response_time = time.time() - start_time
            
            # Ensure result is HealthCheckResult
            if isinstance(result, dict):
                return HealthCheckResult(
                    service_name=service_name,
                    status=HealthStatus(result.get("status", "unknown")),
                    message=result.get("message", ""),
                    timestamp=datetime.now(),
                    response_time=response_time,
                    metadata=result.get("metadata", {}),
                    dependencies=result.get("dependencies", [])
                )
            elif isinstance(result, HealthCheckResult):
                result.response_time = response_time
                return result
            else:
                return HealthCheckResult(
                    service_name=service_name,
                    status=HealthStatus.HEALTHY,
                    message="Health check passed",
                    timestamp=datetime.now(),
                    response_time=response_time
                )
        
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                service_name=service_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check error: {str(e)}",
                timestamp=datetime.now(),
                response_time=response_time
            )
    
    async def _check_all_thresholds(self):
        """Check all metrics against thresholds"""
        current_metrics = self.metrics_collector.get_current_metrics()
        
        for metric in current_metrics.values():
            await self.alert_manager.check_metric_thresholds(metric)
    
    def register_health_check(self, service_name: str, check_func: Callable):
        """Register health check for service"""
        self.health_checks[service_name] = check_func
        logger.info(f"Registered health check for {service_name}")
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        async with self._lock:
            # Run all health checks if not recently run
            current_time = datetime.now()
            outdated_checks = []
            
            for service_name in self.health_checks.keys():
                last_check = self.last_health_check.get(service_name)
                if (not last_check or 
                    (current_time - last_check.timestamp).total_seconds() > self.health_check_interval):
                    outdated_checks.append(service_name)
            
            # Run outdated checks
            for service_name in outdated_checks:
                check_func = self.health_checks[service_name]
                result = await self._run_health_check(service_name, check_func)
                self.last_health_check[service_name] = result
            
            # Compile overall status
            all_healthy = True
            any_critical = False
            service_statuses = {}
            
            for service_name, result in self.last_health_check.items():
                service_statuses[service_name] = {
                    "status": result.status.value,
                    "message": result.message,
                    "response_time": result.response_time,
                    "timestamp": result.timestamp.isoformat(),
                    "metadata": result.metadata
                }
                
                if result.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                    all_healthy = False
                if result.status == HealthStatus.CRITICAL:
                    any_critical = True
            
            # Determine overall status
            if any_critical:
                overall_status = HealthStatus.CRITICAL
            elif not all_healthy:
                overall_status = HealthStatus.DEGRADED
            else:
                overall_status = HealthStatus.HEALTHY
            
            # Get metrics and alerts
            current_metrics = self.metrics_collector.get_current_metrics()
            active_alerts = self.alert_manager.get_active_alerts()
            
            return {
                "overall_status": overall_status.value,
                "services": service_statuses,
                "metrics": {
                    name: {
                        "value": metric.value,
                        "unit": metric.unit,
                        "timestamp": metric.timestamp.isoformat()
                    }
                    for name, metric in current_metrics.items()
                },
                "active_alerts": [
                    {
                        "severity": alert.severity,
                        "title": alert.title,
                        "message": alert.message,
                        "timestamp": alert.timestamp.isoformat()
                    }
                    for alert in active_alerts
                ],
                "timestamp": datetime.now().isoformat()
            }
    
    # Default health checks
    async def _check_system_health(self) -> HealthCheckResult:
        """Check overall system health"""
        try:
            # Check basic system resources
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            issues = []
            status = HealthStatus.HEALTHY
            
            if cpu_percent > 90:
                issues.append(f"High CPU usage: {cpu_percent}%")
                status = HealthStatus.CRITICAL
            elif cpu_percent > 80:
                issues.append(f"Elevated CPU usage: {cpu_percent}%")
                status = HealthStatus.DEGRADED
            
            if memory.percent > 90:
                issues.append(f"High memory usage: {memory.percent}%")
                status = HealthStatus.CRITICAL
            elif memory.percent > 80:
                issues.append(f"Elevated memory usage: {memory.percent}%")
                status = HealthStatus.DEGRADED
            
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > 90:
                issues.append(f"High disk usage: {disk_percent:.1f}%")
                status = HealthStatus.CRITICAL
            elif disk_percent > 80:
                issues.append(f"Elevated disk usage: {disk_percent:.1f}%")
                status = HealthStatus.DEGRADED
            
            message = "; ".join(issues) if issues else "System resources within normal limits"
            
            return HealthCheckResult(
                service_name="system",
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time=0.0,
                metadata={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk_percent
                }
            )
        
        except Exception as e:
            return HealthCheckResult(
                service_name="system",
                status=HealthStatus.UNKNOWN,
                message=f"System health check failed: {str(e)}",
                timestamp=datetime.now(),
                response_time=0.0
            )
    
    async def _check_memory_health(self) -> HealthCheckResult:
        """Check memory health"""
        try:
            memory = psutil.virtual_memory()
            
            if memory.percent > 95:
                status = HealthStatus.CRITICAL
                message = f"Critical memory usage: {memory.percent}%"
            elif memory.percent > 85:
                status = HealthStatus.DEGRADED
                message = f"High memory usage: {memory.percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory.percent}%"
            
            return HealthCheckResult(
                service_name="memory",
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time=0.0,
                metadata={
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent
                }
            )
        
        except Exception as e:
            return HealthCheckResult(
                service_name="memory",
                status=HealthStatus.UNKNOWN,
                message=f"Memory check failed: {str(e)}",
                timestamp=datetime.now(),
                response_time=0.0
            )
    
    async def _check_disk_health(self) -> HealthCheckResult:
        """Check disk health"""
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            if disk_percent > 95:
                status = HealthStatus.CRITICAL
                message = f"Critical disk usage: {disk_percent:.1f}%"
            elif disk_percent > 85:
                status = HealthStatus.DEGRADED
                message = f"High disk usage: {disk_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk usage normal: {disk_percent:.1f}%"
            
            return HealthCheckResult(
                service_name="disk",
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time=0.0,
                metadata={
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_percent": disk_percent
                }
            )
        
        except Exception as e:
            return HealthCheckResult(
                service_name="disk",
                status=HealthStatus.UNKNOWN,
                message=f"Disk check failed: {str(e)}",
                timestamp=datetime.now(),
                response_time=0.0
            )
    
    async def _check_cpu_health(self) -> HealthCheckResult:
        """Check CPU health"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_percent > 95:
                status = HealthStatus.CRITICAL
                message = f"Critical CPU usage: {cpu_percent}%"
            elif cpu_percent > 85:
                status = HealthStatus.DEGRADED
                message = f"High CPU usage: {cpu_percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU usage normal: {cpu_percent}%"
            
            return HealthCheckResult(
                service_name="cpu",
                status=status,
                message=message,
                timestamp=datetime.now(),
                response_time=0.0,
                metadata={
                    "cpu_count": psutil.cpu_count(),
                    "cpu_percent": cpu_percent
                }
            )
        
        except Exception as e:
            return HealthCheckResult(
                service_name="cpu",
                status=HealthStatus.UNKNOWN,
                message=f"CPU check failed: {str(e)}",
                timestamp=datetime.now(),
                response_time=0.0
            )


# Health check endpoints for services
async def neo4j_health_check() -> HealthCheckResult:
    """Check Neo4j database health"""
    try:
        from .neo4j_manager import Neo4jDockerManager
        
        neo4j_manager = Neo4jDockerManager()
        
        # Try to get a session and run a simple query
        start_time = time.time()
        session = await neo4j_manager.get_session_async()
        result = await session.run("RETURN 1 as health")
        await result.single()
        await session.close()
        response_time = time.time() - start_time
        
        return HealthCheckResult(
            service_name="neo4j",
            status=HealthStatus.HEALTHY,
            message="Neo4j database is responsive",
            timestamp=datetime.now(),
            response_time=response_time,
            metadata={
                "response_time_ms": round(response_time * 1000, 2)
            }
        )
    
    except Exception as e:
        return HealthCheckResult(
            service_name="neo4j",
            status=HealthStatus.UNHEALTHY,
            message=f"Neo4j health check failed: {str(e)}",
            timestamp=datetime.now(),
            response_time=0.0
        )


async def sqlite_health_check() -> HealthCheckResult:
    """Check SQLite database health"""
    try:
        import sqlite3
        
        start_time = time.time()
        
        # Try to connect to SQLite and run a simple query
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        
        response_time = time.time() - start_time
        
        return HealthCheckResult(
            service_name="sqlite",
            status=HealthStatus.HEALTHY,
            message="SQLite is functional",
            timestamp=datetime.now(),
            response_time=response_time,
            metadata={
                "response_time_ms": round(response_time * 1000, 2)
            }
        )
    
    except Exception as e:
        return HealthCheckResult(
            service_name="sqlite",
            status=HealthStatus.UNHEALTHY,
            message=f"SQLite health check failed: {str(e)}",
            timestamp=datetime.now(),
            response_time=0.0
        )


# Service health monitoring with HTTP endpoints
import aiohttp


@dataclass
class ServiceEndpoint:
    """Configuration for a service health endpoint"""
    name: str
    health_url: str
    timeout: float = 5.0
    expected_status: int = 200
    critical: bool = True  # If false, service can be degraded


class ServiceHealthMonitor:
    """Real-time service health monitoring via HTTP endpoints"""
    
    def __init__(self, check_interval: int = 30):
        self.services: Dict[str, ServiceEndpoint] = {}
        self.health_history: Dict[str, List[HealthMetrics]] = {}
        self.check_interval = check_interval
        self._monitor_task: Optional[asyncio.Task] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._callbacks: List[Callable] = []
    
    def register_service(self, endpoint: ServiceEndpoint) -> None:
        """Register a service for health monitoring"""
        self.services[endpoint.name] = endpoint
        self.health_history[endpoint.name] = []
        logger.info(f"Registered service {endpoint.name} for health monitoring")
    
    def register_callback(self, callback: Callable[[str, HealthMetrics], None]) -> None:
        """Register callback for health status changes"""
        self._callbacks.append(callback)
    
    async def start_monitoring(self) -> None:
        """Start continuous health monitoring"""
        if self._monitor_task:
            return
        
        self._session = aiohttp.ClientSession()
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Started service health monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop health monitoring"""
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        if self._session:
            await self._session.close()
        
        logger.info("Stopped service health monitoring")
    
    async def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while True:
            try:
                # Check all services concurrently
                check_tasks = []
                for service_name, endpoint in self.services.items():
                    task = self._check_service_health(service_name, endpoint)
                    check_tasks.append(task)
                
                await asyncio.gather(*check_tasks, return_exceptions=True)
                
                # Wait for next check interval
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitor loop: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def _check_service_health(self, service_name: str, endpoint: ServiceEndpoint) -> None:
        """Check health of a single service"""
        start_time = asyncio.get_event_loop().time()
        metrics = HealthMetrics(
            timestamp=datetime.now(),
            response_time_ms=0,
            status_code=None,
            error=None
        )
        
        try:
            async with self._session.get(
                endpoint.health_url,
                timeout=aiohttp.ClientTimeout(total=endpoint.timeout)
            ) as response:
                end_time = asyncio.get_event_loop().time()
                metrics.response_time_ms = (end_time - start_time) * 1000
                metrics.status_code = response.status
                
                if response.status == endpoint.expected_status:
                    # Parse health response if JSON
                    if 'application/json' in response.headers.get('Content-Type', ''):
                        health_data = await response.json()
                        metrics.metadata = health_data
                else:
                    metrics.error = f"Unexpected status: {response.status}"
                    
        except asyncio.TimeoutError:
            metrics.error = "Health check timeout"
        except aiohttp.ClientError as e:
            metrics.error = f"Connection error: {str(e)}"
        except Exception as e:
            metrics.error = f"Unexpected error: {str(e)}"
        
        # Store metrics
        self.health_history[service_name].append(metrics)
        
        # Keep only last 100 health checks
        if len(self.health_history[service_name]) > 100:
            self.health_history[service_name] = self.health_history[service_name][-100:]
        
        # Notify callbacks
        for callback in self._callbacks:
            try:
                await callback(service_name, metrics)
            except Exception as e:
                logger.error(f"Error in health callback: {e}")
    
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get current health status of a service"""
        if service_name not in self.health_history:
            return {
                'status': 'unknown',
                'last_check': None,
                'response_time_ms': 0,
                'error_rate': 0
            }
        
        history = self.health_history[service_name]
        if not history:
            return {
                'status': 'unknown',
                'last_check': None,
                'response_time_ms': 0,
                'error_rate': 0
            }
        
        # Calculate metrics from recent history
        recent_checks = history[-10:]  # Last 10 checks
        latest = history[-1]
        
        error_count = sum(1 for m in recent_checks if m.error is not None)
        error_rate = error_count / len(recent_checks)
        
        successful_checks = [m for m in recent_checks if m.error is None]
        avg_response_time = sum(m.response_time_ms for m in successful_checks) / max(1, len(successful_checks))
        
        # Determine status
        if latest.error:
            status = 'unhealthy'
        elif error_rate > 0.3:
            status = 'degraded'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'last_check': latest.timestamp.isoformat(),
            'response_time_ms': avg_response_time,
            'error_rate': error_rate,
            'latest_error': latest.error,
            'metadata': latest.metadata
        }
    
    async def check_all_services_now(self) -> Dict[str, Dict[str, Any]]:
        """Perform immediate health check on all services"""
        results = {}
        
        # Use existing session if available, create temporary one if not
        if self._session:
            session = self._session
            close_session = False
        else:
            session = aiohttp.ClientSession()
            close_session = True
        
        try:
            # Temporarily set session for health checks
            original_session = self._session
            self._session = session
            
            check_tasks = []
            for service_name, endpoint in self.services.items():
                task = self._check_service_health(service_name, endpoint)
                check_tasks.append(task)
            
            await asyncio.gather(*check_tasks, return_exceptions=True)
            
            for service_name in self.services:
                results[service_name] = await self.get_service_health(service_name)
            
        finally:
            self._session = original_session
            if close_session:
                await session.close()
        
        return results


# Global health monitor instance
_global_health_monitor = None


def get_global_health_monitor() -> SystemHealthMonitor:
    """Get or create global health monitor instance"""
    global _global_health_monitor
    if _global_health_monitor is None:
        _global_health_monitor = SystemHealthMonitor()
    return _global_health_monitor


# Decorator for service health checks
def health_check_endpoint(service_name: str):
    """Decorator to register function as health check endpoint"""
    def decorator(func):
        monitor = get_global_health_monitor()
        monitor.register_health_check(service_name, func)
        return func
    return decorator