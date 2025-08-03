"""
System Health Monitor

Main health monitoring system that coordinates metrics collection, 
service monitoring, and alerting.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from .data_models import HealthCheckResult, HealthStatus, HealthThresholds
from .metrics_collector import MetricsCollector
from .alert_manager import AlertManager, console_notification_handler, log_notification_handler
from .service_health_monitor import ServiceHealthMonitor

logger = logging.getLogger(__name__)


class SystemHealthMonitor:
    """Comprehensive system health monitoring"""
    
    def __init__(self, thresholds: Optional[HealthThresholds] = None):
        self.thresholds = thresholds or HealthThresholds()
        
        # Initialize components
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager(self.thresholds)
        self.service_monitor = ServiceHealthMonitor(self.thresholds)
        
        # Setup default notification handlers
        self.alert_manager.add_notification_handler(console_notification_handler)
        self.alert_manager.add_notification_handler(log_notification_handler)
        
        # Monitoring state
        self._monitoring_active = False
        self._health_check_task = None
        self._health_check_interval = 60  # seconds
        
        # Overall system status
        self._system_status = HealthStatus.UNKNOWN
        self._last_system_check = None
        
        logger.info("System Health Monitor initialized")
    
    async def initialize(self):
        """Initialize the health monitoring system"""
        try:
            await self.service_monitor.initialize()
            await self.metrics_collector.start_collection()
            
            logger.info("System Health Monitor fully initialized")
        except Exception as e:
            logger.error(f"Error initializing health monitor: {e}")
            raise
    
    async def cleanup(self):
        """Clean up all monitoring resources"""
        try:
            await self.stop_monitoring()
            await self.metrics_collector.stop_collection()
            await self.service_monitor.cleanup()
            
            logger.info("System Health Monitor cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def start_monitoring(self):
        """Start comprehensive system monitoring"""
        if self._monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        try:
            self._monitoring_active = True
            
            # Start service monitoring
            await self.service_monitor.start_monitoring()
            
            # Start periodic health checks
            self._health_check_task = asyncio.create_task(self._periodic_health_checks())
            
            logger.info("Started comprehensive system monitoring")
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            self._monitoring_active = False
            raise
    
    async def stop_monitoring(self):
        """Stop all monitoring activities"""
        self._monitoring_active = False
        
        try:
            # Stop periodic health checks
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass
                self._health_check_task = None
            
            # Stop service monitoring
            await self.service_monitor.stop_monitoring()
            
            logger.info("Stopped system monitoring")
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
    
    async def _periodic_health_checks(self):
        """Periodic health check task"""
        while self._monitoring_active:
            try:
                await self._perform_system_health_check()
                await asyncio.sleep(self._health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic health check: {e}")
                await asyncio.sleep(self._health_check_interval)
    
    async def _perform_system_health_check(self):
        """Perform comprehensive system health check"""
        try:
            # Check all services
            service_results = await self.service_monitor.check_all_services()
            
            # Evaluate service health for alerts
            for result in service_results.values():
                self.alert_manager.evaluate_health_check(result)
            
            # Check system metrics for alerts
            current_metrics = self.metrics_collector.get_current_metrics()
            for metric in current_metrics.values():
                self.alert_manager.evaluate_metric(metric)
            
            # Update overall system status
            self._update_system_status(service_results)
            self._last_system_check = datetime.now()
            
        except Exception as e:
            logger.error(f"Error performing system health check: {e}")
            self._system_status = HealthStatus.UNHEALTHY
    
    def _update_system_status(self, service_results: Dict[str, HealthCheckResult]):
        """Update overall system health status"""
        if not service_results:
            self._system_status = HealthStatus.UNKNOWN
            return
        
        # Count services by status
        healthy_count = sum(1 for result in service_results.values() if result.is_healthy())
        critical_count = sum(1 for result in service_results.values() if result.is_critical())
        unhealthy_count = sum(1 for result in service_results.values() 
                            if result.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL])
        
        total_services = len(service_results)
        
        # Determine overall status
        if critical_count > 0:
            self._system_status = HealthStatus.CRITICAL
        elif unhealthy_count > total_services * 0.5:  # More than 50% unhealthy
            self._system_status = HealthStatus.UNHEALTHY
        elif unhealthy_count > 0:
            self._system_status = HealthStatus.DEGRADED
        elif healthy_count == total_services:
            self._system_status = HealthStatus.HEALTHY
        else:
            self._system_status = HealthStatus.DEGRADED
    
    def register_service(self, service_name: str, url: str, **kwargs):
        """Register a service for health monitoring"""
        from .data_models import ServiceEndpoint
        
        endpoint = ServiceEndpoint(
            name=service_name,
            url=url,
            **kwargs
        )
        self.service_monitor.register_service(service_name, endpoint)
    
    def register_health_check(self, service_name: str, check_function):
        """Register a custom health check function"""
        self.service_monitor.register_health_check(service_name, check_function)
    
    async def check_service_health(self, service_name: str) -> HealthCheckResult:
        """Check health of a specific service"""
        return await self.service_monitor.check_service_health(service_name)
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        try:
            # Get service health
            service_statuses = self.service_monitor.get_all_service_statuses()
            
            # Get current metrics
            current_metrics = self.metrics_collector.get_current_metrics()
            
            # Get alert summary
            alert_summary = self.alert_manager.get_alert_summary()
            
            # Get monitoring summary
            monitoring_summary = self.service_monitor.get_monitoring_summary()
            
            return {
                "overall_status": self._system_status.value,
                "last_check": self._last_system_check.isoformat() if self._last_system_check else None,
                "monitoring_active": self._monitoring_active,
                "services": {name: status.to_dict() for name, status in service_statuses.items()},
                "metrics": {name: metric.to_dict() for name, metric in current_metrics.items()},
                "alerts": alert_summary,
                "monitoring": monitoring_summary,
                "thresholds": self.thresholds.to_dict()
            }
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                "overall_status": HealthStatus.UNKNOWN.value,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_service_health(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get health status for a specific service"""
        status = self.service_monitor.get_service_status(service_name)
        if status:
            return status.to_dict()
        return None
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        current_metrics = self.metrics_collector.get_current_metrics()
        return {name: metric.to_dict() for name, metric in current_metrics.items()}
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        alerts = self.alert_manager.get_active_alerts()
        return [alert.to_dict() for alert in alerts]
    
    def get_alerts_by_service(self, service_name: str) -> List[Dict[str, Any]]:
        """Get alerts for a specific service"""
        alerts = self.alert_manager.get_alerts_by_service(service_name)
        return [alert.to_dict() for alert in alerts]
    
    def resolve_alert(self, alert_id: str):
        """Resolve a specific alert"""
        self.alert_manager.resolve_alert(alert_id)
    
    def add_notification_handler(self, handler):
        """Add a custom notification handler"""
        self.alert_manager.add_notification_handler(handler)
    
    def update_thresholds(self, new_thresholds: HealthThresholds):
        """Update health monitoring thresholds"""
        self.thresholds = new_thresholds
        self.alert_manager.update_thresholds(new_thresholds)
        self.service_monitor.thresholds = new_thresholds
        logger.info("Updated health monitoring thresholds")
    
    def add_alert_rule(self, rule_id: str, metric_pattern: str, condition: str,
                      threshold: float, severity: str, message_template: str,
                      service_name: str = "system"):
        """Add a custom alert rule"""
        self.alert_manager.add_alert_rule(
            rule_id, metric_pattern, condition, threshold, 
            severity, message_template, service_name
        )
    
    def remove_alert_rule(self, rule_id: str):
        """Remove an alert rule"""
        self.alert_manager.remove_alert_rule(rule_id)
    
    def get_metrics_history(self, metric_name: str, limit: int = 100):
        """Get historical values for a metric"""
        history = self.metrics_collector.get_metric_history(metric_name, limit)
        return [metric.to_dict() for metric in history]
    
    def record_custom_metric(self, name: str, value: float, metric_type, unit: str = "", **tags):
        """Record a custom application metric"""
        self.metrics_collector.record_custom_metric(name, value, metric_type, unit, **tags)
    
    async def force_health_check(self) -> Dict[str, Any]:
        """Force an immediate comprehensive health check"""
        try:
            await self._perform_system_health_check()
            return await self.get_system_health()
        except Exception as e:
            logger.error(f"Error in forced health check: {e}")
            return {
                "overall_status": HealthStatus.UNHEALTHY.value,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a quick health summary"""
        try:
            service_statuses = self.service_monitor.get_all_service_statuses()
            alert_summary = self.alert_manager.get_alert_summary()
            
            healthy_services = len([s for s in service_statuses.values() 
                                  if s.status == HealthStatus.HEALTHY])
            total_services = len(service_statuses)
            
            return {
                "overall_status": self._system_status.value,
                "healthy_services": f"{healthy_services}/{total_services}",
                "active_alerts": alert_summary.get("active_alerts", 0),
                "critical_alerts": len(self.alert_manager.get_alerts_by_severity("critical")),
                "monitoring_active": self._monitoring_active,
                "last_check": self._last_system_check.isoformat() if self._last_system_check else None
            }
        except Exception as e:
            return {
                "overall_status": HealthStatus.UNKNOWN.value,
                "error": str(e)
            }
    
    def cleanup_old_data(self, max_age_days: int = 7):
        """Clean up old monitoring data"""
        try:
            # Clean up old alerts
            self.alert_manager.cleanup_old_alerts(max_age_days)
            
            # Clear old metrics history
            self.metrics_collector.clear_history()
            
            logger.info(f"Cleaned up monitoring data older than {max_age_days} days")
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")


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


# Context manager for operation timing
class timed_operation:
    """Context manager to time operations and record metrics"""
    
    def __init__(self, operation_name: str, monitor: Optional[SystemHealthMonitor] = None):
        self.operation_name = operation_name
        self.monitor = monitor or get_global_health_monitor()
    
    def __enter__(self):
        return self.monitor.metrics_collector.time_operation(self.operation_name)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # Timer handles the exit