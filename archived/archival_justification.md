# KGAS Archival Justifications

This file documents the rationale for archiving files and directories to maintain project cleanliness and focus on current work.

## Schema Versions Archive - 2025-07-22

### Archived: `/archived/schema_versions_2025_07_22/`

**Files Archived:**
- `meta_schema_2.json` (8.0 KB)
- `meta_schema_3.json` (10.3 KB) 
- `meta_schema_3.0.json` (8.1 KB)
- `meta_schema_3.1.json` (15.9 KB)
- `meta_schema_3.1b.json` (9.1 KB)
- `meta_schema_5.json` (8.1 KB)
- `meta_schema_6.json` (12.5 KB)
- `meta_schema_7.json` (13.2 KB)
- `meta_schema_8.json` (14.7 KB)

**Original Location:** `/lit_review/` directory

**Justification:**
1. **Obsolete Versions**: These schema versions (v2-v8) are development iterations from June 28, 2025 that have been superseded by v9 and v10
2. **Current Schemas**: Active development uses theory_meta_schema_v9.json and theory_meta_schema_v10.json
3. **Space Management**: 108 KB of legacy files were cluttering active lit_review directory
4. **Development Focus**: Current TDD implementation phase requires focus on v9/v10 schemas only
5. **Historical Preservation**: Files archived rather than deleted to maintain development history

**Impact:** 
-  No loss of functionality - current system uses v9/v10
-  Cleaner development environment 
-  Preserved for reference if needed for migration analysis
-  Supports v10 schema migration planning

**Version Strategy Going Forward:**
- **Current Production**: v9 (theory_meta_schema_v9.json)
- **Target Migration**: v10 (theory_meta_schema_v10.json)
- **Archive Policy**: Keep only current and immediate predecessor versions active

## File Renaming - 2025-07-22

### Renamed for Clarity:
- `MODELS.md` � `AI_MODELS.md` (clarifies content is about AI model specifications)
- `CORE_SCHEMAS.md` � `PYDANTIC_SCHEMAS.md` (clarifies these are Pydantic data models)
- `schemas.md` � `DATABASE_SCHEMAS.md` (clarifies these are Neo4j/SQLite schemas)

**Justification:**
1. **Clarity**: Original names were ambiguous and caused confusion
2. **Maintenance**: Clearer file names reduce cognitive load for developers
3. **Documentation**: Supports better documentation organization
4. **No Content Changes**: Only file names changed, all content preserved

## Architecture Review Documents Archive - 2025-07-23

### Archived: `/archived/architecture_reviews_2025_07_23/`

**Files Archived:**
- `ARCHITECTURE_DOCUMENTATION_REVIEW_SUMMARY.md`
- `ARCHITECTURE_REVIEW_ACTION_PLAN.md`
- `ASPIRATIONAL_ARCHITECTURE_IMPROVEMENTS.md`
- `CURRENT_ARCHITECTURE.md`

**Original Location:** `/docs/architecture/`

**Justification:**
1. **Point-in-Time Reviews**: These documents represent architecture reviews and status assessments from a previous point in time
2. **Mixing Concerns**: CURRENT_ARCHITECTURE.md mixed implementation status with architectural design, causing confusion in architecture analysis
3. **Outdated Status**: These documents reflected system state before Phase RELIABILITY was initiated
4. **Clean Separation**: Architecture documentation should focus on design, not implementation status
5. **Historical Reference**: Preserved for tracking architecture evolution and past decisions

**Impact:**
- Cleaner architecture documentation focused on design principles
- Reduced confusion between architecture and implementation
- Historical reviews preserved for reference
- Supports Phase RELIABILITY focus on fixing core issues

**Going Forward:**
- Architecture docs will focus on design, patterns, and decisions
- Implementation status tracked separately in roadmap/phases
- Reviews will be timestamped and archived after serving their purpose

## Legacy Tool Implementations Archive - 2025-07-23

### Archived: `/archived/legacy_tools_2025_07_23/`

**Files Archived:**
- `t01_pdf_loader.py` - Legacy PDF loader implementation
- `t15a_text_chunker.py` - Legacy text chunker implementation  
- `t23a_spacy_ner.py` - Legacy spaCy NER implementation
- `t27_relationship_extractor.py` - Legacy relationship extractor implementation
- `t31_entity_builder.py` - Legacy entity builder implementation
- `t34_edge_builder.py` - Legacy edge builder implementation
- `t49_multihop_query.py` - Legacy multi-hop query implementation
- `vertical_slice_workflow.py` - Deprecated workflow orchestrator

**Original Location:** `/src/tools/phase1/`

**Individual File Justifications:**

### t01_pdf_loader.py
**Justification:** Superseded by `t01_pdf_loader_unified.py` which implements the unified BaseTool interface. Both files contain identical PDF loading functionality using pypdf, but the legacy version uses custom initialization patterns and service injection, while the unified version follows ADR-001 contract-first design with standardized ToolRequest/ToolResult patterns.

### t15a_text_chunker.py  
**Justification:** Replaced by `t15a_text_chunker_unified.py` with identical sliding window chunking logic (512-token chunks, 50-token overlap). Legacy version uses custom service initialization, while unified version implements BaseTool contract with standardized execution interface and error handling.

### t23a_spacy_ner.py
**Justification:** Superseded by `t23a_spacy_ner_unified.py` containing identical spaCy NER functionality and entity type mappings. Legacy version uses custom service patterns, while unified version implements BaseTool interface with consistent contract specification and resource tracking.

### t27_relationship_extractor.py
**Justification:** Replaced by `t27_relationship_extractor_unified.py` with same pattern-based relationship extraction logic. Legacy version inherits from custom base patterns, while unified version uses BaseTool with standardized validation and execution methods.

### t31_entity_builder.py
**Justification:** Superseded by `t31_entity_builder_unified.py` with identical entity mention aggregation and Neo4j node creation logic. Legacy version extends BaseNeo4jTool with custom patterns, while unified version implements BaseTool contract with standardized input/output schemas.

### t34_edge_builder.py
**Justification:** Replaced by `t34_edge_builder_unified.py` containing same relationship edge creation and weight calculation logic. Legacy version uses BaseNeo4jTool inheritance, while unified version follows BaseTool contract with consistent error handling.

### t49_multihop_query.py
**Justification:** Superseded by `t49_multihop_query_unified.py` with identical multi-hop graph query functionality and PageRank integration. Legacy version uses custom Neo4j patterns, while unified version implements BaseTool contract with standardized query interface.

### vertical_slice_workflow.py
**Justification:** File already marked as DEPRECATED in code comments. Contains compatibility wrapper around PipelineOrchestrator with deprecation warnings. All functionality delegated to PipelineOrchestrator, making this file redundant.

**Impact:**
- Eliminates tool interface inconsistency by removing legacy patterns
- Completes migration to unified BaseTool interface (ADR-001)
- Simplifies development by providing single interface pattern
- Reduces maintenance burden of duplicate implementations
- All functionality preserved in unified counterparts

**Files Retained:**
- `t15b_vector_embedder.py` - No unified replacement, contains unique vector store implementation
- `t41_async_text_embedder.py` - No unified replacement, contains unique async optimization patterns  
- `t68_pagerank_optimized.py` - Contains specific performance optimizations not in unified version

**Going Forward:**
- Only unified tool implementations (*_unified.py) should be used in new development
- Tool factory and orchestrator configurations updated to reference unified versions only
- Legacy patterns completely eliminated from active codebase

---

*Archive Policy: Files are archived rather than deleted to preserve project history while maintaining clean active workspace. All archived content can be restored if needed.*