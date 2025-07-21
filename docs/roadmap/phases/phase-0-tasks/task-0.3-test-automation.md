# Task 0.3: Test Automation Implementation

**Duration**: Day 5  
**Owner**: QA/DevOps Lead  
**Priority**: CRITICAL

## Objective

Create comprehensive automated test suite for end-to-end validation of the academic research pipeline, enabling continuous integration and regression testing.

## Implementation Plan

### Morning: Test Framework Setup

#### Step 1: Test Infrastructure
```python
# File: tests/integration/test_complete_pipeline.py

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any

from src.tools.phase1.t01_pdf_loader import PDFLoader
from src.tools.phase1.t15a_text_chunker import TextChunker
from src.tools.phase1.t15b_vector_embedder import VectorEmbedder
from src.tools.phase1.t23a_spacy_ner import SpacyNER
from src.tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor
from src.tools.phase1.t27_relationship_extractor import RelationshipExtractor
from src.tools.phase1.t31_entity_builder import EntityBuilder
from src.tools.phase1.t34_edge_builder import EdgeBuilder
from src.tools.phase1.t49_multihop_query import MultiHopQuery
from src.tools.phase3.t301_multi_document_fusion import T301MultiDocumentFusionTool
from src.core.neo4j_manager import Neo4jManager
from src.core.service_manager import ServiceManager

class TestCompletePipeline:
    """End-to-end integration tests for KGAS academic pipeline"""
    
    @pytest.fixture(scope="class")
    def test_environment(self):
        """Set up test environment with isolated databases"""
        # Create temporary directories
        temp_dir = tempfile.mkdtemp()
        
        # Initialize test services
        config = {
            'neo4j_uri': 'bolt://localhost:7687',
            'neo4j_user': 'neo4j',
            'neo4j_password': 'test_password',
            'neo4j_database': 'test_db',
            'qdrant_host': 'localhost',
            'qdrant_port': 6333,
            'qdrant_collection': 'test_collection'
        }
        
        service_manager = ServiceManager(config)
        
        yield {
            'temp_dir': temp_dir,
            'service_manager': service_manager,
            'config': config
        }
        
        # Cleanup
        shutil.rmtree(temp_dir)
        # Clear test database
        service_manager.cleanup_test_data()
    
    @pytest.fixture
    def sample_pdf(self, test_environment):
        """Provide sample PDF for testing"""
        # Copy test PDF to temp directory
        test_pdf = Path(__file__).parent / 'fixtures' / 'sample_research_paper.pdf'
        temp_pdf = Path(test_environment['temp_dir']) / 'test_paper.pdf'
        shutil.copy(test_pdf, temp_pdf)
        return str(temp_pdf)
    
    @pytest.fixture
    def sample_ontology(self):
        """Provide test ontology"""
        return {
            "entities": {
                "Researcher": {
                    "properties": ["name", "affiliation", "email"]
                },
                "Method": {
                    "properties": ["name", "type", "accuracy"]
                },
                "Dataset": {
                    "properties": ["name", "size", "domain"]
                }
            },
            "relationships": {
                "AUTHORED_BY": {
                    "source": "Paper",
                    "target": "Researcher"
                },
                "USES_METHOD": {
                    "source": "Paper",
                    "target": "Method"
                }
            }
        }
```

