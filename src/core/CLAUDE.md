# Core Services Implementation Instructions

## Mission
Implement and fix all core services (T107, T110, T111, T121) to production standards with unified interfaces, comprehensive error handling, and complete documentation.

## Coding Philosophy

### Zero Tolerance for Shortcuts
- **NO lazy mocking/stubs/fallbacks/pseudo code** - Every service must be fully functional
- **NO simplified implementations** - Build complete functionality or don't build it
- **NO hiding errors** - All errors must surface immediately with full context
- **Fail-fast approach** - Services must fail immediately on invalid state rather than degrading

### Evidence-Based Development
- **Nothing is working until proven working** - All service functionality must be demonstrated
- **Every claim requires raw evidence logs** - Create Evidence.md files with actual service execution logs
- **Comprehensive testing required** - Unit, integration, and stress testing before claiming success
- **Performance evidence required** - Memory usage, response times, and throughput measurements

### Production Standards
- **Complete error handling** - Every service method must handle all possible error conditions
- **Comprehensive logging** - All service operations logged with structured data
- **Full input validation** - All service inputs validated against schemas
- **Resource management** - Proper cleanup of connections, files, and memory

## Codebase Structure

### Core Services Architecture
```
src/core/
├── service_manager.py          # Central service coordination and dependency injection
├── identity_service.py         # T107: Entity mention management and resolution
├── provenance_service.py       # T110: Operation tracking and lineage
├── quality_service.py          # T111: Confidence assessment and propagation
├── workflow_state_service.py   # T121: Workflow checkpoints and recovery
├── config_manager.py           # Unified configuration management
├── error_handler.py            # Centralized error handling
├── logging_config.py           # Structured logging framework
└── tool_protocol.py            # Unified tool interface contracts
```

### Service Dependencies
```
ServiceManager
├── IdentityService (T107)
├── ProvenanceService (T110) 
├── QualityService (T111)
├── WorkflowStateService (T121)
└── Configuration & Error Handling
```

### Entry Points
- **Service Manager**: `get_service_manager()` - Central service factory
- **Individual Services**: Direct instantiation with dependency injection
- **Configuration**: `get_config()` - Unified configuration access

## Critical Service Issues to Resolve

### Issue 1: Service Interface Standardization

**Problem**: Core services use inconsistent interfaces preventing reliable tool integration.

**Evidence Required**:
- Service interface audit with actual method signatures
- Interface compliance test results for all 4 services
- Integration test results showing service interoperability

**Implementation Steps**:

1. **Create Unified Service Interface Standard**
```python
# src/core/service_protocol.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass(frozen=True)
class ServiceRequest:
    operation: str
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None

@dataclass(frozen=True)
class ServiceResponse:
    success: bool
    data: Any
    metadata: Dict[str, Any]
    error_code: Optional[str] = None
    error_message: Optional[str] = None

class CoreService(ABC):
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> ServiceResponse:
        """Initialize service with configuration"""
        pass
    
    @abstractmethod
    def health_check(self) -> ServiceResponse:
        """Check service health and readiness"""
        pass
    
    @abstractmethod
    def get_statistics(self) -> ServiceResponse:
        """Get service performance statistics"""
        pass
    
    @abstractmethod
    def cleanup(self) -> ServiceResponse:
        """Clean up service resources"""
        pass
```

2. **Migrate All Core Services to Unified Interface**

