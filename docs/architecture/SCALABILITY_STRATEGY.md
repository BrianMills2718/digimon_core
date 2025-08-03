# KGAS Scalability Strategy

**Version**: 1.0
**Status**: Target Architecture
**Last Updated**: 2025-07-22

## Overview

This document outlines the scalability strategy for KGAS, addressing how the system can handle growth from academic research scale to larger deployments while maintaining the single-node architecture as long as practical.

## Current Scale Targets

> **📍 ARCHITECTURAL TARGET**: This document defines the target scalability architecture. For current implementation status and bottlenecks, see [docs/roadmap/ROADMAP_OVERVIEW.md](../roadmap/ROADMAP_OVERVIEW.md).

## Known Scalability Anti-Patterns

### Current Implementation Limitations
The following patterns have been identified as potential scalability bottlenecks that will require addressing as the system scales:

#### **1. Synchronous Tool Registry**
- **Current State**: Single synchronous registry for all tool discovery and instantiation
- **Bottleneck**: Will become single point of contention under concurrent load
- **Impact**: Tool access serialization limits concurrent processing capability
- **Resolution Path**: Migrate to async registry with distributed caching (see roadmap post-stage extensions)

#### **2. Memory Manager Per Document**  
- **Current State**: Individual memory manager instances created for each document
- **Bottleneck**: Unnecessary object allocation overhead for large document collections
- **Impact**: Memory fragmentation and GC pressure under high document throughput
- **Resolution Path**: Implement pooled memory managers with object reuse patterns

#### **3. Singleton Service Manager**
- **Current State**: Global singleton pattern for service management
- **Bottleneck**: Breaks distributed deployment patterns and creates global state dependencies
- **Impact**: Prevents horizontal scaling and creates service coupling
- **Resolution Path**: Migrate to dependency injection container with request-scoped instances

### Phase-Based Capacity Planning

| Phase | Documents | Entities | Relationships | Embeddings | Timeline |
|-------|-----------|----------|---------------|------------|----------|
| Phase 1 (MVP) | 10-50 | 10K | 50K | 10K | Months 1-4 |
| Phase 2 (Enhanced) | 100-500 | 100K | 500K | 100K | Months 5-8 |
| Phase 3 (Theory) | 500-1K | 500K | 2.5M | 500K | Months 9-12 |
| Phase 4 (Scale) | 1K-10K | 1M | 10M | 1M | Year 2+ |

### Single-Node Capacity Limits

Based on modern server hardware (e.g., 64-128 cores, 512GB-1TB RAM, NVMe storage):

- **Neo4j**: ~10M nodes, ~100M relationships (with proper tuning)
- **SQLite**: ~1TB database size, ~10M rows per table
- **Processing**: ~100 documents/hour with full pipeline
- **Concurrent users**: 1-10 researchers

## Vertical Scaling Strategy

### 1. Hardware Optimization Path

```yaml
Phase 1-2 Hardware (Development):
  CPU: 8-16 cores
  RAM: 32-64GB
  Storage: 1TB NVMe SSD
  Cost: ~$2-3K or cloud equivalent

Phase 3 Hardware (Research):
  CPU: 32-64 cores
  RAM: 128-256GB
  Storage: 4TB NVMe RAID
  Cost: ~$10-15K or dedicated cloud instance

Phase 4 Hardware (Production):
  CPU: 64-128 cores (AMD EPYC/Intel Xeon)
  RAM: 512GB-1TB
  Storage: 8-16TB NVMe array
  GPU: Optional for embedding generation
  Cost: ~$30-50K or high-end cloud instance
```

### 2. Database Optimization

#### Neo4j Optimization

