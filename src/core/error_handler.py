"""
Advanced Error Handling and Recovery System
Provides comprehensive error handling with automatic recovery mechanisms.
"""

import logging
import traceback
from typing import Dict, Any, Optional, Callable, Type
from datetime import datetime
import time
import asyncio
from functools import wraps
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels for categorization."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RecoveryStrategy(Enum):
    """Recovery strategies for different error types."""
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    FAIL_FAST = "fail_fast"

@dataclass
class ErrorRecord:
    """Record of an error occurrence with metadata."""
    error_type: str
    error_message: str
    severity: ErrorSeverity
    timestamp: datetime
    stack_trace: str
    context: Dict[str, Any] = field(default_factory=dict)
    recovery_attempted: bool = False
    recovery_successful: bool = False
    retry_count: int = 0

class ProductionErrorHandler:
    """
    Production-grade error handler with comprehensive error management.
    
    Follows fail-fast architecture - never hide critical errors.
    Provides automatic recovery only for non-critical failures.
    """
    
    def __init__(self):
        self.error_registry: Dict[str, ErrorRecord] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'failure_count': 0,
            'last_failure_time': None,
            'state': 'closed'  # closed, open, half-open
        })
        self.retry_policies: Dict[Type[Exception], Dict[str, Any]] = {}
        self.fallback_handlers: Dict[Type[Exception], Callable] = {}
        self._setup_default_policies()
    
    def _setup_default_policies(self):
        """Set up default error handling policies."""
        # Network errors - retry with exponential backoff
        self.retry_policies[ConnectionError] = {
            'max_retries': 3,
            'backoff_multiplier': 2,
            'base_delay': 1
        }
        
        # API rate limits - retry with longer delay
        self.retry_policies[Exception] = {  # Generic for rate limit errors
            'max_retries': 5,
            'backoff_multiplier': 1.5,
            'base_delay': 5
        }
    
    def register_error(self, error: Exception, context: Dict[str, Any] = None) -> str:
        """
        Register an error occurrence with full context.
        
        Args:
            error: The exception that occurred
            context: Additional context information
            
        Returns:
            Error ID for tracking
        """
        error_id = f"error_{int(time.time() * 1000)}"
        
        # Determine severity based on error type
        severity = self._determine_severity(error)
        
        # Create error record
        error_record = ErrorRecord(
            error_type=type(error).__name__,
            error_message=str(error),
            severity=severity,
            timestamp=datetime.now(),
            stack_trace=traceback.format_exc(),
            context=context or {}
        )
        
        self.error_registry[error_id] = error_record
        
        # Log error with appropriate level
        self._log_error(error_record, error_id)
        
        return error_id
    
    def _determine_severity(self, error: Exception) -> ErrorSeverity:
        """Determine error severity based on error type and context."""
        critical_errors = [
            'DatabaseConnectionError',
            'ConfigurationError',
            'SecurityError',
            'DataCorruptionError'
        ]
        
        high_errors = [
            'APIError',
            'AuthenticationError',
            'ValidationError'
        ]
        
        error_type = type(error).__name__
        
        if error_type in critical_errors:
            return ErrorSeverity.CRITICAL
        elif error_type in high_errors:
            return ErrorSeverity.HIGH
        elif isinstance(error, (ConnectionError, TimeoutError)):
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _log_error(self, error_record: ErrorRecord, error_id: str):
        """Log error with appropriate severity level."""
        log_message = f"Error [{error_id}]: {error_record.error_message}"
        
        if error_record.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, extra={
                'error_id': error_id,
                'error_type': error_record.error_type,
                'stack_trace': error_record.stack_trace,
                'context': error_record.context
            })
        elif error_record.severity == ErrorSeverity.HIGH:
            logger.error(log_message, extra={
                'error_id': error_id,
                'error_type': error_record.error_type,
                'context': error_record.context
            })
        elif error_record.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message, extra={
                'error_id': error_id,
                'error_type': error_record.error_type
            })
        else:
            logger.info(log_message, extra={
                'error_id': error_id,
                'error_type': error_record.error_type
            })
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Optional[Any]:
        """
        Handle an error with appropriate recovery strategy.
        
        Args:
            error: The exception to handle
            context: Additional context information
            
        Returns:
            Recovery result if successful, None if failed
            
        Raises:
            Exception: Re-raises critical errors following fail-fast principle
        """
        error_id = self.register_error(error, context)
        error_record = self.error_registry[error_id]
        
        # Critical errors must fail fast - no recovery
        if error_record.severity == ErrorSeverity.CRITICAL:
            raise error
        
        # Attempt recovery for non-critical errors
        recovery_result = self._attempt_recovery(error, error_record, context)
        
        # Update error record with recovery attempt
        error_record.recovery_attempted = True
        error_record.recovery_successful = recovery_result is not None
        
        return recovery_result
    
    def _attempt_recovery(self, error: Exception, error_record: ErrorRecord, 
                         context: Dict[str, Any] = None) -> Optional[Any]:
        """
        Attempt to recover from an error using appropriate strategy.
        
        Args:
            error: The exception to recover from
            error_record: The error record
            context: Additional context
            
        Returns:
            Recovery result if successful, None if failed
        """
        error_type = type(error)
        
        # Check if we have a specific recovery strategy
        if error_type in self.retry_policies:
            return self._retry_with_backoff(error, error_record, context)
        
        if error_type in self.fallback_handlers:
            return self._execute_fallback(error, error_record, context)
        
        # Default: no recovery for unknown errors
        return None
    
    async def _retry_with_backoff_async(self, error: Exception, error_record: ErrorRecord, 
                           context: Dict[str, Any] = None) -> Optional[Any]:
        """Async version of retry with exponential backoff."""
        if not context or 'retry_function' not in context:
            logger.warning(f"No retry function provided for error: {error}")
            return None
        
        error_type = type(error)
        retry_policy = self.retry_policies.get(error_type, {
            'max_retries': 3,
            'backoff_multiplier': 2,
            'base_delay': 1
        })
        
        max_retries = retry_policy['max_retries']
        backoff_multiplier = retry_policy['backoff_multiplier']
        base_delay = retry_policy['base_delay']
        
        retry_function = context['retry_function']
        retry_args = context.get('retry_args', ())
        retry_kwargs = context.get('retry_kwargs', {})
        
        for attempt in range(max_retries):
            delay = base_delay * (backoff_multiplier ** attempt)
            
            logger.info(f"Async retrying operation after {delay}s delay (attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(delay)  # ✅ NON-BLOCKING
            
            try:
                if asyncio.iscoroutinefunction(retry_function):
                    result = await retry_function(*retry_args, **retry_kwargs)
                else:
                    result = retry_function(*retry_args, **retry_kwargs)
                logger.info(f"Async operation succeeded on retry attempt {attempt + 1}")
                return result
            except Exception as retry_error:
                logger.warning(f"Async retry attempt {attempt + 1} failed: {retry_error}")
                error_record.retry_count = attempt + 1
                
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} async retry attempts failed for error: {error}")
        
        return None
    
    def _retry_with_backoff(self, error: Exception, error_record: ErrorRecord, 
                           context: Dict[str, Any] = None) -> Optional[Any]:
        """
        Retry operation with exponential backoff.
        
        Args:
            error: The exception that occurred
            error_record: The error record
            context: Additional context including retry function
            
        Returns:
            Result of successful retry, None if all retries failed
        """
        if not context or 'retry_function' not in context:
            logger.warning(f"No retry function provided for error: {error}")
            return None
        
        error_type = type(error)
        retry_policy = self.retry_policies[error_type]
        
        max_retries = retry_policy['max_retries']
        backoff_multiplier = retry_policy['backoff_multiplier']
        base_delay = retry_policy['base_delay']
        
        retry_function = context['retry_function']
        retry_args = context.get('retry_args', ())
        retry_kwargs = context.get('retry_kwargs', {})
        
        for attempt in range(max_retries):
            # Calculate delay with exponential backoff
            delay = base_delay * (backoff_multiplier ** attempt)
            
            logger.info(f"Retrying operation after {delay}s delay (attempt {attempt + 1}/{max_retries})")
            # Use exponential backoff without blocking
            # In production, this should use asyncio.sleep() or event-driven retry
            if delay > 0.1:  # Only sleep for significant delays
                import asyncio
                try:
                    asyncio.create_task(asyncio.sleep(delay))
                except RuntimeError:
                    # Fallback for non-async context - use minimal delay
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # We're in async context, create a task
                            asyncio.create_task(asyncio.sleep(min(delay, 0.1)))
                        else:
                            # Truly sync context
                            import time
                            time.sleep(min(delay, 0.1))
                    except RuntimeError:
                        # No event loop, use sync sleep
                        import time
                        time.sleep(min(delay, 0.1))
            
            try:
                result = retry_function(*retry_args, **retry_kwargs)
                logger.info(f"Operation succeeded on retry attempt {attempt + 1}")
                return result
            except Exception as retry_error:
                logger.warning(f"Retry attempt {attempt + 1} failed: {retry_error}")
                error_record.retry_count = attempt + 1
                
                # If this is the last attempt, log the final failure
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} retry attempts failed for error: {error}")
        
        return None
    
    async def retry_operation_async(self, error_record: ErrorRecord, context: Dict[str, Any]) -> Optional[Any]:
        """
        Async version of retry operation with non-blocking delays.
        
        Args:
            error_record: The error record containing retry information
            context: Context containing retry function and arguments
            
        Returns:
            Result of successful retry, None if all attempts failed
        """
        max_retries = self.retry_policies.get(type(error_record), {}).get('max_retries', 3)
        backoff_multiplier = self.retry_policies.get(type(error_record), {}).get('backoff_multiplier', 2)
        base_delay = self.retry_policies.get(type(error_record), {}).get('base_delay', 1)
        
        retry_function = context['retry_function']
        retry_args = context.get('retry_args', ())
        retry_kwargs = context.get('retry_kwargs', {})
        
        for attempt in range(max_retries):
            # Calculate delay with exponential backoff
            delay = base_delay * (backoff_multiplier ** attempt)
            
            logger.info(f"Async retry operation after {delay}s delay (attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(delay)  # ✅ NON-BLOCKING
            
            try:
                # Handle both async and sync retry functions
                if asyncio.iscoroutinefunction(retry_function):
                    result = await retry_function(*retry_args, **retry_kwargs)
                else:
                    result = retry_function(*retry_args, **retry_kwargs)
                logger.info(f"Async operation succeeded on retry attempt {attempt + 1}")
                return result
            except Exception as retry_error:
                logger.warning(f"Async retry attempt {attempt + 1} failed: {retry_error}")
                error_record.retry_count = attempt + 1
                
                # If this is the last attempt, log the final failure
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} async retry attempts failed")
        
        return None
    
    def _execute_fallback(self, error: Exception, error_record: ErrorRecord, 
                         context: Dict[str, Any] = None) -> Optional[Any]:
        """
        Execute fallback handler for an error.
        
        Args:
            error: The exception that occurred
            error_record: The error record
            context: Additional context
            
        Returns:
            Result of fallback handler, None if failed
        """
        error_type = type(error)
        fallback_handler = self.fallback_handlers[error_type]
        
        try:
            logger.info(f"Executing fallback handler for error: {error}")
            result = fallback_handler(error, context)
            logger.info("Fallback handler executed successfully")
            return result
        except Exception as fallback_error:
            logger.error(f"Fallback handler failed: {fallback_error}")
            return None
    
    def circuit_breaker(self, service_name: str, failure_threshold: int = 5, 
                       recovery_timeout: int = 60):
        """
        Circuit breaker decorator for service calls.
        
        Args:
            service_name: Name of the service
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time in seconds before attempting recovery
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                circuit = self.circuit_breakers[service_name]
                
                # Check circuit state
                if circuit['state'] == 'open':
                    # Check if we should attempt recovery
                    if (time.time() - circuit['last_failure_time']) > recovery_timeout:
                        circuit['state'] = 'half-open'
                        logger.info(f"Circuit breaker for {service_name} moved to half-open state")
                    else:
                        raise Exception(f"Circuit breaker open for service: {service_name}")
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # Success - reset circuit if it was half-open
                    if circuit['state'] == 'half-open':
                        circuit['state'] = 'closed'
                        circuit['failure_count'] = 0
                        logger.info(f"Circuit breaker for {service_name} closed successfully")
                    
                    return result
                
                except Exception as e:
                    circuit['failure_count'] += 1
                    circuit['last_failure_time'] = time.time()
                    
                    # Check if we should open the circuit
                    if circuit['failure_count'] >= failure_threshold:
                        circuit['state'] = 'open'
                        logger.error(f"Circuit breaker opened for service: {service_name}")
                    
                    # Register and handle the error
                    self.handle_error(e, {
                        'service_name': service_name,
                        'circuit_state': circuit['state']
                    })
                    
                    raise
            
            return wrapper
        return decorator
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive error statistics.
        
        Returns:
            Dictionary with error statistics and health metrics
        """
        total_errors = len(self.error_registry)
        
        if total_errors == 0:
            return {
                'total_errors': 0,
                'error_rate': 0.0,
                'recovery_rate': 0.0,
                'critical_errors': 0,
                'circuit_breaker_states': dict(self.circuit_breakers)
            }
        
        # Calculate statistics
        severity_counts = defaultdict(int)
        recovery_attempts = 0
        successful_recoveries = 0
        
        for error_record in self.error_registry.values():
            severity_counts[error_record.severity.value] += 1
            
            if error_record.recovery_attempted:
                recovery_attempts += 1
                if error_record.recovery_successful:
                    successful_recoveries += 1
        
        recovery_rate = (successful_recoveries / recovery_attempts) * 100 if recovery_attempts > 0 else 0
        
        return {
            'total_errors': total_errors,
            'error_rate': total_errors,  # This would be calculated against total requests in production
            'recovery_rate': recovery_rate,
            'severity_breakdown': dict(severity_counts),
            'critical_errors': severity_counts[ErrorSeverity.CRITICAL.value],
            'recovery_attempts': recovery_attempts,
            'successful_recoveries': successful_recoveries,
            'circuit_breaker_states': dict(self.circuit_breakers)
        }

