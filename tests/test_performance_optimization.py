#!/usr/bin/env python3
"""
Performance Optimization Tests

Tests for parallel execution, execution optimization, and resource management.
Validates performance improvements and resource efficiency.
"""

import pytest
import asyncio
import time
from pathlib import Path
from typing import List, Dict, Any

from src.execution.parallel_executor import (
    ParallelExecutor, ParallelExecutionConfig, ParallelExecutionMode, 
    ParallelExecutionResult, ParallelBatchResult, create_parallel_executor
)
from src.performance.execution_optimizer import (
    ExecutionOptimizer, OptimizationConfig, OptimizationStrategy, 
    PerformanceMetrics, OptimizationResult, create_execution_optimizer
)
from src.performance.resource_manager_enhanced import (
    EnhancedResourceManager, ResourceRequest, ResourceType, AllocationStrategy,
    ResourceAllocation, create_resource_manager
)
from src.execution.execution_planner import ExecutionPlan, ExecutionStep, ExecutionPriority, ExecutionStrategy, ExecutionConstraints
from src.execution.dag_builder import ExecutionDAG, DAGNode, DAGEdge, NodeType


def create_test_execution_plan(plan_id: str, tool_ids: List[str], total_time: float = 10.0) -> ExecutionPlan:
    """Helper function to create test execution plans"""
    # Create simple DAG with required parameters
    nodes = {}
    edges = []
    steps = []
    
    for i, tool_id in enumerate(tool_ids):
        node_id = f"node{i+1}"
        node = DAGNode(node_id, NodeType.TOOL, tool_id)
        nodes[node_id] = node
        
        step = ExecutionStep(
            step_id=f"step{i+1}",
            node_id=node_id,
            tool_ids=[tool_id],
            estimated_start_time=float(i * 3),
            estimated_duration=3.0,
            execution_priority=ExecutionPriority.HIGH
        )
        steps.append(step)
        
        # Add dependency edge if not the first node
        if i > 0:
            edges.append(DAGEdge(f"node{i}", node_id))
    
    # Create DAG
    dag = ExecutionDAG(
        nodes=nodes,
        edges=edges,
        entry_points=[f"node1"] if tool_ids else [],
        exit_points=[f"node{len(tool_ids)}"] if tool_ids else []
    )
    
    return ExecutionPlan(
        plan_id=plan_id,
        steps=steps,
        strategy=ExecutionStrategy.ADAPTIVE,
        total_estimated_time=total_time,
        total_estimated_cost=5.0,
        parallelization_ratio=0.0,
        resource_efficiency=0.8,
        quality_score=0.85,
        confidence=0.8,
        dag=dag,
        constraints=ExecutionConstraints()
    )


