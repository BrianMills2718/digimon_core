# Task TD.2: Dependency Injection Implementation

## Overview
Implement proper dependency injection to decouple services and centralize configuration management.

**Duration**: Weeks 3-4  
**Priority**: HIGH  
**Prerequisites**: Task TD.1 (Architectural Decomposition) complete  

## Current Problems

### Service Coupling Issues
```python
# Current tight coupling pattern found in 20+ files
class AnalyticsService:
    def __init__(self):
        # Direct instantiation = tight coupling
        self.identity_service = IdentityService()  
        self.provenance_service = ProvenanceService()
        self.quality_service = QualityService()
```

### Configuration Fragmentation
- config/default.yaml
- Environment variables scattered
- Service-specific configs
- Hardcoded values:
  ```python
  neo4j_uri = "bolt://localhost:7687"
  neo4j_user = "neo4j"
  neo4j_password = "testpassword"  # Found in 15+ files!
  ```

## Implementation Plan

### Step 1: Create Service Interfaces (Day 1-2)

```python
# src/core/interfaces/service_interfaces.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class IdentityServiceInterface(ABC):
    @abstractmethod
    async def create_mention(self, surface_form: str, **kwargs) -> ServiceResponse:
        pass
    
    @abstractmethod
    async def resolve_entity(self, mention_id: str) -> ServiceResponse:
        pass

class ProvenanceServiceInterface(ABC):
    @abstractmethod
    async def start_operation(self, tool_id: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    async def complete_operation(self, operation_id: str, **kwargs) -> ServiceResponse:
        pass

class QualityServiceInterface(ABC):
    @abstractmethod
    async def assess_quality(self, data: Any, **kwargs) -> QualityScore:
        pass

# Service response standardization
@dataclass
class ServiceResponse:
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Step 2: Implement Service Container (Day 3-4)

```python
# src/core/service_container.py
from typing import Type, TypeVar, Dict, Any, Optional
import inspect

T = TypeVar('T')