#### Step 2: Core Pipeline Tests
```python
# Continuation of test_complete_pipeline.py

    def test_document_processing_pipeline(self, test_environment, sample_pdf):
        """Test complete document processing pipeline"""
        
        # Initialize tools
        pdf_loader = PDFLoader()
        text_chunker = TextChunker()
        vector_embedder = VectorEmbedder()
        
        # Step 1: Load PDF
        pdf_result = pdf_loader.execute({
            'input_data': {'file_path': sample_pdf},
            'context': {'validation_mode': False}
        })
        
        assert pdf_result['status'] == 'success'
        assert 'text' in pdf_result['results']
        assert len(pdf_result['results']['text']) > 0
        
        # Step 2: Chunk text
        chunk_result = text_chunker.execute({
            'input_data': {
                'text': pdf_result['results']['text'],
                'chunk_size': 512,
                'overlap': 50
            },
            'context': {'source_document': sample_pdf}
        })
        
        assert chunk_result['status'] == 'success'
        assert 'chunks' in chunk_result['results']
        assert len(chunk_result['results']['chunks']) > 0
        
        # Step 3: Create embeddings
        embed_result = vector_embedder.execute({
            'input_data': {'chunks': chunk_result['results']['chunks']},
            'context': {'model': 'all-MiniLM-L6-v2'}
        })
        
        assert embed_result['status'] == 'success'
        assert 'embeddings' in embed_result['results']
        assert len(embed_result['results']['embeddings']) == len(chunk_result['results']['chunks'])
        
        return {
            'text': pdf_result['results']['text'],
            'chunks': chunk_result['results']['chunks'],
            'embeddings': embed_result['results']['embeddings']
        }
    
    @pytest.mark.asyncio
    async def test_entity_extraction_comparison(self, test_environment, sample_ontology):
        """Test and compare SpaCy vs LLM extraction"""
        
        test_text = """
        Dr. Jane Smith from MIT developed a new machine learning method called 
        TransformerXL that achieves 95% accuracy on the GLUE benchmark dataset.
        """
        
        # SpaCy extraction
        spacy_ner = SpacyNER()
        spacy_result = spacy_ner.execute({
            'input_data': {'text': test_text},
            'context': {}
        })
        
        # LLM extraction with ontology
        llm_extractor = OntologyAwareExtractor()
        llm_result = await llm_extractor.execute({
            'input_data': {'text': test_text},
            'context': {'ontology': sample_ontology}
        })
        
        # Validate both extractions
        assert spacy_result['status'] == 'success'
        assert llm_result['status'] == 'success'
        
        # Compare results
        spacy_entities = spacy_result['results']['entities']
        llm_entities = llm_result['results']['entities']
        
        # LLM should identify domain-specific entities
        llm_entity_types = {e['type'] for e in llm_entities}
        assert 'Method' in llm_entity_types
        assert 'Dataset' in llm_entity_types
        assert 'Researcher' in llm_entity_types
        
        # Log comparison metrics
        print(f"SpaCy found {len(spacy_entities)} entities")
        print(f"LLM found {len(llm_entities)} entities")
        print(f"LLM-only entities: {len(llm_entities) - len(spacy_entities)}")
        
        return {
            'spacy': spacy_entities,
            'llm': llm_entities
        }
```

#### Step 3: Graph Construction Tests
```python
# File: tests/integration/test_graph_construction.py

class TestGraphConstruction:
    """Test knowledge graph construction and analysis"""
    
    def test_entity_and_relationship_building(self, test_environment, extracted_entities):
        """Test graph construction from extracted entities"""
        
        # Initialize builders
        entity_builder = EntityBuilder()
        edge_builder = EdgeBuilder()
        
        # Build entities
        entity_result = entity_builder.execute({
            'input_data': {
                'entities': extracted_entities['llm']
            },
            'context': {
                'source_document': 'test_paper.pdf',
                'confidence_threshold': 0.7
            }
        })
        
        assert entity_result['status'] == 'success'
        assert 'created_nodes' in entity_result['results']
        assert entity_result['results']['created_nodes'] > 0
        
        # Extract relationships
        rel_extractor = RelationshipExtractor()
        rel_result = rel_extractor.execute({
            'input_data': {
                'text': test_text,
                'entities': extracted_entities['llm']
            },
            'context': {}
        })
        
        # Build edges
        edge_result = edge_builder.execute({
            'input_data': {
                'relationships': rel_result['results']['relationships'],
                'entity_map': entity_result['results']['entity_map']
            },
            'context': {}
        })
        
        assert edge_result['status'] == 'success'
        assert 'created_edges' in edge_result['results']
        
        return {
            'nodes': entity_result['results']['created_nodes'],
            'edges': edge_result['results']['created_edges'],
            'graph_id': entity_result['results']['graph_id']
        }
    
    def test_multi_hop_queries(self, test_environment, constructed_graph):
        """Test multi-hop query functionality"""
        
        query_tool = MultiHopQuery()
        
        test_queries = [
            {
                'query': 'Find all methods used by researchers from MIT',
                'max_hops': 2
            },
            {
                'query': 'What datasets are used to evaluate TransformerXL?',
                'max_hops': 3
            }
        ]
        
        for test_query in test_queries:
            result = query_tool.execute({
                'input_data': {
                    'query': test_query['query'],
                    'graph_id': constructed_graph['graph_id'],
                    'max_hops': test_query['max_hops']
                },
                'context': {}
            })
            
            assert result['status'] == 'success'
            assert 'paths' in result['results']
            assert 'interpretation' in result['results']
```

