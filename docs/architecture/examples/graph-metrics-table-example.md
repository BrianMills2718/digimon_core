# Graph Metrics as Table Columns: Practical Examples

## Overview

This document demonstrates how graph-computed metrics become columns in relational tables while maintaining full provenance and enabling statistical analysis.

## Example 1: Basic Entity Table with Graph Metrics

```sql
-- Core entity table enriched with graph metrics
CREATE TABLE entities (
    -- Identity
    entity_id TEXT PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    entity_type TEXT,
    
    -- Source provenance
    source_document TEXT,
    extraction_tool TEXT,
    extraction_timestamp TIMESTAMP,
    extraction_confidence FLOAT,
    
    -- Graph-computed metrics
    pagerank_score FLOAT,
    betweenness_centrality FLOAT,
    closeness_centrality FLOAT,
    eigenvector_centrality FLOAT,
    clustering_coefficient FLOAT,
    
    -- Community detection results
    louvain_community_id INTEGER,
    infomap_community_id INTEGER,
    modularity_class INTEGER,
    
    -- Graph structural properties
    in_degree INTEGER,
    out_degree INTEGER,
    total_degree INTEGER,
    is_bridge_node BOOLEAN,
    connected_component_id INTEGER,
    
    -- Computation metadata
    metrics_computation_timestamp TIMESTAMP,
    metrics_computation_version TEXT,
    graph_snapshot_id TEXT
);

-- Example query for statistical analysis
SELECT 
    entity_type,
    AVG(pagerank_score) as avg_influence,
    AVG(clustering_coefficient) as avg_local_density,
    COUNT(*) as entity_count
FROM entities
GROUP BY entity_type
ORDER BY avg_influence DESC;
```

## Example 2: Relationship Table with Graph Context

```sql
-- Relationships enriched with graph analysis
CREATE TABLE relationships (
    -- Identity
    relationship_id TEXT PRIMARY KEY,
    source_entity_id TEXT,
    target_entity_id TEXT,
    relationship_type TEXT,
    
    -- Relationship properties
    weight FLOAT,
    confidence FLOAT,
    
    -- Graph-computed properties
    edge_betweenness FLOAT,
    is_bridge_edge BOOLEAN,
    triangle_count INTEGER,  -- Number of triangles this edge participates in
    
    -- Path analysis results
    shortest_path_count INTEGER,  -- How many shortest paths use this edge
    average_path_position FLOAT,  -- Average position in paths
    
    -- Community context
    is_inter_community BOOLEAN,  -- Connects different communities
    source_community_id INTEGER,
    target_community_id INTEGER,
    
    -- Provenance
    extraction_source TEXT,
    extraction_method TEXT,
    computation_timestamp TIMESTAMP,
    
    FOREIGN KEY (source_entity_id) REFERENCES entities(entity_id),
    FOREIGN KEY (target_entity_id) REFERENCES entities(entity_id)
);
```

## Example 3: Time-Series Graph Metrics

```sql
-- Track how graph metrics change over time
CREATE TABLE entity_metrics_timeseries (
    entity_id TEXT,
    measurement_date DATE,
    
    -- Evolving graph metrics
    pagerank_score FLOAT,
    community_id INTEGER,
    degree_centrality FLOAT,
    
    -- Change indicators
    pagerank_delta FLOAT,  -- Change from previous period
    community_changed BOOLEAN,
    new_connections INTEGER,
    lost_connections INTEGER,
    
    -- Snapshot reference
    graph_snapshot_id TEXT,
    
    PRIMARY KEY (entity_id, measurement_date),
    FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
);

-- Analyze influence trends
SELECT 
    entity_id,
    canonical_name,
    measurement_date,
    pagerank_score,
    pagerank_score - LAG(pagerank_score) OVER (
        PARTITION BY entity_id ORDER BY measurement_date
    ) as influence_change
FROM entity_metrics_timeseries
JOIN entities USING (entity_id)
WHERE measurement_date >= '2024-01-01'
ORDER BY entity_id, measurement_date;
```

## Example 4: Multi-Algorithm Comparison Table

```sql
-- Compare results from different algorithms
CREATE TABLE algorithm_comparisons (
    entity_id TEXT,
    
    -- Different centrality algorithms
    pagerank_score FLOAT,
    pagerank_computation_time FLOAT,
    
    hits_authority_score FLOAT,
    hits_hub_score FLOAT,
    hits_computation_time FLOAT,
    
    katz_centrality FLOAT,
    katz_alpha_parameter FLOAT,
    katz_computation_time FLOAT,
    
    -- Different community detection algorithms  
    louvain_community INTEGER,
    louvain_modularity FLOAT,
    
    infomap_community INTEGER,
    infomap_code_length FLOAT,
    
    label_propagation_community INTEGER,
    
    -- Algorithm agreement metrics
    centrality_rank_correlation FLOAT,
    community_assignment_agreement FLOAT,
    
    -- Metadata
    computation_date DATE,
    graph_size INTEGER,
    graph_density FLOAT,
    
    FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
);
```

