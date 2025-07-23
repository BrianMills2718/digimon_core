# Task R4: Error Response Format Standardization

**Priority**: HIGH  
**Timeline**: 3-4 days  
**Status**: Pending  
**Dependencies**: Task R2 (Service Protocol Compliance)

## 🔥 **High Priority Issue**

**Files**: Multiple service files across `src/core/`  
**Problem**: Services return inconsistent error response formats, making error handling unpredictable and integration difficult.

## 📋 **Current Inconsistent Formats**

### **IdentityService Error Format**
```python
{
    "status": "error",
    "error": "message", 
    "confidence": 0.0
}
```

### **ProvenanceService Error Format** 
```python
{
    "status": "error",
    "error": "message"
}
```

### **QualityService Error Format**
```python
{
    "status": "error", 
    "error": "message",
    "confidence": 0.0
}
```

### **Neo4j Error Handler Format**
```python
{
    "status": "error",
    "error": "Neo4j database unavailable",
    "message": "Cannot perform operation without database connection",
    "details": "connection error details",
    "recovery_suggestions": [...],
    "operation": "operation_name"
}
```

## 🎯 **Standardized Error Response Format**

### **Unified Error Response Schema**
```python
# src/core/standard_response.py - New file

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class ErrorSeverity(Enum):
    LOW = "low"          # Minor issues, system continues
    MEDIUM = "medium"    # Significant issues, some degradation  
    HIGH = "high"        # Major issues, service impacted
    CRITICAL = "critical"  # System-threatening issues

class ErrorCategory(Enum):
    VALIDATION = "validation"      # Input validation errors
    CONFIGURATION = "configuration"  # Configuration errors
    DATABASE = "database"          # Database connectivity/operation errors  
    SERVICE = "service"            # Service-to-service communication errors
    RESOURCE = "resource"          # Resource exhaustion/unavailability
    SECURITY = "security"          # Authentication/authorization errors
    UNKNOWN = "unknown"            # Uncategorized errors

@dataclass(frozen=True)
class StandardErrorResponse:
    """Standardized error response format for all services"""
    
    # Core error information
    status: str = "error"  # Always "error" for error responses
    error_code: str        # Specific error code (e.g., "DATABASE_UNAVAILABLE")
    error_message: str     # Human-readable error message
    
    # Error classification
    severity: ErrorSeverity
    category: ErrorCategory
    
    # Context information
    timestamp: str         # ISO 8601 timestamp
    service_name: str      # Service that generated the error
    operation: str         # Operation that failed
    
    # Recovery and debugging
    recovery_suggestions: List[str]  # Actionable recovery steps
    debug_info: Dict[str, Any]       # Technical details for debugging
    
    # Optional fields
    correlation_id: Optional[str] = None  # For tracing across services
    user_message: Optional[str] = None    # User-friendly message
    documentation_url: Optional[str] = None  # Link to relevant docs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "status": self.status,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "severity": self.severity.value,
            "category": self.category.value,
            "timestamp": self.timestamp,
            "service_name": self.service_name,
            "operation": self.operation,
            "recovery_suggestions": self.recovery_suggestions,
            "debug_info": self.debug_info,
            "correlation_id": self.correlation_id,
            "user_message": self.user_message,
            "documentation_url": self.documentation_url
        }

@dataclass(frozen=True)
class StandardSuccessResponse:
    """Standardized success response format for all services"""
    
    status: str = "success"  # Always "success" for success responses
    data: Any                # Response data (can be any type)
    
    # Metadata
    timestamp: str           # ISO 8601 timestamp
    service_name: str        # Service that generated the response
    operation: str           # Operation that succeeded
    
    # Performance metrics
    execution_time_ms: float  # Execution time in milliseconds
    
    # Optional fields
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            "status": self.status,
            "data": self.data,
            "timestamp": self.timestamp,
            "service_name": self.service_name,
            "operation": self.operation,
            "execution_time_ms": self.execution_time_ms
        }
        
        if self.correlation_id:
            result["correlation_id"] = self.correlation_id
        if self.metadata:
            result["metadata"] = self.metadata
            
        return result

# Utility functions for creating standard responses
def create_error_response(
    error_code: str,
    error_message: str,
    service_name: str,
    operation: str,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    recovery_suggestions: List[str] = None,
    debug_info: Dict[str, Any] = None,
    **kwargs
) -> StandardErrorResponse:
    """Create standardized error response"""
    
    return StandardErrorResponse(
        error_code=error_code,
        error_message=error_message,
        severity=severity,
        category=category,
        timestamp=datetime.now().isoformat(),
        service_name=service_name,
        operation=operation,
        recovery_suggestions=recovery_suggestions or [],
        debug_info=debug_info or {},
        **kwargs
    )

def create_success_response(
    data: Any,
    service_name: str,
    operation: str,
    execution_time_ms: float,
    **kwargs
) -> StandardSuccessResponse:
    """Create standardized success response"""
    
    return StandardSuccessResponse(
        data=data,
        timestamp=datetime.now().isoformat(),
        service_name=service_name,
        operation=operation,
        execution_time_ms=execution_time_ms,
        **kwargs
    )
```

