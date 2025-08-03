"""
Fixed Base Tool Infrastructure - Allows Standalone Initialization

This version allows tools to work without service_manager dependency.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import time
import psutil
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


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
    EXTRACTION_FAILED = "EXTRACTION_FAILED"
    
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


# MockService removed - we'll use real services from ServiceManager


class BaseTool(ABC):
    """Base class all tools MUST inherit from - Uses real services via ServiceManager"""
    
    def __init__(self, service_manager=None):
        """
        Initialize with service manager
        If no service_manager provided, creates one automatically
        """
        # Get service manager - create if not provided
        if service_manager:
            self.service_manager = service_manager
        else:
            # Import here to avoid circular imports
            from src.core.service_manager import get_service_manager
            self.service_manager = get_service_manager()
            logger.info(f"Created ServiceManager automatically for {self.__class__.__name__}")
        
        # Set up real services from service_manager
        try:
            self.identity_service = self.service_manager.identity_service
            self.provenance_service = self.service_manager.provenance_service
            self.quality_service = self.service_manager.quality_service
            logger.info(f"Initialized {self.__class__.__name__} with real services")
            self.is_standalone = False
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            # Re-raise the error - no fallback to mocks
            raise RuntimeError(f"Failed to initialize real services: {e}")
        
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
                    logger.error(f"Missing required field: {field}")
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
                    "contract": self.get_contract().name,
                    "standalone_mode": getattr(self, 'is_standalone', False)
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
    
    def _create_error_result(self, error_code: str, error_message: str) -> ToolResult:
        """Create standardized error result"""
        execution_time, memory_used = self._end_execution()
        
        return ToolResult(
            tool_id=self.tool_id,
            status="error",
            data=None,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "error_details": error_message
            },
            execution_time=execution_time,
            memory_used=memory_used,
            error_code=error_code,
            error_message=error_message
        )
    
    def _create_success_result(self, data: Any, metadata: Dict[str, Any] = None) -> ToolResult:
        """Create standardized success result"""
        execution_time, memory_used = self._end_execution()
        
        return ToolResult(
            tool_id=self.tool_id,
            status="success",
            data=data,
            metadata=metadata or {"timestamp": datetime.now().isoformat()},
            execution_time=execution_time,
            memory_used=memory_used
        )