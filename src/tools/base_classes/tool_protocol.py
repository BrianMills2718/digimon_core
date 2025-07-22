"""Unified Tool Interface Protocol

This module defines the standardized interface that ALL tools must implement
to enable agent orchestration, contract validation, and consistent tool execution.

Part of the contract-first tool design mandated by ADR-001.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
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


@dataclass(frozen=True)
class ToolRequest:
    """Standardized tool input format
    
    This is the unified input contract that all tools must accept.
    Enables agent orchestration and consistent tool execution.
    """
    tool_id: str
    operation: str
    input_data: Any
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    validation_mode: bool = False


@dataclass(frozen=True)
class ToolResult:
    """Standardized tool output format
    
    This is the unified output contract that all tools must return.
    Enables consistent result processing and error handling.
    """
    tool_id: str
    status: str  # "success" or "error"
    data: Any
    metadata: Dict[str, Any]
    execution_time: float
    memory_used: int
    error_code: Optional[str] = None
    error_message: Optional[str] = None


@dataclass(frozen=True)
class ToolContract:
    """Tool capability and requirement specification
    
    Defines what the tool can do, what it needs, and how it should perform.
    Used for validation, documentation, and agent planning.
    """
    tool_id: str
    name: str
    description: str
    category: str  # "graph", "table", "vector", "cross_modal"
    input_schema: Dict[str, Any]  # JSON Schema for input validation
    output_schema: Dict[str, Any]  # JSON Schema for output validation
    dependencies: List[str]  # Required services/tools
    performance_requirements: Dict[str, Any]
    error_conditions: List[str]


class UnifiedTool(ABC):
    """Contract all tools MUST implement
    
    This abstract base class defines the interface that every tool must implement
    to participate in the unified tool ecosystem. No exceptions.
    
    Key principles:
    - Fail-fast: Invalid inputs cause immediate errors
    - Evidence-based: All operations tracked and measurable
    - No shortcuts: Complete implementation required
    """
    
    def __init__(self):
        """Initialize tool with required attributes"""
        self.tool_id: str = ""
        self.status: ToolStatus = ToolStatus.READY
        self._start_time: float = 0.0
        self._start_memory: int = 0
    
    @abstractmethod
    def get_contract(self) -> ToolContract:
        """Return tool contract specification
        
        This contract is used for:
        - Input/output validation
        - Performance monitoring
        - Error handling
        - Agent planning
        - Documentation generation
        
        Returns:
            Complete tool contract specification
        """
        pass
    
    @abstractmethod
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute tool operation with standardized input/output
        
        This is the primary execution method. All tools must implement this
        with proper error handling, validation, and performance tracking.
        
        Implementation requirements:
        - Validate input against contract
        - Track execution time and memory usage
        - Handle all error conditions gracefully
        - Return standardized ToolResult
        
        Args:
            request: Standardized tool request
            
        Returns:
            Standardized tool result with evidence
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """Validate input against tool contract
        
        Must validate input_data against the JSON schema defined
        in the tool contract. Fail-fast approach required.
        
        Args:
            input_data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    @abstractmethod
    def health_check(self) -> ToolResult:
        """Check tool health and readiness
        
        Must verify:
        - Tool dependencies are available
        - Required resources are accessible
        - Tool is ready for execution
        
        Returns:
            ToolResult indicating health status
        """
        pass
    
    @abstractmethod
    def get_status(self) -> ToolStatus:
        """Get current tool status
        
        Returns:
            Current operational status
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """Clean up tool resources
        
        Must properly clean up:
        - Database connections
        - File handles
        - Memory allocations
        - Temporary resources
        
        Returns:
            True if cleanup successful, False otherwise
        """
        pass
    
    # Helper methods for consistent implementation
    
    def _start_execution_tracking(self) -> None:
        """Start tracking execution metrics"""
        self.status = ToolStatus.PROCESSING
        self._start_time = time.time()
        self._start_memory = psutil.Process().memory_info().rss
    
    def _finish_execution_tracking(self) -> tuple[float, int]:
        """Finish tracking and return metrics"""
        execution_time = time.time() - self._start_time
        memory_used = psutil.Process().memory_info().rss - self._start_memory
        self.status = ToolStatus.READY
        return execution_time, memory_used
    
    def _create_success_result(self, data: Any, metadata: Dict[str, Any] = None) -> ToolResult:
        """Create standardized success result"""
        execution_time, memory_used = self._finish_execution_tracking()
        
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "timestamp": datetime.now().isoformat(),
            "tool_version": getattr(self, "version", "1.0.0")
        })
        
        return ToolResult(
            tool_id=self.tool_id,
            status="success",
            data=data,
            metadata=metadata,
            execution_time=execution_time,
            memory_used=memory_used
        )
    
    def _create_error_result(self, error_code: str, error_message: str, 
                           metadata: Dict[str, Any] = None) -> ToolResult:
        """Create standardized error result"""
        execution_time, memory_used = self._finish_execution_tracking()
        self.status = ToolStatus.ERROR
        
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "timestamp": datetime.now().isoformat(),
            "error_occurred_at": datetime.now().isoformat()
        })
        
        return ToolResult(
            tool_id=self.tool_id,
            status="error",
            data=None,
            metadata=metadata,
            execution_time=execution_time,
            memory_used=memory_used,
            error_code=error_code,
            error_message=error_message
        )


class ToolValidationError(Exception):
    """Raised when tool input validation fails"""
    pass


class ToolExecutionError(Exception):
    """Raised when tool execution fails"""
    pass


class ToolContractError(Exception):
    """Raised when tool contract is invalid"""
    pass