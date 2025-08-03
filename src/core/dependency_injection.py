"""
Dependency Injection Container for KGAS

Provides centralized service management with lifecycle control,
configuration injection, and dependency resolution.
"""

import asyncio
import inspect
import logging
from typing import Dict, Any, List, Optional, Type, Union, Callable, Set
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ServiceLifecycle(Enum):
    """Service lifecycle management options"""
    SINGLETON = "singleton"  # One instance shared across application
    TRANSIENT = "transient"  # New instance on each request
    SCOPED = "scoped"       # One instance per scope/request


class DependencyInjectionError(Exception):
    """Exception raised for dependency injection issues"""
    pass


@dataclass
class ServiceRegistration:
    """Registration information for a service"""
    name: str
    implementation: Union[Type, Callable, Any]
    lifecycle: ServiceLifecycle = ServiceLifecycle.SINGLETON
    dependencies: List[str] = field(default_factory=list)
    config_section: Optional[str] = None
    async_init: bool = False
    factory: Optional[Callable] = None
    instance: Optional[Any] = None
    initialized: bool = False


class ServiceInterface:
    """Base interface for all services (concrete class for testing)"""
    
    async def startup(self) -> None:
        """Initialize service and establish connections"""
        pass
    
    async def shutdown(self) -> None:
        """Cleanup resources and close connections"""
        pass
    
    async def health_check(self) -> Any:
        """Check service health and return status"""
        return {"status": "healthy"}


