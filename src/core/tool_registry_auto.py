"""Tool Auto-Registration System - KGAS Tool Contract Integration Phase

Implements automatic discovery and registration of all unified tools to enable
agent orchestration and systematic tool validation.

This system scans src/tools/ for *_unified.py files and registers them with
the global tool registry after validating interface compliance.
"""

import os
import sys
import importlib
import inspect
import logging
from pathlib import Path
from typing import Dict, List, Any, Type, Optional, Tuple
from dataclasses import dataclass

from .tool_contract import KGASTool, get_tool_registry, ToolRegistry
from .confidence_score import ConfidenceScore
from ..tools.base_classes.tool_protocol import UnifiedTool
from ..tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class BaseToolAdapter(KGASTool):
    """Adapter to make BaseTool compatible with KGASTool interface."""
    
    def __init__(self, base_tool_instance):
        """Initialize adapter with BaseTool instance."""
        self.base_tool = base_tool_instance
        self.tool_id = getattr(base_tool_instance, 'tool_id', 'UNKNOWN')
        self.tool_name = getattr(base_tool_instance, 'tool_name', 'Unknown Tool')
        super().__init__(self.tool_id, self.tool_name)
    
    def execute(self, request):
        """Execute via BaseTool instance."""
        return self.base_tool.execute(request)
    
    def get_theory_compatibility(self):
        """Get theory compatibility - BaseTool doesn't have this, return empty."""
        return []
    
    def get_input_schema(self):
        """Get input schema from contract if available."""
        if hasattr(self.base_tool, 'get_contract'):
            contract = self.base_tool.get_contract()
            return getattr(contract, 'input_schema', {})
        return {}
    
    def get_output_schema(self):
        """Get output schema from contract if available."""
        if hasattr(self.base_tool, 'get_contract'):
            contract = self.base_tool.get_contract()
            return getattr(contract, 'output_schema', {})
        return {}
    
    def validate_input(self, input_data):
        """Validate input via BaseTool."""
        return self.base_tool.validate_input(input_data)


@dataclass
class ToolDiscoveryResult:
    """Result of tool discovery and registration process."""
    discovered_files: List[str]
    valid_tools: List[str]
    registered_tools: List[str]
    failed_tools: List[Tuple[str, str]]  # (tool_name, error_message)
    interface_violations: List[Tuple[str, List[str]]]  # (tool_name, violations)


