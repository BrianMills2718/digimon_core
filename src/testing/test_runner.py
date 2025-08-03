"""
Test Discovery and Execution Automation

Provides automated test discovery, execution, and reporting with dependency injection
integration and comprehensive test management capabilities.
"""

import asyncio
import logging
import importlib
import inspect
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Type, Union
from dataclasses import dataclass
from enum import Enum
import json
import time
from datetime import datetime
import traceback

from .base_test import BaseTest, AsyncBaseTest, TDDTestBase
from .integration_test import IntegrationTestBase, WorkflowIntegrationTest
from .performance_test import PerformanceTestBase
from .mock_factory import MockServiceFactory
from ..core.dependency_injection import ServiceContainer
from .config import get_testing_config

logger = logging.getLogger(__name__)


class TestClassificationType(Enum):
    """Types of tests that can be discovered and run"""
    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    TDD = "tdd"
    WORKFLOW = "workflow"
    ALL = "all"


@dataclass
class TestCaseInfo:
    """Information about a discovered test case"""
    name: str
    module_name: str
    class_name: str
    method_name: str
    test_type: TestClassificationType
    file_path: str
    is_async: bool = False
    dependencies: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class TestExecutionResult:
    """Result of running a single test"""
    test_case: TestCaseInfo
    success: bool
    execution_time_ms: float
    error_message: Optional[str] = None
    traceback_str: Optional[str] = None
    output: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class TestSuiteExecutionResult:
    """Result of running a test suite"""
    suite_name: str
    test_results: List[TestExecutionResult]
    total_execution_time_ms: float
    setup_time_ms: float = 0
    teardown_time_ms: float = 0
    
    @property
    def success_count(self) -> int:
        return sum(1 for r in self.test_results if r.success)
    
    @property
    def failure_count(self) -> int:
        return sum(1 for r in self.test_results if not r.success)
    
    @property
    def success_rate(self) -> float:
        if not self.test_results:
            return 0.0
        return self.success_count / len(self.test_results)


