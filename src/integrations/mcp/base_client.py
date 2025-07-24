"""
Base MCP Client Interface

Provides a unified interface for communicating with Model Context Protocol servers.
This base class handles the common functionality needed by all MCP clients.

Features:
- Async/await patterns for all operations
- Circuit breaker integration for fault tolerance
- Rate limiting to respect server limits
- Comprehensive error handling
- Request/response logging
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, TypeVar, Generic
from dataclasses import dataclass
from datetime import datetime
from contextlib import asynccontextmanager

from ...core.circuit_breaker import CircuitBreaker
from ...core.api_rate_limiter import APIRateLimiter
from ...core.exceptions import ServiceUnavailableError

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class MCPRequest:
    """Standard MCP request structure"""
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP-compliant dictionary"""
        req = {
            "jsonrpc": "2.0",
            "method": self.method,
            "params": self.params
        }
        if self.id:
            req["id"] = self.id
        return req


@dataclass
class MCPResponse(Generic[T]):
    """Standard MCP response structure"""
    success: bool
    data: Optional[T]
    error: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, response_dict: Dict[str, Any]) -> 'MCPResponse':
        """Create MCPResponse from dictionary"""
        if "error" in response_dict:
            return cls(
                success=False,
                data=None,
                error=response_dict["error"],
                metadata=response_dict.get("metadata")
            )
        else:
            return cls(
                success=True,
                data=response_dict.get("result"),
                error=None,
                metadata=response_dict.get("metadata")
            )


class BaseMCPClient(ABC):
    """
    Base class for all MCP client implementations.
    
    Provides common functionality for MCP communication including:
    - Connection management
    - Request/response handling
    - Error handling and retries
    - Rate limiting
    - Circuit breaker protection
    """
    
    def __init__(self, 
                 server_name: str,
                 server_url: str,
                 rate_limiter: APIRateLimiter,
                 circuit_breaker: CircuitBreaker,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize base MCP client.
        
        Args:
            server_name: Name of the MCP server
            server_url: URL of the MCP server
            rate_limiter: Rate limiter instance
            circuit_breaker: Circuit breaker instance
            config: Optional configuration dictionary
        """
        self.server_name = server_name
        self.server_url = server_url
        self.rate_limiter = rate_limiter
        self.circuit_breaker = circuit_breaker
        self.config = config or {}
        self._session = None
        self._connected = False
        
        logger.info(f"Initialized {self.__class__.__name__} for {server_name}")
    
    @abstractmethod
    async def _create_session(self):
        """Create the underlying communication session"""
        pass
    
    @abstractmethod
    async def _close_session(self):
        """Close the underlying communication session"""
        pass
    
    @abstractmethod
    async def _send_request(self, request: MCPRequest) -> Dict[str, Any]:
        """Send request to MCP server and get raw response"""
        pass
    
    @asynccontextmanager
    async def connect(self):
        """Context manager for MCP connection"""
        try:
            await self._create_session()
            self._connected = True
            logger.info(f"Connected to {self.server_name}")
            yield self
        finally:
            await self._close_session()
            self._connected = False
            logger.info(f"Disconnected from {self.server_name}")
    
    async def call_method(self, method: str, params: Dict[str, Any]) -> MCPResponse:
        """
        Call an MCP method with the given parameters.
        
        Args:
            method: MCP method name
            params: Method parameters
            
        Returns:
            MCPResponse containing the result or error
            
        Raises:
            ServiceUnavailableError: If server is unavailable
        """
        if not self._connected:
            raise ServiceUnavailableError(
                self.server_name, 
                "Client not connected. Use async with client.connect():"
            )
        
        # Apply rate limiting
        await self.rate_limiter.acquire(self.server_name)
        
        # Create request
        request = MCPRequest(
            method=method,
            params=params,
            id=f"{method}_{datetime.now().timestamp()}"
        )
        
        # Execute through circuit breaker
        async def make_request():
            try:
                logger.debug(f"Calling {self.server_name}.{method} with params: {params}")
                raw_response = await self._send_request(request)
                
                # Parse response
                response = MCPResponse.from_dict(raw_response)
                
                if not response.success:
                    logger.warning(f"MCP error from {self.server_name}: {response.error}")
                
                return response
                
            except Exception as e:
                logger.error(f"Error calling {self.server_name}.{method}: {e}")
                raise ServiceUnavailableError(self.server_name, str(e))
        
        return await self.circuit_breaker.call(make_request)
    
    async def list_methods(self) -> List[str]:
        """
        List available methods from the MCP server.
        
        Returns:
            List of available method names
        """
        response = await self.call_method("rpc.discover", {})
        if response.success and response.data:
            return response.data.get("methods", [])
        return []
    
    async def get_server_info(self) -> Dict[str, Any]:
        """
        Get information about the MCP server.
        
        Returns:
            Dictionary containing server information
        """
        response = await self.call_method("server.info", {})
        if response.success:
            return response.data or {}
        return {}
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the MCP client.
        
        Returns:
            Dictionary with health information
        """
        return {
            'server_name': self.server_name,
            'server_url': self.server_url,
            'connected': self._connected,
            'circuit_breaker_state': self.circuit_breaker.state.value,
            'rate_limiter_stats': self.rate_limiter.get_service_stats(self.server_name)
        }


class MCPError(Exception):
    """Base exception for MCP-related errors"""
    def __init__(self, server_name: str, message: str, error_data: Optional[Dict[str, Any]] = None):
        self.server_name = server_name
        self.error_data = error_data
        super().__init__(f"MCP Error from {server_name}: {message}")


class MCPMethodNotFoundError(MCPError):
    """Raised when an MCP method is not found"""
    pass


class MCPInvalidParamsError(MCPError):
    """Raised when MCP method parameters are invalid"""
    pass


class MCPInternalError(MCPError):
    """Raised when MCP server has an internal error"""
    pass