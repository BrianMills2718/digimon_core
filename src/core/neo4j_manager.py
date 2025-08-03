#!/usr/bin/env python3
"""
Neo4j Manager - Streamlined Docker-based Neo4j Management

Automatically starts Neo4j when needed and provides connection validation.
Prevents infrastructure blockers in testing and development.

This is the streamlined version using decomposed components.
"""

import logging
from typing import Optional, Dict, Any, List

from src.core.config_manager import ConfigurationManager, get_config
from .input_validator import InputValidator
from .neo4j_management import (
    Neo4jConfig,
    ConnectionManager,
    DockerManager, 
    QueryExecutor,
    PerformanceMonitor,
    AsyncManager,
    Neo4jConfigManager
)

logger = logging.getLogger(__name__)


class Neo4jDockerManager:
    """Manages Neo4j Docker container lifecycle automatically using decomposed components."""
    
    def __init__(self, container_name: str = "neo4j-graphrag"):
        self.container_name = container_name
        
        # Initialize input validator for security
        self.input_validator = InputValidator()
        
        # Get configuration from ConfigurationManager
        config_manager = get_config()
        external_config = {
            'neo4j': config_manager.get_neo4j_config()
        }
        
        # Create Neo4j configuration using config manager
        neo4j_config_manager = Neo4jConfigManager()
        self.config = neo4j_config_manager.create_config_from_external_config(external_config)
        self.config.container_name = container_name
        
        # Initialize component managers
        self.connection_manager = ConnectionManager(self.config)
        self.docker_manager = DockerManager(self.config)
        self.query_executor = QueryExecutor(self.config, self.connection_manager, self.input_validator)
        self.performance_monitor = PerformanceMonitor(self.config, self.connection_manager)
        self.async_manager = AsyncManager(self.config)
        
        logger.info(f"Neo4j Docker Manager initialized for container: {container_name}")
    
    # Connection Management Delegation
    def get_driver(self):
        """Get optimized Neo4j driver instance with connection pooling."""
        return self.connection_manager.get_driver()
    
    def get_session(self):
        """Get session with exponential backoff and comprehensive retry logic."""
        return self.connection_manager.get_session()
    
    def test_connection(self) -> bool:
        """Test database connectivity with actual query."""
        return self.connection_manager.test_connection()
    
    def close(self):
        """Close Neo4j driver and clean up resources."""
        self.connection_manager.close()
    
    # Docker Container Management Delegation
    def is_port_open(self, timeout: int = 1) -> bool:
        """Check if Neo4j port is accessible."""
        return self.docker_manager.is_port_open(timeout)
    
    def is_container_running(self) -> bool:
        """Check if Neo4j container is already running."""
        return self.docker_manager.is_container_running()
    
    def start_neo4j_container(self) -> Dict[str, Any]:
        """Start Neo4j container if not already running."""
        return self.docker_manager.start_neo4j_container()
    
    def stop_neo4j_container(self) -> bool:
        """Stop Neo4j container."""
        return self.docker_manager.stop_neo4j_container()
    
    def ensure_neo4j_available(self) -> Dict[str, Any]:
        """Ensure Neo4j is running and accessible, start if needed."""
        return self.docker_manager.ensure_neo4j_available()
    
    # Query Execution Delegation
    def execute_secure_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute query with mandatory security validation."""
        return self.query_executor.execute_secure_query(query, params)
    
    def execute_secure_write_transaction(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute write transaction with security validation."""
        return self.query_executor.execute_secure_write_transaction(query, params)
    
    def execute_optimized_batch(self, queries_with_params, batch_size=1000):
        """Execute queries in optimized batches with security validation."""
        return self.query_executor.execute_optimized_batch(queries_with_params, batch_size)
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Legacy method name - redirects to secure execution."""
        return self.query_executor.execute_query(query, params)
    
    # Performance Monitoring Delegation
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of Neo4j database."""
        return self.performance_monitor.get_health_status()
    
    def create_optimized_indexes(self):
        """Create optimized indexes for production scale performance."""
        return self.performance_monitor.create_optimized_indexes()
    
    def get_performance_metrics(self):
        """Get current database performance metrics."""
        return self.performance_monitor.get_performance_metrics()
    
    # Async Operations Delegation
    async def get_session_async(self):
        """Real async session with AsyncGraphDatabase for non-blocking Neo4j operations."""
        return await self.async_manager.get_session_async()
    
    async def execute_async_query(self, query: str, params: Dict[str, Any] = None):
        """Execute query asynchronously with full async support."""
        return await self.async_manager.execute_async_query(query, params)
    
    async def execute_async_write_transaction(self, query: str, params: Dict[str, Any] = None):
        """Execute write transaction asynchronously."""
        return await self.async_manager.execute_async_write_transaction(query, params)
    
    async def close_async(self):
        """Close async driver and clean up resources."""
        await self.async_manager.close_async()
    
    # Comprehensive Status and Statistics
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive status from all components."""
        return {
            "connection": self.connection_manager.get_connection_statistics(),
            "container": self.docker_manager.get_container_statistics(),
            "query_performance": self.query_executor.get_query_statistics(),
            "async_operations": self.async_manager.get_async_statistics(),
            "health": self.performance_monitor.get_health_status(),
            "config_summary": self._get_config_summary()
        }
    
    def _get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary."""
        neo4j_config_manager = Neo4jConfigManager()
        return neo4j_config_manager.export_config_summary(self.config)
    
    # Advanced Operations
    def analyze_query_performance(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze performance of a specific query."""
        return self.performance_monitor.analyze_query_performance(query, params)
    
    def get_index_statistics(self) -> Dict[str, Any]:
        """Get statistics about database indexes."""
        return self.performance_monitor.get_index_statistics()
    
    def get_database_size_info(self) -> Dict[str, Any]:
        """Get database size and storage information."""
        return self.performance_monitor.get_database_size_info()
    
    def validate_query_syntax(self, query: str) -> bool:
        """Validate Cypher query syntax without executing."""
        return self.query_executor.validate_query_syntax(query)
    
    # Maintenance Operations
    def reset_statistics(self) -> None:
        """Reset all performance statistics."""
        self.query_executor.reset_statistics()
        self.async_manager.reset_async_statistics()
        self.performance_monitor.clear_performance_history()
        logger.info("All Neo4j manager statistics reset")
    
    def get_container_logs(self, tail_lines: int = 50) -> str:
        """Get container logs for debugging."""
        return self.docker_manager.get_container_logs(tail_lines)


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
    
    # Show comprehensive status
    status = manager.get_comprehensive_status()
    logger.info(f"Comprehensive Status: {status}")