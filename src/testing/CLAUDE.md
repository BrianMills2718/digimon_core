# Testing Module - CLAUDE.md

## Overview
The `src/testing/` directory contains **integration testing framework** that provides comprehensive testing for the GraphRAG system, focusing on cross-component compatibility and preventing integration failures. This module ensures system reliability and component interoperability.

## Testing Architecture

### Integration Testing Pattern
The testing module follows a comprehensive integration testing pattern:
- **IntegrationTester**: Main testing framework for system integration
- **Test Suites**: Organized test collections with results tracking
- **Cross-Component Testing**: Test interactions between components
- **Performance Baseline**: Establish performance benchmarks

### Test Result Pattern
All tests follow a structured result pattern:
- **IntegrationTestResult**: Individual test results with detailed information
- **IntegrationTestSuite**: Collection of test results with summary statistics
- **Status Tracking**: Track pass, fail, skip status for each test
- **Error Details**: Comprehensive error information and debugging data

## Individual Component Patterns

### IntegrationTester (`integration_test_framework.py`)
**Purpose**: Main integration testing framework for GraphRAG system

**Key Patterns**:
- **Comprehensive Testing**: Test all system components and interactions
- **Environment Management**: Setup and teardown test environments
- **Result Collection**: Collect and organize test results
- **Error Handling**: Handle test failures gracefully

**Usage**:
```python
from src.testing.integration_test_framework import IntegrationTester, run_integration_tests

# Run complete integration test suite
suite = run_integration_tests(test_data_dir="examples/pdfs")

# Or use the tester directly
tester = IntegrationTester(test_data_dir="examples/pdfs")
tester.setup()
suite = tester.run_full_integration_suite()
tester.teardown()

# Generate test report
report = tester.generate_report(suite)
print(report)
```

**Core Components**:

#### Test Environment Management
```python
def setup(self):
    """Setup test environment"""

def teardown(self):
    """Cleanup test environment"""
```

**Environment Features**:
- **Temp Directory**: Create temporary directories for test outputs
- **Phase Initialization**: Initialize phase adapters for testing
- **Resource Cleanup**: Clean up test resources after completion
- **Status Reporting**: Report setup and teardown status

#### Full Integration Suite
```python
def run_full_integration_suite(self) -> IntegrationTestSuite:
    """Run the complete integration test suite"""
```

**Suite Features**:
- **Test Categories**: Organize tests into logical categories
- **Result Collection**: Collect results from all test categories
- **Summary Statistics**: Calculate pass/fail/skip statistics
- **Error Handling**: Handle category-level errors gracefully

**Test Categories**:
- **Phase Interface Compatibility**: Test phase interface compliance
- **Cross-Phase Data Flow**: Test data flow between phases
- **UI Integration**: Test UI component integration
- **Error Handling**: Test error handling and recovery
- **Performance Baseline**: Test performance characteristics
- **Service Dependencies**: Test service dependency management

#### Phase Interface Testing
```python
def _test_phase_interface_compatibility(self) -> List[IntegrationTestResult]:
    """Test that all phases implement the interface correctly"""
```

**Interface Testing Features**:
- **Phase Discovery**: Discover all available phases
- **Method Validation**: Validate required interface methods
- **Capability Testing**: Test phase capability reporting
- **Input Validation**: Test input validation functionality

**Required Methods**:
- **execute**: Execute phase processing
- **get_capabilities**: Get phase capabilities
- **validate_input**: Validate input parameters
- **get_phase_info**: Get phase information

#### Cross-Phase Data Flow Testing
```python
def _test_cross_phase_data_flow(self) -> List[IntegrationTestResult]:
    """Test data flow between different phases"""
```

**Data Flow Features**:
- **Phase Chaining**: Test chaining multiple phases together
- **Data Consistency**: Test data consistency across phases
- **Result Propagation**: Test result propagation between phases
- **Error Propagation**: Test error handling across phases

#### UI Integration Testing
```python
def _test_ui_integration(self) -> List[IntegrationTestResult]:
    """Test UI component integration"""
```

**UI Testing Features**:
- **Phase Manager Integration**: Test UI phase manager functionality
- **Document Processing**: Test document processing through UI
- **Result Conversion**: Test result conversion for UI display
- **Error Display**: Test error handling in UI context

#### Error Handling Testing
```python
def _test_error_handling(self) -> List[IntegrationTestResult]:
    """Test error handling and recovery mechanisms"""
```

**Error Testing Features**:
- **Invalid Input**: Test handling of invalid inputs
- **Service Failures**: Test handling of service failures
- **Resource Exhaustion**: Test handling of resource limits
- **Recovery Mechanisms**: Test system recovery after errors

#### Performance Baseline Testing
```python
def _test_performance_baseline(self) -> List[IntegrationTestResult]:
    """Test performance characteristics and establish baselines"""
```

