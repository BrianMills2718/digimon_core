"""
Integration tests for unified interface tools.

These tests verify that tools work together correctly, share services properly,
and maintain data integrity across the pipeline.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, patch

from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
from src.tools.phase1.t02_word_loader_unified import T02WordLoaderUnified
from src.tools.phase1.t03_text_loader_unified import T03TextLoaderUnified
from src.tools.phase1.t04_markdown_loader_unified import T04MarkdownLoaderUnified
from src.tools.phase1.t05_csv_loader_unified import T05CSVLoaderUnified
from src.tools.phase1.t06_json_loader_unified import T06JSONLoaderUnified
from src.tools.phase1.t07_html_loader_unified import T07HTMLLoaderUnified

from src.core.service_manager import ServiceManager
from src.tools.base_tool import ToolRequest, ToolResult


class TestUnifiedToolsIntegration:
    """Integration tests for unified interface tools"""
    
    def setup_method(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.service_manager = ServiceManager()
        
        # Initialize all tools with shared service manager
        self.pdf_loader = T01PDFLoaderUnified(self.service_manager)
        self.word_loader = T02WordLoaderUnified(self.service_manager)
        self.text_loader = T03TextLoaderUnified(self.service_manager)
        self.markdown_loader = T04MarkdownLoaderUnified(self.service_manager)
        self.csv_loader = T05CSVLoaderUnified(self.service_manager)
        self.json_loader = T06JSONLoaderUnified(self.service_manager)
        self.html_loader = T07HTMLLoaderUnified(self.service_manager)
        
        # Create test files
        self._create_test_files()
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _create_test_files(self):
        """Create test files for integration testing"""
        # Text file
        self.text_file = Path(self.test_dir) / "test.txt"
        self.text_file.write_text("""This is a test document.
It contains information about Alice and Bob.
Alice works at TechCorp in Seattle.
Bob manages DataInc in New York.""")
        
        # Markdown file
        self.markdown_file = Path(self.test_dir) / "test.md"
        self.markdown_file.write_text("""---
title: Test Report
author: Alice Johnson
date: 2024-01-01
tags:
  - test
  - integration
---

# Test Report

## Summary

This report covers the integration testing of our unified tools.

## Key Findings

- **Performance**: All tools meet performance requirements
- **Accuracy**: Entity extraction accuracy is 95%
- **Integration**: Services work seamlessly together

### Code Example

```python
def test_integration():
    assert tools_work_together()
```

## References

