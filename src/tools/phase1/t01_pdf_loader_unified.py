"""
T01: PDF Document Loader - Unified Interface Implementation

Migrated to use the unified tool interface while maintaining all existing functionality.
"""

from typing import Dict, Any, Optional, List
import os
from pathlib import Path
import uuid
from datetime import datetime
import pypdf
import logging

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus
from src.core.service_manager import ServiceManager
from src.core.advanced_data_models import Document, ObjectType, QualityTier

logger = logging.getLogger(__name__)


class T01PDFLoaderUnified(BaseTool):
    """T01: PDF Document Loader with unified interface"""
    
    def __init__(self, service_manager: ServiceManager):
        """Initialize with service manager"""
        super().__init__(service_manager)
        self.tool_id = "T01"
        self.identity_service = service_manager.identity_service
        self.provenance_service = service_manager.provenance_service
        self.quality_service = service_manager.quality_service
        self._temp_files = []
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="PDF Document Loader",
            description="Load and extract text from PDF documents with confidence scoring",
            category="document_processing",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to PDF or text file to load"
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
                            "page_count": {"type": "integer"},
                            "text": {"type": "string"},
                            "text_length": {"type": "integer"},
                            "confidence": {"type": "number"},
                            "quality_tier": {"type": "string"},
                            "created_at": {"type": "string"}
                        },
                        "required": ["document_id", "text", "confidence", "page_count"]
                    }
                },
                "required": ["document"]
            },
            dependencies=["identity_service", "provenance_service", "quality_service"],
            performance_requirements={
                "max_execution_time": 30.0,  # 30 seconds for large PDFs
                "max_memory_mb": 2048,       # 2GB for PDF processing
                "min_confidence": 0.8        # Minimum confidence threshold
            },
            error_conditions=[
                "FILE_NOT_FOUND",
                "INVALID_FILE_TYPE",
                "PDF_ENCRYPTED",
                "PDF_CORRUPTED",
                "EXTRACTION_FAILED",
                "MEMORY_LIMIT_EXCEEDED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute PDF loading with unified interface"""
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
            
            # Extract text based on file type
            if file_path.suffix.lower() == '.pdf':
                extraction_result = self._extract_text_from_pdf(file_path)
            elif file_path.suffix.lower() == '.txt':
                extraction_result = self._extract_text_from_txt(file_path)
            else:
                return self._create_error_result(
                    request,
                    "INVALID_FILE_TYPE",
                    f"Unsupported file type: {file_path.suffix}"
                )
            
            if extraction_result["status"] != "success":
                return self._create_error_result(
                    request,
                    extraction_result.get("error_code", "EXTRACTION_FAILED"),
                    extraction_result["error"]
                )
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                text=extraction_result["text"],
                page_count=extraction_result["page_count"],
                file_size=file_path.stat().st_size
            )
            
            # Create document data
            document_data = {
                "document_id": document_id,
                "document_ref": document_ref,
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "page_count": extraction_result["page_count"],
                "text": extraction_result["text"],
                "text_length": len(extraction_result["text"]),
                "confidence": confidence,
                "created_at": datetime.now().isoformat(),
                "tool_version": "1.0.0",
                "extraction_method": "pypdf" if file_path.suffix.lower() == '.pdf' else "text"
            }
            
            # Assess quality
            quality_result = self.quality_service.assess_confidence(
                object_ref=document_ref,
                base_confidence=confidence,
                factors={
                    "text_length": min(1.0, len(extraction_result["text"]) / 10000),
                    "page_count": min(1.0, extraction_result["page_count"] / 10),
                    "file_size": min(1.0, file_path.stat().st_size / (1024 * 1024))
                },
                metadata={
                    "extraction_method": document_data["extraction_method"],
                    "file_type": file_path.suffix.lower()
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
                    "page_count": extraction_result["page_count"],
                    "text_length": len(extraction_result["text"]),
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
                    "extraction_method": document_data["extraction_method"]
                },
                execution_time=execution_time,
                memory_used=memory_used
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in {self.tool_id}: {e}", exc_info=True)
            return self._create_error_result(
                request,
                "UNEXPECTED_ERROR",
                f"Unexpected error during PDF loading: {str(e)}"
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
            allowed_extensions = ['.pdf', '.txt']
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
    
    def _extract_text_from_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from PDF using pypdf"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                # Check if encrypted
                if pdf_reader.is_encrypted:
                    return {
                        "status": "error",
                        "error": "PDF is encrypted and cannot be read",
                        "error_code": "PDF_ENCRYPTED"
                    }
                
                total_pages = len(pdf_reader.pages)
                
                # Extract text from all pages
                text_pages = []
                for page_num in range(total_pages):
                    try:
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        text_pages.append(page_text)
                    except Exception as e:
                        # Continue with other pages if one fails
                        text_pages.append(f"[Error extracting page {page_num + 1}: {str(e)}]")
                
                # Combine all pages
                full_text = "\n\n".join(text_pages)
                
                # Basic text cleaning
                cleaned_text = self._clean_extracted_text(full_text)
                
                return {
                    "status": "success",
                    "text": cleaned_text,
                    "page_count": total_pages
                }
                
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            return {
                "status": "error",
                "error": f"Failed to extract text from PDF: {str(e)}",
                "error_code": "PDF_CORRUPTED" if "corrupted" in str(e).lower() else "EXTRACTION_FAILED"
            }
    
    def _extract_text_from_txt(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            # Basic text cleaning
            cleaned_text = self._clean_extracted_text(text)
            
            return {
                "status": "success",
                "text": cleaned_text,
                "page_count": 1  # Text files are single "page"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to extract text from file: {str(e)}",
                "error_code": "EXTRACTION_FAILED"
            }
    
    def _clean_extracted_text(self, text: str) -> str:
        """Basic text cleaning for extracted text"""
        if not text:
            return ""
        
        import re
        
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newlines
        text = re.sub(r'\n\n+', '\n\n', text)
        
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remove empty lines at start and end
        text = text.strip()
        
        return text
    
    def _calculate_confidence(self, text: str, page_count: int, file_size: int) -> float:
        """Calculate confidence score for extracted text"""
        base_confidence = 0.9  # High confidence for pypdf extraction
        
        # Factors that affect confidence
        factors = []
        
        # Text length factor
        if len(text) > 1000:
            factors.append(0.95)
        elif len(text) > 100:
            factors.append(0.85)
        else:
            factors.append(0.6)
        
        # Page count factor
        if page_count > 5:
            factors.append(0.95)
        elif page_count > 1:
            factors.append(0.9)
        else:
            factors.append(0.8)
        
        # File size factor
        if file_size > 1024 * 1024:  # > 1MB
            factors.append(0.95)
        elif file_size > 100 * 1024:  # > 100KB
            factors.append(0.9)
        else:
            factors.append(0.8)
        
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
            # Check if pypdf is available
            import pypdf
            pypdf_available = True
        except ImportError:
            pypdf_available = False
        
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
        
        healthy = pypdf_available and services_healthy
        
        return ToolResult(
            tool_id=self.tool_id,
            status="success" if healthy else "error",
            data={
                "healthy": healthy,
                "pypdf_available": pypdf_available,
                "services_healthy": services_healthy,
                "supported_formats": [".pdf", ".txt"],
                "status": self.status.value
            },
            metadata={
                "timestamp": datetime.now().isoformat()
            },
            execution_time=0.0,
            memory_used=0
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