# Module Import Resolution Issues - KGAS System

## Problem Statement

**Issue:** Systematic import failures prevent MCP tool system from loading  
**Impact:** System starts in "limited mode" with severely reduced functionality  
**Root Cause:** Relative import assumptions break in different execution contexts  

## Current Import Failures

### Primary Failure Points

```python
# src/orchestration/mcp_adapter.py:44-45
from ..mcp_tools.server_manager import get_mcp_server_manager
from ..tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
```

**Error:**
```
Failed to import MCP components: attempted relative import beyond top-level package
```

### Execution Context Analysis

**Working Context:** When run as installed package
```bash
python -m src.orchestration.parallel_orchestrator
# Relative imports work because 'src' is the package root
```

**Failing Context:** When run as script from project root
```bash
python performance_benchmark.py
# Relative imports fail because execution starts outside package
```

### Impact Chain

1. **MCP Adapter Initialization Fails** → Import errors
2. **Tool Discovery Disabled** → Limited mode activation  
3. **Agent Functionality Reduced** → Core features unavailable
4. **System Appears Broken** → Even when initialization "succeeds"

## Current Module Structure

```
src/
├── orchestration/
│   ├── mcp_adapter.py          # ❌ Fails: ..mcp_tools import
│   ├── agents/
│   │   └── document_agent.py   # Uses mcp_adapter
│   └── ...
├── mcp_tools/
│   ├── server_manager.py       # Target of failed import
│   └── ...
└── tools/
    └── phase1/
        └── phase1_mcp_tools.py # Target of failed import
```

**Problem:** `mcp_adapter.py` assumes it's inside a package where `..mcp_tools` resolves correctly

## Import Strategy Options

### Option 1: Absolute Imports with Environment Detection

**Implementation:**
```python
# src/orchestration/mcp_adapter.py
import sys
import os
from pathlib import Path

# Detect if we're in the source tree
current_dir = Path(__file__).parent
src_dir = current_dir.parent

# Add src to path if not already there
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Now use absolute imports
from mcp_tools.server_manager import get_mcp_server_manager
from tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
```

**Pros:**
- ✅ Works in all execution contexts
- ✅ Clear dependency paths
- ✅ No package structure requirements

**Cons:**
- ❌ Modifies sys.path (side effects)
- ❌ Hardcodes path assumptions
- ❌ Less portable

---

### Option 2: Graceful Import Fallback

**Implementation:**
```python
# src/orchestration/mcp_adapter.py
def _import_mcp_components():
    """Import MCP components with fallback strategies."""
    
    # Strategy 1: Relative imports (package context)
    try:
        from ..mcp_tools.server_manager import get_mcp_server_manager
        from ..tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
        return get_mcp_server_manager, create_phase1_mcp_tools
    except ImportError:
        pass
    
    # Strategy 2: Absolute imports (script context)
    try:
        from mcp_tools.server_manager import get_mcp_server_manager
        from tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
        return get_mcp_server_manager, create_phase1_mcp_tools
    except ImportError:
        pass
    
    # Strategy 3: Path-adjusted imports
    try:
        import sys
        from pathlib import Path
        src_dir = Path(__file__).parent.parent
        if str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))
        
        from mcp_tools.server_manager import get_mcp_server_manager
        from tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
        return get_mcp_server_manager, create_phase1_mcp_tools
    except ImportError:
        pass
    
    # Strategy 4: Return None (limited mode)
    return None, None
```

**Pros:**
- ✅ Graceful degradation
- ✅ Works in multiple contexts
- ✅ Clear fallback behavior

**Cons:**
- ❌ Complex and verbose
- ❌ May mask real import issues
- ❌ Multiple code paths to maintain

---

### Option 3: Package Structure Enforcement

**Implementation:**
```python
# Create proper __init__.py files and enforce package usage
# src/__init__.py
# src/orchestration/__init__.py
# src/mcp_tools/__init__.py
# src/tools/__init__.py
# src/tools/phase1/__init__.py

# Always run as: python -m src.main
# Or install as package: pip install -e .
```

**Pros:**
- ✅ Proper Python package structure
- ✅ Standard relative imports work
- ✅ Clean and maintainable

**Cons:**
- ❌ Requires execution discipline
- ❌ Breaks existing run patterns
- ❌ May need packaging changes

---

### Option 4: Import Service Pattern

