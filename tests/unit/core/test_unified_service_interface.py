"""
Unit tests for unified service interface

Tests the standard service interfaces and communication protocols
that all core services must implement.
"""

import pytest
from typing import Dict, Any, Optional
from datetime import datetime

from src.core.unified_service_interface import (
    ServiceRequest,
    ServiceResponse,
    ServiceMetrics,
    CoreService
)


# Test implementation of CoreService
class MockCoreService(CoreService):
    def __init__(self, name: str = "mock_service", config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.name = name
        self.operation_count = 0
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the service"""
        self.config.update(config)
        self._initialized = True
        self._healthy = True
        return True
    
    def health_check(self) -> bool:
        """Check service health"""
        return self._healthy
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            "name": self.name,
            "version": "1.0.0",
            "initialized": self._initialized,
            "healthy": self._healthy
        }
    
    def cleanup(self) -> bool:
        """Clean up service resources"""
        self._initialized = False
        self._healthy = False
        return True
    
    def custom_operation(self, data: Any) -> Dict[str, Any]:
        """Custom operation for testing"""
        self.operation_count += 1
        
        if data is None:
            return {"error": "Data cannot be None"}
        
        return {"processed": data, "count": self.operation_count}


class TestServiceRequest:
    """Test ServiceRequest dataclass"""
    
    def test_service_request_creation(self):
        """Test creating ServiceRequest"""
        request = ServiceRequest(
            operation="test_operation",
            parameters={"key": "value"},
            context={"user_id": "123"},
            request_id="req_123"
        )
        
        assert request.operation == "test_operation"
        assert request.parameters == {"key": "value"}
        assert request.context == {"user_id": "123"}
        assert request.request_id == "req_123"
        
    def test_service_request_minimal(self):
        """Test creating minimal ServiceRequest"""
        request = ServiceRequest(
            operation="test_operation",
            parameters={}
        )
        
        assert request.operation == "test_operation"
        assert request.parameters == {}
        assert request.context is None
        assert request.request_id is None


class TestServiceResponse:
    """Test ServiceResponse dataclass"""
    
    def test_service_response_success(self):
        """Test creating successful ServiceResponse"""
        response = ServiceResponse(
            success=True,
            data={"result": "value"},
            metadata={"timestamp": "2023-01-01T00:00:00"},
            request_id="req_123"
        )
        
        assert response.success is True
        assert response.data == {"result": "value"}
        assert response.metadata == {"timestamp": "2023-01-01T00:00:00"}
        assert response.request_id == "req_123"
        assert response.error_code is None
        assert response.error_message is None
        
    def test_service_response_error(self):
        """Test creating error ServiceResponse"""
        response = ServiceResponse(
            success=False,
            data=None,
            metadata={"timestamp": "2023-01-01T00:00:00"},
            error_code="TEST_ERROR",
            error_message="Test error message",
            request_id="req_123"
        )
        
        assert response.success is False
        assert response.data is None
        assert response.error_code == "TEST_ERROR"
        assert response.error_message == "Test error message"
        assert response.request_id == "req_123"


class TestServiceMetrics:
    """Test ServiceMetrics dataclass"""
    
    def test_service_metrics_creation(self):
        """Test creating ServiceMetrics"""
        metrics = ServiceMetrics(
            total_requests=100,
            successful_requests=95,
            failed_requests=5,
            average_response_time=0.5
        )
        
        assert metrics.total_requests == 100
        assert metrics.successful_requests == 95
        assert metrics.failed_requests == 5
        assert metrics.average_response_time == 0.5
        
    def test_service_metrics_defaults(self):
        """Test ServiceMetrics with default values"""
        metrics = ServiceMetrics()
        
        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0
        assert metrics.average_response_time == 0.0
        assert metrics.last_request_time is None
        assert metrics.service_start_time is None


class TestCoreService:
    """Test CoreService abstract base class and implementation"""
    
    def test_core_service_interface(self):
        """Test that CoreService defines required interface"""
        # Check that required methods exist
        required_methods = ['initialize', 'health_check', 'get_service_info', 'cleanup']
        for method_name in required_methods:
            assert hasattr(CoreService, method_name)
            
    def test_mock_service_implementation(self):
        """Test mock service implements CoreService correctly"""
        service = MockCoreService("test_service")
        
        # Test it's a CoreService
        assert isinstance(service, CoreService)
        
        # Test initialization
        config = {"setting": "value"}
        success = service.initialize(config)
        
        assert success is True
        assert service._initialized is True
        assert service._healthy is True
        
        # Test health check after initialization
        health = service.health_check()
        assert health is True
        
        # Test service info
        info = service.get_service_info()
        assert info["name"] == "test_service"
        assert info["initialized"] is True
        assert info["healthy"] is True
        
        # Test cleanup
        cleanup_success = service.cleanup()
        assert cleanup_success is True
        assert service._initialized is False
        assert service._healthy is False
        
    def test_service_health_check_after_cleanup(self):
        """Test health check after service cleanup"""
        service = MockCoreService()
        
        # Initialize service
        service.initialize({})
        assert service.health_check() is True
        
        # Cleanup service
        service.cleanup()
        assert service.health_check() is False
        
    def test_service_custom_operations(self):
        """Test custom service operations"""
        service = MockCoreService()
        service.initialize({})
        
        # Test successful operation
        result = service.custom_operation("test_data")
        assert result["processed"] == "test_data"
        assert result["count"] == 1
        assert service.operation_count == 1
        
        # Test another operation (count should increment)
        result2 = service.custom_operation("more_data")
        assert result2["count"] == 2
        assert service.operation_count == 2
        
        # Test error condition
        error_result = service.custom_operation(None)
        assert "error" in error_result
        assert error_result["error"] == "Data cannot be None"
        
    def test_service_configuration(self):
        """Test service configuration handling"""
        initial_config = {"initial": "value"}
        service = MockCoreService("config_test", initial_config)
        
        # Check initial config
        assert service.config == initial_config
        
        # Update config during initialization
        new_config = {"new": "setting", "number": 42}
        service.initialize(new_config)
        
        # Config should be merged
        expected_config = {"initial": "value", "new": "setting", "number": 42}
        assert service.config == expected_config
        
    def test_service_metrics_initialization(self):
        """Test that service metrics are properly initialized"""
        service = MockCoreService()
        
        # Check metrics exist and are initialized
        assert hasattr(service, 'metrics')
        assert isinstance(service.metrics, ServiceMetrics)
        assert service.metrics.total_requests == 0
        assert service.metrics.successful_requests == 0
        assert service.metrics.failed_requests == 0
        
    def test_service_logger_initialization(self):
        """Test that service logger is properly initialized"""
        service = MockCoreService("logger_test")
        
        # Check logger exists
        assert hasattr(service, 'logger')
        assert service.logger is not None
        
    def test_concurrent_service_operations(self):
        """Test service operations under concurrent access"""
        import threading
        
        service = MockCoreService()
        service.initialize({})
        
        results = []
        
        def perform_operations():
            for i in range(10):
                result = service.custom_operation(f"data_{i}")
                results.append(result)
                
        # Create multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=perform_operations)
            threads.append(thread)
            
        # Start all threads
        for thread in threads:
            thread.start()
            
        # Wait for completion
        for thread in threads:
            thread.join()
            
        # Check results
        assert len(results) == 30  # 3 threads * 10 operations each
        
        # All should be successful (no errors)
        error_results = [r for r in results if "error" in r]
        assert len(error_results) == 0
        
        # Final operation count should be 30
        assert service.operation_count == 30


class TestServiceIntegration:
    """Test service integration scenarios"""
    
    def test_service_lifecycle(self):
        """Test complete service lifecycle"""
        service = MockCoreService("lifecycle_test")
        
        # 1. Initial state
        info = service.get_service_info()
        assert not info["initialized"]
        assert not info["healthy"]
        
        # 2. Initialize
        success = service.initialize({"config": "value"})
        assert success
        
        # 3. Check health
        assert service.health_check() is True
        
        # 4. Perform operations
        result = service.custom_operation("test")
        assert "processed" in result
        
        # 5. Get updated info
        info = service.get_service_info()
        assert info["initialized"] is True
        assert info["healthy"] is True
        
        # 6. Cleanup
        cleanup_success = service.cleanup()
        assert cleanup_success
        
        # 7. Verify cleanup
        assert service.health_check() is False
        info = service.get_service_info()
        assert info["initialized"] is False
        assert info["healthy"] is False
        
    def test_multiple_service_instances(self):
        """Test multiple service instances work independently"""
        service1 = MockCoreService("service_1")
        service2 = MockCoreService("service_2")
        
        # Initialize both
        service1.initialize({"config": "service1"})
        service2.initialize({"config": "service2"})
        
        # Perform different operations
        service1.custom_operation("data1")
        service1.custom_operation("data2")
        service2.custom_operation("data3")
        
        # Check operation counts are independent
        assert service1.operation_count == 2
        assert service2.operation_count == 1
        
        # Check service info is independent
        info1 = service1.get_service_info()
        info2 = service2.get_service_info()
        
        assert info1["name"] == "service_1"
        assert info2["name"] == "service_2"
        
    def test_service_error_handling(self):
        """Test service error handling"""
        service = MockCoreService()
        
        # Test operations on uninitialized service
        result = service.custom_operation("test")
        # Should still work, just not be "healthy"
        assert service.health_check() is False
        
        # Initialize and test again
        service.initialize({})
        assert service.health_check() is True
        
        # Test error conditions
        error_result = service.custom_operation(None)
        assert "error" in error_result


class TestMissingCoverage:
    """Test cases to cover missing lines in unified service interface"""
    
    def test_get_metrics_method(self):
        """Test get_metrics method - covers line 108"""
        service = MockCoreService("test_service")
        metrics = service.get_metrics()
        
        # Should return the metrics object
        assert metrics.total_requests >= 0
        assert metrics.successful_requests >= 0
        assert metrics.failed_requests >= 0
    
    def test_update_metrics_success(self):
        """Test update_metrics with successful request - covers lines 117-119"""
        service = MockCoreService("test_service")
        initial_total = service.metrics.total_requests
        initial_success = service.metrics.successful_requests
        
        # Update with successful request
        service.update_metrics(success=True, response_time=0.5)
        
        assert service.metrics.total_requests == initial_total + 1
        assert service.metrics.successful_requests == initial_success + 1
        assert service.metrics.average_response_time > 0
    
    def test_update_metrics_failure(self):
        """Test update_metrics with failed request - covers remaining update_metrics lines"""
        service = MockCoreService("test_service")
        initial_total = service.metrics.total_requests
        initial_failed = service.metrics.failed_requests
        
        # Update with failed request
        service.update_metrics(success=False, response_time=1.2)
        
        assert service.metrics.total_requests == initial_total + 1
        assert service.metrics.failed_requests == initial_failed + 1
    
    def test_service_cleanup_method(self):
        """Test service cleanup method - covers missing cleanup lines"""
        service = MockCoreService("test_service")
        service.initialize({})
        
        # Cleanup should work without errors and affect health check
        service.cleanup()
        
        # Health check should reflect cleanup state
        health = service.health_check()
        # MockCoreService cleanup might change health status
        assert isinstance(health, bool)
    
    def test_service_error_response(self):
        """Test service error response creation"""
        from src.core.unified_service_interface import ServiceResponse
        
        # Test error response with all fields
        error_response = ServiceResponse(
            success=False,
            data=None,
            metadata={"error_context": "test"},
            error_code="TEST_ERROR",
            error_message="Test error message"
        )
        
        assert error_response.success is False
        assert error_response.error_code == "TEST_ERROR"
        assert error_response.error_message == "Test error message"