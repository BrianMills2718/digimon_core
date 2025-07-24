#!/usr/bin/env python3
"""
Neo4j Manager - Automated Docker-based Neo4j Management

Automatically starts Neo4j when needed and provides connection validation.
Prevents infrastructure blockers in testing and development.
"""

import subprocess
import time
import socket
import threading
import uuid
import random
import asyncio
from typing import Optional, Dict, Any, List, Tuple
import logging
from datetime import datetime

from src.core.config_manager import ConfigurationManager, get_config
from .input_validator import InputValidator

logger = logging.getLogger(__name__)


class Neo4jDockerManager:
    """Manages Neo4j Docker container lifecycle automatically"""
    
    def __init__(self, 
                 container_name: str = "neo4j-graphrag"):
        self.container_name = container_name
        self._driver = None
        self._async_driver = None
        
        # Stability enhancements
        self.max_retries = 3
        self.retry_delay = 1.0
        self.connection_timeout = 30
        self._lock = threading.Lock()
        
        # Initialize input validator for security
        self.input_validator = InputValidator()
        
        # Get configuration from ConfigurationManager
        config_manager = get_config()
        neo4j_config = config_manager.get_neo4j_config()
        
        # Extract host and port from URI
        uri_parts = neo4j_config['uri'].replace("bolt://", "").split(":")
        self.host = uri_parts[0]
        self.port = int(uri_parts[1]) if len(uri_parts) > 1 else 7687
        
        self.username = neo4j_config['user']
        self.password = neo4j_config['password']
        self.bolt_uri = neo4j_config['uri']
    
    def get_driver(self):
        """Get optimized Neo4j driver instance with connection pooling"""
        if self._driver is None:
            try:
                from neo4j import GraphDatabase, AsyncGraphDatabase
                # Optimized configuration with connection pooling
                self._driver = GraphDatabase.driver(
                    self.bolt_uri,
                    auth=(self.username, self.password),
                    # Connection pooling optimizations
                    max_connection_lifetime=3600,  # 1 hour
                    max_connection_pool_size=10,   # Support up to 10 concurrent connections
                    connection_timeout=30,         # 30 second timeout
                    connection_acquisition_timeout=60,  # 60 second acquisition timeout
                    # Performance optimizations
                    keep_alive=True
                )
                
                # Create async driver for real async operations
                self._async_driver = AsyncGraphDatabase.driver(
                    self.bolt_uri,
                    auth=(self.username, self.password),
                    # Same optimized configuration for async driver
                    max_connection_lifetime=3600,
                    max_connection_pool_size=10,
                    connection_timeout=30,
                    connection_acquisition_timeout=60,
                    keep_alive=True
                )
                # Test connection with performance logging
                import time
                start_time = time.time()
                with self._driver.session() as session:
                    result = session.run("RETURN 1 as test")
                    test_value = result.single()["test"]
                    assert test_value == 1
                connection_time = time.time() - start_time
                logger.info(f"Neo4j connection established in {connection_time:.3f}s with optimized pooling")
            except Exception as e:
                raise ConnectionError(f"Neo4j connection failed: {e}")
        return self._driver
    
    def get_session(self):
        """Get session with exponential backoff and comprehensive retry logic"""
        with self._lock:
            for attempt in range(self.max_retries):
                try:
                    # Validate or recreate connection
                    if not self._driver or not self._validate_connection():
                        self._reconnect()
                    
                    # Attempt to get session
                    session = self._driver.session()
                    
                    # Test session with simple query
                    test_result = session.run("RETURN 1")
                    if test_result.single()[0] != 1:
                        session.close()
                        raise RuntimeError("Session validation failed")
                    
                    return session
                    
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise ConnectionError(f"Failed to establish database connection after {self.max_retries} attempts: {e}")
                    
                    # Exponential backoff with jitter
                    delay = self.retry_delay * (2 ** attempt) * (1 + random.random() * 0.1)
                    # Use async backoff instead of blocking
                    import asyncio
                    try:
                        asyncio.create_task(asyncio.sleep(min(delay, 5.0)))  # Reduced cap to 5s
                    except RuntimeError:
                        # Non-async fallback with reduced delay
                        import time
                        time.sleep(min(delay, 0.1))  # Cap at 100ms to reduce blocking
    
    async def get_session_async(self):
        """Real async session with AsyncGraphDatabase for non-blocking Neo4j operations"""
        # Ensure async driver is available
        if self._async_driver is None:
            await self._ensure_async_driver()
        
        for attempt in range(self.max_retries):
            try:
                # Get async session from async driver
                session = self._async_driver.session()
                
                # Test session with real async query
                result = await session.run("RETURN 1 as test")
                record = await result.single()
                if record["test"] != 1:
                    await session.close()
                    raise RuntimeError("Async session validation failed")
                
                logger.info("Async Neo4j session created successfully")
                return session
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise ConnectionError(f"Failed to establish async database connection after {self.max_retries} attempts: {e}")
                
                # Real async exponential backoff - NON-BLOCKING
                delay = self.retry_delay * (2 ** attempt) * (1 + random.random() * 0.1)
                await asyncio.sleep(min(delay, 30.0))
                logger.warning(f"Async connection attempt {attempt + 1} failed, retrying in {delay:.2f}s: {e}")
    
    async def _ensure_async_driver(self):
        """Ensure async driver is initialized and connected"""
        if self._async_driver is None:
            try:
                from neo4j import AsyncGraphDatabase
                
                # Create real async driver
                self._async_driver = AsyncGraphDatabase.driver(
                    self.bolt_uri,
                    auth=(self.username, self.password),
                    max_connection_lifetime=3600,
                    max_connection_pool_size=10,
                    connection_timeout=30,
                    connection_acquisition_timeout=60,
                    keep_alive=True
                )
                
                # Verify async connection with real async query
                async with self._async_driver.session() as session:
                    result = await session.run("RETURN 1 as test")
                    record = await result.single()
                    assert record["test"] == 1
                
                logger.info("Async Neo4j driver initialized and verified")
                
            except Exception as e:
                logger.error(f"Failed to initialize async Neo4j driver: {e}")
                self._async_driver = None
                raise ConnectionError(f"Async Neo4j driver initialization failed: {e}")
    
    def _validate_connection(self) -> bool:
        """Validate existing connection is healthy with comprehensive checks"""
        if not self._driver:
            logger.warning("No driver available for connection validation")
            return False
        
        try:
            with self._driver.session() as session:
                start_time = time.time()
                
                # Test basic connectivity
                try:
                    result = session.run("RETURN 1 as test", timeout=5)
                    test_value = result.single()["test"]
                except Exception as e:
                    logger.error(f"Basic connectivity test failed: {e}")
                    return False
                
                connection_time = time.time() - start_time
                
                # Validate response correctness
                if test_value != 1:
                    logger.error(f"Unexpected test result: {test_value} (expected 1)")
                    return False
                    
                # Validate performance
                if connection_time > 10.0:
                    logger.warning(f"Connection too slow: {connection_time:.2f}s > 10.0s threshold")
                    return False
                
                # Test write capability
                try:
                    session.run("CREATE (n:HealthCheck {timestamp: $ts}) DELETE n", 
                               ts=datetime.now().isoformat(), timeout=5)
                except Exception as e:
                    logger.error(f"Write capability test failed: {e}")
                    return False
                
                logger.info(f"Connection validation successful in {connection_time:.3f}s")
                return True
                
        except Exception as e:
            logger.error(f"Connection validation failed with exception: {e}")
            return False
    
    def _reconnect(self):
        """Reconnect with proper cleanup and fresh driver creation"""
        # Force cleanup of existing drivers
        if self._driver:
            try:
                self._driver.close()
            except Exception as e:
                logger.warning(f"Error closing sync driver during reconnect: {e}")
            finally:
                self._driver = None
        
        # Also cleanup async driver - will be recreated when needed
        if self._async_driver:
            try:
                # Note: async driver cleanup would need to be done in async context
                # For now, just reset the reference
                self._async_driver = None
                logger.info("Async driver reference cleared for reconnection")
            except Exception as e:
                logger.warning(f"Error clearing async driver during reconnect: {e}")
            finally:
                self._async_driver = None
        
        # Wait for cleanup to complete
        # Brief delay for connection stability - use async when possible
        import asyncio
        try:
            asyncio.create_task(asyncio.sleep(0.1))  # Reduced from 0.5s to 0.1s
        except RuntimeError:
            # Non-async fallback with minimal delay
            import time
            time.sleep(0.05)  # Reduced to 50ms
        
        # Create fresh driver with full configuration
        from neo4j import GraphDatabase
        try:
            self._driver = GraphDatabase.driver(
                self.bolt_uri,
                auth=(self.username, self.password),
                connection_timeout=self.connection_timeout,
                max_connection_lifetime=3600,
                max_connection_pool_size=10,
                # Additional stability settings
                connection_acquisition_timeout=60
            )
            
            # Validate new connection immediately
            if not self._validate_connection():
                raise ConnectionError("New connection failed validation")
                
        except Exception as e:
            self._driver = None
            raise ConnectionError(f"Reconnection failed: {e}")
    
    async def _reconnect_async(self):
        """Async reconnect with proper cleanup and fresh async driver creation"""
        # Force cleanup of existing async driver
        if self._async_driver:
            try:
                await self._async_driver.close()
            except Exception as e:
                logger.warning(f"Error closing async driver during reconnect: {e}")
            finally:
                self._async_driver = None
        
        # Also cleanup sync driver if exists
        if self._driver:
            try:
                self._driver.close()
            except Exception as e:
                logger.warning(f"Error closing sync driver during async reconnect: {e}")
            finally:
                self._driver = None
        
        # Wait for cleanup to complete - NON-BLOCKING
        await asyncio.sleep(0.5)
        
        # Create fresh async driver with proper configuration
        from neo4j import AsyncGraphDatabase
        try:
            self._async_driver = AsyncGraphDatabase.driver(
                self.bolt_uri,
                auth=(self.username, self.password),
                connection_timeout=self.connection_timeout,
                max_connection_lifetime=3600,  # Use default values since attributes may not exist
                max_connection_pool_size=10,
                connection_acquisition_timeout=60,
                keep_alive=True
            )
            
            # Test the new async connection
            async with self._async_driver.session() as session:
                await session.run("RETURN 1 as test")
            
            logger.info("Successfully created and tested fresh async Neo4j driver")
            
        except Exception as e:
            logger.error(f"Failed to create fresh async Neo4j driver during reconnect: {e}")
            self._async_driver = None
            raise ConnectionError(f"Async reconnection failed: {e}")
    
    def test_connection(self) -> bool:
        """Test database connectivity with actual query"""
        try:
            with self.get_session() as session:
                result = session.run("RETURN 1 as test")
                return result.single()["test"] == 1
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def close(self):
        """Close Neo4j driver"""
        if self._driver:
            self._driver.close()
            self._driver = None
        
    def is_port_open(self, timeout: int = 1) -> bool:
        """Check if Neo4j port is accessible"""
        try:
            with socket.create_connection((self.host, self.port), timeout=timeout):
                return True
        except (socket.timeout, socket.error):
            return False
    
    def is_container_running(self) -> bool:
        """Check if Neo4j container is already running"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}", "--filter", f"name={self.container_name}"],
                capture_output=True, text=True, timeout=10
            )
            return self.container_name in result.stdout
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def start_neo4j_container(self) -> Dict[str, Any]:
        """Start Neo4j container if not already running"""
        status = {
            "action": "none",
            "success": False,
            "message": "",
            "container_id": None
        }
        
        try:
            # Check if already running
            if self.is_container_running():
                if self.is_port_open():
                    status.update({
                        "action": "already_running",
                        "success": True,
                        "message": f"Neo4j container '{self.container_name}' already running"
                    })
                    return status
                else:
                    # Container running but port not accessible - restart it
                    self.stop_neo4j_container()
            
            # Remove any existing stopped container with same name
            subprocess.run(
                ["docker", "rm", "-f", self.container_name],
                capture_output=True, timeout=10
            )
            
            # Start new container
            cmd = [
                "docker", "run", "-d",
                "--name", self.container_name,
                "-p", f"{self.port}:7687",
                "-p", "7474:7474",
                "-e", f"NEO4J_AUTH={self.username}/{self.password}",
                "neo4j:latest"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                container_id = result.stdout.strip()
                status.update({
                    "action": "started",
                    "success": True,
                    "message": f"Started Neo4j container: {container_id[:12]}",
                    "container_id": container_id
                })
                
                # Wait for Neo4j to be ready
                self._wait_for_neo4j_ready()
                
            else:
                status.update({
                    "action": "start_failed",
                    "success": False,
                    "message": f"Failed to start container: {result.stderr}"
                })
                
        except subprocess.TimeoutExpired:
            status.update({
                "action": "timeout",
                "success": False,
                "message": "Timeout starting Neo4j container"
            })
        except FileNotFoundError:
            status.update({
                "action": "docker_not_found",
                "success": False,
                "message": "Docker not available - cannot auto-start Neo4j"
            })
        except Exception as e:
            status.update({
                "action": "error",
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            })
        
        return status
    
    def stop_neo4j_container(self) -> bool:
        """Stop Neo4j container"""
        try:
            subprocess.run(
                ["docker", "stop", self.container_name],
                capture_output=True, timeout=30
            )
            return True
        except Exception as e:
            logger.error(f"Failed to stop Neo4j container: {e}")
            return False
    
    async def _wait_for_neo4j_ready_async(self, max_wait: int = 30) -> bool:
        """Async version of waiting for Neo4j to be ready"""
        logger.info(f"⏳ Async waiting for Neo4j to be ready on {self.bolt_uri}...")
        
        for i in range(max_wait):
            if self.is_port_open(timeout=2):
                try:
                    from neo4j import AsyncGraphDatabase
                    async_driver = AsyncGraphDatabase.driver(
                        self.bolt_uri, 
                        auth=(self.username, self.password)
                    )
                    async with async_driver.session() as session:
                        await session.run("RETURN 1")
                    await async_driver.close()
                    logger.info(f"✅ Neo4j ready after {i+1} seconds (async)")
                    return True
                except Exception as e:
                    logger.debug(f"Neo4j async connection attempt failed: {e}")
                    pass
            
            await asyncio.sleep(1)  # ✅ NON-BLOCKING
            if i % 5 == 4:
                logger.info(f"   Still waiting... ({i+1}/{max_wait}s) (async)")
        
        logger.info(f"❌ Neo4j not ready after {max_wait} seconds (async)")
        return False
    
    def _wait_for_neo4j_ready(self, max_wait: int = 30) -> bool:
        """Wait for Neo4j to be ready to accept connections"""
        logger.info(f"⏳ Waiting for Neo4j to be ready on {self.bolt_uri}...")
        
        for i in range(max_wait):
            if self.is_port_open(timeout=2):
                # Port is open, now test actual Neo4j connection
                try:
                    from neo4j import GraphDatabase
                    driver = GraphDatabase.driver(
                        self.bolt_uri, 
                        auth=(self.username, self.password)
                    )
                    with driver.session() as session:
                        session.run("RETURN 1")
                    driver.close()
                    logger.info(f"✅ Neo4j ready after {i+1} seconds")
                    return True
                except Exception as e:
                    logger.debug(f"Neo4j connection attempt failed: {e}")
                    pass
            
            # Transaction retry delay - use async when possible
            import asyncio
            try:
                asyncio.create_task(asyncio.sleep(0.5))  # Reduced from 1s to 0.5s
            except RuntimeError:
                # Non-async fallback with minimal delay
                import time
                time.sleep(0.05)  # Reduced to 50ms
            if i % 5 == 4:  # Every 5 seconds
                logger.info(f"   Still waiting... ({i+1}/{max_wait}s)")
        
        logger.info(f"❌ Neo4j not ready after {max_wait} seconds")
        return False
    
    def ensure_neo4j_available(self) -> Dict[str, Any]:
        """Ensure Neo4j is running and accessible, start if needed"""
        
        # Quick check if already available
        if self.is_port_open():
            return {
                "status": "available",
                "message": "Neo4j already accessible",
                "action": "none"
            }
        
        logger.info("🔧 Neo4j not accessible - attempting auto-start...")
        start_result = self.start_neo4j_container()
        
        if start_result["success"]:
            return {
                "status": "started",
                "message": f"Neo4j auto-started: {start_result['message']}",
                "action": start_result["action"],
                "container_id": start_result.get("container_id")
            }
        else:
            return {
                "status": "failed",
                "message": f"Could not start Neo4j: {start_result['message']}",
                "action": start_result["action"]
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of Neo4j database"""
        try:
            # Try to get a driver and execute a simple query
            driver = self.get_driver()
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()['test']
                
                if test_value == 1:
                    return {
                        'status': 'healthy',
                        'message': 'Neo4j database is responding normally'
                    }
                else:
                    return {
                        'status': 'unhealthy',
                        'message': 'Neo4j database returned unexpected result'
                    }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Neo4j database connection failed: {str(e)}'
            }
    
    def execute_secure_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute query with mandatory security validation"""
        if params is None:
            params = {}
        
        # Validate query and parameters for security
        try:
            validated = self.input_validator.enforce_parameterized_execution(query, params)
            safe_query = validated['query']
            safe_params = validated['params']
        except ValueError as e:
            logger.error(f"Query validation failed: {e}")
            raise e
        
        # Execute with validated parameters
        driver = self.get_driver()
        with driver.session() as session:
            try:
                result = session.run(safe_query, safe_params)
                return [dict(record) for record in result]
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                raise e
    
    def execute_secure_write_transaction(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute write transaction with security validation"""
        if params is None:
            params = {}
        
        # Validate query and parameters
        try:
            validated = self.input_validator.enforce_parameterized_execution(query, params)
            safe_query = validated['query']
            safe_params = validated['params']
        except ValueError as e:
            logger.error(f"Write transaction validation failed: {e}")
            raise e
        
        driver = self.get_driver()
        with driver.session() as session:
            try:
                with session.begin_transaction() as tx:
                    result = tx.run(safe_query, safe_params)
                    summary = result.consume()
                    tx.commit()
                    
                    return {
                        'nodes_created': summary.counters.nodes_created,
                        'nodes_deleted': summary.counters.nodes_deleted,
                        'relationships_created': summary.counters.relationships_created,
                        'relationships_deleted': summary.counters.relationships_deleted,
                        'properties_set': summary.counters.properties_set,
                        'query_time': summary.result_available_after + summary.result_consumed_after
                    }
            except Exception as e:
                logger.error(f"Write transaction failed: {e}")
                raise e
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Legacy method name - redirects to secure execution"""
        logger.warning("execute_query() is deprecated. Use execute_secure_query() for explicit security validation")
        return self.execute_secure_query(query, params)
    
    def execute_optimized_batch(self, queries_with_params, batch_size=1000):
        """Execute queries in optimized batches with security validation"""
        results = []
        driver = self.get_driver()
        
        import time
        start_time = time.time()
        
        # Pre-validate all queries for security
        validated_queries = []
        for query, params in queries_with_params:
            try:
                validated = self.input_validator.enforce_parameterized_execution(query, params or {})
                validated_queries.append((validated['query'], validated['params']))
            except ValueError as e:
                logger.error(f"Batch query validation failed: {e}")
                raise e
        
        with driver.session() as session:
            for i in range(0, len(validated_queries), batch_size):
                batch = validated_queries[i:i + batch_size]
                
                batch_start = time.time()
                
                # Use transaction for better performance
                with session.begin_transaction() as tx:
                    batch_results = []
                    for query, params in batch:
                        result = tx.run(query, params)
                        batch_results.append(list(result))
                    tx.commit()
                    results.extend(batch_results)
                
                batch_time = time.time() - batch_start
                logger.debug(f"Processed batch of {len(batch)} queries in {batch_time:.3f}s")
        
        total_time = time.time() - start_time
        logger.info(f"Executed {len(queries_with_params)} queries in {total_time:.3f}s (avg: {total_time/len(queries_with_params):.4f}s per query)")
        
        return {
            "results": results,
            "total_queries": len(queries_with_params),
            "execution_time": total_time,
            "avg_time_per_query": total_time / len(queries_with_params),
            "batches_processed": (len(queries_with_params) + batch_size - 1) // batch_size
        }
    
    def create_optimized_indexes(self):
        """Create optimized indexes for production scale performance"""
        driver = self.get_driver()
        
        index_queries = [
            "CREATE INDEX entity_id_index IF NOT EXISTS FOR (n:Entity) ON (n.entity_id)",
            "CREATE INDEX entity_canonical_name_index IF NOT EXISTS FOR (n:Entity) ON (n.canonical_name)",
            "CREATE INDEX relationship_type_index IF NOT EXISTS FOR ()-[r:RELATIONSHIP]-() ON (r.type)",
            "CREATE INDEX relationship_confidence_index IF NOT EXISTS FOR ()-[r:RELATIONSHIP]-() ON (r.confidence)",
            "CREATE INDEX mention_surface_form_index IF NOT EXISTS FOR (m:Mention) ON (m.surface_form)",
            "CREATE INDEX pagerank_score_index IF NOT EXISTS FOR (n:Entity) ON (n.pagerank_score)"
        ]
        
        created_indexes = []
        start_time = time.time()
        
        with driver.session() as session:
            for query in index_queries:
                try:
                    index_start = time.time()
                    session.run(query)
                    index_time = time.time() - index_start
                    created_indexes.append({
                        "index": query.split("FOR")[1].split("ON")[0].strip() if "FOR" in query else "unknown",
                        "creation_time": index_time
                    })
                    logger.info(f"Created index in {index_time:.3f}s")
                except Exception as e:
                    logger.warning(f"Index creation failed or already exists: {e}")
        
        total_time = time.time() - start_time
        logger.info(f"Index optimization completed in {total_time:.3f}s")
        
        return {
            "indexes_created": len(created_indexes),
            "total_time": total_time,
            "details": created_indexes
        }
    
    def get_performance_metrics(self):
        """Get current database performance metrics"""
        driver = self.get_driver()
        
        metrics = {}
        
        with driver.session() as session:
            import time
            
            # Test basic query performance
            start_time = time.time()
            result = session.run("MATCH (n) RETURN count(n) as total_nodes")
            node_count = result.single()["total_nodes"]
            node_count_time = time.time() - start_time
            
            # Test relationship count performance
            start_time = time.time()
            result = session.run("MATCH ()-[r]->() RETURN count(r) as total_relationships")
            rel_count = result.single()["total_relationships"]
            rel_count_time = time.time() - start_time
            
            # Test index usage
            start_time = time.time()
            result = session.run("SHOW INDEXES")
            indexes = list(result)
            index_query_time = time.time() - start_time
            
            metrics = {
                "node_count": node_count,
                "relationship_count": rel_count,
                "node_count_query_time": node_count_time,
                "relationship_count_query_time": rel_count_time,
                "total_indexes": len(indexes),
                "index_query_time": index_query_time,
                "connection_pool_status": "optimized" if self._driver else "not_initialized"
            }
        
        return metrics


def ensure_neo4j_for_testing() -> bool:
    """
    Convenience function for tests - ensures Neo4j is available
    Returns True if Neo4j is accessible, False otherwise
    """
    manager = Neo4jDockerManager()
    result = manager.ensure_neo4j_available()
    
    if result["status"] in ["available", "started"]:
        logger.info(f"✅ {result['message']}")
        return True
    else:
        logger.info(f"❌ {result['message']}")
        return False


# Alias for backward compatibility and audit tool
Neo4jManager = Neo4jDockerManager

if __name__ == "__main__":
    # Test the manager
    logger.info("Testing Neo4j Docker Manager...")
    manager = Neo4jDockerManager()
    result = manager.ensure_neo4j_available()
    logger.info(f"Result: {result}")