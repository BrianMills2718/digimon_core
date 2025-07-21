# Phase 2 Tools - CLAUDE.md

## Overview
The `src/tools/phase2/` directory contains enhanced tools that implement **ontology-aware processing** and **semantic reasoning**. These tools build upon Phase 1 capabilities by adding domain-specific knowledge, LLM-driven extraction, and advanced graph visualization.

## Phase 2 Enhanced Workflow

### Enhanced Path: PDF → Ontology → Semantic Graph → Answer
The Phase 2 workflow enhances the basic pipeline with ontology awareness:
1. **T01**: PDF Loader - Extract text from documents
2. **T15a**: Text Chunker - Split text into processable chunks
3. **T23c**: Ontology-Aware Entity Extractor - LLM-driven extraction with domain ontologies
4. **T31**: Ontology-Aware Graph Builder - Semantic graph construction with ontological validation
5. **T68**: PageRank - Calculate entity importance
6. **T49**: Multi-hop Query - Answer questions with ontological reasoning
7. **Interactive Graph Visualizer** - Rich visualization with ontological structure

### Workflow Orchestration
- **PipelineOrchestrator**: Unified orchestrator with Phase 2 enhanced tools
- **EnhancedVerticalSliceWorkflow**: **REFACTORED** - Delegates to PipelineOrchestrator
- **AsyncMultiDocumentProcessor**: Real async processing with performance improvements

## Tool Architecture Patterns

### Ontology-Aware Pattern
All Phase 2 tools integrate with domain ontologies:
```python
def __init__(self, 
             identity_service: Optional[IdentityService] = None,
             ontology_storage: Optional[OntologyStorageService] = None,
             confidence_threshold: float = 0.7):
    # Initialize with ontology awareness
    self.confidence_threshold = confidence_threshold
    self.current_ontology = None
    self.valid_entity_types = set()
    self.valid_relationship_types = set()
```

### Theory-Driven Validation Pattern
Phase 2 tools implement theory-driven validation:
```python
@dataclass
class TheoryValidationResult:
    entity_id: str
    is_valid: bool
    validation_score: float
    theory_alignment: Dict[str, float]
    concept_hierarchy_path: List[str]
    validation_reasons: List[str]

class TheoryDrivenValidator:
    def validate_entity_against_theory(self, entity: Dict[str, Any]) -> TheoryValidationResult:
        # Validate against theoretical framework
        # Calculate theory alignment
        # Generate validation reasons
```

### Async Processing Pattern
Phase 2 tools support async processing for performance:
```python
class AsyncMultiDocumentProcessor:
    def __init__(self, max_concurrent_docs: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent_docs)
    
    async def process_documents_async(self, document_paths: List[str]) -> List[ProcessingResult]:
        tasks = [asyncio.create_task(self.process_single_document(doc_path)) 
                for doc_path in document_paths]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

## Individual Tool Patterns

### T23c: Ontology-Aware Entity Extractor (`t23c_ontology_aware_extractor.py`)
**Purpose**: Replace generic spaCy NER with domain-specific extraction using LLMs and ontologies

**Key Patterns**:
- **LLM Integration**: Uses OpenAI and Gemini for entity extraction
- **Ontology Alignment**: Validates entities against domain ontologies
- **Theory-Driven Validation**: Validates entities against theoretical frameworks
- **Fallback Mechanisms**: Pattern-based extraction when LLMs unavailable

**Usage**:
```python
from src.tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor

