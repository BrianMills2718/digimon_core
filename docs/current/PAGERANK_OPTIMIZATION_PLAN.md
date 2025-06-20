# PageRank Performance Optimization Plan

**Created**: 2025-06-20  
**Issue**: PageRank takes 47.45s (86% of total processing time)  
**Current Implementation**: `src/tools/phase1/t68_pagerank.py`

## 🔍 Performance Analysis

### Current Workflow
1. **Load graph from Neo4j** (~5-10s)
   - Two UNION queries to get all nodes
   - Separate query to get all edges
   - Creates in-memory mappings
2. **Create NetworkX graph** (~1-2s)
   - Iterates through all nodes and edges
   - Validates entity IDs
   - Adds to NetworkX DiGraph
3. **Calculate PageRank** (~30-35s)
   - NetworkX iterative algorithm
   - Default 100 iterations max
   - Weighted by edge confidence
4. **Store results back to Neo4j** (~5-10s)
   - Individual UPDATE for each entity
   - No batching

### Identified Bottlenecks

#### 1. **NetworkX PageRank Algorithm** (60-70% of time)
- **Issue**: NetworkX uses pure Python implementation
- **Impact**: ~30-35s for moderate graphs
- **Root Cause**: 
  - Iterative power method is computationally intensive
  - Not optimized for sparse graphs
  - No parallelization

#### 2. **Neo4j Round Trips** (20-30% of time)
- **Issue**: Multiple queries and individual updates
- **Impact**: ~10-20s total
- **Root Cause**:
  - Loading: 2 UNION queries + 1 edge query
  - Storing: N individual UPDATE queries (one per entity)

#### 3. **Redundant Data Processing** (10% of time)
- **Issue**: Creating intermediate data structures
- **Impact**: ~2-5s
- **Root Cause**: Converting between Neo4j results → Python dicts → NetworkX

## 🚀 Optimization Strategies

### Option 1: Neo4j Native PageRank (Recommended)
**Potential Speedup**: 10-50x

Neo4j Graph Data Science (GDS) library has native PageRank:
```cypher
CALL gds.graph.create('myGraph', 'Entity', {
  RELATED_TO: {
    properties: 'weight'
  }
})

CALL gds.pageRank.write('myGraph', {
  maxIterations: 20,
  dampingFactor: 0.85,
  writeProperty: 'pagerank_score'
})
```

**Pros**:
- Runs in-database (no data transfer)
- Highly optimized C++ implementation
- Supports parallelization
- Direct property updates

**Cons**:
- Requires GDS plugin installation
- Additional Neo4j configuration

### Option 2: Optimized Python Implementation
**Potential Speedup**: 3-5x

Replace NetworkX with optimized alternatives:
- **graph-tool**: C++ backend, 10-100x faster
- **igraph**: C backend, 5-20x faster
- **scipy.sparse**: Matrix-based computation

Example with scipy:
```python
import scipy.sparse as sp
import numpy as np

def fast_pagerank(adjacency_matrix, damping=0.85, max_iter=100):
    """Optimized PageRank using sparse matrix operations."""
    n = adjacency_matrix.shape[0]
    
    # Column-normalize adjacency matrix
    col_sums = np.array(adjacency_matrix.sum(axis=0)).flatten()
    col_sums[col_sums == 0] = 1
    M = adjacency_matrix / col_sums
    
    # Power iteration
    v = np.ones(n) / n
    for _ in range(max_iter):
        v = damping * M.dot(v) + (1 - damping) / n
    
    return v
```

### Option 3: Batch Neo4j Operations
**Potential Speedup**: 2-3x

Optimize Neo4j interactions:
```python
# Batch load - single query
MATCH (e:Entity)
OPTIONAL MATCH (e)-[r]->(e2:Entity)
RETURN e, collect({rel: r, target: e2}) as relationships

# Batch update - UNWIND
UNWIND $updates as update
MATCH (e:Entity {entity_id: update.id})
SET e.pagerank_score = update.score
```

### Option 4: Caching and Incremental Updates
**Potential Speedup**: Variable

- Cache PageRank scores with timestamps
- Only recalculate when graph changes significantly
- Incremental PageRank for small changes

## 📋 Implementation Plan

### Phase 1: Quick Wins (1-2 days)
1. **Batch Neo4j Updates**
   - Replace individual UPDATEs with UNWIND
   - Expected: 2-3x speedup on write operations

2. **Optimize Graph Loading**
   - Single query with OPTIONAL MATCH
   - Expected: 1.5-2x speedup on read operations

### Phase 2: Algorithm Replacement (3-5 days)
1. **Evaluate Alternatives**
   - Benchmark scipy.sparse vs igraph
   - Test accuracy vs NetworkX

2. **Implement Best Option**
   - Replace NetworkX with chosen library
   - Maintain same interface

### Phase 3: Neo4j GDS Integration (1 week)
1. **Setup GDS Plugin**
   - Install and configure
   - Create projection

2. **Implement Native PageRank**
   - Cypher-based calculation
   - Fall back to Python if unavailable

## 🎯 Success Metrics

### Target Performance
- **Current**: 47.45s
- **Phase 1 Target**: 20-25s (2x improvement)
- **Phase 2 Target**: 10-15s (3-5x improvement)
- **Phase 3 Target**: 2-5s (10-20x improvement)

### Validation
- Results match NetworkX within 0.001 tolerance
- No regression in query accuracy
- Maintains all current features

## 🔧 Quick Implementation

### Immediate Batch Update Fix
```python
def _store_pagerank_scores_batch(self, ranked_entities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Store PageRank scores using batch update."""
    if not self.driver:
        return {"status": "error", "error": "Neo4j not connected"}
    
    try:
        updates = [
            {"id": entity["entity_id"], "score": entity["pagerank_score"]}
            for entity in ranked_entities
        ]
        
        with self.driver.session() as session:
            session.run("""
                UNWIND $updates as update
                MATCH (e:Entity {entity_id: update.id})
                SET e.pagerank_score = update.score,
                    e.pagerank_updated = datetime()
            """, updates=updates)
        
        return {"status": "success", "entities_updated": len(ranked_entities)}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}
```

## 🚦 Recommendation

**Start with Phase 1** (batch operations) for immediate improvement, then evaluate whether Phase 2 (algorithm change) or Phase 3 (Neo4j GDS) provides better ROI based on:
- Current graph sizes
- Infrastructure constraints
- Team expertise

The batch operations alone should reduce PageRank time from 47s to ~25s, bringing total processing time under 20s.