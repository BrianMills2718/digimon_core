# Super-Digimon Operator Specifications

## Overview
This document specifies the attribute requirements for all 106 tools across 7 phases needed for Super-Digimon, with special focus on the 19 JayLZhou GraphRAG operators in Phase 4.

## Core Data Structure Attributes

### Graph Attributes
```python
# Base attributes all graphs have
base_graph_attrs = {
    'nodes',           # List of nodes
    'edges',           # List of edges  
    'node_ids',        # Unique identifiers
    'edge_source',     # Source node of edge
    'edge_target',     # Target node of edge
}

# Additional attributes by graph type
kg_attrs = base_graph_attrs | {
    'entity_name',     # Name of entity
    'relation_name',   # Name of relationship
}

tkg_attrs = kg_attrs | {
    'entity_type',     # Type classification
    'entity_desc',     # Detailed description
    'relation_desc',   # Relationship description
}

rkg_attrs = tkg_attrs | {
    'relation_keywords',  # Keywords for relationships
    'edge_weight',       # Importance scores
}

tree_attrs = base_graph_attrs | {
    'node_content',    # Original text content
    'node_summary',    # Summarized content
    'node_layer',      # Hierarchy level
}

passage_attrs = base_graph_attrs | {
    'passage_content', # Full passage text
    'passage_type',    # Document element type
}
```

### Table Attributes
```python
table_attrs = {
    'columns',         # Column names
    'rows',           # Row data
    'column_types',   # Data types per column
    'primary_key',    # Optional primary key
}
```

### Document Attributes
```python
document_attrs = {
    'content',        # Raw text
    'metadata',       # Title, author, date, etc.
    'sections',       # Document structure
}
```

## Operator Specifications

### 1. Pre-Processing Tools (T01-T05)

#### T01: Document Loader
```python
class DocumentLoader:
    requires = set()  # No prerequisites
    optional = {'file_path', 'url', 'format'}
    produces = {'content', 'metadata', 'sections'}
    output_type = 'Document'
```

#### T02: Text Chunker
```python
class TextChunker:
    requires = {'content'}
    optional = {'chunk_size', 'overlap', 'strategy'}
    produces = {'chunks', 'chunk_metadata'}
    output_type = 'List[Document]'
```

#### T03: Entity Extractor
```python
class EntityExtractor:
    requires = {'content'}
    optional = {'model', 'entity_types', 'confidence_threshold'}
    produces = {'entities', 'entity_positions'}
    output_type = 'List[Entity]'
```

#### T04: Relationship Extractor
```python
class RelationshipExtractor:
    requires = {'content', 'entities'}
    optional = {'model', 'relation_types'}
    produces = {'relationships', 'confidence_scores'}
    output_type = 'List[Relationship]'
```

#### T05: Graph Builder
```python
class GraphBuilder:
    requires = {'entities', 'relationships'}
    optional = {'graph_type', 'deduplication'}
    produces = base_graph_attrs | {'graph_type'}
    output_type = 'Graph'
```

### 2. Entity Operators (T06-T12)

#### T06: Entity VDB Search
```python
class EntityVDBSearch:
    requires = {'node_embeddings', 'query_text'}
    optional = {'top_k', 'threshold'}
    produces = {'matched_nodes', 'similarity_scores'}
    works_with = ['KG', 'TKG', 'RKG']
```

#### T07: Entity RelNode
```python
class EntityRelNode:
    requires = {'edges', 'edge_source', 'edge_target', 'selected_relations'}
    optional = {'direction'}
    produces = {'selected_nodes'}
    works_with = ['KG', 'TKG', 'RKG']
```

#### T08: Entity PPR (Personalized PageRank)
```python
class EntityPPR:
    requires = {'nodes', 'edges', 'edge_source', 'edge_target', 'seed_nodes'}
    optional = {'alpha', 'max_iter'}
    produces = {'node_scores', 'ranked_nodes'}
    works_with = ['All graph types']
```

#### T09: Entity Agent
```python
class EntityAgent:
    requires = {'nodes', 'query_text'}
    optional = {'llm_model', 'prompt_template'}
    produces = {'selected_nodes', 'reasoning'}
    works_with = ['All graph types']
```

#### T10: Entity OneHop
```python
class EntityOneHop:
    requires = {'nodes', 'edges', 'seed_nodes'}
    optional = {'direction', 'edge_types'}
    produces = {'neighbor_nodes'}
    works_with = ['All graph types']
```

#### T11: Entity Link
```python
class EntityLink:
    requires = {'node_embeddings', 'source_nodes'}
    optional = {'similarity_threshold'}
    produces = {'linked_nodes', 'link_scores'}
    works_with = ['KG', 'TKG', 'RKG']
```

#### T12: Entity TFIDF
```python
class EntityTFIDF:
    requires = {'node_content', 'query_text'}
    optional = {'vocab', 'idf_weights'}
    produces = {'ranked_nodes', 'tfidf_scores'}
    works_with = ['Tree', 'Passage']
```

### 3. Relationship Operators (T13-T16)

#### T13: Relationship VDB Search
```python
class RelationshipVDBSearch:
    requires = {'edge_embeddings', 'query_text'}
    optional = {'top_k', 'threshold'}
    produces = {'matched_edges', 'similarity_scores'}
    works_with = ['RKG']
```

#### T14: Relationship OneHop
```python
class RelationshipOneHop:
    requires = {'edges', 'selected_nodes'}
    optional = {'edge_types', 'direction'}
    produces = {'connected_edges'}
    works_with = ['All graph types']
```

