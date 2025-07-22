"""
TDD tests for T04 Markdown Loader - Unified Interface Migration

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


class TestT04MarkdownLoaderUnified:
    """Test-driven development for T04 Markdown Loader unified interface"""
    
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
        from src.tools.phase1.t04_markdown_loader_unified import T04MarkdownLoaderUnified
        self.tool = T04MarkdownLoaderUnified(self.mock_services)
    
    # ===== CONTRACT TESTS (MANDATORY) =====
    
    def test_tool_initialization(self):
        """Tool initializes with required services"""
        assert self.tool is not None
        assert self.tool.tool_id == "T04"
        assert self.tool.services == self.mock_services
        assert isinstance(self.tool, BaseTool)
    
    def test_get_contract(self):
        """Tool provides complete contract specification"""
        contract = self.tool.get_contract()
        
        assert isinstance(contract, ToolContract)
        assert contract.tool_id == "T04"
        assert contract.name == "Markdown Document Loader"
        assert contract.category == "document_processing"
        assert contract.description == "Load and parse Markdown documents with structure preservation"
        
        # Verify input schema
        assert "file_path" in contract.input_schema["properties"]
        assert "workflow_id" in contract.input_schema["properties"]
        assert contract.input_schema["required"] == ["file_path"]
        
        # Verify output schema
        assert "document" in contract.output_schema["properties"]
        assert "text" in contract.output_schema["properties"]["document"]["properties"]
        assert "html" in contract.output_schema["properties"]["document"]["properties"]
        assert "metadata" in contract.output_schema["properties"]["document"]["properties"]
        assert "structure" in contract.output_schema["properties"]["document"]["properties"]
        assert "confidence" in contract.output_schema["properties"]["document"]["properties"]
        
        # Verify dependencies
        assert "identity_service" in contract.dependencies
        assert "provenance_service" in contract.dependencies
        assert "quality_service" in contract.dependencies
        
        # Verify performance requirements
        assert contract.performance_requirements["max_execution_time"] == 10.0
        assert contract.performance_requirements["max_memory_mb"] == 512
    
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
            {"file_path": "test.docx"},  # Not markdown
        ]
        
        for invalid_input in invalid_inputs:
            request = ToolRequest(
                tool_id="T04",
                operation="load",
                input_data=invalid_input,
                parameters={}
            )
            result = self.tool.execute(request)
            assert result.status == "error"
            assert result.error_code in ["INVALID_INPUT", "VALIDATION_FAILED", "INVALID_FILE_TYPE", "FILE_NOT_FOUND"]
    
    def test_output_contract_compliance(self):
        """Tool output matches contract specification"""
        # Mock markdown content
        markdown_content = """# Test Document

This is a test markdown document.

## Section 1

Some content here.

### Subsection 1.1

- List item 1
- List item 2

## Section 2

Another section with **bold** and *italic* text."""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=markdown_content)):
            
            # Setup mocks
            mock_stat.return_value.st_size = 1024
            
            # Mock markdown parsing
            with patch('markdown.Markdown') as mock_md:
                mock_parser = MagicMock()
                mock_parser.convert.return_value = "<h1>Test Document</h1><p>Content</p>"
                mock_parser.Meta = {}
                mock_md.return_value = mock_parser
                
                # Mock service responses
                self.mock_provenance.start_operation.return_value = "op123"
                self.mock_provenance.complete_operation.return_value = {"status": "success"}
                self.mock_quality.assess_confidence.return_value = {
                    "status": "success",
                    "confidence": 0.95,
                    "quality_tier": "HIGH"
                }
                
                valid_input = {
                    "file_path": "test.md",
                    "workflow_id": "wf_123"
                }
                
                request = ToolRequest(
                    tool_id="T04",
                    operation="load",
                    input_data=valid_input,
                    parameters={}
                )
                
                result = self.tool.execute(request)
                
                # Verify output structure
                assert result.status == "success"
                assert result.tool_id == "T04"
                assert "document" in result.data
                
                # Verify document structure
                document = result.data["document"]
                assert "document_id" in document
                assert "text" in document
                assert "html" in document
                assert "metadata" in document
                assert "structure" in document
                assert "confidence" in document
                assert "file_path" in document
                assert "file_size" in document
                
                # Verify metadata
                assert result.execution_time > 0
                assert result.memory_used >= 0
                assert "operation_id" in result.metadata
    
    # ===== FUNCTIONALITY TESTS (MANDATORY) =====
    
    def test_simple_markdown_loading(self):
        """Tool loads simple markdown files correctly"""
        markdown_content = """# Simple Markdown

