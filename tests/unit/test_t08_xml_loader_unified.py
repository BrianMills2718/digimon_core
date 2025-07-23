"""
Mock-free unit tests for T08 XML Loader Unified

Tests the unified XML loader tool with real XML processing using xml.etree.ElementTree.
No mocking is used - all functionality is tested with real data and real processing.
"""

import pytest
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import Mock
import os

from src.tools.phase1.t08_xml_loader_unified import T08XMLLoaderUnified
from src.core.service_manager import ServiceManager
from src.tools.base_tool import ToolRequest


class TestT08XMLLoaderUnifiedMockFree:
    def setup_method(self):
        """Set up test fixtures with real ServiceManager - NO mocks"""
        # Real ServiceManager - NO mocking
        self.service_manager = ServiceManager()
        self.tool = T08XMLLoaderUnified(service_manager=self.service_manager)
        
        # Create real test XML files
        self.test_files = self._create_real_test_xml_files()
    
    def teardown_method(self):
        """Clean up real test files"""
        for file_path in self.test_files.values():
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except:
                pass
    
    def _create_real_test_xml_files(self) -> dict:
        """Create real XML test files for testing"""
        test_files = {}
        
        # Simple XML file
        simple_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<root>
    <title>Test Document</title>
    <content>This is a test XML document with simple structure.</content>
    <metadata>
        <author>Test Author</author>
        <date>2024-01-01</date>
    </metadata>
</root>'''
        
        simple_file = tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False)
        simple_file.write(simple_xml)
        simple_file.close()
        test_files['simple'] = simple_file.name
        
        # Complex XML with attributes and namespaces
        complex_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<books xmlns:fiction="http://example.com/fiction" xmlns:nonfiction="http://example.com/nonfiction">
    <fiction:book id="1" genre="fantasy" available="true">
        <title lang="en">The Fantasy Novel</title>
        <author nationality="US">
            <firstName>John</firstName>
            <lastName>Smith</lastName>
        </author>
        <publication year="2023" publisher="Fantasy Press"/>
        <description>A thrilling fantasy adventure with magic and dragons.</description>
        <chapters>
            <chapter number="1" title="The Beginning">
                <content>Once upon a time in a magical land...</content>
            </chapter>
            <chapter number="2" title="The Journey">
                <content>The hero embarked on a perilous journey...</content>
            </chapter>
        </chapters>
    </fiction:book>
    <nonfiction:book id="2" genre="science" available="false">
        <title lang="en">Understanding Physics</title>
        <author nationality="UK">
            <firstName>Jane</firstName>
            <lastName>Doe</lastName>
        </author>
        <publication year="2022" publisher="Science Books Ltd"/>
        <description>A comprehensive guide to modern physics principles.</description>
        <sections>
            <section name="Mechanics" pages="50"/>
            <section name="Thermodynamics" pages="75"/>
            <section name="Quantum Physics" pages="100"/>
        </sections>
    </nonfiction:book>
</books>'''
        
        complex_file = tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False)
        complex_file.write(complex_xml)
        complex_file.close()
        test_files['complex'] = complex_file.name
        
        # RSS feed XML
        rss_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Test News Feed</title>
        <link>http://example.com</link>
        <description>Test RSS feed for XML parsing</description>
        <item>
            <title>Breaking News: XML Parser Works</title>
            <link>http://example.com/news1</link>
            <description>The XML parser successfully processed this RSS feed.</description>
            <pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
        </item>
        <item>
            <title>Technology Update</title>
            <link>http://example.com/news2</link>
            <description>New advances in XML processing technology.</description>
            <pubDate>Tue, 02 Jan 2024 15:30:00 GMT</pubDate>
        </item>
    </channel>