### Afternoon: End-to-End Workflow & CI/CD

#### Step 4: Complete Workflow Test
```python
# File: tests/integration/test_end_to_end_workflow.py

class TestEndToEndWorkflow:
    """Test complete academic research workflow"""
    
    @pytest.mark.integration
    @pytest.mark.timeout(300)  # 5 minute timeout
    def test_full_academic_workflow(self, test_environment, sample_pdf, sample_ontology):
        """Test complete pipeline from PDF to exports"""
        
        workflow_steps = []
        
        try:
            # Step 1: Document Processing
            start_time = time.time()
            processing_result = self.process_document(sample_pdf)
            workflow_steps.append({
                'step': 'document_processing',
                'duration': time.time() - start_time,
                'status': 'success'
            })
            
            # Step 2: Entity Extraction (LLM)
            start_time = time.time()
            extraction_result = self.extract_entities_llm(
                processing_result['chunks'],
                sample_ontology
            )
            workflow_steps.append({
                'step': 'entity_extraction',
                'duration': time.time() - start_time,
                'entity_count': len(extraction_result['entities'])
            })
            
            # Step 3: Graph Construction
            start_time = time.time()
            graph_result = self.build_knowledge_graph(
                extraction_result['entities'],
                extraction_result['relationships']
            )
            workflow_steps.append({
                'step': 'graph_construction',
                'duration': time.time() - start_time,
                'node_count': graph_result['nodes'],
                'edge_count': graph_result['edges']
            })
            
            # Step 4: Analysis
            start_time = time.time()
            analysis_result = self.analyze_graph(graph_result['graph_id'])
            workflow_steps.append({
                'step': 'graph_analysis',
                'duration': time.time() - start_time,
                'insights_count': len(analysis_result['insights'])
            })
            
            # Step 5: Export
            start_time = time.time()
            export_result = self.export_results(
                graph_result['graph_id'],
                analysis_result
            )
            workflow_steps.append({
                'step': 'export_generation',
                'duration': time.time() - start_time,
                'formats': list(export_result.keys())
            })
            
            # Validate complete workflow
            self.validate_workflow_results(workflow_steps, export_result)
            
        except Exception as e:
            pytest.fail(f"Workflow failed at step {len(workflow_steps)}: {str(e)}")
        
        # Generate performance report
        self.generate_performance_report(workflow_steps)
    
    def validate_workflow_results(self, steps, exports):
        """Validate all workflow outputs"""
        
        # Check all steps completed
        expected_steps = [
            'document_processing',
            'entity_extraction',
            'graph_construction',
            'graph_analysis',
            'export_generation'
        ]
        
        actual_steps = [s['step'] for s in steps]
        assert actual_steps == expected_steps
        
        # Validate exports
        assert 'csv' in exports
        assert 'latex' in exports
        assert 'bibtex' in exports
        assert 'json' in exports
        
        # Validate LaTeX compiles
        with tempfile.NamedTemporaryFile(suffix='.tex', mode='w') as f:
            f.write(exports['latex'])
            f.flush()
            
            # Try to compile LaTeX
            result = subprocess.run(
                ['pdflatex', f.name],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, "LaTeX compilation failed"
        
        # Validate JSON structure
        graph_data = json.loads(exports['json'])
        assert 'nodes' in graph_data
        assert 'edges' in graph_data
        assert 'metadata' in graph_data
```

