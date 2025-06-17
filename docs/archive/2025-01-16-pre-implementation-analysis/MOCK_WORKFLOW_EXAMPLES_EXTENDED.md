# Extended Mock Workflow Examples

These examples specifically test edge cases and entity consistency challenges.

## Example 5: Entity Disambiguation Across Formats

### Analytic Goal
"Track how 'Apple' (the company) vs 'apple' (the fruit) are discussed differently across agricultural reports and tech news."

### Challenge
Same string, different entities, need consistent IDs across formats.

### Workflow

```yaml
Step 1: Multi-Source Ingestion
- T01: Load tech_reports/*.pdf
- T01: Load agriculture_reports/*.pdf
- T05: Load fruit_prices.csv
- T05: Load stock_prices.csv

Step 2: Entity Recognition with Context
Tool: T24 (Custom Entity Recognizer)
Problem: "Apple reports record profits" vs "Apple harvest exceeds expectations"

Output:
entities: [
  {
    "id": "ent_apple_inc_001",  # UUID generated once
    "name": "Apple",
    "type": "ORG",
    "domain": "technology",
    "canonical_name": "Apple Inc.",
    "surface_forms": ["Apple", "AAPL", "Apple Computer"],
    "context_keywords": ["iPhone", "technology", "Cupertino"]
  },
  {
    "id": "ent_apple_fruit_001",  # Different UUID
    "name": "apple",
    "type": "PRODUCT", 
    "domain": "agriculture",
    "canonical_name": "Apple (fruit)",
    "surface_forms": ["apple", "apples", "Apple"],
    "context_keywords": ["fruit", "harvest", "orchard"]
  }
]

Step 3: Build Domain-Specific Graphs
Tech Graph (Neo4j):
  Nodes: ent_apple_inc_001, ent_microsoft_001, ...
  
Agriculture Graph (Neo4j):  
  Nodes: ent_apple_fruit_001, ent_orange_fruit_001, ...

Step 4: Merge to Unified Table
Tool: T115 (Graph to Table)
Challenge: Same surface form, different entities!

Output Table:
| entity_id            | surface_form | canonical_name | domain      | price_data_ref         |
|---------------------|--------------|----------------|-------------|------------------------|
| ent_apple_inc_001   | Apple        | Apple Inc.     | technology  | stock_prices/AAPL      |
| ent_apple_fruit_001 | apple        | Apple (fruit)  | agriculture | fruit_prices/apple_row |

Step 5: Cross-Reference Analysis
Problem: User queries "Show me Apple price trends"
Solution: System must ask "Which Apple?" or analyze both

Critical Design Need:
- Entity IDs must be globally unique (UUID)
- Surface form ≠ Entity ID
- Need entity resolution service that maintains ID mappings
```

## Example 6: Long Processing Chain with State Management

### Analytic Goal
"Analyze 10 years of scientific papers to identify emerging research collaboration patterns."

### Challenge  
Very long pipeline where failure at step 15 shouldn't lose work from steps 1-14.

### Workflow

```yaml
Step 1-5: Initial Processing
[... ingestion, chunking, entity extraction ...]
Checkpoint: Save state to SQLite
{
  "workflow_id": "wf_sci_001",
  "checkpoint": "phase_1_complete",
  "entity_count": 48291,
  "entity_ids": "sqlite://checkpoints/wf_sci_001/entities.db"
}

Step 6-10: Relationship Building  
Tool: T28 (ML Relationship Extractor)
Problem: System crashes after processing 80% of relationships

Recovery:
- Load checkpoint from phase_1
- Check which relationships already extracted
- Resume from chunk_id: "chunk_892341"

Relationship Storage Pattern:
{
  "id": "rel_collab_001",
  "source_id": "ent_mit_001",
  "target_id": "ent_stanford_001", 
  "type": "collaborates_with",
  "evidence_chunks": ["chunk_123", "chunk_456"],
  "extracted_at": "2024-01-15T14:30:00",
  "extraction_batch": "batch_0847"  # For recovery
}

Step 11-15: Temporal Analysis
Problem: Need to track how collaborations change over time

Temporal Entity Design:
{
  "entity_id": "ent_mit_001",
  "temporal_variants": [
    {
      "time_period": "2014",
      "attributes": {"paper_count": 1203, "collaboration_count": 89}
    },
    {
      "time_period": "2015", 
      "attributes": {"paper_count": 1388, "collaboration_count": 94}
    }
  ]
}

Step 16-20: Community Evolution
Track how research communities merge/split over time
Need: Consistent community IDs across time slices
```

