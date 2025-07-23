# Task 5.3.1: Tool Factory Refactoring

**Status**: PENDING  
**Priority**: HIGH  
**Estimated Effort**: 2-3 days  
**Dependencies**: Phase 5.2 completion

## 🎯 **Objective**

Refactor the monolithic ToolFactory class (741 lines, 13 methods) into focused, single-responsibility services to improve maintainability and testability.

## 📊 **Current Status**

**Tool Factory Complexity**: 
- ✅ **File exists and functional** (src/core/tool_factory.py)
- ❌ **Single class with multiple responsibilities** (741 lines)
- ❌ **13 methods handling diverse concerns** (discovery, registration, auditing, caching)
- ❌ **High maintenance burden** for changes

## 🔧 **Current Complex Pattern**

```python
class ToolFactory:  # 741 lines, 13 methods, multiple responsibilities
    def __init__(self):
        self.discovered_tools = {}     # Tool discovery
        self.tool_registry = {}        # Tool registration  
        self.audit_results = {}        # Audit tracking
        self.performance_cache = {}    # Performance caching
        self.instantiated_tools = {}   # Tool instantiation
        self.error_tracking = {}       # Error management
        self.success_rates = {}        # Performance metrics
        # ... 6 more instance variables handling different concerns
        
    def discover_all_tools(self):     # File system scanning
    def audit_all_tools(self):       # Validation testing  
    def get_success_rate(self):       # Performance analysis
    def create_tool_instance(self):   # Tool instantiation
    def cache_performance(self):      # Caching management
    # ... 8 more methods with mixed responsibilities
```

## 🎯 **Target Refactored Architecture**

### **Split into Focused Services:**

```python
# 1. Tool Discovery Service (150-200 lines)
class ToolDiscoveryService:
    """Handles file system scanning and tool identification"""
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.discovered_tools = {}
    
    def discover_tools_in_directory(self, directory: str) -> Dict[str, Any]:
        """Scan directory for tool implementations"""
        pass
    
    def validate_tool_interface(self, tool_class) -> bool:
        """Verify tool implements required interface"""
        pass

# 2. Tool Registry Service (100-150 lines)  
class ToolRegistry:
    """Handles tool registration and instantiation"""
    def __init__(self, discovery_service: ToolDiscoveryService):
        self.discovery = discovery_service
        self.registered_tools = {}
    
    def register_tool(self, tool_name: str, tool_class) -> None:
        """Register tool for use"""
        pass
    
    def create_tool_instance(self, tool_name: str) -> Any:
        """Instantiate registered tool"""
        pass

# 3. Tool Audit Service (200-250 lines)
class ToolAuditService:
    """Handles tool validation and testing"""
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.audit_results = {}
    
    def audit_tool(self, tool_name: str) -> Dict[str, Any]:
        """Validate single tool functionality"""
        pass
    
    def audit_all_tools(self) -> Dict[str, Any]:
        """Validate all registered tools"""
        pass

# 4. Tool Performance Monitor (100-150 lines)
class ToolPerformanceMonitor:
    """Handles performance tracking and caching"""
    def __init__(self):
        self.performance_cache = {}
        self.success_rates = {}
    
    def track_tool_performance(self, tool_name: str, execution_time: float) -> None:
        """Record tool performance metrics"""
        pass
    
    def get_success_rate(self, tool_name: str) -> float:
        """Calculate tool success rate"""
        pass
```

## 🔄 **Migration Strategy**

### **Phase 1: Extract Services (Day 1)**
1. **Create ToolDiscoveryService** - Extract discovery logic
2. **Create ToolRegistry** - Extract registration logic  
3. **Maintain backward compatibility** - Keep ToolFactory as facade
4. **Test individual services** - Ensure functionality preserved

### **Phase 2: Extract Audit and Performance (Day 2)**
1. **Create ToolAuditService** - Extract audit logic
2. **Create ToolPerformanceMonitor** - Extract performance tracking
3. **Update ToolFactory facade** - Delegate to new services
4. **Integration testing** - Verify full functionality

