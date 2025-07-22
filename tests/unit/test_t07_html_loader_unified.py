"""
TDD tests for T07 HTML Loader - Unified Interface Migration

Write these tests FIRST before implementing the unified interface.
These tests MUST fail initially (Red phase).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from typing import Dict, Any
import time
from pathlib import Path

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus
from src.core.service_manager import ServiceManager


class TestT07HTMLLoaderUnified:
    """Test-driven development for T07 HTML Loader unified interface"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_services = Mock(spec=ServiceManager)
        self.mock_identity = Mock()
        self.mock_provenance = Mock()
        self.mock_quality = Mock()
        
        self.mock_services.identity_service = self.mock_identity
        self.mock_services.provenance_service = self.mock_provenance
        self.mock_services.quality_service = self.mock_quality
        
        # Import will fail initially - this is expected in TDD
        from src.tools.phase1.t07_html_loader_unified import T07HTMLLoaderUnified
        self.tool = T07HTMLLoaderUnified(self.mock_services)
    
    # ===== CONTRACT TESTS (MANDATORY) =====
    
    def test_tool_initialization(self):
        """Tool initializes with required services"""
        assert self.tool is not None
        assert self.tool.tool_id == "T07"
        assert self.tool.services == self.mock_services
        assert isinstance(self.tool, BaseTool)
    
    def test_get_contract(self):
        """Tool provides complete contract specification"""
        contract = self.tool.get_contract()
        
        assert isinstance(contract, ToolContract)
        assert contract.tool_id == "T07"
        assert contract.name == "HTML Document Loader"
        assert contract.category == "document_processing"
        assert contract.description == "Load and parse HTML documents with text extraction"
        
        # Verify input schema
        assert "file_path" in contract.input_schema["properties"]
        assert "workflow_id" in contract.input_schema["properties"]
        assert contract.input_schema["required"] == ["file_path"]
        
        # Verify output schema
        assert "document" in contract.output_schema["properties"]
        assert "text" in contract.output_schema["properties"]["document"]["properties"]
        assert "html" in contract.output_schema["properties"]["document"]["properties"]
        assert "metadata" in contract.output_schema["properties"]["document"]["properties"]
        assert "confidence" in contract.output_schema["properties"]["document"]["properties"]
        
        # Verify dependencies
        assert "identity_service" in contract.dependencies
        assert "provenance_service" in contract.dependencies
        assert "quality_service" in contract.dependencies
        
        # Verify performance requirements
        assert contract.performance_requirements["max_execution_time"] == 15.0
        assert contract.performance_requirements["max_memory_mb"] == 1024
    
    def test_input_contract_validation(self):
        """Tool validates inputs according to contract"""
        # Invalid inputs should be rejected
        invalid_inputs = [
            {},  # Empty input
            {"wrong_field": "value"},  # Wrong fields
            None,  # Null input
            {"file_path": ""},  # Empty file path
            {"file_path": 123},  # Wrong type
            {"file_path": "/etc/passwd"},  # Security risk
            {"file_path": "test.pdf"},  # Wrong extension
            {"file_path": "test.docx"},  # Not HTML
        ]
        
        for invalid_input in invalid_inputs:
            request = ToolRequest(
                tool_id="T07",
                operation="load",
                input_data=invalid_input,
                parameters={}
            )
            result = self.tool.execute(request)
            assert result.status == "error"
            assert result.error_code in ["INVALID_INPUT", "VALIDATION_FAILED", "INVALID_FILE_TYPE", "FILE_NOT_FOUND"]
    
    def test_output_contract_compliance(self):
        """Tool output matches contract specification"""
        # Mock HTML content
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <meta charset="utf-8">
    <meta name="description" content="Test description">
</head>
<body>
    <h1>Test Heading</h1>
    <p>Test paragraph content.</p>
</body>
</html>"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=html_content)):
            
            # Setup mocks
            mock_stat.return_value.st_size = 1024
            
            # Mock BeautifulSoup if used
            with patch('bs4.BeautifulSoup') as mock_bs:
                mock_soup = MagicMock()
                mock_soup.get_text.return_value = "Test Heading\nTest paragraph content."
                mock_soup.title.string = "Test Page"
                mock_soup.find_all.return_value = []
                mock_bs.return_value = mock_soup
                
                # Mock service responses
                self.mock_provenance.start_operation.return_value = "op123"
                self.mock_provenance.complete_operation.return_value = {"status": "success"}
                self.mock_quality.assess_confidence.return_value = {
                    "status": "success",
                    "confidence": 0.95,
                    "quality_tier": "HIGH"
                }
                
                valid_input = {
                    "file_path": "test.html",
                    "workflow_id": "wf_123"
                }
                
                request = ToolRequest(
                    tool_id="T07",
                    operation="load",
                    input_data=valid_input,
                    parameters={}
                )
                
                result = self.tool.execute(request)
                
                # Verify output structure
                assert result.status == "success"
                assert result.tool_id == "T07"
                assert "document" in result.data
                
                # Verify document structure
                document = result.data["document"]
                assert "document_id" in document
                assert "text" in document
                assert "html" in document
                assert "metadata" in document
                assert "confidence" in document
                assert "file_path" in document
                assert "file_size" in document
                assert "element_count" in document
                
                # Verify metadata
                assert result.execution_time > 0
                assert result.memory_used >= 0
                assert "operation_id" in result.metadata
    
    # ===== FUNCTIONALITY TESTS (MANDATORY) =====
    
    def test_simple_html_loading(self):
        """Tool loads simple HTML correctly"""
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Simple Page</title>
</head>
<body>
    <h1>Welcome</h1>
    <p>This is a simple HTML page.</p>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
    </ul>
