# Integration Testing - CLAUDE.md

## Overview
The `tests/integration/` directory contains integration tests that validate the interaction between multiple system components, services, and external dependencies. These tests ensure that KGAS components work together correctly in realistic scenarios.

## Directory Structure

### Current State
```
tests/integration/
├── test_complete_pipeline.py      # End-to-end pipeline testing
├── test_database_integration.py   # Database integration tests
├── test_phase_transitions.py      # Phase interface testing
├── test_service_integration.py    # Service interaction tests
└── test_cross_modal_flows.py      # Cross-modal analysis testing
```

### Test Categories

#### **Pipeline Integration Tests**
- **End-to-end workflows**: Complete document processing pipelines
- **Phase transitions**: Integration between processing phases
- **Service coordination**: Multi-service workflow validation
- **Error recovery**: Integration-level error handling and recovery

#### **Database Integration Tests**
- **Bi-store operations**: Neo4j and SQLite coordination
- **Transaction integrity**: Cross-database transaction consistency
- **Query coordination**: Complex queries spanning multiple storage systems
- **Connection management**: Database connection pooling and lifecycle

#### **Service Integration Tests**
- **Service dependencies**: Service interaction and dependency resolution
- **Configuration integration**: Unified configuration across services
- **Event coordination**: Service event handling and propagation
- **Resource sharing**: Shared resource access and coordination

#### **Cross-Modal Integration Tests**
- **Format conversion workflows**: Graph ↔ Table ↔ Vector conversion chains
- **Analytics coordination**: Cross-modal analysis orchestration
- **Source traceability**: Provenance tracking across format conversions
- **Quality consistency**: Quality metrics across different data representations

## Integration Testing Patterns