**T107: Identity Service Standardization**
```python
# src/core/identity_service.py - Updated implementation
class IdentityService(CoreService):
    def create_mention(self, surface_form: str, start_pos: int, end_pos: int, 
                      source_ref: str, entity_type: str = None, 
                      confidence: float = 0.8) -> ServiceResponse:
        """Create mention with comprehensive validation and error handling"""
        try:
            # Input validation
            if not surface_form or not surface_form.strip():
                return ServiceResponse(
                    success=False,
                    data=None,
                    metadata={"timestamp": datetime.now().isoformat()},
                    error_code="INVALID_SURFACE_FORM",
                    error_message="Surface form cannot be empty"
                )
            
            if start_pos < 0 or end_pos <= start_pos:
                return ServiceResponse(
                    success=False,
                    data=None,
                    metadata={"timestamp": datetime.now().isoformat()},
                    error_code="INVALID_POSITION",
                    error_message="Invalid start/end positions"
                )
            
            # Full implementation with error handling
            mention_id = self._generate_mention_id()
            entity_id = self._resolve_or_create_entity(surface_form, entity_type)
            
            mention = {
                "mention_id": mention_id,
                "entity_id": entity_id,
                "surface_form": surface_form,
                "start_pos": start_pos,
                "end_pos": end_pos,
                "source_ref": source_ref,
                "entity_type": entity_type,
                "confidence": confidence,
                "created_at": datetime.now().isoformat()
            }
            
            # Store mention with full error handling
            self._store_mention(mention)
            
            return ServiceResponse(
                success=True,
                data=mention,
                metadata={
                    "operation": "create_mention",
                    "execution_time": self._get_execution_time(),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to create mention: {e}", exc_info=True)
            return ServiceResponse(
                success=False,
                data=None,
                metadata={"timestamp": datetime.now().isoformat()},
                error_code="MENTION_CREATION_FAILED",
                error_message=str(e)
            )
```

3. **Validation Requirements**
```python
# tests/unit/core/test_service_contracts.py
class TestServiceContracts:
    def test_all_services_implement_core_interface(self):
        """Verify all core services implement CoreService interface"""
        services = [IdentityService, ProvenanceService, QualityService, WorkflowStateService]
        for service_class in services:
            assert issubclass(service_class, CoreService)
            
    def test_service_response_consistency(self):
        """Test all services return consistent response format"""
        for service in self.get_all_services():
            response = service.health_check()
            assert isinstance(response, ServiceResponse)
            assert hasattr(response, 'success')
            assert hasattr(response, 'data')
            assert hasattr(response, 'metadata')
            
    def test_error_handling_completeness(self):
        """Test all services handle error conditions properly"""
        for service in self.get_all_services():
            # Test invalid inputs
            response = service.create_mention("", -1, -1, "")
            assert response.success == False
            assert response.error_code is not None
            assert response.error_message is not None
```

### Issue 2: Service Manager Dependency Injection

**Problem**: Service dependencies are not properly managed, leading to circular dependencies and initialization issues.

**Evidence Required**:
- Dependency graph analysis
- Service initialization order validation
- Memory usage measurements for service instances

**Implementation Steps**:

1. **Create Complete Service Manager**
```python
# src/core/service_manager.py - Complete implementation
from typing import Dict, Any, Optional, Type
import threading
from contextlib import contextmanager

class ServiceManager:
    """Thread-safe service manager with dependency injection"""
    
    _instance = None
    _lock = threading.Lock()
    _services: Dict[str, Any] = {}
    _initialized = False
    
    def __new__(cls) -> 'ServiceManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize all services with proper dependency order"""
        if self._initialized:
            return True
            
        try:
            # Initialize in dependency order
            self._initialize_configuration(config)
            self._initialize_error_handler()
            self._initialize_logging()
            self._initialize_core_services()
            
            self._initialized = True
            logger.info("ServiceManager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"ServiceManager initialization failed: {e}")
            self.cleanup()
            return False
    
    @property
    def identity_service(self) -> IdentityService:
        """Get or create identity service instance"""
        return self._get_service('identity', IdentityService)
    
    @property
    def provenance_service(self) -> ProvenanceService:
        """Get or create provenance service instance"""
        return self._get_service('provenance', ProvenanceService)
    
    def _get_service(self, service_name: str, service_class: Type) -> Any:
        """Thread-safe service creation"""
        if service_name not in self._services:
            with self._lock:
                if service_name not in self._services:
                    self._services[service_name] = self._create_service(service_class)
        return self._services[service_name]
    
    def _create_service(self, service_class: Type) -> Any:
        """Create service instance with dependency injection"""
        # Implement full dependency injection
        pass
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all managed services"""
        health_status = {}
        for service_name, service in self._services.items():
            try:
                response = service.health_check()
                health_status[service_name] = response.success
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                health_status[service_name] = False
        return health_status
    
    def cleanup(self) -> None:
        """Clean up all services and resources"""
        for service_name, service in self._services.items():
            try:
                if hasattr(service, 'cleanup'):
                    service.cleanup()
            except Exception as e:
                logger.error(f"Cleanup failed for {service_name}: {e}")
        self._services.clear()
        self._initialized = False
```

