---
status: living
---

# Neo4j Browser Guide

## Getting Started

1. Go to http://localhost:7474
2. Login with:
   - Username: `neo4j`
   - Password: `password`

## Basic Queries to Try

### 1. See Everything in Your Graph
```cypher
MATCH (n) 
RETURN n 
LIMIT 50
```
This shows up to 50 nodes (entities) in your graph.

### 2. See All Relationships
```cypher
MATCH (n)-[r]->(m) 
RETURN n, r, m 
LIMIT 50
```
This shows entities and how they're connected.

### 3. Find Specific Entities
```cypher
// Find all people
MATCH (p:Entity:PERSON) 
RETURN p.canonical_name as Name, p.pagerank_score as Importance

// Find all organizations
MATCH (o:Entity:ORG) 
RETURN o.canonical_name as Organization

// Find a specific person
MATCH (p:Entity) 
WHERE p.canonical_name CONTAINS "Elon Musk"
RETURN p
```

### 4. Find Relationships
```cypher
// Who founded what?
MATCH (founder)-[r:CREATED]->(company)
RETURN founder.canonical_name as Founder, company.canonical_name as Company

// Who works where?
MATCH (person)-[r:WORKS_FOR]->(org)
RETURN person.canonical_name as Person, org.canonical_name as Organization

// Everything about Elon Musk
MATCH (elon:Entity {canonical_name: "Elon Musk"})-[r]-(connected)
RETURN elon, r, connected
```

### 5. Find Important Entities (PageRank)
```cypher
MATCH (e:Entity)
WHERE e.pagerank_score IS NOT NULL
RETURN e.canonical_name as Entity, e.entity_type as Type, e.pagerank_score as Importance
ORDER BY e.pagerank_score DESC
LIMIT 10
```

## Understanding the Visualization

- **Circles (Nodes)** = Entities (people, organizations, places, etc.)
- **Lines (Edges)** = Relationships between entities
- **Colors** = Different entity types
- **Size** = Can represent importance (PageRank score)

## Interactive Features

1. **Click on a node** to see its properties
2. **Double-click a node** to expand its connections
3. **Drag nodes** to rearrange the visualization
4. **Zoom** with mouse wheel
5. **Click relationship lines** to see relationship type

## Useful Queries for Your Data

### See What's in Your Graph
```cypher
// Count entities by type
MATCH (e:Entity)
RETURN e.entity_type as Type, COUNT(e) as Count
ORDER BY Count DESC

// Count relationships by type
MATCH ()-[r]->()
RETURN type(r) as RelationshipType, COUNT(r) as Count
ORDER BY Count DESC
```

### Explore Connections
```cypher
// Find shortest path between two entities
MATCH path = shortestPath(
  (a:Entity {canonical_name: "Tesla"})-[*]-(b:Entity {canonical_name: "Apple"})
)
RETURN path

// Find all entities within 2 hops of Tesla
MATCH (tesla:Entity {canonical_name: "Tesla"})-[*1..2]-(connected)
RETURN DISTINCT tesla, connected
```

### Advanced Visualization
```cypher
// Show top 20 entities with all their relationships
MATCH (e:Entity)
WHERE e.pagerank_score IS NOT NULL
WITH e
ORDER BY e.pagerank_score DESC
LIMIT 20
MATCH (e)-[r]-(connected)
RETURN e, r, connected
```

## Tips

1. **Start simple** - Use LIMIT to avoid overwhelming visualizations
2. **Use RETURN to control** what you see (just names vs full graph)
3. **Click "Export" button** to save visualizations as images
4. **Use the sidebar** to filter by labels (entity types)
5. **Shift+Enter** runs the query (or click the play button)

## Common Issues

- **No results?** Your graph might be empty. Process a PDF first:
  ```bash
  python cli_tool.py process test_document.pdf "What is this about?"
  ```

- **Too many results?** Add `LIMIT 10` or `LIMIT 50` to your query

- **Can't see relationships?** Make sure to RETURN both nodes and relationships:
  ```cypher
  MATCH (n)-[r]->(m) RETURN n, r, m
  ```