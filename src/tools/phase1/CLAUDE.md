# Phase 1 Tools - CLAUDE.md

## Overview
The `src/tools/phase1/` directory contains the core tools that implement the vertical slice workflow: **PDF → PageRank → Answer**. These tools form the foundational pipeline for document processing and knowledge graph construction.

## Vertical Slice Workflow

### Critical Path: PDF → PageRank → Answer
The Phase 1 workflow implements the essential path for document processing:
1. **T01**: PDF Loader - Extract text from documents
2. **T15a**: Text Chunker - Split text into processable chunks
3. **T23a**: spaCy NER - Extract named entities
4. **T27**: Relationship Extractor - Find entity relationships
5. **T31**: Entity Builder - Create graph nodes
6. **T34**: Edge Builder - Create graph relationships
7. **T68**: PageRank - Calculate entity importance
8. **T49**: Multi-hop Query - Answer questions

### Workflow Orchestration
- **PipelineOrchestrator**: Unified orchestrator for all workflow types
- **VerticalSliceWorkflow**: **DEPRECATED** - Use PipelineOrchestrator instead
- **Tool Protocol**: All tools implement the unified Tool interface

## Tool Architecture Patterns

### Service Integration Pattern
All Phase 1 tools follow a consistent service integration pattern:
```python
def __init__(
    self,
    identity_service: IdentityService = None,
    provenance_service: ProvenanceService = None,
    quality_service: QualityService = None
):
    # Allow tools to work standalone for testing
    if identity_service is None:
        from src.core.service_manager import ServiceManager
        service_manager = ServiceManager()
        self.identity_service = service_manager.get_identity_service()
        self.provenance_service = service_manager.get_provenance_service()
        self.quality_service = service_manager.get_quality_service()
    else:
        self.identity_service = identity_service
        self.provenance_service = provenance_service
        self.quality_service = quality_service
    self.tool_id = "TOOL_ID"
```

### Neo4j Integration Pattern
Tools that interact with Neo4j inherit from `BaseNeo4jTool`:
```python
class ToolName(BaseNeo4jTool):
    def __init__(
        self,
        identity_service: Optional[IdentityService] = None,
        provenance_service: Optional[ProvenanceService] = None,
        quality_service: Optional[QualityService] = None,
        neo4j_uri: str = None,
        neo4j_user: str = None,
        neo4j_password: str = None,
        shared_driver: Optional[Driver] = None
    ):
        super().__init__(
            identity_service, provenance_service, quality_service,
            neo4j_uri, neo4j_user, neo4j_password, shared_driver
        )
        self.tool_id = "TOOL_ID"
```

### Operation Tracking Pattern
All tools use consistent operation tracking:
```python
# Start operation tracking
operation_id = self.provenance_service.start_operation(
    tool_id=self.tool_id,
    operation_type="operation_name",
    inputs=[input_refs],
    parameters={
        "param1": value1,
        "param2": value2
    }
)

try:
    # Tool logic here
    # ...
    
    # Complete operation
    completion_result = self.provenance_service.complete_operation(
        operation_id=operation_id,
        outputs=[output_refs],
        success=True,
        metadata={
            "result_count": len(results),
            "processing_time": duration
        }
    )
    
    return {
        "status": "success",
        "results": results,
        "operation_id": operation_id,
        "provenance": completion_result
    }
    
except Exception as e:
    return self._complete_with_error(operation_id, str(e))
```

## Individual Tool Patterns

### T01: PDF Loader (`t01_pdf_loader.py`)
**Purpose**: Extract text from PDF documents with confidence scoring

**Key Patterns**:
- **File Validation**: Comprehensive input validation with security checks
- **Format Support**: PDF and TXT file support
- **Confidence Calculation**: Based on text length, page count, file size
- **Quality Assessment**: Integration with QualityService for confidence propagation

**Usage**:
```python
from src.tools.phase1.t01_pdf_loader import PDFLoader

loader = PDFLoader()
result = loader.load_pdf("document.pdf", workflow_id="wf_123")
```

**Configuration**:
- **Supported Formats**: `.pdf`, `.txt`
- **Base Confidence**: 0.9 for clean text extraction
- **Quality Factors**: Text length, page count, file size