```python
# Configuration for different scales
class Neo4jScalingConfig:
    """Progressive Neo4j configuration for different scales"""
    
    PHASE_1_2 = {
        # Basic configuration
        "dbms.memory.heap.initial_size": "2G",
        "dbms.memory.heap.max_size": "8G",
        "dbms.memory.pagecache.size": "4G",
        "dbms.threads.worker_count": 8
    }
    
    PHASE_3 = {
        # Enhanced performance
        "dbms.memory.heap.initial_size": "16G",
        "dbms.memory.heap.max_size": "32G",
        "dbms.memory.pagecache.size": "64G",
        "dbms.threads.worker_count": 32,
        # Advanced settings
        "dbms.tx_state.memory_allocation": "ON_HEAP",
        "dbms.query.cache_size": 1000,
        "cypher.min_replan_interval": "1h"
    }
    
    PHASE_4 = {
        # Maximum single-node performance
        "dbms.memory.heap.initial_size": "64G",
        "dbms.memory.heap.max_size": "128G",
        "dbms.memory.pagecache.size": "256G",
        "dbms.threads.worker_count": 64,
        # Optimization flags
        "cypher.query_cache_size": 10000,
        "dbms.index.fulltext.eventually_consistent": True,
        "dbms.relationship_grouping_threshold": 50
    }
```

#### Index Strategy

```cypher
-- Phase 1-2: Basic indexes
CREATE INDEX entity_id_idx FOR (e:Entity) ON (e.entity_id);
CREATE INDEX entity_type_idx FOR (e:Entity) ON (e.entity_type);
CREATE TEXT INDEX entity_name_idx FOR (e:Entity) ON (e.canonical_name);

-- Phase 3: Composite and specialized indexes
CREATE INDEX entity_composite_idx FOR (e:Entity) ON (e.entity_type, e.confidence);
CREATE INDEX temporal_idx FOR (e:Entity) ON (e.temporal_start, e.temporal_end);
CREATE POINT INDEX location_idx FOR (l:Location) ON (l.coordinates);

-- Phase 4: Vector indexes for similarity
CREATE VECTOR INDEX entity_embedding_idx FOR (e:Entity) ON (e.embedding)
OPTIONS {indexConfig: {
  `vector.dimensions`: 384,
  `vector.similarity_function`: 'cosine'
}};
```

### 3. Application-Level Optimization

#### Caching Strategy

```python
class MultiLevelCache:
    """Progressive caching strategy for different scales"""
    
    def __init__(self, phase: int):
        if phase <= 2:
            # Simple in-memory cache
            self.entity_cache = LRUCache(maxsize=10_000)
            self.query_cache = TTLCache(maxsize=1_000, ttl=3600)
        elif phase == 3:
            # Redis-backed cache
            self.entity_cache = RedisCache(
                max_memory="4GB",
                eviction_policy="lru"
            )
            self.query_cache = RedisCache(
                max_memory="2GB",
                eviction_policy="lfu"
            )
        else:  # Phase 4
            # Distributed cache with local tier
            self.entity_cache = TieredCache(
                l1=LRUCache(maxsize=100_000),
                l2=RedisCache(max_memory="16GB")
            )
            self.query_cache = TieredCache(
                l1=TTLCache(maxsize=10_000, ttl=300),
                l2=RedisCache(max_memory="8GB")
            )
```

#### Query Optimization

```python
class QueryOptimizer:
    """Adaptive query optimization based on scale"""
    
    def __init__(self, scale_phase: int):
        self.scale_phase = scale_phase
        self.query_planner = self._init_planner()
    
    def optimize_entity_search(self, criteria: Dict) -> str:
        if self.scale_phase <= 2:
            # Simple queries for small scale
            return f"""
                MATCH (e:Entity)
                WHERE e.canonical_name CONTAINS $search_term
                RETURN e LIMIT 100
            """
        elif self.scale_phase == 3:
            # Indexed queries with pagination
            return f"""
                MATCH (e:Entity)
                USING INDEX e:Entity(canonical_name)
                WHERE e.canonical_name CONTAINS $search_term
                AND e.confidence > 0.7
                RETURN e
                SKIP $skip LIMIT $limit
            """
        else:  # Phase 4
            # Parallel subqueries with aggregation
            return f"""
                CALL {{
                    MATCH (e:Entity)
                    WHERE e.entity_type = 'PERSON'
                    AND e.canonical_name CONTAINS $search_term
                    RETURN e
                    UNION
                    MATCH (e:Entity)
                    WHERE e.entity_type = 'ORGANIZATION'
                    AND e.canonical_name CONTAINS $search_term
                    RETURN e
                }}
                WITH e
                WHERE e.confidence > $confidence_threshold
                RETURN e
                ORDER BY e.pagerank_score DESC
                SKIP $skip LIMIT $limit
            """
```

