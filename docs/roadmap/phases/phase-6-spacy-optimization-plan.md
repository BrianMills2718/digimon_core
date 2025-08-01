# Phase 6: spaCy Processing Optimization - Implementation Plan

**Status:** 🟡 PLANNED  
**Timeline:** 4-6 weeks  
**Priority:** P0 - System Scale-Up  
**ADR Reference:** [ADR-016: System Optimization Strategy](../../architecture/adrs/ADR-016-System-Optimization-Strategy.md)

## Objective

Scale the KGAS system to handle **10MB+ documents** (currently limited to 100KB-1MB) by optimizing spaCy text processing through intelligent chunking and component optimization.

## Current Breaking Points Identified

From stress testing results:
- **Text Size Limit**: Performance degrades beyond 100KB-1MB documents
- **Memory Usage**: Peak usage can exceed 2GB for large documents  
- **Processing Time**: Exponential slowdown due to spaCy's O(n²) dependency parsing
- **Tokenization Overhead**: Every word analyzed even for simple entity extraction

## Success Metrics

| **Metric** | **Current** | **Target** | **Measurement** |
|------------|-------------|------------|-----------------|
| Max Document Size | 100KB-1MB | 10MB+ | Stress test validation |
| Processing Speed | 1x baseline | 5-10x faster | Large document benchmarks |
| Memory Usage | 2GB+ peak | <1GB sustained | Memory profiling |
| Entity Accuracy | >95% current | Maintain >95% | Accuracy regression testing |

## Implementation Tasks

### Week 1-2: Chunked Processing Pipeline

#### Task 6.1: Intelligent Text Chunking
- **Deliverable**: `OptimizedSpacyProcessor` class with chunked processing
- **Features**:
  - Configurable chunk size (default 10,000 chars) with overlap (default 500 chars)
  - Sentence boundary awareness to avoid splitting mid-sentence
  - Metadata tracking for chunk provenance and reconstruction
- **Files to Create/Modify**:
  - `src/tools/optimization/chunked_spacy_processor.py`
  - `src/tools/phase1/t23a_spacy_ner_unified.py` (integration)
- **Testing**: Verify chunking doesn't split entities incorrectly

#### Task 6.2: Component Optimization  
- **Deliverable**: Optimized spaCy model loading with disabled unnecessary components
- **Features**:
  - Disable parser and lemmatizer for entity extraction (2-3x speedup)
  - Keep only: tokenizer, tagger, NER components
  - Configurable component selection based on tool requirements
- **Expected Gain**: 2-3x faster processing for entity extraction tasks
- **Testing**: Benchmark processing speed before/after optimization

### Week 3-4: Boundary Entity Merging

#### Task 6.3: Overlapping Entity Detection
- **Deliverable**: Algorithm to detect entities that span chunk boundaries
- **Features**:
  - Entity position tracking across chunks
  - Confidence score preservation during merging
  - Duplicate entity elimination with highest confidence wins
- **Challenge**: Handle cases where entity mentions are split across chunks
- **Testing**: Test with entities that naturally occur at chunk boundaries

#### Task 6.4: Entity Reconstruction
- **Deliverable**: Merge overlapping entities from multiple chunks
- **Features**:
  - Reconstruct complete entities from partial matches
  - Maintain entity relationships across chunk boundaries
  - Preserve provenance information for merged entities
- **Algorithm**: Use character position overlap + similarity scoring
- **Testing**: Verify no entities lost or duplicated in merge process

### Week 5-6: Performance Optimization & Validation

#### Task 6.5: Memory Optimization
- **Deliverable**: Constant memory usage regardless of document size
- **Features**:
  - Streaming processing with chunk disposal after processing
  - Memory pool management for spaCy document objects
  - Garbage collection optimization between chunks
- **Target**: <1GB memory usage even for 10MB+ documents
- **Testing**: Memory profiling with documents of increasing size

#### Task 6.6: Performance Benchmarking
- **Deliverable**: Comprehensive performance validation suite
- **Features**:
  - Benchmark suite for documents 1KB → 10MB+
  - Processing time measurements and trend analysis
  - Memory usage profiling and leak detection
  - Entity accuracy regression testing
- **Validation**: Confirm 5-10x performance improvement achieved
- **Testing**: Automated performance regression prevention

