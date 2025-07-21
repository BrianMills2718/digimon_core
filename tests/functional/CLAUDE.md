# Functional Testing - CLAUDE.md

## Overview
The `tests/functional/` directory contains functional tests that validate end-to-end user workflows and system behavior from a user perspective. These tests ensure that KGAS delivers the expected functionality for real research scenarios and use cases.

## Directory Structure

### Current State
```
tests/functional/
├── test_integration_complete.py     # Complete workflow validation
├── test_mcp_tools_complete.py       # MCP tool functionality testing
├── test_mcp_tools_live.py          # Live MCP integration testing
├── test_pdf_workflow_complete.py    # PDF processing workflow testing
├── test_phase2_integration.py       # Phase 2 feature testing
├── test_ui_complete.py             # UI functionality testing
└── archived_experimental/          # Archived redundant tests
    └── functional_redundant/        # Previously redundant functional tests
```

### Test Categories

#### **End-to-End Workflow Tests**
- **Complete research workflows**: Full document-to-insight pipelines
- **Multi-document analysis**: Cross-document analysis and fusion
- **Cross-modal analysis**: Graph ↔ Table ↔ Vector workflow validation
- **Theory-aware processing**: Domain-specific analysis workflows

#### **User Interface Tests**
- **Streamlit UI functionality**: Complete UI interaction testing
- **Workflow orchestration**: User-driven workflow execution
- **Visualization testing**: Graph and data visualization validation
- **Export functionality**: Data export and report generation

#### **MCP Tool Tests**
- **Tool availability**: All tools accessible via MCP protocol
- **Tool functionality**: Each tool performs as specified
- **Tool integration**: Tools work together in workflows
- **Error handling**: Tool error scenarios and recovery

#### **Research Scenario Tests**
- **Academic use cases**: Real academic research scenarios
- **Data quality validation**: Quality assessment across workflows
- **Performance requirements**: Workflow performance validation
- **Reproducibility**: Consistent results across runs

## Functional Testing Patterns

