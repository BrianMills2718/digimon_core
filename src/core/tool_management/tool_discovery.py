"""
Tool Discovery

Handles discovery and inspection of tool classes in the tools directory.
"""

import importlib
import importlib.util
import inspect
import sys
import logging
from typing import Dict, Any, List
from pathlib import Path


class ToolDiscovery:
    """Discovers and catalogs tool classes in the tools directory"""
    
    def __init__(self, tools_directory: str = "src/tools"):
        self.tools_directory = tools_directory
        self.logger = logging.getLogger(__name__)
    
    def discover_all_tools(self) -> Dict[str, Any]:
        """Discover all tool classes in the tools directory - COMPLETE IMPLEMENTATION"""
        tools = {}
        
        for phase_dir in ["phase1", "phase2", "phase3"]:
            phase_path = Path(self.tools_directory) / phase_dir
            if phase_path.exists():
                phase_tools = self._discover_phase_tools(phase_dir, phase_path)
                tools.update(phase_tools)
        
        return tools
    
    def _discover_phase_tools(self, phase_dir: str, phase_path: Path) -> Dict[str, Any]:
        """Discover tools in a specific phase directory"""
        tools = {}
        
        for py_file in phase_path.glob("*.py"):
            if py_file.name.startswith("t") and py_file.name != "__init__.py":
                tool_name = py_file.stem
                tool_info = self._inspect_tool_file(phase_dir, tool_name, py_file)
                tools[f"{phase_dir}.{tool_name}"] = tool_info
        
        return tools
    
    def _inspect_tool_file(self, phase_dir: str, tool_name: str, py_file: Path) -> Dict[str, Any]:
        """Inspect a tool file and extract tool classes"""
        try:
            module_path = f"src.tools.{phase_dir}.{tool_name}"
            
            # Actually import and inspect the module
            spec = importlib.util.spec_from_file_location(module_path, py_file)
            if spec is None:
                raise ImportError(f"Could not load spec for {module_path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_path] = module
            
            if spec.loader is None:
                raise ImportError(f"No loader found for {module_path}")
            
            spec.loader.exec_module(module)
            
            # Find actual tool classes with execute methods
            tool_classes = self._extract_tool_classes(module)
            
            if tool_classes:
                return {
                    "classes": tool_classes,
                    "module": module_path,
                    "file": str(py_file),
                    "status": "discovered",
                    "class_count": len(tool_classes)
                }
            else:
                return {
                    "error": "No tool classes with execute method found",
                    "status": "failed",
                    "module": module_path,
                    "file": str(py_file)
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed",
                "module": f"src.tools.{phase_dir}.{tool_name}",
                "file": str(py_file)
            }
    
    def _extract_tool_classes(self, module) -> List[type]:
        """Extract tool classes from a module"""
        tool_classes = []
        
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                hasattr(obj, 'execute') and 
                callable(getattr(obj, 'execute'))):
                tool_classes.append(obj)
        
        return tool_classes
    
    def get_tool_statistics(self, discovered_tools: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics about discovered tools"""
        phase_breakdown = {
            "phase1": 0,
            "phase2": 0,
            "phase3": 0
        }
        status_breakdown = {
            "discovered": 0,
            "failed": 0
        }
        stats: Dict[str, Any] = {
            "total_tools": len(discovered_tools),
            "successful_discoveries": 0,
            "failed_discoveries": 0,
            "total_classes": 0,
            "phase_breakdown": phase_breakdown,
            "status_breakdown": status_breakdown
        }
        
        for tool_name, tool_info in discovered_tools.items():
            if tool_info.get("status") == "discovered":
                stats["successful_discoveries"] += 1
                status_breakdown["discovered"] += 1
                stats["total_classes"] += tool_info.get("class_count", 0)
            else:
                stats["failed_discoveries"] += 1
                status_breakdown["failed"] += 1
            
            # Phase breakdown
            if tool_name.startswith("phase1"):
                phase_breakdown["phase1"] += 1
            elif tool_name.startswith("phase2"):
                phase_breakdown["phase2"] += 1
            elif tool_name.startswith("phase3"):
                phase_breakdown["phase3"] += 1
        
        return stats
    
    def validate_tool_structure(self, tool_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the structure of a discovered tool"""
        issues: list[str] = []
        recommendations: list[str] = []
        validation: Dict[str, Any] = {
            "valid": True,
            "issues": issues,
            "recommendations": recommendations
        }
        
        if "error" in tool_info:
            validation["valid"] = False
            issues.append(f"Discovery error: {tool_info['error']}")
            return validation
        
        if tool_info.get("status") != "discovered":
            validation["valid"] = False
            issues.append(f"Tool status is {tool_info.get('status')}, not 'discovered'")
        
        classes = tool_info.get("classes", [])
        if not classes:
            validation["valid"] = False
            issues.append("No tool classes found")
        else:
            # Validate each class
            for tool_class in classes:
                class_validation = self._validate_tool_class(tool_class)
                if not class_validation["valid"]:
                    validation["valid"] = False
                    class_issues = class_validation.get("issues", [])
                    if isinstance(class_issues, list):
                        issues.extend(class_issues)
                validation["recommendations"].extend(class_validation["recommendations"])
        
        return validation
    
    def _validate_tool_class(self, tool_class: type) -> Dict[str, Any]:
        """Validate a specific tool class"""
        issues: list[str] = []
        recommendations: list[str] = []
        validation: Dict[str, Any] = {
            "valid": True,
            "issues": issues,
            "recommendations": recommendations
        }
        
        class_name = tool_class.__name__
        
        # Check for execute method
        if not hasattr(tool_class, 'execute'):
            validation["valid"] = False
            issues.append(f"Class {class_name} missing 'execute' method")
        elif not callable(getattr(tool_class, 'execute')):
            validation["valid"] = False
            issues.append(f"Class {class_name} 'execute' is not callable")
        
        # Check for recommended methods
        recommended_methods = ['validate_input', 'get_info', 'cleanup']
        for method in recommended_methods:
            if not hasattr(tool_class, method):
                recommendations.append(f"Consider adding '{method}' method to {class_name}")
        
        # Check method signatures
        if hasattr(tool_class, 'execute'):
            sig = inspect.signature(tool_class.execute)
            params = list(sig.parameters.keys())
            
            if len(params) < 2:  # self + at least one parameter
                recommendations.append(f"Execute method in {class_name} should accept input parameters")
        
        return validation
    
    def get_tool_dependencies(self, discovered_tools: Dict[str, Any]) -> Dict[str, List[str]]:
        """Analyze dependencies between tools"""
        dependencies = {}
        
        for tool_name, tool_info in discovered_tools.items():
            if tool_info.get("status") != "discovered":
                continue
            
            tool_deps = []
            
            # Analyze imports and dependencies
            try:
                module_path = tool_info.get("module")
                if module_path and module_path in sys.modules:
                    module = sys.modules[module_path]
                    
                    # Check for common dependencies
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if hasattr(attr, '__module__') and attr.__module__:
                            if 'src.tools' in attr.__module__ and attr.__module__ != module_path:
                                dep_tool = attr.__module__.split('.')[-1]
                                if dep_tool not in tool_deps:
                                    tool_deps.append(dep_tool)
            except Exception as e:
                self.logger.warning(f"Could not analyze dependencies for {tool_name}: {e}")
            
            dependencies[tool_name] = tool_deps
        
        return dependencies
