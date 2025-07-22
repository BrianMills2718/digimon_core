# KGAS Integration Testing Strategy

**Status**: Living Document  
**Last Updated**: 2025-07-22  
**Purpose**: Define comprehensive integration testing approach for KGAS 121-tool ecosystem

## Executive Summary

This document establishes the integration testing strategy for KGAS, emphasizing Test-Driven Development (TDD) and systematic validation of tool interactions. The strategy ensures that all 121 tools work together seamlessly while maintaining data integrity, performance, and reliability.

## Core Testing Principles

### 1. Test-Driven Development (TDD)
- **Write tests first**: Define expected behavior before implementation
- **Red-Green-Refactor**: Fail → Pass → Improve cycle
- **Contract-first testing**: Validate tool contracts before integration

### 2. Progressive Integration
- **Unit → Integration → End-to-End**: Build confidence at each level
- **Dependency isolation**: Test with real dependencies, mock external services
- **Incremental validation**: Add tools to integration suite as implemented

### 3. Real Data Testing
- **Minimize mocking**: Use real tool implementations where possible
- **Representative datasets**: Test with academic documents and real workflows
- **Performance under load**: Validate with production-scale data

## Integration Testing Levels

### Level 1: Tool Contract Validation
**Purpose**: Ensure each tool adheres to its defined contract

```python
# Example: Contract validation test
class TestToolContracts:
    def test_entity_extractor_contract(self):
        """Test T23a adheres to its input/output contract"""
        # Given: Input matching contract requirements
        input_data = {
            "chunk_refs": ["chunk_123", "chunk_456"],
            "workflow_state": {"chunks_created": True}
        }
        
        # When: Tool processes input
        result = T23a_SpacyNER().process(input_data)
        
        # Then: Output matches contract
        assert "mention_refs" in result
        assert "produced_state" in result
        assert result["produced_state"]["mentions_created"] == True
        assert all(ref.startswith("mention_") for ref in result["mention_refs"])
```

### Level 2: Tool Chain Integration
**Purpose**: Validate sequences of tools work together

```python
# Example: Tool chain test
class TestToolChains:
    def test_document_to_entities_chain(self):
        """Test complete document → entities pipeline"""
        # Given: A test document
        test_doc = "test_data/sample_paper.pdf"
        
        # When: Process through tool chain
        doc_ref = T01_PDFLoader().process(test_doc)
        chunk_refs = T15a_Chunker().process(doc_ref)
        mention_refs = T23a_SpacyNER().process(chunk_refs)
        entity_refs = T31_EntityBuilder().process(mention_refs)
        
        # Then: Validate end-to-end flow
        assert len(entity_refs) > 0
        entities = load_entities(entity_refs)
        assert all(e.confidence > 0 for e in entities)
        assert all(e.provenance.tool_chain == ["T01", "T15a", "T23a", "T31"])
```

### Level 3: Cross-Modal Integration
**Purpose**: Ensure seamless conversion between representations

```python
# Example: Cross-modal test
class TestCrossModalIntegration:
    def test_graph_to_table_to_graph_preservation(self):
        """Test data integrity through modal conversions"""
        # Given: A knowledge graph
        original_graph = build_test_graph()
        
        # When: Convert graph → table → graph
        table = T115_GraphToTable().process(original_graph)
        reconstructed_graph = T116_TableToGraph().process(table)
        
        # Then: Verify semantic preservation
        assert graph_semantically_equal(original_graph, reconstructed_graph)
        assert all_entities_preserved(original_graph, reconstructed_graph)
        assert all_relationships_preserved(original_graph, reconstructed_graph)
        assert provenance_maintained(original_graph, reconstructed_graph)
```

### Level 4: Service Integration
**Purpose**: Validate core services work with all tools

```python
# Example: Service integration test
class TestServiceIntegration:
    def test_identity_service_integration(self):
        """Test T107 Identity Service with dependent tools"""
        # Given: Multiple mentions of same entity
        mentions = create_duplicate_mentions("Barack Obama", count=5)
        
        # When: Process through identity resolution
        identity_service = T107_IdentityService()
        resolved_entities = []
        
        for mention in mentions:
            entity = T31_EntityBuilder().process(mention, identity_service)
            resolved_entities.append(entity)
        
        # Then: All mentions resolve to same entity
        assert len(set(e.entity_id for e in resolved_entities)) == 1
        assert identity_service.get_mention_count(resolved_entities[0]) == 5
```

### Level 5: End-to-End Workflow Testing
**Purpose**: Validate complete research workflows

