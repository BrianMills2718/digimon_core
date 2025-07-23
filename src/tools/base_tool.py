"""
Base Tool Infrastructure for Unified Tool Interface

Provides the contract-first design for all KGAS tools.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import time
import psutil
from datetime import datetime


class ToolStatus(Enum):
    """Tool operational status"""
    READY = "ready"
    PROCESSING = "processing"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class ToolErrorCode(Enum):
    """Standardized tool error codes for programmatic handling"""
    # Input/Validation Errors
    INVALID_INPUT = "INVALID_INPUT"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    
    # Processing Errors
    PARSE_ERROR = "PARSE_ERROR"
    XML_MALFORMED = "XML_MALFORMED"
    XML_PARSE_ERROR = "XML_PARSE_ERROR"
    YAML_SYNTAX_ERROR = "YAML_SYNTAX_ERROR"
    YAML_PARSE_ERROR = "YAML_PARSE_ERROR"
    EXCEL_CORRUPTED = "EXCEL_CORRUPTED"
    EXCEL_PASSWORD_PROTECTED = "EXCEL_PASSWORD_PROTECTED"
    POWERPOINT_CORRUPTED = "POWERPOINT_CORRUPTED"
    POWERPOINT_PASSWORD_PROTECTED = "POWERPOINT_PASSWORD_PROTECTED"
    SHEET_NOT_FOUND = "SHEET_NOT_FOUND"
    
    # Library/Dependency Errors
    LIBRARY_MISSING = "LIBRARY_MISSING"
    PPTX_LIBRARY_MISSING = "PPTX_LIBRARY_MISSING"
    UNSAFE_YAML_CONTENT = "UNSAFE_YAML_CONTENT"
    NAMESPACE_ERROR = "NAMESPACE_ERROR"
    
    # Archive/ZIP Errors
    ZIP_CORRUPTED = "ZIP_CORRUPTED"
    ZIP_PASSWORD_PROTECTED = "ZIP_PASSWORD_PROTECTED"
    ARCHIVE_EXTRACTION_FAILED = "ARCHIVE_EXTRACTION_FAILED"
    
    # Network/Web Errors
    CONNECTION_ERROR = "CONNECTION_ERROR"
    CONNECTION_TIMEOUT = "CONNECTION_TIMEOUT"
    HTTP_ERROR = "HTTP_ERROR"
    INVALID_URL = "INVALID_URL"
    
    # System Errors
    PROCESSING_ERROR = "PROCESSING_ERROR"
    MEMORY_LIMIT_EXCEEDED = "MEMORY_LIMIT_EXCEEDED"
    EXECUTION_TIMEOUT = "EXECUTION_TIMEOUT"
    HEALTH_CHECK_FAILED = "HEALTH_CHECK_FAILED"
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"


@dataclass(frozen=True)
class ToolRequest:
    """Standardized tool input format"""
    tool_id: str
    operation: str
    input_data: Any
    parameters: Dict[str, Any] = field(default_factory=dict)
    context: Optional[Dict[str, Any]] = field(default=None)
    validation_mode: bool = field(default=False)


@dataclass(frozen=True)
class ToolResult:
    """Standardized tool output format"""
    tool_id: str
    status: str  # "success" or "error"
    data: Any = field(default=None)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = field(default=0.0)
    memory_used: int = field(default=0)
    error_code: Optional[str] = field(default=None)
    error_message: Optional[str] = field(default=None)


@dataclass(frozen=True)
class ToolContract:
    """Tool capability and requirement specification"""
    tool_id: str
    name: str
    description: str
    category: str  # "document_processing", "graph", "table", "vector", "cross_modal"
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    performance_requirements: Dict[str, Any] = field(default_factory=dict)
    error_conditions: List[str] = field(default_factory=list)


class BaseTool(ABC):
    """Base class all tools MUST inherit from"""
    
    def __init__(self, services):
        """Initialize with service manager"""
        self.services = services
        self.tool_id = self.__class__.__name__  # Override in subclass
        self.status = ToolStatus.READY
        self._start_time = None
        self._start_memory = None
    
    @abstractmethod
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        pass
    
    @abstractmethod
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute tool operation with standardized input/output"""
        pass
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input against tool contract"""
        # Basic implementation - override for specific validation
        if input_data is None:
            return False
        
        contract = self.get_contract()
        required_fields = contract.input_schema.get("required", [])
        
        if isinstance(input_data, dict):
            for field in required_fields:
                if field not in input_data:
                    return False
        
        return True
    
    def health_check(self) -> ToolResult:
        """Check tool health and readiness"""
        try:
            # Basic health check - override for specific checks
            healthy = self.status in [ToolStatus.READY, ToolStatus.PROCESSING]
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success" if healthy else "error",
                data={
                    "healthy": healthy,
                    "status": self.status.value,
                    "contract": self.get_contract().name
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
    
    def get_status(self) -> ToolStatus:
        """Get current tool status"""
        return self.status
    
    def cleanup(self) -> bool:
        """Clean up tool resources"""
        # Basic cleanup - override for specific cleanup
        self.status = ToolStatus.READY
        return True
    
    def _start_execution(self):
        """Start execution tracking"""
        self._start_time = time.time()
        try:
            self._start_memory = psutil.Process().memory_info().rss
        except:
            self._start_memory = 0  # Fallback if psutil fails
        self.status = ToolStatus.PROCESSING
    
    def _end_execution(self) -> tuple:
        """End execution tracking and return metrics"""
        execution_time = time.time() - self._start_time if self._start_time else 0.0
        try:
            current_memory = psutil.Process().memory_info().rss
            memory_used = current_memory - self._start_memory if self._start_memory else 0
        except:
            memory_used = 0  # Fallback if psutil fails
        self.status = ToolStatus.READY
        return execution_time, memory_used
    
    def _create_error_result(self, request: ToolRequest, error_code: str, error_message: str) -> ToolResult:
        """Create standardized error result"""
        execution_time, memory_used = self._end_execution()
        self.status = ToolStatus.ERROR
        
        return ToolResult(
            tool_id=self.tool_id,
            status="error",
            data=None,
            metadata={
                "operation": request.operation,
                "timestamp": datetime.now().isoformat()
            },
            execution_time=execution_time,
            memory_used=memory_used,
            error_code=error_code,
            error_message=error_message
        )