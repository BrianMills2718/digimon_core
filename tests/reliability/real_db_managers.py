#!/usr/bin/env python3
"""
REAL DATABASE MANAGERS - NO MOCKING
Actual implementations for Neo4j and SQLite connections
"""

import asyncio
import aiosqlite
import uuid
import logging
from typing import Dict, Any, Optional, List
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from contextlib import asynccontextmanager
import time

logger = logging.getLogger(__name__)


class RealNeo4jManager:
    """Real Neo4j database manager with connection pooling"""
    
    def __init__(self, uri: str, auth: tuple, max_connection_pool_size: int = 50):
        self.uri = uri
        self.auth = auth
        self.max_connection_pool_size = max_connection_pool_size
        self.driver: Optional[AsyncDriver] = None
        self._connection_pool = asyncio.Queue(maxsize=max_connection_pool_size)
        self._pool_initialized = False
        
    async def initialize(self):
        """Initialize Neo4j driver and connection pool"""
        if not self.driver:
            self.driver = AsyncGraphDatabase.driver(
                self.uri, 
                auth=self.auth,
                max_connection_pool_size=self.max_connection_pool_size,
                connection_timeout=30,
                max_transaction_retry_time=15
            )
            
            # Verify connection
            async with self.driver.session() as session:
                await session.run("RETURN 1")
            
            logger.info("Neo4j driver initialized")
    
    async def begin_transaction(self):
        """Begin a new Neo4j transaction"""
        if not self.driver:
            await self.initialize()
        
        session = self.driver.session()
        tx = await session.begin_transaction()
        
        # Wrap to include session cleanup
        return Neo4jTransactionWrapper(tx, session)
    
    @asynccontextmanager
    async def get_session(self):
        """Get a Neo4j session"""
        if not self.driver:
            await self.initialize()
        
        session = self.driver.session()
        try:
            yield session
        finally:
            await session.close()
    
    @asynccontextmanager  
    async def get_read_session(self):
        """Get a read-only Neo4j session"""
        if not self.driver:
            await self.initialize()
        
        session = self.driver.session(default_access_mode="READ")
        try:
            yield session
        finally:
            await session.close()
    
    async def shutdown(self):
        """Shutdown Neo4j driver"""
        if self.driver:
            await self.driver.close()
            logger.info("Neo4j driver closed")


class Neo4jTransactionWrapper:
    """Wrapper for Neo4j transaction that includes session cleanup"""
    
    def __init__(self, transaction, session):
        self.transaction = transaction
        self.session = session
        self._committed = False
        self._rolled_back = False
    
    async def run(self, query: str, **parameters):
        """Run query in transaction"""
        return await self.transaction.run(query, **parameters)
    
    async def commit(self):
        """Commit transaction and close session"""
        if not self._committed and not self._rolled_back:
            await self.transaction.commit()
            self._committed = True
        
        await self.session.close()
    
    async def rollback(self):
        """Rollback transaction and close session"""
        if not self._committed and not self._rolled_back:
            await self.transaction.rollback()
            self._rolled_back = True
        
        await self.session.close()