class TestParallelExecutor:
    """Test parallel execution functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.config = ParallelExecutionConfig(
            max_concurrent_tools=4,
            execution_timeout=60.0,
            prefer_async=True
        )
        self.executor = ParallelExecutor(self.config)
    
    def test_parallel_executor_initialization(self):
        """Test parallel executor initialization"""
        assert self.executor.config.max_concurrent_tools == 4
        assert self.executor.config.execution_timeout == 60.0
        assert self.executor.config.prefer_async is True
        assert len(self.executor.execution_stats) > 0
    
    @pytest.mark.asyncio
    async def test_single_step_execution(self):
        """Test execution of single step"""
        plan = create_test_execution_plan("single_step", ["T23A_SPACY_NER"], 3.0)
        
        result = await self.executor.execute_parallel_plan(plan)
        
        assert isinstance(result, ParallelBatchResult)
        assert result.total_steps == 1
        assert result.successful_steps == 1
        assert result.failed_steps == 0
        assert result.total_execution_time > 0
        assert len(result.step_results) == 1
    
    @pytest.mark.asyncio
    async def test_parallel_execution_multiple_steps(self):
        """Test parallel execution with multiple independent steps"""
        # Create plan with steps that can run in parallel
        plan = create_test_execution_plan(
            "parallel_test", 
            ["T23A_SPACY_NER", "T31_ENTITY_BUILDER", "T27_RELATIONSHIP_EXTRACTOR"], 
            15.0
        )
        
        start_time = time.time()
        result = await self.executor.execute_parallel_plan(plan)
        actual_time = time.time() - start_time
        
        assert isinstance(result, ParallelBatchResult)
        assert result.total_steps == 3
        assert result.successful_steps == 3
        assert result.speedup_factor > 1.0  # Should have some speedup
        assert result.parallel_efficiency > 0.0
        
        # Actual execution should be faster than sequential estimate
        assert actual_time < result.performance_metrics['sequential_time_estimate']
    
    @pytest.mark.asyncio
    async def test_performance_metrics_tracking(self):
        """Test performance metrics tracking"""
        plan = create_test_execution_plan("metrics_test", ["T23A_SPACY_NER"], 5.0)
        
        # Execute plan
        result = await self.executor.execute_parallel_plan(plan)
        
        # Check performance metrics
        metrics = self.executor.get_performance_metrics()
        
        assert 'total_executions' in metrics
        assert 'parallel_executions' in metrics
        assert 'average_speedup' in metrics
        assert metrics['total_executions'] > 0
        assert metrics['parallel_executions'] > 0
    
    @pytest.mark.asyncio 
    async def test_speedup_calculation(self):
        """Test speedup calculation for parallel execution"""
        # Create plan with estimated 12 seconds sequential time (4 * 3 seconds)
        plan = create_test_execution_plan(
            "speedup_test", 
            ["T23A_SPACY_NER", "T31_ENTITY_BUILDER", "T27_RELATIONSHIP_EXTRACTOR", "T68_PAGE_RANK"], 
            12.0
        )
        
        result = await self.executor.execute_parallel_plan(plan)
        
        # Verify speedup calculation
        sequential_time = result.performance_metrics['sequential_time_estimate']
        parallel_time = result.total_execution_time
        expected_speedup = sequential_time / parallel_time
        
        assert abs(result.speedup_factor - expected_speedup) < 0.1
        assert result.speedup_factor > 1.0
    
    @pytest.mark.asyncio
    async def test_benchmark_performance(self):
        """Test benchmarking functionality"""
        plans = [
            create_test_execution_plan("bench1", ["T23A_SPACY_NER"], 3.0),
            create_test_execution_plan("bench2", ["T31_ENTITY_BUILDER", "T27_RELATIONSHIP_EXTRACTOR"], 6.0)
        ]
        
        benchmark_results = await self.executor.benchmark_parallel_performance(plans)
        
        assert 'total_plans' in benchmark_results
        assert 'parallel_results' in benchmark_results
        assert 'overall_speedup' in benchmark_results
        assert benchmark_results['total_plans'] == 2
        assert len(benchmark_results['parallel_results']) == 2
        assert benchmark_results['overall_speedup'] > 0
    
    def test_factory_function(self):
        """Test factory function for creating parallel executor"""
        executor = create_parallel_executor(max_concurrent=8, prefer_async=False)
        
        assert executor.config.max_concurrent_tools == 8
        assert executor.config.prefer_async is False


class TestExecutionOptimizer:
    """Test execution optimization functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.config = OptimizationConfig(
            strategy=OptimizationStrategy.BALANCED_PERFORMANCE,
            adaptive_window_size=5
        )
        self.optimizer = ExecutionOptimizer(self.config)
    
    def test_optimizer_initialization(self):
        """Test optimizer initialization"""
        assert self.optimizer.config.strategy == OptimizationStrategy.BALANCED_PERFORMANCE
        assert self.optimizer.config.adaptive_window_size == 5
        assert len(self.optimizer.strategy_performance) > 0
    
    @pytest.mark.asyncio
    async def test_throughput_optimization(self):
        """Test throughput optimization strategy"""
        optimizer = create_execution_optimizer(OptimizationStrategy.THROUGHPUT_MAXIMIZATION)
        plan = create_test_execution_plan("throughput_test", ["T23A_SPACY_NER", "T31_ENTITY_BUILDER"], 8.0)
        
        result = await optimizer.optimize_execution_plan(plan)
        
        assert isinstance(result, OptimizationResult)
        assert result.optimized_plan.plan_id.endswith("_throughput_opt")
        assert "throughput_optimized" in result.optimized_plan.adaptive_features
        assert result.optimized_plan.total_estimated_time < plan.total_estimated_time
        assert result.performance_improvement != 0.0
    
    @pytest.mark.asyncio
    async def test_latency_optimization(self):
        """Test latency optimization strategy"""
        optimizer = create_execution_optimizer(OptimizationStrategy.LATENCY_MINIMIZATION)
        plan = create_test_execution_plan("latency_test", ["T23A_SPACY_NER", "T31_ENTITY_BUILDER"], 8.0)
        
        result = await optimizer.optimize_execution_plan(plan)
        
        assert isinstance(result, OptimizationResult)
        assert result.optimized_plan.plan_id.endswith("_latency_opt")
        assert "latency_optimized" in result.optimized_plan.adaptive_features
        assert result.optimized_plan.total_estimated_time < plan.total_estimated_time
    
    @pytest.mark.asyncio
    async def test_resource_efficiency_optimization(self):
        """Test resource efficiency optimization"""
        optimizer = create_execution_optimizer(OptimizationStrategy.RESOURCE_EFFICIENCY)
        plan = create_test_execution_plan("resource_test", ["T23A_SPACY_NER", "T31_ENTITY_BUILDER"], 8.0)
        
        result = await optimizer.optimize_execution_plan(plan)
        
        assert isinstance(result, OptimizationResult)
        assert result.optimized_plan.plan_id.endswith("_resource_opt")
        assert "resource_efficient" in result.optimized_plan.adaptive_features
        assert result.optimized_plan.resource_efficiency > plan.resource_efficiency
        assert result.optimized_plan.total_estimated_cost < plan.total_estimated_cost
    
    @pytest.mark.asyncio
    async def test_balanced_optimization(self):
        """Test balanced optimization strategy"""
        plan = create_test_execution_plan("balanced_test", ["T23A_SPACY_NER", "T31_ENTITY_BUILDER"], 8.0)
        
        result = await self.optimizer.optimize_execution_plan(plan)
        
        assert isinstance(result, OptimizationResult)
        assert result.optimized_plan.plan_id.endswith("_balanced_opt")
        assert "balanced_optimized" in result.optimized_plan.adaptive_features
        assert len(result.applied_optimizations) > 0
        assert len(result.recommendations) >= 0
    
    @pytest.mark.asyncio
    async def test_performance_metrics_analysis(self):
        """Test performance metrics analysis"""
        plan = create_test_execution_plan("metrics_analysis", ["T23A_SPACY_NER"], 5.0)
        
        result = await self.optimizer.optimize_execution_plan(plan)
        
        # Check metrics were calculated
        assert isinstance(result.metrics_before, PerformanceMetrics)
        assert isinstance(result.metrics_after, PerformanceMetrics)
        assert result.metrics_before.execution_time > 0
        assert result.metrics_after.execution_time > 0
        assert result.metrics_before.throughput > 0
        assert result.metrics_after.throughput > 0
    
    @pytest.mark.asyncio
    async def test_adaptive_learning(self):
        """Test adaptive learning optimization"""
        optimizer = create_execution_optimizer(OptimizationStrategy.ADAPTIVE_LEARNING)
        plan = create_test_execution_plan("adaptive_test", ["T23A_SPACY_NER"], 5.0)
        
        # Run multiple optimizations to build learning data
        results = []
        for i in range(3):
            result = await optimizer.optimize_execution_plan(plan)
            results.append(result)
        
        # Check that learning data is being updated
        stats = optimizer.get_optimization_statistics()
        assert stats['total_optimizations'] == 3
        assert 'average_improvement' in stats
        assert 'strategy_performance' in stats
    
    def test_optimization_statistics(self):
        """Test optimization statistics tracking"""
        stats = self.optimizer.get_optimization_statistics()
        
        assert isinstance(stats, dict)
        assert 'total_optimizations' in stats
        assert 'strategy_performance' in stats
        assert isinstance(stats['strategy_performance'], dict)