#### Step 5: CI/CD Configuration
```yaml
# File: .github/workflows/integration-tests.yml

name: Integration Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    
    services:
      neo4j:
        image: neo4j:5.13
        env:
          NEO4J_AUTH: neo4j/test_password
          NEO4J_PLUGINS: '["apoc", "graph-data-science"]'
        ports:
          - 7687:7687
        options: >-
          --health-cmd "cypher-shell -u neo4j -p test_password 'RETURN 1'"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      qdrant:
        image: qdrant/qdrant
        ports:
          - 6333:6333
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        python -m spacy download en_core_web_sm
    
    - name: Set up test environment
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        NEO4J_PASSWORD: test_password
      run: |
        cp .env.example .env
        echo "NEO4J_PASSWORD=$NEO4J_PASSWORD" >> .env
        echo "OPENAI_API_KEY=$OPENAI_API_KEY" >> .env
    
    - name: Run integration tests
      run: |
        pytest tests/integration/test_complete_pipeline.py -v --tb=short
        pytest tests/integration/test_graph_construction.py -v --tb=short
        pytest tests/integration/test_end_to_end_workflow.py -v --tb=short
    
    - name: Generate coverage report
      run: |
        pytest --cov=src --cov-report=xml --cov-report=html
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: integration
    
    - name: Archive test reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-reports
        path: |
          htmlcov/
          test_results/
          performance_reports/
```

#### Step 6: Performance Benchmarking
```python
# File: tests/integration/test_performance_benchmarks.py

class PerformanceBenchmarks:
    """Track performance metrics over time"""
    
    PERFORMANCE_THRESHOLDS = {
        'pdf_processing_per_page': 2.0,  # seconds
        'entity_extraction_per_chunk': 1.0,  # seconds
        'graph_construction_per_100_entities': 5.0,  # seconds
        'export_generation': 10.0,  # seconds total
    }
    
    def test_pdf_processing_performance(self, benchmark, sample_pdf):
        """Benchmark PDF processing speed"""
        
        pdf_loader = PDFLoader()
        
        def process_pdf():
            return pdf_loader.execute({
                'input_data': {'file_path': sample_pdf},
                'context': {}
            })
        
        # Run benchmark
        result = benchmark(process_pdf)
        
        # Check against threshold
        pages = self.get_pdf_page_count(sample_pdf)
        time_per_page = result.stats.mean / pages
        
        assert time_per_page < self.PERFORMANCE_THRESHOLDS['pdf_processing_per_page'], \
            f"PDF processing too slow: {time_per_page:.2f}s per page"
    
    def test_complete_pipeline_performance(self, benchmark, sample_pdf):
        """Benchmark complete pipeline performance"""
        
        def run_pipeline():
            # Complete pipeline execution
            return self.execute_complete_pipeline(sample_pdf)
        
        # Run benchmark
        result = benchmark.pedantic(
            run_pipeline,
            rounds=3,
            warmup_rounds=1
        )
        
        # Generate performance report
        report = {
            'mean_time': result.stats.mean,
            'std_dev': result.stats.stddev,
            'min_time': result.stats.min,
            'max_time': result.stats.max,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to tracking file
        self.save_performance_history(report)
        
        # Check for performance regression
        self.check_performance_regression(report)
```

## Deliverables

### Test Suite Components
1. **Integration Tests** (tests/integration/)
   - Complete pipeline test
   - Component integration tests
   - Error handling tests
   - Performance benchmarks

2. **CI/CD Configuration**
   - GitHub Actions workflow
   - Docker compose for test services
   - Environment setup scripts

3. **Test Documentation**
   - Test plan document
   - Coverage report
   - Performance baselines

### Test Metrics
- [ ] Code coverage >80%
- [ ] All critical paths tested
- [ ] Performance benchmarks established
- [ ] CI/CD pipeline green

## Success Criteria

- [ ] Automated tests run in <10 minutes
- [ ] All tests pass consistently
- [ ] Performance within thresholds
- [ ] CI/CD integrated with PR process
- [ ] Test results easily accessible