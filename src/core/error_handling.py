"""Centralized Error Handling Framework for KGAS

This module provides a comprehensive error handling system that ensures
consistent error management, logging, and recovery across all components.

Key features:
- Hierarchical error classification
- Automatic error context capture
- Error recovery strategies
- Centralized error logging
- Error metrics and monitoring
"""

import logging
import traceback
import sys
from typing import Dict, Any, Optional, List, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
from contextlib import contextmanager


logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    DEBUG = "debug"      # Development-time errors
    INFO = "info"        # Informational, not really errors
    WARNING = "warning"  # Recoverable issues
    ERROR = "error"      # Errors that need attention
    CRITICAL = "critical"  # System-threatening errors
    FATAL = "fatal"      # Unrecoverable errors


class ErrorCategory(Enum):
    """Error categories for classification"""
    # System errors
    SYSTEM_RESOURCE = "system_resource"
    SYSTEM_CONFIG = "system_config"
    SYSTEM_DEPENDENCY = "system_dependency"
    
    # Data errors
    DATA_VALIDATION = "data_validation"
    DATA_INTEGRITY = "data_integrity"
    DATA_NOT_FOUND = "data_not_found"
    
    # Service errors
    SERVICE_UNAVAILABLE = "service_unavailable"
    SERVICE_TIMEOUT = "service_timeout"
    SERVICE_RATE_LIMIT = "service_rate_limit"
    
    # Tool errors
    TOOL_EXECUTION = "tool_execution"
    TOOL_VALIDATION = "tool_validation"
    TOOL_CONTRACT = "tool_contract"
    
    # Storage errors
    STORAGE_CONNECTION = "storage_connection"
    STORAGE_CAPACITY = "storage_capacity"
    STORAGE_PERMISSION = "storage_permission"
    
    # Security errors
    SECURITY_AUTH = "security_auth"
    SECURITY_PERMISSION = "security_permission"
    SECURITY_VIOLATION = "security_violation"
    
    # Unknown
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Context information for an error"""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    component: Optional[str] = None
    operation: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    tool_id: Optional[str] = None
    service_id: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KGASError(Exception):
    """Base error class for all KGAS errors
    
    Provides rich error information including:
    - Error code and message
    - Severity and category
    - Context information
    - Recovery suggestions
    - Cause chain
    """
    code: str
    message: str
    severity: ErrorSeverity = ErrorSeverity.ERROR
    category: ErrorCategory = ErrorCategory.UNKNOWN
    context: Optional[ErrorContext] = None
    cause: Optional[Exception] = None
    recovery_suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self):
        return f"[{self.code}] {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization"""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "context": self.context.__dict__ if self.context else None,
            "cause": str(self.cause) if self.cause else None,
            "recovery_suggestions": self.recovery_suggestions,
            "metadata": self.metadata,
            "traceback": self.get_traceback()
        }
    
    def get_traceback(self) -> Optional[str]:
        """Get traceback if available"""
        if self.cause:
            return traceback.format_exception(
                type(self.cause), 
                self.cause, 
                self.cause.__traceback__
            )
        return None


# Specific error types

class ValidationError(KGASError):
    """Data validation errors"""
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            severity=ErrorSeverity.WARNING,
            category=ErrorCategory.DATA_VALIDATION,
            **kwargs
        )
        if field:
            self.metadata["field"] = field


class ResourceError(KGASError):
    """Resource-related errors"""
    def __init__(self, message: str, resource_type: str, **kwargs):
        super().__init__(
            code="RESOURCE_ERROR",
            message=message,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.SYSTEM_RESOURCE,
            **kwargs
        )
        self.metadata["resource_type"] = resource_type


class ServiceError(KGASError):
    """Service-related errors"""
    def __init__(self, message: str, service_id: str, **kwargs):
        super().__init__(
            code="SERVICE_ERROR",
            message=message,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.SERVICE_UNAVAILABLE,
            **kwargs
        )
        if not self.context:
            self.context = ErrorContext()
        self.context.service_id = service_id


class ToolError(KGASError):
    """Tool execution errors"""
    def __init__(self, message: str, tool_id: str, **kwargs):
        super().__init__(
            code="TOOL_ERROR",
            message=message,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.TOOL_EXECUTION,
            **kwargs
        )
        if not self.context:
            self.context = ErrorContext()
        self.context.tool_id = tool_id


class StorageError(KGASError):
    """Storage-related errors"""
    def __init__(self, message: str, storage_type: str, **kwargs):
        super().__init__(
            code="STORAGE_ERROR",
            message=message,
            severity=ErrorSeverity.ERROR,
            category=ErrorCategory.STORAGE_CONNECTION,
            **kwargs
        )
        self.metadata["storage_type"] = storage_type


