# Service API Documentation

**Date**: 2025-08-05  
**Purpose**: Document actual service APIs to resolve interface mismatches

## ProvenanceService API

**Location**: `src/services/provenance_service.py`  
**Database**: SQLite

### Available Methods

```python
class ProvenanceService:
    def __init__(self, connection=None)
    
    def start_operation(self, tool_id: str, operation_type: str,
                       inputs: List[Any] = None, parameters: Dict[str, Any] = None) -> str
    
    def complete_operation(self, operation_id: str, outputs: List[Any] = None,
                         success: bool = True, error_message: str = None,
                         metadata: Dict[str, Any] = None) -> bool
    
    def add_lineage(self, source_operation_id: str, target_operation_id: str,
                    relationship_type: str = "derived_from") -> bool
    
    def get_operation(self, operation_id: str) -> Optional[Dict[str, Any]]
    
    def get_lineage(self, operation_id: str, direction: str = "both") -> List[Dict[str, Any]]
    
    def get_statistics(self) -> Dict[str, Any]
    
    def cleanup(self)
```

### Missing Method
**Expected**: `create_tool_execution_record`  
**Actual**: Use `start_operation` and `complete_operation` pair

### Recommended Adapter
```python
def create_tool_execution_record(self, tool_id: str, workflow_id: str, 
                               input_summary: str, success: bool,
                               error_message: Optional[str] = None,
                               execution_time: float = 0.0):
    """Adapter method for expected interface"""
    operation_id = self.start_operation(
        tool_id=tool_id,
        operation_type="tool_execution",
        inputs=[input_summary],
        parameters={"workflow_id": workflow_id}
    )
    
    if success:
        self.complete_operation(
            operation_id=operation_id,
            success=True,
            metadata={"execution_time": execution_time}
        )
    else:
        self.complete_operation(
            operation_id=operation_id,
            success=False,
            error_message=error_message,
            metadata={"execution_time": execution_time}
        )
    
    return operation_id
```

## IdentityService API

**Location**: `src/services/identity_service.py`  
**Database**: Neo4j

### Available Methods

```python
class IdentityService:
    def __init__(self, neo4j_driver)
    
    def create_mention(self, surface_form: str, start_pos: int, end_pos: int,
                      source_ref: str, entity_type: str = None, 
                      confidence: float = 1.0, properties: Dict[str, Any] = None,
                      entity_id: Optional[str] = None) -> str
    
    def get_entity_by_mention(self, mention_id: str) -> Optional[Dict[str, Any]]
    
    def merge_entities(self, entity_ids: List[str]) -> Optional[str]
    
    def find_similar_entities(self, surface_form: str, entity_type: str = None,
                            threshold: float = 0.8) -> List[Dict[str, Any]]
    
    def get_statistics(self) -> Dict[str, int]
```

### Missing Method
**Expected**: `resolve_entity`  
**Actual**: Use combination of `find_similar_entities` and `create_mention`

### Recommended Adapter
```python
def resolve_entity(self, surface_form: str, entity_type: str = None,
                  source_ref: str = None, confidence: float = 1.0) -> str:
    """Adapter method for expected interface"""
    # First try to find similar entities
    similar = self.find_similar_entities(
        surface_form=surface_form,
        entity_type=entity_type,
        threshold=0.8
    )
    
    if similar:
        # Use existing entity
        entity_id = similar[0]['entity_id']
    else:
        # Create new entity (via mention)
        entity_id = str(uuid.uuid4())
    
    # Create mention linked to entity
    mention_id = self.create_mention(
        surface_form=surface_form,
        start_pos=0,  # Default when not provided
        end_pos=len(surface_form),
        source_ref=source_ref or "unknown",
        entity_type=entity_type,
        confidence=confidence,
        entity_id=entity_id
    )
    
    return entity_id
```

## QualityService API

**Location**: `src/services/quality_service.py`  
**Database**: Neo4j

### Available Methods

Based on the service description, QualityService should provide:

```python
class QualityService:
    def __init__(self, neo4j_driver)
    
    # Expected methods (need verification):
    def calculate_confidence(self, ...) -> float
    def assess_quality(self, ...) -> Dict[str, Any]
    def track_metrics(self, ...) -> None
```

**Status**: Need to verify actual implementation

## Service Interface Alignment

### Current State
- Services have evolved independently
- Tool expectations don't match service interfaces
- Adapter methods needed for compatibility

### Migration Strategy

#### Option 1: Add Adapter Methods to Services
```python
# In ProvenanceService
def create_tool_execution_record(self, ...):
    """Compatibility method for tools expecting this interface"""
    # Implementation using existing methods

# In IdentityService  
def resolve_entity(self, ...):
    """Compatibility method for tools expecting this interface"""
    # Implementation using existing methods
```

#### Option 2: Update Tool Expectations
- Modify tools to use actual service methods
- More work but cleaner long-term solution

#### Option 3: Service Facade Pattern
```python
class ServiceFacade:
    """Provides expected interfaces using actual services"""
    
    def __init__(self, provenance_service, identity_service, quality_service):
        self.provenance = provenance_service
        self.identity = identity_service
        self.quality = quality_service
    
    def create_tool_execution_record(self, ...):
        # Adapter implementation
    
    def resolve_entity(self, ...):
        # Adapter implementation
```

## Recommendations

### Immediate Actions
1. **Add adapter methods** to services for backward compatibility
2. **Document the adapters** as temporary compatibility layer
3. **Plan migration** to actual service methods

### Long-term Actions
1. **Standardize service interfaces** across all services
2. **Update tools** to use actual service methods
3. **Remove adapter methods** once migration complete

## Service Discovery Pattern

Tools currently get services through ServiceManager:

```python
from src.core.service_manager import ServiceManager

service_manager = ServiceManager()
provenance = service_manager.provenance_service
identity = service_manager.identity_service
quality = service_manager.quality_service
```

This provides opportunity to inject adapted services if needed.

## Testing Service Compatibility

### Test Scripts

```python
# Test ProvenanceService
from src.services.provenance_service import ProvenanceService

ps = ProvenanceService()
op_id = ps.start_operation("TEST_TOOL", "test", ["input"])
ps.complete_operation(op_id, ["output"], True)
print(f"Operation {op_id} tracked successfully")

# Test IdentityService (requires Neo4j)
from neo4j import GraphDatabase
from src.services.identity_service import IdentityService

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", ""))
identity = IdentityService(driver)
mention_id = identity.create_mention("Test Entity", 0, 11, "test_doc")
print(f"Mention {mention_id} created successfully")
```

## Next Steps

1. **Verify QualityService methods** - Check actual implementation
2. **Implement adapter methods** - Add compatibility layer
3. **Test with tools** - Verify tools work with adapted services
4. **Document migration plan** - Plan to remove adapters