## 🔧 **Service Migration Plan**

### **Step 1: Update IdentityService**
```python
# src/core/identity_service.py - Standardized responses

from src.core.standard_response import (
    create_error_response, create_success_response,
    ErrorSeverity, ErrorCategory
)
import time

class IdentityService:
    def create_mention(
        self, 
        surface_form: str, 
        start_pos: int, 
        end_pos: int,
        source_ref: str, 
        entity_type: str = None,
        confidence: float = 0.8
    ) -> Dict[str, Any]:
        """Create mention with standardized response format"""
        
        start_time = time.time()
        
        try:
            # Input validation with standard error format
            if not surface_form or not surface_form.strip():
                return create_error_response(
                    error_code="INVALID_SURFACE_FORM",
                    error_message="Surface form cannot be empty or whitespace only",
                    service_name="IdentityService",
                    operation="create_mention",
                    severity=ErrorSeverity.LOW,
                    category=ErrorCategory.VALIDATION,
                    recovery_suggestions=[
                        "Provide a non-empty surface form",
                        "Check that surface form contains actual text content",
                        "Verify text extraction is working correctly"
                    ],
                    debug_info={
                        "surface_form_length": len(surface_form),
                        "surface_form_stripped": surface_form.strip()
                    }
                ).to_dict()
            
            if start_pos < 0 or end_pos <= start_pos:
                return create_error_response(
                    error_code="INVALID_POSITION_RANGE",
                    error_message=f"Invalid position range: start={start_pos}, end={end_pos}",
                    service_name="IdentityService", 
                    operation="create_mention",
                    severity=ErrorSeverity.LOW,
                    category=ErrorCategory.VALIDATION,
                    recovery_suggestions=[
                        "Ensure start_pos >= 0",
                        "Ensure end_pos > start_pos",
                        "Check text indexing calculations"
                    ],
                    debug_info={
                        "start_pos": start_pos,
                        "end_pos": end_pos,
                        "range_size": end_pos - start_pos
                    }
                ).to_dict()
            
            # Create mention
            mention_data = self._create_mention_internal(
                surface_form, start_pos, end_pos, source_ref, entity_type, confidence
            )
            
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return create_success_response(
                data=mention_data,
                service_name="IdentityService",
                operation="create_mention", 
                execution_time_ms=execution_time,
                metadata={
                    "entity_type": entity_type,
                    "confidence": confidence,
                    "source_ref": source_ref
                }
            ).to_dict()
            
        except DatabaseConnectionError as e:
            return create_error_response(
                error_code="DATABASE_CONNECTION_FAILED",
                error_message=f"Failed to connect to identity database: {str(e)}",
                service_name="IdentityService",
                operation="create_mention",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
                recovery_suggestions=getattr(e, 'recovery_suggestions', [
                    "Check database server status",
                    "Verify database credentials",
                    "Check network connectivity"
                ]),
                debug_info={
                    "database_type": getattr(e, 'database_type', 'unknown'),
                    "original_error": str(e)
                }
            ).to_dict()
            
        except Exception as e:
            return create_error_response(
                error_code="MENTION_CREATION_FAILED",
                error_message=f"Unexpected error during mention creation: {str(e)}",
                service_name="IdentityService",
                operation="create_mention",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.UNKNOWN,
                recovery_suggestions=[
                    "Check service logs for detailed error information",
                    "Verify all required dependencies are available",
                    "Try the operation again with the same parameters",
                    "Contact system administrator if error persists"
                ],
                debug_info={
                    "error_type": type(e).__name__,  
                    "surface_form": surface_form,
                    "positions": f"{start_pos}-{end_pos}"
                }
            ).to_dict()
```

