"""
MCP Server Configuration

Central configuration and initialization for the MCP server.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Import core services and configuration
from src.core.service_manager import get_service_manager
from src.core.config_manager import get_config
from src.core.workflow_state_service import WorkflowStateService
from src.core.orchestration.pipeline_orchestrator import PipelineOrchestrator, PipelineConfig
from src.core.tool_factory import create_unified_workflow_config, Phase, OptimizationLevel

logger = logging.getLogger(__name__)


class MCPServerConfig:
    """Configuration manager for MCP server"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._service_manager = None
        self._config_manager = None
        self._workflow_service = None
        self._orchestrator = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize all MCP server components"""
        try:
            if self._initialized:
                return True
            
            # Initialize service manager and configuration
            self._service_manager = get_service_manager()
            self._config_manager = get_config()
            
            # Initialize workflow service
            workflow_storage = self._get_workflow_storage_dir()
            self._workflow_service = WorkflowStateService(workflow_storage)
            
            # Initialize pipeline orchestrator
            self._orchestrator = self._initialize_orchestrator()
            
            self._initialized = True
            self.logger.info("MCP server configuration initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP server configuration: {e}")
            return False
    
    def _get_workflow_storage_dir(self) -> str:
        """Get workflow storage directory from configuration"""
        try:
            if hasattr(self._config_manager, 'workflow'):
                return self._config_manager.workflow.storage_dir
            else:
                from ..core.standard_config import get_file_path
                default_dir = f"{get_file_path('data_dir')}/workflows"
                self.logger.warning(f"Using default workflow storage directory: {default_dir}")
                return default_dir
        except Exception as e:
            self.logger.error(f"Error getting workflow storage directory: {e}")
            from ..core.standard_config import get_file_path
            return f"{get_file_path('data_dir')}/workflows"
    
    def _initialize_orchestrator(self) -> Optional[PipelineOrchestrator]:
        """Initialize pipeline orchestrator with fallback"""
        try:
            unified_config_dict = create_unified_workflow_config(
                phase=Phase.PHASE1,
                optimization_level=OptimizationLevel.STANDARD
            )
            
            # Convert dictionary to PipelineConfig object
            pipeline_config = PipelineConfig(
                tools=unified_config_dict.get('tools', []),
                optimization_level=OptimizationLevel.STANDARD,
                phase=Phase.PHASE1,
                neo4j_uri=unified_config_dict.get('neo4j_uri'),
                neo4j_user=unified_config_dict.get('neo4j_user'),
                neo4j_password=unified_config_dict.get('neo4j_password'),
                confidence_threshold=unified_config_dict.get('confidence_threshold', 0.7),
                workflow_storage_dir=unified_config_dict.get('workflow_storage_dir')
            )
            
            orchestrator = PipelineOrchestrator(pipeline_config, self._config_manager)
            self.logger.info("Pipeline orchestrator initialized successfully")
            return orchestrator
            
        except Exception as e:
            self.logger.warning(f"Could not initialize full orchestrator: {e}")
            self.logger.info("Operating with limited orchestrator functionality")
            return None
    
    @property
    def service_manager(self):
        """Get service manager instance"""
        if not self._initialized:
            self.initialize()
        return self._service_manager
    
    @property
    def config_manager(self):
        """Get configuration manager instance"""
        if not self._initialized:
            self.initialize()
        return self._config_manager
    
    @property
    def workflow_service(self):
        """Get workflow service instance"""
        if not self._initialized:
            self.initialize()
        return self._workflow_service
    
    @property
    def orchestrator(self):
        """Get pipeline orchestrator instance"""
        if not self._initialized:
            self.initialize()
        return self._orchestrator
    
    @property
    def identity_service(self):
        """Get identity service instance"""
        return self.service_manager.identity_service if self.service_manager else None
    
    @property
    def provenance_service(self):
        """Get provenance service instance"""
        return self.service_manager.provenance_service if self.service_manager else None
    
    @property
    def quality_service(self):
        """Get quality service instance"""
        return self.service_manager.quality_service if self.service_manager else None
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get comprehensive server information"""
        return {
            "server_name": "super-digimon",
            "version": "2.0.0",
            "architecture": "decomposed_components",
            "initialized": self._initialized,
            "components": {
                "service_manager": self._service_manager is not None,
                "config_manager": self._config_manager is not None,
                "workflow_service": self._workflow_service is not None,
                "orchestrator": self._orchestrator is not None
            },
            "services": {
                "identity_service": self.identity_service is not None,
                "provenance_service": self.provenance_service is not None,
                "quality_service": self.quality_service is not None
            },
            "capabilities": [
                "identity_management",
                "provenance_tracking", 
                "quality_assessment",
                "workflow_state_management",
                "pipeline_orchestration"
            ]
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check of all components"""
        health_status = {
            "overall_status": "healthy",
            "timestamp": "",
            "components": {}
        }
        
        try:
            from datetime import datetime
            health_status["timestamp"] = datetime.now().isoformat()
            
            # Check service manager
            if self.service_manager:
                try:
                    service_health = self.service_manager.health_check()
                    health_status["components"]["service_manager"] = {
                        "status": "healthy" if service_health else "unhealthy",
                        "details": service_health
                    }
                except Exception as e:
                    health_status["components"]["service_manager"] = {
                        "status": "error",
                        "error": str(e)
                    }
            else:
                health_status["components"]["service_manager"] = {"status": "not_available"}
            
            # Check individual services
            for service_name in ["identity_service", "provenance_service", "quality_service"]:
                service = getattr(self, service_name, None)
                if service:
                    try:
                        # Basic availability check
                        health_status["components"][service_name] = {"status": "healthy"}
                    except Exception as e:
                        health_status["components"][service_name] = {
                            "status": "error",
                            "error": str(e)
                        }
                else:
                    health_status["components"][service_name] = {"status": "not_available"}
            
            # Check workflow service
            if self.workflow_service:
                health_status["components"]["workflow_service"] = {"status": "healthy"}
            else:
                health_status["components"]["workflow_service"] = {"status": "not_available"}
            
            # Check orchestrator
            if self.orchestrator:
                health_status["components"]["orchestrator"] = {"status": "healthy"}
            else:
                health_status["components"]["orchestrator"] = {"status": "limited_functionality"}
            
            # Determine overall status
            unhealthy_components = [
                name for name, status in health_status["components"].items()
                if status.get("status") in ["unhealthy", "error", "not_available"]
            ]
            
            if len(unhealthy_components) > 2:
                health_status["overall_status"] = "unhealthy"
            elif len(unhealthy_components) > 0:
                health_status["overall_status"] = "degraded"
            
        except Exception as e:
            health_status["overall_status"] = "error"
            health_status["error"] = str(e)
        
        return health_status


# Global configuration instance
_global_config = None


def get_mcp_config() -> MCPServerConfig:
    """Get or create global MCP server configuration"""
    global _global_config
    if _global_config is None:
        _global_config = MCPServerConfig()
        _global_config.initialize()
    return _global_config