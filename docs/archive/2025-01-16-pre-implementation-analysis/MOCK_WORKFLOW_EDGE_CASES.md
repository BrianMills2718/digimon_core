# Edge Case Mock Workflows

## Example 11: Schema Evolution Mid-Workflow

### Analytic Goal
"Analyzing social media posts, but halfway through realize we need to track post language."

### Challenge
Need to add attributes to entities/relationships after processing has started.

### Workflow

```yaml
Initial Schema (Steps 1-5):
Entity: {
  "id": str,
  "name": str,
  "type": str,
  "mentioned_in": List[str]
}

Step 6: Realization
"Wait, we need to track language for multi-lingual analysis!"

Problem: 10,000 entities already processed without language attribute

Solution Pattern:
{
  "schema_version": "v1.0",
  "entity": {
    "required": ["id", "name", "type"],
    "optional": ["mentioned_in"]
  }
}

Updated Schema:
{
  "schema_version": "v1.1", 
  "entity": {
    "required": ["id", "name", "type"],
    "optional": ["mentioned_in", "language", "confidence_score"]
  },
  "migration": {
    "from": "v1.0",
    "defaults": {"language": "unknown", "confidence_score": null}
  }
}

Backward Compatibility:
- Old entities still valid
- New tools check: if not hasattr(entity, 'language'): use default
- Can retroactively update old entities if needed
```

## Example 12: Partial Results and Error Propagation

### Analytic Goal
"Extract all companies mentioned in 1000 documents, even if some documents fail."

### Challenge
Some PDFs are corrupted, some text is unreadable, but we want partial results.

### Workflow

```yaml
Step 1: Batch Ingestion with Error Handling
Tool: T01 (PDF Loader)
Input: 1000 PDFs

Output:
{
  "success": [
    {"doc_id": "doc_001", "content": "..."},
    ... // 950 successful
  ],
  "failures": [
    {
      "doc_id": "doc_451",
      "error": "PDF corrupted",
      "error_type": "corrupt_file",
      "severity": "document_level"
    },
    ... // 50 failed
  ],
  "summary": {
    "total": 1000,
    "successful": 950,
    "failed": 50,
    "partial": 0
  }
}

Step 2: Entity Extraction with Confidence Degradation
Tool: T23
Some documents have OCR errors

Output:
{
  "entities": [
    {
      "id": "ent_microsoft_001",
      "name": "Microsoft",
      "confidence": 0.99,
      "extraction_quality": "high"
    },
    {
      "id": "ent_unknown_001", 
      "name": "Mcrosoft",  # OCR error
      "confidence": 0.60,
      "extraction_quality": "low",
      "possible_correction": "Microsoft"
    }
  ]
}

Step 3: Graph Building with Quality Tiers
Build graph but tag nodes/edges by quality:

Graph:
{
  "nodes": [
    {"id": "ent_microsoft_001", "tier": "high_confidence"},
    {"id": "ent_unknown_001", "tier": "low_confidence"}
  ],
  "edges": [
    {
      "source": "ent_microsoft_001",
      "target": "ent_apple_001",
      "confidence": 0.95,
      "tier": "high_confidence"
    }
  ]
}

Step 4: Analysis with Quality Filtering
User can choose:
- "Show all results" (includes low confidence)
- "Show high confidence only"
- "Show results with warnings"

Final Report:
"Found 487 unique companies (423 high confidence, 64 low confidence).
 50 documents could not be processed.
 Confidence degradation detected in 127 entities - manual review recommended."
```

## Example 13: Resource-Constrained Processing

### Analytic Goal
"Process 10 million tweets but only have 16GB RAM."

### Challenge
Data doesn't fit in memory, need streaming processing.

### Workflow

```yaml
Step 1: Streaming Ingestion
Tool: T12 (Stream Processor)
Input: tweets.jsonl (200GB file)

Streaming Pattern:
def process_tweets_stream():
    with open('tweets.jsonl') as f:
        batch = []
        for line in f:
            batch.append(json.loads(line))
            if len(batch) >= 1000:
                yield batch
                batch = []

Step 2: Incremental Entity Extraction
Tool: T23 (modified for streaming)

Entity Deduplication Challenge:
- "Apple" mentioned in batch 1 and batch 1000
- Need consistent entity ID without holding all in memory

Solution: Bloom Filter + Database
{
  "bloom_filter": "probable_entities.bloom",  # Fast membership test
  "entity_cache": "LRU:10000",  # Recent entities in memory
  "entity_store": "sqlite://entities.db"  # Full persistence
}

Step 3: Incremental Graph Building
Tool: T31 (modified for incremental)

Instead of:
graph = build_graph(all_entities)  # Memory error!

Do:
for entity_batch in entity_stream:
    neo4j.merge_nodes(entity_batch)  # Incremental updates
    
Step 4: Streaming Analytics
Tool: T68 (PageRank - modified)

Problem: PageRank needs full graph in memory
Solution: Approximate algorithms
- Sample-based PageRank
- Streaming PageRank approximation
- Or: Run on Neo4j server-side

Result Quality Note:
{
  "algorithm": "approximate_pagerank",
  "sample_size": 100000,
  "confidence_interval": [0.081, 0.084],
  "note": "Approximate result due to memory constraints"
}
```

## Example 14: Provenance Under Data Updates

### Analytic Goal
"Track how conclusions change when source data is corrected/updated."

### Challenge
Original analysis was wrong due to bad data, need to trace impact.

### Workflow

