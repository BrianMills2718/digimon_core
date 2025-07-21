# Tests Suite - CLAUDE.md

## Overview
The `tests/` directory contains the **comprehensive test suite** for the GraphRAG system. It includes unit tests, integration tests, performance tests, security tests, and UI tests that ensure production-grade reliability and quality.

## **CRITICAL TESTING PRINCIPLES**

### **Real Execution Over Mocks**
- **MANDATE**: All functional tests MUST execute real tool operations, not mocked versions
- **NO MOCK FALLBACKS**: Tests should fail if real functionality doesn't work
- **Example**: `tests/functional/test_tools_functional_real.py` demonstrates real execution testing

### **Systematic Coverage Requirements**
- **Unit Tests**: Test individual functions (mocks acceptable for dependencies)
- **Functional Tests**: Test complete tool execution with real data (NO mocks of core functionality)
- **Integration Tests**: Test tool chains working together 
- **End-to-End Tests**: Test complete workflows from user input to results

### **Test Validation Standards**
- **Real Data**: Use actual test documents, not synthetic placeholders
- **Measurable Assertions**: Assert specific, measurable outcomes (entity counts, types, confidence scores)
- **Performance Validation**: Include timing and resource usage validation
- **Error Scenarios**: Test failure modes with real error conditions

## Directory Structure
```
tests/
├── conftest.py                    # Global PyTest fixtures (seed, etc.)
├── functional/                    # High-level functional tests
├── integration/                  # Integration tests (phase chaining, services)
├── performance/                  # Performance and load tests
├── security/                     # Security and resilience tests
├── unit/                         # Component-level unit tests
├── vector_index_health/          # Vector index health checks
├── ui/                           # UI interaction tests (Streamlit)
├── phase3/                       # Specialized Phase-3 fusion tests
├── error_scenarios/              # Failure and edge-case tests
└── ... (additional categories)
```

## Test Categories

### **1. Unit Tests** – Individual Component Testing
- **Purpose**: Validate individual functions, classes, and utilities
- **Mocking Policy**: Acceptable for external dependencies (databases, APIs), NOT for core functionality
- **Coverage Target**: >95% line coverage for core modules

### **2. Functional Tests** – Real Execution Testing  
- **Purpose**: Validate tools execute correctly with real data
- **NO MOCKS POLICY**: Core tool functionality must be tested without mocks
- **Example**: `tests/functional/test_tools_functional_real.py`
- **Requirements**: Must use actual documents, real entity extraction, measurable results

### **3. Integration Tests** – Cross-Component Testing
- **Purpose**: Validate interactions across phases and services
- **Focus**: Tool chains, service communication, data flow
- **Real Workflow Testing**: Complete PDF → Entities → Graph → Results pipelines

### **4. Performance Tests** – Timing and Resource Validation
- **Purpose**: Establish performance baselines and limits
- **Real Load Testing**: Use realistic document sizes and processing volumes
- **Benchmarking**: Track processing times, memory usage, CPU utilization

### **5. Security Tests** – Attack and Resilience Testing  
- **Purpose**: Validate API security, rate limiting, and data privacy
- **Real Attack Simulation**: SQL injection, path traversal, malformed inputs
- **No Security Theater**: Actually attempt to break the system

### **6. UI Tests** – Complete User Experience Testing
- **Purpose**: Validate Streamlit UI workflows and user flows
- **Real User Scenarios**: Upload documents, process, view results, export
- **Cross-Modal Testing**: Test Graph ↔ Table ↔ Vector conversions

### **7. Error Scenario Tests** – Failure Mode Testing
- **Purpose**: Validate graceful degradation and fail-fast logic
- **Real Error Conditions**: Network failures, corrupted files, resource exhaustion
- **Recovery Testing**: System behavior during and after errors

## PyTest Conventions
- **File Naming**: `test_<feature>_*.py`
- **Autouse Fixtures**: `conftest.py` seeds RNGs for determinism
- **Markers**:
  - `@pytest.mark.unit` – Run only unit tests
  - `@pytest.mark.integration` – Run integration tests
  - `@pytest.mark.performance` – Run performance tests (can be skipped in CI)
  - `@pytest.mark.security` – Run security tests
- **Environment Variables**: Use `KGAS_ENV` to switch config (dev/prod)
- **Skipping**: Use `pytest.skip` for tests requiring external resources

