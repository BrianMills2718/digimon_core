#!/usr/bin/env python3
"""
Test script to verify refactored orchestration components work correctly.

Tests the refactored parallel orchestrator and reasoning agent components.
"""

import asyncio
import logging
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from orchestration.resource_management import ResourceManager, ExecutionMode
from orchestration.task_management import TaskCoordinator, ParallelTask
from orchestration.reasoning_components import ReasoningDecisionMaker, ReasoningContextBuilder
from orchestration.base import Task, TaskPriority

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_resource_management():
    """Test resource management components."""
    logger.info("Testing Resource Management...")
    
    # Test basic resource manager
    resource_manager = ResourceManager({
        "max_concurrent_agents": 3,
        "max_memory_mb": 1024,
        "max_reasoning_threads": 2
    })
    
    # Test resource estimation
    requirements = resource_manager.estimate_resource_requirements("document_processing", 1.5)
    logger.info(f"Estimated requirements: {requirements}")
    
    # Test resource allocation
    allocated = resource_manager.resource_pool.allocate(requirements)
    logger.info(f"Resource allocation successful: {allocated}")
    
    # Test utilization
    utilization = resource_manager.resource_pool.get_utilization()
    logger.info(f"Resource utilization: {utilization}")
    
    # Test adaptive parallelism
    recommended_parallelism = resource_manager.adjust_parallelism_level()
    logger.info(f"Recommended parallelism: {recommended_parallelism}")
    
    # Release resources
    resource_manager.resource_pool.release(requirements)
    logger.info("✅ Resource management tests passed")


async def test_task_coordination():
    """Test task coordination components.""" 
    logger.info("Testing Task Coordination...")
    
    # Create task coordinator
    coordinator = TaskCoordinator()
    
    # Create mock resource manager for task creation
    resource_manager = ResourceManager()
    
    # Test task creation
    request = "Extract entities from documents and analyze relationships"
    context = {"complexity_multiplier": 1.2}
    
    parallel_tasks = await coordinator.create_parallel_tasks(request, context, resource_manager)
    logger.info(f"Created {len(parallel_tasks)} parallel tasks")
    
    # Test ready task identification
    ready_tasks = coordinator.get_ready_tasks()
    logger.info(f"Ready tasks: {len(ready_tasks)}")
    
    # Test pipeline stage creation
    stages = coordinator.create_pipeline_stages(parallel_tasks)
    logger.info(f"Created {len(stages)} pipeline stages")
    
    # Test task status
    status = coordinator.get_task_status()
    logger.info(f"Task status: {status}")
    
    coordinator.cleanup()
    logger.info("✅ Task coordination tests passed")


async def test_reasoning_components():
    """Test reasoning components."""
    logger.info("Testing Reasoning Components...")
    
    # Test reasoning decision maker
    decision_maker = ReasoningDecisionMaker({
        "reasoning_threshold": 0.5,
        "complex_task_param_count": 3
    })
    
    # Create test task
    task = Task(
        task_id="test_task",
        task_type="analysis",
        parameters={"param1": "value1", "param2": "value2", "param3": "value3"},
        priority=TaskPriority.HIGH
    )
    
    # Test reasoning decision
    memory_context = {"relevant_executions": []}
    should_reason = await decision_maker.should_apply_reasoning(task, memory_context)
    logger.info(f"Should apply reasoning: {should_reason}")
    
    # Test context builder
    context_builder = ReasoningContextBuilder()
    reasoning_context = await context_builder.build_reasoning_context(
        task, memory_context, "test_agent"
    )
    logger.info(f"Built reasoning context: {reasoning_context.reasoning_type}")
    
    logger.info("✅ Reasoning components tests passed")


async def test_integration():
    """Test integration between components."""
    logger.info("Testing Component Integration...")
    
    # Create all components
    resource_manager = ResourceManager()
    coordinator = TaskCoordinator()
    
    # Create tasks
    request = "Process documents and extract insights"
    context = {"priority_boost": 0.2}
    
    parallel_tasks = await coordinator.create_parallel_tasks(request, context, resource_manager)
    
    # Test resource allocation for tasks
    for task in parallel_tasks:
        requirements = task.resource_requirements
        can_allocate = resource_manager.resource_pool.can_allocate(requirements)
        logger.info(f"Task {task.task.task_id}: can allocate = {can_allocate}")
        
        if can_allocate:
            resource_manager.resource_pool.allocate(requirements)
    
    # Check final resource state
    final_utilization = resource_manager.resource_pool.get_utilization()
    logger.info(f"Final utilization: {final_utilization}")
    
    coordinator.cleanup()
    logger.info("✅ Integration tests passed")


async def main():
    """Run all tests."""
    logger.info("🚀 Starting Refactored Components Tests")
    
    try:
        await test_resource_management()
        await test_task_coordination()
        await test_reasoning_components()
        await test_integration()
        
        logger.info("🎉 All tests passed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)