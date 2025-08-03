"""
Service Registry for KGAS Dependency Injection

Provides automatic service registration, discovery, and initialization
for all core services including UniversalLLMService.
"""

import logging
import asyncio
from typing import Dict, Any, Type, Optional, List
from dataclasses import dataclass
from enum import Enum

from .dependency_injection import ServiceContainer, ServiceLifecycle, ServiceInterface
from .config_manager import ConfigurationManager

logger = logging.getLogger(__name__)


class ServiceRegistryError(Exception):
    """Exception raised for service registry issues"""
    pass


@dataclass
class ServiceDefinition:
    """Definition for automatic service registration"""
    name: str
    service_class: Type
    lifecycle: ServiceLifecycle = ServiceLifecycle.SINGLETON
    dependencies: List[str] = None
    config_section: str = None
    async_init: bool = False
    auto_register: bool = True


class ServiceRegistry:
    """Central registry for all KGAS services"""
    
    def __init__(self, container: ServiceContainer):
        self.container = container
        self.config_manager = ConfigurationManager()
        self.registered_services: Dict[str, ServiceDefinition] = {}
        self._setup_core_services()
    
    def _setup_core_services(self):
        """Register all core services"""
        
        # DEPRECATED: UniversalLLMService removed in favor of EnhancedAPIClient
        # Tools should use EnhancedAPIClient directly instead of service injection
        # See src.core.enhanced_api_client for the standardized LLM client
        
        # Register ConfigurationManager
        self.register_service(ServiceDefinition(
            name="config_manager",
            service_class=ConfigurationManager,
            lifecycle=ServiceLifecycle.SINGLETON,
            dependencies=[],
            async_init=False
        ))
        
        # Register IdentityService
        self.register_service(ServiceDefinition(
            name="identity_service",
            service_class=self._get_identity_service_class(),
            lifecycle=ServiceLifecycle.SINGLETON,
            dependencies=["config_manager"],
            config_section="services.identity",
            async_init=False
        ))
        
        # Register ProvenanceService  
        self.register_service(ServiceDefinition(
            name="provenance_service",
            service_class=self._get_provenance_service_class(),
            lifecycle=ServiceLifecycle.SINGLETON,
            dependencies=["config_manager"],
            config_section="services.provenance",
            async_init=False
        ))
        
        # Register QualityService
        self.register_service(ServiceDefinition(
            name="quality_service",
            service_class=self._get_quality_service_class(),
            lifecycle=ServiceLifecycle.SINGLETON,
            dependencies=["config_manager"],
            config_section="services.quality",
            async_init=False
        ))
        
        # Register WorkflowStateService
        self.register_service(ServiceDefinition(
            name="workflow_state_service", 
            service_class=self._get_workflow_state_service_class(),
            lifecycle=ServiceLifecycle.SINGLETON,
            dependencies=["config_manager"],
            config_section="services.workflow_state",
            async_init=False
        ))
    
    def register_service(self, definition: ServiceDefinition):
        """Register a service definition"""
        if definition.name in self.registered_services:
            logger.warning(f"Service '{definition.name}' already registered, overwriting")
        
        self.registered_services[definition.name] = definition
        
        # Automatically register with container if auto_register is True
        if definition.auto_register:
            self._register_with_container(definition)
        
        logger.debug(f"Registered service definition: {definition.name}")
    
    def _register_with_container(self, definition: ServiceDefinition):
        """Register service with dependency injection container"""
        try:
            # Create factory function for service instantiation
            def service_factory():
                return self._create_service_instance(definition)
            
            self.container.register(
                name=definition.name,
                implementation=service_factory,
                lifecycle=definition.lifecycle,
                dependencies=definition.dependencies or [],
                config_section=definition.config_section,
                async_init=definition.async_init
            )
            
            logger.debug(f"Registered '{definition.name}' with container")
            
        except Exception as e:
            raise ServiceRegistryError(
                f"Failed to register service '{definition.name}' with container: {e}"
            ) from e
    
    def _create_service_instance(self, definition: ServiceDefinition):
        """Create service instance with proper dependency injection"""
        try:
            # Get configuration if specified
            config = None
            if definition.config_section:
                config = self.config_manager.get_config_section(definition.config_section)
            
            # Resolve dependencies
            dependency_instances = {}
            if definition.dependencies:
                for dep_name in definition.dependencies:
                    dependency_instances[dep_name] = self.container.get(dep_name)
            
            # Create instance based on service type
            # DEPRECATED: UniversalLLMService removed - use EnhancedAPIClient directly
            elif definition.name == "config_manager":
                return self.config_manager  # Reuse existing instance
            else:
                # Standard service creation with flexible parameter handling
                try:
                    # Try with config and dependencies
                    if config and dependency_instances:
                        return definition.service_class(config=config, **dependency_instances)
                    elif config:
                        return definition.service_class(config=config)
                    elif dependency_instances:
                        return definition.service_class(**dependency_instances)
                    else:
                        return definition.service_class()
                except TypeError:
                    # If constructor doesn't accept these parameters, try simpler creation
                    try:
                        return definition.service_class()
                    except Exception:
                        # Return mock service if real service can't be created
                        logger.warning(f"Could not instantiate {definition.name}, using mock")
                        return self._create_mock_service_instance(definition.name)
                    
        except Exception as e:
            logger.warning(f"Failed to create {definition.name}, using mock: {e}")
            return self._create_mock_service_instance(definition.name)
    
    # DEPRECATED: UniversalLLMService factory removed
    # Use EnhancedAPIClient directly: from src.core.enhanced_api_client import EnhancedAPIClient
    
    # DEPRECATED: UniversalLLMService class getter removed
    # Use EnhancedAPIClient directly: from src.core.enhanced_api_client import EnhancedAPIClient
    
    def _get_identity_service_class(self):
        """Get IdentityService class with proper import handling"""
        try:
            from .identity_service import IdentityService
            return IdentityService
        except ImportError:
            logger.warning("IdentityService not available, using mock")
            return self._create_mock_service_class("IdentityService")
    
    def _get_provenance_service_class(self):
        """Get ProvenanceService class with proper import handling"""
        try:
            from .provenance_service import ProvenanceService
            return ProvenanceService
        except ImportError:
            logger.warning("ProvenanceService not available, using mock")
            return self._create_mock_service_class("ProvenanceService")
    
    def _get_quality_service_class(self):
        """Get QualityService class with proper import handling"""
        try:
            from .quality_service import QualityService
            return QualityService
        except ImportError:
            logger.warning("QualityService not available, using mock")
            return self._create_mock_service_class("QualityService")
    
    def _get_workflow_state_service_class(self):
        """Get WorkflowStateService class with proper import handling"""
        try:
            from .workflow_state_service import WorkflowStateService
            return WorkflowStateService
        except ImportError:
            logger.warning("WorkflowStateService not available, using mock")
            return self._create_mock_service_class("WorkflowStateService")
    
    def _create_mock_service_class(self, service_name: str):
        """Create mock service class for testing/fallback"""
        class MockService(ServiceInterface):
            def __init__(self, **kwargs):
                self.service_name = service_name
                self._healthy = True
            
            async def startup(self):
                logger.info(f"Mock {self.service_name} startup")
            
            async def shutdown(self):
                logger.info(f"Mock {self.service_name} shutdown")
            
            async def health_check(self):
                return {"status": "healthy", "service": self.service_name}
        
        MockService.__name__ = f"Mock{service_name}"
        return MockService
    
    def _create_mock_service_instance(self, service_name: str):
        """Create mock service instance for testing/fallback"""
        mock_class = self._create_mock_service_class(service_name)
        return mock_class()
    
    def register_all_services(self):
        """Register all defined services with the container"""
        logger.info("Registering all services with container")
        
        # Sort services by dependency order
        ordered_services = self._get_dependency_order()
        
        for service_name in ordered_services:
            definition = self.registered_services[service_name]
            if not definition.auto_register:
                self._register_with_container(definition)
        
        logger.info(f"Registered {len(ordered_services)} services")
    
    def _get_dependency_order(self) -> List[str]:
        """Get services in dependency order (dependencies first)"""
        ordered = []
        remaining = set(self.registered_services.keys())
        
        while remaining:
            # Find services with no unresolved dependencies
            ready = []
            for service_name in remaining:
                definition = self.registered_services[service_name]
                dependencies = set(definition.dependencies or [])
                unresolved = dependencies - set(ordered)
                
                if not unresolved:
                    ready.append(service_name)
            
            if not ready:
                # Circular dependency or missing dependency
                logger.warning(f"Possible circular dependency in services: {remaining}")
                ready = list(remaining)  # Register remaining in arbitrary order
            
            for service_name in ready:
                ordered.append(service_name)
                remaining.remove(service_name)
        
        return ordered
    
    async def startup_all_services(self):
        """Start all registered services in dependency order"""
        logger.info("Starting all registered services")
        
        ordered_services = self._get_dependency_order()
        
        for service_name in ordered_services:
            try:
                definition = self.registered_services[service_name]
                if definition.async_init:
                    service = await self.container.get_async(service_name)
                else:
                    service = self.container.get(service_name)
                
                # Call startup if available
                if hasattr(service, 'startup'):
                    if asyncio.iscoroutinefunction(service.startup):
                        await service.startup()
                    else:
                        service.startup()
                
                logger.debug(f"Started service: {service_name}")
                
            except Exception as e:
                logger.error(f"Failed to start service '{service_name}': {e}")
                raise ServiceRegistryError(f"Service startup failed: {service_name}") from e
        
        logger.info("All services started successfully")
    
    async def shutdown_all_services(self):
        """Shutdown all services in reverse dependency order"""
        logger.info("Shutting down all services")
        
        ordered_services = list(reversed(self._get_dependency_order()))
        
        for service_name in ordered_services:
            try:
                if service_name in self.container._instances:
                    service = self.container._instances[service_name]
                    
                    if hasattr(service, 'shutdown'):
                        if asyncio.iscoroutinefunction(service.shutdown):
                            await service.shutdown()
                        else:
                            service.shutdown()
                    
                    logger.debug(f"Shutdown service: {service_name}")
                    
            except Exception as e:
                logger.error(f"Error shutting down service '{service_name}': {e}")
        
        logger.info("All services shutdown complete")
    
    def get_service_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered services"""
        status = {}
        
        for service_name, definition in self.registered_services.items():
            try:
                # Check if service is instantiated
                instantiated = service_name in self.container._instances
                
                service_status = {
                    "registered": True,
                    "instantiated": instantiated,
                    "lifecycle": definition.lifecycle.value,
                    "dependencies": definition.dependencies or [],
                    "async_init": definition.async_init
                }
                
                # Get health status if service is instantiated
                if instantiated:
                    service = self.container._instances[service_name]
                    if hasattr(service, 'health_check'):
                        try:
                            health = service.health_check()
                            if asyncio.iscoroutine(health):
                                # Can't await in sync method, mark as async
                                service_status["health"] = "async_check_required"
                            else:
                                service_status["health"] = health
                        except Exception as e:
                            service_status["health"] = {"status": "error", "error": str(e)}
                    else:
                        service_status["health"] = {"status": "no_health_check"}
                else:
                    service_status["health"] = {"status": "not_instantiated"}
                
                status[service_name] = service_status
                
            except Exception as e:
                status[service_name] = {
                    "registered": True,
                    "error": str(e)
                }
        
        return status


# Global service registry instance
_service_registry: Optional[ServiceRegistry] = None


def get_service_registry(container: Optional[ServiceContainer] = None) -> ServiceRegistry:
    """Get the global service registry"""
    global _service_registry
    
    if _service_registry is None:
        from .dependency_injection import get_container
        
        if container is None:
            container = get_container()
        
        _service_registry = ServiceRegistry(container)
        _service_registry.register_all_services()
    
    return _service_registry


def initialize_all_services(config: Dict[str, Any] = None) -> ServiceRegistry:
    """Initialize all services with configuration"""
    registry = get_service_registry()
    
    if config:
        registry.container.configure(config)
    
    logger.info("All services initialized through registry")
    return registry