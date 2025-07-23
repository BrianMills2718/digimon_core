# Service Locator Architecture

**Version**: 1.0  
**Status**: Target Architecture  
**Last Updated**: 2025-07-23  

## Overview

KGAS uses a **Service Locator Pattern** with dependency injection to manage service dependencies while avoiding circular dependency issues. This architecture provides clean separation of concerns and enables flexible service composition.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Application Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │      Tools      │  │   Workflows     │  │      MCP API        │  │
│  └─────────┬───────┘  └─────────┬───────┘  └─────────┬───────────┘  │
└───────────┼─────────────────────┼─────────────────────┼───────────────┘
            │                     │                     │
            ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Service Container                                │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │               Interface Layer                                   │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐│ │
│  │  │IIdentityService│ │IQualityService│ │IProvenanceService       ││ │
│  │  └──────────────┘ └──────────────┘ └──────────────────────────┘│ │
│  └─────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │               Implementation Layer                              │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐│ │
│  │  │IdentityService│ │QualityService│ │ProvenanceService        ││ │
│  │  └──────────────┘ └──────────────┘ └──────────────────────────┘│ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Storage Layer                                  │
│  ┌─────────────────────────────┐    ┌─────────────────────────────┐  │
│  │       Neo4j Graph           │    │       SQLite Metadata      │  │
│  │   (Entities, Relations)     │    │   (Provenance, Config)     │  │
│  └─────────────────────────────┘    └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Service Interface Design

### 1. Service Interfaces (Protocols)

All services implement protocol interfaces to enable loose coupling:

```python
from typing import Protocol, Any, Dict, List, Optional
from abc import abstractmethod

class IIdentityService(Protocol):
    """Interface for entity identity management"""
    
    @abstractmethod
    def get_identity(self, entity_id: str) -> Optional[Identity]:
        """Retrieve entity identity by ID"""
        ...
    
    @abstractmethod
    def resolve_entity(self, mention: str, context: Dict[str, Any]) -> EntityResolution:
        """Resolve entity mention to canonical identity"""
        ...
    
    @abstractmethod
    def merge_entities(self, entity_ids: List[str]) -> MergeResult:
        """Merge multiple entity identities"""
        ...

class IQualityService(Protocol):
    """Interface for data quality assessment"""
    
    @abstractmethod
    def assess_quality(self, data: Any) -> QualityScore:
        """Assess quality of data object"""
        ...
    
    @abstractmethod
    def get_quality_tier(self, confidence: float) -> QualityTier:
        """Determine quality tier from confidence score"""
        ...
    
    @abstractmethod
    def validate_schema(self, data: Dict[str, Any], schema_name: str) -> ValidationResult:
        """Validate data against schema"""
        ...

class IProvenanceService(Protocol):
    """Interface for provenance tracking"""
    
    @abstractmethod
    def record_operation(self, operation: Operation) -> ProvenanceRecord:
        """Record an operation for provenance tracking"""
        ...
    
    @abstractmethod
    def get_lineage(self, object_id: str) -> LineageGraph:
        """Get complete lineage for an object"""
        ...
    
    @abstractmethod
    def trace_to_source(self, object_id: str) -> List[SourceDocument]:
        """Trace object back to source documents"""
        ...

class IWorkflowStateService(Protocol):
    """Interface for workflow state management"""
    
    @abstractmethod
    def save_state(self, workflow_id: str, state: WorkflowState) -> bool:
        """Save workflow state"""
        ...
    
    @abstractmethod
    def load_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Load workflow state"""
        ...
```

## Service Container Implementation

### Core Service Container

