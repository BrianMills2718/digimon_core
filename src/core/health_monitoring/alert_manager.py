"""
Alert Manager

Manages alerts, notifications, and alert rules for health monitoring.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Set
from collections import defaultdict

from .data_models import Alert, SystemMetric, HealthCheckResult, AlertSeverity, HealthThresholds

logger = logging.getLogger(__name__)


class AlertRule:
    """Rule for generating alerts based on metric conditions"""
    
    def __init__(self, rule_id: str, metric_pattern: str, condition: str,
                 threshold: float, severity: str, message_template: str,
                 service_name: str = "system"):
        self.rule_id = rule_id
        self.metric_pattern = metric_pattern
        self.condition = condition  # "greater_than", "less_than", "equals"
        self.threshold = threshold
        self.severity = severity
        self.message_template = message_template
        self.service_name = service_name
        self.enabled = True
        self.last_triggered = None
        self.cooldown_period = timedelta(minutes=5)  # Minimum time between alerts
    
    def evaluate(self, metric: SystemMetric) -> Optional[Alert]:
        """Evaluate metric against this rule"""
        if not self.enabled:
            return None
        
        if not self._matches_pattern(metric.name):
            return None
        
        if not self._check_cooldown():
            return None
        
        if self._condition_met(metric.value):
            self.last_triggered = datetime.now()
            return self._create_alert(metric)
        
        return None
    
    def _matches_pattern(self, metric_name: str) -> bool:
        """Check if metric name matches the pattern"""
        # Simple pattern matching - could be enhanced with regex
        return self.metric_pattern in metric_name or metric_name.startswith(self.metric_pattern)
    
    def _check_cooldown(self) -> bool:
        """Check if cooldown period has passed"""
        if self.last_triggered is None:
            return True
        return datetime.now() - self.last_triggered > self.cooldown_period
    
    def _condition_met(self, value: float) -> bool:
        """Check if the condition is met"""
        if self.condition == "greater_than":
            return value > self.threshold
        elif self.condition == "less_than":
            return value < self.threshold
        elif self.condition == "equals":
            return abs(value - self.threshold) < 0.001
        elif self.condition == "greater_equal":
            return value >= self.threshold
        elif self.condition == "less_equal":
            return value <= self.threshold
        return False
    
    def _create_alert(self, metric: SystemMetric) -> Alert:
        """Create alert from metric"""
        message = self.message_template.format(
            metric_name=metric.name,
            value=metric.value,
            threshold=self.threshold,
            unit=metric.unit
        )
        
        return Alert(
            alert_id=str(uuid.uuid4()),
            severity=self.severity,
            title=f"{metric.name} threshold exceeded",
            message=message,
            timestamp=datetime.now(),
            service_name=self.service_name,
            metric_name=metric.name,
            threshold_value=self.threshold,
            actual_value=metric.value
        )


class AlertManager:
    """Manage alerts and notifications"""
    
    def __init__(self, thresholds: Optional[HealthThresholds] = None):
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.thresholds = thresholds or HealthThresholds()
        self.notification_handlers: List[Callable[[Alert], None]] = []
        self.alert_history: List[Alert] = []
        self.max_history = 1000
        
        # Active alert tracking
        self.active_alerts: Set[str] = set()
        self.alert_counts_by_service: Dict[str, int] = defaultdict(int)
        
        # Setup default alert rules
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default alert rules based on thresholds"""
        # CPU usage alerts
        self.add_alert_rule(
            "cpu_warning",
            "system.cpu.usage",
            "greater_than",
            self.thresholds.cpu_warning,
            "warning",
            "CPU usage {value}% exceeds warning threshold {threshold}%"
        )
        
        self.add_alert_rule(
            "cpu_critical",
            "system.cpu.usage",
            "greater_than",
            self.thresholds.cpu_critical,
            "critical",
            "CPU usage {value}% exceeds critical threshold {threshold}%"
        )
        
        # Memory usage alerts
        self.add_alert_rule(
            "memory_warning",
            "system.memory.percent",
            "greater_than",
            self.thresholds.memory_warning,
            "warning",
            "Memory usage {value}% exceeds warning threshold {threshold}%"
        )
        
        self.add_alert_rule(
            "memory_critical",
            "system.memory.percent",
            "greater_than",
            self.thresholds.memory_critical,
            "critical",
            "Memory usage {value}% exceeds critical threshold {threshold}%"
        )
        
        # Disk usage alerts
        self.add_alert_rule(
            "disk_warning",
            "system.disk.percent",
            "greater_than",
            self.thresholds.disk_warning,
            "warning",
            "Disk usage {value}% exceeds warning threshold {threshold}%"
        )
        
        self.add_alert_rule(
            "disk_critical",
            "system.disk.percent",
            "greater_than",
            self.thresholds.disk_critical,
            "critical",
            "Disk usage {value}% exceeds critical threshold {threshold}%"
        )
    
    def add_alert_rule(self, rule_id: str, metric_pattern: str, condition: str,
                      threshold: float, severity: str, message_template: str,
                      service_name: str = "system"):
        """Add an alert rule"""
        rule = AlertRule(
            rule_id=rule_id,
            metric_pattern=metric_pattern,
            condition=condition,
            threshold=threshold,
            severity=severity,
            message_template=message_template,
            service_name=service_name
        )
        self.alert_rules[rule_id] = rule
        logger.info(f"Added alert rule: {rule_id}")
    
    def remove_alert_rule(self, rule_id: str):
        """Remove an alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")
    
    def evaluate_metric(self, metric: SystemMetric):
        """Evaluate a metric against all alert rules"""
        try:
            for rule in self.alert_rules.values():
                alert = rule.evaluate(metric)
                if alert:
                    self.add_alert(alert)
        except Exception as e:
            logger.error(f"Error evaluating metric {metric.name}: {e}")
    
    def evaluate_health_check(self, health_result: HealthCheckResult):
        """Evaluate a health check result for alerts"""
        try:
            # Check response time
            if health_result.response_time > self.thresholds.response_time_critical:
                alert = Alert(
                    alert_id=str(uuid.uuid4()),
                    severity="critical",
                    title=f"{health_result.service_name} response time critical",
                    message=f"Response time {health_result.response_time}ms exceeds critical threshold {self.thresholds.response_time_critical}ms",
                    timestamp=datetime.now(),
                    service_name=health_result.service_name,
                    metric_name="response_time",
                    threshold_value=self.thresholds.response_time_critical,
                    actual_value=health_result.response_time
                )
                self.add_alert(alert)
            elif health_result.response_time > self.thresholds.response_time_warning:
                alert = Alert(
                    alert_id=str(uuid.uuid4()),
                    severity="warning",
                    title=f"{health_result.service_name} response time warning",
                    message=f"Response time {health_result.response_time}ms exceeds warning threshold {self.thresholds.response_time_warning}ms",
                    timestamp=datetime.now(),
                    service_name=health_result.service_name,
                    metric_name="response_time",
                    threshold_value=self.thresholds.response_time_warning,
                    actual_value=health_result.response_time
                )
                self.add_alert(alert)
            
            # Check if service is unhealthy
            if not health_result.is_healthy():
                alert = Alert(
                    alert_id=str(uuid.uuid4()),
                    severity="error" if health_result.is_critical() else "warning",
                    title=f"{health_result.service_name} health check failed",
                    message=f"Service {health_result.service_name} is {health_result.status.value}: {health_result.message}",
                    timestamp=datetime.now(),
                    service_name=health_result.service_name,
                    metric_name="health_status"
                )
                self.add_alert(alert)
                
        except Exception as e:
            logger.error(f"Error evaluating health check for {health_result.service_name}: {e}")
    
    def add_alert(self, alert: Alert):
        """Add a new alert"""
        try:
            self.alerts[alert.alert_id] = alert
            self.active_alerts.add(alert.alert_id)
            self.alert_counts_by_service[alert.service_name] += 1
            
            # Add to history
            self.alert_history.append(alert)
            if len(self.alert_history) > self.max_history:
                self.alert_history.pop(0)
            
            # Send notifications
            self._send_notifications(alert)
            
            logger.warning(f"Alert created: {alert.title} - {alert.message}")
            
        except Exception as e:
            logger.error(f"Error adding alert: {e}")
    
    def resolve_alert(self, alert_id: str, resolved_at: Optional[datetime] = None):
        """Resolve an alert"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.resolve(resolved_at)
            self.active_alerts.discard(alert_id)
            
            # Send resolution notification
            self._send_resolution_notification(alert)
            
            logger.info(f"Alert resolved: {alert.title}")
    
    def resolve_alerts_for_service(self, service_name: str):
        """Resolve all active alerts for a service"""
        for alert_id, alert in self.alerts.items():
            if alert.service_name == service_name and alert.is_active():
                self.resolve_alert(alert_id)
    
    def add_notification_handler(self, handler: Callable[[Alert], None]):
        """Add a notification handler"""
        self.notification_handlers.append(handler)
    
    def _send_notifications(self, alert: Alert):
        """Send notifications for an alert"""
        for handler in self.notification_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error sending notification: {e}")
    
    def _send_resolution_notification(self, alert: Alert):
        """Send notification for alert resolution"""
        # Could implement specific resolution notification logic
        pass
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return [alert for alert in self.alerts.values() if alert.is_active()]
    
    def get_alerts_by_service(self, service_name: str) -> List[Alert]:
        """Get alerts for a specific service"""
        return [alert for alert in self.alerts.values() if alert.service_name == service_name]
    
    def get_alerts_by_severity(self, severity: str) -> List[Alert]:
        """Get alerts by severity level"""
        return [alert for alert in self.alerts.values() if alert.severity == severity and alert.is_active()]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of alert status"""
        active_alerts = self.get_active_alerts()
        
        severity_counts = defaultdict(int)
        for alert in active_alerts:
            severity_counts[alert.severity] += 1
        
        return {
            "total_alerts": len(self.alerts),
            "active_alerts": len(active_alerts),
            "resolved_alerts": len(self.alerts) - len(active_alerts),
            "severity_breakdown": dict(severity_counts),
            "alerts_by_service": dict(self.alert_counts_by_service),
            "alert_rules_count": len(self.alert_rules)
        }
    
    def cleanup_old_alerts(self, max_age_days: int = 7):
        """Clean up old resolved alerts"""
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        alerts_to_remove = []
        for alert_id, alert in self.alerts.items():
            if alert.resolved and alert.resolved_at and alert.resolved_at < cutoff_date:
                alerts_to_remove.append(alert_id)
        
        for alert_id in alerts_to_remove:
            del self.alerts[alert_id]
        
        logger.info(f"Cleaned up {len(alerts_to_remove)} old alerts")
    
    def disable_rule(self, rule_id: str):
        """Disable an alert rule"""
        if rule_id in self.alert_rules:
            self.alert_rules[rule_id].enabled = False
            logger.info(f"Disabled alert rule: {rule_id}")
    
    def enable_rule(self, rule_id: str):
        """Enable an alert rule"""
        if rule_id in self.alert_rules:
            self.alert_rules[rule_id].enabled = True
            logger.info(f"Enabled alert rule: {rule_id}")
    
    def update_thresholds(self, new_thresholds: HealthThresholds):
        """Update health thresholds and recreate default rules"""
        self.thresholds = new_thresholds
        
        # Remove old default rules
        default_rules = ["cpu_warning", "cpu_critical", "memory_warning", 
                        "memory_critical", "disk_warning", "disk_critical"]
        for rule_id in default_rules:
            self.remove_alert_rule(rule_id)
        
        # Recreate with new thresholds
        self._setup_default_rules()
        
        logger.info("Updated alert thresholds and rules")


# Default notification handlers
def console_notification_handler(alert: Alert):
    """Simple console notification handler"""
    severity_emoji = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "critical": "🚨"
    }
    
    emoji = severity_emoji.get(alert.severity, "📢")
    print(f"{emoji} [{alert.severity.upper()}] {alert.title}")
    print(f"   Service: {alert.service_name}")
    print(f"   Message: {alert.message}")
    print(f"   Time: {alert.timestamp}")


def log_notification_handler(alert: Alert):
    """Log-based notification handler"""
    log_level = {
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }.get(alert.severity, logging.INFO)
    
    logger.log(log_level, f"ALERT [{alert.severity}] {alert.title} - {alert.message}")


async def webhook_notification_handler(alert: Alert, webhook_url: str):
    """Webhook notification handler (async)"""
    import aiohttp
    
    payload = {
        "alert_id": alert.alert_id,
        "severity": alert.severity,
        "title": alert.title,
        "message": alert.message,
        "service_name": alert.service_name,
        "timestamp": alert.timestamp.isoformat()
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status == 200:
                    logger.info(f"Webhook notification sent for alert {alert.alert_id}")
                else:
                    logger.error(f"Webhook notification failed: {response.status}")
    except Exception as e:
        logger.error(f"Error sending webhook notification: {e}")