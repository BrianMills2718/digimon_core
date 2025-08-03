"""
Testing Infrastructure Package

Provides comprehensive testing infrastructure with dependency injection support,
mock service factories, and integration testing capabilities.
"""

from .base_test import BaseTest, AsyncBaseTest, TDDTestBase
from .mock_factory import MockServiceFactory
from .fixtures import ServiceFixtures
from .integration_test import IntegrationTestBase
from .performance_test import PerformanceTestBase
from .test_runner import TestExecutionRunner, TestFrameworkAutomation
from .config import get_testing_config, TestingConfig

__all__ = [
    "BaseTest",
    "AsyncBaseTest", 
    "TDDTestBase",
    "MockServiceFactory",
    "ServiceFixtures",
    "IntegrationTestBase",
    "PerformanceTestBase",
    "TestExecutionRunner",
    "TestFrameworkAutomation",
    "get_testing_config",
    "TestingConfig"
]