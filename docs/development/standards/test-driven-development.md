# Test-Driven Development (TDD) Standards for KGAS

## Overview

This document establishes mandatory Test-Driven Development (TDD) practices for all KGAS development. TDD is not optional - it is a core architectural requirement that ensures quality, maintainability, and confidence in our academic research tool.

## TDD Philosophy for KGAS

### Why TDD is Critical for Academic Software
1. **Reproducibility**: Tests document expected behavior and ensure consistent results
2. **Confidence in Research**: Researchers must trust the tool's correctness
3. **Theory Validation**: Tests validate theoretical implementations
4. **Refactoring Safety**: Academic software evolves rapidly with new theories
5. **Documentation**: Tests serve as executable specifications

### Core TDD Principles
1. **Red-Green-Refactor**: Write failing test → Make it pass → Improve code
2. **Test First, Always**: No production code without a failing test
3. **One Test, One Behavior**: Each test validates exactly one behavior
4. **Fast Feedback**: Tests must run quickly to maintain flow
5. **Evidence-Based**: All claims backed by passing tests

## TDD Workflow for KGAS Tools

### Standard TDD Cycle for New Tools

```python
# Step 1: Write Contract Test (RED)
class TestT123NewTool:
    """Contract tests for T123 - must be written FIRST"""
    
    def test_contract_compliance(self):
        """Test tool complies with its contract"""
        tool = T123NewTool(mock_services())
        
        # Contract defines expected input/output
        input_data = {
            "entities": [{"id": "e1", "name": "Test"}],
            "confidence_threshold": 0.8
        }
        
        result = tool.execute(input_data)
        
        # Contract validation
        assert result["status"] in ["success", "error"]
        assert "data" in result or "error" in result
        assert result.get("tool_id") == "T123"
        
    def test_required_functionality(self):
        """Test core functionality - write BEFORE implementation"""
        tool = T123NewTool(mock_services())
        
        # This test MUST fail initially
        result = tool.process_entities([
            {"id": "e1", "name": "Apple", "type": "ORG"},
            {"id": "e2", "name": "Apple", "type": "FRUIT"}
        ])
        
        assert len(result["disambiguated"]) == 2
        assert result["disambiguated"][0]["id"] != result["disambiguated"][1]["id"]

# Step 2: Minimal Implementation (GREEN)
class T123NewTool(BaseTool):
    """Implement ONLY enough to pass tests"""
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Minimal implementation to pass contract test
            result = self.process_entities(params.get("entities", []))
            return {
                "status": "success",
                "data": result,
                "tool_id": "T123"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "tool_id": "T123"
            }
    
    def process_entities(self, entities: List[Dict]) -> Dict[str, Any]:
        # Just enough to make test pass
        return {"disambiguated": entities}

# Step 3: Add More Tests (RED)
def test_confidence_threshold_filtering(self):
    """Add new test for next behavior"""
    tool = T123NewTool(mock_services())
    
    entities = [
        {"id": "e1", "confidence": 0.9},
        {"id": "e2", "confidence": 0.7},
        {"id": "e3", "confidence": 0.6}
    ]
    
    result = tool.process_entities(entities, threshold=0.8)
    
    # Only high confidence entities should pass
    assert len(result["disambiguated"]) == 1
    assert result["disambiguated"][0]["id"] == "e1"

# Step 4: Implement Feature (GREEN)
# Step 5: Refactor (REFACTOR)
# Repeat cycle...
```

### TDD for Services

```python
# Step 1: Service Contract Test
class TestIdentityService:
    """TDD for core services"""
    
    def test_service_initialization(self):
        """Service must initialize with required dependencies"""
        service = IdentityService(db_manager=mock_db())
        assert service.is_initialized()
        assert service.health_check()["status"] == "healthy"
    
    def test_entity_resolution_contract(self):
        """Define expected behavior FIRST"""
        service = IdentityService(mock_db())
        
        # This defines our contract
        mentions = [
            {"text": "Apple", "context": "technology company"},
            {"text": "Apple", "context": "fruit nutrition"}
        ]
        
        entities = service.resolve_mentions(mentions)
        
        # Contract: Different contexts = different entities
        assert len(entities) == 2
        assert entities[0]["canonical_name"] == "Apple Inc."
        assert entities[1]["canonical_name"] == "Apple (fruit)"
```

### TDD for Integration

```python
# Integration tests also follow TDD
class TestPhaseIntegration:
    """TDD for tool chains"""
    
    def test_document_to_knowledge_graph_flow(self):
        """Define expected integration behavior"""
        # Write this BEFORE implementing integration
        
        # Given a PDF document
        pdf_path = "test_data/sample.pdf"
        
        # When processed through the pipeline
        result = pipeline.process(pdf_path)
        
        # Then we get a knowledge graph
        assert result["status"] == "success"
        assert len(result["entities"]) > 0
        assert len(result["relationships"]) > 0
        assert result["graph_id"] is not None
```

