"""
Prometheus Metrics Collection System

Provides comprehensive metrics collection for the KGAS system using Prometheus.
Collects performance, usage, and system health metrics for quantitative monitoring.

Features:
- Custom metrics for document processing
- System resource metrics
- API call metrics
- Database operation metrics
- Performance timers
- Error tracking
"""

import time
import psutil
import threading
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from contextlib import contextmanager
from datetime import datetime
import socket
import os

try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server, CollectorRegistry, REGISTRY
    from prometheus_client.core import REGISTRY as DEFAULT_REGISTRY
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Create mock classes for when prometheus_client is not available
    class Counter:
        def __init__(self, *args, **kwargs): pass
        def inc(self, amount=1): pass
        def labels(self, **kwargs): return self
    
    class Histogram:
        def __init__(self, *args, **kwargs): pass
        def observe(self, amount): pass
        def time(self): return MockTimer()
        def labels(self, **kwargs): return self
    
    class Gauge:
        def __init__(self, *args, **kwargs): pass
        def set(self, value): pass
        def inc(self, amount=1): pass
        def dec(self, amount=1): pass
        def labels(self, **kwargs): return self
    
    class Summary:
        def __init__(self, *args, **kwargs): pass
        def observe(self, amount): pass
        def time(self): return MockTimer()
        def labels(self, **kwargs): return self
    
    class MockTimer:
        def __enter__(self): return self
        def __exit__(self, *args): pass
    
    def start_http_server(port, addr='', registry=None):
        pass

from src.core.config_manager import ConfigurationManager
from .logging_config import get_logger


@dataclass
class MetricConfiguration:
    """Configuration for metrics collection"""
    enabled: bool = True
    http_port: int = 8000
    http_addr: str = '0.0.0.0'
    collection_interval: float = 5.0
    system_metrics_enabled: bool = True
    custom_labels: Dict[str, str] = None