**Implementation:**
```python
# src/core/import_service.py
class ImportService:
    """Centralized import resolution service."""
    
    def __init__(self):
        self._resolved_imports = {}
        self._setup_paths()
    
    def _setup_paths(self):
        """Ensure src directory is in Python path."""
        import sys
        from pathlib import Path
        
        # Find src directory relative to this file
        current_file = Path(__file__).resolve()
        src_dir = current_file.parent.parent
        
        if str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))
    
    def get_mcp_manager(self):
        """Get MCP server manager with import resolution."""
        if 'mcp_manager' not in self._resolved_imports:
            try:
                from mcp_tools.server_manager import get_mcp_server_manager
                self._resolved_imports['mcp_manager'] = get_mcp_server_manager
            except ImportError as e:
                logger.warning(f"MCP manager import failed: {e}")
                self._resolved_imports['mcp_manager'] = None
        
        return self._resolved_imports['mcp_manager']

# Usage in mcp_adapter.py
from ..core.import_service import ImportService
import_service = ImportService()
get_mcp_server_manager = import_service.get_mcp_manager()
```

**Pros:**
- ✅ Centralized import logic
- ✅ Cacheable resolution
- ✅ Clean service interface
- ✅ Testable import logic

**Cons:**
- ❌ Additional architectural layer
- ❌ More complex for simple imports
- ❌ Overkill for current needs

## Recommended Solution

### Phase 1: Immediate Fix (Option 2 - Graceful Fallback)

**Rationale:**
- Minimal code changes
- Works with existing structure
- Provides clear failure modes
- Can be implemented quickly

**Implementation in mcp_adapter.py:**
```python
def _safe_import_mcp_tools():
    """Import MCP tools with fallback handling."""
    try:
        # Try relative import first (package context)
        from ..mcp_tools.server_manager import get_mcp_server_manager
        from ..tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
        return get_mcp_server_manager, create_phase1_mcp_tools, None
    except ImportError as e1:
        try:
            # Try absolute import (script context)
            import sys
            from pathlib import Path
            src_dir = Path(__file__).parent.parent
            if str(src_dir) not in sys.path:
                sys.path.insert(0, str(src_dir))
            
            from mcp_tools.server_manager import get_mcp_server_manager
            from tools.phase1.phase1_mcp_tools import create_phase1_mcp_tools
            return get_mcp_server_manager, create_phase1_mcp_tools, None
        except ImportError as e2:
            # Return None for limited mode
            return None, None, f"Import failed: {e1}, {e2}"

# In MCPToolAdapter.__init__:
get_mcp_server_manager, create_phase1_mcp_tools, error = _safe_import_mcp_tools()
if error:
    logger.warning(f"MCP tools unavailable: {error}")
    self._limited_mode = True
else:
    self._limited_mode = False
```

### Phase 2: Long-term Fix (Option 3 - Package Structure)

**After immediate issues resolved:**
1. Ensure all directories have proper `__init__.py` files
2. Create standardized entry points
3. Add packaging configuration
4. Update documentation for proper execution

## Validation Plan

### Test Cases

```python
def test_import_resolution():
    """Test import resolution in different contexts."""
    
    # Test 1: Package context
    # Run from package root with proper structure
    
    # Test 2: Script context  
    # Run from project root as script
    
    # Test 3: Limited mode
    # Simulate import failures, verify graceful degradation
    
    # Test 4: Path manipulation
    # Verify sys.path changes work correctly
```

### Integration Tests

```python
def test_mcp_adapter_initialization():
    """Test MCP adapter works in both modes."""
    
    # Full mode: All imports successful
    adapter_full = MCPToolAdapter()
    assert not adapter_full._limited_mode
    assert adapter_full.has_tool("load_documents")
    
    # Limited mode: Imports failed
    # (Mock import failures)
    adapter_limited = MCPToolAdapter()
    assert adapter_limited._limited_mode
    assert adapter_limited.get_available_tools() == []
```

## Success Criteria

**Immediate Success:**
- [ ] System starts without import errors
- [ ] MCP tools load when available
- [ ] Limited mode works when tools unavailable
- [ ] Clear error messages for diagnosis

**Long-term Success:**
- [ ] Clean package structure
- [ ] Consistent execution patterns
- [ ] Maintainable import logic
- [ ] Good developer experience

## Risk Assessment

**Low Risk:**
- Graceful fallback pattern
- Backward compatible changes
- Clear error handling

**Medium Risk:**
- sys.path manipulation side effects
- Multiple import strategies to maintain

**High Risk:**
- Package structure changes (Phase 2)
- Breaking existing run patterns

## Implementation Priority

1. **Immediate:** Implement graceful fallback in mcp_adapter.py
2. **Next:** Test resolution across different execution contexts  
3. **Future:** Consider package structure improvements
4. **Long-term:** Standardize import patterns across codebase

This approach provides immediate relief while planning for better long-term architecture.