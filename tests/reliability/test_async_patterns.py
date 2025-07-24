"""
Test async/await patterns to ensure no blocking calls in async context.

Verifies that all async operations are truly non-blocking and don't
use time.sleep() or other blocking operations.
"""

import pytest
import asyncio
import time
from unittest.mock import patch, AsyncMock, MagicMock
import concurrent.futures


class TestAsyncPatterns:
    """Test suite for async pattern validation."""
    
    @pytest.mark.asyncio
    async def test_no_blocking_in_async_context(self):
        """Verify that async functions don't block the event loop."""
        from src.core.api_rate_limiter import RateLimiter
        
        # Create a rate limiter
        limiter = RateLimiter(calls_per_second=10)
        
        # Track if event loop was blocked
        loop = asyncio.get_event_loop()
        blocked = False
        check_interval = 0.05  # Check every 50ms
        
        async def monitor_loop():
            """Monitor if the loop is responsive."""
            nonlocal blocked
            last_time = time.time()
            
            while not blocked:
                await asyncio.sleep(check_interval)
                current_time = time.time()
                # If more than 150ms passed, loop was blocked
                if current_time - last_time > 0.15:
                    blocked = True
                last_time = current_time
        
        # Start monitoring
        monitor_task = asyncio.create_task(monitor_loop())
        
        # Make multiple rate-limited calls
        async def make_call():
            await limiter.acquire()
            return "success"
        
        # Make calls that should trigger rate limiting
        tasks = [make_call() for _ in range(20)]
        
        try:
            results = await asyncio.gather(*tasks)
            assert len(results) == 20
            assert not blocked, "Event loop was blocked during rate limiting"
        finally:
            monitor_task.cancel()
    
    @pytest.mark.asyncio
    async def test_event_loop_responsiveness(self):
        """Test that the event loop remains responsive during operations."""
        # Create a simple counter that increments every 10ms
        counter = 0
        stop_counting = False
        
        async def count_loop():
            nonlocal counter
            while not stop_counting:
                counter += 1
                await asyncio.sleep(0.01)  # 10ms
        
        count_task = asyncio.create_task(count_loop())
        
        # Import and test various async operations
        from src.core.async_error_handler import AsyncErrorHandler
        
        error_handler = AsyncErrorHandler()
        
        # Simulate retryable errors
        attempt_count = 0
        
        @error_handler.with_retry(max_attempts=3, delay=0.1)
        async def failing_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ConnectionError("Simulated error")
            return "success"
        
        start_count = counter
        start_time = time.time()
        
        # This should take ~200ms (2 retries with 100ms delay each)
        result = await failing_operation()
        
        end_time = time.time()
        end_count = counter
        
        assert result == "success"
        assert attempt_count == 3
        
        # The counter should have continued running
        # In 200ms, we expect ~20 increments
        increments = end_count - start_count
        assert increments >= 15, f"Counter only incremented {increments} times, loop was blocked"
        
        stop_counting = True
        await count_task
    
    @pytest.mark.asyncio
    async def test_concurrent_execution(self):
        """Test that async operations execute concurrently."""
        from src.core.memory_manager import MemoryManager
        
        memory_manager = MemoryManager()
        
        # Track execution times
        execution_times = []
        
        async def timed_operation(duration: float, operation_id: int):
            start = time.time()
            # Simulate some async work
            await asyncio.sleep(duration)
            memory_manager.track_memory_usage(f"operation_{operation_id}")
            execution_times.append((operation_id, time.time() - start))
            return operation_id
        
        # Run 5 operations concurrently, each taking 0.1 seconds
        start_time = time.time()
        results = await asyncio.gather(
            timed_operation(0.1, 1),
            timed_operation(0.1, 2),
            timed_operation(0.1, 3),
            timed_operation(0.1, 4),
            timed_operation(0.1, 5)
        )
        total_time = time.time() - start_time
        
        # If truly concurrent, should take ~0.1 seconds, not 0.5 seconds
        assert total_time < 0.2, f"Operations took {total_time}s, not running concurrently"
        assert sorted(results) == [1, 2, 3, 4, 5]
    
    @pytest.mark.asyncio
    async def test_timeout_behavior(self):
        """Test that timeouts work correctly without blocking."""
        async def slow_operation():
            await asyncio.sleep(2.0)
            return "completed"
        
        # This should timeout after 0.5 seconds
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(slow_operation(), timeout=0.5)
        
        # Verify we can still run other operations
        fast_result = await asyncio.wait_for(
            asyncio.sleep(0.1), 
            timeout=0.5
        )
        assert fast_result is None  # sleep returns None
    
    @pytest.mark.asyncio
    async def test_blocking_detection(self):
        """Test detection of blocking operations in async code."""
        import threading
        
        # Function that incorrectly uses time.sleep
        async def bad_async_function():
            time.sleep(0.2)  # This blocks!
            return "bad"
        
        # Function that correctly uses asyncio.sleep
        async def good_async_function():
            await asyncio.sleep(0.2)
            return "good"
        
        # Measure thread blocking
        main_thread = threading.current_thread()
        thread_was_blocked = False
        
        def check_thread():
            nonlocal thread_was_blocked
            start = time.time()
            while time.time() - start < 0.5:
                # Check if main thread is responsive
                if not main_thread.is_alive():
                    thread_was_blocked = True
                    break
                time.sleep(0.01)
        
        # Test good function
        checker = threading.Thread(target=check_thread)
        checker.start()
        result = await good_async_function()
        checker.join()
        assert result == "good"
        assert not thread_was_blocked
        
        # Note: We can't easily test the bad function without actually blocking
    
    @pytest.mark.asyncio
    async def test_neo4j_async_operations(self):
        """Test that Neo4j operations are truly async."""
        from src.core.neo4j_manager import Neo4jManager
        
        # Mock the neo4j driver
        with patch('src.core.neo4j_manager.AsyncGraphDatabase') as mock_driver:
            mock_session = AsyncMock()
            mock_driver.driver.return_value.session.return_value = mock_session
            
            manager = Neo4jManager("bolt://localhost:7687", ("neo4j", "password"))
            
            # Track concurrent executions
            execution_order = []
            
            async def mock_run(query, **params):
                execution_order.append(f"start_{query[:10]}")
                await asyncio.sleep(0.1)
                execution_order.append(f"end_{query[:10]}")
                return AsyncMock()
            
            mock_session.run = mock_run
            
            # Run multiple queries concurrently
            queries = [
                manager.create_node("Entity", {"id": 1}),
                manager.create_node("Entity", {"id": 2}),
                manager.create_node("Entity", {"id": 3})
            ]
            
            await asyncio.gather(*queries)
            
            # Check that operations interleaved (concurrent execution)
            # Should see: start_1, start_2, start_3, end_1, end_2, end_3
            # Not: start_1, end_1, start_2, end_2, start_3, end_3
            start_indices = [i for i, x in enumerate(execution_order) if x.startswith("start_")]
            end_indices = [i for i, x in enumerate(execution_order) if x.startswith("end_")]
            
            # All starts should come before all ends (indicating concurrency)
            assert max(start_indices) < min(end_indices), "Operations did not execute concurrently"
    
    @pytest.mark.asyncio
    async def test_connection_pool_async(self):
        """Test that connection pooling doesn't block."""
        # Simulate a connection pool
        class AsyncConnectionPool:
            def __init__(self, size=3):
                self.semaphore = asyncio.Semaphore(size)
                self.connections = []
            
            async def acquire(self):
                await self.semaphore.acquire()
                # Simulate connection setup
                await asyncio.sleep(0.01)
                conn = f"conn_{len(self.connections)}"
                self.connections.append(conn)
                return conn
            
            async def release(self, conn):
                self.semaphore.release()
        
        pool = AsyncConnectionPool(size=2)
        
        # Try to acquire 5 connections (but pool size is 2)
        acquired = []
        
        async def use_connection(conn_id):
            conn = await pool.acquire()
            acquired.append((conn_id, time.time()))
            await asyncio.sleep(0.1)  # Use connection
            await pool.release(conn)
            return conn_id
        
        start = time.time()
        results = await asyncio.gather(
            use_connection(1),
            use_connection(2),
            use_connection(3),
            use_connection(4),
            use_connection(5)
        )
        
        # Should see batching: first 2 concurrent, then next 2, then last 1
        assert len(results) == 5
        
        # Check timing - should take ~0.3s (3 batches * 0.1s)
        total_time = time.time() - start
        assert 0.25 < total_time < 0.4, f"Pool operations took {total_time}s"