### Research Workflow Test Template
```python
import pytest
from typing import Dict, Any, List
from pathlib import Path
import time

# System imports
from src.core.service_manager import ServiceManager
from src.core.pipeline_orchestrator import PipelineOrchestrator
from src.core.analytics_service import AnalyticsService

# UI testing imports
import streamlit as st
from streamlit.testing.v1 import AppTest

# Test utilities
from tests.utils.functional_data import create_research_scenario
from tests.utils.assertions import assert_research_quality

class TestResearchWorkflow:
    """
    Functional test for complete research workflows.
    
    Tests real user scenarios from document upload
    to research insights and export.
    """
    
    @pytest.fixture(scope="class")
    def research_environment(self):
        """Set up research environment with real data."""
        # Initialize system
        services = ServiceManager()
        
        # Create research scenario
        scenario = create_research_scenario("multi_author_collaboration")
        
        return {
            "services": services,
            "scenario": scenario,
            "docs": scenario["documents"],
            "expected_insights": scenario["expected_insights"]
        }
    
    def test_complete_research_workflow(self, research_environment):
        """Test complete research workflow from documents to insights."""
        services = research_environment["services"]
        scenario = research_environment["scenario"]
        
        # Step 1: Document Processing
        pipeline = PipelineOrchestrator(services)
        processing_results = []
        
        for doc in scenario["documents"]:
            result = pipeline.process_document(doc["path"])
            assert result["status"] == "success", f"Failed to process {doc['name']}"
            assert "entities" in result["data"]
            assert "relationships" in result["data"]
            processing_results.append(result)
        
        # Step 2: Multi-Document Fusion
        analytics = AnalyticsService(services)
        fusion_result = analytics.fuse_documents(processing_results)
        
        assert fusion_result["status"] == "success"
        assert "unified_graph" in fusion_result["data"]
        
        # Step 3: Cross-Modal Analysis
        graph_data = fusion_result["data"]["unified_graph"]
        
        # Graph analysis
        graph_insights = analytics.analyze_graph_patterns(graph_data)
        assert graph_insights["status"] == "success"
        
        # Table analysis
        table_data = analytics.convert_to_table(graph_data)
        table_insights = analytics.analyze_table_statistics(table_data["data"]["dataframe"])
        assert table_insights["status"] == "success"
        
        # Vector analysis
        vector_data = analytics.convert_to_vectors(graph_data)
        vector_insights = analytics.analyze_vector_similarity(vector_data["data"]["embeddings"])
        assert vector_insights["status"] == "success"
        
        # Step 4: Validate Research Quality
        research_results = {
            "graph_insights": graph_insights["data"],
            "table_insights": table_insights["data"],
            "vector_insights": vector_insights["data"],
            "unified_graph": graph_data
        }
        
        # Custom research quality assertions
        assert_research_quality(research_results, scenario["expected_insights"])
    
    def test_theory_aware_workflow(self, research_environment):
        """Test theory-aware research workflow."""
        services = research_environment["services"]
        
        # Create theory-specific scenario
        theory_scenario = create_research_scenario("social_network_analysis")
        
        # Step 1: Theory Selection and Ontology Generation
        theory_service = services.theory_repository
        ontology_result = theory_service.generate_ontology(
            domain="social network analysis",
            user_conversation="Analyze collaboration patterns in academic networks"
        )
        
        assert ontology_result["status"] == "success"
        theory_id = ontology_result["data"]["theory_id"]
        
        # Step 2: Theory-Aware Processing
        pipeline = PipelineOrchestrator(services)
        pipeline.set_theory_context(theory_id)
        
        theory_results = []
        for doc in theory_scenario["documents"]:
            result = pipeline.process_document_with_theory(doc["path"], theory_id)
            assert result["status"] == "success"
            assert result["data"]["theory_compliance"]["theory_id"] == theory_id
            theory_results.append(result)
        
        # Step 3: Theory-Specific Analysis
        analytics = AnalyticsService(services)
        theory_analysis = analytics.analyze_with_theory(theory_results, theory_id)
        
        assert theory_analysis["status"] == "success"
        assert "theory_specific_insights" in theory_analysis["data"]
        
        # Validate theory compliance
        for insight in theory_analysis["data"]["theory_specific_insights"]:
            assert "ontology_alignment" in insight
            assert insight["ontology_alignment"]["theory_id"] == theory_id
    
    @pytest.mark.slow
    def test_performance_requirements(self, research_environment):
        """Test workflow performance meets requirements."""
        services = research_environment["services"]
        scenario = research_environment["scenario"]
        
        # Performance requirements
        max_processing_time_per_doc = 30  # seconds
        max_total_workflow_time = 300     # seconds (5 minutes)
        min_entity_extraction_rate = 5    # entities per page minimum
        
        start_time = time.time()
        
        pipeline = PipelineOrchestrator(services)
        analytics = AnalyticsService(services)
        
        # Process documents with timing
        doc_times = []
        all_results = []
        
        for doc in scenario["documents"]:
            doc_start = time.time()
            result = pipeline.process_document(doc["path"])
            doc_time = time.time() - doc_start
            
            assert result["status"] == "success"
            assert doc_time < max_processing_time_per_doc
            
            doc_times.append(doc_time)
            all_results.append(result)
            
            # Validate extraction rate
            entity_count = len(result["data"]["entities"])
            page_count = result["data"]["metadata"].get("page_count", 1)
            extraction_rate = entity_count / page_count
            
            assert extraction_rate >= min_entity_extraction_rate
        
        # Multi-document fusion with timing
        fusion_start = time.time()
        fusion_result = analytics.fuse_documents(all_results)
        fusion_time = time.time() - fusion_start
        
        assert fusion_result["status"] == "success"
        assert fusion_time < 60  # Fusion should complete within 1 minute
        
        # Total workflow time
        total_time = time.time() - start_time
        assert total_time < max_total_workflow_time
        
        # Performance metrics
        avg_doc_time = sum(doc_times) / len(doc_times)
        print(f"Performance Metrics:")
        print(f"  Average document processing time: {avg_doc_time:.2f}s")
        print(f"  Multi-document fusion time: {fusion_time:.2f}s")
        print(f"  Total workflow time: {total_time:.2f}s")
```

