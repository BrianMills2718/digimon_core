"""
Async Connection Pool Manager

Manages HTTP connection pooling for optimized async API client performance.
"""

import aiohttp
import asyncio
import ssl
import time
from typing import Dict, Any, Optional

from ..logging_config import get_logger


class AsyncConnectionPoolManager:
    """Manages HTTP connection pooling for async API clients"""
    
    def __init__(self):
        self.logger = get_logger("core.async_connection_pool")
        self.session = None
        self.session_initialized = False
        self.connection_stats = {
            "active_connections": 0,
            "idle_connections": 0,
            "total_connections": 0,
            "pool_utilization": 0.0,
            "connection_reuse_rate": 0.0,
            "total_requests": 0
        }
    
    async def initialize_session(self, 
                               total_connections: int = 100,
                               connections_per_host: int = 30,
                               keepalive_timeout: int = 30,
                               connect_timeout: int = 10,
                               total_timeout: int = 60) -> None:
        """Initialize optimized HTTP session with connection pooling"""
        if self.session_initialized:
            return
        
        try:
            # Create optimized connector
            connector = aiohttp.TCPConnector(
                limit=total_connections,        # Total connection pool size
                limit_per_host=connections_per_host,  # Connections per host
                ttl_dns_cache=300,  # DNS cache TTL
                use_dns_cache=True,
                keepalive_timeout=keepalive_timeout,
                enable_cleanup_closed=True
            )
            
            # Configure timeouts
            timeout = aiohttp.ClientTimeout(
                total=total_timeout, 
                connect=connect_timeout
            )
            
            # Create session
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
            
            self.session_initialized = True
            self.logger.info(f"HTTP session initialized with {total_connections} total connections, "
                           f"{connections_per_host} per host")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize HTTP session: {e}")
            raise
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get the current session, initializing if needed"""
        if not self.session_initialized:
            await self.initialize_session()
        return self.session
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get detailed connection pool statistics"""
        if not self.session_initialized or not self.session:
            return self.connection_stats
        
        try:
            connector = self.session.connector
            if hasattr(connector, '_connections'):
                # Get actual connection pool statistics
                total_connections = len(connector._connections)
                active_connections = sum(
                    1 for conns in connector._connections.values() 
                    for conn in conns if not conn.is_closing()
                )
                idle_connections = total_connections - active_connections
                
                self.connection_stats.update({
                    "active_connections": active_connections,
                    "idle_connections": idle_connections,
                    "total_connections": total_connections,
                    "pool_utilization": (active_connections / max(100, 1)) * 100,  # Based on limit=100
                    "connection_reuse_rate": (total_connections / max(self.connection_stats["total_requests"], 1)) * 100
                })
        except Exception as e:
            self.logger.error(f"Error getting connection stats: {e}")
        
        return self.connection_stats
    
    def increment_request_count(self):
        """Increment the total request count for statistics"""
        self.connection_stats["total_requests"] += 1
    
    async def optimize_pool(self) -> Dict[str, Any]:
        """Analyze and optimize connection pool based on usage patterns"""
        optimization_results = {
            'optimizations_applied': [],
            'performance_improvements': {},
            'recommendations': []
        }
        
        if not self.session_initialized:
            optimization_results['recommendations'].append(
                'Initialize HTTP session for connection pooling'
            )
            return optimization_results
        
        stats = self.get_connection_stats()
        
        # Analyze pool utilization
        utilization = stats.get('pool_utilization', 0)
        if utilization > 80:
            optimization_results['recommendations'].append(
                'Consider increasing connection pool size (high utilization)'
            )
        elif utilization < 20:
            optimization_results['recommendations'].append(
                'Consider decreasing connection pool size (low utilization)'
            )
        
        # Analyze connection reuse
        reuse_rate = stats.get('connection_reuse_rate', 0)
        if reuse_rate < 50:
            optimization_results['recommendations'].append(
                'Low connection reuse - consider keepalive optimization'
            )
        
        optimization_results['current_stats'] = stats
        return optimization_results
    
    async def health_check(self) -> Dict[str, Any]:
        """Check connection pool health"""
        health_status = {
            "session_initialized": self.session_initialized,
            "session_closed": False,
            "healthy": True,
            "issues": []
        }
        
        if self.session_initialized and self.session:
            health_status["session_closed"] = self.session.closed
            if self.session.closed:
                health_status["healthy"] = False
                health_status["issues"].append("Session is closed")
        elif self.session_initialized:
            health_status["healthy"] = False
            health_status["issues"].append("Session initialized but not available")
        
        health_status["connection_stats"] = self.get_connection_stats()
        return health_status
    
    async def close(self):
        """Close the HTTP session and cleanup resources"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.logger.info("HTTP session closed")
        
        self.session_initialized = False
        self.session = None
