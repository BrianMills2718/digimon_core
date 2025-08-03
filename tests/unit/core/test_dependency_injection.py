"""
Unit tests for dependency injection system

Tests the ServiceContainer implementation with service registration,
resolution, and lifecycle management.
"""

import pytest
import asyncio
from typing import Any, Dict

from src.core.dependency_injection import (
    ServiceContainer,
    ServiceInterface,
    DependencyInjectionError,
    ServiceLifecycle,
    get_container
)


# Test service classes
class MockService(ServiceInterface):
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.initialized = False
        self.name = "mock_service"
        
    async def startup(self) -> None:
        self.initialized = True
        
    async def shutdown(self) -> None:
        self.initialized = False
        
    async def health_check(self) -> Any:
        return {"status": "healthy" if self.initialized else "stopped"}


class SimpleService:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.value = "simple"


@pytest.fixture
def container():
    """Create fresh DI container for each test"""
    return ServiceContainer()


class TestServiceContainer:
    """Test dependency injection container functionality"""
    
    def test_container_initialization(self, container):
        """Test container initializes correctly"""
        assert container._services == {}
        assert container._instances == {}
        assert container._resolving == set()
        assert container._configuration == {}
        assert not container._started
        
    def test_register_service(self, container):
        """Test registering a service"""
        result = container.register("test_service", MockService)
        
        # Should return container for chaining
        assert result is container
        assert "test_service" in container._services
        assert container._services["test_service"].name == "test_service"
        assert container._services["test_service"].implementation == MockService
        
    def test_register_with_lifecycle(self, container):
        """Test registering service with specific lifecycle"""
        container.register(
            "transient_service", 
            SimpleService, 
            lifecycle=ServiceLifecycle.TRANSIENT
        )
        
        registration = container._services["transient_service"]
        assert registration.lifecycle == ServiceLifecycle.TRANSIENT
        
    def test_configure_container(self, container):
        """Test configuring the container"""
        config = {"database_url": "test://localhost", "debug": True}
        result = container.configure(config)
        
        # Should return container for chaining
        assert result is container
        assert container._configuration == config
        
    def test_get_singleton_service(self, container):
        """Test getting singleton service returns same instance"""
        container.register("singleton_service", SimpleService)
        
        instance1 = container.get("singleton_service")
        instance2 = container.get("singleton_service")
        
        assert isinstance(instance1, SimpleService)
        assert instance1 is instance2  # Same instance
        
    def test_get_transient_service(self, container):
        """Test getting transient service returns new instances"""
        container.register(
            "transient_service", 
            SimpleService, 
            lifecycle=ServiceLifecycle.TRANSIENT
        )
        
        instance1 = container.get("transient_service")
        instance2 = container.get("transient_service")
        
        assert isinstance(instance1, SimpleService)
        assert isinstance(instance2, SimpleService)
        assert instance1 is not instance2  # Different instances
        
    def test_get_nonexistent_service(self, container):
        """Test getting non-existent service raises error"""
        with pytest.raises(DependencyInjectionError) as exc_info:
            container.get("nonexistent_service")
            
        assert "Service 'nonexistent_service' is not registered" in str(exc_info.value)
        
    def test_circular_dependency_detection(self, container):
        """Test circular dependency detection"""
        # Simulate circular dependency by manually adding to resolving set
        container.register("circular_service", SimpleService)
        container._resolving.add("circular_service")
        
        with pytest.raises(DependencyInjectionError) as exc_info:
            container.get("circular_service")
            
        assert "Circular dependency detected" in str(exc_info.value)
        
    @pytest.mark.asyncio
    async def test_get_async_service(self, container):
        """Test getting service asynchronously"""
        container.register("async_service", MockService)
        
        instance = await container.get_async("async_service")
        
        assert isinstance(instance, MockService)
        
    @pytest.mark.asyncio
    async def test_get_async_nonexistent_service(self, container):
        """Test getting non-existent service async raises error"""
        with pytest.raises(DependencyInjectionError) as exc_info:
            await container.get_async("nonexistent_async_service")
            
        assert "Service 'nonexistent_async_service' is not registered" in str(exc_info.value)


class TestGlobalContainer:
    """Test global container functions"""
    
    def test_get_container_function(self):
        """Test global container function works"""
        container = get_container()
        
        assert isinstance(container, ServiceContainer)
        
        # Should return same instance (singleton)
        container2 = get_container()
        assert container is container2


class TestServiceInterface:
    """Test ServiceInterface base class"""
    
    @pytest.mark.asyncio
    async def test_service_interface_methods(self):
        """Test ServiceInterface base methods"""
        service = ServiceInterface()
        
        # Should not raise exceptions
        await service.startup()
        await service.shutdown()
        
        health = await service.health_check()
        assert health == {"status": "healthy"}


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_service_creation_exception(self, container):
        """Test handling of service creation exceptions"""
        class FailingService:
            def __init__(self):
                raise Exception("Constructor failed")
                
        container.register("failing_service", FailingService)
        
        with pytest.raises(DependencyInjectionError):
            container.get("failing_service")


class TestRegistrationOverwrite:
    """Test service registration overwrite scenarios"""
    
    def test_register_overwrite_warning(self, container):
        """Test registering same service twice logs warning"""
        container.register("duplicate_service", SimpleService)
        
        # Should not raise error, just log warning
        container.register("duplicate_service", MockService)
        
        # Should have the new service
        registration = container._services["duplicate_service"]
        assert registration.implementation == MockService