```python
# Example: Complete workflow test
class TestEndToEndWorkflows:
    def test_academic_research_workflow(self):
        """Test complete academic paper analysis workflow"""
        # Given: Research question and papers
        research_question = "What are the key themes in AI ethics?"
        test_papers = ["paper1.pdf", "paper2.pdf", "paper3.pdf"]
        
        # When: Execute complete workflow
        workflow = AcademicResearchWorkflow()
        result = workflow.execute(
            papers=test_papers,
            question=research_question,
            analysis_modes=["graph", "statistical", "thematic"]
        )
        
        # Then: Validate complete results
        assert result.has_graph_analysis()
        assert result.has_statistical_summary()
        assert result.has_thematic_clusters()
        assert result.all_findings_traceable_to_source()
        assert result.confidence_scores_propagated()
```

## Testing Infrastructure

### Test Data Management
```yaml
test_data/:
  documents/:
    - sample_papers/       # Academic papers for testing
    - edge_cases/          # Problematic documents
    - performance/         # Large documents for load testing
  
  expected_outputs/:
    - entities/            # Known good entity extractions
    - relationships/       # Expected relationships
    - cross_modal/         # Cross-modal conversion results
  
  fixtures/:
    - mock_services/       # Service mocks for isolation
    - test_graphs/         # Pre-built test graphs
    - workflow_states/     # Saved workflow states
```

### Test Execution Framework
```python
# pytest configuration for integration tests
# conftest.py

@pytest.fixture(scope="session")
def integration_test_env():
    """Setup integration test environment"""
    # Start test databases
    neo4j_test = start_test_neo4j()
    sqlite_test = start_test_sqlite()
    
    # Initialize core services
    services = initialize_core_services(neo4j_test, sqlite_test)
    
    # Load test data
    load_test_fixtures()
    
    yield services
    
    # Cleanup
    cleanup_test_data()
    stop_test_databases()

@pytest.fixture
def clean_state(integration_test_env):
    """Ensure clean state for each test"""
    integration_test_env.reset()
    return integration_test_env
```

### Continuous Integration Pipeline
```yaml
# .github/workflows/integration_tests.yml
name: Integration Tests

on: [push, pull_request]

jobs:
  integration_tests:
    runs-on: ubuntu-latest
    
    steps:
    - name: Setup Test Environment
      run: |
        docker-compose -f docker-compose.test.yml up -d
        python scripts/wait_for_services.py
    
    - name: Run Contract Tests
      run: pytest tests/integration/contracts/ -v
    
    - name: Run Tool Chain Tests
      run: pytest tests/integration/chains/ -v
    
    - name: Run Cross-Modal Tests
      run: pytest tests/integration/cross_modal/ -v
    
    - name: Run Service Integration Tests
      run: pytest tests/integration/services/ -v
    
    - name: Run End-to-End Tests
      run: pytest tests/integration/e2e/ -v --slow
    
    - name: Generate Coverage Report
      run: |
        coverage combine
        coverage report
        coverage html
```

## Test Categories and Patterns

### 1. Contract Compliance Tests
**Pattern**: Validate tool input/output contracts

#### Acceptance Criteria
| Criterion | Threshold | Measurement | Action if Failed |
|-----------|-----------|-------------|------------------|
| Contract Validation | 100% | All fields present/typed | Block deployment |
| Schema Compliance | 100% | JSON schema validation | Fix immediately |
| Error Handling | 100% | All error cases handled | Add missing handlers |
| Performance | < 100ms | Contract validation time | Optimize validation |

```python
def test_tool_contract(tool_class, valid_input, invalid_inputs):
    """Generic contract test pattern with acceptance criteria"""
    # Measure validation performance
    start_time = time.time()
    
    # Valid input produces valid output
    result = tool_class().process(valid_input)
    assert validate_output_contract(result)
    
    # Performance check
    validation_time = time.time() - start_time
    assert validation_time < 0.1, f"Contract validation too slow: {validation_time}s"
    
    # Invalid inputs raise appropriate errors
    for invalid in invalid_inputs:
        with pytest.raises(ContractViolation):
            tool_class().process(invalid)
```

### 2. Data Flow Tests
**Pattern**: Trace data through tool chains

#### Acceptance Criteria
| Criterion | Threshold | Measurement | Action if Failed |
|-----------|-----------|-------------|------------------|
| Data Integrity | 100% | No data loss | Debug pipeline |
| Provenance Tracking | 100% | Complete lineage | Fix tracking |
| Chain Latency | < 1s/tool | Per-tool overhead | Optimize bottlenecks |
| Memory Usage | < +50MB/tool | Memory growth | Fix memory leaks |