extractor = OntologyAwareExtractor()
result = extractor.extract_entities(
    text_content, 
    ontology, 
    source_ref, 
    confidence_threshold=0.7,
    use_theory_validation=True
)
```

**Theory-Driven Validation**:
- **Concept Hierarchy**: Hierarchical concept structure from ontology
- **Validation Rules**: Rule-based validation against concept requirements
- **Theory Alignment**: Calculate alignment with theoretical frameworks
- **Validation Scoring**: Comprehensive scoring based on multiple factors

**LLM Integration**:
- **OpenAI**: GPT-based entity extraction with structured output
- **Gemini**: Google's Gemini model for entity extraction
- **Mock APIs**: Fallback for testing without API keys
- **Batch Processing**: Efficient batch processing of multiple texts

### T31: Ontology-Aware Graph Builder (`t31_ontology_graph_builder.py`)
**Purpose**: Build knowledge graphs using domain ontologies for high-quality entity resolution

**Key Patterns**:
- **Ontological Validation**: Validate entities and relationships against ontology
- **Semantic Embeddings**: Use embeddings for entity resolution
- **Graph Metrics**: Comprehensive metrics for graph quality assessment
- **Entity Merging**: Intelligent entity merging based on semantic similarity

**Usage**:
```python
from src.tools.phase2.t31_ontology_graph_builder import OntologyAwareGraphBuilder

builder = OntologyAwareGraphBuilder()
builder.set_ontology(domain_ontology)
result = builder.build_graph_from_extraction(extraction_result, source_document)
```

**Graph Metrics**:
- **Ontology Coverage**: Percentage of ontology types used
- **Semantic Density**: Average relationships per entity
- **Confidence Distribution**: Distribution of confidence scores
- **Entity Type Distribution**: Distribution of entity types

**Entity Resolution**:
- **Semantic Similarity**: Use embeddings for entity matching
- **Ontological Constraints**: Validate against ontology constraints
- **Confidence Thresholding**: Filter low-confidence entities
- **Entity Merging**: Merge similar entities with high confidence

### Interactive Graph Visualizer (`interactive_graph_visualizer.py`)
**Purpose**: Create rich, interactive visualizations of ontology-aware knowledge graphs

**Key Patterns**:
- **Plotly Integration**: Interactive visualizations with Plotly
- **Ontological Structure**: Display ontological structure and relationships
- **Semantic Exploration**: Enable semantic exploration of graph data
- **Filtering Options**: Multiple filtering options for graph exploration

**Usage**:
```python
from src.tools.phase2.interactive_graph_visualizer import InteractiveGraphVisualizer

visualizer = InteractiveGraphVisualizer()
data = visualizer.fetch_graph_data(source_document="doc123", ontology_domain="climate")
fig = visualizer.create_interactive_plot(data)
```

**Visualization Features**:
- **Interactive Plots**: Zoom, pan, hover interactions
- **Color Coding**: Entity types, confidence levels, ontology domains
- **Layout Algorithms**: Spring, circular, Kamada-Kawai layouts
- **Semantic Heatmaps**: Semantic similarity heatmaps
- **Ontology Structure**: Display ontological hierarchy

**Configuration Options**:
- **Max Nodes/Edges**: Limit visualization size for performance
- **Color Schemes**: Different color schemes for different attributes
- **Confidence Filtering**: Filter by confidence threshold
- **Layout Options**: Different layout algorithms

### Async Multi-Document Processor (`async_multi_document_processor.py`)
**Purpose**: Real async multi-document processing with performance improvements

**Key Patterns**:
- **Concurrency Control**: Semaphore-based concurrency control
- **Performance Tracking**: Comprehensive performance statistics
- **Error Handling**: Robust error handling for async operations
- **Evidence Logging**: Log processing evidence for audit trails

**Usage**:
```python
from src.tools.phase2.async_multi_document_processor import AsyncMultiDocumentProcessor

