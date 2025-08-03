"""
Service Interfaces for Dependency Injection

Defines abstract interfaces that all services must implement.
This enables loose coupling, easy testing, and flexible service swapping.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, AsyncContextManager, AsyncIterator
from contextlib import asynccontextmanager


class ServiceResponse:
    """Standard response format for all service operations"""
    
    def __init__(self, success: bool, data: Any = None, 
                 error: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}


class ServiceInterface(ABC):
    """Base interface for all services"""
    
    @abstractmethod
    async def startup(self) -> None:
        """Initialize service and establish connections"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Cleanup resources and close connections"""
        pass
    
    @abstractmethod
    async def health_check(self) -> ServiceResponse:
        """Check service health and return status"""
        pass


class IdentityServiceInterface(ServiceInterface):
    """Interface for entity identity management service"""
    
    @abstractmethod
    async def create_mention(self, surface_form: str, context: Optional[str] = None, 
                           confidence: Optional[float] = None, **kwargs) -> ServiceResponse:
        """Create a new entity mention
        
        Args:
            surface_form: Text representation of the entity
            context: Surrounding context for disambiguation
            confidence: Confidence score for the mention
            **kwargs: Additional metadata
            
        Returns:
            ServiceResponse with mention_id in data field
        """
        pass
    
    @abstractmethod
    async def resolve_entity(self, mention_id: str) -> ServiceResponse:
        """Resolve a mention to a canonical entity
        
        Args:
            mention_id: ID of the mention to resolve
            
        Returns:
            ServiceResponse with entity information
        """
        pass
    
    @abstractmethod
    async def get_entity_by_id(self, entity_id: str) -> ServiceResponse:
        """Get entity by canonical ID
        
        Args:
            entity_id: Canonical entity ID
            
        Returns:
            ServiceResponse with entity details
        """
        pass
    
    @abstractmethod
    async def search_entities(self, query: str, limit: int = 10) -> ServiceResponse:
        """Search for entities by text query
        
        Args:
            query: Search query text
            limit: Maximum number of results
            
        Returns:
            ServiceResponse with list of matching entities
        """
        pass
    
    @abstractmethod
    async def link_entities(self, entity1_id: str, entity2_id: str, 
                          relationship_type: str) -> ServiceResponse:
        """Create a relationship between two entities
        
        Args:
            entity1_id: First entity ID
            entity2_id: Second entity ID
            relationship_type: Type of relationship
            
        Returns:
            ServiceResponse with relationship details
        """
        pass


class ProvenanceServiceInterface(ServiceInterface):
    """Interface for data provenance tracking service"""
    
    @abstractmethod
    async def record_operation(self, operation_type: str, inputs: Dict[str, Any],
                             outputs: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> ServiceResponse:
        """Record a data processing operation
        
        Args:
            operation_type: Type of operation performed
            inputs: Input data and parameters
            outputs: Output data and results
            metadata: Additional operation metadata
            
        Returns:
            ServiceResponse with operation_id
        """
        pass
    
    @abstractmethod
    async def get_lineage(self, data_id: str, direction: str = "both") -> ServiceResponse:
        """Get data lineage for a given data item
        
        Args:
            data_id: ID of the data item
            direction: "upstream", "downstream", or "both"
            
        Returns:
            ServiceResponse with lineage graph
        """
        pass
    
    @abstractmethod
    async def analyze_impact(self, operation_id: str) -> ServiceResponse:
        """Analyze the impact of a given operation
        
        Args:
            operation_id: ID of the operation to analyze
            
        Returns:
            ServiceResponse with impact analysis
        """
        pass
    
    @abstractmethod
    async def validate_provenance(self, data_id: str) -> ServiceResponse:
        """Validate the provenance chain for data integrity
        
        Args:
            data_id: ID of the data to validate
            
        Returns:
            ServiceResponse with validation results
        """
        pass


class QualityServiceInterface(ServiceInterface):
    """Interface for data quality assessment service"""
    
    @abstractmethod
    async def assess_data_quality(self, data: Any, schema: Optional[Dict[str, Any]] = None) -> ServiceResponse:
        """Assess overall data quality
        
        Args:
            data: Data to assess
            schema: Optional schema for validation
            
        Returns:
            ServiceResponse with quality scores and metrics
        """
        pass
    
    @abstractmethod
    async def validate_extraction(self, extracted_data: Any, 
                                source_data: Any) -> ServiceResponse:
        """Validate data extraction quality
        
        Args:
            extracted_data: Data that was extracted
            source_data: Original source data
            
        Returns:
            ServiceResponse with validation results
        """
        pass
    
    @abstractmethod
    async def calculate_confidence(self, data: Any, context: Optional[Dict[str, Any]] = None) -> ServiceResponse:
        """Calculate confidence score for data
        
        Args:
            data: Data to score
            context: Additional context for scoring
            
        Returns:
            ServiceResponse with confidence score
        """
        pass
    
    @abstractmethod
    async def generate_quality_report(self, data_set_id: str) -> ServiceResponse:
        """Generate comprehensive quality report
        
        Args:
            data_set_id: ID of the data set to report on
            
        Returns:
            ServiceResponse with quality report
        """
        pass


class Neo4jServiceInterface(ServiceInterface):
    """Interface for Neo4j database service"""
    
    @abstractmethod
    async def execute_query(self, cypher: str, parameters: Optional[Dict[str, Any]] = None) -> ServiceResponse:
        """Execute a Cypher query
        
        Args:
            cypher: Cypher query string
            parameters: Query parameters
            
        Returns:
            ServiceResponse with query results
        """
        pass
    
    @abstractmethod
    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[Any]:
        """Get a database session for transaction management
        
        Returns:
            Async context manager for database session
        """
        yield  # This makes it an async generator
    
    @abstractmethod
    async def execute_transaction(self, queries: List[Dict[str, Any]]) -> ServiceResponse:
        """Execute multiple queries in a transaction
        
        Args:
            queries: List of {"cypher": str, "parameters": dict} queries
            
        Returns:
            ServiceResponse with transaction results
        """
        pass
    
    @abstractmethod
    async def get_database_info(self) -> ServiceResponse:
        """Get database information and statistics
        
        Returns:
            ServiceResponse with database info
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close database connections"""
        pass


class ConfigServiceInterface(ServiceInterface):
    """Interface for configuration management service"""
    
    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        pass
    
    @abstractmethod
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section
        
        Args:
            section: Section name
            
        Returns:
            Dictionary of configuration values
        """
        pass
    
    @abstractmethod
    async def reload_config(self) -> ServiceResponse:
        """Reload configuration from sources
        
        Returns:
            ServiceResponse indicating success/failure
        """
        pass


class LoggingServiceInterface(ServiceInterface):
    """Interface for centralized logging service"""
    
    @abstractmethod
    def get_logger(self, name: str) -> Any:
        """Get logger instance for a component
        
        Args:
            name: Logger name
            
        Returns:
            Logger instance
        """
        pass
    
    @abstractmethod
    async def log_operation(self, level: str, message: str, 
                          context: Optional[Dict[str, Any]] = None) -> None:
        """Log an operation with context
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            context: Additional context data
        """
        pass