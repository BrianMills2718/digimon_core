"""
Tool Instantiator

Handles tool instantiation, configuration, and lifecycle management.
"""

import gc
import logging
import weakref
import threading
from typing import Dict, Any, Optional, Type, List, Union
from datetime import datetime
from contextlib import contextmanager

from .tool_discovery import ToolDiscovery
from .workflow_config import Phase, OptimizationLevel, create_unified_workflow_config


class ToolInstantiator:
    """Manages tool instantiation, configuration, and lifecycle"""
    
    def __init__(self, tools_directory: str = "src/tools"):
        self.tool_discovery = ToolDiscovery(tools_directory)
        self.logger = logging.getLogger(__name__)
        self._tool_instances: weakref.WeakValueDictionary[str, Any] = weakref.WeakValueDictionary()
        self._tool_configs: Dict[str, Any] = {}
        self._instance_lock = threading.Lock()
        self._creation_stats: Dict[str, int] = {
            "total_created": 0,
            "successful_creations": 0,
            "failed_creations": 0,
            "active_instances": 0
        }
    
    def create_tool_instance(self, tool_name: str, config: Optional[Dict[str, Any]] = None, 
                           force_new: bool = False) -> Dict[str, Any]:
        """Create or retrieve a tool instance with comprehensive error handling"""
        try:
            # Check if instance already exists and force_new is False
            if not force_new and tool_name in self._tool_instances:
                existing_instance = self._tool_instances[tool_name]
                if existing_instance is not None:
                    return {
                        "success": True,
                        "instance": existing_instance,
                        "created_new": False,
                        "tool_name": tool_name,
                        "timestamp": datetime.now().isoformat()
                    }
            
            # Discover the tool class
            tools = self.tool_discovery.discover_all_tools()
            if tool_name not in tools:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not found",
                    "available_tools": list(tools.keys()),
                    "tool_name": tool_name,
                    "timestamp": datetime.now().isoformat()
                }
            
            tool_info = tools[tool_name]
            if "error" in tool_info:
                return {
                    "success": False,
                    "error": f"Tool discovery failed: {tool_info['error']}",
                    "tool_name": tool_name,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get the first available tool class
            tool_classes = tool_info.get("classes", [])
            if not tool_classes:
                return {
                    "success": False,
                    "error": "No tool classes found",
                    "tool_name": tool_name,
                    "timestamp": datetime.now().isoformat()
                }
            
            tool_class = tool_classes[0]  # Use first available class
            
            # Create instance with configuration
            instance = self._instantiate_tool_class(tool_class, config or {})
            
            # Store instance with weak reference
            with self._instance_lock:
                self._tool_instances[tool_name] = instance
                self._tool_configs[tool_name] = config or {}
                self._creation_stats["total_created"] += 1
                self._creation_stats["successful_creations"] += 1
                self._creation_stats["active_instances"] = len(self._tool_instances)
            
            return {
                "success": True,
                "instance": instance,
                "created_new": True,
                "tool_name": tool_name,
                "tool_class": tool_class.__name__,
                "configuration": config or {},
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create tool instance '{tool_name}': {e}", exc_info=True)
            
            with self._instance_lock:
                self._creation_stats["total_created"] += 1
                self._creation_stats["failed_creations"] += 1
            
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "tool_name": tool_name,
                "timestamp": datetime.now().isoformat()
            }
    
    def _instantiate_tool_class(self, tool_class: Type, config: Dict[str, Any]) -> Any:
        """Instantiate a tool class with configuration"""
        try:
            # Check if tool class accepts configuration in constructor
            import inspect
            sig = inspect.signature(tool_class.__init__)
            params = list(sig.parameters.keys())
            
            # Create instance based on constructor signature
            if len(params) > 1:  # More than just 'self'
                # Try to pass config as keyword arguments
                try:
                    instance = tool_class(**config)
                except TypeError:
                    # Fallback to positional arguments if available
                    if config and len(params) >= 2:
                        first_param = list(config.values())[0]
                        instance = tool_class(first_param)
                    else:
                        instance = tool_class()
            else:
                # No config parameters, create with defaults
                instance = tool_class()
            
            # Set configuration attributes if possible
            if hasattr(instance, 'configure') and callable(instance.configure):
                instance.configure(config)
            elif config:
                # Set config attributes directly
                for key, value in config.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
            
            return instance
            
        except Exception as e:
            raise RuntimeError(f"Failed to instantiate {tool_class.__name__}: {e}")
    
    def get_tool_instance(self, tool_name: str) -> Optional[Any]:
        """Get existing tool instance"""
        return self._tool_instances.get(tool_name)
    
    def remove_tool_instance(self, tool_name: str) -> bool:
        """Remove tool instance and clean up resources"""
        try:
            with self._instance_lock:
                if tool_name in self._tool_instances:
                    instance = self._tool_instances[tool_name]
                    
                    # Call cleanup method if available
                    if hasattr(instance, 'cleanup') and callable(instance.cleanup):
                        try:
                            instance.cleanup()
                        except Exception as e:
                            self.logger.warning(f"Cleanup failed for {tool_name}: {e}")
                    
                    # Remove from tracking
                    del self._tool_instances[tool_name]
                    if tool_name in self._tool_configs:
                        del self._tool_configs[tool_name]
                    
                    self._creation_stats["active_instances"] = len(self._tool_instances)
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to remove tool instance '{tool_name}': {e}")
            return False
    
    def create_workflow_tools(self, phase: Phase, optimization_level: OptimizationLevel = OptimizationLevel.STANDARD) -> Dict[str, Any]:
        """Create all tools for a specific workflow phase"""
        workflow_config = create_unified_workflow_config(phase, optimization_level)
        required_tools = workflow_config.get("tools", [])
        
        results: Dict[str, Any] = {
            "phase": phase.value,
            "optimization_level": optimization_level.value,
            "total_tools": len(required_tools),
            "successful_creations": 0,
            "failed_creations": 0,
            "tool_instances": {},
            "errors": [],
            "timestamp": datetime.now().isoformat()
        }
        
        for tool_name in required_tools:
            # Find matching tool (handle naming variations)
            matching_tool = self._find_matching_tool(tool_name)
            
            if matching_tool:
                # Create tool instance with workflow configuration
                tool_config = self._extract_tool_config(workflow_config, tool_name)
                creation_result = self.create_tool_instance(matching_tool, tool_config)
                
                if creation_result["success"]:
                    tool_instances = results["tool_instances"]
                    if isinstance(tool_instances, dict):
                        tool_instances[tool_name] = creation_result["instance"]
                    results["successful_creations"] += 1
                else:
                    errors = results["errors"]
                    if isinstance(errors, list):
                        errors.append(f"{tool_name}: {creation_result['error']}")
                    results["failed_creations"] += 1
            else:
                results["errors"].append(f"Tool '{tool_name}' not found in discovered tools")
                results["failed_creations"] += 1
        
        return results
    
    def _find_matching_tool(self, requested_tool: str) -> Optional[str]:
        """Find matching tool name in discovered tools"""
        discovered_tools = self.tool_discovery.discover_all_tools()
        
        # Direct match
        if requested_tool in discovered_tools:
            return requested_tool
        
        # Try phase-prefixed versions
        for phase in ["phase1", "phase2", "phase3"]:
            candidate = f"{phase}.{requested_tool}"
            if candidate in discovered_tools:
                return candidate
        
        # Try partial matching
        for discovered_name in discovered_tools.keys():
            if requested_tool in discovered_name or discovered_name.endswith(requested_tool):
                return discovered_name
        
        return None
    
    def _extract_tool_config(self, workflow_config: Dict[str, Any], tool_name: str) -> Dict[str, Any]:
        """Extract tool-specific configuration from workflow config"""
        tool_config = {}
        
        # Add performance settings
        if "performance" in workflow_config:
            tool_config.update(workflow_config["performance"])
        
        # Add service configurations
        if "services" in workflow_config:
            tool_config["services"] = workflow_config["services"]
        
        # Add phase-specific settings
        tool_config["phase"] = workflow_config.get("phase", "phase1")
        tool_config["optimization_level"] = workflow_config.get("optimization_level", "standard")
        
        return tool_config
    
    @contextmanager
    def managed_tool_instance(self, tool_name: str, config: Optional[Dict[str, Any]] = None):
        """Context manager for automatic tool lifecycle management"""
        instance_result = self.create_tool_instance(tool_name, config)
        
        if not instance_result["success"]:
            raise RuntimeError(f"Failed to create tool instance: {instance_result['error']}")
        
        instance = instance_result["instance"]
        
        try:
            yield instance
        finally:
            # Cleanup is handled by weak references, but we can force it
            if hasattr(instance, 'cleanup') and callable(instance.cleanup):
                try:
                    instance.cleanup()
                except Exception as e:
                    self.logger.warning(f"Cleanup failed for {tool_name}: {e}")
    
    def cleanup_all_instances(self) -> Dict[str, Any]:
        """Clean up all tool instances and release resources"""
        errors: list[str] = []
        cleanup_results: Dict[str, Any] = {
            "total_instances": len(self._tool_instances),
            "successful_cleanups": 0,
            "failed_cleanups": 0,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
        
        # Get list of current instances (copy to avoid modification during iteration)
        with self._instance_lock:
            instance_names = list(self._tool_instances.keys())
        
        for tool_name in instance_names:
            try:
                if self.remove_tool_instance(tool_name):
                    cleanup_results["successful_cleanups"] += 1
                else:
                    cleanup_results["failed_cleanups"] += 1
                    errors.append(f"Failed to remove {tool_name}")
            except Exception as e:
                cleanup_results["failed_cleanups"] += 1
                errors.append(f"{tool_name}: {str(e)}")
        
        # Force garbage collection
        collected = gc.collect()
        cleanup_results["garbage_collected"] = collected
        
        # Reset stats
        with self._instance_lock:
            self._creation_stats["active_instances"] = 0
        
        return cleanup_results
    
    def get_instantiation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive instantiation statistics"""
        with self._instance_lock:
            stats = {
                "timestamp": datetime.now().isoformat(),
                "creation_stats": self._creation_stats.copy(),
                "active_instances": {
                    "count": len(self._tool_instances),
                    "names": list(self._tool_instances.keys())
                },
                "memory_usage": {
                    "weak_references": len(self._tool_instances),
                    "configurations": len(self._tool_configs)
                },
                "success_rate": 0.0
            }
        
        # Calculate success rate
        creation_stats = stats["creation_stats"]
        if isinstance(creation_stats, dict):
            total_attempts = creation_stats.get("total_created", 0)
            if total_attempts > 0:
                successful = creation_stats.get("successful_creations", 0)
                success_rate = (successful / total_attempts) * 100
                stats["success_rate"] = round(success_rate, 2)
        
        return stats
    
    def validate_tool_instance(self, tool_name: str) -> Dict[str, Any]:
        """Validate a tool instance for proper functionality"""
        errors: list[str] = []
        recommendations: list[str] = []
        validation: Dict[str, Any] = {
            "tool_name": tool_name,
            "valid": False,
            "exists": False,
            "callable": False,
            "has_execute": False,
            "configuration_valid": False,
            "errors": errors,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Check if instance exists
            instance = self.get_tool_instance(tool_name)
            if instance is None:
                errors.append("Tool instance does not exist")
                return validation
            
            validation["exists"] = True
            
            # Check if instance has execute method
            if hasattr(instance, 'execute') and callable(instance.execute):
                validation["has_execute"] = True
                validation["callable"] = True
                
                # Test execute method with minimal input
                try:
                    test_result = instance.execute({"test": True})
                    if isinstance(test_result, dict):
                        validation["valid"] = True
                    else:
                        errors.append(f"Execute method returned {type(test_result)}, expected dict")
                except Exception as e:
                    errors.append(f"Execute method failed: {str(e)}")
            else:
                errors.append("Tool instance missing callable execute method")
            
            # Check configuration
            if tool_name in self._tool_configs:
                config = self._tool_configs[tool_name]
                validation["configuration_valid"] = isinstance(config, dict)
                if not validation["configuration_valid"]:
                    errors.append("Invalid configuration format")
            
            # Generate recommendations
            if not validation["valid"]:
                recommendations.append("Tool instance requires fixing before use")
            
            if not validation["has_execute"]:
                recommendations.append("Implement execute method for tool compatibility")
            
        except Exception as e:
            errors.append(f"Validation failed: {str(e)}")
            self.logger.error(f"Tool validation failed for {tool_name}: {e}")
            self.logger.error(f"Tool validation failed for {tool_name}: {e}")
        
        return validation