```python
from typing import Type, TypeVar, Callable, Dict, Any
from threading import Lock
import inspect

T = TypeVar('T')

class ServiceContainer:
    """Service locator with dependency injection and lazy initialization"""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
        self._lock = Lock()
    
    def register_factory(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """Register a factory function for a service type"""
        with self._lock:
            self._factories[service_type] = factory
    
    def register_singleton(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """Register a singleton service (created once, reused)"""
        with self._lock:
            self._factories[service_type] = factory
            # Mark as singleton
            self._singletons[service_type] = None
    
    def register_instance(self, service_type: Type[T], instance: T) -> None:
        """Register a pre-created service instance"""
        with self._lock:
            self._services[service_type] = instance
    
    def get(self, service_type: Type[T]) -> T:
        """Get service instance, creating if necessary"""
        with self._lock:
            # Return existing instance if available
            if service_type in self._services:
                return self._services[service_type]
            
            # Handle singletons
            if service_type in self._singletons:
                if self._singletons[service_type] is None:
                    self._singletons[service_type] = self._create_service(service_type)
                return self._singletons[service_type]
            
            # Create new instance
            return self._create_service(service_type)
    
    def _create_service(self, service_type: Type[T]) -> T:
        """Create service instance using registered factory"""
        if service_type not in self._factories:
            raise ServiceNotRegisteredError(f"No factory registered for {service_type}")
        
        factory = self._factories[service_type]
        
        # Check if factory needs dependency injection
        sig = inspect.signature(factory)
        if len(sig.parameters) > 0:
            # Factory needs dependencies - inject them
            return factory(self)
        else:
            # Simple factory
            return factory()
    
    def clear(self) -> None:
        """Clear all services (useful for testing)"""
        with self._lock:
            self._services.clear()
            self._singletons.clear()
    
    def is_registered(self, service_type: Type) -> bool:
        """Check if service type is registered"""
        return service_type in self._factories or service_type in self._services

class ServiceNotRegisteredError(Exception):
    """Raised when requesting unregistered service"""
    pass
```

### Service Registration and Bootstrap

```python
class ServiceBootstrapper:
    """Handles service registration and container setup"""
    
    @staticmethod
    def configure_container() -> ServiceContainer:
        """Configure service container with all KGAS services"""
        container = ServiceContainer()
        
        # Register core services as singletons
        container.register_singleton(
            IIdentityService,
            lambda c: IdentityService(
                neo4j_manager=c.get(INeo4jManager),
                quality_service=c.get(IQualityService)
            )
        )
        
        container.register_singleton(
            IQualityService,
            lambda c: QualityService(
                config=c.get(IConfigManager)
            )
        )
        
        container.register_singleton(
            IProvenanceService,
            lambda c: ProvenanceService(
                sqlite_manager=c.get(ISQLiteManager),
                identity_service=c.get(IIdentityService)
            )
        )
        
        container.register_singleton(
            IWorkflowStateService,
            lambda c: WorkflowStateService(
                sqlite_manager=c.get(ISQLiteManager)
            )
        )
        
        # Register infrastructure services
        container.register_singleton(
            INeo4jManager,
            lambda c: Neo4jManager(config=c.get(IConfigManager))
        )
        
        container.register_singleton(
            ISQLiteManager,
            lambda c: SQLiteManager(config=c.get(IConfigManager))
        )
        
        container.register_singleton(
            IConfigManager,
            lambda c: ConfigManager()
        )
        
        # Register schema manager
        container.register_singleton(
            ISchemaManager,
            lambda c: SchemaManager()
        )
        
        return container
```

## Service Implementation Pattern

### Service Implementation Structure

```python
class IdentityService:
    """Implementation of IIdentityService using service locator pattern"""
    
    def __init__(self, container: ServiceContainer):
        self.container = container
        # Services are resolved lazily via properties
    
    @property
    def neo4j_manager(self) -> INeo4jManager:
        """Lazy access to Neo4j manager"""
        return self.container.get(INeo4jManager)
    
    @property
    def quality_service(self) -> IQualityService:
        """Lazy access to quality service"""
        return self.container.get(IQualityService)
    
    @property
    def provenance_service(self) -> IProvenanceService:
        """Lazy access to provenance service"""
        return self.container.get(IProvenanceService)
    
    def get_identity(self, entity_id: str) -> Optional[Identity]:
        """Get entity identity with quality assessment"""
        # Use Neo4j to retrieve entity
        entity_data = self.neo4j_manager.get_entity(entity_id)
        if not entity_data:
            return None
        
        # Assess quality using quality service
        quality = self.quality_service.assess_quality(entity_data)
        
        # Create identity with quality info
        identity = Identity(
            entity_id=entity_id,
            canonical_name=entity_data["canonical_name"],
            entity_type=entity_data["entity_type"],
            quality_tier=quality.tier,
            confidence=quality.confidence
        )
        
        # Record access for provenance
        self.provenance_service.record_operation(
            Operation(
                type="identity_access",
                entity_id=entity_id,
                result=identity
            )
        )
        
        return identity
    
    def resolve_entity(self, mention: str, context: Dict[str, Any]) -> EntityResolution:
        """Resolve entity mention with context-aware disambiguation"""
        # Implementation details...
        pass
```

