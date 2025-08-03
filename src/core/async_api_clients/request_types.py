"""
Async API Request/Response Types

Core data types for async API client requests and responses.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional


class AsyncAPIRequestType(Enum):
    """Types of async API requests"""
    TEXT_GENERATION = "text_generation"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"
    COMPLETION = "completion"
    CHAT = "chat"


@dataclass
class AsyncAPIRequest:
    """Async API request configuration"""
    service_type: str
    request_type: AsyncAPIRequestType
    prompt: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    model: Optional[str] = None
    additional_params: Optional[Dict[str, Any]] = None


@dataclass
class AsyncAPIResponse:
    """Async API response wrapper"""
    success: bool
    service_used: str
    request_type: AsyncAPIRequestType
    response_data: Any
    response_time: float
    tokens_used: Optional[int] = None
    error: Optional[str] = None
    fallback_used: bool = False