class SecurityError(KGASError):
    """Security-related errors"""
    def __init__(self, message: str, violation_type: str, **kwargs):
        super().__init__(
            code="SECURITY_ERROR",
            message=message,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SECURITY_VIOLATION,
            **kwargs
        )
        self.metadata["violation_type"] = violation_type


# Error handler registry

class ErrorHandler:
    """Centralized error handler with recovery strategies"""
    
    def __init__(self):
        self.handlers: Dict[Type[Exception], List[Callable]] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        self.error_metrics: Dict[str, int] = {}
        self.error_log: List[KGASError] = []
        self.max_log_size = 1000
    
    def register_handler(
        self, 
        error_type: Type[Exception], 
        handler: Callable[[Exception], Optional[Any]]
    ):
        """Register an error handler for a specific error type
        
        Args:
            error_type: Type of error to handle
            handler: Function to handle the error
        """
        if error_type not in self.handlers:
            self.handlers[error_type] = []
        self.handlers[error_type].append(handler)
    
    def register_recovery_strategy(
        self,
        strategy_name: str,
        strategy_func: Callable[[KGASError], bool]
    ):
        """Register a recovery strategy
        
        Args:
            strategy_name: Name of the recovery strategy
            strategy_func: Function that attempts recovery, returns True if successful
        """
        self.recovery_strategies[strategy_name] = strategy_func
    
    def handle_error(self, error: Exception, context: Optional[ErrorContext] = None) -> KGASError:
        """Handle an error with appropriate handlers
        
        Args:
            error: The error to handle
            context: Optional error context
            
        Returns:
            KGASError with full context
        """
        # Convert to KGASError if needed
        if isinstance(error, KGASError):
            kgas_error = error
            if context and not kgas_error.context:
                kgas_error.context = context
        else:
            kgas_error = self._convert_to_kgas_error(error, context)
        
        # Update metrics
        self._update_metrics(kgas_error)
        
        # Log error
        self._log_error(kgas_error)
        
        # Run registered handlers
        error_type = type(error)
        for handler_type, handlers in self.handlers.items():
            if issubclass(error_type, handler_type):
                for handler in handlers:
                    try:
                        result = handler(error)
                        if result is not None:
                            kgas_error.metadata["handler_result"] = result
                    except Exception as e:
                        logger.error(f"Error handler failed: {e}")
        
        # Attempt recovery if suggestions exist
        if kgas_error.recovery_suggestions:
            self._attempt_recovery(kgas_error)
        
        return kgas_error
    
    def _convert_to_kgas_error(self, error: Exception, context: Optional[ErrorContext]) -> KGASError:
        """Convert standard exception to KGASError"""
        # Map common exceptions
        error_mappings = {
            ValueError: (ErrorCategory.DATA_VALIDATION, ErrorSeverity.WARNING),
            KeyError: (ErrorCategory.DATA_NOT_FOUND, ErrorSeverity.WARNING),
            ConnectionError: (ErrorCategory.STORAGE_CONNECTION, ErrorSeverity.ERROR),
            TimeoutError: (ErrorCategory.SERVICE_TIMEOUT, ErrorSeverity.ERROR),
            PermissionError: (ErrorCategory.SECURITY_PERMISSION, ErrorSeverity.CRITICAL),
            MemoryError: (ErrorCategory.SYSTEM_RESOURCE, ErrorSeverity.CRITICAL),
            RuntimeError: (ErrorCategory.UNKNOWN, ErrorSeverity.ERROR)
        }
        
        category = ErrorCategory.UNKNOWN
        severity = ErrorSeverity.ERROR
        
        for error_type, (cat, sev) in error_mappings.items():
            if isinstance(error, error_type):
                category = cat
                severity = sev
                break
        
        return KGASError(
            code=type(error).__name__.upper(),
            message=str(error),
            severity=severity,
            category=category,
            context=context,
            cause=error
        )
    
    def _update_metrics(self, error: KGASError):
        """Update error metrics"""
        metric_key = f"{error.category.value}:{error.code}"
        self.error_metrics[metric_key] = self.error_metrics.get(metric_key, 0) + 1
        
        # Also track by severity
        severity_key = f"severity:{error.severity.value}"
        self.error_metrics[severity_key] = self.error_metrics.get(severity_key, 0) + 1
    
    def _log_error(self, error: KGASError):
        """Log error to internal log"""
        self.error_log.append(error)
        
        # Maintain log size limit
        if len(self.error_log) > self.max_log_size:
            self.error_log = self.error_log[-self.max_log_size:]
        
        # Log to Python logger
        log_method = getattr(logger, error.severity.value, logger.error)
        log_method(
            f"{error.code}: {error.message}",
            extra={
                "error_data": error.to_dict()
            }
        )
    
    def _attempt_recovery(self, error: KGASError) -> bool:
        """Attempt to recover from error using registered strategies"""
        for suggestion in error.recovery_suggestions:
            if suggestion in self.recovery_strategies:
                try:
                    strategy = self.recovery_strategies[suggestion]
                    if strategy(error):
                        logger.info(f"Recovery successful using strategy: {suggestion}")
                        return True
                except Exception as e:
                    logger.error(f"Recovery strategy {suggestion} failed: {e}")
        return False
    
    def get_error_report(self) -> Dict[str, Any]:
        """Get error statistics report"""
        return {
            "total_errors": sum(self.error_metrics.values()),
            "errors_by_category": {
                k: v for k, v in self.error_metrics.items() 
                if k.startswith(next(iter(ErrorCategory.__members__.values())).value)
            },
            "errors_by_severity": {
                k.replace("severity:", ""): v 
                for k, v in self.error_metrics.items() 
                if k.startswith("severity:")
            },
            "recent_errors": [
                {
                    "code": e.code,
                    "message": e.message,
                    "timestamp": e.context.timestamp if e.context else None
                }
                for e in self.error_log[-10:]
            ]
        }


