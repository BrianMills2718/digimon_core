# CLAUDE.md

This file guides Claude Code through Phase 3 Advanced GraphRAG implementation. It travels with every session to provide actionable context and success criteria.

## Current Status

**Phase 2**: Complete with 85.7% adversarial pass rate ✅  
**Current Phase**: Phase 3 - Advanced GraphRAG System  
**Databases**: Neo4j + Qdrant + SQLite operational ✅  
**Priority**: Multi-document fusion and advanced reasoning capabilities

## Phase 3 Implementation Priority

### T301: Multi-Document Knowledge Fusion (START HERE)
**Purpose**: Consolidate knowledge across document collections with conflict resolution  
**Location**: `src/tools/phase3/t301_multi_document_fusion.py`  
**Key Methods**:
```python
def fuse_documents(document_refs: List[str], fusion_strategy: str) -> FusionResult
def resolve_entity_conflicts(entities: List[Entity]) -> Entity
def merge_relationship_evidence(relationships: List[Relationship]) -> Relationship
def calculate_knowledge_consistency(graph_data: GraphData) -> ConsistencyMetrics
```

**Implementation Steps**:
1. Design entity consolidation algorithms with confidence scoring
2. Implement relationship evidence aggregation
3. Build conflict resolution using LLM arbitration
4. Create consistency metrics and validation

**Success Criteria**:
- [ ] 100 documents → consolidated knowledge graph with <5% entity duplicates
- [ ] Conflicting information resolved with evidence chains
- [ ] Confidence scores properly aggregated across sources
- [ ] Performance: <10s per document addition to existing graph

### T302: Advanced Reasoning Engine
**After T301 works perfectly**  
**Purpose**: LLM-driven logical inference over knowledge graphs  
**Key Methods**:
```python
def infer_implicit_relationships(graph: GraphData, reasoning_depth: int) -> List[Relationship]
def validate_logical_consistency(graph: GraphData) -> ValidationResult
def generate_reasoning_chains(query: str, graph: GraphData) -> ReasoningChain
```

### T303: Temporal Knowledge Tracking
**After T302 works perfectly**  
**Purpose**: Track entity and relationship evolution over time  
**Key Methods**:
```python
def create_temporal_snapshot(graph: GraphData, timestamp: datetime) -> TemporalSnapshot
def track_entity_evolution(entity_id: str) -> EvolutionHistory
def analyze_knowledge_drift(time_range: Tuple[datetime, datetime]) -> DriftAnalysis
```

### T304: Cross-Domain Ontology Federation
**After T303 works perfectly**  
**Purpose**: Connect and reason across multiple domain ontologies  

### T305: Advanced Query Understanding
**After T304 works perfectly**  
**Purpose**: LLM preprocessing for complex research questions  

### T306: Research Evaluation Framework
**After T305 works perfectly**  
**Purpose**: Benchmarking against academic GraphRAG standards  

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

## Immediate Next Actions

1. [ ] **Start T301**: Create `src/tools/phase3/t301_multi_document_fusion.py`
2. [ ] **Write Tests**: Create `tests/phase3/test_multi_document_scenarios.py`
3. [ ] **Design Architecture**: Document fusion strategy in `docs/phase3/`
4. [ ] **Implement Core**: Entity consolidation and conflict resolution
5. [ ] **Validate**: Test with 10+ document collection
6. [ ] **Only then**: Proceed to T302 Advanced Reasoning

## Success Metrics for Phase 3

**T301 Complete When**:
- 95% entity deduplication across 100 documents
- Conflict resolution with traceable evidence chains
- Sub-linear performance scaling with document count

**Phase 3 Complete When**:
- Multi-document knowledge fusion operational
- Advanced reasoning with 3+ hop logical inference
- Temporal knowledge tracking over months/years
- Cross-domain ontology federation working
- Research evaluation framework with academic benchmarks
- All capabilities maintain Phase 2's 85%+ adversarial robustness

Remember: **Phase 3 is research-grade GraphRAG**. Each tool must advance the state of the art while maintaining production robustness.