## TDD Requirements by Component Type

### 1. Tool Development TDD

Every tool MUST have:

```python
# tests/unit/test_t{number}_{name}.py
class TestT{Number}{Name}:
    """Mandatory TDD test structure"""
    
    # 1. Contract Tests (REQUIRED)
    def test_contract_input_validation(self):
        """Tool rejects invalid inputs"""
        
    def test_contract_output_format(self):
        """Tool produces expected output structure"""
        
    def test_contract_error_handling(self):
        """Tool handles errors per contract"""
    
    # 2. Functionality Tests (REQUIRED)
    def test_core_functionality(self):
        """Tool performs its primary function"""
        
    def test_edge_cases(self):
        """Tool handles boundary conditions"""
        
    def test_performance_requirements(self):
        """Tool meets performance targets"""
    
    # 3. Integration Tests (REQUIRED)
    def test_service_integration(self):
        """Tool integrates with required services"""
        
    def test_workflow_state_management(self):
        """Tool manages workflow state correctly"""
```

### 2. Service Development TDD

```python
# tests/unit/test_{service_name}_service.py
class Test{ServiceName}Service:
    """Service TDD requirements"""
    
    # 1. Initialization Tests
    def test_service_initialization(self):
        """Service initializes with dependencies"""
    
    def test_health_check(self):
        """Service reports health status"""
    
    # 2. API Contract Tests  
    def test_api_contract(self):
        """All public methods tested FIRST"""
    
    # 3. State Management Tests
    def test_concurrent_access(self):
        """Service handles concurrent requests"""
    
    def test_resource_cleanup(self):
        """Service cleans up resources"""
```

### 3. Cross-Modal Analysis TDD

```python
# tests/unit/test_cross_modal_{transform}.py
class TestCrossModal{Transform}:
    """Cross-modal TDD requirements"""
    
    def test_transformation_preserves_semantics(self):
        """Semantic meaning preserved across modalities"""
        
    def test_transformation_reversibility(self):
        """Transformations can round-trip when applicable"""
        
    def test_information_loss_tracking(self):
        """Any information loss is tracked and reported"""
```

## TDD Metrics and Standards

### Coverage Requirements
```yaml
# .coveragerc
[coverage:run]
source = src/
omit = 
    */tests/*
    */migrations/*

[coverage:report]
fail_under = 95  # 95% minimum coverage
show_missing = True
skip_covered = False

[coverage:html]
directory = coverage_html_report
```

### Performance Test Requirements
```python
# Every tool must have performance tests
@pytest.mark.performance
def test_tool_performance(self, benchmark):
    """TDD includes performance requirements"""
    tool = T123NewTool(real_services())
    
    # Performance must be defined BEFORE implementation
    result = benchmark.pedantic(
        tool.execute,
        args=[large_dataset],
        iterations=10,
        rounds=5
    )
    
    # Assert performance requirements
    assert result.stats["mean"] < 2.0  # seconds
    assert result.stats["stddev"] < 0.5
```

### Test Execution Standards
```bash
# Pre-commit hook enforces TDD
#!/bin/bash
# .git/hooks/pre-commit

# Run tests before every commit
pytest tests/unit/ -x --ff

# Check coverage
coverage run -m pytest tests/
coverage report --fail-under=95

# Run contract validation
python scripts/validate_contracts.py

# If any fail, block commit
```

## TDD Documentation Requirements

### Test Documentation Template
```python
def test_complex_behavior(self):
    """
    Test: [Behavior being tested]
    
    Given: [Initial conditions]
    When: [Action taken]
    Then: [Expected outcome]
    
    Theory: [Academic theory being validated if applicable]
    
    Performance: [Expected performance characteristics]
    """
```

### Theory-Aware Test Documentation
```python
def test_betweenness_centrality_calculation(self):
    """
    Test: Betweenness centrality follows Freeman's definition
    
    Given: A graph with known betweenness values
    When: Calculate betweenness centrality
    Then: Results match Freeman (1977) formula within 0.001
    
    Theory: Freeman, L.C. (1977). "A set of measures of centrality 
            based on betweenness". Sociometry. 40 (1): 35–41.
    
    Performance: O(V*E) for unweighted graphs
    """
```

## TDD Validation and Monitoring

### Continuous TDD Metrics
```python
# scripts/tdd_metrics.py
"""Generate TDD compliance report"""

def generate_tdd_report():
    """Weekly TDD metrics"""
    return {
        "test_first_compliance": calculate_test_first_percentage(),
        "coverage_trends": get_coverage_over_time(),
        "test_execution_time": measure_test_suite_performance(),
        "failed_test_resolution_time": track_red_to_green_time(),
        "refactoring_frequency": measure_refactoring_cycles()
    }
```