This is a simple markdown file.

## Features

- **Bold text**
- *Italic text*
- `Code snippets`

### Code Block

```python
def hello():
    print("Hello, World!")
```

End of document."""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=markdown_content)):
            
            mock_stat.return_value.st_size = len(markdown_content)
            
            # Mock services
            self.mock_provenance.start_operation.return_value = "op123"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.95,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T04",
                operation="load",
                input_data={"file_path": "simple.md"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert result.data["document"]["text"] == markdown_content
            assert len(result.data["document"]["html"]) > 0
            assert result.data["document"]["confidence"] >= 0.9
            
            # Check structure extraction
            structure = result.data["document"]["structure"]
            assert "headings" in structure
            assert len(structure["headings"]) >= 3  # h1, h2, h3
    
    def test_markdown_with_frontmatter(self):
        """Tool extracts frontmatter metadata correctly"""
        markdown_content = """---
title: Test Document
author: John Doe
date: 2024-01-01
tags: 
  - test
  - markdown
  - example
---

# Test Document

This document has frontmatter metadata.

## Content

The actual content starts here."""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=markdown_content)):
            
            mock_stat.return_value.st_size = len(markdown_content)
            
            self.mock_provenance.start_operation.return_value = "op124"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.93,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T04",
                operation="load",
                input_data={"file_path": "frontmatter.md"},
                parameters={"extract_frontmatter": True}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            metadata = result.data["document"]["metadata"]
            assert metadata["title"] == "Test Document"
            assert metadata["author"] == "John Doe"
            # YAML might parse date as datetime.date object
            assert str(metadata["date"]) == "2024-01-01"
            assert "test" in metadata["tags"]
    
    def test_markdown_with_tables(self):
        """Tool handles markdown tables correctly"""
        markdown_content = """# Document with Tables

## Data Table

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

## Another Section

More content after the table."""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=markdown_content)):
            
            mock_stat.return_value.st_size = len(markdown_content)
            
            self.mock_provenance.start_operation.return_value = "op125"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.94,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T04",
                operation="load",
                input_data={"file_path": "tables.md"},
                parameters={"extract_tables": True}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            structure = result.data["document"]["structure"]
            assert "tables" in structure
            assert len(structure["tables"]) >= 1
            # Should contain table data
            assert structure["tables"][0]["rows"] >= 2
            assert structure["tables"][0]["columns"] == 3
    
    def test_markdown_with_links_and_images(self):
        """Tool extracts links and images correctly"""
        markdown_content = """# Document with Links and Images

