# Core Services Module - CLAUDE.md

## Overview
The `src/core/` directory contains the foundational services that all other tools depend on. This module implements the core architecture patterns, service management, and infrastructure components for the GraphRAG system.

## Core Services Architecture

### Service Manager Pattern
- **Singleton Pattern**: All core services use singleton pattern for shared instances
- **ServiceManager**: Central service registry providing shared instances across tools
- **Lazy Loading**: Services are created on first access, not at initialization
- **Thread Safety**: All services use proper locking for thread-safe initialization

### Core Services (T-Series)
- **T107: Identity Service** (`identity_service.py`) - Mention/entity management
- **T110: Provenance Service** (`provenance_service.py`) - Operation tracking
- **T111: Quality Service** (`quality_service.py`) - Confidence management  
- **T121: Workflow State Service** (`workflow_state_service.py`) - Checkpoint/restore

## Configuration Management

### Unified Configuration System
- **ConfigurationManager**: Singleton pattern with thread-safe initialization
- **YAML Configuration**: Primary configuration format with environment overrides
- **Environment Variables**: Automatic override of config values from environment
- **Validation**: JSON Schema validation for configuration integrity

### Configuration Structure
```python
# Core configuration classes
EntityProcessingConfig    # Entity processing parameters
TextProcessingConfig      # Text processing parameters  
GraphConstructionConfig   # Graph construction parameters
APIConfig                 # API interaction settings
Neo4jConfig              # Database connection settings
WorkflowConfig           # Workflow management settings
SystemConfig             # Complete system configuration
```

### Configuration Loading
```python
from src.core.config import get_config, load_config

# Load with defaults
config = get_config()

# Load from specific file
config = load_config("config/production.yaml")

# Force reload
config = load_config("config/new.yaml", force_reload=True)
```

## Tool Protocol & Adapters

### Tool Interface (Tool Protocol)
All tools must implement the `Tool` abstract base class:
```python
class Tool(ABC):
    @abstractmethod
    def execute(self, input_data: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]
    
    @abstractmethod
    def get_tool_info(self) -> Dict[str, Any]
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult
```

### Tool Adapters Pattern
- **BaseToolAdapter**: Base class for all tool adapters with centralized configuration
- **SimplifiedToolAdapter**: Eliminates boilerplate for common tool patterns
- **ToolAdapterBridge**: Bridges existing tools to unified Tool protocol
- **Registry Pattern**: OptimizedToolAdapterRegistry for adapter management

### Adapter Creation
```python
from src.core.tool_adapters import create_simplified_adapter

# Create simplified adapter
adapter = create_simplified_adapter(
    tool_class=PDFLoader,
    tool_method="load_pdf",
    input_key="pdf_path",
    output_key="text_chunks"
)
```

## Pipeline Orchestration

### PipelineOrchestrator
- **Unified Execution**: Single orchestrator for all workflow types
- **Phase Support**: PHASE1, PHASE2, PHASE3 with different optimization levels
- **Optimization Levels**: STANDARD, OPTIMIZED, ENHANCED
- **Tool Protocol Integration**: Uses Tool interface for consistent execution

### Pipeline Configuration
```python
from src.core.pipeline_orchestrator import PipelineConfig, OptimizationLevel, Phase

config = PipelineConfig(
    tools=[tool1, tool2, tool3],
    optimization_level=OptimizationLevel.OPTIMIZED,
    phase=Phase.PHASE1,
    confidence_threshold=0.7
)
```

## Error Handling & Validation

### Production Error Handler
- **Circuit Breaker Pattern**: Real circuit breakers for different service types
- **Fail-Fast Philosophy**: Critical errors fail immediately
- **Graceful Degradation**: Non-critical errors return degraded responses
- **Service Types**: database, api, file_system, service

### Contract Validation
- **ContractValidator**: Validates tool implementations against contracts
- **Schema Validation**: JSON Schema validation for input/output contracts
- **Interface Validation**: Ensures tool instances match declared interfaces
- **Data Flow Validation**: Validates data flow through tool chains

