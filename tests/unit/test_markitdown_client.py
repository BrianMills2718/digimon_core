"""
Tests for MarkItDown MCP Client

Tests the MCP client for Microsoft's MarkItDown document conversion service.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import json
import aiohttp

from src.integrations.mcp.markitdown_client import (
    MarkItDownMCPClient, 
    MarkItDownDocument,
    MarkItDownError,
    ConversionOptions
)
from src.integrations.mcp.base_client import MCPRequest, MCPResponse
from src.core.api_rate_limiter import APIRateLimiter
from src.core.circuit_breaker import CircuitBreaker


class TestMarkItDownMCPClient:
    """Test suite for MarkItDown MCP client"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter"""
        return APIRateLimiter()
    
    @pytest.fixture
    def circuit_breaker(self):
        """Create circuit breaker"""
        return CircuitBreaker("markitdown")
    
    @pytest.fixture
    def client(self, rate_limiter, circuit_breaker):
        """Create MarkItDown MCP client"""
        return MarkItDownMCPClient(
            server_url="http://localhost:8010",
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker
        )
    
    @pytest.mark.asyncio
    async def test_convert_document_docx(self, client):
        """Test: Convert DOCX document to markdown"""
        # Mock response
        mock_response = {
            "result": {
                "content": "# Document Title\n\nThis is the document content.",
                "metadata": {
                    "title": "Document Title",
                    "author": "John Doe",
                    "created": "2024-01-15",
                    "word_count": 150,
                    "page_count": 3
                },
                "conversion_time": 0.25
            }
        }
        
        # Mock HTTP request
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            # Test conversion
            result = await client.convert_document(
                file_path=Path("/path/to/document.docx"),
                options=ConversionOptions(
                    preserve_formatting=True,
                    extract_images=True
                )
            )
        
        # Verify request
        mock_send.assert_called_once()
        request = mock_send.call_args[0][0]
        assert request.method == "convert_document"
        assert request.params["file_path"] == "/path/to/document.docx"
        assert request.params["options"]["preserve_formatting"] is True
        
        # Verify response
        assert isinstance(result.data, MarkItDownDocument)
        assert result.data.markdown_content == "# Document Title\n\nThis is the document content."
        assert result.data.metadata["title"] == "Document Title"
        assert result.data.word_count == 150
    
    @pytest.mark.asyncio
    async def test_convert_excel_with_tables(self, client):
        """Test: Convert Excel with table preservation"""
        # Mock response with table
        mock_response = {
            "result": {
                "content": "# Sales Data\n\n| Product | Q1 | Q2 | Q3 | Q4 |\n|---------|----|----|----|\n| Widget A | 100 | 150 | 200 | 175 |",
                "metadata": {
                    "sheets": ["Sales", "Inventory"],
                    "table_count": 3,
                    "formula_count": 12
                },
                "conversion_time": 0.35
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.convert_document(
                file_path=Path("/data/sales.xlsx"),
                options=ConversionOptions(extract_tables=True)
            )
        
        assert "| Product | Q1 | Q2 | Q3 | Q4 |" in result.data.markdown_content
        assert result.data.metadata["table_count"] == 3
    
    @pytest.mark.asyncio
    async def test_convert_powerpoint_with_speaker_notes(self, client):
        """Test: Convert PowerPoint preserving speaker notes"""
        mock_response = {
            "result": {
                "content": "# Slide 1: Introduction\n\nMain content\n\n**Speaker Notes:** Remember to mention...",
                "metadata": {
                    "slide_count": 25,
                    "has_speaker_notes": True,
                    "has_animations": True
                }
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.convert_document(
                file_path=Path("/presentations/quarterly.pptx"),
                options=ConversionOptions(include_speaker_notes=True)
            )
        
        assert "**Speaker Notes:**" in result.data.markdown_content
        assert result.data.metadata["slide_count"] == 25
    
    @pytest.mark.asyncio
    async def test_batch_convert_documents(self, client):
        """Test: Batch convert multiple documents"""
        # Mock responses for different documents
        mock_responses = [
            {"result": {"content": "# Doc1", "metadata": {"title": "Doc1"}}},
            {"result": {"content": "# Doc2", "metadata": {"title": "Doc2"}}},
            {"result": {"content": "# Doc3", "metadata": {"title": "Doc3"}}}
        ]
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = mock_responses
            
            file_paths = [
                Path("/docs/doc1.docx"),
                Path("/docs/doc2.pdf"),
                Path("/docs/doc3.xlsx")
            ]
            
            results = await client.batch_convert(file_paths)
        
        assert len(results) == 3
        assert all(r.success for r in results)
        assert results[0].data.markdown_content == "# Doc1"
        assert results[2].data.metadata["title"] == "Doc3"
    
    @pytest.mark.asyncio
    async def test_convert_with_custom_template(self, client):
        """Test: Convert with custom markdown template"""
        mock_response = {
            "result": {
                "content": "---\ntitle: Custom Document\ndate: 2024-01-15\n---\n\n# Content",
                "metadata": {"template_applied": "academic"}
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.convert_document(
                file_path=Path("/docs/paper.docx"),
                options=ConversionOptions(
                    template="academic",
                    include_frontmatter=True
                )
            )
        
        assert "---\ntitle: Custom Document" in result.data.markdown_content
        assert result.data.metadata["template_applied"] == "academic"
    
    @pytest.mark.asyncio
    async def test_extract_document_metadata(self, client):
        """Test: Extract metadata without full conversion"""
        mock_response = {
            "result": {
                "metadata": {
                    "title": "Quick Check",
                    "author": "Jane Smith",
                    "file_size": 125000,
                    "format": "docx",
                    "created": "2024-01-10",
                    "modified": "2024-01-15"
                }
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.get_document_metadata(Path("/docs/check.docx"))
        
        assert result.data["title"] == "Quick Check"
        assert result.data["file_size"] == 125000
    
    @pytest.mark.asyncio
    async def test_error_handling_unsupported_format(self, client):
        """Test: Handle unsupported file format"""
        mock_error = {
            "error": {
                "code": "unsupported_format",
                "message": "File format .xyz is not supported"
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_error
            
            result = await client.convert_document(Path("/docs/unknown.xyz"))
        
        assert not result.success
        assert result.error["code"] == "unsupported_format"
    
    @pytest.mark.asyncio
    async def test_convert_with_ocr(self, client):
        """Test: Convert scanned PDF with OCR"""
        mock_response = {
            "result": {
                "content": "# Scanned Document\n\nOCR extracted text here...",
                "metadata": {
                    "ocr_applied": True,
                    "ocr_confidence": 0.92,
                    "pages_processed": 5
                }
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.convert_document(
                file_path=Path("/scans/document.pdf"),
                options=ConversionOptions(enable_ocr=True)
            )
        
        assert result.data.metadata["ocr_applied"] is True
        assert result.data.metadata["ocr_confidence"] == 0.92
    
    @pytest.mark.asyncio
    async def test_convert_complex_document_structure(self, client):
        """Test: Convert document with complex structure"""
        mock_response = {
            "result": {
                "content": """# Main Document

## Table of Contents
1. [Introduction](#introduction)
2. [Methods](#methods)

## Introduction

Text with **bold** and *italic* formatting.

## Methods

### Subsection

- Bullet point 1
- Bullet point 2
  - Nested point

```python
def example():
    return "code block"
```

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
""",
                "metadata": {
                    "structure": {
                        "headings": 4,
                        "lists": 2,
                        "tables": 1,
                        "code_blocks": 1
                    }
                }
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.convert_document(Path("/docs/complex.docx"))
        
        content = result.data.markdown_content
        assert "```python" in content
        assert "| Header 1 | Header 2 |" in content
        assert result.data.metadata["structure"]["code_blocks"] == 1
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test: MCP server health check"""
        mock_response = {
            "result": {
                "status": "healthy",
                "version": "1.0.5",
                "supported_formats": [
                    ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
                    ".pdf", ".rtf", ".odt", ".ods", ".odp"
                ]
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            health = await client.get_health_status()
        
        assert health["service_status"] == "healthy"
        assert health["version"] == "1.0.5"
        assert ".docx" in health["supported_formats"]