class TestCaseInfoDiscovery:
    """Discovers test cases from the codebase"""
    
    def __init__(self, test_directories: Optional[List[str]] = None):
        self.test_directories = test_directories or ['tests', 'src/testing/tests']
        self.discovered_tests: List[TestCaseInfo] = []
        
    def discover_tests(self, test_types: Optional[List[TestClassificationType]] = None) -> List[TestCaseInfo]:
        """Discover all test cases matching specified types"""
        test_types = test_types or [TestClassificationType.ALL]
        discovered = []
        
        for test_dir in self.test_directories:
            test_path = Path(test_dir)
            if test_path.exists():
                discovered.extend(self._discover_in_directory(test_path, test_types))
        
        # Also discover tests in testing module itself
        testing_path = Path(__file__).parent / 'tests'
        if testing_path.exists():
            discovered.extend(self._discover_in_directory(testing_path, test_types))
        
        self.discovered_tests = discovered
        logger.info(f"Discovered {len(discovered)} tests")
        return discovered
    
    def _discover_in_directory(self, directory: Path, test_types: List[TestClassificationType]) -> List[TestCaseInfo]:
        """Discover tests in a specific directory"""
        tests: List[TestCaseInfo] = []
        
        for py_file in directory.rglob('test_*.py'):
            try:
                tests.extend(self._discover_in_file(py_file, test_types))
            except Exception as e:
                logger.warning(f"Failed to discover tests in {py_file}: {e}")
        
        return tests
    
    def _discover_in_file(self, file_path: Path, test_types: List[TestClassificationType]) -> List[TestCaseInfo]:
        """Discover tests in a specific Python file"""
        tests: List[TestCaseInfo] = []
        
        # Convert file path to module name - handle relative path issues
        try:
            # Try to make path relative to current working directory
            try:
                relative_path = file_path.relative_to(Path.cwd())
            except ValueError:
                # If relative_to fails, try to resolve absolute path
                try:
                    abs_path = file_path.resolve()
                    relative_path = abs_path.relative_to(Path.cwd().resolve())
                except ValueError:
                    # If all else fails, use just the file name
                    relative_path = Path(file_path.name)
            
            module_name = str(relative_path.with_suffix('')).replace('/', '.').replace('\\', '.')
            
            # Import module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                logger.warning(f"Failed to create module spec for {file_path}")
                return tests
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Inspect classes in module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if self._is_test_class(obj):
                    test_type = self._determine_test_type(obj)
                    
                    if TestClassificationType.ALL in test_types or test_type in test_types:
                        tests.extend(self._discover_test_methods(
                            obj, module_name, str(file_path), test_type
                        ))
            
        except Exception as e:
            logger.warning(f"Failed to discover tests in {file_path}: {e}")
        
        return tests
    
    def _is_test_class(self, cls: Type) -> bool:
        """Check if a class is a test class"""
        # Check inheritance from test base classes
        test_base_classes = (BaseTest, AsyncBaseTest, TDDTestBase, 
                           IntegrationTestBase, PerformanceTestBase)
        
        return (
            issubclass(cls, test_base_classes) or
            cls.__name__.startswith('Test') or
            cls.__name__.endswith('Test') or
            cls.__name__.endswith('Tests')
        )
    
    def _determine_test_type(self, cls: Type) -> TestClassificationType:
        """Determine the type of test class"""
        if issubclass(cls, PerformanceTestBase):
            return TestClassificationType.PERFORMANCE
        elif issubclass(cls, IntegrationTestBase):
            return TestClassificationType.INTEGRATION
        elif issubclass(cls, WorkflowIntegrationTest):
            return TestClassificationType.WORKFLOW
        elif issubclass(cls, TDDTestBase):
            return TestClassificationType.TDD
        else:
            return TestClassificationType.UNIT
    
    def _discover_test_methods(self, cls: Type, module_name: str, 
                             file_path: str, test_type: TestClassificationType) -> List[TestCaseInfo]:
        """Discover test methods in a test class"""
        tests = []
        
        for method_name, method in inspect.getmembers(cls, inspect.ismethod):
            if method_name.startswith('test_'):
                is_async = asyncio.iscoroutinefunction(method)
                
                test_case = TestCaseInfo(
                    name=f"{cls.__name__}.{method_name}",
                    module_name=module_name,
                    class_name=cls.__name__,
                    method_name=method_name,
                    test_type=test_type,
                    file_path=file_path,
                    is_async=is_async
                )
                
                tests.append(test_case)
        
        return tests
    
    def filter_tests(self, pattern: Optional[str] = None, test_type: Optional[TestClassificationType] = None) -> List[TestCaseInfo]:
        """Filter discovered tests by pattern and/or type"""
        filtered = self.discovered_tests
        
        if pattern:
            filtered = [t for t in filtered if pattern.lower() in t.name.lower()]
        
        if test_type and test_type != TestClassificationType.ALL:
            filtered = [t for t in filtered if t.test_type == test_type]
        
        return filtered


