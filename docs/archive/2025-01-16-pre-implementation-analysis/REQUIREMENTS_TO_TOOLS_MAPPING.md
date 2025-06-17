# Requirements to Tools Mapping

This document maps the synthesized requirements to our 106 tools, identifying gaps and modifications needed.

## Identity System Requirements → Tools

### Three-Level Identity System

**Surface Form → Mention → Entity**

| Requirement | Existing Tools | Modifications Needed |
|------------|----------------|---------------------|
| Surface form detection | T13-T14 (Text cleaning/normalization) | Add surface form preservation |
| Mention creation | T23-T24 (Entity recognition) | Add mention ID generation |
| Entity resolution | T25 (Coreference), T29 (Disambiguation) | Add three-level tracking |
| Entity merging | T26 (Entity Linker) | Add merge operation |
| Multi-language names | T17-T18 (Language detection/translation) | Integrate with entity system |

**New Tools Needed**:
- T107: Identity Service Interface (wraps above tools)

## Quality/Confidence Requirements → Tools

### Universal Quality Framework

| Requirement | Existing Tools | Modifications Needed |
|------------|----------------|---------------------|
| Extraction confidence | T23-T28 (All extraction tools) | Add confidence scores |
| Propagation | None explicit | Add to all tools |
| Aggregation | T74 (Clustering) partial | Add confidence aggregation |
| Quality filtering | None explicit | Add to all retrieval tools |

**Modifications for ALL tools**:
- Add `confidence` to all outputs
- Add `quality_tier` classification
- Add `warnings` list for issues

## Versioning Requirements → Tools

### Four-Level Versioning

| Requirement | Existing Tools | Modifications Needed |
|------------|----------------|---------------------|
| Schema versioning | None | Add to MCP server layer |
| Data versioning | T40 (Version Controller) | Expand beyond graphs |
| Graph versioning | T40 (Version Controller) | Already supports |
| Analysis versioning | None explicit | Add to analysis tools |

**New Tools Needed**:
- T108: Version Service Interface

## Data Flow Requirements → Tools

### Reference-Based Architecture

| Requirement | Existing Tools | Modifications Needed |
|------------|----------------|---------------------|
| Reference generation | None explicit | Add to all storage tools |
| Reference resolution | None explicit | Add to all retrieval tools |
| Streaming support | T12 (Stream Processor) | Extend to all ingestion |
| Batch processing | Implicit in some | Make explicit in all |

**Pattern to Apply Everywhere**:
```python
# Instead of returning data, return:
{
    "refs": ["storage://type/id"],
    "count": 1000,
    "sample": [... first 10 ...]
}
```

## Format Transformation Requirements → Tools

### Flexible Transformations

| Transformation | Existing Tools | Gaps |
|----------------|----------------|------|
| Document → Chunks | T15-T16 (Chunkers) | ✓ |
| Chunks → Entities | T23-T24 (Entity recognition) | ✓ |
| Entities → Graph | T31-T35 (Graph builders) | ✓ |
| Graph → Table | **Missing** | Need T115 |
| Table → Graph | **Missing** | Need T116 |
| Any → Embeddings | T41-T44 (Embedders) | ✓ |
| Graph → Statistics | T68-T75 (Analysis) | Partial |

**New Tools Needed**:
- T115: Graph to Table Converter
- T116: Table to Graph Builder
- T117: Format Auto-Selector

## Advanced Requirements → Tools

### Temporal Reasoning

| Requirement | Existing Tools | Modifications Needed |
|------------|----------------|---------------------|
| Temporal validity | None explicit | Add temporal attributes |
| Paradox detection | None | New algorithm needed |
| Multi-timeline | None | New representation |
| Semantic drift | None | New tracking system |

**New Tools Needed**:
- T118: Temporal Reasoner
- T119: Semantic Evolution Tracker

### Causal Preservation

| Requirement | Existing Tools | Modifications Needed |
|------------|----------------|---------------------|
| Causal graphs | Basic graph support | Add causal metadata |
| Confounder tracking | None | Add to relationships |
| Counterfactuals | None | New analysis type |

**Integration Needed**:
- Modify PyWhy integration (T116 placeholder)
- Add causal metadata to all graph tools

### Uncertainty Propagation

| Requirement | Existing Tools | Modifications Needed |
|------------|----------------|---------------------|
| Track uncertainty | None systematic | Add to all tools |
| Propagate | None | New algorithms |
| Monte Carlo | None | Add sampling methods |

**New Service Needed**:
- T120: Uncertainty Propagation Service

## Tool Modification Summary

### High Priority Modifications

**ALL Tools Must Add**:
1. Confidence scores in outputs
2. Quality tier classification  
3. Reference-based returns
4. Streaming support (where applicable)
5. Provenance metadata

### Tool-Specific Critical Modifications

**Entity Recognition Tools (T23-T24)**:
- Generate mention IDs
- Track surface forms
- Output entity candidates with scores

**Graph Building Tools (T31-T35)**:
- Accept mentions and entities
- Preserve all metadata
- Support incremental building

**Analysis Tools (T49-T75)**:
- Work with references not full data
- Propagate confidence
- Support partial results

### New Tools Summary (T107-T120)

1. **T107**: Identity Service Interface
2. **T108**: Version Service Interface  
3. **T109**: Entity Normalizer (from previous)
4. **T110**: Provenance Service Interface
5. **T111**: Quality Service Interface
6. **T112**: Constraint Engine
7. **T113**: Ontology Manager (from previous)
8. **T114**: Provenance Tracker (from previous)
9. **T115**: Graph to Table Converter
10. **T116**: Table to Graph Builder
11. **T117**: Format Auto-Selector
12. **T118**: Temporal Reasoner
13. **T119**: Semantic Evolution Tracker
14. **T120**: Uncertainty Propagation Service

## Implementation Strategy

### Phase 1: Core Infrastructure
1. Implement service interfaces (T107-T111)
2. Modify entity tools for three-level system
3. Add quality/confidence to base tools
4. Implement reference architecture

### Phase 2: Critical Converters
1. Graph ↔ Table converters (T115-T116)
2. Format selector (T117)
3. Streaming modifications
4. Uncertainty basics (T120)

### Phase 3: Advanced Features
1. Temporal reasoning (T118)
2. Semantic evolution (T119)
3. Constraint engine (T112)
4. Ontology manager (T113)

## Validation Checklist

Each modified tool must:
- [ ] Accept and return references (not full data)
- [ ] Track confidence scores
- [ ] Generate provenance metadata
- [ ] Support streaming (if applicable)
- [ ] Handle partial failures gracefully
- [ ] Preserve entity identity through pipeline
- [ ] Maintain quality tier information

This mapping shows that while our 106 tools cover most functionality, they need systematic modifications to support the requirements discovered through mock workflows. The addition of 14 new tools (T107-T120) and modifications to existing tools will create a system capable of handling all the complexities revealed in our analysis.