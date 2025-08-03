"""
Base Test Classes with Dependency Injection Support

Provides foundation classes for all tests with built-in dependency injection,
service lifecycle management, and standardized test patterns.
"""

import asyncio
import os
import unittest
import pytest
from typing import Dict, Any, Optional, List, Callable, Union, Awaitable
from unittest.mock import Mock, MagicMock
import logging

from ..core.dependency_injection import ServiceContainer, ServiceLifecycle, get_container
from ..core.interfaces.service_interfaces import (
    ServiceInterface, ServiceResponse,
    IdentityServiceInterface,
    ProvenanceServiceInterface,
    QualityServiceInterface,
    Neo4jServiceInterface
)
from .mock_factory import MockServiceFactory
from .config import get_testing_config

logger = logging.getLogger(__name__)


class BaseTest(unittest.TestCase):
    """
    Base test class with dependency injection support for synchronous tests
    """
    
    def setUp(self):
        """Initialize test container and common fixtures"""
        self.container = ServiceContainer()
        self.mock_factory = MockServiceFactory()
        self.test_config = self._get_test_config()
        
        # Configure container for testing
        self.container.configure(self.test_config)
        
        # Set up logging for tests
        logging.basicConfig(level=logging.DEBUG)
        
        logger.debug(f"BaseTest setup complete for {self.__class__.__name__}")
    
    def tearDown(self):
        """Clean up container and services"""
        if hasattr(self, 'container') and self.container:
            try:
                self.container.shutdown()
                logger.debug("Container shutdown complete")
            except Exception as e:
                logger.warning(f"Error during container shutdown: {e}")
    
    def _get_test_config(self) -> Dict[str, Any]:
        """Get test configuration with safe defaults"""
        config = get_testing_config()
        return config.to_dict()
    
    def register_mock_service(self, name: str, interface_class: Optional[type] = None,
                            **mock_methods: Any) -> Mock:
        """Register a mock service with the container"""
        mock_service = self.mock_factory.create_mock_service(
            interface_class or ServiceInterface,
            **mock_methods
        )
        
        self.container.register(
            name,
            mock_service,
            lifecycle=ServiceLifecycle.SINGLETON
        )
        
        logger.debug(f"Registered mock service '{name}' with methods: {list(mock_methods.keys())}")
        return mock_service
    
    def register_real_service(self, name: str, service_class: type, 
                            dependencies: Optional[List[str]] = None, **kwargs: Any) -> None:
        """Register a real service with the container"""
        self.container.register(
            name,
            service_class,
            lifecycle=ServiceLifecycle.SINGLETON,
            dependencies=dependencies or [],
            **kwargs
        )
        
        logger.debug(f"Registered real service '{name}' with dependencies: {dependencies}")
    
    def get_service(self, name: str) -> Union[IdentityServiceInterface, ProvenanceServiceInterface, QualityServiceInterface, Neo4jServiceInterface, ServiceInterface]:
        """Get a service from the container"""
        return self.container.get(name)
    
    def assert_service_response(self, response: ServiceResponse, 
                              success: bool = True, 
                              contains_data: bool = True):
        """Assert standard service response format"""
        self.assertIsInstance(response, ServiceResponse)
        self.assertEqual(response.success, success)
        
        if success and contains_data:
            self.assertIsNotNone(response.data)
        elif not success:
            self.assertIsNotNone(response.error)
    
    def create_test_data(self, data_type: str = "mention") -> Dict[str, Any]:
        """Create standard test data for different types"""
        if data_type == "mention":
            return {
                "surface_form": "Test Entity",
                "start_pos": 0,
                "end_pos": 11,
                "source_ref": "test_document",
                "confidence": 0.9
            }
        elif data_type == "entity":
            return {
                "entity_id": "test_entity_123",
                "canonical_name": "Test Entity",
                "entity_type": "PERSON",
                "confidence": 0.9
            }
        elif data_type == "relationship":
            return {
                "source_id": "entity_1",
                "target_id": "entity_2", 
                "relationship_type": "RELATED_TO",
                "confidence": 0.8
            }
        else:
            raise ValueError(f"Unknown test data type: {data_type}")