# Global error handler instance
_error_handler = ErrorHandler()


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance"""
    return _error_handler


# Context managers for error handling

@contextmanager
def error_context(component: str, operation: str, **kwargs):
    """Context manager that captures error context
    
    Usage:
        with error_context("ToolFactory", "create_tool", tool_id="T01"):
            # Code that might raise errors
            pass
    """
    context = ErrorContext(
        component=component,
        operation=operation,
        **kwargs
    )
    
    try:
        yield context
    except Exception as e:
        # Enhance error with context
        error = get_error_handler().handle_error(e, context)
        raise error


@contextmanager
def suppress_errors(*error_types: Type[Exception], default=None, log=True):
    """Context manager that suppresses specific errors
    
    Usage:
        with suppress_errors(ValidationError, default={}):
            # Code that might raise ValidationError
            result = risky_operation()
    """
    try:
        yield
    except error_types as e:
        if log:
            get_error_handler().handle_error(e)
        return default


# Decorators for error handling

def handle_errors(
    error_code: str = "UNKNOWN_ERROR",
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    recovery_suggestions: List[str] = None
):
    """Decorator that adds error handling to functions
    
    Usage:
        @handle_errors(
            error_code="TOOL_EXECUTION_ERROR",
            category=ErrorCategory.TOOL_EXECUTION,
            recovery_suggestions=["retry", "check_input"]
        )
        def execute_tool(tool_id: str):
            # Tool execution code
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KGASError:
                # Re-raise KGAS errors as-is
                raise
            except Exception as e:
                # Convert to KGASError with metadata
                error = KGASError(
                    code=error_code,
                    message=str(e),
                    severity=severity,
                    category=category,
                    cause=e,
                    recovery_suggestions=recovery_suggestions or [],
                    context=ErrorContext(
                        component=func.__module__,
                        operation=func.__name__
                    )
                )
                get_error_handler().handle_error(error)
                raise error
        return wrapper
    return decorator


# Recovery strategies

def register_default_recovery_strategies():
    """Register default recovery strategies"""
    handler = get_error_handler()
    
    # Retry strategy
    def retry_strategy(error: KGASError) -> bool:
        """Simple retry strategy"""
        if "retry_count" not in error.metadata:
            error.metadata["retry_count"] = 0
        
        if error.metadata["retry_count"] < 3:
            error.metadata["retry_count"] += 1
            logger.info(f"Retrying operation (attempt {error.metadata['retry_count']})")
            return True
        return False
    
    handler.register_recovery_strategy("retry", retry_strategy)
    
    # Fallback strategy
    def fallback_strategy(error: KGASError) -> bool:
        """Use fallback service/tool"""
        if "fallback" in error.metadata:
            logger.info(f"Using fallback: {error.metadata['fallback']}")
            return True
        return False
    
    handler.register_recovery_strategy("fallback", fallback_strategy)
    
    # Circuit breaker strategy
    def circuit_breaker_strategy(error: KGASError) -> bool:
        """Circuit breaker pattern"""
        if error.category == ErrorCategory.SERVICE_UNAVAILABLE:
            logger.info("Circuit breaker activated for service")
            # In real implementation, would track service status
            return True
        return False
    
    handler.register_recovery_strategy("circuit_breaker", circuit_breaker_strategy)


# Initialize default strategies
register_default_recovery_strategies()


# Utility functions

def create_error(
    code: str,
    message: str,
    **kwargs
) -> KGASError:
    """Convenience function to create a KGAS error
    
    Args:
        code: Error code
        message: Error message
        **kwargs: Additional error attributes
        
    Returns:
        KGASError instance
    """
    return KGASError(code=code, message=message, **kwargs)


def log_and_raise(
    code: str,
    message: str,
    **kwargs
):
    """Create, log, and raise an error
    
    Args:
        code: Error code
        message: Error message
        **kwargs: Additional error attributes
    """
    error = create_error(code, message, **kwargs)
    get_error_handler().handle_error(error)
    raise error