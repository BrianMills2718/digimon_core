#!/usr/bin/env python3
"""
Production Error Handler with Real Circuit Breakers
Implements fail-fast error handling philosophy with genuine circuit breaker patterns
"""

import time
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import logging

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5
    timeout: int = 60  # seconds
    recovery_timeout: int = 30  # seconds

@dataclass
class CircuitBreaker:
    """Real circuit breaker implementation"""
    config: CircuitBreakerConfig
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    last_failure_time: float = 0
    next_attempt_time: float = 0

class ProductionErrorHandler:
    """Production-ready error handler with real circuit breakers"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.error_counts: Dict[str, int] = {}
        self.logger = logging.getLogger(__name__)
        
        # Configure circuit breakers for different service types
        self.circuit_breaker_configs = {
            'database': CircuitBreakerConfig(failure_threshold=5, timeout=60),
            'api': CircuitBreakerConfig(failure_threshold=3, timeout=30),
            'file_system': CircuitBreakerConfig(failure_threshold=10, timeout=15),
            'service': CircuitBreakerConfig(failure_threshold=5, timeout=45),
        }
    
    def _get_circuit_breaker(self, service_type: str) -> CircuitBreaker:
        """Get or create circuit breaker for service type"""
        if service_type not in self.circuit_breakers:
            config = self.circuit_breaker_configs.get(
                service_type, 
                CircuitBreakerConfig()
            )
            self.circuit_breakers[service_type] = CircuitBreaker(config=config)
        return self.circuit_breakers[service_type]
    
    def _can_execute(self, circuit_breaker: CircuitBreaker) -> bool:
        """Check if request can be executed based on circuit breaker state"""
        current_time = time.time()
        
        if circuit_breaker.state == CircuitBreakerState.CLOSED:
            return True
        
        elif circuit_breaker.state == CircuitBreakerState.OPEN:
            if current_time >= circuit_breaker.next_attempt_time:
                circuit_breaker.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        
        elif circuit_breaker.state == CircuitBreakerState.HALF_OPEN:
            return True
        
        return False
    
    def _record_success(self, circuit_breaker: CircuitBreaker):
        """Record successful operation"""
        circuit_breaker.failure_count = 0
        circuit_breaker.state = CircuitBreakerState.CLOSED
    
    def _record_failure(self, circuit_breaker: CircuitBreaker):
        """Record failed operation and update circuit breaker state"""
        current_time = time.time()
        circuit_breaker.failure_count += 1
        circuit_breaker.last_failure_time = current_time
        
        if circuit_breaker.failure_count >= circuit_breaker.config.failure_threshold:
            circuit_breaker.state = CircuitBreakerState.OPEN
            circuit_breaker.next_attempt_time = current_time + circuit_breaker.config.timeout
    
    def handle_database_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """Handle database errors with circuit breaker"""
        service_type = 'database'
        circuit_breaker = self._get_circuit_breaker(service_type)
        
        # Check if we can attempt the operation
        if not self._can_execute(circuit_breaker):
            raise RuntimeError(f"Database circuit breaker OPEN - operation {operation} blocked")
        
        # Record the failure
        self._record_failure(circuit_breaker)
        
        # Log detailed error information
        error_info = {
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'circuit_breaker_state': circuit_breaker.state.value,
            'failure_count': circuit_breaker.failure_count,
            'timestamp': time.time()
        }
        
        self.logger.error(f"Database error in {operation}: {error}")
        
        # For critical database errors, fail fast
        if isinstance(error, (ConnectionError, TimeoutError)):
            raise error
        
        return error_info
    
    def handle_api_error(self, error: Exception, api_name: str) -> Optional[Dict[str, Any]]:
        """Handle API errors with graceful degradation"""
        service_type = 'api'
        circuit_breaker = self._get_circuit_breaker(service_type)
        
        if not self._can_execute(circuit_breaker):
            # Return degraded response instead of failing
            return {
                'status': 'degraded',
                'message': f'API {api_name} temporarily unavailable',
                'fallback_used': True
            }
        
        self._record_failure(circuit_breaker)
        
        # For rate limit errors, implement backoff
        if 'rate limit' in str(error).lower():
            time.sleep(min(circuit_breaker.failure_count * 2, 30))  # Exponential backoff
        
        self.logger.warning(f"API error for {api_name}: {error}")
        return None  # Caller should handle the error
    
    def handle_tool_error(self, tool_id: str, error: Exception, context: Dict[str, Any]):
        """Handle tool execution errors with circuit breaker"""
        service_type = 'service'
        circuit_breaker = self._get_circuit_breaker(service_type)
        
        if not self._can_execute(circuit_breaker):
            raise RuntimeError(f"Tool service circuit breaker OPEN - tool {tool_id} blocked")
        
        self._record_failure(circuit_breaker)
        
        self.logger.error(f"Tool {tool_id} error: {error}")
        
        # Always re-raise tool errors (fail fast)
        raise error
    
    def record_success(self, service_type: str):
        """Record successful operation for service type"""
        if service_type in self.circuit_breakers:
            circuit_breaker = self.circuit_breakers[service_type]
            self._record_success(circuit_breaker)
    
    def get_circuit_breaker_status(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive circuit breaker monitoring data"""
        status = {}
        for service_type, circuit_breaker in self.circuit_breakers.items():
            status[service_type] = {
                'state': circuit_breaker.state.value,
                'failure_count': circuit_breaker.failure_count,
                'last_failure_time': circuit_breaker.last_failure_time,
                'next_attempt_time': circuit_breaker.next_attempt_time,
                'failure_threshold': circuit_breaker.config.failure_threshold,
                'timeout': circuit_breaker.config.timeout
            }
        return status
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool information for audit compatibility"""
        return {
            "name": "ProductionErrorHandler",
            "category": "CoreService",
            "description": "Production-ready error handler with real circuit breakers",
            "circuit_breakers": len(self.circuit_breakers),
            "error_counts": len(self.error_counts)
        }

# Exception classes for different error types
class ValidationError(Exception):
    """Raised when input validation fails"""
    pass

class ProcessingError(Exception):
    """Raised when data processing fails"""
    pass

class DatabaseConnectionError(Exception):
    """Raised when database operations fail"""
    pass

class ServiceUnavailableError(Exception):
    """Raised when external services are unavailable"""
    pass

class SystemError(Exception):
    """Raised for system-level errors"""
    pass