"""Custom Exception Classes for Core Services

This module defines custom exception classes for better error categorization
and handling across all core services in the KGAS system.
"""

from typing import Optional, Any, Dict


class KGASServiceError(Exception):
    """Base exception for all KGAS service errors."""
    
    def __init__(self, message: str, error_code: str = None, context: Dict[str, Any] = None):
        super().__init__(message)
        self.error_code = error_code or "KGAS_SERVICE_ERROR"
        self.context = context or {}


class ServiceInitializationError(KGASServiceError):
    """Raised when a service fails to initialize properly."""
    
    def __init__(self, service_name: str, message: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Service '{service_name}' initialization failed: {message}",
            "SERVICE_INITIALIZATION_FAILED",
            context
        )
        self.service_name = service_name


class ServiceConfigurationError(KGASServiceError):
    """Raised when service configuration is invalid."""
    
    def __init__(self, service_name: str, config_key: str, message: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Invalid configuration for service '{service_name}', key '{config_key}': {message}",
            "INVALID_SERVICE_CONFIGURATION",
            context
        )
        self.service_name = service_name
        self.config_key = config_key


class ServiceHealthCheckError(KGASServiceError):
    """Raised when service health check fails."""
    
    def __init__(self, service_name: str, reason: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Health check failed for service '{service_name}': {reason}",
            "SERVICE_HEALTH_CHECK_FAILED",
            context
        )
        self.service_name = service_name


# Quality Service Specific Exceptions
class QualityAssessmentError(KGASServiceError):
    """Raised when quality assessment operations fail."""
    
    def __init__(self, object_ref: str, message: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Quality assessment failed for object '{object_ref}': {message}",
            "QUALITY_ASSESSMENT_FAILED",
            context
        )
        self.object_ref = object_ref


class ConfidencePropagationError(KGASServiceError):
    """Raised when confidence propagation fails."""
    
    def __init__(self, operation_type: str, message: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Confidence propagation failed for operation '{operation_type}': {message}",
            "CONFIDENCE_PROPAGATION_FAILED",
            context
        )
        self.operation_type = operation_type


class QualityRuleError(KGASServiceError):
    """Raised when quality rule operations fail."""
    
    def __init__(self, rule_id: str, message: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Quality rule error for rule '{rule_id}': {message}",
            "QUALITY_RULE_ERROR",
            context
        )
        self.rule_id = rule_id


# Provenance Service Specific Exceptions
class OperationTrackingError(KGASServiceError):
    """Raised when operation tracking fails."""
    
    def __init__(self, operation_id: str, message: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Operation tracking failed for operation '{operation_id}': {message}",
            "OPERATION_TRACKING_FAILED",
            context
        )
        self.operation_id = operation_id


class LineageAnalysisError(KGASServiceError):
    """Raised when lineage analysis fails."""
    
    def __init__(self, object_ref: str, message: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Lineage analysis failed for object '{object_ref}': {message}",
            "LINEAGE_ANALYSIS_FAILED",
            context
        )
        self.object_ref = object_ref


class ProvenanceChainError(KGASServiceError):
    """Raised when provenance chain operations fail."""
    
    def __init__(self, target_ref: str, message: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Provenance chain error for target '{target_ref}': {message}",
            "PROVENANCE_CHAIN_ERROR",
            context
        )
        self.target_ref = target_ref


# Identity Service Specific Exceptions
class EntityResolutionError(KGASServiceError):
    """Raised when entity resolution fails."""
    
    def __init__(self, entity_identifier: str, message: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Entity resolution failed for '{entity_identifier}': {message}",
            "ENTITY_RESOLUTION_FAILED",
            context
        )
        self.entity_identifier = entity_identifier


class MentionCreationError(KGASServiceError):
    """Raised when mention creation fails."""
    
    def __init__(self, surface_form: str, message: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Mention creation failed for surface form '{surface_form}': {message}",
            "MENTION_CREATION_FAILED",
            context
        )
        self.surface_form = surface_form


# Workflow State Service Specific Exceptions
class WorkflowStateError(KGASServiceError):
    """Raised when workflow state operations fail."""
    
    def __init__(self, workflow_id: str, message: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Workflow state error for workflow '{workflow_id}': {message}",
            "WORKFLOW_STATE_ERROR",
            context
        )
        self.workflow_id = workflow_id


class CheckpointError(KGASServiceError):
    """Raised when checkpoint operations fail."""
    
    def __init__(self, checkpoint_id: str, message: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Checkpoint error for checkpoint '{checkpoint_id}': {message}",
            "CHECKPOINT_ERROR",
            context
        )
        self.checkpoint_id = checkpoint_id


# Database and Storage Exceptions
class DatabaseConnectionError(KGASServiceError):
    """Raised when database connection fails."""
    
    def __init__(self, database_type: str, message: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Database connection failed for {database_type}: {message}",
            "DATABASE_CONNECTION_FAILED",
            context
        )
        self.database_type = database_type


class DataPersistenceError(KGASServiceError):
    """Raised when data persistence operations fail."""
    
    def __init__(self, operation: str, message: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Data persistence failed for operation '{operation}': {message}",
            "DATA_PERSISTENCE_FAILED",
            context
        )
        self.operation = operation


# Resource and Performance Exceptions
class ResourceExhaustionError(KGASServiceError):
    """Raised when system resources are exhausted."""
    
    def __init__(self, resource_type: str, message: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Resource exhaustion for {resource_type}: {message}",
            "RESOURCE_EXHAUSTION",
            context
        )
        self.resource_type = resource_type


class PerformanceThresholdError(KGASServiceError):
    """Raised when performance thresholds are exceeded."""
    
    def __init__(self, metric_name: str, threshold: float, actual: float, context: Dict[str, Any] = None):
        super().__init__(
            f"Performance threshold exceeded for {metric_name}: {actual} > {threshold}",
            "PERFORMANCE_THRESHOLD_EXCEEDED",
            context
        )
        self.metric_name = metric_name
        self.threshold = threshold
        self.actual = actual


# Validation and Input Exceptions
class InputValidationError(KGASServiceError):
    """Raised when input validation fails."""
    
    def __init__(self, parameter_name: str, message: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Input validation failed for parameter '{parameter_name}': {message}",
            "INPUT_VALIDATION_FAILED",
            context
        )
        self.parameter_name = parameter_name


class SchemaValidationError(KGASServiceError):
    """Raised when schema validation fails."""
    
    def __init__(self, schema_name: str, message: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Schema validation failed for '{schema_name}': {message}",
            "SCHEMA_VALIDATION_FAILED",
            context
        )
        self.schema_name = schema_name


# Recovery and Retry Exceptions
class RetryExhaustionError(KGASServiceError):
    """Raised when retry attempts are exhausted."""
    
    def __init__(self, operation: str, max_retries: int, context: Dict[str, Any] = None):
        super().__init__(
            f"Retry exhaustion for operation '{operation}' after {max_retries} attempts",
            "RETRY_EXHAUSTION",
            context
        )
        self.operation = operation
        self.max_retries = max_retries


class RecoveryError(KGASServiceError):
    """Raised when error recovery fails."""
    
    def __init__(self, recovery_strategy: str, message: str, context: Dict[str, Any] = None):
        super().__init__(
            f"Recovery failed for strategy '{recovery_strategy}': {message}",
            "RECOVERY_FAILED",
            context
        )
        self.recovery_strategy = recovery_strategy