## Example 7: Conflicting Information Resolution

### Analytic Goal
"Reconcile conflicting financial data from different sources about the same companies."

### Challenge
Different sources report different values for same entity/attribute.

### Workflow

```yaml
Step 1: Multi-Source Ingestion
- SEC filings: "Apple revenue: $394.3B"
- News article: "Apple revenue approximately $395B"  
- Analyst report: "Apple revenue: $393.8B"

Step 2: Entity Recognition
All map to same entity: ent_apple_inc_001

Step 3: Conflict Detection
Tool: T29 (Entity Disambiguator) - repurposed for conflict resolution

Conflict Representation:
{
  "entity_id": "ent_apple_inc_001",
  "attribute": "revenue_2023",
  "conflicting_values": [
    {
      "value": 394.3,
      "unit": "billion_usd",
      "source": "doc_sec_10k_2023",
      "source_type": "primary",
      "confidence": 0.99,
      "extracted_by": "T27",
      "extraction_date": "2024-01-10"
    },
    {
      "value": 395.0,
      "unit": "billion_usd", 
      "source": "doc_news_001",
      "source_type": "secondary",
      "confidence": 0.70,
      "extracted_by": "T28",
      "extraction_date": "2024-01-11"
    }
  ],
  "resolution": {
    "method": "source_hierarchy",  # Primary sources win
    "selected_value": 394.3,
    "confidence": 0.99,
    "alternatives_preserved": true
  }
}

Step 4: Propagate to All Formats
- Neo4j: Store resolved value + alternatives as properties
- Table: Include confidence column
- Analysis: Can do sensitivity analysis on conflicts
```

## Example 8: Mixed Structured/Unstructured Analysis

### Analytic Goal
"Combine customer transaction data with support tickets to identify which products cause most issues."

### Challenge
Join structured data (transactions) with unstructured (ticket text).

### Workflow

```yaml
Step 1: Dual Ingestion
- T05: Load transactions.csv
  | transaction_id | customer_id | product_id | amount | date |
  
- T06: Load support_tickets.json
  {
    "ticket_id": "tkt_001",
    "customer_id": "cust_123", 
    "text": "My PowerWidget Pro keeps overheating...",
    "product_mentioned": null  # Not structured!
  }

Step 2: Extract Products from Tickets
Tool: T24 (Custom Entity Recognition)
Input: ticket text
Output: Detected product entities

Problem: Fuzzy matching needed
- Ticket: "PowerWidget Pro" 
- Transaction: "PWR-WIDGET-PRO-2023"
- Need to match these!

Step 3: Entity Resolution Table
Create mapping table:
| surface_form      | canonical_id        | confidence |
|------------------|--------------------:|------------|
| PowerWidget Pro  | prod_pwr_widget_001 | 0.95       |
| PWR-WIDGET-PRO   | prod_pwr_widget_001 | 1.00       |
| Power Widget     | prod_pwr_widget_001 | 0.85       |

Step 4: Join Analysis
Now can join:
- Transactions (via product_id → canonical_id)
- Support tickets (via extracted entities → canonical_id)

Result: 
| product_canonical_id | transaction_count | support_ticket_count | issue_rate |
|--------------------|------------------|---------------------|------------|
| prod_pwr_widget_001| 10,847           | 823                 | 7.6%       |
```

## Example 9: Iterative Refinement Workflow

### Analytic Goal  
"Build a knowledge graph of medical conditions, iteratively improving accuracy."

### Challenge
Need to track iterations and improvements.

### Workflow

