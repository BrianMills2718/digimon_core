# Attribute-Based Implementation Plan

## Preplanning for Attribute-Based Super-Digimon

### Phase 1: Foundation Refactoring (Week 1)

#### 1.1 Attribute Schema Definition
```python
# Core attribute schemas using Pydantic
class NodeAttributes(BaseModel):
    # Identity
    id: str
    entity_name: Optional[str]
    chunk_key: Optional[str]
    source_id: Optional[List[str]]  # Can link to multiple sources
    
    # Content
    original_content: Optional[str]
    text: Optional[str]
    embedding: Optional[List[float]]
    
    # Semantic
    entity_type: Optional[str]
    entity_description: Optional[str]
    keywords: Optional[List[str]]
    
    # Structural
    layer: Optional[int]
    community_id: Optional[str]
    importance_score: Optional[float]
    
    # Metadata
    confidence_score: Optional[float]
    timestamp: Optional[datetime]
    provenance: Optional[Dict[str, Any]]

class EdgeAttributes(BaseModel):
    # Identity
    id: str
    source: str
    target: str
    relation_name: Optional[str]
    
    # Semantic
    relation_description: Optional[str]
    relation_keywords: Optional[List[str]]
    relation_type: Optional[str]
    
    # Quantitative
    edge_weight: Optional[float]
    confidence_score: Optional[float]
    
    # Metadata
    evidence: Optional[List[str]]
    timestamp: Optional[datetime]
    provenance: Optional[Dict[str, Any]]
```

#### 1.2 Graph Capabilities Detection
```python
@dataclass
class GraphCapabilities:
    """What attributes and properties this graph has"""
    node_attributes: Set[str]
    edge_attributes: Set[str]
    graph_properties: Dict[str, Any]
    
    def has_node_attr(self, attr: str) -> bool:
        return attr in self.node_attributes
    
    def has_edge_attr(self, attr: str) -> bool:
        return attr in self.edge_attributes
```

### Phase 2: Operator Refactoring (Week 1-2)

#### 2.1 Operator Base Class
```python
class AttributeBasedOperator(BaseMCPTool):
    # Required attributes
    required_node_attrs: Set[str] = set()
    required_edge_attrs: Set[str] = set()
    required_graph_props: Dict[str, Any] = {}
    
    # Optional attributes that enhance functionality
    optional_node_attrs: Set[str] = set()
    optional_edge_attrs: Set[str] = set()
    
    # Benefits from optional attributes
    optional_benefits: Dict[str, str] = {}
    
    def validate_graph(self, graph_caps: GraphCapabilities) -> ValidationResult:
        """Check if graph has required attributes"""
        missing_node = self.required_node_attrs - graph_caps.node_attributes
        missing_edge = self.required_edge_attrs - graph_caps.edge_attributes
        
        if missing_node or missing_edge:
            return ValidationResult(
                valid=False,
                missing_node_attrs=missing_node,
                missing_edge_attrs=missing_edge,
                suggestions=self.suggest_enhancements(missing_node, missing_edge)
            )
        return ValidationResult(valid=True)
```

#### 2.2 Example Operator Refactoring
```python
@mcp_tool
class EntityVDBSearchTool(AttributeBasedOperator):
    """Vector search over graph nodes"""
    
    # Minimal requirements - just needs text to embed
    required_node_attrs = {"text"}  # or "original_content"
    
    # Optional enhancements
    optional_node_attrs = {"entity_type", "entity_description", "layer"}
    optional_benefits = {
        "entity_type": "Can filter results by type",
        "layer": "Can restrict search to specific hierarchy levels"
    }

@mcp_tool  
class ChunkOccurrenceTool(AttributeBasedOperator):
    """Find chunks where entities co-occur"""
    
    # Strict requirements
    required_node_attrs = {"entity_name", "source_id"}
    required_edge_attrs = set()  # Just needs edges to exist
    
    # Won't work without these attributes
    incompatible_if_missing = True
```

### Phase 3: Graph Builder Refactoring (Week 2)

#### 3.1 Flexible Graph Construction
```python
class AttributeBasedGraphBuilder:
    def build_graph(self,
                   documents: List[Document],
                   config: GraphBuildConfig) -> AttributeGraph:
        """
        Build graph with requested attributes
        
        config.attributes = {
            "nodes": ["entity_name", "entity_type", "source_id"],
            "edges": ["relation_name", "edge_weight"]
        }
        """
        
    def detect_buildable_attributes(self, 
                                  documents: List[Document]) -> Dict[str, List[str]]:
        """What attributes can we extract from these documents?"""
```

