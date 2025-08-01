# ADR-016: System Optimization Strategy for Scale and Performance

**Status:** Approved  
**Date:** 2025-08-01  
**Decision Makers:** System Architecture Team  
**Stakeholders:** Performance Engineering, Product Engineering  

## Context

The KGAS system has achieved **100% functional vertical slice** with excellent performance for small-to-medium workloads. Stress testing has identified specific **breaking points and boundaries** where the system's performance degrades or fails:

### Identified System Boundaries (Current)
- **Text Processing**: Degrades beyond 100KB-1MB documents
- **Entity Resolution**: Limited to exact/fuzzy string matching (60-70% accuracy)
- **Graph Operations**: Becomes slow with >10K nodes without proper indexing
- **Concurrency**: Resource contention beyond 20-50 concurrent operations
- **Memory Usage**: Peak usage can exceed 2GB for large documents

### Business Requirements
- **Scale to enterprise workloads**: 10MB+ documents, 100K+ entity graphs
- **Improve entity accuracy**: 85-95% entity deduplication accuracy  
- **Support high concurrency**: 100+ concurrent operations
- **Maintain sub-second response times**: Even for complex queries on large graphs

## Decision

We will implement a **three-phase optimization strategy** to address the identified breaking points and scale the system to enterprise requirements:

### Phase 1: spaCy Processing Optimization
### Phase 2: Semantic Entity Resolution  
### Phase 3: Neo4j Performance Optimization

## Architecture Decision

### Phase 1: spaCy Processing Optimization

#### **Problem Statement**
spaCy processes entire documents as single units, causing exponential slowdown for large texts due to tokenization overhead, dependency parsing complexity O(n²), and memory constraints.

#### **Solution Architecture**

```python
# New Architecture: Chunked Processing Pipeline
class OptimizedSpacyProcessor:
    def __init__(self, chunk_size=10000, overlap=500):
        # Load optimized spaCy model
        self.nlp = spacy.load("en_core_web_sm", disable=["parser", "lemmatizer"])
        self.chunk_size = chunk_size
        self.overlap = overlap
        
    def process_large_document(self, text: str) -> List[Entity]:
        """Process large documents using intelligent chunking"""
        if len(text) <= self.chunk_size:
            return self._process_single_chunk(text)
        
        chunks = self._create_overlapping_chunks(text)
        all_entities = []
        
        for chunk in chunks:
            entities = self._process_single_chunk(chunk.text)
            all_entities.extend(entities)
        
        # Merge overlapping entities from chunk boundaries
        return self._merge_boundary_entities(all_entities, chunks)
    
    def _create_overlapping_chunks(self, text: str) -> List[TextChunk]:
        """Create overlapping chunks with sentence boundary awareness"""
        chunks = []
        sentences = self._split_sentences(text)
        
        current_chunk = ""
        current_size = 0
        
        for sentence in sentences:
            if current_size + len(sentence) > self.chunk_size and current_chunk:
                chunks.append(TextChunk(current_chunk, len(chunks)))
                # Keep overlap from previous chunk
                current_chunk = current_chunk[-self.overlap:] + sentence
                current_size = len(current_chunk)
            else:
                current_chunk += sentence
                current_size += len(sentence)
        
        if current_chunk:
            chunks.append(TextChunk(current_chunk, len(chunks)))
        
        return chunks
```

#### **Implementation Strategy**
1. **Intelligent Chunking**: Split large texts into overlapping chunks with sentence boundary awareness
2. **Component Optimization**: Disable unused spaCy components (parser, lemmatizer) for 2-3x speedup
3. **Sentence-Level Processing**: Process sentence-by-sentence for very large documents
4. **Boundary Entity Merging**: Sophisticated algorithm to merge entities spanning chunk boundaries

#### **Expected Performance Gains**
- **Text Size Limit**: 100KB → 10MB+ documents
- **Processing Speed**: 5-10x faster for large documents
- **Memory Usage**: Constant memory usage regardless of document size
- **Accuracy**: Maintains >95% entity detection accuracy

---

### Phase 2: Semantic Entity Resolution Enhancement

#### **Problem Statement**
Current entity resolution relies on exact string matching and basic fuzzy matching, achieving only 60-70% accuracy for entity deduplication. Cannot handle aliases, abbreviations, or semantic equivalence.

#### **Solution Architecture**

