"""
Tool Registry for Unified KGAS System

Manages all tools and their compatibility.
No hardcoded lists. Dynamic discovery.
"""

from typing import Dict, List, Optional, Type
import logging
from pathlib import Path
import importlib.util
import inspect

from unified_data_contract import ToolCategory, DataCategory, can_chain_categories
from base_tool import UnifiedTool, ToolMetadata

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Dynamic tool registry that discovers and manages tools.
    No hardcoding. Tools self-register based on their metadata.
    """
    
    def __init__(self):
        self.tools: Dict[str, UnifiedTool] = {}
        self.categories: Dict[ToolCategory, List[str]] = {
            category: [] for category in ToolCategory
        }
        self.data_producers: Dict[DataCategory, List[str]] = {
            category: [] for category in DataCategory
        }
        self.data_consumers: Dict[DataCategory, List[str]] = {
            category: [] for category in DataCategory
        }
        self.logger = logging.getLogger("ToolRegistry")
    
    def register_tool(self, tool: UnifiedTool):
        """Register a tool and index its capabilities"""
        tool_id = tool.metadata.tool_id
        
        if tool_id in self.tools:
            self.logger.warning(f"Tool {tool_id} already registered, overwriting")
        
        # Store the tool
        self.tools[tool_id] = tool
        
        # Index by category
        self.categories[tool.metadata.category].append(tool_id)
        
        # Index by data types produced
        for data_type in tool.metadata.output_types:
            self.data_producers[data_type].append(tool_id)
        
        # Index by data types consumed
        for data_type in tool.metadata.input_types:
            self.data_consumers[data_type].append(tool_id)
        
        self.logger.info(f"Registered {tool_id}: {tool.metadata.name}")
    
    def discover_tools_from_module(self, module_path: str):
        """Dynamically discover and register tools from a Python module"""
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location("tools_module", module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find all UnifiedTool subclasses
            discovered = 0
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, UnifiedTool) and 
                    obj != UnifiedTool):
                    try:
                        # Instantiate and register
                        tool_instance = obj()
                        self.register_tool(tool_instance)
                        discovered += 1
                    except Exception as e:
                        self.logger.error(f"Failed to instantiate {name}: {e}")
            
            self.logger.info(f"Discovered {discovered} tools from {module_path}")
            return discovered
            
        except Exception as e:
            self.logger.error(f"Failed to discover tools from {module_path}: {e}")
            return 0
    
    def get_tool(self, tool_id: str) -> Optional[UnifiedTool]:
        """Get a tool by ID"""
        return self.tools.get(tool_id)
    
    def get_tools_by_category(self, category: ToolCategory) -> List[UnifiedTool]:
        """Get all tools in a category"""
        tool_ids = self.categories.get(category, [])
        return [self.tools[tid] for tid in tool_ids]
    
    def find_compatible_tools(self, source_tool_id: str) -> List[str]:
        """
        Find all tools that can accept output from the source tool.
        
        This is the KEY difference from the hardcoded system:
        - Uses category-based compatibility rules
        - Checks data type compatibility
        - Returns ALL compatible tools, not just a hardcoded list
        """
        source_tool = self.tools.get(source_tool_id)
        if not source_tool:
            return []
        
        compatible = []
        
        # Get tools that can accept this category
        source_category = source_tool.metadata.category
        for target_category in ToolCategory:
            if can_chain_categories(source_category, target_category):
                # Get all tools in the target category
                for target_tool_id in self.categories[target_category]:
                    target_tool = self.tools[target_tool_id]
                    
                    # Check data type compatibility
                    if self._check_data_compatibility(source_tool, target_tool):
                        compatible.append(target_tool_id)
        
        return compatible
    
    def _check_data_compatibility(self, source: UnifiedTool, target: UnifiedTool) -> bool:
        """
        Check if target can consume what source produces.
        
        Key insight: With unified data contract, tools can consume
        ANY data type that exists in UnifiedData. They just use what
        they need and ignore the rest.
        """
        # If target has no input requirements, it can accept anything
        if not target.metadata.input_types:
            return True
        
        # Check if source produces at least one type target needs
        source_outputs = set(source.metadata.output_types)
        target_inputs = set(target.metadata.input_types)
        
        # If there's overlap, they're compatible
        return bool(source_outputs & target_inputs)
    
    def find_chain_path(self, start_category: ToolCategory, 
                       end_category: ToolCategory) -> List[List[str]]:
        """
        Find possible tool chains from start to end category.
        Returns multiple paths if available.
        """
        paths = []
        
        # Get starting tools
        start_tools = self.categories.get(start_category, [])
        
        for start_tool in start_tools:
            # Try to build chains from this starting point
            self._find_paths_recursive(start_tool, end_category, [start_tool], paths)
        
        return paths
    
    def _find_paths_recursive(self, current_tool_id: str, 
                            target_category: ToolCategory,
                            current_path: List[str], 
                            all_paths: List[List[str]],
                            max_depth: int = 10):
        """Recursively find paths to target category"""
        
        if len(current_path) > max_depth:
            return  # Prevent infinite recursion
        
        current_tool = self.tools[current_tool_id]
        
        # If we've reached the target category, save this path
        if current_tool.metadata.category == target_category:
            all_paths.append(current_path.copy())
            return
        
        # Try all compatible next tools
        compatible = self.find_compatible_tools(current_tool_id)
        for next_tool_id in compatible:
            if next_tool_id not in current_path:  # Avoid cycles
                new_path = current_path + [next_tool_id]
                self._find_paths_recursive(next_tool_id, target_category, 
                                         new_path, all_paths, max_depth)
    
    def get_statistics(self) -> Dict:
        """Get registry statistics"""
        stats = {
            "total_tools": len(self.tools),
            "by_category": {},
            "by_data_type_produced": {},
            "by_data_type_consumed": {},
            "compatibility_matrix": {}
        }
        
        # Count by category
        for category in ToolCategory:
            stats["by_category"][category.value] = len(self.categories[category])
        
        # Count by data types
        for data_type in DataCategory:
            stats["by_data_type_produced"][data_type.value] = len(self.data_producers[data_type])
            stats["by_data_type_consumed"][data_type.value] = len(self.data_consumers[data_type])
        
        # Build compatibility matrix
        for tool_id in self.tools:
            compatible = self.find_compatible_tools(tool_id)
            stats["compatibility_matrix"][tool_id] = len(compatible)
        
        return stats
    
    def describe_tool(self, tool_id: str) -> Dict:
        """Get detailed information about a tool"""
        tool = self.tools.get(tool_id)
        if not tool:
            return {"error": f"Tool {tool_id} not found"}
        
        compatible_tools = self.find_compatible_tools(tool_id)
        
        return {
            "tool_id": tool.metadata.tool_id,
            "name": tool.metadata.name,
            "description": tool.metadata.description,
            "category": tool.metadata.category.value,
            "inputs": [t.value for t in tool.metadata.input_types],
            "outputs": [t.value for t in tool.metadata.output_types],
            "compatible_with": compatible_tools,
            "compatibility_count": len(compatible_tools)
        }