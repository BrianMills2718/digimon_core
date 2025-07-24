"""
Test unified error handling framework.

Ensures all services follow consistent error patterns, have proper
recovery strategies, and maintain error taxonomy consistency.
"""

import pytest
import asyncio
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock

from src.core.error_taxonomy import (
    ErrorCategory, ErrorSeverity, RecoveryStrategy,
    KGASError, RecoveryResult, ErrorMetrics,
    CentralizedErrorHandler, get_global_error_handler,
    handle_errors, handle_errors_async, handle_errors_sync
)


class TestErrorClassification:
    """Test suite for error classification and categorization."""
    
    def test_error_category_determination(self):
        """Test that errors are properly categorized."""
        handler = CentralizedErrorHandler()
        
        # Test data corruption detection
        corruption_error = Exception("Data corruption detected in entity mappings")
        category, severity = handler._determine_category_and_severity(corruption_error, str(corruption_error))
        assert category == ErrorCategory.DATA_CORRUPTION
        assert severity == ErrorSeverity.CATASTROPHIC
        
        # Test academic integrity detection
        integrity_error = Exception("Citation fabrication detected")
        category, severity = handler._determine_category_and_severity(integrity_error, str(integrity_error))
        assert category == ErrorCategory.ACADEMIC_INTEGRITY
        assert severity == ErrorSeverity.CRITICAL
        
        # Test database failures
        db_error = Exception("Neo4j connection failed")
        category, severity = handler._determine_category_and_severity(db_error, str(db_error))
        assert category == ErrorCategory.DATABASE_FAILURE
        assert severity == ErrorSeverity.HIGH
        
        # Test resource exhaustion
        memory_error = Exception("Memory pool exhausted")
        category, severity = handler._determine_category_and_severity(memory_error, str(memory_error))
        assert category == ErrorCategory.RESOURCE_EXHAUSTION
        assert severity == ErrorSeverity.HIGH
        
        # Test network failures
        network_error = Exception("Network timeout connecting to service")
        category, severity = handler._determine_category_and_severity(network_error, str(network_error))
        assert category == ErrorCategory.NETWORK_FAILURE
        assert severity == ErrorSeverity.MEDIUM
    
    def test_recovery_strategy_selection(self):
        """Test automatic recovery strategy selection."""
        handler = CentralizedErrorHandler()
        
        # Create test errors
        corruption_error = KGASError(
            error_id="test-1",
            category=ErrorCategory.DATA_CORRUPTION,
            severity=ErrorSeverity.CATASTROPHIC,
            message="Data corruption",
            context={},
            timestamp="2025-01-01T00:00:00",
            service_name="test",
            operation="test"
        )
        
        network_error = KGASError(
            error_id="test-2",
            category=ErrorCategory.NETWORK_FAILURE,
            severity=ErrorSeverity.MEDIUM,
            message="Network timeout",
            context={},
            timestamp="2025-01-01T00:00:00",
            service_name="test",
            operation="test"
        )
        
        # Test strategy selection
        assert handler._select_recovery_strategy(corruption_error) == RecoveryStrategy.ABORT_AND_ALERT
        assert handler._select_recovery_strategy(network_error) == RecoveryStrategy.RETRY
    
    def test_recovery_suggestions_generation(self):
        """Test recovery suggestion generation."""
        handler = CentralizedErrorHandler()
        
        # Test data corruption suggestions
        suggestions = handler._generate_recovery_suggestions(ErrorCategory.DATA_CORRUPTION, "IntegrityError")
        assert "Initiate immediate data integrity check" in suggestions
        assert "Rollback to last known good state" in suggestions
        
        # Test resource exhaustion suggestions
        suggestions = handler._generate_recovery_suggestions(ErrorCategory.RESOURCE_EXHAUSTION, "MemoryError")
        assert "Clear caches and free memory" in suggestions
        assert "Restart connection pools" in suggestions


