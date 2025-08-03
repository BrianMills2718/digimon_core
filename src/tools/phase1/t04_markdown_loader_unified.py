"""
T04: Markdown Document Loader - Unified Interface Implementation

Loads and parses Markdown documents with structure preservation and metadata extraction.
"""

from typing import Dict, Any, Optional, List
import os
from pathlib import Path
import uuid
from datetime import datetime
import logging
import re
import yaml
import markdown
from markdown.extensions.toc import TocExtension
from markdown.extensions.meta import MetaExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.codehilite import CodeHiliteExtension

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class T04MarkdownLoaderUnified(BaseTool):
    """T04: Markdown Document Loader with unified interface"""
    
    def __init__(self, service_manager: ServiceManager):
        """Initialize with service manager"""
        super().__init__(service_manager)
        self.tool_id = "T04_MARKDOWN_LOADER"
        self.identity_service = service_manager.identity_service
        self.provenance_service = service_manager.provenance_service
        self.quality_service = service_manager.quality_service
        self._temp_files = []
        
        # Initialize markdown parser with extensions
        self.md = markdown.Markdown(extensions=[
            'meta',
            'toc',
            'tables',
            'codehilite',
            'fenced_code',
            'nl2br',
            'sane_lists',
            'smarty',
            'admonition'
        ])
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="Markdown Document Loader",
            description="Load and parse Markdown documents with structure preservation",
            category="document_processing",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to markdown file to load"
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
                            "structure": {
                                "type": "object",
                                "properties": {
                                    "headings": {"type": "array"},
                                    "links": {"type": "array"},
                                    "images": {"type": "array"},
                                    "tables": {"type": "array"},
                                    "code_blocks": {"type": "array"},
                                    "max_heading_level": {"type": "integer"},
                                    "has_lists": {"type": "boolean"},
                                    "has_blockquotes": {"type": "boolean"},
                                    "total_sections": {"type": "integer"}
                                }
                            },
                            "confidence": {"type": "number"},
                            "quality_tier": {"type": "string"},
                            "created_at": {"type": "string"}
                        },
                        "required": ["document_id", "text", "html", "metadata", "structure", "confidence"]
                    }
                },
                "required": ["document"]
            },
            dependencies=["identity_service", "provenance_service", "quality_service"],
            performance_requirements={
                "max_execution_time": 10.0,  # 10 seconds for markdown parsing
                "max_memory_mb": 512,        # 512MB for markdown processing
                "min_confidence": 0.8        # Minimum confidence threshold
            },
            error_conditions=[
                "FILE_NOT_FOUND",
                "INVALID_FILE_TYPE",
                "PARSING_ERROR",
                "PERMISSION_DENIED",
                "FILE_ACCESS_ERROR",
                "MEMORY_LIMIT_EXCEEDED",
                "INVALID_MARKDOWN"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute markdown loading with unified interface"""
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
            
            # Load markdown content
            load_result = self._load_markdown_file(file_path, request.parameters)
            
            if load_result["status"] != "success":
                return self._create_error_result(
                    request,
                    load_result.get("error_code", "PARSING_ERROR"),
                    load_result["error"]
                )
            
            text = load_result["text"]
            html = load_result["html"]
            metadata = load_result["metadata"]
            structure = load_result["structure"]
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                text=text,
                structure=structure,
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
                "html": html,
                "metadata": metadata,
                "structure": structure,
                "confidence": confidence,
                "created_at": datetime.now().isoformat(),
                "tool_version": "1.0.0"
            }
            
            # Assess quality
            quality_result = self.quality_service.assess_confidence(
                object_ref=document_ref,
                base_confidence=confidence,
                factors={
                    "structure_richness": min(1.0, len(structure.get("headings", [])) / 10),
                    "content_length": min(1.0, len(text) / 10000),
                    "metadata_completeness": min(1.0, len(metadata) / 5),
                    "has_code": 1.0 if structure.get("code_blocks") else 0.7,
                    "has_links": 1.0 if structure.get("links") else 0.8
                },
                metadata={
                    "file_type": file_path.suffix.lower(),
                    "has_frontmatter": bool(metadata),
                    "structure_depth": structure.get("max_heading_level", 0)
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
                    "html_length": len(html),
                    "heading_count": len(structure.get("headings", [])),
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
                    "parser": "python-markdown",
                    "extensions_used": ["meta", "toc", "tables", "codehilite"]
                },
                execution_time=execution_time,
                memory_used=memory_used
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in {self.tool_id}: {e}", exc_info=True)
            return self._create_error_result(
                request,
                "UNEXPECTED_ERROR",
                f"Unexpected error during markdown loading: {str(e)}"
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
            allowed_extensions = ['.md', '.markdown', '.mdown', '.mkd', '.mdx']
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
    
    def _load_markdown_file(self, file_path: Path, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Load and parse markdown file"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            # Extract frontmatter if requested
            metadata = {}
            content = raw_content
            
            if parameters.get("extract_frontmatter", True):
                frontmatter_result = self._extract_frontmatter(raw_content)
                metadata = frontmatter_result["metadata"]
                content = frontmatter_result["content"]
            
            # Parse markdown to HTML
            self.md.reset()
            html = self.md.convert(content)
            
            # Extract markdown metadata (from Meta extension)
            if hasattr(self.md, 'Meta'):
                for key, values in self.md.Meta.items():
                    metadata[key] = values[0] if len(values) == 1 else values
            
            # Extract structure
            structure = self._extract_structure(content, html, parameters)
            
            return {
                "status": "success",
                "text": raw_content,
                "html": html,
                "metadata": metadata,
                "structure": structure
            }
            
        except PermissionError as e:
            logger.error(f"Permission denied: {str(e)}")
            return {
                "status": "error",
                "error": f"Permission denied: {str(e)}",
                "error_code": "PERMISSION_DENIED"
            }
        except Exception as e:
            logger.error(f"Failed to load markdown file: {str(e)}")
            return {
                "status": "error",
                "error": f"Failed to load markdown file: {str(e)}",
                "error_code": "FILE_ACCESS_ERROR"
            }
    
    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown content"""
        metadata = {}
        
        # Check for YAML frontmatter
        if content.startswith('---\n'):
            try:
                # Find end of frontmatter
                end_index = content.find('\n---\n', 4)
                if end_index != -1:
                    yaml_content = content[4:end_index]
                    # Parse YAML
                    metadata = yaml.safe_load(yaml_content) or {}
                    # Remove frontmatter from content
                    content = content[end_index + 5:]
            except yaml.YAMLError as e:
                logger.warning(f"Failed to parse YAML frontmatter: {e}")
                metadata["frontmatter_error"] = str(e)
        
        return {
            "metadata": metadata,
            "content": content
        }
    
    def _extract_structure(self, content: str, html: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structural information from markdown"""
        structure = {
            "headings": [],
            "links": [],
            "images": [],
            "tables": [],
            "code_blocks": [],
            "max_heading_level": 0,
            "has_lists": False,
            "has_blockquotes": False,
            "total_sections": 0
        }
        
        # Extract headings
        heading_pattern = r'^(#{1,6})\s+(.+)$'
        for match in re.finditer(heading_pattern, content, re.MULTILINE):
            level = len(match.group(1))
            title = match.group(2).strip()
            structure["headings"].append({
                "level": level,
                "title": title,
                "line": content[:match.start()].count('\n') + 1
            })
            structure["max_heading_level"] = max(structure["max_heading_level"], level)
        
        structure["total_sections"] = len(structure["headings"])
        
        # Extract links if requested
        if parameters.get("extract_links", True):
            # Inline links: [text](url)
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            for match in re.finditer(link_pattern, content):
                structure["links"].append({
                    "text": match.group(1),
                    "url": match.group(2),
                    "type": "inline"
                })
            
            # Reference links: [text][ref]
            ref_link_pattern = r'\[([^\]]+)\]\[([^\]]+)\]'
            ref_def_pattern = r'^\[([^\]]+)\]:\s*(.+)(?:\s+"([^"]+)")?$'
            
            # First collect reference definitions
            ref_defs = {}
            for match in re.finditer(ref_def_pattern, content, re.MULTILINE):
                ref_defs[match.group(1)] = {
                    "url": match.group(2),
                    "title": match.group(3) if match.group(3) else None
                }
            
            # Then find reference links
            for match in re.finditer(ref_link_pattern, content):
                ref = match.group(2)
                if ref in ref_defs:
                    structure["links"].append({
                        "text": match.group(1),
                        "url": ref_defs[ref]["url"],
                        "title": ref_defs[ref]["title"],
                        "type": "reference"
                    })
        
        # Extract images if requested
        if parameters.get("extract_images", True):
            # Inline images: ![alt](url)
            img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
            for match in re.finditer(img_pattern, content):
                structure["images"].append({
                    "alt": match.group(1),
                    "url": match.group(2),
                    "type": "inline"
                })
            
            # Reference images: ![alt][ref]
            ref_img_pattern = r'!\[([^\]]*)\]\[([^\]]+)\]'
            for match in re.finditer(ref_img_pattern, content):
                ref = match.group(2)
                if ref in ref_defs:
                    structure["images"].append({
                        "alt": match.group(1),
                        "url": ref_defs[ref]["url"],
                        "type": "reference"
                    })
        
        # Extract tables if requested
        if parameters.get("extract_tables", True):
            # Simple table detection
            table_pattern = r'^\|.*\|$'
            table_lines = []
            in_table = False
            
            for line in content.split('\n'):
                if re.match(table_pattern, line):
                    if not in_table:
                        in_table = True
                        table_lines = []
                    table_lines.append(line)
                elif in_table and line.strip() == '':
                    # End of table
                    if len(table_lines) >= 2:  # Header + separator minimum
                        cols = len(table_lines[0].split('|')) - 2  # Exclude empty splits
                        rows = len(table_lines) - 1  # Exclude separator
                        structure["tables"].append({
                            "rows": rows,
                            "columns": cols,
                            "has_header": True
                        })
                    in_table = False
                    table_lines = []
            
            # Check if last table wasn't closed
            if in_table and len(table_lines) >= 2:
                cols = len(table_lines[0].split('|')) - 2
                rows = len(table_lines) - 1
                structure["tables"].append({
                    "rows": rows,
                    "columns": cols,
                    "has_header": True
                })
        
        # Extract code blocks if requested
        if parameters.get("extract_code_blocks", True):
            # Fenced code blocks ```lang
            code_pattern = r'```(\w*)\n(.*?)```'
            for match in re.finditer(code_pattern, content, re.DOTALL):
                language = match.group(1) or "plain"
                code = match.group(2).rstrip()
                structure["code_blocks"].append({
                    "language": language,
                    "code": code,
                    "lines": len(code.split('\n'))
                })
        
        # Check for lists
        list_pattern = r'^\s*[-*+]\s+|^\s*\d+\.\s+'
        if re.search(list_pattern, content, re.MULTILINE):
            structure["has_lists"] = True
        
        # Check for blockquotes
        blockquote_pattern = r'^\s*>\s+'
        if re.search(blockquote_pattern, content, re.MULTILINE):
            structure["has_blockquotes"] = True
        
        # Analyze structure if requested
        if parameters.get("analyze_structure", True):
            structure["structure_score"] = self._calculate_structure_score(structure)
        
        return structure
    
    def _calculate_structure_score(self, structure: Dict[str, Any]) -> float:
        """Calculate a score for document structure richness"""
        score = 0.5  # Base score
        
        # Add points for various elements
        if structure["headings"]:
            score += min(0.2, len(structure["headings"]) * 0.02)
        
        if structure["links"]:
            score += min(0.1, len(structure["links"]) * 0.01)
        
        if structure["images"]:
            score += min(0.1, len(structure["images"]) * 0.02)
        
        if structure["tables"]:
            score += 0.05
        
        if structure["code_blocks"]:
            score += min(0.1, len(structure["code_blocks"]) * 0.02)
        
        if structure["has_lists"]:
            score += 0.025
        
        if structure["has_blockquotes"]:
            score += 0.025
        
        return min(1.0, score)
    
    def _calculate_confidence(self, text: str, structure: Dict[str, Any], 
                            metadata: Dict[str, Any], file_size: int) -> float:
        """Calculate confidence score for loaded markdown"""
        # Base confidence for successfully parsed markdown
        base_confidence = 0.85
        
        # Factors that affect confidence
        factors = []
        
        # Text length factor
        if len(text) > 100:
            factors.append(0.95)
        elif len(text) > 10:
            factors.append(0.85)
        elif len(text) > 0:
            factors.append(0.70)
        else:
            factors.append(0.30)  # Empty file
        
        # Structure richness factor
        structure_score = structure.get("structure_score", 0.7)
        factors.append(structure_score)
        
        # Metadata factor
        if metadata:
            factors.append(0.95)
        else:
            factors.append(0.85)
        
        # File size factor
        if file_size > 1024:  # > 1KB
            factors.append(0.95)
        elif file_size > 0:
            factors.append(0.85)
        else:
            factors.append(0.40)
        
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
            # Check if markdown library is available
            try:
                import markdown
                markdown_available = True
                markdown_version = markdown.__version__ if hasattr(markdown, '__version__') else "unknown"
            except ImportError:
                markdown_available = False
                markdown_version = None
            
            # Check if yaml library is available
            try:
                import yaml
                yaml_available = True
                yaml_version = yaml.__version__ if hasattr(yaml, '__version__') else "unknown"
            except ImportError:
                yaml_available = False
                yaml_version = None
            
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
            
            healthy = markdown_available and services_healthy
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success" if healthy else "error",
                data={
                    "healthy": healthy,
                    "markdown_available": markdown_available,
                    "markdown_version": markdown_version,
                    "yaml_available": yaml_available,
                    "yaml_version": yaml_version,
                    "services_healthy": services_healthy,
                    "supported_formats": [".md", ".markdown", ".mdown", ".mkd", ".mdx"],
                    "supported_extensions": ["meta", "toc", "tables", "codehilite", "fenced_code"],
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