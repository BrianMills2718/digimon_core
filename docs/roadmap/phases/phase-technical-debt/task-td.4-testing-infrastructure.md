# Task TD.4: Testing Infrastructure Overhaul

## Overview
Achieve >95% test coverage with comprehensive testing infrastructure including unit, integration, and performance tests.

**Duration**: Weeks 7-8  
**Priority**: HIGH  
**Prerequisites**: Task TD.3 (AnyIO Migration) complete  

## Current Testing Gaps

### Coverage Issues
- **Critical files with 0% coverage**:
  - base_neo4j_tool.py
  - phase1_mcp_tools.py
  - Several monitoring modules
- **Overall coverage**: Inconsistent, many files <50%
- **Integration tests**: Limited end-to-end testing

### Testing Challenges
- Large classes impossible to test (2000+ line files)
- Tight coupling requires extensive mocking
- No automated performance regression testing
- Limited async testing patterns

## Implementation Plan

### Step 1: Testing Framework Enhancement (Day 1-2)

```python
# tests/conftest.py
import pytest
import anyio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
from src.core.service_container import ServiceContainer

@pytest.fixture
async def container() -> AsyncGenerator[ServiceContainer, None]:
    """Provide configured test container"""
    container = ServiceContainer()
    
    # Register test doubles
    container.register(IdentityServiceInterface, MockIdentityService)
    container.register(ProvenanceServiceInterface, MockProvenanceService)
    container.register(QualityServiceInterface, MockQualityService)
    
    yield container
    
    # Cleanup
    await container.dispose()

@pytest.fixture
def anyio_backend():
    """Use anyio for async tests"""
    return "asyncio"

@pytest.fixture
async def test_db() -> AsyncGenerator[TestDatabase, None]:
    """Provide test database"""
    db = TestDatabase()
    await db.setup()
    yield db
    await db.teardown()

# tests/fixtures/test_data.py
class TestDataFactory:
    """Factory for creating test data"""
    
    @staticmethod
    def create_document(content: str = "Test content") -> Document:
        return Document(
            id="test-doc-1",
            content=content,
            metadata={"source": "test"}
        )
    
    @staticmethod
    def create_chunk(text: str = "Test chunk") -> TextChunk:
        return TextChunk(
            id="test-chunk-1",
            text=text,
            start_pos=0,
            end_pos=len(text)
        )
    
    @staticmethod
    def create_entity(name: str = "Test Entity") -> Entity:
        return Entity(
            id="test-entity-1",
            name=name,
            type="PERSON",
            confidence=0.95
        )
```

### Step 2: Unit Test Coverage Expansion (Day 3-5)

```python
# tests/unit/orchestrators/test_document_processing_orchestrator.py
import pytest
from unittest.mock import AsyncMock, patch
from src.core.orchestrators.document_processing_orchestrator import DocumentProcessingOrchestrator

class TestDocumentProcessingOrchestrator:
    """Comprehensive unit tests for document processing"""
    
    @pytest.fixture
    async def orchestrator(self, container):
        """Create orchestrator with mocked dependencies"""
        return DocumentProcessingOrchestrator(container)
    
    async def test_process_single_document(self, orchestrator):
        """Test single document processing"""
        # Arrange
        doc_path = "test.pdf"
        expected_content = "Test content"
        
        with patch.object(orchestrator.pdf_loader, 'load_pdf') as mock_load:
            mock_load.return_value = expected_content
            
            # Act
            result = await orchestrator.process_document(doc_path)
            
            # Assert
            assert result.content == expected_content
            mock_load.assert_called_once_with(doc_path)
    
    async def test_parallel_document_processing(self, orchestrator):
        """Test parallel processing performance"""
        # Arrange
        docs = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
        
        with patch.object(orchestrator, 'process_document') as mock_process:
            mock_process.side_effect = [
                ProcessedDocument(f"content-{i}") 
                for i in range(len(docs))
            ]
            
            # Act
            results = await orchestrator.process_documents_parallel(docs)
            
            # Assert
            assert len(results) == len(docs)
            assert mock_process.call_count == len(docs)
    
    async def test_error_handling(self, orchestrator):
        """Test error handling in document processing"""
        # Arrange
        doc_path = "error.pdf"
        
        with patch.object(orchestrator.pdf_loader, 'load_pdf') as mock_load:
            mock_load.side_effect = FileNotFoundError("File not found")
            
            # Act & Assert
            with pytest.raises(ProcessingError) as exc_info:
                await orchestrator.process_document(doc_path)
            
            assert "File not found" in str(exc_info.value)
    
    @pytest.mark.parametrize("doc_count,expected_batches", [
        (5, 1),    # Single batch
        (15, 2),   # Two batches
        (100, 10), # Ten batches
    ])
    async def test_batch_processing(self, orchestrator, doc_count, expected_batches):
        """Test batch processing logic"""
        docs = [f"doc{i}.pdf" for i in range(doc_count)]
        
        with patch.object(orchestrator, '_process_batch') as mock_batch:
            await orchestrator.process_documents_parallel(docs)
            
            assert mock_batch.call_count == expected_batches

# tests/unit/tools/test_base_neo4j_tool.py
class TestBaseNeo4jTool:
    """Test base Neo4j tool functionality"""
    
    @pytest.fixture
    async def tool(self, container):
        """Create tool with test container"""
        from src.tools.phase1.base_neo4j_tool import BaseNeo4jTool
        return BaseNeo4jTool(container)
    
    async def test_connection_management(self, tool):
        """Test Neo4j connection lifecycle"""
        # Test connection
        assert not tool.is_connected()
        
        await tool.connect()
        assert tool.is_connected()
        
        await tool.disconnect()
        assert not tool.is_connected()
    
    async def test_query_execution(self, tool, test_db):
        """Test query execution"""
        # Setup test data
        await test_db.execute("CREATE (n:Test {name: 'test'})")
        
        # Execute query
        result = await tool.execute_query(
            "MATCH (n:Test) RETURN n.name as name"
        )
        
        assert len(result) == 1
        assert result[0]['name'] == 'test'
    
    async def test_transaction_rollback(self, tool, test_db):
        """Test transaction rollback on error"""
        async with tool.transaction() as tx:
            await tx.run("CREATE (n:Test {name: 'test'})")
            
            # Force error
            raise ValueError("Test error")
        
        # Verify rollback
        result = await tool.execute_query("MATCH (n:Test) RETURN count(n) as count")
        assert result[0]['count'] == 0
```

