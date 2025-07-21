import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from src.core.tool_discovery_service import ToolDiscoveryService
from src.core.tool_registry_service import ToolRegistryService
from src.core.tool_audit_service import ToolAuditService
from src.core.tool_performance_monitor import ToolPerformanceMonitor


# Phase and OptimizationLevel enums for workflow configuration
class Phase(Enum):
    PHASE1 = "phase1"
    PHASE2 = "phase2"
    PHASE3 = "phase3"


class OptimizationLevel(Enum):
    MINIMAL = "minimal"
    STANDARD = "standard"
    PERFORMANCE = "performance"
    COMPREHENSIVE = "comprehensive"


def create_unified_workflow_config(phase: Phase = Phase.PHASE1, 
                                  optimization_level: OptimizationLevel = OptimizationLevel.STANDARD) -> Dict[str, Any]:
    """Create a unified workflow configuration for the specified phase and optimization level."""
    base_config = {
        "phase": phase.value,
        "optimization_level": optimization_level.value,
        "created_at": datetime.now().isoformat(),
        "tools": [],
        "services": {
            "neo4j": True,
            "identity_service": True,
            "quality_service": True,
            "provenance_service": True
        }
    }
    
    # Phase-specific configuration
    if phase == Phase.PHASE1:
        base_config.update({
            "description": "Phase 1: Basic entity extraction and graph construction",
            "tools": [
                "t01_pdf_loader",
                "t15a_text_chunker",
                "t23a_spacy_ner",
                "t27_relationship_extractor",
                "t31_entity_builder",
                "t34_edge_builder",
                "t49_multihop_query",
                "t68_pagerank"
            ],
            "capabilities": {
                "document_processing": True,
                "entity_extraction": True,
                "relationship_extraction": True,
                "graph_construction": True,
                "basic_queries": True
            }
        })
    elif phase == Phase.PHASE2:
        base_config.update({
            "description": "Phase 2: Enhanced processing with ontology awareness",
            "tools": [
                "t23c_ontology_aware_extractor",
                "t31_ontology_graph_builder",
                "async_multi_document_processor"
            ],
            "capabilities": {
                "ontology_aware_extraction": True,
                "enhanced_graph_building": True,
                "multi_document_processing": True,
                "async_processing": True
            }
        })
    elif phase == Phase.PHASE3:
        base_config.update({
            "description": "Phase 3: Advanced multi-document fusion",
            "tools": [
                "t301_multi_document_fusion",
                "basic_multi_document_workflow"
            ],
            "capabilities": {
                "multi_document_fusion": True,
                "cross_document_entity_resolution": True,
                "conflict_resolution": True,
                "advanced_workflows": True
            }
        })
    
    # Optimization level adjustments
    if optimization_level == OptimizationLevel.MINIMAL:
        base_config["performance"] = {
            "batch_size": 5,
            "concurrency": 1,
            "timeout": 30,
            "memory_limit": "1GB"
        }
    elif optimization_level == OptimizationLevel.STANDARD:
        base_config["performance"] = {
            "batch_size": 10,
            "concurrency": 2,
            "timeout": 60,
            "memory_limit": "2GB"
        }
    elif optimization_level == OptimizationLevel.PERFORMANCE:
        base_config["performance"] = {
            "batch_size": 20,
            "concurrency": 4,
            "timeout": 120,
            "memory_limit": "4GB"
        }
    elif optimization_level == OptimizationLevel.COMPREHENSIVE:
        base_config["performance"] = {
            "batch_size": 50,
            "concurrency": 8,
            "timeout": 300,
            "memory_limit": "8GB"
        }
    
    return base_config