### T15a: Text Chunker (`t15a_text_chunker.py`)
**Purpose**: Split text into overlapping chunks for processing

**Key Patterns**:
- **Sliding Window**: 512-token chunks with 50-token overlap
- **Position Tracking**: Character-level position tracking for provenance
- **Quality Inheritance**: Confidence propagation from source document
- **Tokenization**: Simple whitespace-based tokenization

**Usage**:
```python
from src.tools.phase1.t15a_text_chunker import TextChunker

chunker = TextChunker()
result = chunker.chunk_text("storage://document/doc123", text_content, 0.8)
```

**Configuration**:
- **Chunk Size**: 512 tokens
- **Overlap Size**: 50 tokens
- **Min Chunk Size**: 100 tokens
- **Quality Degradation**: 0.98 factor for chunking

### T23a: spaCy NER (`t23a_spacy_ner.py`)
**Purpose**: Extract named entities using spaCy's pre-trained models

**Key Patterns**:
- **Lazy Loading**: spaCy model loaded only when needed
- **Entity Filtering**: Target specific entity types (PERSON, ORG, GPE, etc.)
- **Type Mapping**: Map spaCy types to schema-compliant types
- **Mention Creation**: Integration with IdentityService for mention tracking

**Usage**:
```python
from src.tools.phase1.t23a_spacy_ner import SpacyNER

ner = SpacyNER()
result = ner.extract_entities("storage://chunk/chunk123", text_content, 0.8)
```

**Supported Entity Types**:
- **PERSON**: People, including fictional
- **ORG**: Companies, agencies, institutions
- **GPE**: Countries, cities, states
- **PRODUCT**: Objects, vehicles, foods
- **EVENT**: Named events, battles, wars
- **WORK_OF_ART**: Titles of books, songs
- **LAW**: Named documents made into laws
- **LANGUAGE**: Any named language
- **FACILITY**: Buildings, airports, highways
- **MONEY**: Monetary values
- **DATE**: Absolute or relative dates
- **TIME**: Times smaller than a day

### T27: Relationship Extractor (`t27_relationship_extractor.py`)
**Purpose**: Extract relationships between entities using pattern matching

**Key Patterns**:
- **Pattern-Based**: Simple verb-based patterns (X verb Y)
- **Dependency Parsing**: spaCy dependency parsing for complex relationships
- **Proximity-Based**: Fallback to proximity-based relationship detection
- **Confidence Scoring**: Based on pattern strength and context

**Usage**:
```python
from src.tools.phase1.t27_relationship_extractor import RelationshipExtractor

extractor = RelationshipExtractor()
result = extractor.extract_relationships("storage://chunk/chunk123", text_content, entities, 0.8)
```

**Relationship Patterns**:
- **Ownership**: "X owns Y", "X possessed Y"
- **Employment**: "X works for Y", "X employed by Y"
- **Location**: "X located in Y", "X based in Y"
- **Partnership**: "X partners with Y", "X collaborates with Y"
- **Creation**: "X created Y", "X founded Y"
- **Leadership**: "X leads Y", "X manages Y"
- **Membership**: "X member of Y", "X belongs to Y"

### T31: Entity Builder (`t31_entity_builder.py`)
**Purpose**: Convert entity mentions into graph nodes and store in Neo4j

**Key Patterns**:
- **Mention Aggregation**: Group mentions by entity using IdentityService
- **Canonical Names**: Assign canonical names to entities
- **Neo4j Integration**: Create and store entity nodes
- **Quality Assessment**: Assess entity quality based on mention count

**Usage**:
```python
from src.tools.phase1.t31_entity_builder import EntityBuilder

builder = EntityBuilder()
result = builder.build_entities(mentions, source_refs)
```

**Entity Properties**:
- **canonical_name**: Primary identifier for the entity
- **entity_type**: Type of entity (PERSON, ORG, etc.)
- **mention_count**: Number of mentions for this entity
- **confidence**: Overall confidence score
- **properties**: Additional entity properties

### T34: Edge Builder (`t34_edge_builder.py`)
**Purpose**: Create weighted relationship edges in Neo4j from extracted relationships

**Key Patterns**:
- **Entity Verification**: Verify all entities exist before creating relationships
- **Weight Calculation**: Confidence-based edge weights
- **Relationship Types**: Map to Neo4j relationship types
- **Quality Assessment**: Assess edge quality based on evidence

