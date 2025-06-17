# Implementation Roadmap - Vertical Slice First

This roadmap has been restructured to implement a complete vertical slice (PDF → PageRank → Answer) before horizontal expansion.

## Overview

**Goal**: Build a PhD thesis prototype that can perform virtually any analytical method through flexible data structuring and transformation.

**Core Innovation**: Three-level identity system + Universal quality tracking + Format-agnostic processing + Complete provenance + Tool contracts.

## NEW: Vertical Slice Strategy

**Key Change**: Instead of implementing all tools in each phase sequentially, we build one complete workflow first to validate the architecture early.

### Why Vertical Slice First?

1. **Early Validation**: Discover integration issues immediately
2. **Architecture Proof**: Confirm design decisions work end-to-end
3. **Faster Feedback**: See results in days, not months
4. **Risk Reduction**: Major pivots possible before extensive coding

### Target Workflow: PDF → PageRank → Answer

This workflow exercises:
- Ingestion (PDF loading)
- Processing (NLP, entity extraction)
- Construction (graph building)
- Storage (Neo4j, FAISS)
- Analysis (PageRank)
- Retrieval (search, ranking)
- Generation (answer synthesis)

## Phase 0: Minimal Foundation for Vertical Slice

### Core Services (Minimal Implementations)

#### T107: Identity Service (MINIMAL)
- [ ] Basic mention creation
- [ ] Simple entity linking
- [ ] Defer: Complex merging, full history

#### T110: Provenance Service (MINIMAL)
- [ ] Basic operation recording
- [ ] Simple lineage
- [ ] Defer: Impact analysis, cascading

#### T111: Quality Service (MINIMAL)
- [ ] Basic confidence tracking
- [ ] Simple propagation
- [ ] Defer: Complex aggregation

#### T121: Workflow State Service (NEW - MINIMAL)
- [ ] Basic checkpointing
- [ ] Simple restore
- [ ] Defer: Compression, cleanup

### Core Data Models (Minimal)
- [ ] BaseObject with essential fields
- [ ] Entity with basic identity
- [ ] Relationship with confidence
- [ ] Mention as simple object
- [ ] Chunk with references

### Storage (Minimal)
- [ ] Neo4j basic setup
- [ ] SQLite simple schema
- [ ] FAISS basic index
- [ ] Reference system proof

### MCP Infrastructure (Minimal)
- [ ] Basic server framework
- [ ] Simple tool registration
- [ ] Basic validation
- [ ] Tool contract support

## Phase 1: Vertical Slice Implementation

### 1. Ingestion Layer
- [ ] **T01: PDF Loader (MINIMAL)**
  - Basic text extraction
  - Simple confidence (0.9 for clean text)
  - Create document with metadata
  - Defer: OCR quality, tables, images

### 2. Processing Layer
- [ ] **T15a: Sliding Window Chunker (MINIMAL)**
  - Fixed 512-token chunks
  - 50-token overlap
  - Simple position tracking
  - Defer: Semantic chunking

- [ ] **T23a: spaCy NER (MINIMAL)**
  - Standard entity types only
  - Create mentions with positions
  - Basic confidence (0.85)
  - Defer: Custom types, LLM variant

- [ ] **T27: Pattern Relationship Extractor (MINIMAL)**
  - Simple verb patterns
  - Basic confidence scoring
  - Link to entity mentions
  - Defer: Complex patterns, LLM

### 3. Construction Layer
- [ ] **T31: Entity Node Builder (MINIMAL)**
  - Mention → Entity conversion
  - Simple deduplication by name
  - Optional resolution based on config
  - Defer: Complex merging

- [ ] **T34: Relationship Edge Builder (MINIMAL)**
  - Create edges from extractions
  - Weight = confidence
  - Preserve mention links
  - Defer: Complex weights

- [ ] **T41: Sentence Embedder (MINIMAL)**
  - Use sentence-transformers
  - Embed entity descriptions
  - Store with references
  - Defer: Multiple models

### 4. Storage Layer
- [ ] **T76: Neo4j Storage (MINIMAL)**
  - Store entities and relationships
  - Basic CRUD operations
  - Simple reference generation
  - Defer: Versioning, batching

- [ ] **T78: FAISS Storage (MINIMAL)**
  - Store embeddings
  - Basic search capability
  - Reference-based storage
  - Defer: Advanced indices

### 5. Analysis Layer
- [ ] **T68: PageRank (MINIMAL)**
  - Standard PageRank algorithm
  - Handle confidence as edge weights
  - Return scored entities
  - Defer: Personalized variants