processor = AsyncMultiDocumentProcessor(max_concurrent_docs=5)
results = await processor.process_documents_async(document_paths)
```

**Performance Features**:
- **Concurrent Processing**: Process multiple documents simultaneously
- **Resource Management**: Efficient resource usage with semaphores
- **Performance Stats**: Track processing times and success rates
- **Benchmarking**: Compare against sequential processing

**Processing Pipeline**:
- **Document Loading**: Async document loading with format support
- **Text Chunking**: Async text chunking for large documents
- **Entity Extraction**: Async entity extraction from chunks
- **Result Aggregation**: Aggregate results from multiple documents

### Enhanced Vertical Slice Workflow (`enhanced_vertical_slice_workflow.py`)
**Purpose**: Enhanced Phase 2 workflow using unified orchestrator with ontology awareness

**Key Patterns**:
- **Orchestrator Delegation**: Delegate to PipelineOrchestrator instead of duplicate logic
- **Phase 2 Configuration**: Use Phase 2 enhanced tools and configuration
- **Enhanced Metadata**: Add Phase 2 specific metadata to results
- **Resource Management**: Proper resource cleanup and management

**Usage**:
```python
from src.tools.phase2.enhanced_vertical_slice_workflow import EnhancedVerticalSliceWorkflow

workflow = EnhancedVerticalSliceWorkflow()
result = workflow.execute_enhanced_workflow(
    document_paths, 
    queries, 
    confidence_threshold=0.7
)
```

**Enhanced Features**:
- **Ontology Awareness**: Full ontology-aware processing pipeline
- **Semantic Validation**: Semantic validation of entities and relationships
- **Enhanced Queries**: Multi-hop queries with ontological reasoning
- **Interactive Visualization**: Rich graph visualization capabilities

## Common Commands & Workflows

### Development Commands
```bash
# Run Phase 2 tool tests
python -m pytest tests/unit/tools/phase2/ -v

# Test ontology-aware extraction
python -c "from src.tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor; print(OntologyAwareExtractor().get_tool_info())"

# Test graph visualization
python -c "from src.tools.phase2.interactive_graph_visualizer import InteractiveGraphVisualizer; print(InteractiveGraphVisualizer().get_tool_info())"

# Test async processing
python -c "import asyncio; from src.tools.phase2.async_multi_document_processor import AsyncMultiDocumentProcessor; print(asyncio.run(AsyncMultiDocumentProcessor().get_performance_stats()))"
```

### Debugging Commands
```bash
# Check ontology storage
python -c "from src.core.ontology_storage_service import OntologyStorageService; print(OntologyStorageService().list_ontologies())"

# Test theory validation
python -c "from src.tools.phase2.t23c_ontology_aware_extractor import TheoryDrivenValidator; print('Theory validation available')"

