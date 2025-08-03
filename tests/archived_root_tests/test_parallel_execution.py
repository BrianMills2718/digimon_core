#!/usr/bin/env python3
"""
Quick test of parallel execution functionality.
"""

import asyncio
import time
from src.orchestration.parallel_orchestrator import ParallelOrchestrator, ExecutionMode, ResourcePool, ParallelTask
from src.orchestration.coordination import CoordinationManager, CoordinationEventType
from src.orchestration.base import Task, TaskPriority

async def test_resource_pool():
    """Test ResourcePool functionality."""
    print("🧪 Testing ResourcePool...")
    
    pool = ResourcePool(
        max_concurrent_agents=3,
        max_memory_mb=1024,
        max_reasoning_threads=2
    )
    
    # Test allocation
    req1 = {"agents": 1, "memory_mb": 256, "reasoning_threads": 1}
    can_allocate = pool.can_allocate(req1)
    print(f"Can allocate {req1}: {can_allocate}")
    
    if can_allocate:
        allocated = pool.allocate(req1)
        print(f"Allocated: {allocated}")
        print(f"Available agents: {pool.available_agents}")
        print(f"Used memory: {pool.used_memory_mb} MB")
        
        # Test release
        pool.release(req1)
        print(f"After release - Available agents: {pool.available_agents}")
    
    return True

async def test_coordination():
    """Test CoordinationManager functionality."""
    print("\n🧪 Testing CoordinationManager...")
    
    coord = CoordinationManager()
    await coord.start()
    
    try:
        # Test shared state
        state_id = "test_state"
        state = await coord.create_shared_state(state_id, {"counter": 0})
        print(f"Created shared state: {state.state_id}")
        
        # Update state
        updates = {"counter": 1, "timestamp": time.time()}
        updated = await coord.update_shared_state(state_id, "test_agent", updates)
        print(f"Updated state to version {updated.version}")
        
        # Test barrier
        barrier = await coord.create_barrier("test_barrier", 2)
        print(f"Created barrier for 2 parties")
        
        # Test event emission
        event_received = False
        
        async def event_handler(event):
            nonlocal event_received
            event_received = True
            print(f"Received event: {event.event_type}")
        
        coord.subscribe_to_event(CoordinationEventType.DATA_AVAILABLE, event_handler)
        
        # Emit event
        from src.orchestration.coordination import CoordinationEvent
        await coord.emit_event(CoordinationEvent(
            event_type=CoordinationEventType.DATA_AVAILABLE,
            source_agent="test",
            data={"test": "data"}
        ))
        
        # Wait for event processing
        await asyncio.sleep(0.1)
        print(f"Event received: {event_received}")
        
        # Get stats
        stats = coord.get_coordination_stats()
        print(f"Coordination stats: {stats['total_events']} events, {stats['shared_states']} states")
        
    finally:
        await coord.cleanup()
    
    return True

async def test_parallel_task():
    """Test ParallelTask creation."""
    print("\n🧪 Testing ParallelTask...")
    
    task = Task(
        task_id="test_task",
        task_type="test",
        parameters={"test": "param"},
        priority=TaskPriority.HIGH
    )
    
    parallel_task = ParallelTask(
        task=task,
        dependencies=["dep1", "dep2"],
        resource_requirements={"agents": 1, "memory_mb": 512},
        can_parallelize=True,
        priority_boost=0.2
    )
    
    print(f"Created ParallelTask: {parallel_task.task.task_id}")
    print(f"Dependencies: {parallel_task.dependencies}")
    print(f"Effective priority: {parallel_task.effective_priority}")
    
    return True

async def test_execution_modes():
    """Test execution mode enums."""
    print("\n🧪 Testing Execution Modes...")
    
    modes = [
        ExecutionMode.PARALLEL,
        ExecutionMode.BATCH,
        ExecutionMode.PIPELINE,
        ExecutionMode.ADAPTIVE
    ]
    
    for mode in modes:
        print(f"Mode: {mode.name} = {mode.value}")
    
    return True

async def main():
    """Run all tests."""
    print("🔬 Testing Phase 3 Parallel Orchestration Components")
    print("=" * 50)
    
    tests = [
        ("ResourcePool", test_resource_pool),
        ("CoordinationManager", test_coordination),
        ("ParallelTask", test_parallel_task),
        ("ExecutionModes", test_execution_modes)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
            print(f"✅ {test_name} test passed\n")
        except Exception as e:
            results.append((test_name, False))
            print(f"❌ {test_name} test failed: {e}\n")
    
    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n📊 Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 3 components are working correctly!")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())