## Tool Integration Pattern

### BaseTool Integration

```python
class BaseTool:
    """Base class for all KGAS tools using service locator pattern"""
    
    def __init__(self, service_container: ServiceContainer):
        self.container = service_container
        self.tool_id = self.get_tool_id()
        
        # Validate required services are available
        self._validate_service_dependencies()
    
    @property
    def identity_service(self) -> IIdentityService:
        """Access to identity service"""
        return self.container.get(IIdentityService)
    
    @property
    def quality_service(self) -> IQualityService:
        """Access to quality service"""
        return self.container.get(IQualityService)
    
    @property
    def provenance_service(self) -> IProvenanceService:
        """Access to provenance service"""
        return self.container.get(IProvenanceService)
    
    @property
    def schema_manager(self) -> ISchemaManager:
        """Access to schema manager"""
        return self.container.get(ISchemaManager)
    
    def _validate_service_dependencies(self) -> None:
        """Ensure all required services are registered"""
        required_services = [
            IIdentityService,
            IQualityService,
            IProvenanceService,
            ISchemaManager
        ]
        
        for service_type in required_services:
            if not self.container.is_registered(service_type):
                raise ServiceNotRegisteredError(
                    f"Tool {self.tool_id} requires {service_type.__name__} but it's not registered"
                )
    
    @abstractmethod
    def get_tool_id(self) -> str:
        """Return unique tool identifier"""
        pass
    
    @abstractmethod
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute tool operation"""
        pass
```

### Tool Implementation Example

```python
class T01PdfLoaderTool(BaseTool):
    """PDF loader tool using service locator pattern"""
    
    def get_tool_id(self) -> str:
        return "T01"
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Load PDF with full service integration"""
        start_time = time.time()
        
        try:
            # Record operation start
            operation = Operation(
                type="pdf_load",
                tool_id=self.tool_id,
                inputs=request.input_data,
                started_at=datetime.utcnow()
            )
            
            # Load PDF content
            pdf_content = self._load_pdf_content(request.input_data["file_path"])
            
            # Extract entities using identity service
            entities = self._extract_entities(pdf_content)
            
            # Assess quality for each entity
            quality_entities = []
            for entity in entities:
                quality = self.quality_service.assess_quality(entity)
                enhanced_entity = {
                    **entity,
                    "quality_tier": quality.tier,
                    "confidence": quality.confidence
                }
                quality_entities.append(enhanced_entity)
            
            # Convert to database format
            db_entities = [
                self.schema_manager.to_database(Entity(**entity))
                for entity in quality_entities
            ]
            
            # Create result
            result = ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "entities": db_entities,
                    "document_id": request.input_data["file_path"],
                    "entity_count": len(db_entities)
                },
                execution_time=time.time() - start_time
            )
            
            # Record operation completion
            operation.completed_at = datetime.utcnow()
            operation.outputs = result.data
            operation.status = "success"
            self.provenance_service.record_operation(operation)
            
            return result
            
        except Exception as e:
            # Record operation failure
            operation.completed_at = datetime.utcnow()
            operation.error = str(e)
            operation.status = "error"
            self.provenance_service.record_operation(operation)
            
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                error=str(e),
                execution_time=time.time() - start_time
            )
```

## Benefits of Service Locator Pattern

### 1. **Eliminates Circular Dependencies**
```python
# Before: Circular dependency problem
class ServiceManager:
    def __init__(self):
        self.identity = IdentityService(self)  # Circular!

# After: Service Locator solution
class IdentityService:
    def __init__(self, container: ServiceContainer):
        self.container = container  # No circular dependency
```

### 2. **Lazy Service Resolution**
- Services are created only when needed
- Avoids initialization order problems
- Reduces startup time and memory usage