### UI Functional Testing
```python
class TestStreamlitUI:
    """Test Streamlit UI functionality."""
    
    def test_document_upload_workflow(self):
        """Test complete document upload and processing workflow."""
        # Initialize Streamlit app test
        app = AppTest.from_file("streamlit_app.py")
        app.run()
        
        # Check initial state
        assert not app.exception
        assert "KGAS - Knowledge Graph Analysis System" in app.title[0].value
        
        # Simulate file upload
        test_file = Path("test_data/sample_paper.pdf")
        app.file_uploader[0].upload_file(test_file)
        app.button[0].click()  # Process button
        
        # Wait for processing
        app.run()
        
        # Check results
        assert "Processing completed successfully" in app.success[0].value
        assert len(app.dataframe) > 0  # Results displayed
        
        # Test graph visualization
        assert len(app.plotly_chart) > 0  # Graph displayed
        
        # Test export functionality
        app.download_button[0].click()
        assert app.download_button[0].url is not None
    
    def test_interactive_analysis_workflow(self):
        """Test interactive analysis features."""
        app = AppTest.from_file("streamlit_app.py")
        app.run()
        
        # Load pre-processed data
        app.selectbox[0].select("Load Sample Data").click()
        app.run()
        
        # Test different analysis modes
        analysis_modes = ["Graph Analysis", "Table Analysis", "Vector Analysis"]
        
        for mode in analysis_modes:
            app.selectbox[1].select(mode)
            app.button[1].click()  # Analyze button
            app.run()
            
            # Verify results for each mode
            assert len(app.json) > 0  # Analysis results
            if mode == "Graph Analysis":
                assert len(app.plotly_chart) > 0  # Graph visualization
            elif mode == "Table Analysis":
                assert len(app.dataframe) > 0  # Table data
            elif mode == "Vector Analysis":
                assert len(app.scatter_chart) > 0  # Vector visualization
    
    def test_cross_modal_conversion_ui(self):
        """Test cross-modal conversion in UI."""
        app = AppTest.from_file("streamlit_app.py")
        app.run()
        
        # Load sample graph data
        app.selectbox[0].select("Load Sample Graph").click()
        app.run()
        
        # Test format conversions
        conversions = [
            ("Graph to Table", "dataframe"),
            ("Graph to Vector", "scatter_chart"),
            ("Table to Graph", "plotly_chart")
        ]
        
        for conversion, expected_component in conversions:
            app.selectbox[2].select(conversion)
            app.button[2].click()  # Convert button
            app.run()
            
            # Verify conversion results
            assert len(getattr(app, expected_component)) > 0
            assert "Conversion completed successfully" in app.success[0].value
```

### MCP Tool Functional Testing
```python
class TestMCPToolFunctionality:
    """Test MCP tool functionality end-to-end."""
    
    @pytest.fixture(scope="class")
    def mcp_environment(self):
        """Set up MCP testing environment."""
        from src.tools.phase1.phase1_mcp_tools import app as phase1_app
        from src.tools.phase2.phase2_mcp_tools import app as phase2_app
        
        return {
            "phase1_tools": phase1_app,
            "phase2_tools": phase2_app,
            "test_docs": create_test_document_set()
        }
    
    def test_pdf_processing_mcp_workflow(self, mcp_environment):
        """Test complete PDF processing workflow via MCP."""
        phase1_tools = mcp_environment["phase1_tools"]
        test_doc = mcp_environment["test_docs"]["academic_paper"]
        
        # Step 1: Load PDF
        pdf_result = phase1_tools.call_tool("load_pdf", {
            "file_path": test_doc["path"]
        })
        assert pdf_result["status"] == "success"
        assert "text_content" in pdf_result["data"]
        
        # Step 2: Chunk text
        chunk_result = phase1_tools.call_tool("chunk_text", {
            "text": pdf_result["data"]["text_content"],
            "chunk_size": 1000,
            "overlap": 200
        })
        assert chunk_result["status"] == "success"
        assert len(chunk_result["data"]["chunks"]) > 0
        
        # Step 3: Extract entities
        entities_result = phase1_tools.call_tool("extract_entities_spacy", {
            "text": pdf_result["data"]["text_content"]
        })
        assert entities_result["status"] == "success"
        assert len(entities_result["data"]["entities"]) > 0
        
        # Step 4: Extract relationships
        relationships_result = phase1_tools.call_tool("extract_relationships", {
            "text": pdf_result["data"]["text_content"],
            "entities": entities_result["data"]["entities"]
        })
        assert relationships_result["status"] == "success"
        
        # Step 5: Build graph
        graph_result = phase1_tools.call_tool("build_entity_graph", {
            "entities": entities_result["data"]["entities"],
            "relationships": relationships_result["data"]["relationships"]
        })
        assert graph_result["status"] == "success"
        assert "graph_data" in graph_result["data"]
    
    def test_multi_document_mcp_workflow(self, mcp_environment):
        """Test multi-document processing via MCP."""
        phase2_tools = mcp_environment["phase2_tools"]
        test_docs = [
            mcp_environment["test_docs"]["paper_1"],
            mcp_environment["test_docs"]["paper_2"]
        ]
        
        # Process multiple documents
        multi_doc_result = phase2_tools.call_tool("process_multiple_documents", {
            "file_paths": [doc["path"] for doc in test_docs],
            "fusion_enabled": True
        })
        
        assert multi_doc_result["status"] == "success"
        assert "individual_results" in multi_doc_result["data"]
        assert "fusion_result" in multi_doc_result["data"]
        assert len(multi_doc_result["data"]["individual_results"]) == 2
        
        # Verify cross-document connections
        fusion_data = multi_doc_result["data"]["fusion_result"]
        assert "cross_document_entities" in fusion_data
        assert len(fusion_data["cross_document_entities"]) > 0
    
    def test_theory_aware_mcp_workflow(self, mcp_environment):
        """Test theory-aware processing via MCP."""
        phase2_tools = mcp_environment["phase2_tools"]
        test_doc = mcp_environment["test_docs"]["domain_specific"]
        
        # Generate ontology
        ontology_result = phase2_tools.call_tool("generate_ontology", {
            "domain": "machine learning",
            "conversation": "Analyze ML research papers for algorithmic innovation patterns"
        })
        assert ontology_result["status"] == "success"
        theory_id = ontology_result["data"]["theory_id"]
        
        # Process with theory
        theory_processing_result = phase2_tools.call_tool("extract_entities_with_ontology", {
            "file_path": test_doc["path"],
            "theory_id": theory_id
        })
        
        assert theory_processing_result["status"] == "success"
        assert "theory_compliant_entities" in theory_processing_result["data"]
        
        # Verify theory compliance
        for entity in theory_processing_result["data"]["theory_compliant_entities"]:
            assert "ontology_alignment" in entity
            assert entity["ontology_alignment"]["theory_id"] == theory_id
```

