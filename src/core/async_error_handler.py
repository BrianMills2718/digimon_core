"""
Async-safe Error Handler for GraphRAG System.

Provides comprehensive error handling with retry logic that doesn't block
the event loop.
"""

import asyncio
import functools
from typing import Type, Tuple, Optional, Callable, Any, Union
from datetime import datetime
import logging
import traceback

logger = logging.getLogger(__name__)


class AsyncErrorHandler:
    """
    Asynchronous error handler with retry logic.
    
    Features:
    - Non-blocking retry delays
    - Exponential backoff
    - Configurable retry strategies
    - Detailed error tracking
    """
    
    def __init__(self):
        """Initialize the error handler."""
        self.error_counts = {}
        self.last_errors = {}
        self.retry_strategies = {
            ConnectionError: (3, 1.0),  # 3 retries, 1 second initial delay
            TimeoutError: (2, 0.5),     # 2 retries, 0.5 second initial delay
            asyncio.TimeoutError: (2, 0.5),
            Exception: (1, 0.1)         # 1 retry, 0.1 second delay for others
        }
    
    def set_retry_strategy(self, error_type: Type[Exception], 
                          max_attempts: int, initial_delay: float) -> None:
        """
        Set retry strategy for a specific error type.
        
        Args:
            error_type: Type of exception
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay between retries (seconds)
        """
        self.retry_strategies[error_type] = (max_attempts, initial_delay)
        logger.info(f"Set retry strategy for {error_type.__name__}: "
                   f"{max_attempts} attempts, {initial_delay}s initial delay")
    
    async def handle_error(self, error: Exception, context: Optional[dict] = None) -> dict:
        """
        Handle an error with logging and tracking.
        
        Args:
            error: The exception that occurred
            context: Optional context information
            
        Returns:
            Error information dictionary
        """
        error_type = type(error).__name__
        error_key = f"{error_type}_{str(error)}"
        
        # Track error count
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        self.last_errors[error_type] = {
            'error': str(error),
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'traceback': traceback.format_exc()
        }
        
        logger.error(f"Error handled: {error_type}: {error}", 
                    extra={'context': context}, exc_info=True)
        
        return {
            'error_type': error_type,
            'error_message': str(error),
            'count': self.error_counts[error_key],
            'context': context
        }
    
    def with_retry(self, max_attempts: Optional[int] = None, 
                   delay: Optional[float] = None,
                   backoff_factor: float = 2.0,
                   exceptions: Tuple[Type[Exception], ...] = (Exception,)):
        """
        Decorator for adding retry logic to async functions.
        
        Args:
            max_attempts: Maximum number of attempts (overrides strategy)
            delay: Initial delay between retries (overrides strategy)
            backoff_factor: Factor to multiply delay by after each attempt
            exceptions: Tuple of exceptions to catch and retry
            
        Returns:
            Decorated function with retry logic
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                last_exception = None
                
                # Determine retry parameters
                retry_attempts = max_attempts
                retry_delay = delay
                
                if retry_attempts is None or retry_delay is None:
                    # Find the best matching strategy
                    for exc_type in exceptions:
                        if exc_type in self.retry_strategies:
                            strategy_attempts, strategy_delay = self.retry_strategies[exc_type]
                            if retry_attempts is None:
                                retry_attempts = strategy_attempts
                            if retry_delay is None:
                                retry_delay = strategy_delay
                            break
                    else:
                        # Use default if no specific strategy found
                        if retry_attempts is None:
                            retry_attempts = 1
                        if retry_delay is None:
                            retry_delay = 0.1
                
                current_delay = retry_delay
                
                for attempt in range(retry_attempts + 1):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt < retry_attempts:
                            logger.warning(
                                f"Attempt {attempt + 1}/{retry_attempts + 1} failed for "
                                f"{func.__name__}: {type(e).__name__}: {e}. "
                                f"Retrying in {current_delay}s..."
                            )
                            
                            # Use asyncio.sleep for non-blocking delay
                            await asyncio.sleep(current_delay)
                            current_delay *= backoff_factor
                        else:
                            # Final attempt failed
                            await self.handle_error(e, {
                                'function': func.__name__,
                                'args': args,
                                'kwargs': kwargs,
                                'attempts': retry_attempts + 1
                            })
                
                # All attempts failed, re-raise the last exception
                raise last_exception
            
            return wrapper
        return decorator
    
    async def with_timeout(self, coro: Callable, timeout: float, 
                          error_message: Optional[str] = None) -> Any:
        """
        Execute a coroutine with a timeout.
        
        Args:
            coro: Coroutine to execute
            timeout: Timeout in seconds
            error_message: Optional custom error message
            
        Returns:
            Result of the coroutine
            
        Raises:
            asyncio.TimeoutError: If timeout is exceeded
        """
        try:
            return await asyncio.wait_for(coro, timeout)
        except asyncio.TimeoutError:
            msg = error_message or f"Operation timed out after {timeout}s"
            await self.handle_error(asyncio.TimeoutError(msg))
            raise
    
    def get_error_statistics(self) -> dict:
        """
        Get error statistics.
        
        Returns:
            Dictionary with error counts and recent errors
        """
        return {
            'error_counts': dict(self.error_counts),
            'recent_errors': dict(self.last_errors),
            'total_errors': sum(self.error_counts.values())
        }
    
    def reset_statistics(self) -> None:
        """Reset error statistics."""
        self.error_counts.clear()
        self.last_errors.clear()
        logger.info("Error statistics reset")


# Singleton instance
_error_handler = AsyncErrorHandler()


def get_error_handler() -> AsyncErrorHandler:
    """Get the singleton error handler instance."""
    return _error_handler


# Convenience decorators
def with_retry(*args, **kwargs):
    """Convenience decorator using the singleton error handler."""
    return _error_handler.with_retry(*args, **kwargs)


async def handle_error(error: Exception, context: Optional[dict] = None) -> dict:
    """Convenience function using the singleton error handler."""
    return await _error_handler.handle_error(error, context)