**Usage**:
```python
from src.tools.phase1.t34_edge_builder import EdgeBuilder

builder = EdgeBuilder()
result = builder.build_edges(relationships, source_refs)
```

**Edge Properties**:
- **weight**: Confidence-based weight (0.1 to 1.0)
- **confidence**: Extraction confidence
- **evidence_text**: Text evidence for the relationship
- **extraction_method**: Method used for extraction
- **properties**: Additional edge properties

### T68: PageRank Calculator (`t68_pagerank.py`)
**Purpose**: Calculate PageRank centrality scores for entities in the Neo4j graph

**Key Patterns**:
- **Graph Loading**: Load graph from Neo4j with entity filtering
- **NetworkX Integration**: Use NetworkX for PageRank calculation
- **Score Storage**: Store PageRank scores back to Neo4j
- **Result Ranking**: Rank entities by PageRank scores

**Usage**:
```python
from src.tools.phase1.t68_pagerank import PageRankCalculator

calculator = PageRankCalculator()
result = calculator.calculate_pagerank("neo4j://graph/main")
```

**Configuration**:
- **Damping Factor**: 0.85 (from config)
- **Max Iterations**: 100 (from config)
- **Tolerance**: 1e-6 (from config)
- **Min Score**: 0.0001 (from config)

### T49: Multi-hop Query (`t49_multihop_query.py`)
**Purpose**: Perform multi-hop queries on the Neo4j graph to find answers

**Key Patterns**:
- **Entity Extraction**: Extract query entities from natural language
- **Path Finding**: 1-hop, 2-hop, and 3-hop path discovery
- **Result Ranking**: PageRank-weighted result ranking
- **Path Explanation**: Generate explanations for query paths

**Usage**:
```python
from src.tools.phase1.t49_multihop_query import MultiHopQuery

query_engine = MultiHopQuery()
result = query_engine.query_graph("What companies does John Smith work for?")
```

**Query Parameters**:
- **max_hops**: Maximum number of hops (1-3)
- **result_limit**: Maximum results per query (default 20)
- **min_path_weight**: Minimum path weight threshold (0.01)
- **pagerank_boost**: Boost factor for PageRank scores (2.0)

## Common Commands & Workflows

### Development Commands
```bash
# Run Phase 1 tool tests
python -m pytest tests/unit/tools/phase1/ -v

# Test individual tools
python -c "from src.tools.phase1.t01_pdf_loader import PDFLoader; print(PDFLoader().get_tool_info())"

# Test workflow execution
python -c "from src.core.pipeline_orchestrator import PipelineOrchestrator; print(PipelineOrchestrator().execute(['test.pdf']))"

# Check Neo4j connectivity
python -c "from src.tools.phase1.base_neo4j_tool import BaseNeo4jTool; tool = BaseNeo4jTool(); print('Neo4j connected:', tool.driver is not None)"
```

### Debugging Commands
```bash
# Check tool status
python -c "from src.tools.phase1.t68_pagerank import PageRankCalculator; print(PageRankCalculator().get_neo4j_stats())"

# Validate entity extraction
python -c "from src.tools.phase1.t23a_spacy_ner import SpacyNER; ner = SpacyNER(); print(ner.get_supported_entity_types())"

# Test relationship patterns
python -c "from src.tools.phase1.t27_relationship_extractor import RelationshipExtractor; extractor = RelationshipExtractor(); print(extractor.get_supported_relationship_types())"
```

## Code Style & Conventions

### File Organization
- **Tool Files**: One tool per file with clear T-series naming (e.g., `t01_pdf_loader.py`)
- **Base Classes**: Shared base classes in separate files (e.g., `base_neo4j_tool.py`)
- **Error Handling**: Dedicated error handling modules (e.g., `neo4j_error_handler.py`)
- **Workflows**: Workflow orchestration in separate files