### Research Scenario Testing
```python
class TestResearchScenarios:
    """Test realistic research scenarios."""
    
    def test_literature_review_scenario(self):
        """Test literature review research scenario."""
        # Scenario: Researcher analyzing 10 papers on a specific topic
        scenario = create_research_scenario("literature_review", {
            "topic": "transformer neural networks",
            "paper_count": 10,
            "expected_themes": ["attention mechanism", "self-attention", "BERT", "GPT"]
        })
        
        services = ServiceManager()
        pipeline = PipelineOrchestrator(services)
        analytics = AnalyticsService(services)
        
        # Process all papers
        paper_results = []
        for paper in scenario["papers"]:
            result = pipeline.process_document(paper["path"])
            assert result["status"] == "success"
            paper_results.append(result)
        
        # Multi-document fusion
        fusion_result = analytics.fuse_documents(paper_results)
        assert fusion_result["status"] == "success"
        
        # Theme analysis
        theme_analysis = analytics.analyze_themes(fusion_result["data"]["unified_graph"])
        assert theme_analysis["status"] == "success"
        
        # Verify expected themes found
        found_themes = set(theme["name"] for theme in theme_analysis["data"]["themes"])
        expected_themes = set(scenario["expected_themes"])
        
        # Should find at least 70% of expected themes
        theme_overlap = len(found_themes.intersection(expected_themes)) / len(expected_themes)
        assert theme_overlap >= 0.7
    
    def test_collaboration_network_analysis(self):
        """Test collaboration network analysis scenario."""
        scenario = create_research_scenario("collaboration_analysis", {
            "focus": "academic collaboration patterns",
            "author_count": 25,
            "institution_count": 8
        })
        
        services = ServiceManager()
        pipeline = PipelineOrchestrator(services)
        analytics = AnalyticsService(services)
        
        # Process collaboration data
        results = []
        for doc in scenario["documents"]:
            result = pipeline.process_document(doc["path"])
            assert result["status"] == "success"
            results.append(result)
        
        # Build collaboration network
        fusion_result = analytics.fuse_documents(results)
        collaboration_network = analytics.build_collaboration_network(
            fusion_result["data"]["unified_graph"]
        )
        
        assert collaboration_network["status"] == "success"
        network_data = collaboration_network["data"]
        
        # Network analysis
        network_metrics = analytics.analyze_network_metrics(network_data)
        assert network_metrics["status"] == "success"
        
        # Verify network properties
        assert network_metrics["data"]["author_count"] >= scenario["author_count"] * 0.8
        assert network_metrics["data"]["institution_count"] >= scenario["institution_count"] * 0.8
        assert network_metrics["data"]["avg_collaboration_degree"] > 1.0
    
    def test_concept_evolution_analysis(self):
        """Test concept evolution analysis scenario."""
        scenario = create_research_scenario("concept_evolution", {
            "concept": "artificial intelligence",
            "time_span": "2010-2024",
            "paper_count": 15
        })
        
        services = ServiceManager()
        pipeline = PipelineOrchestrator(services)
        analytics = AnalyticsService(services)
        
        # Process papers with temporal context
        temporal_results = []
        for paper in scenario["papers"]:
            result = pipeline.process_document(paper["path"])
            # Add temporal metadata
            result["data"]["temporal_metadata"] = {
                "publication_year": paper["year"],
                "time_period": paper["period"]
            }
            temporal_results.append(result)
        
        # Temporal fusion
        temporal_fusion = analytics.fuse_documents_with_temporal_context(temporal_results)
        assert temporal_fusion["status"] == "success"
        
        # Concept evolution analysis
        evolution_analysis = analytics.analyze_concept_evolution(
            temporal_fusion["data"]["temporal_graph"],
            concept=scenario["concept"]
        )
        
        assert evolution_analysis["status"] == "success"
        evolution_data = evolution_analysis["data"]
        
        # Verify evolution patterns
        assert "temporal_trends" in evolution_data
        assert "concept_relationships" in evolution_data
        assert len(evolution_data["temporal_trends"]) > 0
        
        # Should detect evolution over time
        time_periods = set(trend["period"] for trend in evolution_data["temporal_trends"])
        assert len(time_periods) >= 3  # Multiple time periods detected
```

