# Mock Workflow Examples for Super-Digimon

These examples demonstrate complete workflows from data ingestion to analysis results, showing data flow, transformations, and system interactions.

## Example 1: Company Relationship Analysis from 10-K Filings

### Analytic Goal
"Identify the competitive landscape and partnership network for tech companies from their SEC filings, then analyze which companies have the strongest strategic positions."

### Input Corpus
- 50 PDF files: 10-K annual reports from 10 tech companies over 5 years
- Size: ~500 pages per document

### Complete Workflow

```yaml
Step 1: Document Ingestion
Tool: T01 (PDF Loader)
Input: 
  - file_paths: ["reports/AAPL_2023_10K.pdf", ...]
  - extract_tables: true
Output:
  documents: [
    {
      "id": "doc_001",
      "source_path": "reports/AAPL_2023_10K.pdf",
      "content": "Full text content...",
      "metadata": {
        "company": "Apple Inc",
        "year": 2023,
        "doc_type": "10-K"
      },
      "tables": [...]
    }
  ]
Storage: SQLite (metadata + doc references)
MCP Log: {"tool": "T01", "timestamp": "2024-01-15T10:00:00", "input_files": 50, "output_docs": 50}

Step 2: Semantic Chunking
Tool: T15 (Semantic Chunker)
Input:
  - documents: [doc_001, doc_002, ...]
  - chunk_size: 512
  - overlap: 50
Output:
  chunks: [
    {
      "id": "chunk_001_001",
      "doc_id": "doc_001",
      "content": "Apple competes primarily with Samsung...",
      "position": 0,
      "metadata": {"section": "Competition"}
    }
  ]
Storage: SQLite (chunk metadata)
MCP Log: {"tool": "T15", "chunks_created": 25000}

Step 3: Entity Recognition
Tool: T23 (SpaCy Entity Recognizer)
Input:
  - chunks: [chunk_001_001, ...]
  - model: "en_core_web_lg"
Output:
  entities: [
    {
      "id": "ent_apple",
      "name": "Apple Inc",
      "type": "ORG",
      "mentions": [
        {"chunk_id": "chunk_001_001", "position": 0},
        {"chunk_id": "chunk_001_047", "position": 156}
      ]
    },
    {
      "id": "ent_samsung",
      "name": "Samsung",
      "type": "ORG",
      "mentions": [...]
    }
  ]
Storage: Neo4j (as nodes)
MCP Log: {"tool": "T23", "entities_found": 847, "unique_entities": 234}

Step 4: Coreference Resolution
Tool: T25 (Coreference Resolver)
Input:
  - chunks: [chunk_001_001, ...]
  - entities: [ent_apple, ent_samsung, ...]
Output:
  resolved_entities: [
    {
      "id": "ent_apple",
      "name": "Apple Inc",
      "type": "ORG",
      "aliases": ["Apple", "the Company", "AAPL"],
      "mentions": [...] // expanded list
    }
  ]
Storage: Neo4j (update nodes)
MCP Log: {"tool": "T25", "coreferences_resolved": 1243}

Step 5: Relationship Extraction
Tool: T28 (ML Relationship Extractor)
Input:
  - chunks: [chunk_001_001, ...]
  - entities: [resolved entities]
Output:
  relationships: [
    {
      "id": "rel_001",
      "source_id": "ent_apple",
      "target_id": "ent_samsung",
      "type": "competes_with",
      "confidence": 0.92,
      "evidence": ["chunk_001_001", "chunk_003_044"],
      "attributes": {
        "domains": ["smartphones", "tablets"],
        "extracted_from": "Competition section"
      }
    },
    {
      "id": "rel_002",
      "source_id": "ent_apple",
      "target_id": "ent_nvidia",
      "type": "partners_with",
      "confidence": 0.87,
      "evidence": ["chunk_001_234"]
    }
  ]
Storage: Neo4j (as edges)
MCP Log: {"tool": "T28", "relationships_found": 523}

Step 6: Generate Embeddings
Tool: T41 (Sentence Embedder)
Input:
  - texts: [entity names and descriptions]
  - model: "all-MiniLM-L6-v2"
Output:
  embeddings: [
    {
      "id": "ent_apple",
      "embedding": [0.123, -0.456, ...] // 384 dimensions
    }
  ]
Storage: FAISS index
MCP Log: {"tool": "T41", "embeddings_created": 234}

Step 7: Build FAISS Index
Tool: T45 (FAISS Indexer)
Input:
  - embeddings: [array of vectors]
  - index_type: "IVF"
Output:
  index_id: "idx_companies_2024"
Storage: FAISS (serialized index)
MCP Log: {"tool": "T45", "index_built": true, "vectors": 234}

Step 8: Community Detection
Tool: T73 (Community Detection)
Input:
  - graph: Neo4j graph reference
  - algorithm: "louvain"
Output:
  communities: [
    {
      "id": "comm_001",
      "entity_ids": ["ent_apple", "ent_google", "ent_microsoft"],
      "label": "Big Tech Ecosystem",
      "modularity": 0.76
    },
    {
      "id": "comm_002", 
      "entity_ids": ["ent_nvidia", "ent_amd", "ent_intel"],
      "label": "Chip Manufacturers"
    }
  ]
Storage: Neo4j (as meta-nodes)
MCP Log: {"tool": "T73", "communities_found": 12}

Step 9: PageRank Analysis
Tool: T68 (PageRank)
Input:
  - graph: Neo4j graph
  - damping: 0.85
Output:
  pagerank_scores: [
    {"entity_id": "ent_apple", "score": 0.0823},
    {"entity_id": "ent_microsoft", "score": 0.0756},
    {"entity_id": "ent_nvidia", "score": 0.0689}
  ]
Storage: SQLite (as analysis results)
MCP Log: {"tool": "T68", "iterations": 47, "converged": true}

Step 10: Convert to Table for Statistical Analysis
Tool: T115 (Graph to Table Converter)
Input:
  - graph_metrics: [pagerank_scores, community_assignments]
  - entity_attributes: [type, sector, market_cap]
Output:
  dataframe: 
    | entity_id | name      | pagerank | community | type | partnerships | competitions |
    |-----------|-----------|----------|-----------|------|--------------|--------------|
    | ent_apple | Apple Inc | 0.0823   | comm_001  | ORG  | 15          | 8            |
Storage: In-memory pandas DataFrame
MCP Log: {"tool": "T115", "rows": 234, "columns": 7}

Step 11: Statistical Analysis
Tool: T117 (Statistical Test Runner)
Input:
  - dataframe: company_metrics
  - tests: ["correlation", "anova", "regression"]
Output:
  results: {
    "correlation": {
      "pagerank_partnerships": 0.72,
      "p_value": 0.0001
    },
    "anova": {
      "f_statistic": 14.3,
      "p_value": 0.0023,
      "interpretation": "Significant difference in PageRank between communities"
    },
    "regression": {
      "model": "pagerank ~ partnerships + competitions + sector",
      "r_squared": 0.64,
      "coefficients": {...}
    }
  }
Storage: SQLite (analysis results)
MCP Log: {"tool": "T117", "tests_run": 3}

Step 12: Generate Answer
Tool: T57 (Answer Generation)
Input:
  - question: "Which companies have the strongest strategic positions?"
  - context: [top PageRank entities, community analysis, statistical results]
Output:
  answer: "Based on the network analysis of 10-K filings, Apple Inc, Microsoft, 
           and Google demonstrate the strongest strategic positions with PageRank 
           scores of 0.082, 0.076, and 0.071 respectively. Statistical analysis 
           shows a significant correlation (r=0.72, p<0.001) between partnership 
           count and network centrality..."
Storage: SQLite (query results)
MCP Log: {"tool": "T57", "answer_generated": true}
```

