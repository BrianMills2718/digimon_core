"""
Performance Testing Infrastructure

Provides comprehensive performance testing with monitoring, benchmarking,
and automated performance regression detection.
"""

import asyncio
import logging
import time
import statistics
import resource
import psutil
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime, timedelta

from .base_test import AsyncBaseTest
from .fixtures import ServiceFixtures
from ..core.dependency_injection import ServiceContainer
from .config import get_testing_config

logger = logging.getLogger(__name__)


class PerformanceMetric(Enum):
    """Types of performance metrics to collect"""
    EXECUTION_TIME = "execution_time_ms"
    MEMORY_USAGE = "memory_usage_mb" 
    CPU_USAGE = "cpu_usage_percent"
    THROUGHPUT = "operations_per_second"
    LATENCY = "latency_ms"
    ERROR_RATE = "error_rate_percent"


@dataclass
class PerformanceBaseline:
    """Performance baseline for regression testing"""
    metric_name: str
    baseline_value: float
    tolerance_percent: float = field(default_factory=lambda: get_testing_config().performance.baseline_tolerance_percent)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def is_within_tolerance(self, measured_value: float) -> bool:
        """Check if measured value is within acceptable tolerance"""
        tolerance_amount = self.baseline_value * (self.tolerance_percent / 100.0)
        return abs(measured_value - self.baseline_value) <= tolerance_amount


@dataclass
class PerformanceResult:
    """Result of a performance test"""
    test_name: str
    metrics: Dict[PerformanceMetric, float]
    execution_count: int
    total_duration_ms: float
    baseline_comparisons: Dict[str, bool] = field(default_factory=dict)
    detailed_measurements: List[Dict[str, Any]] = field(default_factory=list)
    regression_detected: bool = False
    
    def get_summary(self) -> Dict[str, Any]:
        """Get human-readable summary of results"""
        return {
            'test': self.test_name,
            'executions': self.execution_count,
            'duration_ms': self.total_duration_ms,
            'avg_execution_time_ms': self.metrics.get(PerformanceMetric.EXECUTION_TIME, 0),
            'throughput_ops_sec': self.metrics.get(PerformanceMetric.THROUGHPUT, 0),
            'memory_usage_mb': self.metrics.get(PerformanceMetric.MEMORY_USAGE, 0),
            'cpu_usage_percent': self.metrics.get(PerformanceMetric.CPU_USAGE, 0),
            'regression_detected': self.regression_detected,
            'baseline_checks': self.baseline_comparisons
        }


