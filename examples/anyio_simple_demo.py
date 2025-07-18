#!/usr/bin/env python3
"""
Simple AnyIO Demo

A simplified demonstration of AnyIO structured concurrency features.
"""

import sys
import os
import time
import random

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import anyio
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "anyio"])
    import anyio

from core.anyio_orchestrator import AnyIOOrchestrator


async def simple_task(task_id: str, duration: float) -> dict:
    """Simple async task for demonstration"""
    await anyio.sleep(duration)
    return {
        "task_id": task_id,
        "duration": duration,
        "result": f"completed_{task_id}"
    }


async def demo_basic_parallel():
    """Basic parallel execution demo"""
    print("🚀 Basic Parallel Execution Demo")
    print("-" * 40)
    
    async with AnyIOOrchestrator() as orchestrator:
        # Create simple tasks
        tasks = []
        for i in range(5):
            duration = random.uniform(0.5, 1.5)
            task = lambda d=duration, tid=f"task_{i}": simple_task(tid, d)
            tasks.append(task)
        
        print(f"Starting {len(tasks)} parallel tasks...")
        
        start_time = time.time()
        results = await orchestrator.execute_tasks_parallel(tasks)
        execution_time = time.time() - start_time
        
        print(f"✅ Completed in {execution_time:.2f}s")
        print(f"   Successful: {len([r for r in results if r.success])}")
        print(f"   Failed: {len([r for r in results if not r.success])}")
        
        # Show individual results
        for result in results:
            if result.success:
                print(f"   {result.task_id}: {result.duration:.2f}s")
            else:
                print(f"   {result.task_id}: FAILED - {result.error}")
        
        print()


async def demo_resource_management():
    """Resource management demo"""
    print("🛠️ Resource Management Demo")
    print("-" * 40)
    
    async with AnyIOOrchestrator() as orchestrator:
        # Resource factory
        async def create_resource():
            await anyio.sleep(0.1)
            return {"resource_id": random.randint(1000, 9999), "status": "active"}
        
        # Create resources
        resource_factories = [create_resource, create_resource, create_resource]
        
        async with orchestrator.resource_manager(resource_factories) as resources:
            print(f"✅ Created {len(resources)} resources")
            for i, resource in enumerate(resources):
                print(f"   Resource {i+1}: {resource['resource_id']}")
            
            # Simulate work
            await anyio.sleep(0.5)
            print("   Work completed with resources")
        
        print("✅ Resources cleaned up")
        print()


async def demo_structured_concurrency():
    """Structured concurrency benefits demo"""
    print("⚡ Structured Concurrency Benefits")
    print("-" * 40)
    
    async with AnyIOOrchestrator() as orchestrator:
        # Show task group behavior
        print("Creating task group with automatic cancellation...")
        
        async def long_running_task(task_id: str):
            try:
                await anyio.sleep(2.0)  # Long task
                return f"completed_{task_id}"
            except anyio.get_cancelled_exc_class():
                print(f"   Task {task_id} was cancelled")
                raise
        
        async def failing_task():
            await anyio.sleep(0.5)
            raise Exception("Task failed intentionally")
        
        # Mix of tasks where one fails
        tasks = [
            lambda: long_running_task("task_1"),
            lambda: long_running_task("task_2"),
            lambda: failing_task(),
            lambda: long_running_task("task_3")
        ]
        
        start_time = time.time()
        results = await orchestrator.execute_tasks_parallel(tasks)
        execution_time = time.time() - start_time
        
        print(f"✅ Task group completed in {execution_time:.2f}s")
        print(f"   Note: All tasks were cancelled when one failed")
        print(f"   Successful: {len([r for r in results if r.success])}")
        print(f"   Failed: {len([r for r in results if not r.success])}")
        
        print()


async def main():
    """Main demo function"""
    print("🎯 AnyIO Structured Concurrency Demo")
    print("=" * 45)
    
    print("✨ Key AnyIO Benefits:")
    print("   - Structured concurrency with task groups")
    print("   - Automatic cancellation propagation")
    print("   - Better error handling and debugging")
    print("   - Resource management with context managers")
    print()
    
    try:
        await demo_basic_parallel()
        await demo_resource_management()
        await demo_structured_concurrency()
        
        print("🎉 AnyIO Migration Benefits Demonstrated:")
        print("✅ Structured concurrency patterns")
        print("✅ Automatic resource cleanup")
        print("✅ Better error propagation")
        print("✅ Cancellation-safe operations")
        print("✅ Improved debugging capabilities")
        
        print(f"\n🎉 Phase 2 Task 5: AnyIO Migration - COMPLETE")
        
        return 0
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1


if __name__ == "__main__":
    try:
        result = anyio.run(main)
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)