### Test Structure Template
```python
import pytest
from typing import Dict, Any, List
from pathlib import Path

# Core system imports
from src.core.service_manager import ServiceManager
from src.core.pipeline_orchestrator import PipelineOrchestrator
from src.core.analytics_service import AnalyticsService

# Test utilities
from tests.utils.test_data import create_test_document
from tests.utils.test_setup import setup_test_environment

class TestComponentIntegration:
    """
    Integration test following standard patterns.
    
    Tests the interaction between multiple components
    in realistic usage scenarios.
    """
    
    @pytest.fixture(scope="class")
    def integration_environment(self):
        """Set up integration test environment."""
        # Set up test databases
        env = setup_test_environment()
        
        # Initialize services
        service_manager = ServiceManager(test_mode=True)
        
        # Create test data
        test_docs = [
            create_test_document("academic_paper_1.pdf"),
            create_test_document("academic_paper_2.pdf")
        ]
        
        return {
            "services": service_manager,
            "test_docs": test_docs,
            "env": env
        }
    
    def test_complete_pipeline_integration(self, integration_environment):
        """Test complete document processing pipeline."""
        services = integration_environment["services"]
        test_docs = integration_environment["test_docs"]
        
        # Initialize pipeline
        pipeline = PipelineOrchestrator(services)
        
        # Process documents
        results = []
        for doc in test_docs:
            result = pipeline.process_document(doc["path"])
            assert result["status"] == "success"
            assert "entities" in result["data"]
            assert "relationships" in result["data"]
            results.append(result)
        
        # Verify cross-document integration
        analytics = AnalyticsService(services)
        fusion_result = analytics.fuse_documents(results)
        
        assert fusion_result["status"] == "success"
        assert "unified_graph" in fusion_result["data"]
        assert fusion_result["data"]["cross_references"] > 0
    
    def test_database_consistency(self, integration_environment):
        """Test data consistency across Neo4j and SQLite."""
        services = integration_environment["services"]
        
        # Create test entity in Neo4j
        neo4j_manager = services.neo4j_manager
        entity_data = {
            "id": "test_entity_123",
            "name": "Test Entity",
            "type": "Person",
            "confidence": 0.95
        }
        
        # Store in Neo4j
        neo4j_result = neo4j_manager.create_entity(entity_data)
        assert neo4j_result["status"] == "success"
        
        # Check SQLite provenance
        sqlite_manager = services.sqlite_manager
        provenance_result = sqlite_manager.get_provenance("test_entity_123")
        
        assert provenance_result["status"] == "success"
        assert len(provenance_result["data"]) > 0
        
        # Verify data consistency
        neo4j_entity = neo4j_manager.get_entity("test_entity_123")
        assert neo4j_entity["data"]["confidence"] == entity_data["confidence"]
    
    def test_service_interaction(self, integration_environment):
        """Test interaction between core services."""
        services = integration_environment["services"]
        
        # Test Identity Service + Quality Service interaction
        identity = services.identity_service
        quality = services.quality_service
        
        # Create entities with quality assessment
        entities = [
            {"name": "Dr. Jane Smith", "type": "Person", "confidence": 0.9},
            {"name": "Jane Smith", "type": "Person", "confidence": 0.85},
            {"name": "University of Example", "type": "Organization", "confidence": 0.95}
        ]
        
        # Process through identity resolution
        resolved_entities = []
        for entity in entities:
            # Quality assessment
            quality_result = quality.assess_entity_quality(entity)
            entity["quality_tier"] = quality_result["tier"]
            
            # Identity resolution
            identity_result = identity.resolve_entity(entity)
            resolved_entities.append(identity_result)
        
        # Verify identity resolution worked
        assert len(resolved_entities) == 2  # Jane Smith entities should be merged
        
        # Verify quality service integration
        for entity in resolved_entities:
            assert "quality_tier" in entity
            assert entity["quality_tier"] in ["HIGH", "MEDIUM", "LOW"]
    
    @pytest.mark.slow
    def test_cross_modal_workflow(self, integration_environment):
        """Test cross-modal analysis workflow integration."""
        services = integration_environment["services"]
        
        # Start with graph data
        graph_data = {
            "entities": [
                {"id": "e1", "name": "Research Topic A", "type": "Topic"},
                {"id": "e2", "name": "Dr. Smith", "type": "Person"},
                {"id": "e3", "name": "University X", "type": "Organization"}
            ],
            "relationships": [
                {"source": "e1", "target": "e2", "type": "researched_by"},
                {"source": "e2", "target": "e3", "type": "affiliated_with"}
            ]
        }
        
        analytics = AnalyticsService(services)
        
        # Convert to table format
        table_result = analytics.convert_to_table(graph_data)
        assert table_result["status"] == "success"
        assert "dataframe" in table_result["data"]
        
        # Perform table analysis
        stats_result = analytics.analyze_table_statistics(table_result["data"]["dataframe"])
        assert stats_result["status"] == "success"
        
        # Convert to vector format
        vector_result = analytics.convert_to_vectors(graph_data)
        assert vector_result["status"] == "success"
        assert "embeddings" in vector_result["data"]
        
        # Perform vector analysis
        similarity_result = analytics.analyze_vector_similarity(vector_result["data"]["embeddings"])
        assert similarity_result["status"] == "success"
        
        # Verify source traceability
        for result in [table_result, vector_result, stats_result, similarity_result]:
            assert "provenance" in result
            assert "source_graph" in result["provenance"]
```

### Database Integration Patterns
```python
class TestDatabaseIntegration:
    """Test database integration patterns."""
    
    def test_transaction_coordination(self, test_services):
        """Test coordinated transactions across databases."""
        neo4j = test_services.neo4j_manager
        sqlite = test_services.sqlite_manager
        
        # Start coordinated transaction
        with test_services.transaction_manager.coordinated_transaction():
            # Neo4j operations
            entity_result = neo4j.create_entity({
                "id": "txn_test_1",
                "name": "Transaction Test",
                "type": "Test"
            })
            
            # SQLite operations
            provenance_result = sqlite.log_provenance({
                "object_id": "txn_test_1",
                "operation": "CREATE_ENTITY",
                "tool_id": "test_tool"
            })
            
            # Both should succeed together
            assert entity_result["status"] == "success"
            assert provenance_result["status"] == "success"
        
        # Verify both operations persisted
        assert neo4j.entity_exists("txn_test_1")
        assert len(sqlite.get_provenance("txn_test_1")["data"]) > 0
    
    def test_query_coordination(self, test_services):
        """Test queries spanning multiple databases."""
        # Create test data in both databases
        self._setup_test_data(test_services)
        
        # Query requiring both Neo4j and SQLite data
        query_manager = test_services.query_manager
        
        result = query_manager.execute_cross_database_query({
            "graph_query": "MATCH (e:Entity) RETURN e.id, e.confidence",
            "metadata_query": "SELECT object_id, confidence_score FROM quality_metrics",
            "join_on": "id"
        })
        
        assert result["status"] == "success"
        assert "combined_results" in result["data"]
        assert len(result["data"]["combined_results"]) > 0
```