### 4. Data Partitioning Strategy

#### Temporal Partitioning

```python
class TemporalPartitionManager:
    """Partition data by time periods for better performance"""
    
    def partition_by_year(self, year: int) -> str:
        """Create year-based partitions"""
        return f"""
            CALL apoc.create.node(['Entity', 'Entity_{year}'], {{
                entity_id: $entity_id,
                year: {year}
            }})
        """
    
    def query_with_partition_hint(self, start_year: int, end_year: int):
        """Query specific partitions"""
        labels = [f"Entity_{year}" for year in range(start_year, end_year + 1)]
        return f"""
            MATCH (e:{':'.join(labels)})
            WHERE e.temporal_start >= $start_date
            AND e.temporal_end <= $end_date
            RETURN e
        """
```

#### Domain-Based Sharding

```python
class DomainShardManager:
    """Logical sharding by domain for better locality"""
    
    def __init__(self):
        self.domain_prefixes = {
            "political_science": "pol_",
            "sociology": "soc_",
            "economics": "eco_",
            "psychology": "psy_"
        }
    
    def shard_entity(self, entity: Entity, domain: str) -> Entity:
        """Add domain-specific prefix for logical sharding"""
        prefix = self.domain_prefixes.get(domain, "gen_")
        entity.entity_id = f"{prefix}{entity.entity_id}"
        entity.labels.append(f"Domain_{domain.title()}")
        return entity
    
    def query_domain_shard(self, domain: str) -> str:
        """Query specific domain shard"""
        return f"""
            MATCH (e:Entity:Domain_{domain.title()})
            WHERE e.entity_id STARTS WITH '{self.domain_prefixes[domain]}'
            RETURN e
        """
```

## Horizontal Scaling Preparation

### 1. Microservice Decomposition Points

```yaml
Future Service Boundaries:
  - Document Processing Service:
      - PDF/Word/Text extraction
      - OCR processing
      - Language detection
      - Can scale independently
      
  - Entity Extraction Service:
      - NER processing
      - Entity resolution
      - CPU-intensive, stateless
      - Easily parallelizable
      
  - Graph Construction Service:
      - Relationship extraction
      - Graph updates
      - Can batch process
      
  - Analytics Service:
      - Graph algorithms
      - Statistical analysis
      - Read-heavy, cacheable
      
  - Theory Service:
      - Theory validation
      - Ontology management
      - Mostly read operations
```

### 2. Data Layer Preparation

```python
class ScalableDataAccess:
    """Data access layer prepared for future distribution"""
    
    def __init__(self):
        self.read_replicas = []
        self.write_primary = None
        self.sharding_key = None
    
    async def prepare_for_sharding(self):
        """Add sharding key to all entities"""
        return """
            MATCH (e:Entity)
            WHERE NOT EXISTS(e.shard_key)
            SET e.shard_key = 
                CASE 
                    WHEN e.entity_type = 'PERSON' THEN hash(e.entity_id) % 4
                    WHEN e.entity_type = 'ORGANIZATION' THEN hash(e.entity_id) % 4 + 4
                    ELSE hash(e.entity_id) % 8
                END
            RETURN count(e)
        """
    
    async def add_read_replica(self, replica_config: Dict):
        """Prepare for read scaling"""
        # Future: Add read replica support
        pass
```

### 3. Session Affinity for Scaling

```python
class SessionManager:
    """Manage user sessions for future multi-node deployment"""
    
    def __init__(self):
        self.session_store = {}  # Will become Redis/Hazelcast
        self.sticky_routing = {}  # User -> Node mapping
    
    def get_node_for_user(self, user_id: str) -> str:
        """Route user to same node (future use)"""
        if user_id not in self.sticky_routing:
            # For now, always return primary
            self.sticky_routing[user_id] = "primary"
        return self.sticky_routing[user_id]
```

