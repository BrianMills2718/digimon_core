# Tool Chain Examples and Compatibility

This document provides concrete examples of tool chains based on common analytical workflows.

## Visual Tool Compatibility Map

```
┌─────────────────────┐
│   INGESTION LAYER   │
├─────────────────────┤
│ T01: PDF            │──┐
│ T02: Word           │──┤
│ T03: Text           │──┤
│ T04: HTML           │──┼──→ Creates: Document
│ T05: CSV            │──┤
│ T06: JSON           │──┤
│ T07: Excel          │──┘
└─────────────────────┘
           ↓
┌─────────────────────┐
│  PROCESSING LAYER   │
├─────────────────────┤
│ T15: Chunker        │──→ Creates: Chunks (with doc_ref)
│ T16: Semantic Chunk │
└─────────────────────┘
           ↓
┌─────────────────────┐
│  EXTRACTION LAYER   │
├─────────────────────┤
│ T23: Entity NER     │──→ Creates: Mentions (with chunk_ref)
│ T24: Custom NER     │
│ T27: Relation Ext   │──→ Creates: Relationship Mentions
└─────────────────────┘
           ↓
┌─────────────────────┐
│ RESOLUTION LAYER    │
├─────────────────────┤
│ T25: Coreference    │──→ Links: Mentions → Chains
│ T26: Entity Linker  │──→ Links: Mentions → KB
│ T29: Disambiguator  │──→ Resolves: Entity conflicts
└─────────────────────┘
           ↓
┌─────────────────────┐
│ CONSTRUCTION LAYER  │
├─────────────────────┤
│ T31: Entity Builder │──→ Creates: Entities (from mentions)
│ T34: Relation Build │──→ Creates: Relationships
│ T37: Deduplicator   │──→ Merges: Duplicate entities
└─────────────────────┘
           ↓
┌─────────────────────┐
│   STORAGE LAYER     │
├─────────────────────┤
│ T76: Neo4j Store    │──→ Stores: Graphs
│ T77: SQLite Store   │──→ Stores: Metadata
│ T78: FAISS Store    │──→ Stores: Vectors
└─────────────────────┘
```

## Detailed Tool Chain Examples

### Example 1: Financial Report Analysis

**Goal**: Extract company relationships from 10-K filings

```yaml
workflow: financial_analysis
steps:
  - tool: T01_PDF_Loader
    input: 
      file_path: "apple_10k_2023.pdf"
    output:
      document_ref: "doc_001"
      confidence: 0.95
      
  - tool: T15_Chunker
    input:
      document_ref: "doc_001"
      chunk_size: 1000
      chunk_overlap: 200
    output:
      chunk_refs: ["chunk_001", ..., "chunk_245"]
      
  - tool: T23_Entity_Recognizer
    input:
      chunk_refs: ["chunk_001", ..., "chunk_245"]
      entity_types: ["ORG", "PERSON", "MONEY", "PERCENT"]
      create_mentions: true
    output:
      mention_refs: ["mention_001", ..., "mention_1834"]
      
  - tool: T25_Coreference_Resolver
    input:
      mention_refs: ["mention_001", ..., "mention_1834"]
    output:
      coreference_chains: [
        {
          chain_id: "coref_001",
          mention_refs: ["mention_001", "mention_234", "mention_567"],
          canonical_text: "Apple Inc."
        }
      ]
      
  - tool: T31_Entity_Builder
    input:
      coreference_chains: [...]
      merge_strategy: "conservative"
    output:
      entity_refs: ["ent_001", ..., "ent_156"]
      
  - tool: T34_Relationship_Builder
    input:
      entity_refs: ["ent_001", ..., "ent_156"]
      chunk_refs: ["chunk_001", ..., "chunk_245"]
      relationship_types: ["subsidiary_of", "competes_with", "supplies_to"]
    output:
      relationship_refs: ["rel_001", ..., "rel_423"]
```

