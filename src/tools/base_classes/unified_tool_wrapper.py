"""Unified Tool Wrapper for Legacy Tool Migration

This wrapper helps migrate existing tools to the unified interface
without requiring a complete rewrite. It provides default implementations
and adapters for the UnifiedTool interface.
"""

import time
import psutil
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import jsonschema

from .tool_protocol import (
    UnifiedTool, ToolStatus, ToolRequest, ToolResult, 
    ToolContract, ToolValidationError, ToolExecutionError
)

logger = logging.getLogger(__name__)


class UnifiedToolWrapper(UnifiedTool):
    """Wrapper to adapt legacy tools to the unified interface
    
    This wrapper provides:
    - Default implementations for all UnifiedTool methods
    - Adaptation of legacy execute() methods
    - Automatic contract generation from tool info
    - Built-in performance tracking
    - Input validation based on contract
    """
    
    def __init__(self, legacy_tool: Any):
        """Initialize wrapper with legacy tool instance
        
        Args:
            legacy_tool: Existing tool instance to wrap
        """
        super().__init__()
        self.legacy_tool = legacy_tool
        self.tool_id = getattr(legacy_tool, 'tool_id', self._infer_tool_id())
        self.status = ToolStatus.READY
        self._contract = None
        self._performance_monitor = None
        
        # Cache tool info if available
        self._tool_info = None
        if hasattr(legacy_tool, 'get_tool_info'):
            try:
                self._tool_info = legacy_tool.get_tool_info()
            except Exception as e:
                logger.warning(f"Failed to get tool info: {e}")
    
    def get_contract(self) -> ToolContract:
        """Generate contract from legacy tool information"""
        if self._contract is None:
            self._contract = self._generate_contract()
        return self._contract
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute tool with unified interface"""
        self._start_execution_tracking()
        
        try:
            # Validate input
            if not self.validate_input(request.input_data):
                return self._create_error_result(
                    "INVALID_INPUT",
                    "Input validation failed against tool contract"
                )
            
            # Adapt to legacy execute method
            if hasattr(self.legacy_tool, 'execute'):
                # Try different legacy execute signatures
                result = self._execute_legacy_tool(request)
            else:
                # Fallback to other common method names
                result = self._execute_alternative_methods(request)
            
            # Convert legacy result to ToolResult
            return self._convert_to_tool_result(result, request)
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}", exc_info=True)
            return self._create_error_result(
                "EXECUTION_ERROR",
                f"Tool execution failed: {str(e)}"
            )
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input against tool contract"""
        try:
            contract = self.get_contract()
            jsonschema.validate(input_data, contract.input_schema)
            
            # Also use legacy validation if available
            if hasattr(self.legacy_tool, 'validate_input'):
                return self.legacy_tool.validate_input(input_data)
            
            return True
            
        except jsonschema.ValidationError as e:
            logger.error(f"Input validation failed: {e}")
            return False
        except Exception as e:
            logger.warning(f"Validation error: {e}")
            # Be permissive if validation fails
            return True
    
    def health_check(self) -> ToolResult:
        """Check tool health and readiness"""
        try:
            # Check if legacy tool has health check
            if hasattr(self.legacy_tool, 'health_check'):
                legacy_result = self.legacy_tool.health_check()
                return self._convert_to_tool_result(legacy_result, None)
            
            # Default health check
            healthy = True
            health_data = {
                "healthy": healthy,
                "tool_id": self.tool_id,
                "status": self.status.value,
                "has_execute": hasattr(self.legacy_tool, 'execute'),
                "wrapped_tool": self.legacy_tool.__class__.__name__
            }
            
            # Check service dependencies if available
            if hasattr(self.legacy_tool, 'service_manager'):
                try:
                    services_healthy = all(
                        getattr(self.legacy_tool, svc, None) is not None
                        for svc in ['identity_service', 'provenance_service', 'quality_service']
                        if hasattr(self.legacy_tool, svc)
                    )
                    health_data["services_healthy"] = services_healthy
                    healthy = healthy and services_healthy
                except Exception:
                    health_data["services_healthy"] = False
                    healthy = False
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success" if healthy else "error",
                data=health_data,
                metadata={"timestamp": datetime.now().isoformat()},
                execution_time=0.0,
                memory_used=0
            )
            
        except Exception as e:
            return self._create_error_result(
                "HEALTH_CHECK_FAILED",
                f"Health check failed: {str(e)}"
            )
    
    def get_status(self) -> ToolStatus:
        """Get current tool status"""
        return self.status
    
    def cleanup(self) -> bool:
        """Clean up tool resources"""
        try:
            # Call legacy cleanup if available
            if hasattr(self.legacy_tool, 'cleanup'):
                return self.legacy_tool.cleanup()
            
            # Default cleanup
            if hasattr(self.legacy_tool, 'driver'):
                # Close Neo4j driver if present
                try:
                    self.legacy_tool.driver.close()
                except Exception:
                    pass
            
            return True
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False
    
    def _generate_contract(self) -> ToolContract:
        """Generate contract from legacy tool information"""
        # Use cached tool info or get it
        tool_info = self._tool_info or {}
        
        # Infer tool properties
        tool_id = self.tool_id
        name = tool_info.get('name', tool_id.replace('_', ' ').title())
        description = tool_info.get('description', f"Legacy tool {tool_id}")
        
        # Determine category from tool ID or info
        category = self._infer_category(tool_id, tool_info)
        
        # Generate schemas based on tool type
        input_schema = self._generate_input_schema(tool_id, tool_info)
        output_schema = self._generate_output_schema(tool_id, tool_info)
        
        # Infer dependencies
        dependencies = self._infer_dependencies()
        
        # Default performance requirements
        performance_requirements = {
            "max_execution_time": 60.0,
            "max_memory_mb": 1000,
            "min_accuracy": 0.8
        }
        
        # Common error conditions
        error_conditions = [
            "INVALID_INPUT",
            "EXECUTION_ERROR",
            "SERVICE_UNAVAILABLE",
            "RESOURCE_LIMIT_EXCEEDED"
        ]
        
        return ToolContract(
            tool_id=tool_id,
            name=name,
            description=description,
            category=category,
            input_schema=input_schema,
            output_schema=output_schema,
            dependencies=dependencies,
            performance_requirements=performance_requirements,
            error_conditions=error_conditions
        )
    
    def _infer_tool_id(self) -> str:
        """Infer tool ID from class name"""
        class_name = self.legacy_tool.__class__.__name__
        # Convert CamelCase to UPPER_SNAKE_CASE
        import re
        words = re.findall(r'[A-Z][a-z]*', class_name)
        return '_'.join(words).upper()
    
    def _infer_category(self, tool_id: str, tool_info: Dict[str, Any]) -> str:
        """Infer tool category from ID and info"""
        # Check tool info first
        if 'category' in tool_info:
            return tool_info['category']
        
        # Infer from tool ID ranges
        try:
            tool_num = int(''.join(filter(str.isdigit, tool_id)))
            if 1 <= tool_num <= 30:
                return "graph"
            elif 31 <= tool_num <= 60:
                return "table"
            elif 61 <= tool_num <= 90:
                return "vector"
            elif 91 <= tool_num <= 121:
                return "cross_modal"
        except ValueError:
            pass
        
        # Default based on keywords
        tool_id_lower = tool_id.lower()
        if any(kw in tool_id_lower for kw in ['graph', 'node', 'edge', 'pagerank']):
            return "graph"
        elif any(kw in tool_id_lower for kw in ['table', 'csv', 'dataframe']):
            return "table"
        elif any(kw in tool_id_lower for kw in ['vector', 'embedding', 'similarity']):
            return "vector"
        else:
            return "graph"  # Default
    
    def _generate_input_schema(self, tool_id: str, tool_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate input schema based on tool type"""
        # Tool-specific schemas
        tool_schemas = {
            "T01_PDF_LOADER": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "workflow_id": {"type": "string"}
                },
                "required": ["file_path"]
            },
            "T15A_TEXT_CHUNKER": {
                "type": "object",
                "properties": {
                    "document_ref": {"type": "string"},
                    "text": {"type": "string"},
                    "confidence": {"type": "number"}
                },
                "required": ["document_ref", "text"]
            },
            "T23A_SPACY_NER": {
                "type": "object",
                "properties": {
                    "chunk_ref": {"type": "string"},
                    "text": {"type": "string"},
                    "confidence": {"type": "number"}
                },
                "required": ["chunk_ref", "text"]
            },
            "T27_RELATIONSHIP_EXTRACTOR": {
                "type": "object",
                "properties": {
                    "chunk_ref": {"type": "string"},
                    "text": {"type": "string"},
                    "entities": {"type": "array"},
                    "confidence": {"type": "number"}
                },
                "required": ["chunk_ref", "text", "entities"]
            },
            "T31_ENTITY_BUILDER": {
                "type": "object",
                "properties": {
                    "mentions": {"type": "array"},
                    "mention_refs": {"type": "array"}
                },
                "required": ["mentions"]
            },
            "T34_EDGE_BUILDER": {
                "type": "object",
                "properties": {
                    "relationships": {"type": "array"},
                    "relationship_refs": {"type": "array"}
                },
                "required": ["relationships"]
            },
            "T68_PAGERANK": {
                "type": "object",
                "properties": {
                    "graph_ref": {"type": "string"}
                },
                "required": ["graph_ref"]
            },
            "T49_MULTIHOP_QUERY": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_hops": {"type": "integer"},
                    "graph_ref": {"type": "string"}
                },
                "required": ["query"]
            }
        }
        
        # Return specific schema or generic
        return tool_schemas.get(tool_id, {
            "type": "object",
            "properties": {
                "input_data": {"type": ["object", "array", "string"]}
            }
        })
    
    def _generate_output_schema(self, tool_id: str, tool_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate output schema based on tool type"""
        # Generic successful output schema
        return {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["success", "error"]},
                "results": {"type": ["array", "object"]},
                "operation_id": {"type": "string"},
                "metadata": {"type": "object"}
            },
            "required": ["status"]
        }
    
    def _infer_dependencies(self) -> list:
        """Infer tool dependencies"""
        dependencies = []
        
        # Check for service dependencies
        if hasattr(self.legacy_tool, 'identity_service'):
            dependencies.append("identity_service")
        if hasattr(self.legacy_tool, 'provenance_service'):
            dependencies.append("provenance_service")
        if hasattr(self.legacy_tool, 'quality_service'):
            dependencies.append("quality_service")
        
        # Check for Neo4j dependency
        if hasattr(self.legacy_tool, 'driver'):
            dependencies.append("neo4j")
        
        return dependencies
    
    def _execute_legacy_tool(self, request: ToolRequest) -> Dict[str, Any]:
        """Execute legacy tool with various signatures"""
        execute_method = getattr(self.legacy_tool, 'execute')
        
        # Try different parameter combinations
        try:
            # Try with full request
            return execute_method(request.input_data, {'validation_mode': request.validation_mode})
        except TypeError:
            try:
                # Try with just input data
                return execute_method(request.input_data)
            except TypeError:
                try:
                    # Try with no parameters (validation mode)
                    return execute_method()
                except TypeError:
                    # Try with individual parameters
                    if isinstance(request.input_data, dict):
                        return execute_method(**request.input_data)
                    else:
                        raise ToolExecutionError(f"Unable to call execute method with provided input")
    
    def _execute_alternative_methods(self, request: ToolRequest) -> Dict[str, Any]:
        """Try alternative method names for execution"""
        # Map of common method patterns
        method_mappings = {
            "T01_PDF_LOADER": ("load_pdf", ["file_path", "workflow_id"]),
            "T15A_TEXT_CHUNKER": ("chunk_text", ["document_ref", "text", "confidence"]),
            "T23A_SPACY_NER": ("extract_entities", ["chunk_ref", "text", "confidence"]),
            "T27_RELATIONSHIP_EXTRACTOR": ("extract_relationships", ["chunk_ref", "text", "entities", "confidence"]),
            "T31_ENTITY_BUILDER": ("build_entities", ["mentions", "source_refs"]),
            "T34_EDGE_BUILDER": ("build_edges", ["relationships", "source_refs"]),
            "T68_PAGERANK": ("calculate_pagerank", ["graph_ref"]),
            "T49_MULTIHOP_QUERY": ("query_graph", ["query", "max_hops", "graph_ref"])
        }
        
        if self.tool_id in method_mappings:
            method_name, param_names = method_mappings[self.tool_id]
            if hasattr(self.legacy_tool, method_name):
                method = getattr(self.legacy_tool, method_name)
                
                # Extract parameters from input
                if isinstance(request.input_data, dict):
                    params = [request.input_data.get(p) for p in param_names if p in request.input_data]
                    return method(*params)
        
        raise ToolExecutionError(f"No suitable execution method found for {self.tool_id}")
    
    def _convert_to_tool_result(self, legacy_result: Any, request: Optional[ToolRequest]) -> ToolResult:
        """Convert legacy result format to ToolResult"""
        execution_time, memory_used = self._finish_execution_tracking()
        
        # Handle different legacy result formats
        if isinstance(legacy_result, dict):
            status = legacy_result.get("status", "success")
            
            # Extract data based on common patterns
            data = None
            if "results" in legacy_result:
                data = legacy_result["results"]
            elif "data" in legacy_result:
                data = legacy_result["data"]
            elif status == "success":
                # Use entire result as data, excluding metadata fields
                data = {k: v for k, v in legacy_result.items() 
                       if k not in ["status", "operation_id", "provenance", "metadata"]}
            
            # Extract metadata
            metadata = legacy_result.get("metadata", {})
            metadata.update({
                "tool_version": getattr(self.legacy_tool, 'version', '1.0.0'),
                "wrapped_tool": self.legacy_tool.__class__.__name__,
                "timestamp": datetime.now().isoformat()
            })
            
            # Add operation_id if present
            if "operation_id" in legacy_result:
                metadata["operation_id"] = legacy_result["operation_id"]
            
            return ToolResult(
                tool_id=self.tool_id,
                status=status,
                data=data,
                metadata=metadata,
                execution_time=execution_time,
                memory_used=memory_used,
                error_code=legacy_result.get("error_code"),
                error_message=legacy_result.get("error", legacy_result.get("error_message"))
            )
        else:
            # Wrap non-dict results
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data=legacy_result,
                metadata={
                    "wrapped_result": True,
                    "timestamp": datetime.now().isoformat()
                },
                execution_time=execution_time,
                memory_used=memory_used
            )


def wrap_legacy_tool(legacy_tool: Any) -> UnifiedTool:
    """Convenience function to wrap a legacy tool
    
    Args:
        legacy_tool: Legacy tool instance to wrap
        
    Returns:
        UnifiedTool-compliant wrapper
    """
    return UnifiedToolWrapper(legacy_tool)