### 6. Retrieval Layer
- [ ] **T49: Entity Search (MINIMAL)**
  - Vector similarity search
  - Combine with PageRank scores
  - Basic ranking formula
  - Defer: Complex scoring

### 7. Generation Layer
- [ ] **T90: Response Generator (MINIMAL)**
  - Template-based generation
  - Include top entities by PageRank
  - Show confidence scores
  - Basic provenance
  - Defer: LLM generation

## Vertical Slice Validation

### Integration Tests
- [ ] Load test PDF successfully
- [ ] Extract 10+ entities with mentions
- [ ] Build graph with 20+ relationships
- [ ] Calculate PageRank scores
- [ ] Search for entities by query
- [ ] Generate answer with scores

### Quality Validation
- [ ] Confidence propagates correctly
- [ ] Provenance tracks all operations
- [ ] State checkpoints work
- [ ] Partial results on errors

### Performance Baseline
- [ ] Process 10-page PDF in <30 seconds
- [ ] Sub-second search responses
- [ ] Memory usage <1GB

## Phase 2: Horizontal Expansion

After vertical slice validation:

### Complete Core Services
- [ ] T107: Full identity management
- [ ] T108: Version service
- [ ] T109: Entity normalizer
- [ ] T110: Complete provenance
- [ ] T111: Full quality service
- [ ] T112-T120: Remaining core services

### Expand Ingestion (T02-T12)
- [ ] Word, HTML, Markdown loaders
- [ ] CSV, JSON, Excel loaders
- [ ] API connectors
- [ ] Stream processing

### Expand Processing (T14-T30)
- [ ] Text cleaning and normalization
- [ ] Language detection and translation
- [ ] Advanced tokenization
- [ ] T23b: LLM entity extraction
- [ ] T25: Coreference resolution
- [ ] Entity linking and disambiguation

### Expand Construction (T35-T48)
- [ ] Reference edge builder
- [ ] Graph merger and deduplicator
- [ ] Schema validation
- [ ] Advanced embedders
- [ ] Multiple vector indices

### Complete Retrieval (T50-T67)
- [ ] All 19 GraphRAG operators
- [ ] Community detection
- [ ] Subgraph extraction
- [ ] Advanced ranking

### Add Analysis (T69-T75)
- [ ] Centrality measures
- [ ] Path finding
- [ ] Clustering algorithms
- [ ] Flow analysis

### Complete Interface (T82-T106)
- [ ] Natural language parsing
- [ ] Query planning
- [ ] Multi-query aggregation
- [ ] Export formats
- [ ] Monitoring and alerts

## Phase 3: Advanced Features

### Format Conversion
- [ ] T115: Graph→Table converter
- [ ] T116: Table→Graph builder
- [ ] T117: Format auto-selector

### Temporal and Causal
- [ ] T118: Temporal reasoner
- [ ] T119: Semantic evolution
- [ ] Causal analysis integration

### Statistical Integration
- [ ] PyWhy integration
- [ ] Statistical test runner
- [ ] Uncertainty propagation

## Implementation Principles

### Vertical Slice Principles
1. **Minimal but Complete**: Each tool works end-to-end
2. **Defer Complexity**: Advanced features come later
3. **Contract First**: Define tool contracts before coding
4. **Test the Flow**: Integration over perfection

### Quality Requirements
1. Every operation tracks confidence
2. All data includes provenance
3. Failures produce partial results
4. State can be checkpointed

### Testing Requirements
1. **No mocks or simulations** - Real databases only
2. **Test with real data** - Actual PDFs, real text
3. **Full integration tests** - Complete data flows
4. **Docker test environments** - Isolated but real

### Architecture Rules
1. Tools use contracts for requirements
2. Reference-based data passing
3. Streaming where possible
4. Domain-adaptive behavior

## Success Criteria

### Vertical Slice Success (2 weeks)
- [ ] PDF → Answer workflow runs
- [ ] PageRank scores influence results  
- [ ] Confidence tracked throughout
- [ ] Basic UI shows results
- [ ] Architecture validated

### MVP Success (2 months)
- [ ] 20+ tools implemented
- [ ] Multiple analysis types work
- [ ] Format conversion operational
- [ ] Can run paper examples

### Full Success (4 months)
- [ ] 121 tools implemented
- [ ] All mock workflows run
- [ ] Statistical integration works
- [ ] Ready for thesis defense

## Next Steps

1. **Week 1**: Implement minimal core services
2. **Week 2**: Build vertical slice tools
3. **Week 3**: Integration and testing
4. **Week 4**: Demo and architecture review
5. **Month 2+**: Horizontal expansion based on learnings