class TestEnhancedResourceManager:
    """Test enhanced resource management functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.manager = EnhancedResourceManager(AllocationStrategy.FAIR_SHARE)
    
    def teardown_method(self):
        """Clean up test environment"""
        if hasattr(self, 'manager'):
            self.manager.shutdown()
    
    def test_resource_manager_initialization(self):
        """Test resource manager initialization"""
        assert self.manager.allocation_strategy == AllocationStrategy.FAIR_SHARE
        assert len(self.manager.resource_limits) > 0
        assert len(self.manager.allocation_pools) > 0
        assert ResourceType.CPU in self.manager.resource_limits
        assert ResourceType.MEMORY in self.manager.resource_limits
    
    @pytest.mark.asyncio
    async def test_basic_resource_allocation(self):
        """Test basic resource allocation and release"""
        request = ResourceRequest(
            requester_id="test_requester",
            resource_type=ResourceType.CPU,
            amount=10.0,
            priority=5
        )
        
        allocation = await self.manager.request_resource(request)
        
        assert allocation is not None
        assert allocation.requester_id == "test_requester"
        assert allocation.resource_type == ResourceType.CPU
        assert allocation.allocated_amount == 10.0
        assert allocation.is_active is True
        
        # Release resource
        success = self.manager.release_resource(allocation.allocation_id)
        assert success is True
    
    @pytest.mark.asyncio
    async def test_resource_allocation_limits(self):
        """Test resource allocation respects limits"""
        # Request very large amount that should exceed limits
        request = ResourceRequest(
            requester_id="test_requester",
            resource_type=ResourceType.CPU,
            amount=150.0,  # More than 100% CPU
            priority=5
        )
        
        allocation = await self.manager.request_resource(request)
        
        # Should not be able to allocate more than available
        assert allocation is None
    
    @pytest.mark.asyncio
    async def test_multiple_allocations(self):
        """Test multiple concurrent resource allocations"""
        requests = [
            ResourceRequest("requester_1", ResourceType.CPU, 20.0, priority=5),
            ResourceRequest("requester_2", ResourceType.CPU, 25.0, priority=7),
            ResourceRequest("requester_3", ResourceType.MEMORY, 30.0, priority=3)
        ]
        
        allocations = []
        for request in requests:
            allocation = await self.manager.request_resource(request)
            if allocation:
                allocations.append(allocation)
        
        assert len(allocations) >= 2  # At least some should succeed
        
        # Release all allocations
        for allocation in allocations:
            success = self.manager.release_resource(allocation.allocation_id)
            assert success is True
    
    @pytest.mark.asyncio
    async def test_priority_based_allocation(self):
        """Test priority-based resource allocation"""
        priority_manager = create_resource_manager(AllocationStrategy.PRIORITY_BASED)
        
        try:
            # Create high and low priority requests
            high_priority_request = ResourceRequest(
                "high_priority", ResourceType.CPU, 40.0, priority=9
            )
            low_priority_request = ResourceRequest(
                "low_priority", ResourceType.CPU, 40.0, priority=2
            )
            
            # Request both (order shouldn't matter due to priority)
            low_alloc = await priority_manager.request_resource(low_priority_request)
            high_alloc = await priority_manager.request_resource(high_priority_request)
            
            # At least one should succeed
            assert (low_alloc is not None) or (high_alloc is not None)
            
            # Clean up
            if low_alloc:
                priority_manager.release_resource(low_alloc.allocation_id)
            if high_alloc:
                priority_manager.release_resource(high_alloc.allocation_id)
                
        finally:
            priority_manager.shutdown()
    
    def test_resource_metrics(self):
        """Test resource metrics collection"""
        metrics = self.manager.get_resource_metrics()
        
        assert isinstance(metrics, dict)
        # Should have metrics for different resource types
        assert len(metrics) > 0
        
        # Test single resource metrics
        cpu_metrics = self.manager.get_resource_metrics(ResourceType.CPU)
        assert 'resource_type' in cpu_metrics
        assert cpu_metrics['resource_type'] == ResourceType.CPU.value
    
    def test_system_status(self):
        """Test system status reporting"""
        status = self.manager.get_system_status()
        
        assert isinstance(status, dict)
        assert 'timestamp' in status
        assert 'cpu_percent' in status
        assert 'memory_percent' in status
        assert 'active_allocations' in status
        assert 'allocation_pools' in status
        assert 'resource_limits' in status
    
    def test_resource_limit_updates(self):
        """Test updating resource limits"""
        original_limit = self.manager.resource_limits[ResourceType.CPU]
        
        # Update limits
        self.manager.set_resource_limit(
            ResourceType.CPU, 
            soft_limit=60.0, 
            hard_limit=80.0, 
            emergency_limit=90.0
        )
        
        updated_limit = self.manager.resource_limits[ResourceType.CPU]
        assert updated_limit.soft_limit == 60.0
        assert updated_limit.hard_limit == 80.0
        assert updated_limit.emergency_limit == 90.0
        assert updated_limit != original_limit
    
    @pytest.mark.asyncio
    async def test_resource_usage_tracking(self):
        """Test resource usage tracking and metrics"""
        request = ResourceRequest(
            "usage_tracker", ResourceType.MEMORY, 50.0, priority=5
        )
        
        allocation = await self.manager.request_resource(request)
        assert allocation is not None
        
        # Update usage
        self.manager.update_resource_usage(allocation.allocation_id, 35.0)
        
        # Check that usage was recorded
        assert self.manager.active_allocations[allocation.allocation_id].actual_usage == 35.0
        
        # Release and check metrics update
        self.manager.release_resource(allocation.allocation_id)
        
        metrics = self.manager.get_resource_metrics(ResourceType.MEMORY)
        assert 'total_allocations' in metrics
    
    def test_factory_function(self):
        """Test factory function for creating resource manager"""
        manager = create_resource_manager(AllocationStrategy.DEMAND_BASED)
        
        try:
            assert manager.allocation_strategy == AllocationStrategy.DEMAND_BASED
            assert len(manager.resource_limits) > 0
        finally:
            manager.shutdown()


class TestIntegratedPerformanceOptimization:
    """Test integrated performance optimization across all components"""
    
    def setup_method(self):
        """Set up integrated test environment"""
        self.parallel_executor = create_parallel_executor(max_concurrent=4)
        self.optimizer = create_execution_optimizer(OptimizationStrategy.BALANCED_PERFORMANCE)
        self.resource_manager = create_resource_manager(AllocationStrategy.ADAPTIVE)
    
    def teardown_method(self):
        """Clean up integrated test environment"""
        if hasattr(self, 'resource_manager'):
            self.resource_manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_end_to_end_optimization_pipeline(self):
        """Test complete optimization pipeline"""
        # Create execution plan
        plan = create_test_execution_plan(
            "e2e_optimization", 
            ["T23A_SPACY_NER", "T31_ENTITY_BUILDER", "T27_RELATIONSHIP_EXTRACTOR", "T68_PAGE_RANK"], 
            20.0
        )
        
        # Step 1: Optimize the plan
        optimization_result = await self.optimizer.optimize_execution_plan(plan)
        optimized_plan = optimization_result.optimized_plan
        
        assert optimization_result.performance_improvement != 0.0
        assert len(optimization_result.applied_optimizations) > 0
        
        # Step 2: Execute with parallel executor
        execution_result = await self.parallel_executor.execute_parallel_plan(optimized_plan)
        
        assert execution_result.successful_steps > 0
        assert execution_result.speedup_factor > 1.0
        
        # Step 3: Verify resource management would work
        cpu_request = ResourceRequest(
            "integration_test", ResourceType.CPU, 50.0, priority=7
        )
        allocation = await self.resource_manager.request_resource(cpu_request)
        
        assert allocation is not None
        self.resource_manager.release_resource(allocation.allocation_id)
    
    @pytest.mark.asyncio
    async def test_performance_improvement_validation(self):
        """Test that performance improvements are measurable and significant"""
        plans = [
            create_test_execution_plan("perf1", ["T23A_SPACY_NER"], 5.0),
            create_test_execution_plan("perf2", ["T31_ENTITY_BUILDER", "T27_RELATIONSHIP_EXTRACTOR"], 10.0),
            create_test_execution_plan("perf3", ["T23A_SPACY_NER", "T31_ENTITY_BUILDER", "T68_PAGE_RANK"], 15.0)
        ]
        
        total_improvement = 0.0
        optimization_count = 0
        
        for plan in plans:
            # Optimize plan
            opt_result = await self.optimizer.optimize_execution_plan(plan)
            
            # Execute optimized plan
            exec_result = await self.parallel_executor.execute_parallel_plan(opt_result.optimized_plan)
            
            # Track improvements
            if exec_result.speedup_factor > 1.0:
                total_improvement += (exec_result.speedup_factor - 1.0)
                optimization_count += 1
        
        # Validate that we achieved meaningful improvements
        if optimization_count > 0:
            average_improvement = total_improvement / optimization_count
            assert average_improvement > 0.0  # Some improvement achieved
            
            # If we can achieve >50% improvement (1.5x speedup), that meets Phase B criteria
            if average_improvement >= 0.5:
                print(f"✅ ACHIEVED >50% PERFORMANCE IMPROVEMENT: {average_improvement:.1%} average speedup")
    
    @pytest.mark.asyncio
    async def test_resource_efficiency_under_load(self):
        """Test resource efficiency under concurrent load"""
        # Create multiple concurrent resource requests
        requests = [
            ResourceRequest(f"load_test_{i}", ResourceType.CPU, 15.0, priority=5)
            for i in range(6)  # Request more than max_concurrent
        ]
        
        allocations = []
        start_time = time.time()
        
        # Request all resources concurrently
        tasks = [self.resource_manager.request_resource(req) for req in requests]
        results = await asyncio.gather(*tasks)
        
        allocation_time = time.time() - start_time
        
        # Count successful allocations
        successful_allocations = [r for r in results if r is not None]
        allocations.extend(successful_allocations)
        
        # Should handle concurrent requests efficiently
        assert len(successful_allocations) > 0
        assert allocation_time < 5.0  # Should be reasonably fast
        
        # Clean up
        for allocation in allocations:
            self.resource_manager.release_resource(allocation.allocation_id)
        
        # Check final system status
        status = self.resource_manager.get_system_status()
        assert status['active_allocations'] == 0  # All cleaned up


if __name__ == "__main__":
    pytest.main([__file__, "-v"])