Here is a [link to example](https://example.com).

![Alt text for image](image.png)

Another [reference link][ref1].

![Another image][img1]

[ref1]: https://reference.com "Reference Title"
[img1]: another-image.jpg "Image Title"

## External Resources

- [Documentation](https://docs.example.com)
- [GitHub](https://github.com/example/repo)"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=markdown_content)):
            
            mock_stat.return_value.st_size = len(markdown_content)
            
            self.mock_provenance.start_operation.return_value = "op126"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.92,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T04",
                operation="load",
                input_data={"file_path": "links.md"},
                parameters={"extract_links": True, "extract_images": True}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            structure = result.data["document"]["structure"]
            assert "links" in structure
            assert "images" in structure
            assert len(structure["links"]) >= 4
            assert len(structure["images"]) >= 2
    
    def test_complex_nested_structure(self):
        """Tool handles complex nested markdown structures"""
        markdown_content = """# Main Title

## Chapter 1

### Section 1.1

Some content here.

#### Subsection 1.1.1

- Nested list item 1
  - Sub-item 1.1
  - Sub-item 1.2
- Nested list item 2

##### Deep Heading 1.1.1.1

Very deep content.

### Section 1.2

1. Ordered item 1
2. Ordered item 2
   1. Nested ordered 2.1
   2. Nested ordered 2.2

## Chapter 2

> Blockquote with **bold** and *italic* text.
> 
> Multiple lines in blockquote."""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=markdown_content)):
            
            mock_stat.return_value.st_size = len(markdown_content)
            
            self.mock_provenance.start_operation.return_value = "op127"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.95,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T04",
                operation="load",
                input_data={"file_path": "complex.md"},
                parameters={"analyze_structure": True}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            structure = result.data["document"]["structure"]
            assert structure["max_heading_level"] >= 5
            assert structure["has_lists"] == True
            assert structure["has_blockquotes"] == True
            assert structure["total_sections"] >= 4
    
    def test_edge_case_empty_markdown(self):
        """Tool handles empty markdown files gracefully"""
        markdown_content = ""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=markdown_content)):
            
            mock_stat.return_value.st_size = 0
            
            self.mock_provenance.start_operation.return_value = "op128"
            
            request = ToolRequest(
                tool_id="T04",
                operation="load",
                input_data={"file_path": "empty.md"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Should handle gracefully
            assert result.status in ["success", "error"]
            if result.status == "success":
                assert result.data["document"]["text"] == ""
                assert result.data["document"]["confidence"] < 0.5  # Low confidence for empty
    
    def test_markdown_with_code_blocks(self):
        """Tool preserves code blocks correctly"""
        markdown_content = '''# Code Examples

## Python Example

```python
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)

# Test the function
print(factorial(5))  # Output: 120
```

## JavaScript Example

```javascript
const greet = (name) => {
    console.log(`Hello, ${name}!`);
};

greet('World');
```

## Inline Code

Use `pip install package` to install packages.'''
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=markdown_content)):
            
            mock_stat.return_value.st_size = len(markdown_content)
            
            self.mock_provenance.start_operation.return_value = "op129"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.96,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T04",
                operation="load",
                input_data={"file_path": "code.md"},
                parameters={"extract_code_blocks": True}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            structure = result.data["document"]["structure"]
            assert "code_blocks" in structure
            assert len(structure["code_blocks"]) >= 2
            assert structure["code_blocks"][0]["language"] == "python"
            assert structure["code_blocks"][1]["language"] == "javascript"
    
    # ===== INTEGRATION TESTS (MANDATORY) =====
    
    def test_identity_service_integration(self):
        """Tool integrates with IdentityService correctly"""
        markdown_content = "# Test\n\nIdentity service test."
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=markdown_content)):
            
            mock_stat.return_value.st_size = len(markdown_content)
            
            self.mock_provenance.start_operation.return_value = "op130"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.90,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T04",
                operation="load",
                input_data={"file_path": "test.md", "workflow_id": "wf_123"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            # Verify document ID follows pattern
            assert result.data["document"]["document_id"].startswith("wf_123_")
    
    def test_provenance_tracking(self):
        """Tool tracks provenance correctly"""
        markdown_content = "# Provenance Test"
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=markdown_content)):
            
            mock_stat.return_value.st_size = len(markdown_content)
            
            # Setup provenance mock
            self.mock_provenance.start_operation.return_value = "op131"
            self.mock_provenance.complete_operation.return_value = {
                "status": "success",
                "operation_id": "op131"
            }
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.85,
                "quality_tier": "MEDIUM"
            }
            
            request = ToolRequest(
                tool_id="T04",
                operation="load",
                input_data={"file_path": "test.md"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Verify provenance was tracked
            self.mock_provenance.start_operation.assert_called_once()
            call_args = self.mock_provenance.start_operation.call_args[1]
            assert call_args["tool_id"] == "T04"
            assert call_args["operation_type"] == "load_document"
            
            self.mock_provenance.complete_operation.assert_called_once()
            complete_args = self.mock_provenance.complete_operation.call_args[1]
            assert complete_args["operation_id"] == "op131"
            assert complete_args["success"] == True
    
    def test_quality_service_integration(self):
        """Tool integrates with quality service for confidence scoring"""
        markdown_content = """# High Quality Document

## Well-Structured Content

This is a well-structured markdown document with:

- Clear headings
- Proper formatting
- Good organization
- Rich content

### Technical Details

```python
# High quality code example
class Example:
    def __init__(self):
        self.quality = "high"
```

### References

1. [Important Link](https://example.com)
2. [Documentation](https://docs.example.com)
3. [Resources](https://resources.example.com)"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=markdown_content)):
            
            mock_stat.return_value.st_size = len(markdown_content)
            
            self.mock_provenance.start_operation.return_value = "op132"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            
            # Mock quality assessment
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.97,
                "quality_tier": "HIGH",
                "factors": {
                    "structure": 0.98,
                    "content_richness": 0.96
                }
            }
            
            request = ToolRequest(
                tool_id="T04",
                operation="load",
                input_data={"file_path": "quality_test.md"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Verify quality service was used
            self.mock_quality.assess_confidence.assert_called_once()
            quality_args = self.mock_quality.assess_confidence.call_args[1]
            assert quality_args["base_confidence"] > 0.8
            assert "factors" in quality_args
            
            # Result should have quality-adjusted confidence
            assert result.data["document"]["confidence"] == 0.97
            assert result.data["document"]["quality_tier"] == "HIGH"
    
    # ===== PERFORMANCE TESTS (MANDATORY) =====
    
    @pytest.mark.performance
    def test_performance_requirements(self):
        """Tool meets performance benchmarks"""
        # Create large markdown document
        test_markdown = "# Large Document\n\n"
        for i in range(1000):
            test_markdown += f"## Section {i}\n\n"
            test_markdown += f"Content for section {i} with some text.\n\n"
            test_markdown += f"- List item 1 in section {i}\n"
            test_markdown += f"- List item 2 in section {i}\n\n"
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=test_markdown)):
            
            # 1MB file
            mock_stat.return_value.st_size = 1024 * 1024
            
            self.mock_provenance.start_operation.return_value = "op133"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.93,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T04",
                operation="load",
                input_data={"file_path": "performance_test.md"},
                parameters={}
            )
            
            # Measure performance
            start_time = time.time()
            result = self.tool.execute(request)
            execution_time = time.time() - start_time
            
            # Performance assertions
            assert result.status == "success"
            assert execution_time < 10.0  # Max 10 seconds
            assert result.execution_time < 10.0
            assert result.memory_used < 512 * 1024 * 1024  # Max 512MB
    
    # ===== ERROR HANDLING TESTS =====
    
    def test_handles_file_not_found(self):
        """Tool handles missing files appropriately"""
        with patch('pathlib.Path.exists', return_value=False):
            
            request = ToolRequest(
                tool_id="T04",
                operation="load",
                input_data={"file_path": "nonexistent.md"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code == "FILE_NOT_FOUND"
            assert "not found" in result.error_message.lower()
    
    def test_handles_malformed_markdown(self):
        """Tool handles malformed markdown gracefully"""
        # Markdown with unclosed code blocks and broken syntax
        malformed_markdown = """# Malformed

```python
def broken():
    # Never closed code block
    
## Broken heading without proper spacing
###Also broken

[Broken link](
![Broken image]("""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=malformed_markdown)):
            
            mock_stat.return_value.st_size = len(malformed_markdown)
            
            self.mock_provenance.start_operation.return_value = "op134"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.70,
                "quality_tier": "LOW"
            }
            
            request = ToolRequest(
                tool_id="T04",
                operation="load",
                input_data={"file_path": "malformed.md"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Should still succeed but with lower confidence
            assert result.status == "success"
            assert result.data["document"]["confidence"] < 0.8
    
    def test_handles_invalid_frontmatter(self):
        """Tool handles invalid YAML frontmatter gracefully"""
        markdown_with_bad_yaml = """---
title: Unclosed quote "
tags:
  - item1
  - item2
    - badly indented
invalid yaml: [
---

# Document

Content after bad frontmatter."""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=markdown_with_bad_yaml)):
            
            mock_stat.return_value.st_size = len(markdown_with_bad_yaml)
            
            self.mock_provenance.start_operation.return_value = "op135"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.80,
                "quality_tier": "MEDIUM"
            }
            
            request = ToolRequest(
                tool_id="T04",
                operation="load",
                input_data={"file_path": "bad_yaml.md"},
                parameters={"extract_frontmatter": True}
            )
            
            result = self.tool.execute(request)
            
            # Should handle gracefully
            assert result.status == "success"
            # Frontmatter parsing should fail gracefully
            assert result.data["document"]["metadata"].get("frontmatter_error") is not None or \
                   len(result.data["document"]["metadata"]) == 0
    
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
        assert result.tool_id == "T04"
        assert result.status in ["success", "error"]
        
        if result.status == "success":
            assert result.data["healthy"] == True
            assert "supported_formats" in result.data
            assert ".md" in result.data["supported_formats"]
            assert ".markdown" in result.data["supported_formats"]
    
    def test_cleanup(self):
        """Tool cleans up resources properly"""
        # Setup some mock resources
        self.tool._temp_files = ["temp1.md", "temp2.md"]
        
        success = self.tool.cleanup()
        
        assert success == True
        assert len(self.tool._temp_files) == 0