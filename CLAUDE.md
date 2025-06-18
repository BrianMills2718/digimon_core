# CLAUDE.md

This file guides Claude Code through Super-Digimon GraphRAG system development. It travels with every session to provide actionable context and strategic focus.

## Current Status - STRATEGIC PAUSE ⚠️

**Last Updated**: 2025-06-18  
**Phase 1**: ✅ Fully functional (484 entities, 228 relationships extracted)  
**Phase 2**: ❌ Integration broken (API compatibility issues)  
**Phase 3**: 🔧 Standalone tools working but not integrated  
**Critical Issue**: **Cannot reliably switch between phases** due to missing integration architecture  
**Strategic Decision**: **Architecture-First Development** - Fix integration foundation before adding complexity

## v2.0 Strategic Focus: Integration Architecture First

### 🎯 PRIORITY: Architecture Foundation Before Features

**Why Phase 1→2 Integration Failed**:
- No common interface contracts between phases
- Service API evolution without backward compatibility  
- UI retrofitted instead of properly abstracted
- No automated integration testing

**Current Approach is Wrong**: Building Phase 3+ without fixing Phase 1→2 integration compounds the problem exponentially.

### Immediate Priorities (Architecture Foundation):

#### A1: Service Compatibility Layer ⭐ START HERE
**Purpose**: Fix core service API drift that breaks Phase 2  
**Critical Issue**: `WorkflowStateService.update_workflow_progress()` API mismatch
**Required Fix**:
```python
# Phase 2 calls (broken):
service.update_workflow_progress(workflow_id, current_step=9, metadata={...})

# Service expects (working):  
service.update_workflow_progress(workflow_id, step_number=9, error_message=...)

# Solution: Add backward compatibility layer
```

#### A2: Standard Phase Interface Design
**Purpose**: Define common contract all phases must implement  
**Required Interface**:
```python
class GraphRAGPhase(ABC):
    @abstractmethod
    def process_document(self, request: ProcessingRequest) -> ProcessingResult:
        pass
    
    @abstractmethod
    def get_phase_info(self) -> Dict[str, Any]:
        pass
```

#### A3: UI Adapter Pattern  
**Purpose**: Handle phase differences cleanly instead of retrofitting
**Current Problem**: UI assumes all phases work like Phase 1
**Required Solution**: Adapter layer that translates UI requests to phase-specific calls

#### A4: Integration Testing Framework
**Purpose**: Automated validation that phases work together
**Why Critical**: Manual testing missed the Phase 1→2 incompatibility  
**Required Coverage**: Service compatibility, phase switching, UI integration

### Original Phase 3 Plan (Postponed):

#### T301: Multi-Document Knowledge Fusion ✅ COMPLETE
**Purpose**: Modular MCP tools for flexible knowledge fusion across document collections  
**Location**: `src/tools/phase3/t301_multi_document_fusion_tools.py`  
**Status**: Implemented but NOT integrated into main MCP server
**Architecture**: Separate MCP tools for maximum flexibility and composability

**To expose the tools**:
```bash
# Option 1: Run standalone Phase 3 MCP server
python src/tools/phase3/t301_multi_document_fusion_tools.py

# Option 2: Integrate into main server (not done yet)
# Would require importing tools in src/mcp_server.py
```

**Individual MCP Tools**:
```python
@mcp.tool()
def calculate_entity_similarity(
    entity1_name: str, entity2_name: str,
    entity1_type: str, entity2_type: str,
    use_embeddings: bool = True,  # OpenAI embeddings for semantic understanding
    use_string_matching: bool = True  # Fast string comparison
) -> Dict[str, Any]

@mcp.tool()
def find_entity_clusters(
    entities: List[Dict], 
    similarity_threshold: float = 0.85,
    use_embeddings: bool = True  # Can disable for speed
) -> Dict[str, Any]

@mcp.tool()
def resolve_entity_conflicts(
    entities: List[Dict],
    strategy: str = "confidence_weighted",  # or "temporal_priority", "evidence_based"
    use_llm: bool = False,
    llm_model: Optional[str] = None
) -> Dict[str, Any]

@mcp.tool()
def merge_relationship_evidence(
    relationships: List[Dict]
) -> Dict[str, Any]

@mcp.tool()
def check_fusion_consistency(
    entities: List[Dict],
    relationships: List[Dict],
    check_duplicates: bool = True,
    check_conflicts: bool = True,
    check_ontology: bool = False
) -> Dict[str, Any]
```

**Implementation Requirements**:
1. Each tool must be independently callable via MCP
2. OpenAI embeddings integration for semantic similarity (with on/off switch)
3. Multiple conflict resolution strategies
4. Flexible consistency checking options
5. Clear separation of concerns - no monolithic classes