class RefactoredToolFactory:
    """
    Refactored ToolFactory that acts as a facade to focused services.
    
    This class provides the same interface as the original ToolFactory
    but delegates responsibilities to specialized services:
    - ToolDiscoveryService: Tool discovery and scanning
    - ToolRegistryService: Tool registration and instantiation
    - ToolAuditService: Tool validation and testing
    - ToolPerformanceMonitor: Performance tracking and caching
    """
    
    def __init__(self, tools_directory: str = "src/tools"):
        """
        Initialize the refactored tool factory with focused services.
        
        Args:
            tools_directory: Base directory containing tool implementations
        """
        self.tools_directory = tools_directory
        self.logger = logging.getLogger(__name__)
        
        # Initialize specialized services
        self.discovery_service = ToolDiscoveryService(tools_directory)
        self.registry_service = ToolRegistryService(self.discovery_service)
        self.audit_service = ToolAuditService(self.registry_service)
        self.performance_monitor = ToolPerformanceMonitor()
        
        self.logger.info("RefactoredToolFactory initialized with specialized services")
    
    # ===================
    # DISCOVERY METHODS
    # ===================
    
    def discover_all_tools(self) -> Dict[str, Any]:
        """
        Discover all tool classes in the tools directory.
        
        Delegates to ToolDiscoveryService for actual discovery logic.
        
        Returns:
            Dict mapping tool names to their metadata and classes
        """
        self.logger.info("Discovering all tools via ToolDiscoveryService")
        discovered_tools = self.discovery_service.discover_all_tools()
        
        # Maintain compatibility with original interface
        self.discovered_tools = discovered_tools
        
        return discovered_tools
    
    def get_discovery_statistics(self) -> Dict[str, Any]:
        """Get statistics about tool discovery."""
        return self.discovery_service.get_discovery_statistics()
    
    # ===================
    # REGISTRY METHODS
    # ===================
    
    def create_all_tools(self) -> Dict[str, Any]:
        """
        Create and return instances of all discovered tools.
        
        Delegates to ToolRegistryService for tool instantiation.
        
        Returns:
            Dict mapping tool names to their instances
        """
        self.logger.info("Creating all tool instances via ToolRegistryService")
        
        tool_instances = {}
        registered_tools = self.registry_service.list_registered_tools()
        
        for tool_name in registered_tools:
            try:
                instance = self.registry_service.get_tool_instance(tool_name)
                if instance:
                    tool_instances[tool_name] = instance
                    self.logger.debug(f"Created instance for tool: {tool_name}")
                else:
                    self.logger.warning(f"Failed to create instance for tool: {tool_name}")
            except Exception as e:
                self.logger.error(f"Error creating instance for {tool_name}: {e}")
                tool_instances[tool_name] = {"error": str(e)}
        
        return tool_instances
    
    def get_tool_by_name(self, tool_name: str) -> Optional[Any]:
        """
        Get actual tool instance by name.
        
        Args:
            tool_name: Name of the tool to retrieve
            
        Returns:
            Tool instance or None if not found
        """
        return self.registry_service.get_tool_instance(tool_name)
    
    def get_registry_statistics(self) -> Dict[str, Any]:
        """Get statistics about tool registration."""
        return self.registry_service.get_registry_statistics()
    
    # ===================
    # AUDIT METHODS
    # ===================
    
    def audit_all_tools(self) -> Dict[str, Any]:
        """
        Audit all tools with environment consistency tracking.
        
        Delegates to ToolAuditService for comprehensive validation.
        
        Returns:
            Dictionary containing complete audit results
        """
        self.logger.info("Starting comprehensive tool audit via ToolAuditService")
        return self.audit_service.audit_all_tools()
    
    async def audit_all_tools_async(self) -> Dict[str, Any]:
        """
        Asynchronous version of comprehensive tool audit.
        
        Returns:
            Dictionary containing complete audit results
        """
        self.logger.info("Starting async comprehensive tool audit via ToolAuditService")
        return await self.audit_service.audit_all_tools_async()
    
    def audit_all_tools_with_consistency_validation(self) -> Dict[str, Any]:
        """
        Audit all tools with mandatory consistency validation.
        
        This method provides enhanced validation with strict consistency checks.
        
        Returns:
            Dictionary containing audit results with consistency metrics
        """
        self.logger.info("Starting audit with mandatory consistency validation")
        
        # Run comprehensive audit
        audit_results = self.audit_service.audit_all_tools()
        
        # Add enhanced consistency validation
        audit_results["enhanced_validation"] = True
        audit_results["validation_timestamp"] = datetime.now().isoformat()
        
        # Calculate enhanced consistency metrics
        consistency_score = self._calculate_enhanced_consistency_score(audit_results)
        audit_results["enhanced_consistency_score"] = consistency_score
        
        return audit_results
    
    def get_audit_history(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """Get audit history for tools."""
        return self.audit_service.get_audit_history(tool_name)
    
    # ===================
    # PERFORMANCE METHODS
    # ===================
    
    def get_success_rate(self, tool_name: Optional[str] = None) -> float:
        """
        Calculate tool success rate.
        
        Args:
            tool_name: Specific tool name, or None for overall rate
            
        Returns:
            Success rate as percentage (0.0 to 100.0)
        """
        if tool_name:
            # Get success rate from performance monitor first, fall back to audit service
            perf_rate = self.performance_monitor.get_success_rate(tool_name)
            if perf_rate > 0:
                return perf_rate
            return self.audit_service.get_success_rate(tool_name)
        else:
            # Calculate overall success rate from audit service
            return self.audit_service.get_success_rate()
    
    def track_tool_performance(self, tool_name: str, execution_time: float, 
                             success: bool = True, **kwargs) -> None:
        """Track performance metrics for a tool execution."""
        self.performance_monitor.track_tool_performance(
            tool_name, execution_time, success=success, **kwargs
        )
    
    def get_performance_summary(self, tool_name: str) -> Dict[str, Any]:
        """Get comprehensive performance summary for a tool."""
        return self.performance_monitor.get_tool_performance_summary(tool_name)
    
    def get_performance_issues(self) -> Dict[str, List[Dict[str, Any]]]:
        """Identify tools with performance issues."""
        return self.performance_monitor.get_performance_issues()
    
    def cache_performance(self, tool_name: str, cache_key: str, data: Any, 
                         ttl_seconds: int = 3600) -> None:
        """Cache performance-related data with TTL."""
        self.performance_monitor.cache_performance_data(tool_name, cache_key, data, ttl_seconds)
    
    def get_cached_data(self, tool_name: str, cache_key: str) -> Optional[Any]:
        """Retrieve cached performance data."""
        return self.performance_monitor.get_cached_data(tool_name, cache_key)
    
    # ===================
    # COMPOSITE METHODS
    # ===================
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status across all services.
        
        Returns:
            Dictionary containing status from all services
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "discovery": {
                "statistics": self.discovery_service.get_discovery_statistics(),
                "discovered_tools": len(self.discovery_service.discovered_tools)
            },
            "registry": {
                "statistics": self.registry_service.get_registry_statistics(),
                "registered_tools": len(self.registry_service.registered_tools)
            },
            "performance": {
                "all_stats": self.performance_monitor.get_all_performance_stats(),
                "issues": self.performance_monitor.get_performance_issues()
            },
            "overall_success_rate": self.get_success_rate()
        }
    
    def refresh_all_services(self, force: bool = False) -> Dict[str, Any]:
        """
        Refresh all services and return updated status.
        
        Args:
            force: If True, forces complete refresh of all services
            
        Returns:
            Dictionary containing refresh results
        """
        self.logger.info(f"Refreshing all services (force={force})")
        
        refresh_results = {
            "timestamp": datetime.now().isoformat(),
            "force_refresh": force
        }
        
        # Refresh discovery
        discovered_tools = self.discovery_service.refresh_discovery(force=force)
        refresh_results["discovery"] = {
            "tools_discovered": len(discovered_tools),
            "status": "completed"
        }
        
        # Refresh registry from discovery
        newly_registered = self.registry_service.refresh_from_discovery(force=force)
        refresh_results["registry"] = {
            "newly_registered": newly_registered,
            "total_registered": len(self.registry_service.registered_tools),
            "status": "completed"
        }
        
        # Clear old performance data if force refresh
        if force:
            self.performance_monitor.clear_performance_data()
            refresh_results["performance"] = {
                "data_cleared": True,
                "status": "reset"
            }
        
        self.logger.info(f"Service refresh completed: {newly_registered} new tools registered")
        return refresh_results
    
    def validate_all_services(self) -> Dict[str, Any]:
        """
        Validate all services are working correctly.
        
        Returns:
            Dictionary containing validation results
        """
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        try:
            # Validate discovery service
            discovery_stats = self.discovery_service.get_discovery_statistics()
            validation_results["services"]["discovery"] = {
                "status": "healthy",
                "tools_discovered": discovery_stats.get("total_tools_discovered", 0)
            }
        except Exception as e:
            validation_results["services"]["discovery"] = {
                "status": "error",
                "error": str(e)
            }
        
        try:
            # Validate registry service
            registry_validation = self.registry_service.validate_all_registrations()
            validation_results["services"]["registry"] = {
                "status": "healthy",
                "valid_tools": registry_validation["valid_tools"],
                "invalid_tools": registry_validation["invalid_tools"]
            }
        except Exception as e:
            validation_results["services"]["registry"] = {
                "status": "error",
                "error": str(e)
            }
        
        try:
            # Validate performance monitor
            all_stats = self.performance_monitor.get_all_performance_stats()
            validation_results["services"]["performance_monitor"] = {
                "status": "healthy",
                "monitored_tools": len(all_stats)
            }
        except Exception as e:
            validation_results["services"]["performance_monitor"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Determine overall health
        service_statuses = [s.get("status") for s in validation_results["services"].values()]
        if all(status == "healthy" for status in service_statuses):
            validation_results["overall_status"] = "healthy"
        elif any(status == "error" for status in service_statuses):
            validation_results["overall_status"] = "degraded"
        else:
            validation_results["overall_status"] = "unknown"
        
        return validation_results
    
    # ===================
    # PRIVATE METHODS
    # ===================
    
    def _calculate_enhanced_consistency_score(self, audit_results: Dict[str, Any]) -> float:
        """
        Calculate enhanced consistency score for audit results.
        
        Args:
            audit_results: Results from comprehensive audit
            
        Returns:
            Consistency score from 0.0 to 100.0
        """
        try:
            total_tools = audit_results.get("total_tools", 0)
            working_tools = audit_results.get("working_tools", 0)
            
            if total_tools == 0:
                return 0.0
            
            # Base score from working tools ratio
            base_score = (working_tools / total_tools) * 100
            
            # Apply consistency penalties
            consistency_metrics = audit_results.get("consistency_metrics", {})
            env_impact = consistency_metrics.get("overall_environment_impact", {})
            
            # Penalize for high environmental impact
            severity = env_impact.get("severity", "low")
            if severity == "high":
                base_score *= 0.8
            elif severity == "medium":
                base_score *= 0.9
            
            return max(0.0, min(100.0, base_score))
            
        except Exception as e:
            self.logger.warning(f"Error calculating consistency score: {e}")
            return 0.0
    
    # ===================
    # BACKWARD COMPATIBILITY
    # ===================
    
    @property
    def discovered_tools(self) -> Dict[str, Any]:
        """Backward compatibility property for discovered tools."""
        return getattr(self, '_discovered_tools', self.discovery_service.discovered_tools)
    
    @discovered_tools.setter
    def discovered_tools(self, value: Dict[str, Any]) -> None:
        """Backward compatibility setter for discovered tools."""
        self._discovered_tools = value


# Backward compatibility alias
ToolFactory = RefactoredToolFactory