### Issue 3: Comprehensive Error Handling Framework

**Problem**: Services lack consistent error handling and recovery mechanisms.

**Evidence Required**:
- Error condition testing results for all services
- Error recovery validation with actual failure scenarios
- Performance impact measurement of error handling

**Implementation Steps**:

1. **Create Service Error Handling Framework**
```python
# src/core/service_error_handler.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, Callable
import logging

class ServiceErrorSeverity(Enum):
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ServiceError:
    service_name: str
    operation: str
    error_code: str
    message: str
    severity: ServiceErrorSeverity
    context: Dict[str, Any]
    recovery_action: Optional[Callable] = None

class ServiceErrorHandler:
    """Centralized error handling for all core services"""
    
    def __init__(self):
        self.error_counts = {}
        self.recovery_strategies = {}
        
    def handle_service_error(self, error: ServiceError) -> bool:
        """Handle service error with appropriate response"""
        try:
            # Log error with full context
            self._log_error(error)
            
            # Track error frequency
            self._track_error(error)
            
            # Attempt recovery if strategy exists
            recovery_successful = self._attempt_recovery(error)
            
            # Escalate if critical or recovery failed
            if error.severity == ServiceErrorSeverity.CRITICAL or not recovery_successful:
                self._escalate_error(error)
                
            return recovery_successful
            
        except Exception as e:
            logger.critical(f"Error handler itself failed: {e}")
            return False
    
    def register_recovery_strategy(self, error_code: str, strategy: Callable) -> None:
        """Register recovery strategy for specific error type"""
        self.recovery_strategies[error_code] = strategy
    
    def _attempt_recovery(self, error: ServiceError) -> bool:
        """Attempt to recover from error"""
        if error.recovery_action:
            try:
                return error.recovery_action()
            except Exception as e:
                logger.error(f"Recovery action failed: {e}")
                
        strategy = self.recovery_strategies.get(error.error_code)
        if strategy:
            try:
                return strategy(error)
            except Exception as e:
                logger.error(f"Recovery strategy failed: {e}")
                
        return False
```

2. **Implement Service-Specific Error Handling**
```python
# Example: Enhanced IdentityService with comprehensive error handling
class IdentityService(CoreService):
    def __init__(self, error_handler: ServiceErrorHandler):
        self.error_handler = error_handler
        self._setup_error_recovery()
    
    def _setup_error_recovery(self):
        """Setup error recovery strategies"""
        self.error_handler.register_recovery_strategy(
            "DATABASE_CONNECTION_LOST",
            self._recover_database_connection
        )
        self.error_handler.register_recovery_strategy(
            "MEMORY_LIMIT_EXCEEDED",
            self._clear_cache_and_retry
        )
    
    def create_mention(self, **kwargs) -> ServiceResponse:
        """Create mention with comprehensive error handling"""
        try:
            # Validate inputs with specific error codes
            validation_error = self._validate_mention_inputs(**kwargs)
            if validation_error:
                self.error_handler.handle_service_error(validation_error)
                return self._create_error_response(validation_error)
            
            # Attempt operation with error handling
            result = self._create_mention_internal(**kwargs)
            return self._create_success_response(result)
            
        except DatabaseConnectionError as e:
            error = ServiceError(
                service_name="IdentityService",
                operation="create_mention",
                error_code="DATABASE_CONNECTION_LOST",
                message=str(e),
                severity=ServiceErrorSeverity.ERROR,
                context=kwargs,
                recovery_action=self._recover_database_connection
            )
            self.error_handler.handle_service_error(error)
            return self._create_error_response(error)
            
        except Exception as e:
            error = ServiceError(
                service_name="IdentityService",
                operation="create_mention",
                error_code="UNEXPECTED_ERROR",
                message=str(e),
                severity=ServiceErrorSeverity.CRITICAL,
                context=kwargs
            )
            self.error_handler.handle_service_error(error)
            return self._create_error_response(error)
```