### Step 3: Integration Testing Framework (Day 6-7)

```python
# tests/integration/test_end_to_end_pipeline.py
import pytest
from pathlib import Path
from src.core.orchestrators.workflow_coordinator import WorkflowCoordinator

class TestEndToEndPipeline:
    """End-to-end pipeline integration tests"""
    
    @pytest.fixture
    async def coordinator(self, container):
        """Create workflow coordinator"""
        return WorkflowCoordinator(container)
    
    @pytest.mark.integration
    async def test_pdf_to_graph_pipeline(self, coordinator, tmp_path):
        """Test complete PDF to graph pipeline"""
        # Arrange - Create test PDF
        test_pdf = tmp_path / "test.pdf"
        create_test_pdf(test_pdf, content="John works at Acme Corp.")
        
        # Act - Run pipeline
        result = await coordinator.execute_workflow(
            workflow_type="pdf_to_graph",
            config={
                "input_files": [str(test_pdf)],
                "output_format": "neo4j"
            }
        )
        
        # Assert - Verify graph creation
        assert result.success
        assert len(result.entities) >= 2  # John, Acme Corp
        assert len(result.relationships) >= 1  # works_at
        
        # Verify in Neo4j
        graph_data = await coordinator.query_graph(
            "MATCH (p:PERSON)-[r:WORKS_AT]->(o:ORG) RETURN p, r, o"
        )
        assert len(graph_data) == 1
    
    @pytest.mark.integration
    async def test_multi_document_fusion(self, coordinator, tmp_path):
        """Test multi-document fusion pipeline"""
        # Create multiple test documents
        docs = []
        for i in range(3):
            doc = tmp_path / f"doc{i}.pdf"
            create_test_pdf(doc, content=f"Document {i} content")
            docs.append(str(doc))
        
        # Run fusion pipeline
        result = await coordinator.execute_workflow(
            workflow_type="multi_document_fusion",
            config={
                "input_files": docs,
                "fusion_strategy": "consensus"
            }
        )
        
        assert result.success
        assert result.fused_document is not None
        assert len(result.source_references) == 3
    
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_large_scale_processing(self, coordinator, large_dataset):
        """Test processing of large datasets"""
        # Process 100 documents
        result = await coordinator.execute_workflow(
            workflow_type="batch_processing",
            config={
                "input_directory": large_dataset,
                "parallel_workers": 10,
                "batch_size": 20
            }
        )
        
        assert result.success
        assert result.documents_processed == 100
        assert result.processing_time < 300  # 5 minutes max
```

### Step 4: Performance Testing Suite (Day 8-9)

