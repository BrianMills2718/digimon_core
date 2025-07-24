"""
Content Core MCP Client

Client for the content-core server providing access to:
- URL content extraction (web pages)
- Document processing (PDFs, Word docs)
- Video content extraction (YouTube transcripts)
- Audio file processing
- Intelligent auto-engine selection
- Structured JSON responses

Based on: lfnovo/content-core
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .http_client import HTTPMCPClient
from .base_client import MCPResponse
from ...core.circuit_breaker import CircuitBreaker
from ...core.api_rate_limiter import APIRateLimiter
import logging

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Supported content types"""
    WEBPAGE = "webpage"
    PDF = "pdf"
    WORD_DOC = "word"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    TEXT = "text"
    UNKNOWN = "unknown"


class ExtractionEngine(Enum):
    """Content extraction engines"""
    AUTO = "auto"  # Intelligent selection
    BEAUTIFULSOUP = "beautifulsoup"
    PLAYWRIGHT = "playwright"
    PYPDF = "pypdf"
    DOCX = "docx"
    YOUTUBE_TRANSCRIPT = "youtube_transcript"
    WHISPER = "whisper"
    TESSERACT = "tesseract"


@dataclass
class ExtractedContent:
    """Extracted content representation"""
    content_id: str
    source_url: str
    content_type: ContentType
    extraction_engine: str
    title: str
    text: str
    structured_data: Dict[str, Any]
    metadata: Dict[str, Any]
    extraction_time: datetime
    word_count: int
    language: str
    success: bool
    error_message: Optional[str] = None


@dataclass
class DocumentSection:
    """Section of a document"""
    section_id: str
    title: str
    level: int  # Heading level (1-6)
    content: str
    word_count: int
    page_numbers: Optional[List[int]] = None


@dataclass
class MediaTranscript:
    """Transcript from video/audio"""
    transcript_id: str
    source_url: str
    media_type: str  # video, audio
    duration_seconds: float
    language: str
    segments: List[Dict[str, Any]]  # timestamp, text pairs
    full_text: str
    word_count: int


@dataclass
class ExtractedTable:
    """Table extracted from content"""
    table_id: str
    headers: List[str]
    rows: List[List[str]]
    caption: Optional[str] = None
    page_number: Optional[int] = None


@dataclass
class ExtractedImage:
    """Image extracted from content"""
    image_id: str
    url: Optional[str]
    caption: Optional[str]
    alt_text: Optional[str]
    ocr_text: Optional[str]
    page_number: Optional[int] = None


