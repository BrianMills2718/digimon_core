# Task TD.1: Architectural Decomposition

## Overview
Break down monster files and fix critical syntax errors to improve maintainability and testability.

**Duration**: Weeks 1-2  
**Priority**: CRITICAL  
**Prerequisites**: None  

## Current State Analysis

### Monster Files
1. **t301_multi_document_fusion.py**: 2,423 lines
   - Mixed responsibilities: fusion, conflict resolution, quality assessment
   - Impossible to unit test effectively
   - High cognitive load for developers

2. **tool_adapters.py**: 1,892 lines
   - All adapters in single file
   - High duplication between adapters
   - Difficult to modify individual adapters

3. **pipeline_orchestrator.py**: 1,460 lines
   - Handles all workflow types
   - Mixed concerns: execution, validation, monitoring
   - Complex conditional logic

### Syntax Errors
- Multiple `await` outside async function in:
  - production_monitoring.py:275
  - backup_manager.py (indentation)
  - metrics_collector.py (indentation)

## Implementation Plan

### Step 1: Fix Syntax Errors (Day 1-2) - TDD Approach

**🧪 TDD PROCESS**:
1. **Red Phase**: Write tests that expose syntax errors
2. **Green Phase**: Fix syntax errors to make tests pass  
3. **Refactor Phase**: Clean up fixes while maintaining passing tests

**Test First - Create Failing Tests**:
```python
# tests/unit/monitoring/test_syntax_errors_fix.py
def test_production_monitoring_compiles():
    """Test that production_monitoring.py compiles without syntax errors"""
    import py_compile
    import tempfile
    
    # This should fail initially due to await outside async
    try:
        py_compile.compile('src/monitoring/production_monitoring.py', doraise=True)
        assert False, "Expected syntax error not found"
    except py_compile.PyCompileError as e:
        assert "await" in str(e) and "outside async function" in str(e)

def test_backup_manager_compiles():
    """Test that backup_manager.py compiles without indentation errors"""
    # Similar pattern for backup_manager.py

def test_metrics_collector_compiles():
    """Test that metrics_collector.py compiles without import errors"""
    # Similar pattern for metrics_collector.py
```

**Then Fix - Make Tests Pass**:
```python
# VERIFIED ISSUE: production_monitoring.py:275
# Current problematic code:
await asyncio.sleep(min(interval, 1.0))  # Outside async function - Line 275

# TDD Fix: Move inside async function or convert to sync
def _monitoring_loop_sync(self, interval: float):
    """Sync version for non-async contexts"""
    time.sleep(min(interval, 1.0))

async def _monitoring_loop_async(self, interval: float):  
    """Async version for async contexts"""
    await asyncio.sleep(min(interval, 1.0))
```

**🎯 VERIFIED FILES TO FIX** (2025-07-25 Analysis):
- [x] **src/monitoring/production_monitoring.py:275** - `await asyncio.sleep(min(interval, 1.0))` outside async ✅ VERIFIED
- [x] **src/core/backup_manager.py:793** - Malformed import causing IndentationError ✅ VERIFIED
- [x] **src/core/metrics_collector.py:180** - Similar malformed import pattern ✅ VERIFIED

**Success Criteria**:
- [ ] All files pass `python -m py_compile` 
- [ ] All syntax error tests pass
- [ ] No functionality regression in affected modules

### Step 2: Decompose PipelineOrchestrator (Day 3-5)

**Current Structure**:
```python
class PipelineOrchestrator:
    # 1,460 lines handling everything
    def orchestrate_research_workflow(...)  # 137 lines
    def _execute_tool(...)  # 74 lines
    def _process_document(...)  # 118 lines
    # ... many more mixed responsibilities
```

**Target Structure**:
```python
# src/core/orchestrators/document_processing_orchestrator.py
class DocumentProcessingOrchestrator:
    """Handles T01-T15A document processing pipeline"""
    def __init__(self, service_container: ServiceContainer):
        self.pdf_loader = service_container.resolve(PDFLoaderInterface)
        self.text_chunker = service_container.resolve(TextChunkerInterface)
    
    async def process_documents(self, documents: List[Path]) -> List[ProcessedDocument]:
        # Focused on document processing only
        pass

# src/core/orchestrators/graph_building_orchestrator.py  
class GraphBuildingOrchestrator:
    """Handles T23A-T34 graph construction pipeline"""
    async def build_graph(self, chunks: List[TextChunk]) -> Graph:
        # Focused on graph building only
        pass

# src/core/orchestrators/analytics_orchestrator.py
class AnalyticsOrchestrator:
    """Handles T68 PageRank and T49 queries"""
    async def analyze_graph(self, graph: Graph) -> AnalyticsResults:
        # Focused on analytics only
        pass

# src/core/orchestrators/workflow_coordinator.py
class WorkflowCoordinator:
    """Coordinates between specialized orchestrators"""
    def __init__(self, orchestrators: Dict[str, BaseOrchestrator]):
        self.orchestrators = orchestrators
    
    async def execute_workflow(self, workflow_type: str, config: Dict) -> Results:
        # Delegates to appropriate orchestrators
        pass
```