```python
# tests/performance/test_performance_regression.py
import pytest
import time
from statistics import mean, stdev
from src.core.performance_monitor import PerformanceBaseline

class TestPerformanceRegression:
    """Automated performance regression testing"""
    
    @pytest.fixture
    def baseline(self):
        """Load performance baseline"""
        return PerformanceBaseline.load("baselines/current.json")
    
    @pytest.mark.performance
    async def test_document_processing_performance(self, orchestrator, baseline):
        """Test document processing doesn't regress"""
        # Run multiple iterations
        times = []
        for _ in range(10):
            start = time.time()
            await orchestrator.process_document("test.pdf")
            times.append(time.time() - start)
        
        avg_time = mean(times)
        baseline_time = baseline.get_metric("document_processing")
        
        # Allow 10% regression
        assert avg_time <= baseline_time * 1.1, \
            f"Performance regression: {avg_time:.3f}s vs {baseline_time:.3f}s baseline"
    
    @pytest.mark.performance
    async def test_parallel_scaling(self, orchestrator):
        """Test parallel processing scales properly"""
        results = {}
        
        for num_docs in [1, 5, 10, 20]:
            docs = [f"doc{i}.pdf" for i in range(num_docs)]
            
            start = time.time()
            await orchestrator.process_documents_parallel(docs)
            duration = time.time() - start
            
            results[num_docs] = duration
        
        # Verify sub-linear scaling
        # 20 docs should take less than 20x time of 1 doc
        assert results[20] < results[1] * 10
    
    @pytest.mark.performance
    @pytest.mark.memory
    async def test_memory_usage(self, orchestrator, memory_monitor):
        """Test memory usage stays within bounds"""
        # Monitor memory during processing
        with memory_monitor.track() as monitor:
            await orchestrator.process_large_document("large.pdf")
        
        # Check peak memory
        assert monitor.peak_memory < 500 * 1024 * 1024  # 500MB max
        
        # Check for leaks
        assert monitor.memory_leaked < 10 * 1024 * 1024  # 10MB tolerance

# tests/performance/conftest.py
@pytest.fixture
def memory_monitor():
    """Memory usage monitor"""
    return MemoryMonitor()

class MemoryMonitor:
    def track(self):
        return self
    
    def __enter__(self):
        self.start_memory = self._get_memory()
        self.peak_memory = self.start_memory
        return self
    
    def __exit__(self, *args):
        self.end_memory = self._get_memory()
        self.memory_leaked = self.end_memory - self.start_memory
    
    def _get_memory(self):
        import psutil
        return psutil.Process().memory_info().rss
```

### Step 5: Test Automation & CI Integration (Day 10-12)

```python
# .github/workflows/test-suite.yml
name: Comprehensive Test Suite

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run unit tests with coverage
        run: |
          pytest tests/unit -v --cov=src --cov-report=xml --cov-report=html
      
      - name: Check coverage threshold
        run: |
          coverage report --fail-under=95
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
  
  integration-tests:
    runs-on: ubuntu-latest
    services:
      neo4j:
        image: neo4j:latest
        env:
          NEO4J_AUTH: neo4j/testpassword
        options: >-
          --health-cmd "cypher-shell 'RETURN 1'"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      - name: Run integration tests
        run: |
          pytest tests/integration -v -m integration
  
  performance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Download baseline
        uses: actions/download-artifact@v3
        with:
          name: performance-baseline
      
      - name: Run performance tests
        run: |
          pytest tests/performance -v -m performance
      
      - name: Compare with baseline
        run: |
          python scripts/compare_performance.py current.json baseline.json
```

## Test Organization

### Directory Structure
```
tests/
├── unit/                    # Unit tests (isolated components)
│   ├── orchestrators/
│   ├── tools/
│   ├── services/
│   └── core/
├── integration/            # Integration tests (component interaction)
│   ├── pipelines/
│   ├── workflows/
│   └── services/
├── performance/            # Performance tests
│   ├── benchmarks/
│   └── regression/
├── fixtures/              # Shared test fixtures
├── data/                  # Test data files
└── conftest.py           # Pytest configuration
```

## Success Criteria

### Week 7 Completion
- [ ] Test framework enhanced with fixtures
- [ ] Unit test coverage >95% for core modules
- [ ] All zero-coverage files have tests
- [ ] Test data factory implemented

### Week 8 Completion
- [ ] Integration test suite complete
- [ ] Performance test suite automated
- [ ] CI/CD pipeline configured
- [ ] Coverage reporting automated
- [ ] Performance baselines established

## Coverage Targets

### Must Have 95%+ Coverage
- All orchestrator classes
- All service classes
- All tool implementations
- Core utilities

### Can Have Lower Coverage
- UI components (80%+)
- External integrations (70%+)
- Generated code (exempt)

## Testing Best Practices

### Unit Tests
```python
# Good: Focused, fast, isolated
async def test_entity_extraction():
    extractor = EntityExtractor()
    entities = await extractor.extract("John works at Acme")
    assert len(entities) == 2
    assert entities[0].name == "John"

# Bad: Too many concerns
async def test_everything():
    # Tests loading, extraction, graph building...
```

### Integration Tests
```python
# Good: Tests interaction between components
async def test_pdf_to_entities_flow():
    loader = PDFLoader()
    extractor = EntityExtractor()
    
    content = await loader.load("test.pdf")
    entities = await extractor.extract(content)
    
    assert entities  # Simple assertion

# Bad: Tests implementation details
```

### Performance Tests
```python
# Good: Measures specific metric
@pytest.mark.performance
async def test_processing_throughput():
    throughput = await measure_throughput()
    assert throughput > BASELINE_THROUGHPUT

# Bad: No clear performance target
```