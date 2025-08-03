#!/usr/bin/env python3
"""
Cross-Modal Resilience - Circuit breaker and retry logic for cross-modal conversion

Provides resilience patterns including circuit breaker, retry with exponential backoff,
and error classification for robust cross-modal data conversion.
"""

import asyncio
import time
import random
import logging
from typing import Callable, Any, Dict, Optional
from datetime import datetime, timedelta

from .cross_modal_types import (
    CircuitBreakerState, CircuitBreakerError, RetryConfig,
    ClassifiedError, ErrorClassification, should_retry_error
)

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker pattern for resilient cross-modal operations"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise CircuitBreakerError("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful operation"""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
    
    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN


async def retry_with_backoff(
    func: Callable, 
    *args, 
    retry_config: Optional[RetryConfig] = None, 
    **kwargs
) -> Any:
    """
    Execute function with exponential backoff retry logic
    
    Args:
        func: Function to execute
        retry_config: Retry configuration
        *args, **kwargs: Arguments for the function
        
    Returns:
        Function result
        
    Raises:
        Last exception if all retries fail
    """
    if retry_config is None:
        retry_config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(retry_config.max_attempts):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            # Don't retry on final attempt
            if attempt == retry_config.max_attempts - 1:
                break
                
            # Check if error should be retried
            if not should_retry_error(e):
                logger.warning(f"Non-retryable error: {e}")
                break
            
            # Calculate delay with exponential backoff
            delay = min(
                retry_config.base_delay * (retry_config.exponential_base ** attempt),
                retry_config.max_delay
            )
            
            # Add jitter to prevent thundering herd
            if retry_config.jitter:
                delay *= (0.5 + random.random() * 0.5)
            
            logger.info(f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s: {e}")
            await asyncio.sleep(delay)
    
    raise last_exception


class ErrorClassifier:
    """Classifies errors for appropriate handling"""
    
    def classify_error(self, error: Exception) -> ClassifiedError:
        """
        Classify an error for retry and handling decisions
        
        Args:
            error: Exception to classify
            
        Returns:
            ClassifiedError with appropriate classification
        """
        if isinstance(error, (ConnectionError, TimeoutError, OSError)):
            classification = ErrorClassification.TRANSIENT
        elif isinstance(error, (ValueError, TypeError, KeyError)):
            classification = ErrorClassification.PERMANENT
        else:
            classification = ErrorClassification.UNKNOWN
            
        return ClassifiedError(
            error=error,
            classification=classification,
            timestamp=datetime.now().isoformat()
        )


class ResilienceManager:
    """Manages resilience patterns for cross-modal operations"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.error_classifier = ErrorClassifier()
        
    def get_circuit_breaker(self, operation_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for operation"""
        if operation_name not in self.circuit_breakers:
            self.circuit_breakers[operation_name] = CircuitBreaker()
        return self.circuit_breakers[operation_name]
    
    async def execute_with_resilience(
        self,
        func: Callable,
        operation_name: str,
        retry_config: Optional[RetryConfig] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with full resilience patterns
        
        Args:
            func: Function to execute
            operation_name: Name for circuit breaker tracking
            retry_config: Retry configuration
            *args, **kwargs: Function arguments
            
        Returns:
            Function result
        """
        circuit_breaker = self.get_circuit_breaker(operation_name)
        
        async def resilient_func():
            return circuit_breaker.call(func, *args, **kwargs)
        
        return await retry_with_backoff(
            resilient_func,
            retry_config=retry_config
        )