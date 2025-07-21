# KGAS Testing Standards

**Purpose**: Define comprehensive testing requirements for KGAS components  
**Last Updated**: 2025-07-21  
**Scope**: All tools, services, and system components

---

## Test Type Definitions

### **Unit Tests** 🧪
**Purpose**: Test individual functions and classes in isolation  
**Characteristics**:
- Use mocks/stubs for external dependencies
- Fast execution (milliseconds to seconds)
- Focus on single function or method behavior
- Test edge cases and error conditions

**File Pattern**: `test_[component]_unit.py`
**Location**: `tests/unit/`

**Example**:
```python
def test_entity_extraction_unit():
    """Unit test with mocked dependencies."""
    mock_nlp = Mock()
    extractor = EntityExtractor(nlp_model=mock_nlp)
    result = extractor.extract(['John Smith'])
    assert result['entities'] is not None
```

### **Integration Tests** 🔗
**Purpose**: Test component interactions without mocks  
**Characteristics**:
- Use real services and dependencies
- Test data flow between components
- Verify service integration (Identity, Provenance, Quality)
- Moderate execution time (seconds to minutes)

**File Pattern**: `test_[component]_integration.py`
**Location**: `tests/integration/`

**Example**:
```python
def test_tool_service_integration():
    """Integration test with real service manager."""
    service_manager = get_service_manager()
    tool = SpacyNER(service_manager)
    result = tool.execute({'text': 'John Smith works at Acme Corp'})
    
    # Verify service integration
    assert 'provenance_id' in result
    assert 'quality' in result
    # Verify actual entity extraction
    assert len(result['entities']) > 0
```

### **Functional Tests** ⚡
**Purpose**: Test complete workflows with real data  
**Characteristics**:
- Use actual sample data (not mocks)
- Test end-to-end functionality
- Verify tool produces expected results
- Can take longer to execute (minutes)

**File Pattern**: `test_[component]_functional.py`
**Location**: `tests/functional/`

**Example**:
```python
def test_pdf_extraction_functional():
    """Functional test with real PDF file."""
    pdf_loader = PDFLoader()
    sample_pdf = 'test_data/sample_academic_paper.pdf'
    
    result = pdf_loader.execute({
        'file_path': sample_pdf,
        'extract_tables': True
    })
    
    assert result['status'] == 'success'
    assert len(result['text']) > 1000  # Reasonable text extraction
    assert result['pages'] > 0
    assert 'execution_time' in result
```

### **End-to-End Tests** 🎯
**Purpose**: Test complete user workflows from UI to results  
**Characteristics**:
- Test full system integration
- Include UI interactions where applicable
- Test realistic user scenarios
- Longest execution time (minutes to hours)

**File Pattern**: `test_[workflow]_e2e.py`
**Location**: `tests/e2e/`

**Example**:
```python
def test_academic_analysis_workflow_e2e():
    """End-to-end test of complete academic analysis."""
    # 1. Document ingestion
    # 2. Entity extraction
    # 3. Relationship extraction
    # 4. Graph construction
    # 5. Analysis and export
    # Verify complete workflow produces academic outputs
```

---

## Testing Requirements by Component Type

### **For All Tools**

#### Required Test Coverage
1. **Unit Tests**: ✅ MANDATORY
   - Input validation testing
   - Error condition handling
   - Core logic without external dependencies

2. **Functional Tests**: ✅ MANDATORY  
   - Real execution with sample data
   - Validation mode testing
   - Performance timing verification

3. **Integration Tests**: ✅ MANDATORY
   - Service integration (Identity, Provenance, Quality)
   - Pipeline orchestrator integration
   - Cross-tool workflow testing

4. **End-to-End Tests**: 📋 RECOMMENDED
   - For critical workflow tools
   - For user-facing functionality

#### Test Implementation Pattern
```python
# tests/unit/test_[tool]_unit.py
class TestToolUnit:
    def test_initialization(self):
        """Test tool can be created."""
        
    def test_input_validation(self):
        """Test input validation logic."""
        
    def test_error_handling(self):
        """Test error conditions."""

# tests/functional/test_[tool]_functional.py  
class TestToolFunctional:
    def test_with_real_data(self):
        """Test with actual sample data."""
        
    def test_validation_mode(self):
        """Test validation mode works."""
        
    def test_performance_acceptable(self):
        """Test execution time is reasonable."""

# tests/integration/test_[tool]_integration.py
class TestToolIntegration:
    def test_service_integration(self):
        """Test integration with core services."""
        
    def test_pipeline_integration(self):
        """Test tool works in pipeline."""
```

### **For Services**

#### Required Test Coverage
1. **Unit Tests**: Test individual service methods
2. **Integration Tests**: Test service interactions
3. **Functional Tests**: Test service workflows
4. **Performance Tests**: Test under load

#### Service-Specific Tests
```python
# Identity Service
def test_entity_resolution_accuracy()
def test_cross_document_linking()
def test_mention_tracking()

# Provenance Service  
def test_operation_tracking()
def test_lineage_reconstruction()
def test_audit_trail_completeness()

# Quality Service
def test_confidence_assessment()
def test_tier_classification()
def test_quality_propagation()
```

### **For System Components**

#### Pipeline Orchestrator Tests
- Workflow execution testing
- State management testing
- Error recovery testing
- Checkpoint/resume testing

#### Database Integration Tests
- Neo4j connection and operations
- SQLite schema validation
- Cross-database transaction testing
- Data consistency verification

---

## Test Data Management