### Error Patterns
```python
from src.core.error_handler import ProductionErrorHandler

handler = ProductionErrorHandler()

# Database errors - fail fast
try:
    db_operation()
except Exception as e:
    handler.handle_database_error(e, "query_entities")

# API errors - graceful degradation  
try:
    api_call()
except Exception as e:
    result = handler.handle_api_error(e, "openai_embedding")
    if result and result.get('fallback_used'):
        # Use fallback response
```

## Logging & Monitoring

### Centralized Logging
- **Structured Logging**: Consistent logging format across all components
- **Logger Factory**: `get_logger()` function with namespace prefixing
- **Component Loggers**: Specialized loggers for different system components
- **Environment Configuration**: Log level and output controlled via environment

### Logging Patterns
```python
from src.core.logging_config import get_logger, log_operation_start, log_operation_end

logger = get_logger("core.service_name")

# Operation logging
log_operation_start(logger, "process_document", doc_id="123", phase="extraction")
# ... operation code ...
log_operation_end(logger, "process_document", duration=2.5, success=True, entities=15)

# Tool execution logging
log_tool_execution(logger, "PDFLoader", "doc.pdf", True, 1.2)
```

### Monitoring Integration
- **Prometheus Metrics**: Built-in metrics collection
- **Grafana Dashboards**: Pre-configured monitoring dashboards
- **Health Checks**: Comprehensive health checking system
- **Distributed Tracing**: Async operation tracing

## Data Models & Schemas

### Core Data Models
- **StandardEntity**: Standardized entity representation
- **StandardRelationship**: Standardized relationship representation
- **EntitySchema**: Entity schema definitions and validation
- **SchemaEnforcer**: Runtime schema enforcement

### Schema Validation
```python
from src.core.schema_enforcer import SchemaEnforcer

enforcer = SchemaEnforcer(production_mode=True)
validation_result = enforcer.validate_entity(entity_data)
```

## Service Integration Patterns

### Service Creation
```python
from src.core.service_manager import get_service_manager

# Get shared service manager
service_manager = get_service_manager()

# Get shared services
identity_service = service_manager.identity_service
provenance_service = service_manager.provenance_service
quality_service = service_manager.quality_service
neo4j_driver = service_manager.get_neo4j_driver()
```

### Service Configuration
```python
# Configure identity service before first use
service_manager.configure_identity_service(
    use_embeddings=True,
    persistence_path="./data/entities.db",
    similarity_threshold=0.85
)
```

## Workflow State Management

### Checkpoint System
- **WorkflowCheckpoint**: Serializable workflow state snapshots
- **WorkflowProgress**: Progress tracking for long operations
- **Recovery**: Automatic recovery from checkpoints on restart
- **Storage**: JSON-based checkpoint storage with metadata

### Workflow Patterns
```python
from src.core.workflow_state_service import WorkflowStateService

state_service = WorkflowStateService("./data/workflows")

# Start workflow
workflow_id = state_service.start_workflow("document_processing", 5)

# Create checkpoint
checkpoint_id = state_service.create_checkpoint(
    workflow_id=workflow_id,
    step_name="entity_extraction",
    step_number=2,
    state_data={"entities": [...], "relationships": [...]}
)

# Restore from checkpoint
state_data = state_service.restore_from_checkpoint(checkpoint_id)
```

## Common Commands & Workflows

### Development Commands
```bash
# Run core service tests
python -m pytest tests/unit/core/ -v

# Validate all contracts
python -c "from src.core.contract_validator import validate_all_contracts; validate_all_contracts()"

# Check service health
python -c "from src.core.health_checker import HealthChecker; HealthChecker().run_all_checks()"

# Generate configuration schema
python -c "from src.core.config import ConfigurationManager; print(ConfigurationManager().validate_config())"
```

### Debugging Commands
```bash
# Check circuit breaker status
python -c "from src.core.error_handler import ProductionErrorHandler; print(ProductionErrorHandler().get_circuit_breaker_status())"

# View service statistics
python -c "from src.core.service_manager import get_service_manager; print(get_service_manager().get_service_stats())"

# Check workflow checkpoints
python -c "from src.core.workflow_state_service import WorkflowStateService; print(WorkflowStateService().get_service_statistics())"
```

## Code Style & Conventions

### File Organization
- **Service Files**: One service per file with clear naming (e.g., `identity_service.py`)
- **Configuration**: Centralized in `config.py` with dataclass-based structure
- **Protocols**: Abstract base classes in separate files (e.g., `tool_protocol.py`)
- **Adapters**: Tool adapters in `tool_adapters.py` with clear naming

