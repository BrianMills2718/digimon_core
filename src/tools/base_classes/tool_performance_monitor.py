"""Tool Performance Monitoring Framework

Monitors performance of all tools to ensure they meet requirements
and provides evidence for optimization decisions.
"""

import time
import psutil
import threading
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
from datetime import datetime
import statistics
import json
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


@dataclass
class ToolPerformanceMetrics:
    """Performance metrics for a single tool execution"""
    tool_id: str
    operation: str
    execution_time: float
    memory_used: int
    cpu_percent: float
    input_size: int
    output_size: int
    accuracy: Optional[float]
    timestamp: str
    success: bool
    error_code: Optional[str] = None


class ToolPerformanceMonitor:
    """Monitor performance of all tools
    
    Tracks execution time, memory usage, CPU usage, and accuracy
    to ensure tools meet performance requirements.
    """
    
    def __init__(self, storage_dir: str = "./data/performance"):
        self.metrics: List[ToolPerformanceMetrics] = []
        self.benchmarks: Dict[str, Dict[str, float]] = {}
        self.performance_requirements: Dict[str, Dict[str, Any]] = {}
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
    
    @contextmanager
    def monitor_tool_execution(self, tool_id: str, operation: str, input_data: Any):
        """Monitor tool execution performance
        
        Context manager that tracks performance metrics during tool execution.
        
        Args:
            tool_id: ID of the tool being monitored
            operation: Operation being performed
            input_data: Input data to the tool
            
        Yields:
            PerformanceContext for setting output data
        """
        process = psutil.Process()
        start_time = time.time()
        start_memory = process.memory_info().rss
        
        # Create context for output tracking
        context = PerformanceContext()
        
        try:
            # Start CPU monitoring
            process.cpu_percent()  # First call to initialize
            
            yield context
            
            # Calculate metrics
            execution_time = time.time() - start_time
            end_memory = process.memory_info().rss
            memory_used = end_memory - start_memory
            cpu_percent = process.cpu_percent()
            
            input_size = self._calculate_data_size(input_data)
            output_size = self._calculate_data_size(context.output_data)
            
            metrics = ToolPerformanceMetrics(
                tool_id=tool_id,
                operation=operation,
                execution_time=execution_time,
                memory_used=memory_used,
                cpu_percent=cpu_percent,
                input_size=input_size,
                output_size=output_size,
                accuracy=context.accuracy,
                timestamp=datetime.now().isoformat(),
                success=context.success,
                error_code=context.error_code
            )
            
            with self._lock:
                self.metrics.append(metrics)
                self._update_benchmarks(metrics)
                self._check_performance_requirements(metrics)
                self._persist_metrics(metrics)
                
        except Exception as e:
            logger.error(f"Performance monitoring error: {e}")
            # Still track failed execution
            metrics = ToolPerformanceMetrics(
                tool_id=tool_id,
                operation=operation,
                execution_time=time.time() - start_time,
                memory_used=0,
                cpu_percent=0,
                input_size=self._calculate_data_size(input_data),
                output_size=0,
                accuracy=None,
                timestamp=datetime.now().isoformat(),
                success=False,
                error_code="MONITORING_ERROR"
            )
            with self._lock:
                self.metrics.append(metrics)
    
    def register_performance_requirements(self, tool_id: str, requirements: Dict[str, Any]):
        """Register performance requirements for a tool
        
        Args:
            tool_id: Tool identifier
            requirements: Dict with max_execution_time, max_memory_mb, min_accuracy
        """
        self.performance_requirements[tool_id] = requirements
        logger.info(f"Registered performance requirements for {tool_id}: {requirements}")
    
    def _check_performance_requirements(self, metrics: ToolPerformanceMetrics):
        """Check if metrics meet performance requirements"""
        requirements = self.performance_requirements.get(metrics.tool_id)
        if not requirements:
            return
        
        violations = []
        
        # Check execution time
        max_time = requirements.get("max_execution_time", float("inf"))
        if metrics.execution_time > max_time:
            violation = f"Execution time {metrics.execution_time:.2f}s exceeds limit {max_time}s"
            violations.append(violation)
            logger.warning(f"{metrics.tool_id}: {violation}")
        
        # Check memory usage
        max_memory_mb = requirements.get("max_memory_mb", float("inf"))
        memory_mb = metrics.memory_used / (1024 * 1024)
        if memory_mb > max_memory_mb:
            violation = f"Memory usage {memory_mb:.2f}MB exceeds limit {max_memory_mb}MB"
            violations.append(violation)
            logger.warning(f"{metrics.tool_id}: {violation}")
        
        # Check accuracy
        min_accuracy = requirements.get("min_accuracy", 0.0)
        if metrics.accuracy is not None and metrics.accuracy < min_accuracy:
            violation = f"Accuracy {metrics.accuracy:.2f} below requirement {min_accuracy}"
            violations.append(violation)
            logger.warning(f"{metrics.tool_id}: {violation}")
        
        # Check CPU usage
        max_cpu = requirements.get("max_cpu_percent", 100.0)
        if metrics.cpu_percent > max_cpu:
            violation = f"CPU usage {metrics.cpu_percent:.1f}% exceeds limit {max_cpu}%"
            violations.append(violation)
            logger.warning(f"{metrics.tool_id}: {violation}")
        
        # Save violations
        if violations:
            self._save_violations(metrics.tool_id, violations, metrics.timestamp)
    
    def _calculate_data_size(self, data: Any) -> int:
        """Calculate approximate size of data in bytes"""
        try:
            if data is None:
                return 0
            elif isinstance(data, (str, bytes)):
                return len(data.encode('utf-8') if isinstance(data, str) else data)
            elif isinstance(data, (list, tuple)):
                return sum(self._calculate_data_size(item) for item in data)
            elif isinstance(data, dict):
                size = sum(self._calculate_data_size(k) + self._calculate_data_size(v) 
                          for k, v in data.items())
                return size
            else:
                # Rough estimate for other types
                return len(str(data).encode('utf-8'))
        except Exception:
            return 0
    
    def _update_benchmarks(self, metrics: ToolPerformanceMetrics):
        """Update running benchmarks for the tool"""
        tool_benchmarks = self.benchmarks.setdefault(metrics.tool_id, {})
        
        # Get recent metrics for this tool (last 100)
        recent_metrics = [m for m in self.metrics[-100:] 
                         if m.tool_id == metrics.tool_id and m.success]
        
        if recent_metrics:
            # Calculate statistics
            exec_times = [m.execution_time for m in recent_metrics]
            memory_usage = [m.memory_used for m in recent_metrics]
            cpu_usage = [m.cpu_percent for m in recent_metrics]
            
            tool_benchmarks.update({
                "avg_execution_time": statistics.mean(exec_times),
                "p95_execution_time": self._percentile(exec_times, 0.95),
                "max_execution_time": max(exec_times),
                "avg_memory_mb": statistics.mean(memory_usage) / (1024 * 1024),
                "max_memory_mb": max(memory_usage) / (1024 * 1024),
                "avg_cpu_percent": statistics.mean(cpu_usage),
                "success_rate": len(recent_metrics) / len([m for m in self.metrics[-100:] 
                                                          if m.tool_id == metrics.tool_id])
            })
            
            if any(m.accuracy is not None for m in recent_metrics):
                accuracies = [m.accuracy for m in recent_metrics if m.accuracy is not None]
                tool_benchmarks["avg_accuracy"] = statistics.mean(accuracies)
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _persist_metrics(self, metrics: ToolPerformanceMetrics):
        """Save metrics to disk for evidence"""
        try:
            # Save individual metric
            metric_file = self.storage_dir / f"{metrics.tool_id}_metrics.jsonl"
            with open(metric_file, 'a') as f:
                f.write(json.dumps(metrics.__dict__) + '\n')
            
            # Update summary
            self._update_summary()
            
        except Exception as e:
            logger.error(f"Failed to persist metrics: {e}")
    
    def _update_summary(self):
        """Update performance summary file"""
        try:
            summary = {
                "last_updated": datetime.now().isoformat(),
                "total_executions": len(self.metrics),
                "tools_monitored": list(self.benchmarks.keys()),
                "benchmarks": self.benchmarks,
                "requirements": self.performance_requirements
            }
            
            summary_file = self.storage_dir / "performance_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to update summary: {e}")
    
    def _save_violations(self, tool_id: str, violations: List[str], timestamp: str):
        """Save performance violations"""
        try:
            violations_file = self.storage_dir / "performance_violations.jsonl"
            violation_record = {
                "tool_id": tool_id,
                "timestamp": timestamp,
                "violations": violations
            }
            with open(violations_file, 'a') as f:
                f.write(json.dumps(violation_record) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to save violations: {e}")
    
    def get_tool_performance_report(self, tool_id: str) -> Dict[str, Any]:
        """Get comprehensive performance report for a tool"""
        tool_metrics = [m for m in self.metrics if m.tool_id == tool_id]
        
        if not tool_metrics:
            return {"error": f"No metrics found for tool {tool_id}"}
        
        successful_metrics = [m for m in tool_metrics if m.success]
        failed_metrics = [m for m in tool_metrics if not m.success]
        
        report = {
            "tool_id": tool_id,
            "total_executions": len(tool_metrics),
            "successful_executions": len(successful_metrics),
            "failed_executions": len(failed_metrics),
            "success_rate": len(successful_metrics) / len(tool_metrics) * 100,
            "benchmarks": self.benchmarks.get(tool_id, {}),
            "requirements": self.performance_requirements.get(tool_id, {}),
            "recent_metrics": [m.__dict__ for m in tool_metrics[-10:]]
        }
        
        # Check requirement compliance
        if tool_id in self.performance_requirements:
            requirements = self.performance_requirements[tool_id]
            benchmarks = self.benchmarks.get(tool_id, {})
            
            compliance = {
                "execution_time": benchmarks.get("avg_execution_time", 0) <= 
                                 requirements.get("max_execution_time", float("inf")),
                "memory_usage": benchmarks.get("avg_memory_mb", 0) <= 
                               requirements.get("max_memory_mb", float("inf")),
                "accuracy": benchmarks.get("avg_accuracy", 1.0) >= 
                           requirements.get("min_accuracy", 0.0)
            }
            report["requirement_compliance"] = compliance
            report["overall_compliant"] = all(compliance.values())
        
        return report
    
    def get_overall_performance_report(self) -> Dict[str, Any]:
        """Get performance report for all tools"""
        return {
            "summary": {
                "total_tools_monitored": len(self.benchmarks),
                "total_executions": len(self.metrics),
                "monitoring_period": {
                    "start": self.metrics[0].timestamp if self.metrics else None,
                    "end": self.metrics[-1].timestamp if self.metrics else None
                }
            },
            "tool_reports": {
                tool_id: self.get_tool_performance_report(tool_id)
                for tool_id in self.benchmarks.keys()
            }
        }


class PerformanceContext:
    """Context for tracking output data and results"""
    
    def __init__(self):
        self.output_data: Any = None
        self.accuracy: Optional[float] = None
        self.success: bool = True
        self.error_code: Optional[str] = None
    
    def set_output(self, data: Any):
        """Set output data for size calculation"""
        self.output_data = data
    
    def set_accuracy(self, accuracy: float):
        """Set accuracy metric if applicable"""
        self.accuracy = accuracy
    
    def set_error(self, error_code: str):
        """Mark execution as failed"""
        self.success = False
        self.error_code = error_code