class ServiceContainer:
    """Dependency injection container for service management"""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register(self, interface: Type[T], implementation: Type[T], singleton: bool = True):
        """Register a service implementation for an interface"""
        if singleton:
            self._singletons[interface] = None  # Lazy instantiation
        self._services[interface] = implementation
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]):
        """Register a factory function for complex service creation"""
        self._factories[interface] = factory
    
    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service by its interface"""
        # Check singletons first
        if interface in self._singletons:
            if self._singletons[interface] is None:
                self._singletons[interface] = self._create_instance(interface)
            return self._singletons[interface]
        
        # Check factories
        if interface in self._factories:
            return self._factories[interface]()
        
        # Create new instance
        if interface in self._services:
            return self._create_instance(interface)
        
        raise ValueError(f"No registration found for {interface}")
    
    def _create_instance(self, interface: Type[T]) -> T:
        """Create instance with dependency injection"""
        implementation = self._services[interface]
        
        # Get constructor parameters
        sig = inspect.signature(implementation.__init__)
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Try to resolve parameter type
            if param.annotation != param.empty:
                try:
                    kwargs[param_name] = self.resolve(param.annotation)
                except ValueError:
                    # Can't resolve, skip (will use default if available)
                    pass
        
        return implementation(**kwargs)

# src/core/container_config.py
def configure_container() -> ServiceContainer:
    """Configure the dependency injection container"""
    container = ServiceContainer()
    
    # Register services
    container.register(IdentityServiceInterface, IdentityService)
    container.register(ProvenanceServiceInterface, ProvenanceService)
    container.register(QualityServiceInterface, QualityService)
    
    # Register with factory for complex initialization
    container.register_factory(
        Neo4jManagerInterface,
        lambda: Neo4jManager(
            uri=config.get("neo4j.uri"),
            user=config.get("neo4j.user"),
            password=config.get("neo4j.password")
        )
    )
    
    return container
```

### Step 3: Refactor Services to Use DI (Day 5-6)

```python
# Before: Tight coupling
class AnalyticsService:
    def __init__(self):
        self.identity_service = IdentityService()
        self.provenance_service = ProvenanceService()

# After: Dependency injection
class AnalyticsService:
    def __init__(
        self,
        identity_service: IdentityServiceInterface,
        provenance_service: ProvenanceServiceInterface,
        quality_service: QualityServiceInterface
    ):
        self.identity_service = identity_service
        self.provenance_service = provenance_service
        self.quality_service = quality_service

# Usage with container
container = configure_container()
analytics_service = container.resolve(AnalyticsService)
```

### Step 4: Centralize Configuration (Day 7-8)

```python
# src/core/configuration/config_schema.py
from pydantic import BaseModel, Field
from typing import Optional

class DatabaseConfig(BaseModel):
    uri: str = Field(..., env="NEO4J_URI")
    user: str = Field(..., env="NEO4J_USER")
    password: str = Field(..., env="NEO4J_PASSWORD", min_length=8)
    pool_size: int = Field(10, env="NEO4J_POOL_SIZE")

class APIConfig(BaseModel):
    openai_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    google_key: Optional[str] = Field(None, env="GOOGLE_API_KEY")

class ApplicationConfig(BaseModel):
    database: DatabaseConfig
    api: APIConfig
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# src/core/configuration/config_manager.py
class ConfigManager:
    """Centralized configuration management"""
    _instance: Optional['ConfigManager'] = None
    _config: Optional[ApplicationConfig] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_config(self, config_path: str = "config/default.yaml") -> ApplicationConfig:
        """Load configuration from file and environment"""
        # Load base config from YAML
        with open(config_path) as f:
            yaml_config = yaml.safe_load(f)
        
        # Override with environment variables
        config_dict = deep_merge(yaml_config, os.environ)
        
        # Validate with schema
        self._config = ApplicationConfig(**config_dict)
        return self._config
    
    @property
    def config(self) -> ApplicationConfig:
        if self._config is None:
            self.load_config()
        return self._config
```

### Step 5: Remove Hardcoded Values (Day 9-10)

```python
# Find all hardcoded values
grep -r "bolt://localhost" src/
grep -r "neo4j.*password" src/
grep -r "api_key.*=" src/

# Replace with configuration
# Before:
neo4j_uri = "bolt://localhost:7687"
neo4j_password = "testpassword"

# After:
config = ConfigManager().config
neo4j_uri = config.database.uri
neo4j_password = config.database.password
```

## Migration Strategy

### Phase 1: Add New System (Don't Remove Old)
1. Implement interfaces alongside existing classes
2. Create service container
3. Register all services
4. Test container resolution

### Phase 2: Gradual Migration
1. Update one service at a time
2. Run tests after each change
3. Keep old initialization as fallback
4. Monitor for issues

### Phase 3: Remove Old System
1. Remove direct instantiation code
2. Remove hardcoded values
3. Update all imports
4. Final testing

## Testing Approach

```python
# tests/unit/core/test_service_container.py
class TestServiceContainer:
    def test_register_and_resolve(self):
        container = ServiceContainer()
        container.register(IdentityServiceInterface, MockIdentityService)
        
        service = container.resolve(IdentityServiceInterface)
        assert isinstance(service, MockIdentityService)
    
    def test_singleton_behavior(self):
        container = ServiceContainer()
        container.register(IdentityServiceInterface, IdentityService, singleton=True)
        
        service1 = container.resolve(IdentityServiceInterface)
        service2 = container.resolve(IdentityServiceInterface)
        assert service1 is service2
    
    def test_dependency_injection(self):
        container = configure_container()
        analytics = container.resolve(AnalyticsService)
        
        assert analytics.identity_service is not None
        assert isinstance(analytics.identity_service, IdentityServiceInterface)
```

## Success Criteria

### Week 3 Completion
- [ ] All service interfaces defined
- [ ] Service container implemented
- [ ] Container configuration complete
- [ ] 5+ services migrated to DI

### Week 4 Completion  
- [ ] All services using DI
- [ ] Zero hardcoded credentials
- [ ] Configuration fully centralized
- [ ] All tests passing
- [ ] Documentation updated

## Benefits
1. **Testability**: Easy to mock dependencies
2. **Flexibility**: Easy to swap implementations
3. **Configuration**: Single source of truth
4. **Maintainability**: Clear dependencies
5. **Security**: No hardcoded secrets

## Risks & Mitigation
- **Risk**: Breaking existing functionality
- **Mitigation**: Gradual migration with fallbacks
- **Risk**: Performance overhead
- **Mitigation**: Singleton pattern for services
- **Risk**: Complex debugging
- **Mitigation**: Clear error messages in container