</rss>'''
        
        rss_file = tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False)
        rss_file.write(rss_xml)
        rss_file.close()
        test_files['rss'] = rss_file.name
        
        # Malformed XML for error testing
        malformed_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<root>
    <unclosed_tag>This tag is not closed properly
    <another_tag>Content here</another_tag>
</root>'''
        
        malformed_file = tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False)
        malformed_file.write(malformed_xml)
        malformed_file.close()
        test_files['malformed'] = malformed_file.name
        
        return test_files
    
    def test_tool_contract_real(self):
        """Test tool contract with REAL contract validation"""
        contract = self.tool.get_contract()
        
        # Verify contract structure
        assert contract.tool_id == "T08"
        assert contract.name == "XML Document Loader"
        assert contract.category == "document_processing"
        assert "file_path" in contract.input_schema["required"]
        assert "document" in contract.output_schema["required"]
        assert len(contract.dependencies) > 0
        
        # Verify performance requirements
        assert "max_execution_time" in contract.performance_requirements
        assert "max_memory_mb" in contract.performance_requirements
        assert "min_confidence" in contract.performance_requirements
        
        # Verify error conditions
        assert "XML_MALFORMED" in contract.error_conditions
        assert "FILE_NOT_FOUND" in contract.error_conditions
    
    def test_simple_xml_loading_real(self):
        """Test loading simple XML with REAL processing"""
        request = ToolRequest(
            tool_id="T08",
            operation="load_xml",
            input_data={
                "file_path": self.test_files['simple'],
                "workflow_id": "test_workflow_simple"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify successful execution
        assert result.status == "success"
        assert result.tool_id == "T08"
        assert result.execution_time > 0
        
        # Verify document data
        doc = result.data["document"]
        assert doc["document_id"] == "test_workflow_simple_" + Path(self.test_files['simple']).stem
        assert doc["file_name"] == Path(self.test_files['simple']).name
        assert doc["element_count"] > 0
        assert doc["confidence"] > 0.5
        assert len(doc["text_content"]) > 0
        
        # Verify XML structure
        xml_structure = doc["xml_structure"]
        assert xml_structure["tag"] == "root"
        assert "children" in xml_structure
        assert len(xml_structure["children"]) >= 3  # title, content, metadata
        
        # Verify specific content
        assert "Test Document" in doc["text_content"]
        assert "Test Author" in doc["text_content"]
    
    def test_complex_xml_with_namespaces_real(self):
        """Test loading complex XML with namespaces and attributes with REAL processing"""
        request = ToolRequest(
            tool_id="T08",
            operation="load_xml",
            input_data={
                "file_path": self.test_files['complex'],
                "workflow_id": "test_workflow_complex",
                "parse_options": {
                    "include_attributes": True,
                    "namespace_aware": True
                }
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify successful execution
        assert result.status == "success"
        
        # Verify document data
        doc = result.data["document"]
        assert doc["element_count"] > 10  # Complex structure
        assert doc["attributes_count"] > 5  # Multiple attributes
        assert doc["namespace_count"] == 2  # fiction and nonfiction namespaces
        assert doc["confidence"] > 0.5
        
        # Verify XML structure with attributes
        xml_structure = doc["xml_structure"]
        assert xml_structure["tag"] == "books"
        
        # Find book elements and verify attributes
        book_elements = [child for child in xml_structure.get("children", []) if "book" in child["tag"]]
        assert len(book_elements) == 2
        
        # Verify attributes are included
        for book in book_elements:
            assert "attributes" in book
            assert "id" in book["attributes"]
            assert "genre" in book["attributes"]
    
    def test_rss_feed_parsing_real(self):
        """Test RSS feed XML parsing with REAL processing"""
        request = ToolRequest(
            tool_id="T08",
            operation="load_xml",
            input_data={
                "file_path": self.test_files['rss'],
                "workflow_id": "test_workflow_rss"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify successful execution
        assert result.status == "success"
        
        # Verify RSS-specific content
        doc = result.data["document"]
        assert "Test News Feed" in doc["text_content"]
        assert "Breaking News: XML Parser Works" in doc["text_content"]
        assert "Technology Update" in doc["text_content"]
        
        # Verify RSS structure
        xml_structure = doc["xml_structure"]
        assert xml_structure["tag"] == "rss"
        assert "attributes" in xml_structure
        assert xml_structure["attributes"]["version"] == "2.0"
    
    def test_parse_options_functionality_real(self):
        """Test different parse options with REAL processing"""
        # Test with flattened text
        request_flat = ToolRequest(
            tool_id="T08",
            operation="load_xml",
            input_data={
                "file_path": self.test_files['simple'],
                "parse_options": {
                    "flatten_text": True,
                    "preserve_whitespace": False
                }
            },
            parameters={}
        )
        
        result_flat = self.tool.execute(request_flat)
        assert result_flat.status == "success"
        
        # Test without attributes
        request_no_attr = ToolRequest(
            tool_id="T08",
            operation="load_xml",
            input_data={
                "file_path": self.test_files['complex'],
                "parse_options": {
                    "include_attributes": False
                }
            },
            parameters={}
        )
        
        result_no_attr = self.tool.execute(request_no_attr)
        assert result_no_attr.status == "success"
        
        # Verify attributes are not included
        xml_structure = result_no_attr.data["document"]["xml_structure"]
        def check_no_attributes(element):
            assert "attributes" not in element or not element["attributes"]
            for child in element.get("children", []):
                check_no_attributes(child)
        
        check_no_attributes(xml_structure)
    
    def test_error_handling_malformed_xml_real(self):
        """Test error handling with REAL malformed XML"""
        request = ToolRequest(
            tool_id="T08",
            operation="load_xml",
            input_data={
                "file_path": self.test_files['malformed']
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify error handling
        assert result.status == "error"
        assert result.error_code == "XML_MALFORMED"
        assert "XML parse error" in result.error_message
    
    def test_file_not_found_error_real(self):
        """Test file not found error with REAL missing file"""
        request = ToolRequest(
            tool_id="T08",
            operation="load_xml",
            input_data={
                "file_path": "/path/to/nonexistent/file.xml"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify error handling
        assert result.status == "error"
        assert result.error_code == "FILE_NOT_FOUND"
        assert "File not found" in result.error_message
    
    def test_invalid_file_type_error_real(self):
        """Test invalid file type error with REAL non-XML file"""
        # Create a non-XML file
        txt_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        txt_file.write("This is not an XML file")
        txt_file.close()
        
        try:
            request = ToolRequest(
                tool_id="T08",
                operation="load_xml",
                input_data={
                    "file_path": txt_file.name
                },
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Verify error handling
            assert result.status == "error"
            assert result.error_code == "INVALID_FILE_TYPE"
            assert "Invalid file extension" in result.error_message
        finally:
            os.unlink(txt_file.name)
    
    def test_input_validation_real(self):
        """Test input validation with REAL validation logic"""
        # Test missing file_path
        result = self.tool.validate_input({})
        assert result == False
        
        result = self.tool.validate_input({"file_path": ""})
        assert result == False
        
        # Test valid input
        result = self.tool.validate_input({"file_path": "/some/path.xml"})
        assert result == True
    
    def test_health_check_real(self):
        """Test health check with REAL service verification"""
        result = self.tool.health_check()
        
        # Verify health check structure
        assert isinstance(result.data, dict)
        assert "healthy" in result.data
        assert "elementtree_available" in result.data
        assert "services_healthy" in result.data
        assert "supported_formats" in result.data
        
        # Verify ElementTree is available
        assert result.data["elementtree_available"] == True
        
        # Verify supported formats
        supported_formats = result.data["supported_formats"]
        assert ".xml" in supported_formats
        assert ".xhtml" in supported_formats
        assert ".svg" in supported_formats
        assert ".rss" in supported_formats
    
    def test_cleanup_functionality_real(self):
        """Test cleanup functionality with REAL resource management"""
        # Add some temp files to the tool
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        self.tool._temp_files.append(temp_file.name)
        
        # Verify cleanup works
        cleanup_result = self.tool.cleanup()
        assert cleanup_result == True
        assert len(self.tool._temp_files) == 0
        assert not os.path.exists(temp_file.name)
    
    def test_confidence_calculation_real(self):
        """Test confidence calculation with REAL XML parsing metrics"""
        # Test with simple XML
        request_simple = ToolRequest(
            tool_id="T08",
            operation="load_xml",
            input_data={"file_path": self.test_files['simple']},
            parameters={}
        )
        
        result_simple = self.tool.execute(request_simple)
        confidence_simple = result_simple.data["document"]["confidence"]
        
        # Test with complex XML
        request_complex = ToolRequest(
            tool_id="T08",
            operation="load_xml",
            input_data={"file_path": self.test_files['complex']},
            parameters={}
        )
        
        result_complex = self.tool.execute(request_complex)
        confidence_complex = result_complex.data["document"]["confidence"]
        
        # Complex XML should have equal or higher confidence due to more structure
        assert confidence_simple > 0.5
        assert confidence_complex > 0.5
        assert confidence_complex >= confidence_simple - 0.1  # Allow small variance
    
    def test_performance_metrics_real(self):
        """Test performance metrics with REAL execution measurement"""
        request = ToolRequest(
            tool_id="T08",
            operation="load_xml",
            input_data={"file_path": self.test_files['complex']},
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify performance metrics are captured
        assert result.execution_time > 0
        assert result.memory_used >= 0  # Memory might be 0 in some environments
        
        # Verify reasonable execution time (should be under 1 second for test files)
        assert result.execution_time < 1.0
    
    def test_service_integration_real(self):
        """Test service integration with REAL services"""
        request = ToolRequest(
            tool_id="T08",
            operation="load_xml",
            input_data={
                "file_path": self.test_files['simple'],
                "workflow_id": "test_service_integration"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify service integration
        assert result.status == "success"
        assert "operation_id" in result.metadata
        
        # Verify provenance tracking
        operation_id = result.metadata["operation_id"]
        assert operation_id is not None
        
        # Verify quality assessment
        doc = result.data["document"]
        assert "quality_tier" in doc
        assert doc["confidence"] > 0
    
    def test_xml_structure_extraction_real(self):
        """Test XML structure extraction with REAL parsing"""
        request = ToolRequest(
            tool_id="T08",
            operation="load_xml",
            input_data={"file_path": self.test_files['complex']},
            parameters={}
        )
        
        result = self.tool.execute(request)
        xml_structure = result.data["document"]["xml_structure"]
        
        # Verify structure completeness
        assert xml_structure["tag"] == "books"
        assert "children" in xml_structure
        
        # Verify nested structure
        books = [child for child in xml_structure["children"] if "book" in child["tag"]]
        assert len(books) == 2
        
        # Verify attributes
        for book in books:
            assert "attributes" in book
            assert "id" in book["attributes"]
            
            # Verify nested children
            book_children = book.get("children", [])
            titles = [child for child in book_children if child["tag"] == "title"]
            assert len(titles) == 1
    
    def test_text_content_extraction_real(self):
        """Test text content extraction with REAL text processing"""
        request = ToolRequest(
            tool_id="T08",
            operation="load_xml",
            input_data={
                "file_path": self.test_files['rss'],
                "parse_options": {"flatten_text": True}
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        text_content = result.data["document"]["text_content"]
        
        # Verify all expected text is extracted
        assert "Test News Feed" in text_content
        assert "Breaking News: XML Parser Works" in text_content
        assert "Technology Update" in text_content
        assert "http://example.com" in text_content
        
        # Verify text is properly formatted
        assert len(text_content.strip()) > 0
        assert text_content.count("Breaking News") == 1  # Should appear exactly once