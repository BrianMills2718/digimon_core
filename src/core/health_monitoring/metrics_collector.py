"""
System Metrics Collector

Collects and stores system metrics for health monitoring.
"""

import asyncio
import logging
import threading
import time
import psutil
from collections import deque
from datetime import datetime
from typing import Dict, Any, Optional

from .data_models import SystemMetric, MetricType

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collect and store system metrics"""
    
    def __init__(self, max_history=10000):
        self.metrics_history = deque(maxlen=max_history)
        self.current_metrics: Dict[str, SystemMetric] = {}
        self._lock = threading.Lock()
        
        # Background collection task
        self.collection_task = None
        self.collection_interval = 30  # seconds
        self._running = False
        
    async def start_collection(self):
        """Start background metrics collection"""
        if self.collection_task is None:
            self._running = True
            self.collection_task = asyncio.create_task(self._collect_system_metrics())
            logger.info("Started metrics collection")
    
    async def stop_collection(self):
        """Stop background metrics collection"""
        self._running = False
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
            self.collection_task = None
            logger.info("Stopped metrics collection")
    
    async def _collect_system_metrics(self):
        """Background task to collect system metrics"""
        while self._running:
            try:
                await self._collect_cpu_metrics()
                await self._collect_memory_metrics()
                await self._collect_disk_metrics()
                await self._collect_network_metrics()
                await self._collect_process_metrics()
                
                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_cpu_metrics(self):
        """Collect CPU metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.record_metric("system.cpu.usage", cpu_percent, MetricType.GAUGE, unit="%")
            
            cpu_count = psutil.cpu_count()
            self.record_metric("system.cpu.count", cpu_count, MetricType.GAUGE)
            
            # Load averages (Unix-like systems only)
            if hasattr(psutil, 'getloadavg'):
                load_avg = psutil.getloadavg()
                self.record_metric("system.load.1min", load_avg[0], MetricType.GAUGE)
                self.record_metric("system.load.5min", load_avg[1], MetricType.GAUGE)
                self.record_metric("system.load.15min", load_avg[2], MetricType.GAUGE)
            
            # CPU frequency
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                self.record_metric("system.cpu.frequency", cpu_freq.current, MetricType.GAUGE, unit="MHz")
            
        except Exception as e:
            logger.error(f"Error collecting CPU metrics: {e}")
    
    async def _collect_memory_metrics(self):
        """Collect memory metrics"""
        try:
            memory = psutil.virtual_memory()
            self.record_metric("system.memory.total", memory.total, MetricType.GAUGE, unit="bytes")
            self.record_metric("system.memory.available", memory.available, MetricType.GAUGE, unit="bytes")
            self.record_metric("system.memory.used", memory.used, MetricType.GAUGE, unit="bytes")
            self.record_metric("system.memory.percent", memory.percent, MetricType.GAUGE, unit="%")
            
            # Swap memory
            swap = psutil.swap_memory()
            self.record_metric("system.swap.total", swap.total, MetricType.GAUGE, unit="bytes")
            self.record_metric("system.swap.used", swap.used, MetricType.GAUGE, unit="bytes")
            self.record_metric("system.swap.percent", swap.percent, MetricType.GAUGE, unit="%")
            
        except Exception as e:
            logger.error(f"Error collecting memory metrics: {e}")
    
    async def _collect_disk_metrics(self):
        """Collect disk metrics"""
        try:
            # Disk usage for root partition
            disk_usage = psutil.disk_usage('/')
            self.record_metric("system.disk.total", disk_usage.total, MetricType.GAUGE, unit="bytes")
            self.record_metric("system.disk.used", disk_usage.used, MetricType.GAUGE, unit="bytes")
            self.record_metric("system.disk.free", disk_usage.free, MetricType.GAUGE, unit="bytes")
            
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            self.record_metric("system.disk.percent", disk_percent, MetricType.GAUGE, unit="%")
            
            # Disk I/O statistics
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self.record_metric("system.disk.read_bytes", disk_io.read_bytes, MetricType.COUNTER, unit="bytes")
                self.record_metric("system.disk.write_bytes", disk_io.write_bytes, MetricType.COUNTER, unit="bytes")
                self.record_metric("system.disk.read_count", disk_io.read_count, MetricType.COUNTER)
                self.record_metric("system.disk.write_count", disk_io.write_count, MetricType.COUNTER)
            
        except Exception as e:
            logger.error(f"Error collecting disk metrics: {e}")
    
    async def _collect_network_metrics(self):
        """Collect network metrics"""
        try:
            net_io = psutil.net_io_counters()
            if net_io:
                self.record_metric("system.network.bytes_sent", net_io.bytes_sent, MetricType.COUNTER, unit="bytes")
                self.record_metric("system.network.bytes_recv", net_io.bytes_recv, MetricType.COUNTER, unit="bytes")
                self.record_metric("system.network.packets_sent", net_io.packets_sent, MetricType.COUNTER)
                self.record_metric("system.network.packets_recv", net_io.packets_recv, MetricType.COUNTER)
                self.record_metric("system.network.errin", net_io.errin, MetricType.COUNTER)
                self.record_metric("system.network.errout", net_io.errout, MetricType.COUNTER)
                self.record_metric("system.network.dropin", net_io.dropin, MetricType.COUNTER)
                self.record_metric("system.network.dropout", net_io.dropout, MetricType.COUNTER)
            
            # Network connections
            connections = len(psutil.net_connections())
            self.record_metric("system.network.connections", connections, MetricType.GAUGE)
            
        except Exception as e:
            logger.error(f"Error collecting network metrics: {e}")
    
    async def _collect_process_metrics(self):
        """Collect process-specific metrics"""
        try:
            import os
            process = psutil.Process(os.getpid())
            
            # Current process metrics
            memory_info = process.memory_info()
            self.record_metric("process.memory.rss", memory_info.rss, MetricType.GAUGE, unit="bytes")
            self.record_metric("process.memory.vms", memory_info.vms, MetricType.GAUGE, unit="bytes")
            
            cpu_percent = process.cpu_percent()
            self.record_metric("process.cpu.percent", cpu_percent, MetricType.GAUGE, unit="%")
            
            # Thread count
            num_threads = process.num_threads()
            self.record_metric("process.threads", num_threads, MetricType.GAUGE)
            
            # File descriptors (Unix-like systems only)
            if hasattr(process, 'num_fds'):
                num_fds = process.num_fds()
                self.record_metric("process.file_descriptors", num_fds, MetricType.GAUGE)
            
        except Exception as e:
            logger.error(f"Error collecting process metrics: {e}")
    
    def record_metric(self, name: str, value: float, metric_type: MetricType, 
                     unit: str = "", tags: Optional[Dict[str, str]] = None):
        """Record a metric data point"""
        try:
            metric = SystemMetric(
                name=name,
                value=value,
                metric_type=metric_type,
                timestamp=datetime.now(),
                tags=tags or {},
                unit=unit
            )
            
            with self._lock:
                self.current_metrics[name] = metric
                self.metrics_history.append(metric)
            
        except Exception as e:
            logger.error(f"Error recording metric {name}: {e}")
    
    def get_current_metrics(self) -> Dict[str, SystemMetric]:
        """Get current metric values"""
        with self._lock:
            return self.current_metrics.copy()
    
    def get_metric_history(self, metric_name: str, limit: int = 100) -> list[SystemMetric]:
        """Get historical values for a specific metric"""
        with self._lock:
            history = [m for m in self.metrics_history if m.name == metric_name]
            return list(history)[-limit:]
    
    def get_metrics_by_pattern(self, pattern: str) -> Dict[str, SystemMetric]:
        """Get metrics matching a name pattern"""
        with self._lock:
            return {name: metric for name, metric in self.current_metrics.items() 
                   if pattern in name}
    
    def clear_history(self):
        """Clear metric history"""
        with self._lock:
            self.metrics_history.clear()
            logger.info("Cleared metrics history")
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics about collected metrics"""
        with self._lock:
            return {
                "total_metrics": len(self.current_metrics),
                "history_size": len(self.metrics_history),
                "collection_running": self._running,
                "collection_interval": self.collection_interval,
                "metric_types": list(set(m.metric_type.value for m in self.current_metrics.values()))
            }
    
    async def collect_snapshot(self) -> Dict[str, SystemMetric]:
        """Collect a one-time snapshot of all metrics"""
        try:
            await self._collect_cpu_metrics()
            await self._collect_memory_metrics()
            await self._collect_disk_metrics()
            await self._collect_network_metrics()
            await self._collect_process_metrics()
            
            return self.get_current_metrics()
        except Exception as e:
            logger.error(f"Error collecting metrics snapshot: {e}")
            return {}
    
    def record_custom_metric(self, name: str, value: float, metric_type: MetricType,
                           unit: str = "", **tags):
        """Record a custom application metric"""
        self.record_metric(name, value, metric_type, unit, tags)
    
    def increment_counter(self, name: str, value: float = 1.0, **tags):
        """Increment a counter metric"""
        current = self.current_metrics.get(name)
        if current and current.metric_type == MetricType.COUNTER:
            new_value = current.value + value
        else:
            new_value = value
        
        self.record_metric(name, new_value, MetricType.COUNTER, tags=tags)
    
    def set_gauge(self, name: str, value: float, unit: str = "", **tags):
        """Set a gauge metric value"""
        self.record_metric(name, value, MetricType.GAUGE, unit, tags)
    
    def time_operation(self, operation_name: str):
        """Context manager to time an operation"""
        return MetricTimer(self, operation_name)


class MetricTimer:
    """Context manager for timing operations"""
    
    def __init__(self, collector: MetricsCollector, operation_name: str):
        self.collector = collector
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (time.time() - self.start_time) * 1000  # Convert to milliseconds
            self.collector.record_metric(
                f"operation.{self.operation_name}.duration",
                duration,
                MetricType.TIMER,
                unit="ms"
            )