class AsyncBaseTest(BaseTest):
    """
    Base test class with dependency injection support for async tests
    """
    
    def setUp(self):
        """Initialize async test environment"""
        super().setUp()
        
        # Create event loop for async operations
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        logger.debug(f"AsyncBaseTest setup complete with event loop")
    
    def tearDown(self):
        """Clean up async resources"""
        if hasattr(self, 'container') and self.container:
            try:
                # Use event loop to shutdown async services
                self.loop.run_until_complete(self.container.shutdown_async())
                logger.debug("Async container shutdown complete")
            except Exception as e:
                logger.warning(f"Error during async container shutdown: {e}")
        
        # Clean up event loop
        if hasattr(self, 'loop') and self.loop:
            try:
                self.loop.close()
                logger.debug("Event loop closed")
            except Exception as e:
                logger.warning(f"Error closing event loop: {e}")
        
        super().tearDown()
    
    async def async_get_service(self, name: str) -> Union[IdentityServiceInterface, ProvenanceServiceInterface, QualityServiceInterface, Neo4jServiceInterface, ServiceInterface]:
        """Get a service from the container asynchronously"""
        return await self.container.get_async(name)
    
    async def start_services(self):
        """Start all registered services asynchronously"""
        await self.container.startup_async()
        logger.debug("All services started successfully")
    
    async def stop_services(self):
        """Stop all services asynchronously"""
        await self.container.shutdown_async()
        logger.debug("All services stopped successfully")
    
    def run_async_test(self, coro: Awaitable[Any]) -> Any:
        """Helper to run async test methods"""
        return self.loop.run_until_complete(coro)
    
    async def assert_async_service_response(self, coro: Any, success: bool = True,
                                          contains_data: bool = True) -> ServiceResponse:
        """Assert async service response format"""
        response = await coro
        self.assert_service_response(response, success, contains_data)
        return response


class TDDTestBase(AsyncBaseTest):
    """
    Base class specifically for TDD (Test-Driven Development) patterns
    
    Enforces TDD best practices:
    - Tests define behavior first
    - Clear test structure (Arrange, Act, Assert)
    - Behavior-focused testing over implementation testing
    """
    
    def setUp(self):
        """Initialize TDD test environment"""
        super().setUp()
        
        # TDD-specific setup
        self.test_results = []
        self.behavior_under_test = None
        
        logger.debug("TDD test environment initialized")
    
    def define_behavior(self, description: str) -> None:
        """Define the behavior being tested (TDD practice)"""
        self.behavior_under_test = description
        logger.info(f"Testing behavior: {description}")
    
    def arrange(self, **fixtures) -> Dict[str, Any]:
        """Arrange phase of TDD test (setup test data and conditions)"""
        arranged_data = {}
        
        for name, value in fixtures.items():
            arranged_data[name] = value
            logger.debug(f"Arranged fixture '{name}': {type(value).__name__}")
        
        return arranged_data
    
    def act(self, action_description: Optional[str] = None) -> 'TDDTestBase':
        """Act phase indicator (execute the code under test)"""
        if action_description:
            logger.debug(f"Acting: {action_description}")
        return self  # Enable chaining
    
    def assert_behavior(self, condition: bool, message: str) -> None:
        """Assert behavior matches expectation (TDD focus on behavior)"""
        self.assertTrue(condition, f"Behavior assertion failed: {message}")
        
        if self.behavior_under_test:
            self.test_results.append(f"✅ {self.behavior_under_test}: {message}")
        
        logger.debug(f"Behavior verified: {message}")
    
    def assert_behavior_equals(self, actual: Any, expected: Any, context: str = "") -> None:
        """Assert behavior produces expected result"""
        self.assertEqual(actual, expected, 
                        f"Behavior assertion failed {context}: expected {expected}, got {actual}")
        
        if self.behavior_under_test:
            self.test_results.append(f"✅ {self.behavior_under_test} {context}: Got expected result")
    
    def assert_error_behavior(self, exception_type: type, context: str = "") -> Any:
        """Assert that specific error behavior occurs (context manager)"""
        return self.assertRaises(exception_type)
    
    def get_test_summary(self) -> List[str]:
        """Get summary of test results for TDD feedback"""
        return self.test_results.copy()


# Pytest fixtures for dependency injection testing
@pytest.fixture
def test_container():
    """Pytest fixture providing a test container"""
    container = ServiceContainer()
    config = get_testing_config()
    container.configure(config.to_dict())
    
    yield container
    
    # Cleanup
    try:
        container.shutdown()
    except Exception as e:
        logger.warning(f"Error during container cleanup: {e}")


@pytest.fixture
def mock_factory():
    """Pytest fixture providing a mock service factory"""
    return MockServiceFactory()


@pytest.fixture
async def async_test_container():
    """Pytest fixture providing an async test container"""
    container = ServiceContainer()
    config = get_testing_config()
    container.configure(config.to_dict())
    
    yield container
    
    # Async cleanup
    try:
        await container.shutdown_async()
    except Exception as e:
        logger.warning(f"Error during async container cleanup: {e}")