**Performance Features**:
- **Execution Time**: Measure execution time for operations
- **Memory Usage**: Monitor memory usage during operations
- **Resource Consumption**: Track resource consumption
- **Baseline Establishment**: Establish performance baselines

#### Service Dependencies Testing
```python
def _test_service_dependencies(self) -> List[IntegrationTestResult]:
    """Test service dependency management and connectivity"""
```

**Dependency Features**:
- **Service Connectivity**: Test service connectivity
- **Dependency Resolution**: Test dependency resolution
- **Service Failures**: Test handling of service failures
- **Fallback Mechanisms**: Test fallback mechanisms

### IntegrationTestResult
**Purpose**: Individual test result with detailed information

**Key Patterns**:
- **Structured Results**: Consistent result structure across all tests
- **Error Information**: Comprehensive error information and context
- **Performance Metrics**: Track execution time and performance
- **Test Metadata**: Include test type and classification

**Data Structure**:
```python
@dataclass
class IntegrationTestResult:
    test_name: str
    test_type: str
    status: str  # "pass", "fail", "skip"
    execution_time: float
    details: Dict[str, Any]
    error_message: Optional[str] = None
```

**Result Features**:
- **Test Identification**: Unique test name and type
- **Status Tracking**: Pass, fail, or skip status
- **Performance Tracking**: Execution time measurement
- **Detailed Information**: Additional test details and context
- **Error Details**: Comprehensive error information

### IntegrationTestSuite
**Purpose**: Collection of test results with summary statistics

**Key Patterns**:
- **Result Collection**: Collect and organize test results
- **Summary Statistics**: Calculate pass/fail/skip statistics
- **Timing Information**: Track suite execution timing
- **Report Generation**: Generate comprehensive test reports

**Data Structure**:
```python
@dataclass 
class IntegrationTestSuite:
    suite_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    tests: List[IntegrationTestResult] = None
```

**Suite Features**:
- **Suite Identification**: Unique suite name and timing
- **Result Collection**: Collection of all test results
- **Duration Calculation**: Calculate total suite duration
- **Summary Statistics**: Calculate pass/fail/skip statistics

**Summary Properties**:
```python
@property
def duration(self) -> float:
    """Calculate suite duration in seconds"""

@property
def summary(self) -> Dict[str, int]:
    """Calculate summary statistics"""
```

## Common Commands & Workflows

### Development Commands
```bash
# Run integration tests
python -c "from src.testing.integration_test_framework import run_integration_tests; suite = run_integration_tests(); print(f'Tests: {suite.summary}')"

# Test integration tester
python -c "from src.testing.integration_test_framework import IntegrationTester; tester = IntegrationTester(); print('Integration tester created successfully')"

# Test test result creation
python -c "from src.testing.integration_test_framework import IntegrationTestResult; result = IntegrationTestResult('test', 'unit', 'pass', 1.0, {}); print(f'Test result: {result.status}')"

# Test test suite creation
python -c "from src.testing.integration_test_framework import IntegrationTestSuite; suite = IntegrationTestSuite('test_suite', datetime.now()); print(f'Test suite: {suite.suite_name}')"
```

### Testing Commands
```bash
# Run specific test categories
python -c "from src.testing.integration_test_framework import IntegrationTester; tester = IntegrationTester(); tester.setup(); results = tester._test_phase_interface_compatibility(); print(f'Interface tests: {len(results)}')"

# Test phase interface compatibility
python -c "from src.testing.integration_test_framework import IntegrationTester; tester = IntegrationTester(); tester.setup(); results = tester._test_phase_interface_compatibility(); passed = sum(1 for r in results if r.status == 'pass'); print(f'Passed: {passed}/{len(results)}')"

# Test cross-phase data flow
python -c "from src.testing.integration_test_framework import IntegrationTester; tester = IntegrationTester(); tester.setup(); results = tester._test_cross_phase_data_flow(); print(f'Data flow tests: {len(results)}')"

# Test UI integration
python -c "from src.testing.integration_test_framework import IntegrationTester; tester = IntegrationTester(); tester.setup(); results = tester._test_ui_integration(); print(f'UI integration tests: {len(results)}')"
```

### Debugging Commands
```bash
# Check test environment setup
python -c "from src.testing.integration_test_framework import IntegrationTester; tester = IntegrationTester(); tester.setup(); print(f'Temp directory: {tester.temp_dir}')"

# Test error handling
python -c "from src.testing.integration_test_framework import IntegrationTester; tester = IntegrationTester(); tester.setup(); results = tester._test_error_handling(); print(f'Error handling tests: {len(results)}')"

# Test performance baseline
python -c "from src.testing.integration_test_framework import IntegrationTester; tester = IntegrationTester(); tester.setup(); results = tester._test_performance_baseline(); print(f'Performance tests: {len(results)}')"

# Test service dependencies
python -c "from src.testing.integration_test_framework import IntegrationTester; tester = IntegrationTester(); tester.setup(); results = tester._test_service_dependencies(); print(f'Service dependency tests: {len(results)}')"
```