class ToolAutoRegistry:
    """Auto-discovery and registration system for KGAS tools."""
    
    def __init__(self, base_path: Optional[str] = None):
        """Initialize auto-registry system.
        
        Args:
            base_path: Base path to search for tools. Defaults to src/tools/
        """
        if base_path is None:
            # Get path relative to this file
            current_dir = Path(__file__).parent
            base_path = current_dir.parent / "tools"
        
        self.base_path = Path(base_path)
        self.tool_registry = get_tool_registry()
        self.required_methods = ['execute', 'validate_input', 'health_check', 'get_status']
    
    def discover_unified_tools(self) -> List[Path]:
        """Scan src/tools/ for *_unified.py files and return tool file paths.
        
        Returns:
            List of Path objects for unified tool files
        """
        unified_files = []
        
        try:
            # Recursively search for *_unified.py files
            for unified_file in self.base_path.rglob("*_unified.py"):
                # Skip __pycache__ and other non-tool files
                if "__pycache__" not in str(unified_file):
                    unified_files.append(unified_file)
                    logger.debug(f"Discovered unified tool file: {unified_file}")
            
            logger.info(f"Discovered {len(unified_files)} unified tool files")
            return unified_files
            
        except Exception as e:
            logger.error(f"Failed to discover unified tools: {e}")
            return []
    
    def extract_tool_classes(self, file_path: Path) -> List[Type]:
        """Extract tool classes from a Python file.
        
        Args:
            file_path: Path to Python file to examine
            
        Returns:
            List of tool class types found in the file
        """
        tool_classes = []
        
        try:
            # Convert file path to module name
            relative_path = file_path.relative_to(self.base_path.parent.parent)
            module_name = str(relative_path).replace(os.sep, '.').replace('.py', '')
            
            # Import the module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                logger.warning(f"Could not create module spec for {file_path}")
                return []
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find classes that inherit from KGASTool, UnifiedTool, or BaseTool
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, (KGASTool, BaseTool)) or 
                    (hasattr(obj, '__bases__') and any(
                        base.__name__ in ['UnifiedTool', 'BaseKGASTool', 'TheoryAwareKGASTool', 'BaseTool'] 
                        for base in obj.__bases__
                    ))):
                    # Skip abstract base classes
                    if not inspect.isabstract(obj) and obj.__name__ not in ['KGASTool', 'BaseTool']:
                        tool_classes.append(obj)
                        logger.debug(f"Found tool class: {name} in {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to extract tool classes from {file_path}: {e}")
            return []
        
        return tool_classes
    
    def validate_tool_contract(self, tool_class: Type) -> Tuple[bool, List[str]]:
        """Verify tool implements required interface contract.
        
        Args:
            tool_class: Tool class to validate
            
        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations = []
        
        try:
            # Check required methods exist and are callable
            for method_name in self.required_methods:
                if not hasattr(tool_class, method_name):
                    violations.append(f"Missing required method: {method_name}")
                elif not callable(getattr(tool_class, method_name)):
                    violations.append(f"Method {method_name} is not callable")
            
            # Skip instantiation during validation - just check method signatures
            # We'll do real instantiation later in create_tool_instance
            
            # Skip attribute checking during validation - attributes are set in __init__
            
        except Exception as e:
            violations.append(f"Contract validation failed: {str(e)}")
        
        is_valid = len(violations) == 0
        return is_valid, violations
    
    def create_tool_instance(self, tool_class: Type) -> Optional[KGASTool]:
        """Create tool instance with proper initialization.
        
        Args:
            tool_class: Tool class to instantiate
            
        Returns:
            Tool instance or None if creation failed
        """
        try:
            # Check if this is a BaseTool (needs ServiceManager)
            if issubclass(tool_class, BaseTool):
                # BaseTool expects ServiceManager
                from ..core.service_manager import ServiceManager
                service_manager = ServiceManager()
                base_tool_instance = tool_class(service_manager)
                # Wrap in adapter for KGASTool compatibility
                return BaseToolAdapter(base_tool_instance)
            
            # Determine how to instantiate the tool for KGASTool
            if hasattr(tool_class, '__init__'):
                sig = inspect.signature(tool_class.__init__)
                params = list(sig.parameters.keys())[1:]  # Skip 'self'
                
                if len(params) == 0:
                    # No parameters required
                    return tool_class()
                elif len(params) >= 2:
                    # Assume first two are tool_id and tool_name
                    class_name = tool_class.__name__
                    
                    # Generate tool_id from class name
                    tool_id = class_name.upper()
                    if 'unified' in class_name.lower():
                        tool_id = tool_id.replace('UNIFIED', '').replace('_UNIFIED', '')
                    if tool_id.endswith('TOOL'):
                        tool_id = tool_id[:-4]
                    
                    # Generate tool_name from class name
                    tool_name = class_name.replace('Unified', '').replace('Tool', '')
                    tool_name = ' '.join(word.capitalize() for word in tool_name.split('_') if word)
                    
                    return tool_class(tool_id, tool_name)
                else:
                    # Single parameter - try with ServiceManager for compatibility
                    from ..core.service_manager import ServiceManager
                    service_manager = ServiceManager()
                    return tool_class(service_manager)
            else:
                return tool_class()
                
        except Exception as e:
            logger.error(f"Failed to create instance of {tool_class.__name__}: {e}")
            return None
    
    def register_tool_instance(self, tool_instance: KGASTool) -> bool:
        """Register tool instance with the global registry.
        
        Args:
            tool_instance: Tool instance to register
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            self.tool_registry.register_tool(tool_instance)
            logger.info(f"Successfully registered tool: {tool_instance.tool_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register tool {tool_instance.tool_id}: {e}")
            return False
    
    def auto_register_all_tools(self) -> ToolDiscoveryResult:
        """Auto-discover, validate, and register all unified tools.
        
        Returns:
            ToolDiscoveryResult with complete registration results
        """
        logger.info("Starting auto-registration of all unified tools")
        
        result = ToolDiscoveryResult(
            discovered_files=[],
            valid_tools=[],
            registered_tools=[],
            failed_tools=[],
            interface_violations=[]
        )
        
        try:
            # Step 1: Discover all unified tool files
            unified_files = self.discover_unified_tools()
            result.discovered_files = [str(f) for f in unified_files]
            
            # Step 2: Extract and validate tool classes from each file
            for file_path in unified_files:
                try:
                    tool_classes = self.extract_tool_classes(file_path)
                    
                    for tool_class in tool_classes:
                        class_name = tool_class.__name__
                        
                        # Step 3: Validate contract compliance
                        is_valid, violations = self.validate_tool_contract(tool_class)
                        
                        if not is_valid:
                            result.interface_violations.append((class_name, violations))
                            logger.warning(f"Tool {class_name} failed contract validation: {violations}")
                            continue
                        
                        result.valid_tools.append(class_name)
                        
                        # Step 4: Create and register tool instance
                        tool_instance = self.create_tool_instance(tool_class)
                        if tool_instance is None:
                            result.failed_tools.append((class_name, "Failed to create tool instance"))
                            continue
                        
                        # Step 5: Register with global registry
                        if self.register_tool_instance(tool_instance):
                            result.registered_tools.append(tool_instance.tool_id)
                        else:
                            result.failed_tools.append((class_name, "Failed to register tool instance"))
                
                except Exception as e:
                    logger.error(f"Failed to process file {file_path}: {e}")
                    result.failed_tools.append((str(file_path), str(e)))
            
            # Log summary
            logger.info(f"Auto-registration complete: {len(result.registered_tools)} tools registered")
            logger.info(f"Discovery summary: {len(result.discovered_files)} files, "
                       f"{len(result.valid_tools)} valid tools, "
                       f"{len(result.failed_tools)} failures, "
                       f"{len(result.interface_violations)} violations")
            
        except Exception as e:
            logger.error(f"Auto-registration failed: {e}")
            result.failed_tools.append(("AUTO_REGISTRATION", str(e)))
        
        return result
    
    def get_tool(self, tool_id: str):
        """Get a registered tool by ID.
        
        Args:
            tool_id: The tool ID to retrieve
            
        Returns:
            The tool instance or None if not found
        """
        # Try to get from global registry
        try:
            from src.core.tool_contract import get_tool_registry
            registry = get_tool_registry()
            tool = registry.get_tool(tool_id)
            if tool:
                return tool
        except Exception as e:
            logger.debug(f"Could not get tool from global registry: {e}")
        
        return None