## Running Tests
```bash
# Run ALL tests
pytest -v

# Run fast unit tests only
pytest -m unit -v

# Run integration tests
pytest -m integration -v

# Run performance tests (may be slow)
pytest -m performance -v --durations=10

# Run tests with coverage
pytest --cov=src --cov-report=term-missing -v
```

## Continuous Integration
- CI runs `pytest -m "not performance"` to keep pipelines fast
- Performance tests run nightly on dedicated runners
- Failing tests block merges to `main`

## Fixtures & Utilities
- **`conftest.py`** seeds RNGs for deterministic results (seed=42)
- Additional fixtures live in `tests/unit/fixtures.py` and similar files
- **`fake_data/`** directories hold mock documents, PDFs, and graphs

## Writing New Tests

### **Functional Test Requirements (NO MOCKS)**
1. **Real Execution**: Test actual tool execution, not mocked versions
2. **Real Data**: Use actual test documents, not empty strings or placeholders  
3. **Measurable Results**: Assert specific counts, types, values (e.g., "found 5 entities")
4. **Error Handling**: Test real error scenarios (missing files, network failures)

### **Test Implementation Standards**
1. **File Organization**: Create test files in appropriate subdirectory (`functional/`, `unit/`, etc.)
2. **Import Pattern**: Use absolute imports (`from src.tools.phase1.t23a_spacy_ner import SpacyNER`)
3. **Fixtures**: Use fixtures from `conftest.py` or create new ones for real test data
4. **Performance Marking**: Mark slow tests with `@pytest.mark.slow` or `@pytest.mark.performance`
5. **Clear Assertions**: Use `assert` statements with specific, measurable expectations
6. **Independence**: Keep tests independent and idempotent

### **Example: Functional Test Pattern**
```python
def test_spacy_ner_functional_real():
    """Test SpaCy NER with real execution - NO MOCKS."""
    from src.tools.phase1.t23a_spacy_ner import SpacyNER
    
    ner = SpacyNER()
    test_text = "Apple Inc. was founded by Steve Jobs in Cupertino, California."
    
    # REAL execution (no mocks)
    result = ner.extract_entities_working(test_text)
    
    # MEASURABLE assertions
    assert len(result) >= 4, f"Expected at least 4 entities, got {len(result)}"
    entity_names = [e["name"] for e in result]
    assert any("Apple" in name for name in entity_names), "Should find Apple Inc."
    assert any("Jobs" in name for name in entity_names), "Should find Steve Jobs"
    
    # SPECIFIC type validation
    entity_types = [e["type"] for e in result]
    assert "ORG" in entity_types, "Should find organization entities"
    assert "PERSON" in entity_types, "Should find person entities"
```

### **Anti-Patterns to Avoid**
```python
# ❌ BAD: Mocking core functionality
def test_spacy_ner_bad():
    ner = SpacyNER()
    ner.extract_entities = Mock(return_value=[...])  # DON'T DO THIS
    
# ❌ BAD: Unmeasurable assertions  
def test_tool_bad():
    result = tool.execute()
    assert result  # Too vague
    
# ❌ BAD: Synthetic data
def test_with_fake_data():
    fake_text = "Entity1 Entity2"  # Not realistic
```

## Coverage Targets
- **Core Modules**: ≥ 95 % line coverage
- **Tool Phases**: ≥ 90 % branch coverage
- **Services**: ≥ 90 % functional coverage

## Troubleshooting
| Issue | Fix |
|-------|-----|
| Tests fail randomly | Ensure RNG seeding, isolate external resources |
| Slow tests | Add `@pytest.mark.slow`, mock heavy dependencies |
| Database connection errors | Spin up Neo4j via docker-compose before running tests |

## Useful Commands
```bash
# Re-run only failed tests
pytest --last-failed -v

# Debug a single test
pytest tests/functional/test_pipeline.py::test_phase1 --pdb

# Profile slow tests
pytest --profile -m performance
```

## CI Integration
CI pipeline stages:
1. **Install** – `pip install -r requirements-dev.txt`
2. **Lint** – `ruff` and `mypy`
3. **Test** – `pytest -m "not performance"`
4. **Coverage** – Fail if coverage < target
5. **Artifacts** – Upload coverage XML & HTML reports

## Adding New Test Categories
1. Create subdirectory under `tests/`.
2. Add `__init__.py` (optional) to mark as package.
3. Add tests and (optionally) fixtures.
4. Update this CLAUDE.md with new category description. 