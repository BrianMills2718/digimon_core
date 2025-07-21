# Phase 3 Tools - CLAUDE.md

## Overview
The `src/tools/phase3/` directory contains **multi-document knowledge fusion** tools that consolidate knowledge across document collections with conflict resolution. These tools implement the most advanced phase of the GraphRAG system, focusing on cross-document knowledge integration and consistency.

## Phase 3 Multi-Document Fusion Workflow

### Fusion Path: Multi-Document → Knowledge Fusion → Unified Graph
The Phase 3 workflow implements advanced multi-document processing:
1. **Document Processing**: Process multiple documents using Phase 1/2 workflows
2. **Entity Clustering**: Find clusters of similar entities across documents
3. **Conflict Resolution**: Resolve conflicts between conflicting information
4. **Knowledge Fusion**: Merge knowledge from multiple sources
5. **Consistency Checking**: Ensure temporal and logical consistency
6. **Unified Graph**: Create a unified knowledge graph from all sources

### Workflow Orchestration
- **MultiDocumentFusion**: Advanced fusion with LLM-based conflict resolution
- **BasicMultiDocumentWorkflow**: Basic implementation with 100% reliability focus
- **PipelineOrchestrator**: Integration with unified orchestrator

## Tool Architecture Patterns

### Consolidation Pattern
Phase 3 tools consolidate functionality from multiple sources:
```python
"""
CONSOLIDATED TOOL CLASSES (Priority 2 Consolidation)
These classes consolidate functionality from:
- t301_fusion_tools.py 
- t301_multi_document_fusion_tools.py
- t301_mcp_tools.py
"""
```

### Fail-Fast Architecture Pattern
Phase 3 tools implement fail-fast error handling:
```python
# Custom exceptions for fail-fast architecture
class EntityConflictResolutionError(Exception):
    """Exception raised when LLM conflict resolution fails."""
    pass

class TemporalConsistencyError(Exception):
    """Exception raised when temporal consistency calculation fails."""
    pass

class AccuracyMeasurementError(Exception):
    """Exception raised when accuracy measurement fails."""
    pass
```

### 100% Reliability Pattern
Phase 3 tools ensure 100% reliability with graceful error handling:
```python
def execute(self, request: ProcessingRequest) -> PhaseResult:
    """Execute multi-document processing with 100% reliability"""
    try:
        # Processing logic
        return self.create_success_result(...)
    except Exception as e:
        # 100% reliability - always return a result
        error_trace = traceback.format_exc()
        self.logger.error("❌ Phase 3 Exception: %s", str(e), exc_info=True)
        return self.create_error_result(
            f"Phase 3 processing error: {str(e)}\nTraceback: {error_trace}",
            execution_time=0.0
        )
```

## Individual Tool Patterns

### T301: Multi-Document Fusion (`t301_multi_document_fusion.py`)
**Purpose**: Consolidate knowledge across document collections with conflict resolution

**Key Patterns**:
- **Entity Similarity Calculation**: Multiple methods for entity similarity
- **Entity Clustering**: Find clusters of similar entities
- **Conflict Resolution**: Resolve conflicts using multiple strategies
- **LLM Integration**: Use LLMs for complex conflict resolution
- **Consistency Checking**: Ensure temporal and logical consistency

**Usage**:
```python
from src.tools.phase3.t301_multi_document_fusion import MultiDocumentFusion

fusion = MultiDocumentFusion(
    confidence_threshold=0.8,
    similarity_threshold=0.85,
    conflict_resolution_model="gpt-4"
)
result = fusion.fuse_documents(document_refs, fusion_strategy="evidence_based")
```

**Core Components**:

#### EntitySimilarityCalculator
```python
calculator = EntitySimilarityCalculator()
similarity = calculator.calculate(
    entity1_name="Apple Inc",
    entity2_name="Apple",
    entity1_type="ORG",
    entity2_type="ORG",
    use_embeddings=True,
    use_string_matching=True
)
```

**Similarity Methods**:
- **Exact Match**: Perfect string matches
- **Substring Match**: One entity name contains the other
- **Word Overlap**: Common words between entity names
- **Embedding Similarity**: Semantic similarity using embeddings

#### EntityClusterFinder
```python
finder = EntityClusterFinder()
clusters = finder.find_clusters(
    entities=entity_list,
    similarity_threshold=0.8,
    max_cluster_size=50
)
```

**Clustering Features**:
- **Similarity-Based Clustering**: Group entities by similarity
- **Size Limits**: Prevent oversized clusters
- **Type Matching**: Only cluster entities of same type
- **Confidence Scoring**: Score clusters by confidence

#### ConflictResolver
```python
resolver = ConflictResolver()
resolved = resolver.resolve(
    conflicting_entities=conflict_list,
    strategy="confidence_weighted"
)
```

