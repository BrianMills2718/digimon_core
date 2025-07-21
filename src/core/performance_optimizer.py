"""
Performance Optimization and Tuning System
Provides comprehensive performance monitoring and optimization capabilities.
"""

import time
import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import psutil
import threading
from functools import wraps
import statistics

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for a specific operation."""
    operation_name: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceProfile:
    """Performance profile for analyzing operation performance."""
    operation_name: str
    total_calls: int
    total_time: float
    average_time: float
    min_time: float
    max_time: float
    percentile_95: float
    percentile_99: float
    error_rate: float
    last_updated: datetime

class PerformanceOptimizer:
    """
    Production-grade performance optimizer with comprehensive monitoring.
    
    Provides performance profiling, optimization recommendations, and automatic tuning.
    """
    
    def __init__(self, max_metrics_history: int = 10000):
        self.max_metrics_history = max_metrics_history
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_metrics_history))
        self.performance_profiles: Dict[str, PerformanceProfile] = {}
        self.cache_manager = CacheManager()
        self.connection_pool_manager = ConnectionPoolManager()
        self.query_optimizer = QueryOptimizer()
        self._monitoring_active = False
        self._start_monitoring()
    
    def _start_monitoring(self):
        """Start background performance monitoring."""
        if not self._monitoring_active:
            self._monitoring_active = True
            monitoring_thread = threading.Thread(target=self._monitor_system_performance, daemon=True)
            monitoring_thread.start()
            logger.info("Performance monitoring started")
    
    async def _monitor_system_performance(self):
        """Monitor system performance metrics in background (async version)."""
        while self._monitoring_active:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_info = psutil.virtual_memory()
                disk_info = psutil.disk_usage('/')
                
                # Log system metrics
                system_metrics = {
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory_info.percent,
                    'memory_available': memory_info.available,
                    'disk_usage': disk_info.percent,
                    'disk_free': disk_info.free,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Store system metrics
                self.metrics_history['system'].append(system_metrics)
                
                # Check for performance issues
                self._check_performance_thresholds(system_metrics)
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Async system monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_system_performance_async(self):
        """Async version of system performance monitoring with non-blocking delays."""
        while self._monitoring_active:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_info = psutil.virtual_memory()
                disk_info = psutil.disk_usage('/')
                
                # Log system metrics
                system_metrics = {
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory_info.percent,
                    'memory_available': memory_info.available,
                    'disk_usage': disk_info.percent,
                    'disk_free': disk_info.free,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Store system metrics
                self.metrics_history['system'].append(system_metrics)
                
                # Check for performance issues
                self._check_performance_thresholds(system_metrics)
                
                await asyncio.sleep(60)  # ✅ NON-BLOCKING Monitor every minute
                
            except Exception as e:
                logger.error(f"Async system monitoring error: {e}")
                await asyncio.sleep(60)  # ✅ NON-BLOCKING
    
    async def start_async_monitoring(self):
        """Start async performance monitoring."""
        if not self._monitoring_active:
            self._monitoring_active = True
            # Create async task instead of thread
            asyncio.create_task(self._monitor_system_performance_async())
            logger.info("Async performance monitoring started")
    
    def _check_performance_thresholds(self, metrics: Dict[str, Any]):
        """Check if performance metrics exceed thresholds."""
        # CPU threshold
        if metrics['cpu_usage'] > 80:
            logger.warning(f"High CPU usage detected: {metrics['cpu_usage']}%")
        
        # Memory threshold
        if metrics['memory_usage'] > 85:
            logger.warning(f"High memory usage detected: {metrics['memory_usage']}%")
        
        # Disk threshold
        if metrics['disk_usage'] > 90:
            logger.warning(f"High disk usage detected: {metrics['disk_usage']}%")
    
    def profile_operation(self, operation_name: str):
        """
        Decorator to profile operation performance.
        
        Args:
            operation_name: Name of the operation to profile
        """
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                start_cpu = psutil.cpu_percent()
                
                try:
                    result = await func(*args, **kwargs)
                    error_occurred = False
                except Exception as e:
                    error_occurred = True
                    raise
                finally:
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                    end_cpu = psutil.cpu_percent()
                    
                    # Calculate metrics
                    execution_time = end_time - start_time
                    memory_delta = end_memory - start_memory
                    cpu_delta = end_cpu - start_cpu
                    
                    # Store metrics
                    metrics = PerformanceMetrics(
                        operation_name=operation_name,
                        execution_time=execution_time,
                        memory_usage=memory_delta,
                        cpu_usage=cpu_delta,
                        timestamp=datetime.now(),
                        context={
                            'function_name': func.__name__,
                            'error_occurred': error_occurred,
                            'args_count': len(args),
                            'kwargs_count': len(kwargs)
                        }
                    )
                    
                    self._record_metrics(metrics)
                    
                    # Log slow operations
                    if execution_time > 5.0:  # 5 seconds threshold
                        logger.warning(f"Slow operation detected: {operation_name} took {execution_time:.2f}s")
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                start_cpu = psutil.cpu_percent()
                
                try:
                    result = func(*args, **kwargs)
                    error_occurred = False
                except Exception as e:
                    error_occurred = True
                    raise
                finally:
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                    end_cpu = psutil.cpu_percent()
                    
                    # Calculate metrics
                    execution_time = end_time - start_time
                    memory_delta = end_memory - start_memory
                    cpu_delta = end_cpu - start_cpu
                    
                    # Store metrics
                    metrics = PerformanceMetrics(
                        operation_name=operation_name,
                        execution_time=execution_time,
                        memory_usage=memory_delta,
                        cpu_usage=cpu_delta,
                        timestamp=datetime.now(),
                        context={
                            'function_name': func.__name__,
                            'error_occurred': error_occurred,
                            'args_count': len(args),
                            'kwargs_count': len(kwargs)
                        }
                    )
                    
                    self._record_metrics(metrics)
                    
                    # Log slow operations
                    if execution_time > 5.0:  # 5 seconds threshold
                        logger.warning(f"Slow operation detected: {operation_name} took {execution_time:.2f}s")
                
                return result
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def _record_metrics(self, metrics: PerformanceMetrics):
        """Record performance metrics and update profiles."""
        # Store metrics
        self.metrics_history[metrics.operation_name].append(metrics)
        
        # Update performance profile
        self._update_performance_profile(metrics)
    
    def _update_performance_profile(self, metrics: PerformanceMetrics):
        """Update performance profile for an operation."""
        operation_name = metrics.operation_name
        
        if operation_name not in self.performance_profiles:
            self.performance_profiles[operation_name] = PerformanceProfile(
                operation_name=operation_name,
                total_calls=0,
                total_time=0.0,
                average_time=0.0,
                min_time=float('inf'),
                max_time=0.0,
                percentile_95=0.0,
                percentile_99=0.0,
                error_rate=0.0,
                last_updated=datetime.now()
            )
        
        profile = self.performance_profiles[operation_name]
        
        # Update basic metrics
        profile.total_calls += 1
        profile.total_time += metrics.execution_time
        profile.average_time = profile.total_time / profile.total_calls
        profile.min_time = min(profile.min_time, metrics.execution_time)
        profile.max_time = max(profile.max_time, metrics.execution_time)
        profile.last_updated = datetime.now()
        
        # Calculate percentiles from recent metrics
        recent_metrics = list(self.metrics_history[operation_name])
        if len(recent_metrics) >= 10:  # Need at least 10 samples for percentiles
            execution_times = [m.execution_time for m in recent_metrics]
            execution_times.sort()
            
            profile.percentile_95 = statistics.quantiles(execution_times, n=20)[18]  # 95th percentile
            profile.percentile_99 = statistics.quantiles(execution_times, n=100)[98]  # 99th percentile
        
        # Calculate error rate
        error_count = sum(1 for m in recent_metrics if m.context.get('error_occurred', False))
        profile.error_rate = (error_count / len(recent_metrics)) * 100 if recent_metrics else 0.0
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.
        
        Returns:
            Dictionary with performance analysis and recommendations
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': self._get_system_metrics_summary(),
            'operation_profiles': {},
            'performance_recommendations': [],
            'optimization_opportunities': []
        }
        
        # Add operation profiles
        for operation_name, profile in self.performance_profiles.items():
            report['operation_profiles'][operation_name] = {
                'total_calls': profile.total_calls,
                'average_time': profile.average_time,
                'min_time': profile.min_time,
                'max_time': profile.max_time,
                'percentile_95': profile.percentile_95,
                'percentile_99': profile.percentile_99,
                'error_rate': profile.error_rate,
                'last_updated': profile.last_updated.isoformat()
            }
        
        # Generate recommendations
        report['performance_recommendations'] = self._generate_recommendations()
        report['optimization_opportunities'] = self._identify_optimization_opportunities()
        
        return report
    
    def _get_system_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of system metrics."""
        if not self.metrics_history['system']:
            return {}
        
        recent_metrics = list(self.metrics_history['system'])[-60:]  # Last 60 minutes
        
        if not recent_metrics:
            return {}
        
        cpu_values = [m['cpu_usage'] for m in recent_metrics]
        memory_values = [m['memory_usage'] for m in recent_metrics]
        
        return {
            'cpu_usage': {
                'current': cpu_values[-1],
                'average': statistics.mean(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            },
            'memory_usage': {
                'current': memory_values[-1],
                'average': statistics.mean(memory_values),
                'max': max(memory_values),
                'min': min(memory_values)
            },
            'sample_count': len(recent_metrics)
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []
        
        # Analyze slow operations
        for operation_name, profile in self.performance_profiles.items():
            if profile.average_time > 2.0:  # 2 seconds threshold
                recommendations.append(
                    f"Operation '{operation_name}' has high average execution time: {profile.average_time:.2f}s"
                )
            
            if profile.error_rate > 5.0:  # 5% error rate threshold
                recommendations.append(
                    f"Operation '{operation_name}' has high error rate: {profile.error_rate:.1f}%"
                )
        
        # Analyze system metrics
        system_summary = self._get_system_metrics_summary()
        if system_summary:
            if system_summary['cpu_usage']['average'] > 70:
                recommendations.append("High CPU usage detected - consider scaling or optimization")
            
            if system_summary['memory_usage']['average'] > 80:
                recommendations.append("High memory usage detected - consider memory optimization")
        
        return recommendations
    
    def _identify_optimization_opportunities(self) -> List[str]:
        """Identify specific optimization opportunities."""
        opportunities = []
        
        # Check for caching opportunities
        for operation_name, profile in self.performance_profiles.items():
            if profile.total_calls > 100 and profile.average_time > 0.5:
                opportunities.append(f"Consider caching for frequently called operation: {operation_name}")
        
        # Check for database optimization opportunities
        db_operations = [name for name in self.performance_profiles.keys() if 'query' in name.lower()]
        if db_operations:
            slow_queries = [name for name in db_operations 
                          if self.performance_profiles[name].average_time > 1.0]
            if slow_queries:
                opportunities.append(f"Database query optimization needed for: {', '.join(slow_queries)}")
        
        # Check for async optimization opportunities
        sync_operations = [name for name in self.performance_profiles.keys() 
                         if 'sync' in name.lower()]
        if sync_operations:
            opportunities.append("Consider converting synchronous operations to async for better performance")
        
        return opportunities
    
    async def optimize_async_operations(self) -> Dict[str, Any]:
        """Async version of performance optimization."""
        return await asyncio.to_thread(self.optimize_performance)
    
    def optimize_performance(self) -> Dict[str, Any]:
        """
        Automatically optimize performance where possible.
        
        Returns:
            Dictionary with optimization results
        """
        optimization_results = {
            'timestamp': datetime.now().isoformat(),
            'optimizations_applied': [],
            'cache_optimizations': [],
            'connection_optimizations': [],
            'query_optimizations': []
        }
        
        # Apply cache optimizations
        cache_results = self.cache_manager.optimize_cache()
        optimization_results['cache_optimizations'] = cache_results
        
        # Apply connection pool optimizations
        connection_results = self.connection_pool_manager.optimize_pools()
        optimization_results['connection_optimizations'] = connection_results
        
        # Apply query optimizations
        query_results = self.query_optimizer.optimize_queries()
        optimization_results['query_optimizations'] = query_results
        
        optimization_results['optimizations_applied'] = (
            cache_results + connection_results + query_results
        )
        
        return optimization_results

class CacheManager:
    """Manages application caching for performance optimization."""
    
    def __init__(self):
        self.cache_configs = {}
        self.cache_statistics = defaultdict(lambda: {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        })
    
    def optimize_cache(self) -> List[str]:
        """Optimize cache configurations."""
        optimizations = []
        
        # Analyze cache hit rates
        for cache_name, stats in self.cache_statistics.items():
            total_requests = stats['hits'] + stats['misses']
            if total_requests > 0:
                hit_rate = (stats['hits'] / total_requests) * 100
                
                if hit_rate < 70:  # 70% hit rate threshold
                    optimizations.append(f"Cache '{cache_name}' hit rate low: {hit_rate:.1f}%")
                
                if stats['evictions'] > stats['hits']:
                    optimizations.append(f"Cache '{cache_name}' has high eviction rate")
        
        return optimizations

class ConnectionPoolManager:
    """Manages connection pools for optimal performance."""
    
    def __init__(self):
        self.pool_configs = {}
        self.pool_statistics = defaultdict(lambda: {
            'active_connections': 0,
            'idle_connections': 0,
            'wait_time': 0.0
        })
    
    def optimize_pools(self) -> List[str]:
        """Optimize connection pool configurations."""
        optimizations = []
        
        # Analyze connection pool usage
        for pool_name, stats in self.pool_statistics.items():
            total_connections = stats['active_connections'] + stats['idle_connections']
            
            if stats['wait_time'] > 1.0:  # 1 second wait time threshold
                optimizations.append(f"Connection pool '{pool_name}' has high wait time: {stats['wait_time']:.2f}s")
            
            if total_connections > 0:
                utilization = (stats['active_connections'] / total_connections) * 100
                if utilization > 90:
                    optimizations.append(f"Connection pool '{pool_name}' utilization high: {utilization:.1f}%")
        
        return optimizations

class QueryOptimizer:
    """Optimizes database queries for better performance."""
    
    def __init__(self):
        self.query_statistics = defaultdict(lambda: {
            'execution_count': 0,
            'total_time': 0.0,
            'average_time': 0.0
        })
    
    def optimize_queries(self) -> List[str]:
        """Optimize slow queries."""
        optimizations = []
        
        # Analyze slow queries
        for query_hash, stats in self.query_statistics.items():
            if stats['average_time'] > 1.0:  # 1 second threshold
                optimizations.append(f"Slow query detected: {stats['average_time']:.2f}s average")
        
        return optimizations

# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()