### Service Integration Patterns
```python
class TestServiceIntegration:
    """Test service integration patterns."""
    
    def test_service_dependency_resolution(self, test_services):
        """Test service dependency resolution and initialization."""
        # Test that services are properly injected
        pipeline = PipelineOrchestrator(test_services)
        
        # Verify all required services are available
        assert hasattr(pipeline, 'identity_service')
        assert hasattr(pipeline, 'quality_service')
        assert hasattr(pipeline, 'provenance_service')
        assert hasattr(pipeline, 'pii_service')
        
        # Test service interaction
        test_entity = {"name": "Test Entity", "type": "Person"}
        
        # Should work through service dependencies
        result = pipeline.process_entity(test_entity)
        assert result["status"] == "success"
    
    def test_configuration_propagation(self, test_services):
        """Test configuration propagation across services."""
        # Update configuration
        config_manager = test_services.config_manager
        config_manager.update_setting("quality.confidence_threshold", 0.8)
        
        # Verify propagation to quality service
        quality_service = test_services.quality_service
        assert quality_service.confidence_threshold == 0.8
        
        # Test configuration-dependent behavior
        low_confidence_entity = {"name": "Test", "confidence": 0.7}
        high_confidence_entity = {"name": "Test", "confidence": 0.9}
        
        low_result = quality_service.assess_quality(low_confidence_entity)
        high_result = quality_service.assess_quality(high_confidence_entity)
        
        assert low_result["tier"] == "LOW"
        assert high_result["tier"] == "HIGH"
```

## Test Data Management

### Test Data Creation
```python
# tests/utils/test_data.py
def create_test_document(name: str, content_type: str = "academic") -> Dict[str, Any]:
    """Create test document with realistic content."""
    templates = {
        "academic": {
            "content": "Dr. Jane Smith from University of Example published research on machine learning.",
            "expected_entities": [
                {"name": "Dr. Jane Smith", "type": "Person"},
                {"name": "University of Example", "type": "Organization"},
                {"name": "machine learning", "type": "Topic"}
            ],
            "expected_relationships": [
                {"source": "Dr. Jane Smith", "target": "University of Example", "type": "affiliated_with"},
                {"source": "Dr. Jane Smith", "target": "machine learning", "type": "researches"}
            ]
        }
    }
    
    template = templates[content_type]
    return {
        "name": name,
        "content": template["content"],
        "path": f"test_data/{name}",
        "expected_entities": template["expected_entities"],
        "expected_relationships": template["expected_relationships"]
    }

def create_test_dataset(size: str = "small") -> List[Dict[str, Any]]:
    """Create test dataset of various sizes."""
    sizes = {
        "small": 3,
        "medium": 10,
        "large": 50
    }
    
    num_docs = sizes[size]
    return [create_test_document(f"test_doc_{i}.pdf") for i in range(num_docs)]
```

### Test Environment Setup
```python
# tests/utils/test_setup.py
def setup_test_environment() -> Dict[str, Any]:
    """Set up isolated test environment."""
    # Create temporary databases
    test_neo4j = setup_test_neo4j()
    test_sqlite = setup_test_sqlite()
    
    # Set test configuration
    os.environ["KGAS_TEST_MODE"] = "true"
    os.environ["KGAS_NEO4J_URI"] = test_neo4j["uri"]
    os.environ["KGAS_SQLITE_PATH"] = test_sqlite["path"]
    
    return {
        "neo4j": test_neo4j,
        "sqlite": test_sqlite,
        "cleanup": lambda: cleanup_test_environment(test_neo4j, test_sqlite)
    }

def cleanup_test_environment(neo4j_config: Dict, sqlite_config: Dict):
    """Clean up test environment after tests."""
    # Stop test Neo4j instance
    stop_test_neo4j(neo4j_config)
    
    # Remove test SQLite database
    Path(sqlite_config["path"]).unlink(missing_ok=True)
    
    # Clean environment variables
    del os.environ["KGAS_TEST_MODE"]
    del os.environ["KGAS_NEO4J_URI"]
    del os.environ["KGAS_SQLITE_PATH"]
```