### TDD Dashboards
```yaml
# TDD metrics tracked in CI/CD
metrics:
  - test_coverage:
      target: 95%
      minimum: 90%
      trend: increasing
      
  - test_first_compliance:
      target: 100%
      minimum: 95%
      measurement: commit_history_analysis
      
  - test_execution_time:
      target: < 5 minutes
      maximum: 10 minutes
      trend: stable_or_decreasing
      
  - test_failure_rate:
      target: < 5%
      maximum: 10%
      window: rolling_7_days
```

## TDD Anti-Patterns to Avoid

### ❌ Writing Tests After Code
```python
# WRONG: Implementation first
def calculate_similarity(self, vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# Then writing test - THIS IS NOT TDD!
def test_similarity():
    assert calculate_similarity([1,0], [1,0]) == 1.0
```

### ❌ Testing Implementation Details
```python
# WRONG: Testing private methods
def test_private_helper(self):
    tool = MyTool()
    # Don't test private methods directly
    assert tool._internal_helper() == expected
```

### ❌ Tautological Tests
```python
# WRONG: Test doesn't actually test behavior
def test_returns_dict(self):
    result = tool.execute({})
    assert isinstance(result, dict)  # Too generic
```

### ✅ Correct TDD Approach
```python
# RIGHT: Behavior-driven test first
def test_cosine_similarity_orthogonal_vectors(self):
    """Orthogonal vectors have zero similarity"""
    tool = VectorSimilarityTool()
    
    # Define expected behavior FIRST
    vec1 = [1, 0, 0]
    vec2 = [0, 1, 0]
    
    similarity = tool.calculate_similarity(vec1, vec2)
    
    assert similarity == 0.0  # Orthogonal = zero similarity
    
# THEN implement to pass test
```

## TDD Integration with Roadmap

### Phase-Specific TDD Requirements

#### Phase 1-3: Foundation Tools
- Test coverage baseline: 95%
- Contract tests: 100% required
- Performance tests: Required for I/O operations

#### Phase 4-6: Advanced Analytics  
- Theory validation tests: Required
- Cross-modal preservation tests: Required
- Statistical accuracy tests: ±0.001 tolerance

#### Phase 7: Service Architecture
- Integration tests: Required for all services
- Concurrency tests: Required
- Fault tolerance tests: Required

#### Phase 8: External Integration
- Mock external services: Required
- Circuit breaker tests: Required  
- Fallback behavior tests: Required

## TDD Tooling and Infrastructure

### Required Testing Tools
```bash
# requirements/test.txt
pytest==7.4.0
pytest-asyncio==0.21.0
pytest-benchmark==4.0.0
pytest-cov==4.1.0
pytest-mock==3.11.1
pytest-timeout==2.1.0
pytest-xdist==3.3.1  # Parallel execution
hypothesis==6.82.0   # Property-based testing
faker==19.3.0       # Test data generation
```

### TDD IDE Configuration
```json
// .vscode/settings.json
{
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "--strict-markers",
        "--tb=short",
        "-vv"
    ],
    "python.testing.autoTestDiscoverOnSaveEnabled": true,
    "testExplorer.showOnRun": true
}
```

## Enforcement and Compliance

### Git Hooks
```bash
#!/bin/bash
# .git/hooks/pre-push
# Enforce TDD before push

# Check for tests for new files
new_files=$(git diff --name-only --diff-filter=A origin/main HEAD | grep -E "src/.*\.py$")

for file in $new_files; do
    test_file=$(echo $file | sed 's/src/tests\/unit/; s/.py$/_test.py/')
    if [ ! -f "$test_file" ]; then
        echo "ERROR: No test file found for $file"
        echo "Expected: $test_file"
        exit 1
    fi
done

# Run all tests
pytest tests/ --cov=src/ --cov-fail-under=95
```

### CI/CD Gates
```yaml
# .github/workflows/tdd-enforcement.yml
name: TDD Enforcement

on: [push, pull_request]

jobs:
  tdd-compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check Test-First Compliance
        run: python scripts/check_tdd_compliance.py
        
      - name: Run Tests with Coverage
        run: |
          pytest tests/ --cov=src/ --cov-report=xml
          coverage report --fail-under=95
          
      - name: Validate Contracts
        run: python scripts/validate_all_contracts.py
        
      - name: Performance Tests
        run: pytest tests/ -m performance --benchmark-only
```

## TDD Culture and Training

### TDD Onboarding Checklist
- [ ] Read "Test-Driven Development" by Kent Beck
- [ ] Complete KGAS TDD tutorial
- [ ] Write first tool using TDD with mentor
- [ ] Pass TDD certification quiz
- [ ] Contribute to test framework improvements

### TDD Resources
- Internal TDD workshops (monthly)
- Pair programming sessions focused on TDD
- TDD champions for each phase
- Regular TDD retrospectives

This comprehensive TDD framework ensures that quality is built into KGAS from the ground up, supporting our mission to create a trustworthy academic research tool.