### **Step 2: Update ProvenanceService**
```python  
# src/core/provenance_service.py - Standardized responses

class ProvenanceService:
    def start_operation(
        self,
        tool_id: str,
        operation_type: str, 
        inputs: List[str],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Start operation tracking with standardized response"""
        
        start_time = time.time()
        
        try:
            # Validation
            if not tool_id:
                return create_error_response(
                    error_code="INVALID_TOOL_ID",
                    error_message="Tool ID cannot be empty",
                    service_name="ProvenanceService",
                    operation="start_operation",
                    severity=ErrorSeverity.LOW,
                    category=ErrorCategory.VALIDATION,
                    recovery_suggestions=[
                        "Provide a valid tool ID",
                        "Check tool registration",
                        "Verify tool configuration"
                    ],
                    debug_info={"provided_tool_id": repr(tool_id)}
                ).to_dict()
            
            # Start tracking
            operation_id = self._start_operation_internal(
                tool_id, operation_type, inputs, parameters
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            return create_success_response(
                data={"operation_id": operation_id},
                service_name="ProvenanceService",
                operation="start_operation",
                execution_time_ms=execution_time,
                metadata={
                    "tool_id": tool_id,
                    "operation_type": operation_type,
                    "input_count": len(inputs),
                    "parameter_count": len(parameters)
                }
            ).to_dict()
            
        except Exception as e:
            return create_error_response(
                error_code="OPERATION_START_FAILED",
                error_message=f"Failed to start operation tracking: {str(e)}",
                service_name="ProvenanceService", 
                operation="start_operation",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.SERVICE,
                recovery_suggestions=[
                    "Check provenance service health",
                    "Verify operation tracking storage is available",
                    "Check for resource constraints"
                ],
                debug_info={
                    "tool_id": tool_id,
                    "operation_type": operation_type,
                    "error_type": type(e).__name__
                }
            ).to_dict()
```

### **Step 3: Response Validation Framework**
```python
# src/core/response_validator.py - New file

from typing import Dict, Any, List
import jsonschema

# JSON Schema for standard error responses
ERROR_RESPONSE_SCHEMA = {
    "type": "object",
    "required": [
        "status", "error_code", "error_message", "severity", 
        "category", "timestamp", "service_name", "operation",
        "recovery_suggestions", "debug_info"
    ],
    "properties": {
        "status": {"type": "string", "enum": ["error"]},
        "error_code": {"type": "string", "minLength": 1},
        "error_message": {"type": "string", "minLength": 1},
        "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
        "category": {"type": "string", "enum": [
            "validation", "configuration", "database", 
            "service", "resource", "security", "unknown"
        ]},
        "timestamp": {"type": "string"},  # ISO 8601 format
        "service_name": {"type": "string", "minLength": 1},
        "operation": {"type": "string", "minLength": 1}, 
        "recovery_suggestions": {
            "type": "array",
            "items": {"type": "string", "minLength": 1}
        },
        "debug_info": {"type": "object"},
        "correlation_id": {"type": ["string", "null"]},
        "user_message": {"type": ["string", "null"]},
        "documentation_url": {"type": ["string", "null"]}
    },
    "additionalProperties": False
}

# JSON Schema for standard success responses  
SUCCESS_RESPONSE_SCHEMA = {
    "type": "object",
    "required": [
        "status", "data", "timestamp", "service_name", 
        "operation", "execution_time_ms"
    ],
    "properties": {
        "status": {"type": "string", "enum": ["success"]},
        "data": {},  # Can be any type
        "timestamp": {"type": "string"},
        "service_name": {"type": "string", "minLength": 1},
        "operation": {"type": "string", "minLength": 1},
        "execution_time_ms": {"type": "number", "minimum": 0},
        "correlation_id": {"type": ["string", "null"]},
        "metadata": {"type": ["object", "null"]}
    },
    "additionalProperties": False
}

class ResponseValidator:
    """Validate service responses against standard schemas"""
    
    @staticmethod
    def validate_error_response(response: Dict[str, Any]) -> List[str]:
        """Validate error response format, return list of issues"""
        issues = []
        
        try:
            jsonschema.validate(response, ERROR_RESPONSE_SCHEMA)
        except jsonschema.ValidationError as e:
            issues.append(f"Schema validation failed: {e.message}")
        
        # Additional semantic validation
        if response.get("status") != "error":
            issues.append("Error responses must have status='error'")
        
        if not response.get("recovery_suggestions"):
            issues.append("Error responses must include recovery suggestions")
        
        return issues
    
    @staticmethod
    def validate_success_response(response: Dict[str, Any]) -> List[str]:
        """Validate success response format, return list of issues"""
        issues = []
        
        try:
            jsonschema.validate(response, SUCCESS_RESPONSE_SCHEMA)
        except jsonschema.ValidationError as e:
            issues.append(f"Schema validation failed: {e.message}")
        
        if response.get("status") != "success":
            issues.append("Success responses must have status='success'")
        
        return issues
    
    @staticmethod
    def validate_service_responses(service_responses: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Validate multiple service responses"""
        results = {}
        
        for i, response in enumerate(service_responses):
            response_id = f"response_{i}"
            
            if response.get("status") == "error":
                issues = ResponseValidator.validate_error_response(response)
            elif response.get("status") == "success":
                issues = ResponseValidator.validate_success_response(response)
            else:
                issues = ["Response must have status 'success' or 'error'"]
            
            if issues:
                results[response_id] = issues
        
        return results
```