## Running Integration Tests

### Test Execution Commands
```bash
# Run all integration tests
python -m pytest tests/integration/ -v

# Run specific test category
python -m pytest tests/integration/test_complete_pipeline.py -v

# Run with coverage
python -m pytest tests/integration/ --cov=src --cov-report=html

# Run slow tests (marked with @pytest.mark.slow)
python -m pytest tests/integration/ -m slow

# Run tests in parallel (if pytest-xdist installed)
python -m pytest tests/integration/ -n auto
```

### Test Configuration
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    database: marks tests that require database setup
    external: marks tests that require external services
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
```

## Performance Integration Testing

### Load Testing
```python
@pytest.mark.slow
def test_pipeline_load_performance(integration_environment):
    """Test pipeline performance under load."""
    services = integration_environment["services"]
    pipeline = PipelineOrchestrator(services)
    
    # Create load test data
    documents = create_test_dataset("large")  # 50 documents
    
    start_time = time.time()
    results = []
    
    for doc in documents:
        result = pipeline.process_document(doc["path"])
        results.append(result)
    
    processing_time = time.time() - start_time
    
    # Performance assertions
    assert all(r["status"] == "success" for r in results)
    assert processing_time < 300  # Should complete within 5 minutes
    assert len(results) == len(documents)
    
    # Calculate performance metrics
    avg_time_per_doc = processing_time / len(documents)
    assert avg_time_per_doc < 6  # Average < 6 seconds per document

@pytest.mark.slow
def test_concurrent_processing(integration_environment):
    """Test concurrent document processing."""
    import asyncio
    from src.tools.phase2.async_multi_document_processor import AsyncMultiDocumentProcessor
    
    services = integration_environment["services"]
    processor = AsyncMultiDocumentProcessor(services)
    
    documents = create_test_dataset("medium")  # 10 documents
    
    async def run_concurrent_test():
        start_time = time.time()
        results = await processor.process_documents_async([doc["path"] for doc in documents])
        processing_time = time.time() - start_time
        
        # Should be faster than sequential processing
        assert processing_time < len(documents) * 3  # Significant speedup expected
        assert all(r["status"] == "success" for r in results)
        
        return results
    
    results = asyncio.run(run_concurrent_test())
    assert len(results) == len(documents)
```

## Continuous Integration

### CI Integration Test Pipeline
```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    
    services:
      neo4j:
        image: neo4j:5.13
        env:
          NEO4J_AUTH: neo4j/testpassword
        ports:
          - 7687:7687
          - 7474:7474
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install -r requirements/test.txt
      
      - name: Wait for Neo4j
        run: |
          timeout 300 bash -c 'until curl -f http://localhost:7474; do sleep 5; done'
      
      - name: Run integration tests
        run: |
          python -m pytest tests/integration/ -v --cov=src --cov-report=xml
        env:
          NEO4J_URI: bolt://localhost:7687
          NEO4J_USERNAME: neo4j
          NEO4J_PASSWORD: testpassword
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## Best Practices

### Integration Test Guidelines
1. **Test Real Interactions**: Use actual service implementations, not mocks
2. **Isolated Environments**: Each test should have isolated data and state
3. **Realistic Data**: Use realistic test data that mirrors production scenarios
4. **Performance Awareness**: Include performance assertions for critical paths
5. **Error Scenarios**: Test error conditions and recovery mechanisms
6. **Resource Cleanup**: Always clean up resources after tests complete

### Debugging Integration Tests
```bash
# Run single test with detailed logging
python -m pytest tests/integration/test_complete_pipeline.py::TestPipelineIntegration::test_complete_pipeline_integration -v -s --log-cli-level=DEBUG

# Run with debugger on failure
python -m pytest tests/integration/ --pdb

# Generate detailed test report
python -m pytest tests/integration/ --html=report.html --self-contained-html
```

Integration tests are critical for ensuring that KGAS components work together correctly in realistic scenarios. Focus on testing actual component interactions, realistic data flows, and performance characteristics.