"""
Tests for Pandoc MCP Client

Tests the MCP client for Pandoc document conversion service.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import json

from src.integrations.mcp.pandoc_client import (
    PandocMCPClient,
    PandocDocument,
    PandocError,
    ConversionFormat
)
from src.integrations.mcp.base_client import MCPRequest, MCPResponse
from src.core.api_rate_limiter import APIRateLimiter
from src.core.circuit_breaker import CircuitBreaker


class TestPandocMCPClient:
    """Test suite for Pandoc MCP client"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter"""
        return APIRateLimiter()
    
    @pytest.fixture
    def circuit_breaker(self):
        """Create circuit breaker"""
        return CircuitBreaker("pandoc")
    
    @pytest.fixture
    def client(self, rate_limiter, circuit_breaker):
        """Create Pandoc MCP client"""
        return PandocMCPClient(
            server_url="http://localhost:8011",
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker
        )
    
    @pytest.mark.asyncio
    async def test_convert_markdown_to_latex(self, client):
        """Test: Convert Markdown to LaTeX"""
        mock_response = {
            "result": {
                "content": "\\documentclass{article}\n\\begin{document}\n\\section{Title}\nContent\n\\end{document}",
                "metadata": {
                    "from_format": "markdown",
                    "to_format": "latex",
                    "pandoc_version": "3.1.9"
                },
                "warnings": []
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.convert(
                content="# Title\n\nContent",
                from_format=ConversionFormat.MARKDOWN,
                to_format=ConversionFormat.LATEX
            )
        
        # Verify request
        mock_send.assert_called_once()
        request = mock_send.call_args[0][0]
        assert request.method == "convert"
        assert request.params["from_format"] == "markdown"
        assert request.params["to_format"] == "latex"
        
        # Verify response
        assert isinstance(result.data, PandocDocument)
        assert "\\section{Title}" in result.data.content
        assert result.data.from_format == "markdown"
        assert result.data.to_format == "latex"
    
    @pytest.mark.asyncio
    async def test_convert_with_bibliography(self, client):
        """Test: Convert with bibliography processing"""
        mock_response = {
            "result": {
                "content": "Document with citation [@smith2020].\n\n# References",
                "metadata": {
                    "bibliography_processed": True,
                    "citation_count": 5
                }
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.convert(
                content="Document with citation [@smith2020].",
                from_format=ConversionFormat.MARKDOWN,
                to_format=ConversionFormat.MARKDOWN,
                options={
                    "bibliography": "/refs/library.bib",
                    "csl": "/styles/apa.csl"
                }
            )
        
        assert "[@smith2020]" in result.data.content
        assert result.data.metadata["citation_count"] == 5
    
    @pytest.mark.asyncio
    async def test_convert_html_to_markdown(self, client):
        """Test: Convert HTML to Markdown"""
        mock_response = {
            "result": {
                "content": "# Heading\n\nThis is a **bold** paragraph.",
                "metadata": {
                    "extracted_links": 3,
                    "extracted_images": 2
                }
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            html_content = "<h1>Heading</h1><p>This is a <strong>bold</strong> paragraph.</p>"
            result = await client.convert(
                content=html_content,
                from_format=ConversionFormat.HTML,
                to_format=ConversionFormat.MARKDOWN
            )
        
        assert "# Heading" in result.data.content
        assert "**bold**" in result.data.content
    
    @pytest.mark.asyncio
    async def test_convert_with_filters(self, client):
        """Test: Apply Pandoc filters during conversion"""
        mock_response = {
            "result": {
                "content": "Filtered content with transformations",
                "metadata": {
                    "filters_applied": ["pandoc-citeproc", "pandoc-crossref"]
                }
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.convert_with_filters(
                content="Original content",
                from_format=ConversionFormat.MARKDOWN,
                to_format=ConversionFormat.LATEX,
                filters=["pandoc-citeproc", "pandoc-crossref"]
            )
        
        request = mock_send.call_args[0][0]
        assert request.params["filters"] == ["pandoc-citeproc", "pandoc-crossref"]
        assert result.data.metadata["filters_applied"] == ["pandoc-citeproc", "pandoc-crossref"]
    
    @pytest.mark.asyncio
    async def test_convert_with_template(self, client):
        """Test: Convert using custom template"""
        mock_response = {
            "result": {
                "content": "<!-- Custom Template -->\n<article>Content</article>",
                "metadata": {
                    "template_used": "article.html",
                    "template_variables": {"author": "John Doe"}
                }
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.convert(
                content="Content",
                from_format=ConversionFormat.MARKDOWN,
                to_format=ConversionFormat.HTML,
                options={
                    "template": "article.html",
                    "variables": {"author": "John Doe"}
                }
            )
        
        assert "<!-- Custom Template -->" in result.data.content
        assert result.data.metadata["template_used"] == "article.html"
    
    @pytest.mark.asyncio
    async def test_batch_convert_formats(self, client):
        """Test: Batch convert to multiple formats"""
        mock_responses = [
            {"result": {"content": "# Markdown", "metadata": {}}},
            {"result": {"content": "<h1>HTML</h1>", "metadata": {}}},
            {"result": {"content": "\\section{LaTeX}", "metadata": {}}}
        ]
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = mock_responses
            
            results = await client.batch_convert_formats(
                content="# Original",
                from_format=ConversionFormat.MARKDOWN,
                to_formats=[
                    ConversionFormat.MARKDOWN,
                    ConversionFormat.HTML,
                    ConversionFormat.LATEX
                ]
            )
        
        assert len(results) == 3
        assert results[0].data.content == "# Markdown"
        assert results[1].data.content == "<h1>HTML</h1>"
        assert results[2].data.content == "\\section{LaTeX}"
    
    @pytest.mark.asyncio
    async def test_extract_metadata(self, client):
        """Test: Extract document metadata"""
        mock_response = {
            "result": {
                "metadata": {
                    "title": "Document Title",
                    "author": ["John Doe", "Jane Smith"],
                    "date": "2024-01-15",
                    "abstract": "This is the abstract",
                    "keywords": ["pandoc", "conversion"],
                    "lang": "en"
                }
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.extract_metadata(
                "---\ntitle: Document Title\n---\n\nContent"
            )
        
        assert result.data["title"] == "Document Title"
        assert "John Doe" in result.data["author"]
        assert result.data["lang"] == "en"
    
    @pytest.mark.asyncio
    async def test_validate_document(self, client):
        """Test: Validate document structure"""
        mock_response = {
            "result": {
                "valid": True,
                "format_detected": "markdown",
                "issues": [],
                "statistics": {
                    "word_count": 500,
                    "heading_count": 5,
                    "link_count": 10
                }
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.validate_document(
                "# Valid Markdown\n\nContent here",
                expected_format=ConversionFormat.MARKDOWN
            )
        
        assert result.data["valid"] is True
        assert result.data["format_detected"] == "markdown"
        assert result.data["statistics"]["word_count"] == 500
    
    @pytest.mark.asyncio
    async def test_convert_with_math_rendering(self, client):
        """Test: Convert with math equation rendering"""
        mock_response = {
            "result": {
                "content": "Equation: $E = mc^2$",
                "metadata": {
                    "math_engine": "mathjax",
                    "math_equations": 3
                }
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.convert(
                content="Equation: $E = mc^2$",
                from_format=ConversionFormat.MARKDOWN,
                to_format=ConversionFormat.HTML,
                options={"mathjax": True}
            )
        
        assert "$E = mc^2$" in result.data.content
        assert result.data.metadata["math_engine"] == "mathjax"
    
    @pytest.mark.asyncio
    async def test_error_invalid_format(self, client):
        """Test: Handle invalid format error"""
        mock_error = {
            "error": {
                "code": "invalid_format",
                "message": "Unknown format: invalid"
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_error
            
            result = await client.convert(
                content="Test",
                from_format="invalid",  # Invalid format
                to_format=ConversionFormat.HTML
            )
        
        assert not result.success
        assert result.error["code"] == "invalid_format"
    
    @pytest.mark.asyncio
    async def test_get_supported_formats(self, client):
        """Test: Get list of supported formats"""
        mock_response = {
            "result": {
                "input_formats": ["markdown", "html", "latex", "docx", "rst"],
                "output_formats": ["markdown", "html", "latex", "pdf", "epub"],
                "extensions": {
                    "markdown": ["smart", "footnotes", "tables"],
                    "html": ["raw_html", "native_divs"]
                }
            }
        }
        
        with patch.object(client, '_send_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.get_supported_formats()
        
        assert "markdown" in result.data["input_formats"]
        assert "pdf" in result.data["output_formats"]
        assert "smart" in result.data["extensions"]["markdown"]