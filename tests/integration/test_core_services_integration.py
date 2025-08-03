"""
Integration tests for core services

Tests the integration between dependency injection, service management,
and unified service interfaces working together.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from src.core.dependency_injection import DependencyContainer
from src.core.unified_service_interface import CoreService
from src.core.security_validation import SecurityValidator


# Mock service implementations for integration testing
class MockIntegrationService(CoreService):
    """Mock service for integration testing"""
    
    def __init__(self, name: str = "mock_integration_service", config=None):
        super().__init__(config)
        self.name = name
        
    def initialize(self, config: dict) -> bool:
        self.config.update(config)
        self._initialized = True
        self._healthy = True
        return True
    
    def health_check(self) -> bool:
        return self._healthy
    
    def get_service_info(self) -> dict:
        return {
            "name": self.name,
            "initialized": self._initialized,
            "healthy": self._healthy
        }
    
    def cleanup(self) -> bool:
        self._initialized = False
        self._healthy = False
        return True


@pytest.fixture
def integration_container():
    """Create DI container for integration tests"""
    return DependencyContainer()


@pytest.fixture
def temp_project_for_security(tmp_path):
    """Create temporary project for security testing"""
    # Create a test file with security issues
    test_file = tmp_path / "test_service.py"
    test_file.write_text("""
class TestService:
    def __init__(self):
        self.api_key = "sk-test123456789"
        self.password = "secret123"
