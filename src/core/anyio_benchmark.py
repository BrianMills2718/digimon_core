"""AnyIO Performance Benchmark

Benchmarks the performance improvements from migrating asyncio.gather
to AnyIO structured concurrency.
"""

import asyncio
import anyio
import time
from typing import List, Dict, Any
from dataclasses import dataclass
from .logging_config import get_logger

logger = get_logger("core.anyio_benchmark")


@dataclass
class BenchmarkResult:
    """Results from performance benchmark"""
    implementation: str
    total_time: float
    requests_per_second: float
    average_latency: float
    success_rate: float
    memory_usage: int


class AnyIOBenchmark:
    """Benchmark AnyIO vs asyncio.gather performance"""
    
    def __init__(self):
        self.logger = get_logger("core.anyio_benchmark")
        
    async def simulate_async_work(self, duration: float = 0.1) -> str:
        """Simulate async work with sleep"""
        await anyio.sleep(duration)
        return f"completed_{int(time.time() * 1000)}"
        
    async def simulate_async_work_asyncio(self, duration: float = 0.1) -> str:
        """Simulate async work with asyncio sleep"""
        await asyncio.sleep(duration)
        return f"completed_{int(time.time() * 1000)}"
        
    async def benchmark_anyio_implementation(self, num_tasks: int = 100, 
                                           task_duration: float = 0.1) -> BenchmarkResult:
        """Benchmark AnyIO structured concurrency implementation"""
        self.logger.info(f"Starting AnyIO benchmark with {num_tasks} tasks")
        
        start_time = time.time()
        results = []
        successful_tasks = 0
        
        # Use AnyIO structured concurrency
        async with anyio.create_task_group() as tg:
            for i in range(num_tasks):
                tg.start_soon(self._anyio_task_wrapper, i, task_duration, results)
        
        total_time = time.time() - start_time
        successful_tasks = len([r for r in results if r is not None])
        
        return BenchmarkResult(
            implementation="AnyIO",
            total_time=total_time,
            requests_per_second=successful_tasks / total_time if total_time > 0 else 0,
            average_latency=total_time / num_tasks if num_tasks > 0 else 0,
            success_rate=successful_tasks / num_tasks if num_tasks > 0 else 0,
            memory_usage=0  # TODO: Add memory tracking
        )
        
    async def _anyio_task_wrapper(self, task_id: int, duration: float, results: List):
        """Wrapper for AnyIO task execution"""
        try:
            result = await self.simulate_async_work(duration)
            results.append(result)
        except Exception as e:
            self.logger.error(f"Task {task_id} failed: {e}")
            results.append(None)
            
    async def benchmark_asyncio_implementation(self, num_tasks: int = 100, 
                                             task_duration: float = 0.1) -> BenchmarkResult:
        """Benchmark traditional asyncio.gather implementation"""
        self.logger.info(f"Starting asyncio.gather benchmark with {num_tasks} tasks")
        
        start_time = time.time()
        
        # Use traditional asyncio.gather
        tasks = [
            self.simulate_async_work_asyncio(task_duration) 
            for _ in range(num_tasks)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        successful_tasks = len([r for r in results if not isinstance(r, Exception)])
        
        return BenchmarkResult(
            implementation="asyncio.gather",
            total_time=total_time,
            requests_per_second=successful_tasks / total_time if total_time > 0 else 0,
            average_latency=total_time / num_tasks if num_tasks > 0 else 0,
            success_rate=successful_tasks / num_tasks if num_tasks > 0 else 0,
            memory_usage=0  # TODO: Add memory tracking
        )
        
    async def run_comparative_benchmark(self, num_tasks: int = 100, 
                                      task_duration: float = 0.1,
                                      iterations: int = 3) -> Dict[str, Any]:
        """Run comparative benchmark between AnyIO and asyncio.gather
        
        Args:
            num_tasks: Number of concurrent tasks
            task_duration: Duration of each task in seconds
            iterations: Number of benchmark iterations
            
        Returns:
            Comprehensive benchmark results
        """
        self.logger.info(f"Running comparative benchmark: {num_tasks} tasks, "
                        f"{task_duration}s duration, {iterations} iterations")
        
        anyio_results = []
        asyncio_results = []
        
        # Run multiple iterations for better accuracy
        for i in range(iterations):
            self.logger.info(f"Iteration {i + 1}/{iterations}")
            
            # Test AnyIO implementation
            anyio_result = await self.benchmark_anyio_implementation(num_tasks, task_duration)
            anyio_results.append(anyio_result)
            
            # Small delay between tests
            await anyio.sleep(0.1)
            
            # Test asyncio.gather implementation
            asyncio_result = await self.benchmark_asyncio_implementation(num_tasks, task_duration)
            asyncio_results.append(asyncio_result)
            
            # Small delay between iterations
            await anyio.sleep(0.1)
        
        # Calculate averages
        avg_anyio_time = sum(r.total_time for r in anyio_results) / len(anyio_results)
        avg_asyncio_time = sum(r.total_time for r in asyncio_results) / len(asyncio_results)
        
        avg_anyio_rps = sum(r.requests_per_second for r in anyio_results) / len(anyio_results)
        avg_asyncio_rps = sum(r.requests_per_second for r in asyncio_results) / len(asyncio_results)
        
        # Calculate performance improvement
        performance_improvement = avg_asyncio_time / avg_anyio_time if avg_anyio_time > 0 else 1.0
        rps_improvement = avg_anyio_rps / avg_asyncio_rps if avg_asyncio_rps > 0 else 1.0
        
        results = {
            "test_configuration": {
                "num_tasks": num_tasks,
                "task_duration": task_duration,
                "iterations": iterations
            },
            "anyio_results": {
                "average_time": avg_anyio_time,
                "average_rps": avg_anyio_rps,
                "all_results": [
                    {
                        "time": r.total_time,
                        "rps": r.requests_per_second,
                        "success_rate": r.success_rate
                    }
                    for r in anyio_results
                ]
            },
            "asyncio_results": {
                "average_time": avg_asyncio_time,
                "average_rps": avg_asyncio_rps,
                "all_results": [
                    {
                        "time": r.total_time,
                        "rps": r.requests_per_second,
                        "success_rate": r.success_rate
                    }
                    for r in asyncio_results
                ]
            },
            "performance_comparison": {
                "time_improvement": performance_improvement,
                "rps_improvement": rps_improvement,
                "percentage_improvement": (performance_improvement - 1.0) * 100,
                "target_met": performance_improvement >= 1.5,  # Target: >1.5x improvement
                "summary": f"AnyIO is {performance_improvement:.2f}x faster than asyncio.gather"
            }
        }
        
        # Log results
        self.logger.info(f"Benchmark complete: AnyIO {performance_improvement:.2f}x faster")
        self.logger.info(f"Target 1.5x improvement: {'✅ MET' if performance_improvement >= 1.5 else '❌ NOT MET'}")
        
        return results
        
    async def benchmark_real_world_scenario(self) -> Dict[str, Any]:
        """Benchmark realistic scenarios similar to KGAS usage"""
        scenarios = [
            {"name": "Small Batch", "tasks": 10, "duration": 0.05},
            {"name": "Medium Batch", "tasks": 50, "duration": 0.1},
            {"name": "Large Batch", "tasks": 100, "duration": 0.1},
            {"name": "API Simulation", "tasks": 25, "duration": 0.2},
        ]
        
        results = {}
        
        for scenario in scenarios:
            self.logger.info(f"Testing scenario: {scenario['name']}")
            
            result = await self.run_comparative_benchmark(
                num_tasks=scenario["tasks"],
                task_duration=scenario["duration"],
                iterations=2  # Fewer iterations for multiple scenarios
            )
            
            results[scenario["name"]] = result
            
        # Calculate overall performance improvement
        total_improvements = [
            result["performance_comparison"]["time_improvement"]
            for result in results.values()
        ]
        
        overall_improvement = sum(total_improvements) / len(total_improvements)
        
        summary = {
            "scenarios_tested": len(scenarios),
            "overall_improvement": overall_improvement,
            "target_met": overall_improvement >= 1.5,
            "scenario_results": results
        }
        
        self.logger.info(f"Real-world benchmark complete: {overall_improvement:.2f}x average improvement")
        
        return summary


async def run_anyio_performance_validation() -> Dict[str, Any]:
    """Run AnyIO performance validation
    
    Returns:
        Performance validation results
    """
    benchmark = AnyIOBenchmark()
    
    # Run comprehensive benchmark
    results = await benchmark.benchmark_real_world_scenario()
    
    # Add validation summary
    validation_summary = {
        "validation_status": "PASS" if results["target_met"] else "FAIL",
        "overall_improvement": results["overall_improvement"],
        "target_improvement": 1.5,
        "improvement_achieved": results["overall_improvement"] >= 1.5,
        "scenarios_tested": results["scenarios_tested"],
        "recommendation": (
            "AnyIO migration successful - performance target achieved"
            if results["target_met"]
            else "AnyIO migration needs optimization - performance target not met"
        )
    }
    
    return {
        "validation_summary": validation_summary,
        "detailed_results": results
    }


def main():
    """Main function for running benchmark"""
    async def run_benchmark():
        return await run_anyio_performance_validation()
    
    return anyio.run(run_benchmark)


if __name__ == "__main__":
    results = main()
    print(f"AnyIO Performance Validation: {results['validation_summary']['validation_status']}")
    print(f"Improvement: {results['validation_summary']['overall_improvement']:.2f}x")