def auto_register_all_tools() -> ToolDiscoveryResult:
    """Convenience function to auto-register all tools.
    
    Returns:
        ToolDiscoveryResult with registration results
    """
    auto_registry = ToolAutoRegistry()
    return auto_registry.auto_register_all_tools()


def get_registered_tool_count() -> int:
    """Get count of currently registered tools.
    
    Returns:
        Number of tools in the registry
    """
    return len(get_tool_registry().list_tools())


def get_tool_discovery_summary() -> Dict[str, Any]:
    """Get summary of tool discovery and registration.
    
    Returns:
        Dictionary with discovery summary information
    """
    auto_registry = ToolAutoRegistry()
    
    # Discovery only (no registration)
    unified_files = auto_registry.discover_unified_tools()
    
    summary = {
        "discovered_files": len(unified_files),
        "registered_tools": get_registered_tool_count(),
        "discovery_files": [str(f) for f in unified_files[:10]]  # First 10 for brevity
    }
    
    return summary


if __name__ == "__main__":
    # Test the auto-registration system
    logging.basicConfig(level=logging.INFO)
    
    print("KGAS Tool Auto-Registration System")
    print("=" * 40)
    
    # Show current state
    print(f"Current registered tools: {get_registered_tool_count()}")
    
    # Run discovery summary
    summary = get_tool_discovery_summary()
    print(f"Discovered unified files: {summary['discovered_files']}")
    
    # Run full auto-registration
    print("\nRunning auto-registration...")
    result = auto_register_all_tools()
    
    print(f"\nRegistration Results:")
    print(f"- Files discovered: {len(result.discovered_files)}")
    print(f"- Valid tools: {len(result.valid_tools)}")
    print(f"- Tools registered: {len(result.registered_tools)}")
    print(f"- Failed tools: {len(result.failed_tools)}")
    print(f"- Interface violations: {len(result.interface_violations)}")
    
    if result.registered_tools:
        print(f"\nRegistered tools: {result.registered_tools}")
    
    if result.failed_tools:
        print(f"\nFailed tools:")
        for tool_name, error in result.failed_tools[:5]:  # Show first 5
            print(f"  - {tool_name}: {error}")
    
    if result.interface_violations:
        print(f"\nInterface violations:")
        for tool_name, violations in result.interface_violations[:3]:  # Show first 3
            print(f"  - {tool_name}: {violations}")