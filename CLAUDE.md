# KGAS Development Instructions - Real Issues Resolution

## Current Priority Tasks (2025-08-03)

### 🚨 Critical Issues in Production Code (Immediate Fix Required)

#### 1. Enhanced Batch Scheduler - Simulation Processing
**File**: `src/processing/enhanced_batch_scheduler.py`  
**Issue**: Lines 373-378 use `asyncio.sleep()` for document processing simulation instead of real tools  
**Problem**: Production batch scheduler doesn't actually process documents - it just sleeps and returns fake results

**Current Violation**:
```python
# CRITICAL VIOLATION at line 373:
await asyncio.sleep(job.estimated_processing_time / 10)  # Simulated for testing

# Simulate random failures for testing retry logic  
import random
if random.random() < 0.1 and job.retry_count == 0:  # 10% failure rate
    raise Exception("Simulated processing failure")
```

**Required Fix**: Replace simulation with real document processing pipeline using existing tools:
- Import and use `T01PDFLoaderUnified`, `T15ATextChunkerUnified`, `T23ASpacyNERUnified` 
- Initialize with `ServiceManager()` for real database connections
- Execute actual tool pipeline: `pdf_loader.execute()` → `chunker.execute()` → `ner.execute()`
- Return real processing results (entity counts, processing times, actual errors)
- Remove all `asyncio.sleep()` and `random.random()` simulation patterns

**Success Criteria**: Batch scheduler processes real documents and extracts actual entities instead of sleeping

#### 2. Graph Visualizer - Fake Success Responses  
**File**: `src/tools/phase2/interactive_graph_visualizer.py`  
**Issue**: Lines 252-259 return fake success responses when database is unavailable  
**Problem**: Tool lies about success status instead of failing fast

**Current Violation**:
```python
# VIOLATION at line 252:
if not self.is_connected:
    return {
        "status": "success",  # LIE - not actually successful
        "result": "Visualization query executed in offline mode",
        "message": "Database connection not available - returning mock response",
        "nodes": 0,
        "edges": 0
    }
```

**Required Fix**: Fail fast with error status instead of lying about success:
- Change `"status": "success"` to `"status": "error"`
- Return proper error message with actionable information
- Remove "offline mode" pretense - either connect to database or fail
- Add error code like `"error_code": "DATABASE_UNAVAILABLE"`
- Include connection troubleshooting info in error message

**Success Criteria**: Tool honestly reports failures instead of returning fake success

#### 3. Mock APIs in Production Imports
**File**: `src/tools/phase2/extraction_components/llm_integration.py`  
**Issue**: Lines 506+ contain MockAPIProvider class in production code  
**Problem**: Risk of production code accidentally using mock APIs instead of real ones

**Current Violation**:
```python
# VIOLATION at line 506:
class MockAPIProvider:
    """Provides mock LLM responses for testing."""
    
    def mock_extract(self, text: str, ontology: 'DomainOntology') -> Dict[str, Any]:
        # Generate mock entities based on ontology types...
```

**Required Fix**: Move mock classes to test-only location:
- Create `tests/mocks/llm_mock_provider.py` for test-only mocks
- Remove `MockAPIProvider` from production file
- Update any test imports to use `from tests.mocks.llm_mock_provider import MockAPIProvider`
- Ensure production code paths never import or use mock classes
- Add validation to prevent accidental mock usage in production

**Success Criteria**: No mock/test classes accessible from production code imports

### ⚠️ Technical Debt Issues (Medium Priority)

#### 4. Placeholder Algorithm Implementations
**File**: `src/mcp_tools/algorithm_tools.py`  
**Issue**: Lines 417-421 contain placeholder implementations that return fake data  
**Problem**: Functions return placeholder classifications instead of real analysis

**Current Violation**:
```python
# VIOLATION at line 417:
# TODO: Implement actual analysis logic based on theory
# This is a placeholder implementation
classification = "placeholder"
confidence = 0.5
```

