"""
Async API Clients Module

Decomposed async API client components for performance optimization.
Provides OpenAI, Gemini, and enhanced multi-service async clients.
"""

# Import core request/response types
from .request_types import (
    AsyncAPIRequestType,
    AsyncAPIRequest,
    AsyncAPIResponse
)

# Import individual clients
from .openai_client import AsyncOpenAIClient
from .gemini_client import AsyncGeminiClient
from .enhanced_client import AsyncEnhancedAPIClient

# Import utilities
from .performance_monitor import AsyncClientPerformanceMonitor
from .connection_pool import AsyncConnectionPoolManager

# Import global client functions
from .client_factory import (
    get_async_api_client,
    close_async_api_client
)

__all__ = [
    # Request/Response types
    "AsyncAPIRequestType",
    "AsyncAPIRequest", 
    "AsyncAPIResponse",
    
    # Individual clients
    "AsyncOpenAIClient",
    "AsyncGeminiClient",
    "AsyncEnhancedAPIClient",
    
    # Utilities
    "AsyncClientPerformanceMonitor",
    "AsyncConnectionPoolManager",
    
    # Factory functions
    "get_async_api_client",
    "close_async_api_client"
]
