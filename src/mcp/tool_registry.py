"""
MCP Tool Registry - Registers all KGAS tools for MCP access
"""
import importlib
import inspect
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
import logging

from ..core.base_tool import BaseTool, ToolRequest, ToolResult

logger = logging.getLogger(__name__)

@dataclass
class ToolRegistration:
    """Information about a registered tool"""
    tool_id: str
    module_path: str
    class_name: str
    tool_instance: Optional[BaseTool] = None
    description: str = ""
    input_schema: Dict[str, Any] = None
    output_schema: Dict[str, Any] = None

class MCPToolRegistry:
    """Registers all KGAS tools for MCP access"""
    
    def __init__(self, service_manager=None):
        self.tools: Dict[str, ToolRegistration] = {}
        self.service_manager = service_manager
        self._register_all_tools()
    
    def _register_all_tools(self):
        """Register all 8 vertical slice tools"""
        tools_to_register = [
            ("T01_PDF_LOADER", "src.tools.phase1.t01_pdf_loader_unified", "T01PDFLoaderUnified"),
            ("T15A_TEXT_CHUNKER", "src.tools.phase1.t15a_text_chunker_unified", "T15ATextChunkerUnified"),
            ("T23A_SPACY_NER", "src.tools.phase1.t23a_spacy_ner_unified", "T23ASpacyNERUnified"),
            ("T27_RELATIONSHIP_EXTRACTOR", "src.tools.phase1.t27_relationship_extractor_unified", "T27RelationshipExtractorUnified"),
            ("T31_ENTITY_BUILDER", "src.tools.phase1.t31_entity_builder_unified", "T31EntityBuilderUnified"),
            ("T34_EDGE_BUILDER", "src.tools.phase1.t34_edge_builder_unified", "T34EdgeBuilderUnified"),
            ("T68_PAGE_RANK", "src.tools.phase1.t68_pagerank_unified", "T68PageRankCalculatorUnified"),
            ("T49_MULTI_HOP_QUERY", "src.tools.phase1.t49_multihop_query_unified", "T49MultiHopQueryUnified")
        ]
        
        for tool_id, module_path, class_name in tools_to_register:
            try:
                self.register_tool(tool_id, module_path, class_name)
                logger.info(f"Successfully registered tool: {tool_id}")
            except Exception as e:
                logger.error(f"Failed to register tool {tool_id}: {e}")
    
    def register_tool(self, tool_id: str, module_path: str, class_name: str):
        """Register individual tool for MCP access"""
        try:
            # Dynamic import of the tool module
            module = importlib.import_module(module_path)
            tool_class = getattr(module, class_name)
            
            # Validate it's a proper tool class
            if not issubclass(tool_class, BaseTool):
                raise ValueError(f"Tool class {class_name} is not a subclass of BaseTool")
            
            # Create tool instance if service manager available
            tool_instance = None
            if self.service_manager:
                try:
                    tool_instance = tool_class(self.service_manager)
                except Exception as e:
                    logger.warning(f"Could not instantiate {tool_id}: {e}. Will instantiate on demand.")
            
            # Extract tool metadata
            description = self._extract_tool_description(tool_class)
            input_schema = self._extract_input_schema(tool_class)
            output_schema = self._extract_output_schema(tool_class)
            
            # Register the tool
            registration = ToolRegistration(
                tool_id=tool_id,
                module_path=module_path,
                class_name=class_name,
                tool_instance=tool_instance,
                description=description,
                input_schema=input_schema,
                output_schema=output_schema
            )
            
            self.tools[tool_id] = registration
            
        except Exception as e:
            logger.error(f"Failed to register tool {tool_id}: {e}")
            raise
    
    def _extract_tool_description(self, tool_class) -> str:
        """Extract tool description from class docstring or attributes"""
        if hasattr(tool_class, '__doc__') and tool_class.__doc__:
            return tool_class.__doc__.strip().split('\n')[0]
        elif hasattr(tool_class, 'description'):
            return tool_class.description
        else:
            return f"KGAS Tool: {tool_class.__name__}"
    
    def _extract_input_schema(self, tool_class) -> Dict[str, Any]:
        """Extract input schema from tool class"""
        # Try to get execute method signature
        try:
            execute_method = getattr(tool_class, 'execute')
            sig = inspect.signature(execute_method)
            
            # Look for ToolRequest parameter
            for param in sig.parameters.values():
                if param.annotation == ToolRequest:
                    return {
                        "type": "object",
                        "properties": {
                            "input_data": {
                                "type": "object",
                                "description": "Input data for the tool"
                            },
                            "parameters": {
                                "type": "object", 
                                "description": "Tool parameters"
                            }
                        },
                        "required": ["input_data"]
                    }
        except Exception as e:
            logger.debug(f"Could not extract input schema: {e}")
        
        # Default schema
        return {
            "type": "object",
            "properties": {
                "input_data": {"type": "object"},
                "parameters": {"type": "object"}
            }
        }
    
    def _extract_output_schema(self, tool_class) -> Dict[str, Any]:
        """Extract output schema from tool class"""
        return {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "result": {"type": "object"},
                "error": {"type": "string"},
                "metadata": {"type": "object"}
            }
        }
    
    def get_tool_manifest(self) -> Dict[str, Any]:
        """Return MCP-compatible tool manifest"""
        tools_manifest = []
        
        for tool_id, registration in self.tools.items():
            tool_manifest = {
                "name": tool_id,
                "description": registration.description,
                "inputSchema": registration.input_schema,
                "outputSchema": registration.output_schema
            }
            tools_manifest.append(tool_manifest)
        
        return {
            "tools": tools_manifest,
            "version": "1.0.0",
            "protocol_version": "1.0.0"
        }
    
    def get_tool(self, tool_id: str) -> Optional[ToolRegistration]:
        """Get tool registration by ID"""
        return self.tools.get(tool_id)
    
    def list_tools(self) -> List[str]:
        """List all registered tool IDs"""
        return list(self.tools.keys())
    
    def get_tool_instance(self, tool_id: str) -> Optional[BaseTool]:
        """Get instantiated tool by ID"""
        registration = self.tools.get(tool_id)
        if not registration:
            return None
        
        # Return existing instance if available
        if registration.tool_instance:
            return registration.tool_instance
        
        # Create instance on demand
        if self.service_manager:
            try:
                module = importlib.import_module(registration.module_path)
                tool_class = getattr(module, registration.class_name)
                tool_instance = tool_class(self.service_manager)
                registration.tool_instance = tool_instance
                return tool_instance
            except Exception as e:
                logger.error(f"Failed to create tool instance for {tool_id}: {e}")
                return None
        
        return None
    
    async def call_tool(self, tool_id: str, request_data: Dict[str, Any]) -> ToolResult:
        """Call a tool via MCP interface"""
        tool_instance = self.get_tool_instance(tool_id)
        if not tool_instance:
            return ToolResult(
                tool_id=tool_id,
                status="error",
                data=None,
                metadata={},
                execution_time=0.0,
                memory_used=0,
                error_code="TOOL_NOT_FOUND",
                error_message=f"Tool {tool_id} not found or could not be instantiated"
            )
        
        try:
            # Convert request data to ToolRequest (matching base_tool.ToolRequest interface)
            tool_request = ToolRequest(
                tool_id=tool_id,
                operation="execute",
                input_data=request_data.get('input_data', {}),
                parameters=request_data.get('parameters', {}),
                context=request_data.get('context', {}),
                validation_mode=False
            )
            
            # Execute the tool (tools are synchronous, not async)
            result = tool_instance.execute(tool_request)
            return result
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_id}: {e}")
            return ToolResult(
                tool_id=tool_id,
                status="error",
                data=None,
                metadata={},
                execution_time=0.0,
                memory_used=0,
                error_code="TOOL_EXECUTION_FAILED",
                error_message=f"Tool execution failed: {str(e)}"
            )
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        instantiated_count = sum(1 for reg in self.tools.values() if reg.tool_instance is not None)
        
        return {
            "total_tools": len(self.tools),
            "instantiated_tools": instantiated_count,
            "tools_by_id": list(self.tools.keys()),
            "registry_status": "operational" if self.tools else "empty"
        }