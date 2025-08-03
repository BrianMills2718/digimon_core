"""
Async Client Performance Monitor

Monitors and tracks performance metrics for async API client operations.
"""

import time
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

from ..logging_config import get_logger


@dataclass
class PerformanceMetric:
    """Individual performance metric record"""
    operation: str
    duration: float
    timestamp: str
    success: bool
    service: str
    additional_data: Dict[str, Any] = None


class AsyncClientPerformanceMonitor:
    """Monitors performance of async API client operations"""
    
    def __init__(self):
        self.logger = get_logger("core.async_performance_monitor")
        self.metrics: List[PerformanceMetric] = []
        self.performance_stats = {
            "total_requests": 0,
            "concurrent_requests": 0,
            "batch_requests": 0,
            "cache_hits": 0,
            "average_response_time": 0.0,
            "total_response_time": 0.0,
            "successful_requests": 0,
            "failed_requests": 0
        }
        
        # Performance thresholds
        self.thresholds = {
            "max_response_time": 10.0,  # 10 seconds
            "max_concurrent_requests": 50,
            "target_cache_hit_rate": 20.0  # 20%
        }
    
    def start_operation(self, operation: str, service: str) -> str:
        """Start tracking an operation"""
        operation_id = f"{operation}_{service}_{int(time.time() * 1000)}"
        self.performance_stats["total_requests"] += 1
        self.performance_stats["concurrent_requests"] += 1
        return operation_id
    
    def end_operation(self, operation_id: str, operation: str, service: str, 
                     success: bool, start_time: float, 
                     additional_data: Dict[str, Any] = None) -> None:
        """End tracking an operation"""
        duration = time.time() - start_time
        
        # Record metric
        metric = PerformanceMetric(
            operation=operation,
            duration=duration,
            timestamp=datetime.now().isoformat(),
            success=success,
            service=service,
            additional_data=additional_data or {}
        )
        self.metrics.append(metric)
        
        # Update stats
        self.performance_stats["concurrent_requests"] -= 1
        self.performance_stats["total_response_time"] += duration
        
        if success:
            self.performance_stats["successful_requests"] += 1
        else:
            self.performance_stats["failed_requests"] += 1
        
        # Update average response time
        if self.performance_stats["total_requests"] > 0:
            self.performance_stats["average_response_time"] = (
                self.performance_stats["total_response_time"] / 
                self.performance_stats["total_requests"]
            )
        
        # Check thresholds
        self._check_performance_thresholds(metric)
    
    def record_cache_hit(self):
        """Record a cache hit"""
        self.performance_stats["cache_hits"] += 1
    
    def record_batch_operation(self, batch_size: int):
        """Record a batch operation"""
        self.performance_stats["batch_requests"] += batch_size
    
    def _check_performance_thresholds(self, metric: PerformanceMetric):
        """Check if performance metric exceeds thresholds"""
        if metric.duration > self.thresholds["max_response_time"]:
            self.logger.warning(
                f"Operation {metric.operation} on {metric.service} exceeded response time threshold: "
                f"{metric.duration:.2f}s (threshold: {self.thresholds['max_response_time']}s)"
            )
        
        if self.performance_stats["concurrent_requests"] > self.thresholds["max_concurrent_requests"]:
            self.logger.warning(
                f"Concurrent requests exceeded threshold: "
                f"{self.performance_stats['concurrent_requests']} "
                f"(threshold: {self.thresholds['max_concurrent_requests']})"
            )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        total_requests = self.performance_stats["total_requests"]
        cache_hit_rate = 0.0
        if total_requests > 0:
            cache_hit_rate = (self.performance_stats["cache_hits"] / total_requests) * 100
        
        success_rate = 0.0
        if total_requests > 0:
            success_rate = (self.performance_stats["successful_requests"] / total_requests) * 100
        
        return {
            **self.performance_stats,
            "cache_hit_rate_percent": cache_hit_rate,
            "success_rate_percent": success_rate,
            "metrics_count": len(self.metrics),
            "performance_thresholds": self.thresholds,
            "threshold_violations": self._count_threshold_violations()
        }
    
    def _count_threshold_violations(self) -> Dict[str, int]:
        """Count threshold violations in recorded metrics"""
        violations = {
            "response_time_violations": 0,
            "concurrent_request_violations": 0
        }
        
        for metric in self.metrics:
            if metric.duration > self.thresholds["max_response_time"]:
                violations["response_time_violations"] += 1
        
        return violations
    
    def get_service_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """Get performance breakdown by service"""
        service_stats = {}
        
        for metric in self.metrics:
            service = metric.service
            if service not in service_stats:
                service_stats[service] = {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "total_duration": 0.0,
                    "average_duration": 0.0,
                    "min_duration": float('inf'),
                    "max_duration": 0.0
                }
            
            stats = service_stats[service]
            stats["total_requests"] += 1
            stats["total_duration"] += metric.duration
            
            if metric.success:
                stats["successful_requests"] += 1
            else:
                stats["failed_requests"] += 1
            
            stats["min_duration"] = min(stats["min_duration"], metric.duration)
            stats["max_duration"] = max(stats["max_duration"], metric.duration)
            
            # Calculate average
            if stats["total_requests"] > 0:
                stats["average_duration"] = stats["total_duration"] / stats["total_requests"]
        
        # Handle case where no metrics exist
        for service, stats in service_stats.items():
            if stats["min_duration"] == float('inf'):
                stats["min_duration"] = 0.0
        
        return service_stats
    
    def reset_metrics(self):
        """Reset all performance metrics"""
        self.metrics.clear()
        self.performance_stats = {
            "total_requests": 0,
            "concurrent_requests": 0,
            "batch_requests": 0,
            "cache_hits": 0,
            "average_response_time": 0.0,
            "total_response_time": 0.0,
            "successful_requests": 0,
            "failed_requests": 0
        }
        self.logger.info("Performance metrics reset")
    
    def set_threshold(self, threshold_name: str, value: float):
        """Update a performance threshold"""
        if threshold_name in self.thresholds:
            old_value = self.thresholds[threshold_name]
            self.thresholds[threshold_name] = value
            self.logger.info(f"Updated threshold {threshold_name}: {old_value} -> {value}")
        else:
            raise ValueError(f"Unknown threshold: {threshold_name}")