### Data Traceability Chain
```
PDF Files → Documents (SQLite) → Chunks (SQLite) → 
Entities (Neo4j) → Relationships (Neo4j) → 
Embeddings (FAISS) → Communities (Neo4j) → 
Metrics (SQLite) → Statistical Results (SQLite) → 
Natural Language Answer

Full Provenance Preserved:
- Answer cites specific PageRank scores
- Scores trace to graph structure  
- Graph traces to extracted relationships
- Relationships trace to specific chunks
- Chunks trace to original PDF pages
```

---

## Example 2: Medical Research Literature Analysis

### Analytic Goal
"Find emerging treatment patterns for diabetes by analyzing recent research papers, identifying which drug combinations are being studied together and their reported efficacy."

### Input Corpus
- 200 JSON files from PubMed API
- Each containing paper metadata + abstracts

### Workflow Summary (Abbreviated)

```yaml
Step 1: JSON Ingestion (T06)
- Load papers with metadata
- Store in SQLite

Step 2: Entity Recognition (T24 - Custom Medical)
- Extract: drugs, diseases, outcomes
- Use medical ontology

Step 3: Relationship Extraction (T27 - Rule Based)
- Pattern: "Drug X improved Outcome Y"
- Pattern: "Drug A combined with Drug B"

Step 4: Build Knowledge Graph
- Nodes: Drugs, Diseases, Outcomes
- Edges: treats, combines_with, improves

Step 5: Path Finding (T54)
- Find: Drug → treats → Diabetes → measured_by → Outcome
- Identify multi-hop treatment pathways

Step 6: Temporal Analysis
- Group by publication year
- Track emerging combinations

Step 7: Convert to Table
- Drug combinations × Outcomes × Time

Step 8: Statistical Trend Analysis
- Time series of drug combination mentions
- Efficacy score aggregation

Result: Identification of emerging combination therapies with statistical significance
```

---

## Example 3: Simple Customer Feedback Analysis

