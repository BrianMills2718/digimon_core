"""
Functional tests for AnyIO benchmark system

Tests the actual performance benchmarking functionality with real
AnyIO structured concurrency vs asyncio.gather comparisons.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch

from src.core.anyio_benchmark import (
    AnyIOBenchmark,
    BenchmarkResult,
    run_anyio_performance_validation
)


@pytest.fixture
def anyio_benchmark():
    """Create AnyIO benchmark instance"""
    return AnyIOBenchmark()


class TestBenchmarkResult:
    """Test BenchmarkResult data structure"""
    
    def test_benchmark_result_creation(self):
        """Test creating BenchmarkResult"""
        result = BenchmarkResult(
            implementation="AnyIO",
            total_time=2.5,
            requests_per_second=40.0,
            average_latency=0.025,
            success_rate=1.0,
            memory_usage=1024
        )
        
        assert result.implementation == "AnyIO"
        assert result.total_time == 2.5
        assert result.requests_per_second == 40.0
        assert result.average_latency == 0.025
        assert result.success_rate == 1.0
        assert result.memory_usage == 1024


class TestAnyIOBenchmark:
    """Test AnyIO benchmark functionality"""
    
    def test_benchmark_initialization(self, anyio_benchmark):
        """Test benchmark initialization"""
        assert anyio_benchmark.logger is not None
        
    @pytest.mark.asyncio
    async def test_simulate_async_work(self, anyio_benchmark):
        """Test async work simulation"""
        start_time = time.time()
        result = await anyio_benchmark.simulate_async_work(0.1)
        end_time = time.time()
        
        # Should take approximately the specified duration
        duration = end_time - start_time
        assert 0.08 <= duration <= 0.15  # Allow some tolerance
        
        # Should return a string result
        assert isinstance(result, str)
        assert result.startswith("completed_")
        
    @pytest.mark.asyncio
    async def test_simulate_async_work_asyncio(self, anyio_benchmark):
        """Test asyncio work simulation"""
        start_time = time.time()
        result = await anyio_benchmark.simulate_async_work_asyncio(0.1)
        end_time = time.time()
        
        # Should take approximately the specified duration
        duration = end_time - start_time
        assert 0.08 <= duration <= 0.15  # Allow some tolerance
        
        # Should return a string result
        assert isinstance(result, str)
        assert result.startswith("completed_")
        
    @pytest.mark.asyncio
    async def test_benchmark_anyio_implementation(self, anyio_benchmark):
        """Test AnyIO implementation benchmarking"""
        num_tasks = 10
        task_duration = 0.01  # Short duration for testing
        
        result = await anyio_benchmark.benchmark_anyio_implementation(num_tasks, task_duration)
        
        # Check result structure
        assert isinstance(result, BenchmarkResult)
        assert result.implementation == "AnyIO"
        assert result.total_time > 0
        assert result.requests_per_second > 0
        assert result.success_rate > 0
        
        # Should process all tasks
        expected_successful = num_tasks
        actual_successful = int(result.success_rate * num_tasks)
        assert actual_successful == expected_successful
        
    @pytest.mark.asyncio
    async def test_benchmark_asyncio_implementation(self, anyio_benchmark):
        """Test asyncio.gather implementation benchmarking"""
        num_tasks = 10
        task_duration = 0.01  # Short duration for testing
        
        result = await anyio_benchmark.benchmark_asyncio_implementation(num_tasks, task_duration)
        
        # Check result structure
        assert isinstance(result, BenchmarkResult)
        assert result.implementation == "asyncio.gather"
        assert result.total_time > 0
        assert result.requests_per_second > 0
        assert result.success_rate > 0
        
        # Should process all tasks
        expected_successful = num_tasks
        actual_successful = int(result.success_rate * num_tasks)
        assert actual_successful == expected_successful
        
    @pytest.mark.asyncio
    async def test_run_comparative_benchmark(self, anyio_benchmark):
        """Test comparative benchmark between AnyIO and asyncio"""
        num_tasks = 5
        task_duration = 0.01
        iterations = 2
        
        results = await anyio_benchmark.run_comparative_benchmark(
            num_tasks, task_duration, iterations
        )
        
        # Check results structure
        assert "test_configuration" in results
        assert "anyio_results" in results
        assert "asyncio_results" in results
        assert "performance_comparison" in results
        
        # Check test configuration
        config = results["test_configuration"]
        assert config["num_tasks"] == num_tasks
        assert config["task_duration"] == task_duration
        assert config["iterations"] == iterations
        
        # Check AnyIO results
        anyio_results = results["anyio_results"]
        assert "average_time" in anyio_results
        assert "average_rps" in anyio_results
        assert "all_results" in anyio_results
        assert len(anyio_results["all_results"]) == iterations
        
        # Check asyncio results
        asyncio_results = results["asyncio_results"]
        assert "average_time" in asyncio_results
        assert "average_rps" in asyncio_results
        assert "all_results" in asyncio_results
        assert len(asyncio_results["all_results"]) == iterations
        
        # Check performance comparison
        comparison = results["performance_comparison"]
        assert "time_improvement" in comparison
        assert "rps_improvement" in comparison
        assert "percentage_improvement" in comparison
        assert "target_met" in comparison
        assert "summary" in comparison
        
        # Performance metrics should be positive
        assert comparison["time_improvement"] > 0
        assert comparison["rps_improvement"] > 0
        
    @pytest.mark.asyncio
    async def test_benchmark_real_world_scenario(self, anyio_benchmark):
        """Test real-world scenario benchmarking"""
        results = await anyio_benchmark.benchmark_real_world_scenario()
        
        # Check results structure
        assert "scenarios_tested" in results
        assert "overall_improvement" in results
        assert "target_met" in results
        assert "scenario_results" in results
        
        # Should test multiple scenarios
        assert results["scenarios_tested"] > 0
        assert results["overall_improvement"] > 0
        
        # Check individual scenario results
        scenario_results = results["scenario_results"]
        assert len(scenario_results) > 0
        
        for scenario_name, scenario_result in scenario_results.items():
            assert "test_configuration" in scenario_result
            assert "performance_comparison" in scenario_result
            
    @pytest.mark.asyncio
    async def test_benchmark_with_different_task_counts(self, anyio_benchmark):
        """Test benchmarking with different task counts"""
        task_counts = [5, 10, 20]
        
        for count in task_counts:
            result = await anyio_benchmark.benchmark_anyio_implementation(count, 0.01)
            
            # Should scale appropriately
            assert result.success_rate == 1.0  # All tasks should succeed
            
            # Requests per second should scale with task count (roughly)
            expected_min_rps = count / 2  # Conservative estimate
            assert result.requests_per_second >= expected_min_rps
            
    @pytest.mark.asyncio
    async def test_benchmark_error_handling(self, anyio_benchmark):
        """Test benchmark error handling"""
        # Test with invalid parameters
        result = await anyio_benchmark.benchmark_anyio_implementation(0, 0.01)
        
        # Should handle zero tasks gracefully
        assert isinstance(result, BenchmarkResult)
        assert result.total_time >= 0
        assert result.success_rate == 0  # No tasks to succeed
        
    @pytest.mark.asyncio
    async def test_concurrent_benchmark_runs(self, anyio_benchmark):
        """Test running multiple benchmarks concurrently"""
        import asyncio
        
        # Run multiple benchmarks concurrently
        tasks = [
            anyio_benchmark.benchmark_anyio_implementation(5, 0.01),
            anyio_benchmark.benchmark_asyncio_implementation(5, 0.01),
            anyio_benchmark.benchmark_anyio_implementation(3, 0.01)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should complete successfully
        assert len(results) == 3
        for result in results:
            assert isinstance(result, BenchmarkResult)
            assert result.total_time > 0
            assert result.success_rate > 0


class TestPerformanceValidation:
    """Test performance validation functionality"""
    
    @pytest.mark.asyncio
    async def test_run_anyio_performance_validation(self):
        """Test running complete performance validation"""
        results = await run_anyio_performance_validation()
        
        # Check results structure
        assert "validation_summary" in results
        assert "detailed_results" in results
        
        # Check validation summary
        summary = results["validation_summary"]
        assert "validation_status" in summary
        assert "overall_improvement" in summary
        assert "target_improvement" in summary
        assert "improvement_achieved" in summary
        assert "scenarios_tested" in summary
        assert "recommendation" in summary
        
        # Should test multiple scenarios
        assert summary["scenarios_tested"] > 0
        assert summary["target_improvement"] == 1.5
        assert summary["overall_improvement"] > 0
        
        # Validation status should be PASS or FAIL
        assert summary["validation_status"] in ["PASS", "FAIL"]
        
        # Check detailed results
        detailed = results["detailed_results"]
        assert "scenario_results" in detailed
        assert len(detailed["scenario_results"]) > 0
        
    @pytest.mark.asyncio
    async def test_performance_validation_target_achievement(self):
        """Test performance validation target achievement"""
        results = await run_anyio_performance_validation()
        
        summary = results["validation_summary"]
        
        # Check if target was achieved
        target_met = summary["improvement_achieved"]
        overall_improvement = summary["overall_improvement"]
        
        if target_met:
            # If target was met, improvement should be >= 1.5
            assert overall_improvement >= 1.5
            assert summary["validation_status"] == "PASS"
        else:
            # If target was not met, improvement should be < 1.5
            assert overall_improvement < 1.5
            assert summary["validation_status"] == "FAIL"
            
    @pytest.mark.asyncio
    async def test_performance_measurement_accuracy(self, anyio_benchmark):
        """Test accuracy of performance measurements"""
        # Run the same benchmark multiple times
        num_runs = 3
        results = []
        
        for _ in range(num_runs):
            result = await anyio_benchmark.benchmark_anyio_implementation(10, 0.01)
            results.append(result)
        
        # Results should be consistent (within reasonable variance)
        times = [r.total_time for r in results]
        rps_values = [r.requests_per_second for r in results]
        
        # Calculate coefficient of variation (should be < 50% for consistent measurements)
        import statistics
        
        time_mean = statistics.mean(times)
        time_stdev = statistics.stdev(times) if len(times) > 1 else 0
        time_cv = (time_stdev / time_mean) * 100 if time_mean > 0 else 0
        
        rps_mean = statistics.mean(rps_values)
        rps_stdev = statistics.stdev(rps_values) if len(rps_values) > 1 else 0
        rps_cv = (rps_stdev / rps_mean) * 100 if rps_mean > 0 else 0
        
        # Measurements should be reasonably consistent
        assert time_cv < 50, f"Time measurements too variable: {time_cv}% CV"
        assert rps_cv < 50, f"RPS measurements too variable: {rps_cv}% CV"


class TestBenchmarkIntegration:
    """Test benchmark integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_benchmark_with_logging(self, anyio_benchmark):
        """Test benchmark with logging integration"""
        # Capture log messages
        with patch.object(anyio_benchmark.logger, 'info') as mock_logger:
            await anyio_benchmark.benchmark_anyio_implementation(5, 0.01)
            
            # Should have logged benchmark start
            mock_logger.assert_called()
            
    @pytest.mark.asyncio
    async def test_end_to_end_benchmark_workflow(self):
        """Test complete end-to-end benchmark workflow"""
        # 1. Create benchmark instance
        benchmark = AnyIOBenchmark()
        
        # 2. Run comparative benchmark
        comparison_results = await benchmark.run_comparative_benchmark(
            num_tasks=5,
            task_duration=0.01,
            iterations=2
        )
        
        # 3. Run real-world scenarios
        realworld_results = await benchmark.benchmark_real_world_scenario()
        
        # 4. Run validation
        validation_results = await run_anyio_performance_validation()
        
        # All should complete successfully
        assert comparison_results["performance_comparison"]["time_improvement"] > 0
        assert realworld_results["overall_improvement"] > 0
        assert validation_results["validation_summary"]["overall_improvement"] > 0
        
    @pytest.mark.asyncio
    async def test_benchmark_performance_under_load(self, anyio_benchmark):
        """Test benchmark system performance under load"""
        import time
        
        # Run larger benchmark to test performance
        start_time = time.time()
        result = await anyio_benchmark.benchmark_anyio_implementation(50, 0.005)
        end_time = time.time()
        
        benchmark_overhead = end_time - start_time - result.total_time
        
        # Benchmark overhead should be minimal (< 50% of actual work time)
        max_overhead = result.total_time * 0.5
        assert benchmark_overhead < max_overhead, f"Benchmark overhead too high: {benchmark_overhead}s"
        
        # Should still provide accurate measurements
        assert result.success_rate == 1.0
        assert result.total_time > 0
        assert result.requests_per_second > 0


