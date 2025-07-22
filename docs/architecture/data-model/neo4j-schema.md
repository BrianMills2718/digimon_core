# Neo4j Data Model Specification

**Version**: 1.0
**Status**: Current Implementation
**Last Updated**: 2025-07-22

## Overview

This document provides the complete specification for the Neo4j graph database schema used in KGAS for storing entities and their relationships.

## Node Types

### Entity Node

The primary node type representing identified entities from documents.

```cypher
(Entity {
  // Identity
  entity_id: String!              // Unique identifier (format: "entity_<uuid>")
  canonical_name: String!         // Primary display name
  entity_type: String!            // Type from: PERSON, ORG, GPE, PRODUCT, EVENT, etc.
  
  // Quality Metrics  
  confidence: Float!              // Overall confidence score (0.0-1.0)
  pagerank_score: Float           // PageRank centrality score (0.0-1.0)
  mention_count: Integer          // Number of mentions found
  
  // Surface Forms
  surface_forms: [String]         // Alternative names/mentions
  
  // Metadata
  created_at: DateTime!           // ISO 8601 timestamp
  updated_at: DateTime            // Last modification timestamp
  tool_version: String            // Tool that created this entity
})
```

**Constraints**:
- `entity_id` is unique across all Entity nodes
- `confidence` must be between 0.0 and 1.0
- `entity_type` must be from allowed types list

**Indexes**:
- Unique constraint on `entity_id`
- Index on `entity_type` for type-based queries
- Index on `canonical_name` for name searches
- Index on `pagerank_score` for ranking queries

## Relationship Types

### RELATED_TO

The primary relationship type connecting entities.

```cypher
(Entity)-[RELATED_TO {
  // Identity
  relationship_id: String!        // Unique identifier
  relationship_type: String!      // Semantic type (e.g., "WORKS_FOR", "LOCATED_IN")
  
  // Quality Metrics
  weight: Float!                  // Relationship strength (0.1-1.0) 
  confidence: Float!              // Extraction confidence (0.0-1.0)
  
  // Evidence
  evidence_text: String           // Text snippet supporting this relationship
  extraction_method: String       // Method used: "pattern_based", "proximity_based", etc.
  pattern_confidence: Float       // Confidence in pattern match
  
  // Metadata
  created_at: DateTime!           // ISO 8601 timestamp
  tool_version: String            // Tool that created this relationship
}]->(Entity)
```

**Constraints**:
- `weight` must be between 0.1 and 1.0
- `confidence` must be between 0.0 and 1.0
- Source and target must be valid Entity nodes

## Example Data

### Entity Examples

```cypher
// Person Entity
{
  entity_id: "entity_123e4567-e89b-12d3-a456-426614174000",
  canonical_name: "John Smith",
  entity_type: "PERSON",
  confidence: 0.92,
  pagerank_score: 0.0045,
  mention_count: 5,
  surface_forms: ["John Smith", "J. Smith", "Smith, John"],
  created_at: "2025-07-22T10:30:00Z",
  tool_version: "T31_v1.0"
}

// Organization Entity  
{
  entity_id: "entity_987f6543-b21a-34c5-d678-123456789012",
  canonical_name: "Acme Corporation",
  entity_type: "ORG",
  confidence: 0.88,
  pagerank_score: 0.0123,
  mention_count: 12,
  surface_forms: ["Acme Corp", "Acme Corporation", "ACME"],
  created_at: "2025-07-22T10:31:00Z",
  tool_version: "T31_v1.0"
}
```

### Relationship Examples

```cypher
// Employment Relationship
{
  relationship_id: "rel_456a7890-123b-45c6-789d-012345678901",
  relationship_type: "WORKS_FOR",
  weight: 0.85,
  confidence: 0.9,
  evidence_text: "John Smith is the CEO of Acme Corporation",
  extraction_method: "pattern_based",
  pattern_confidence: 0.95,
  created_at: "2025-07-22T10:32:00Z",
  tool_version: "T34_v1.0"
}
```

## Common Queries

### Find Entity by ID
```cypher
MATCH (e:Entity {entity_id: $entity_id})
RETURN e
```

### Find Entities by Type
```cypher
MATCH (e:Entity {entity_type: $type})
RETURN e
ORDER BY e.pagerank_score DESC
LIMIT 100
```

### Find Related Entities
```cypher
MATCH (e1:Entity {entity_id: $entity_id})-[r:RELATED_TO]-(e2:Entity)
RETURN e1, r, e2
ORDER BY r.weight DESC
```

### Multi-hop Query
```cypher
MATCH path = (e1:Entity {canonical_name: $name1})-[*1..3]-(e2:Entity {canonical_name: $name2})
RETURN path
LIMIT 10
```

### PageRank Update
```cypher
MATCH (e:Entity)
SET e.pagerank_score = $scores[e.entity_id]
```

## Data Integrity Rules

1. **Entity Uniqueness**: No duplicate `entity_id` values
2. **Relationship Validity**: Both endpoints must exist
3. **Type Consistency**: Entity types from controlled vocabulary
4. **Confidence Bounds**: All confidence scores 0.0-1.0
5. **Required Fields**: All fields marked with `!` must be present

## Performance Considerations

### Current Scale
- Entities: ~1,000 per document
- Relationships: ~5,000 per document  
- Query response: < 100ms for single-hop

### Optimization Strategies
1. Use indexes for common query patterns
2. Batch operations for bulk updates
3. Limit multi-hop queries to 3 hops
4. Use weight threshold for path queries

## Migration and Evolution

### Schema Version
Current: 1.0

### Future Additions (Planned)
```cypher
// Version 2.0 Additions
(Entity {
  // ... existing fields ...
  
  // New fields
  embedding: [Float]              // Vector embedding
  cluster_id: String              // Community detection cluster
  temporal_relevance: Float       // Time-based importance
  source_documents: [String]      // Document references
})
```

### Backward Compatibility
- New fields will be optional
- Existing queries will continue to work
- Migration scripts will populate defaults

## Consistency with SQLite

### Entity ID Mapping
- Entity IDs in Neo4j match mention records in SQLite
- Ensures traceability back to source documents

### Transaction Boundaries  
- Entity creation is atomic within Neo4j
- Cross-store consistency not guaranteed (eventual consistency)

## Error Scenarios

### Common Issues
1. **Duplicate Entity**: Attempt to create entity with existing ID
2. **Orphan Relationship**: Creating relationship with non-existent entity
3. **Invalid Type**: Using entity type not in vocabulary
4. **Constraint Violation**: Confidence or weight out of bounds

### Error Handling
- Return specific error codes
- Log constraint violations
- No partial updates (all or nothing)