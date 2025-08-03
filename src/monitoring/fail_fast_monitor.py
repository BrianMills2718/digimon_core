#!/usr/bin/env python3
"""
Fail-Fast Monitoring System
Tracks and reports when services fail fast without fallback
Provides metrics for production monitoring
"""

import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)

@dataclass
class FailureEvent:
    """Record of a fail-fast event"""
    timestamp: str
    service: str
    operation: str
    error_type: str
    error_message: str
    context: Dict[str, Any] = field(default_factory=dict)
    recovery_time: Optional[float] = None
    
@dataclass
class ServiceMetrics:
    """Metrics for a specific service"""
    total_calls: int = 0
    failed_calls: int = 0
    fail_fast_events: int = 0
    fallback_attempts: int = 0  # Should always be 0 in production
    last_failure: Optional[str] = None
    failure_rate: float = 0.0
    avg_recovery_time: float = 0.0
    
class FailFastMonitor:
    """
    Production monitoring for fail-fast behaviors
    Tracks when services fail without fallback
    """
    
    def __init__(self, 
                 metrics_dir: str = "logs/metrics",
                 alert_threshold: float = 0.1,
                 window_size: int = 100):
        """
        Initialize fail-fast monitor
        
        Args:
            metrics_dir: Directory for metrics storage
            alert_threshold: Failure rate threshold for alerts
            window_size: Size of sliding window for metrics
        """
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        self.alert_threshold = alert_threshold
        self.window_size = window_size
        
        # In-memory metrics
        self.service_metrics: Dict[str, ServiceMetrics] = defaultdict(ServiceMetrics)
        self.failure_events: deque = deque(maxlen=1000)
        self.recent_calls: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Alert callbacks
        self.alert_handlers = []
        
        # Start time
        self.start_time = time.time()
        
        logger.info(f"Fail-fast monitor initialized with threshold={alert_threshold}")
    
    def record_call(self, service: str, operation: str, success: bool, 
                   error: Optional[Exception] = None,
                   context: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a service call
        
        Args:
            service: Service name (e.g., "gemini_api", "neo4j")
            operation: Operation name (e.g., "extract_entities", "query")
            success: Whether the call succeeded
            error: Exception if call failed
            context: Additional context
        """
        with self.lock:
            metrics = self.service_metrics[service]
            metrics.total_calls += 1
            
            # Track in sliding window
            self.recent_calls[service].append(success)
            
            if not success:
                metrics.failed_calls += 1
                metrics.last_failure = datetime.now().isoformat()
                
                # Check if this is a fail-fast event (no fallback attempted)
                if error and not self._is_fallback_error(error):
                    metrics.fail_fast_events += 1
                    
                    # Record failure event
                    event = FailureEvent(
                        timestamp=datetime.now().isoformat(),
                        service=service,
                        operation=operation,
                        error_type=type(error).__name__,
                        error_message=str(error),
                        context=context or {}
                    )
                    self.failure_events.append(event)
                    
                    # Check for alerts
                    self._check_alerts(service, metrics)
                    
                    logger.info(f"Fail-fast event: {service}.{operation} - {type(error).__name__}")
            
            # Update failure rate
            if len(self.recent_calls[service]) > 0:
                metrics.failure_rate = (
                    sum(1 for x in self.recent_calls[service] if not x) / 
                    len(self.recent_calls[service])
                )
    
    def record_fallback_attempt(self, service: str, operation: str) -> None:
        """
        Record a fallback attempt (should not happen in production)
        
        Args:
            service: Service name
            operation: Operation that attempted fallback
        """
        with self.lock:
            metrics = self.service_metrics[service]
            metrics.fallback_attempts += 1
            
            # This should trigger an alert in production
            logger.error(f"⚠️ FALLBACK ATTEMPTED: {service}.{operation} - This violates fail-fast policy!")
            
            # Immediate alert
            self._send_alert(
                service=service,
                alert_type="FALLBACK_VIOLATION",
                message=f"Fallback attempted in {service}.{operation}",
                severity="CRITICAL"
            )
    
    def record_recovery(self, service: str, recovery_time: float) -> None:
        """
        Record service recovery after failure
        
        Args:
            service: Service name
            recovery_time: Time taken to recover (seconds)
        """
        with self.lock:
            metrics = self.service_metrics[service]
            
            # Update average recovery time
            if metrics.avg_recovery_time == 0:
                metrics.avg_recovery_time = recovery_time
            else:
                # Exponential moving average
                metrics.avg_recovery_time = (
                    0.9 * metrics.avg_recovery_time + 0.1 * recovery_time
                )
    
    def _is_fallback_error(self, error: Exception) -> bool:
        """
        Check if error indicates a fallback attempt
        
        Args:
            error: The exception to check
            
        Returns:
            True if this looks like a fallback attempt
        """
        error_str = str(error).lower()
        fallback_indicators = [
            "fallback", "mock", "simulation", "degraded", 
            "simplified", "stub", "dummy"
        ]
        return any(indicator in error_str for indicator in fallback_indicators)
    
    def _check_alerts(self, service: str, metrics: ServiceMetrics) -> None:
        """
        Check if alerts should be triggered
        
        Args:
            service: Service name
            metrics: Current metrics for the service
        """
        # Alert on high failure rate
        if metrics.failure_rate > self.alert_threshold:
            self._send_alert(
                service=service,
                alert_type="HIGH_FAILURE_RATE",
                message=f"Failure rate {metrics.failure_rate:.1%} exceeds threshold {self.alert_threshold:.1%}",
                severity="WARNING"
            )
        
        # Alert on repeated fail-fast events
        recent_events = [
            e for e in self.failure_events 
            if e.service == service and 
            datetime.fromisoformat(e.timestamp) > datetime.now() - timedelta(minutes=5)
        ]
        if len(recent_events) > 10:
            self._send_alert(
                service=service,
                alert_type="REPEATED_FAILURES",
                message=f"{len(recent_events)} failures in last 5 minutes",
                severity="ERROR"
            )
    
    def _send_alert(self, service: str, alert_type: str, 
                   message: str, severity: str) -> None:
        """
        Send an alert
        
        Args:
            service: Service name
            alert_type: Type of alert
            message: Alert message
            severity: Alert severity (INFO, WARNING, ERROR, CRITICAL)
        """
        alert = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "type": alert_type,
            "message": message,
            "severity": severity
        }
        
        # Log the alert
        if severity == "CRITICAL":
            logger.critical(f"🚨 {alert_type}: {message}")
        elif severity == "ERROR":
            logger.error(f"❌ {alert_type}: {message}")
        elif severity == "WARNING":
            logger.warning(f"⚠️ {alert_type}: {message}")
        else:
            logger.info(f"ℹ️ {alert_type}: {message}")
        
        # Call registered handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
        
        # Save to file
        alert_file = self.metrics_dir / f"alerts_{datetime.now():%Y%m%d}.jsonl"
        with open(alert_file, 'a') as f:
            f.write(json.dumps(alert) + '\n')
    
    def register_alert_handler(self, handler) -> None:
        """
        Register a callback for alerts
        
        Args:
            handler: Callback function that receives alert dict
        """
        self.alert_handlers.append(handler)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics
        
        Returns:
            Dictionary of metrics
        """
        with self.lock:
            uptime = time.time() - self.start_time
            
            return {
                "uptime_seconds": uptime,
                "services": {
                    name: asdict(metrics)
                    for name, metrics in self.service_metrics.items()
                },
                "recent_failures": [
                    asdict(event) for event in 
                    list(self.failure_events)[-10:]
                ],
                "policy_violations": {
                    "fallback_attempts": sum(
                        m.fallback_attempts 
                        for m in self.service_metrics.values()
                    )
                }
            }
    
    def save_metrics(self) -> None:
        """Save current metrics to file"""
        metrics = self.get_metrics()
        
        # Save detailed metrics
        metrics_file = self.metrics_dir / f"metrics_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Save summary
        summary_file = self.metrics_dir / "latest_metrics.json"
        with open(summary_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        logger.info(f"Metrics saved to {metrics_file}")
    
    def generate_report(self) -> str:
        """
        Generate a human-readable report
        
        Returns:
            Formatted report string
        """
        metrics = self.get_metrics()
        
        report = []
        report.append("="*60)
        report.append("FAIL-FAST MONITORING REPORT")
        report.append("="*60)
        report.append(f"Uptime: {metrics['uptime_seconds']/3600:.1f} hours")
        report.append("")
        
        # Service metrics
        report.append("Service Metrics:")
        for service, data in metrics['services'].items():
            report.append(f"\n  {service}:")
            report.append(f"    Total calls: {data['total_calls']}")
            report.append(f"    Failed calls: {data['failed_calls']}")
            report.append(f"    Fail-fast events: {data['fail_fast_events']}")
            report.append(f"    Failure rate: {data['failure_rate']:.1%}")
            
            if data['fallback_attempts'] > 0:
                report.append(f"    ⚠️ FALLBACK ATTEMPTS: {data['fallback_attempts']}")
        
        # Policy violations
        violations = metrics['policy_violations']
        if violations['fallback_attempts'] > 0:
            report.append("\n⚠️ POLICY VIOLATIONS:")
            report.append(f"  Fallback attempts: {violations['fallback_attempts']}")
        else:
            report.append("\n✅ No policy violations (no fallback attempts)")
        
        # Recent failures
        if metrics['recent_failures']:
            report.append("\nRecent Failures:")
            for failure in metrics['recent_failures'][-5:]:
                report.append(f"  {failure['timestamp']}: {failure['service']}.{failure['operation']}")
                report.append(f"    Error: {failure['error_type']}")
        
        report.append("="*60)
        
        return "\n".join(report)


# Global monitor instance
_monitor: Optional[FailFastMonitor] = None

def get_monitor() -> FailFastMonitor:
    """Get or create the global monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = FailFastMonitor()
    return _monitor

def record_service_call(service: str, operation: str, success: bool,
                        error: Optional[Exception] = None,
                        context: Optional[Dict[str, Any]] = None) -> None:
    """
    Convenience function to record a service call
    
    Args:
        service: Service name
        operation: Operation name
        success: Whether the call succeeded
        error: Exception if failed
        context: Additional context
    """
    monitor = get_monitor()
    monitor.record_call(service, operation, success, error, context)

def record_fallback_violation(service: str, operation: str) -> None:
    """
    Record a fallback policy violation
    
    Args:
        service: Service name
        operation: Operation that attempted fallback
    """
    monitor = get_monitor()
    monitor.record_fallback_attempt(service, operation)