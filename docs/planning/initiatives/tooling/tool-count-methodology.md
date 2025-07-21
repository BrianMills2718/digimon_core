**Doc status**: Living – auto-checked by doc-governance CI

# Tool Count Methodology

**Document Purpose**: Standardize tool counting across all documentation  
**Created**: 2025-06-19  
**Status**: OFFICIAL COUNTING STANDARD

## Executive Summary

**Official Tool Count**: 13 Core GraphRAG Tools  
**Total Available Tools**: 33 (13 core + 20 MCP server tools)  
**Methodology**: Count by functional verification, not file count

## Counting Standards

### 1. What Counts as a "Tool"

A tool is counted if it meets ALL criteria:
- ✅ Has a complete implementation (not stub/placeholder)
- ✅ Can be invoked and produces results
- ✅ Has been functionally verified with test data
- ✅ Provides distinct functionality (not just a variant)

### 2. What Does NOT Count

The following are NOT counted as separate tools:
- ❌ Base classes or abstract implementations
- ❌ Optimized variants of the same functionality
- ❌ Test utilities or helper functions
- ❌ Archived or experimental implementations
- ❌ Duplicate implementations with same functionality

### 3. Official Tool Breakdown

#### Core GraphRAG Tools (13 Total)

**Phase 1: Core Pipeline (8 tools)**
- T01: PDF Loader
- T02: Text Chunker
- T03: Entity Extractor
- T04: Relationship Extractor
- T05: Graph Builder
- T06: Community Detector
- T07: Query Engine
- T08: Visualization Engine

**Phase 2: Enhanced Processing (3 tools)**
- T09: Ontology Generator
- T10: Enhanced Entity Extractor
- T11: Enhanced Relationship Builder

**Phase 3: Multi-Document (2 tools)**
- T12: Document Fusion Engine
- T13: Multi-Document Query Interface

#### MCP Server Tools (20 Additional)

**Phase 1 Pipeline Tools**
- load_pdf
- chunk_text
- extract_entities
- extract_relationships
- build_graph
- detect_communities
- run_pagerank
- query_graph
- visualize_graph
- get_graph_stats

**Phase 2 Enhancement Tools**
- generate_ontology
- extract_entities_with_ontology
- build_enhanced_graph

**Phase 3 Multi-Doc Tools**
- load_multiple_pdfs
- fuse_documents
- query_multi_docs

**Utility Tools**
- clear_graph
- export_graph
- get_service_status

### 4. File Count vs Functional Count

**File Count Reality** (~19 files):
- Phase 1: 11 files (includes base classes, variants)
- Phase 2: 4 files (includes unused enhanced versions)
- Phase 3: 4 files (includes experimental code)

**Functional Count Reality** (13 tools):
- Only count tools that meet ALL criteria above
- Exclude duplicates, variants, and experiments
- Focus on distinct, working functionality

### 5. Reporting Standards

When reporting tool counts in documentation:
1. Always use functional count (13) as primary metric
2. Clarify if discussing file count vs functional count
3. Reference this document for methodology
4. Update counts only after functional verification

### 6. Verification Commands

```bash
# Count functional tools (correct method)
python scripts/verify_tool_functionality.py

# Count tool files (for reference only)
find src/tools -name "*.py" -type f | grep -v __pycache__ | wc -l
```

## References

- [`TOOL_COUNT_CLARIFICATION.md`](TOOL_COUNT_CLARIFICATION.md)
- [`TOOL_ROADMAP_RECONCILIATION.md`](TOOL_ROADMAP_RECONCILIATION.md)
- [`CURRENT_REALITY_AUDIT.md`](CURRENT_REALITY_AUDIT.md)-e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>