## Example 5: Statistical Analysis Ready View

```sql
-- Create view optimized for statistical software export
CREATE VIEW statistical_analysis_view AS
SELECT 
    -- Entity properties
    e.entity_id,
    e.canonical_name,
    e.entity_type,
    
    -- Graph metrics (independent variables)
    e.pagerank_score,
    e.betweenness_centrality,
    e.clustering_coefficient,
    e.in_degree,
    e.out_degree,
    
    -- Community membership (categorical)
    e.louvain_community_id,
    CASE 
        WHEN e.louvain_community_id = mc.largest_community 
        THEN 1 ELSE 0 
    END as in_largest_community,
    
    -- Computed features
    e.in_degree::FLOAT / NULLIF(e.out_degree, 0) as in_out_ratio,
    LOG(e.pagerank_score + 1) as log_pagerank,
    
    -- Relationship aggregates
    COUNT(DISTINCT r.target_entity_id) as unique_connections,
    AVG(r.weight) as avg_connection_strength,
    SUM(CASE WHEN r.is_inter_community THEN 1 ELSE 0 END) as bridge_connections,
    
    -- Provenance
    e.extraction_confidence,
    e.source_document

FROM entities e
LEFT JOIN relationships r ON e.entity_id = r.source_entity_id
CROSS JOIN (
    SELECT louvain_community_id as largest_community
    FROM entities
    GROUP BY louvain_community_id
    ORDER BY COUNT(*) DESC
    LIMIT 1
) mc
GROUP BY e.entity_id, mc.largest_community;

-- Export for R/Stata/SPSS
-- .mode csv
-- .output statistical_analysis_data.csv
-- SELECT * FROM statistical_analysis_view;
```

## Provenance Tracking Example

```sql
-- Full provenance for reproducibility
CREATE TABLE computation_provenance (
    computation_id TEXT PRIMARY KEY,
    computation_type TEXT,  -- 'pagerank', 'community_detection', etc.
    
    -- Algorithm details
    algorithm_name TEXT,
    algorithm_version TEXT,
    algorithm_parameters JSON,
    
    -- Data snapshot
    graph_snapshot_id TEXT,
    node_count INTEGER,
    edge_count INTEGER,
    
    -- Execution details
    start_timestamp TIMESTAMP,
    end_timestamp TIMESTAMP,
    computation_duration_seconds FLOAT,
    
    -- Results summary
    results_summary JSON,
    
    -- Reproducibility
    random_seed INTEGER,
    software_versions JSON,
    hardware_info JSON
);

-- Link metrics to their computation provenance
ALTER TABLE entities 
ADD COLUMN pagerank_computation_id TEXT 
REFERENCES computation_provenance(computation_id);
```

## Usage in Analysis Workflow

```python
# Python example showing workflow
import pandas as pd
from sqlalchemy import create_engine

class CrossModalAnalysis:
    def __init__(self, neo4j_conn, sqlite_conn):
        self.neo4j = neo4j_conn
        self.sqlite = sqlite_conn
        
    def compute_and_sync_metrics(self):
        # 1. Compute metrics in Neo4j
        pagerank_results = self.neo4j.run("""
            CALL gds.pageRank.stream('myGraph')
            YIELD nodeId, score
            RETURN gds.util.asNode(nodeId).id AS entity_id, score
        """)
        
        # 2. Sync to SQLite for statistical analysis
        for record in pagerank_results:
            self.sqlite.execute("""
                UPDATE entities 
                SET pagerank_score = ?,
                    metrics_computation_timestamp = CURRENT_TIMESTAMP
                WHERE entity_id = ?
            """, (record['score'], record['entity_id']))
        
        # 3. Export for statistical analysis
        df = pd.read_sql("""
            SELECT * FROM statistical_analysis_view
        """, self.sqlite)
        
        # 4. Run statistical analysis
        correlation = df[['pagerank_score', 'betweenness_centrality']].corr()
        
        # 5. Store results back
        self.sqlite.execute("""
            INSERT INTO analysis_results 
            (analysis_type, result_data, timestamp)
            VALUES ('centrality_correlation', ?, CURRENT_TIMESTAMP)
        """, (correlation.to_json(),))
```

This approach ensures that graph-computed metrics are fully available for statistical analysis while maintaining complete provenance and enabling reproducible research workflows.