- [Documentation](https://docs.example.com)
- [GitHub](https://github.com/example/repo)
""")
        
        # CSV file
        self.csv_file = Path(self.test_dir) / "test.csv"
        self.csv_file.write_text("""name,company,location,role
Alice Johnson,TechCorp,Seattle,Engineer
Bob Smith,DataInc,New York,Manager
Carol White,AILabs,Boston,Researcher""")
        
        # JSON file
        self.json_file = Path(self.test_dir) / "test.json"
        self.json_file.write_text("""{
    "report": {
        "title": "Integration Test Report",
        "author": "Test Suite",
        "entities": [
            {"name": "Alice Johnson", "type": "PERSON", "company": "TechCorp"},
            {"name": "Bob Smith", "type": "PERSON", "company": "DataInc"},
            {"name": "TechCorp", "type": "ORG", "location": "Seattle"},
            {"name": "DataInc", "type": "ORG", "location": "New York"}
        ]
    }
}""")
        
        # HTML file
        self.html_file = Path(self.test_dir) / "test.html"
        self.html_file.write_text("""<!DOCTYPE html>
<html>
<head>
    <title>Test Report</title>
    <meta name="author" content="Alice Johnson">
    <meta name="date" content="2024-01-01">
</head>
<body>
    <h1>Integration Test Report</h1>
    <p>This report was created by <strong>Alice Johnson</strong> at <em>TechCorp</em>.</p>
    <p>Contributors include <strong>Bob Smith</strong> from <em>DataInc</em>.</p>
    <ul>
        <li>Location: Seattle, New York</li>
        <li>Status: Active</li>
    </ul>
</body>
</html>""")
    
    def test_service_sharing_across_tools(self):
        """Test that all tools share the same service instances"""
        # Verify all tools use the same service manager
        assert self.pdf_loader.services == self.service_manager
        assert self.word_loader.services == self.service_manager
        assert self.text_loader.services == self.service_manager
        assert self.markdown_loader.services == self.service_manager
        assert self.csv_loader.services == self.service_manager
        assert self.json_loader.services == self.service_manager
        assert self.html_loader.services == self.service_manager
        
        # Verify service instances are shared
        assert self.pdf_loader.identity_service == self.text_loader.identity_service
        assert self.word_loader.provenance_service == self.csv_loader.provenance_service
        assert self.markdown_loader.quality_service == self.json_loader.quality_service
    
    def test_consistent_document_ids_across_tools(self):
        """Test that document IDs follow consistent patterns"""
        workflow_id = "wf_integration_test"
        
        # Load files with same workflow ID
        text_result = self._load_file(self.text_loader, self.text_file, workflow_id)
        markdown_result = self._load_file(self.markdown_loader, self.markdown_file, workflow_id)
        csv_result = self._load_file(self.csv_loader, self.csv_file, workflow_id)
        
        # Verify document IDs follow pattern
        assert text_result.data["document"]["document_id"].startswith(workflow_id)
        assert markdown_result.data["document"]["document_id"].startswith(workflow_id)
        assert csv_result.data["dataset"]["dataset_id"].startswith(workflow_id)
        
        # Verify document refs follow pattern
        assert text_result.data["document"]["document_ref"].startswith("storage://document/")
        assert markdown_result.data["document"]["document_ref"].startswith("storage://document/")
        assert csv_result.data["dataset"]["dataset_ref"].startswith("storage://dataset/")
    
    def test_provenance_tracking_across_pipeline(self):
        """Test that provenance is properly tracked across tool operations"""
        # Mock provenance service to track calls
        provenance_calls = []
        
        def mock_start_operation(**kwargs):
            provenance_calls.append(("start", kwargs))
            return f"op_{len(provenance_calls)}"
        
        def mock_complete_operation(**kwargs):
            provenance_calls.append(("complete", kwargs))
            return {"status": "success"}
        
        self.service_manager.provenance_service.start_operation = mock_start_operation
        self.service_manager.provenance_service.complete_operation = mock_complete_operation
        
        # Execute multiple tools
        self._load_file(self.text_loader, self.text_file)
        self._load_file(self.markdown_loader, self.markdown_file)
        self._load_file(self.json_loader, self.json_file)
        
        # Verify provenance tracking
        start_calls = [call for call in provenance_calls if call[0] == "start"]
        complete_calls = [call for call in provenance_calls if call[0] == "complete"]
        
        assert len(start_calls) == 3
        assert len(complete_calls) == 3
        
        # Verify operation IDs match
        for i, (start, complete) in enumerate(zip(start_calls, complete_calls)):
            assert complete[1]["operation_id"] == f"op_{i*2 + 1}"
    
    def test_quality_assessment_consistency(self):
        """Test that quality assessment is consistent across tools"""
        # Mock quality service to track assessments
        quality_assessments = []
        
        def mock_assess_confidence(**kwargs):
            quality_assessments.append(kwargs)
            return {
                "status": "success",
                "confidence": kwargs["base_confidence"] * 0.95,
                "quality_tier": "HIGH" if kwargs["base_confidence"] > 0.8 else "MEDIUM"
            }
        
        self.service_manager.quality_service.assess_confidence = mock_assess_confidence
        
        # Load different file types
        results = [
            self._load_file(self.text_loader, self.text_file),
            self._load_file(self.markdown_loader, self.markdown_file),
            self._load_file(self.csv_loader, self.csv_file),
            self._load_file(self.json_loader, self.json_file),
            self._load_file(self.html_loader, self.html_file)
        ]
        
        # Verify quality assessments
        assert len(quality_assessments) == 5
        
        # Check that all assessments have required fields
        for assessment in quality_assessments:
            assert "base_confidence" in assessment
            assert "factors" in assessment
            assert "metadata" in assessment
        
        # Verify confidence propagation
        for result, assessment in zip(results, quality_assessments):
            doc_key = "document" if "document" in result.data else "dataset"
            expected_confidence = assessment["base_confidence"] * 0.95
            actual_confidence = result.data[doc_key]["confidence"]
            assert abs(actual_confidence - expected_confidence) < 0.01
    
    def test_error_handling_consistency(self):
        """Test that error handling is consistent across tools"""
        # Test with non-existent files
        fake_file = Path(self.test_dir) / "nonexistent.txt"
        
        tools_and_extensions = [
            (self.text_loader, ".txt"),
            (self.markdown_loader, ".md"),
            (self.csv_loader, ".csv"),
            (self.json_loader, ".json"),
            (self.html_loader, ".html")
        ]
        
        for tool, ext in tools_and_extensions:
            request = ToolRequest(
                tool_id=tool.tool_id,
                operation="load",
                input_data={"file_path": str(fake_file.with_suffix(ext))},
                parameters={}
            )
            
            result = tool.execute(request)
            
            # All tools should return consistent error format
            assert result.status == "error"
            assert result.error_code == "FILE_NOT_FOUND"
            assert "not found" in result.error_message.lower()
    
    def test_metadata_consistency_across_formats(self):
        """Test that metadata extraction is consistent across different formats"""
        # Load files that contain metadata
        markdown_result = self._load_file(self.markdown_loader, self.markdown_file)
        json_result = self._load_file(self.json_loader, self.json_file)
        html_result = self._load_file(self.html_loader, self.html_file)
        
        # Extract metadata
        md_metadata = markdown_result.data["document"]["metadata"]
        json_data = json_result.data["document"]["data"]  # JSON data structure
        html_metadata = html_result.data["document"]["metadata"]
        
        # Verify common metadata fields
        assert md_metadata["title"] == "Test Report"
        assert md_metadata["author"] == "Alice Johnson"
        
        # JSON data should contain the report structure
        assert "Integration Test Report" in str(json_data)
        
        assert html_metadata["title"] == "Test Report"
        assert html_metadata["author"] == "Alice Johnson"
    
    def test_performance_requirements_compliance(self):
        """Test that all tools meet their performance requirements"""
        import time
        
        tools_and_files = [
            (self.text_loader, self.text_file, 5.0),  # max 5s
            (self.markdown_loader, self.markdown_file, 10.0),  # max 10s
            (self.csv_loader, self.csv_file, 10.0),  # max 10s
            (self.json_loader, self.json_file, 5.0),  # max 5s
            (self.html_loader, self.html_file, 10.0)  # max 10s
        ]
        
        for tool, file_path, max_time in tools_and_files:
            start_time = time.time()
            result = self._load_file(tool, file_path)
            execution_time = time.time() - start_time
            
            # Verify successful execution
            assert result.status == "success"
            
            # Verify performance requirement
            assert execution_time < max_time, f"{tool.tool_id} took {execution_time}s, max is {max_time}s"
            
            # Verify execution time is tracked
            assert result.execution_time > 0
            assert result.execution_time < max_time
    
    def test_tool_health_checks(self):
        """Test that all tools report health status correctly"""
        tools = [
            self.pdf_loader, self.word_loader, self.text_loader,
            self.markdown_loader, self.csv_loader, self.json_loader,
            self.html_loader
        ]
        
        for tool in tools:
            health_result = tool.health_check()
            
            # Verify health check result format
            assert isinstance(health_result, ToolResult)
            assert health_result.tool_id == tool.tool_id
            assert health_result.status in ["success", "error"]
            
            if health_result.status == "success":
                assert health_result.data["healthy"] in [True, False]
                assert "supported_formats" in health_result.data
                assert "status" in health_result.data
    
    def test_resource_cleanup(self):
        """Test that tools clean up resources properly"""
        # Track cleanup calls
        cleanup_results = []
        
        tools = [
            self.text_loader, self.markdown_loader, self.csv_loader,
            self.json_loader, self.html_loader
        ]
        
        for tool in tools:
            # Simulate tool having temporary files
            tool._temp_files = ["temp1.txt", "temp2.txt"]
            
            # Call cleanup
            success = tool.cleanup()
            cleanup_results.append((tool.tool_id, success))
            
            # Verify cleanup
            assert success == True
            assert len(tool._temp_files) == 0
        
        # All tools should clean up successfully
        assert all(result[1] for result in cleanup_results)
    
    def test_cross_tool_data_flow(self):
        """Test data flow between different tools"""
        # Load a CSV file
        csv_result = self._load_file(self.csv_loader, self.csv_file)
        assert csv_result.status == "success"
        
        # Extract data from CSV
        dataset_data = csv_result.data["dataset"]
        data_rows = dataset_data["data"]  # List of row dictionaries
        
        # Verify we can extract entities from the data
        entities_found = []
        for row in data_rows:
            if "name" in row:
                entities_found.append(row["name"])
            if "company" in row:
                entities_found.append(row["company"])
        
        assert "Alice Johnson" in entities_found
        assert "TechCorp" in entities_found
        assert "Bob Smith" in entities_found
        assert "DataInc" in entities_found
    
    def _load_file(self, tool, file_path, workflow_id=None):
        """Helper method to load a file with a tool"""
        input_data = {"file_path": str(file_path)}
        if workflow_id:
            input_data["workflow_id"] = workflow_id
        
        request = ToolRequest(
            tool_id=tool.tool_id,
            operation="load",
            input_data=input_data,
            parameters={}
        )
        
        return tool.execute(request)


class TestUnifiedToolsEndToEnd:
    """End-to-end tests for complete document processing pipeline"""
    
    def setup_method(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.service_manager = ServiceManager()
        self._create_realistic_documents()
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _create_realistic_documents(self):
        """Create realistic documents for end-to-end testing"""
        # Research paper in markdown
        self.research_paper = Path(self.test_dir) / "research_paper.md"
        self.research_paper.write_text("""---
title: "Analysis of Social Networks in Academic Collaboration"
authors: 
  - Dr. Sarah Chen
  - Prof. Michael Torres
  - Dr. Emily Watson
institution: Stanford University
date: 2024-01-15
keywords: [social networks, collaboration, academia, graph analysis]
---

# Analysis of Social Networks in Academic Collaboration

## Abstract

This paper analyzes collaboration patterns among researchers at Stanford University,
MIT, and Harvard University using graph-based approaches. We examined 10,000 papers
published between 2020-2023.

## Introduction

Academic collaboration has grown significantly. Dr. Sarah Chen from Stanford's 
Computer Science department has pioneered new methods for analyzing these networks.
Her work with Prof. Michael Torres from MIT has revealed interesting patterns.

## Methodology

We used PageRank and community detection algorithms to identify key researchers
and collaboration clusters. Dr. Emily Watson from Harvard contributed the 
statistical analysis framework.

## Results

Our analysis revealed that:
- Stanford researchers collaborate most frequently with MIT (45% of papers)
- Harvard maintains strong ties with both institutions (30% cross-institutional)
- The most central researcher is Dr. Chen with a PageRank score of 0.0234

## References

1. Chen, S., Torres, M. (2023). "Graph-Based Analysis of Research Networks"
2. Watson, E. (2023). "Statistical Methods for Network Analysis"
3. Torres, M., Chen, S., Watson, E. (2024). "Cross-Institutional Collaboration Patterns"
""")
        
        # Data file in CSV
        self.collaboration_data = Path(self.test_dir) / "collaborations.csv"
        self.collaboration_data.write_text("""researcher_name,institution,department,papers_count,h_index,collaboration_score
Dr. Sarah Chen,Stanford University,Computer Science,127,42,0.89
Prof. Michael Torres,MIT,Data Science,203,58,0.92
Dr. Emily Watson,Harvard University,Statistics,89,35,0.76
Dr. James Liu,Stanford University,Computer Science,67,28,0.71
Prof. Maria Garcia,MIT,AI Research,156,49,0.85
Dr. Robert Johnson,Harvard University,Applied Math,94,37,0.73
Dr. Lisa Anderson,Stanford University,Data Science,112,41,0.88
Prof. David Kim,MIT,Computer Science,189,54,0.91""")
        
        # Conference proceedings in HTML
        self.conference_html = Path(self.test_dir) / "conference.html"
        self.conference_html.write_text("""<!DOCTYPE html>
<html>
<head>
    <title>International Conference on Graph Analysis 2024</title>
    <meta name="conference" content="ICGA 2024">
    <meta name="location" content="San Francisco, CA">
    <meta name="date" content="2024-03-15">
</head>
<body>
    <h1>ICGA 2024 - Keynote Speakers</h1>
    
    <div class="speaker">
        <h2>Dr. Sarah Chen - Stanford University</h2>
        <p>Topic: "Advances in Academic Network Analysis"</p>
        <p>Dr. Chen will present her groundbreaking work on using PageRank 
        for identifying influential researchers.</p>
    </div>
    
    <div class="speaker">
        <h2>Prof. Michael Torres - MIT</h2>
        <p>Topic: "Community Detection in Large-Scale Networks"</p>
        <p>Prof. Torres will discuss new algorithms for detecting research communities.</p>
    </div>
    
    <div class="speaker">
        <h2>Dr. Emily Watson - Harvard University</h2>
        <p>Topic: "Statistical Validation of Network Metrics"</p>
        <p>Dr. Watson will present statistical methods for validating network analysis results.</p>
    </div>
    
    <div class="organizers">
        <h3>Conference Organizers</h3>
        <ul>
            <li>Stanford University - Host Institution</li>
            <li>MIT - Co-sponsor</li>
            <li>Harvard University - Co-sponsor</li>
            <li>National Science Foundation - Funding Partner</li>
        </ul>
    </div>
</body>
</html>""")
    
    def test_complete_document_processing_pipeline(self):
        """Test complete pipeline from document loading to entity extraction"""
        workflow_id = "wf_e2e_test"
        
        # Step 1: Load all documents
        markdown_loader = T04MarkdownLoaderUnified(self.service_manager)
        csv_loader = T05CSVLoaderUnified(self.service_manager)
        html_loader = T07HTMLLoaderUnified(self.service_manager)
        
        paper_result = self._load_document(markdown_loader, self.research_paper, workflow_id)
        data_result = self._load_document(csv_loader, self.collaboration_data, workflow_id)
        conference_result = self._load_document(html_loader, self.conference_html, workflow_id)
        
        # Verify all documents loaded successfully
        assert paper_result.status == "success"
        assert data_result.status == "success"
        assert conference_result.status == "success"
        
        # Step 2: Extract and verify entities from each document
        paper_entities = self._extract_entities_from_text(paper_result.data["document"]["text"])
        conference_entities = self._extract_entities_from_text(conference_result.data["document"]["text"])
        
        # Verify key entities are found
        assert "Dr. Sarah Chen" in paper_entities
        assert "Stanford University" in paper_entities
        assert "MIT" in paper_entities
        assert "Harvard University" in paper_entities
        assert "Prof. Michael Torres" in paper_entities
        
        # Step 3: Verify metadata extraction
        paper_metadata = paper_result.data["document"]["metadata"]
        assert paper_metadata["title"] == "Analysis of Social Networks in Academic Collaboration"
        assert "Dr. Sarah Chen" in paper_metadata["authors"]
        assert paper_metadata["institution"] == "Stanford University"
        
        # Step 4: Verify data extraction from CSV
        dataset_data = data_result.data["dataset"]
        assert dataset_data["rows"] == 8  # Number of rows
        assert dataset_data["column_names"] == ["researcher_name", "institution", "department", 
                                         "papers_count", "h_index", "collaboration_score"]
        
        # Find Dr. Chen's data
        data_rows = dataset_data["data"]  # List of row dictionaries
        chen_data = next(row for row in data_rows if row["researcher_name"] == "Dr. Sarah Chen")
        assert chen_data["institution"] == "Stanford University"
        assert chen_data["papers_count"] == 127
        assert chen_data["h_index"] == 42
        
        # Step 5: Verify HTML content extraction
        html_data = conference_result.data["document"]
        assert html_data["element_count"]["total"] > 5  # Should have multiple elements
        assert "Dr. Sarah Chen" in html_data["text"]  # Should extract text content
        
        # Step 6: Verify cross-document entity consistency
        common_entities = self._find_common_entities(
            paper_entities, conference_entities, data_rows
        )
        
        assert "Dr. Sarah Chen" in common_entities
        assert "Prof. Michael Torres" in common_entities
        assert "Dr. Emily Watson" in common_entities
        assert "Stanford University" in common_entities
        assert "MIT" in common_entities
        assert "Harvard University" in common_entities
    
    def test_workflow_id_propagation(self):
        """Test that workflow ID propagates correctly through pipeline"""
        workflow_id = "wf_propagation_test"
        
        # Create a chain of operations
        operations = []
        
        def track_operation(**kwargs):
            operations.append(kwargs)
            return f"op_{len(operations)}"
        
        self.service_manager.provenance_service.start_operation = track_operation
        self.service_manager.provenance_service.complete_operation = lambda **k: {"status": "success"}
        
        # Load documents with same workflow ID
        loaders = [
            T04MarkdownLoaderUnified(self.service_manager),
            T05CSVLoaderUnified(self.service_manager),
            T07HTMLLoaderUnified(self.service_manager)
        ]
        
        for loader, file_path in zip(loaders, 
                                     [self.research_paper, self.collaboration_data, self.conference_html]):
            self._load_document(loader, file_path, workflow_id)
        
        # Verify workflow ID in all operations
        for op in operations:
            if "parameters" in op and "workflow_id" in op["parameters"]:
                assert op["parameters"]["workflow_id"] == workflow_id
    
    def test_confidence_score_propagation(self):
        """Test that confidence scores propagate correctly through pipeline"""
        # Track confidence scores
        confidence_scores = {}
        
        def track_confidence(**kwargs):
            doc_ref = kwargs.get("object_ref", "unknown")
            confidence_scores[doc_ref] = kwargs["base_confidence"]
            return {
                "status": "success",
                "confidence": kwargs["base_confidence"] * 0.95,
                "quality_tier": "HIGH"
            }
        
        self.service_manager.quality_service.assess_confidence = track_confidence
        
        # Load documents
        loaders_and_files = [
            (T04MarkdownLoaderUnified(self.service_manager), self.research_paper),
            (T05CSVLoaderUnified(self.service_manager), self.collaboration_data),
            (T07HTMLLoaderUnified(self.service_manager), self.conference_html)
        ]
        
        results = []
        for loader, file_path in loaders_and_files:
            result = self._load_document(loader, file_path)
            results.append(result)
        
        # Verify confidence scores
        for result in results:
            doc_key = "document" if "document" in result.data else "dataset"
            confidence = result.data[doc_key]["confidence"]
            
            # Should be high confidence for well-structured documents
            assert confidence > 0.8
            assert result.data[doc_key]["quality_tier"] == "HIGH"
    
    def test_error_recovery_in_pipeline(self):
        """Test that pipeline handles errors gracefully"""
        # Create a corrupted file
        corrupted_file = Path(self.test_dir) / "corrupted.json"
        corrupted_file.write_text("{invalid json content")
        
        # Try to load corrupted file
        json_loader = T06JSONLoaderUnified(self.service_manager)
        
        request = ToolRequest(
            tool_id="T06",
            operation="load",
            input_data={"file_path": str(corrupted_file)},
            parameters={}
        )
        
        result = json_loader.execute(request)
        
        # Should handle error gracefully
        assert result.status == "error"
        assert result.error_code in ["PARSING_ERROR", "INVALID_JSON", "JSON_MALFORMED"]
        
        # Should still be able to process other files
        csv_result = self._load_document(
            T05CSVLoaderUnified(self.service_manager),
            self.collaboration_data
        )
        assert csv_result.status == "success"
    
    def _load_document(self, loader, file_path, workflow_id=None):
        """Helper to load a document"""
        input_data = {"file_path": str(file_path)}
        if workflow_id:
            input_data["workflow_id"] = workflow_id
        
        request = ToolRequest(
            tool_id=loader.tool_id,
            operation="load",
            input_data=input_data,
            parameters={}
        )
        
        return loader.execute(request)
    
    def _extract_entities_from_text(self, text):
        """Helper to extract entities from text (simulated)"""
        # Simulate entity extraction
        entities = []
        
        # Person entities
        person_patterns = ["Dr.", "Prof."]
        for line in text.split('\n'):
            for pattern in person_patterns:
                if pattern in line:
                    # Extract name after title
                    parts = line.split(pattern)
                    if len(parts) > 1:
                        name_part = parts[1].split()[0:2]
                        if name_part:
                            entities.append(f"{pattern} {' '.join(name_part)}".strip())
        
        # Organization entities
        org_names = ["Stanford University", "MIT", "Harvard University", 
                    "National Science Foundation"]
        for org in org_names:
            if org in text:
                entities.append(org)
        
        return list(set(entities))
    
    def _find_common_entities(self, *entity_lists):
        """Find entities that appear in multiple sources"""
        common = set()
        
        # Flatten all entity sources
        all_entities = []
        for entity_list in entity_lists:
            if isinstance(entity_list, list):
                if len(entity_list) > 0 and isinstance(entity_list[0], dict):
                    # Handle CSV rows
                    for row in entity_list:
                        all_entities.extend(row.values())
                else:
                    all_entities.extend(entity_list)
        
        # Convert to strings and find duplicates
        entity_strings = [str(e) for e in all_entities]
        for entity in set(entity_strings):
            if entity_strings.count(entity) > 1:
                common.add(entity)
        
        return common