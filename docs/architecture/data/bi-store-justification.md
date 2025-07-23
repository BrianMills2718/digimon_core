# Bi-Store Architecture Justification

## Overview

KGAS employs a bi-store architecture with Neo4j and SQLite, each optimized for different analytical modalities required in academic social science research.

## ⚠️ CRITICAL RELIABILITY ISSUE

**IDENTIFIED**: Bi-store operations lack distributed transaction consistency, creating risk of data corruption where Neo4j entities are created but SQLite identity tracking fails, leaving orphaned graph nodes.

**STATUS**: Phase RELIABILITY Issue C2 - requires distributed transaction implementation across both stores.

**IMPACT**: Current implementation unsuitable for production use until transaction consistency is implemented.

## Architectural Decision

### Neo4j (Graph + Vector Store)
**Purpose**: Graph-native operations and vector similarity search

**Optimized for**:
- Network analysis (centrality, community detection, pathfinding)
- Relationship traversal and pattern matching
- Vector similarity search (using native HNSW index)
- Graph-based machine learning features

**Example Operations**:
```cypher
-- Find influential entities
MATCH (n:Entity)
RETURN n.name, n.pagerank_score
ORDER BY n.pagerank_score DESC

-- Vector similarity search
MATCH (n:Entity)
WHERE n.embedding IS NOT NULL
WITH n, vector.similarity.cosine(n.embedding, $query_vector) AS similarity
RETURN n, similarity
ORDER BY similarity DESC
```

### SQLite (Relational Store)
**Purpose**: Statistical analysis and structured data operations

**Optimized for**:
- Statistical analysis (regression, correlation, hypothesis testing)
- Structured Equation Modeling (SEM)
- Time series analysis
- Tabular data export for R/SPSS/Stata
- Complex aggregations and pivot operations
- Workflow metadata and provenance tracking

**Example Operations**:
```sql
-- Correlation analysis preparation
SELECT 
    e1.pagerank_score,
    e1.betweenness_centrality,
    COUNT(r.id) as relationship_count,
    AVG(r.weight) as avg_relationship_strength
FROM entities e1
LEFT JOIN relationships r ON e1.id = r.source_id
GROUP BY e1.id;

-- SEM data preparation
CREATE VIEW sem_data AS
SELECT 
    e.id,
    e.community_id,
    e.pagerank_score as influence,
    e.clustering_coefficient as cohesion,
    COUNT(DISTINCT r.target_id) as out_degree
FROM entities e
LEFT JOIN relationships r ON e.id = r.source_id
GROUP BY e.id;
```

## Why Not Single Store?

### Graph Databases (Neo4j alone)
- **Limitation**: Not optimized for statistical operations
- **Challenge**: Difficult to export to statistical software
- **Missing**: Native support for complex aggregations needed in social science

### Relational Databases (PostgreSQL/SQLite alone)
- **Limitation**: Recursive queries for graph algorithms are inefficient
- **Challenge**: No native vector similarity search
- **Missing**: Natural graph traversal operations

### Document Stores (MongoDB alone)
- **Limitation**: Neither graph-native nor optimized for statistics
- **Challenge**: Complex joins for relationship analysis
- **Missing**: ACID guarantees for research reproducibility

## Cross-Modal Synchronization

The bi-store architecture enables synchronized views:

```python
class CrossModalSync:
    def sync_graph_to_table(self, graph_metrics: Dict):
        """Sync graph analysis results to relational tables"""
        # Store graph metrics in SQLite for statistical analysis
        self.sqlite.execute("""
            INSERT INTO entity_metrics 
            (entity_id, pagerank, betweenness, community_id, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, graph_metrics)
    
    def sync_table_to_graph(self, statistical_results: Dict):
        """Sync statistical results back to graph"""
        # Update graph with statistical findings
        self.neo4j.query("""
            MATCH (n:Entity {id: $entity_id})
            SET n.regression_coefficient = $coefficient,
                n.significance = $p_value
        """, statistical_results)
```

## Research Workflow Integration

### Example: Mixed Methods Analysis
1. **Graph Analysis** (Neo4j): Identify influential actors and communities
2. **Export to Table** (SQLite): Prepare data for statistical analysis
3. **Statistical Analysis** (SQLite/R): Run regression, SEM, or other tests
4. **Integrate Results** (Both): Update graph with statistical findings
5. **Vector Search** (Neo4j): Find similar patterns in other datasets

This bi-store approach provides the **best tool for each job** while maintaining **data coherence** and **analytical flexibility** required for sophisticated social science research.