"""Performance Monitor (<150 lines)

Tracks performance metrics and resource usage during pipeline execution.
Monitors CPU, memory, execution times, and throughput.
"""

from typing import Dict, Any, List, Optional
import time
import psutil
import threading
from collections import deque
from ...logging_config import get_logger

logger = get_logger("core.orchestration.performance_monitor")


class PerformanceMonitor:
    """Monitor performance and resource usage during pipeline execution"""
    
    def __init__(self, sampling_interval: float = 1.0, max_samples: int = 1000):
        self.logger = get_logger("core.orchestration.performance_monitor")
        self.sampling_interval = sampling_interval
        self.max_samples = max_samples
        
        # Performance data
        self.cpu_samples = deque(maxlen=max_samples)
        self.memory_samples = deque(maxlen=max_samples)
        self.tool_metrics = []
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        self.start_time = None
        self.process = psutil.Process()
        
        # Performance thresholds
        self.cpu_threshold = 80.0  # %
        self.memory_threshold = 80.0  # %
        self.execution_time_threshold = 300.0  # seconds
        
    def start_monitoring(self):
        """Start performance monitoring"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.start_time = time.time()
        
        # Start background monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("Performance monitoring started")
        
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
            
        self.logger.info("Performance monitoring stopped")
        
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Sample CPU usage
                cpu_percent = self.process.cpu_percent()
                self.cpu_samples.append({
                    "timestamp": time.time(),
                    "cpu_percent": cpu_percent
                })
                
                # Sample memory usage
                memory_info = self.process.memory_info()
                memory_percent = self.process.memory_percent()
                self.memory_samples.append({
                    "timestamp": time.time(),
                    "memory_rss": memory_info.rss,
                    "memory_vms": memory_info.vms,
                    "memory_percent": memory_percent
                })
                
                # Check thresholds
                self._check_performance_thresholds(cpu_percent, memory_percent)
                
                time.sleep(self.sampling_interval)
                
            except Exception as e:
                self.logger.error(f"Error in performance monitoring loop: {e}")
                time.sleep(self.sampling_interval)
                
    def record_tool_metrics(self, tool_name: str, execution_time: float, 
                          memory_before: int, memory_after: int, result_size: int = 0):
        """Record performance metrics for a specific tool"""
        metrics = {
            "tool_name": tool_name,
            "timestamp": time.time(),
            "execution_time": execution_time,
            "memory_before": memory_before,
            "memory_after": memory_after,
            "memory_delta": memory_after - memory_before,
            "result_size": result_size,
            "throughput": result_size / execution_time if execution_time > 0 else 0
        }
        
        self.tool_metrics.append(metrics)
        
        # Log performance warnings
        if execution_time > self.execution_time_threshold:
            self.logger.warning(f"Tool {tool_name} exceeded execution time threshold: {execution_time:.2f}s")
            
        if metrics["memory_delta"] > 100 * 1024 * 1024:  # 100MB
            self.logger.warning(f"Tool {tool_name} used significant memory: {metrics['memory_delta'] / 1024 / 1024:.1f}MB")
            
    def _check_performance_thresholds(self, cpu_percent: float, memory_percent: float):
        """Check if performance metrics exceed thresholds"""
        if cpu_percent > self.cpu_threshold:
            self.logger.warning(f"High CPU usage detected: {cpu_percent:.1f}%")
            
        if memory_percent > self.memory_threshold:
            self.logger.warning(f"High memory usage detected: {memory_percent:.1f}%")
            
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        if not self.start_time:
            return {"status": "not_started"}
            
        current_time = time.time()
        monitoring_duration = current_time - self.start_time
        
        # Calculate CPU statistics
        cpu_stats = self._calculate_cpu_stats()
        
        # Calculate memory statistics  
        memory_stats = self._calculate_memory_stats()
        
        # Calculate tool performance statistics
        tool_stats = self._calculate_tool_stats()
        
        return {
            "monitoring_duration": monitoring_duration,
            "sampling_interval": self.sampling_interval,
            "total_samples": len(self.cpu_samples),
            "cpu": cpu_stats,
            "memory": memory_stats,
            "tools": tool_stats,
            "system_info": self._get_system_info()
        }
        
    def _calculate_cpu_stats(self) -> Dict[str, Any]:
        """Calculate CPU usage statistics"""
        if not self.cpu_samples:
            return {}
            
        cpu_values = [sample["cpu_percent"] for sample in self.cpu_samples]
        
        return {
            "current": cpu_values[-1] if cpu_values else 0,
            "average": sum(cpu_values) / len(cpu_values),
            "min": min(cpu_values),
            "max": max(cpu_values),
            "samples": len(cpu_values),
            "threshold_exceeded": any(cpu > self.cpu_threshold for cpu in cpu_values)
        }
        
    def _calculate_memory_stats(self) -> Dict[str, Any]:
        """Calculate memory usage statistics"""
        if not self.memory_samples:
            return {}
            
        memory_rss_values = [sample["memory_rss"] for sample in self.memory_samples]
        memory_percent_values = [sample["memory_percent"] for sample in self.memory_samples]
        
        return {
            "current_rss": memory_rss_values[-1] if memory_rss_values else 0,
            "current_percent": memory_percent_values[-1] if memory_percent_values else 0,
            "average_rss": sum(memory_rss_values) / len(memory_rss_values),
            "average_percent": sum(memory_percent_values) / len(memory_percent_values),
            "min_rss": min(memory_rss_values),
            "max_rss": max(memory_rss_values),
            "min_percent": min(memory_percent_values),
            "max_percent": max(memory_percent_values),
            "samples": len(memory_rss_values),
            "threshold_exceeded": any(mem > self.memory_threshold for mem in memory_percent_values)
        }
        
    def _calculate_tool_stats(self) -> Dict[str, Any]:
        """Calculate tool performance statistics"""
        if not self.tool_metrics:
            return {"total_tools": 0}
            
        execution_times = [metric["execution_time"] for metric in self.tool_metrics]
        memory_deltas = [metric["memory_delta"] for metric in self.tool_metrics]
        
        # Find slowest and fastest tools
        slowest_tool = max(self.tool_metrics, key=lambda x: x["execution_time"])
        fastest_tool = min(self.tool_metrics, key=lambda x: x["execution_time"])
        
        return {
            "total_tools": len(self.tool_metrics),
            "total_execution_time": sum(execution_times),
            "average_execution_time": sum(execution_times) / len(execution_times),
            "slowest_tool": {
                "name": slowest_tool["tool_name"],
                "execution_time": slowest_tool["execution_time"]
            },
            "fastest_tool": {
                "name": fastest_tool["tool_name"],
                "execution_time": fastest_tool["execution_time"]
            },
            "total_memory_usage": sum(memory_deltas),
            "average_memory_usage": sum(memory_deltas) / len(memory_deltas)
        }
        
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "cpu_count": psutil.cpu_count(),
            "cpu_count_physical": psutil.cpu_count(logical=False),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "process_id": self.process.pid
        }
        
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics"""
        try:
            cpu_percent = self.process.cpu_percent()
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            return {
                "timestamp": time.time(),
                "cpu_percent": cpu_percent,
                "memory_rss": memory_info.rss,
                "memory_vms": memory_info.vms,
                "memory_percent": memory_percent,
                "monitoring_active": self.monitoring_active
            }
        except Exception as e:
            self.logger.error(f"Error getting real-time metrics: {e}")
            return {"error": str(e)}
            
    def reset(self):
        """Reset performance monitoring data"""
        self.stop_monitoring()
        self.cpu_samples.clear()
        self.memory_samples.clear()
        self.tool_metrics.clear()
        self.start_time = None
        
    def health_check(self) -> bool:
        """Check if performance monitor is healthy"""
        try:
            # Test if we can get current metrics
            self.get_real_time_metrics()
            return True
        except Exception:
            return False