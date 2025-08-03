# KGAS Development Instructions - Tool Contract Integration Phase

## Current Priority Tasks (2025-08-03)

### 🎯 **PHASE: Tool Contract Integration & Registry Completion**

The previous phase successfully eliminated production readiness violations (fake processing, mock APIs, placeholder implementations). Evidence in `evidence/current/Evidence_Phase_Production_Readiness_Fixes.md` shows critical simulation patterns were replaced with real implementations.

**Current Phase Goal**: Complete tool contract integration and registry system to enable agent orchestration and systematic tool validation.

## Coding Philosophy

### **NO LAZY IMPLEMENTATIONS**
- **NO mocking/stubs/fallbacks/pseudo-code/simplified implementations** in production code
- **NO placeholder returns** - either implement real functionality or raise NotImplementedError
- **NO fake success responses** - fail fast with honest error messages

### **FAIL-FAST PRINCIPLES**
- **Surface errors immediately** - don't hide them behind fallbacks
- **Honest error messages** with actionable troubleshooting information
- **Real processing only** - eliminate all simulation patterns

### **EVIDENCE-BASED DEVELOPMENT**
- **All claims require raw evidence** in structured evidence files under `evidence/current/`
- **Raw execution logs required** for all functionality claims
- **No success declarations without demonstrable proof** 
- **Archive completed phases** to `evidence/completed/` to avoid chronological confusion

### **VALIDATION + SELF-HEALING**
- **Every validator must have coupled self-healing capability**
- **Contract validation must auto-register missing tools**
- **System must detect and repair interface mismatches**

## Codebase Structure

### **Key Entry Points**
- **Tool Registry**: `src/core/tool_contract.py` - Central tool registration and contract management
- **Tool Protocol**: `src/tools/base_classes/tool_protocol.py` - Unified ToolRequest/ToolResult interface
- **Service Manager**: `src/core/service_manager.py` - Shared service instances for tools
- **Pipeline Orchestrator**: `src/core/pipeline_orchestrator.py` - Workflow execution

### **Tool Implementation Structure**
```
src/tools/
├── phase1/                     # Foundation tools (PDF→Entities→Graph→Query)
│   ├── t01_pdf_loader_unified.py       # Real PDF processing
│   ├── t15a_text_chunker_unified.py    # Real text chunking
│   ├── t23a_spacy_ner_unified.py       # Real entity extraction
│   └── ...
├── base_classes/               # Tool contracts and protocols
│   ├── tool_protocol.py        # ToolRequest/ToolResult interface
│   └── ...
└── contracts/                  # Tool contract definitions
```

### **Integration Points**
- **Contract Validation**: `tests/unit/test_tool_contracts.py` - Validates tool compliance
- **Service Integration**: All tools use ServiceManager for database/service access
- **MCP Adapter**: `src/orchestration/mcp_adapter.py` - External tool exposure

## Critical Issues Identified by Contract Validation

### 🚨 **Issue 1: Tool Registry Not Populated**
**Problem**: Contract validation shows 15 failed tests due to missing tool registrations
**Evidence**: `pytest tests/unit/test_tool_contracts.py -v` shows:
```
AssertionError: Missing tools: ['T01_PDF_LOADER', 'T15A_TEXT_CHUNKER', 'T23A_SPACY_NER', ...]
```

**Root Cause**: Tools exist but are not registered in the tool registry system

**Required Fix**: 
1. **Auto-Registration System**: Create tool auto-discovery that scans `src/tools/` and registers all unified tools
2. **Contract Compliance**: Ensure all tools implement ToolRequest/ToolResult interface correctly
3. **Registry Population**: Populate `get_tool_registry()` with all available tools

**Implementation Steps**:
```python
# In src/core/tool_registry_auto.py (NEW FILE)
def auto_register_all_tools():
    """Auto-discover and register all tools in src/tools/"""
    # Scan for *_unified.py files
    # Import each tool class
    # Validate implements UnifiedTool interface
    # Register with tool registry
    # Return registration results
```

**Success Criteria**: All contract tests pass - `pytest tests/unit/test_tool_contracts.py -v` shows 0 failures

### 🚨 **Issue 2: ConfidenceScore Interface Mismatches**
**Problem**: ConfidenceScore class missing required methods
**Evidence**: Contract validation shows:
```
AttributeError: 'ConfidenceScore' object has no attribute 'combine_with'
AttributeError: 'ConfidenceScore' object has no attribute 'decay'
```

**Required Fix**: Complete ConfidenceScore implementation with all required methods:
- `combine_with()` - Combine confidence scores from multiple sources
- `decay()` - Apply confidence decay over processing steps
- Proper validation error handling
- Quality tier conversion compliance

