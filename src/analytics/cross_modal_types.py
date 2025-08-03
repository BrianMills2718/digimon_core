#!/usr/bin/env python3
"""
Cross-Modal Types - Common types and exceptions for cross-modal conversion

Contains all shared data types, enums, and exception classes used across
the cross-modal conversion system.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class DataFormat(Enum):
    """Supported data formats for cross-modal conversion"""
    GRAPH = "graph"
    TABLE = "table"
    VECTOR = "vector"
    MULTIMODAL = "multimodal"


@dataclass
class ConversionMetadata:
    """Metadata about a conversion operation"""
    source_format: DataFormat
    target_format: DataFormat
    conversion_timestamp: str
    processing_time: float
    node_count: Optional[int] = None
    edge_count: Optional[int] = None
    record_count: Optional[int] = None
    vector_dimension: Optional[int] = None


@dataclass
class ConversionResult:
    """Result of a cross-modal conversion operation"""
    data: Any
    metadata: ConversionMetadata
    validation_result: Optional['ValidationResult'] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class ValidationResult:
    """Result of validating a conversion"""
    is_valid: bool
    semantic_preservation_score: float
    structural_integrity_score: float
    issues: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []


class ConversionError(Exception):
    """Base exception for conversion errors"""
    pass


class ConversionIntegrityError(ConversionError):
    """Exception raised when data integrity is compromised during conversion"""
    pass


class ErrorClassification(Enum):
    """Classification of conversion errors for retry logic"""
    TRANSIENT = "transient"  # Network, temporary resource issues
    PERMANENT = "permanent"  # Data format issues, validation failures
    UNKNOWN = "unknown"      # Unclassified errors


@dataclass
class ClassifiedError:
    """Error with classification for retry decisions"""
    error: Exception
    classification: ErrorClassification
    retry_count: int = 0
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


def should_retry_error(error: Exception) -> bool:
    """Determine if an error should be retried based on its type"""
    retry_error_types = (ConnectionError, TimeoutError, OSError)
    permanent_error_types = (ValueError, TypeError, ConversionIntegrityError)
    
    return isinstance(error, retry_error_types) and not isinstance(error, permanent_error_types)


class CircuitBreakerError(ConversionError):
    """Exception raised when circuit breaker is open"""
    pass


class CircuitBreakerState(Enum):
    """States of the circuit breaker"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class RetryConfig:
    """Configuration for retry logic"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True