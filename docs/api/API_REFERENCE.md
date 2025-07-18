---
status: living
---

# KGAS API Reference

## /query Endpoint

The `/query` endpoint provides a unified interface for querying the KGAS knowledge graph using a JSON-based DSL or GraphQL.

### HTTP Endpoint
- **POST /query**
- **Content-Type**: application/json

### JSON DSL Grammar
```json
{
  "select": ["entity", "relationship"],
  "where": {
    "entity_type": "Person",
    "property": {"name": "Alice"}
  },
  "limit": 10,
  "order_by": "confidence",
  "desc": true
}
```
- **select**: List of result types ("entity", "relationship")
- **where**: Filter conditions (entity type, properties, relationship type, etc.)
- **limit**: Max results
- **order_by**: Field to sort by (e.g., "confidence")
- **desc**: Sort descending if true

### Example Query
```json
{
  "select": ["relationship"],
  "where": {
    "relationship_type": "IdentifiesWith",
    "confidence": {"$gte": 0.8}
  },
  "limit": 5
}
```

### GraphQL Support
- The API also supports GraphQL queries via Strawberry (see /graphql endpoint).
- Example:
```graphql
query {
  relationships(type: "IdentifiesWith", minConfidence: 0.8) {
    source { name }
    target { name }
    confidence
  }
}
```

### Response Format
```json
{
  "results": [
    {"entity_id": "123", "name": "Alice", ...},
    ...
  ],
  "count": 2
}
```

---
For authentication, error codes, and advanced usage, see SECURITY.md and ARCHITECTURE.md. 