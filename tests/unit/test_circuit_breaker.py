"""
Test-Driven Development: Circuit Breaker Pattern Tests

Following TDD methodology:
1. Write tests first (RED phase)
2. Implement minimal code (GREEN phase)
3. Refactor for quality (REFACTOR phase)
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
import time

from src.core.circuit_breaker import CircuitBreaker, CircuitBreakerState, CircuitBreakerError
from src.core.exceptions import ServiceUnavailableError


class TestCircuitBreaker:
    """Test suite for Circuit Breaker pattern implementation"""
    
    @pytest.fixture
    def circuit_breaker(self):
        """Create circuit breaker with test configuration"""
        return CircuitBreaker(
            name="test_service",
            failure_threshold=3,
            timeout_seconds=1.0,
            recovery_timeout=5.0
        )
    
    def test_circuit_breaker_initial_state(self, circuit_breaker):
        """Test: Circuit breaker starts in CLOSED state"""
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.last_failure_time is None
    
    @pytest.mark.asyncio
    async def test_successful_call_keeps_circuit_closed(self, circuit_breaker):
        """Test: Successful calls keep circuit in CLOSED state"""
        async def successful_operation():
            return "success"
        
        result = await circuit_breaker.call(successful_operation)
        
        assert result == "success"
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_failures_increase_count(self, circuit_breaker):
        """Test: Failed calls increase failure count"""
        async def failing_operation():
            raise ServiceUnavailableError("test_service", "Test failure")
        
        # First failure
        with pytest.raises(ServiceUnavailableError):
            await circuit_breaker.call(failing_operation)
        
        assert circuit_breaker.failure_count == 1
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        
        # Second failure
        with pytest.raises(ServiceUnavailableError):
            await circuit_breaker.call(failing_operation)
        
        assert circuit_breaker.failure_count == 2
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
    
    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold_failures(self, circuit_breaker):
        """Test: Circuit opens after reaching failure threshold"""
        async def failing_operation():
            raise ServiceUnavailableError("test_service", "Test failure")
        
        # Reach failure threshold (3 failures)
        for _ in range(3):
            with pytest.raises(ServiceUnavailableError):
                await circuit_breaker.call(failing_operation)
        
        assert circuit_breaker.state == CircuitBreakerState.OPEN
        assert circuit_breaker.failure_count == 3
        assert circuit_breaker.last_failure_time is not None
    
    @pytest.mark.asyncio
    async def test_open_circuit_rejects_calls_immediately(self, circuit_breaker):
        """Test: Open circuit rejects calls without executing them"""
        async def failing_operation():
            raise ServiceUnavailableError("test_service", "Test failure")
        
        async def tracked_operation():
            tracked_operation.called = True
            return "should_not_execute"
        
        tracked_operation.called = False
        
        # Open the circuit
        for _ in range(3):
            with pytest.raises(ServiceUnavailableError):
                await circuit_breaker.call(failing_operation)
        
        assert circuit_breaker.state == CircuitBreakerState.OPEN
        
        # Try to call - should be rejected immediately
        with pytest.raises(CircuitBreakerError):
            await circuit_breaker.call(tracked_operation)
        
        assert not tracked_operation.called
    
    @pytest.mark.asyncio
    async def test_circuit_transitions_to_half_open_after_timeout(self, circuit_breaker):
        """Test: Circuit transitions to HALF_OPEN after recovery timeout"""
        async def failing_operation():
            raise ServiceUnavailableError("test_service", "Test failure")
        
        # Open the circuit
        for _ in range(3):
            with pytest.raises(ServiceUnavailableError):
                await circuit_breaker.call(failing_operation)
        
        assert circuit_breaker.state == CircuitBreakerState.OPEN
        
        # Manually set last failure time to simulate timeout
        circuit_breaker.last_failure_time = datetime.now() - timedelta(seconds=6)
        
        # Next call should transition to HALF_OPEN
        async def test_operation():
            return "testing"
        
        result = await circuit_breaker.call(test_operation)
        
        assert result == "testing"
        assert circuit_breaker.state == CircuitBreakerState.CLOSED  # Should close on success
        assert circuit_breaker.failure_count == 0  # Should reset count
    
    @pytest.mark.asyncio
    async def test_half_open_success_closes_circuit(self, circuit_breaker):
        """Test: Successful call in HALF_OPEN state closes circuit"""
        # Force circuit to HALF_OPEN state
        circuit_breaker.state = CircuitBreakerState.HALF_OPEN
        circuit_breaker.failure_count = 3
        
        async def successful_operation():
            return "recovery_success"
        
        result = await circuit_breaker.call(successful_operation)
        
        assert result == "recovery_success"
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_half_open_failure_reopens_circuit(self, circuit_breaker):
        """Test: Failed call in HALF_OPEN state reopens circuit"""
        # Force circuit to HALF_OPEN state
        circuit_breaker.state = CircuitBreakerState.HALF_OPEN
        circuit_breaker.failure_count = 2
        
        async def failing_operation():
            raise ServiceUnavailableError("test_service", "Recovery failed")
        
        with pytest.raises(ServiceUnavailableError):
            await circuit_breaker.call(failing_operation)
        
        assert circuit_breaker.state == CircuitBreakerState.OPEN
        assert circuit_breaker.failure_count == 3
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, circuit_breaker):
        """Test: Circuit breaker handles operation timeouts"""
        async def slow_operation():
            await asyncio.sleep(2.0)  # Longer than 1.0s timeout
            return "should_timeout"
        
        with pytest.raises(asyncio.TimeoutError):
            await circuit_breaker.call(slow_operation)
        
        assert circuit_breaker.failure_count == 1
    
    def test_circuit_breaker_metrics(self, circuit_breaker):
        """Test: Circuit breaker provides operational metrics"""
        metrics = circuit_breaker.get_metrics()
        
        expected_keys = [
            'name', 'state', 'failure_count', 'failure_threshold',
            'last_failure_time', 'total_calls', 'successful_calls', 'failed_calls'
        ]
        
        for key in expected_keys:
            assert key in metrics
        
        assert metrics['name'] == 'test_service'
        assert metrics['state'] == CircuitBreakerState.CLOSED.value
        assert metrics['failure_threshold'] == 3
    
    @pytest.mark.asyncio
    async def test_concurrent_calls_are_handled_correctly(self, circuit_breaker):
        """Test: Circuit breaker handles concurrent calls correctly"""
        call_count = 0
        
        async def counting_operation():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)
            return f"call_{call_count}"
        
        # Execute multiple concurrent calls
        tasks = [circuit_breaker.call(counting_operation) for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all(result.startswith("call_") for result in results)
        assert circuit_breaker.state == CircuitBreakerState.CLOSED


class TestCircuitBreakerIntegration:
    """Integration tests for circuit breaker with external services"""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_with_external_service_mock(self):
        """Test: Circuit breaker integration with external service simulation"""
        circuit_breaker = CircuitBreaker(
            name="external_api",
            failure_threshold=2,
            timeout_seconds=0.5,
            recovery_timeout=2.0
        )
        
        # Mock external service that fails then recovers
        call_count = 0
        
        async def unreliable_service():
            nonlocal call_count
            call_count += 1
            
            if call_count <= 2:
                raise ServiceUnavailableError("external_api", f"Failure {call_count}")
            return f"Success on call {call_count}"
        
        # First two calls should fail and open circuit
        with pytest.raises(ServiceUnavailableError):
            await circuit_breaker.call(unreliable_service)
        
        with pytest.raises(ServiceUnavailableError):
            await circuit_breaker.call(unreliable_service)
        
        assert circuit_breaker.state == CircuitBreakerState.OPEN
        
        # Immediate third call should be rejected by circuit breaker
        with pytest.raises(CircuitBreakerError):
            await circuit_breaker.call(unreliable_service)
        
        # Simulate timeout passage
        circuit_breaker.last_failure_time = datetime.now() - timedelta(seconds=3)
        
        # Fourth call should succeed and close circuit
        result = await circuit_breaker.call(unreliable_service)
        assert result == "Success on call 3"
        assert circuit_breaker.state == CircuitBreakerState.CLOSED