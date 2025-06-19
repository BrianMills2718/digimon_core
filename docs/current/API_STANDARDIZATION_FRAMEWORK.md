# API Standardization Framework

**Purpose**: Prevent WorkflowStateService-type parameter mismatches across components  
**Root Cause**: Inconsistent interface contracts between phases and services  
**Solution**: Standardized API patterns with enforcement mechanisms

---

## Problem Analysis

### Historical API Mismatch Example
**Issue**: Phase 2 called WorkflowStateService with `current_step` parameter while service expected `step_number`
**Impact**: Complete Phase 1 → Phase 2 integration failure
**Root Cause**: No standardized interface contracts between components

### Current Risk Areas
1. **Parameter Naming**: Inconsistent names for same concepts (`step_number` vs `current_step`)
2. **Data Types**: Mixed string/integer types for IDs
3. **Return Formats**: Varying response structures across phases
4. **Error Handling**: Different exception types and error codes
5. **Async Patterns**: Mixed sync/async interfaces

---

## Standardization Principles

### 1. Consistent Naming Conventions
**Rule**: Use standardized parameter names across all interfaces

**Standard Parameters**:
```python
# Document processing
document_id: str          # Unique document identifier
document_path: str        # File path to document
document_content: str     # Raw document text

# Workflow state  
step_number: int          # Current step in workflow (NOT current_step)
phase_id: str            # Phase identifier (phase1, phase2, etc.)
workflow_id: str         # Unique workflow instance ID

# Entity processing
entity_id: str           # Unique entity identifier  
entity_type: str         # Entity classification
entity_text: str         # Original entity mention

# Relationship processing
relationship_id: str     # Unique relationship identifier
source_entity_id: str    # Source entity reference
target_entity_id: str    # Target entity reference
relationship_type: str   # Relationship classification

# Results and status
success: bool            # Operation success flag
error_message: str       # Human-readable error description
result_data: dict        # Structured result payload
```

### 2. Standardized Response Format
**Rule**: All API responses follow consistent structure

```python
# Standard Response Pattern
class StandardResponse:
    success: bool
    data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    metadata: Dict[str, Any]  # execution_time, version, etc.
    
# Success Response
{
    "success": true,
    "data": {
        "entities": [...],
        "relationships": [...]
    },
    "error_message": null,
    "metadata": {
        "execution_time": 1.23,
        "version": "1.0.0",
        "timestamp": "2025-06-19T10:30:00Z"
    }
}

# Error Response  
{
    "success": false,
    "data": null,
    "error_message": "Neo4j connection failed: Connection refused",
    "metadata": {
        "error_code": "NEO4J_CONNECTION_ERROR",
        "retry_after": 30,
        "timestamp": "2025-06-19T10:30:00Z"
    }
}
```

### 3. Interface Contract Definitions
**Rule**: All component interfaces must have explicit contracts

```python
# Example: Phase Interface Contract
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class PhaseInput:
    document_id: str
    document_path: str
    step_number: int
    workflow_id: str
    previous_results: Optional[Dict[str, Any]] = None

@dataclass 
class PhaseOutput:
    success: bool
    data: Dict[str, Any]
    error_message: Optional[str]
    metadata: Dict[str, Any]

class PhaseInterface(ABC):
    @abstractmethod
    def process(self, input_data: PhaseInput) -> PhaseOutput:
        """Process document through this phase"""
        pass
        
    @abstractmethod
    def validate_input(self, input_data: PhaseInput) -> bool:
        """Validate input data format"""
        pass
```

---

## Implementation Standards

### Service Interface Pattern
```python
# Standard Service Interface
class ServiceInterface(ABC):
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> StandardResponse:
        """Initialize service with configuration"""
        pass
        
    @abstractmethod  
    def health_check(self) -> StandardResponse:
        """Check service health status"""
        pass
        
    @abstractmethod
    def process(self, request: Dict[str, Any]) -> StandardResponse:
        """Process service request"""
        pass
        
    @abstractmethod
    def cleanup(self) -> StandardResponse:
        """Clean up service resources"""
        pass
```

### Error Handling Pattern
```python
# Standard Error Handling
class APIError(Exception):
    def __init__(self, message: str, error_code: str, retry_after: Optional[int] = None):
        self.message = message
        self.error_code = error_code  
        self.retry_after = retry_after
        super().__init__(self.message)

class WorkflowStateServiceError(APIError):
    pass

class Neo4jConnectionError(APIError):
    pass

# Standard Error Response Helper
def create_error_response(error: APIError) -> StandardResponse:
    return StandardResponse(
        success=False,
        data=None,
        error_message=error.message,
        metadata={
            "error_code": error.error_code,
            "retry_after": error.retry_after,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### Async/Await Consistency
```python
# All async operations follow same pattern
async def async_operation(input_data: Any) -> StandardResponse:
    try:
        result = await some_async_work(input_data)
        return StandardResponse(
            success=True,
            data=result,
            error_message=None,
            metadata={"execution_time": time.time()}
        )
    except Exception as e:
        return create_error_response(APIError(str(e), "ASYNC_ERROR"))