**Required Fix**: Implement actual algorithm logic or remove functions:
- Either implement real classification algorithms based on theory
- Or remove placeholder functions and return clear "not implemented" errors
- Document which algorithms are needed vs. which should be removed
- Replace fake confidence scores with real calculated values

#### 5. UI Components with Placeholder Data Methods
**Files**: Multiple UI files have placeholder data retrieval methods
- `src/ui/enhanced_dashboard.py` line 451: "Helper methods for data retrieval (placeholders)"
- `src/ui/research_analytics_dashboard.py` line 731: "Data retrieval methods (placeholders)"  
- `src/ui/batch_processing_monitor.py` line 558: "Helper methods for data retrieval (placeholders)"

**Required Fix**: Implement real data retrieval or remove placeholder UI:
- Connect to actual data sources (Neo4j, SQLite, service APIs)
- Replace placeholder methods with real database queries
- Remove UI components that can't be implemented with real data
- Add proper error handling for data retrieval failures

#### 6. Incomplete API Integrations
**File**: `src/api/cross_modal_api.py`  
**Issue**: Line 195 has TODO for core service integration  
**Problem**: API endpoints may not integrate with core pipeline services

**Current Violation**:
```python
# TODO: When core services are fixed, integrate with pipeline:
# from src.core.orchestration import PipelineOrchestrator, PipelineConfig, Phase
```

**Required Fix**: Complete API integration with core services:
- Import and integrate with `PipelineOrchestrator`
- Connect API endpoints to real service pipeline
- Test API endpoints with actual data processing
- Remove TODO comments once integration is complete

## Implementation Standards

### Zero Tolerance for Shortcuts
- **NO `asyncio.sleep()` FOR PROCESSING** - Use actual document processing tools, not time delays
- **NO FAKE SUCCESS RESPONSES** - Fail fast with honest error messages
- **NO MOCK/TEST CODE IN PRODUCTION** - Keep test utilities in test-only directories
- **NO PLACEHOLDER IMPLEMENTATIONS** - Either implement real functionality or remove features
- **REAL SERVICE INTEGRATION** - Connect to actual databases, APIs, and processing pipelines

### Evidence Requirements
For each fix, create `Evidence_Fix_{TaskName}.md` with:
1. **Before/After Code Comparison** - Show actual code changes made
2. **Execution Evidence** - Logs proving real processing vs. simulation
3. **Error Handling Evidence** - Demonstrate proper error responses
4. **Integration Testing** - Show services work together correctly

### Validation Commands

```bash
# Search for remaining simulation patterns
grep -r "asyncio\.sleep.*processing\|simulate.*processing" src/

# Find fake success responses  
grep -r "status.*success.*mock\|status.*success.*fake" src/

# Find mock/test code in production
find src/ -name "*.py" -exec grep -l "Mock\|mock.*class\|fake.*class" {} \;

# Find placeholder implementations
grep -r "placeholder.*implementation\|TODO.*implement" src/
```

### File Structure Reference

**Core Processing Tools** (for batch scheduler fix):
```
src/tools/phase1/
├── t01_pdf_loader_unified.py    # Real PDF processing
├── t15a_text_chunker_unified.py # Real text chunking  
├── t23a_spacy_ner_unified.py    # Real entity extraction
└── base_tool.py                 # ToolRequest/ToolResult interfaces
```

**Service Integration** (for all fixes):
```
src/core/
├── service_manager.py           # Real service connections
└── pipeline_orchestrator.py    # Real workflow orchestration
```

## DO NOT
- Add any fallback or mock patterns to production code
- Hide errors with fake success responses
- Use simulated processing instead of real tools
- Leave placeholder implementations in production
- Mix test utilities with production code

## DO  
- Fail fast when services are unavailable
- Use real processing tools for all operations
- Return honest error messages with actionable information
- Implement complete functionality or remove incomplete features
- Separate test code from production code clearly

## Success Metrics
- **No `asyncio.sleep()` patterns** in processing code
- **No fake success responses** when operations fail
- **No mock/test classes** accessible from production imports
- **Real processing results** from actual tool execution
- **Honest error handling** with proper status codes