class TestBenchmarkUtilities:
    """Test benchmark utility functions"""
    
    def test_main_function(self):
        """Test main function execution"""
        from src.core.anyio_benchmark import main
        
        # Should return results without errors
        with patch('src.core.anyio_benchmark.run_anyio_performance_validation') as mock_validation:
            mock_validation.return_value = {
                "validation_summary": {
                    "validation_status": "PASS",
                    "overall_improvement": 2.0
                }
            }
            
            # Mock anyio.run to avoid actual async execution in test
            with patch('anyio.run') as mock_run:
                mock_run.return_value = {
                    "validation_summary": {
                        "validation_status": "PASS",
                        "overall_improvement": 2.0
                    }
                }
                
                result = main()
                
                assert result is not None
                mock_run.assert_called_once()
                
    @pytest.mark.asyncio
    async def test_benchmark_result_serialization(self, anyio_benchmark):
        """Test that benchmark results can be serialized"""
        import json
        
        result = await anyio_benchmark.benchmark_anyio_implementation(5, 0.01)
        
        # Should be able to convert to dict and serialize
        result_dict = {
            "implementation": result.implementation,
            "total_time": result.total_time,
            "requests_per_second": result.requests_per_second,
            "average_latency": result.average_latency,
            "success_rate": result.success_rate,
            "memory_usage": result.memory_usage
        }
        
        # Should be JSON serializable
        json_str = json.dumps(result_dict)
        parsed = json.loads(json_str)
        
        assert parsed["implementation"] == result.implementation
        assert parsed["total_time"] == result.total_time