```python
# New Architecture: Semantic Entity Resolution System
class SemanticEntityResolver:
    def __init__(self):
        # Load semantic embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.entity_clusters = {}
        self.embedding_cache = LRUCache(maxsize=10000)
        
    def resolve_entity(self, entity_text: str, context: str = "") -> EntityCluster:
        """Resolve entity using semantic similarity"""
        
        # Generate context-aware embedding
        full_text = f"{entity_text} {context[:100]}" if context else entity_text
        entity_embedding = self._get_cached_embedding(full_text)
        
        # Find similar existing entities
        best_match = self._find_best_semantic_match(entity_embedding)
        
        if best_match and best_match.similarity > 0.85:
            # Add to existing cluster
            best_match.cluster.add_alias(entity_text, best_match.similarity)
            return best_match.cluster
        else:
            # Create new cluster
            return self._create_new_entity_cluster(entity_text, entity_embedding)
    
    def _find_best_semantic_match(self, embedding) -> Optional[EntityMatch]:
        """Find best matching entity cluster using cosine similarity"""
        best_similarity = 0.0
        best_cluster = None
        
        for cluster in self.entity_clusters.values():
            similarity = cosine_similarity([embedding], [cluster.embedding])[0][0]
            if similarity > best_similarity:
                best_similarity = similarity
                best_cluster = cluster
        
        if best_similarity > 0.75:  # Minimum threshold
            return EntityMatch(best_cluster, best_similarity)
        return None

class EntityCluster:
    def __init__(self, canonical_name: str, embedding: np.ndarray):
        self.canonical_name = canonical_name
        self.aliases = {canonical_name}
        self.embedding = embedding
        self.confidence_scores = {}
        
    def add_alias(self, alias: str, similarity: float):
        """Add alias with confidence tracking"""
        if similarity > 0.80:
            self.aliases.add(alias)
            self.confidence_scores[alias] = similarity
            
        # Update canonical name if better match found
        if similarity > self.confidence_scores.get(self.canonical_name, 0.0):
            self.canonical_name = alias
```

#### **Implementation Strategy**
1. **Semantic Embeddings**: Use Sentence-BERT for context-aware entity embeddings
2. **Entity Clustering**: Group semantically similar entities into clusters with aliases
3. **Context-Aware Resolution**: Include surrounding text context for disambiguation
4. **Performance Optimization**: LRU cache for embeddings, batch processing
5. **Confidence Tracking**: Track and update confidence scores for entity mappings

#### **Expected Performance Gains**
- **Entity Resolution Accuracy**: 60-70% → 85-95%
- **Alias Detection**: Handle abbreviations, variations, and semantic equivalents
- **Context Disambiguation**: Distinguish "Apple" (company) vs "Apple" (fruit)
- **Scalability**: Efficient similarity search using approximate nearest neighbors

---

### Phase 3: Neo4j Performance Optimization

#### **Problem Statement**
Neo4j queries become exponentially slower as graph size grows beyond 10K nodes due to lack of indexes, suboptimal query patterns, and poor schema design.

#### **Solution Architecture**

```python
# New Architecture: High-Performance Graph Operations
class OptimizedNeo4jManager:
    def __init__(self, driver):
        self.driver = driver
        self._create_essential_indexes()
        self._configure_performance_settings()
    
    def _create_essential_indexes(self):
        """Create indexes for common query patterns"""
        with self.driver.session() as session:
            indexes = [
                # Primary entity lookup
                "CREATE INDEX entity_name_idx IF NOT EXISTS FOR (e:Entity) ON (e.canonical_name)",
                "CREATE INDEX entity_type_idx IF NOT EXISTS FOR (e:Entity) ON (e.entity_type)",
                
                # Relationship lookups
                "CREATE INDEX rel_type_idx IF NOT EXISTS FOR ()-[r:RELATIONSHIP]-() ON (r.relationship_type)",
                
                # Composite indexes for complex queries
                "CREATE INDEX entity_type_confidence_idx IF NOT EXISTS FOR (e:Entity) ON (e.entity_type, e.confidence)",
                "CREATE INDEX pagerank_score_idx IF NOT EXISTS FOR (e:Entity) ON (e.pagerank_score)",
                
                # Full-text search
                "CREATE FULLTEXT INDEX entity_search_idx IF NOT EXISTS FOR (e:Entity) ON EACH [e.canonical_name, e.aliases]"
            ]
            
            for index_query in indexes:
                session.run(index_query)
    
    def bulk_create_entities(self, entities: List[Entity]) -> BulkResult:
        """Optimized bulk entity creation"""
        with self.driver.session() as session:
            # Batch insert using UNWIND for performance
            result = session.run("""
                UNWIND $entities AS entity
                CREATE (e:Entity {
                    canonical_name: entity.name,
                    entity_type: entity.type,
                    confidence: entity.confidence,
                    aliases: entity.aliases,
                    created_at: datetime()
                })
                RETURN count(e) as created_count
            """, entities=[{
                'name': e.canonical_name,
                'type': e.entity_type,
                'confidence': e.confidence,
                'aliases': list(e.aliases)
            } for e in entities])
            
            return BulkResult(result.single()['created_count'])
    
    def find_entities_paginated(self, entity_type: str, limit: int = 100, 
                               skip: int = 0, min_confidence: float = 0.5) -> List[Entity]:
        """Optimized entity search with pagination"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e:Entity {entity_type: $type})
                WHERE e.confidence >= $min_confidence
                RETURN e
                ORDER BY e.confidence DESC, e.canonical_name
                SKIP $skip LIMIT $limit
            """, type=entity_type, min_confidence=min_confidence, skip=skip, limit=limit)
            
            return [self._entity_from_record(record) for record in result]
    
    def execute_path_query_optimized(self, start_entity: str, end_entity: str, 
                                   max_hops: int = 3) -> List[Path]:
        """Optimized path finding with relationship type hints"""
        with self.driver.session() as session:
            # Use specific relationship types for better performance
            result = session.run("""
                MATCH path = (start:Entity {canonical_name: $start})-
                    [:WORKS_FOR|:LOCATED_IN|:OWNS*1..$max_hops]-
                    (end:Entity {canonical_name: $end})
                WHERE length(path) <= $max_hops
                RETURN path, length(path) as path_length
                ORDER BY path_length ASC
                LIMIT 10
            """, start=start_entity, end=end_entity, max_hops=max_hops)
            
            return [self._path_from_record(record) for record in result]
```