```python
def test_data_flow(tool_chain, input_data):
    """Verify data flows correctly through tools with criteria"""
    provenance = ProvenanceTracker()
    memory_tracker = MemoryTracker()
    
    current_data = input_data
    for tool in tool_chain:
        # Track memory before
        memory_before = memory_tracker.current_usage()
        tool_start = time.time()
        
        # Process
        previous_hash = hash_data(current_data)
        current_data = tool.process(current_data)
        provenance.record(tool, previous_hash, hash_data(current_data))
        
        # Verify acceptance criteria
        tool_time = time.time() - tool_start
        assert tool_time < 1.0, f"{tool} exceeded latency threshold: {tool_time}s"
        
        memory_growth = memory_tracker.current_usage() - memory_before
        assert memory_growth < 50_000_000, f"{tool} memory growth: {memory_growth/1e6}MB"
    
    # Verify complete provenance chain
    assert provenance.validate_chain()
    assert provenance.no_data_loss()
```

### 3. Performance Integration Tests
**Pattern**: Validate performance under integration

#### Acceptance Criteria
| Criterion | Threshold | Measurement | Action if Failed |
|-----------|-----------|-------------|------------------|
| Throughput | > 100 docs/hour | Documents processed | Scale infrastructure |
| Latency (p95) | < 5s/doc | Processing time | Profile bottlenecks |
| Memory Usage | < 8GB | Peak memory | Optimize memory usage |
| CPU Usage | < 80% | Average CPU | Parallelize work |
| Error Rate | < 0.1% | Failed operations | Fix error sources |

```python
@pytest.mark.performance
def test_integration_performance(large_dataset):
    """Ensure integration meets performance targets with criteria"""
    metrics = PerformanceMetrics()
    
    # Process large dataset through complete pipeline
    start_time = time.time()
    results = []
    errors = 0
    
    for doc in large_dataset:
        try:
            result = complete_pipeline.process(doc)
            results.append(result)
            metrics.record_success(time.time() - start_time)
        except Exception as e:
            errors += 1
            metrics.record_error(e)
    
    # Calculate metrics
    duration = time.time() - start_time
    throughput = len(results) / (duration / 3600)  # docs/hour
    error_rate = errors / len(large_dataset)
    
    # Verify acceptance criteria
    assert throughput > 100, f"Throughput too low: {throughput} docs/hour"
    assert metrics.p95_latency < 5.0, f"P95 latency too high: {metrics.p95_latency}s"
    assert metrics.peak_memory < 8e9, f"Memory usage too high: {metrics.peak_memory/1e9}GB"
    assert metrics.avg_cpu < 80, f"CPU usage too high: {metrics.avg_cpu}%"
    assert error_rate < 0.001, f"Error rate too high: {error_rate*100}%"
```

### 4. Failure Recovery Tests
**Pattern**: Validate graceful failure handling

#### Acceptance Criteria
| Criterion | Threshold | Measurement | Action if Failed |
|-----------|-----------|-------------|------------------|
| Recovery Success | > 95% | Successful recoveries | Improve recovery logic |
| Recovery Time | < 30s | Time to recover | Optimize checkpoints |
| Data Loss | 0% | Data preserved | Fix checkpoint system |
| Error Messages | 100% clear | Message quality | Improve error clarity |
| Retry Success | > 80% | Retry effectiveness | Fix root causes |

```python
def test_failure_recovery(tool_chain, failure_point):
    """Test recovery from failures in tool chain with criteria"""
    # Setup failure injection
    inject_failure_at(tool_chain, failure_point)
    
    # Execute with recovery
    workflow = WorkflowWithRecovery(tool_chain)
    recovery_start = time.time()
    
    result = workflow.execute_with_checkpoints()
    recovery_time = time.time() - recovery_start
    
    # Verify recovery acceptance criteria
    assert result.recovered_from_failure, "Recovery failed"
    assert recovery_time < 30, f"Recovery too slow: {recovery_time}s"
    assert result.checkpoint_used == failure_point - 1
    assert result.final_output_valid()
    assert result.no_data_loss()
    
    # Check error message quality
    assert result.error_message is not None
    assert "recovery" in result.error_message.lower()
    assert len(result.error_message) > 20  # Meaningful message
```

### 5. Cross-Modal Consistency Tests
**Pattern**: Ensure consistency across representations

