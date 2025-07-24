"""
MarkItDown MCP Client

MCP client for Microsoft's MarkItDown document conversion service.
Converts various document formats (Office, PDF, etc.) to Markdown.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

from .base_client import BaseMCPClient, MCPRequest, MCPResponse
from .http_client import HTTPMCPClient
from ..exceptions import MCPError


logger = logging.getLogger(__name__)


@dataclass
class ConversionOptions:
    """Options for document conversion"""
    preserve_formatting: bool = True
    extract_tables: bool = True
    extract_images: bool = False
    include_speaker_notes: bool = True
    enable_ocr: bool = False
    template: Optional[str] = None
    include_frontmatter: bool = False


@dataclass
class MarkItDownDocument:
    """Converted document with metadata"""
    markdown_content: str
    metadata: Dict[str, Any]
    word_count: int
    conversion_time: float
    source_format: str
    

class MarkItDownError(MCPError):
    """MarkItDown-specific errors"""
    pass


class MarkItDownMCPClient(HTTPMCPClient):
    """
    MCP client for MarkItDown document conversion.
    
    Supports conversion of:
    - Microsoft Office documents (Word, Excel, PowerPoint)
    - PDF files (with optional OCR)
    - OpenDocument formats
    - Rich Text Format (RTF)
    - And more
    """
    
    def __init__(self, server_url: str, rate_limiter, circuit_breaker):
        """Initialize MarkItDown MCP client"""
        super().__init__(
            server_name="markitdown",
            server_url=server_url,
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker
        )
        self.supported_formats = {
            '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt',
            '.pdf', '.rtf', '.odt', '.ods', '.odp', '.txt',
            '.html', '.htm', '.xml', '.csv', '.tsv'
        }
    
    async def convert_document(
        self,
        file_path: Path,
        options: Optional[ConversionOptions] = None
    ) -> MCPResponse[MarkItDownDocument]:
        """
        Convert document to Markdown.
        
        Args:
            file_path: Path to document file
            options: Conversion options
            
        Returns:
            MCPResponse with converted document
        """
        if options is None:
            options = ConversionOptions()
        
        # Validate file format
        suffix = file_path.suffix.lower()
        if suffix not in self.supported_formats:
            return MCPResponse(
                success=False,
                error={
                    "code": "unsupported_format",
                    "message": f"File format {suffix} is not supported"
                }
            )
        
        request = MCPRequest(
            method="convert_document",
            params={
                "file_path": str(file_path),
                "options": {
                    "preserve_formatting": options.preserve_formatting,
                    "extract_tables": options.extract_tables,
                    "extract_images": options.extract_images,
                    "include_speaker_notes": options.include_speaker_notes,
                    "enable_ocr": options.enable_ocr,
                    "template": options.template,
                    "include_frontmatter": options.include_frontmatter
                }
            }
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        result = response["result"]
        document = MarkItDownDocument(
            markdown_content=result["content"],
            metadata=result.get("metadata", {}),
            word_count=result["metadata"].get("word_count", len(result["content"].split())),
            conversion_time=result.get("conversion_time", 0),
            source_format=suffix
        )
        
        return MCPResponse(success=True, data=document)
    
    async def batch_convert(
        self,
        file_paths: List[Path],
        options: Optional[ConversionOptions] = None
    ) -> List[MCPResponse[MarkItDownDocument]]:
        """
        Convert multiple documents in batch.
        
        Args:
            file_paths: List of document paths
            options: Conversion options (applied to all)
            
        Returns:
            List of conversion results
        """
        if options is None:
            options = ConversionOptions()
        
        # Process documents concurrently
        import asyncio
        tasks = []
        for file_path in file_paths:
            task = self.convert_document(file_path, options)
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
                        "file": str(file_paths[i])
                    }
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def get_document_metadata(
        self,
        file_path: Path
    ) -> MCPResponse[Dict[str, Any]]:
        """
        Extract metadata without full conversion.
        
        Args:
            file_path: Path to document
            
        Returns:
            Document metadata
        """
        request = MCPRequest(
            method="get_metadata",
            params={"file_path": str(file_path)}
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
    
    async def convert_with_custom_rules(
        self,
        file_path: Path,
        rules: Dict[str, Any]
    ) -> MCPResponse[MarkItDownDocument]:
        """
        Convert document with custom transformation rules.
        
        Args:
            file_path: Path to document
            rules: Custom conversion rules
            
        Returns:
            Converted document
        """
        request = MCPRequest(
            method="convert_with_rules",
            params={
                "file_path": str(file_path),
                "rules": rules
            }
        )
        
        response = await self._send_request(request)
        
        if "error" in response:
            return MCPResponse(
                success=False,
                error=response["error"]
            )
        
        result = response["result"]
        document = MarkItDownDocument(
            markdown_content=result["content"],
            metadata=result.get("metadata", {}),
            word_count=len(result["content"].split()),
            conversion_time=result.get("conversion_time", 0),
            source_format=file_path.suffix.lower()
        )
        
        return MCPResponse(success=True, data=document)
    
    async def extract_structured_data(
        self,
        file_path: Path,
        schema: Optional[Dict[str, Any]] = None
    ) -> MCPResponse[Dict[str, Any]]:
        """
        Extract structured data from document.
        
        Args:
            file_path: Path to document
            schema: Optional schema for extraction
            
        Returns:
            Structured data
        """
        request = MCPRequest(
            method="extract_structured",
            params={
                "file_path": str(file_path),
                "schema": schema
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
            data=response["result"]["data"]
        )
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get MarkItDown service health status"""
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
            "version": result.get("version"),
            "supported_formats": result.get("supported_formats", list(self.supported_formats)),
            "circuit_breaker_state": self.circuit_breaker.state.name,
            "rate_limit_remaining": self.rate_limiter.get_remaining_requests(self.server_name)
        }