### Naming Conventions
- **Tool IDs**: Uppercase with underscores (e.g., `T01_PDF_LOADER`)
- **Methods**: snake_case (e.g., `load_pdf`, `extract_entities`)
- **Variables**: snake_case (e.g., `chunk_size`, `max_hops`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_CHUNK_SIZE`)

### Error Handling Patterns
- **Complete with Error**: Use `_complete_with_error()` for operation failures
- **Complete with Success**: Use `_complete_success()` for successful operations
- **Neo4j Errors**: Use `_complete_with_neo4j_error()` for database errors
- **Input Validation**: Comprehensive input validation before processing

### Logging Patterns
- **Operation Logging**: Log operation start/end with timing
- **Error Logging**: Log errors with context and operation ID
- **Debug Logging**: Use DEBUG level for detailed processing information
- **Performance Logging**: Log processing times and result counts

## Integration Points

### Core Services Integration
- **IdentityService**: Entity mention management and linking
- **ProvenanceService**: Operation tracking and lineage
- **QualityService**: Confidence assessment and propagation
- **ServiceManager**: Shared service instance management

### Neo4j Integration
- **BaseNeo4jTool**: Shared Neo4j driver management
- **Connection Pooling**: Efficient connection reuse
- **Error Handling**: Graceful Neo4j error handling
- **Transaction Management**: Proper transaction handling

### External Dependencies
- **spaCy**: NLP processing and entity extraction
- **pypdf**: PDF text extraction
- **NetworkX**: Graph algorithms and PageRank
- **Neo4j**: Graph database storage

## Performance Considerations

### Optimization Patterns
- **Lazy Loading**: spaCy models loaded only when needed
- **Shared Drivers**: Neo4j driver sharing via BaseNeo4jTool
- **Batch Processing**: Process multiple items in batches
- **Connection Pooling**: Efficient database connection management

### Memory Management
- **Streaming Processing**: Process large documents in chunks
- **Result Limiting**: Limit query results to prevent memory issues
- **Cleanup**: Proper cleanup of resources and connections
- **Caching**: Strategic caching of frequently accessed data

## Testing Patterns

### Unit Testing
- **Tool Isolation**: Test each tool independently
- **Mock Services**: Mock core services for isolated testing
- **Input Validation**: Test input validation thoroughly
- **Error Scenarios**: Test error handling and edge cases

### Integration Testing
- **Workflow Testing**: Test complete workflow execution
- **Neo4j Integration**: Test Neo4j operations with test database
- **Service Integration**: Test integration with core services
- **End-to-End**: Test complete PDF → Answer pipeline

### Test Data
- **Sample Documents**: Use consistent test PDFs and text
- **Entity Sets**: Standardized entity sets for testing
- **Relationship Sets**: Known relationship patterns for validation
- **Query Sets**: Standardized queries for testing

## Troubleshooting

### Common Issues
1. **spaCy Model Missing**: Install with `python -m spacy download en_core_web_sm`
2. **Neo4j Connection**: Check Neo4j server status and credentials
3. **Memory Issues**: Reduce chunk size or batch size for large documents
4. **Performance Issues**: Check Neo4j indexes and query optimization

### Debug Commands
```bash
# Check spaCy installation
python -c "import spacy; print(spacy.load('en_core_web_sm'))"

# Test Neo4j connection
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password')); print(driver.verify_connectivity())"

# Check tool dependencies
python -c "from src.tools.phase1.t01_pdf_loader import PDFLoader; print(PDFLoader().get_supported_formats())"
```

## Migration & Upgrades

### Tool Versioning
- **Version Tracking**: Each tool has version information
- **Backward Compatibility**: Maintain compatibility with existing data
- **Migration Scripts**: Automated migration for data format changes
- **Deprecation Warnings**: Clear warnings for deprecated functionality

### Workflow Migration
- **PipelineOrchestrator**: Migrate from deprecated VerticalSliceWorkflow
- **Configuration Updates**: Update tool configurations as needed
- **Data Migration**: Migrate existing graph data if schema changes
- **Testing**: Comprehensive testing after migration

## Security Considerations

### Input Validation
- **File Path Validation**: Validate file paths to prevent path traversal
- **Text Input Validation**: Validate text inputs for size and content
- **Query Validation**: Validate query inputs for injection prevention
- **Entity Validation**: Validate entity data for consistency

### Data Protection
- **PII Handling**: Integrate with PII service for sensitive data
- **Access Control**: Proper access control for database operations
- **Audit Logging**: Comprehensive audit logging for operations
- **Data Sanitization**: Sanitize all inputs before processing 