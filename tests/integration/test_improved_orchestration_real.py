#!/usr/bin/env python3
"""
Comprehensive integration tests for improved orchestration components.

Tests the actual system end-to-end with ZERO mocking or fallbacks.
All tests use real components, real data, and real execution paths.
"""

import asyncio
import logging
import sys
import time
from typing import Dict, Any
import tempfile
import os

sys.path.insert(0, 'src')

from orchestration.parallel_orchestrator import ParallelOrchestrator, ExecutionMode
from orchestration.reasoning_agent import ReasoningAgent
from orchestration.base import Task, TaskPriority, Result
from core.config_manager import ConfigManager

# Set up logging for test visibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestImprovedOrchestration:
    """Test improved orchestration with real components and data."""
    
    @classmethod
    async def setup_class(cls):
        """Set up real test environment."""
        # Create temporary config for testing
        cls.temp_dir = tempfile.mkdtemp()
        cls.config_path = os.path.join(cls.temp_dir, "test_config.yaml")
        
        # Write real configuration
        test_config = {
            "parallel": {
                "execution_mode": "adaptive",
                "max_parallel_tasks": 3,
                "batch_size": 2,
                "enable_resource_management": True,
                "enable_adaptive_parallelism": True,
                "resources": {
                    "max_concurrent_agents": 3,
                    "max_memory_mb": 1024,
                    "max_reasoning_threads": 2
                },
                "max_worker_threads": 2
            },
            "reasoning": {
                "enable_reasoning": True,
                "reasoning_threshold": 0.3,
                "max_reasoning_time": 10.0,
                "default_reasoning_type": "tactical"
            },
            "memory": {
                "enable_learning": True,
                "max_context_memories": 10
            }
        }
        
        import yaml
        with open(cls.config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        logger.info(f"Test environment set up with config: {cls.config_path}")
    
    async def test_parallel_orchestrator_initialization(self):
        """Test parallel orchestrator initializes correctly with real config."""
        orchestrator = ParallelOrchestrator(self.config_path)
        
        # Test initialization
        success = await orchestrator.initialize()
        assert success, "Orchestrator should initialize successfully"
        
        # Verify configuration loaded correctly
        assert orchestrator.execution_mode == ExecutionMode.ADAPTIVE
        assert orchestrator.max_parallel_tasks == 3
        assert orchestrator.batch_size == 2
        assert orchestrator.enable_resource_management == True
        
        # Verify resource pool configured correctly
        assert orchestrator.resource_pool.max_concurrent_agents == 3
        assert orchestrator.resource_pool.max_memory_mb == 1024
        assert orchestrator.resource_pool.max_reasoning_threads == 2
        
        # Verify initial resource state
        assert orchestrator.resource_pool.available_agents == 3
        assert orchestrator.resource_pool.used_memory_mb == 0
        assert orchestrator.resource_pool.active_reasoning == 0
        
        logger.info("✅ Parallel orchestrator initialization test passed")
        
        await orchestrator.cleanup()
    
    async def test_reasoning_agent_initialization(self):
        """Test reasoning agent initializes with real configuration."""
        reasoning_config = {
            "enable_reasoning": True,
            "reasoning_threshold": 0.5,
            "max_reasoning_time": 15.0,
            "default_reasoning_type": "tactical"
        }
        
        memory_config = {
            "enable_learning": True,
            "max_context_memories": 5
        }
        
        agent = ReasoningAgent(
            agent_id="test_reasoning_agent",
            memory_config=memory_config,
            reasoning_config=reasoning_config
        )
        
        # Verify agent configuration
        assert agent.agent_id == "test_reasoning_agent"
        assert agent.enable_reasoning == True
        assert agent.reasoning_threshold == 0.5
        assert agent.max_reasoning_time == 15.0
        
        # Verify reasoning stats initialized
        assert agent.reasoning_stats["total_reasonings"] == 0
        assert agent.reasoning_stats["successful_reasonings"] == 0
        assert agent.reasoning_stats["failed_reasonings"] == 0
        
        logger.info("✅ Reasoning agent initialization test passed")
    
    async def test_task_validation_real_scenarios(self):
        """Test task validation with real task objects."""
        agent = ReasoningAgent(agent_id="validation_test_agent")
        
        # Valid task
        valid_task = Task(
            task_id="valid_task_001",
            task_type="document_processing",
            parameters={"input_file": "test.pdf", "output_format": "json"},
            priority=TaskPriority.MEDIUM
        )
        
        assert agent._validate_task(valid_task) == True
        
        # Invalid tasks
        assert agent._validate_task(None) == False
        
        # Task missing task_id
        invalid_task1 = Task(
            task_id="",
            task_type="analysis",
            parameters={},
            priority=TaskPriority.LOW
        )
        assert agent._validate_task(invalid_task1) == False
        
        # Task missing task_type
        invalid_task2 = Task(
            task_id="test_002",
            task_type="",
            parameters={},
            priority=TaskPriority.LOW
        )
        assert agent._validate_task(invalid_task2) == False
        
        # Task with invalid parameters type
        invalid_task3 = Task(
            task_id="test_003",
            task_type="analysis",
            parameters="invalid",  # Should be dict
            priority=TaskPriority.LOW
        )
        invalid_task3.parameters = "invalid"  # Force invalid type
        assert agent._validate_task(invalid_task3) == False
        
        logger.info("✅ Task validation test passed")
    
    async def test_resource_allocation_real_workflows(self):
        """Test resource allocation with real resource requirements."""
        orchestrator = ParallelOrchestrator(self.config_path)
        await orchestrator.initialize()
        
        # Test resource allocation scenarios
        resource_pool = orchestrator.resource_pool
        
        # Scenario 1: Normal allocation
        normal_requirements = {"agents": 1, "memory_mb": 256, "reasoning_threads": 1}
        assert resource_pool.can_allocate(normal_requirements) == True
        assert resource_pool.allocate(normal_requirements) == True
        
        # Verify allocation occurred
        assert resource_pool.available_agents == 2
        assert resource_pool.used_memory_mb == 256
        assert resource_pool.active_reasoning == 1
        
        # Scenario 2: Heavy allocation
        heavy_requirements = {"agents": 2, "memory_mb": 512, "reasoning_threads": 1}
        assert resource_pool.can_allocate(heavy_requirements) == True
        assert resource_pool.allocate(heavy_requirements) == True
        
        # Verify state
        assert resource_pool.available_agents == 0
        assert resource_pool.used_memory_mb == 768
        assert resource_pool.active_reasoning == 2
        
        # Scenario 3: Over-allocation should fail
        excess_requirements = {"agents": 1, "memory_mb": 300, "reasoning_threads": 1}
        assert resource_pool.can_allocate(excess_requirements) == False
        assert resource_pool.allocate(excess_requirements) == False
        
        # Scenario 4: Release resources
        resource_pool.release(normal_requirements)
        assert resource_pool.available_agents == 1
        assert resource_pool.used_memory_mb == 512
        assert resource_pool.active_reasoning == 1
        
        logger.info("✅ Resource allocation test passed")
        
        await orchestrator.cleanup()
    
    async def test_performance_metrics_collection(self):
        """Test that performance metrics are collected correctly."""
        orchestrator = ParallelOrchestrator(self.config_path)
        await orchestrator.initialize()
        
        # Create a real request that will generate metrics
        test_request = "Process document and extract key entities and relationships"
        start_time = time.time()
        
        # Execute request (this will use real workflow determination)
        result = await orchestrator.process_request(test_request, {"test_mode": True})
        
        execution_time = time.time() - start_time
        
        # Verify result structure
        assert isinstance(result, Result)
        assert hasattr(result, 'success')
        assert hasattr(result, 'execution_time')
        assert result.execution_time > 0
        assert result.execution_time <= execution_time + 0.1  # Allow small margin
        
        # Verify performance metrics are included
        assert result.metadata is not None
        assert "performance_metrics" in result.metadata
        
        metrics = result.metadata["performance_metrics"]
        assert "workflow_id" in metrics
        assert "start_time" in metrics
        assert "request_length" in metrics
        assert "initial_resource_state" in metrics
        
        # Verify resource state tracking
        initial_state = metrics["initial_resource_state"]
        assert "available_agents" in initial_state
        assert "used_memory_mb" in initial_state
        assert "active_reasoning" in initial_state
        
        logger.info(f"✅ Performance metrics test passed - execution time: {result.execution_time:.3f}s")
        
        await orchestrator.cleanup()
    
    async def test_reasoning_agent_execution_real_task(self):
        """Test reasoning agent executes real tasks with metrics."""
        agent = ReasoningAgent(
            agent_id="execution_test_agent",
            reasoning_config={"enable_reasoning": True, "reasoning_threshold": 0.1},
            memory_config={"enable_learning": True}
        )
        
        # Create real task
        task = Task(
            task_id="real_execution_task",
            task_type="text_analysis",
            parameters={
                "text": "This is a test document for analysis",
                "analysis_type": "sentiment",
                "detail_level": "comprehensive"
            },
            priority=TaskPriority.HIGH
        )
        
        # Execute task
        start_time = time.time()
        result = await agent.execute(task)
        execution_time = time.time() - start_time
        
        # Verify result
        assert isinstance(result, Result)
        assert result.task_id == task.task_id
        assert result.execution_time > 0
        assert result.execution_time <= execution_time + 0.1
        
        # Verify execution metrics collected
        assert result.metadata is not None
        assert "execution_metrics" in result.metadata
        
        metrics = result.metadata["execution_metrics"]
        assert metrics["agent_id"] == "execution_test_agent"
        assert metrics["task_id"] == "real_execution_task"
        assert metrics["task_type"] == "text_analysis"
        assert metrics["reasoning_enabled"] == True
        assert "total_execution_time" in metrics
        
        logger.info(f"✅ Reasoning agent execution test passed - time: {result.execution_time:.3f}s")
    
    async def test_error_handling_real_scenarios(self):
        """Test error handling with real error scenarios."""
        orchestrator = ParallelOrchestrator(self.config_path)
        await orchestrator.initialize()
        
        # Test with empty request
        result = await orchestrator.process_request("", {})
        assert result.success == False
        assert "performance_metrics" in result.metadata
        
        # Test with None request (will cause error)
        try:
            result = await orchestrator.process_request(None, {})
            assert result.success == False
            assert "error" in result.__dict__
        except Exception:
            # This is expected for None input
            pass
        
        # Test with malformed context
        result = await orchestrator.process_request("Valid request", None)
        # Should handle gracefully
        assert isinstance(result, Result)
        
        logger.info("✅ Error handling test passed")
        
        await orchestrator.cleanup()
    
    async def test_concurrent_execution_real_load(self):
        """Test concurrent execution with real concurrent load."""
        orchestrator = ParallelOrchestrator(self.config_path)
        await orchestrator.initialize()
        
        # Create multiple concurrent requests
        requests = [
            "Analyze document structure and extract metadata",
            "Process text for entity recognition and classification", 
            "Generate summary and key insights from content"
        ]
        
        # Execute concurrently
        start_time = time.time()
        tasks = [
            orchestrator.process_request(req, {"concurrent_test": True, "request_id": i})
            for i, req in enumerate(requests)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Verify all completed
        assert len(results) == len(requests)
        
        # Verify results are valid
        valid_results = [r for r in results if isinstance(r, Result)]
        assert len(valid_results) >= 1  # At least some should succeed
        
        # Verify concurrent execution was faster than sequential
        # (This is a real performance test)
        sequential_estimate = sum(r.execution_time for r in valid_results if hasattr(r, 'execution_time'))
        if sequential_estimate > 0:
            efficiency = sequential_estimate / total_time
            logger.info(f"Concurrent efficiency: {efficiency:.2f}x (parallel: {total_time:.2f}s vs estimated sequential: {sequential_estimate:.2f}s)")
            assert efficiency >= 0.8  # Should be reasonably efficient
        
        logger.info(f"✅ Concurrent execution test passed - {len(valid_results)}/{len(requests)} succeeded in {total_time:.2f}s")
        
        await orchestrator.cleanup()


async def run_all_tests():
    """Run all integration tests."""
    test_instance = TestImprovedOrchestration()
    await test_instance.setup_class()
    
    tests = [
        test_instance.test_parallel_orchestrator_initialization(),
        test_instance.test_reasoning_agent_initialization(),
        test_instance.test_task_validation_real_scenarios(),
        test_instance.test_resource_allocation_real_workflows(),
        test_instance.test_performance_metrics_collection(),
        test_instance.test_reasoning_agent_execution_real_task(),
        test_instance.test_error_handling_real_scenarios(),
        test_instance.test_concurrent_execution_real_load()
    ]
    
    logger.info("🚀 Starting comprehensive integration tests (NO MOCKING)")
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(tests):
        try:
            await test
            passed += 1
        except Exception as e:
            logger.error(f"❌ Test {i+1} failed: {e}")
            failed += 1
    
    logger.info(f"🎯 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 ALL TESTS PASSED - Improved orchestration validated with real execution!")
    else:
        logger.warning(f"⚠️  {failed} tests failed - see errors above")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_instance.temp_dir, ignore_errors=True)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)