#### T15: Relationship Aggregator
```python
class RelationshipAggregator:
    requires = {'edges', 'node_scores'}
    optional = {'aggregation_method'}
    produces = {'edge_scores', 'ranked_edges'}
    works_with = ['All graph types']
```

#### T16: Relationship Agent
```python
class RelationshipAgent:
    requires = {'edges', 'query_text'}
    optional = {'llm_model', 'context'}
    produces = {'selected_edges', 'reasoning'}
    works_with = ['TKG', 'RKG']
```

### 4. Chunk Operators (T17-T19)

#### T17: Chunk Aggregator
```python
class ChunkAggregator:
    requires = {'chunks', 'edge_scores', 'chunk_edge_mapping'}
    optional = {'aggregation_method', 'top_k'}
    produces = {'ranked_chunks', 'chunk_scores'}
    works_with = ['All graph types']
```

#### T18: Chunk FromRel
```python
class ChunkFromRel:
    requires = {'chunks', 'selected_edges', 'chunk_edge_mapping'}
    optional = set()
    produces = {'selected_chunks'}
    works_with = ['All graph types']
```

#### T19: Chunk Occurrence
```python
class ChunkOccurrence:
    requires = {'chunks', 'entity_pairs', 'chunk_entity_mapping'}
    optional = {'min_occurrence'}
    produces = {'ranked_chunks', 'occurrence_counts'}
    works_with = ['KG', 'TKG', 'RKG']
```

### 5. Subgraph Operators (T20-T22)

#### T20: Subgraph KHopPath
```python
class SubgraphKHopPath:
    requires = {'nodes', 'edges', 'start_nodes', 'end_nodes'}
    optional = {'k', 'path_limit'}
    produces = {'paths', 'path_nodes', 'path_edges'}
    works_with = ['All graph types']
```

#### T21: Subgraph Steiner
```python
class SubgraphSteiner:
    requires = {'nodes', 'edges', 'terminal_nodes'}
    optional = {'edge_weights'}
    produces = {'steiner_tree', 'tree_nodes', 'tree_edges'}
    works_with = ['All graph types']
```

#### T22: Subgraph AgentPath
```python
class SubgraphAgentPath:
    requires = {'paths', 'query_text'}
    optional = {'llm_model', 'max_paths'}
    produces = {'selected_paths', 'path_relevance'}
    works_with = ['All graph types']
```

### 6. Community Operators (T23-T24)

#### T23: Community Entity
```python
class CommunityEntity:
    requires = {'communities', 'selected_nodes'}
    optional = set()
    produces = {'selected_communities'}
    works_with = ['All graph types']
```

#### T24: Community Layer
```python
class CommunityLayer:
    requires = {'hierarchical_communities', 'layer_threshold'}
    optional = {'aggregation_level'}
    produces = {'layer_communities', 'community_summaries'}
    works_with = ['All graph types']
```

### 7. Post-Processing Tools (T25-T26)

#### T25: Result Synthesizer
```python
class ResultSynthesizer:
    requires = {'retrieved_content', 'query_text'}
    optional = {'synthesis_method', 'max_length'}
    produces = {'synthesized_answer', 'source_references'}
    output_type = 'Document'
```

#### T26: Visualizer
```python
class Visualizer:
    requires = {'graph_data'}
    optional = {'layout', 'style', 'focus_nodes'}
    produces = {'visualization', 'interactive_graph'}
    output_type = 'Visualization'
```

## Additional Infrastructure Tools

### Vector Database Builders
```python
class EntityVDBBuilder:
    requires = {'nodes', 'node_content'}
    produces = {'node_embeddings', 'vector_index'}

class RelationshipVDBBuilder:
    requires = {'edges', 'edge_descriptions'}
    produces = {'edge_embeddings', 'vector_index'}

class ChunkVDBBuilder:
    requires = {'chunks'}
    produces = {'chunk_embeddings', 'vector_index'}
```

### Graph Type Builders
```python
class ERGraphBuilder:
    requires = {'entities', 'relationships'}
    produces = kg_attrs

class RKGraphBuilder:
    requires = {'entities', 'relationships', 'keywords'}
    produces = rkg_attrs

class TreeGraphBuilder:
    requires = {'chunks', 'summaries'}
    produces = tree_attrs

class PassageGraphBuilder:
    requires = {'passages', 'connections'}
    produces = passage_attrs
```

## Operator Composition Patterns

### Example: HippoRAG
```python
pipeline = "entity_extractor | relationship_extractor | graph_builder(type='kg') | entity_vdb_builder | chunk_aggregator"
```

### Example: LightRAG
```python
pipeline = "rk_graph_builder | entity_vdb_builder | relationship_vdb_builder | entity_relnode | chunk_fromrel"
```

### Example: RAPTOR
```python
pipeline = "text_chunker | tree_graph_builder | entity_vdb_search | result_synthesizer"
```

## Compatibility Matrix Summary

| Operator Type | KG | TKG | RKG | Tree | Passage |
|--------------|----|----|-----|------|---------|
| Entity VDB | ✓ | ✓ | ✓ | ✗ | ✗ |
| Entity PPR | ✓ | ✓ | ✓ | ✓ | ✓ |
| Entity TFIDF | ✗ | ✗ | ✗ | ✓ | ✓ |
| Relationship VDB | ✗ | ✗ | ✓ | ✗ | ✗ |
| All Subgraph Ops | ✓ | ✓ | ✓ | ✓ | ✓ |

## Notes

1. **Embeddings**: VDB operations require pre-computed embeddings
2. **Graph Types**: Some operators only work with specific graph types
3. **LLM Dependencies**: Agent operators require LLM access
4. **Composability**: Operators can be chained if output/input attributes match