```yaml
Iteration 1: Basic Extraction
- Extract entities: diseases, symptoms, treatments
- Build initial graph
- Measure: 72% accuracy (against gold standard)

Version Tracking:
{
  "graph_version": "med_kg_v1",
  "created_at": "2024-01-15T10:00:00",
  "metrics": {"accuracy": 0.72, "coverage": 0.65},
  "parent_version": null
}

Iteration 2: Add Coreference
- T25: Resolve "the disease" → specific disease
- Rebuild graph with same entity IDs
- Measure: 79% accuracy

Version Tracking:
{
  "graph_version": "med_kg_v2",
  "created_at": "2024-01-15T14:00:00", 
  "metrics": {"accuracy": 0.79, "coverage": 0.65},
  "parent_version": "med_kg_v1",
  "changes": ["added_coreference_resolution"]
}

Iteration 3: Add Domain Knowledge
- Import medical ontology
- Re-run extraction with constraints
- Measure: 86% accuracy

Key Requirement: Entity IDs must be stable across versions!
- ent_diabetes_001 in v1 must be same entity in v2, v3
- New entities get new IDs
- Deleted entities marked as deprecated, not removed
```

## Example 10: Cross-Format Aggregation

### Analytic Goal
"Calculate market share by combining: company graphs, product tables, sales vectors."

### Challenge  
Aggregate across completely different storage formats.

### Workflow

```yaml
Data Sources:
1. Company Graph (Neo4j):
   - Companies linked by ownership
   - Example: Nestle owns 30+ brands

2. Product Table (SQLite):
   | product_id | brand | category | 
   |------------|-------|----------|
   | prod_001   | KitKat| Chocolate|

3. Sales Embeddings (FAISS):
   - Sales patterns encoded as vectors
   - Similar patterns = similar vectors

Step 1: Company Aggregation
Query: Find all subsidiaries of Nestle
Output: [brand_001, brand_002, ..., brand_030]

Step 2: Product Mapping
Query: Find all products for these brands
Output: [prod_001, prod_002, ..., prod_250]  

Step 3: Vector Aggregation
Query: Find sales vectors for these products
Challenge: How to aggregate 250 vectors?
Solution: Weighted mean by product revenue

Step 4: Market Share Calculation
Aggregate Table:
| parent_company | total_products | market_vector | market_share |
|---------------|----------------|---------------|--------------|
| Nestle        | 250            | [0.23, ...]   | 18.7%        |

Critical: Same entity (Nestle) has different representations:
- Neo4j: Node with ID "ent_nestle_001"
- SQLite: Foreign key "ent_nestle_001"  
- FAISS: Associated with vector IDs
```

## Key Insights from Extended Examples

### 1. **Entity Identity Management is Critical**
- UUIDs must be generated once and propagated everywhere
- Surface forms ≠ Entity IDs
- Need canonical forms + aliases
- Version stability required

### 2. **Checkpoint/Recovery Architecture**
- Long workflows need intermediate saves
- State must be queryable ("what's already done?")
- Batch IDs for partial recovery

### 3. **Conflict Resolution Framework**
- Multiple values for same entity/attribute
- Need source hierarchy 
- Preserve alternatives for sensitivity analysis
- Confidence scores essential

### 4. **Cross-Format Join Patterns**
- Entity ID is the universal join key
- Need mapping tables for fuzzy matches
- Aggregation strategies for different formats

### 5. **Temporal Consistency**
- Entities evolve but IDs must remain stable
- Need temporal attributes/versions
- Graph versions with parent tracking

### 6. **Format-Specific Aggregation**
- Graphs: Traverse and collect
- Tables: SQL GROUP BY
- Vectors: Mathematical operations
- Must be combinable!

## Design Requirements Discovered

### 1. **Universal Entity Service**
```python
class EntityService:
    def create_entity(surface_form, context) -> UUID
    def resolve_entity(surface_form, context) -> UUID
    def get_canonical_form(entity_id) -> str
    def get_all_surface_forms(entity_id) -> List[str]
    def merge_entities(id1, id2) -> UUID
```

### 2. **Checkpoint Manager**
```python
class CheckpointManager:
    def save_state(workflow_id, phase, data_refs)
    def load_state(workflow_id, phase) -> data_refs
    def get_progress(workflow_id) -> completion_status
```

### 3. **Conflict Resolver**
```python  
class ConflictResolver:
    def detect_conflicts(entity_id, attribute) -> conflicts
    def resolve(conflicts, strategy) -> resolved_value
    def preserve_alternatives(entity_id, attribute, all_values)
```

### 4. **Cross-Format Aggregator**
```python
class AggregationEngine:
    def aggregate_from_graph(entity_ids, operation)
    def aggregate_from_table(entity_ids, operation)  
    def aggregate_from_vectors(entity_ids, operation)
    def combine_aggregations(results) -> unified_result
```