class RealSQLiteManager:
    """Real SQLite database manager with connection pooling"""
    
    def __init__(self, database_path: str, max_connections: int = 50):
        self.database_path = database_path
        self.max_connections = max_connections
        self._connection_pool: List[aiosqlite.Connection] = []
        self._available_connections = asyncio.Queue(maxsize=max_connections)
        self._lock = asyncio.Lock()
        self._initialized = False
    
    async def initialize(self):
        """Initialize SQLite connection pool"""
        if self._initialized:
            return
        
        async with self._lock:
            if self._initialized:
                return
            
            # Create initial connection pool
            for _ in range(min(5, self.max_connections)):  # Start with 5 connections
                conn = await aiosqlite.connect(
                    self.database_path,
                    timeout=30.0,
                    isolation_level=None  # Enable manual transaction control
                )
                
                # Enable foreign key constraints
                await conn.execute("PRAGMA foreign_keys = ON")
                await conn.execute("PRAGMA journal_mode = WAL")  # Better concurrency
                await conn.commit()
                
                self._connection_pool.append(conn)
                await self._available_connections.put(conn)
            
            self._initialized = True
            logger.info(f"SQLite connection pool initialized with {len(self._connection_pool)} connections")
    
    async def _get_connection(self) -> aiosqlite.Connection:
        """Get connection from pool"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Try to get existing connection
            conn = await asyncio.wait_for(self._available_connections.get(), timeout=10.0)
            return conn
        except asyncio.TimeoutError:
            # Pool exhausted, create new connection if under limit
            if len(self._connection_pool) < self.max_connections:
                conn = await aiosqlite.connect(
                    self.database_path,
                    timeout=30.0,
                    isolation_level=None
                )
                await conn.execute("PRAGMA foreign_keys = ON")
                await conn.execute("PRAGMA journal_mode = WAL")
                await conn.commit()
                
                self._connection_pool.append(conn)
                logger.info(f"Created new SQLite connection, pool size: {len(self._connection_pool)}")
                return conn
            else:
                raise Exception("SQLite connection pool exhausted")
    
    def _return_connection(self, conn: aiosqlite.Connection):
        """Return connection to pool"""
        try:
            self._available_connections.put_nowait(conn)
        except asyncio.QueueFull:
            # Pool is full, close this connection
            asyncio.create_task(conn.close())
    
    async def begin_transaction(self):
        """Begin a new SQLite transaction"""
        conn = await self._get_connection()
        
        # Begin transaction
        await conn.execute("BEGIN IMMEDIATE")
        
        return SQLiteTransactionWrapper(conn, self)
    
    @asynccontextmanager
    async def get_read_connection(self):
        """Get a read-only SQLite connection"""
        conn = await self._get_connection()
        try:
            yield conn
        finally:
            self._return_connection(conn)
    
    async def shutdown(self):
        """Shutdown SQLite connection pool"""
        async with self._lock:
            while not self._available_connections.empty():
                try:
                    conn = self._available_connections.get_nowait()
                    await conn.close()
                except:
                    pass
            
            for conn in self._connection_pool:
                try:
                    await conn.close()
                except:
                    pass
            
            self._connection_pool.clear()
            logger.info("SQLite connection pool closed")


class SQLiteTransactionWrapper:
    """Wrapper for SQLite transaction with connection management"""
    
    def __init__(self, connection: aiosqlite.Connection, manager: RealSQLiteManager):
        self.connection = connection
        self.manager = manager
        self._committed = False
        self._rolled_back = False
    
    async def execute(self, query: str, parameters=None):
        """Execute query in transaction"""
        if parameters is None:
            parameters = []
        return await self.connection.execute(query, parameters)
    
    async def executemany(self, query: str, parameters_list):
        """Execute query multiple times in transaction"""
        return await self.connection.executemany(query, parameters_list)
    
    async def commit(self):
        """Commit transaction and return connection to pool"""
        if not self._committed and not self._rolled_back:
            await self.connection.commit()
            self._committed = True
        
        self.manager._return_connection(self.connection)
    
    async def rollback(self):
        """Rollback transaction and return connection to pool"""
        if not self._committed and not self._rolled_back:
            await self.connection.rollback()
            self._rolled_back = True
        
        self.manager._return_connection(self.connection)


class ConnectionHealthMonitor:
    """Monitor health of database connections"""
    
    def __init__(self, neo4j_manager: RealNeo4jManager, sqlite_manager: RealSQLiteManager):
        self.neo4j_manager = neo4j_manager
        self.sqlite_manager = sqlite_manager
        self.monitoring = False
        self.health_stats = {
            'neo4j': {'healthy': True, 'last_check': None, 'error_count': 0},
            'sqlite': {'healthy': True, 'last_check': None, 'error_count': 0}
        }
    
    async def start_monitoring(self, check_interval: int = 30):
        """Start health monitoring"""
        self.monitoring = True
        
        while self.monitoring:
            await self._check_neo4j_health()
            await self._check_sqlite_health()
            await asyncio.sleep(check_interval)
    
    async def _check_neo4j_health(self):
        """Check Neo4j health"""
        try:
            start_time = time.time()
            async with self.neo4j_manager.get_session() as session:
                result = await session.run("RETURN 1 as health_check")
                await result.single()
            
            response_time = time.time() - start_time
            
            self.health_stats['neo4j'].update({
                'healthy': True,
                'last_check': time.time(),
                'response_time': response_time,
                'error_count': 0
            })
            
        except Exception as e:
            self.health_stats['neo4j'].update({
                'healthy': False,
                'last_check': time.time(),
                'last_error': str(e),
                'error_count': self.health_stats['neo4j']['error_count'] + 1
            })
            logger.error(f"Neo4j health check failed: {e}")
    
    async def _check_sqlite_health(self):
        """Check SQLite health"""
        try:
            start_time = time.time()
            async with self.sqlite_manager.get_read_connection() as conn:
                cursor = await conn.execute("SELECT 1 as health_check")
                await cursor.fetchone()
            
            response_time = time.time() - start_time
            
            self.health_stats['sqlite'].update({
                'healthy': True,
                'last_check': time.time(),
                'response_time': response_time,
                'error_count': 0
            })
            
        except Exception as e:
            self.health_stats['sqlite'].update({
                'healthy': False,
                'last_check': time.time(),
                'last_error': str(e),
                'error_count': self.health_stats['sqlite']['error_count'] + 1
            })
            logger.error(f"SQLite health check failed: {e}")
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring = False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        return self.health_stats.copy()


# Performance monitoring utilities
class DatabasePerformanceMonitor:
    """Monitor database performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'neo4j': {'queries': 0, 'total_time': 0, 'errors': 0},
            'sqlite': {'queries': 0, 'total_time': 0, 'errors': 0}
        }
    
    def record_neo4j_query(self, duration: float, success: bool = True):
        """Record Neo4j query performance"""
        self.metrics['neo4j']['queries'] += 1
        self.metrics['neo4j']['total_time'] += duration
        if not success:
            self.metrics['neo4j']['errors'] += 1
    
    def record_sqlite_query(self, duration: float, success: bool = True):
        """Record SQLite query performance"""
        self.metrics['sqlite']['queries'] += 1
        self.metrics['sqlite']['total_time'] += duration
        if not success:
            self.metrics['sqlite']['errors'] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = {}
        
        for db, metrics in self.metrics.items():
            if metrics['queries'] > 0:
                stats[db] = {
                    'total_queries': metrics['queries'],
                    'total_time': metrics['total_time'],
                    'average_time': metrics['total_time'] / metrics['queries'],
                    'error_rate': metrics['errors'] / metrics['queries'],
                    'queries_per_second': metrics['queries'] / metrics['total_time'] if metrics['total_time'] > 0 else 0
                }
            else:
                stats[db] = {
                    'total_queries': 0,
                    'total_time': 0,
                    'average_time': 0,
                    'error_rate': 0,
                    'queries_per_second': 0
                }
        
        return stats
    
    def reset_metrics(self):
        """Reset performance metrics"""
        for db in self.metrics:
            self.metrics[db] = {'queries': 0, 'total_time': 0, 'errors': 0}