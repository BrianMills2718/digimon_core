"""
Base Tool Class for Unified KGAS System

All tools MUST inherit from this and use UnifiedData.
No exceptions. No custom data formats.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time
import logging
from enum import Enum

from unified_data_contract import UnifiedData, ToolCategory, DataCategory

logger = logging.getLogger(__name__)


@dataclass
class ToolMetadata:
    """Metadata about a tool"""
    tool_id: str
    name: str
    description: str
    category: ToolCategory
    input_types: List[DataCategory]  # What data types this tool reads
    output_types: List[DataCategory]  # What data types this tool produces
    version: str = "1.0.0"


class ToolStatus(Enum):
    """Tool execution status"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"  # Some data processed successfully


@dataclass
class ToolResult:
    """Result from tool execution"""
    status: ToolStatus
    data: UnifiedData  # ALWAYS UnifiedData, no exceptions
    execution_time: float
    message: Optional[str] = None
    error: Optional[str] = None


class UnifiedTool(ABC):
    """
    Base class for ALL tools in the system.
    Enforces unified data contract.
    """
    
    def __init__(self, metadata: ToolMetadata):
        self.metadata = metadata
        self.logger = logging.getLogger(f"Tool.{metadata.tool_id}")
    
    @abstractmethod
    def process(self, data: UnifiedData) -> UnifiedData:
        """
        Process the unified data.
        Tools read what they need and add their outputs.
        
        Args:
            data: UnifiedData containing all information
            
        Returns:
            The SAME UnifiedData object with additions
        """
        pass
    
    def execute(self, data: UnifiedData) -> ToolResult:
        """
        Execute the tool with timing and error handling.
        
        Args:
            data: UnifiedData to process
            
        Returns:
            ToolResult with status and processed data
        """
        start_time = time.time()
        
        try:
            # Validate input data has what we need
            validation_error = self._validate_input(data)
            if validation_error:
                return ToolResult(
                    status=ToolStatus.FAILED,
                    data=data,
                    execution_time=time.time() - start_time,
                    error=validation_error
                )
            
            # Process the data
            self.logger.info(f"Processing with {self.metadata.tool_id}")
            processed_data = self.process(data)
            
            # Track that this tool processed the data
            processed_data.add_processing_step(self.metadata.tool_id)
            
            execution_time = time.time() - start_time
            self.logger.info(f"Completed in {execution_time:.2f}s")
            
            return ToolResult(
                status=ToolStatus.SUCCESS,
                data=processed_data,
                execution_time=execution_time,
                message=f"Processed successfully by {self.metadata.tool_id}"
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Failed with error: {e}")
            
            return ToolResult(
                status=ToolStatus.FAILED,
                data=data,
                execution_time=execution_time,
                error=str(e)
            )
    
    def _validate_input(self, data: UnifiedData) -> Optional[str]:
        """
        Validate that input data has required types.
        
        Returns:
            Error message if validation fails, None if valid
        """
        for required_type in self.metadata.input_types:
            if required_type == DataCategory.TEXT and not data.text:
                return f"Tool {self.metadata.tool_id} requires text input"
            elif required_type == DataCategory.ENTITIES and not data.entities:
                return f"Tool {self.metadata.tool_id} requires entities"
            elif required_type == DataCategory.RELATIONSHIPS and not data.relationships:
                return f"Tool {self.metadata.tool_id} requires relationships"
            elif required_type == DataCategory.GRAPH and not data.graph_data:
                return f"Tool {self.metadata.tool_id} requires graph data"
            elif required_type == DataCategory.TABLE and not data.table_data:
                return f"Tool {self.metadata.tool_id} requires table data"
            elif required_type == DataCategory.VECTOR and not data.vector_data:
                return f"Tool {self.metadata.tool_id} requires vector data"
        
        return None
    
    def can_process(self, data: UnifiedData) -> bool:
        """Check if this tool can process the given data"""
        return self._validate_input(data) is None
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool information"""
        return {
            "tool_id": self.metadata.tool_id,
            "name": self.metadata.name,
            "description": self.metadata.description,
            "category": self.metadata.category.value,
            "input_types": [t.value for t in self.metadata.input_types],
            "output_types": [t.value for t in self.metadata.output_types],
            "version": self.metadata.version
        }