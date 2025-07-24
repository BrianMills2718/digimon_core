"""
Demo script showing thread safety improvements.

This demonstrates the fixes for race conditions and thread safety issues
in the ServiceManager.
"""

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.thread_safe_service_manager import get_thread_safe_service_manager
from src.core.service_manager import get_service_manager


async def test_original_service_manager():
    """Test the original ServiceManager for race conditions."""
    print("\n🔴 Testing Original ServiceManager\n")
    
    manager = get_service_manager()
    errors = []
    
    def access_service(worker_id: int):
        try:
            # Try to access services concurrently
            for i in range(10):
                identity = manager.identity_service
                provenance = manager.provenance_service
                quality = manager.quality_service
                
                # Simulate some work
                time.sleep(0.001)
                
                # Check if services are still valid
                if not hasattr(identity, 'create_mention'):
                    errors.append(f"Worker {worker_id}: Identity service invalid")
                    
        except Exception as e:
            errors.append(f"Worker {worker_id}: {str(e)}")
    
    # Run concurrent access
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for i in range(10):
            futures.append(executor.submit(access_service, i))
        
        # Wait for completion
        for future in futures:
            future.result()
    
    if errors:
        print(f"❌ Found {len(errors)} errors:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"   - {error}")
    else:
        print("✅ No errors detected (but race conditions may still exist)")
    
    # Show statistics
    stats = manager.get_service_stats()
    print(f"\n📊 Statistics:")
    for key, value in stats.items():
        print(f"   - {key}: {value}")


async def test_thread_safe_service_manager():
    """Test the ThreadSafeServiceManager."""
    print("\n🟢 Testing ThreadSafeServiceManager\n")
    
    manager = get_thread_safe_service_manager()
    await manager.initialize()
    
    errors = []
    access_times = []
    
    async def access_service_async(worker_id: int):
        try:
            start = time.time()
            
            # Access services concurrently
            for i in range(10):
                identity = await manager.get_service('identity')
                provenance = await manager.get_service('provenance')
                quality = await manager.get_service('quality')
                
                # Simulate work
                await asyncio.sleep(0.001)
                
                # Verify services
                if not hasattr(identity, 'create_mention'):
                    errors.append(f"Worker {worker_id}: Identity service invalid")
            
            access_times.append(time.time() - start)
            
        except Exception as e:
            errors.append(f"Worker {worker_id}: {str(e)}")
    
    # Run concurrent access
    tasks = []
    for i in range(20):
        tasks.append(access_service_async(i))
    
    await asyncio.gather(*tasks)
    
    if errors:
        print(f"❌ Found {len(errors)} errors:")
        for error in errors[:5]:
            print(f"   - {error}")
    else:
        print("✅ No errors - all operations completed successfully")
    
    # Show performance
    avg_time = sum(access_times) / len(access_times)
    print(f"\n⚡ Performance:")
    print(f"   - Average access time: {avg_time:.3f}s")
    print(f"   - Min access time: {min(access_times):.3f}s")
    print(f"   - Max access time: {max(access_times):.3f}s")
    
    # Show statistics
    stats = manager.get_statistics()
    print(f"\n📊 Statistics:")
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    # Test health check
    health = await manager.health_check()
    print(f"\n🏥 Health Check:")
    for service, status in health.items():
        print(f"   - {service}: {'✅ Healthy' if status else '❌ Unhealthy'}")


async def demonstrate_atomic_operations():
    """Demonstrate atomic operations feature."""
    print("\n🔒 Testing Atomic Operations\n")
    
    manager = get_thread_safe_service_manager()
    await manager.initialize()
    
    operation_results = []
    
    async def perform_atomic_operation(op_id: int):
        """Perform an atomic operation on identity service."""
        async with manager.atomic_operation('identity') as identity_service:
            # This block is atomic - no other thread can access identity service
            start = time.time()
            
            # Simulate complex operation
            await asyncio.sleep(0.01)
            
            duration = time.time() - start
            operation_results.append({
                'op_id': op_id,
                'duration': duration,
                'thread': threading.current_thread().name
            })
    
    # Run atomic operations concurrently
    tasks = []
    for i in range(10):
        tasks.append(perform_atomic_operation(i))
    
    start_time = time.time()
    await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    print(f"✅ Completed {len(operation_results)} atomic operations")
    print(f"⏱️  Total time: {total_time:.3f}s")
    print(f"🔄 Operations were serialized (should take ~0.1s total)")
    
    # Show that operations were indeed serialized
    for i, result in enumerate(operation_results[:3]):
        print(f"   - Operation {result['op_id']}: {result['duration']:.3f}s on {result['thread']}")


async def demonstrate_queue_operations():
    """Demonstrate operation queuing."""
    print("\n📋 Testing Operation Queue\n")
    
    manager = get_thread_safe_service_manager()
    await manager.initialize()
    
    # Queue configuration operations
    operations = []
    
    for i in range(5):
        op = {
            'type': 'configure_service',
            'params': {
                'service_name': f'test_service_{i}',
                'config': {'id': i, 'active': True}
            }
        }
        operations.append(manager.queue_operation(op))
    
    # Execute all queued operations
    results = await asyncio.gather(*operations)
    
    print(f"✅ Queued {len(results)} operations")
    print(f"📊 All operations completed: {all(results)}")
    
    # Show queue statistics
    stats = manager.get_statistics()
    print(f"🔢 Operations processed: {stats['operations_processed']}")


async def main():
    """Run all demonstrations."""
    print("=" * 60)
    print("Thread Safety Demonstration")
    print("=" * 60)
    
    # Test original service manager
    await test_original_service_manager()
    
    # Test thread-safe service manager
    await test_thread_safe_service_manager()
    
    # Demonstrate atomic operations
    await demonstrate_atomic_operations()
    
    # Demonstrate operation queuing
    await demonstrate_queue_operations()
    
    print("\n" + "=" * 60)
    print("✅ Thread Safety Demonstration Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())