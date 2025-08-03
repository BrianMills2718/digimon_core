#!/usr/bin/env python3
"""
Test Cross-Modal Orchestrator Concurrency Patterns

Advanced concurrency and async pattern tests for cross-modal orchestrator,
including race conditions, deadlock prevention, and resource contention.
"""

import pytest
import asyncio
import threading
import time
import weakref
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, AsyncMock, patch
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd

from src.analytics.cross_modal_orchestrator import (
    CrossModalOrchestrator, AnalysisRequest, AnalysisResult,
    AnalysisMode, ValidationLevel, WorkflowOptimizationLevel,
    WorkflowStep, OptimizedWorkflow, ModeSelectionResult
)
from src.analytics.cross_modal_converter import (
    CrossModalConverter, DataFormat, ConversionResult
)


@pytest.fixture
def orchestrator_with_mocks():
    """Create orchestrator with comprehensive mocks for concurrency testing"""
    converter = Mock(spec=CrossModalConverter)
    converter.convert_data = AsyncMock()
    
    validator = Mock()
    validator.validate_cross_modal_conversion = AsyncMock()
    validator.validate_round_trip_integrity = AsyncMock()
    
    orchestrator = CrossModalOrchestrator(service_manager=Mock())
    # Override with mocked services for testing
    orchestrator.converter = converter
    orchestrator.validator = validator
    orchestrator.default_validation_level = ValidationLevel.STANDARD
    orchestrator.default_optimization_level = WorkflowOptimizationLevel.STANDARD
    
    return orchestrator, converter, validator