### Example 2: Multi-Format Analysis (CSV + Text)

**Goal**: Combine structured data with unstructured text

```yaml
workflow: multi_format_merge
parallel_streams:
  stream_1:
    - tool: T05_CSV_Loader
      input: 
        file_path: "company_data.csv"
      output:
        table_ref: "table_001"
        
    - tool: T116_Table_to_Graph
      input:
        table_ref: "table_001"
        source_column: "company_name"
        target_column: "parent_company"
        relationship_type: "subsidiary_of"
      output:
        entity_refs: ["ent_csv_001", ..., "ent_csv_089"]
        
  stream_2:
    - tool: T03_Text_Loader
      input:
        file_path: "news_articles.txt"
      output:
        document_ref: "doc_002"
        
    - tool: T15_Chunker → T23_NER → T31_Entity_Builder
      output:
        entity_refs: ["ent_txt_001", ..., "ent_txt_234"]
        
  merge:
    - tool: T29_Disambiguator
      input:
        entity_sets: [
          ["ent_csv_001", ..., "ent_csv_089"],
          ["ent_txt_001", ..., "ent_txt_234"]
        ]
      output:
        merged_entities: ["ent_merged_001", ..., "ent_merged_278"]
        merge_map: {
          "ent_csv_001": "ent_merged_001",
          "ent_txt_045": "ent_merged_001"
        }
```

### Example 3: Quality-Degraded Pipeline

**Goal**: Handle poor quality scanned documents

```yaml
workflow: low_quality_processing
steps:
  - tool: T01_PDF_Loader
    input:
      file_path: "old_scan.pdf"
      ocr_enabled: true
    output:
      document_ref: "doc_003"
      confidence: 0.67  # Low OCR confidence
      warnings: ["Poor scan quality", "Handwritten sections"]
      
  - tool: T15_Chunker
    input:
      document_ref: "doc_003"
    output:
      chunk_refs: ["chunk_001", ..., "chunk_089"]
      confidence: 0.67  # Propagated
      
  - tool: T23_Entity_Recognizer
    input:
      chunk_refs: ["chunk_001", ..., "chunk_089"]
      confidence_threshold: 0.5  # Lowered due to OCR quality
    output:
      mention_refs: ["mention_001", ..., "mention_234"]
      confidence: 0.58  # Further degraded
      quality_tier: "low"
      
  # Quality-aware processing
  - tool: T31_Entity_Builder
    input:
      mention_refs: ["mention_001", ..., "mention_234"]
      min_confidence: 0.5
      create_all_candidates: true  # Keep alternatives
    output:
      entity_refs: ["ent_001", ..., "ent_045"]
      alternative_entities: [
        {
          surface: "App1e",  # OCR error
          candidates: [
            {"entity": "Apple", "confidence": 0.72},
            {"entity": "App1e", "confidence": 0.28}
          ]
        }
      ]
```

### Example 4: Streaming Large Dataset

**Goal**: Process 10 million tweets without memory overflow

```yaml
workflow: streaming_twitter_analysis
steps:
  - tool: T06_JSON_Loader
    mode: streaming
    input:
      file_path: "tweets_10m.jsonl"
      batch_size: 10000
    yields:  # Streaming output
      document_batches: Iterator[List[DocumentRef]]
      
  - tool: T15_Chunker
    mode: streaming
    input:
      document_iterator: Iterator[List[DocumentRef]]
      chunks_per_doc: 1  # Tweets are small
    yields:
      chunk_batches: Iterator[List[ChunkRef]]
      
  - tool: T23_Entity_Recognizer
    mode: streaming
    input:
      chunk_iterator: Iterator[List[ChunkRef]]
      batch_size: 5000
    yields:
      mention_batches: Iterator[List[MentionRef]]
      
  - tool: T31_Entity_Builder
    mode: streaming_aggregation
    input:
      mention_iterator: Iterator[List[MentionRef]]
      dedup_strategy: "incremental"  # Dedup within batches
    output:
      entity_refs: ["ent_001", ..., "ent_534289"]
      processing_stats: {
        "batches_processed": 2000,
        "entities_merged": 156234,
        "peak_memory_mb": 1200
      }
```

