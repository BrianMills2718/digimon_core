"""
Connection Pool Manager for Neo4j and SQLite.

Provides efficient connection pooling with health checks, automatic recovery,
and graceful resource management.
"""

import asyncio
import time
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from neo4j import AsyncGraphDatabase
import aiosqlite

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """Connection state enumeration."""
    IDLE = "idle"
    ACTIVE = "active"
    UNHEALTHY = "unhealthy"
    CLOSED = "closed"


@dataclass
class PooledConnection:
    """Wrapper for pooled connections."""
    id: str
    connection: Any  # Neo4j session or SQLite connection
    state: ConnectionState = ConnectionState.IDLE
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    use_count: int = 0
    health_check_failures: int = 0
    
    def is_healthy(self) -> bool:
        """Check if connection is healthy."""
        return self.state != ConnectionState.UNHEALTHY and self.health_check_failures < 3


class ConnectionPoolManager:
    """
    Manages connection pools with health checking and recovery.
    
    Features:
    - Dynamic pool sizing
    - Health checks and automatic recovery
    - Connection lifecycle management
    - Graceful shutdown
    - Statistics tracking
    """
    
    def __init__(self, min_size: int = 5, max_size: int = 20, 
                 connection_type: str = "neo4j",
                 connection_params: Optional[Dict[str, Any]] = None):
        """
        Initialize connection pool manager.
        
        Args:
            min_size: Minimum number of connections to maintain
            max_size: Maximum number of connections allowed
            connection_type: Type of connection (neo4j or sqlite)
            connection_params: Connection parameters
        """
        self.min_size = min_size
        self.max_size = max_size
        self.connection_type = connection_type
        self.connection_params = connection_params or {}
        
        self._pool: List[PooledConnection] = []
        self._available: asyncio.Queue = asyncio.Queue()
        self._lock = asyncio.Lock()
        self._closed = False
        self._waiters: List[asyncio.Future] = []
        
        # Statistics
        self._stats = {
            'total_acquisitions': 0,
            'total_releases': 0,
            'total_wait_time': 0.0,
            'peak_active': 0,
            'connection_creates': 0,
            'connection_destroys': 0,
            'health_check_failures': 0
        }
        
        # Callbacks
        self.on_connection_created: Optional[Callable] = None
        self.on_connection_destroyed: Optional[Callable] = None
        
        # Background tasks
        self._health_check_task = None
        self._maintenance_task = None
        
        logger.info(f"ConnectionPoolManager initialized: min={min_size}, max={max_size}")
        
        # Start pool initialization
        asyncio.create_task(self._initialize_pool())
    
    async def _initialize_pool(self) -> None:
        """Initialize the connection pool with minimum connections."""
        tasks = []
        for _ in range(self.min_size):
            tasks.append(self._create_connection())
        
        connections = await asyncio.gather(*tasks, return_exceptions=True)
        
        async with self._lock:
            for conn in connections:
                if isinstance(conn, PooledConnection):
                    self._pool.append(conn)
                    await self._available.put(conn)
        
        # Start background tasks
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        self._maintenance_task = asyncio.create_task(self._maintenance_loop())
        
        logger.info(f"Pool initialized with {len(self._pool)} connections")
    
    async def _create_connection(self) -> PooledConnection:
        """Create a new connection."""
        conn_id = str(uuid.uuid4())[:8]
        
        try:
            if self.connection_type == "neo4j":
                driver = AsyncGraphDatabase.driver(
                    self.connection_params.get('uri', 'bolt://localhost:7687'),
                    auth=self.connection_params.get('auth', ('neo4j', 'password'))
                )
                connection = driver.session()
            elif self.connection_type == "sqlite":
                connection = await aiosqlite.connect(
                    self.connection_params.get('database', ':memory:')
                )
            else:
                raise ValueError(f"Unknown connection type: {self.connection_type}")
            
            pooled_conn = PooledConnection(
                id=conn_id,
                connection=connection,
                state=ConnectionState.IDLE
            )
            
            self._stats['connection_creates'] += 1
            
            if self.on_connection_created:
                self.on_connection_created(pooled_conn)
            
            logger.debug(f"Created connection {conn_id}")
            return pooled_conn
            
        except Exception as e:
            logger.error(f"Failed to create connection: {e}")
            raise
    
    async def acquire_connection(self, timeout: Optional[float] = 30.0) -> Any:
        """
        Acquire a connection from the pool.
        
        Args:
            timeout: Maximum time to wait for connection
            
        Returns:
            Connection object
            
        Raises:
            asyncio.TimeoutError: If timeout exceeded
            RuntimeError: If pool is closed
        """
        if self._closed:
            raise RuntimeError("Pool is closed")
        
        start_time = time.time()
        self._stats['total_acquisitions'] += 1
        
        try:
            # Try to get available connection
            if timeout:
                conn = await asyncio.wait_for(
                    self._acquire_connection(), 
                    timeout=timeout
                )
            else:
                conn = await self._acquire_connection()
            
            wait_time = time.time() - start_time
            self._stats['total_wait_time'] += wait_time
            
            # Update peak active connections
            active_count = sum(1 for c in self._pool if c.state == ConnectionState.ACTIVE)
            self._stats['peak_active'] = max(self._stats['peak_active'], active_count)
            
            return conn.connection
            
        except asyncio.TimeoutError:
            logger.warning(f"Connection acquisition timed out after {timeout}s")
            raise
    
    async def _acquire_connection(self) -> PooledConnection:
        """Internal method to acquire connection."""
        while True:
            try:
                # Try to get from available queue
                conn = self._available.get_nowait()
                
                # Check if connection is still healthy
                if conn.is_healthy():
                    conn.state = ConnectionState.ACTIVE
                    conn.last_used = datetime.now()
                    conn.use_count += 1
                    return conn
                else:
                    # Unhealthy connection, destroy it
                    await self._destroy_connection(conn)
                    
            except asyncio.QueueEmpty:
                # No available connections
                async with self._lock:
                    # Can we create more?
                    if len(self._pool) < self.max_size:
                        conn = await self._create_connection()
                        self._pool.append(conn)
                        conn.state = ConnectionState.ACTIVE
                        conn.use_count += 1
                        return conn
                
                # Need to wait for a connection
                await asyncio.sleep(0.1)
    
    async def release_connection(self, connection: Any) -> None:
        """
        Release a connection back to the pool.
        
        Args:
            connection: Connection to release
        """
        self._stats['total_releases'] += 1
        
        async with self._lock:
            # Find the pooled connection wrapper
            for conn in self._pool:
                if conn.connection == connection:
                    if conn.state == ConnectionState.ACTIVE:
                        conn.state = ConnectionState.IDLE
                        conn.last_used = datetime.now()
                        await self._available.put(conn)
                    break
            else:
                logger.warning("Released connection not found in pool")
    
    async def health_check_all(self) -> int:
        """
        Perform health checks on all connections.
        
        Returns:
            Number of healthy connections
        """
        healthy_count = 0
        
        async with self._lock:
            for conn in self._pool[:]:  # Copy list to allow modification
                if await self._check_connection_health(conn):
                    healthy_count += 1
                else:
                    conn.health_check_failures += 1
                    if conn.health_check_failures >= 3:
                        await self._destroy_connection(conn)
                        self._pool.remove(conn)
        
        # Ensure minimum connections
        await self._ensure_minimum_connections()
        
        return healthy_count
    
    async def _check_connection_health(self, conn: PooledConnection) -> bool:
        """Check if a connection is healthy."""
        if conn.state == ConnectionState.CLOSED:
            return False
        
        try:
            if self.connection_type == "neo4j":
                # Test Neo4j connection
                result = await conn.connection.run("RETURN 1")
                await result.consume()
            elif self.connection_type == "sqlite":
                # Test SQLite connection
                await conn.connection.execute("SELECT 1")
            
            return True
            
        except Exception as e:
            logger.warning(f"Health check failed for connection {conn.id}: {e}")
            self._stats['health_check_failures'] += 1
            return False
    
    async def _ensure_minimum_connections(self) -> None:
        """Ensure pool has minimum number of connections."""
        async with self._lock:
            current_count = len(self._pool)
            if current_count < self.min_size:
                tasks = []
                for _ in range(self.min_size - current_count):
                    tasks.append(self._create_connection())
                
                new_connections = await asyncio.gather(*tasks, return_exceptions=True)
                
                for conn in new_connections:
                    if isinstance(conn, PooledConnection):
                        self._pool.append(conn)
                        await self._available.put(conn)
    
    async def resize_pool(self, min_size: Optional[int] = None, 
                         max_size: Optional[int] = None) -> None:
        """
        Dynamically resize the connection pool.
        
        Args:
            min_size: New minimum size
            max_size: New maximum size
        """
        async with self._lock:
            if min_size is not None:
                self.min_size = min_size
            if max_size is not None:
                self.max_size = max_size
            
            # Remove excess connections if needed
            if len(self._pool) > self.max_size:
                excess = len(self._pool) - self.max_size
                for _ in range(excess):
                    try:
                        conn = self._available.get_nowait()
                        await self._destroy_connection(conn)
                        self._pool.remove(conn)
                    except asyncio.QueueEmpty:
                        break
        
        # Ensure minimum connections
        await self._ensure_minimum_connections()
        
        logger.info(f"Pool resized: min={self.min_size}, max={self.max_size}")
    
    async def _destroy_connection(self, conn: PooledConnection) -> None:
        """Destroy a connection."""
        try:
            conn.state = ConnectionState.CLOSED
            
            if self.connection_type == "neo4j":
                await conn.connection.close()
            elif self.connection_type == "sqlite":
                await conn.connection.close()
            
            self._stats['connection_destroys'] += 1
            
            if self.on_connection_destroyed:
                self.on_connection_destroyed(conn)
            
            logger.debug(f"Destroyed connection {conn.id}")
            
        except Exception as e:
            logger.error(f"Error destroying connection {conn.id}: {e}")
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the connection pool."""
        logger.info("Shutting down connection pool")
        self._closed = True
        
        # Cancel background tasks
        if self._health_check_task:
            self._health_check_task.cancel()
        if self._maintenance_task:
            self._maintenance_task.cancel()
        
        # Wait for all connections to be returned
        timeout = 30
        start = time.time()
        
        while time.time() - start < timeout:
            active_count = sum(1 for c in self._pool if c.state == ConnectionState.ACTIVE)
            if active_count == 0:
                break
            await asyncio.sleep(0.1)
        
        # Destroy all connections
        async with self._lock:
            for conn in self._pool:
                await self._destroy_connection(conn)
            self._pool.clear()
        
        logger.info("Connection pool shutdown complete")
    
    async def _health_check_loop(self) -> None:
        """Background task for periodic health checks."""
        while not self._closed:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self.health_check_all()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
    
    async def _maintenance_loop(self) -> None:
        """Background task for pool maintenance."""
        while not self._closed:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                # Remove old idle connections
                async with self._lock:
                    now = datetime.now()
                    for conn in self._pool[:]:
                        if (conn.state == ConnectionState.IDLE and 
                            now - conn.last_used > timedelta(minutes=5)):
                            # Remove idle connection older than 5 minutes
                            await self._destroy_connection(conn)
                            self._pool.remove(conn)
                
                # Ensure minimum connections
                await self._ensure_minimum_connections()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Maintenance loop error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        active_count = sum(1 for c in self._pool if c.state == ConnectionState.ACTIVE)
        idle_count = sum(1 for c in self._pool if c.state == ConnectionState.IDLE)
        
        return {
            'total_connections': len(self._pool),
            'active_connections': active_count,
            'idle_connections': idle_count,
            'min_size': self.min_size,
            'max_size': self.max_size,
            'current_active': active_count
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics."""
        stats = self.get_stats()
        stats.update(self._stats)
        
        # Calculate averages
        if self._stats['total_acquisitions'] > 0:
            stats['average_wait_time'] = (
                self._stats['total_wait_time'] / self._stats['total_acquisitions']
            )
        else:
            stats['average_wait_time'] = 0.0
        
        return stats
    
    def reset_statistics(self) -> None:
        """Reset statistics counters."""
        self._stats = {
            'total_acquisitions': 0,
            'total_releases': 0,
            'total_wait_time': 0.0,
            'peak_active': 0,
            'connection_creates': 0,
            'connection_destroys': 0,
            'health_check_failures': 0
        }
    
    # Test helper methods
    def _mark_unhealthy(self, connection: Any) -> None:
        """Mark a connection as unhealthy (for testing)."""
        for conn in self._pool:
            if conn.connection == connection:
                conn.state = ConnectionState.UNHEALTHY
                break
    
    async def _simulate_all_connections_failed(self) -> None:
        """Simulate all connections failing (for testing)."""
        async with self._lock:
            for conn in self._pool:
                conn.state = ConnectionState.UNHEALTHY
                conn.health_check_failures = 3
    
    async def trigger_recovery(self) -> None:
        """Trigger connection recovery (for testing)."""
        await self.health_check_all()