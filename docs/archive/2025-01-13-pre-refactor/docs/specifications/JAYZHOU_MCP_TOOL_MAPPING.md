# GraphRAG Core Tools → MCP Tool Specifications

## Overview

This document maps the JayLZhou GraphRAG operators within Super-Digimon's 106-tool system. This includes:
- 19 retrieval operators from the JayLZhou GraphRAG paper (Phase 4 core operators)
- Additional infrastructure and transformation tools across other phases

**Note**: These 19 operators form the core of Phase 4 (T49-T67) within the complete 106-tool system.

## Entity Operators (7 Tools)

### 1. entity_vdb_search
**Description**: Select top-k entities from vector database based on similarity
**Parameters**:
- `query`: string - Search query
- `top_k`: integer (default: 10) - Number of results
- `threshold`: float (optional) - Similarity threshold
**Returns**: List of entities with scores
**Example Methods**: G-retriever, RAPTOR, KGP

### 2. entity_relnode_extract
**Description**: Extract entities from given relationships
**Parameters**:
- `relationships`: List[string] - Relationship IDs
- `direction`: enum["source", "target", "both"] (default: "both")
**Returns**: List of unique entities
**Example Methods**: LightRAG

### 3. entity_ppr_rank
**Description**: Run Personalized PageRank on graph, return top-k entities
**Parameters**:
- `seed_entities`: List[string] - Starting entities
- `damping_factor`: float (default: 0.85)
- `top_k`: integer (default: 10)
- `max_iterations`: integer (default: 100)
**Returns**: List of entities with PPR scores
**Example Methods**: FastGraphRAG

### 4. entity_agent_find
**Description**: Use LLM to identify relevant entities
**Parameters**:
- `query`: string - User query
- `context`: string - Graph context
- `max_entities`: integer (default: 10)
**Returns**: List of entities with reasoning
**Example Methods**: ToG

### 5. entity_onehop_neighbors
**Description**: Get one-hop neighbor entities
**Parameters**:
- `entities`: List[string] - Source entities
- `edge_types`: List[string] (optional) - Filter by edge types
- `direction`: enum["in", "out", "both"] (default: "both")
**Returns**: List of neighbor entities
**Example Methods**: LightRAG

### 6. entity_similarity_link
**Description**: Find most similar entity for each input
**Parameters**:
- `entities`: List[string] - Source entities
- `similarity_metric`: enum["embedding", "structural", "semantic"]
- `top_k`: integer (default: 1)
**Returns**: List of entity pairs with similarity scores
**Example Methods**: HippoRAG

### 7. entity_tfidf_rank
**Description**: Rank entities using TF-IDF matrix
**Parameters**:
- `query`: string - Search query
- `top_k`: integer (default: 10)
- `doc_frequency_threshold`: float (optional)
**Returns**: List of entities with TF-IDF scores
**Example Methods**: KGP

## Relationship Operators (4 Tools)

### 8. relationship_vdb_search
**Description**: Retrieve relationships by vector similarity
**Parameters**:
- `query`: string - Search query
- `top_k`: integer (default: 10)
- `relationship_types`: List[string] (optional)
**Returns**: List of relationships with scores
**Example Methods**: LightRAG, G-retriever

### 9. relationship_onehop_extract
**Description**: Get relationships connected to entities
**Parameters**:
- `entities`: List[string] - Source entities
- `hop_distance`: integer (default: 1)
- `relationship_types`: List[string] (optional)
**Returns**: List of relationships
**Example Methods**: MS GraphRAG Local Search

### 10. relationship_score_aggregate
**Description**: Score relationships based on entity importance
**Parameters**:
- `entity_scores`: Dict[string, float] - Entity PPR/importance scores
- `score_method`: enum["sum", "product", "max"]
- `top_k`: integer (default: 10)
**Returns**: List of relationships with aggregated scores
**Example Methods**: FastGraphRAG

### 11. relationship_agent_find
**Description**: Use LLM to identify relevant relationships
**Parameters**:
- `query`: string - User query
- `entity_context`: List[string] - Related entities
- `max_relationships`: integer (default: 10)
**Returns**: List of relationships with reasoning
**Example Methods**: ToG

## Chunk Operators (3 Tools)

### 12. chunk_score_aggregate
**Description**: Select chunks based on relationship scores
**Parameters**:
- `relationship_scores`: Dict[string, float]
- `chunk_relationship_map`: Dict - Chunk-relationship associations
- `top_k`: integer (default: 10)
- `aggregation`: enum["sum", "max", "weighted"]
**Returns**: List of chunks with scores
**Example Methods**: HippoRAG

### 13. chunk_from_relationships
**Description**: Get chunks containing specific relationships
**Parameters**:
- `relationships`: List[string] - Target relationships
- `include_context`: boolean (default: true) - Include surrounding text
**Returns**: List of chunks
**Example Methods**: LightRAG

### 14. chunk_entity_occurrence
**Description**: Rank chunks by entity co-occurrence
**Parameters**:
- `entities`: List[string] - Target entities
- `min_entities`: integer (default: 2) - Minimum entities per chunk
- `top_k`: integer (default: 10)
**Returns**: List of chunks with occurrence counts
**Example Methods**: MS GraphRAG Local Search

