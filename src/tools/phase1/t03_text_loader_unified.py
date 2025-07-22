"""
T03: Text Document Loader - Unified Interface Implementation

Loads plain text documents with encoding detection and normalization.
"""

from typing import Dict, Any, Optional, List
import os
from pathlib import Path
import uuid
from datetime import datetime
import logging
import chardet

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class T03TextLoaderUnified(BaseTool):
    """T03: Text Document Loader with unified interface"""
    
    def __init__(self, service_manager: ServiceManager):
        """Initialize with service manager"""
        super().__init__(service_manager)
        self.tool_id = "T03"
        self.identity_service = service_manager.identity_service
        self.provenance_service = service_manager.provenance_service
        self.quality_service = service_manager.quality_service
        self._temp_files = []
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="Text Document Loader",
            description="Load plain text documents with encoding detection",
            category="document_processing",
            input_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to text file to load"
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
                            "encoding": {"type": "string"},
                            "encoding_confidence": {"type": "number"},
                            "line_count": {"type": "integer"},
                            "has_unicode": {"type": "boolean"},
                            "confidence": {"type": "number"},
                            "quality_tier": {"type": "string"},
                            "created_at": {"type": "string"}
                        },
                        "required": ["document_id", "text", "encoding", "confidence", "line_count"]
                    }
                },
                "required": ["document"]
            },
            dependencies=["identity_service", "provenance_service", "quality_service"],
            performance_requirements={
                "max_execution_time": 5.0,  # 5 seconds for text files
                "max_memory_mb": 512,       # 512MB for text processing
                "min_confidence": 0.8       # Minimum confidence threshold
            },
            error_conditions=[
                "FILE_NOT_FOUND",
                "INVALID_FILE_TYPE",
                "ENCODING_ERROR",
                "DECODING_FAILED",
                "PERMISSION_DENIED",
                "FILE_ACCESS_ERROR",
                "MEMORY_LIMIT_EXCEEDED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute text loading with unified interface"""
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
            
            # Load text with encoding detection
            load_result = self._load_text_file(file_path, request.parameters)
            
            if load_result["status"] != "success":
                return self._create_error_result(
                    request,
                    load_result.get("error_code", "EXTRACTION_FAILED"),
                    load_result["error"]
                )
            
            text = load_result["text"]
            encoding = load_result["encoding"]
            encoding_confidence = load_result.get("encoding_confidence", 1.0)
            
            # Normalize line endings if requested
            if request.parameters.get("normalize_line_endings", False):
                text = self._normalize_line_endings(text)
            
            # Analyze text
            line_count = len(text.splitlines()) if text else 0
            has_unicode = self._has_unicode(text)
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                text=text,
                line_count=line_count,
                encoding_confidence=encoding_confidence,
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
                "encoding": encoding,
                "encoding_confidence": encoding_confidence,
                "line_count": line_count,
                "has_unicode": has_unicode,
                "confidence": confidence,
                "created_at": datetime.now().isoformat(),
                "tool_version": "1.0.0"
            }
            
            # Assess quality
            quality_result = self.quality_service.assess_confidence(
                object_ref=document_ref,
                base_confidence=confidence,
                factors={
                    "text_length": min(1.0, len(text) / 10000),
                    "encoding_confidence": encoding_confidence,
                    "line_count": min(1.0, line_count / 1000),
                    "file_size": min(1.0, file_path.stat().st_size / (1024 * 1024))
                },
                metadata={
                    "file_type": file_path.suffix.lower(),
                    "encoding": encoding,
                    "has_unicode": has_unicode
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
                    "line_count": line_count,
                    "encoding": encoding,
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
                    "encoding_method": "chardet" if request.parameters.get("detect_encoding") else "default"
                },
                execution_time=execution_time,
                memory_used=memory_used
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in {self.tool_id}: {e}", exc_info=True)
            return self._create_error_result(
                request,
                "UNEXPECTED_ERROR",
                f"Unexpected error during text loading: {str(e)}"
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
            allowed_extensions = ['.txt', '.text', '.log', '.md', '.markdown', '.rst', '.csv', '.tsv']
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
    
    def _load_text_file(self, file_path: Path, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Load text file with encoding detection"""
        try:
            # Try to detect encoding if requested
            if parameters.get("detect_encoding", False):
                return self._load_with_encoding_detection(file_path)
            else:
                # Default to UTF-8
                return self._load_with_encoding(file_path, "utf-8")
                
        except PermissionError as e:
            logger.error(f"Permission denied: {str(e)}")
            return {
                "status": "error",
                "error": f"Permission denied: {str(e)}",
                "error_code": "PERMISSION_DENIED"
            }
        except Exception as e:
            logger.error(f"Failed to load text file: {str(e)}")
            return {
                "status": "error",
                "error": f"Failed to load text file: {str(e)}",
                "error_code": "FILE_ACCESS_ERROR"
            }
    
    def _load_with_encoding(self, file_path: Path, encoding: str) -> Dict[str, Any]:
        """Load file with specific encoding"""
        try:
            # Try text mode first
            with open(file_path, 'r', encoding=encoding) as f:
                text = f.read()
            
            return {
                "status": "success",
                "text": text,
                "encoding": encoding,
                "encoding_confidence": 1.0
            }
        except UnicodeDecodeError as e:
            logger.error(f"Decoding error with {encoding}: {str(e)}")
            return {
                "status": "error",
                "error": f"Failed to decode file with {encoding}: {str(e)}",
                "error_code": "DECODING_FAILED"
            }
        except Exception as e:
            # Handle cases where mock_open returns bytes instead of text
            if "decode" in str(e):
                return {
                    "status": "error",
                    "error": f"Failed to decode file: {str(e)}",
                    "error_code": "DECODING_FAILED"
                }
            raise
    
    def _load_with_encoding_detection(self, file_path: Path) -> Dict[str, Any]:
        """Load file with automatic encoding detection"""
        try:
            # Read raw bytes for detection
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            
            # Detect encoding
            detection = chardet.detect(raw_data)
            encoding = detection['encoding']
            confidence = detection['confidence']
            
            if not encoding:
                # Fallback to UTF-8
                encoding = 'utf-8'
                confidence = 0.5
            
            # Decode with detected encoding
            try:
                text = raw_data.decode(encoding)
                return {
                    "status": "success",
                    "text": text,
                    "encoding": encoding,
                    "encoding_confidence": confidence
                }
            except UnicodeDecodeError:
                # Try UTF-8 as fallback
                try:
                    text = raw_data.decode('utf-8', errors='replace')
                    return {
                        "status": "success",
                        "text": text,
                        "encoding": "utf-8",
                        "encoding_confidence": 0.3
                    }
                except Exception as e:
                    return {
                        "status": "error",
                        "error": f"Failed to decode file: {str(e)}",
                        "error_code": "ENCODING_ERROR"
                    }
                    
        except Exception as e:
            logger.error(f"Encoding detection failed: {str(e)}")
            return {
                "status": "error",
                "error": f"Encoding detection failed: {str(e)}",
                "error_code": "ENCODING_ERROR"
            }
    
    def _normalize_line_endings(self, text: str) -> str:
        """Normalize different line endings to consistent format"""
        # Convert all line endings to \n
        text = text.replace('\r\n', '\n')  # Windows
        text = text.replace('\r', '\n')    # Old Mac
        return text
    
    def _has_unicode(self, text: str) -> bool:
        """Check if text contains unicode characters beyond ASCII"""
        try:
            text.encode('ascii')
            return False
        except UnicodeEncodeError:
            return True
    
    def _calculate_confidence(self, text: str, line_count: int, 
                            encoding_confidence: float, file_size: int) -> float:
        """Calculate confidence score for loaded text"""
        # Base confidence for successfully loaded text
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
        
        # Encoding confidence factor
        factors.append(encoding_confidence)
        
        # File size factor
        if file_size > 1024:  # > 1KB
            factors.append(0.95)
        elif file_size > 0:
            factors.append(0.85)
        else:
            factors.append(0.40)
        
        # Line count factor
        if line_count > 10:
            factors.append(0.95)
        elif line_count > 1:
            factors.append(0.90)
        elif line_count == 1:
            factors.append(0.85)
        else:
            factors.append(0.50)
        
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
            # Check if chardet is available
            try:
                import chardet
                chardet_available = True
                chardet_version = chardet.__version__ if hasattr(chardet, '__version__') else "unknown"
            except ImportError:
                chardet_available = False
                chardet_version = None
            
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
            
            healthy = services_healthy  # chardet is optional
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success" if healthy else "error",
                data={
                    "healthy": healthy,
                    "chardet_available": chardet_available,
                    "chardet_version": chardet_version,
                    "services_healthy": services_healthy,
                    "supported_formats": [".txt", ".text", ".log", ".md", ".markdown", ".rst", ".csv", ".tsv"],
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