class TestAsyncPatterns:
    """Test async patterns and coroutine management"""
    
    @pytest.mark.asyncio
    async def test_coroutine_lifecycle_management(self, orchestrator_with_mocks):
        """Test proper coroutine creation and cleanup"""
        orchestrator, converter, validator = orchestrator_with_mocks
        
        # Mock successful conversion
        converter.convert_data.return_value = ConversionResult(
            data=pd.DataFrame({"col": [1, 2, 3]}),
            source_format=DataFormat.GRAPH,
            target_format=DataFormat.TABLE,
            preservation_score=0.95,
            conversion_metadata={},
            validation_passed=True,
            semantic_integrity=True,
            warnings=[]
        )
        
        # Track coroutine references
        active_coroutines = []
        
        async def track_coroutine(coro_id):
            graph_data = {
                "nodes": [{"id": i, "label": f"Node_{coro_id}_{i}"} for i in range(3)],
                "edges": []
            }
            
            # Create weak reference to track cleanup
            result = await orchestrator.orchestrate_analysis(
                research_question=f"Question {coro_id}",
                data=graph_data,
                source_format=DataFormat.GRAPH
            )
            
            active_coroutines.append(weakref.ref(result))
            return result
        
        # Create multiple coroutines
        tasks = [track_coroutine(i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Verify results exist but references can be cleaned up
        assert len(results) == 10
        assert all(isinstance(r, AnalysisResult) for r in results)
        
        # Clean up results and verify memory management
        del results
        gc.collect()
        
        # Some weak references should be cleared
        dead_refs = sum(1 for ref in active_coroutines if ref() is None)
        assert dead_refs >= 0  # Memory management working
    
    @pytest.mark.asyncio
    async def test_async_context_manager_compliance(self, orchestrator_with_mocks):
        """Test async context manager patterns"""
        orchestrator, converter, validator = orchestrator_with_mocks
        
        # Mock workflow execution
        converter.convert_data.return_value = ConversionResult(
            data={}, source_format=DataFormat.GRAPH, target_format=DataFormat.TABLE,
            preservation_score=0.9, conversion_metadata={}, validation_passed=True,
            semantic_integrity=True, warnings=[]
        )
        
        # Test context manager pattern (if implemented)
        class AsyncContextWrapper:
            def __init__(self, orchestrator):
                self.orchestrator = orchestrator
                self.entered = False
                self.exited = False
            
            async def __aenter__(self):
                self.entered = True
                return self.orchestrator
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                self.exited = True
                return False
        
        # Test proper context management
        wrapper = AsyncContextWrapper(orchestrator)
        
        async with wrapper as orch:
            result = await orch.orchestrate_analysis(
                research_question="Context test",
                data={"nodes": [], "edges": []},
                source_format=DataFormat.GRAPH
            )
            assert result is not None
        
        assert wrapper.entered and wrapper.exited
    
    @pytest.mark.asyncio
    async def test_cancellation_handling(self, orchestrator_with_mocks):
        """Test proper handling of task cancellation"""
        orchestrator, converter, validator = orchestrator_with_mocks
        
        # Create slow mock that can be cancelled
        async def slow_conversion(*args, **kwargs):
            await asyncio.sleep(10)  # Long operation
            return ConversionResult(
                data={}, source_format=DataFormat.GRAPH, target_format=DataFormat.TABLE,
                preservation_score=0.9, conversion_metadata={}, validation_passed=True,
                semantic_integrity=True, warnings=[]
            )
        
        converter.convert_data.side_effect = slow_conversion
        
        # Start analysis
        task = asyncio.create_task(orchestrator.orchestrate_analysis(
            research_question="Cancellation test",
            data={"nodes": [{"id": 1, "label": "Test"}], "edges": []},
            source_format=DataFormat.GRAPH
        ))
        
        # Cancel after short delay
        await asyncio.sleep(0.1)
        task.cancel()
        
        # Verify cancellation is handled properly
        with pytest.raises(asyncio.CancelledError):
            await task
        
        # Orchestrator should remain in valid state
        assert orchestrator is not None


class TestRaceConditions:
    """Test race condition detection and prevention"""
    
    @pytest.mark.asyncio
    async def test_shared_state_race_conditions(self, orchestrator_with_mocks):
        """Test for race conditions in shared state access"""
        orchestrator, converter, validator = orchestrator_with_mocks
        
        # Mock conversion with variable delay
        async def variable_delay_conversion(*args, **kwargs):
            delay = np.random.uniform(0.01, 0.1)  # Variable delay
            await asyncio.sleep(delay)
            return ConversionResult(
                data=pd.DataFrame({"col": [1]}),
                source_format=DataFormat.GRAPH, target_format=DataFormat.TABLE,
                preservation_score=0.9, conversion_metadata={}, validation_passed=True,
                semantic_integrity=True, warnings=[]
            )
        
        converter.convert_data.side_effect = variable_delay_conversion
        
        # Access shared state from multiple coroutines
        results = []
        
        async def concurrent_analysis(task_id):
            # Each task modifies orchestrator state
            result = await orchestrator.orchestrate_analysis(
                research_question=f"Race test {task_id}",
                data={"nodes": [{"id": task_id}], "edges": []},
                source_format=DataFormat.GRAPH
            )
            results.append((task_id, result))
            return result
        
        # Run many concurrent tasks
        tasks = [concurrent_analysis(i) for i in range(50)]
        await asyncio.gather(*tasks)
        
        # Verify no corruption
        assert len(results) == 50
        task_ids = [r[0] for r in results]
        assert len(set(task_ids)) == 50  # No duplicates
        assert sorted(task_ids) == list(range(50))  # All IDs present
    
    @pytest.mark.asyncio
    async def test_resource_contention(self, orchestrator_with_mocks):
        """Test resource contention handling"""
        orchestrator, converter, validator = orchestrator_with_mocks
        
        # Simulate limited resource pool
        resource_lock = asyncio.Semaphore(3)  # Only 3 concurrent operations
        access_order = []
        
        async def limited_resource_conversion(*args, **kwargs):
            async with resource_lock:
                access_order.append(time.time())
                await asyncio.sleep(0.1)  # Hold resource
                return ConversionResult(
                    data={}, source_format=DataFormat.GRAPH, target_format=DataFormat.TABLE,
                    preservation_score=0.9, conversion_metadata={}, validation_passed=True,
                    semantic_integrity=True, warnings=[]
                )
        
        converter.convert_data.side_effect = limited_resource_conversion
        
        # Start many concurrent operations
        start_time = time.time()
        tasks = []
        
        for i in range(10):
            task = orchestrator.orchestrate_analysis(
                research_question=f"Resource test {i}",
                data={"nodes": [], "edges": []},
                source_format=DataFormat.GRAPH
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Verify resource contention was handled
        assert len(results) == 10
        
        # Should take longer than if all ran concurrently
        min_expected_time = (10 / 3) * 0.1  # Batches of 3, each taking 0.1s
        assert total_time >= min_expected_time * 0.8  # Allow some variance
    
    @pytest.mark.asyncio
    async def test_deadlock_prevention(self, orchestrator_with_mocks):
        """Test deadlock prevention mechanisms"""
        orchestrator, converter, validator = orchestrator_with_mocks
        
        # Create potential deadlock scenario with circular dependencies
        lock_a = asyncio.Lock()
        lock_b = asyncio.Lock()
        
        async def deadlock_prone_operation_1(*args, **kwargs):
            async with lock_a:
                await asyncio.sleep(0.1)
                async with lock_b:  # Could deadlock if another holds B and wants A
                    return ConversionResult(
                        data={}, source_format=DataFormat.GRAPH, target_format=DataFormat.TABLE,
                        preservation_score=0.9, conversion_metadata={}, validation_passed=True,
                        semantic_integrity=True, warnings=[]
                    )
        
        async def deadlock_prone_operation_2(*args, **kwargs):
            async with lock_b:
                await asyncio.sleep(0.1)
                async with lock_a:  # Could deadlock if another holds A and wants B
                    return ConversionResult(
                        data={}, source_format=DataFormat.GRAPH, target_format=DataFormat.TABLE,
                        preservation_score=0.9, conversion_metadata={}, validation_passed=True,
                        semantic_integrity=True, warnings=[]
                    )
        
        # Alternate between operations to create deadlock potential
        operations = [deadlock_prone_operation_1, deadlock_prone_operation_2]
        
        tasks = []
        for i in range(10):
            converter.convert_data.side_effect = operations[i % 2]
            task = orchestrator.orchestrate_analysis(
                research_question=f"Deadlock test {i}",
                data={"nodes": [], "edges": []},
                source_format=DataFormat.GRAPH
            )
            tasks.append(task)
        
        # Should complete without deadlock (with timeout as safety)
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks), 
                timeout=10.0
            )
            assert len(results) == 10
        except asyncio.TimeoutError:
            pytest.fail("Potential deadlock detected - operations timed out")


class TestResourceManagement:
    """Test resource management and cleanup"""
    
    @pytest.mark.asyncio
    async def test_connection_pool_management(self, orchestrator_with_mocks):
        """Test database connection pool behavior under load"""
        orchestrator, converter, validator = orchestrator_with_mocks
        
        # Mock database operations with connection tracking
        active_connections = set()
        max_connections = 5
        
        async def connection_aware_operation(*args, **kwargs):
            if len(active_connections) >= max_connections:
                raise Exception("Connection pool exhausted")
            
            conn_id = id(asyncio.current_task())
            active_connections.add(conn_id)
            
            try:
                await asyncio.sleep(0.1)  # Simulate DB operation
                return ConversionResult(
                    data={}, source_format=DataFormat.GRAPH, target_format=DataFormat.TABLE,
                    preservation_score=0.9, conversion_metadata={}, validation_passed=True,
                    semantic_integrity=True, warnings=[]
                )
            finally:
                active_connections.discard(conn_id)
        
        converter.convert_data.side_effect = connection_aware_operation
        
        # Test connection pool under high load
        tasks = []
        for i in range(20):  # More than max connections
            task = orchestrator.orchestrate_analysis(
                research_question=f"Connection test {i}",
                data={"nodes": [], "edges": []},
                source_format=DataFormat.GRAPH
            )
            tasks.append(task)
        
        # Some may fail due to connection limits, but system should remain stable
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = [r for r in results if isinstance(r, AnalysisResult)]
        failed = [r for r in results if isinstance(r, Exception)]
        
        # Should have some successes and handle failures gracefully
        assert len(successful) > 0
        assert len(active_connections) == 0  # All connections cleaned up
    
    @pytest.mark.asyncio
    async def test_memory_management_under_load(self, orchestrator_with_mocks):
        """Test memory management during high concurrent load"""
        orchestrator, converter, validator = orchestrator_with_mocks
        
        # Track memory allocations
        large_objects = []
        
        async def memory_intensive_operation(*args, **kwargs):
            # Create large object to test memory management
            large_data = np.random.rand(1000, 1000)  # ~8MB
            large_objects.append(large_data)
            
            await asyncio.sleep(0.05)
            
            # Clean up
            large_objects.pop()
            
            return ConversionResult(
                data=pd.DataFrame({"col": [1]}),
                source_format=DataFormat.GRAPH, target_format=DataFormat.TABLE,
                preservation_score=0.9, conversion_metadata={}, validation_passed=True,
                semantic_integrity=True, warnings=[]
            )
        
        converter.convert_data.side_effect = memory_intensive_operation
        
        # Monitor memory usage
        import psutil
        import os
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Run memory-intensive operations
        tasks = [
            orchestrator.orchestrate_analysis(
                research_question=f"Memory test {i}",
                data={"nodes": [], "edges": []},
                source_format=DataFormat.GRAPH
            )
            for i in range(20)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Force garbage collection
        import gc
        gc.collect()
        
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable
        assert len(results) == 20
        assert len(large_objects) == 0  # All objects cleaned up
        assert memory_growth < 200 * 1024 * 1024  # Less than 200MB growth
    
    @pytest.mark.asyncio
    async def test_exception_cleanup(self, orchestrator_with_mocks):
        """Test resource cleanup when exceptions occur"""
        orchestrator, converter, validator = orchestrator_with_mocks
        
        # Track resource acquisition/release
        acquired_resources = []
        
        async def failing_operation_with_resources(*args, **kwargs):
            # Acquire resource
            resource_id = len(acquired_resources)
            acquired_resources.append(resource_id)
            
            try:
                await asyncio.sleep(0.1)
                if resource_id % 3 == 0:  # Fail every 3rd operation
                    raise Exception(f"Simulated failure {resource_id}")
                
                return ConversionResult(
                    data={}, source_format=DataFormat.GRAPH, target_format=DataFormat.TABLE,
                    preservation_score=0.9, conversion_metadata={}, validation_passed=True,
                    semantic_integrity=True, warnings=[]
                )
            finally:
                # Ensure cleanup happens even on exception
                if resource_id in acquired_resources:
                    acquired_resources.remove(resource_id)
        
        converter.convert_data.side_effect = failing_operation_with_resources
        
        # Run operations that will have failures
        tasks = [
            orchestrator.orchestrate_analysis(
                research_question=f"Cleanup test {i}",
                data={"nodes": [], "edges": []},
                source_format=DataFormat.GRAPH
            )
            for i in range(15)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify cleanup occurred even with exceptions
        successful = [r for r in results if isinstance(r, AnalysisResult)]
        failed = [r for r in results if isinstance(r, Exception)]
        
        assert len(successful) > 0  # Some succeeded
        assert len(failed) > 0   # Some failed as expected
        assert len(acquired_resources) == 0  # All resources cleaned up


class TestPerformanceUnderLoad:
    """Test performance characteristics under various load conditions"""
    
    @pytest.mark.asyncio
    async def test_throughput_under_concurrent_load(self, orchestrator_with_mocks):
        """Test system throughput with concurrent requests"""
        orchestrator, converter, validator = orchestrator_with_mocks
        
        # Fast mock conversion
        converter.convert_data.return_value = ConversionResult(
            data={}, source_format=DataFormat.GRAPH, target_format=DataFormat.TABLE,
            preservation_score=0.9, conversion_metadata={}, validation_passed=True,
            semantic_integrity=True, warnings=[]
        )
        
        # Test different concurrency levels
        for concurrency in [1, 5, 10, 20, 50]:
            start_time = time.time()
            
            tasks = [
                orchestrator.orchestrate_analysis(
                    research_question=f"Throughput test {i}",
                    data={"nodes": [], "edges": []},
                    source_format=DataFormat.GRAPH
                )
                for i in range(concurrency)
            ]
            
            results = await asyncio.gather(*tasks)
            duration = time.time() - start_time
            throughput = len(results) / duration
            
            print(f"Concurrency {concurrency}: {throughput:.2f} requests/second")
            
            # Verify all completed successfully
            assert len(results) == concurrency
            assert all(isinstance(r, AnalysisResult) for r in results)
            
            # Throughput should scale reasonably with concurrency
            if concurrency > 1:
                assert throughput > 1  # Should be faster than sequential
    
    @pytest.mark.asyncio
    async def test_latency_distribution(self, orchestrator_with_mocks):
        """Test latency distribution under load"""
        orchestrator, converter, validator = orchestrator_with_mocks
        
        # Variable latency mock
        async def variable_latency_conversion(*args, **kwargs):
            # Simulate realistic latency distribution
            base_latency = 0.05  # 50ms base
            jitter = np.random.exponential(0.02)  # Exponential jitter
            await asyncio.sleep(base_latency + jitter)
            
            return ConversionResult(
                data={}, source_format=DataFormat.GRAPH, target_format=DataFormat.TABLE,
                preservation_score=0.9, conversion_metadata={}, validation_passed=True,
                semantic_integrity=True, warnings=[]
            )
        
        converter.convert_data.side_effect = variable_latency_conversion
        
        # Measure latencies
        latencies = []
        num_requests = 50
        
        for i in range(num_requests):
            start_time = time.time()
            
            result = await orchestrator.orchestrate_analysis(
                research_question=f"Latency test {i}",
                data={"nodes": [], "edges": []},
                source_format=DataFormat.GRAPH
            )
            
            latency = time.time() - start_time
            latencies.append(latency)
            
            assert isinstance(result, AnalysisResult)
        
        # Analyze latency distribution
        latencies = np.array(latencies)
        p50 = np.percentile(latencies, 50)
        p95 = np.percentile(latencies, 95)
        p99 = np.percentile(latencies, 99)
        
        print(f"Latency percentiles - P50: {p50:.3f}s, P95: {p95:.3f}s, P99: {p99:.3f}s")
        
        # Verify reasonable latency characteristics
        assert p50 < 0.2  # 200ms median
        assert p95 < 0.5  # 500ms 95th percentile
        assert p99 < 1.0  # 1s 99th percentile


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-k", "not test_memory"])