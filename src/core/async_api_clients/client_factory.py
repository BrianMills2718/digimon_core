"""
Async API Client Factory

Factory functions for managing global async API client instances.
"""

import asyncio
from typing import Optional

from .enhanced_client import AsyncEnhancedAPIClient
from ..logging_config import get_logger


# Global async client instance
_async_client: Optional[AsyncEnhancedAPIClient] = None
_client_lock = asyncio.Lock()

logger = get_logger("core.async_client_factory")


async def get_async_api_client() -> AsyncEnhancedAPIClient:
    """Get the global async API client instance"""
    global _async_client
    
    if _async_client is None:
        async with _client_lock:
            if _async_client is None:
                _async_client = AsyncEnhancedAPIClient()
                await _async_client.initialize_clients()
                logger.info("Global async API client initialized")
    
    return _async_client


async def close_async_api_client():
    """Close the global async API client"""
    global _async_client
    
    if _async_client is not None:
        async with _client_lock:
            if _async_client is not None:
                await _async_client.close()
                _async_client = None
                logger.info("Global async API client closed")


def is_client_initialized() -> bool:
    """Check if the global client is initialized"""
    return _async_client is not None


async def reset_async_api_client():
    """Reset the global async API client (close and recreate)"""
    await close_async_api_client()
    return await get_async_api_client()