class PerformanceMonitor:
    """Real-time performance monitoring during tests"""
    
    def __init__(self):
        self.start_time = None
        self.measurements = []
        self.process = psutil.Process()
        
    def start_monitoring(self) -> None:
        """Start performance monitoring"""
        self.start_time = time.time()
        self.measurements = []
        
        # Record initial state
        self._record_measurement("start")
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return summary"""
        if self.start_time is None:
            return {}
        
        self._record_measurement("end")
        
        total_time = time.time() - self.start_time
        
        # Calculate aggregated metrics
        memory_values = [m['memory_mb'] for m in self.measurements if 'memory_mb' in m]
        cpu_values = [m['cpu_percent'] for m in self.measurements if 'cpu_percent' in m]
        
        return {
            'total_time_ms': total_time * 1000,
            'avg_memory_mb': statistics.mean(memory_values) if memory_values else 0,
            'max_memory_mb': max(memory_values) if memory_values else 0,
            'avg_cpu_percent': statistics.mean(cpu_values) if cpu_values else 0,
            'max_cpu_percent': max(cpu_values) if cpu_values else 0,
            'measurement_count': len(self.measurements)
        }
    
    def _record_measurement(self, label: str) -> None:
        """Record a performance measurement"""
        try:
            memory_info = self.process.memory_info()
            cpu_percent = self.process.cpu_percent()
            
            measurement = {
                'timestamp': time.time(),
                'label': label,
                'memory_mb': memory_info.rss / 1024 / 1024,  # Convert to MB
                'cpu_percent': cpu_percent,
                'elapsed_ms': (time.time() - self.start_time) * 1000 if self.start_time else 0
            }
            
            self.measurements.append(measurement)
            
        except Exception as e:
            logger.warning(f"Failed to record performance measurement: {e}")


class PerformanceTestBase(AsyncBaseTest):
    """Base class for performance testing with comprehensive monitoring"""
    
    def setUp(self) -> None:
        """Initialize performance test environment"""
        super().setUp()
        
        self.fixtures = ServiceFixtures()
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self.performance_results: List[PerformanceResult] = []
        self.monitor = PerformanceMonitor()
        
        # Performance test configuration from centralized config
        config = get_testing_config()
        self.default_iterations = config.performance.default_iterations
        self.warmup_iterations = config.performance.warmup_iterations
        self.timeout_seconds = config.performance.timeout_seconds
        
        logger.debug("Performance test environment initialized")
    
    def load_baselines(self, baseline_file: Optional[str] = None) -> Dict[str, PerformanceBaseline]:
        """Load performance baselines from file"""
        if baseline_file is None:
            return {}
        
        try:
            with open(baseline_file, 'r') as f:
                baseline_data = json.load(f)
            
            baselines = {}
            for name, data in baseline_data.items():
                baselines[name] = PerformanceBaseline(
                    metric_name=data['metric_name'],
                    baseline_value=data['baseline_value'],
                    tolerance_percent=data.get('tolerance_percent', 10.0),
                    created_at=data.get('created_at', datetime.now().isoformat())
                )
            
            self.baselines = baselines
            logger.info(f"Loaded {len(baselines)} performance baselines")
            return baselines
            
        except Exception as e:
            logger.warning(f"Failed to load baselines: {e}")
            return {}
    
    def save_baselines(self, baseline_file: str) -> None:
        """Save performance baselines to file"""
        try:
            baseline_data = {}
            for name, baseline in self.baselines.items():
                baseline_data[name] = {
                    'metric_name': baseline.metric_name,
                    'baseline_value': baseline.baseline_value,
                    'tolerance_percent': baseline.tolerance_percent,
                    'created_at': baseline.created_at
                }
            
            with open(baseline_file, 'w') as f:
                json.dump(baseline_data, f, indent=2)
            
            logger.info(f"Saved {len(self.baselines)} baselines to {baseline_file}")
            
        except Exception as e:
            logger.error(f"Failed to save baselines: {e}")
    
    async def benchmark_service_method(self, service_name: str, method_name: str,
                                     method_params: Optional[Dict[str, Any]] = None,
                                     iterations: Optional[int] = None) -> PerformanceResult:
        """Benchmark a specific service method"""
        iterations = iterations or self.default_iterations
        method_params = method_params or {}
        
        test_name = f"{service_name}.{method_name}"
        logger.info(f"Benchmarking {test_name} with {iterations} iterations")
        
        # Get service
        service = await self.async_get_service(service_name)
        method = getattr(service, method_name)
        
        # Warmup
        logger.debug(f"Warming up with {self.warmup_iterations} iterations")
        for _ in range(self.warmup_iterations):
            try:
                await method(**method_params)
            except Exception as e:
                logger.warning(f"Warmup iteration failed: {e}")
        
        # Start monitoring
        self.monitor.start_monitoring()
        
        # Benchmark iterations
        execution_times: List[float] = []
        error_count = 0
        detailed_measurements: List[Dict[str, Any]] = []
        
        total_start_time = time.time()
        
        for i in range(iterations):
            iteration_start = time.time()
            
            try:
                result = await method(**method_params)
                execution_time = (time.time() - iteration_start) * 1000
                execution_times.append(execution_time)
                
                detailed_measurements.append({
                    'iteration': i + 1,
                    'execution_time_ms': execution_time,
                    'success': True,
                    'result_size': len(str(result)) if result else 0
                })
                
            except Exception as e:
                error_count += 1
                execution_time = (time.time() - iteration_start) * 1000
                execution_times.append(execution_time)  # Include failed execution time
                
                detailed_measurements.append({
                    'iteration': i + 1,
                    'execution_time_ms': execution_time,
                    'success': False,
                    'error': str(e)
                })
                
                logger.warning(f"Iteration {i+1} failed: {e}")
        
        total_duration = (time.time() - total_start_time) * 1000
        
        # Stop monitoring
        monitor_results = self.monitor.stop_monitoring()
        
        # Calculate metrics
        avg_execution_time = statistics.mean(execution_times) if execution_times else 0
        throughput = iterations / (total_duration / 1000) if total_duration > 0 else 0
        error_rate = (error_count / iterations) * 100 if iterations > 0 else 0
        
        metrics = {
            PerformanceMetric.EXECUTION_TIME: float(avg_execution_time),
            PerformanceMetric.THROUGHPUT: float(throughput),
            PerformanceMetric.ERROR_RATE: float(error_rate),
            PerformanceMetric.MEMORY_USAGE: float(monitor_results.get('avg_memory_mb', 0.0)),
            PerformanceMetric.CPU_USAGE: float(monitor_results.get('avg_cpu_percent', 0.0))
        }
        
        # Check against baselines
        baseline_comparisons = {}
        regression_detected = False
        
        for metric, value in metrics.items():
            baseline_key = f"{test_name}_{metric.value}"
            if baseline_key in self.baselines:
                baseline = self.baselines[baseline_key]
                within_tolerance = baseline.is_within_tolerance(value)
                baseline_comparisons[baseline_key] = within_tolerance
                
                if not within_tolerance:
                    regression_detected = True
                    logger.warning(f"Performance regression detected for {baseline_key}: "
                                 f"{value} vs baseline {baseline.baseline_value}")
        
        # Create result
        result = PerformanceResult(
            test_name=test_name,
            metrics=metrics,
            execution_count=iterations,
            total_duration_ms=total_duration,
            baseline_comparisons=baseline_comparisons,
            detailed_measurements=detailed_measurements,
            regression_detected=regression_detected
        )
        
        self.performance_results.append(result)
        
        logger.info(f"Benchmark completed: {test_name} - "
                   f"Avg: {avg_execution_time:.2f}ms, "
                   f"Throughput: {throughput:.2f} ops/sec, "
                   f"Errors: {error_rate:.1f}%")
        
        return result
    
    async def benchmark_workflow(self, workflow_name: str, 
                                workflow_steps: List[Dict[str, Any]],
                                iterations: Optional[int] = None) -> PerformanceResult:
        """Benchmark a complete workflow"""
        iterations = iterations or self.default_iterations
        
        logger.info(f"Benchmarking workflow '{workflow_name}' with {iterations} iterations")
        
        # Warmup
        for _ in range(self.warmup_iterations):
            try:
                await self._execute_workflow_steps(workflow_steps)
            except Exception as e:
                logger.warning(f"Workflow warmup failed: {e}")
        
        # Benchmark
        self.monitor.start_monitoring()
        
        execution_times: List[float] = []
        error_count = 0
        detailed_measurements: List[Dict[str, Any]] = []
        
        total_start_time = time.time()
        
        for i in range(iterations):
            iteration_start = time.time()
            
            try:
                step_results = await self._execute_workflow_steps(workflow_steps)
                execution_time = (time.time() - iteration_start) * 1000
                execution_times.append(execution_time)
                
                detailed_measurements.append({
                    'iteration': i + 1,
                    'execution_time_ms': execution_time,
                    'success': True,
                    'steps_completed': len(step_results)
                })
                
            except Exception as e:
                error_count += 1
                execution_time = (time.time() - iteration_start) * 1000
                execution_times.append(execution_time)
                
                detailed_measurements.append({
                    'iteration': i + 1,
                    'execution_time_ms': execution_time,
                    'success': False,
                    'error': str(e)
                })
        
        total_duration = (time.time() - total_start_time) * 1000
        monitor_results = self.monitor.stop_monitoring()
        
        # Calculate metrics
        avg_execution_time = statistics.mean(execution_times) if execution_times else 0
        throughput = iterations / (total_duration / 1000) if total_duration > 0 else 0
        error_rate = (error_count / iterations) * 100 if iterations > 0 else 0
        
        metrics = {
            PerformanceMetric.EXECUTION_TIME: float(avg_execution_time),
            PerformanceMetric.THROUGHPUT: float(throughput),
            PerformanceMetric.ERROR_RATE: float(error_rate),
            PerformanceMetric.MEMORY_USAGE: float(monitor_results.get('avg_memory_mb', 0.0)),
            PerformanceMetric.CPU_USAGE: float(monitor_results.get('avg_cpu_percent', 0.0))
        }
        
        result = PerformanceResult(
            test_name=workflow_name,
            metrics=metrics,
            execution_count=iterations,
            total_duration_ms=total_duration,
            detailed_measurements=detailed_measurements
        )
        
        self.performance_results.append(result)
        
        logger.info(f"Workflow benchmark completed: {workflow_name} - "
                   f"Avg: {avg_execution_time:.2f}ms, "
                   f"Throughput: {throughput:.2f} workflows/sec")
        
        return result
    
    async def _execute_workflow_steps(self, steps: List[Dict[str, Any]]) -> List[Any]:
        """Execute workflow steps and return results"""
        results = []
        
        for step in steps:
            service_name = step['service']
            method_name = step['method']
            params = step.get('params', {})
            
            service = await self.async_get_service(service_name)
            method = getattr(service, method_name)
            
            result = await method(**params)
            results.append(result)
        
        return results
    
    async def stress_test_service(self, service_name: str, method_name: str,
                                concurrent_calls: Optional[int] = None,
                                duration_seconds: Optional[int] = None,
                                **method_params: Any) -> Dict[str, Any]:
        """Perform stress test with concurrent calls"""
        config = get_testing_config()
        concurrent_calls = concurrent_calls or config.performance.concurrent_calls
        duration_seconds = duration_seconds or config.performance.stress_duration_seconds
        
        logger.info(f"Stress testing {service_name}.{method_name} - "
                   f"{concurrent_calls} concurrent calls for {duration_seconds}s")
        
        service = await self.async_get_service(service_name)
        method = getattr(service, method_name)
        
        # Track results
        successful_calls = 0
        failed_calls = 0
        response_times = []
        start_time = time.time()
        
        async def worker():
            nonlocal successful_calls, failed_calls
            
            while time.time() - start_time < duration_seconds:
                call_start = time.time()
                
                try:
                    await method(**method_params)
                    successful_calls += 1
                    response_times.append((time.time() - call_start) * 1000)
                    
                except Exception as e:
                    failed_calls += 1
                    logger.debug(f"Stress test call failed: {e}")
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.01)
        
        # Run concurrent workers
        self.monitor.start_monitoring()
        
        tasks = [asyncio.create_task(worker()) for _ in range(concurrent_calls)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        monitor_results = self.monitor.stop_monitoring()
        
        total_calls = successful_calls + failed_calls
        success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
        avg_response_time = statistics.mean(response_times) if response_times else 0
        throughput = successful_calls / duration_seconds
        
        stress_results = {
            'service': service_name,
            'method': method_name,
            'duration_seconds': duration_seconds,
            'concurrent_calls': concurrent_calls,
            'total_calls': total_calls,
            'successful_calls': successful_calls,
            'failed_calls': failed_calls,
            'success_rate_percent': success_rate,
            'avg_response_time_ms': avg_response_time,
            'throughput_ops_sec': throughput,
            'monitor_results': monitor_results
        }
        
        logger.info(f"Stress test completed: {success_rate:.1f}% success rate, "
                   f"{throughput:.2f} ops/sec average")
        
        return stress_results
    
    def create_baseline(self, test_name: str, metric: PerformanceMetric, 
                       value: float, tolerance_percent: Optional[float] = None) -> None:
        """Create a performance baseline for regression testing"""
        baseline_key = f"{test_name}_{metric.value}"
        
        if tolerance_percent is None:
            tolerance_percent = get_testing_config().performance.baseline_tolerance_percent
            
        baseline = PerformanceBaseline(
            metric_name=metric.value,
            baseline_value=value,
            tolerance_percent=tolerance_percent
        )
        
        self.baselines[baseline_key] = baseline
        logger.info(f"Created baseline {baseline_key}: {value} ±{tolerance_percent}%")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance test summary"""
        if not self.performance_results:
            return {"message": "No performance tests have been run"}
        
        # Calculate aggregate statistics
        all_execution_times = []
        all_throughputs = []
        regression_count = 0
        
        for result in self.performance_results:
            all_execution_times.append(result.metrics.get(PerformanceMetric.EXECUTION_TIME, 0))
            all_throughputs.append(result.metrics.get(PerformanceMetric.THROUGHPUT, 0))
            
            if result.regression_detected:
                regression_count += 1
        
        return {
            'total_tests': len(self.performance_results),
            'regressions_detected': regression_count,
            'avg_execution_time_ms': statistics.mean(all_execution_times) if all_execution_times else 0,
            'avg_throughput_ops_sec': statistics.mean(all_throughputs) if all_throughputs else 0,
            'baselines_configured': len(self.baselines),
            'test_results': [result.get_summary() for result in self.performance_results]
        }