### 3. **Flexible Configuration**
```python
# Different configurations for different environments
def create_production_container():
    container = ServiceContainer()
    container.register_singleton(IIdentityService, ProductionIdentityService)
    return container

def create_test_container():
    container = ServiceContainer()
    container.register_singleton(IIdentityService, MockIdentityService)
    return container
```

### 4. **Clean Testing**
```python
def test_tool_with_mock_services():
    # Create test container with mocks
    container = ServiceContainer()
    container.register_instance(IQualityService, MockQualityService())
    container.register_instance(IIdentityService, MockIdentityService())
    
    # Tool uses mock services automatically
    tool = T01PdfLoaderTool(container)
    result = tool.execute(test_request)
    
    assert result.status == "success"
```

## Service Lifecycle Management

### Application Startup
```python
def initialize_application():
    """Initialize KGAS application with service container"""
    
    # 1. Create and configure container
    container = ServiceBootstrapper.configure_container()
    
    # 2. Validate all services can be created
    container.get(IIdentityService)  # Force creation to validate
    container.get(IQualityService)
    container.get(IProvenanceService)
    
    # 3. Initialize tool registry with container
    tool_registry = ToolRegistry(container)
    
    # 4. Start MCP server with tool registry
    mcp_server = MCPServer(tool_registry)
    mcp_server.start()
    
    return container, tool_registry, mcp_server
```

### Graceful Shutdown
```python
def shutdown_application(container: ServiceContainer):
    """Gracefully shutdown all services"""
    
    # Get all services that need cleanup
    services = [
        container.get(INeo4jManager),
        container.get(ISQLiteManager),
        container.get(IProvenanceService)
    ]
    
    # Shutdown each service
    for service in services:
        if hasattr(service, 'close'):
            service.close()
    
    # Clear container
    container.clear()
```

## Error Handling and Recovery

### Service Fault Tolerance
```python
class ResilientServiceContainer(ServiceContainer):
    """Service container with fault tolerance"""
    
    def get(self, service_type: Type[T]) -> T:
        """Get service with retry logic"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                return super().get(service_type)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise ServiceCreationError(f"Failed to create {service_type.__name__} after {max_retries} attempts") from e
                
                # Log retry attempt
                logger.warning(f"Service creation failed, attempt {attempt + 1}/{max_retries}: {e}")
                time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
```

### Circuit Breaker Pattern
```python
class CircuitBreakerService:
    """Wraps services with circuit breaker pattern"""
    
    def __init__(self, service: Any, failure_threshold: int = 5):
        self.service = service
        self.failure_threshold = failure_threshold
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call_service(self, method_name: str, *args, **kwargs):
        """Call service method with circuit breaker protection"""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > 60:  # 1 minute timeout
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker open for {self.service.__class__.__name__}")
        
        try:
            method = getattr(self.service, method_name)
            result = method(*args, **kwargs)
            
            # Reset on success
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            
            raise
```

## Configuration and Customization

### Environment-Specific Configuration
```python
class EnvironmentConfig:
    """Environment-specific service configuration"""
    
    @staticmethod
    def get_container_for_environment(env: str) -> ServiceContainer:
        if env == "production":
            return ProductionServiceBootstrapper.configure_container()
        elif env == "development":
            return DevelopmentServiceBootstrapper.configure_container()
        elif env == "test":
            return TestServiceBootstrapper.configure_container()
        else:
            raise ValueError(f"Unknown environment: {env}")

class ProductionServiceBootstrapper:
    @staticmethod
    def configure_container() -> ServiceContainer:
        container = ServiceContainer()
        
        # Production services with real implementations
        container.register_singleton(IIdentityService, lambda c: ProductionIdentityService(c))
        container.register_singleton(IQualityService, lambda c: ProductionQualityService(c))
        
        return container

class TestServiceBootstrapper:
    @staticmethod
    def configure_container() -> ServiceContainer:
        container = ServiceContainer()
        
        # Test services with fast, predictable implementations
        container.register_singleton(IIdentityService, lambda c: MockIdentityService())
        container.register_singleton(IQualityService, lambda c: MockQualityService())
        
        return container
```

The Service Locator Architecture provides a robust, testable, and maintainable foundation for KGAS service management while eliminating circular dependency issues and enabling flexible service composition.