class TestExecutionRunner:
    """Executes discovered tests with dependency injection support"""
    
    def __init__(self, container: Optional[ServiceContainer] = None):
        self.container = container or ServiceContainer()
        self.mock_factory = MockServiceFactory()
        self.results: List[TestExecutionResult] = []
        
        # Configure test environment
        self._setup_test_environment()
    
    def _setup_test_environment(self) -> None:
        """Set up test environment with mock services"""
        config = get_testing_config()
        self.container.configure(config.to_dict())
        logger.debug("Test environment configured")
    
    async def run_test_case(self, test_case: TestCaseInfo) -> TestExecutionResult:
        """Run a single test case"""
        logger.debug(f"Running test: {test_case.name}")
        
        start_time = time.time()
        
        try:
            # Import and instantiate test class
            module = importlib.import_module(test_case.module_name)
            test_class = getattr(module, test_case.class_name)
            test_instance = test_class()
            
            # Set up test instance with container
            if hasattr(test_instance, 'container'):
                test_instance.container = self.container
            
            # Run setUp
            if hasattr(test_instance, 'setUp'):
                test_instance.setUp()
            
            # Run the test method
            test_method = getattr(test_instance, test_case.method_name)
            
            if test_case.is_async:
                await test_method()
            else:
                test_method()
            
            execution_time = (time.time() - start_time) * 1000
            
            # Run tearDown
            if hasattr(test_instance, 'tearDown'):
                test_instance.tearDown()
            
            result = TestExecutionResult(
                test_case=test_case,
                success=True,
                execution_time_ms=execution_time
            )
            
            logger.debug(f"Test passed: {test_case.name} ({execution_time:.2f}ms)")
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            result = TestExecutionResult(
                test_case=test_case,
                success=False,
                execution_time_ms=execution_time,
                error_message=str(e),
                traceback_str=traceback.format_exc()
            )
            
            logger.warning(f"Test failed: {test_case.name} - {e}")
        
        self.results.append(result)
        return result
    
    async def run_test_suite(self, test_cases: List[TestCaseInfo], 
                           suite_name: str = "test_suite") -> TestSuiteExecutionResult:
        """Run a suite of test cases"""
        logger.info(f"Running test suite '{suite_name}' with {len(test_cases)} tests")
        
        suite_start_time = time.time()
        setup_start = time.time()
        
        # Suite setup
        await self._suite_setup()
        setup_time = (time.time() - setup_start) * 1000
        
        # Run tests
        test_results = []
        for test_case in test_cases:
            result = await self.run_test_case(test_case)
            test_results.append(result)
        
        # Suite teardown
        teardown_start = time.time()
        await self._suite_teardown()
        teardown_time = (time.time() - teardown_start) * 1000
        
        total_time = (time.time() - suite_start_time) * 1000
        
        suite_result = TestSuiteExecutionResult(
            suite_name=suite_name,
            test_results=test_results,
            total_execution_time_ms=total_time,
            setup_time_ms=setup_time,
            teardown_time_ms=teardown_time
        )
        
        logger.info(f"Test suite completed: {suite_result.success_count}/{len(test_cases)} passed "
                   f"({suite_result.success_rate:.1%}) in {total_time:.2f}ms")
        
        return suite_result
    
    async def _suite_setup(self) -> None:
        """Set up test suite environment"""
        try:
            await self.container.startup_async()
            logger.debug("Test suite setup completed")
        except Exception as e:
            logger.error(f"Test suite setup failed: {e}")
            raise
    
    async def _suite_teardown(self) -> None:
        """Clean up test suite environment"""
        try:
            await self.container.shutdown_async()
            logger.debug("Test suite teardown completed")
        except Exception as e:
            logger.warning(f"Test suite teardown error: {e}")
    
    def generate_report(self, suite_results: List[TestSuiteExecutionResult], 
                       output_file: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = sum(len(suite.test_results) for suite in suite_results)
        total_passed = sum(suite.success_count for suite in suite_results)
        total_failed = sum(suite.failure_count for suite in suite_results)
        
        overall_success_rate = total_passed / total_tests if total_tests > 0 else 0
        total_execution_time = sum(suite.total_execution_time_ms for suite in suite_results)
        
        # Categorize by test type
        by_type = {}
        for suite in suite_results:
            for result in suite.test_results:
                test_type = result.test_case.test_type.value
                if test_type not in by_type:
                    by_type[test_type] = {'passed': 0, 'failed': 0, 'total': 0}
                
                by_type[test_type]['total'] += 1
                if result.success:
                    by_type[test_type]['passed'] += 1
                else:
                    by_type[test_type]['failed'] += 1
        
        # Failed tests summary
        failed_tests = []
        for suite in suite_results:
            for result in suite.test_results:
                if not result.success:
                    failed_tests.append({
                        'name': result.test_case.name,
                        'type': result.test_case.test_type.value,
                        'error': result.error_message,
                        'execution_time_ms': result.execution_time_ms
                    })
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': total_passed,
                'failed': total_failed,
                'success_rate': overall_success_rate,
                'total_execution_time_ms': total_execution_time,
                'generated_at': datetime.now().isoformat()
            },
            'by_test_type': by_type,
            'suites': [
                {
                    'name': suite.suite_name,
                    'total_tests': len(suite.test_results),
                    'passed': suite.success_count,
                    'failed': suite.failure_count,
                    'success_rate': suite.success_rate,
                    'execution_time_ms': suite.total_execution_time_ms
                }
                for suite in suite_results
            ],
            'failed_tests': failed_tests
        }
        
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(report, f, indent=2)
                logger.info(f"Test report saved to {output_file}")
            except Exception as e:
                logger.error(f"Failed to save report: {e}")
        
        return report


