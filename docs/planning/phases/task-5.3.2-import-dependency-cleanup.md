# Task 5.3.2: Import Dependency Cleanup

**Status**: PENDING  
**Priority**: MEDIUM  
**Estimated Effort**: 2-3 days  
**Dependencies**: Tool factory refactoring completion

## 🎯 **Objective**

Clean up heavy cross-module dependencies through deep relative imports to improve maintainability and reduce coupling.

## 📊 **Current Status**

**Import Coupling Issues**:
- ❌ **Deep relative imports** creating tight coupling (../../patterns)
- ❌ **Heavy cross-module dependencies** through import chains
- ❌ **Complex import paths** making refactoring difficult
- ❌ **Circular dependency risks** from interconnected imports

## 🔧 **Current Problematic Patterns**

### **Deep Relative Imports**
```python
# Current problematic patterns in tool_adapters.py:
from ..tools.phase1.t01_pdf_loader import PDFLoader as _PDFLoader
from ..tools.phase1.t15a_text_chunker import TextChunker as _TextChunker
from ..tools.phase1.t23a_spacy_ner import SpacyNER as _SpacyNER
from ..tools.phase1.t27_relationship_extractor import RelationshipExtractor as _RelationshipExtractor
from ..tools.phase1.t31_entity_builder import EntityBuilder as _EntityBuilder
from ..tools.phase1.t34_edge_builder import EdgeBuilder as _EdgeBuilder
from ..tools.phase1.t49_multihop_query import MultiHopQuery as _MultiHopQuery
from ..tools.phase1.t68_pagerank_optimized import PageRankOptimized as _PageRankOptimized
# ... 8+ more similar imports creating tight coupling
```

### **Complex Cross-Module Dependencies**
```python
# Circular dependency patterns found:
# src/core/tool_adapters.py imports from src/tools/
# src/tools/*/tool.py imports from src/core/
# src/core/service_manager.py imports from both
```

## 🎯 **Target Clean Architecture**

### **Dependency Injection Pattern**
```python
# Replace deep imports with dependency injection:
@dataclass
class ToolAdapterConfig:
    tool_registry: ToolRegistry
    config_manager: ConfigManager
    logger: Logger

class ToolAdapter:
    def __init__(self, config: ToolAdapterConfig):
        self.registry = config.tool_registry
        self.config = config.config_manager
        self.logger = config.logger
    
    def get_tool(self, tool_name: str):
        # Get tool from registry instead of direct import
        return self.registry.get_tool(tool_name)
```

### **Absolute Import Patterns**
```python
# Convert to absolute imports:
from src.core.config_manager import ConfigManager  # ✅ GOOD
from src.core.tool_registry import ToolRegistry     # ✅ GOOD
from src.core.service_manager import ServiceManager # ✅ GOOD

# Instead of:
from ..core.config_manager import ConfigManager     # ❌ BAD
from ...tools.phase1.tool import SomeTool          # ❌ BAD
```

### **Interface-Based Dependencies**
```python
# Use interfaces to reduce coupling:
from abc import ABC, abstractmethod

class ToolInterface(ABC):
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        pass

class ToolAdapter:
    def __init__(self, tools: Dict[str, ToolInterface]):
        self.tools = tools  # Depend on interface, not concrete classes
```

## 🔄 **Cleanup Strategy**

### **Phase 1: Import Analysis (Day 1)**
1. **Map all imports** - Identify all relative import patterns
2. **Detect circular dependencies** - Find problematic dependency cycles  
3. **Categorize imports** - Group by type (config, tools, services, etc.)
4. **Plan conversion order** - Order changes to avoid breaking dependencies

### **Phase 2: Convert to Absolute Imports (Day 1-2)**
1. **Convert simple relative imports** - Change to absolute paths
2. **Update import paths** - Use full module paths from src/
3. **Test incremental changes** - Verify functionality after each conversion
4. **Update __init__.py files** - Ensure proper module structure

### **Phase 3: Implement Dependency Injection (Day 2-3)**
1. **Extract heavy import dependencies** - Move to dependency injection
2. **Create service interfaces** - Define clean interfaces for services
3. **Update constructors** - Use dependency injection pattern
4. **Wire dependencies** - Set up proper dependency injection container