## Test Data and Scenarios

### Research Scenario Creation
```python
# tests/utils/functional_data.py
def create_research_scenario(scenario_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create realistic research scenarios for functional testing."""
    
    scenarios = {
        "multi_author_collaboration": {
            "description": "Multi-author paper analysis with collaboration patterns",
            "documents": [
                create_academic_paper("Smith et al. - Machine Learning Advances", 
                                    authors=["Dr. Jane Smith", "Dr. Bob Johnson", "Dr. Alice Chen"],
                                    institutions=["MIT", "Stanford"],
                                    topics=["machine learning", "neural networks"]),
                create_academic_paper("Johnson & Chen - Deep Learning Applications",
                                    authors=["Dr. Bob Johnson", "Dr. Alice Chen"],
                                    institutions=["Stanford", "Berkeley"],
                                    topics=["deep learning", "computer vision"])
            ],
            "expected_insights": {
                "cross_author_collaboration": True,
                "institution_networks": True,
                "topic_overlap": ["machine learning"],
                "collaboration_strength": 0.7
            }
        },
        
        "social_network_analysis": {
            "description": "Social network analysis with theory-aware processing",
            "documents": [
                create_social_network_paper("Network Centrality in Organizations"),
                create_social_network_paper("Information Flow in Social Groups"),
                create_social_network_paper("Community Detection Algorithms")
            ],
            "expected_insights": {
                "network_metrics": ["centrality", "clustering", "community"],
                "theory_alignment": "social_network_theory",
                "methodological_consistency": True
            }
        }
    }
    
    scenario = scenarios.get(scenario_type, {})
    if params:
        scenario.update(params)
    
    return scenario

def create_academic_paper(title: str, authors: List[str], institutions: List[str], 
                         topics: List[str]) -> Dict[str, Any]:
    """Create realistic academic paper content."""
    content = f"""
    {title}
    
    Authors: {', '.join(authors)}
    Institutions: {', '.join(institutions)}
    
    Abstract: This paper presents research on {', '.join(topics)}. 
    The authors from {institutions[0]} and {institutions[1] if len(institutions) > 1 else institutions[0]} 
    collaborated to advance understanding in {topics[0]}.
    
    Introduction: Recent advances in {topics[0]} have shown promising results...
    
    Methodology: We applied {topics[1] if len(topics) > 1 else topics[0]} techniques...
    
    Results: Our findings demonstrate significant improvements...
    
    Conclusion: This work contributes to the field of {topics[0]} by...
    """
    
    return {
        "title": title,
        "content": content,
        "path": f"test_data/papers/{title.replace(' ', '_')}.pdf",
        "metadata": {
            "authors": authors,
            "institutions": institutions,
            "topics": topics
        }
    }
```

