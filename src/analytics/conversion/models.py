#!/usr/bin/env python3
"""
Data models and exceptions for cross-modal conversion.

Contains all data classes, enums, and exceptions used throughout the
cross-modal conversion system.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime


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
    data_size_before: int
    data_size_after: int
    semantic_features_preserved: List[str]
    quality_metrics: Dict[str, float]
    conversion_parameters: Dict[str, Any]


@dataclass
class ConversionResult:
    """Result of a cross-modal conversion operation"""
    data: Any
    source_format: DataFormat
    target_format: DataFormat
    preservation_score: float
    conversion_metadata: ConversionMetadata
    validation_passed: bool
    semantic_integrity: bool
    warnings: List[str]


@dataclass
class ValidationResult:
    """Result of conversion validation"""
    valid: bool
    preservation_score: float
    semantic_match: bool
    integrity_score: float
    details: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


class ConversionError(Exception):
    """Exception raised when conversion fails"""
    pass


class ConversionIntegrityError(ConversionError):
    """Exception raised when conversion integrity check fails"""
    pass


class ErrorClassification(Enum):
    """Classification of errors for recovery strategies"""
    TRANSIENT = "transient"          # Network, timeout - retry possible
    STRUCTURAL = "structural"        # Invalid data format - fix input
    RESOURCE = "resource"            # Memory, disk space - cleanup needed
    CONFIGURATION = "configuration"  # Missing service, auth - admin action
    LOGIC = "logic"                  # Programming error - bug fix needed


@dataclass
class ClassifiedError:
    """Error with classification and recovery information"""
    original_error: Exception
    classification: ErrorClassification
    recovery_strategy: str
    retry_recommended: bool
    user_actionable: bool
    suggested_actions: List[str]


class CircuitBreakerError(ConversionError):
    """Exception raised when circuit breaker is open"""
    pass


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Service failing, blocking calls
    HALF_OPEN = "half_open"  # Testing if service recovered


def should_retry_error(error: Exception) -> bool:
    """Simple retry logic for transient errors"""
    return isinstance(error, (ConnectionError, TimeoutError))