#### Acceptance Criteria
| Criterion | Threshold | Measurement | Action if Failed |
|-----------|-----------|-------------|------------------|
| Entity Preservation | 100% | All entities present | Fix conversion logic |
| Relationship Accuracy | > 98% | Relations preserved | Debug mapping |
| Confidence Consistency | ±0.01 | Score deviation | Calibrate scoring |
| Conversion Speed | < 2s | Transform time | Optimize algorithms |
| Round-trip Fidelity | > 99% | Information retained | Fix data loss |

```python
def test_cross_modal_consistency(test_graph):
    """Verify consistency across all modal representations with criteria"""
    # Measure conversion performance
    conversion_times = {}
    
    # Convert to all representations
    start = time.time()
    table = graph_to_table(test_graph)
    conversion_times['graph_to_table'] = time.time() - start
    
    start = time.time()
    vector = graph_to_vector(test_graph)
    conversion_times['graph_to_vector'] = time.time() - start
    
    # Verify conversion speed criteria
    for conversion, duration in conversion_times.items():
        assert duration < 2.0, f"{conversion} too slow: {duration}s"
    
    # Verify same information accessible
    graph_entities = extract_entities(test_graph)
    table_entities = extract_entities(table)
    vector_entities = extract_entities(vector)
    
    # Entity preservation check
    assert len(table_entities) == len(graph_entities), "Entity loss in table conversion"
    assert len(vector_entities) == len(graph_entities), "Entity loss in vector conversion"
    
    # Relationship accuracy
    graph_rels = extract_relationships(test_graph)
    table_rels = extract_relationships(table)
    preserved_ratio = len(table_rels) / len(graph_rels)
    assert preserved_ratio > 0.98, f"Only {preserved_ratio*100}% relationships preserved"
    
    # Confidence consistency
    for entity in graph_entities:
        table_conf = get_confidence(table, entity)
        graph_conf = get_confidence(test_graph, entity)
        assert abs(table_conf - graph_conf) < 0.01, f"Confidence drift: {abs(table_conf - graph_conf)}"
```

## Test Data Requirements

### Minimum Test Dataset
1. **Documents**: 10 diverse academic papers
2. **Entities**: 100+ test entities with variations
3. **Relationships**: 500+ test relationships
4. **Edge Cases**: Malformed PDFs, special characters, large files
5. **Performance**: 1GB+ dataset for load testing

### Test Data Generation
```python
# scripts/generate_test_data.py
def generate_integration_test_data():
    """Generate comprehensive test data"""
    # Create synthetic documents
    docs = generate_synthetic_papers(count=10)
    
    # Create entity variations
    entities = generate_entity_variations(
        base_entities=["Apple Inc", "Barack Obama", "Paris"],
        variations_per_entity=10
    )
    
    # Create relationship patterns
    relationships = generate_relationship_patterns(
        entities=entities,
        patterns=["works_for", "located_in", "related_to"]
    )
    
    # Save test data
    save_test_fixtures(docs, entities, relationships)
```

## Monitoring and Reporting

### Integration Test Metrics
- **Coverage**: % of tool interactions tested
- **Reliability**: Success rate over time
- **Performance**: Processing time trends
- **Quality**: Data integrity through chains

### Test Result Dashboard
```python
# Generate integration test report
def generate_integration_report():
    """Create comprehensive test report"""
    report = {
        "contract_compliance": calculate_contract_coverage(),
        "chain_coverage": calculate_chain_coverage(),
        "cross_modal_validation": cross_modal_test_results(),
        "performance_benchmarks": collect_performance_data(),
        "failure_scenarios": failure_test_summary()
    }
    
    generate_html_report(report)
    post_to_dashboard(report)
```

## Best Practices

### 1. Test Independence
- Each test should be independent
- Use fixtures for shared setup
- Clean state between tests

### 2. Real Data Priority
- Prefer real tool implementations
- Mock only external services
- Use representative test data

### 3. Performance Awareness
- Tag slow tests appropriately
- Run performance tests separately
- Monitor test execution time

### 4. Continuous Validation
- Run integration tests on every PR
- Nightly full integration suite
- Weekly performance benchmarks

### 5. Test Maintenance
- Update tests when contracts change
- Remove obsolete test scenarios
- Keep test data current

## Migration to TDD

### For Existing Tools
1. Write tests for current behavior
2. Refactor with test coverage
3. Add integration tests

### For New Tools
1. Write contract tests first
2. Write integration tests
3. Implement to pass tests

## Comprehensive Test Acceptance Criteria

### Overall System Acceptance Thresholds

#### Level 1: Unit Test Criteria
| Metric | Threshold | Measurement | Blocking |
|--------|-----------|-------------|----------|
| Code Coverage | > 90% | Coverage.py | Yes |
| Test Pass Rate | 100% | pytest results | Yes |
| Performance | < 100ms | Per test timing | No |
| Assertions | > 3 per test | Static analysis | No |