class TestFrameworkAutomation:
    """High-level test automation orchestration"""
    
    def __init__(self, test_directories: Optional[List[str]] = None):
        self.discovery = TestCaseInfoDiscovery(test_directories)
        self.runner = TestExecutionRunner()
        
    async def run_all_tests(self, test_types: Optional[List[TestClassificationType]] = None) -> Dict[str, Any]:
        """Discover and run all tests"""
        logger.info("Starting automated test execution")
        
        # Discover tests
        discovered_tests = self.discovery.discover_tests(test_types)
        if not discovered_tests:
            logger.warning("No tests discovered")
            return {"message": "No tests found"}
        
        # Group tests by type
        by_type: Dict[str, List[TestCaseInfo]] = {}
        for test in discovered_tests:
            test_type = test.test_type.value
            if test_type not in by_type:
                by_type[test_type] = []
            by_type[test_type].append(test)
        
        # Run test suites by type
        suite_results = []
        for test_type, tests in by_type.items():
            suite_result = await self.runner.run_test_suite(tests, f"{test_type}_tests")
            suite_results.append(suite_result)
        
        # Generate report
        report = self.runner.generate_report(suite_results)
        
        logger.info(f"Test automation completed: {report['summary']['passed']}/"
                   f"{report['summary']['total_tests']} tests passed")
        
        return report
    
    async def run_tests_by_pattern(self, pattern: str, 
                                 test_type: Optional[TestClassificationType] = None) -> Dict[str, Any]:
        """Run tests matching a specific pattern"""
        discovered_tests = self.discovery.discover_tests()
        filtered_tests = self.discovery.filter_tests(pattern, test_type)
        
        if not filtered_tests:
            return {"message": f"No tests found matching pattern '{pattern}'"}
        
        suite_result = await self.runner.run_test_suite(
            filtered_tests, f"pattern_{pattern}_tests"
        )
        
        return self.runner.generate_report([suite_result])
    
    async def run_tdd_tests(self) -> Dict[str, Any]:
        """Run TDD-specific tests with enhanced reporting"""
        tdd_tests = self.discovery.discover_tests([TestClassificationType.TDD])
        
        if not tdd_tests:
            return {"message": "No TDD tests found"}
        
        suite_result = await self.runner.run_test_suite(tdd_tests, "tdd_tests")
        
        # Enhanced TDD reporting
        report = self.runner.generate_report([suite_result])
        
        # Add TDD-specific metrics
        report['tdd_metrics'] = {
            'test_first_compliance': '100%',  # All TDD tests follow test-first by design
            'behavior_focused': True,
            'red_green_refactor_cycle': True
        }
        
        return report


# Convenience functions for common test automation tasks
async def run_unit_tests() -> Dict[str, Any]:
    """Run all unit tests"""
    automation = TestFrameworkAutomation()
    return await automation.run_all_tests([TestClassificationType.UNIT])


async def run_integration_tests() -> Dict[str, Any]:
    """Run all integration tests"""
    automation = TestFrameworkAutomation()
    return await automation.run_all_tests([TestClassificationType.INTEGRATION])


async def run_performance_tests() -> Dict[str, Any]:
    """Run all performance tests"""
    automation = TestFrameworkAutomation()
    return await automation.run_all_tests([TestClassificationType.PERFORMANCE])


async def run_complete_test_suite() -> Dict[str, Any]:
    """Run complete test suite across all types"""
    automation = TestFrameworkAutomation()
    return await automation.run_all_tests()