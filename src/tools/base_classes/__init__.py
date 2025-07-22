"""Base classes for unified tool interface

This module provides the foundational classes for the unified tool interface:
- UnifiedTool: Abstract base class all tools must implement
- ToolRequest/ToolResult: Standardized input/output contracts
- ToolContract: Tool capability specification
- ToolContractValidator: Contract compliance validation
- ToolPerformanceMonitor: Performance tracking and requirements checking
"""

from .tool_protocol import (
    UnifiedTool,
    ToolStatus,
    ToolRequest,
    ToolResult,
    ToolContract,
    ToolValidationError,
    ToolExecutionError,
    ToolContractError
)

from .tool_validator import ToolContractValidator

from .tool_performance_monitor import (
    ToolPerformanceMonitor,
    ToolPerformanceMetrics,
    PerformanceContext
)

__all__ = [
    # Core protocol
    "UnifiedTool",
    "ToolStatus",
    "ToolRequest",
    "ToolResult",
    "ToolContract",
    
    # Exceptions
    "ToolValidationError",
    "ToolExecutionError",
    "ToolContractError",
    
    # Validation
    "ToolContractValidator",
    
    # Performance monitoring
    "ToolPerformanceMonitor",
    "ToolPerformanceMetrics",
    "PerformanceContext"
]