class ContentCoreMCPClient(HTTPMCPClient):
    """
    MCP client for multi-format content extraction.
    
    Provides:
    - Intelligent content type detection
    - Automatic engine selection
    - Structured content extraction
    - Multi-format support
    - OCR capabilities for images
    - Transcript extraction for media
    """
    
    def __init__(self,
                 rate_limiter: APIRateLimiter,
                 circuit_breaker: CircuitBreaker,
                 api_key: Optional[str] = None,
                 server_url: str = "http://localhost:8005"):
        """
        Initialize Content Core MCP client.
        
        Args:
            rate_limiter: Rate limiter instance
            circuit_breaker: Circuit breaker instance
            api_key: Optional API key for premium features
            server_url: MCP server URL
        """
        config = {}
        if api_key:
            config['headers'] = {'X-ContentCore-API-Key': api_key}
        
        super().__init__(
            server_name="content_core",
            server_url=server_url,
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker,
            config=config
        )
    
    async def extract_content(self,
                            url: str,
                            engine: ExtractionEngine = ExtractionEngine.AUTO,
                            extract_tables: bool = True,
                            extract_images: bool = True,
                            extract_links: bool = True,
                            clean_text: bool = True) -> MCPResponse[ExtractedContent]:
        """
        Extract content from any supported URL/file.
        
        Args:
            url: URL or file path to extract from
            engine: Extraction engine (auto-selected if AUTO)
            extract_tables: Extract tables from content
            extract_images: Extract images and their metadata
            extract_links: Extract hyperlinks
            clean_text: Clean and normalize extracted text
            
        Returns:
            MCPResponse containing extracted content
        """
        params = {
            "url": url,
            "engine": engine.value,
            "extract_tables": extract_tables,
            "extract_images": extract_images,
            "extract_links": extract_links,
            "clean_text": clean_text
        }
        
        response = await self.call_method("extract_content", params)
        
        if response.success and response.data:
            content = self._parse_extracted_content(response.data)
            return MCPResponse(success=True, data=content, metadata=response.metadata)
        
        return response
    
    async def extract_webpage(self,
                            url: str,
                            wait_for_selector: Optional[str] = None,
                            remove_selectors: Optional[List[str]] = None,
                            screenshot: bool = False) -> MCPResponse[ExtractedContent]:
        """
        Extract content specifically from web pages.
        
        Args:
            url: Webpage URL
            wait_for_selector: CSS selector to wait for (dynamic content)
            remove_selectors: CSS selectors of elements to remove
            screenshot: Capture screenshot of the page
            
        Returns:
            MCPResponse containing webpage content
        """
        params = {
            "url": url,
            "screenshot": screenshot
        }
        
        if wait_for_selector:
            params["wait_for_selector"] = wait_for_selector
        if remove_selectors:
            params["remove_selectors"] = remove_selectors
        
        response = await self.call_method("extract_webpage", params)
        
        if response.success and response.data:
            content = self._parse_extracted_content(response.data)
            return MCPResponse(success=True, data=content, metadata=response.metadata)
        
        return response
    
    async def extract_pdf(self,
                        url: str,
                        extract_images: bool = True,
                        ocr_images: bool = False,
                        merge_pages: bool = True) -> MCPResponse[ExtractedContent]:
        """
        Extract content from PDF files.
        
        Args:
            url: PDF file URL or path
            extract_images: Extract embedded images
            ocr_images: Run OCR on images
            merge_pages: Merge pages into single text
            
        Returns:
            MCPResponse containing PDF content
        """
        params = {
            "url": url,
            "extract_images": extract_images,
            "ocr_images": ocr_images,
            "merge_pages": merge_pages
        }
        
        response = await self.call_method("extract_pdf", params)
        
        if response.success and response.data:
            content = self._parse_extracted_content(response.data)
            return MCPResponse(success=True, data=content, metadata=response.metadata)
        
        return response
    
    async def extract_document(self,
                             url: str,
                             preserve_formatting: bool = False,
                             extract_comments: bool = True,
                             extract_metadata: bool = True) -> MCPResponse[ExtractedContent]:
        """
        Extract content from Word/Office documents.
        
        Args:
            url: Document URL or path
            preserve_formatting: Preserve text formatting
            extract_comments: Extract document comments
            extract_metadata: Extract document metadata
            
        Returns:
            MCPResponse containing document content
        """
        params = {
            "url": url,
            "preserve_formatting": preserve_formatting,
            "extract_comments": extract_comments,
            "extract_metadata": extract_metadata
        }
        
        response = await self.call_method("extract_document", params)
        
        if response.success and response.data:
            content = self._parse_extracted_content(response.data)
            return MCPResponse(success=True, data=content, metadata=response.metadata)
        
        return response
    
    async def extract_media_transcript(self,
                                     url: str,
                                     language: Optional[str] = None,
                                     timestamps: bool = True,
                                     speaker_labels: bool = False) -> MCPResponse[MediaTranscript]:
        """
        Extract transcript from video/audio files.
        
        Args:
            url: Media file URL (YouTube, audio file, etc.)
            language: Language code for transcription
            timestamps: Include timestamps
            speaker_labels: Attempt speaker diarization
            
        Returns:
            MCPResponse containing media transcript
        """
        params = {
            "url": url,
            "timestamps": timestamps,
            "speaker_labels": speaker_labels
        }
        
        if language:
            params["language"] = language
        
        response = await self.call_method("extract_media_transcript", params)
        
        if response.success and response.data:
            transcript = self._parse_media_transcript(response.data)
            return MCPResponse(success=True, data=transcript, metadata=response.metadata)
        
        return response
    
    async def extract_structured_data(self,
                                    url: str,
                                    schema: Optional[Dict[str, Any]] = None) -> MCPResponse[Dict[str, Any]]:
        """
        Extract structured data from content.
        
        Args:
            url: Content URL
            schema: Expected data schema (for validation)
            
        Returns:
            MCPResponse containing structured data
        """
        params = {"url": url}
        
        if schema:
            params["schema"] = schema
        
        response = await self.call_method("extract_structured_data", params)
        
        if response.success:
            return MCPResponse(
                success=True,
                data=response.data.get("structured_data", {}),
                metadata=response.metadata
            )
        
        return response
    
    async def batch_extract(self,
                          urls: List[str],
                          parallel: int = 5) -> MCPResponse[List[ExtractedContent]]:
        """
        Extract content from multiple URLs in batch.
        
        Args:
            urls: List of URLs to process
            parallel: Number of parallel extractions
            
        Returns:
            MCPResponse containing list of extracted content
        """
        params = {
            "urls": urls[:100],  # Limit batch size
            "parallel": min(parallel, 10)
        }
        
        response = await self.call_method("batch_extract", params)
        
        if response.success and response.data:
            contents = [self._parse_extracted_content(c) for c in response.data.get("results", [])]
            return MCPResponse(success=True, data=contents, metadata=response.metadata)
        
        return response
    
    async def detect_content_type(self, url: str) -> MCPResponse[ContentType]:
        """
        Detect the content type of a URL.
        
        Args:
            url: URL to analyze
            
        Returns:
            MCPResponse containing detected content type
        """
        params = {"url": url}
        
        response = await self.call_method("detect_content_type", params)
        
        if response.success and response.data:
            try:
                content_type = ContentType(response.data.get("content_type", "unknown"))
            except:
                content_type = ContentType.UNKNOWN
            
            return MCPResponse(success=True, data=content_type, metadata=response.metadata)
        
        return response
    
    # Helper Methods
    
    def _parse_extracted_content(self, data: Dict[str, Any]) -> ExtractedContent:
        """Parse extracted content from MCP response"""
        # Parse extraction time
        extraction_time = datetime.now()
        if data.get("extraction_time"):
            try:
                extraction_time = datetime.fromisoformat(data["extraction_time"])
            except:
                pass
        
        # Parse content type
        content_type = ContentType.UNKNOWN
        if data.get("content_type"):
            try:
                content_type = ContentType(data["content_type"])
            except:
                pass
        
        return ExtractedContent(
            content_id=data.get("content_id", ""),
            source_url=data.get("source_url", ""),
            content_type=content_type,
            extraction_engine=data.get("extraction_engine", ""),
            title=data.get("title", ""),
            text=data.get("text", ""),
            structured_data=data.get("structured_data", {}),
            metadata=data.get("metadata", {}),
            extraction_time=extraction_time,
            word_count=data.get("word_count", 0),
            language=data.get("language", "en"),
            success=data.get("success", True),
            error_message=data.get("error_message")
        )
    
    def _parse_media_transcript(self, data: Dict[str, Any]) -> MediaTranscript:
        """Parse media transcript from MCP response"""
        return MediaTranscript(
            transcript_id=data.get("transcript_id", ""),
            source_url=data.get("source_url", ""),
            media_type=data.get("media_type", ""),
            duration_seconds=data.get("duration_seconds", 0.0),
            language=data.get("language", "en"),
            segments=data.get("segments", []),
            full_text=data.get("full_text", ""),
            word_count=data.get("word_count", 0)
        )