## Integration Points

### T23A Integration
```python
# Enhanced T23A with chunked processing
class T23ASpacyNERUnified(BaseTool):
    def __init__(self, service_manager, chunk_size=10000):
        super().__init__(service_manager)
        self.chunked_processor = OptimizedSpacyProcessor(chunk_size=chunk_size)
    
    def execute(self, request: ToolRequest) -> ToolResult:
        text = request.input_data.get("text", "")
        
        if len(text) > self.chunk_size:
            # Use chunked processing for large documents
            entities = self.chunked_processor.process_large_document(text)
        else:
            # Use original processing for small documents
            entities = self._process_single_chunk(text)
        
        return self._create_success_result(entities)
```

### T27 Integration
- Relationship extraction will benefit from consistent entity positions
- Boundary merging ensures relationships aren't lost across chunks
- Maintains existing relationship pattern matching logic

### Service Integration
- Identity Service: Enhanced entity deduplication with position tracking
- Provenance Service: Track chunk-level processing provenance
- Quality Service: Maintain confidence scores through merging process

## Risk Mitigation

### Technical Risks
1. **Entity Boundary Splits**: Entity mentions split across chunks
   - **Mitigation**: Sentence boundary awareness, overlap buffer zones
   
2. **Accuracy Degradation**: Chunking may reduce entity detection accuracy
   - **Mitigation**: Comprehensive accuracy regression testing, tunable overlap
   
3. **Relationship Loss**: Important relationships spanning chunks lost
   - **Mitigation**: Larger overlap zones, relationship reconstruction logic

### Performance Risks
1. **Overhead from Chunking**: Processing overhead may negate benefits
   - **Mitigation**: Benchmark chunk size optimization, bypass for small docs
   
2. **Memory Usage from Overlap**: Overlapping chunks increase memory usage
   - **Mitigation**: Configurable overlap size, streaming chunk disposal

## Testing Strategy

### Unit Tests
- Chunk boundary detection and sentence preservation
- Entity merging algorithm correctness
- Memory cleanup and garbage collection
- Component disable/enable functionality

### Integration Tests  
- End-to-end pipeline with large documents (1MB, 5MB, 10MB)
- Entity accuracy comparison: chunked vs non-chunked
- Memory usage profiling under various document sizes
- Processing time benchmarks with statistical significance

### Stress Tests
- Maximum document size boundaries (find new breaking point)
- Concurrent processing of multiple large documents
- Memory leak detection over extended processing sessions
- Entity accuracy at extreme overlap configurations

## Rollout Plan

### Phase 1: Development (Weeks 1-4)
- Implement chunked processing and boundary merging
- Unit testing and basic integration validation
- Internal benchmarking and optimization

### Phase 2: Integration (Weeks 5-6)
- Full T23A integration with backward compatibility
- Comprehensive testing suite execution
- Performance validation against success metrics

### Phase 3: Deployment (Week 6+)
- Feature flag rollout for chunked processing
- Production monitoring and performance tracking
- Documentation updates and user guidance

## Dependencies

### Internal
- Existing T23A implementation and test suite
- spaCy model management in ResourceManager
- Service integration points (Identity, Provenance, Quality)

### External
- spaCy library version compatibility
- Sufficient system memory for development/testing
- Performance testing infrastructure

## Success Criteria

Phase 6 is considered successful when:

1. ✅ **10MB+ Document Processing**: System can process documents >10MB without failure
2. ✅ **5-10x Performance Gain**: Measurable speedup on large documents
3. ✅ **<1GB Memory Usage**: Sustained memory usage under 1GB regardless of document size
4. ✅ **>95% Entity Accuracy**: No significant accuracy regression from chunking
5. ✅ **Backward Compatibility**: Existing functionality unchanged for small documents
6. ✅ **Comprehensive Testing**: Full test suite passes with performance validation

## References

- [ADR-016: System Optimization Strategy](../../architecture/adrs/ADR-016-System-Optimization-Strategy.md)
- [System Stress Test Results](../../analysis/system-boundary-analysis.md)
- [spaCy Performance Documentation](https://spacy.io/usage/processing-pipelines#efficiency)
- [Current T23A Implementation](../../../src/tools/phase1/t23a_spacy_ner_unified.py)