## Performance Monitoring

### Key Metrics to Track

```python
class ScalabilityMetrics:
    """Track metrics indicating when to scale"""
    
    THRESHOLDS = {
        "cpu_usage": 0.8,          # 80% CPU -> consider scaling
        "memory_usage": 0.85,      # 85% RAM -> add memory
        "query_time_p95": 2.0,     # 2s queries -> optimize
        "disk_io_wait": 0.3,       # 30% IO wait -> faster storage
        "entity_count": 900_000,   # Approaching 1M limit
        "relationship_count": 9_000_000  # Approaching 10M limit
    }
    
    async def check_scaling_triggers(self) -> List[str]:
        """Check if any scaling triggers are hit"""
        triggers = []
        
        # Check system metrics
        if psutil.cpu_percent() > self.THRESHOLDS["cpu_usage"] * 100:
            triggers.append("CPU usage high - consider more cores")
            
        if psutil.virtual_memory().percent > self.THRESHOLDS["memory_usage"] * 100:
            triggers.append("Memory usage high - add more RAM")
            
        # Check Neo4j metrics
        entity_count = await self.get_entity_count()
        if entity_count > self.THRESHOLDS["entity_count"]:
            triggers.append("Approaching entity limit - prepare for sharding")
            
        return triggers
```

## Migration Path to Distributed Architecture

### Phase 4+ Transition Plan

```yaml
Step 1 - Read Scaling (Month 1):
  - Add Neo4j read replicas
  - Implement read/write splitting
  - Cache layer expansion
  
Step 2 - Service Extraction (Month 2-3):
  - Extract document processing
  - Extract entity extraction
  - Message queue integration
  
Step 3 - Data Sharding (Month 4-6):
  - Implement entity sharding
  - Relationship partitioning
  - Cross-shard query federation
  
Step 4 - Full Distribution (Month 7-12):
  - Kubernetes deployment
  - Auto-scaling policies
  - Multi-region support
```

## Cost-Benefit Analysis

### Single-Node Benefits
- **Simplicity**: No distributed system complexity
- **Consistency**: ACID guarantees without coordination
- **Cost**: Single server cheaper than cluster
- **Maintenance**: Easier backup, monitoring, debugging
- **Performance**: No network overhead

### When to Scale Horizontally
- Entity count exceeds 5M consistently
- Concurrent users exceed 20
- Query latency P95 > 5 seconds
- Document processing backlog > 24 hours
- Hardware costs exceed $100K/year

## Implementation Guidelines

### 1. Design for Scale from Day 1
```python
# Good: Prepared for sharding
entity_id = f"{domain_prefix}_{uuid.uuid4()}"

# Bad: No sharding consideration  
entity_id = str(uuid.uuid4())
```

### 2. Monitor Early and Often
```python
# Add metrics collection from the start
@track_performance
async def process_document(doc: Document):
    start_time = time.time()
    # ... processing ...
    metrics.record("document_processing_time", time.time() - start_time)
```

### 3. Optimize Before Scaling
- Profile and optimize queries
- Add appropriate indexes
- Implement caching layers
- Use batch operations

### 4. Test at Scale
```python
# Regular scale testing
async def scale_test():
    # Generate realistic data
    await generate_entities(count=1_000_000)
    await generate_relationships(count=10_000_000)
    
    # Run performance benchmarks
    results = await run_benchmark_suite()
    assert results.p95_latency < 2.0  # seconds
```

## Summary

The KGAS scalability strategy:

1. **Starts simple**: Single-node architecture appropriate for research
2. **Scales vertically**: Hardware upgrades handle growth to ~1M entities  
3. **Optimizes aggressively**: Caching, indexing, query optimization
4. **Prepares for distribution**: Clean service boundaries, sharding keys
5. **Monitors continuously**: Metrics indicate when to scale
6. **Migrates gradually**: Clear path to distributed architecture when needed

This approach balances the simplicity needed for academic research with the capability to handle larger deployments, ensuring KGAS can grow with its users' needs while maintaining architectural integrity.