### Issue 4: Performance Monitoring and Optimization

**Problem**: No performance monitoring or optimization framework for core services.

**Evidence Required**:
- Performance baseline measurements for all services
- Resource usage tracking under various loads
- Performance optimization results with before/after metrics

**Implementation Steps**:

1. **Create Performance Monitoring Framework**
```python
# src/core/performance_monitor.py
import time
import psutil
import threading
from dataclasses import dataclass
from typing import Dict, Any, List
from contextlib import contextmanager

@dataclass
class PerformanceMetrics:
    operation: str
    duration: float
    memory_used: int
    cpu_percent: float
    timestamp: str

class PerformanceMonitor:
    """Monitor performance of all core service operations"""
    
    def __init__(self):
        self.metrics = []
        self.thresholds = {
            'max_duration': 5.0,  # 5 seconds
            'max_memory': 100 * 1024 * 1024,  # 100MB
            'max_cpu': 80.0  # 80%
        }
    
    @contextmanager
    def monitor_operation(self, operation: str):
        """Context manager to monitor operation performance"""
        process = psutil.Process()
        start_time = time.time()
        start_memory = process.memory_info().rss
        
        try:
            yield
        finally:
            duration = time.time() - start_time
            end_memory = process.memory_info().rss
            memory_used = end_memory - start_memory
            cpu_percent = process.cpu_percent()
            
            metrics = PerformanceMetrics(
                operation=operation,
                duration=duration,
                memory_used=memory_used,
                cpu_percent=cpu_percent,
                timestamp=datetime.now().isoformat()
            )
            
            self.metrics.append(metrics)
            self._check_thresholds(metrics)
    
    def _check_thresholds(self, metrics: PerformanceMetrics):
        """Check if performance metrics exceed thresholds"""
        if metrics.duration > self.thresholds['max_duration']:
            logger.warning(f"Operation {metrics.operation} exceeded duration threshold: {metrics.duration}s")
        
        if metrics.memory_used > self.thresholds['max_memory']:
            logger.warning(f"Operation {metrics.operation} exceeded memory threshold: {metrics.memory_used} bytes")
        
        if metrics.cpu_percent > self.thresholds['max_cpu']:
            logger.warning(f"Operation {metrics.operation} exceeded CPU threshold: {metrics.cpu_percent}%")
```

2. **Integrate Performance Monitoring into Services**
```python
# Example: IdentityService with performance monitoring
class IdentityService(CoreService):
    def __init__(self, performance_monitor: PerformanceMonitor):
        self.performance_monitor = performance_monitor
    
    def create_mention(self, **kwargs) -> ServiceResponse:
        """Create mention with performance monitoring"""
        with self.performance_monitor.monitor_operation("identity_create_mention"):
            return self._create_mention_internal(**kwargs)
    
    def get_entity_by_mention(self, mention_id: str) -> ServiceResponse:
        """Get entity with performance monitoring"""
        with self.performance_monitor.monitor_operation("identity_get_entity"):
            return self._get_entity_internal(mention_id)
```

## Service Testing Requirements