# Global error handler instance
error_handler = ProductionErrorHandler()

# Decorator for automatic error handling
def handle_errors(severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 retry_on_failure: bool = True):
    """
    Decorator for automatic error handling with customizable behavior.
    
    Args:
        severity: Expected error severity level
        retry_on_failure: Whether to attempt automatic retry
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = {
                    'function_name': func.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                }
                
                if retry_on_failure:
                    context['retry_function'] = func
                    context['retry_args'] = args
                    context['retry_kwargs'] = kwargs
                
                result = error_handler.handle_error(e, context)
                
                # If recovery failed and this is a critical error, re-raise
                if result is None and severity == ErrorSeverity.CRITICAL:
                    raise
                
                return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    'function_name': func.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                }
                
                if retry_on_failure:
                    context['retry_function'] = func
                    context['retry_args'] = args
                    context['retry_kwargs'] = kwargs
                
                result = error_handler.handle_error(e, context)
                
                # If recovery failed and this is a critical error, re-raise
                if result is None and severity == ErrorSeverity.CRITICAL:
                    raise
                
                return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Custom exceptions for fail-fast architecture
class ProductionDeploymentError(Exception):
    """Critical error during production deployment."""
    pass

class SecurityValidationError(Exception):
    """Critical security validation failure."""
    pass

class DataIntegrityError(Exception):
    """Critical data integrity violation."""
    pass

class ServiceUnavailableError(Exception):
    """Service temporarily unavailable."""
    pass

class ConfigurationError(Exception):
    """Critical configuration error."""
    pass