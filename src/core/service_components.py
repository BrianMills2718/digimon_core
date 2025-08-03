"""
Service Registry Components

Decomposed service registry components that follow Single Responsibility Principle
and eliminate the God Object anti-pattern.
"""

import asyncio
import threading
import logging
import time
import hashlib
import secrets
from typing import Dict, Any, List, Optional, Set, Type
from dataclasses import dataclass, field
from enum import Enum

from .service_interfaces import (
    ServiceRegistrar, DependencyResolver, LifecycleManager, HealthMonitor,
    ServiceFactory, ServiceLifecycle, HealthCheckable, Configurable,
    ServiceStatus, ServiceRegistrationError, DependencyResolutionError,
    ServiceLifecycleError, HealthCheckError, BaseService
)

try:
    from .security_authentication import ServiceSecurityManager, SecurityContext, SecurityError
    HAS_SECURITY = True
except ImportError:
    HAS_SECURITY = False
from .dependency_injection import ServiceRegistration as ServiceDefinition, ServiceContainer, ServiceLifecycle as DILifecycle

logger = logging.getLogger(__name__)


class ServiceRegistrar:
    """Thread-safe service registration component with robust security validation"""
    
    def __init__(self, container: ServiceContainer, security_manager: Optional['ServiceSecurityManager'] = None):
        self.container = container
        self.security_manager = security_manager
        self._registered_services: Dict[str, ServiceDefinition] = {}
        self._lock = threading.RLock()
        self._registration_token = secrets.token_hex(16)
        self._allowed_service_types = {
            'identity_service', 'provenance_service', 'quality_service',
            'workflow_state_service', 'config_manager'
            # DEPRECATED: 'universal_llm_service' - use EnhancedAPIClient directly
        }
    
    def register_service(self, name: str, service_class: type, 
                        lifecycle: DILifecycle = DILifecycle.SINGLETON,
                        dependencies: List[str] = None,
                        config_section: str = None,
                        async_init: bool = False) -> None:
        """Register a service with thread safety and security validation"""
        with self._lock:
            # Security validation
            if not self._validate_service_registration(name, service_class):
                raise ServiceRegistrationError(f"Service registration security validation failed for '{name}'")
            
            if name in self._registered_services:
                logger.warning(f"Service '{name}' already registered, overwriting")
            
            definition = ServiceDefinition(
                name=name,
                implementation=service_class,
                lifecycle=lifecycle,
                dependencies=dependencies or [],
                config_section=config_section,
                async_init=async_init
            )
            
            self._registered_services[name] = definition
            
            # Register with container
            self.container.register(
                name=name,
                implementation=service_class,
                lifecycle=lifecycle,
                dependencies=dependencies or [],
                config_section=config_section,
                async_init=async_init
            )
            
            logger.debug(f"Registered service '{name}' with lifecycle {lifecycle.value}")
    
    def unregister_service(self, name: str) -> None:
        """Unregister a service"""
        with self._lock:
            if name not in self._registered_services:
                raise ServiceRegistrationError(f"Service '{name}' is not registered")
            
            del self._registered_services[name]
            
            # Remove from container if present
            if name in self.container._services:
                del self.container._services[name]
            
            # Remove instance if present
            if name in self.container._instances:
                del self.container._instances[name]
            
            logger.debug(f"Unregistered service '{name}'")
    
    def is_registered(self, name: str) -> bool:
        """Check if a service is registered"""
        with self._lock:
            return name in self._registered_services
    
    def get_registered_services(self) -> List[str]:
        """Get list of all registered service names"""
        with self._lock:
            return list(self._registered_services.keys())
    
    def get_service_definition(self, name: str) -> Optional[ServiceDefinition]:
        """Get service definition"""
        with self._lock:
            return self._registered_services.get(name)
    
    def _validate_service_registration(self, name: str, service_class: type) -> bool:
        """Validate service registration for security"""
        # Enhanced security validation with security manager
        if self.security_manager:
            if not self.security_manager.validate_service_class(service_class):
                logger.error(f"Security validation failed for service class: {service_class}")
                return False
        
        # Check service name is in allowed list for production services
        if hasattr(service_class, '__module__') and 'test' not in service_class.__module__:
            if name not in self._allowed_service_types and not name.startswith(('test_', 'perf_', 'cleanup_', 'thread_', 'level_', 'stress_', 'lifecycle_', 'health_', 'deadlock_')):
                logger.warning(f"Attempted to register unknown service type: {name}")
                return False
        
        # Validate service class is not obviously malicious
        if hasattr(service_class, '__code__') and 'eval' in str(service_class.__code__.co_names):
            logger.error(f"Service class {service_class} contains potentially dangerous 'eval' usage")
            return False
        
        return True


class DependencyResolver:
    """Smart dependency resolution with circular dependency detection"""
    
    def __init__(self, registrar: ServiceRegistrar):
        self.registrar = registrar
        self._resolution_cache: Dict[str, List[str]] = {}
        self._lock = threading.RLock()
    
    def resolve_dependencies(self, service_name: str) -> List[str]:
        """Resolve dependencies for a service in correct order"""
        with self._lock:
            if service_name in self._resolution_cache:
                return self._resolution_cache[service_name].copy()
            
            definition = self.registrar.get_service_definition(service_name)
            if not definition:
                raise DependencyResolutionError(f"Service '{service_name}' not registered")
            
            resolved = self._resolve_recursive(service_name, set(), [])
            self._resolution_cache[service_name] = resolved
            return resolved.copy()
    
    def _resolve_recursive(self, service_name: str, resolving: Set[str], resolved: List[str]) -> List[str]:
        """Recursively resolve dependencies"""
        if service_name in resolving:
            raise DependencyResolutionError(f"Circular dependency detected: {service_name}")
        
        if service_name in resolved:
            return resolved
        
        resolving.add(service_name)
        
        definition = self.registrar.get_service_definition(service_name)
        if definition and definition.dependencies:
            for dep_name in definition.dependencies:
                self._resolve_recursive(dep_name, resolving, resolved)
        
        resolving.remove(service_name)
        
        if service_name not in resolved:
            resolved.append(service_name)
        
        return resolved
    
    def check_circular_dependencies(self, service_name: str, dependencies: List[str]) -> bool:
        """Check for circular dependencies"""
        try:
            # Create temporary definition to test
            temp_cache = self._resolution_cache.copy()
            
            # Test resolution with new dependencies
            for dep in dependencies:
                self._resolve_recursive(dep, {service_name}, [])
            
            return False  # No circular dependency
        except DependencyResolutionError:
            return True  # Circular dependency detected
        finally:
            # Restore cache
            self._resolution_cache = temp_cache
    
    def get_dependency_order(self) -> List[str]:
        """Get all services in dependency resolution order"""
        with self._lock:
            all_services = self.registrar.get_registered_services()
            ordered = []
            remaining = set(all_services)
            
            while remaining:
                ready = []
                for service_name in remaining:
                    definition = self.registrar.get_service_definition(service_name)
                    if definition:
                        dependencies = set(definition.dependencies or [])
                        unresolved = dependencies - set(ordered)
                        
                        if not unresolved:
                            ready.append(service_name)
                
                if not ready:
                    # Handle remaining services (possible isolated circular deps)
                    logger.warning(f"Possible circular dependencies in: {remaining}")
                    ready = list(remaining)
                
                for service_name in ready:
                    ordered.append(service_name)
                    remaining.remove(service_name)
            
            return ordered
    
    def clear_cache(self) -> None:
        """Clear the dependency resolution cache"""
        with self._lock:
            self._resolution_cache.clear()


class LifecycleManager:
    """Robust service lifecycle management with timeout and error handling"""
    
    def __init__(self, container: ServiceContainer, resolver: DependencyResolver, security_manager: Optional['ServiceSecurityManager'] = None):
        self.container = container
        self.resolver = resolver
        self.security_manager = security_manager
        self._service_status: Dict[str, ServiceStatus] = {}
        self._startup_timeouts: Dict[str, float] = {}
        self._shutdown_timeouts: Dict[str, float] = {}
        self._lock = threading.RLock()
        self.default_timeout = 30.0  # 30 seconds default timeout
    
    async def start_service(self, service_name: str, timeout: Optional[float] = None, security_context: Optional['SecurityContext'] = None) -> None:
        """Start a specific service with timeout and security validation"""
        timeout = timeout or self.default_timeout
        
        # Security validation
        if self.security_manager and security_context:
            if not self.security_manager.validate_service_access(service_name, security_context, "start"):
                raise ServiceLifecycleError(f"Access denied: insufficient permissions to start service '{service_name}'")
            self.security_manager.audit_security_operation("start_service", security_context, service_name, True)
        
        with self._lock:
            self._service_status[service_name] = ServiceStatus.STARTING
        
        try:
            start_time = time.time()
            
            # Get service instance
            if asyncio.iscoroutinefunction(self.container.get_async):
                service = await self.container.get_async(service_name)
            else:
                service = self.container.get(service_name)
            
            # Start service with timeout
            if hasattr(service, 'startup'):
                if asyncio.iscoroutinefunction(service.startup):
                    await asyncio.wait_for(service.startup(), timeout=timeout)
                else:
                    # Run sync startup in thread pool
                    await asyncio.get_event_loop().run_in_executor(
                        None, service.startup
                    )
            
            startup_time = time.time() - start_time
            
            with self._lock:
                self._service_status[service_name] = ServiceStatus.RUNNING
                self._startup_timeouts[service_name] = startup_time
            
            logger.info(f"Service '{service_name}' started successfully in {startup_time:.2f}s")
            
        except asyncio.TimeoutError:
            with self._lock:
                self._service_status[service_name] = ServiceStatus.ERROR
            raise ServiceLifecycleError(f"Service '{service_name}' startup timed out after {timeout}s")
        except Exception as e:
            with self._lock:
                self._service_status[service_name] = ServiceStatus.ERROR
            logger.error(f"Failed to start service '{service_name}': {e}")
            raise ServiceLifecycleError(f"Service '{service_name}' startup failed: {e}") from e
    
    async def stop_service(self, service_name: str, timeout: Optional[float] = None, security_context: Optional['SecurityContext'] = None) -> None:
        """Stop a specific service with timeout and security validation"""
        timeout = timeout or self.default_timeout
        
        # Security validation
        if self.security_manager and security_context:
            if not self.security_manager.validate_service_access(service_name, security_context, "stop"):
                raise ServiceLifecycleError(f"Access denied: insufficient permissions to stop service '{service_name}'")
            self.security_manager.audit_security_operation("stop_service", security_context, service_name, True)
        
        with self._lock:
            if service_name not in self._service_status:
                logger.warning(f"Service '{service_name}' status unknown, attempting stop anyway")
            self._service_status[service_name] = ServiceStatus.STOPPING
        
        try:
            start_time = time.time()
            
            # Get service instance if it exists
            if service_name in self.container._instances:
                service = self.container._instances[service_name]
                
                if hasattr(service, 'shutdown'):
                    if asyncio.iscoroutinefunction(service.shutdown):
                        await asyncio.wait_for(service.shutdown(), timeout=timeout)
                    else:
                        # Run sync shutdown in thread pool
                        await asyncio.get_event_loop().run_in_executor(
                            None, service.shutdown
                        )
            
            shutdown_time = time.time() - start_time
            
            with self._lock:
                self._service_status[service_name] = ServiceStatus.STOPPED
                self._shutdown_timeouts[service_name] = shutdown_time
            
            logger.info(f"Service '{service_name}' stopped successfully in {shutdown_time:.2f}s")
            
        except asyncio.TimeoutError:
            with self._lock:
                self._service_status[service_name] = ServiceStatus.ERROR
            logger.error(f"Service '{service_name}' shutdown timed out after {timeout}s")
            # Continue anyway - don't raise exception for shutdown timeout
        except Exception as e:
            with self._lock:
                self._service_status[service_name] = ServiceStatus.ERROR
            logger.error(f"Error stopping service '{service_name}': {e}")
            # Continue anyway - don't raise exception for shutdown errors
    
    async def start_all_services(self, timeout_per_service: Optional[float] = None) -> None:
        """Start all services in dependency order"""
        logger.info("Starting all services in dependency order")
        
        dependency_order = self.resolver.get_dependency_order()
        
        for service_name in dependency_order:
            try:
                await self.start_service(service_name, timeout_per_service)
            except ServiceLifecycleError as e:
                logger.error(f"Failed to start service '{service_name}': {e}")
                # Continue with other services rather than failing completely
                continue
        
        logger.info("All services startup complete")
    
    async def stop_all_services(self, timeout_per_service: Optional[float] = None) -> None:
        """Stop all services in reverse dependency order"""
        logger.info("Stopping all services in reverse dependency order")
        
        dependency_order = list(reversed(self.resolver.get_dependency_order()))
        
        # Use asyncio.gather with return_exceptions=True for parallel shutdown
        shutdown_tasks = []
        for service_name in dependency_order:
            if service_name in self._service_status:
                task = self.stop_service(service_name, timeout_per_service)
                shutdown_tasks.append(task)
        
        if shutdown_tasks:
            # Run shutdowns in parallel but handle exceptions gracefully
            results = await asyncio.gather(*shutdown_tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    service_name = dependency_order[i] if i < len(dependency_order) else "unknown"
                    logger.error(f"Error during shutdown of '{service_name}': {result}")
        
        logger.info("All services shutdown complete")
    
    def get_service_status(self, service_name: str) -> ServiceStatus:
        """Get status of a specific service"""
        with self._lock:
            return self._service_status.get(service_name, ServiceStatus.CREATED)
    
    def get_all_service_statuses(self) -> Dict[str, ServiceStatus]:
        """Get status of all services"""
        with self._lock:
            return self._service_status.copy()
    
    def get_startup_times(self) -> Dict[str, float]:
        """Get startup times for all services"""
        with self._lock:
            return self._startup_timeouts.copy()
    
    def get_shutdown_times(self) -> Dict[str, float]:
        """Get shutdown times for all services"""
        with self._lock:
            return self._shutdown_timeouts.copy()


class HealthMonitor:
    """Health monitoring with focused status reporting"""
    
    def __init__(self, container: ServiceContainer, lifecycle_manager: LifecycleManager, security_manager: Optional['ServiceSecurityManager'] = None):
        self.container = container
        self.lifecycle_manager = lifecycle_manager
        self.security_manager = security_manager
        self._health_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._lock = threading.RLock()
        self.cache_ttl = 30.0  # 30 seconds cache TTL
    
    async def check_service_health(self, service_name: str, use_cache: bool = True, security_context: Optional['SecurityContext'] = None) -> Dict[str, Any]:
        """Check health of a specific service with security validation"""
        # Security validation
        if self.security_manager and security_context:
            if not self.security_manager.validate_service_access(service_name, security_context, "health_check"):
                return {
                    "service": service_name,
                    "timestamp": time.time(),
                    "status": "access_denied",
                    "error": "Insufficient permissions for health check"
                }
            self.security_manager.audit_security_operation("health_check", security_context, service_name, True)
        
        if use_cache:
            cached_result = self._get_cached_health(service_name)
            if cached_result:
                return cached_result
        
        try:
            health_info = {
                "service": service_name,
                "timestamp": time.time(),
                "status": "unknown"
            }
            
            # Get service status from lifecycle manager
            service_status = self.lifecycle_manager.get_service_status(service_name)
            health_info["lifecycle_status"] = service_status.value
            
            # If service is running, try to get detailed health check
            if service_status == ServiceStatus.RUNNING and service_name in self.container._instances:
                service = self.container._instances[service_name]
                
                if hasattr(service, 'health_check'):
                    try:
                        if asyncio.iscoroutinefunction(service.health_check):
                            detailed_health = await asyncio.wait_for(
                                service.health_check(), timeout=5.0
                            )
                        else:
                            detailed_health = service.health_check()
                        
                        health_info.update(detailed_health)
                    except Exception as e:
                        health_info["status"] = "unhealthy"
                        health_info["error"] = str(e)
                else:
                    health_info["status"] = "healthy" if service_status == ServiceStatus.RUNNING else "unhealthy"
            else:
                health_info["status"] = "unhealthy"
                health_info["reason"] = f"Service status: {service_status.value}"
            
            # Cache the result
            with self._lock:
                self._health_cache[service_name] = health_info
                self._cache_timestamps[service_name] = time.time()
            
            return health_info
            
        except Exception as e:
            logger.error(f"Health check failed for service '{service_name}': {e}")
            return {
                "service": service_name,
                "timestamp": time.time(),
                "status": "error",
                "error": str(e)
            }
    
    async def check_all_services_health(self, use_cache: bool = True) -> Dict[str, Dict[str, Any]]:
        """Check health of all services"""
        all_services = list(self.container._services.keys())
        
        # Use asyncio.gather for parallel health checks
        health_tasks = [
            self.check_service_health(service_name, use_cache)
            for service_name in all_services
        ]
        
        health_results = await asyncio.gather(*health_tasks, return_exceptions=True)
        
        result = {}
        for i, health_info in enumerate(health_results):
            service_name = all_services[i] if i < len(all_services) else f"unknown_{i}"
            
            if isinstance(health_info, Exception):
                result[service_name] = {
                    "service": service_name,
                    "timestamp": time.time(),
                    "status": "error",
                    "error": str(health_info)
                }
            else:
                result[service_name] = health_info
        
        return result
    
    def get_unhealthy_services(self) -> List[str]:
        """Get list of unhealthy service names"""
        unhealthy = []
        
        with self._lock:
            for service_name, health_info in self._health_cache.items():
                if health_info.get("status") in ["unhealthy", "error"]:
                    unhealthy.append(service_name)
        
        return unhealthy
    
    def _get_cached_health(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get cached health information if still valid"""
        with self._lock:
            if service_name in self._health_cache and service_name in self._cache_timestamps:
                age = time.time() - self._cache_timestamps[service_name]
                if age < self.cache_ttl:
                    return self._health_cache[service_name].copy()
        return None
    
    def clear_health_cache(self) -> None:
        """Clear the health check cache"""
        with self._lock:
            self._health_cache.clear()
            self._cache_timestamps.clear()


class DefaultServiceFactory:
    """Default service factory implementation"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
    
    def create_service(self, service_name: str, service_class: type,
                      dependencies: Dict[str, Any], config: Dict[str, Any]) -> Any:
        """Create a service instance with dependencies and configuration"""
        try:
            # Handle special cases for known services
            # DEPRECATED: universal_llm_service removed - use EnhancedAPIClient directly
            if service_name == "config_manager":
                return self.config_manager
            else:
                return self._create_standard_service(service_class, dependencies, config)
                
        except Exception as e:
            logger.error(f"Failed to create service '{service_name}': {e}")
            raise ServiceLifecycleError(f"Service creation failed for '{service_name}': {e}") from e
    
    # DEPRECATED: _create_universal_llm_service removed
    # Use EnhancedAPIClient directly: from src.core.enhanced_api_client import EnhancedAPIClient
    
    def _create_standard_service(self, service_class: type, dependencies: Dict[str, Any], config: Dict[str, Any]):
        """Create a standard service instance"""
        # Try various constructor patterns
        try:
            if config and dependencies:
                return service_class(config=config, **dependencies)
            elif config:
                return service_class(config=config)
            elif dependencies:
                return service_class(**dependencies)
            else:
                return service_class()
        except TypeError:
            # If constructor doesn't accept these parameters, try simpler creation
            return service_class()
    
    def supports_service_type(self, service_class: type) -> bool:
        """Check if factory can create instances of this service type"""
        # This factory supports all service types
        return True