class TestCentralizedErrorHandler:
    """Test suite for centralized error handler."""
    
    @pytest.mark.asyncio
    async def test_error_handling_flow(self):
        """Test complete error handling flow."""
        handler = CentralizedErrorHandler()
        
        # Track escalations
        escalated_errors = []
        handler.register_escalation_handler(lambda e: escalated_errors.append(e))
        
        # Create test error
        test_error = Exception("Test network failure")
        context = {
            "service_name": "TestService",
            "operation": "test_operation",
            "attempt": 1
        }
        
        # Handle error
        result = await handler.handle_error(test_error, context)
        
        # Verify error was classified
        assert isinstance(result, KGASError)
        assert result.category == ErrorCategory.NETWORK_FAILURE
        assert result.severity == ErrorSeverity.MEDIUM
        assert result.service_name == "TestService"
        assert result.operation == "test_operation"
        
        # Check metrics were recorded
        metrics = handler.error_metrics.get_error_summary()
        assert metrics["total_errors"] == 1
        assert metrics["error_breakdown"]["network_failure"] == 1
        
        # Not critical, so no escalation
        assert len(escalated_errors) == 0
    
    @pytest.mark.asyncio
    async def test_recovery_strategy_execution(self):
        """Test recovery strategy execution."""
        handler = CentralizedErrorHandler()
        
        # Register custom recovery strategies
        retry_called = False
        
        async def custom_retry_strategy(error):
            nonlocal retry_called
            retry_called = True
            return True
        
        handler.register_recovery_strategy("network_timeout", custom_retry_strategy)
        
        # Test network error recovery
        network_error = Exception("Network timeout occurred")
        context = {
            "service_name": "TestService",
            "operation": "fetch_data"
        }
        
        result = await handler.handle_error(network_error, context)
        
        # Should have attempted recovery
        assert result.category == ErrorCategory.NETWORK_FAILURE
        
        # Test data corruption (no auto-recovery)
        corruption_error = Exception("Data corruption detected")
        context = {
            "service_name": "TestService",
            "operation": "validate_data"
        }
        
        result = await handler.handle_error(corruption_error, context)
        assert result.category == ErrorCategory.DATA_CORRUPTION
        assert result.severity == ErrorSeverity.CATASTROPHIC
    
    @pytest.mark.asyncio
    async def test_error_escalation(self):
        """Test critical error escalation."""
        handler = CentralizedErrorHandler()
        
        escalated_errors = []
        async def track_escalation(error):
            escalated_errors.append(error)
        
        handler.register_escalation_handler(track_escalation)
        
        # Critical error should escalate
        critical_error = Exception("Critical system failure - data corruption detected")
        context = {
            "service_name": "TestService",
            "operation": "critical_operation"
        }
        
        result = await handler.handle_error(critical_error, context)
        assert len(escalated_errors) == 1
        assert result.severity == ErrorSeverity.CATASTROPHIC
        
        # Academic integrity violation should also escalate
        integrity_error = Exception("Academic integrity violation: citation fabrication")
        context = {
            "service_name": "TestService",
            "operation": "citation_check"
        }
        
        result = await handler.handle_error(integrity_error, context)
        assert len(escalated_errors) == 2
        assert result.category == ErrorCategory.ACADEMIC_INTEGRITY
    
    @pytest.mark.asyncio
    async def test_error_tracking_and_statistics(self):
        """Test error tracking and statistics."""
        handler = CentralizedErrorHandler()
        
        # Generate various errors
        for i in range(10):
            if i < 7:
                error = Exception("Network timeout error")
            else:
                error = Exception("Validation failed")
            
            context = {
                "service_name": "TestService",
                "operation": "operation",
                "index": i
            }
            await handler.handle_error(error, context)
        
        # Check statistics
        metrics = handler.error_metrics.get_error_summary()
        assert metrics["total_errors"] == 10
        assert metrics["error_breakdown"]["network_failure"] == 7
        assert metrics["error_breakdown"]["validation_failure"] == 3
    
    @pytest.mark.asyncio
    async def test_error_metrics(self):
        """Test error metrics tracking."""
        metrics = ErrorMetrics(max_history=10)
        
        # Record some errors
        for i in range(5):
            error = KGASError(
                error_id=f"test-{i}",
                category=ErrorCategory.NETWORK_FAILURE if i < 3 else ErrorCategory.DATABASE_FAILURE,
                severity=ErrorSeverity.MEDIUM,
                message=f"Test error {i}",
                context={},
                timestamp="2025-01-01T00:00:00",
                service_name="TestService",
                operation="test_op"
            )
            metrics.record_error(error)
        
        # Record recovery attempts
        for i in range(3):
            result = RecoveryResult(
                success=i < 2,  # First 2 succeed
                strategy_used=RecoveryStrategy.RETRY,
                error_id=f"test-{i}",
                recovery_time=0.5,
                message="Recovery attempt"
            )
            metrics.record_recovery(result)
        
        # Check metrics
        summary = metrics.get_error_summary()
        assert summary["total_errors"] == 5
        assert summary["error_breakdown"]["network_failure"] == 3
        assert summary["error_breakdown"]["database_failure"] == 2
        assert summary["recovery_success_rates"]["retry"]["success_rate"] == 2/3