class MetricsCollector:
    """Centralized metrics collection system for KGAS"""
    
    def __init__(self, config_manager: ConfigurationManager = None):
        self.config_manager = config_manager or get_config()
        self.logger = get_logger("metrics.collector")
        
        # Get metrics configuration
        metrics_config = self.config_manager.get_system_config().get("metrics", {})
        self.config = MetricConfiguration(
            enabled=metrics_config.get("enabled", True),
            http_port=metrics_config.get("http_port", 8000),
            http_addr=metrics_config.get("http_addr", "0.0.0.0"),
            collection_interval=metrics_config.get("collection_interval", 5.0),
            system_metrics_enabled=metrics_config.get("system_metrics_enabled", True),
            custom_labels=metrics_config.get("custom_labels", {})
        )
        
        # Initialize metrics registry
        self.registry = CollectorRegistry() if PROMETHEUS_AVAILABLE else None
        
        # System state
        self.http_server_started = False
        self.system_metrics_thread = None
        self.shutdown_event = threading.Event()
        
        # Initialize metrics
        self._initialize_metrics()
        
        if self.config.enabled:
            self.logger.info("Metrics collection initialized - Prometheus available: %s", PROMETHEUS_AVAILABLE)
        else:
            self.logger.info("Metrics collection disabled")
    
    def _initialize_metrics(self):
        """Initialize all 41 KGAS-specific metrics."""
        
        # Document Processing Metrics (7 metrics)
        self.documents_processed = Counter('kgas_documents_processed_total', 'Total documents processed', ['document_type', 'status'], registry=self.registry)
        self.document_processing_time = Histogram('kgas_document_processing_duration_seconds', 'Document processing time', ['document_type'], registry=self.registry)
        self.entities_extracted = Counter('kgas_entities_extracted_total', 'Total entities extracted', ['entity_type'], registry=self.registry)
        self.relationships_extracted = Counter('kgas_relationships_extracted_total', 'Total relationships extracted', ['relationship_type'], registry=self.registry)
        self.documents_failed = Counter('kgas_documents_failed_total', 'Total failed documents', ['failure_reason'], registry=self.registry)
        self.document_size_histogram = Histogram('kgas_document_size_bytes', 'Document size distribution', buckets=[1024, 10240, 102400, 1048576, 10485760], registry=self.registry)
        self.processing_queue_size = Gauge('kgas_processing_queue_size', 'Current processing queue size', registry=self.registry)
        
        # API Call Metrics (8 metrics)
        self.api_calls_total = Counter('kgas_api_calls_total', 'Total API calls', ['provider', 'endpoint', 'status'], registry=self.registry)
        self.api_call_duration = Histogram('kgas_api_call_duration_seconds', 'API call duration', ['provider', 'endpoint'], registry=self.registry)
        self.api_errors = Counter('kgas_api_errors_total', 'Total API errors', ['provider', 'error_type'], registry=self.registry)
        self.api_rate_limits = Counter('kgas_api_rate_limits_total', 'Total API rate limit hits', ['provider'], registry=self.registry)
        self.api_retries = Counter('kgas_api_retries_total', 'Total API retries', ['provider', 'reason'], registry=self.registry)
        self.api_response_size = Histogram('kgas_api_response_size_bytes', 'API response size', ['provider'], registry=self.registry)
        self.active_api_connections = Gauge('kgas_active_api_connections', 'Current active API connections', ['provider'], registry=self.registry)
        self.api_quota_remaining = Gauge('kgas_api_quota_remaining', 'Remaining API quota', ['provider'], registry=self.registry)
        
        # Database Operations Metrics (8 metrics)
        self.database_operations = Counter('kgas_database_operations_total', 'Total database operations', ['operation', 'database'], registry=self.registry)
        self.database_query_duration = Histogram('kgas_database_query_duration_seconds', 'Database query duration', ['operation', 'database'], registry=self.registry)
        self.neo4j_nodes_total = Gauge('kgas_neo4j_nodes_total', 'Total Neo4j nodes', ['label'], registry=self.registry)
        self.neo4j_relationships_total = Gauge('kgas_neo4j_relationships_total', 'Total Neo4j relationships', ['type'], registry=self.registry)
        self.database_connections = Gauge('kgas_database_connections_active', 'Active database connections', ['database'], registry=self.registry)
        self.database_errors = Counter('kgas_database_errors_total', 'Database errors', ['database', 'error_type'], registry=self.registry)
        self.database_transaction_duration = Histogram('kgas_database_transaction_duration_seconds', 'Database transaction duration', registry=self.registry)
        self.database_pool_size = Gauge('kgas_database_pool_size', 'Database connection pool size', ['database'], registry=self.registry)
        
        # System Resource Metrics (6 metrics)
        self.cpu_usage = Gauge('kgas_cpu_usage_percent', 'CPU usage percentage', registry=self.registry)
        self.memory_usage = Gauge('kgas_memory_usage_bytes', 'Memory usage in bytes', ['type'], registry=self.registry)
        self.disk_usage = Gauge('kgas_disk_usage_bytes', 'Disk usage in bytes', ['mount_point', 'type'], registry=self.registry)
        self.network_io = Counter('kgas_network_io_bytes_total', 'Network I/O bytes', ['direction'], registry=self.registry)
        self.file_descriptors = Gauge('kgas_file_descriptors_open', 'Open file descriptors', registry=self.registry)
        self.system_load = Gauge('kgas_system_load_average', 'System load average', ['period'], registry=self.registry)
        
        # Workflow and Processing Metrics (6 metrics)
        self.concurrent_operations = Gauge('kgas_concurrent_operations', 'Current concurrent operations', ['operation_type'], registry=self.registry)
        self.queue_size = Gauge('kgas_queue_size', 'Queue size', ['queue_name'], registry=self.registry)
        self.errors_total = Counter('kgas_errors_total', 'Total errors', ['component', 'error_type'], registry=self.registry)
        self.component_health = Gauge('kgas_component_health', 'Component health status', ['component'], registry=self.registry)
        self.workflow_executions = Counter('kgas_workflow_executions_total', 'Total workflow executions', ['workflow_type', 'status'], registry=self.registry)
        self.workflow_duration = Histogram('kgas_workflow_duration_seconds', 'Workflow execution duration', ['workflow_type'], registry=self.registry)
        
        # Performance and Optimization Metrics (6 metrics)
        self.cache_operations = Counter('kgas_cache_operations_total', 'Cache operations', ['operation', 'cache_name', 'result'], registry=self.registry)
        self.cache_hit_ratio = Gauge('kgas_cache_hit_ratio', 'Cache hit ratio', ['cache_name'], registry=self.registry)
        self.backup_operations = Counter('kgas_backup_operations_total', 'Backup operations', ['operation', 'status'], registry=self.registry)
        self.backup_size = Gauge('kgas_backup_size_bytes', 'Backup size in bytes', ['backup_type'], registry=self.registry)
        self.trace_spans = Counter('kgas_trace_spans_total', 'Total trace spans created', ['service', 'operation'], registry=self.registry)
        self.performance_improvement = Gauge('kgas_performance_improvement_percent', 'Performance improvement percentage', ['component'], registry=self.registry)
        
        # Verify metric count
        metric_attributes = [attr for attr in dir(self) if not attr.startswith('_') and hasattr(getattr(self, attr), '_name')]
        metric_count = len(metric_attributes)
        
        self.logger.info(f"Initialized {metric_count} KGAS metrics")
        
        if metric_count != 41:
            from .config_manager import ConfigurationError
