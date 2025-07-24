"""
Pandoc MCP Client

MCP client for Pandoc universal document converter.
Supports conversion between dozens of markup formats.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging

from .base_client import BaseMCPClient, MCPRequest, MCPResponse
from .http_client import HTTPMCPClient
from ..exceptions import MCPError


logger = logging.getLogger(__name__)


class ConversionFormat(str, Enum):
    """Supported Pandoc formats"""
    # Markup formats
    MARKDOWN = "markdown"
    HTML = "html"
    LATEX = "latex"
    RST = "rst"
    ASCIIDOC = "asciidoc"
    TEXTILE = "textile"
    ORG = "org"
    MEDIAWIKI = "mediawiki"
    DOKUWIKI = "dokuwiki"
    
    # Document formats
    DOCX = "docx"
    ODT = "odt"
    EPUB = "epub"
    PDF = "pdf"
    
    # Presentation formats
    BEAMER = "beamer"
    REVEALJS = "revealjs"
    SLIDY = "slidy"
    
    # Other formats
    JSON = "json"
    NATIVE = "native"
    PLAIN = "plain"


@dataclass
class PandocDocument:
    """Converted document with metadata"""
    content: str
    from_format: str
    to_format: str
    metadata: Dict[str, Any]
    warnings: List[str]
    

class PandocError(MCPError):
    """Pandoc-specific errors"""
    pass


class PandocMCPClient(HTTPMCPClient):
    """
    MCP client for Pandoc document conversion.
    
    Provides universal document conversion between markup formats,
    with support for filters, templates, and bibliography processing.
    """
    
    def __init__(self, server_url: str, rate_limiter, circuit_breaker):
        """Initialize Pandoc MCP client"""
        super().__init__(
            server_name="pandoc",
            server_url=server_url,
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker
        )
    
    async def convert(
        self,
        content: str,
        from_format: Union[str, ConversionFormat],
        to_format: Union[str, ConversionFormat],
        options: Optional[Dict[str, Any]] = None
    ) -> MCPResponse[PandocDocument]:
        """
        Convert document between formats.
        
        Args:
            content: Source document content
            from_format: Input format
            to_format: Output format
            options: Pandoc options (template, bibliography, etc.)
            
        Returns:
            MCPResponse with converted document
        """
        # Convert enum to string if needed
        if isinstance(from_format, ConversionFormat):
            from_format = from_format.value
        if isinstance(to_format, ConversionFormat):
            to_format = to_format.value
        
        request = MCPRequest(
            method="convert",
            params={
                "content": content,
                "from_format": from_format,
                "to_format": to_format,
                "options": options or {}
            }
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        result = response["result"]
        document = PandocDocument(
            content=result["content"],
            from_format=from_format,
            to_format=to_format,
            metadata=result.get("metadata", {}),
            warnings=result.get("warnings", [])
        )
        
        return MCPResponse(success=True, data=document)
    
    async def convert_with_filters(
        self,
        content: str,
        from_format: Union[str, ConversionFormat],
        to_format: Union[str, ConversionFormat],
        filters: List[str],
        options: Optional[Dict[str, Any]] = None
    ) -> MCPResponse[PandocDocument]:
        """
        Convert with Pandoc filters applied.
        
        Args:
            content: Source content
            from_format: Input format
            to_format: Output format
            filters: List of filter names/paths
            options: Additional options
            
        Returns:
            Filtered and converted document
        """
        if isinstance(from_format, ConversionFormat):
            from_format = from_format.value
        if isinstance(to_format, ConversionFormat):
            to_format = to_format.value
        
        request = MCPRequest(
            method="convert_with_filters",
            params={
                "content": content,
                "from_format": from_format,
                "to_format": to_format,
                "filters": filters,
                "options": options or {}
            }
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        result = response["result"]
        document = PandocDocument(
            content=result["content"],
            from_format=from_format,
            to_format=to_format,
            metadata=result.get("metadata", {}),
            warnings=result.get("warnings", [])
        )
        
        return MCPResponse(success=True, data=document)
    
    async def batch_convert_formats(
        self,
        content: str,
        from_format: Union[str, ConversionFormat],
        to_formats: List[Union[str, ConversionFormat]],
        options: Optional[Dict[str, Any]] = None
    ) -> List[MCPResponse[PandocDocument]]:
        """
        Convert to multiple output formats.
        
        Args:
            content: Source content
            from_format: Input format
            to_formats: List of output formats
            options: Conversion options
            
        Returns:
            List of conversion results
        """
        import asyncio
        
        tasks = []
        for to_format in to_formats:
            task = self.convert(content, from_format, to_format, options)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error responses
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(MCPResponse(
                    success=False,
                    error={
                        "code": "conversion_error",
                        "message": str(result),
                        "format": str(to_formats[i])
                    }
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def extract_metadata(
        self,
        content: str,
        format: Optional[Union[str, ConversionFormat]] = None
    ) -> MCPResponse[Dict[str, Any]]:
        """
        Extract document metadata.
        
        Args:
            content: Document content
            format: Document format (auto-detected if None)
            
        Returns:
            Document metadata
        """
        if format and isinstance(format, ConversionFormat):
            format = format.value
        
        request = MCPRequest(
            method="extract_metadata",
            params={
                "content": content,
                "format": format
            }
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]["metadata"]
        )
    
    async def validate_document(
        self,
        content: str,
        expected_format: Union[str, ConversionFormat]
    ) -> MCPResponse[Dict[str, Any]]:
        """
        Validate document structure and format.
        
        Args:
            content: Document content
            expected_format: Expected format
            
        Returns:
            Validation results
        """
        if isinstance(expected_format, ConversionFormat):
            expected_format = expected_format.value
        
        request = MCPRequest(
            method="validate",
            params={
                "content": content,
                "expected_format": expected_format
            }
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]
        )
    
    async def get_supported_formats(self) -> MCPResponse[Dict[str, Any]]:
        """
        Get list of supported input/output formats.
        
        Returns:
            Supported formats and extensions
        """
        request = MCPRequest(method="get_formats")
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        return MCPResponse(
            success=True,
            data=response["result"]
        )
    
    async def convert_with_template(
        self,
        content: str,
        from_format: Union[str, ConversionFormat],
        to_format: Union[str, ConversionFormat],
        template_path: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> MCPResponse[PandocDocument]:
        """
        Convert using custom template.
        
        Args:
            content: Source content
            from_format: Input format
            to_format: Output format
            template_path: Path to template file
            variables: Template variables
            
        Returns:
            Converted document with template applied
        """
        if isinstance(from_format, ConversionFormat):
            from_format = from_format.value
        if isinstance(to_format, ConversionFormat):
            to_format = to_format.value
        
        options = {
            "template": template_path,
            "variables": variables or {}
        }
        
        return await self.convert(content, from_format, to_format, options)
    
    async def convert_academic_paper(
        self,
        content: str,
        from_format: Union[str, ConversionFormat],
        to_format: Union[str, ConversionFormat],
        bibliography: Optional[str] = None,
        csl_style: Optional[str] = None
    ) -> MCPResponse[PandocDocument]:
        """
        Convert academic paper with bibliography.
        
        Args:
            content: Paper content with citations
            from_format: Input format
            to_format: Output format
            bibliography: Path to .bib file
            csl_style: Citation style (e.g., 'apa.csl')
            
        Returns:
            Converted paper with formatted citations
        """
        options = {}
        if bibliography:
            options["bibliography"] = bibliography
        if csl_style:
            options["csl"] = csl_style
        
        # Add common academic options
        options.update({
            "number-sections": True,
            "toc": True,
            "reference-section-title": "References"
        })
        
        return await self.convert(content, from_format, to_format, options)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get Pandoc service health status"""
        response = await self._send_request(MCPRequest(method="health"))
        
        if "error" in response:
            return {
                "service_status": "unhealthy",
                "error": response["error"],
                "circuit_breaker_state": self.circuit_breaker.state.name
            }
        
        result = response.get("result", {})
        return {
            "service_status": result.get("status", "unknown"),
            "version": result.get("pandoc_version"),
            "features": result.get("features", []),
            "circuit_breaker_state": self.circuit_breaker.state.name,
            "rate_limit_remaining": self.rate_limiter.get_remaining_requests(self.server_name)
        }