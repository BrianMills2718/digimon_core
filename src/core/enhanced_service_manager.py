"""Enhanced Service Manager with Dependency Injection

Modernized service manager that uses the unified service interface
and dependency injection framework for improved maintainability,
testability, and configuration management.
"""

from typing import Optional, Dict, Any, Type, TypeVar
import threading
from .dependency_injection import get_container, register_service, resolve_service, cleanup_services
from .unified_service_interface import CoreService, ServiceResponse, create_service_response
from .config_manager import get_config
from .logging_config import get_logger

logger = get_logger("core.enhanced_service_manager")

T = TypeVar('T')


class EnhancedServiceManager:
    """Enhanced service manager with dependency injection and unified interfaces
    
    Provides centralized service management with:
    - Dependency injection container
    - Unified service interfaces
    - Configuration management
    - Health monitoring
    - Lifecycle management
    """
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager or get_config()
        self.logger = get_logger("core.enhanced_service_manager")
        self.container = get_container()
        self._lock = threading.RLock()
        self._initialized = False
        
    def initialize(self) -> bool:
        """Initialize all services with dependency injection
        
        Returns:
            True if initialization successful, False otherwise
        """
        if self._initialized:
            return True
            
        with self._lock:
            if self._initialized:
                return True
                
            try:
                # Register all core services
                self._register_core_services()
                
                # Initialize services with configuration
                self._initialize_services()
                
                self._initialized = True
                self.logger.info("Enhanced service manager initialized successfully")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to initialize service manager: {e}")
                return False
                
    def _register_core_services(self):
        """Register all core services with the dependency injection container"""
        
        # Identity Service
        try:
            from .identity_service import IdentityService
            config = {
                'use_embeddings': self.config_manager.entity_processing.embedding_batch_size > 0,
                'similarity_threshold': self.config_manager.entity_processing.confidence_threshold,
                'persistence_enabled': True
            }
            register_service(IdentityService, IdentityService, singleton=True, config=config)
            self.logger.info("Registered IdentityService")
        except ImportError as e:
            self.logger.warning(f"IdentityService not available: {e}")
            
        # Provenance Service
        try:
            from .provenance_service import ProvenanceService
            config = {
                'enable_lineage_tracking': True,
                'max_lineage_depth': 10
            }
            register_service(ProvenanceService, ProvenanceService, singleton=True, config=config)
            self.logger.info("Registered ProvenanceService")
        except ImportError as e:
            self.logger.warning(f"ProvenanceService not available: {e}")
            
        # Quality Service
        try:
            from .quality_service import QualityService
            config = {
                'confidence_threshold': self.config_manager.entity_processing.confidence_threshold,
                'quality_metrics_enabled': True
            }
            register_service(QualityService, QualityService, singleton=True, config=config)
            self.logger.info("Registered QualityService")
        except ImportError as e:
            self.logger.warning(f"QualityService not available: {e}")
            
        # Workflow State Service
        try:
            from .workflow_state_service import WorkflowStateService
            config = {
                'checkpoint_enabled': True,
                'storage_path': self.config_manager.workflow.storage_dir
            }
            register_service(WorkflowStateService, WorkflowStateService, singleton=True, config=config)
            self.logger.info("Registered WorkflowStateService")
        except ImportError as e:
            self.logger.warning(f"WorkflowStateService not available: {e}")
            
    def _initialize_services(self):
        """Initialize all registered services"""
        health_status = self.container.health_check()
        
        for service_name, is_healthy in health_status.items():
            if is_healthy:
                self.logger.info(f"Service {service_name} initialized and healthy")
            else:
                self.logger.warning(f"Service {service_name} initialization failed or unhealthy")
                
    def get_service(self, service_type: Type[T]) -> Optional[T]:
        """Get a service instance by type
        
        Args:
            service_type: Type of service to retrieve
            
        Returns:
            Service instance or None if not available
        """
        try:
            if not self._initialized:
                self.initialize()
                
            return resolve_service(service_type)
        except Exception as e:
            self.logger.error(f"Failed to resolve service {service_type.__name__}: {e}")
            return None
            
    def get_identity_service(self):
        """Get Identity Service instance"""
        try:
            from .identity_service import IdentityService
            return self.get_service(IdentityService)
        except ImportError:
            self.logger.warning("IdentityService not available")
            return None
            
    def get_provenance_service(self):
        """Get Provenance Service instance"""
        try:
            from .provenance_service import ProvenanceService
            return self.get_service(ProvenanceService)
        except ImportError:
            self.logger.warning("ProvenanceService not available")
            return None
            
    def get_quality_service(self):
        """Get Quality Service instance"""
        try:
            from .quality_service import QualityService
            return self.get_service(QualityService)
        except ImportError:
            self.logger.warning("QualityService not available")
            return None
            
    def get_workflow_state_service(self):
        """Get Workflow State Service instance"""
        try:
            from .workflow_state_service import WorkflowStateService
            return self.get_service(WorkflowStateService)
        except ImportError:
            self.logger.warning("WorkflowStateService not available")
            return None
            
    def get_neo4j_driver(self, uri: str = None, user: str = None, password: str = None):
        """Get Neo4j driver with connection pooling
        
        Args:
            uri: Neo4j URI (optional, uses config if not provided)
            user: Neo4j username (optional, uses config if not provided)
            password: Neo4j password (optional, uses config if not provided)
            
        Returns:
            Neo4j driver instance or None if connection fails
        """
        try:
            from neo4j import GraphDatabase
            
            # Use provided parameters or fall back to configuration
            neo4j_config = self.config_manager.neo4j
            uri = uri or neo4j_config.uri
            user = user or neo4j_config.user  
            password = password or neo4j_config.password
            
            driver = GraphDatabase.driver(
                uri,
                auth=(user, password),
                max_connection_pool_size=neo4j_config.max_connection_pool_size,
                connection_acquisition_timeout=neo4j_config.connection_acquisition_timeout,
                keep_alive=neo4j_config.keep_alive
            )
            
            # Test connection
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
                
            self.logger.info(f"Neo4j connection established to {uri}")
            return driver
            
        except Exception as e:
            self.logger.warning(f"Neo4j connection failed: {e}")
            return None
            
    def health_check(self) -> Dict[str, bool]:
        """Check health of all managed services
        
        Returns:
            Dictionary mapping service names to health status
        """
        if not self._initialized:
            return {"service_manager": False, "error": "Not initialized"}
            
        try:
            health_status = self.container.health_check()
            health_status["service_manager"] = True
            return health_status
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {"service_manager": False, "error": str(e)}
            
    def get_service_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all services
        
        Returns:
            Dictionary with service metrics
        """
        metrics = {}
        
        try:
            # Get health status
            health_status = self.health_check()
            metrics["health_status"] = health_status
            
            # Get individual service metrics
            for service_name in health_status:
                if service_name != "service_manager" and health_status[service_name]:
                    try:
                        # Get service instance and metrics if available
                        service_class_name = service_name.replace("_", "").title()
                        if hasattr(self, f"get_{service_name}"):
                            service = getattr(self, f"get_{service_name}")()
                            if service and hasattr(service, 'get_metrics'):
                                metrics[service_name] = service.get_metrics()
                    except Exception as e:
                        self.logger.warning(f"Failed to get metrics for {service_name}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Failed to collect service metrics: {e}")
            metrics["error"] = str(e)
            
        return metrics
        
    def reconfigure_service(self, service_type: Type[T], new_config: Dict[str, Any]) -> bool:
        """Reconfigure a service with new configuration
        
        Args:
            service_type: Type of service to reconfigure
            new_config: New configuration dictionary
            
        Returns:
            True if reconfiguration successful, False otherwise
        """
        try:
            # Get existing service
            service = self.get_service(service_type)
            if not service:
                self.logger.error(f"Service {service_type.__name__} not found for reconfiguration")
                return False
                
            # Reinitialize with new configuration
            if hasattr(service, 'initialize'):
                success = service.initialize(new_config)
                if success:
                    self.logger.info(f"Service {service_type.__name__} reconfigured successfully")
                else:
                    self.logger.error(f"Failed to reconfigure service {service_type.__name__}")
                return success
            else:
                self.logger.warning(f"Service {service_type.__name__} does not support reconfiguration")
                return False
                
        except Exception as e:
            self.logger.error(f"Error reconfiguring service {service_type.__name__}: {e}")
            return False
            
    def shutdown(self):
        """Shutdown all services and clean up resources"""
        try:
            self.logger.info("Shutting down enhanced service manager")
            cleanup_services()
            self._initialized = False
            self.logger.info("Enhanced service manager shutdown complete")
        except Exception as e:
            self.logger.error(f"Error during service manager shutdown: {e}")


# Global instance
_enhanced_service_manager = None
_manager_lock = threading.Lock()


def get_enhanced_service_manager() -> EnhancedServiceManager:
    """Get global enhanced service manager instance
    
    Returns:
        Global EnhancedServiceManager instance
    """
    global _enhanced_service_manager
    if _enhanced_service_manager is None:
        with _manager_lock:
            if _enhanced_service_manager is None:
                _enhanced_service_manager = EnhancedServiceManager()
                # Auto-initialize on first access
                _enhanced_service_manager.initialize()
    return _enhanced_service_manager


# Backward compatibility with existing service manager interface
def get_service_manager():
    """Backward compatibility wrapper for existing code
    
    Returns:
        Enhanced service manager with compatibility methods
    """
    return get_enhanced_service_manager()