### Quality Assertions
```python
# tests/utils/assertions.py
def assert_research_quality(results: Dict[str, Any], expected_insights: Dict[str, Any]):
    """Assert research quality meets expectations."""
    
    # Entity extraction quality
    if "entities" in results:
        entities = results["entities"]
        assert len(entities) > 0, "No entities extracted"
        
        # Quality distribution check
        high_quality = [e for e in entities if e.get("confidence", 0) > 0.8]
        assert len(high_quality) / len(entities) > 0.3, "Insufficient high-quality entities"
    
    # Relationship quality
    if "relationships" in results:
        relationships = results["relationships"]
        assert len(relationships) > 0, "No relationships extracted"
        
        # Relationship diversity
        rel_types = set(r.get("type") for r in relationships)
        assert len(rel_types) > 1, "Insufficient relationship diversity"
    
    # Cross-modal consistency
    if "graph_insights" in results and "table_insights" in results:
        graph_entities = results["graph_insights"].get("entity_count", 0)
        table_entities = results["table_insights"].get("entity_count", 0)
        
        # Should be reasonably consistent
        entity_consistency = abs(graph_entities - table_entities) / max(graph_entities, table_entities)
        assert entity_consistency < 0.2, "Cross-modal entity count inconsistency"
    
    # Expected insight validation
    for insight_key, expected_value in expected_insights.items():
        if insight_key in results:
            if isinstance(expected_value, bool):
                assert results[insight_key] == expected_value, f"Expected {insight_key} to be {expected_value}"
            elif isinstance(expected_value, (int, float)):
                assert results[insight_key] >= expected_value, f"Expected {insight_key} >= {expected_value}"
            elif isinstance(expected_value, list):
                result_items = results[insight_key]
                overlap = set(result_items).intersection(set(expected_value))
                assert len(overlap) > 0, f"Expected overlap in {insight_key}"
```

## Running Functional Tests

### Test Execution
```bash
# Run all functional tests
python -m pytest tests/functional/ -v

# Run specific workflow tests
python -m pytest tests/functional/test_integration_complete.py -v

# Run UI tests (requires additional setup)
python -m pytest tests/functional/test_ui_complete.py -v

# Run with performance timing
python -m pytest tests/functional/ -v --durations=10

# Run slow tests
python -m pytest tests/functional/ -m slow --timeout=600
```

### Test Reports
```bash
# Generate HTML test report
python -m pytest tests/functional/ --html=functional_test_report.html --self-contained-html

# Generate coverage report
python -m pytest tests/functional/ --cov=src --cov-report=html --cov-report=term

# Generate performance report
python -m pytest tests/functional/ --benchmark-json=benchmark.json
```

## Continuous Integration

### Functional Test Pipeline
```yaml
# .github/workflows/functional-tests.yml
name: Functional Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  functional-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y poppler-utils tesseract-ocr
      
      - name: Install Python dependencies
        run: |
          pip install -e .
          pip install -r requirements/test.txt
          pip install -r requirements/functional.txt
      
      - name: Start services
        run: |
          docker-compose -f docker-compose.test.yml up -d
          sleep 30  # Wait for services to start
      
      - name: Run functional tests
        run: |
          python -m pytest tests/functional/ -v --timeout=300
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      
      - name: Upload test artifacts
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: functional-test-artifacts
          path: |
            test_outputs/
            logs/
            screenshots/
```

## Best Practices

### Functional Test Guidelines
1. **User-Centric**: Test from the user's perspective and workflow
2. **Realistic Data**: Use realistic research scenarios and data
3. **End-to-End**: Test complete workflows, not just individual components
4. **Quality Focus**: Validate research quality and accuracy
5. **Performance Aware**: Include performance requirements in tests
6. **Reproducible**: Tests should produce consistent results

### Test Environment Management
- Use isolated test environments for each test
- Clean up resources after each test run
- Use realistic but controlled test data
- Monitor test execution time and resource usage
- Implement proper error handling and cleanup

Functional tests ensure that KGAS delivers real value to researchers and meets the quality standards expected for academic research tools.