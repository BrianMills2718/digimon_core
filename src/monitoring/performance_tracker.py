"""
Performance tracking for KGAS operations.

Tracks execution times, establishes baselines, and detects degradation.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import json
import aiofiles
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Single performance measurement."""
    operation: str
    start_time: float
    end_time: float
    duration: float
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class PerformanceBaseline:
    """Baseline metrics for an operation."""
    operation: str
    p50: float  # Median
    p75: float  # 75th percentile
    p95: float  # 95th percentile
    p99: float  # 99th percentile
    mean: float
    std_dev: float
    sample_count: int
    established_at: str
    
    def is_degraded(self, duration: float) -> bool:
        """Check if duration indicates degradation."""
        # Degraded if >= 2 standard deviations above mean
        # or > p95 baseline
        return duration > self.p95 or duration >= (self.mean + 2 * self.std_dev)


class PerformanceTracker:
    """
    Tracks operation performance and establishes baselines.
    
    Features:
    - Automatic timing of operations
    - Rolling window metrics
    - Baseline establishment
    - Degradation detection
    - Persistent storage
    """
    
    def __init__(self, 
                 window_size: int = 1000,
                 baseline_samples: int = 100,
                 storage_path: Optional[Path] = None):
        """
        Initialize performance tracker.
        
        Args:
            window_size: Size of rolling window for metrics
            baseline_samples: Samples needed to establish baseline
            storage_path: Path for persistent storage
        """
        self.window_size = window_size
        self.baseline_samples = baseline_samples
        self.storage_path = storage_path or Path("performance_data.json")
        
        # Rolling windows for each operation
        self._metrics: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=window_size)
        )
        
        # Established baselines
        self._baselines: Dict[str, PerformanceBaseline] = {}
        
        # Active timers - maps timer_id to (start_time, operation)
        self._active_timers: Dict[str, Tuple[float, str]] = {}
        
        # Statistics
        self._stats = {
            "total_operations": 0,
            "degraded_operations": 0,
            "baseline_updates": 0
        }
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
        
        # Flag to track if baselines are loaded
        self._baselines_loaded = False
        
    async def _load_baselines(self):
        """Load baselines from storage."""
        try:
            if self.storage_path.exists():
                async with aiofiles.open(self.storage_path, 'r') as f:
                    data = json.loads(await f.read())
                    for op, baseline_data in data.get("baselines", {}).items():
                        self._baselines[op] = PerformanceBaseline(**baseline_data)
                logger.info(f"Loaded {len(self._baselines)} performance baselines")
        except Exception as e:
            logger.error(f"Failed to load baselines: {e}")
    
    async def _save_baselines(self):
        """Save baselines to storage."""
        try:
            data = {
                "baselines": {
                    op: {
                        "operation": b.operation,
                        "p50": b.p50,
                        "p75": b.p75,
                        "p95": b.p95,
                        "p99": b.p99,
                        "mean": b.mean,
                        "std_dev": b.std_dev,
                        "sample_count": b.sample_count,
                        "established_at": b.established_at
                    }
                    for op, b in self._baselines.items()
                },
                "stats": self._stats
            }
            
            async with aiofiles.open(self.storage_path, 'w') as f:
                await f.write(json.dumps(data, indent=2))
                
        except Exception as e:
            logger.error(f"Failed to save baselines: {e}")
    
    async def _ensure_baselines_loaded(self):
        """Ensure baselines are loaded."""
        if not self._baselines_loaded:
            await self._load_baselines()
            self._baselines_loaded = True
    
    async def start_operation(self, operation: str, metadata: Optional[Dict] = None) -> str:
        """
        Start timing an operation.
        
        Args:
            operation: Operation name
            metadata: Optional metadata
            
        Returns:
            Timer ID for this operation
        """
        await self._ensure_baselines_loaded()
        
        timer_id = f"{operation}_{time.time()}_{id(metadata)}"
        
        async with self._lock:
            self._active_timers[timer_id] = (time.perf_counter(), operation)
            
        return timer_id
    
    async def end_operation(self, timer_id: str, success: bool = True) -> float:
        """
        End timing an operation.
        
        Args:
            timer_id: Timer ID from start_operation
            success: Whether operation succeeded
            
        Returns:
            Operation duration in seconds
        """
        async with self._lock:
            timer_data = self._active_timers.pop(timer_id, None)
            if timer_data is None:
                raise ValueError(f"No active timer for {timer_id}")
            
            start_time, operation = timer_data
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            # Record metric
            metric = PerformanceMetric(
                operation=operation,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                success=success
            )
            
            self._metrics[operation].append(metric)
            self._stats["total_operations"] += 1
            
            # Check for degradation
            if operation in self._baselines:
                baseline = self._baselines[operation]
                if baseline.is_degraded(duration):
                    self._stats["degraded_operations"] += 1
                    logger.warning(
                        f"Performance degradation detected for {operation}: "
                        f"{duration:.3f}s (baseline p95: {baseline.p95:.3f}s)"
                    )
            
            # Update baseline if needed
            await self._update_baseline_if_needed(operation)
            
            return duration
    
    async def _update_baseline_if_needed(self, operation: str):
        """Update baseline if enough samples collected."""
        metrics = self._metrics[operation]
        
        # Need enough successful samples
        successful_metrics = [m for m in metrics if m.success]
        if len(successful_metrics) < self.baseline_samples:
            return
            
        # Calculate new baseline
        durations = [m.duration for m in successful_metrics[-self.baseline_samples:]]
        durations.sort()
        
        baseline = PerformanceBaseline(
            operation=operation,
            p50=durations[len(durations) // 2],
            p75=durations[min(int(len(durations) * 0.75), len(durations) - 1)],
            p95=durations[min(int(len(durations) * 0.95), len(durations) - 1)],
            p99=durations[min(int(len(durations) * 0.99), len(durations) - 1)],
            mean=statistics.mean(durations),
            std_dev=statistics.stdev(durations) if len(durations) > 1 else 0.0,
            sample_count=len(durations),
            established_at=datetime.now().isoformat()
        )
        
        # Only update if significantly different or new
        should_update = operation not in self._baselines
        if not should_update and operation in self._baselines:
            old = self._baselines[operation]
            # Update if mean changed by >10%
            should_update = abs(baseline.mean - old.mean) / old.mean > 0.1
        
        if should_update:
            self._baselines[operation] = baseline
            self._stats["baseline_updates"] += 1
            await self._save_baselines()
            logger.info(f"Updated baseline for {operation}: p95={baseline.p95:.3f}s")
    
    def time_operation(self, operation: str):
        """
        Decorator for timing operations.
        
        Usage:
            @tracker.time_operation("process_document")
            async def process_document(doc):
                ...
        """
        def decorator(func: Callable):
            async def async_wrapper(*args, **kwargs):
                timer_id = await self.start_operation(operation)
                try:
                    result = await func(*args, **kwargs)
                    await self.end_operation(timer_id, success=True)
                    return result
                except Exception as e:
                    await self.end_operation(timer_id, success=False)
                    raise
                    
            def sync_wrapper(*args, **kwargs):
                # For sync functions, create a new event loop if needed
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                timer_id = loop.run_until_complete(
                    self.start_operation(operation)
                )
                try:
                    result = func(*args, **kwargs)
                    loop.run_until_complete(
                        self.end_operation(timer_id, success=True)
                    )
                    return result
                except Exception as e:
                    loop.run_until_complete(
                        self.end_operation(timer_id, success=False)
                    )
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator
    
    async def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """Get statistics for a specific operation."""
        async with self._lock:
            metrics = list(self._metrics.get(operation, []))
            if not metrics:
                return {"error": "No metrics for operation"}
            
            recent_durations = [m.duration for m in metrics[-100:] if m.success]
            if not recent_durations:
                return {"error": "No successful operations"}
            
            recent_durations_sorted = sorted(recent_durations)
            stats = {
                "operation": operation,
                "sample_count": len(metrics),
                "success_rate": sum(1 for m in metrics if m.success) / len(metrics),
                "recent_p50": statistics.median(recent_durations),
                "recent_p95": recent_durations_sorted[min(int(len(recent_durations_sorted) * 0.95), len(recent_durations_sorted) - 1)],
                "recent_mean": statistics.mean(recent_durations),
            }
            
            if operation in self._baselines:
                baseline = self._baselines[operation]
                stats["baseline"] = {
                    "p50": baseline.p50,
                    "p95": baseline.p95,
                    "mean": baseline.mean,
                    "sample_count": baseline.sample_count,
                    "established_at": baseline.established_at
                }
                stats["degradation_rate"] = sum(
                    1 for m in metrics[-100:]
                    if m.success and baseline.is_degraded(m.duration)
                ) / min(100, len(metrics))
            
            return stats
    
    async def get_system_summary(self) -> Dict[str, Any]:
        """Get overall system performance summary."""
        async with self._lock:
            summary = {
                "total_operations": self._stats["total_operations"],
                "degraded_operations": self._stats["degraded_operations"],
                "degradation_rate": (
                    self._stats["degraded_operations"] / 
                    max(1, self._stats["total_operations"])
                ),
                "tracked_operations": list(self._metrics.keys()),
                "operations_with_baselines": list(self._baselines.keys()),
                "baseline_updates": self._stats["baseline_updates"]
            }
            
            # Add per-operation summaries
            operation_stats = {}
            for op in self._metrics:
                stats = await self.get_operation_stats(op)
                if "error" not in stats:
                    operation_stats[op] = stats
            
            summary["operations"] = operation_stats
            
            return summary


# Global tracker instance
_global_tracker: Optional[PerformanceTracker] = None


def get_performance_tracker() -> PerformanceTracker:
    """Get or create global performance tracker."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = PerformanceTracker()
    return _global_tracker