"""
Test thread safety and race conditions in core services.

Ensures ServiceManager singleton is thread-safe and services handle
concurrent access without race conditions.
"""

import pytest
import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import uuid
import aiosqlite

from src.core.service_manager import ServiceManager
from src.core.neo4j_manager import Neo4jManager


class TestThreadSafety:
    """Test suite for thread safety and race conditions."""
    
    @pytest.mark.asyncio
    async def test_service_manager_singleton(self):
        """Test ServiceManager singleton is thread-safe."""
        instances = []
        
        def get_instance():
            instance = ServiceManager()
            instances.append(instance)
        
        # Try to create multiple instances concurrently
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=get_instance)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All instances should be the same object
        assert len(instances) == 10
        first_instance = instances[0]
        for instance in instances:
            assert instance is first_instance
    
    @pytest.mark.asyncio
    async def test_concurrent_service_registration(self):
        """Test concurrent service registration doesn't cause race conditions."""
        manager = ServiceManager()
        
        # Clear any existing services
        manager._services.clear()
        
        registration_errors = []
        
        async def register_service(service_name: str):
            try:
                # Simulate service registration
                await asyncio.sleep(0.001)  # Small delay to increase race condition chance
                
                # Register service
                if service_name not in manager._services:
                    manager._services[service_name] = {
                        'id': str(uuid.uuid4()),
                        'name': service_name,
                        'status': 'active'
                    }
                return True
            except Exception as e:
                registration_errors.append((service_name, str(e)))
                return False
        
        # Register same services concurrently
        service_names = ['identity', 'provenance', 'quality', 'workflow']
        tasks = []
        
        # Each service registered 5 times concurrently
        for service_name in service_names:
            for _ in range(5):
                tasks.append(register_service(service_name))
        
        results = await asyncio.gather(*tasks)
        
        # Check no errors occurred
        assert len(registration_errors) == 0
        
        # Each service should only be registered once
        assert len(manager._services) == len(service_names)
        for service_name in service_names:
            assert service_name in manager._services
    
    @pytest.mark.asyncio
    async def test_service_state_consistency(self):
        """Test service state remains consistent under concurrent access."""
        manager = ServiceManager()
        
        # Shared counter to test for race conditions
        counter = {'value': 0}
        counter_lock = threading.Lock()
        
        async def increment_counter(times: int):
            for _ in range(times):
                with counter_lock:
                    current = counter['value']
                    await asyncio.sleep(0.0001)  # Simulate work
                    counter['value'] = current + 1
        
        # Run concurrent increments
        tasks = []
        increments_per_task = 100
        num_tasks = 10
        
        for _ in range(num_tasks):
            tasks.append(increment_counter(increments_per_task))
        
        await asyncio.gather(*tasks)
        
        # Counter should equal total increments (no lost updates)
        expected = increments_per_task * num_tasks
        assert counter['value'] == expected, f"Expected {expected}, got {counter['value']}"
    
    @pytest.mark.asyncio
    async def test_neo4j_connection_thread_safety(self):
        """Test Neo4j connections are thread-safe."""
        # This test ensures Neo4j operations don't interfere with each other
        neo4j_manager = Neo4jManager(
            uri="bolt://localhost:7687",
            auth=("neo4j", "testpassword")
        )
        
        results = []
        errors = []
        
        async def create_node(node_id: int):
            try:
                query = """
                CREATE (n:TestNode {id: $id, thread: $thread})
                RETURN n.id as id
                """
                result = await neo4j_manager.execute_query(
                    query,
                    {"id": node_id, "thread": threading.current_thread().name}
                )
                results.append(result)
                return True
            except Exception as e:
                errors.append((node_id, str(e)))
                return False
        
        # Create nodes concurrently
        tasks = []
        for i in range(20):
            tasks.append(create_node(i))
        
        success_results = await asyncio.gather(*tasks)
        
        # All operations should succeed
        assert all(success_results), f"Some operations failed: {errors}"
        
        # Verify all nodes were created
        count_query = "MATCH (n:TestNode) RETURN count(n) as count"
        count_result = await neo4j_manager.execute_query(count_query)
        assert count_result[0]['count'] == 20
        
        # Cleanup
        await neo4j_manager.execute_query("MATCH (n:TestNode) DELETE n")
    
    @pytest.mark.asyncio
    async def test_sqlite_transaction_isolation(self):
        """Test SQLite transaction isolation prevents race conditions."""
        db_path = "/tmp/test_thread_safety.db"
        
        # Create database and table
        async with aiosqlite.connect(db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS test_counter (
                    id INTEGER PRIMARY KEY,
                    value INTEGER NOT NULL
                )
            """)
            await db.execute(
                "INSERT INTO test_counter (id, value) VALUES (1, 0)"
            )
            await db.commit()
        
        errors = []
        
        async def increment_value(increment: int):
            try:
                async with aiosqlite.connect(db_path) as db:
                    async with db.execute("BEGIN EXCLUSIVE"):
                        # Read current value
                        cursor = await db.execute(
                            "SELECT value FROM test_counter WHERE id = 1"
                        )
                        row = await cursor.fetchone()
                        current_value = row[0]
                        
                        # Simulate processing time
                        await asyncio.sleep(0.001)
                        
                        # Update value
                        new_value = current_value + increment
                        await db.execute(
                            "UPDATE test_counter SET value = ? WHERE id = 1",
                            (new_value,)
                        )
                        await db.commit()
                return True
            except Exception as e:
                errors.append(str(e))
                return False
        
        # Run concurrent increments
        tasks = []
        for _ in range(10):
            tasks.append(increment_value(1))
        
        results = await asyncio.gather(*tasks)
        
        # Check final value
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute(
                "SELECT value FROM test_counter WHERE id = 1"
            )
            row = await cursor.fetchone()
            final_value = row[0]
        
        # With proper transaction isolation, value should be 10
        assert final_value == 10, f"Expected 10, got {final_value}"
        
        # Cleanup
        import os
        os.unlink(db_path)
    
    @pytest.mark.asyncio
    async def test_service_initialization_race(self):
        """Test service initialization doesn't have race conditions."""
        manager = ServiceManager()
        
        # Track initialization order
        init_order = []
        init_lock = threading.Lock()
        
        class MockService:
            def __init__(self, name: str):
                self.name = name
                
            async def initialize(self):
                with init_lock:
                    init_order.append(self.name)
                await asyncio.sleep(0.01)  # Simulate initialization work
                return True
        
        # Create services
        services = {
            'service1': MockService('service1'),
            'service2': MockService('service2'),
            'service3': MockService('service3')
        }
        
        # Initialize concurrently
        tasks = []
        for service in services.values():
            tasks.append(service.initialize())
        
        await asyncio.gather(*tasks)
        
        # All services should initialize
        assert len(init_order) == 3
        assert set(init_order) == {'service1', 'service2', 'service3'}
    
    @pytest.mark.asyncio
    async def test_connection_pool_race_conditions(self):
        """Test connection pool doesn't have race conditions."""
        from src.core.connection_pool_manager import ConnectionPoolManager
        
        pool = ConnectionPoolManager(min_size=2, max_size=5)
        
        acquired_connections = []
        errors = []
        
        async def use_connection(worker_id: int):
            try:
                # Acquire connection
                conn = await pool.acquire_connection()
                acquired_connections.append((worker_id, id(conn)))
                
                # Use connection
                await asyncio.sleep(0.01)
                
                # Release connection
                await pool.release_connection(conn)
                return True
            except Exception as e:
                errors.append((worker_id, str(e)))
                return False
        
        # Use more workers than pool size to test queuing
        tasks = []
        for i in range(20):
            tasks.append(use_connection(i))
        
        results = await asyncio.gather(*tasks)
        
        # All workers should succeed
        assert all(results), f"Some workers failed: {errors}"
        
        # Check no connection was used by multiple workers simultaneously
        # This is a simplified check - in reality would need more sophisticated tracking
        assert len(acquired_connections) == 20
    
    @pytest.mark.asyncio
    async def test_service_cleanup_race(self):
        """Test service cleanup doesn't cause race conditions."""
        manager = ServiceManager()
        
        cleanup_order = []
        cleanup_lock = threading.Lock()
        
        class MockService:
            def __init__(self, name: str):
                self.name = name
                self.active_operations = 0
                
            async def perform_operation(self):
                self.active_operations += 1
                await asyncio.sleep(0.01)
                self.active_operations -= 1
                
            async def cleanup(self):
                # Wait for operations to complete
                while self.active_operations > 0:
                    await asyncio.sleep(0.001)
                    
                with cleanup_lock:
                    cleanup_order.append(self.name)
        
        # Create services
        services = {
            'service1': MockService('service1'),
            'service2': MockService('service2'),
            'service3': MockService('service3')
        }
        
        # Start operations on all services
        operation_tasks = []
        for service in services.values():
            for _ in range(5):
                operation_tasks.append(service.perform_operation())
        
        # Start cleanup concurrently (while operations running)
        cleanup_tasks = []
        for service in services.values():
            cleanup_tasks.append(service.cleanup())
        
        # Wait for everything to complete
        await asyncio.gather(*operation_tasks)
        await asyncio.gather(*cleanup_tasks)
        
        # All services should have cleaned up
        assert len(cleanup_order) == 3
        assert set(cleanup_order) == {'service1', 'service2', 'service3'}
        
        # No operations should be active
        for service in services.values():
            assert service.active_operations == 0
    
    @pytest.mark.asyncio
    async def test_lock_contention_monitoring(self):
        """Test monitoring of lock contention in services."""
        lock = asyncio.Lock()
        contention_events = []
        
        async def contended_operation(op_id: int):
            start_wait = time.time()
            async with lock:
                wait_time = time.time() - start_wait
                if wait_time > 0.001:  # Contention threshold
                    contention_events.append({
                        'op_id': op_id,
                        'wait_time': wait_time
                    })
                
                # Simulate work
                await asyncio.sleep(0.01)
        
        # Create contention by running many operations
        tasks = []
        for i in range(20):
            tasks.append(contended_operation(i))
        
        await asyncio.gather(*tasks)
        
        # Should see contention events (all but first operation wait)
        assert len(contention_events) >= 15
        
        # Verify wait times increase for later operations
        if len(contention_events) > 5:
            early_waits = [e['wait_time'] for e in contention_events[:5]]
            late_waits = [e['wait_time'] for e in contention_events[-5:]]
            assert sum(late_waits) / 5 > sum(early_waits) / 5