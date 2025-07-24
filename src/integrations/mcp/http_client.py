"""
HTTP-based MCP Client Implementation

Implements the MCP client interface for HTTP/HTTPS-based MCP servers.
Most MCP servers use HTTP as the transport layer.

Features:
- HTTP/HTTPS transport with aiohttp
- JSON-RPC 2.0 protocol support
- Connection pooling
- Request timeout handling
- Automatic retries with exponential backoff
"""

import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

from .base_client import BaseMCPClient, MCPRequest, MCPResponse, MCPError
from ...core.exceptions import ServiceUnavailableError
import logging

logger = logging.getLogger(__name__)


class HTTPMCPClient(BaseMCPClient):
    """
    HTTP/HTTPS implementation of MCP client.
    
    Uses aiohttp for async HTTP communication with MCP servers.
    Implements JSON-RPC 2.0 protocol over HTTP.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize HTTP MCP client with additional HTTP-specific config"""
        super().__init__(*args, **kwargs)
        
        # HTTP-specific configuration
        self.timeout = self.config.get('timeout', 30)
        self.max_retries = self.config.get('max_retries', 3)
        self.headers = self.config.get('headers', {})
        self.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    async def _create_session(self):
        """Create aiohttp client session"""
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        
        self._session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=self.headers
        )
        logger.debug(f"Created HTTP session for {self.server_name}")
    
    async def _close_session(self):
        """Close aiohttp client session"""
        if self._session:
            await self._session.close()
            self._session = None
            logger.debug(f"Closed HTTP session for {self.server_name}")
    
    async def _send_request(self, request: MCPRequest) -> Dict[str, Any]:
        """
        Send HTTP request to MCP server.
        
        Args:
            request: MCP request to send
            
        Returns:
            Raw response dictionary
            
        Raises:
            ServiceUnavailableError: If server is unavailable
        """
        if not self._session:
            raise ServiceUnavailableError(self.server_name, "HTTP session not created")
        
        request_data = request.to_dict()
        
        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(self.max_retries):
            try:
                async with self._session.post(
                    self.server_url,
                    json=request_data
                ) as response:
                    # Check HTTP status
                    if response.status == 429:  # Rate limited
                        retry_after = response.headers.get('Retry-After', 60)
                        self.rate_limiter.handle_429_response(
                            self.server_name, 
                            int(retry_after)
                        )
                        raise ServiceUnavailableError(
                            self.server_name,
                            f"Rate limited. Retry after {retry_after}s"
                        )
                    
                    if response.status >= 500:  # Server error
                        raise ServiceUnavailableError(
                            self.server_name,
                            f"Server error: HTTP {response.status}"
                        )
                    
                    if response.status >= 400:  # Client error
                        error_text = await response.text()
                        raise MCPError(
                            self.server_name,
                            f"Client error: HTTP {response.status}",
                            {"status": response.status, "body": error_text}
                        )
                    
                    # Parse JSON response
                    response_data = await response.json()
                    
                    # Update rate limiter from headers
                    self.rate_limiter.update_from_headers(
                        self.server_name,
                        dict(response.headers)
                    )
                    
                    return response_data
                    
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = (2 ** attempt) * 1.0
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{self.max_retries}), "
                        f"retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All retry attempts failed: {e}")
        
        # All retries exhausted
        raise ServiceUnavailableError(
            self.server_name,
            f"Failed after {self.max_retries} attempts: {last_error}"
        )