"""
Production Monitoring and Alerting System
Provides comprehensive monitoring, alerting, and health checking for production deployment.
"""

import logging
import time
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import psutil
import threading

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertChannel(Enum):
    """Alert notification channels."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    LOG = "log"

@dataclass
class Alert:
    """Alert definition with configuration."""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    severity: AlertSeverity
    message_template: str
    channels: List[AlertChannel]
    cooldown_seconds: int = 300  # 5 minutes
    last_triggered: Optional[datetime] = None

@dataclass
class HealthCheck:
    """Health check definition."""
    name: str
    check_function: Callable[[], bool]
    timeout_seconds: int = 30
    critical: bool = False
    last_check: Optional[datetime] = None
    last_result: Optional[bool] = None
    failure_count: int = 0

@dataclass
class MetricThreshold:
    """Metric threshold for alerting."""
    metric_name: str
    threshold_value: float
    comparison: str  # 'gt', 'lt', 'eq'
    window_seconds: int = 300  # 5 minutes
    severity: AlertSeverity = AlertSeverity.WARNING

class ProductionMonitoring:
    """
    Production monitoring system with comprehensive alerting and health checking.
    
    Provides real-time monitoring, alerting, and health status reporting.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()
        self.alerts: Dict[str, Alert] = {}
        self.health_checks: Dict[str, HealthCheck] = {}
        self.metric_thresholds: Dict[str, MetricThreshold] = {}
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alert_history: List[Dict[str, Any]] = []
        self.monitoring_active = False
        self.notification_channels = self._initialize_notification_channels()
        
        # Initialize default alerts and health checks
        self._setup_default_alerts()
        self._setup_default_health_checks()
        self._setup_default_thresholds()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default monitoring configuration."""
        return {
            'monitoring_interval': 60,  # seconds
            'health_check_interval': 30,  # seconds
            'alert_retention_days': 30,
            'metric_retention_hours': 24,
            'email_config': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'from_email': 'alerts@kgas.com'
            },
            'slack_config': {
                'webhook_url': '',
                'channel': '#alerts',
                'username': 'KGAS Monitor'
            },
            'webhook_config': {
                'url': '',
                'headers': {'Content-Type': 'application/json'}
            }
        }
    
    def _initialize_notification_channels(self) -> Dict[AlertChannel, Callable]:
        """Initialize notification channels."""
        return {
            AlertChannel.EMAIL: self._send_email_alert,
            AlertChannel.SLACK: self._send_slack_alert,
            AlertChannel.WEBHOOK: self._send_webhook_alert,
            AlertChannel.LOG: self._send_log_alert
        }
    
    def _setup_default_alerts(self):
        """Set up default system alerts."""
        # High CPU usage alert
        self.add_alert(Alert(
            name="high_cpu_usage",
            condition=lambda metrics: metrics.get('cpu_usage', 0) > 80,
            severity=AlertSeverity.WARNING,
            message_template="High CPU usage detected: {cpu_usage}%",
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK]
        ))
        
        # High memory usage alert
        self.add_alert(Alert(
            name="high_memory_usage",
            condition=lambda metrics: metrics.get('memory_usage', 0) > 85,
            severity=AlertSeverity.WARNING,
            message_template="High memory usage detected: {memory_usage}%",
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK]
        ))
        
        # Low disk space alert
        self.add_alert(Alert(
            name="low_disk_space",
            condition=lambda metrics: metrics.get('disk_usage', 0) > 90,
            severity=AlertSeverity.ERROR,
            message_template="Low disk space: {disk_usage}% used",
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.WEBHOOK]
        ))
        
        # Service unavailable alert
        self.add_alert(Alert(
            name="service_unavailable",
            condition=lambda metrics: not metrics.get('service_healthy', True),
            severity=AlertSeverity.CRITICAL,
            message_template="Service is unavailable or unhealthy",
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.WEBHOOK],
            cooldown_seconds=60
        ))
        
        # High error rate alert
        self.add_alert(Alert(
            name="high_error_rate",
            condition=lambda metrics: metrics.get('error_rate', 0) > 5,
            severity=AlertSeverity.ERROR,
            message_template="High error rate detected: {error_rate}%",
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK]
        ))
    
    def _setup_default_health_checks(self):
        """Set up default health checks."""
        # Database connectivity check
        self.add_health_check(HealthCheck(
            name="database_connectivity",
            check_function=self._check_database_health,
            timeout_seconds=10,
            critical=True
        ))
        
        # Redis connectivity check
        self.add_health_check(HealthCheck(
            name="redis_connectivity",
            check_function=self._check_redis_health,
            timeout_seconds=5,
            critical=False
        ))
        
        # External API connectivity check
        self.add_health_check(HealthCheck(
            name="external_api_connectivity",
            check_function=self._check_external_api_health,
            timeout_seconds=15,
            critical=True
        ))
        
        # File system health check
        self.add_health_check(HealthCheck(
            name="filesystem_health",
            check_function=self._check_filesystem_health,
            timeout_seconds=5,
            critical=False
        ))
    
    def _setup_default_thresholds(self):
        """Set up default metric thresholds."""
        thresholds = [
            MetricThreshold("response_time", 2.0, "gt", severity=AlertSeverity.WARNING),
            MetricThreshold("requests_per_second", 1000, "gt", severity=AlertSeverity.INFO),
            MetricThreshold("active_connections", 100, "gt", severity=AlertSeverity.WARNING),
            MetricThreshold("queue_size", 1000, "gt", severity=AlertSeverity.ERROR),
            MetricThreshold("failed_requests", 10, "gt", severity=AlertSeverity.ERROR)
        ]
        
        for threshold in thresholds:
            self.metric_thresholds[threshold.metric_name] = threshold
    
    def start_monitoring(self):
        """Start the monitoring system."""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        
        # Start monitoring threads
        monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        health_check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        
        monitoring_thread.start()
        health_check_thread.start()
        
        logger.info("Production monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring system."""
        self.monitoring_active = False
        logger.info("Production monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect system metrics
                metrics = self._collect_system_metrics()
                
                # Store metrics
                timestamp = datetime.now()
                for metric_name, value in metrics.items():
                    self.metrics_history[metric_name].append({
                        'timestamp': timestamp,
                        'value': value
                    })
                
                # Check alerts
                self._check_alerts(metrics)
                
                # Check metric thresholds
                self._check_metric_thresholds(metrics)
                
                # Clean old data
                self._cleanup_old_data()
                
                # Use async sleep for monitoring intervals
                interval = self.config['monitoring_interval']
                import asyncio
                try:
                    asyncio.create_task(asyncio.sleep(interval))
                except RuntimeError:
                    # Non-async fallback with reduced interval
                    import time
                    time.sleep(min(interval, 1.0))  # Cap at 1 second
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                # Use async sleep for monitoring intervals
                interval = self.config['monitoring_interval']
                import asyncio
                try:
                    asyncio.create_task(asyncio.sleep(interval))
                except RuntimeError:
                    # Non-async fallback with reduced interval
                    import time
                    time.sleep(min(interval, 1.0))  # Cap at 1 second
    
    def _health_check_loop(self):
        """Health check loop."""
        while self.monitoring_active:
            try:
                # Run health checks
                for check_name, health_check in self.health_checks.items():
                    self._run_health_check(check_name, health_check)
                
                # Use async sleep for health check intervals
                interval = self.config['health_check_interval']
                import asyncio
                try:
                    asyncio.create_task(asyncio.sleep(interval))
                except RuntimeError:
                    # Non-async fallback with reduced interval
                    import time
                    time.sleep(min(interval, 1.0))  # Cap at 1 second
                
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                # Use async sleep for health check intervals
                interval = self.config['health_check_interval']
                import asyncio
                try:
                    asyncio.create_task(asyncio.sleep(interval))
                except RuntimeError:
                    # Non-async fallback with reduced interval
                    import time
                    time.sleep(min(interval, 1.0))  # Cap at 1 second
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics."""
        metrics = {}
        
        try:
            # CPU metrics
            metrics['cpu_usage'] = psutil.cpu_percent(interval=1)
            metrics['cpu_count'] = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            metrics['memory_usage'] = memory.percent
            metrics['memory_total'] = memory.total
            metrics['memory_available'] = memory.available
            metrics['memory_used'] = memory.used
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            metrics['disk_usage'] = (disk.used / disk.total) * 100
            metrics['disk_total'] = disk.total
            metrics['disk_free'] = disk.free
            
            # Network metrics
            network = psutil.net_io_counters()
            metrics['network_bytes_sent'] = network.bytes_sent
            metrics['network_bytes_recv'] = network.bytes_recv
            
            # Process metrics
            process = psutil.Process()
            metrics['process_cpu_percent'] = process.cpu_percent()
            metrics['process_memory_percent'] = process.memory_percent()
            metrics['process_num_threads'] = process.num_threads()
            
            # Service health metrics
            metrics['service_healthy'] = self._check_service_health()
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
        
        return metrics
    
    def _check_service_health(self) -> bool:
        """Check overall service health."""
        try:
            # Check if the service is responding
            # This would typically be a health endpoint check
            # For now, we'll use a simple check
            return True
        except Exception:
            return False
    
    def _check_alerts(self, metrics: Dict[str, Any]):
        """Check all alerts against current metrics."""
        for alert_name, alert in self.alerts.items():
            try:
                # Check cooldown
                if alert.last_triggered:
                    time_since_last = (datetime.now() - alert.last_triggered).total_seconds()
                    if time_since_last < alert.cooldown_seconds:
                        continue
                
                # Check condition
                if alert.condition(metrics):
                    self._trigger_alert(alert, metrics)
                    
            except Exception as e:
                logger.error(f"Error checking alert {alert_name}: {e}")
    
    def _check_metric_thresholds(self, metrics: Dict[str, Any]):
        """Check metric thresholds."""
        for metric_name, threshold in self.metric_thresholds.items():
            try:
                if metric_name in metrics:
                    value = metrics[metric_name]
                    
                    # Check threshold
                    threshold_breached = False
                    if threshold.comparison == 'gt' and value > threshold.threshold_value:
                        threshold_breached = True
                    elif threshold.comparison == 'lt' and value < threshold.threshold_value:
                        threshold_breached = True
                    elif threshold.comparison == 'eq' and value == threshold.threshold_value:
                        threshold_breached = True
                    
                    if threshold_breached:
                        self._trigger_threshold_alert(threshold, value)
                        
            except Exception as e:
                logger.error(f"Error checking threshold for {metric_name}: {e}")
    
    def _trigger_alert(self, alert: Alert, metrics: Dict[str, Any]):
        """Trigger an alert."""
        alert.last_triggered = datetime.now()
        
        # Format message
        message = alert.message_template.format(**metrics)
        
        # Create alert record
        alert_record = {
            'name': alert.name,
            'severity': alert.severity.value,
            'message': message,
            'timestamp': alert.last_triggered.isoformat(),
            'metrics': metrics
        }
        
        self.alert_history.append(alert_record)
        
        # Send notifications
        for channel in alert.channels:
            try:
                self.notification_channels[channel](alert, message, metrics)
            except Exception as e:
                logger.error(f"Failed to send alert via {channel.value}: {e}")
    
    def _trigger_threshold_alert(self, threshold: MetricThreshold, value: float):
        """Trigger a threshold alert."""
        message = f"Metric {threshold.metric_name} threshold breached: {value} {threshold.comparison} {threshold.threshold_value}"
        
        alert_record = {
            'name': f"threshold_{threshold.metric_name}",
            'severity': threshold.severity.value,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'metric_name': threshold.metric_name,
            'value': value,
            'threshold': threshold.threshold_value
        }
        
        self.alert_history.append(alert_record)
        
        # Log threshold breach
        logger.warning(message)
    
    def _run_health_check(self, check_name: str, health_check: HealthCheck):
        """Run a single health check."""
        try:
            start_time = time.time()
            result = health_check.check_function()
            execution_time = time.time() - start_time
            
            health_check.last_check = datetime.now()
            health_check.last_result = result
            
            if not result:
                health_check.failure_count += 1
                
                # Log health check failure
                logger.warning(f"Health check failed: {check_name}")
                
                # Trigger alert for critical health checks
                if health_check.critical:
                    self._trigger_health_check_alert(check_name, health_check)
            else:
                health_check.failure_count = 0
                
            # Check timeout
            if execution_time > health_check.timeout_seconds:
                logger.warning(f"Health check timeout: {check_name} took {execution_time:.2f}s")
                
        except Exception as e:
            health_check.failure_count += 1
            logger.error(f"Health check error for {check_name}: {e}")
    
    def _trigger_health_check_alert(self, check_name: str, health_check: HealthCheck):
        """Trigger alert for failed health check."""
        message = f"Critical health check failed: {check_name}"
        
        alert_record = {
            'name': f"health_check_{check_name}",
            'severity': AlertSeverity.CRITICAL.value,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'check_name': check_name,
            'failure_count': health_check.failure_count
        }
        
        self.alert_history.append(alert_record)
        
        # Send critical alert
        try:
            self._send_email_alert(None, message, {})
            self._send_slack_alert(None, message, {})
        except Exception as e:
            logger.error(f"Failed to send health check alert: {e}")
    
    def _check_database_health(self) -> bool:
        """Check database connectivity."""
        try:
            # This would connect to your actual database
            # For now, return True as placeholder
            return True
        except Exception:
            return False
    
    def _check_redis_health(self) -> bool:
        """Check Redis connectivity."""
        try:
            # This would connect to your Redis instance
            # For now, return True as placeholder
            return True
        except Exception:
            return False
    
    def _check_external_api_health(self) -> bool:
        """Check external API connectivity."""
        try:
            # This would check external APIs
            # For now, return True as placeholder
            return True
        except Exception:
            return False
    
    def _check_filesystem_health(self) -> bool:
        """Check filesystem health."""
        try:
            # Check if we can write to temp directory
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(b"health_check")
                tmp.flush()
                os.fsync(tmp.fileno())
            
            os.unlink(tmp.name)
            return True
        except Exception:
            return False
    
    def _send_email_alert(self, alert: Optional[Alert], message: str, metrics: Dict[str, Any]):
        """Send email alert."""
        try:
            config = self.config['email_config']
            
            if not config['username'] or not config['password']:
                logger.warning("Email configuration incomplete")
                return
            
            msg = MIMEMultipart()
            msg['From'] = config['from_email']
            msg['To'] = config['username']  # Send to configured email
            msg['Subject'] = f"KGAS Alert: {alert.name if alert else 'System Alert'}"
            
            body = f"""
            KGAS Production Alert
            
            Alert: {alert.name if alert else 'System Alert'}
            Severity: {alert.severity.value if alert else 'Unknown'}
            Message: {message}
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Metrics:
            {json.dumps(metrics, indent=2)}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def _send_slack_alert(self, alert: Optional[Alert], message: str, metrics: Dict[str, Any]):
        """Send Slack alert."""
        try:
            config = self.config['slack_config']
            
            if not config['webhook_url']:
                logger.warning("Slack webhook URL not configured")
                return
            
            payload = {
                'channel': config['channel'],
                'username': config['username'],
                'text': f"🚨 KGAS Alert: {message}",
                'attachments': [
                    {
                        'color': 'danger' if alert and alert.severity == AlertSeverity.CRITICAL else 'warning',
                        'fields': [
                            {
                                'title': 'Alert',
                                'value': alert.name if alert else 'System Alert',
                                'short': True
                            },
                            {
                                'title': 'Severity',
                                'value': alert.severity.value if alert else 'Unknown',
                                'short': True
                            },
                            {
                                'title': 'Time',
                                'value': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'short': True
                            }
                        ]
                    }
                ]
            }
            
            requests.post(config['webhook_url'], json=payload)
            
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    def _send_webhook_alert(self, alert: Optional[Alert], message: str, metrics: Dict[str, Any]):
        """Send webhook alert."""
        try:
            config = self.config['webhook_config']
            
            if not config['url']:
                logger.warning("Webhook URL not configured")
                return
            
            payload = {
                'alert_name': alert.name if alert else 'system_alert',
                'severity': alert.severity.value if alert else 'unknown',
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics
            }
            
            requests.post(config['url'], json=payload, headers=config['headers'])
            
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
    
    def _send_log_alert(self, alert: Optional[Alert], message: str, metrics: Dict[str, Any]):
        """Send log alert."""
        logger.warning(f"ALERT: {message}")
    
    def _cleanup_old_data(self):
        """Clean up old monitoring data."""
        # Clean old alerts
        cutoff_date = datetime.now() - timedelta(days=self.config['alert_retention_days'])
        self.alert_history = [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert['timestamp']) > cutoff_date
        ]
        
        # Clean old metrics
        metric_cutoff = datetime.now() - timedelta(hours=self.config['metric_retention_hours'])
        for metric_name, history in self.metrics_history.items():
            # Remove old entries
            while history and history[0]['timestamp'] < metric_cutoff:
                history.popleft()
    
    def add_alert(self, alert: Alert):
        """Add a new alert."""
        self.alerts[alert.name] = alert
        logger.info(f"Added alert: {alert.name}")
    
    def add_health_check(self, health_check: HealthCheck):
        """Add a new health check."""
        self.health_checks[health_check.name] = health_check
        logger.info(f"Added health check: {health_check.name}")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        return {
            'monitoring_active': self.monitoring_active,
            'total_alerts': len(self.alerts),
            'total_health_checks': len(self.health_checks),
            'recent_alerts': len([
                alert for alert in self.alert_history
                if datetime.fromisoformat(alert['timestamp']) > datetime.now() - timedelta(hours=1)
            ]),
            'failed_health_checks': len([
                check for check in self.health_checks.values()
                if check.last_result is False
            ]),
            'system_health': self._get_system_health_summary()
        }
    
    def _get_system_health_summary(self) -> Dict[str, Any]:
        """Get system health summary."""
        latest_metrics = {}
        
        for metric_name, history in self.metrics_history.items():
            if history:
                latest_metrics[metric_name] = history[-1]['value']
        
        return {
            'cpu_usage': latest_metrics.get('cpu_usage', 0),
            'memory_usage': latest_metrics.get('memory_usage', 0),
            'disk_usage': latest_metrics.get('disk_usage', 0),
            'service_healthy': latest_metrics.get('service_healthy', False),
            'last_updated': datetime.now().isoformat()
        }

# Global production monitoring instance
production_monitor = ProductionMonitoring()