### Comprehensive Test Suite Structure
```python
# tests/unit/core/test_service_comprehensive.py
class TestServiceComprehensive:
    """Comprehensive testing for all core services"""
    
    def test_service_initialization(self):
        """Test service initialization with various configurations"""
        # Test valid configurations
        # Test invalid configurations
        # Test partial configurations
        # Verify error handling for each case
        
    def test_service_operations_under_load(self):
        """Test service operations under various load conditions"""
        # Single-threaded performance
        # Multi-threaded performance
        # Memory pressure testing
        # CPU pressure testing
        
    def test_error_conditions_comprehensive(self):
        """Test all possible error conditions"""
        # Invalid inputs
        # Database failures
        # Memory exhaustion
        # Network failures
        # Concurrent access issues
        
    def test_recovery_mechanisms(self):
        """Test error recovery mechanisms"""
        # Database reconnection
        # Cache clearing
        # Service restart
        # State recovery
```

### Performance Validation Tests
```python
# tests/performance/test_service_performance.py
class TestServicePerformance:
    def test_service_response_times(self):
        """Validate service response times meet requirements"""
        # Test each service operation
        # Measure response times under various conditions
        # Verify times meet performance requirements
        
    def test_memory_usage_patterns(self):
        """Validate memory usage stays within bounds"""
        # Monitor memory usage during operations
        # Test for memory leaks
        # Verify cleanup effectiveness
        
    def test_concurrent_access_performance(self):
        """Test performance under concurrent access"""
        # Multiple threads accessing services
        # Measure contention and deadlock potential
        # Verify thread safety
```

## Evidence Collection Requirements

### Service Implementation Evidence
Create `Evidence_Core_Services.md` with:

1. **Service Interface Compliance**
   - Method signature verification for all services
   - Response format consistency validation
   - Error handling completeness verification

2. **Performance Metrics**
   - Response time measurements for all operations
   - Memory usage tracking under various loads
   - CPU utilization during intensive operations

3. **Error Handling Validation**
   - Error condition testing results
   - Recovery mechanism effectiveness
   - Error escalation procedures

4. **Integration Testing Results**
   - Service interoperability validation
   - Cross-service communication testing
   - End-to-end workflow execution

### Continuous Validation Process

1. **Update Verification Configuration**
```yaml
# gemini-review-tool/core-services-review.yaml
claims_of_success:
  - "All 4 core services implement unified CoreService interface"
  - "Service Manager provides thread-safe dependency injection"
  - "Comprehensive error handling covers all failure modes"
  - "Performance monitoring tracks all operations"
  - "All services pass comprehensive test suites"

files_to_review:
  - "src/core/service_manager.py"
  - "src/core/identity_service.py"
  - "src/core/provenance_service.py"
  - "src/core/quality_service.py"
  - "src/core/workflow_state_service.py"
  - "src/core/service_protocol.py"
  - "src/core/service_error_handler.py"
  - "src/core/performance_monitor.py"
  - "tests/unit/core/*.py"
  - "Evidence_Core_Services.md"
```

2. **Execute Validation Cycle**
```bash
# Run comprehensive test suite
python -m pytest tests/unit/core/ -v --cov=src/core --cov-report=html

# Run performance tests
python -m pytest tests/performance/ -v

# Generate evidence report
python scripts/generate_service_evidence.py

# Run Gemini review
python gemini-review-tool/gemini_review.py --config gemini-review-tool/core-services-review.yaml
```

## Success Criteria

Core services implementation is complete when:

1. **All services implement unified interface** - Verified by interface compliance tests
2. **Error handling is comprehensive** - Verified by error injection testing
3. **Performance meets requirements** - Verified by performance benchmark tests
4. **Thread safety is guaranteed** - Verified by concurrent access tests
5. **Gemini review finds no issues** - Verified by clean review report

Each criterion must be supported by evidence in `Evidence_Core_Services.md` before claiming success.