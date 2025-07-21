import importlib
import importlib.util
import inspect
import logging
from typing import Dict, Any, List, Optional, Type
from pathlib import Path
from datetime import datetime

from src.core.config_manager import get_config


class ToolDiscoveryService:
    """
    Service responsible for discovering tool implementations across phase directories.
    
    Handles file system scanning, module loading, and tool class identification.
    Separated from ToolFactory to provide focused responsibility for tool discovery.
    """
    
    def __init__(self, tools_directory: str = "src/tools"):
        """
        Initialize the tool discovery service.
        
        Args:
            tools_directory: Base directory containing tool implementations
        """
        self.tools_directory = tools_directory
        self.discovered_tools: Dict[str, Any] = {}
        self.discovery_cache: Dict[str, Dict[str, Any]] = {}
        self.last_discovery_time: Optional[datetime] = None
        self.logger = logging.getLogger(__name__)
        
        # Get configuration for discovery settings
        self.config = get_config()
        
    def discover_tools_in_directory(self, directory: str) -> Dict[str, Any]:
        """
        Scan a specific directory for tool implementations.
        
        Args:
            directory: Directory path to scan for tools
            
        Returns:
            Dict mapping tool names to their metadata and classes
        """
        tools = {}
        directory_path = Path(directory)
        
        if not directory_path.exists():
            self.logger.warning(f"Directory does not exist: {directory}")
            return tools
            
        self.logger.info(f"Discovering tools in directory: {directory}")
        
        for py_file in directory_path.glob("*.py"):
            if py_file.name.startswith("t") and py_file.name != "__init__.py":
                tool_name = py_file.stem
                
                try:
                    tool_info = self._load_tool_from_file(py_file, tool_name)
                    if tool_info:
                        tools[tool_name] = tool_info
                        self.logger.debug(f"Discovered tool: {tool_name}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to load tool {tool_name} from {py_file}: {e}")
                    tools[tool_name] = {
                        "error": str(e),
                        "status": "error",
                        "file_path": str(py_file)
                    }
        
        return tools
    
    def discover_all_tools(self) -> Dict[str, Any]:
        """
        Discover all tool classes across all phase directories.
        
        Returns:
            Dict mapping tool names to their metadata and classes
        """
        tools = {}
        discovery_start = datetime.now()
        
        self.logger.info("Starting comprehensive tool discovery")
        
        # Scan each phase directory
        for phase_dir in ["phase1", "phase2", "phase3"]:
            phase_path = Path(self.tools_directory) / phase_dir
            
            if phase_path.exists():
                phase_tools = self.discover_tools_in_directory(str(phase_path))
                
                # Add phase information to each tool
                for tool_name, tool_info in phase_tools.items():
                    if isinstance(tool_info, dict) and "error" not in tool_info:
                        tool_info["phase"] = phase_dir
                    tools[tool_name] = tool_info
                    
                self.logger.info(f"Discovered {len(phase_tools)} tools in {phase_dir}")
            else:
                self.logger.warning(f"Phase directory does not exist: {phase_path}")
        
        # Update discovery metadata
        self.discovered_tools = tools
        self.last_discovery_time = discovery_start
        
        discovery_duration = (datetime.now() - discovery_start).total_seconds()
        self.logger.info(f"Tool discovery completed in {discovery_duration:.2f}s. Found {len(tools)} tools.")
        
        return tools
    
    def validate_tool_interface(self, tool_class: Type) -> bool:
        """
        Verify that a tool class implements the required interface.
        
        Args:
            tool_class: Tool class to validate
            
        Returns:
            True if tool implements required interface, False otherwise
        """
        required_methods = ["execute", "get_tool_info"]
        
        for method_name in required_methods:
            if not hasattr(tool_class, method_name):
                self.logger.warning(f"Tool {tool_class.__name__} missing required method: {method_name}")
                return False
                
            method = getattr(tool_class, method_name)
            if not callable(method):
                self.logger.warning(f"Tool {tool_class.__name__} has non-callable {method_name}")
                return False
        
        return True
    
    def get_tool_metadata(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific discovered tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool metadata dictionary or None if not found
        """
        if tool_name in self.discovered_tools:
            return self.discovered_tools[tool_name]
        
        # If not in cache, try to discover it
        self.logger.info(f"Tool {tool_name} not in cache, re-running discovery")
        self.discover_all_tools()
        
        return self.discovered_tools.get(tool_name)
    
    def list_discovered_tools(self) -> List[str]:
        """
        Get list of all discovered tool names.
        
        Returns:
            List of tool names
        """
        return list(self.discovered_tools.keys())
    
    def get_tools_by_phase(self, phase: str) -> Dict[str, Any]:
        """
        Get all tools belonging to a specific phase.
        
        Args:
            phase: Phase name (phase1, phase2, phase3)
            
        Returns:
            Dict of tools for the specified phase
        """
        phase_tools = {}
        
        for tool_name, tool_info in self.discovered_tools.items():
            if isinstance(tool_info, dict) and tool_info.get("phase") == phase:
                phase_tools[tool_name] = tool_info
        
        return phase_tools
    
    def get_discovery_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the tool discovery process.
        
        Returns:
            Dictionary containing discovery statistics
        """
        stats = {
            "total_tools_discovered": len(self.discovered_tools),
            "last_discovery_time": self.last_discovery_time.isoformat() if self.last_discovery_time else None,
            "tools_by_phase": {},
            "tools_with_errors": 0,
            "valid_tools": 0
        }
        
        # Count tools by phase and status
        for tool_name, tool_info in self.discovered_tools.items():
            if isinstance(tool_info, dict):
                phase = tool_info.get("phase", "unknown")
                if phase not in stats["tools_by_phase"]:
                    stats["tools_by_phase"][phase] = 0
                stats["tools_by_phase"][phase] += 1
                
                if "error" in tool_info:
                    stats["tools_with_errors"] += 1
                else:
                    stats["valid_tools"] += 1
        
        return stats
    
    def refresh_discovery(self, force: bool = False) -> Dict[str, Any]:
        """
        Refresh tool discovery, optionally forcing a full rediscovery.
        
        Args:
            force: If True, forces rediscovery even if cache is recent
            
        Returns:
            Updated tools dictionary
        """
        if force or not self.last_discovery_time:
            self.logger.info("Forcing full tool rediscovery")
            return self.discover_all_tools()
        
        # Check if discovery is recent (within last 5 minutes)
        if self.last_discovery_time:
            time_since_discovery = (datetime.now() - self.last_discovery_time).total_seconds()
            if time_since_discovery < 300:  # 5 minutes
                self.logger.debug("Using cached discovery results (recent)")
                return self.discovered_tools
        
        # Rediscover if cache is stale
        self.logger.info("Discovery cache is stale, refreshing")
        return self.discover_all_tools()
    
    def _load_tool_from_file(self, py_file: Path, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a tool class from a Python file.
        
        Args:
            py_file: Path to the Python file
            tool_name: Name of the tool
            
        Returns:
            Tool information dictionary or None if loading failed
        """
        try:
            # Determine module path based on file location
            relative_path = py_file.relative_to(Path(self.tools_directory).parent.parent)
            module_path = str(relative_path.with_suffix("")).replace("/", ".")
            
            # Load the module
            spec = importlib.util.spec_from_file_location(module_path, py_file)
            if not spec or not spec.loader:
                self.logger.error(f"Could not create module spec for {py_file}")
                return None
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find tool classes in the module
            tool_classes = []
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    name.lower().replace('_', '').startswith(tool_name.lower().replace('_', '')) and
                    hasattr(obj, 'execute')):
                    tool_classes.append(obj)
            
            if not tool_classes:
                self.logger.warning(f"No tool classes found in {py_file}")
                return None
            
            # Use the first matching tool class
            tool_class = tool_classes[0]
            
            # Validate the tool interface
            if not self.validate_tool_interface(tool_class):
                return {
                    "error": "Tool does not implement required interface",
                    "status": "interface_error",
                    "file_path": str(py_file),
                    "class_name": tool_class.__name__
                }
            
            # Extract tool metadata
            tool_info = {
                "class": tool_class,
                "class_name": tool_class.__name__,
                "module_path": module_path,
                "file_path": str(py_file),
                "status": "discovered",
                "discovery_time": datetime.now().isoformat(),
                "has_execute": hasattr(tool_class, 'execute'),
                "has_get_tool_info": hasattr(tool_class, 'get_tool_info'),
                "interface_valid": True
            }
            
            # Try to get additional tool info if available
            try:
                if hasattr(tool_class, 'get_tool_info'):
                    instance = tool_class()
                    additional_info = instance.get_tool_info()
                    if isinstance(additional_info, dict):
                        tool_info.update(additional_info)
            except Exception as e:
                self.logger.debug(f"Could not get additional info for {tool_name}: {e}")
            
            return tool_info
            
        except Exception as e:
            self.logger.error(f"Failed to load tool from {py_file}: {e}")
            return None