#### Level 2: Integration Test Criteria
| Metric | Threshold | Measurement | Blocking |
|--------|-----------|-------------|----------|
| Contract Coverage | 100% | All tools tested | Yes |
| Chain Coverage | > 95% | Tool combinations | Yes |
| Cross-modal Tests | 100% | All conversions | Yes |
| Performance Tests | Pass all | Defined thresholds | Yes |
| Recovery Tests | > 95% pass | Failure scenarios | Yes |

#### Level 3: End-to-End Test Criteria
| Metric | Threshold | Measurement | Blocking |
|--------|-----------|-------------|----------|
| Workflow Success | > 98% | Complete workflows | Yes |
| Data Integrity | 100% | No data loss | Yes |
| Performance | < 30s/workflow | Average time | No |
| Memory Stability | < 8GB peak | Resource monitor | Yes |
| Error Recovery | > 90% | Recovery success | No |

### Performance Benchmarks by Phase

#### Phase 1-3 (Core Pipeline)
| Operation | Target | Acceptable | Critical |
|-----------|--------|------------|----------|
| Document Load | < 2s | < 5s | > 10s |
| Entity Extraction | < 100ms/page | < 200ms | > 500ms |
| Graph Build | < 5s/100 entities | < 10s | > 20s |
| Confidence Scoring | < 50ms/entity | < 100ms | > 200ms |

#### Phase 4-6 (Advanced Features)
| Operation | Target | Acceptable | Critical |
|-----------|--------|------------|----------|
| Cross-modal Transform | < 2s | < 5s | > 10s |
| Pattern Analysis | < 10s | < 20s | > 30s |
| Uncertainty Calc | < 200ms | < 500ms | > 1s |
| Theory Application | < 5s | < 10s | > 20s |

#### Phase 7-8 (Production)
| Operation | Target | Acceptable | Critical |
|-----------|--------|------------|----------|
| API Response | < 200ms p95 | < 500ms | > 1s |
| Concurrent Users | > 100 | > 50 | < 25 |
| Request/sec | > 100 | > 50 | < 25 |
| Availability | > 99.9% | > 99% | < 99% |

### Test Environment Requirements

#### Infrastructure
```yaml
test_infrastructure:
  databases:
    neo4j:
      version: "5.x"
      memory: "2GB"
      cpu: "2 cores"
    sqlite:
      version: "3.x"
      memory: "1GB"
  
  services:
    redis:
      version: "7.x"
      memory: "1GB"
  
  compute:
    min_memory: "8GB"
    min_cpu: "4 cores"
    disk: "50GB SSD"
```

#### Test Data Standards
```yaml
test_data_requirements:
  documents:
    min_count: 100
    formats: ["pdf", "docx", "txt", "md", "html"]
    size_range: "1KB - 50MB"
    languages: ["en", "es", "fr", "de"]
  
  entities:
    min_count: 1000
    types: ["person", "org", "location", "concept"]
    variations: 10 per entity
  
  relationships:
    min_count: 5000
    types: 20+
    confidence_range: "0.0 - 1.0"
```

### Continuous Integration Gates

#### PR Merge Criteria
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Code coverage > 90%
- [ ] Performance benchmarks met
- [ ] No security vulnerabilities
- [ ] Documentation updated

#### Release Criteria
- [ ] All acceptance thresholds met
- [ ] End-to-end tests pass
- [ ] Performance regression < 5%
- [ ] Load tests pass
- [ ] Security audit complete
- [ ] Deployment tested

### Test Failure Response

#### Immediate Actions (Blocking)
1. **Stop deployment pipeline**
2. **Notify responsible team**
3. **Create incident ticket**
4. **Begin root cause analysis**

#### Investigation Process
```bash
# 1. Identify failing test
pytest -x tests/failing_test.py -vv

# 2. Check recent changes
git log --oneline -10

# 3. Run with debugging
pytest --pdb tests/failing_test.py

# 4. Check performance profile
pytest --profile tests/failing_test.py

# 5. Verify environment
python scripts/verify_test_env.py
```

#### Resolution Tracking
| Issue Type | SLA | Escalation |
|------------|-----|------------|
| Test Failure | 4 hours | Team Lead |
| Performance Regression | 8 hours | Tech Lead |
| Data Loss | 2 hours | CTO |
| Security Issue | 1 hour | Security Team |

This strategy ensures comprehensive integration testing while embracing TDD principles for ongoing development with clear, measurable acceptance criteria at every level.