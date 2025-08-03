"""Unified Service Interface

Defines standard interfaces that all core services must implement.
Ensures consistency across service implementations and enables proper
dependency injection and lifecycle management.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Protocol, List
from dataclasses import dataclass
from datetime import datetime
from .logging_config import get_logger

logger = get_logger("core.unified_service_interface")


@dataclass(frozen=True)
class ServiceRequest:
    """Standard request format for all service operations"""
    operation: str
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None


@dataclass(frozen=True)
class ServiceResponse:
    """Standard response format for all service operations"""
    success: bool
    data: Any
    metadata: Dict[str, Any]
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    request_id: Optional[str] = None


@dataclass
class ServiceMetrics:
    """Standard metrics collected for all services"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    service_start_time: Optional[datetime] = None


class CoreService(ABC):
    """Abstract base class for all core services
    
    Defines the unified interface that all services must implement.
    Provides common functionality for configuration, health checks,
    metrics collection, and lifecycle management.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger(f"core.{self.__class__.__name__}")
        self.metrics = ServiceMetrics()
        self._initialized = False
        self._healthy = False
        
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize service with configuration
        
        Args:
            config: Service configuration dictionary
            
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check service health and readiness
        
        Returns:
            True if service is healthy and ready, False otherwise
        """
        pass
    
    @abstractmethod
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information and capabilities
        
        Returns:
            Dictionary containing service name, version, capabilities, etc.
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """Clean up service resources
        
        Returns:
            True if cleanup successful, False otherwise
        """
        pass
    
    def get_metrics(self) -> ServiceMetrics:
        """Get service performance metrics
        
        Returns:
            ServiceMetrics object with current metrics
        """
        return self.metrics
    
    def update_metrics(self, success: bool, response_time: float):
        """Update service metrics after request processing
        
        Args:
            success: Whether the request was successful
            response_time: Time taken to process the request in seconds
        """
        self.metrics.total_requests += 1
        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
            
        # Update average response time
        total_successful = self.metrics.successful_requests
        if total_successful > 1:
            self.metrics.average_response_time = (
                (self.metrics.average_response_time * (total_successful - 1) + response_time) / total_successful
            )
        else:
            self.metrics.average_response_time = response_time
            
        self.metrics.last_request_time = datetime.now()
    
    def is_initialized(self) -> bool:
        """Check if service has been initialized
        
        Returns:
            True if service is initialized, False otherwise
        """
        return self._initialized
    
    def is_healthy(self) -> bool:
        """Check if service is currently healthy
        
        Returns:
            True if service is healthy, False otherwise
        """
        return self._healthy


class IdentityServiceProtocol(Protocol):
    """Protocol for Identity Service interface"""
    
    def create_mention(self, surface_form: str, start_pos: int, end_pos: int,
                      source_ref: str, entity_type: str = None,
                      confidence: float = 0.8) -> ServiceResponse:
        """Create a new entity mention"""
        ...
    
    def resolve_entity(self, mention_id: str) -> ServiceResponse:
        """Resolve entity for a given mention"""
        ...
    
    def get_entity_by_id(self, entity_id: str) -> ServiceResponse:
        """Get entity information by ID"""
        ...


class ProvenanceServiceProtocol(Protocol):
    """Protocol for Provenance Service interface"""
    
    def log_operation(self, operation: str, input_data: Any, output_data: Any,
                     metadata: Optional[Dict[str, Any]] = None) -> ServiceResponse:
        """Log an operation for provenance tracking"""
        ...
    
    def get_provenance(self, entity_id: str) -> ServiceResponse:
        """Get provenance information for an entity"""
        ...
    
    def trace_lineage(self, entity_id: str, depth: int = 5) -> ServiceResponse:
        """Trace the lineage of an entity"""
        ...


class QualityServiceProtocol(Protocol):
    """Protocol for Quality Service interface"""
    
    def assess_quality(self, data: Any, context: Optional[Dict[str, Any]] = None) -> ServiceResponse:
        """Assess the quality of data"""
        ...
    
    def validate_confidence(self, confidence: float, context: Dict[str, Any]) -> ServiceResponse:
        """Validate confidence score"""
        ...
    
    def aggregate_confidence(self, confidences: List[float]) -> ServiceResponse:
        """Aggregate multiple confidence scores"""
        ...


class WorkflowStateServiceProtocol(Protocol):
    """Protocol for Workflow State Service interface"""
    
    def create_checkpoint(self, workflow_id: str, state: Dict[str, Any]) -> ServiceResponse:
        """Create a workflow checkpoint"""
        ...
    
    def restore_checkpoint(self, workflow_id: str, checkpoint_id: str) -> ServiceResponse:
        """Restore workflow from checkpoint"""
        ...
    
    def get_workflow_status(self, workflow_id: str) -> ServiceResponse:
        """Get current workflow status"""
        ...


class SecurityServiceProtocol(Protocol):
    """Protocol for Security Service interface"""
    
    def authenticate(self, credentials: Dict[str, str]) -> ServiceResponse:
        """Authenticate user credentials"""
        ...
    
    def authorize(self, user_id: str, resource: str, action: str) -> ServiceResponse:
        """Authorize user action on resource"""
        ...
    
    def encrypt_sensitive_data(self, data: str) -> ServiceResponse:
        """Encrypt sensitive data"""
        ...
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> ServiceResponse:
        """Decrypt sensitive data"""
        ...


def validate_service_implementation(service: Any, protocol: type) -> bool:
    """Validate that a service implements the required protocol
    
    Args:
        service: Service instance to validate
        protocol: Protocol type to validate against
        
    Returns:
        True if service implements protocol, False otherwise
    """
    try:
        # Check if service implements required methods
        if hasattr(protocol, '__annotations__'):
            for method_name in protocol.__annotations__:
                if not hasattr(service, method_name):
                    logger.error(f"Service {service.__class__.__name__} missing method: {method_name}")
                    return False
                    
                method = getattr(service, method_name)
                if not callable(method):
                    logger.error(f"Service {service.__class__.__name__} method {method_name} is not callable")
                    return False
        
        # Check if service extends CoreService
        if not isinstance(service, CoreService):
            logger.warning(f"Service {service.__class__.__name__} does not extend CoreService")
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating service implementation: {e}")
        return False


def create_service_response(success: bool, data: Any = None, 
                          error_code: str = None, error_message: str = None,
                          metadata: Optional[Dict[str, Any]] = None,
                          request_id: Optional[str] = None) -> ServiceResponse:
    """Helper function to create standardized service responses
    
    Args:
        success: Whether the operation was successful
        data: Response data (None if error)
        error_code: Error code if operation failed
        error_message: Error message if operation failed
        metadata: Additional metadata
        request_id: Request ID for tracking
        
    Returns:
        Standardized ServiceResponse object
    """
    return ServiceResponse(
        success=success,
        data=data,
        metadata=metadata or {},
        error_code=error_code,
        error_message=error_message,
        request_id=request_id
    )


def create_service_request(operation: str, parameters: Dict[str, Any],
                         context: Optional[Dict[str, Any]] = None,
                         request_id: Optional[str] = None) -> ServiceRequest:
    """Helper function to create standardized service requests
    
    Args:
        operation: Operation name
        parameters: Operation parameters
        context: Optional execution context
        request_id: Request ID for tracking
        
    Returns:
        Standardized ServiceRequest object
    """
    return ServiceRequest(
        operation=operation,
        parameters=parameters,
        context=context,
        request_id=request_id
    )