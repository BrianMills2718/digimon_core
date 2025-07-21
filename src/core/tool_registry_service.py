import logging
from typing import Dict, Any, Optional, Type, List
from datetime import datetime
from threading import Lock

from src.core.tool_discovery_service import ToolDiscoveryService
from src.core.config_manager import get_config


class ToolRegistryService:
    """
    Service responsible for tool registration and instantiation.
    
    Manages the registry of available tools and provides thread-safe
    tool instance creation with proper lifecycle management.
    
    This is separate from the validation-based ToolRegistry in tool_registry.py.
    """
    
    def __init__(self, discovery_service: Optional[ToolDiscoveryService] = None):
        """
        Initialize the tool registry service.
        
        Args:
            discovery_service: ToolDiscoveryService instance for tool discovery
        """
        self.discovery_service = discovery_service or ToolDiscoveryService()
        self.registered_tools: Dict[str, Type] = {}
        self.tool_instances: Dict[str, Any] = {}
        self.tool_metadata: Dict[str, Dict[str, Any]] = {}
        self.registration_lock = Lock()
        self.instantiation_lock = Lock()
        self.logger = logging.getLogger(__name__)
        
        # Get configuration
        self.config = get_config()
        
        # Auto-discover and register tools on initialization
        self._auto_register_discovered_tools()
        
    def register_tool(self, tool_name: str, tool_class: Type, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a tool class for use.
        
        Args:
            tool_name: Unique name for the tool
            tool_class: Tool class to register
            metadata: Optional metadata about the tool
            
        Returns:
            True if registration successful, False otherwise
        """
        with self.registration_lock:
            try:
                # Validate tool interface
                if not self.discovery_service.validate_tool_interface(tool_class):
                    self.logger.error(f"Tool {tool_name} does not implement required interface")
                    return False
                
                # Register the tool
                self.registered_tools[tool_name] = tool_class
                self.tool_metadata[tool_name] = metadata or {}
                self.tool_metadata[tool_name].update({
                    "registration_time": datetime.now().isoformat(),
                    "class_name": tool_class.__name__,
                    "status": "registered"
                })
                
                self.logger.info(f"Successfully registered tool: {tool_name}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to register tool {tool_name}: {e}")
                return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a tool and cleanup its instances.
        
        Args:
            tool_name: Name of tool to unregister
            
        Returns:
            True if unregistration successful, False otherwise
        """
        with self.registration_lock:
            try:
                # Remove from registry
                if tool_name in self.registered_tools:
                    del self.registered_tools[tool_name]
                
                if tool_name in self.tool_metadata:
                    del self.tool_metadata[tool_name]
                
                # Cleanup instances
                with self.instantiation_lock:
                    if tool_name in self.tool_instances:
                        instance = self.tool_instances[tool_name]
                        # Call cleanup if available
                        if hasattr(instance, 'cleanup'):
                            try:
                                instance.cleanup()
                            except Exception as e:
                                self.logger.warning(f"Error during tool cleanup for {tool_name}: {e}")
                        
                        del self.tool_instances[tool_name]
                
                self.logger.info(f"Successfully unregistered tool: {tool_name}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to unregister tool {tool_name}: {e}")
                return False
    
    def create_tool_instance(self, tool_name: str, config: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """
        Create an instance of a registered tool.
        
        Args:
            tool_name: Name of the tool to instantiate
            config: Optional configuration for the tool
            
        Returns:
            Tool instance or None if creation failed
        """
        if tool_name not in self.registered_tools:
            self.logger.error(f"Tool {tool_name} is not registered")
            return None
        
        try:
            tool_class = self.registered_tools[tool_name]
            
            # Create instance with configuration if provided
            if config:
                instance = tool_class(**config)
            else:
                instance = tool_class()
            
            # Initialize if method exists
            if hasattr(instance, 'initialize'):
                instance.initialize()
            
            self.logger.debug(f"Created instance of tool: {tool_name}")
            return instance
            
        except Exception as e:
            self.logger.error(f"Failed to create instance of tool {tool_name}: {e}")
            return None
    
    def get_tool_instance(self, tool_name: str, config: Optional[Dict[str, Any]] = None, 
                         force_new: bool = False) -> Optional[Any]:
        """
        Get a tool instance, creating it if necessary.
        
        Args:
            tool_name: Name of the tool
            config: Optional configuration for the tool
            force_new: If True, creates a new instance even if one exists
            
        Returns:
            Tool instance or None if creation failed
        """
        with self.instantiation_lock:
            # Return existing instance if available and not forcing new
            if not force_new and tool_name in self.tool_instances:
                return self.tool_instances[tool_name]
            
            # Create new instance
            instance = self.create_tool_instance(tool_name, config)
            if instance:
                self.tool_instances[tool_name] = instance
                
                # Update metadata
                if tool_name in self.tool_metadata:
                    self.tool_metadata[tool_name]["last_instantiated"] = datetime.now().isoformat()
                    self.tool_metadata[tool_name]["instance_created"] = True
            
            return instance
    
    def is_tool_registered(self, tool_name: str) -> bool:
        """
        Check if a tool is registered.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            True if tool is registered, False otherwise
        """
        return tool_name in self.registered_tools
    
    def list_registered_tools(self) -> List[str]:
        """
        Get list of all registered tool names.
        
        Returns:
            List of registered tool names
        """
        return list(self.registered_tools.keys())
    
    def get_tool_metadata(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a registered tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool metadata dictionary or None if not found
        """
        return self.tool_metadata.get(tool_name)
    
    def get_tools_by_phase(self, phase: str) -> List[str]:
        """
        Get tool names for a specific phase.
        
        Args:
            phase: Phase name (phase1, phase2, phase3)
            
        Returns:
            List of tool names for the specified phase
        """
        phase_tools = []
        
        for tool_name, metadata in self.tool_metadata.items():
            if metadata.get("phase") == phase:
                phase_tools.append(tool_name)
        
        return phase_tools
    
    def cleanup_all_instances(self) -> None:
        """
        Cleanup all tool instances.
        
        Calls cleanup method on all instances if available.
        """
        with self.instantiation_lock:
            for tool_name, instance in self.tool_instances.items():
                try:
                    if hasattr(instance, 'cleanup'):
                        instance.cleanup()
                    self.logger.debug(f"Cleaned up instance: {tool_name}")
                except Exception as e:
                    self.logger.warning(f"Error cleaning up {tool_name}: {e}")
            
            self.tool_instances.clear()
            self.logger.info("All tool instances cleaned up")
    
    def get_registry_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the tool registry.
        
        Returns:
            Dictionary containing registry statistics
        """
        with self.registration_lock:
            with self.instantiation_lock:
                stats = {
                    "total_registered_tools": len(self.registered_tools),
                    "total_instances": len(self.tool_instances),
                    "tools_by_phase": {},
                    "tools_with_instances": 0,
                    "tools_without_instances": 0,
                    "registration_summary": {}
                }
                
                # Count tools by phase
                for tool_name, metadata in self.tool_metadata.items():
                    phase = metadata.get("phase", "unknown")
                    if phase not in stats["tools_by_phase"]:
                        stats["tools_by_phase"][phase] = 0
                    stats["tools_by_phase"][phase] += 1
                    
                    # Count instances
                    if tool_name in self.tool_instances:
                        stats["tools_with_instances"] += 1
                    else:
                        stats["tools_without_instances"] += 1
                    
                    # Registration summary
                    stats["registration_summary"][tool_name] = {
                        "registered": True,
                        "has_instance": tool_name in self.tool_instances,
                        "phase": phase,
                        "class_name": metadata.get("class_name", "unknown")
                    }
                
                return stats
    
    def refresh_from_discovery(self, force: bool = False) -> int:
        """
        Refresh registry from discovery service.
        
        Args:
            force: If True, forces rediscovery of tools
            
        Returns:
            Number of newly registered tools
        """
        self.logger.info("Refreshing registry from discovery service")
        
        # Get fresh tool discovery
        discovered_tools = self.discovery_service.refresh_discovery(force=force)
        
        newly_registered = 0
        
        for tool_name, tool_info in discovered_tools.items():
            if (isinstance(tool_info, dict) and 
                "class" in tool_info and 
                "error" not in tool_info):
                
                if not self.is_tool_registered(tool_name):
                    # Register newly discovered tool
                    tool_class = tool_info["class"]
                    metadata = {key: value for key, value in tool_info.items() 
                              if key != "class"}
                    
                    if self.register_tool(tool_name, tool_class, metadata):
                        newly_registered += 1
        
        self.logger.info(f"Registry refresh complete. {newly_registered} new tools registered.")
        return newly_registered
    
    def _auto_register_discovered_tools(self) -> None:
        """
        Automatically register all discovered tools.
        """
        self.logger.info("Auto-registering discovered tools")
        
        discovered_tools = self.discovery_service.discover_all_tools()
        registered_count = 0
        
        for tool_name, tool_info in discovered_tools.items():
            if (isinstance(tool_info, dict) and 
                "class" in tool_info and 
                "error" not in tool_info):
                
                tool_class = tool_info["class"]
                metadata = {key: value for key, value in tool_info.items() 
                          if key != "class"}
                
                if self.register_tool(tool_name, tool_class, metadata):
                    registered_count += 1
        
        self.logger.info(f"Auto-registration complete. {registered_count} tools registered.")
    
    def validate_all_registrations(self) -> Dict[str, Any]:
        """
        Validate all registered tools for interface compliance.
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "total_tools": len(self.registered_tools),
            "valid_tools": 0,
            "invalid_tools": 0,
            "tool_results": {}
        }
        
        for tool_name, tool_class in self.registered_tools.items():
            try:
                is_valid = self.discovery_service.validate_tool_interface(tool_class)
                validation_results["tool_results"][tool_name] = {
                    "valid": is_valid,
                    "class_name": tool_class.__name__,
                    "has_execute": hasattr(tool_class, 'execute'),
                    "has_get_tool_info": hasattr(tool_class, 'get_tool_info')
                }
                
                if is_valid:
                    validation_results["valid_tools"] += 1
                else:
                    validation_results["invalid_tools"] += 1
                    
            except Exception as e:
                validation_results["tool_results"][tool_name] = {
                    "valid": False,
                    "error": str(e),
                    "class_name": tool_class.__name__ if hasattr(tool_class, '__name__') else "unknown"
                }
                validation_results["invalid_tools"] += 1
        
        self.logger.info(f"Validation complete: {validation_results['valid_tools']}/{validation_results['total_tools']} tools valid")
        return validation_results