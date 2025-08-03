"""
Improved Service Registry

Refactored service registry that eliminates God Object anti-pattern by using
focused components that follow Single Responsibility Principle and SOLID principles.
"""

import asyncio
import threading
import logging
from typing import Dict, Any, List, Optional

from .service_interfaces import (
    ServiceStatus, ServiceRegistrationError, ServiceLifecycleError
)
from .service_components import (
    ServiceRegistrar, DependencyResolver, LifecycleManager,
    HealthMonitor, DefaultServiceFactory
)
from .dependency_injection import ServiceContainer, ServiceLifecycle
from .config_manager import ConfigurationManager

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """
    Minimal service registry that purely delegates to focused components.
    
    This is NOT a God Object - it's a thin facade with zero business logic.
    All actual work is done by the specialized components.
    """
    
    def __init__(self, container: Optional[ServiceContainer] = None, security_manager: Optional['ServiceSecurityManager'] = None):
        # Core dependencies - minimal setup only
        self.container = container or ServiceContainer()
        self.security_manager = security_manager
        
        # Focused components - each handles ONE responsibility
        self.registrar = ServiceRegistrar(self.container, security_manager)
        self.dependency_resolver = DependencyResolver(self.registrar)
        self.lifecycle_manager = LifecycleManager(self.container, self.dependency_resolver, security_manager)
        self.health_monitor = HealthMonitor(self.container, self.lifecycle_manager, security_manager)
        
        # Factory for service creation
        config_manager = ConfigurationManager()
        self.service_factory = DefaultServiceFactory(config_manager)
        
        # NO complex initialization logic here - keep it minimal
    
    # Pure delegation methods - no business logic
    def register_service(self, name: str, service_class: type, **kwargs) -> None:
        """Pure delegation to registrar"""
        return self.registrar.register_service(name, service_class, **kwargs)
    
    def unregister_service(self, name: str) -> None:
        """Pure delegation to registrar"""
        return self.registrar.unregister_service(name)
    
    def is_registered(self, name: str) -> bool:
        """Pure delegation to registrar"""
        return self.registrar.is_registered(name)
    
    def get_registered_services(self) -> List[str]:
        """Pure delegation to registrar"""
        return self.registrar.get_registered_services()
    
    def get_dependency_order(self) -> List[str]:
        """Pure delegation to dependency resolver"""
        return self.dependency_resolver.get_dependency_order()
    
    async def start_service(self, service_name: str, timeout: Optional[float] = None, security_context: Optional['SecurityContext'] = None) -> None:
        """Pure delegation to lifecycle manager"""
        return await self.lifecycle_manager.start_service(service_name, timeout, security_context)
    
    async def stop_service(self, service_name: str, timeout: Optional[float] = None, security_context: Optional['SecurityContext'] = None) -> None:
        """Pure delegation to lifecycle manager"""
        return await self.lifecycle_manager.stop_service(service_name, timeout, security_context)
    
    async def startup_all_services(self, timeout_per_service: Optional[float] = None) -> None:
        """Pure delegation to lifecycle manager"""
        return await self.lifecycle_manager.start_all_services(timeout_per_service)
    
    async def shutdown_all_services(self, timeout_per_service: Optional[float] = None) -> None:
        """Pure delegation to lifecycle manager"""
        return await self.lifecycle_manager.stop_all_services(timeout_per_service)
    
    def get_service_status(self, service_name: str) -> ServiceStatus:
        """Pure delegation to lifecycle manager"""
        return self.lifecycle_manager.get_service_status(service_name)
    
    async def check_service_health(self, service_name: str, security_context: Optional['SecurityContext'] = None) -> Dict[str, Any]:
        """Pure delegation to health monitor"""
        return await self.health_monitor.check_service_health(service_name, True, security_context)
    
    async def check_all_services_health(self) -> Dict[str, Dict[str, Any]]:
        """Pure delegation to health monitor"""
        return await self.health_monitor.check_all_services_health()
    
    def get_unhealthy_services(self) -> List[str]:
        """Pure delegation to health monitor"""
        return self.health_monitor.get_unhealthy_services()


class CoreServiceInitializer:
    """Separate service for core service initialization - follows SRP"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
    
    def setup_core_services(self) -> None:
        """Initialize core services - simple registration only"""
        try:
            logger.info("Setting up core services")
            
            # Simple registration - no complex logic
            self.registry.register_service("config_manager", ConfigurationManager)
            
            # Try to register optional services if available
            self._try_register_optional_services()
            
            logger.info(f"Core services setup complete. Registered {len(self.registry.get_registered_services())} services.")
            
        except Exception as e:
            logger.error(f"Failed to setup core services: {e}")
            raise
    
    def _try_register_optional_services(self) -> None:
        """Try to register optional services if their classes are available"""
        optional_services = [
            # DEPRECATED: ("universal_llm_service", "src.core.universal_llm_service", "UniversalLLMService"),
            # Use EnhancedAPIClient directly instead
            ("identity_service", "src.core.identity_service", "IdentityService"),
            ("provenance_service", "src.core.provenance_service", "ProvenanceService"),
            ("quality_service", "src.core.quality_service", "QualityService"),
            ("workflow_state_service", "src.core.workflow_state_service", "WorkflowStateService")
        ]
        
        for service_name, module_name, class_name in optional_services:
            try:
                import importlib
                module = importlib.import_module(module_name)
                service_class = getattr(module, class_name)
                self.registry.register_service(
                    service_name, 
                    service_class,
                    lifecycle=ServiceLifecycle.SINGLETON,
                    dependencies=["config_manager"] if service_name != "config_manager" else []
                )
                logger.debug(f"Registered optional service: {service_name}")
            except Exception as e:
                logger.debug(f"Could not register optional service {service_name}: {e}")


# Factory function for backward compatibility
def get_improved_service_registry(with_security: bool = False) -> ServiceRegistry:
    """Factory function to get a configured service registry"""
    security_manager = None
    
    if with_security:
        try:
            from .security_authentication import create_secure_service_registry
            registry, auth_provider, security_manager = create_secure_service_registry()
        except ImportError:
            logger.warning("Security authentication not available, creating registry without security")
            registry = ServiceRegistry()
    else:
        registry = ServiceRegistry()
    
    # Initialize core services using the separate initializer
    initializer = CoreServiceInitializer(registry)
    initializer.setup_core_services()
    
    return registry


# For backward compatibility  
ImprovedServiceRegistry = ServiceRegistry