### Example 5: Cross-Format Analysis with Confidence

**Goal**: Combine high-confidence structured data with low-confidence extracted data

```yaml
workflow: confidence_aware_merge
steps:
  # High confidence path
  - path: structured_data
    - tool: T07_Excel_Loader
      output:
        table_ref: "table_001"
        confidence: 1.0  # Structured data
        
  # Low confidence path  
  - path: unstructured_data
    - tool: T01_PDF_Loader
      output:
        confidence: 0.72  # Poor scan
        
  # Merge with confidence weighting
  - tool: T29_Disambiguator
    input:
      entity_sets: [structured_entities, extracted_entities]
      resolution_strategy: "confidence_weighted"
    output:
      merged_entities: [...],
      resolution_log: [
        {
          entities: ["ent_excel_001", "ent_pdf_045"],
          decision: "kept ent_excel_001",
          reason: "Higher confidence (1.0 vs 0.65)"
        }
      ]
```

## Tool Compatibility Rules

### 1. Data Type Compatibility

| Output Type | Compatible Input Tools |
|------------|----------------------|
| Document | All chunkers (T15-T16) |
| Chunk | All NER tools (T23-T24), Embedders (T41-T44) |
| Mention | Coreference (T25), Linkers (T26), Disambiguator (T29) |
| Entity | Relationship builders (T34), Analysis tools (T68-T75) |
| Table | Table→Graph (T116), Statistical tools |
| Graph | All graph algorithms (T68-T75), Converters (T115) |

### 2. Confidence Propagation Patterns

```
High Confidence (>0.8):
- Use standard thresholds
- Trust automated decisions
- Minimal human review

Medium Confidence (0.6-0.8):
- Lower thresholds
- Keep alternatives
- Flag for review

Low Confidence (<0.6):
- Keep all candidates
- Require human validation
- Use ensemble methods
```

### 3. Streaming Compatibility

**Full Streaming Support:**
- T01-T07 (Loaders with file streaming)
- T15-T16 (Chunkers)
- T23-T24 (NER with batching)
- T41-T44 (Embedders with batching)

**Aggregation Required:**
- T25 (Coreference - needs document context)
- T31 (Entity Builder - needs deduplication)
- T68-T75 (Graph algorithms - need full graph)

**Hybrid (Stream + Checkpoint):**
- T34 (Relationship Builder - can stream with periodic dedup)
- T37 (Deduplicator - can work incrementally)

## Error Handling Patterns

### Pattern 1: Cascading Confidence
```python
if upstream_confidence < 0.5:
    # Switch to more conservative algorithm
    use_algorithm = "rule_based"
    increase_human_review = True
```

### Pattern 2: Partial Result Aggregation
```python
results = {
    "successful": processed_successfully,
    "failed": processing_failed,
    "partial": partially_processed,
    "stats": {
        "success_rate": len(successful) / total,
        "avg_confidence": mean(confidences)
    }
}
```

### Pattern 3: Alternative Path Selection
```python
if primary_tool_fails:
    if has_structured_data:
        use_tool_chain = ["T05", "T116", "T68"]  # CSV path
    else:
        use_tool_chain = ["T03", "T15", "T23"]  # Text path
```

## Validation Checklist

Before implementing a tool chain, verify:

- [ ] All tools in chain have compatible input/output types
- [ ] Confidence thresholds are appropriate for data quality
- [ ] Memory requirements fit within constraints
- [ ] Streaming is used for large datasets
- [ ] Error handling covers partial failures
- [ ] Identity preservation is maintained
- [ ] Quality tracking is continuous
- [ ] References are used (not full objects)

This ensures robust, scalable tool chains that maintain data quality throughout the analysis pipeline.