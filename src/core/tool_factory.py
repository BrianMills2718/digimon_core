"""
Tool Factory Module

Unified tool discovery, auditing, and instantiation system.
Refactored into modular components for maintainability.
"""

import logging
from typing import Dict, Any, Optional, List

# Import decomposed components
from .tool_management import (
    Phase,
    OptimizationLevel,
    create_unified_workflow_config,
    ToolDiscovery,
    ToolAuditor,
    AsyncToolAuditor,
    EnvironmentMonitor,
    ConsistencyValidator,
    ToolInstantiator
)


class ToolFactory:
    """Unified tool discovery, auditing, and instantiation system"""
    
    def __init__(self, tools_directory: str = "src/tools", max_concurrent: int = 3):
        self.tools_directory = tools_directory
        self.max_concurrent = max_concurrent
        self.logger = logging.getLogger(__name__)
        
        # Initialize decomposed components
        self.tool_discovery = ToolDiscovery(tools_directory)
        self.tool_auditor = ToolAuditor(tools_directory)
        self.async_tool_auditor = AsyncToolAuditor(tools_directory, max_concurrent)
        self.environment_monitor = EnvironmentMonitor()
        self.consistency_validator = ConsistencyValidator()
        self.tool_instantiator = ToolInstantiator(tools_directory)
        
        # Backward compatibility properties
        self.discovered_tools = {}
    
    # Tool Discovery Methods (delegated to ToolDiscovery)
    def discover_all_tools(self) -> Dict[str, Any]:
        """Discover all tool classes in the tools directory"""
        tools = self.tool_discovery.discover_all_tools()
        self.discovered_tools = tools  # Maintain backward compatibility
        return tools
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Get statistics about discovered tools"""
        discovered_tools = self.discover_all_tools()
        stats = self.tool_discovery.get_tool_statistics(discovered_tools)
        
        # Add instantiation statistics
        instantiation_stats = self.tool_instantiator.get_instantiation_statistics()
        stats.update({
            "instantiation_stats": instantiation_stats,
            "max_concurrent": self.max_concurrent
        })
        
        return stats
    
    def get_tool_dependencies(self, discovered_tools: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze dependencies between tools"""
        if discovered_tools is None:
            discovered_tools = self.discover_all_tools()
        return self.tool_discovery.get_tool_dependencies(discovered_tools)
    
    # Tool Auditing Methods (delegated to ToolAuditor)
    def audit_all_tools(self) -> Dict[str, Any]:
        """Audit all tools with environment consistency tracking"""
        return self.tool_auditor.audit_all_tools()
    
    def audit_with_consistency_validation(self) -> Dict[str, Any]:
        """Audit tools with mandatory consistency validation"""
        return self.tool_auditor.audit_with_consistency_validation()
    
    def audit_all_tools_with_consistency_validation(self) -> Dict[str, Any]:
        """Audit tools with mandatory consistency validation (backward compatibility)"""
        return self.tool_auditor.audit_with_consistency_validation()
    
    def get_success_rate(self) -> float:
        """Calculate ACTUAL tool success rate"""
        return self.tool_auditor.get_success_rate()
    
    def generate_audit_summary(self, audit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive audit summary"""
        return self.tool_auditor.generate_audit_summary(audit_results)
    
    # Async Auditing Methods (delegated to AsyncToolAuditor)
    async def audit_all_tools_async(self) -> Dict[str, Any]:
        """Audit all tools asynchronously with concurrency control"""
        return await self.async_tool_auditor.audit_all_tools_async()
    
    async def audit_tools_by_phase(self, phase: str) -> Dict[str, Any]:
        """Audit tools from a specific phase asynchronously"""
        return await self.async_tool_auditor.audit_tools_by_phase(phase)
    
    async def compare_sync_vs_async_performance(self) -> Dict[str, Any]:
        """Compare synchronous vs asynchronous auditing performance"""
        return await self.async_tool_auditor.compare_sync_vs_async_performance()
    
    async def get_audit_statistics(self) -> Dict[str, Any]:
        """Get comprehensive audit statistics"""
        return await self.async_tool_auditor.get_audit_statistics()
    
    def set_concurrency_limit(self, max_concurrent: int) -> None:
        """Set the maximum number of concurrent tool audits"""
        self.max_concurrent = max_concurrent
        self.async_tool_auditor.set_concurrency_limit(max_concurrent)
    
    # Environment Monitoring Methods (delegated to EnvironmentMonitor)
    def capture_test_environment(self) -> Dict[str, Any]:
        """Capture comprehensive test environment for consistency validation"""
        return self.environment_monitor.capture_test_environment()
    
    def _capture_test_environment(self) -> Dict[str, Any]:
        """Backward compatibility method"""
        return self.environment_monitor.capture_test_environment()
    
    def calculate_environment_impact(self, pre_env: Dict, post_env: Dict) -> Dict[str, Any]:
        """Calculate the impact of tool testing on system environment"""
        return self.environment_monitor.calculate_environment_impact(pre_env, post_env)
    
    def _calculate_environment_impact(self, pre_env: Dict, post_env: Dict) -> Dict[str, Any]:
        """Backward compatibility method"""
        return self.environment_monitor.calculate_environment_impact(pre_env, post_env)
    
    def analyze_stability_trends(self, impact_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze stability trends across multiple impact measurements"""
        return self.environment_monitor.analyze_stability_trends(impact_history)
    
    # Consistency Validation Methods (delegated to ConsistencyValidator)
    def calculate_consistency_metrics(self, audit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate consistency metrics from audit results"""
        return self.consistency_validator.calculate_consistency_metrics(audit_results)
    
    def _calculate_consistency_metrics(self, audit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Backward compatibility method"""
        return self.consistency_validator.calculate_consistency_metrics(audit_results)
    
    def validate_tool_consistency(self, tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate consistency across multiple tool execution results"""
        return self.consistency_validator.validate_tool_consistency(tool_results)
    
    def generate_consistency_report(self, consistency_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive consistency report"""
        return self.consistency_validator.generate_consistency_report(consistency_metrics)
    
    # Tool Instantiation Methods (delegated to ToolInstantiator)
    def create_tool_instance(self, tool_name: str, config: Optional[Dict[str, Any]] = None, 
                           force_new: bool = False) -> Dict[str, Any]:
        """Create or retrieve a tool instance with comprehensive error handling"""
        return self.tool_instantiator.create_tool_instance(tool_name, config, force_new)
    
    def get_tool_instance(self, tool_name: str):
        """Get existing tool instance"""
        return self.tool_instantiator.get_tool_instance(tool_name)
    
    def get_tool_by_name(self, tool_name: str):
        """Get actual tool instance by name (backward compatibility)"""
        result = self.tool_instantiator.create_tool_instance(tool_name)
        if result["success"]:
            return result["instance"]
        else:
            if "not found" in result.get("error", "").lower():
                raise ValueError(f"Tool {tool_name} not found")
            else:
                raise RuntimeError(f"Tool {tool_name} has error: {result['error']}")
    
    def create_all_tools(self) -> List[Any]:
        """Create and return instances of all discovered tools (backward compatibility)"""
        if not self.discovered_tools:
            self.discover_all_tools()

        tool_instances = []
        for tool_name in self.discovered_tools:
            try:
                tool_instance = self.get_tool_by_name(tool_name)
                if tool_instance:
                    tool_instances.append(tool_instance)
            except (ValueError, RuntimeError) as e:
                self.logger.warning(f"Could not create instance for tool {tool_name}: {e}")
        
        return tool_instances
    
    def remove_tool_instance(self, tool_name: str) -> bool:
        """Remove tool instance and clean up resources"""
        return self.tool_instantiator.remove_tool_instance(tool_name)
    
    def managed_tool_instance(self, tool_name: str, config: Optional[Dict[str, Any]] = None):
        """Context manager for automatic tool lifecycle management"""
        return self.tool_instantiator.managed_tool_instance(tool_name, config)
    
    def cleanup_all_instances(self) -> Dict[str, Any]:
        """Clean up all tool instances and release resources"""
        return self.tool_instantiator.cleanup_all_instances()
    
    def get_instantiation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive instantiation statistics"""
        return self.tool_instantiator.get_instantiation_statistics()
    
    def validate_tool_instance(self, tool_name: str) -> Dict[str, Any]:
        """Validate a tool instance for proper functionality"""
        return self.tool_instantiator.validate_tool_instance(tool_name)
    
    # Workflow Configuration Methods
    def create_unified_workflow_config(self, phase: Phase = Phase.PHASE1, 
                                      optimization_level: OptimizationLevel = OptimizationLevel.STANDARD) -> Dict[str, Any]:
        """Create a unified workflow configuration for the specified phase and optimization level"""
        return create_unified_workflow_config(phase, optimization_level)
    
    def create_workflow_tools(self, phase: Phase, optimization_level: OptimizationLevel = OptimizationLevel.STANDARD) -> Dict[str, Any]:
        """Create all tools for a specific workflow phase"""
        return self.tool_instantiator.create_workflow_tools(phase, optimization_level)


# Backward compatibility exports
__all__ = [
    "ToolFactory",
    "Phase", 
    "OptimizationLevel",
    "create_unified_workflow_config"
]