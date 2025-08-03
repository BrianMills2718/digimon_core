"""
Async Manager

Handles asynchronous Neo4j operations with real async drivers and non-blocking patterns.
"""

import asyncio
import random
import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from .neo4j_types import Neo4jConfig, ConnectionStatus, ConnectionError, QueryError

logger = logging.getLogger(__name__)


class AsyncManager:
    """Manages asynchronous Neo4j operations with real AsyncGraphDatabase."""
    
    def __init__(self, config: Neo4jConfig):
        self.config = config
        self._async_driver = None
        self._connection_status = ConnectionStatus.DISCONNECTED
        self._last_activity = None
        self.operation_stats = {
            "total_operations": 0,
            "total_time": 0.0,
            "error_count": 0
        }
    
    async def get_session_async(self):
        """Real async session with AsyncGraphDatabase for non-blocking Neo4j operations."""
        # Ensure async driver is available
        if self._async_driver is None:
            await self._ensure_async_driver()
        
        for attempt in range(self.config.max_retries):
            try:
                # Get async session from async driver
                session = self._async_driver.session()
                
                # Test session with real async query
                result = await session.run("RETURN 1 as test")
                record = await result.single()
                if record["test"] != 1:
                    await session.close()
                    raise RuntimeError("Async session validation failed")
                
                # Update stats
                self._last_activity = datetime.now()
                self.operation_stats["total_operations"] += 1
                
                logger.debug("Async Neo4j session created successfully")
                return session
                
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    self._connection_status = ConnectionStatus.ERROR
                    self.operation_stats["error_count"] += 1
                    raise ConnectionError(f"Failed to establish async database connection after {self.config.max_retries} attempts: {e}")
                
                # Real async exponential backoff - NON-BLOCKING
                delay = self.config.retry_delay * (2 ** attempt) * (1 + random.random() * 0.1)
                await asyncio.sleep(min(delay, 30.0))
                logger.warning(f"Async connection attempt {attempt + 1} failed, retrying in {delay:.2f}s: {e}")
    
    async def _ensure_async_driver(self):
        """Ensure async driver is initialized and connected."""
        if self._async_driver is None:
            try:
                from neo4j import AsyncGraphDatabase
                
                # Create real async driver
                self._async_driver = AsyncGraphDatabase.driver(
                    self.config.bolt_uri,
                    auth=(self.config.username, self.config.password),
                    max_connection_lifetime=self.config.max_connection_lifetime,
                    max_connection_pool_size=self.config.max_connection_pool_size,
                    connection_timeout=self.config.connection_timeout,
                    connection_acquisition_timeout=self.config.connection_acquisition_timeout,
                    keep_alive=self.config.keep_alive
                )
                
                # Verify async connection with real async query
                async with self._async_driver.session() as session:
                    result = await session.run("RETURN 1 as test")
                    record = await result.single()
                    assert record["test"] == 1
                
                self._connection_status = ConnectionStatus.CONNECTED
                logger.info("Async Neo4j driver initialized and verified")
                
            except Exception as e:
                logger.error(f"Failed to initialize async Neo4j driver: {e}")
                self._async_driver = None
                self._connection_status = ConnectionStatus.ERROR
                raise ConnectionError(f"Async Neo4j driver initialization failed: {e}")
    
    async def execute_async_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute query asynchronously with full async support."""
        if params is None:
            params = {}
        
        start_time = time.time()
        
        try:
            async with await self.get_session_async() as session:
                result = await session.run(query, params)
                records = []
                
                async for record in result:
                    records.append(dict(record))
                
                execution_time = time.time() - start_time
                
                # Update statistics
                self.operation_stats["total_operations"] += 1
                self.operation_stats["total_time"] += execution_time
                
                logger.debug(f"Async query executed in {execution_time:.3f}s, returned {len(records)} records")
                return records
                
        except Exception as e:
            execution_time = time.time() - start_time
            self.operation_stats["error_count"] += 1
            logger.error(f"Async query execution failed after {execution_time:.3f}s: {e}")
            raise QueryError(f"Async query execution failed: {e}")
    
    async def execute_async_write_transaction(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute write transaction asynchronously."""
        if params is None:
            params = {}
        
        start_time = time.time()
        
        try:
            async with await self.get_session_async() as session:
                async with session.begin_transaction() as tx:
                    result = await tx.run(query, params)
                    summary = await result.consume()
                    await tx.commit()
                    
                    execution_time = time.time() - start_time
                    
                    transaction_result = {
                        'nodes_created': summary.counters.nodes_created,
                        'nodes_deleted': summary.counters.nodes_deleted,
                        'relationships_created': summary.counters.relationships_created,
                        'relationships_deleted': summary.counters.relationships_deleted,
                        'properties_set': summary.counters.properties_set,
                        'query_time': summary.result_available_after + summary.result_consumed_after,
                        'execution_time': execution_time
                    }
                    
                    # Update statistics
                    self.operation_stats["total_operations"] += 1
                    self.operation_stats["total_time"] += execution_time
                    
                    logger.info(f"Async write transaction completed in {execution_time:.3f}s")
                    return transaction_result
                    
        except Exception as e:
            execution_time = time.time() - start_time
            self.operation_stats["error_count"] += 1
            logger.error(f"Async write transaction failed after {execution_time:.3f}s: {e}")
            raise QueryError(f"Async write transaction failed: {e}")
    
    async def execute_concurrent_queries(self, queries_with_params: List[tuple], max_concurrent: int = 5) -> List[Dict[str, Any]]:
        """Execute multiple queries concurrently with controlled concurrency."""
        if not queries_with_params:
            return []
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_single_query(query_data):
            query, params = query_data
            async with semaphore:
                try:
                    return await self.execute_async_query(query, params)
                except Exception as e:
                    logger.error(f"Concurrent query failed: {e}")
                    return {"error": str(e), "query": query[:50] + "..."}
        
        start_time = time.time()
        
        # Execute all queries concurrently
        tasks = [execute_single_query(query_data) for query_data in queries_with_params]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        execution_time = time.time() - start_time
        
        # Process results and handle exceptions
        processed_results = []
        error_count = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "error": str(result),
                    "query_index": i,
                    "query": queries_with_params[i][0][:50] + "..."
                })
                error_count += 1
            else:
                processed_results.append(result)
        
        logger.info(f"Concurrent execution completed: {len(queries_with_params)} queries in {execution_time:.3f}s, {error_count} errors")
        
        return {
            "results": processed_results,
            "total_queries": len(queries_with_params),
            "execution_time": execution_time,
            "error_count": error_count,
            "success_rate": (len(queries_with_params) - error_count) / len(queries_with_params),
            "queries_per_second": len(queries_with_params) / execution_time if execution_time > 0 else 0
        }
    
    async def _wait_for_neo4j_ready_async(self, max_wait: int = 30) -> bool:
        """Async version of waiting for Neo4j to be ready."""
        logger.info(f"⏳ Async waiting for Neo4j to be ready on {self.config.bolt_uri}...")
        
        for i in range(max_wait):
            # Check if port is accessible (using sync check for simplicity)
            if self._is_port_open_sync():
                try:
                    from neo4j import AsyncGraphDatabase
                    test_driver = AsyncGraphDatabase.driver(
                        self.config.bolt_uri, 
                        auth=(self.config.username, self.config.password)
                    )
                    async with test_driver.session() as session:
                        await session.run("RETURN 1")
                    await test_driver.close()
                    
                    logger.info(f"✅ Neo4j ready after {i+1} seconds (async)")
                    return True
                    
                except Exception as e:
                    logger.debug(f"Neo4j async connection attempt failed: {e}")
                    pass
            
            await asyncio.sleep(1)  # ✅ NON-BLOCKING
            if i % 5 == 4:
                logger.info(f"   Still waiting... ({i+1}/{max_wait}s) (async)")
        
        logger.warning(f"❌ Neo4j not ready after {max_wait} seconds (async)")
        return False
    
    def _is_port_open_sync(self, timeout: int = 2) -> bool:
        """Synchronous port check helper."""
        import socket
        try:
            with socket.create_connection((self.config.host, self.config.port), timeout=timeout):
                return True
        except (socket.timeout, socket.error):
            return False
    
    async def _reconnect_async(self):
        """Async reconnect with proper cleanup and fresh async driver creation."""
        # Force cleanup of existing async driver
        if self._async_driver:
            try:
                await self._async_driver.close()
            except Exception as e:
                logger.warning(f"Error closing async driver during reconnect: {e}")
            finally:
                self._async_driver = None
        
        # Wait for cleanup to complete - NON-BLOCKING
        await asyncio.sleep(0.5)
        
        # Create fresh async driver with proper configuration
        from neo4j import AsyncGraphDatabase
        try:
            self._async_driver = AsyncGraphDatabase.driver(
                self.config.bolt_uri,
                auth=(self.config.username, self.config.password),
                connection_timeout=self.config.connection_timeout,
                max_connection_lifetime=self.config.max_connection_lifetime,
                max_connection_pool_size=self.config.max_connection_pool_size,
                connection_acquisition_timeout=self.config.connection_acquisition_timeout,
                keep_alive=self.config.keep_alive
            )
            
            # Test the new async connection
            async with self._async_driver.session() as session:
                await session.run("RETURN 1 as test")
            
            self._connection_status = ConnectionStatus.CONNECTED
            logger.info("Successfully created and tested fresh async Neo4j driver")
            
        except Exception as e:
            logger.error(f"Failed to create fresh async Neo4j driver during reconnect: {e}")
            self._async_driver = None
            self._connection_status = ConnectionStatus.ERROR
            raise ConnectionError(f"Async reconnection failed: {e}")
    
    async def test_async_connection(self) -> bool:
        """Test async database connectivity."""
        try:
            async with await self.get_session_async() as session:
                result = await session.run("RETURN 1 as test")
                record = await result.single()
                return record["test"] == 1
        except Exception as e:
            logger.error(f"Async connection test failed: {e}")
            return False
    
    async def close_async(self):
        """Close async driver and clean up resources."""
        if self._async_driver:
            try:
                await self._async_driver.close()
                self._connection_status = ConnectionStatus.DISCONNECTED
                logger.info("Async Neo4j driver closed successfully")
            except Exception as e:
                logger.error(f"Error closing async Neo4j driver: {e}")
            finally:
                self._async_driver = None
    
    def get_async_statistics(self) -> Dict[str, Any]:
        """Get async operation statistics."""
        avg_time = (
            self.operation_stats["total_time"] / self.operation_stats["total_operations"]
            if self.operation_stats["total_operations"] > 0 else 0.0
        )
        
        error_rate = (
            self.operation_stats["error_count"] / self.operation_stats["total_operations"]
            if self.operation_stats["total_operations"] > 0 else 0.0
        )
        
        return {
            "connection_status": self._connection_status.value,
            "last_activity": self._last_activity.isoformat() if self._last_activity else None,
            "total_operations": self.operation_stats["total_operations"],
            "total_execution_time": self.operation_stats["total_time"],
            "average_execution_time": avg_time,
            "error_count": self.operation_stats["error_count"],
            "error_rate": error_rate,
            "operations_per_second": (
                self.operation_stats["total_operations"] / self.operation_stats["total_time"]
                if self.operation_stats["total_time"] > 0 else 0.0
            ),
            "has_async_driver": self._async_driver is not None
        }
    
    def reset_async_statistics(self):
        """Reset async operation statistics."""
        self.operation_stats = {
            "total_operations": 0,
            "total_time": 0.0,
            "error_count": 0
        }
        logger.info("Async operation statistics reset")
    
    async def health_check_async(self) -> Dict[str, Any]:
        """Perform async health check."""
        try:
            start_time = time.time()
            
            # Test basic connectivity
            result = await self.execute_async_query("RETURN 1 as test")
            
            execution_time = time.time() - start_time
            
            if result and len(result) > 0 and result[0].get("test") == 1:
                return {
                    "status": "healthy",
                    "message": "Async Neo4j connection is working",
                    "response_time": execution_time,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": "Async query returned unexpected result",
                    "response_time": execution_time,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Async health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }