"""Service Interface Protocol for KGAS

This module defines the standardized interface that all core services must implement
to ensure consistency, testability, and maintainability across the system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service operational status"""
    INITIALIZING = "initializing"
    READY = "ready"
    DEGRADED = "degraded"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class ServiceType(Enum):
    """Types of services in KGAS"""
    IDENTITY = "identity"
    PROVENANCE = "provenance"
    QUALITY = "quality"
    WORKFLOW = "workflow"
    STORAGE = "storage"
    CACHE = "cache"
    MONITORING = "monitoring"
    SECURITY = "security"


@dataclass(frozen=True)
class ServiceInfo:
    """Service metadata and capabilities"""
    service_id: str
    name: str
    version: str
    description: str
    service_type: ServiceType
    dependencies: List[str]
    capabilities: List[str]
    configuration: Dict[str, Any]
    health_endpoints: List[str]


@dataclass(frozen=True)
class ServiceHealth:
    """Service health status"""
    service_id: str
    status: ServiceStatus
    healthy: bool
    uptime_seconds: float
    last_check: str
    checks: Dict[str, bool]
    metrics: Dict[str, float]
    errors: List[str]


@dataclass(frozen=True)
class ServiceMetrics:
    """Service performance metrics"""
    service_id: str
    timestamp: str
    request_count: int
    error_count: int
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    active_connections: int
    memory_usage_mb: float
    cpu_usage_percent: float


@dataclass(frozen=True)
class ServiceOperation:
    """Standard service operation result"""
    success: bool
    data: Any
    error: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Dict[str, Any] = None
    duration_ms: float = 0.0


class ServiceProtocol(ABC):
    """Base protocol that all KGAS services must implement
    
    This protocol ensures:
    - Consistent initialization and lifecycle management
    - Standardized health checking and monitoring
    - Uniform error handling and recovery
    - Common configuration management
    - Predictable service discovery
    """
    
    def __init__(self):
        """Initialize service base attributes"""
        self.service_id: str = ""
        self.status: ServiceStatus = ServiceStatus.INITIALIZING
        self._start_time: float = 0.0
        self._error_handlers: Dict[str, Callable] = {}
        self._health_checks: Dict[str, Callable] = {}
    
    @abstractmethod
    def get_service_info(self) -> ServiceInfo:
        """Get service metadata and capabilities
        
        Returns:
            Complete service information including dependencies and capabilities
        """
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> ServiceOperation:
        """Initialize service with configuration
        
        This method should:
        - Validate configuration
        - Initialize internal components
        - Establish connections
        - Register health checks
        - Set status to READY on success
        
        Args:
            config: Service-specific configuration
            
        Returns:
            Operation result indicating success/failure
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> ServiceOperation:
        """Gracefully shutdown service
        
        This method should:
        - Stop accepting new requests
        - Complete in-flight operations
        - Close connections
        - Clean up resources
        - Set status to SHUTDOWN
        
        Returns:
            Operation result indicating success/failure
        """
        pass
    
    @abstractmethod
    def health_check(self) -> ServiceHealth:
        """Perform comprehensive health check
        
        This method should check:
        - Internal component status
        - External dependencies
        - Resource availability
        - Performance thresholds
        
        Returns:
            Detailed health status
        """
        pass
    
    @abstractmethod
    def get_metrics(self) -> ServiceMetrics:
        """Get current service metrics
        
        Returns:
            Current performance metrics
        """
        pass
    
    @abstractmethod
    def validate_dependencies(self) -> ServiceOperation:
        """Validate all service dependencies are available
        
        Returns:
            Operation result with dependency status
        """
        pass
    
    # Common helper methods that can be overridden
    
    def register_health_check(self, name: str, check_func: Callable[[], bool]):
        """Register a health check function
        
        Args:
            name: Health check name
            check_func: Function that returns True if healthy
        """
        self._health_checks[name] = check_func
    
    def register_error_handler(self, error_type: str, handler_func: Callable[[Exception], Any]):
        """Register an error handler for specific error types
        
        Args:
            error_type: Type of error to handle
            handler_func: Function to handle the error
        """
        self._error_handlers[error_type] = handler_func
    
    def handle_error(self, error: Exception) -> ServiceOperation:
        """Handle an error using registered handlers
        
        Args:
            error: Exception to handle
            
        Returns:
            Operation result from error handling
        """
        error_type = type(error).__name__
        
        if error_type in self._error_handlers:
            try:
                result = self._error_handlers[error_type](error)
                return ServiceOperation(
                    success=False,
                    data=result,
                    error=str(error),
                    error_code=error_type
                )
            except Exception as handler_error:
                logger.error(f"Error handler failed: {handler_error}")
        
        # Default error handling
        return ServiceOperation(
            success=False,
            data=None,
            error=str(error),
            error_code=error_type
        )
    
    def get_status(self) -> ServiceStatus:
        """Get current service status
        
        Returns:
            Current operational status
        """
        return self.status
    
    def get_uptime(self) -> float:
        """Get service uptime in seconds
        
        Returns:
            Uptime in seconds since initialization
        """
        if self._start_time > 0:
            return datetime.now().timestamp() - self._start_time
        return 0.0
    
    def set_status(self, status: ServiceStatus):
        """Set service status with logging
        
        Args:
            status: New service status
        """
        old_status = self.status
        self.status = status
        logger.info(f"Service {self.service_id} status changed: {old_status.value} -> {status.value}")


class CoreService(ServiceProtocol):
    """Base class for core KGAS services
    
    Provides common implementation for:
    - Configuration management
    - Health check aggregation
    - Metrics collection
    - Error handling
    """
    
    def __init__(self, service_id: str, service_type: ServiceType):
        super().__init__()
        self.service_id = service_id
        self.service_type = service_type
        self.config: Dict[str, Any] = {}
        self._metrics = {
            "request_count": 0,
            "error_count": 0,
            "total_response_time": 0.0,
            "response_times": []
        }
    
    def health_check(self) -> ServiceHealth:
        """Perform health check by aggregating all registered checks"""
        checks = {}
        errors = []
        
        # Run all registered health checks
        for check_name, check_func in self._health_checks.items():
            try:
                checks[check_name] = check_func()
            except Exception as e:
                checks[check_name] = False
                errors.append(f"{check_name}: {str(e)}")
        
        # Determine overall health
        all_healthy = all(checks.values()) if checks else True
        
        # Determine status based on health
        if all_healthy and self.status == ServiceStatus.READY:
            status = ServiceStatus.READY
        elif not all_healthy and self.status == ServiceStatus.READY:
            status = ServiceStatus.DEGRADED
        else:
            status = self.status
        
        return ServiceHealth(
            service_id=self.service_id,
            status=status,
            healthy=all_healthy,
            uptime_seconds=self.get_uptime(),
            last_check=datetime.now().isoformat(),
            checks=checks,
            metrics={
                "request_count": self._metrics["request_count"],
                "error_rate": self._metrics["error_count"] / max(1, self._metrics["request_count"])
            },
            errors=errors
        )
    
    def get_metrics(self) -> ServiceMetrics:
        """Get current service metrics"""
        response_times = self._metrics["response_times"][-1000:]  # Keep last 1000
        
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            sorted_times = sorted(response_times)
            p95_response = sorted_times[int(len(sorted_times) * 0.95)]
            p99_response = sorted_times[int(len(sorted_times) * 0.99)]
        else:
            avg_response = p95_response = p99_response = 0.0
        
        # Get system metrics
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / (1024 * 1024)
        cpu_percent = process.cpu_percent()
        
        return ServiceMetrics(
            service_id=self.service_id,
            timestamp=datetime.now().isoformat(),
            request_count=self._metrics["request_count"],
            error_count=self._metrics["error_count"],
            avg_response_time=avg_response,
            p95_response_time=p95_response,
            p99_response_time=p99_response,
            active_connections=0,  # Override in subclass if applicable
            memory_usage_mb=memory_mb,
            cpu_usage_percent=cpu_percent
        )
    
    def track_request(self, duration_ms: float, success: bool = True):
        """Track a request for metrics
        
        Args:
            duration_ms: Request duration in milliseconds
            success: Whether request succeeded
        """
        self._metrics["request_count"] += 1
        if not success:
            self._metrics["error_count"] += 1
        self._metrics["total_response_time"] += duration_ms
        self._metrics["response_times"].append(duration_ms)
        
        # Keep only last 1000 response times
        if len(self._metrics["response_times"]) > 1000:
            self._metrics["response_times"] = self._metrics["response_times"][-1000:]


# Service discovery and registration

class ServiceRegistry:
    """Central registry for all KGAS services
    
    Provides:
    - Service registration and discovery
    - Dependency resolution
    - Health monitoring
    - Graceful shutdown coordination
    """
    
    def __init__(self):
        self.services: Dict[str, ServiceProtocol] = {}
        self._shutdown_order: List[str] = []
    
    def register(self, service: ServiceProtocol) -> bool:
        """Register a service
        
        Args:
            service: Service instance to register
            
        Returns:
            True if registration successful
        """
        try:
            info = service.get_service_info()
            self.services[info.service_id] = service
            
            # Update shutdown order based on dependencies
            self._update_shutdown_order()
            
            logger.info(f"Registered service: {info.service_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service: {e}")
            return False
    
    def get_service(self, service_id: str) -> Optional[ServiceProtocol]:
        """Get a registered service by ID
        
        Args:
            service_id: Service identifier
            
        Returns:
            Service instance or None
        """
        return self.services.get(service_id)
    
    def get_services_by_type(self, service_type: ServiceType) -> List[ServiceProtocol]:
        """Get all services of a specific type
        
        Args:
            service_type: Type of services to retrieve
            
        Returns:
            List of matching services
        """
        matching = []
        for service in self.services.values():
            info = service.get_service_info()
            if info.service_type == service_type:
                matching.append(service)
        return matching
    
    def health_check_all(self) -> Dict[str, ServiceHealth]:
        """Perform health checks on all services
        
        Returns:
            Dict mapping service ID to health status
        """
        health_results = {}
        for service_id, service in self.services.items():
            try:
                health_results[service_id] = service.health_check()
            except Exception as e:
                health_results[service_id] = ServiceHealth(
                    service_id=service_id,
                    status=ServiceStatus.ERROR,
                    healthy=False,
                    uptime_seconds=0,
                    last_check=datetime.now().isoformat(),
                    checks={},
                    metrics={},
                    errors=[f"Health check failed: {str(e)}"]
                )
        return health_results
    
    def shutdown_all(self) -> Dict[str, ServiceOperation]:
        """Shutdown all services in dependency order
        
        Returns:
            Dict mapping service ID to shutdown result
        """
        shutdown_results = {}
        
        # Shutdown in reverse dependency order
        for service_id in reversed(self._shutdown_order):
            if service_id in self.services:
                service = self.services[service_id]
                try:
                    shutdown_results[service_id] = service.shutdown()
                except Exception as e:
                    shutdown_results[service_id] = ServiceOperation(
                        success=False,
                        data=None,
                        error=f"Shutdown failed: {str(e)}"
                    )
        
        return shutdown_results
    
    def _update_shutdown_order(self):
        """Update shutdown order based on dependencies"""
        # Simple topological sort for shutdown order
        visited = set()
        order = []
        
        def visit(service_id: str):
            if service_id in visited:
                return
            visited.add(service_id)
            
            if service_id in self.services:
                info = self.services[service_id].get_service_info()
                for dep in info.dependencies:
                    if dep in self.services:
                        visit(dep)
                order.append(service_id)
        
        for service_id in self.services:
            visit(service_id)
        
        self._shutdown_order = order


# Global service registry instance
_service_registry = ServiceRegistry()


def get_service_registry() -> ServiceRegistry:
    """Get the global service registry instance
    
    Returns:
        Global ServiceRegistry instance
    """
    return _service_registry


# Convenience functions

def register_service(service: ServiceProtocol) -> bool:
    """Register a service with the global registry
    
    Args:
        service: Service to register
        
    Returns:
        True if registration successful
    """
    return get_service_registry().register(service)


def get_service(service_id: str) -> Optional[ServiceProtocol]:
    """Get a service from the global registry
    
    Args:
        service_id: Service identifier
        
    Returns:
        Service instance or None
    """
    return get_service_registry().get_service(service_id)


def get_all_service_health() -> Dict[str, ServiceHealth]:
    """Get health status of all registered services
    
    Returns:
        Dict mapping service ID to health status
    """
    return get_service_registry().health_check_all()