class ServiceContainer:
    """Dependency injection container with lifecycle management"""
    
    def __init__(self):
        self._services: Dict[str, ServiceRegistration] = {}
        self._instances: Dict[str, Any] = {}
        self._resolving: Set[str] = set()  # Track circular dependencies
        self._configuration: Dict[str, Any] = {}
        self._started: bool = False
        self._lock = asyncio.Lock()
    
    def register(self, name: str, implementation: Union[Type, Callable, Any],
                 lifecycle: ServiceLifecycle = ServiceLifecycle.SINGLETON,
                 dependencies: Optional[List[str]] = None,
                 config_section: Optional[str] = None,
                 async_init: bool = False,
                 factory: Optional[Callable] = None) -> 'ServiceContainer':
        """Register a service with the container"""
        if name in self._services:
            logger.warning(f"Service '{name}' already registered, overwriting")
        
        registration = ServiceRegistration(
            name=name,
            implementation=implementation,
            lifecycle=lifecycle,
            dependencies=dependencies or [],
            config_section=config_section,
            async_init=async_init,
            factory=factory
        )
        
        self._services[name] = registration
        logger.debug(f"Registered service '{name}' with lifecycle {lifecycle.value}")
        
        return self
    
    def configure(self, configuration: Dict[str, Any]) -> 'ServiceContainer':
        """Set configuration for the container"""
        self._configuration = configuration
        logger.debug("Container configuration updated")
        return self
    
    def get(self, name: str) -> Any:
        """Get a service instance synchronously"""
        if name not in self._services:
            raise DependencyInjectionError(f"Service '{name}' is not registered")
        
        registration = self._services[name]
        
        # Check for circular dependencies
        if name in self._resolving:
            raise DependencyInjectionError(
                f"Circular dependency detected involving service '{name}'"
            )
        
        # Return existing singleton instance
        if (registration.lifecycle == ServiceLifecycle.SINGLETON and 
            name in self._instances):
            return self._instances[name]
        
        # Create new instance
        try:
            self._resolving.add(name)
            instance = self._create_instance(registration)
            
            # Cache singleton instances
            if registration.lifecycle == ServiceLifecycle.SINGLETON:
                self._instances[name] = instance
                registration.instance = instance
                registration.initialized = True
            
            return instance
            
        finally:
            self._resolving.discard(name)
    
    async def get_async(self, name: str) -> Any:
        """Get a service instance asynchronously"""
        async with self._lock:
            if name not in self._services:
                raise DependencyInjectionError(f"Service '{name}' is not registered")
            
            registration = self._services[name]
            
            # Check for circular dependencies
            if name in self._resolving:
                raise DependencyInjectionError(
                    f"Circular dependency detected involving service '{name}'"
                )
            
            # Return existing singleton instance
            if (registration.lifecycle == ServiceLifecycle.SINGLETON and 
                name in self._instances):
                return self._instances[name]
            
            # Create new instance
            try:
                self._resolving.add(name)
                instance = await self._create_instance_async(registration)
                
                # Cache singleton instances
                if registration.lifecycle == ServiceLifecycle.SINGLETON:
                    self._instances[name] = instance
                    registration.instance = instance
                    registration.initialized = True
                
                return instance
                
            finally:
                self._resolving.discard(name)
    
    def _create_instance(self, registration: ServiceRegistration) -> Any:
        """Create a service instance synchronously"""
        
        # Handle different implementation types
        if inspect.isclass(registration.implementation):
            return self._instantiate_class(registration)
        elif callable(registration.implementation) and not hasattr(registration.implementation, '_mock_name'):
            # Don't call mock objects - they're already instances for testing
            return registration.implementation()
        else:
            # Direct instance (including mocks)
            return registration.implementation
    
    async def _create_instance_async(self, registration: ServiceRegistration) -> Any:
        """Create a service instance asynchronously"""
        
        if inspect.isclass(registration.implementation):
            instance = self._instantiate_class(registration)
        elif callable(registration.implementation) and not hasattr(registration.implementation, '_mock_name'):
            # Don't call mock objects - they're already instances for testing
            instance = registration.implementation()
        else:
            # Direct instance (including mocks)
            instance = registration.implementation
        
        # Handle async initialization
        if registration.async_init and hasattr(instance, 'startup'):
            await instance.startup()
        
        return instance
    
    def _instantiate_class(self, registration: ServiceRegistration) -> Any:
        """Instantiate a class with dependency injection"""
        cls = registration.implementation
        
        # Resolve dependencies
        dependencies = {}
        for dep_name in registration.dependencies:
            dependencies[dep_name] = self.get(dep_name)
        
        # Get configuration if specified
        config = None
        if registration.config_section:
            config = self._configuration.get(registration.config_section, {})
        
        # Inspect constructor for parameter injection
        sig = inspect.signature(cls.__init__)
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Inject by parameter name if it matches a dependency
            if param_name in dependencies:
                kwargs[param_name] = dependencies[param_name]
            elif param_name == 'config' and config:
                kwargs['config'] = config
            elif param_name in self._configuration:
                kwargs[param_name] = self._configuration[param_name]
        
        # Add any remaining dependencies as keyword arguments
        for dep_name, dep_instance in dependencies.items():
            if dep_name not in kwargs:
                kwargs[dep_name] = dep_instance
        
        if config and 'config' not in kwargs:
            kwargs['config'] = config
        
        try:
            return cls(**kwargs)
        except Exception as e:
            raise DependencyInjectionError(
                f"Failed to instantiate service '{registration.name}': {e}"
            ) from e
    
    def startup(self) -> None:
        """Start all registered services synchronously"""
        logger.info("Starting service container")
        
        for name, registration in self._services.items():
            if registration.lifecycle == ServiceLifecycle.SINGLETON:
                try:
                    instance = self.get(name)
                    if hasattr(instance, 'startup') and callable(instance.startup):
                        if asyncio.iscoroutinefunction(instance.startup):
                            logger.warning(
                                f"Service '{name}' has async startup but called synchronously"
                            )
                        else:
                            instance.startup()
                except Exception as e:
                    logger.error(f"Failed to start service '{name}': {e}")
                    raise
        
        self._started = True
        logger.info("Service container started successfully")
    
    async def startup_async(self) -> None:
        """Start all registered services asynchronously"""
        logger.info("Starting service container (async)")
        
        for name, registration in self._services.items():
            if registration.lifecycle == ServiceLifecycle.SINGLETON:
                try:
                    instance = await self.get_async(name)
                    if hasattr(instance, 'startup') and callable(instance.startup):
                        if asyncio.iscoroutinefunction(instance.startup):
                            await instance.startup()
                        else:
                            instance.startup()
                except Exception as e:
                    logger.error(f"Failed to start service '{name}': {e}")
                    raise
        
        self._started = True
        logger.info("Service container started successfully (async)")
    
    def shutdown(self) -> None:
        """Shutdown all services synchronously"""
        logger.info("Shutting down service container")
        
        # Shutdown in reverse order of startup
        service_names = list(self._services.keys())
        for name in reversed(service_names):
            if name in self._instances:
                instance = self._instances[name]
                if hasattr(instance, 'shutdown') and callable(instance.shutdown):
                    try:
                        if asyncio.iscoroutinefunction(instance.shutdown):
                            logger.warning(
                                f"Service '{name}' has async shutdown but called synchronously"
                            )
                        else:
                            instance.shutdown()
                    except Exception as e:
                        logger.error(f"Error shutting down service '{name}': {e}")
        
        self._instances.clear()
        self._started = False
        logger.info("Service container shutdown complete")
    
    async def shutdown_async(self) -> None:
        """Shutdown all services asynchronously"""
        logger.info("Shutting down service container (async)")
        
        # Shutdown in reverse order of startup
        service_names = list(self._services.keys())
        for name in reversed(service_names):
            if name in self._instances:
                instance = self._instances[name]
                if hasattr(instance, 'shutdown') and callable(instance.shutdown):
                    try:
                        if asyncio.iscoroutinefunction(instance.shutdown):
                            await instance.shutdown()
                        else:
                            instance.shutdown()
                    except Exception as e:
                        logger.error(f"Error shutting down service '{name}': {e}")
        
        self._instances.clear()
        self._started = False
        logger.info("Service container shutdown complete (async)")


# Global container instance for application-wide use
_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """Get the global service container"""
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container