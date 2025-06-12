# Graph Attributes Specification for Super-Digimon

## Overview

This document defines all possible graph attributes that can be composed to create flexible graph structures. Rather than fixed graph types (KG, TKG, RKG, etc.), Super-Digimon uses a composable attribute system.

## Core Principle

**Graph Types are Composites of Attributes**, just as Methods are Composites of Operators.

Traditional approach:
- KG = Fixed set of attributes
- TKG = KG + more attributes
- RKG = TKG + even more attributes

Super-Digimon approach:
- Any combination of attributes is valid
- Operators declare required/optional attributes
- Graphs can be progressively enhanced

## Node Attributes

### Content Attributes
- **original_content**: Full text of the chunk/passage
- **text**: Processed/summarized text content
- **embedding**: Vector representation

### Identity Attributes
- **id**: Unique identifier
- **entity_name**: Human-readable name
- **chunk_key**: Reference to source chunk
- **source_id**: Link to origin document(s)

### Semantic Attributes
- **entity_type**: Category (Person, Organization, etc.)
- **entity_description**: Detailed description
- **keywords**: Associated keywords
- **confidence_score**: Extraction confidence

### Structural Attributes
- **layer**: Hierarchical level (for trees)
- **community_id**: Community membership
- **position**: Spatial/temporal position
- **importance_score**: Node importance metrics

### Metadata Attributes
- **timestamp**: Creation/modification time
- **provenance**: How this node was created
- **version**: Version number
- **annotations**: User/system annotations

## Edge Attributes

### Identity Attributes
- **id**: Unique edge identifier
- **relation_name**: Relationship type/predicate
- **source**: Source node ID
- **target**: Target node ID

### Semantic Attributes
- **relation_description**: Detailed description
- **relation_keywords**: Associated keywords
- **relation_type**: Category of relationship
- **confidence_score**: Relationship confidence

### Quantitative Attributes
- **edge_weight**: Numerical weight
- **strength**: Relationship strength
- **frequency**: Occurrence count
- **probability**: Probabilistic weight

### Metadata Attributes
- **timestamp**: When relationship established
- **provenance**: How edge was created
- **evidence**: Supporting evidence
- **annotations**: Additional metadata

## Graph-Level Attributes

### Structural Properties
- **is_directed**: Directed vs undirected
- **is_hierarchical**: Tree-like structure
- **allows_multi_edges**: Multiple edges between nodes
- **is_dynamic**: Temporal evolution support

### Semantic Properties
- **domain**: Domain ontology used
- **language**: Natural language
- **schema_version**: Attribute schema version

## Attribute Combinations (Examples)

### Traditional "Graph Types" as Attribute Sets

**Chunk Tree**:
```yaml
nodes:
  required: [id, original_content, layer]
  optional: [text, embedding]
edges:
  required: [source, target]
  optional: []
properties:
  is_hierarchical: true
  is_directed: true
```

**Knowledge Graph (KG)**:
```yaml
nodes:
  required: [entity_name, source_id]
  optional: [confidence_score]
edges:
  required: [relation_name, source, target]
  optional: [edge_weight]
properties:
  is_directed: true
```

**Textual Knowledge Graph (TKG)**:
```yaml
nodes:
  required: [entity_name, entity_type, entity_description, source_id]
  optional: [keywords, embedding]
edges:
  required: [relation_name, relation_description, source, target]
  optional: [edge_weight, confidence_score]
properties:
  is_directed: true
```

### Novel Combinations

**Passage Graph with Entity Extraction**:
```yaml
nodes:
  required: [chunk_key, original_content, entity_name, entity_type]
  optional: [entity_description, embedding]
edges:
  required: [source, target, relation_name]
  optional: [shared_entities, edge_weight]
```

**Hierarchical Knowledge Graph**:
```yaml
nodes:
  required: [entity_name, entity_type, layer, source_id]
  optional: [community_id, importance_score]
edges:
  required: [relation_name, source, target]
  optional: [edge_weight, relation_type]
properties:
  is_hierarchical: true
```

## Attribute Detection

Tools to detect current graph attributes:

```python
@mcp_tool
class GraphAttributeDetector:
    def detect_node_attributes(graph: Graph) -> Set[str]
    def detect_edge_attributes(graph: Graph) -> Set[str]
    def detect_graph_properties(graph: Graph) -> Dict[str, Any]
```

## Attribute Enhancement

Tools to add attributes to existing graphs:

```python
@mcp_tool
class AttributeEnhancer:
    def add_entity_types(graph: Graph) -> Graph
    def add_edge_weights(graph: Graph) -> Graph
    def add_source_tracking(graph: Graph) -> Graph
    def add_confidence_scores(graph: Graph) -> Graph
```

## Operator-Attribute Mapping

Instead of "compatible_graphs", operators declare:

```python
class OperatorRequirements:
    required_node_attributes: Set[str]
    optional_node_attributes: Set[str]
    required_edge_attributes: Set[str]
    optional_edge_attributes: Set[str]
    required_graph_properties: Dict[str, Any]
```

## Benefits

1. **Flexibility**: Create any combination of attributes
2. **Extensibility**: Add new attributes without changing types
3. **Clarity**: Explicit about what each operator needs
4. **Progressive Enhancement**: Start simple, add as needed
5. **Reusability**: Same graph can support different analyses

## Implementation Notes

1. Use Pydantic models for attribute validation
2. Store attributes in flexible key-value structures
3. Track attribute lineage in meta-graph
4. Provide clear error messages for missing attributes
5. Suggest enhancement tools when attributes are missing