**Success Criteria**:
- [x] All 5 tools exposed as separate MCP endpoints in standalone server
- [x] Embeddings work correctly when enabled (using EnhancedIdentityService)
- [x] String matching provides fast alternative when embeddings disabled
- [x] Each tool validates inputs and handles errors gracefully
- [x] Tools can be composed into custom pipelines
- [x] Performance: <1s for string matching, <3s with embeddings per entity pair
- [ ] Integration into main Super-Digimon MCP server (optional)

#### T302: Advanced Reasoning Engine (POSTPONED)
**Status**: Postponed until horizontal capabilities complete  
**Purpose**: LLM-driven logical inference over knowledge graphs  
**Rationale**: Need complete data extraction before advanced reasoning  

#### T303-T306: (POSTPONED)
- T303: Temporal Knowledge Tracking
- T304: Cross-Domain Ontology Federation  
- T305: Advanced Query Understanding
- T306: Research Evaluation Framework

**These will be revisited after horizontal capabilities are solid**  

## Critical Implementation Rules

### 1. Build on Phase 2 Foundation
```python
# Always use existing Phase 2 components
from src.tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor
from src.tools.phase2.t31_ontology_graph_builder import OntologyAwareGraphBuilder
from src.core.enhanced_identity_service import EnhancedIdentityService

# Phase 3 tools extend, don't replace Phase 2
class MultiDocumentFusion(OntologyAwareGraphBuilder):
    def __init__(self, base_builder: OntologyAwareGraphBuilder):
        self.base_builder = base_builder
```

### 2. Advanced Quality Gates
**Before marking ANY Phase 3 tool complete**:
- [ ] All Phase 2 functionality preserved and enhanced
- [ ] Multi-document scenarios tested (10+ documents)
- [ ] Temporal consistency validated across time ranges
- [ ] Cross-domain federation scenarios proven
- [ ] Research-grade evaluation metrics computed
- [ ] Academic reproducibility maintained (TORC compliance)

### 3. Research-Grade Testing Requirements
```python
# Phase 3 requires research validation
def test_academic_benchmark():
    # Test against known GraphRAG datasets
    # Compare with published baselines
    # Validate statistical significance
    pass

def test_multi_domain_scenarios():
    # Climate + Economics ontologies
    # Medicine + Technology domains
    # Cross-domain reasoning validation
    pass
```

### 4. Performance Requirements
- **Multi-Document Fusion**: <10s per document addition
- **Advanced Reasoning**: <30s for 3-hop logical inference
- **Temporal Analysis**: <60s for 1-year knowledge evolution
- **Cross-Domain**: <5s for ontology mapping operations
- **Memory Efficiency**: <2GB for 1000-document collections

## Development Standards

### Enhanced Self-Healing Patterns for Phase 3

1. **Graceful degradation for complex reasoning**
   ```python
   # Good: Fallback to simpler reasoning
   try:
       result = advanced_multi_hop_reasoning(query, max_depth=5)
   except ComplexityError:
       result = simple_graph_traversal(query, max_depth=2)
   ```

2. **Incremental processing for large document sets**
   ```python
   # Good: Process in batches with checkpoints
   for batch in chunk_documents(documents, batch_size=10):
       checkpoint_id = create_checkpoint(batch_id)
       try:
           process_document_batch(batch)
           commit_checkpoint(checkpoint_id)
       except Exception:
           rollback_to_checkpoint(checkpoint_id)
   ```

3. **Confidence-aware conflict resolution**
   ```python
   # Good: Weight by evidence strength
   def resolve_conflicts(conflicting_facts):
       return weighted_average(
           facts=conflicting_facts,
           weights=[f.confidence * f.evidence_count for f in conflicting_facts]
       )
   ```

## UI Testing Interface Requirements

### 🔥 CRITICAL: NO MOCK FUNCTIONALITY EVER

**The UI must NEVER contain mocked, stubbed, or fake functionality.**

**If a feature isn't available, the UI must:**
1. **Crash loudly** with clear error messages
2. **Disable the feature** completely 
3. **Show honest status** about what's missing
4. **NEVER pretend** something works when it doesn't

### UI Update Protocol

**MANDATORY: Update UI after every phase implementation**

After implementing any new phase or feature:

1. **Add real integration** to UI for the new functionality
2. **Create test scenarios** that prove the new features work
3. **Remove any temporary placeholders** from previous versions
4. **Test actual functionality** end-to-end with real data
5. **Update UI documentation** with new capabilities

### UI Testing Requirements

**For each phase, the UI must provide:**

#### Phase 1 Testing
- **Document upload** → **Real PDF/TXT processing** → **Actual entity extraction**
- **Query interface** → **Real graph database queries** → **Actual results**
- **Graph visualization** → **Real extracted entities/relationships**
- **Export functionality** → **Actual data from processing pipeline**