from src.core.config_manager import get_config

            raise ConfigurationError(f"Expected 41 metrics, initialized {metric_count}. Metrics: {metric_attributes}")
    
    def start_metrics_server(self):
        """Start the Prometheus metrics HTTP server"""
        if not self.config.enabled or not PROMETHEUS_AVAILABLE:
            self.logger.info("Metrics server not started - disabled or Prometheus unavailable")
            return
        
        if self.http_server_started:
            self.logger.warning("Metrics server already started")
            return
        
        try:
            # Check if port is available
            if self._is_port_in_use(self.config.http_port):
                self.logger.warning("Port %d is already in use, metrics server not started", self.config.http_port)
                return
            
            start_http_server(self.config.http_port, self.config.http_addr, self.registry)
            self.http_server_started = True
            self.logger.info("Metrics server started on %s:%d", self.config.http_addr, self.config.http_port)
            
            # Start system metrics collection
            if self.config.system_metrics_enabled:
                self.start_system_metrics_collection()
                
        except Exception as e:
            self.logger.error("Failed to start metrics server: %s", str(e))
    
    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is already in use"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex(('localhost', port))
                return result == 0
        except Exception:
            return False
    
    def start_system_metrics_collection(self):
        """Start background thread for system metrics collection"""
        if self.system_metrics_thread and self.system_metrics_thread.is_alive():
            return
        
        self.system_metrics_thread = threading.Thread(
            target=self._collect_system_metrics_loop,
            daemon=True
        )
        self.system_metrics_thread.start()
        self.logger.info("System metrics collection started")
    
    def _collect_system_metrics_loop(self):
        """Background loop for collecting system metrics"""
        while not self.shutdown_event.wait(self.config.collection_interval):
            try:
                self._collect_system_metrics()
            except Exception as e:
                self.logger.error("Error collecting system metrics: %s", str(e))
    
    def _collect_system_metrics(self):
        """Collect current system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            self.cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.memory_usage.labels(type='used').set(memory.used)
            self.memory_usage.labels(type='available').set(memory.available)
            self.memory_usage.labels(type='total').set(memory.total)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.disk_usage.labels(type='used').set(disk.used)
            self.disk_usage.labels(type='free').set(disk.free)
            self.disk_usage.labels(type='total').set(disk.total)
            
        except Exception as e:
            self.logger.error("Error collecting system metrics: %s", str(e))
    
    # Metric recording methods
    def record_document_processed(self, component: str, phase: str, operation: str, 
                                 document_type: str = "unknown", processing_time: float = 0.0):
        """Record a document processing event"""
        if not self.config.enabled:
            return
        
        labels = {
            'component': component,
            'phase': phase,
            'operation': operation
        }
        
        self.documents_processed.labels(**labels).inc()
        
        if processing_time > 0:
            self.document_processing_time.labels(**labels, document_type=document_type).observe(processing_time)
    
    def record_entities_extracted(self, component: str, phase: str, operation: str, 
                                 entity_type: str, count: int):
        """Record entities extracted"""
        if not self.config.enabled:
            return
        
        self.entities_extracted.labels(
            component=component,
            phase=phase,
            operation=operation,
            entity_type=entity_type
        ).inc(count)
    
    def record_relationships_extracted(self, component: str, phase: str, operation: str, 
                                     relationship_type: str, count: int):
        """Record relationships extracted"""
        if not self.config.enabled:
            return
        
        self.relationships_extracted.labels(
            component=component,
            phase=phase,
            operation=operation,
            relationship_type=relationship_type
        ).inc(count)
    
    def record_api_call(self, api_provider: str, endpoint: str, status: str, duration: float):
        """Record an API call"""
        if not self.config.enabled:
            return
        
        self.api_calls_total.labels(
            api_provider=api_provider,
            endpoint=endpoint,
            status=status
        ).inc()
        
        self.api_call_duration.labels(
            api_provider=api_provider,
            endpoint=endpoint
        ).observe(duration)
    
    def record_database_operation(self, database_type: str, operation: str, status: str, duration: float):
        """Record a database operation"""
        if not self.config.enabled:
            return
        
        self.database_operations.labels(
            database_type=database_type,
            operation=operation,
            status=status
        ).inc()
        
        self.database_query_duration.labels(
            database_type=database_type,
            operation=operation
        ).observe(duration)
    
    def record_error(self, component: str, error_type: str):
        """Record an error event"""
        if not self.config.enabled:
            return
        
        self.errors_total.labels(
            component=component,
            error_type=error_type
        ).inc()
    
    def set_component_health(self, component: str, healthy: bool):
        """Set component health status"""
        if not self.config.enabled:
            return
        
        self.component_health.labels(component=component).set(1 if healthy else 0)
    
    def record_workflow_execution(self, workflow_type: str, status: str, duration: float):
        """Record a workflow execution"""
        if not self.config.enabled:
            return
        
        self.workflow_executions.labels(
            workflow_type=workflow_type,
            status=status
        ).inc()
        
        self.workflow_duration.labels(workflow_type=workflow_type).observe(duration)
    
    @contextmanager
    def time_operation(self, metric_name: str, **labels):
        """Context manager for timing operations"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            if metric_name == 'document_processing':
                self.document_processing_time.labels(**labels).observe(duration)
            elif metric_name == 'api_call':
                self.api_call_duration.labels(**labels).observe(duration)
            elif metric_name == 'database_query':
                self.database_query_duration.labels(**labels).observe(duration)
            elif metric_name == 'workflow':
                self.workflow_duration.labels(**labels).observe(duration)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary"""
        try:
            # Get current system metrics
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "metrics_enabled": self.config.enabled,
                "prometheus_available": PROMETHEUS_AVAILABLE,
                "http_server_started": self.http_server_started,
                "metrics_endpoint": f"http://{self.config.http_addr}:{self.config.http_port}/metrics" if self.http_server_started else None,
                "system_metrics": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_used_gb": memory.used / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_used_gb": disk.used / (1024**3)
                }
            }
        except Exception as e:
            self.logger.error("Error getting metrics summary: %s", str(e))
            return {"error": str(e)}
    
    def shutdown(self):
        """Shutdown metrics collection"""
        self.shutdown_event.set()
        
        if self.system_metrics_thread and self.system_metrics_thread.is_alive():
            self.system_metrics_thread.join(timeout=5.0)
        
        self.logger.info("Metrics collector shutdown complete")
    
    def verify_metric_count(self) -> Dict[str, Any]:
        """Verify that exactly 41 metrics are implemented."""
        
        metric_objects = []
        for attr_name in dir(self):
            if not attr_name.startswith('_'):
                attr = getattr(self, attr_name)
                if hasattr(attr, '_name') and hasattr(attr, '_type'):
                    metric_objects.append({
                        'name': attr._name,
                        'type': attr._type,
                        'documentation': getattr(attr, '_documentation', ''),
                        'labelnames': getattr(attr, '_labelnames', [])
                    })
        
        verification_result = {
            'total_metrics': len(metric_objects),
            'expected_metrics': 41,
            'verification_passed': len(metric_objects) == 41,
            'metric_details': metric_objects,
            'verification_timestamp': datetime.now().isoformat()
        }
        
        # Log evidence to Evidence.md
        with open('Evidence.md', 'a') as f:
            f.write(f"\n## Metrics Verification Evidence\n")
            f.write(f"**Timestamp**: {verification_result['verification_timestamp']}\n")
            f.write(f"**Total Metrics**: {verification_result['total_metrics']}\n")
            f.write(f"**Expected**: {verification_result['expected_metrics']}\n")
            f.write(f"**Verification Passed**: {verification_result['verification_passed']}\n")
            f.write(f"```json\n{json.dumps(verification_result, indent=2)}\n```\n\n")
        
        return verification_result


# Global metrics collector instance
_metrics_collector = None


def get_metrics_collector(config_manager: ConfigurationManager = None) -> MetricsCollector:
    """Get or create the global metrics collector instance"""
    global _metrics_collector
    
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(config_manager)
    
    return _metrics_collector


def initialize_metrics(config_manager: ConfigurationManager = None) -> MetricsCollector:
    """Initialize and start the metrics collection system"""
    collector = get_metrics_collector(config_manager)
    collector.start_metrics_server()
    return collector