## Subgraph Operators (3 Tools)

### 15. subgraph_khop_paths
**Description**: Find k-hop paths between entities
**Parameters**:
- `start_entities`: List[string]
- `end_entities`: List[string] (optional)
- `k`: integer - Number of hops
- `max_paths`: integer (default: 10)
**Returns**: List of paths with nodes and edges
**Example Methods**: DALK

### 16. subgraph_steiner_tree
**Description**: Compute minimum spanning tree connecting entities
**Parameters**:
- `terminal_entities`: List[string] - Must-include entities
- `weight_attribute`: string (optional) - Edge weight property
**Returns**: Subgraph structure
**Example Methods**: G-retriever

### 17. subgraph_agent_filter
**Description**: Use LLM to filter relevant paths
**Parameters**:
- `paths`: List[Dict] - Candidate paths
- `query`: string - User query
- `max_paths`: integer (default: 5)
**Returns**: List of filtered paths with relevance scores
**Example Methods**: ToG

## Community Operators (2 Tools)

### 18. community_by_entities
**Description**: Find communities containing specific entities
**Parameters**:
- `entities`: List[string] - Target entities
- `community_level`: integer (optional) - Hierarchical level
**Returns**: List of communities with summaries
**Example Methods**: MS GraphRAG Local Search

### 19. community_by_layer
**Description**: Get all communities at/below specified layer
**Parameters**:
- `max_layer`: integer - Maximum hierarchical level
- `min_size`: integer (optional) - Minimum community size
**Returns**: List of communities with metadata
**Example Methods**: MS GraphRAG Global Search

## Additional Super-Digimon Tools

### Structure Transformation Tools

### 20. transform_graph_to_table
**Description**: Convert graph data to tabular format
**Parameters**:
- `subgraph`: Dict - Graph structure
- `node_attributes`: List[string] - Attributes to include
- `edge_as_columns`: boolean - Include edges as columns
- `output_format`: enum["dataframe", "csv", "json"]
**Returns**: Structured table data

### 21. transform_table_to_graph
**Description**: Create graph from tabular data
**Parameters**:
- `table_data`: Dict - Input table
- `entity_columns`: List[string] - Columns containing entities
- `relationship_rules`: Dict - How to infer relationships
**Returns**: Graph structure

### 22. transform_document_to_structures
**Description**: Extract multiple structures from documents
**Parameters**:
- `documents`: List[string] - Input documents
- `target_structures`: List[enum["graph", "table", "timeline"]]
- `extraction_config`: Dict - Structure-specific settings
**Returns**: Dict of extracted structures

### Analysis Preparation Tools

### 23. prepare_statistical_analysis
**Description**: Format data for statistical packages
**Parameters**:
- `data`: Dict - Input data (graph/table)
- `analysis_type`: enum["regression", "sem", "descriptive"]
- `variable_mapping`: Dict - Variable specifications
- `output_format`: enum["r", "python", "stata", "spss"]
**Returns**: Analysis-ready dataset

### 24. prepare_causal_model
**Description**: Structure data for causal analysis
**Parameters**:
- `entities`: List[Dict] - Nodes with attributes
- `relationships`: List[Dict] - Causal edges
- `model_type`: enum["dag", "bayesian", "do_calculus"]
**Returns**: Causal model structure

### 25. prepare_argument_network
**Description**: Build argumentation framework
**Parameters**:
- `claims`: List[Dict] - Argument nodes
- `relations`: List[Dict] - Attack/support edges
- `framework`: enum["dung", "bipolar", "weighted"]
**Returns**: Argument network structure

### 26. prepare_process_trace
**Description**: Create temporal event sequences
**Parameters**:
- `events`: List[Dict] - Event data
- `entities`: List[string] - Actors/entities
- `temporal_resolution`: enum["seconds", "minutes", "hours", "days"]
**Returns**: Process trace structure

## Tool Composition Examples

### HippoRAG Method
```yaml
pipeline:
  - entity_vdb_search: {top_k: 20}
  - entity_similarity_link: {top_k: 1}
  - chunk_score_aggregate: {top_k: 10}
```

### FastGraphRAG Method
```yaml
pipeline:
  - entity_ppr_rank: {top_k: 15}
  - relationship_score_aggregate: {score_method: "sum"}
  - chunk_score_aggregate: {aggregation: "weighted"}
```

### LightRAG Method
```yaml
pipeline:
  - entity_relnode_extract: {direction: "both"}
  - relationship_vdb_search: {top_k: 10}
  - chunk_from_relationships: {include_context: true}
```

## MCP Tool Interface Standard

All tools follow this Pydantic base model:

```python
class MCPToolInput(BaseModel):
    """Base model for all MCP tool inputs"""
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    context: Optional[Dict[str, Any]] = None

class MCPToolOutput(BaseModel):
    """Base model for all MCP tool outputs"""
    request_id: str
    success: bool
    data: Any
    metadata: Dict[str, Any]
    execution_time_ms: float
    reasoning_trace: Optional[str] = None
```

This mapping provides a complete specification for implementing all JayLZhou GraphRAG operators as granular MCP tools, plus additional tools needed for the Super-Digimon vision.