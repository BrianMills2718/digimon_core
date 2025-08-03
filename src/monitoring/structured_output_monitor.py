#!/usr/bin/env python3
"""
Structured Output Monitoring and Validation Framework

Provides comprehensive monitoring for structured LLM output across all system components.
Tracks performance metrics, validation rates, error patterns, and system health.
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque
import threading
from contextlib import contextmanager
import traceback

logger = logging.getLogger(__name__)


@dataclass
class StructuredOutputMetrics:
    """Metrics for a single structured output operation"""
    component: str  # "entity_extraction", "mcp_adapter", "reasoning"
    schema_name: str  # Name of Pydantic schema used
    success: bool
    response_time_ms: float
    model_used: str
    temperature: float
    max_tokens: int
    input_length: int
    output_length: int
    validation_error: Optional[str] = None
    llm_error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    request_id: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validation check"""
    check_name: str
    success: bool
    value: Union[float, int, str, bool]
    threshold: Union[float, int, str, bool]
    message: str
    severity: str  # "info", "warning", "error", "critical"
    timestamp: datetime = field(default_factory=datetime.now)


class StructuredOutputMonitor:
    """
    Central monitoring system for structured output operations.
    
    Tracks all structured LLM calls across the system and provides:
    - Real-time performance metrics
    - Error rate monitoring
    - Validation success tracking
    - Performance degradation alerts
    - Historical trend analysis
    """
    
    def __init__(self, 
                 max_history_size: int = 10000,
                 alert_thresholds: Optional[Dict[str, float]] = None):
        """
        Initialize monitoring system.
        
        Args:
            max_history_size: Maximum number of metrics to keep in memory
            alert_thresholds: Custom alert thresholds for various metrics
        """
        self.max_history_size = max_history_size
        self.metrics_history: deque = deque(maxlen=max_history_size)
        self.validation_history: deque = deque(maxlen=max_history_size)
        
        # Thread-safe access
        self._lock = threading.RLock()
        
        # Alert thresholds
        self.alert_thresholds = alert_thresholds or {
            "success_rate_threshold": 0.95,  # Alert if success rate < 95%
            "avg_response_time_threshold": 5000,  # Alert if avg response > 5s
            "validation_error_rate_threshold": 0.05,  # Alert if validation errors > 5%
            "llm_error_rate_threshold": 0.02,  # Alert if LLM errors > 2%
        }
        
        # Component-specific metrics
        self.component_stats = defaultdict(lambda: {
            "total_requests": 0,
            "successful_requests": 0,
            "validation_failures": 0,
            "llm_failures": 0,
            "total_response_time": 0.0,
            "schema_usage": defaultdict(int)
        })
        
        # Recent performance tracking (last hour)
        self.recent_window = timedelta(hours=1)
        
        logger.info("Structured output monitor initialized")
    
    @contextmanager
    def track_operation(self, 
                       component: str,
                       schema_name: str,
                       model: str = "unknown",
                       temperature: float = 0.05,
                       max_tokens: int = 32000,
                       input_text: str = "",
                       request_id: Optional[str] = None):
        """
        Context manager to track a structured output operation.
        
        Usage:
            with monitor.track_operation("entity_extraction", "EntityExtractionResponse") as tracker:
                result = llm_service.structured_completion(...)
                tracker.set_success(True, result)
        """
        start_time = time.time()
        tracker = OperationTracker(
            component=component,
            schema_name=schema_name,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            input_length=len(input_text),
            request_id=request_id,
            start_time=start_time
        )
        
        try:
            yield tracker
        except Exception as e:
            # Capture any uncaught exceptions
            tracker.set_error(llm_error=str(e))
            raise
        finally:
            # Record the operation
            self.record_operation(tracker.to_metrics())
    
    def record_operation(self, metrics: StructuredOutputMetrics) -> None:
        """Record a completed structured output operation."""
        with self._lock:
            # Add to history
            self.metrics_history.append(metrics)
            
            # Update component stats
            stats = self.component_stats[metrics.component]
            stats["total_requests"] += 1
            stats["total_response_time"] += metrics.response_time_ms
            stats["schema_usage"][metrics.schema_name] += 1
            
            if metrics.success:
                stats["successful_requests"] += 1
            elif metrics.validation_error:
                stats["validation_failures"] += 1
            elif metrics.llm_error:
                stats["llm_failures"] += 1
            
            logger.debug(f"Recorded {metrics.component} operation: {metrics.success}")
    
    def validate_system_health(self) -> List[ValidationResult]:
        """
        Validate overall system health and return any alerts.
        
        Returns:
            List of validation results, with failures indicating issues
        """
        results = []
        
        with self._lock:
            # Get recent metrics (last hour)
            recent_metrics = self._get_recent_metrics()
            
            if not recent_metrics:
                results.append(ValidationResult(
                    check_name="metrics_availability",
                    success=False,
                    value=0,
                    threshold=1,
                    message="No recent structured output metrics available",
                    severity="warning"
                ))
                return results
            
            # Overall success rate
            total_ops = len(recent_metrics)
            successful_ops = sum(1 for m in recent_metrics if m.success)
            success_rate = successful_ops / total_ops if total_ops > 0 else 0.0
            
            results.append(ValidationResult(
                check_name="overall_success_rate",
                success=success_rate >= self.alert_thresholds["success_rate_threshold"],
                value=success_rate,
                threshold=self.alert_thresholds["success_rate_threshold"],
                message=f"Overall success rate: {success_rate:.2%} ({successful_ops}/{total_ops})",
                severity="critical" if success_rate < 0.90 else "warning" if success_rate < 0.95 else "info"
            ))
            
            # Average response time
            response_times = [m.response_time_ms for m in recent_metrics]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
            
            results.append(ValidationResult(
                check_name="avg_response_time",
                success=avg_response_time <= self.alert_thresholds["avg_response_time_threshold"],
                value=avg_response_time,
                threshold=self.alert_thresholds["avg_response_time_threshold"],
                message=f"Average response time: {avg_response_time:.0f}ms",
                severity="warning" if avg_response_time > 3000 else "info"
            ))
            
            # Validation error rate
            validation_errors = sum(1 for m in recent_metrics if m.validation_error)
            validation_error_rate = validation_errors / total_ops if total_ops > 0 else 0.0
            
            results.append(ValidationResult(
                check_name="validation_error_rate",
                success=validation_error_rate <= self.alert_thresholds["validation_error_rate_threshold"],
                value=validation_error_rate,
                threshold=self.alert_thresholds["validation_error_rate_threshold"],
                message=f"Validation error rate: {validation_error_rate:.2%} ({validation_errors}/{total_ops})",
                severity="error" if validation_error_rate > 0.10 else "warning" if validation_error_rate > 0.05 else "info"
            ))
            
            # LLM error rate
            llm_errors = sum(1 for m in recent_metrics if m.llm_error)
            llm_error_rate = llm_errors / total_ops if total_ops > 0 else 0.0
            
            results.append(ValidationResult(
                check_name="llm_error_rate",
                success=llm_error_rate <= self.alert_thresholds["llm_error_rate_threshold"],
                value=llm_error_rate,
                threshold=self.alert_thresholds["llm_error_rate_threshold"],
                message=f"LLM error rate: {llm_error_rate:.2%} ({llm_errors}/{total_ops})",
                severity="error" if llm_error_rate > 0.05 else "warning" if llm_error_rate > 0.02 else "info"
            ))
            
            # Component-specific validation
            for component, recent_component_metrics in self._group_recent_by_component(recent_metrics).items():
                if len(recent_component_metrics) >= 5:  # Only validate if sufficient data
                    component_success_rate = sum(1 for m in recent_component_metrics if m.success) / len(recent_component_metrics)
                    
                    results.append(ValidationResult(
                        check_name=f"{component}_success_rate",
                        success=component_success_rate >= 0.90,  # Component-specific threshold
                        value=component_success_rate,
                        threshold=0.90,
                        message=f"{component} success rate: {component_success_rate:.2%}",
                        severity="error" if component_success_rate < 0.80 else "warning" if component_success_rate < 0.90 else "info"
                    ))
            
            # Record validation results
            for result in results:
                self.validation_history.append(result)
        
        return results
    
    def get_performance_summary(self, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """
        Get comprehensive performance summary.
        
        Args:
            time_window: Time window for analysis (defaults to last hour)
        
        Returns:
            Performance summary dictionary
        """
        time_window = time_window or self.recent_window
        
        with self._lock:
            recent_metrics = self._get_recent_metrics(time_window)
            
            if not recent_metrics:
                return {"error": "No recent metrics available"}
            
            # Overall statistics
            total_ops = len(recent_metrics)
            successful_ops = sum(1 for m in recent_metrics if m.success)
            validation_errors = sum(1 for m in recent_metrics if m.validation_error)
            llm_errors = sum(1 for m in recent_metrics if m.llm_error)
            
            response_times = [m.response_time_ms for m in recent_metrics]
            avg_response_time = sum(response_times) / len(response_times)
            
            # Component breakdown
            component_breakdown = {}
            for component, metrics in self._group_recent_by_component(recent_metrics).items():
                component_successful = sum(1 for m in metrics if m.success)
                component_breakdown[component] = {
                    "total_operations": len(metrics),
                    "success_rate": component_successful / len(metrics),
                    "avg_response_time": sum(m.response_time_ms for m in metrics) / len(metrics),
                    "most_used_schema": max(
                        (m.schema_name for m in metrics),
                        key=lambda x: sum(1 for m in metrics if m.schema_name == x),
                        default="none"
                    )
                }
            
            # Schema usage patterns
            schema_usage = defaultdict(int)
            for metric in recent_metrics:
                schema_usage[metric.schema_name] += 1
            
            return {
                "time_window_hours": time_window.total_seconds() / 3600,
                "overall_stats": {
                    "total_operations": total_ops,
                    "success_rate": successful_ops / total_ops,
                    "validation_error_rate": validation_errors / total_ops,
                    "llm_error_rate": llm_errors / total_ops,
                    "avg_response_time_ms": avg_response_time,
                    "median_response_time_ms": sorted(response_times)[len(response_times) // 2] if response_times else 0,
                    "max_response_time_ms": max(response_times) if response_times else 0
                },
                "component_breakdown": component_breakdown,
                "schema_usage": dict(schema_usage),
                "recent_alerts": [
                    {
                        "check": r.check_name,
                        "success": r.success,
                        "severity": r.severity,
                        "message": r.message
                    }
                    for r in list(self.validation_history)[-10:]  # Last 10 validation results
                    if not r.success
                ]
            }
    
    def _get_recent_metrics(self, time_window: Optional[timedelta] = None) -> List[StructuredOutputMetrics]:
        """Get metrics within the specified time window."""
        time_window = time_window or self.recent_window
        cutoff_time = datetime.now() - time_window
        
        return [
            metric for metric in self.metrics_history
            if metric.timestamp >= cutoff_time
        ]
    
    def _group_recent_by_component(self, metrics: List[StructuredOutputMetrics]) -> Dict[str, List[StructuredOutputMetrics]]:
        """Group metrics by component."""
        grouped = defaultdict(list)
        for metric in metrics:
            grouped[metric.component].append(metric)
        return dict(grouped)
    
    def export_metrics(self, filepath: str, format: str = "json") -> bool:
        """
        Export metrics to file for analysis.
        
        Args:
            filepath: Path to export file
            format: Export format ("json" or "csv")
        
        Returns:
            True if export successful
        """
        try:
            with self._lock:
                if format.lower() == "json":
                    data = {
                        "export_timestamp": datetime.now().isoformat(),
                        "metrics": [
                            {
                                "component": m.component,
                                "schema_name": m.schema_name,
                                "success": m.success,
                                "response_time_ms": m.response_time_ms,
                                "model_used": m.model_used,
                                "temperature": m.temperature,
                                "max_tokens": m.max_tokens,
                                "input_length": m.input_length,
                                "output_length": m.output_length,
                                "validation_error": m.validation_error,
                                "llm_error": m.llm_error,
                                "timestamp": m.timestamp.isoformat(),
                                "request_id": m.request_id
                            }
                            for m in self.metrics_history
                        ],
                        "validation_results": [
                            {
                                "check_name": v.check_name,
                                "success": v.success,
                                "value": v.value,
                                "threshold": v.threshold,
                                "message": v.message,
                                "severity": v.severity,
                                "timestamp": v.timestamp.isoformat()
                            }
                            for v in self.validation_history
                        ]
                    }
                    
                    with open(filepath, 'w') as f:
                        json.dump(data, f, indent=2, default=str)
                        
                elif format.lower() == "csv":
                    import csv
                    with open(filepath, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            "timestamp", "component", "schema_name", "success",
                            "response_time_ms", "model_used", "temperature",
                            "input_length", "output_length", "validation_error",
                            "llm_error", "request_id"
                        ])
                        
                        for m in self.metrics_history:
                            writer.writerow([
                                m.timestamp.isoformat(),
                                m.component,
                                m.schema_name,
                                m.success,
                                m.response_time_ms,
                                m.model_used,
                                m.temperature,
                                m.input_length,
                                m.output_length,
                                m.validation_error or "",
                                m.llm_error or "",
                                m.request_id or ""
                            ])
                else:
                    raise ValueError(f"Unsupported format: {format}")
                
                logger.info(f"Exported {len(self.metrics_history)} metrics to {filepath}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            return False


class OperationTracker:
    """Helper class for tracking a single operation."""
    
    def __init__(self, component: str, schema_name: str, model: str,
                 temperature: float, max_tokens: int, input_length: int,
                 request_id: Optional[str], start_time: float):
        self.component = component
        self.schema_name = schema_name
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.input_length = input_length
        self.request_id = request_id
        self.start_time = start_time
        
        # To be set during operation
        self.success = False
        self.output_length = 0
        self.validation_error: Optional[str] = None
        self.llm_error: Optional[str] = None
    
    def set_success(self, success: bool, output_data: Any = None) -> None:
        """Mark operation as successful."""
        self.success = success
        if output_data and hasattr(output_data, 'model_dump_json'):
            self.output_length = len(output_data.model_dump_json())
        elif output_data:
            self.output_length = len(str(output_data))
    
    def set_validation_error(self, error: str) -> None:
        """Mark operation as having validation error."""
        self.success = False
        self.validation_error = error
    
    def set_llm_error(self, error: str) -> None:
        """Mark operation as having LLM error."""
        self.success = False
        self.llm_error = error
    
    def set_error(self, validation_error: str = None, llm_error: str = None) -> None:
        """Mark operation as failed with specific error."""
        self.success = False
        if validation_error:
            self.validation_error = validation_error
        if llm_error:
            self.llm_error = llm_error
    
    def to_metrics(self) -> StructuredOutputMetrics:
        """Convert tracker to metrics object."""
        response_time_ms = (time.time() - self.start_time) * 1000
        
        return StructuredOutputMetrics(
            component=self.component,
            schema_name=self.schema_name,
            success=self.success,
            response_time_ms=response_time_ms,
            model_used=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            input_length=self.input_length,
            output_length=self.output_length,
            validation_error=self.validation_error,
            llm_error=self.llm_error,
            request_id=self.request_id
        )


# Global monitor instance
_monitor: Optional[StructuredOutputMonitor] = None

def get_monitor() -> StructuredOutputMonitor:
    """Get global monitor instance."""
    global _monitor
    if _monitor is None:
        _monitor = StructuredOutputMonitor()
    return _monitor

def track_structured_output(component: str, schema_name: str, **kwargs):
    """Convenience function for tracking structured output operations."""
    return get_monitor().track_operation(component, schema_name, **kwargs)