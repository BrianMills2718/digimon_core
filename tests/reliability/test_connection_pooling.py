"""
Test connection pool management for Neo4j and SQLite.

Ensures connection pools handle exhaustion gracefully and provide
proper health checking and recovery.
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List

from src.core.connection_pool_manager import ConnectionPoolManager


class TestConnectionPooling:
    """Test suite for connection pool management."""
    
    @pytest.mark.asyncio
    async def test_pool_limits(self):
        """Test that pool respects size limits."""
        pool = ConnectionPoolManager(min_size=2, max_size=5)
        
        # Acquire connections up to max
        connections = []
        for i in range(5):
            conn = await pool.acquire_connection()
            assert conn is not None
            connections.append(conn)
        
        # Try to acquire one more - should wait or fail
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(pool.acquire_connection(), timeout=1.0)
        
        # Release one and try again
        await pool.release_connection(connections[0])
        
        # Now should succeed
        conn = await asyncio.wait_for(pool.acquire_connection(), timeout=1.0)
        assert conn is not None
    
    @pytest.mark.asyncio
    async def test_connection_health_checks(self):
        """Test automatic health checking of connections."""
        pool = ConnectionPoolManager(min_size=3, max_size=5)
        
        # Get some connections
        conns = []
        for _ in range(3):
            conn = await pool.acquire_connection()
            conns.append(conn)
        
        # Release them back
        for conn in conns:
            await pool.release_connection(conn)
        
        # Simulate one connection becoming unhealthy
        pool._mark_unhealthy(conns[0])
        
        # Health check should detect and remove bad connection
        healthy_count = await pool.health_check_all()
        assert healthy_count == 2  # Only 2 healthy connections
        
        # Pool should create new connection to maintain min_size
        await asyncio.sleep(0.1)
        stats = pool.get_stats()
        assert stats['total_connections'] >= pool.min_size
    
    @pytest.mark.asyncio
    async def test_automatic_recovery(self):
        """Test automatic recovery from connection failures."""
        pool = ConnectionPoolManager(min_size=2, max_size=5)
        
        # Simulate all connections failing
        await pool._simulate_all_connections_failed()
        
        # Pool should detect and start recovery
        await pool.trigger_recovery()
        
        # Give time for recovery
        await asyncio.sleep(0.5)
        
        # Should have healthy connections again
        conn = await pool.acquire_connection()
        assert conn is not None
        assert conn.is_healthy()
    
    @pytest.mark.asyncio
    async def test_concurrent_access(self):
        """Test pool handles concurrent access correctly."""
        pool = ConnectionPoolManager(min_size=2, max_size=10)
        
        # Track acquisition times
        acquisition_times = []
        
        async def use_connection(worker_id: int):
            start = time.time()
            conn = await pool.acquire_connection()
            acquisition_times.append((worker_id, time.time() - start))
            
            # Simulate work
            await asyncio.sleep(0.1)
            
            await pool.release_connection(conn)
            return worker_id
        
        # Launch 20 workers (more than pool max)
        workers = [use_connection(i) for i in range(20)]
        results = await asyncio.gather(*workers)
        
        assert len(results) == 20
        
        # First 10 should get connections quickly
        fast_acquisitions = sorted(acquisition_times, key=lambda x: x[1])[:10]
        for worker_id, acq_time in fast_acquisitions:
            assert acq_time < 0.1, f"Worker {worker_id} waited {acq_time}s"
        
        # Rest had to wait
        slow_acquisitions = sorted(acquisition_times, key=lambda x: x[1])[10:]
        for worker_id, acq_time in slow_acquisitions:
            assert acq_time >= 0.1, f"Worker {worker_id} got connection too fast"
    
    @pytest.mark.asyncio
    async def test_connection_lifecycle(self):
        """Test full connection lifecycle management."""
        pool = ConnectionPoolManager(min_size=1, max_size=3)
        
        # Track connection events
        events = []
        
        pool.on_connection_created = lambda conn: events.append(('created', conn.id))
        pool.on_connection_destroyed = lambda conn: events.append(('destroyed', conn.id))
        
        # Use connections
        conn1 = await pool.acquire_connection()
        events.append(('acquired', conn1.id))
        
        await pool.release_connection(conn1)
        events.append(('released', conn1.id))
        
        # Force connection to be destroyed
        pool._mark_unhealthy(conn1)
        await pool.health_check_all()
        
        # Check lifecycle events
        assert ('created', conn1.id) in events
        assert ('acquired', conn1.id) in events
        assert ('released', conn1.id) in events
        assert ('destroyed', conn1.id) in events
    
    @pytest.mark.asyncio
    async def test_pool_resize(self):
        """Test dynamic pool resizing."""
        pool = ConnectionPoolManager(min_size=2, max_size=10)
        
        initial_stats = pool.get_stats()
        assert initial_stats['min_size'] == 2
        assert initial_stats['max_size'] == 10
        
        # Increase pool size
        await pool.resize_pool(min_size=5, max_size=15)
        
        # Should create more connections to meet new minimum
        await asyncio.sleep(0.2)
        stats = pool.get_stats()
        assert stats['total_connections'] >= 5
        assert stats['max_size'] == 15
        
        # Decrease pool size
        await pool.resize_pool(min_size=1, max_size=5)
        
        # Excess connections should be removed
        await asyncio.sleep(0.2)
        stats = pool.get_stats()
        assert stats['total_connections'] <= 5
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown(self):
        """Test graceful pool shutdown."""
        pool = ConnectionPoolManager(min_size=3, max_size=5)
        
        # Acquire some connections
        conns = []
        for _ in range(3):
            conn = await pool.acquire_connection()
            conns.append(conn)
        
        # Start shutdown (should wait for connections to be returned)
        shutdown_task = asyncio.create_task(pool.shutdown())
        
        # Pool should not shutdown immediately
        await asyncio.sleep(0.1)
        assert not shutdown_task.done()
        
        # Release connections
        for conn in conns:
            await pool.release_connection(conn)
        
        # Now shutdown should complete
        await shutdown_task
        
        # Pool should be closed
        with pytest.raises(RuntimeError, match="Pool is closed"):
            await pool.acquire_connection()
    
    @pytest.mark.asyncio
    async def test_connection_timeout(self):
        """Test connection acquisition timeout."""
        pool = ConnectionPoolManager(min_size=1, max_size=1)
        
        # Acquire the only connection
        conn1 = await pool.acquire_connection()
        
        # Try to acquire another with timeout
        with pytest.raises(asyncio.TimeoutError):
            await pool.acquire_connection(timeout=0.5)
        
        # Release and try again
        await pool.release_connection(conn1)
        
        # Should succeed now
        conn2 = await pool.acquire_connection(timeout=0.5)
        assert conn2 is not None
    
    @pytest.mark.asyncio
    async def test_statistics_tracking(self):
        """Test pool statistics tracking."""
        pool = ConnectionPoolManager(min_size=2, max_size=5)
        
        # Reset statistics
        pool.reset_statistics()
        
        # Perform operations
        conn1 = await pool.acquire_connection()
        conn2 = await pool.acquire_connection()
        await pool.release_connection(conn1)
        await pool.release_connection(conn2)
        
        # Check statistics
        stats = pool.get_statistics()
        assert stats['total_acquisitions'] == 2
        assert stats['total_releases'] == 2
        assert stats['current_active'] == 0
        assert stats['peak_active'] == 2
        assert 'average_wait_time' in stats
        assert 'total_wait_time' in stats