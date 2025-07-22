"""
T07: HTML Document Loader - Unified Interface Implementation

Loads and parses HTML documents with text extraction and metadata parsing.
"""

from typing import Dict, Any, Optional, List
import os
from pathlib import Path
import uuid
from datetime import datetime
import logging
from bs4 import BeautifulSoup
import re

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class T07HTMLLoaderUnified(BaseTool):
    """T07: HTML Document Loader with unified interface"""
    
    def __init__(self, service_manager: ServiceManager):
        """Initialize with service manager"""
        super().__init__(service_manager)
        self.tool_id = "T07"
        self.identity_service = service_manager.identity_service
        self.provenance_service = service_manager.provenance_service
        self.quality_service = service_manager.quality_service
        self._temp_files = []
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="HTML Document Loader",
            description="Load and parse HTML documents with text extraction",
            category="document_processing",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to HTML file to load"
                    },
                    "workflow_id": {
                        "type": "string",
                        "description": "Optional workflow ID for tracking"
                    }
                },
                "required": ["file_path"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "document": {
                        "type": "object",
                        "properties": {
                            "document_id": {"type": "string"},
                            "document_ref": {"type": "string"},
                            "file_path": {"type": "string"},
                            "file_name": {"type": "string"},
                            "file_size": {"type": "integer"},
                            "text": {"type": "string"},
                            "html": {"type": "string"},
                            "metadata": {"type": "object"},
                            "element_count": {"type": "object"},
                            "forms": {"type": "array"},
                            "tables": {"type": "array"},
                            "confidence": {"type": "number"},
                            "quality_tier": {"type": "string"},
                            "created_at": {"type": "string"}
                        },
                        "required": ["document_id", "text", "html", "metadata", "confidence"]
                    }
                },
                "required": ["document"]
            },
            dependencies=["identity_service", "provenance_service", "quality_service"],
            performance_requirements={
                "max_execution_time": 15.0,  # 15 seconds for large HTML
                "max_memory_mb": 1024,       # 1GB for HTML processing
                "min_confidence": 0.8        # Minimum confidence threshold
            },
            error_conditions=[
                "FILE_NOT_FOUND",
                "INVALID_FILE_TYPE",
                "HTML_MALFORMED",
                "PARSING_FAILED",
                "ENCODING_ERROR",
                "MEMORY_LIMIT_EXCEEDED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute HTML loading with unified interface"""
        self._start_execution()
        
        try:
            # Validate input
            if not self.validate_input(request.input_data):
                return self._create_error_result(
                    request,
                    "INVALID_INPUT",
                    "Input validation failed. Required: file_path"
                )
            
            # Extract parameters
            file_path = request.input_data.get("file_path")
            workflow_id = request.input_data.get("workflow_id")
            
            # Validate file path
            validation_result = self._validate_file_path(file_path)
            if not validation_result["valid"]:
                return self._create_error_result(
                    request,
                    validation_result["error_code"],
                    validation_result["error_message"]
                )
            
            file_path = Path(file_path)
            
            # Start provenance tracking
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="load_document",
                used={},
                parameters={
                    "file_path": str(file_path),
                    "workflow_id": workflow_id
                }
            )
            
            # Generate workflow ID if not provided
            if not workflow_id:
                workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
            
            # Create document ID
            document_id = f"{workflow_id}_{file_path.stem}"
            document_ref = f"storage://document/{document_id}"
            
            # Load and parse HTML
            parse_result = self._parse_html(file_path, request.parameters)
            
            if parse_result["status"] != "success":
                return self._create_error_result(
                    request,
                    parse_result.get("error_code", "EXTRACTION_FAILED"),
                    parse_result["error"]
                )
            
            # Extract components based on parameters
            soup = parse_result["soup"]
            text = self._extract_text(soup, request.parameters)
            metadata = self._extract_metadata(soup)
            element_count = self._count_elements(soup)
            
            # Extract optional components
            forms = self._extract_forms(soup) if request.parameters.get("extract_forms", False) else None
            tables = self._extract_tables(soup) if request.parameters.get("extract_tables", False) else None
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                text=text,
                element_count=element_count,
                metadata=metadata,
                file_size=file_path.stat().st_size
            )
            
            # Create document data
            document_data = {
                "document_id": document_id,
                "document_ref": document_ref,
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "text": text,
                "html": parse_result["html"],
                "metadata": metadata,
                "element_count": element_count,
                "confidence": confidence,
                "created_at": datetime.now().isoformat(),
                "tool_version": "1.0.0"
            }
            
            # Add optional fields
            if forms is not None:
                document_data["forms"] = forms
            if tables is not None:
                document_data["tables"] = tables
            
            # Assess quality
            quality_result = self.quality_service.assess_confidence(
                object_ref=document_ref,
                base_confidence=confidence,
                factors={
                    "text_length": min(1.0, len(text) / 10000),
                    "element_richness": min(1.0, element_count.get("total", 0) / 100),
                    "metadata_completeness": self._calculate_metadata_completeness(metadata),
                    "file_size": min(1.0, file_path.stat().st_size / (1024 * 1024))
                },
                metadata={
                    "file_type": file_path.suffix.lower(),
                    "element_types": list(element_count.keys())
                }
            )
            
            if quality_result["status"] == "success":
                document_data["confidence"] = quality_result["confidence"]
                document_data["quality_tier"] = quality_result["quality_tier"]
            
            # Complete provenance
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=[document_ref],
                success=True,
                metadata={
                    "text_length": len(text),
                    "element_count": element_count.get("total", 0),
                    "has_metadata": bool(metadata),
                    "confidence": document_data["confidence"]
                }
            )
            
            # Get execution metrics
            execution_time, memory_used = self._end_execution()
            
            # Create success result
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "document": document_data
                },
                metadata={
                    "operation_id": operation_id,
                    "workflow_id": workflow_id,
                    "parser": "beautifulsoup4"
                },
                execution_time=execution_time,
                memory_used=memory_used
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in {self.tool_id}: {e}", exc_info=True)
            return self._create_error_result(
                request,
                "UNEXPECTED_ERROR",
                f"Unexpected error during HTML loading: {str(e)}"
            )
    
    def _validate_file_path(self, file_path: str) -> Dict[str, Any]:
        """Validate file path for security and existence"""
        if not file_path:
            return {
                "valid": False,
                "error_code": "INVALID_INPUT",
                "error_message": "File path cannot be empty"
            }
        
        try:
            path = Path(file_path)
            
            # Check if path exists
            if not path.exists():
                return {
                    "valid": False,
                    "error_code": "FILE_NOT_FOUND",
                    "error_message": f"File not found: {file_path}"
                }
            
            # Check if it's a file
            if not path.is_file():
                return {
                    "valid": False,
                    "error_code": "INVALID_INPUT",
                    "error_message": f"Path is not a file: {file_path}"
                }
            
            # Check extension
            allowed_extensions = ['.html', '.htm']
            if path.suffix.lower() not in allowed_extensions:
                return {
                    "valid": False,
                    "error_code": "INVALID_FILE_TYPE",
                    "error_message": f"Invalid file extension. Allowed: {allowed_extensions}"
                }
            
            # Basic security check - prevent path traversal
            if ".." in str(path) or str(path).startswith("/etc"):
                return {
                    "valid": False,
                    "error_code": "VALIDATION_FAILED",
                    "error_message": "Invalid file path"
                }
            
            return {"valid": True}
            
        except Exception as e:
            return {
                "valid": False,
                "error_code": "VALIDATION_FAILED",
                "error_message": f"Path validation failed: {str(e)}"
            }
    
    def _parse_html(self, file_path: Path, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Parse HTML file using BeautifulSoup"""
        try:
            encoding = parameters.get("encoding", "utf-8")
            
            with open(file_path, 'r', encoding=encoding) as f:
                html_content = f.read()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            return {
                "status": "success",
                "soup": soup,
                "html": html_content
            }
            
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error: {str(e)}")
            return {
                "status": "error",
                "error": f"Encoding error: {str(e)}",
                "error_code": "ENCODING_ERROR"
            }
        except Exception as e:
            logger.error(f"Failed to parse HTML: {str(e)}")
            return {
                "status": "error",
                "error": f"Failed to parse HTML: {str(e)}",
                "error_code": "PARSING_FAILED"
            }
    
    def _extract_text(self, soup: BeautifulSoup, parameters: Dict[str, Any]) -> str:
        """Extract text content from parsed HTML"""
        # Remove scripts and styles if requested
        if parameters.get("exclude_scripts", True):
            for script in soup(["script"]):
                script.decompose()
        
        if parameters.get("exclude_styles", True):
            for style in soup(["style"]):
                style.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from HTML head"""
        metadata = {}
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.string
        
        # Extract meta tags
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            # Standard meta tags
            if tag.get('name'):
                metadata[tag['name']] = tag.get('content', '')
            # Open Graph tags
            elif tag.get('property'):
                metadata[tag['property']] = tag.get('content', '')
            # Charset
            elif tag.get('charset'):
                metadata['charset'] = tag['charset']
        
        # Extract canonical link
        canonical = soup.find('link', {'rel': 'canonical'})
        if canonical and canonical.get('href'):
            metadata['canonical'] = canonical['href']
        
        # Extract language
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            metadata['language'] = html_tag['lang']
        
        return metadata
    
    def _count_elements(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Count different types of HTML elements"""
        element_count = {}
        
        # Common elements to count
        elements_to_count = [
            'div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'table', 'form', 'img', 'a',
            'span', 'article', 'section', 'header', 'footer'
        ]
        
        total = 0
        for element in elements_to_count:
            count = len(soup.find_all(element))
            if count > 0:
                element_count[element] = count
                total += count
        
        element_count['total'] = total
        
        return element_count
    
    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract form data from HTML"""
        forms = []
        
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get').lower(),
                'fields': []
            }
            
            # Extract input fields
            for input_tag in form.find_all(['input', 'textarea', 'select']):
                field = {
                    'type': input_tag.name,
                    'name': input_tag.get('name', ''),
                    'id': input_tag.get('id', ''),
                    'placeholder': input_tag.get('placeholder', '')
                }
                
                if input_tag.name == 'input':
                    field['input_type'] = input_tag.get('type', 'text')
                
                form_data['fields'].append(field)
            
            forms.append(form_data)
        
        return forms
    
    def _extract_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract table data from HTML"""
        tables = []
        
        for table in soup.find_all('table'):
            table_data = {
                'headers': [],
                'rows': []
            }
            
            # Extract headers
            thead = table.find('thead')
            if thead:
                header_row = thead.find('tr')
                if header_row:
                    table_data['headers'] = [
                        th.get_text(strip=True) 
                        for th in header_row.find_all(['th', 'td'])
                    ]
            else:
                # Try to find headers in first row
                first_row = table.find('tr')
                if first_row and first_row.find('th'):
                    table_data['headers'] = [
                        th.get_text(strip=True) 
                        for th in first_row.find_all('th')
                    ]
            
            # Extract rows
            tbody = table.find('tbody') or table
            for row in tbody.find_all('tr'):
                # Skip header rows
                if row.find('th') and not table_data['headers']:
                    continue
                
                row_data = [
                    td.get_text(strip=True) 
                    for td in row.find_all(['td', 'th'])
                ]
                if row_data:
                    table_data['rows'].append(row_data)
            
            tables.append(table_data)
        
        return tables
    
    def _calculate_metadata_completeness(self, metadata: Dict[str, Any]) -> float:
        """Calculate metadata completeness score"""
        important_fields = ['title', 'description', 'keywords', 'author']
        present = sum(1 for field in important_fields if field in metadata)
        return present / len(important_fields) if important_fields else 0.0
    
    def _calculate_confidence(self, text: str, element_count: Dict[str, int], 
                            metadata: Dict[str, Any], file_size: int) -> float:
        """Calculate confidence score for loaded HTML"""
        base_confidence = 0.9  # High confidence for parsed HTML
        
        # Factors that affect confidence
        factors = []
        
        # Text length factor
        if len(text) > 1000:
            factors.append(0.95)
        elif len(text) > 100:
            factors.append(0.85)
        else:
            factors.append(0.60)
        
        # Element richness factor
        total_elements = element_count.get('total', 0)
        if total_elements > 50:
            factors.append(0.95)
        elif total_elements > 10:
            factors.append(0.90)
        else:
            factors.append(0.75)
        
        # Metadata factor
        if len(metadata) > 3:
            factors.append(0.95)
        elif len(metadata) > 0:
            factors.append(0.85)
        else:
            factors.append(0.70)
        
        # File size factor
        if file_size > 1024 * 10:  # > 10KB
            factors.append(0.95)
        elif file_size > 1024:  # > 1KB
            factors.append(0.90)
        else:
            factors.append(0.80)
        
        # Calculate weighted average
        if factors:
            final_confidence = (base_confidence + sum(factors)) / (len(factors) + 1)
        else:
            final_confidence = base_confidence
        
        # Ensure confidence is in valid range
        return max(0.1, min(1.0, final_confidence))
    
    def health_check(self) -> ToolResult:
        """Check tool health and readiness"""
        try:
            # Check if BeautifulSoup is available
            try:
                from bs4 import BeautifulSoup
                bs4_available = True
                bs4_version = BeautifulSoup.__version__ if hasattr(BeautifulSoup, '__version__') else "unknown"
            except ImportError:
                bs4_available = False
                bs4_version = None
            
            # Check service dependencies
            services_healthy = True
            if self.services:
                try:
                    # Basic check that services exist
                    _ = self.identity_service
                    _ = self.provenance_service
                    _ = self.quality_service
                except:
                    services_healthy = False
            
            healthy = bs4_available and services_healthy
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success" if healthy else "error",
                data={
                    "healthy": healthy,
                    "beautifulsoup_available": bs4_available,
                    "beautifulsoup_version": bs4_version,
                    "services_healthy": services_healthy,
                    "supported_formats": [".html", ".htm"],
                    "status": self.status.value
                },
                metadata={
                    "timestamp": datetime.now().isoformat()
                },
                execution_time=0.0,
                memory_used=0
            )
            
        except Exception as e:
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={"healthy": False},
                metadata={"error": str(e)},
                execution_time=0.0,
                memory_used=0,
                error_code="HEALTH_CHECK_FAILED",
                error_message=str(e)
            )
    
    def cleanup(self) -> bool:
        """Clean up any temporary files"""
        try:
            # Clean up temp files if any
            for temp_file in self._temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
            
            self._temp_files = []
            self.status = ToolStatus.READY
            return True
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False