#### **Implementation Strategy**
1. **Strategic Indexing**: Create indexes for all common query patterns
2. **Batch Operations**: Use UNWIND for bulk inserts/updates (10-100x faster)
3. **Query Optimization**: Rewrite queries to use indexes effectively
4. **Schema Optimization**: Use specific relationship types instead of generic ones
5. **Performance Monitoring**: Profile queries and identify bottlenecks
6. **Configuration Tuning**: Optimize Neo4j memory and cache settings

#### **Expected Performance Gains**
- **Query Speed**: 10-100x faster queries on large graphs
- **Graph Size Limit**: 10K → 100K+ nodes with maintained performance
- **Bulk Operations**: 100x faster entity/relationship creation
- **Memory Efficiency**: Better memory utilization through proper indexing

---

## Implementation Roadmap

### **Phase 1: spaCy Optimization** (4-6 weeks)
- **Week 1-2**: Implement chunked processing pipeline
- **Week 3-4**: Add boundary entity merging logic
- **Week 5-6**: Performance testing and optimization

### **Phase 2: Semantic Resolution** (6-8 weeks)  
- **Week 1-2**: Integrate Sentence-BERT embeddings
- **Week 3-4**: Implement entity clustering system
- **Week 5-6**: Add context-aware disambiguation
- **Week 7-8**: Performance optimization and caching

### **Phase 3: Neo4j Optimization** (4-6 weeks)
- **Week 1-2**: Create indexes and optimize schema
- **Week 3-4**: Implement batch operations
- **Week 5-6**: Query optimization and performance monitoring

### **Integration Phase** (2-3 weeks)
- **Week 1**: End-to-end integration testing
- **Week 2**: Performance validation against targets
- **Week 3**: Documentation and deployment preparation

## Success Metrics

| **Metric** | **Current** | **Target** | **Phase** |
|------------|-------------|------------|-----------|
| Max Document Size | 100KB | 10MB+ | Phase 1 |
| Entity Resolution Accuracy | 60-70% | 85-95% | Phase 2 |
| Max Graph Size (performant) | 10K nodes | 100K+ nodes | Phase 3 |
| Query Response Time | Variable | <1s for 95% queries | Phase 3 |
| Concurrent Operations | 20 | 100+ | All Phases |
| Memory Usage (Large Docs) | 2GB+ peak | <1GB sustained | Phase 1 |

## Risks and Mitigations

### **Technical Risks**
1. **Embedding Model Performance**: SentenceBERT may be slow for real-time operations
   - **Mitigation**: Implement caching, batch processing, and consider lighter models
   
2. **Neo4j Index Overhead**: Many indexes may slow write operations
   - **Mitigation**: Profile write performance, optimize index selection
   
3. **Memory Usage**: Embedding caches may consume significant memory
   - **Mitigation**: Implement LRU caching, configurable memory limits

### **Integration Risks**
1. **Backward Compatibility**: Optimizations may break existing functionality
   - **Mitigation**: Comprehensive regression testing, feature flags
   
2. **Performance Regression**: Some optimizations may have edge cases
   - **Mitigation**: A/B testing, gradual rollout, monitoring

## Alternatives Considered

### **Alternative 1: Switch to Transformer-based NER**
- **Pros**: Higher accuracy, better domain adaptation
- **Cons**: Much slower, higher memory usage, more complex deployment
- **Decision**: Keep spaCy for speed, add semantic layer on top

### **Alternative 2: Use Graph Database Alternatives**
- **Pros**: Some alternatives may have better performance characteristics  
- **Cons**: Neo4j ecosystem is mature, switching cost is high
- **Decision**: Optimize Neo4j usage rather than switching

### **Alternative 3: Implement Custom Entity Resolution**
- **Pros**: Could be optimized for specific use case
- **Cons**: High development cost, maintenance burden
- **Decision**: Use proven embedding models with optimization layer

## Decision Rationale

This three-phase approach addresses the **specific breaking points identified through stress testing** while maintaining the **100% functional vertical slice** achieved. Each phase delivers independent value and can be implemented incrementally.

The solution maintains **architectural consistency** with the existing system while providing **clear performance boundaries** and **measurable success criteria**.

## References

- System Stress Test Results (2025-08-01)
- spaCy Performance Documentation
- Sentence-BERT Paper (Reimers & Gurevych, 2019)
- Neo4j Performance Tuning Guide
- KGAS Vertical Slice Validation Report

---

**Approved by:** System Architecture Team  
**Implementation Owner:** Performance Engineering Team  
**Review Date:** 2025-09-01 (Monthly review during implementation)