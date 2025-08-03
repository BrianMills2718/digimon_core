"""
Execution Monitor - Pipeline Visibility and Debugging Tools

Addresses PRIORITY ISSUE 3.2: Create execution monitor for pipeline visibility.
This fixes the execution monitoring gaps identified in the Gemini AI findings.

Key Features:
- Step-by-step execution tracking
- Performance profiling
- Real-time monitoring dashboard
- Pipeline visibility
- Debugging tools for production use

This addresses the Gemini AI finding: "Resource sharing bottlenecks and execution monitoring gaps"
"""

import time
import threading
import logging
import json
import uuid
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from contextlib import contextmanager
from collections import defaultdict, deque
from enum import Enum
import weakref

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)

class ExecutionStatus(Enum):
    """Execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ExecutionPriority(Enum):
    """Execution priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ExecutionStep:
    """Individual execution step tracking"""
    step_id: str
    step_name: str
    tool_id: Optional[str]
    operation: str
    status: ExecutionStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    memory_start: Optional[int] = None
    memory_end: Optional[int] = None
    memory_peak: Optional[int] = None
    input_size: Optional[int] = None
    output_size: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    parent_execution_id: Optional[str] = None

@dataclass
class ExecutionTrace:
    """Complete execution trace for a pipeline"""
    execution_id: str
    pipeline_name: str
    pipeline_type: str
    status: ExecutionStatus
    priority: ExecutionPriority
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: Optional[float] = None
    steps: List[ExecutionStep] = None
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    total_memory_used: Optional[int] = None
    peak_memory: Optional[int] = None
    error_summary: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []

class ExecutionMonitor:
    """
    Execution monitor for comprehensive pipeline visibility and debugging.
    
    Provides step-by-step execution tracking, performance profiling, and real-time
    monitoring capabilities for production debugging and optimization.
    """
    
    def __init__(self, max_traces: int = 1000, enable_realtime: bool = True):
        self.max_traces = max_traces
        self.enable_realtime = enable_realtime
        
        # Thread-safe storage
        self._traces: Dict[str, ExecutionTrace] = {}
        self._active_executions: Dict[str, ExecutionTrace] = {}
        self._traces_lock = threading.RLock()
        
        # Performance monitoring
        self._performance_stats = defaultdict(list)
        self._step_timings = defaultdict(deque)
        self._memory_snapshots = deque(maxlen=1000)
        
        # Real-time monitoring
        self._realtime_listeners = []
        self._monitoring_thread = None
        self._monitoring_active = False
        
        # Statistics
        self._total_executions = 0
        self._total_steps = 0
        self._total_errors = 0
        
        logger.info(f"ExecutionMonitor initialized (max_traces={max_traces}, realtime={enable_realtime})")
        
        if enable_realtime:
            self._start_realtime_monitoring()
    
    def _start_realtime_monitoring(self):
        """Start real-time monitoring thread"""
        if not self._monitoring_active:
            self._monitoring_active = True
            self._monitoring_thread = threading.Thread(target=self._monitoring_worker, daemon=True)
            self._monitoring_thread.start()
            logger.info("Real-time execution monitoring started")
    
    def _monitoring_worker(self):
        """Background worker for real-time monitoring"""
        while self._monitoring_active:
            try:
                # Capture memory snapshot if available
                if PSUTIL_AVAILABLE:
                    memory_info = psutil.virtual_memory()
                    self._memory_snapshots.append({
                        "timestamp": datetime.now(),
                        "memory_percent": memory_info.percent,
                        "memory_available": memory_info.available,
                        "memory_used": memory_info.used
                    })
                
                # Check for stalled executions
                self._check_stalled_executions()
                
                # Notify real-time listeners
                self._notify_realtime_listeners()
                
                time.sleep(1.0)  # Monitor every second
                
            except Exception as e:
                logger.error(f"Error in execution monitoring worker: {e}")
                time.sleep(5.0)  # Wait longer on error
    
    def _check_stalled_executions(self):
        """Check for executions that may be stalled"""
        stall_threshold = timedelta(minutes=10)  # 10 minute threshold
        current_time = datetime.now()
        
        with self._traces_lock:
            for execution_id, trace in self._active_executions.items():
                if trace.status == ExecutionStatus.RUNNING:
                    # Check if any step has been running too long
                    for step in trace.steps:
                        if (step.status == ExecutionStatus.RUNNING and 
                            step.start_time and 
                            (current_time - step.start_time) > stall_threshold):
                            
                            logger.warning(f"Potentially stalled execution detected: {execution_id}, step: {step.step_name}")
                            self._notify_stalled_execution(execution_id, step)
    
    def _notify_stalled_execution(self, execution_id: str, step: ExecutionStep):
        """Notify about stalled execution"""
        notification = {
            "type": "stalled_execution",
            "execution_id": execution_id,
            "step_id": step.step_id,
            "step_name": step.step_name,
            "duration": (datetime.now() - step.start_time).total_seconds() if step.start_time else 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to all real-time listeners
        for listener in self._realtime_listeners:
            try:
                if callable(listener):
                    listener(notification)
            except Exception as e:
                logger.error(f"Error notifying real-time listener: {e}")
    
    def _notify_realtime_listeners(self):
        """Notify real-time listeners of current status"""
        if not self._realtime_listeners:
            return
        
        status_update = {
            "type": "status_update",
            "timestamp": datetime.now().isoformat(),
            "active_executions": len(self._active_executions),
            "total_executions": self._total_executions,
            "total_steps": self._total_steps,
            "total_errors": self._total_errors,
            "memory_usage": self._get_current_memory_usage()
        }
        
        for listener in self._realtime_listeners[:]:  # Copy to avoid modification during iteration
            try:
                if callable(listener):
                    listener(status_update)
            except Exception as e:
                logger.error(f"Error notifying real-time listener: {e}")
                # Remove broken listeners
                self._realtime_listeners.remove(listener)
    
    def start_execution(self, pipeline_name: str, pipeline_type: str = "unknown", 
                       priority: ExecutionPriority = ExecutionPriority.MEDIUM,
                       metadata: Dict[str, Any] = None) -> str:
        """
        Start tracking a new pipeline execution.
        
        Args:
            pipeline_name: Name of the pipeline being executed
            pipeline_type: Type of pipeline (e.g., "graphrag", "document_processing")
            priority: Execution priority level
            metadata: Additional metadata for the execution
            
        Returns:
            Execution ID for tracking
        """
        execution_id = str(uuid.uuid4())
        
        trace = ExecutionTrace(
            execution_id=execution_id,
            pipeline_name=pipeline_name,
            pipeline_type=pipeline_type,
            status=ExecutionStatus.RUNNING,
            priority=priority,
            start_time=datetime.now(),
            metadata=metadata or {}
        )
        
        with self._traces_lock:
            self._traces[execution_id] = trace
            self._active_executions[execution_id] = trace
            self._total_executions += 1
        
        logger.info(f"Started execution tracking: {pipeline_name} (ID: {execution_id})")
        
        # Notify real-time listeners
        self._notify_execution_started(trace)
        
        return execution_id
    
    def _notify_execution_started(self, trace: ExecutionTrace):
        """Notify listeners about execution start"""
        notification = {
            "type": "execution_started",
            "execution_id": trace.execution_id,
            "pipeline_name": trace.pipeline_name,
            "pipeline_type": trace.pipeline_type,
            "priority": trace.priority.name,
            "timestamp": trace.start_time.isoformat()
        }
        
        for listener in self._realtime_listeners:
            try:
                if callable(listener):
                    listener(notification)
            except Exception as e:
                logger.error(f"Error notifying execution start: {e}")
    
    @contextmanager
    def track_step(self, execution_id: str, step_name: str, tool_id: str = None, 
                   operation: str = "unknown", metadata: Dict[str, Any] = None):
        """
        Context manager to track an individual execution step.
        
        Args:
            execution_id: Execution ID from start_execution
            step_name: Name of the step being executed
            tool_id: Optional tool ID if this is a tool execution
            operation: Operation being performed
            metadata: Additional step metadata
            
        Usage:
            with monitor.track_step(exec_id, "entity_extraction", "T23A", "extract_entities") as step_id:
                # Perform step operations
                pass
        """
        step_id = str(uuid.uuid4())
        step = ExecutionStep(
            step_id=step_id,
            step_name=step_name,
            tool_id=tool_id,
            operation=operation,
            status=ExecutionStatus.RUNNING,
            start_time=datetime.now(),
            metadata=metadata or {},
            parent_execution_id=execution_id
        )
        
        # Capture initial memory if available
        if PSUTIL_AVAILABLE:
            try:
                step.memory_start = psutil.Process().memory_info().rss
            except Exception:
                pass
        
        with self._traces_lock:
            if execution_id in self._traces:
                self._traces[execution_id].steps.append(step)
                self._traces[execution_id].total_steps += 1
                self._total_steps += 1
        
        logger.debug(f"Started step: {step_name} (ID: {step_id}, Execution: {execution_id})")
        
        try:
            yield step_id
            
            # Step completed successfully
            step.status = ExecutionStatus.COMPLETED
            step.end_time = datetime.now()
            step.duration = (step.end_time - step.start_time).total_seconds()
            
            with self._traces_lock:
                if execution_id in self._traces:
                    self._traces[execution_id].completed_steps += 1
            
            logger.debug(f"Completed step: {step_name} in {step.duration:.3f}s")
            
        except Exception as e:
            # Step failed
            step.status = ExecutionStatus.FAILED
            step.end_time = datetime.now()
            step.duration = (step.end_time - step.start_time).total_seconds() if step.start_time else 0
            step.error_message = str(e)
            
            with self._traces_lock:
                if execution_id in self._traces:
                    self._traces[execution_id].failed_steps += 1
                self._total_errors += 1
            
            logger.error(f"Failed step: {step_name} - {e}")
            raise
            
        finally:
            # Capture final memory if available
            if PSUTIL_AVAILABLE:
                try:
                    step.memory_end = psutil.Process().memory_info().rss
                    if step.memory_start:
                        step.memory_peak = max(step.memory_start, step.memory_end)
                except Exception:
                    pass
            
            # Record step timing for performance analysis
            if step.duration:
                self._step_timings[step_name].append(step.duration)
                if len(self._step_timings[step_name]) > 100:  # Keep last 100 timings
                    self._step_timings[step_name].popleft()
            
            # Notify real-time listeners
            self._notify_step_completed(step)
    
    def _notify_step_completed(self, step: ExecutionStep):
        """Notify listeners about step completion"""
        notification = {
            "type": "step_completed",
            "execution_id": step.parent_execution_id,
            "step_id": step.step_id,
            "step_name": step.step_name,
            "tool_id": step.tool_id,
            "status": step.status.value,
            "duration": step.duration,
            "error_message": step.error_message,
            "timestamp": datetime.now().isoformat()
        }
        
        for listener in self._realtime_listeners:
            try:
                if callable(listener):
                    listener(notification)
            except Exception as e:
                logger.error(f"Error notifying step completion: {e}")
    
    def complete_execution(self, execution_id: str, status: ExecutionStatus = ExecutionStatus.COMPLETED,
                          error_summary: str = None, metadata: Dict[str, Any] = None):
        """
        Complete an execution trace.
        
        Args:
            execution_id: Execution ID to complete
            status: Final execution status
            error_summary: Summary of any errors that occurred
            metadata: Additional completion metadata
        """
        with self._traces_lock:
            if execution_id not in self._traces:
                logger.warning(f"Execution ID not found: {execution_id}")
                return
            
            trace = self._traces[execution_id]
            trace.status = status
            trace.end_time = datetime.now()
            trace.total_duration = (trace.end_time - trace.start_time).total_seconds()
            trace.error_summary = error_summary
            
            if metadata:
                trace.metadata.update(metadata)
            
            # Calculate memory usage
            total_memory = 0
            peak_memory = 0
            for step in trace.steps:
                if step.memory_start and step.memory_end:
                    memory_used = step.memory_end - step.memory_start
                    total_memory += memory_used
                if step.memory_peak:
                    peak_memory = max(peak_memory, step.memory_peak)
            
            trace.total_memory_used = total_memory if total_memory > 0 else None
            trace.peak_memory = peak_memory if peak_memory > 0 else None
            
            # Remove from active executions
            if execution_id in self._active_executions:
                del self._active_executions[execution_id]
            
            # Cleanup old traces if needed
            self._cleanup_old_traces()
        
        logger.info(f"Completed execution: {trace.pipeline_name} in {trace.total_duration:.3f}s (Status: {status.value})")
        
        # Notify real-time listeners
        self._notify_execution_completed(trace)
    
    def _notify_execution_completed(self, trace: ExecutionTrace):
        """Notify listeners about execution completion"""
        notification = {
            "type": "execution_completed",
            "execution_id": trace.execution_id,
            "pipeline_name": trace.pipeline_name,
            "status": trace.status.value,
            "duration": trace.total_duration,
            "total_steps": trace.total_steps,
            "completed_steps": trace.completed_steps,
            "failed_steps": trace.failed_steps,
            "error_summary": trace.error_summary,
            "timestamp": trace.end_time.isoformat() if trace.end_time else None
        }
        
        for listener in self._realtime_listeners:
            try:
                if callable(listener):
                    listener(notification)
            except Exception as e:
                logger.error(f"Error notifying execution completion: {e}")
    
    def _cleanup_old_traces(self):
        """Remove old traces to prevent memory buildup"""
        if len(self._traces) <= self.max_traces:
            return
        
        # Sort by completion time and keep the most recent
        sorted_traces = sorted(
            [(tid, trace) for tid, trace in self._traces.items() if trace.status != ExecutionStatus.RUNNING],
            key=lambda x: x[1].end_time or x[1].start_time,
            reverse=True
        )
        
        # Keep only the most recent traces
        traces_to_keep = sorted_traces[:self.max_traces]
        traces_to_remove = set(self._traces.keys()) - {tid for tid, _ in traces_to_keep}
        
        for tid in traces_to_remove:
            if tid not in self._active_executions:  # Don't remove active executions
                del self._traces[tid]
        
        logger.debug(f"Cleaned up {len(traces_to_remove)} old execution traces")
    
    def get_execution_trace(self, execution_id: str) -> Optional[ExecutionTrace]:
        """Get complete execution trace by ID"""
        with self._traces_lock:
            return self._traces.get(execution_id)
    
    def get_active_executions(self) -> List[ExecutionTrace]:
        """Get all currently active executions"""
        with self._traces_lock:
            return list(self._active_executions.values())
    
    def get_recent_executions(self, limit: int = 50) -> List[ExecutionTrace]:
        """Get recent executions ordered by start time"""
        with self._traces_lock:
            traces = sorted(
                self._traces.values(),
                key=lambda x: x.start_time,
                reverse=True
            )
            return traces[:limit]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        with self._traces_lock:
            # Calculate step timing statistics
            step_stats = {}
            for step_name, timings in self._step_timings.items():
                if timings:
                    timings_list = list(timings)
                    step_stats[step_name] = {
                        "count": len(timings_list),
                        "avg_duration": sum(timings_list) / len(timings_list),
                        "min_duration": min(timings_list),
                        "max_duration": max(timings_list),
                        "recent_avg": sum(timings_list[-10:]) / min(10, len(timings_list))
                    }
            
            # Calculate execution statistics
            completed_executions = [t for t in self._traces.values() if t.status == ExecutionStatus.COMPLETED]
            failed_executions = [t for t in self._traces.values() if t.status == ExecutionStatus.FAILED]
            
            execution_stats = {
                "total_executions": self._total_executions,
                "completed_executions": len(completed_executions),
                "failed_executions": len(failed_executions),
                "success_rate": len(completed_executions) / max(1, len(completed_executions) + len(failed_executions)),
                "active_executions": len(self._active_executions),
                "total_steps": self._total_steps,
                "total_errors": self._total_errors
            }
            
            if completed_executions:
                durations = [e.total_duration for e in completed_executions if e.total_duration]
                if durations:
                    execution_stats.update({
                        "avg_execution_time": sum(durations) / len(durations),
                        "min_execution_time": min(durations),
                        "max_execution_time": max(durations)
                    })
            
            # Memory statistics
            memory_stats = {}
            if self._memory_snapshots:
                recent_memory = list(self._memory_snapshots)[-10:]  # Last 10 snapshots
                memory_stats = {
                    "current_memory_percent": recent_memory[-1]["memory_percent"],
                    "avg_memory_percent": sum(m["memory_percent"] for m in recent_memory) / len(recent_memory),
                    "snapshots_count": len(self._memory_snapshots)
                }
            
            return {
                "execution_stats": execution_stats,
                "step_stats": step_stats,
                "memory_stats": memory_stats,
                "monitoring_active": self._monitoring_active,
                "realtime_listeners": len(self._realtime_listeners)
            }
    
    def _get_current_memory_usage(self) -> Optional[float]:
        """Get current memory usage percentage"""
        if PSUTIL_AVAILABLE:
            try:
                return psutil.virtual_memory().percent
            except Exception:
                pass
        return None
    
    def add_realtime_listener(self, listener: Callable[[Dict[str, Any]], None]):
        """Add a real-time monitoring listener"""
        self._realtime_listeners.append(listener)
        logger.info(f"Added real-time listener. Total listeners: {len(self._realtime_listeners)}")
    
    def remove_realtime_listener(self, listener: Callable[[Dict[str, Any]], None]):
        """Remove a real-time monitoring listener"""
        if listener in self._realtime_listeners:
            self._realtime_listeners.remove(listener)
            logger.info(f"Removed real-time listener. Total listeners: {len(self._realtime_listeners)}")
    
    def export_trace(self, execution_id: str, format: str = "json") -> Optional[str]:
        """
        Export execution trace in specified format.
        
        Args:
            execution_id: Execution ID to export
            format: Export format ("json", "csv", "text")
            
        Returns:
            Exported trace data as string
        """
        trace = self.get_execution_trace(execution_id)
        if not trace:
            return None
        
        if format.lower() == "json":
            return json.dumps(asdict(trace), indent=2, default=str)
        elif format.lower() == "text":
            return self._format_trace_text(trace)
        else:
            logger.warning(f"Unsupported export format: {format}")
            return None
    
    def _format_trace_text(self, trace: ExecutionTrace) -> str:
        """Format execution trace as human-readable text"""
        lines = [
            f"Execution Trace: {trace.execution_id}",
            f"Pipeline: {trace.pipeline_name} ({trace.pipeline_type})",
            f"Status: {trace.status.value}",
            f"Duration: {trace.total_duration:.3f}s" if trace.total_duration else "Duration: In Progress",
            f"Steps: {trace.completed_steps}/{trace.total_steps}",
            ""
        ]
        
        if trace.steps:
            lines.append("Step Details:")
            for step in trace.steps:
                duration_str = f"{step.duration:.3f}s" if step.duration else "In Progress"
                status_icon = "✓" if step.status == ExecutionStatus.COMPLETED else "✗" if step.status == ExecutionStatus.FAILED else "⏳"
                lines.append(f"  {status_icon} {step.step_name} ({duration_str})")
                if step.error_message:
                    lines.append(f"    Error: {step.error_message}")
            lines.append("")
        
        if trace.error_summary:
            lines.append(f"Errors: {trace.error_summary}")
        
        return "\n".join(lines)
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on execution monitor"""
        health_status = {
            "healthy": True,
            "issues": [],
            "checks": {}
        }
        
        # Check monitoring thread
        health_status["checks"]["monitoring_thread_active"] = self._monitoring_active
        if not self._monitoring_active and self.enable_realtime:
            health_status["healthy"] = False
            health_status["issues"].append("Real-time monitoring thread not active")
        
        # Check memory usage
        current_memory = self._get_current_memory_usage()
        if current_memory:
            health_status["checks"]["memory_usage_percent"] = current_memory
            if current_memory > 90:
                health_status["healthy"] = False
                health_status["issues"].append(f"High memory usage: {current_memory:.1f}%")
        
        # Check for stalled executions
        stalled_count = 0
        with self._traces_lock:
            for trace in self._active_executions.values():
                if trace.start_time and (datetime.now() - trace.start_time) > timedelta(hours=1):
                    stalled_count += 1
        
        health_status["checks"]["stalled_executions"] = stalled_count
        if stalled_count > 0:
            health_status["issues"].append(f"{stalled_count} potentially stalled executions")
        
        # Check trace storage
        health_status["checks"]["trace_count"] = len(self._traces)
        health_status["checks"]["active_executions"] = len(self._active_executions)
        
        return health_status
    
    def shutdown(self):
        """Shutdown execution monitor and cleanup resources"""
        logger.info("Shutting down ExecutionMonitor")
        
        # Stop monitoring thread
        self._monitoring_active = False
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5)
        
        # Clear listeners
        self._realtime_listeners.clear()
        
        # Final cleanup
        with self._traces_lock:
            active_count = len(self._active_executions)
            if active_count > 0:
                logger.warning(f"Shutting down with {active_count} active executions")
            
            self._traces.clear()
            self._active_executions.clear()
        
        logger.info("ExecutionMonitor shutdown completed")

# Singleton instance for global access
_execution_monitor_instance: Optional[ExecutionMonitor] = None
_execution_monitor_lock = threading.Lock()

def get_execution_monitor(max_traces: int = 1000, enable_realtime: bool = True) -> ExecutionMonitor:
    """Get singleton ExecutionMonitor instance"""
    global _execution_monitor_instance
    
    if _execution_monitor_instance is None:
        with _execution_monitor_lock:
            if _execution_monitor_instance is None:
                _execution_monitor_instance = ExecutionMonitor(max_traces, enable_realtime)
    
    return _execution_monitor_instance

def shutdown_execution_monitor():
    """Shutdown the global execution monitor instance"""
    global _execution_monitor_instance
    
    if _execution_monitor_instance:
        with _execution_monitor_lock:
            if _execution_monitor_instance:
                _execution_monitor_instance.shutdown()
                _execution_monitor_instance = None