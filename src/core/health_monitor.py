"""
Comprehensive System Health Monitoring - Main Interface

Streamlined health monitoring interface using decomposed components.
Reduced from 1,047 lines to focused interface.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable

from .health_monitoring import (
    SystemHealthMonitor, HealthThresholds, HealthStatus,
    get_global_health_monitor, health_check_endpoint, timed_operation,
    ServiceEndpoint, HealthCheckResult, SystemMetric, MetricsCollector, Alert, AlertManager
)

logger = logging.getLogger(__name__)


class HealthMonitor:
    """
    Main health monitoring interface that coordinates all health monitoring activities.
    
    Uses decomposed components for maintainability and testing:
    - SystemHealthMonitor: Main coordination
    - MetricsCollector: System metrics collection
    - AlertManager: Alert rules and notifications  
    - ServiceHealthMonitor: Service endpoint monitoring
    """
    
    def __init__(self, thresholds: Optional[HealthThresholds] = None):
        """Initialize health monitor with decomposed components"""
        self.thresholds = thresholds or HealthThresholds()
        
        # Use decomposed system health monitor
        self.system_monitor = SystemHealthMonitor(self.thresholds)
        
        # Monitoring state
        self._initialized = False
        
        logger.info("✅ Health Monitor initialized with decomposed architecture")
    
    async def initialize(self):
        """Initialize the health monitoring system"""
        if self._initialized:
            return
        
        try:
            await self.system_monitor.initialize()
            self._initialized = True
            logger.info("Health Monitor fully initialized")
        except Exception as e:
            logger.error(f"Error initializing health monitor: {e}")
            raise
    
    async def cleanup(self):
        """Clean up all monitoring resources"""
        try:
            await self.system_monitor.cleanup()
            self._initialized = False
            logger.info("Health Monitor cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def start_monitoring(self):
        """Start comprehensive system monitoring"""
        if not self._initialized:
            await self.initialize()
        
        await self.system_monitor.start_monitoring()
        logger.info("Started comprehensive health monitoring")
    
    async def stop_monitoring(self):
        """Stop all monitoring activities"""
        await self.system_monitor.stop_monitoring()
        logger.info("Stopped health monitoring")
    
    def register_service(self, service_name: str, url: str, **kwargs):
        """Register a service for health monitoring"""
        self.system_monitor.register_service(service_name, url, **kwargs)
    
    def register_health_check(self, service_name: str, check_function: Callable):
        """Register a custom health check function"""
        self.system_monitor.register_health_check(service_name, check_function)
    
    async def check_service_health(self, service_name: str) -> HealthCheckResult:
        """Check health of a specific service"""
        return await self.system_monitor.check_service_health(service_name)
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        return await self.system_monitor.get_system_health()
    
    async def get_service_health(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get health status for a specific service"""
        return await self.system_monitor.get_service_health(service_name)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        return self.system_monitor.get_current_metrics()
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        return self.system_monitor.get_active_alerts()
    
    def get_alerts_by_service(self, service_name: str) -> List[Dict[str, Any]]:
        """Get alerts for a specific service"""
        return self.system_monitor.get_alerts_by_service(service_name)
    
    def resolve_alert(self, alert_id: str):
        """Resolve a specific alert"""
        self.system_monitor.resolve_alert(alert_id)
    
    def add_notification_handler(self, handler: Callable):
        """Add a custom notification handler"""
        self.system_monitor.add_notification_handler(handler)
    
    def update_thresholds(self, new_thresholds: HealthThresholds):
        """Update health monitoring thresholds"""
        self.system_monitor.update_thresholds(new_thresholds)
    
    def add_alert_rule(self, rule_id: str, metric_pattern: str, condition: str,
                      threshold: float, severity: str, message_template: str,
                      service_name: str = "system"):
        """Add a custom alert rule"""
        self.system_monitor.add_alert_rule(
            rule_id, metric_pattern, condition, threshold, 
            severity, message_template, service_name
        )
    
    def remove_alert_rule(self, rule_id: str):
        """Remove an alert rule"""
        self.system_monitor.remove_alert_rule(rule_id)
    
    def get_metrics_history(self, metric_name: str, limit: int = 100):
        """Get historical values for a metric"""
        return self.system_monitor.get_metrics_history(metric_name, limit)
    
    def record_custom_metric(self, name: str, value: float, metric_type, unit: str = "", **tags):
        """Record a custom application metric"""
        self.system_monitor.record_custom_metric(name, value, metric_type, unit, **tags)
    
    async def force_health_check(self) -> Dict[str, Any]:
        """Force an immediate comprehensive health check"""
        return await self.system_monitor.force_health_check()
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a quick health summary"""
        return self.system_monitor.get_health_summary()
    
    def cleanup_old_data(self, max_age_days: int = 7):
        """Clean up old monitoring data"""
        self.system_monitor.cleanup_old_data(max_age_days)
    
    def get_monitoring_info(self) -> Dict[str, Any]:
        """Get information about the monitoring system"""
        return {
            "tool_id": "health_monitor",
            "tool_type": "MONITORING",
            "status": "functional" if self._initialized else "not_initialized",
            "description": "Comprehensive system health monitoring",
            "version": "2.0.0",
            "architecture": "decomposed_components",
            "dependencies": ["psutil", "aiohttp", "asyncio"],
            "capabilities": [
                "system_metrics_collection",
                "service_health_monitoring",
                "alert_management",
                "notification_handling",
                "threshold_monitoring",
                "historical_tracking"
            ],
            "components": {
                "system_monitor": "SystemHealthMonitor",
                "metrics_collector": "MetricsCollector",
                "alert_manager": "AlertManager",
                "service_monitor": "ServiceHealthMonitor"
            },
            "initialized": self._initialized,
            "decomposed": True,
            "file_count": 6,  # Main file + 5 component files
            "total_lines": 202  # This main file line count
        }
    
    # Context manager support
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        await self.start_monitoring()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()


# Convenience functions using global monitor
def get_health_monitor() -> HealthMonitor:
    """Get global health monitor instance"""
    # Create wrapper around global system monitor
    monitor = HealthMonitor()
    monitor.system_monitor = get_global_health_monitor()
    return monitor


async def quick_health_check() -> Dict[str, Any]:
    """Perform a quick system health check"""
    monitor = get_global_health_monitor()
    return await monitor.force_health_check()


def register_service_health_check(service_name: str, check_function: Callable):
    """Register a service health check (convenience function)"""
    monitor = get_global_health_monitor()
    monitor.register_health_check(service_name, check_function)


def record_metric(name: str, value: float, metric_type, unit: str = "", **tags):
    """Record a metric (convenience function)"""
    monitor = get_global_health_monitor()
    monitor.record_custom_metric(name, value, metric_type, unit, **tags)


# Export the original interfaces for backward compatibility
from .health_monitoring.system_health_monitor import (
    get_global_health_monitor as get_global_system_health_monitor
)
from .health_monitoring.data_models import HealthStatus, MetricType

# Export main classes
__all__ = [
    "HealthMonitor",
    "HealthStatus", 
    "MetricType",
    "HealthThresholds",
    "get_health_monitor",
    "quick_health_check",
    "register_service_health_check",
    "record_metric",
    "health_check_endpoint",
    "timed_operation"
]