### Test Data Organization
```
test_data/
├── documents/
│   ├── sample_academic_paper.pdf
│   ├── policy_document.docx
│   └── news_article.txt
├── entities/
│   ├── sample_entities.json
│   └── complex_entity_relationships.json
├── graphs/
│   ├── small_test_graph.json
│   └── performance_test_graph.json
└── expected_results/
    ├── t01_expected_pdf_output.json
    └── t23a_expected_entities.json
```

### Test Data Requirements
1. **Realistic Data**: Use data representative of actual use cases
2. **Size Variation**: Small data for unit tests, larger for functional tests
3. **Edge Cases**: Include problematic data that might cause failures
4. **Expected Results**: Provide expected outputs for comparison
5. **Privacy**: Ensure test data contains no real PII or sensitive information

### Sample Data Standards
```python
# Sample data should be accessible via standard method
def get_sample_data(data_type: str, size: str = 'small') -> Dict[str, Any]:
    """
    Get standardized sample data for testing.
    
    Args:
        data_type: 'pdf', 'text', 'entities', 'graph', etc.
        size: 'small', 'medium', 'large' for performance testing
    """
```

---

## Performance Testing Standards

### Performance Benchmarks
```python
def test_tool_performance():
    """Test tool meets performance requirements."""
    tool = SampleTool()
    
    # Time execution
    start_time = time.time()
    result = tool.execute(get_sample_data('medium'))
    execution_time = time.time() - start_time
    
    # Performance assertions
    assert execution_time < EXPECTED_MAX_TIME
    assert result['status'] == 'success'
    assert 'execution_time' in result
    
    # Memory usage (if applicable)
    # Resource usage validation
```

### Performance Standards by Tool Type
- **Text Processing Tools**: < 5 seconds for 10MB text
- **NLP Tools**: < 30 seconds for 50 document batch
- **Graph Operations**: < 10 seconds for 1000 node graph  
- **Database Operations**: < 2 seconds for typical queries
- **File Processing**: < 60 seconds for 100MB files

---

## Validation Mode Testing

### Validation Mode Requirements
All tools must support validation mode for rapid testing:

```python
def test_validation_mode():
    """Test tool validation mode works correctly."""
    tool = SampleTool()
    
    result = tool.execute(
        input_data={'sample': 'data'},
        context={'validation_mode': True}
    )
    
    # Validation mode assertions
    assert result['status'] == 'success'
    assert result['execution_time'] < 1.0  # Fast execution
    assert 'validation_mode' in result
    assert result['validation_mode'] is True
```

### Validation Mode Standards
- **Fast Execution**: < 1 second preferred, < 5 seconds maximum
- **Realistic Results**: Use representative but potentially mock data
- **Full Interface**: Test complete input/output interface
- **Error Handling**: Test error conditions in validation mode

---

## Test Execution and CI/CD

### Test Categories by Speed
```bash
# Fast tests (< 30 seconds total) - run on every commit
pytest tests/unit/ --maxfail=5

# Medium tests (< 5 minutes total) - run on pull requests  
pytest tests/functional/ --timeout=300

# Slow tests (< 30 minutes total) - run nightly
pytest tests/integration/ tests/e2e/ --timeout=1800
```

### Test Organization
```bash
# By speed
pytest -m "fast"     # Unit tests
pytest -m "medium"   # Functional tests  
pytest -m "slow"     # Integration/E2E tests

# By component
pytest -k "test_pdf"     # All PDF-related tests
pytest -k "test_t23a"    # All T23A tool tests
```

### Required Test Markers
```python
import pytest

@pytest.mark.fast
def test_unit_functionality():
    """Fast unit test."""

@pytest.mark.medium  
def test_functional_workflow():
    """Medium-speed functional test."""
    
@pytest.mark.slow
def test_integration_complete():
    """Slow integration test."""
    
@pytest.mark.requires_neo4j
def test_database_integration():
    """Test requiring Neo4j database."""
```

---

## Quality Gates

### Test Coverage Requirements
- **Unit Test Coverage**: ≥ 80% line coverage for all components
- **Critical Path Coverage**: 100% coverage for critical functionality
- **Integration Coverage**: All service integrations must be tested
- **Regression Coverage**: All bug fixes must include regression tests

### Test Quality Standards
- **Test Isolation**: Tests must not depend on each other
- **Deterministic**: Tests must produce consistent results
- **Clear Assertions**: Each test should have clear pass/fail criteria
- **Meaningful Names**: Test names should describe what is being tested

### Automated Quality Checks
```bash
# Coverage reporting
pytest --cov=src --cov-report=html --cov-fail-under=80

# Performance regression detection
pytest --benchmark-only --benchmark-compare

# Test reliability check (flaky test detection)
pytest --count=10 tests/integration/
```

---

## Testing Tools and Infrastructure

### Required Testing Libraries
```python
# Core testing
import pytest
import unittest.mock

# Performance testing
import pytest-benchmark
import time
import psutil

# Database testing  
import pytest-neo4j
import sqlite3

# Async testing
import pytest-asyncio
```

### Test Environment Setup
```bash
# Test environment preparation
docker compose -f docker-compose.test.yml up -d neo4j-test
export NEO4J_URI="bolt://localhost:7688"  # Test database
export TEST_MODE=true
```

### Test Data Fixtures
```python
@pytest.fixture
def sample_pdf_document():
    """Provide sample PDF for testing."""
    return Path('test_data/documents/sample_academic_paper.pdf')

@pytest.fixture  
def service_manager():
    """Provide configured service manager for testing."""
    return get_test_service_manager()

@pytest.fixture
def clean_database():
    """Provide clean test database."""
    # Setup clean test database
    yield
    # Cleanup after test
```

---

These testing standards ensure comprehensive quality assurance across all KGAS components while maintaining reasonable test execution times and clear quality gates.