#### Phase 2 Testing (when available)
- **Ontology selection** → **Real ontology-aware extraction**
- **Comparison view** → **Phase 1 vs Phase 2 results side-by-side**
- **Enhanced visualization** → **Ontology-typed entities with colors**
- **Quality metrics** → **Real confidence scores and ontology compliance**

#### Phase 3 Testing (when available)
- **Multi-document upload** → **Real T301 fusion tools**
- **Entity deduplication** → **Actual similarity calculations with embeddings**
- **Conflict resolution** → **Real strategy selection and LLM arbitration**
- **Cross-document queries** → **Actual federated search across documents**

### Failure Modes

**Good: Feature unavailable**
```python
if not PHASE2_AVAILABLE:
    st.error("❌ Phase 2 not installed. Run: pip install -r requirements_phase2.txt")
    st.stop()  # Hard stop, no fake functionality
```

**Bad: Mocked functionality**
```python
if not PHASE2_AVAILABLE:
    # This is FORBIDDEN
    result = "Mock ontology extraction results..."
    st.info("Using simulated Phase 2 results")
```

### Testing Validation

**Each phase must have UI tests that prove:**

1. **Upload real documents** from `examples/pdfs/`
2. **Process with actual pipeline** (no mocking)
3. **Query with real database** (Neo4j/SQLite/Qdrant)
4. **Export actual results** that can be validated externally
5. **Compare phases** with identical documents to show differences

### UI Architecture Rules

1. **Real integrations only** - Import actual pipeline components
2. **Fail fast** - If import fails, show error and stop
3. **No degradation** - Either feature works 100% or is disabled
4. **Honest status** - Show exactly what's available/missing
5. **Test scenarios** - Provide sample data that proves functionality

## Project Structure (Phase 3 Focus)

```
Digimons/
├── src/tools/phase3/           # NEW: Phase 3 implementations
│   ├── t301_multi_document_fusion.py
│   ├── t302_advanced_reasoning.py
│   ├── t303_temporal_knowledge.py
│   ├── t304_cross_domain_federation.py
│   ├── t305_query_understanding.py
│   └── t306_evaluation_framework.py
├── src/tools/phase2/           # EXISTING: Phase 2 foundation
│   ├── t23c_ontology_aware_extractor.py
│   ├── t31_ontology_graph_builder.py
│   └── interactive_graph_visualizer.py
├── tests/phase3/               # NEW: Phase 3 testing
│   ├── test_multi_document_scenarios.py
│   ├── test_temporal_analysis.py
│   └── test_research_benchmarks.py
└── docs/phase3/               # NEW: Phase 3 documentation
    ├── MULTI_DOCUMENT_ARCHITECTURE.md
    └── RESEARCH_EVALUATION_PROTOCOL.md
```

## Environment Variables (Phase 3 Extensions)

```bash
# Existing Phase 2 variables remain unchanged
NEO4J_URI=bolt://localhost:7687
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

# NEW: Phase 3 specific configurations
REASONING_MODEL=gemini-2.0-flash-exp
MAX_REASONING_DEPTH=5
TEMPORAL_GRANULARITY=daily
BENCHMARK_DATASETS_PATH=./data/benchmarks
FUSION_CONFIDENCE_THRESHOLD=0.8
```

## Immediate Next Actions (Architecture Foundation)

1. [ ] **A1: Fix Service Compatibility**: Add backward compatibility to WorkflowStateService
2. [ ] **A2: Design Phase Interface**: Create GraphRAGPhase abstract base class  
3. [ ] **A3: Build UI Adapter**: Create adapter pattern for phase-agnostic UI
4. [ ] **A4: Integration Testing**: Automated framework to catch phase interaction issues
5. [ ] **Validate**: Prove Phase 1 ↔ Phase 2 switching works reliably in UI
6. [ ] **Only then**: Proceed with horizontal capabilities (tables, enhanced PDF)

## Success Metrics for v2.0 Architecture (REVISED)

**Architecture Foundation Complete When**:
- [ ] **Phase Switching**: User can reliably switch Phase 1 ↔ 2 ↔ 3 in UI without errors
- [ ] **Service Compatibility**: Core services maintain backward compatibility across versions
- [ ] **Integration Testing**: >95% automated test coverage for phase interactions  
- [ ] **Interface Compliance**: All phases implement standard GraphRAGPhase contract
- [ ] **UI Abstraction**: UI handles phase differences through adapter pattern, not retrofitting
- [ ] **Error Handling**: Graceful failure with actionable error messages when phases unavailable

**Only After Architecture Foundation**:
- Table extraction and PDF enhancements (horizontal capabilities)
- Advanced reasoning and temporal tracking (vertical capabilities)  
- Multi-document fusion integration (T301 → main pipeline)
- Research evaluation framework (academic benchmarks)

Remember: **Integration Architecture > Feature Accumulation**. Fix the foundation first, then build on it.