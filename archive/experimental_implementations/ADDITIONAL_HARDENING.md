# Additional Hardening from Adversarial Testing

## 1. Specification Drift Prevention

### Problem Found
T31 was specified to "create entity nodes" but implementation includes full community detection. This kind of feature creep makes testing and maintenance harder.

### Solution: Specification Compliance Check
```python
# In each tool file, add a SPECIFICATION section
"""
SPECIFICATION COMPLIANCE:
- Spec says: "Create entity nodes in graph"
- Implementation: Creates nodes + detects communities
- Justification: Community detection added as optional feature per user request
- Deviations tracked in: SPEC_DEVIATIONS.md
"""
```

### New Rule
If implementation differs from spec:
1. Document the deviation in the code
2. Add to SPEC_DEVIATIONS.md
3. Get explicit approval before adding major features

## 2. Test Entity Creation Pattern

### Problem Found
Test entities created directly in Neo4j often lack required fields (timestamps, canonical_name, etc.)

### Solution: Test Data Builders
```python
# test_utils/builders.py
class TestEntityBuilder:
    @staticmethod
    def create_entity(
        session,
        id: str,
        name: str,
        entity_type: str = "TEST",
        **kwargs
    ):
        """Create test entity with ALL required fields."""
        session.run("""
            CREATE (e:Entity {
                id: $id,
                name: $name,
                canonical_name: $canonical_name,
                entity_type: $entity_type,
                created_at: datetime(),
                updated_at: datetime(),
                confidence: $confidence
            })
        """, 
        id=id,
        name=name,
        canonical_name=kwargs.get('canonical_name', name),
        entity_type=entity_type,
        confidence=kwargs.get('confidence', 1.0)
        )

# Usage in tests
TestEntityBuilder.create_entity(session, "test1", "Test Entity")
```

## 3. Edge Case Test Requirements

### Problem Found
Tools work in happy path but fail on edge cases (empty graph, disconnected nodes, missing data)

### Solution: Mandatory Edge Case Tests
Every tool MUST have tests for:
```python
def test_empty_input():
    """Tool handles empty input gracefully."""
    result = tool.process([])
    assert result['status'] in ['success', 'error']
    assert result['metadata']['duration_ms'] >= 0

def test_disconnected_graph():
    """Tool handles disconnected components."""
    # Create islands in graph
    result = tool.process_graph_with_islands()
    assert result['status'] == 'success'

def test_missing_optional_data():
    """Tool works when optional fields are missing."""
    # Create entities without optional fields
    result = tool.process_minimal_entities()
    assert result['status'] in ['success', 'partial']

def test_malformed_input():
    """Tool handles malformed input gracefully."""
    result = tool.process("not_a_valid_reference")
    assert result['status'] == 'error'
    assert 'error' in result
```

## 4. Integration Test Pattern

### Problem Found
Tools tested in isolation work, but fail when chained together

### Solution: Chain Testing
```python
# test_integration/test_chains.py
def test_pdf_to_pagerank_chain():
    """Test full chain from PDF to PageRank."""
    # Load PDF
    pdf_result = pdf_loader.load_pdf("test.pdf")
    assert pdf_result['status'] == 'success'
    
    # Chunk
    chunk_result = chunker.chunk_document(pdf_result['document_ref'])
    assert chunk_result['status'] == 'success'
    
    # Extract entities
    entity_result = extractor.extract(chunk_result['chunk_refs'][0])
    assert entity_result['status'] == 'success'
    
    # Run PageRank
    pr_result = pagerank.compute()
    assert pr_result['status'] == 'success'
    
    # Verify data flows correctly
    assert pr_result['metadata']['entity_count'] > 0
```

## 5. Performance Monitoring

### Problem Found
No visibility into performance degradation over time

### Solution: Performance Benchmarks
```python
# test_performance/benchmarks.py
class PerformanceBenchmark:
    THRESHOLDS = {
        'T01_pdf_load': 5000,  # 5 seconds for 10MB PDF
        'T13_chunk': 1000,     # 1 second for 100 chunks
        'T68_pagerank': 5000,  # 5 seconds for 1000 entities
    }
    
    def test_tool_performance(self, tool_name, operation, data):
        start = time.time()
        result = operation(data)
        duration_ms = (time.time() - start) * 1000
        
        threshold = self.THRESHOLDS.get(tool_name, 10000)
        assert duration_ms < threshold, \
            f"{tool_name} took {duration_ms}ms, threshold is {threshold}ms"
```

## 6. Automated Hardcoded Value Detection

### Problem Found
Hardcoded thresholds sneak in despite best intentions

### Solution: AST-based Detection
```python
# scripts/detect_hardcoded.py
import ast

class HardcodedDetector(ast.NodeVisitor):
    def __init__(self):
        self.violations = []
    
    def visit_Compare(self, node):
        # Detect: if value > 3.0
        if isinstance(node.comparators[0], ast.Num):
            if node.comparators[0].n not in [0, 1, -1]:  # Allow 0, 1, -1
                self.violations.append({
                    'line': node.lineno,
                    'value': node.comparators[0].n,
                    'code': ast.get_source_segment(self.source, node)
                })
        self.generic_visit(node)

# Run in CI/CD or pre-commit
```

## 7. Reality Check Protocol

### Problem Found
It's easy to claim success without thorough testing

### Solution: Adversarial Test Suite
```python
# test_adversarial/reality_check.py
class RealityCheck:
    """Run after any major milestone claim."""
    
    def test_no_mocks(self):
        """Verify no mocks in production code."""
        # Scan for Mock, MagicMock, patch
        
    def test_deterministic_results(self):
        """Verify randomness where expected."""
        # Run algorithm multiple times
        # Same input + parameters = same output?
        
    def test_performance_claims(self):
        """Verify performance is as claimed."""
        # Actually measure with real data
        
    def test_persistence(self):
        """Verify data persists across restarts."""
        # Create data, restart services, check data

```

## 8. Tool Capability Matrix

### Problem Found
Unclear which tools are fully implemented vs partially implemented

### Solution: Capability Tracking
```markdown
# TOOL_CAPABILITY_MATRIX.md

| Tool | Specified | Implemented | Tested | Edge Cases | Performance | Production Ready |
|------|-----------|-------------|---------|------------|-------------|------------------|
| T01  | ✅        | ✅          | ✅      | ⚠️         | ✅          | 🟡              |
| T23b | ✅        | ✅          | ✅      | ✅         | ✅          | 🟢              |
| T31  | ✅        | ✅*         | ✅      | ❌         | ✅          | 🟡              |
| T94  | ✅        | ⚠️          | ⚠️      | ❌         | ❌          | 🔴              |

* = Deviates from specification
```

## Pre-Continuation Checklist

Before continuing with more implementation:

1. [ ] Fix remaining Phase 1 issues (T41 embeddings, T94 NLQ)
2. [ ] Create test data builders
3. [ ] Add edge case tests to existing tools
4. [ ] Set up hardcoded value detection
5. [ ] Create integration test suite
6. [ ] Document all specification deviations
7. [ ] Create capability matrix for current tools
8. [ ] Run full adversarial test suite again

Only after these are complete should we proceed with new tool implementation.