### **Phase 3: Update Dependencies (Day 3)**
1. **Update callers** - Use new services directly where appropriate
2. **Deprecate ToolFactory facade** - Phase out monolithic class
3. **Update dependency injection** - Wire new services properly
4. **Final testing** - Comprehensive system validation

## 📈 **Success Criteria**

### **Primary Metrics**
- [ ] **ToolFactory split into 4 focused services** 
- [ ] **Each service < 250 lines** with single responsibility
- [ ] **Improved testability** - Each service independently testable
- [ ] **Reduced coupling** - Clear interfaces between services

### **Quality Metrics**
- [ ] **All existing functionality preserved**
- [ ] **Performance maintained or improved**
- [ ] **Full test coverage** for each new service
- [ ] **Clean dependency injection** setup

## 🧪 **Validation Commands**

### **Service Structure Verification**
```bash
# Verify service files created
ls -la src/core/tool_discovery_service.py
ls -la src/core/tool_registry.py  
ls -la src/core/tool_audit_service.py
ls -la src/core/tool_performance_monitor.py

# Check line counts (should be < 250 each)
wc -l src/core/tool_*_service.py src/core/tool_registry.py src/core/tool_performance_monitor.py

# Verify single responsibility (method count should be < 8 per service)
grep -c "def " src/core/tool_*_service.py src/core/tool_registry.py src/core/tool_performance_monitor.py
```

### **Functionality Verification**
```bash
# Test service integration
python -c "
from src.core.tool_discovery_service import ToolDiscoveryService
from src.core.tool_registry import ToolRegistry
from src.core.tool_audit_service import ToolAuditService
from src.core.tool_performance_monitor import ToolPerformanceMonitor

# Test service instantiation
discovery = ToolDiscoveryService(config_manager)
registry = ToolRegistry(discovery)
audit = ToolAuditService(registry)  
monitor = ToolPerformanceMonitor()

print('✅ All services instantiate successfully')
"

# Test full workflow
python -c "
# Test complete tool workflow through services
discovery = ToolDiscoveryService(config_manager)
tools = discovery.discover_tools_in_directory('src/tools/')
print(f'✅ Discovered {len(tools)} tools')

registry = ToolRegistry(discovery)
for tool_name in tools:
    registry.register_tool(tool_name, tools[tool_name])
print('✅ Tools registered successfully')

audit = ToolAuditService(registry)
results = audit.audit_all_tools()
print(f'✅ Audit completed: {results[\"working_tools\"]}/{results[\"total_tools\"]} working')
"
```

## ⚠️ **Implementation Considerations**

### **Dependency Injection**
- Use dependency injection to wire services together
- Avoid circular dependencies between services
- Provide clean interfaces for testing

### **Backward Compatibility**
- Maintain ToolFactory as facade during transition
- Provide clear deprecation warnings
- Update callers gradually to use new services

### **Error Handling**
- Preserve all existing error handling behavior
- Ensure error propagation works correctly across services
- Test error scenarios thoroughly

### **Performance**
- Ensure no performance regression from service split
- Optimize service interactions for efficiency
- Maintain or improve caching behavior

## 🚀 **Expected Benefits**

### **Maintainability Improvements**
- **Single responsibility** - Each service has clear, focused purpose
- **Reduced complexity** - Smaller, more manageable code units
- **Improved testability** - Individual services can be tested in isolation
- **Better debugging** - Issues isolated to specific services

### **Architecture Benefits**
- **Clean separation of concerns** - Discovery, registration, audit, performance
- **Dependency injection ready** - Services can be easily mocked/replaced
- **Future extensibility** - New functionality can be added as focused services
- **Reduced maintenance burden** - Changes affect smaller, focused codebases

---

## 📞 **Support Resources**

### **Reference Implementations**
- `src/core/service_manager.py` - Service dependency injection patterns
- `src/core/config_manager.py` - Single responsibility service example
- `tests/unit/` - Unit testing patterns for services

### **Architecture Documentation**
- `docs/architecture/systems/` - Service architecture guidance
- `docs/architecture/adrs/` - Architectural decision records

This refactoring is critical for improving code maintainability and supporting future development while preserving all existing functionality.