### 🚨 **Issue 3: Tool Interface Standardization Gap**
**Problem**: Tools may not implement unified ToolRequest/ToolResult interface consistently
**Evidence**: Previous batch scheduler fix required manual interface adaptation

**Required Fix**: 
1. **Interface Audit**: Verify all `*_unified.py` tools implement `execute(ToolRequest) -> ToolResult`
2. **Interface Migration**: Update any tools using legacy dictionary interfaces
3. **Validation Testing**: Ensure all tools can be called via contract interface

## Evidence Structure Requirements

**Current Phase Evidence**: `evidence/current/Evidence_Phase_Tool_Contract_Integration.md`

**Required Evidence Sections**:
1. **Auto-Registration Results**
   - Tool discovery scan results
   - Registration success/failure rates
   - Contract compliance verification
   
2. **Contract Validation Results**
   - Full contract test suite results
   - Interface compatibility verification  
   - ConfidenceScore method implementation proof

3. **Integration Testing Results**
   - Tool execution via registry
   - ToolRequest/ToolResult interface testing
   - Service manager integration verification

## Implementation Plan

### **Step 1: Auto-Registration System**
**File**: `src/core/tool_registry_auto.py` (NEW)
```python
def discover_unified_tools():
    """Scan src/tools/ for *_unified.py files and return tool classes"""
    
def validate_tool_contract(tool_class):
    """Verify tool implements UnifiedTool interface"""
    
def auto_register_all_tools():
    """Auto-discover, validate, and register all tools"""
```

### **Step 2: ConfidenceScore Completion**
**File**: `src/core/confidence_score.py` (UPDATE)
```python
class ConfidenceScore:
    def combine_with(self, other: 'ConfidenceScore') -> 'ConfidenceScore':
        """Combine confidence scores from multiple sources"""
        
    def decay(self, factor: float) -> 'ConfidenceScore':
        """Apply confidence decay over processing steps"""
```

### **Step 3: Tool Interface Migration**
**Files**: All `src/tools/phase1/*_unified.py` tools
- Verify `execute(ToolRequest) -> ToolResult` signature
- Update any legacy dictionary interfaces
- Test via contract validation

### **Step 4: Integration Testing**
**File**: `evidence/current/Evidence_Phase_Tool_Contract_Integration.md`
- Document all tool registration results
- Prove contract compliance with test results
- Demonstrate tool execution via registry

## Validation Commands

### **Contract Validation**
```bash
# Run complete contract test suite
python -m pytest tests/unit/test_tool_contracts.py -v

# Validate specific tool registration
python -c "from src.core.tool_contract import get_tool_registry; print(get_tool_registry().list_tools())"

# Test auto-registration
python -c "from src.core.tool_registry_auto import auto_register_all_tools; print(auto_register_all_tools())"
```

### **Interface Testing**
```bash
# Test ToolRequest/ToolResult interface
python scripts/validation/validate_mcp_tools_standalone.py

# Verify service manager integration
python -c "from src.core.service_manager import ServiceManager; sm = ServiceManager(); print(sm.health_check())"
```

## Success Criteria

### **Phase Complete When**:
1. **Contract tests pass**: `pytest tests/unit/test_tool_contracts.py -v` shows 0 failures
2. **Tool registry populated**: All unified tools discoverable via registry
3. **Interface standardization**: All tools use ToolRequest/ToolResult consistently
4. **ConfidenceScore complete**: All required methods implemented and tested
5. **Evidence documented**: Complete execution logs in evidence file

### **Next Phase Preparation**:
Once tool contracts are complete, next phase will focus on:
- Agent orchestration with validated tool registry
- Cross-modal analysis workflows
- Performance optimization with real tool chains

## DO NOT
- Create any fallback or mock patterns in production code
- Hide contract validation failures behind workarounds
- Use dictionary interfaces instead of ToolRequest/ToolResult
- Manually register tools instead of using auto-discovery
- Skip evidence documentation for any implementation claims

## DO
- Implement complete auto-registration system
- Fix all contract validation failures systematically  
- Use ToolRequest/ToolResult interface consistently
- Document all implementation with execution evidence
- Test integration thoroughly before claiming success

## Files Modified This Phase
- `src/processing/enhanced_batch_scheduler.py` - Fixed simulation patterns with real tool calls
- `src/tools/phase2/interactive_graph_visualizer.py` - Fixed fake success responses
- `src/mcp_tools/algorithm_tools.py` - Fixed placeholder implementations
- `src/ui/enhanced_dashboard.py` - Fixed placeholder data methods
- `src/api/cross_modal_api.py` - Completed pipeline integration
- Created: `tests/mocks/llm_mock_provider.py` - Test-only mock isolation

Evidence of previous phase completion: `evidence/current/Evidence_Phase_Production_Readiness_Fixes.md`