#### 3.2 Progressive Enhancement Tools
```python
@mcp_tool
class AddEntityTypes(AttributeBasedOperator):
    """Add entity_type attribute to existing graph"""
    
    required_node_attrs = {"entity_name"}
    adds_node_attrs = {"entity_type"}
    
@mcp_tool
class AddEdgeWeights(AttributeBasedOperator):
    """Calculate and add edge weights"""
    
    required_edge_attrs = {"source", "target"}
    optional_edge_attrs = {"relation_name"}  # Better weights with this
    adds_edge_attrs = {"edge_weight"}
```

### Phase 4: Orchestrator Enhancement (Week 2-3)

#### 4.1 Attribute-Aware Planning
```python
class AttributeAwareOrchestrator:
    def plan_analysis(self, 
                     query: str,
                     available_graphs: List[AttributeGraph]) -> Pipeline:
        """
        1. Determine required operators for query
        2. Check which graphs have required attributes
        3. Plan enhancement steps if needed
        4. Build optimal pipeline
        """
        
    def suggest_graph_enhancements(self,
                                  graph: AttributeGraph,
                                  target_operators: List[str]) -> List[Enhancement]:
        """What attributes to add for these operators?"""
```

#### 4.2 Dynamic Pipeline Adaptation
```python
class AdaptivePipeline:
    def execute_with_enhancement(self, 
                                graph: AttributeGraph,
                                operators: List[AttributeBasedOperator]):
        for op in operators:
            validation = op.validate_graph(graph.capabilities)
            
            if not validation.valid:
                # Enhance graph with missing attributes
                for enhancer in validation.suggestions:
                    graph = enhancer.enhance(graph)
                    
            # Now execute operator
            result = op.execute(graph)
```

### Phase 5: Meta-Graph Integration (Week 3)

#### 5.1 Attribute Lineage Tracking
```python
class AttributeLineage:
    """Track how each attribute was added"""
    
    attribute_name: str
    source_tool: str
    timestamp: datetime
    confidence: float
    provenance: Dict[str, Any]
```

#### 5.2 Cross-Structure Attribute Mapping
```python
class CrossStructureMapper:
    """Map attributes between different structures"""
    
    def map_graph_to_table_attrs(self, 
                                graph_attrs: Set[str]) -> Dict[str, str]:
        """
        entity_name -> row_id
        entity_type -> category_column
        edge_weight -> correlation_value
        """
```

## Critical Design Decisions

### 1. Attribute Storage
- **Option A**: Store as key-value pairs (flexible but less typed)
- **Option B**: Pydantic models with Optional fields (typed but fixed schema)
- **Recommendation**: Hybrid - Pydantic for known attributes, key-value for extensions

### 2. Backward Compatibility
- Create adapters that map old graph types to attribute sets
- `KG` → `{entity_name, source_id, relation_name}`
- `TKG` → `KG + {entity_type, entity_description, relation_description}`

### 3. Performance Considerations
- Index frequently accessed attributes
- Lazy loading for large attributes (original_content)
- Cache attribute detection results

### 4. User Experience
- Clear error messages: "ChunkOccurrence requires 'source_id' attribute"
- Helpful suggestions: "Use AddSourceTracking tool to add this attribute"
- Visual feedback showing available operators for current graph

## Implementation Priority

1. **Week 1**: Core attribute schemas and detection
2. **Week 1-2**: Refactor 5 key operators to attribute-based
3. **Week 2**: Graph builder with flexible attributes  
4. **Week 2-3**: Orchestrator with attribute awareness
5. **Week 3**: Enhancement tools and meta-graph tracking

## Success Metrics

1. Can build a graph with any valid combination of attributes
2. Operators correctly validate attribute requirements
3. Clear error messages and enhancement suggestions
4. Successful pipeline adaptation when attributes missing
5. Full lineage tracking of attribute additions

## Risks and Mitigations

1. **Risk**: Attribute explosion
   - **Mitigation**: Define core vs extended attributes

2. **Risk**: Performance overhead
   - **Mitigation**: Efficient attribute detection caching

3. **Risk**: User confusion
   - **Mitigation**: Good defaults and clear documentation

4. **Risk**: Breaking changes
   - **Mitigation**: Compatibility layer for existing code