**Resolution Strategies**:
- **Confidence Weighted**: Weight by confidence scores
- **Time Based**: Prefer newer information
- **Evidence Based**: Weight by evidence strength
- **LLM Based**: Use LLM for complex conflicts

#### RelationshipMerger
```python
merger = RelationshipMerger()
merged = merger.merge(relationships=relationship_list)
```

**Merging Features**:
- **Evidence Combination**: Combine evidence from multiple sources
- **Confidence Aggregation**: Aggregate confidence scores
- **Conflict Detection**: Detect conflicting relationships
- **Quality Assessment**: Assess merged relationship quality

#### ConsistencyChecker
```python
checker = ConsistencyChecker()
consistency = checker.check(
    entities=entity_list,
    relationships=relationship_list
)
```

**Consistency Checks**:
- **Entity Consistency**: Check entity attribute consistency
- **Relationship Consistency**: Check relationship consistency
- **Temporal Consistency**: Check temporal contradictions
- **Ontological Compliance**: Check ontology compliance

### Basic Multi-Document Workflow (`basic_multi_document_workflow.py`)
**Purpose**: Basic implementation of Phase 3 multi-document processing with 100% reliability

**Key Patterns**:
- **100% Reliability**: Never crashes, always returns results
- **Phase Integration**: Integrate with previous phase results
- **Graceful Degradation**: Handle errors gracefully
- **Comprehensive Logging**: Detailed logging for debugging

**Usage**:
```python
from src.tools.phase3.basic_multi_document_workflow import BasicMultiDocumentWorkflow

workflow = BasicMultiDocumentWorkflow()
result = workflow.execute(ProcessingRequest(
    documents=["doc1.pdf", "doc2.pdf"],
    queries=["What are the main entities?"]
))
```

**Processing Pipeline**:
- **Input Validation**: Validate all inputs before processing
- **Phase Integration**: Build on previous phase results
- **Document Processing**: Process each document individually
- **Result Fusion**: Fuse results from multiple documents
- **Query Answering**: Answer queries using fused knowledge

## Data Models

### FusionResult
```python
@dataclass
class FusionResult:
    total_documents: int = 0
    entities_before_fusion: int = 0
    entities_after_fusion: int = 0
    relationships_before_fusion: int = 0
    relationships_after_fusion: int = 0
    conflicts_resolved: int = 0
    fusion_time_seconds: float = 0.0
    consistency_score: float = 0.0
    evidence_chains: List[Dict[str, Any]] = field(default_factory=list)
    duplicate_clusters: List[List[str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
```

### ConsistencyMetrics
```python
@dataclass
class ConsistencyMetrics:
    entity_consistency: float = 0.0
    relationship_consistency: float = 0.0
    temporal_consistency: float = 0.0
    ontological_compliance: float = 0.0
    overall_score: float = 0.0
    inconsistencies: List[Dict[str, Any]] = field(default_factory=list)
```

### EntityCluster
```python
@dataclass
class EntityCluster:
    cluster_id: str = "default_cluster"
    entities: List[Entity] = field(default_factory=list)
    canonical_entity: Optional[Entity] = None
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)
```

## Common Commands & Workflows

### Development Commands
```bash
# Run Phase 3 tool tests
python -m pytest tests/unit/tools/phase3/ -v

# Test multi-document fusion
python -c "from src.tools.phase3.t301_multi_document_fusion import MultiDocumentFusion; print(MultiDocumentFusion().get_tool_info())"

# Test basic workflow
python -c "from src.tools.phase3.basic_multi_document_workflow import BasicMultiDocumentWorkflow; print(BasicMultiDocumentWorkflow().get_tool_info())"

# Test entity similarity
python -c "from src.tools.phase3.t301_multi_document_fusion import EntitySimilarityCalculator; print(EntitySimilarityCalculator().get_tool_info())"
```

### Debugging Commands
```bash
# Check fusion capabilities
python -c "from src.tools.phase3.basic_multi_document_workflow import BasicMultiDocumentWorkflow; print(BasicMultiDocumentWorkflow().get_capabilities())"

# Test conflict resolution
python -c "from src.tools.phase3.t301_multi_document_fusion import ConflictResolver; print(ConflictResolver().get_tool_info())"

# Check consistency metrics
python -c "from src.tools.phase3.t301_multi_document_fusion import ConsistencyMetrics; print(ConsistencyMetrics().get_tool_info())"
```

## Code Style & Conventions

### File Organization
- **Consolidated Files**: Single file consolidates multiple tool implementations
- **Data Classes**: Use dataclasses for structured data models
- **Exception Classes**: Custom exceptions for fail-fast architecture
- **MCP Integration**: MCP server endpoints for external access

### Naming Conventions
- **Tool Names**: Descriptive names with fusion/fusion prefixes
- **Data Classes**: Use descriptive names for result models
- **Exception Classes**: Use `Error` suffix for custom exceptions
- **MCP Tools**: Use descriptive names for MCP endpoints