### Analytic Goal
"Categorize customer feedback by topic and sentiment, identify main pain points."

### Input Corpus
- 1 CSV file with 10,000 customer reviews

### Workflow (Showing Flexibility)

```yaml
Step 1: CSV Ingestion (T05)
Output: Table with columns [id, date, review_text, rating]

Step 2: Sentiment Analysis (T85)
Output: Table with added column [sentiment_score]

Step 3: Topic Modeling (T74 - Clustering)
Output: Table with added column [topic_cluster]

Step 4: Aggregate Statistics
- Group by topic
- Calculate average sentiment per topic
- Count reviews per topic

Step 5: Generate Summary
Output: "Main pain points: Shipping delays (2,341 mentions, -0.72 sentiment), 
         Product quality (1,823 mentions, -0.65 sentiment)..."

Note: This workflow stays in table format throughout - no graph needed!
```

---

## Key Observations from Mock Workflows

### 1. **Data Format Transitions**
- Documents → Chunks → Entities/Relations → Graph
- Graph → Table (for statistics)
- Any format → Embeddings → Vector index
- **Critical**: Need clear schemas for each transition

### 2. **Storage Patterns**
- **SQLite**: Metadata, chunks, analysis results, provenance
- **Neo4j**: Entities, relationships, communities (graph structure)
- **FAISS**: Vector embeddings only
- **In-memory**: Intermediate DataFrames for analysis

### 3. **Traceability Requirements**
Each step must preserve:
- Source references (which doc/chunk/entity)
- Confidence scores
- Evidence links
- Timestamp and tool used
- Parameters applied

### 4. **MCP Interaction Pattern**
```python
# Every tool call:
mcp_server.execute_tool(
    tool_id="T23",
    params={...},
    context={
        "workflow_id": "wf_001",
        "step": 3,
        "previous_output": "chunk_refs"
    }
) → {
    "result": {...},
    "metadata": {
        "execution_time": 1.23,
        "records_processed": 25000,
        "storage_refs": ["neo4j://nodes/ent_*"]
    }
}
```

### 5. **Critical Design Decisions Validated**
- ✅ Three-database architecture makes sense
- ✅ Attribute-based flexibility is essential
- ✅ Tool chaining requires careful compatibility
- ✅ Some workflows never need graphs (Example 3)
- ✅ Statistical analysis requires graph→table conversion

### 6. **Potential Issues Discovered**
1. **Large intermediate results**: 25,000 chunks could overwhelm memory
   - Solution: Process in batches, store references not full data

2. **Entity ID consistency**: Same entity across tools needs consistent ID
   - Solution: UUID generation at first creation, propagate throughout

3. **Confidence propagation**: How does confidence flow through pipeline?
   - Solution: Compound confidence scores, maintain evidence chain

4. **Partial failures**: What if step 7 of 12 fails?
   - Solution: Checkpoint after each major phase, allow resume

## Example 4: Causal Analysis of Sales Data

### Analytic Goal
"Determine which marketing activities causally impact sales, not just correlations."

### Input Corpus
- Historical sales data (CSV)
- Marketing spend data (Excel)
- External events calendar (JSON)

### Workflow (Demonstrating Causal Analysis)

```yaml
Step 1: Multi-Source Ingestion
- T05: Load sales.csv → sales_table
- T07: Load marketing.xlsx → marketing_table  
- T06: Load events.json → events_list

Step 2: Data Integration
- Custom merge logic on date columns
- Output: Unified DataFrame

Step 3: Build Causal Graph (T116)
Input: Domain knowledge + data
Output:
  causal_graph: {
    nodes: ["TV_Spend", "Online_Spend", "Sales", "Season", "Competitor_Activity"],
    edges: [
      {"from": "TV_Spend", "to": "Sales", "type": "direct_cause"},
      {"from": "Season", "to": "Sales", "type": "confounder"},
      {"from": "Season", "to": "TV_Spend", "type": "confounder"}
    ]
  }

Step 4: Causal Effect Estimation (PyWhy DoWhy)
- Identify confounders from graph
- Apply causal inference methods
- Output: Average Treatment Effects (ATE)

Step 5: Sensitivity Analysis
- Test robustness of causal claims
- Vary assumptions

Result: "TV advertising causes $1.20 return per dollar spent (95% CI: $0.90-$1.50) 
         after controlling for seasonal effects. Online advertising shows no 
         significant causal effect when properly controlled."
```

### Key Insight
This workflow moves between tables and graphs based on analytical needs:
- Tables for data storage and manipulation
- Causal graph for reasoning about confounders
- Back to tables for statistical estimation
- Natural language for conclusions

---

These examples confirm our architecture is sound but highlight the critical need for:
1. Precise data schemas
2. Clear compatibility rules
3. Robust traceability metadata
4. Efficient reference passing (not full data copies)
5. Flexible format transitions based on analytical needs