""")
    return tmp_path


class TestDependencyInjectionIntegration:
    """Test dependency injection with real services"""
    
    def test_register_and_resolve_service(self, integration_container):
        """Test registering and resolving a service"""
        # Register service
        integration_container.register_singleton(
            MockIntegrationService,
            MockIntegrationService,
            {"test": "config"}
        )
        
        # Resolve service
        service = integration_container.resolve(MockIntegrationService)
        
        # Verify service
        assert isinstance(service, MockIntegrationService)
        assert service.name == "mock_integration_service"
        
        # Test service operations
        config = {"test": "config"}
        success = service.initialize(config)
        assert success
        
        health = service.health_check()
        assert health
        
    def test_singleton_behavior_integration(self, integration_container):
        """Test singleton behavior in integration scenario"""
        integration_container.register_singleton(
            MockIntegrationService,
            MockIntegrationService
        )
        
        # Resolve multiple times
        service1 = integration_container.resolve(MockIntegrationService)
        service2 = integration_container.resolve(MockIntegrationService)
        
        # Should be same instance
        assert service1 is service2
        
        # Initialize one, should affect both
        service1.initialize({"test": "value"})
        assert service1._initialized
        assert service2._initialized
        
    def test_transient_behavior_integration(self, integration_container):
        """Test transient behavior in integration scenario"""
        integration_container.register_transient(
            MockIntegrationService,
            MockIntegrationService
        )
        
        # Resolve multiple times
        service1 = integration_container.resolve(MockIntegrationService)
        service2 = integration_container.resolve(MockIntegrationService)
        
        # Should be different instances
        assert service1 is not service2
        
        # Initialize one, should not affect the other
        service1.initialize({"test": "value"})
        assert service1._initialized
        assert not service2._initialized


class TestServiceInterfaceIntegration:
    """Test unified service interface integration"""
    
    def test_multiple_services_same_interface(self):
        """Test multiple services implementing same interface"""
        service1 = MockIntegrationService("service_1")
        service2 = MockIntegrationService("service_2")
        
        services = [service1, service2]
        
        # Initialize all services
        config = {"test": "config"}
        for service in services:
            success = service.initialize(config)
            assert success
            
        # Check health of all services
        for service in services:
            health = service.health_check()
            assert health
            
        # Get info from all services
        for i, service in enumerate(services, 1):
            info = service.get_service_info()
            assert info["name"] == f"service_{i}"
            
    def test_service_lifecycle_integration(self):
        """Test complete service lifecycle"""
        service = MockIntegrationService("lifecycle_service")
        
        # 1. Initial state
        assert not service._initialized
        
        # 2. Initialize
        success = service.initialize({"config": "value"})
        assert success
        assert service._initialized
        
        # 3. Health check
        health = service.health_check()
        assert health
        
        # 4. Get info
        info = service.get_service_info()
        assert info["healthy"]
        
        # 5. Cleanup
        cleanup_success = service.cleanup()
        assert cleanup_success
        assert not service._initialized
        
        # 6. Health check after cleanup
        health_after_cleanup = service.health_check()
        assert not health_after_cleanup


class TestSecurityValidationIntegration:
    """Test security validation integration"""
    
    def test_security_validation_with_real_files(self, temp_project_for_security):
        """Test security validation on real files"""
        validator = SecurityValidator()
        
        # Scan file for security issues
        issues = validator.scan_file(str(temp_project_for_security / "test_service.py"))
        
        # Should find security issues
        assert len(issues) > 0
        
        # Issues should have required fields
        for issue in issues:
            assert hasattr(issue, 'file_path')
            assert hasattr(issue, 'line_number')
            assert hasattr(issue, 'issue_type')
            assert hasattr(issue, 'severity')
            
    def test_security_validation_performance_integration(self, temp_project_for_security):
        """Test security validation performance"""
        import time
        
        validator = SecurityValidator()
        
        # Measure scan time
        start_time = time.time()
        issues = validator.scan_file(str(temp_project_for_security / "test_service.py"))
        end_time = time.time()
        
        scan_time = end_time - start_time
        
        # Should complete quickly
        assert scan_time < 1.0  # Less than 1 second for small file
        
        # Should still find issues
        assert len(issues) > 0


class TestCrossServiceIntegration:
    """Test integration across different service types"""
    
    def test_service_container_with_security_validation(self, integration_container, temp_project_for_security):
        """Test integrating service container with security validation"""
        # Register security validator as a service
        integration_container.register_singleton(
            SecurityValidator,
            SecurityValidator
        )
        
        # Resolve and use security validator
        validator = integration_container.resolve(SecurityValidator)
        assert isinstance(validator, SecurityValidator)
        
        # Use validator to scan file  
        issues = validator.scan_file(str(temp_project_for_security / "test_service.py"))
        
        # Should work as expected
        assert len(issues) > 0
        
    def test_concurrent_service_access(self, integration_container):
        """Test concurrent access to services"""
        import threading
        import time
        
        # Register service
        integration_container.register_singleton(
            MockIntegrationService,
            MockIntegrationService
        )
        
        results = []
        
        def access_service():
            service = integration_container.resolve(MockIntegrationService)
            service.initialize({})
            health = service.health_check()
            results.append(health)
            
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=access_service)
            threads.append(thread)
            
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
            
        # Wait for completion
        for thread in threads:
            thread.join()
        end_time = time.time()
        
        # All should succeed
        assert len(results) == 10
        assert all(results)
        
        # Should complete reasonably quickly
        total_time = end_time - start_time
        assert total_time < 2.0
        
    def test_service_cleanup_integration(self, integration_container):
        """Test service cleanup integration"""
        # Register multiple services
        integration_container.register_singleton(MockIntegrationService, MockIntegrationService)
        
        # Resolve and initialize service
        service = integration_container.resolve(MockIntegrationService)
        service.initialize({})
        
        assert service._initialized
        
        # Cleanup service
        cleanup_success = service.cleanup()
        
        assert cleanup_success
        assert not service._initialized
        
        # Clear container
        integration_container.cleanup()
        
        # Container should be empty
        assert len(integration_container._services) == 0
        assert len(integration_container._singletons) == 0


class TestFullSystemIntegration:
    """Test full system integration scenarios"""
    
    def test_complete_service_ecosystem(self, integration_container, temp_project_for_security):
        """Test complete service ecosystem working together"""
        # Register services
        integration_container.register_singleton(MockIntegrationService, MockIntegrationService)
        integration_container.register_singleton(SecurityValidator, SecurityValidator)
        
        # Resolve all services
        service = integration_container.resolve(MockIntegrationService)
        security_validator = integration_container.resolve(SecurityValidator)
        
        # Initialize service
        service.initialize({"name": "test"})
        
        # Test service works
        assert service.health_check()
        
        # Use security validator
        issues = security_validator.scan_file(str(temp_project_for_security / "test_service.py"))
        assert len(issues) > 0
        
        # Get service info
        info = service.get_service_info()
        assert info["initialized"]
        
        # Cleanup service
        cleanup_success = service.cleanup()
        assert cleanup_success
        
    def test_performance_under_load(self, integration_container):
        """Test system performance under load"""
        import time
        import threading
        
        # Register multiple services
        for i in range(3):
            class_name = f"TestService{i}"
            service_class = type(class_name, (MockIntegrationService,), {})
            integration_container.register_singleton(service_class, service_class)
        
        results = []
        
        def load_test():
            # Access all services
            for i in range(3):
                class_name = f"TestService{i}"
                service_class = type(class_name, (MockIntegrationService,), {})
                service = integration_container.resolve(service_class)
                service.initialize({f"service": i})
                health = service.health_check()
                results.append(health)
        
        # Run load test with multiple threads
        threads = []
        start_time = time.time()
        
        for _ in range(5):
            thread = threading.Thread(target=load_test)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
            
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should handle load well
        assert len(results) == 15  # 5 threads * 3 services each
        assert all(results)  # All operations should succeed
        assert total_time < 3.0  # Should complete within reasonable time