### Error Handling Patterns
- **Fail-Fast**: Custom exceptions for specific error types
- **100% Reliability**: Always return results, never crash
- **Graceful Degradation**: Handle errors gracefully
- **Comprehensive Logging**: Log all errors with context

### Logging Patterns
- **Fusion Logging**: Log fusion progress and results
- **Conflict Logging**: Log conflict resolution decisions
- **Consistency Logging**: Log consistency check results
- **Performance Logging**: Log fusion timing and metrics

## Integration Points

### Phase Integration
- **Phase 1 Integration**: Build on Phase 1 entity extraction
- **Phase 2 Integration**: Build on Phase 2 ontology-aware processing
- **PipelineOrchestrator**: Integration with unified orchestrator
- **Service Manager**: Integration with core services

### LLM Integration
- **OpenAI API**: GPT-based conflict resolution
- **Conflict Resolution**: LLM-based complex conflict resolution
- **Prompt Engineering**: Structured prompts for conflict resolution
- **Response Parsing**: Parse LLM responses for resolution decisions

### Database Integration
- **Neo4j**: Graph database for fused knowledge storage
- **Entity Storage**: Store fused entities in graph database
- **Relationship Storage**: Store fused relationships in graph database
- **Graph Updates**: Update graph with fusion results

### MCP Integration
- **FastMCP**: MCP server for external tool access
- **Tool Endpoints**: MCP endpoints for fusion tools
- **External Access**: Allow external systems to use fusion tools
- **API Compatibility**: Maintain API compatibility for external users

## Performance Considerations

### Fusion Optimization
- **Batch Processing**: Process documents in batches
- **Similarity Caching**: Cache similarity calculations
- **Cluster Optimization**: Optimize clustering algorithms
- **Conflict Resolution**: Efficient conflict resolution strategies

### Memory Management
- **Entity Streaming**: Stream entities for large datasets
- **Cluster Limits**: Limit cluster sizes for memory efficiency
- **Result Aggregation**: Aggregate results efficiently
- **Cleanup**: Proper cleanup of temporary data

### LLM Optimization
- **Prompt Optimization**: Optimize prompts for efficiency
- **Response Caching**: Cache LLM responses when possible
- **Batch LLM Calls**: Batch LLM calls for efficiency
- **Fallback Mechanisms**: Fallback when LLMs unavailable

## Testing Patterns

### Unit Testing
- **Tool Isolation**: Test each fusion tool independently
- **Data Model Testing**: Test data models and serialization
- **Exception Testing**: Test custom exception handling
- **MCP Testing**: Test MCP endpoint functionality

### Integration Testing
- **Phase Integration**: Test integration with previous phases
- **LLM Integration**: Test LLM integration with mock responses
- **Database Integration**: Test database integration
- **End-to-End**: Test complete fusion pipeline

### Reliability Testing
- **Error Scenarios**: Test error handling and recovery
- **Edge Cases**: Test edge cases and boundary conditions
- **Performance Testing**: Test performance with large datasets
- **Stress Testing**: Test under high load conditions

## Troubleshooting

### Common Issues
1. **LLM API Issues**: Check API keys and rate limits
2. **Memory Issues**: Reduce batch sizes for large datasets
3. **Performance Issues**: Optimize similarity calculations
4. **Consistency Issues**: Check temporal and logical consistency

### Debug Commands
```bash
# Check LLM connectivity
python -c "from src.core.enhanced_api_client import EnhancedAPIClient; print(EnhancedAPIClient().test_connectivity())"

# Test fusion accuracy
python -c "from src.tools.phase3.t301_multi_document_fusion import MultiDocumentFusion; fusion = MultiDocumentFusion(); print(fusion.measure_fusion_accuracy(None, []))"

# Check consistency metrics
python -c "from src.tools.phase3.t301_multi_document_fusion import MultiDocumentFusion; fusion = MultiDocumentFusion(); print(fusion.calculate_knowledge_consistency())"
```

## Migration & Upgrades

### Phase 2 to Phase 3 Migration
- **Tool Integration**: Integrate Phase 3 tools with Phase 2 results
- **Data Migration**: Migrate Phase 2 data to Phase 3 format
- **Workflow Updates**: Update workflows to include fusion
- **Configuration Updates**: Configure fusion parameters

### Configuration Updates
- **Fusion Configuration**: Configure fusion strategies and thresholds
- **LLM Configuration**: Configure LLM models for conflict resolution
- **Performance Configuration**: Configure performance parameters
- **MCP Configuration**: Configure MCP server settings

### Data Migration
- **Entity Migration**: Migrate entities to fusion-aware format
- **Relationship Migration**: Migrate relationships with fusion metadata
- **Graph Migration**: Migrate graph data with fusion results
- **Consistency Migration**: Add consistency metrics to existing data 