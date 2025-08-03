#!/usr/bin/env python3
"""
Reliability components for cross-modal conversion.

Provides circuit breaker pattern and retry logic with exponential backoff
for resilient handling of external service dependencies.
"""

import anyio
import time
import logging
from datetime import datetime
from typing import Any, Callable

from .models import CircuitBreakerError, CircuitBreakerState

logger = logging.getLogger("analytics.conversion.reliability")


class CircuitBreaker:
    """Circuit breaker for external service calls"""
    
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.recovery_timeout = recovery_timeout
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self._lock = anyio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        async with self._lock:
            await self._check_state()
            
            if self.state == CircuitBreakerState.OPEN:
                raise CircuitBreakerError("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise
    
    async def _check_state(self):
        """Check and update circuit breaker state"""
        now = datetime.now()
        
        if self.state == CircuitBreakerState.OPEN:
            if self.last_failure_time and (now - self.last_failure_time).total_seconds() > self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker transitioning to HALF_OPEN state")
        
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Stay in half-open, will transition based on next call result
            pass
    
    async def _on_success(self):
        """Handle successful call"""
        async with self._lock:
            self.failure_count = 0
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                logger.info("Circuit breaker transitioned to CLOSED state")
    
    async def _on_failure(self):
        """Handle failed call"""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if (self.state == CircuitBreakerState.CLOSED and 
                self.failure_count >= self.failure_threshold):
                self.state = CircuitBreakerState.OPEN
                logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
            
            elif self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
                logger.warning("Circuit breaker reopened during half-open test")
    
    def get_state(self) -> dict[str, Any]:
        """Get current circuit breaker state"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout
        }


class RetryConfig:
    """Configuration for retry logic"""
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 60.0, backoff_factor: float = 2.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor


async def retry_with_backoff(func: Callable, *args, retry_config: RetryConfig = None, **kwargs) -> Any:
    """Execute function with exponential backoff retry logic"""
    if retry_config is None:
        retry_config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(retry_config.max_attempts):
        try:
            return await func(*args, **kwargs)
        except (ConnectionError, TimeoutError) as e:
            last_exception = e
            if attempt == retry_config.max_attempts - 1:
                raise
            
            # Calculate delay with exponential backoff
            delay = min(
                retry_config.base_delay * (retry_config.backoff_factor ** attempt),
                retry_config.max_delay
            )
            
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s")
            await anyio.sleep(delay)
        
        except Exception as e:
            # Non-retryable errors
            raise
    
    # This should never be reached, but just in case
    raise last_exception