```yaml
Version 1: Original Analysis (January 1)
Source: earnings_report_v1.pdf
Extract: "Revenue: $100M"  # Actually a typo
Build graph, run analysis
Conclusion: "Company underperforming"

Version 2: Corrected Data (January 15)
Source: earnings_report_v2.pdf  
Extract: "Revenue: $1000M"  # Corrected

Provenance Challenge: What was affected?

Dependency Graph:
earnings_report_v1.pdf
  → chunk_001 
    → entity_revenue_001 (value: $100M)
      → relationship_underperforms_market
        → analysis_result_001: "Sell recommendation"
          → report_001.pdf (sent to clients!)

Update Cascade:
{
  "update_source": "earnings_report_v2.pdf",
  "replaces": "earnings_report_v1.pdf",
  "affected_entities": ["entity_revenue_001"],
  "affected_relationships": ["relationship_underperforms_market"],
  "affected_analyses": ["analysis_result_001"],
  "affected_outputs": ["report_001.pdf"],
  "impact_severity": "CRITICAL",
  "notification_required": true
}

Versioned Results:
{
  "analysis_id": "revenue_analysis",
  "versions": [
    {
      "version": "v1",
      "date": "2024-01-01",
      "conclusion": "Sell",
      "confidence": 0.90,
      "based_on": "earnings_report_v1.pdf",
      "status": "SUPERSEDED"
    },
    {
      "version": "v2", 
      "date": "2024-01-15",
      "conclusion": "Buy",
      "confidence": 0.95,
      "based_on": "earnings_report_v2.pdf",
      "status": "CURRENT"
    }
  ]
}
```

## Example 15: Multi-Stage Disambiguation

### Analytic Goal
"Identify all mentions of 'Cambridge' and classify by type (university, city, company)."

### Challenge
Multiple valid entities with same name, context determines which.

### Workflow

```yaml
Step 1: Initial Entity Detection
Text: "Cambridge announced new AI research"
Problem: Which Cambridge?

Candidates:
[
  {"id": "ent_cambridge_uni_uk", "type": "University", "location": "UK"},
  {"id": "ent_cambridge_uni_us", "type": "University", "location": "US"},  
  {"id": "ent_cambridge_city_uk", "type": "City", "location": "UK"},
  {"id": "ent_cambridge_city_us", "type": "City", "location": "US"},
  {"id": "ent_cambridge_analytics", "type": "Company", "sector": "Tech"}
]

Step 2: Context Collection
Look at surrounding context:
- "AI research" → likely university or company
- Check document metadata: source = "academic_journal" → likely university
- Other entities nearby: "MIT" → likely Cambridge, MA (US)

Step 3: Disambiguation Scoring
{
  "text": "Cambridge announced new AI research",
  "candidates": [
    {
      "entity_id": "ent_cambridge_uni_us",
      "score": 0.75,
      "evidence": ["AI research", "near MIT", "academic source"]
    },
    {
      "entity_id": "ent_cambridge_uni_uk",
      "score": 0.60,
      "evidence": ["AI research", "academic source"]
    },
    {
      "entity_id": "ent_cambridge_analytics",
      "score": 0.40,
      "evidence": ["AI research"]
    }
  ],
  "selected": "ent_cambridge_uni_us",
  "confidence": 0.75,
  "ambiguity_preserved": true  # Keep alternatives
}

Step 4: Graph Building with Ambiguity
Store primary choice + alternatives:
{
  "mention_id": "mention_001",
  "surface_text": "Cambridge",
  "primary_entity": "ent_cambridge_uni_us",
  "alternatives": [
    {"entity": "ent_cambridge_uni_uk", "score": 0.60},
    {"entity": "ent_cambridge_analytics", "score": 0.40}
  ]
}

Step 5: Analysis with Ambiguity Awareness
When computing metrics, can:
- Use only primary entities (fast, deterministic)
- Weight by confidence scores
- Run sensitivity analysis on different disambiguations
```

## Critical Design Patterns Emerging

### 1. **Three-Level Identity System**
```
Surface Form: "Apple", "Cambridge"
     ↓
Mention ID: "mention_001" (specific occurrence)
     ↓  
Entity ID: "ent_apple_inc_001" (canonical entity)
```

### 2. **Quality/Confidence Tiers Throughout**
- Document level: successful/partial/failed
- Entity level: confidence scores
- Relationship level: evidence strength  
- Analysis level: exact vs approximate

### 3. **Versioning at Every Level**
- Schema versions (with migrations)
- Entity versions (with history)
- Graph versions (with lineage)
- Analysis versions (with provenance)

### 4. **Streaming-First Design**
- Batch processing with yields
- Incremental updates
- Bounded memory usage
- Approximate algorithms when needed

### 5. **Graceful Degradation**
- Partial results better than no results
- Confidence scores on everything
- Clear communication of limitations
- Preservation of alternatives

## Implementation Requirements

### 1. **Memory-Aware Processing**
```python
class MemoryAwareProcessor:
    def process(self, data_stream, memory_limit):
        if estimated_size(data_stream) < memory_limit:
            return exact_processing(data_stream)
        else:
            return approximate_processing(data_stream)
```

### 2. **Update Cascade Tracking**
```python
class ProvenanceTracker:
    def record_lineage(self, input_id, output_id, tool_id)
    def find_affected(self, changed_input_id) -> List[affected_items]
    def invalidate_cascade(self, changed_input_id)
```

### 3. **Ambiguity Preservation**
```python
class AmbiguityManager:
    def store_alternatives(self, mention, candidates_with_scores)
    def get_primary(self, mention_id) -> entity_id
    def get_alternatives(self, mention_id) -> List[(entity_id, score)]
    def run_sensitivity_analysis(self, analysis, disambiguation_strategy)
```