class TestErrorHandlingIntegration:
    """Test error handling integration with services."""
    
    @pytest.mark.asyncio
    async def test_decorator_error_handling(self):
        """Test error handling decorator."""
        handler = get_global_error_handler()
        
        # Track errors
        errors_handled = []
        
        async def track_errors(error):
            errors_handled.append(error)
        
        handler.register_escalation_handler(track_errors)
        
        # Test async function with decorator
        @handle_errors("TestService", "test_operation")
        async def failing_operation():
            raise Exception("Test failure")
        
        # Should raise but handle error
        with pytest.raises(Exception):
            await failing_operation()
        
        # Error should be tracked
        metrics = handler.error_metrics.get_error_summary()
        assert metrics["total_errors"] > 0
    
    @pytest.mark.asyncio
    async def test_context_manager_error_handling(self):
        """Test error handling context manager."""
        handler = CentralizedErrorHandler()
        
        # Test async context manager
        try:
            async with handle_errors_async("TestService", "test_op", handler):
                raise Exception("Test error in context")
        except Exception:
            pass  # Expected
        
        # Check error was handled
        metrics = handler.error_metrics.get_error_summary()
        assert metrics["total_errors"] == 1
    
    @pytest.mark.asyncio
    async def test_system_health_assessment(self):
        """Test system health assessment from errors."""
        handler = CentralizedErrorHandler()
        
        # Generate different severity errors
        # Low severity errors
        for i in range(5):
            error = Exception("Minor validation error")
            await handler.handle_error(error, {"service_name": "test", "operation": "validate"})
        
        # Check health - should be healthy with few errors
        health = handler.get_system_health_from_errors()
        assert health["health_score"] >= 8
        assert health["status"] == "healthy"
        
        # Add critical errors
        for i in range(3):
            error = Exception("Critical data corruption detected")
            await handler.handle_error(error, {"service_name": "test", "operation": "check"})
        
        # Health should degrade
        health = handler.get_system_health_from_errors()
        assert health["health_score"] < 3
        assert health["status"] == "unhealthy"
    
    @pytest.mark.asyncio
    async def test_error_recovery_strategies(self):
        """Test built-in recovery strategies."""
        handler = CentralizedErrorHandler()
        
        # Test database recovery
        db_error = KGASError(
            error_id="test-db",
            category=ErrorCategory.DATABASE_FAILURE,
            severity=ErrorSeverity.HIGH,
            message="Database connection lost",
            context={},
            timestamp="2025-01-01T00:00:00",
            service_name="test",
            operation="query"
        )
        
        result = await handler._recover_database_connection(db_error)
        assert isinstance(result, bool)
        
        # Test memory recovery
        memory_error = KGASError(
            error_id="test-mem",
            category=ErrorCategory.RESOURCE_EXHAUSTION,
            severity=ErrorSeverity.HIGH,
            message="Memory exhausted",
            context={},
            timestamp="2025-01-01T00:00:00",
            service_name="test",
            operation="process"
        )
        
        result = await handler._recover_memory_exhaustion(memory_error)
        assert result is True  # Should succeed with gc.collect()
    
    @pytest.mark.asyncio
    async def test_academic_integrity_handling(self):
        """Test academic integrity violation handling."""
        handler = CentralizedErrorHandler()
        
        # Track escalations
        escalations = []
        handler.register_escalation_handler(lambda e: escalations.append(e))
        
        # Create academic integrity violation
        error = Exception("Academic integrity violation: fabricated citation detected")
        context = {
            "service_name": "CitationService",
            "operation": "verify_citation",
            "citation_id": "fake-123"
        }
        
        result = await handler.handle_error(error, context)
        
        # Should be categorized correctly
        assert result.category == ErrorCategory.ACADEMIC_INTEGRITY
        assert result.severity == ErrorSeverity.CRITICAL
        
        # Should be escalated
        assert len(escalations) == 1
        
        # Recovery should fail (never auto-recover from integrity violations)
        recovery_result = await handler._handle_academic_integrity(result)
        assert recovery_result is False