## Code Style & Conventions

### Testing Design Patterns
- **Comprehensive Coverage**: Test all system components and interactions
- **Environment Isolation**: Isolate test environments from production
- **Result Tracking**: Track detailed results and statistics
- **Error Handling**: Handle test failures gracefully

### Naming Conventions
- **Test Classes**: Use `Tester` suffix for test framework classes
- **Result Classes**: Use `Result` suffix for result classes
- **Suite Classes**: Use `Suite` suffix for test suite classes
- **Method Names**: Use descriptive names for test methods

### Error Handling Patterns
- **Graceful Failures**: Handle test failures without crashing
- **Error Details**: Provide comprehensive error information
- **Recovery Mechanisms**: Implement recovery mechanisms for failures
- **Status Tracking**: Track error status in result objects

### Logging Patterns
- **Test Logging**: Log test execution and results
- **Error Logging**: Log errors with context and debugging information
- **Performance Logging**: Log performance metrics and timing
- **Summary Logging**: Log test suite summaries and statistics

## Integration Points

### Core Integration
- **Phase Interface**: Integration with phase interface system
- **Phase Adapters**: Integration with phase adapters
- **Service Manager**: Integration with service manager
- **Configuration**: Integration with configuration system

### UI Integration
- **UI Phase Manager**: Integration with UI phase manager
- **Document Processing**: Integration with document processing
- **Result Conversion**: Integration with result conversion
- **Error Display**: Integration with error display

### External Dependencies
- **Pathlib**: File path handling
- **Dataclasses**: Structured data models
- **Datetime**: Time tracking and measurement
- **Tempfile**: Temporary file and directory management

## Performance Considerations

### Test Performance
- **Parallel Testing**: Run tests in parallel when possible
- **Test Isolation**: Isolate tests to prevent interference
- **Resource Management**: Manage test resources efficiently
- **Cleanup**: Clean up test resources after completion

### Memory Management
- **Test Data**: Manage test data efficiently
- **Result Storage**: Store test results efficiently
- **Resource Cleanup**: Clean up resources after tests
- **Memory Monitoring**: Monitor memory usage during tests

### Speed Optimization
- **Test Selection**: Select relevant tests for specific scenarios
- **Caching**: Cache test results when appropriate
- **Incremental Testing**: Run incremental tests for faster feedback
- **Parallel Execution**: Execute tests in parallel when possible

## Testing Patterns

### Unit Testing
- **Component Testing**: Test individual components independently
- **Method Testing**: Test individual methods and functions
- **Interface Testing**: Test component interfaces
- **Error Testing**: Test error handling and edge cases

### Integration Testing
- **Cross-Component Testing**: Test interactions between components
- **Data Flow Testing**: Test data flow through the system
- **Service Integration**: Test service integration and dependencies
- **End-to-End Testing**: Test complete workflows

### Performance Testing
- **Baseline Testing**: Establish performance baselines
- **Load Testing**: Test system performance under load
- **Resource Testing**: Test resource consumption and limits
- **Scalability Testing**: Test system scalability

## Troubleshooting

### Common Issues
1. **Test Environment Issues**: Check test environment setup and cleanup
2. **Phase Initialization Issues**: Check phase adapter initialization
3. **Service Dependency Issues**: Check service connectivity and dependencies
4. **Performance Issues**: Check performance baselines and resource usage

### Debug Commands
```bash
# Check test environment
python -c "from src.testing.integration_test_framework import IntegrationTester; tester = IntegrationTester(); tester.setup(); print('Test environment setup successful')"

# Check phase initialization
python -c "from src.core.phase_adapters import initialize_phase_adapters; success = initialize_phase_adapters(); print(f'Phase adapters initialized: {success}')"

# Check available phases
python -c "from src.core.graphrag_phase_interface import get_available_phases; phases = get_available_phases(); print(f'Available phases: {phases}')"

# Test phase interface
python -c "from src.core.graphrag_phase_interface import phase_registry; print(f'Phase registry: {phase_registry}')"
```

## Migration & Upgrades

### Test Migration
- **Test Updates**: Update tests for new components and interfaces
- **Result Migration**: Migrate test result structures
- **Suite Migration**: Migrate test suite structures
- **Framework Migration**: Migrate testing framework

### Component Migration
- **Interface Updates**: Update tests for interface changes
- **Service Updates**: Update tests for service changes
- **UI Updates**: Update tests for UI changes
- **Configuration Updates**: Update tests for configuration changes

### Performance Migration
- **Baseline Updates**: Update performance baselines
- **Metric Updates**: Update performance metrics
- **Threshold Updates**: Update performance thresholds
- **Resource Updates**: Update resource requirements 