</body>
</html>"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=html_content)):
            
            mock_stat.return_value.st_size = 512
            
            # Mock services
            self.mock_provenance.start_operation.return_value = "op123"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.93,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T07",
                operation="load",
                input_data={"file_path": "simple.html"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert len(result.data["document"]["text"]) > 0
            assert "Welcome" in result.data["document"]["text"]
            assert "simple HTML page" in result.data["document"]["text"]
            assert result.data["document"]["metadata"]["title"] == "Simple Page"
            assert result.data["document"]["confidence"] >= 0.9
    
    def test_complex_html_with_scripts_and_styles(self):
        """Tool handles HTML with scripts and styles correctly"""
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Complex Page</title>
    <style>
        body { font-family: Arial; }
        .hidden { display: none; }
    </style>
    <script>
        function test() {
            console.log("This should be ignored");
        }
    </script>
</head>
<body>
    <h1>Main Content</h1>
    <p>Visible paragraph.</p>
    <div class="hidden">Hidden content</div>
    <script>console.log("Inline script");</script>
    <p>Another paragraph.</p>
</body>
</html>"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=html_content)):
            
            mock_stat.return_value.st_size = 1024
            
            self.mock_provenance.start_operation.return_value = "op124"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.91,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T07",
                operation="load",
                input_data={"file_path": "complex.html"},
                parameters={"exclude_scripts": True, "exclude_styles": True}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            # Should not contain script or style content
            assert "console.log" not in result.data["document"]["text"]
            assert "font-family" not in result.data["document"]["text"]
            # Should contain visible content
            assert "Main Content" in result.data["document"]["text"]
            assert "Visible paragraph" in result.data["document"]["text"]
    
    def test_html_with_forms_and_inputs(self):
        """Tool extracts form data correctly"""
        html_content = """<!DOCTYPE html>
<html>
<body>
    <h1>Contact Form</h1>
    <form action="/submit" method="post">
        <label for="name">Name:</label>
        <input type="text" id="name" name="name" placeholder="Enter your name">
        
        <label for="email">Email:</label>
        <input type="email" id="email" name="email">
        
        <textarea name="message" placeholder="Your message"></textarea>
        
        <button type="submit">Submit</button>
    </form>
</body>
</html>"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=html_content)):
            
            mock_stat.return_value.st_size = 768
            
            self.mock_provenance.start_operation.return_value = "op125"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.92,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T07",
                operation="load",
                input_data={"file_path": "form.html"},
                parameters={"extract_forms": True}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert "Contact Form" in result.data["document"]["text"]
            assert "forms" in result.data["document"]
            forms = result.data["document"]["forms"]
            assert len(forms) == 1
            assert forms[0]["action"] == "/submit"
            assert forms[0]["method"] == "post"
            assert len(forms[0]["fields"]) >= 3
    
    def test_html_with_tables(self):
        """Tool extracts table data correctly"""
        html_content = """<!DOCTYPE html>
<html>
<body>
    <h1>Data Table</h1>
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Age</th>
                <th>City</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>John</td>
                <td>30</td>
                <td>New York</td>
            </tr>
            <tr>
                <td>Jane</td>
                <td>25</td>
                <td>Los Angeles</td>
            </tr>
        </tbody>
    </table>
</body>
</html>"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=html_content)):
            
            mock_stat.return_value.st_size = 1024
            
            self.mock_provenance.start_operation.return_value = "op126"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.94,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T07",
                operation="load",
                input_data={"file_path": "table.html"},
                parameters={"extract_tables": True}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert "tables" in result.data["document"]
            tables = result.data["document"]["tables"]
            assert len(tables) == 1
            assert len(tables[0]["headers"]) == 3
            assert len(tables[0]["rows"]) == 2
            assert tables[0]["headers"] == ["Name", "Age", "City"]
    
    def test_html_with_metadata(self):
        """Tool extracts metadata correctly"""
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Page with Metadata</title>
    <meta name="description" content="This is a test page with metadata">
    <meta name="keywords" content="test, html, metadata">
    <meta name="author" content="Test Author">
    <meta property="og:title" content="Open Graph Title">
    <meta property="og:description" content="Open Graph Description">
    <link rel="canonical" href="https://example.com/page">
</head>
<body>
    <h1>Content</h1>
    <p>Page content here.</p>
</body>
</html>"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=html_content)):
            
            mock_stat.return_value.st_size = 768
            
            self.mock_provenance.start_operation.return_value = "op127"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.95,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T07",
                operation="load",
                input_data={"file_path": "metadata.html"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            metadata = result.data["document"]["metadata"]
            assert metadata["title"] == "Page with Metadata"
            assert metadata["description"] == "This is a test page with metadata"
            assert metadata["keywords"] == "test, html, metadata"
            assert metadata["author"] == "Test Author"
            assert "og:title" in metadata
            assert metadata["canonical"] == "https://example.com/page"
    
    def test_edge_case_empty_html(self):
        """Tool handles empty HTML files gracefully"""
        html_content = """<!DOCTYPE html>
<html>
<head></head>
<body></body>
</html>"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=html_content)):
            
            mock_stat.return_value.st_size = 50
            
            self.mock_provenance.start_operation.return_value = "op128"
            
            request = ToolRequest(
                tool_id="T07",
                operation="load",
                input_data={"file_path": "empty.html"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Should handle gracefully
            assert result.status in ["success", "error"]
            if result.status == "success":
                assert result.data["document"]["text"].strip() == ""
                assert result.data["document"]["element_count"]["total"] <= 5
    
    def test_edge_case_large_html(self):
        """Tool handles large HTML files efficiently"""
        # Create large HTML with many elements
        large_content = """<!DOCTYPE html>
<html>
<head><title>Large Page</title></head>
<body>
"""
        for i in range(1000):
            large_content += f'<div id="section{i}"><h2>Section {i}</h2><p>Content for section {i} with some text.</p></div>\n'
        large_content += """
</body>
</html>"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=large_content)):
            
            # 5MB file
            mock_stat.return_value.st_size = 5 * 1024 * 1024
            
            self.mock_provenance.start_operation.return_value = "op129"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.95,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T07",
                operation="load",
                input_data={"file_path": "large.html"},
                parameters={"memory_limit_mb": 500}
            )
            
            start_time = time.time()
            result = self.tool.execute(request)
            execution_time = time.time() - start_time
            
            assert result.status == "success"
            assert result.data["document"]["element_count"]["div"] >= 1000
            assert execution_time < 15.0  # Performance requirement
    
    def test_malformed_html_handling(self):
        """Tool handles malformed HTML gracefully"""
        malformed_html = """<html>
<head><title>Malformed</title>
<body>
    <p>Unclosed paragraph
    <div>Unclosed div
    <p>Another paragraph</p>
    </body>
</html>"""  # Missing closing tags
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=malformed_html)):
            
            mock_stat.return_value.st_size = 256
            
            self.mock_provenance.start_operation.return_value = "op130"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.85,
                "quality_tier": "MEDIUM"
            }
            
            request = ToolRequest(
                tool_id="T07",
                operation="load",
                input_data={"file_path": "malformed.html"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Should still extract text despite malformed HTML
            assert result.status == "success"
            assert "Unclosed paragraph" in result.data["document"]["text"]
            assert "Another paragraph" in result.data["document"]["text"]
    
    # ===== INTEGRATION TESTS (MANDATORY) =====
    
    def test_identity_service_integration(self):
        """Tool integrates with IdentityService correctly"""
        html_content = "<html><body>Test</body></html>"
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=html_content)):
            
            mock_stat.return_value.st_size = 100
            
            self.mock_provenance.start_operation.return_value = "op131"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.90,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T07",
                operation="load",
                input_data={"file_path": "test.html", "workflow_id": "wf_123"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            # Verify document ID follows pattern
            assert result.data["document"]["document_id"].startswith("wf_123_")
    
    def test_provenance_tracking(self):
        """Tool tracks provenance correctly"""
        html_content = "<html><body>Content</body></html>"
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=html_content)):
            
            mock_stat.return_value.st_size = 50
            
            # Setup provenance mock
            self.mock_provenance.start_operation.return_value = "op132"
            self.mock_provenance.complete_operation.return_value = {
                "status": "success",
                "operation_id": "op132"
            }
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.85,
                "quality_tier": "MEDIUM"
            }
            
            request = ToolRequest(
                tool_id="T07",
                operation="load",
                input_data={"file_path": "test.html"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Verify provenance was tracked
            self.mock_provenance.start_operation.assert_called_once()
            call_args = self.mock_provenance.start_operation.call_args[1]
            assert call_args["tool_id"] == "T07"
            assert call_args["operation_type"] == "load_document"
            
            self.mock_provenance.complete_operation.assert_called_once()
            complete_args = self.mock_provenance.complete_operation.call_args[1]
            assert complete_args["operation_id"] == "op132"
            assert complete_args["success"] == True
    
    def test_quality_service_integration(self):
        """Tool integrates with quality service for confidence scoring"""
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Quality Test</title>
    <meta name="description" content="High quality content">
</head>
<body>
    """ + "\n".join([f"<p>Paragraph {i} with substantial content.</p>" for i in range(50)]) + """
</body>
</html>"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=html_content)):
            
            mock_stat.return_value.st_size = 2048
            
            self.mock_provenance.start_operation.return_value = "op133"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            
            # Mock quality assessment
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.96,
                "quality_tier": "HIGH",
                "factors": {
                    "structure": 0.95,
                    "content_richness": 0.98
                }
            }
            
            request = ToolRequest(
                tool_id="T07",
                operation="load",
                input_data={"file_path": "quality_test.html"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Verify quality service was used
            self.mock_quality.assess_confidence.assert_called_once()
            quality_args = self.mock_quality.assess_confidence.call_args[1]
            assert quality_args["base_confidence"] > 0.8
            assert "factors" in quality_args
            
            # Result should have quality-adjusted confidence
            assert result.data["document"]["confidence"] == 0.96
            assert result.data["document"]["quality_tier"] == "HIGH"
    
    # ===== PERFORMANCE TESTS (MANDATORY) =====
    
    @pytest.mark.performance
    def test_performance_requirements(self):
        """Tool meets performance benchmarks"""
        # Create moderately complex HTML
        test_html = """<!DOCTYPE html>
<html>
<head><title>Performance Test</title></head>
<body>
"""
        # Add many elements
        for i in range(500):
            test_html += f"""
    <article id="article{i}">
        <h2>Article {i}</h2>
        <p>Content paragraph 1 for article {i}.</p>
        <p>Content paragraph 2 for article {i}.</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
    </article>
"""
        test_html += """
</body>
</html>"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=test_html)):
            
            # 3MB file
            mock_stat.return_value.st_size = 3 * 1024 * 1024
            
            self.mock_provenance.start_operation.return_value = "op134"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.93,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T07",
                operation="load",
                input_data={"file_path": "performance_test.html"},
                parameters={}
            )
            
            # Measure performance
            start_time = time.time()
            result = self.tool.execute(request)
            execution_time = time.time() - start_time
            
            # Performance assertions
            assert result.status == "success"
            assert execution_time < 15.0  # Max 15 seconds
            assert result.execution_time < 15.0
            assert result.memory_used < 1024 * 1024 * 1024  # Max 1GB
    
    # ===== ERROR HANDLING TESTS =====
    
    def test_handles_encoding_errors(self):
        """Tool handles encoding errors appropriately"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')):
            
            mock_stat.return_value.st_size = 100
            
            self.mock_provenance.start_operation.return_value = "op135"
            
            request = ToolRequest(
                tool_id="T07",
                operation="load",
                input_data={"file_path": "bad_encoding.html"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code in ["ENCODING_ERROR", "EXTRACTION_FAILED"]
            assert "encoding" in result.error_message.lower() or "decode" in result.error_message.lower()
    
    def test_handles_file_not_found(self):
        """Tool handles missing files appropriately"""
        with patch('pathlib.Path.exists', return_value=False):
            
            request = ToolRequest(
                tool_id="T07",
                operation="load",
                input_data={"file_path": "nonexistent.html"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code == "FILE_NOT_FOUND"
            assert "not found" in result.error_message.lower()
    
    # ===== UNIFIED INTERFACE TESTS =====
    
    def test_tool_status_management(self):
        """Tool manages status correctly"""
        assert self.tool.get_status() == ToolStatus.READY
        
        # During execution, status should change
        # This would need proper async handling in real implementation
        
    def test_health_check(self):
        """Tool health check works correctly"""
        result = self.tool.health_check()
        
        assert isinstance(result, ToolResult)
        assert result.tool_id == "T07"
        assert result.status in ["success", "error"]
        
        if result.status == "success":
            assert result.data["healthy"] == True
            assert "supported_formats" in result.data
            assert ".html" in result.data["supported_formats"]
            assert ".htm" in result.data["supported_formats"]
    
    def test_cleanup(self):
        """Tool cleans up resources properly"""
        # Setup some mock resources
        self.tool._temp_files = ["temp1.html", "temp2.html"]
        
        success = self.tool.cleanup()
        
        assert success == True
        assert len(self.tool._temp_files) == 0