### Step 3: Split t301_multi_document_fusion.py (Day 6-8)

**Current monolith**:
```python
class T301MultiDocumentFusion:
    # 2,423 lines of mixed concerns
```

**Target modular structure**:
```python
# src/tools/phase3/fusion/document_fusion.py
class DocumentFusion:
    """Core document fusion logic"""
    def fuse_documents(self, documents: List[Document]) -> FusedDocument:
        pass

# src/tools/phase3/fusion/conflict_resolution.py
class ConflictResolver:
    """Handles conflicts between document sources"""
    def resolve_conflicts(self, conflicts: List[Conflict]) -> Resolution:
        pass

# src/tools/phase3/fusion/quality_assessment.py
class QualityAssessor:
    """Assesses quality of fused results"""
    def assess_quality(self, fusion_result: FusedDocument) -> QualityScore:
        pass

# src/tools/phase3/fusion/fusion_utilities.py
"""Shared utilities for document fusion"""
def calculate_similarity(doc1: Document, doc2: Document) -> float:
    pass

# src/tools/phase3/t301_multi_document_fusion_unified.py
class T301MultiDocumentFusionUnified(BaseTool):
    """Thin wrapper coordinating fusion components"""
    def __init__(self):
        self.fusion = DocumentFusion()
        self.resolver = ConflictResolver()
        self.assessor = QualityAssessor()
```

### Step 4: Refactor tool_adapters.py (Day 9-10)

**Current structure**:
```python
# tool_adapters.py - 1,892 lines
class ToolAdapter1: ...
class ToolAdapter2: ...
# ... 20+ adapters in one file
```

**Target structure**:
```python
# src/core/adapters/base_adapter.py
class BaseToolAdapter(ABC):
    """Base class for all tool adapters"""
    @abstractmethod
    def adapt(self, tool: BaseTool) -> AdaptedTool:
        pass

# src/core/adapters/document_adapters.py
class PDFLoaderAdapter(BaseToolAdapter):
    """Adapter for PDF loading tools"""
    pass

class WordLoaderAdapter(BaseToolAdapter):
    """Adapter for Word loading tools"""
    pass

# src/core/adapters/analysis_adapters.py
class NERAdapter(BaseToolAdapter):
    """Adapter for NER tools"""
    pass

# src/core/adapters/adapter_factory.py
class AdapterFactory:
    """Factory for creating appropriate adapters"""
    def create_adapter(self, tool_type: str) -> BaseToolAdapter:
        # Returns appropriate adapter based on tool type
        pass
```

## Testing Strategy

### Unit Tests for Decomposed Components
```python
# tests/unit/orchestrators/test_document_processing_orchestrator.py
class TestDocumentProcessingOrchestrator:
    def test_process_single_document(self):
        # Test single document processing
        pass
    
    def test_process_multiple_documents_parallel(self):
        # Test parallel processing
        pass

# tests/unit/fusion/test_document_fusion.py
class TestDocumentFusion:
    def test_fuse_similar_documents(self):
        # Test fusion of similar content
        pass
```

## Success Criteria

### Immediate (End of Week 1)
- [ ] All syntax errors resolved
- [ ] Tests pass without syntax errors
- [ ] No `await` outside async function

### Week 2 Completion
- [ ] PipelineOrchestrator < 200 lines
- [ ] Each orchestrator < 400 lines  
- [ ] t301 split into 4+ files, each < 500 lines
- [ ] tool_adapters split into 5+ files
- [ ] All tests passing
- [ ] No functionality regression

## Rollback Plan
1. All changes in feature branches
2. Incremental merging with full test suite
3. Performance benchmarks before/after
4. Easy revert if issues detected

## Next Steps
After completion:
1. Move to Task TD.2 (Dependency Injection)
2. Update all imports in dependent code
3. Run full integration test suite
4. Update documentation