# Check graph metrics
python -c "from src.tools.phase2.t31_ontology_graph_builder import OntologyAwareGraphBuilder; print(OntologyAwareGraphBuilder().adversarial_test_entity_resolution())"
```

## Code Style & Conventions

### File Organization
- **Tool Files**: One tool per file with clear naming (e.g., `t23c_ontology_aware_extractor.py`)
- **Data Classes**: Use dataclasses for structured data (e.g., `OntologyExtractionResult`)
- **Validation Classes**: Separate validation logic into dedicated classes
- **Async Support**: Async versions of tools for performance

### Naming Conventions
- **Tool Names**: Descriptive names with ontology/async prefixes
- **Data Classes**: Use `Result` suffix for result classes
- **Validation Classes**: Use `Validator` suffix for validation classes
- **Async Methods**: Use `async` prefix for async methods

### Error Handling Patterns
- **Theory Validation**: Comprehensive validation with detailed results
- **Async Error Handling**: Proper exception handling in async contexts
- **Ontology Validation**: Validate against ontology constraints
- **Fallback Mechanisms**: Graceful fallbacks when primary methods fail

### Logging Patterns
- **Ontology Logging**: Log ontology loading and validation
- **Async Logging**: Log async operation progress and timing
- **Validation Logging**: Log validation results and reasons
- **Performance Logging**: Log performance metrics and improvements

## Integration Points

### Ontology Integration
- **DomainOntology**: Integration with domain-specific ontologies
- **OntologyStorageService**: Ontology storage and retrieval
- **Theory Validation**: Theory-driven validation frameworks
- **Concept Hierarchy**: Hierarchical concept structures

### LLM Integration
- **OpenAI API**: GPT-based entity extraction
- **Gemini API**: Google's Gemini model integration
- **Async API Clients**: Async API client integration
- **Mock APIs**: Testing without API dependencies

### Visualization Integration
- **Plotly**: Interactive visualization library
- **NetworkX**: Graph analysis and layout algorithms
- **Neo4j**: Graph database integration
- **Color Schemes**: Custom color schemes for different entity types

### Async Integration
- **asyncio**: Python async/await support
- **aiofiles**: Async file I/O operations
- **Semaphores**: Concurrency control
- **Performance Tracking**: Async performance monitoring

## Performance Considerations

### Async Optimization
- **Concurrent Processing**: Process multiple documents simultaneously
- **Resource Management**: Efficient resource usage with semaphores
- **Async I/O**: Use async I/O for file and network operations
- **Performance Monitoring**: Track performance metrics and improvements

### Ontology Optimization
- **Lazy Loading**: Load ontologies only when needed
- **Caching**: Cache ontology data for repeated access
- **Validation Caching**: Cache validation results
- **Batch Processing**: Process entities and relationships in batches

### Visualization Optimization
- **Node/Edge Limits**: Limit visualization size for performance
- **Lazy Rendering**: Render visualizations on demand
- **Caching**: Cache visualization data and layouts
- **Progressive Loading**: Load visualization data progressively

## Testing Patterns

### Unit Testing
- **Tool Isolation**: Test each tool independently
- **Mock Ontologies**: Use mock ontologies for testing
- **Async Testing**: Test async functionality with asyncio
- **Validation Testing**: Test theory-driven validation

### Integration Testing
- **Ontology Integration**: Test ontology integration end-to-end
- **LLM Integration**: Test LLM integration with mock APIs
- **Visualization Testing**: Test visualization with sample data
- **Async Integration**: Test async processing pipeline

### Adversarial Testing
- **Entity Resolution**: Test entity resolution edge cases
- **Validation Edge Cases**: Test validation with edge cases
- **Performance Testing**: Test performance with large datasets
- **Error Scenarios**: Test error handling and recovery

## Troubleshooting

### Common Issues
1. **LLM API Issues**: Check API keys and rate limits
2. **Ontology Loading**: Verify ontology file paths and formats
3. **Async Performance**: Monitor concurrency and resource usage
4. **Visualization Performance**: Reduce node/edge limits for large graphs

### Debug Commands
```bash
# Check LLM API status
python -c "from src.core.enhanced_api_client import EnhancedAPIClient; print(EnhancedAPIClient().test_connectivity())"

# Test ontology loading
python -c "from src.ontology_generator import DomainOntology; print(DomainOntology.load_from_file('test_ontology.yaml'))"

# Check async performance
python -c "import asyncio; from src.tools.phase2.async_multi_document_processor import AsyncMultiDocumentProcessor; print(asyncio.run(AsyncMultiDocumentProcessor().get_performance_stats()))"
```

## Migration & Upgrades

### Phase 1 to Phase 2 Migration
- **Tool Replacement**: Replace Phase 1 tools with Phase 2 equivalents
- **Ontology Integration**: Add ontology awareness to existing workflows
- **Async Support**: Add async processing capabilities
- **Enhanced Visualization**: Upgrade to interactive visualizations

### Configuration Updates
- **Ontology Configuration**: Configure domain ontologies
- **LLM Configuration**: Configure LLM API keys and settings
- **Async Configuration**: Configure concurrency limits
- **Visualization Configuration**: Configure visualization settings

### Data Migration
- **Entity Migration**: Migrate entities to ontology-aware format
- **Relationship Migration**: Migrate relationships with ontological validation
- **Graph Migration**: Migrate graph data with enhanced metadata
- **Validation Migration**: Add theory-driven validation to existing data 