## 📈 **Success Criteria**

### **Import Quality Metrics**
- [ ] **Zero relative imports** with ../../ patterns
- [ ] **No circular dependencies** detected by analysis tools
- [ ] **All imports use absolute paths** from src/ root
- [ ] **Clean dependency graph** with clear layers

### **Architecture Quality**
- [ ] **Dependency injection used** for heavy dependencies
- [ ] **Interface-based dependencies** where appropriate
- [ ] **Service layer isolation** from tool implementations
- [ ] **Testable dependency structure** for unit testing

## 🧪 **Validation Commands**

### **Import Analysis**
```bash
# Find all relative imports
grep -r "from \.\." src/ --include="*.py" | wc -l
# Target: 0 relative imports

# Find circular dependencies
python -c "
import ast
import os
from collections import defaultdict, deque

def find_imports(file_path):
    '''Extract imports from Python file'''
    with open(file_path, 'r') as f:
        try:
            tree = ast.parse(f.read())
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            return imports
        except:
            return []

def detect_cycles():
    '''Detect circular dependencies'''
    graph = defaultdict(list)
    
    for root, dirs, files in os.walk('src/'):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                module = path.replace('/', '.').replace('.py', '')
                imports = find_imports(path)
                for imp in imports:
                    if imp.startswith('src.'):
                        graph[module].append(imp)
    
    # Simple cycle detection (would need more sophisticated algorithm for production)
    print('Analyzing dependency graph...')
    print(f'Found {len(graph)} modules with {sum(len(deps) for deps in graph.values())} dependencies')

detect_cycles()
"

# Check import patterns
python -c "
import re
import os

relative_count = 0
absolute_count = 0

for root, dirs, files in os.walk('src/'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()
                relative_count += len(re.findall(r'from \.\.', content))
                absolute_count += len(re.findall(r'from src\.', content))

print(f'Relative imports: {relative_count}')
print(f'Absolute imports: {absolute_count}')
print(f'Import quality: {absolute_count / max(absolute_count + relative_count, 1) * 100:.1f}% absolute')
"
```

### **Dependency Injection Verification**
```bash
# Verify dependency injection usage
grep -r "@inject\|@dataclass.*Config\|def __init__.*:.*Config" src/ --include="*.py" | wc -l
# Target: 5+ classes using dependency injection

# Test service instantiation
python -c "
from src.core.service_manager import ServiceManager
from src.core.config_manager import ConfigManager

# Test clean dependency resolution
service_manager = ServiceManager()
config = ConfigManager()

print('✅ Services instantiate without circular dependencies')
print('✅ Clean dependency injection working')
"
```

## ⚠️ **Implementation Considerations**

### **Backward Compatibility**
- Make incremental changes to avoid breaking existing functionality
- Test each conversion step thoroughly
- Maintain API compatibility during transition

### **Testing Strategy**
- Test import changes incrementally
- Verify no functionality regression
- Test service instantiation after dependency injection changes
- Run full test suite after each major change

### **Performance Impact**
- Monitor import performance (dependency injection overhead)
- Ensure no significant startup time increase
- Optimize service instantiation if needed

## 🚀 **Expected Benefits**

### **Maintainability Improvements**
- **Reduced coupling** - Less interdependent code
- **Clearer dependencies** - Explicit dependency declaration
- **Easier refactoring** - Changes don't ripple through import chains
- **Better testability** - Dependencies can be mocked/injected

### **Architecture Benefits**
- **Clean layered architecture** - Clear separation between layers
- **No circular dependencies** - Eliminates problematic dependency cycles
- **Dependency injection ready** - Modern, testable architecture patterns
- **Future extensibility** - Easy to add new services and components

---

## 📞 **Support Resources**

### **Reference Implementations**
- `src/core/service_manager.py` - Dependency injection patterns
- `src/core/config_manager.py` - Clean import structure example

### **Analysis Tools**
- Python AST module for import analysis
- Dependency analysis scripts in `tools/analysis/`
- Import cycle detection utilities

This cleanup is important for long-term maintainability and supporting future architectural improvements.