"""
Connection Manager

Handles Neo4j driver creation, session management, and connection validation.
"""

import time
import random
import threading
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from .neo4j_types import (
    Neo4jConfig, ConnectionStatus, ConnectionInfo, 
    ConnectionError, ValidationError
)

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages Neo4j driver and session connections with pooling optimization."""
    
    def __init__(self, config: Neo4jConfig):
        self.config = config
        self._driver = None
        self._connection_info = ConnectionInfo(status=ConnectionStatus.DISCONNECTED)
        self._lock = threading.Lock()
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate Neo4j configuration."""
        if not self.config.bolt_uri:
            raise ValidationError("Bolt URI is required")
        
        if not self.config.username or not self.config.password:
            raise ValidationError("Username and password are required")
        
        if self.config.port <= 0 or self.config.port > 65535:
            raise ValidationError("Invalid port number")
        
        if self.config.max_retries < 0:
            raise ValidationError("Max retries cannot be negative")
    
    def get_driver(self):
        """Get optimized Neo4j driver instance with connection pooling."""
        if self._driver is None:
            try:
                from neo4j import GraphDatabase
                
                # Optimized configuration with connection pooling
                self._driver = GraphDatabase.driver(
                    self.config.bolt_uri,
                    auth=(self.config.username, self.config.password),
                    # Connection pooling optimizations
                    max_connection_lifetime=self.config.max_connection_lifetime,
                    max_connection_pool_size=self.config.max_connection_pool_size,
                    connection_timeout=self.config.connection_timeout,
                    connection_acquisition_timeout=self.config.connection_acquisition_timeout,
                    # Performance optimizations
                    keep_alive=self.config.keep_alive
                )
                
                # Test connection with performance logging
                start_time = time.time()
                with self._driver.session() as session:
                    result = session.run("RETURN 1 as test")
                    test_value = result.single()["test"]
                    assert test_value == 1
                
                connection_time = time.time() - start_time
                
                # Update connection info
                self._connection_info = ConnectionInfo(
                    status=ConnectionStatus.CONNECTED,
                    connected_at=datetime.now(),
                    last_activity=datetime.now(),
                    connection_count=1,
                    performance_stats={"initial_connection_time": connection_time}
                )
                
                logger.info(f"Neo4j connection established in {connection_time:.3f}s with optimized pooling")
                
            except Exception as e:
                self._connection_info = ConnectionInfo(
                    status=ConnectionStatus.ERROR,
                    error_message=str(e)
                )
                raise ConnectionError(f"Neo4j connection failed: {e}")
        
        return self._driver
    
    def get_session(self):
        """Get session with exponential backoff and comprehensive retry logic."""
        with self._lock:
            for attempt in range(self.config.max_retries):
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
                    
                    # Update connection info
                    self._connection_info.last_activity = datetime.now()
                    self._connection_info.connection_count += 1
                    
                    return session
                    
                except Exception as e:
                    if attempt == self.config.max_retries - 1:
                        self._connection_info.status = ConnectionStatus.ERROR
                        self._connection_info.error_message = str(e)
                        raise ConnectionError(f"Failed to establish database connection after {self.config.max_retries} attempts: {e}")
                    
                    # Exponential backoff with jitter
                    delay = self.config.retry_delay * (2 ** attempt) * (1 + random.random() * 0.1)
                    delay = min(delay, 5.0)  # Cap at 5 seconds
                    
                    self._connection_info.status = ConnectionStatus.RETRY
                    logger.warning(f"Connection attempt {attempt + 1} failed, retrying in {delay:.2f}s: {e}")
                    
                    # Non-blocking sleep
                    time.sleep(delay)
    
    def _validate_connection(self) -> bool:
        """Validate existing connection is healthy with comprehensive checks."""
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
                
                # Update performance stats
                self._connection_info.performance_stats = {
                    "last_validation_time": connection_time,
                    "validation_timestamp": datetime.now().isoformat()
                }
                
                logger.info(f"Connection validation successful in {connection_time:.3f}s")
                return True
                
        except Exception as e:
            logger.error(f"Connection validation failed with exception: {e}")
            self._connection_info.status = ConnectionStatus.ERROR
            self._connection_info.error_message = str(e)
            return False
    
    def _reconnect(self):
        """Reconnect with proper cleanup and fresh driver creation."""
        # Force cleanup of existing driver
        if self._driver:
            try:
                self._driver.close()
            except Exception as e:
                logger.warning(f"Error closing driver during reconnect: {e}")
            finally:
                self._driver = None
        
        # Brief delay for connection stability
        time.sleep(0.1)
        
        # Create fresh driver with full configuration
        from neo4j import GraphDatabase
        try:
            self._driver = GraphDatabase.driver(
                self.config.bolt_uri,
                auth=(self.config.username, self.config.password),
                connection_timeout=self.config.connection_timeout,
                max_connection_lifetime=self.config.max_connection_lifetime,
                max_connection_pool_size=self.config.max_connection_pool_size,
                connection_acquisition_timeout=self.config.connection_acquisition_timeout
            )
            
            # Validate new connection immediately
            if not self._validate_connection():
                raise ConnectionError("New connection failed validation")
                
            self._connection_info.status = ConnectionStatus.CONNECTED
            self._connection_info.connected_at = datetime.now()
            
        except Exception as e:
            self._driver = None
            self._connection_info.status = ConnectionStatus.ERROR
            self._connection_info.error_message = str(e)
            raise ConnectionError(f"Reconnection failed: {e}")
    
    def test_connection(self) -> bool:
        """Test database connectivity with actual query."""
        try:
            with self.get_session() as session:
                result = session.run("RETURN 1 as test")
                return result.single()["test"] == 1
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_connection_info(self) -> ConnectionInfo:
        """Get current connection information."""
        return self._connection_info
    
    def close(self):
        """Close Neo4j driver and clean up resources."""
        if self._driver:
            try:
                self._driver.close()
                self._connection_info.status = ConnectionStatus.DISCONNECTED
                logger.info("Neo4j driver closed successfully")
            except Exception as e:
                logger.error(f"Error closing Neo4j driver: {e}")
            finally:
                self._driver = None
    
    def get_connection_statistics(self) -> Dict[str, Any]:
        """Get connection statistics and health information."""
        return {
            "status": self._connection_info.status.value,
            "connected_at": self._connection_info.connected_at.isoformat() if self._connection_info.connected_at else None,
            "last_activity": self._connection_info.last_activity.isoformat() if self._connection_info.last_activity else None,
            "connection_count": self._connection_info.connection_count,
            "has_driver": self._driver is not None,
            "config": {
                "max_pool_size": self.config.max_connection_pool_size,
                "connection_timeout": self.config.connection_timeout,
                "max_lifetime": self.config.max_connection_lifetime
            },
            "performance_stats": self._connection_info.performance_stats or {},
            "error_message": self._connection_info.error_message
        }