```

---

## Enforcement Mechanisms

### 1. Interface Validation Tests
```python
# tests/integration/test_api_contracts.py
def test_phase_interface_compliance():
    """Verify all phases implement standard interface"""
    for phase_class in [Phase1Workflow, Phase2Workflow, Phase3Workflow]:
        assert issubclass(phase_class, PhaseInterface)
        
def test_parameter_consistency():
    """Verify consistent parameter naming across components"""
    # Check WorkflowStateService uses step_number not current_step
    assert 'step_number' in WorkflowStateService.update_step.__annotations__
    assert 'current_step' not in WorkflowStateService.update_step.__annotations__
    
def test_response_format_compliance():
    """Verify all API responses follow StandardResponse format"""
    for service in [Phase1Service, Phase2Service, Neo4jService]:
        response = service.health_check()
        assert isinstance(response, StandardResponse)
        assert hasattr(response, 'success')
        assert hasattr(response, 'data')
        assert hasattr(response, 'error_message')
        assert hasattr(response, 'metadata')
```

### 2. Pre-commit Hooks
```bash
# .git/hooks/pre-commit
#!/bin/bash

# Check for API parameter consistency
echo "Checking API parameter consistency..."
if grep -r "current_step" src/ --include="*.py"; then
    echo "ERROR: Found 'current_step' parameter. Use 'step_number' instead."
    exit 1
fi

# Validate interface compliance
echo "Validating interface compliance..."
python scripts/validate_api_contracts.py
if [ $? -ne 0 ]; then
    echo "ERROR: API contract validation failed"
    exit 1
fi

# Check response format consistency
echo "Checking response format consistency..."  
python scripts/validate_response_formats.py
if [ $? -ne 0 ]; then
    echo "ERROR: Response format validation failed"
    exit 1
fi
```

### 3. Integration Test Gates
```python
# Mandatory tests before any API changes
class APIIntegrationTests:
    def test_cross_phase_communication(self):
        """Test Phase 1 → Phase 2 → Phase 3 data flow"""
        phase1_output = Phase1Workflow().process(test_input)
        assert phase1_output.success
        
        # Phase 2 should accept Phase 1 output without parameter mismatches
        phase2_input = create_phase2_input(phase1_output.data)
        phase2_output = Phase2Workflow().process(phase2_input) 
        assert phase2_output.success
        
    def test_service_parameter_compatibility(self):
        """Test service calls use correct parameter names"""
        workflow_service = WorkflowStateService()
        
        # Should work with step_number, not current_step
        response = workflow_service.update_step(
            workflow_id="test",
            step_number=2  # NOT current_step
        )
        assert response.success
```

---

## Migration Plan

### Phase 1: Current System Audit (Week 1)
- [ ] Identify all API parameter mismatches
- [ ] Document current interface variations
- [ ] Create compatibility mapping

### Phase 2: Standard Interface Implementation (Week 2-3)
- [ ] Implement StandardResponse class
- [ ] Create PhaseInterface base class  
- [ ] Migrate WorkflowStateService to standard parameters
- [ ] Update all service interfaces

### Phase 3: Validation Framework (Week 4)
- [ ] Create API contract validation tests
- [ ] Implement pre-commit hooks
- [ ] Add integration test gates
- [ ] Document enforcement procedures

### Phase 4: Rollout and Verification (Week 5)
- [ ] Deploy standardized interfaces
- [ ] Run comprehensive integration tests
- [ ] Verify no breaking changes
- [ ] Update all documentation

---

## Monitoring and Maintenance

### Ongoing Compliance Checks
```bash
# Daily automated checks
./scripts/check_api_compliance.sh

# Weekly comprehensive validation
./scripts/run_integration_contract_tests.sh

# Monthly interface review
./scripts/audit_api_consistency.sh
```

### Change Management Process
1. **API Change Proposal**: Document all interface modifications
2. **Impact Analysis**: Identify affected components
3. **Compatibility Testing**: Verify no breaking changes
4. **Documentation Update**: Update interface contracts
5. **Rollout Validation**: Confirm successful deployment

### Success Metrics
- **Zero Parameter Mismatches**: No WorkflowStateService-type errors
- **100% Interface Compliance**: All components follow StandardResponse
- **Integration Test Coverage**: 100% pass rate on cross-component tests
- **Documentation Accuracy**: All interface docs match implementation

---

**Implementation**: Deploy this framework immediately to prevent future API compatibility issues across the GraphRAG system.