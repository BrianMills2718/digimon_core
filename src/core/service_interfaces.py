"""
Service Interfaces for KGAS Dependency Injection

Defines focused interfaces that follow Interface Segregation Principle
and support proper dependency injection patterns.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Protocol, runtime_checkable
from enum import Enum


class ServiceStatus(Enum):
    """Service status enumeration"""
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@runtime_checkable
class ServiceLifecycle(Protocol):
    """Interface for service lifecycle management"""
    
    async def startup(self) -> None:
        """Initialize service and establish connections"""
        ...
    
    async def shutdown(self) -> None:
        """Cleanup resources and close connections"""
        ...
    
    def get_status(self) -> ServiceStatus:
        """Get current service status"""
        ...


@runtime_checkable
class HealthCheckable(Protocol):
    """Interface for services that support health checking"""
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health and return status information"""
        ...
    
    def is_healthy(self) -> bool:
        """Quick health status check"""
        ...


@runtime_checkable
class Configurable(Protocol):
    """Interface for services that accept configuration"""
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the service with provided settings"""
        ...
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current service configuration"""
        ...


@runtime_checkable
class ServiceRegistrar(Protocol):
    """Interface for service registration functionality"""
    
    def register_service(self, name: str, service_class: type, **kwargs) -> None:
        """Register a service with the container"""
        ...
    
    def unregister_service(self, name: str) -> None:
        """Unregister a service from the container"""
        ...
    
    def is_registered(self, name: str) -> bool:
        """Check if a service is registered"""
        ...
    
    def get_registered_services(self) -> List[str]:
        """Get list of all registered service names"""
        ...


@runtime_checkable
class DependencyResolver(Protocol):
    """Interface for dependency resolution functionality"""
    
    def resolve_dependencies(self, service_name: str) -> List[str]:
        """Resolve dependencies for a service in correct order"""
        ...
    
    def check_circular_dependencies(self, service_name: str, dependencies: List[str]) -> bool:
        """Check for circular dependencies"""
        ...
    
    def get_dependency_order(self) -> List[str]:
        """Get services in dependency resolution order"""
        ...


@runtime_checkable
class LifecycleManager(Protocol):
    """Interface for service lifecycle management"""
    
    async def start_service(self, service_name: str) -> None:
        """Start a specific service"""
        ...
    
    async def stop_service(self, service_name: str) -> None:
        """Stop a specific service"""
        ...
    
    async def start_all_services(self) -> None:
        """Start all registered services in dependency order"""
        ...
    
    async def stop_all_services(self) -> None:
        """Stop all services in reverse dependency order"""
        ...
    
    def get_service_status(self, service_name: str) -> ServiceStatus:
        """Get status of a specific service"""
        ...


@runtime_checkable
class HealthMonitor(Protocol):
    """Interface for health monitoring functionality"""
    
    async def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check health of a specific service"""
        ...
    
    async def check_all_services_health(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all services"""
        ...
    
    def get_unhealthy_services(self) -> List[str]:
        """Get list of unhealthy service names"""
        ...


@runtime_checkable
class ServiceFactory(Protocol):
    """Interface for service instance creation"""
    
    def create_service(self, service_name: str, service_class: type, 
                      dependencies: Dict[str, Any], config: Dict[str, Any]) -> Any:
        """Create a service instance with dependencies and configuration"""
        ...
    
    def supports_service_type(self, service_class: type) -> bool:
        """Check if factory can create instances of this service type"""
        ...


class BaseService(ABC):
    """Base service implementation providing common functionality"""
    
    def __init__(self, name: str):
        self.name = name
        self._status = ServiceStatus.CREATED
        self._config: Dict[str, Any] = {}
        self._startup_time: Optional[float] = None
        self._shutdown_time: Optional[float] = None
    
    @abstractmethod
    async def startup(self) -> None:
        """Service-specific startup logic"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Service-specific shutdown logic"""
        pass
    
    def get_status(self) -> ServiceStatus:
        """Get current service status"""
        return self._status
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the service"""
        self._config.update(config)
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self._config.copy()
    
    async def health_check(self) -> Dict[str, Any]:
        """Default health check implementation"""
        return {
            "status": "healthy" if self._status == ServiceStatus.RUNNING else "unhealthy",
            "service": self.name,
            "uptime": self._get_uptime(),
            "configuration_loaded": bool(self._config)
        }
    
    def is_healthy(self) -> bool:
        """Quick health check"""
        return self._status == ServiceStatus.RUNNING
    
    def _get_uptime(self) -> Optional[float]:
        """Get service uptime in seconds"""
        if self._startup_time is not None:
            return asyncio.get_event_loop().time() - self._startup_time
        return None
    
    def _set_status(self, status: ServiceStatus) -> None:
        """Set service status with timestamp tracking"""
        self._status = status
        if status == ServiceStatus.RUNNING:
            self._startup_time = asyncio.get_event_loop().time()
        elif status == ServiceStatus.STOPPED:
            self._shutdown_time = asyncio.get_event_loop().time()


class ServiceRegistrationError(Exception):
    """Exception raised for service registration issues"""
    pass


class DependencyResolutionError(Exception):
    """Exception raised for dependency resolution issues"""
    pass


class ServiceLifecycleError(Exception):
    """Exception raised for service lifecycle issues"""
    pass


class HealthCheckError(Exception):
    """Exception raised for health check issues"""
    pass