## 🧪 **Testing Strategy**

### **Response Format Validation Tests**
```python
def test_all_services_use_standard_error_format():
    """Test that all services return standardized error responses"""
    
    services = [
        IdentityService(),
        ProvenanceService(),
        QualityService(),
        WorkflowStateService()
    ]
    
    for service in services:
        # Test with invalid inputs to trigger errors
        error_response = service.some_method(invalid_input="")
        
        # Validate error response format
        issues = ResponseValidator.validate_error_response(error_response)
        assert not issues, f"Service {service.__class__.__name__} error format issues: {issues}"
        
        # Check required fields
        assert error_response["status"] == "error"
        assert error_response["error_code"]
        assert error_response["recovery_suggestions"]
        assert error_response["service_name"] == service.__class__.__name__

def test_error_messages_are_actionable():
    """Test that error messages provide actionable recovery guidance"""
    
    service = IdentityService()
    response = service.create_mention("", -1, -1, "")
    
    assert response["status"] == "error"
    assert len(response["recovery_suggestions"]) > 0
    assert all(len(suggestion) > 10 for suggestion in response["recovery_suggestions"])
    
    # Should include specific guidance
    suggestions_text = " ".join(response["recovery_suggestions"]).lower()
    assert any(keyword in suggestions_text for keyword in ["check", "verify", "ensure", "provide"])

def test_success_responses_include_timing():
    """Test that success responses include execution timing"""
    
    service = IdentityService()
    response = service.create_mention("test entity", 0, 10, "source123")
    
    assert response["status"] == "success"
    assert "execution_time_ms" in response
    assert isinstance(response["execution_time_ms"], (int, float))
    assert response["execution_time_ms"] >= 0
```

## 📝 **Implementation Steps**

### **Day 1: Infrastructure**
1. **Create Standard Response Classes**: Implement `StandardErrorResponse` and `StandardSuccessResponse`
2. **Create Response Validator**: Schema validation and testing utilities
3. **Define Error Codes**: Comprehensive error code enumeration

### **Day 2-3: Service Migration**
1. **Update IdentityService**: Migrate to standard response format
2. **Update ProvenanceService**: Migrate to standard response format  
3. **Update QualityService**: Migrate to standard response format
4. **Update WorkflowStateService**: Migrate to standard response format

### **Day 4: Integration and Testing**
1. **Integration Testing**: Test service-to-service communication with new formats
2. **Tool Integration**: Update tools to handle standardized responses
3. **Response Validation**: Add response validation to CI/CD pipeline

## ✅ **Success Criteria**

1. **Format Consistency**: All services use identical error/success response formats
2. **Schema Compliance**: All responses pass schema validation
3. **Actionable Errors**: All error responses include specific recovery guidance
4. **Performance Tracking**: All responses include execution timing
5. **Debugging Support**: All errors include sufficient debug information
6. **Integration Works**: Tools and services handle new formats correctly

## 🚫 **Risks and Mitigation**

### **Risk 1: Breaking Tool Integration**
- **Mitigation**: Maintain backward compatibility during transition
- **Validation**: Test all tool integrations with new response formats

### **Risk 2: Response Size Inflation**
- **Mitigation**: Keep debug info concise, optional fields truly optional
- **Validation**: Monitor response sizes before/after

### **Risk 3: Performance Impact**
- **Mitigation**: Minimize response construction overhead
- **Validation**: Performance benchmarks for response creation

This task establishes the foundation for reliable error handling and debugging across the entire system.