"""
Production-ready Circuit Breaker Pattern Implementation

Provides resilient external service communication with automatic failure detection,
circuit opening, and recovery mechanisms following the Circuit Breaker pattern.

Features:
- Three states: CLOSED, OPEN, HALF_OPEN
- Configurable failure threshold and recovery timeout
- Operation timeout handling
- Thread-safe concurrent operation
- Comprehensive metrics collection
- Real failure detection and recovery
"""

import asyncio
import threading
from enum import Enum
from datetime import datetime, timedelta
from typing import Callable, Dict, Any, Optional, Awaitable
from dataclasses import dataclass, field
import logging

from .exceptions import CircuitBreakerError, ServiceUnavailableError

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker operational states"""
    CLOSED = "closed"      # Normal operation, failures counted
    OPEN = "open"         # Circuit open, calls rejected immediately
    HALF_OPEN = "half_open"  # Testing service recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior"""
    name: str
    failure_threshold: int = 5
    timeout_seconds: float = 30.0
    recovery_timeout: float = 60.0


class CircuitBreaker:
    """
    Thread-safe circuit breaker for resilient external service calls.
    
    Implements the Circuit Breaker pattern with three states:
    - CLOSED: Normal operation, counting failures
    - OPEN: Service considered down, rejecting calls
    - HALF_OPEN: Testing if service has recovered
    """
    
    def __init__(self, name: str, failure_threshold: int = 5, 
                 timeout_seconds: float = 30.0, recovery_timeout: float = 60.0):
        """
        Initialize circuit breaker with configuration.
        
        Args:
            name: Unique name for this circuit breaker
            failure_threshold: Number of failures before opening circuit
            timeout_seconds: Timeout for individual operations
            recovery_timeout: Time to wait before attempting recovery
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.recovery_timeout = recovery_timeout
        
        # Circuit state
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        
        # Metrics
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        
        # Thread safety
        self._lock = threading.RLock()
        
        logger.debug(f"Circuit breaker '{name}' initialized with threshold={failure_threshold}")
    
    async def call(self, operation: Callable[[], Awaitable[Any]]) -> Any:
        """
        Execute operation through circuit breaker.
        
        Args:
            operation: Async callable to execute
            
        Returns:
            Result of the operation
            
        Raises:
            CircuitBreakerError: If circuit is open
            asyncio.TimeoutError: If operation times out
            ServiceUnavailableError: If operation fails
        """
        with self._lock:
            self.total_calls += 1
            
            # Check if circuit should transition to HALF_OPEN
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                    logger.info(f"Circuit breaker '{self.name}' transitioning to HALF_OPEN")
                else:
                    # Circuit is open, reject call immediately
                    logger.warning(f"Circuit breaker '{self.name}' is OPEN, rejecting call")
                    raise CircuitBreakerError(self.name)
        
        # Execute operation with timeout
        try:
            start_time = datetime.now()
            result = await asyncio.wait_for(operation(), timeout=self.timeout_seconds)
            
            # Operation succeeded
            with self._lock:
                self._on_success()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.debug(f"Circuit breaker '{self.name}' call succeeded in {execution_time:.3f}s")
            
            return result
            
        except asyncio.TimeoutError:
            # Operation timed out
            with self._lock:
                self._on_failure()
            
            logger.warning(f"Circuit breaker '{self.name}' call timed out after {self.timeout_seconds}s")
            raise
            
        except Exception as e:
            # Operation failed
            with self._lock:
                self._on_failure()
            
            logger.warning(f"Circuit breaker '{self.name}' call failed: {e}")
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt circuit reset"""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = datetime.now() - self.last_failure_time
        return time_since_failure.total_seconds() >= self.recovery_timeout
    
    def _on_success(self) -> None:
        """Handle successful operation - reset circuit if needed"""
        self.successful_calls += 1
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            # Recovery successful, close circuit
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.last_failure_time = None
            logger.info(f"Circuit breaker '{self.name}' recovered, state reset to CLOSED")
        elif self.state == CircuitBreakerState.CLOSED:
            # Reset failure count on successful call
            self.failure_count = 0
    
    def _on_failure(self) -> None:
        """Handle failed operation - open circuit if threshold reached"""
        self.failed_calls += 1
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            # Recovery attempt failed, reopen circuit
            self.state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker '{self.name}' recovery failed, reopening circuit")
        elif self.state == CircuitBreakerState.CLOSED and self.failure_count >= self.failure_threshold:
            # Threshold reached, open circuit
            self.state = CircuitBreakerState.OPEN
            logger.error(f"Circuit breaker '{self.name}' opened after {self.failure_count} failures")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current circuit breaker metrics.
        
        Returns:
            Dictionary containing operational metrics
        """
        with self._lock:
            return {
                'name': self.name,
                'state': self.state.value,
                'failure_count': self.failure_count,
                'failure_threshold': self.failure_threshold,
                'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
                'total_calls': self.total_calls,
                'successful_calls': self.successful_calls,
                'failed_calls': self.failed_calls,
                'success_rate': self.successful_calls / max(1, self.total_calls),
                'recovery_timeout': self.recovery_timeout,
                'timeout_seconds': self.timeout_seconds
            }
    
    def reset(self) -> None:
        """
        Manually reset circuit breaker to CLOSED state.
        
        Note: This should only be used for testing or manual intervention.
        """
        with self._lock:
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.last_failure_time = None
            logger.info(f"Circuit breaker '{self.name}' manually reset to CLOSED")
    
    def force_open(self) -> None:
        """
        Manually force circuit breaker to OPEN state.
        
        Note: This should only be used for testing or emergency situations.
        """
        with self._lock:
            self.state = CircuitBreakerState.OPEN
            self.last_failure_time = datetime.now()
            logger.warning(f"Circuit breaker '{self.name}' manually forced to OPEN")
    
    def get_state(self) -> str:
        """Get current circuit breaker state as string."""
        with self._lock:
            return self.state.value
    
    def can_execute(self) -> bool:
        """Check if circuit breaker allows execution."""
        with self._lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            elif self.state == CircuitBreakerState.HALF_OPEN:
                return True
            else:  # OPEN
                return self._should_attempt_reset()
    
    def execute(self, operation: Callable) -> Any:
        """Synchronous wrapper for execute operation (compatibility)."""
        # For sync operation, just check state and call
        if not self.can_execute():
            raise CircuitBreakerError(self.name)
        
        try:
            result = operation()
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise e
    
    def record_success(self) -> None:
        """Record successful operation."""
        with self._lock:
            self._on_success()
    
    def record_failure(self) -> None:
        """Record failed operation."""
        with self._lock:
            self._on_failure()
    
    def __str__(self) -> str:
        """String representation of circuit breaker state"""
        with self._lock:
            return (f"CircuitBreaker(name='{self.name}', state={self.state.value}, "
                   f"failures={self.failure_count}/{self.failure_threshold})")
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"CircuitBreaker(name='{self.name}', state={self.state.value}, "
               f"failure_count={self.failure_count}, threshold={self.failure_threshold}, "
               f"timeout={self.timeout_seconds}s, recovery_timeout={self.recovery_timeout}s)")


class CircuitBreakerManager:
    """
    Manager for multiple circuit breakers with centralized configuration.
    
    Provides a registry of circuit breakers for different services and
    centralized monitoring capabilities.
    """
    
    def __init__(self):
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.RLock()
    
    def get_circuit_breaker(self, name: str, **kwargs) -> CircuitBreaker:
        """
        Get or create circuit breaker for a service.
        
        Args:
            name: Service name
            **kwargs: Circuit breaker configuration parameters
            
        Returns:
            CircuitBreaker instance for the service
        """
        if name not in self._circuit_breakers:
            with self._lock:
                if name not in self._circuit_breakers:
                    self._circuit_breakers[name] = CircuitBreaker(name=name, **kwargs)
        
        return self._circuit_breakers[name]
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metrics for all registered circuit breakers.
        
        Returns:
            Dictionary mapping service names to their metrics
        """
        with self._lock:
            return {name: cb.get_metrics() for name, cb in self._circuit_breakers.items()}
    
    def get_breaker(self, name: str, **kwargs) -> CircuitBreaker:
        """
        Alias for get_circuit_breaker for backward compatibility.
        
        Args:
            name: Service name
            **kwargs: Circuit breaker configuration parameters
            
        Returns:
            CircuitBreaker instance
        """
        return self.get_circuit_breaker(name, **kwargs)
    
    def reset_all(self) -> None:
        """Reset all circuit breakers to CLOSED state"""
        with self._lock:
            for circuit_breaker in self._circuit_breakers.values():
                circuit_breaker.reset()
    
    def get_health_status(self) -> Dict[str, str]:
        """
        Get health status for all services.
        
        Returns:
            Dictionary mapping service names to their current states
        """
        with self._lock:
            return {name: cb.state.value for name, cb in self._circuit_breakers.items()}


# Global circuit breaker manager instance
_circuit_breaker_manager = CircuitBreakerManager()


def get_circuit_breaker(service_name: str, **kwargs) -> CircuitBreaker:
    """
    Get circuit breaker for a service.
    
    Args:
        service_name: Name of the service
        **kwargs: Circuit breaker configuration
        
    Returns:
        CircuitBreaker instance
    """
    return _circuit_breaker_manager.get_circuit_breaker(service_name, **kwargs)


def get_all_circuit_breaker_metrics() -> Dict[str, Dict[str, Any]]:
    """Get metrics for all circuit breakers"""
    return _circuit_breaker_manager.get_all_metrics()


def reset_all_circuit_breakers() -> None:
    """Reset all circuit breakers - for testing only"""
    _circuit_breaker_manager.reset_all()