### Naming Conventions
- **Classes**: PascalCase (e.g., `IdentityService`, `PipelineOrchestrator`)
- **Methods**: snake_case (e.g., `create_mention`, `validate_input`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_CONFIDENCE_THRESHOLD`)
- **Private Methods**: Leading underscore (e.g., `_init_database`, `_load_config`)

### Error Handling Patterns
- **Fail Fast**: Critical errors raise exceptions immediately
- **Graceful Degradation**: Non-critical errors return error dictionaries
- **Circuit Breakers**: Service-level failure protection
- **Validation**: Comprehensive input/output validation

### Logging Patterns
- **Structured Logging**: Use `get_logger()` with component names
- **Operation Logging**: Use `log_operation_start/end()` for timing
- **Error Logging**: Log errors with context and severity
- **Debug Logging**: Use DEBUG level for detailed troubleshooting

## Integration Points

### External Dependencies
- **Neo4j**: Graph database integration via `neo4j_manager.py`
- **OpenAI API**: Embedding and LLM services via `enhanced_api_client.py`
- **Google API**: Gemini integration via `async_api_client.py`
- **SQLite**: Local persistence for services

### Internal Dependencies
- **Tools**: All tools depend on core services
- **Workflows**: Pipeline orchestrators use core services
- **UI**: User interfaces integrate with core services
- **Testing**: Test frameworks use core service mocks

## Performance Considerations

### Optimization Patterns
- **Lazy Loading**: Services created on first access
- **Connection Pooling**: Neo4j connection pooling via ServiceManager
- **Caching**: Embedding and configuration caching
- **Async Operations**: Async API clients for non-blocking operations

### Memory Management
- **Singleton Services**: Shared instances prevent duplication
- **Resource Cleanup**: Proper cleanup of database connections
- **Checkpoint Cleanup**: Automatic cleanup of old checkpoints
- **Cache Limits**: Bounded caches to prevent memory leaks

## Security Considerations

### PII Handling
- **PII Service**: Dedicated service for PII redaction and storage
- **Encryption**: PII data encrypted at rest
- **Access Control**: Environment-based PII service configuration
- **Audit Trail**: PII operations logged for compliance

### Input Validation
- **Schema Validation**: JSON Schema validation for all inputs
- **Security Validation**: Path traversal and injection attack detection
- **Size Limits**: Input size limits to prevent DoS attacks
- **Sanitization**: Input sanitization before processing

## Testing Patterns

### Unit Testing
- **Service Isolation**: Each service tested independently
- **Mock Dependencies**: External dependencies mocked
- **Contract Testing**: Tool contracts validated automatically
- **Error Scenarios**: Comprehensive error scenario testing

### Integration Testing
- **Service Integration**: Core services tested together
- **End-to-End**: Complete pipeline testing
- **Performance Testing**: Load and stress testing
- **Recovery Testing**: Checkpoint and recovery testing

## Troubleshooting

### Common Issues
1. **Service Initialization Failures**: Check configuration and dependencies
2. **Circuit Breaker Trips**: Monitor error patterns and service health
3. **Checkpoint Corruption**: Validate checkpoint file integrity
4. **Memory Leaks**: Monitor service instance counts and cache sizes

### Debug Commands
```bash
# Check service health
python -c "from src.core.health_checker import HealthChecker; HealthChecker().run_all_checks()"

# Validate configuration
python -c "from src.core.config import get_config; print(get_config().validate_config())"

# Check circuit breakers
python -c "from src.core.error_handler import ProductionErrorHandler; print(ProductionErrorHandler().get_circuit_breaker_status())"
```

## Migration & Upgrades

### Configuration Migration
- **Backward Compatibility**: Old config formats supported with warnings
- **Migration Scripts**: Automated migration of configuration files
- **Validation**: Configuration validation after migration
- **Rollback**: Ability to rollback to previous configurations

### Service Upgrades
- **Version Compatibility**: Service version compatibility checking
- **Gradual Migration**: Support for running multiple service versions
- **Data Migration**: Automatic data format migration
- **Downtime Minimization**: Zero-downtime upgrade strategies 