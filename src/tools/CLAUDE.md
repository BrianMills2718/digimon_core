# Tools Implementation Instructions

## Mission
Implement all 121 tools with contract-first design, complete functionality, and comprehensive documentation to enable cross-modal analysis and agent orchestration.

## Coding Philosophy

### Zero Tolerance for Shortcuts
- **NO lazy mocking/stubs/fallbacks/pseudo code** - Every tool must be fully functional
- **NO simplified implementations** - Build complete tool functionality or don't build it
- **NO hiding errors** - All errors must surface immediately with clear context
- **Fail-fast approach** - Tools must fail immediately on invalid inputs rather than degrading

### Evidence-Based Development
- **Nothing is working until proven working** - All tool functionality must be demonstrated
- **Every claim requires raw evidence logs** - Create Evidence.md files with actual tool execution logs
- **Comprehensive testing required** - Unit, integration, and workflow testing before claiming success
- **Performance evidence required** - Execution times, memory usage, and accuracy measurements

### Production Standards
- **Complete error handling** - Every tool must handle all possible error conditions
- **Comprehensive logging** - All tool operations logged with structured data
- **Full input validation** - All tool inputs validated against contracts
- **Resource management** - Proper cleanup of connections, files, and memory

## Codebase Structure

### Tools Architecture
```
src/tools/
├── phase1/                     # Foundation tools (17 implemented)
│   ├── t01_pdf_loader.py       # T01: Document loading
│   ├── t15a_text_chunker.py    # T15A: Text chunking
│   ├── t23a_spacy_ner.py       # T23A: Entity extraction
│   ├── t27_relationship_extractor.py # T27: Relationship extraction
│   ├── t31_entity_builder.py   # T31: Graph entity construction
│   ├── t34_edge_builder.py     # T34: Graph edge construction
│   ├── t68_pagerank.py         # T68: PageRank analysis
│   ├── t49_multihop_query.py   # T49: Multi-hop queries
│   └── phase1_mcp_tools.py     # MCP tool exposure
├── phase2/                     # Performance tools (6 implemented)
├── phase3/                     # Advanced tools (3 implemented)
└── base_classes/               # Tool base classes and protocols
    ├── tool_protocol.py        # Unified tool interface
    ├── base_neo4j_tool.py      # Neo4j integration base
    └── tool_contracts.py       # Tool contract definitions
```

### Tool Categories (121 Total)
```
T01-T30:  Graph Analysis Tools    (5 implemented, 25 remaining)
T31-T60:  Table Analysis Tools    (2 implemented, 28 remaining)  
T61-T90:  Vector Analysis Tools   (2 implemented, 28 remaining)
T91-T121: Cross-Modal Tools       (0 implemented, 31 remaining)
```

### Entry Points
- **MCP Server**: `src/mcp_server.py` - Tool exposure via MCP protocol
- **Pipeline Orchestrator**: `src/core/pipeline_orchestrator.py` - Tool workflow execution
- **Tool Factory**: `src/core/tool_factory.py` - Tool instantiation and configuration

## Critical Tool Issues to Resolve

### Issue 1: Tool Interface Contract Standardization

**Problem**: 12 existing tools use legacy interfaces instead of unified contract-first design.

**Evidence Required**:
- Tool interface audit with actual method signatures for all 26 tools
- Contract compliance test results for each tool
- Agent orchestration testing with unified interfaces

**Implementation Steps**:

1. **Create Unified Tool Interface Contract**
```python
# src/tools/base_classes/tool_protocol.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class ToolStatus(Enum):
    READY = "ready"
    PROCESSING = "processing" 
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass(frozen=True)
class ToolRequest:
    """Standardized tool input format"""
    tool_id: str
    operation: str
    input_data: Any
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    validation_mode: bool = False

@dataclass(frozen=True)
class ToolResult:
    """Standardized tool output format"""
    tool_id: str
    status: str  # "success" or "error"
    data: Any
    metadata: Dict[str, Any]
    execution_time: float
    memory_used: int
    error_code: Optional[str] = None
    error_message: Optional[str] = None

@dataclass(frozen=True)
class ToolContract:
    """Tool capability and requirement specification"""
    tool_id: str
    name: str
    description: str
    category: str  # "graph", "table", "vector", "cross_modal"
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    dependencies: List[str]
    performance_requirements: Dict[str, Any]
    error_conditions: List[str]

class UnifiedTool(ABC):
    """Contract all tools MUST implement"""
    
    @abstractmethod
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        pass
    
    @abstractmethod
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute tool operation with standardized input/output"""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """Validate input against tool contract"""
        pass
    
    @abstractmethod
    def health_check(self) -> ToolResult:
        """Check tool health and readiness"""
        pass
    
    @abstractmethod
    def get_status(self) -> ToolStatus:
        """Get current tool status"""
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """Clean up tool resources"""
        pass
```

2. **Migrate All 26 Existing Tools to Unified Interface**

**Example: T23A spaCy NER Migration**
```python
# src/tools/phase1/t23a_spacy_ner.py - Updated implementation
class SpacyNER(UnifiedTool):
    """T23A: spaCy Named Entity Recognition with unified interface"""
    
    def __init__(self, service_manager: ServiceManager):
        self.service_manager = service_manager
        self.tool_id = "T23A_SPACY_NER"
        self.status = ToolStatus.READY
        self.performance_monitor = PerformanceMonitor()
        self._initialize_spacy()
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="spaCy Named Entity Recognition",
            description="Extract named entities using spaCy pre-trained models",
            category="graph",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "minLength": 1},
                    "chunk_ref": {"type": "string"},
                    "confidence_threshold": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                },
                "required": ["text", "chunk_ref"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entity_id": {"type": "string"},
                                "surface_form": {"type": "string"},
                                "entity_type": {"type": "string"},
                                "confidence": {"type": "number"},
                                "start_pos": {"type": "integer"},
                                "end_pos": {"type": "integer"}
                            },
                            "required": ["entity_id", "surface_form", "entity_type", "confidence"]
                        }
                    },
                    "total_entities": {"type": "integer"}
                },
                "required": ["entities", "total_entities"]
            },
            dependencies=["identity_service", "provenance_service", "quality_service"],
            performance_requirements={
                "max_execution_time": 10.0,
                "max_memory_mb": 500,
                "min_accuracy": 0.85
            },
            error_conditions=[
                "EMPTY_TEXT",
                "SPACY_MODEL_NOT_AVAILABLE",
                "ENTITY_CREATION_FAILED",
                "MEMORY_LIMIT_EXCEEDED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute entity extraction with comprehensive error handling"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        try:
            # Set status to processing
            self.status = ToolStatus.PROCESSING
            
            # Validate input against contract
            if not self.validate_input(request.input_data):
                return self._create_error_result(
                    request,
                    "INVALID_INPUT",
                    "Input validation failed against tool contract"
                )
            
            # Extract parameters with defaults
            text = request.input_data.get("text")
            chunk_ref = request.input_data.get("chunk_ref")
            confidence_threshold = request.parameters.get("confidence_threshold", 0.8)
            
            # Validate text is not empty
            if not text or not text.strip():
                return self._create_error_result(
                    request,
                    "EMPTY_TEXT",
                    "Text input cannot be empty"
                )
            
            # Check spaCy model availability
            if not self.nlp:
                self._initialize_spacy()
                if not self.nlp:
                    return self._create_error_result(
                        request,
                        "SPACY_MODEL_NOT_AVAILABLE",
                        "spaCy model not available. Install with: python -m spacy download en_core_web_sm"
                    )
            
            # Process text with spaCy
            doc = self.nlp(text)
            
            # Extract entities with comprehensive processing
            entities = []
            for ent in doc.ents:
                # Filter by entity types and confidence
                if ent.label_ not in self.target_entity_types:
                    continue
                
                if len(ent.text.strip()) < 2:  # Skip very short entities
                    continue
                
                # Calculate entity confidence
                entity_confidence = self._calculate_entity_confidence(
                    ent.text, ent.label_, confidence_threshold
                )
                
                if entity_confidence < confidence_threshold:
                    continue
                
                # Create mention through identity service
                mention_result = self.service_manager.identity_service.create_mention(
                    surface_form=ent.text,
                    start_pos=ent.start_char,
                    end_pos=ent.end_char,
                    source_ref=chunk_ref,
                    entity_type=ent.label_,
                    confidence=entity_confidence
                )
                
                if mention_result.success:
                    entity_data = {
                        "entity_id": mention_result.data["entity_id"],
                        "mention_id": mention_result.data["mention_id"],
                        "surface_form": ent.text,
                        "entity_type": ent.label_,
                        "confidence": entity_confidence,
                        "start_pos": ent.start_char,
                        "end_pos": ent.end_char,
                        "created_at": datetime.now().isoformat()
                    }
                    entities.append(entity_data)
                else:
                    logger.warning(f"Failed to create mention for entity: {ent.text}")
            
            # Calculate execution metrics
            execution_time = time.time() - start_time
            memory_used = psutil.Process().memory_info().rss - start_memory
            
            # Reset status
            self.status = ToolStatus.READY
            
            # Create success result
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "entities": entities,
                    "total_entities": len(entities),
                    "entity_types": self._count_entity_types(entities),
                    "processing_stats": {
                        "text_length": len(text),
                        "entities_found": len(doc.ents),
                        "entities_extracted": len(entities),
                        "confidence_threshold": confidence_threshold
                    }
                },
                metadata={
                    "tool_version": "1.0.0",
                    "spacy_model": self.get_model_info(),
                    "operation": request.operation,
                    "timestamp": datetime.now().isoformat()
                },
                execution_time=execution_time,
                memory_used=memory_used
            )
            
        except Exception as e:
            self.status = ToolStatus.ERROR
            logger.error(f"Unexpected error in {self.tool_id}: {e}", exc_info=True)
            return self._create_error_result(
                request,
                "UNEXPECTED_ERROR",
                f"Unexpected error during entity extraction: {str(e)}"
            )
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input against tool contract"""
        try:
            # Validate against JSON schema
            jsonschema.validate(input_data, self.get_contract().input_schema)
            return True
        except jsonschema.ValidationError as e:
            logger.error(f"Input validation failed: {e}")
            return False
    
    def health_check(self) -> ToolResult:
        """Check tool health and readiness"""
        try:
            # Check spaCy model availability
            if not self.nlp:
                self._initialize_spacy()
            
            model_available = self.nlp is not None
            
            # Check service dependencies
            dependencies_healthy = True
            if self.service_manager:
                health_status = self.service_manager.health_check()
                dependencies_healthy = all(health_status.values())
            
            # Overall health status
            healthy = model_available and dependencies_healthy
            status = "success" if healthy else "error"
            
            return ToolResult(
                tool_id=self.tool_id,
                status=status,
                data={
                    "healthy": healthy,
                    "spacy_model_available": model_available,
                    "dependencies_healthy": dependencies_healthy,
                    "tool_status": self.status.value,
                    "supported_entity_types": list(self.target_entity_types)
                },
                metadata={
                    "health_check_timestamp": datetime.now().isoformat()
                },
                execution_time=0.0,
                memory_used=0
            )
            
        except Exception as e:
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={"healthy": False},
                metadata={"error": str(e)},
                execution_time=0.0,
                memory_used=0,
                error_code="HEALTH_CHECK_FAILED",
                error_message=str(e)
            )
```

3. **Tool Contract Validation Framework**
```python
# src/tools/base_classes/tool_validator.py
class ToolContractValidator:
    """Validate tools against their contracts"""
    
    def validate_tool_contract(self, tool: UnifiedTool) -> bool:
        """Validate tool implements its contract correctly"""
        try:
            contract = tool.get_contract()
            
            # Validate contract completeness
            if not self._validate_contract_completeness(contract):
                return False
            
            # Validate tool methods
            if not self._validate_tool_methods(tool):
                return False
            
            # Validate input/output schemas
            if not self._validate_schemas(contract):
                return False
            
            # Test tool with valid inputs
            if not self._test_tool_execution(tool, contract):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Contract validation failed for {tool.tool_id}: {e}")
            return False
    
    def _test_tool_execution(self, tool: UnifiedTool, contract: ToolContract) -> bool:
        """Test tool execution with sample data"""
        try:
            # Generate valid test input
            test_input = self._generate_test_input(contract.input_schema)
            
            # Create test request
            request = ToolRequest(
                tool_id=contract.tool_id,
                operation="test",
                input_data=test_input,
                parameters={},
                validation_mode=True
            )
            
            # Execute tool
            result = tool.execute(request)
            
            # Validate result format
            if not isinstance(result, ToolResult):
                return False
            
            # Validate output schema
            if result.status == "success":
                jsonschema.validate(result.data, contract.output_schema)
            
            return True
            
        except Exception as e:
            logger.error(f"Tool execution test failed: {e}")
            return False
```

### Issue 2: Complete Tool Registry and Documentation

**Problem**: 95 of 121 tools are not implemented and lack documentation.

**Evidence Required**:
- Complete tool registry with implementation status
- Tool documentation for all 121 tools
- Implementation priority matrix with dependencies

**Implementation Steps**:

1. **Create Complete Tool Registry**
```python
# src/tools/tool_registry.py
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class ToolCategory(Enum):
    GRAPH = "graph"
    TABLE = "table" 
    VECTOR = "vector"
    CROSS_MODAL = "cross_modal"

class ImplementationStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    DEPRECATED = "deprecated"

@dataclass
class ToolRegistryEntry:
    tool_id: str
    name: str
    description: str
    category: ToolCategory
    status: ImplementationStatus
    priority: int  # 1-10, 10 being highest
    dependencies: List[str]
    file_path: Optional[str]
    documentation_path: Optional[str]
    test_coverage: float
    performance_benchmarks: Dict[str, float]

class ToolRegistry:
    """Complete registry of all 121 tools"""
    
    def __init__(self):
        self.tools = self._initialize_complete_registry()
    
    def _initialize_complete_registry(self) -> Dict[str, ToolRegistryEntry]:
        """Initialize complete 121-tool registry"""
        registry = {}
        
        # Graph Analysis Tools (T01-T30)
        graph_tools = [
            ("T01", "PDF Loader", "Load and extract text from PDF documents", 10),
            ("T02", "Word Loader", "Load and extract text from Word documents", 8),
            ("T03", "Text Loader", "Load plain text documents", 6),
            ("T04", "Markdown Loader", "Load and parse Markdown documents", 5),
            ("T05", "CSV Loader", "Load structured data from CSV files", 7),
            ("T06", "Degree Centrality", "Calculate degree centrality for graph nodes", 8),
            ("T07", "Betweenness Centrality", "Calculate betweenness centrality", 7),
            ("T08", "Closeness Centrality", "Calculate closeness centrality", 6),
            ("T09", "Eigenvector Centrality", "Calculate eigenvector centrality", 6),
            ("T10", "PageRank", "Calculate PageRank scores", 9),
            ("T11", "Community Detection", "Detect communities using Louvain", 8),
            ("T12", "Modularity", "Calculate network modularity", 6),
            ("T13", "Label Propagation", "Community detection via label propagation", 5),
            ("T14", "Shortest Path", "Find shortest paths between nodes", 7),
            ("T15", "All Paths", "Find all paths between nodes", 5),
            ("T16", "Path Analysis", "Analyze path patterns and properties", 6),
            ("T17", "Ego Network", "Extract ego networks around nodes", 6),
            ("T18", "K-hop Neighborhood", "Extract k-hop neighborhoods", 7),
            ("T19", "Subgraph Extraction", "Extract subgraphs by criteria", 7),
            ("T20", "Graph Clustering", "Cluster nodes by similarity", 6),
            ("T21", "Graph Metrics", "Calculate global graph metrics", 5),
            ("T22", "Node Similarity", "Calculate node similarity scores", 6),
            ("T23", "Entity Extraction", "Extract named entities from text", 10),
            ("T24", "Relation Extraction", "Extract relationships between entities", 9),
            ("T25", "Coreference Resolution", "Resolve entity coreferences", 7),
            ("T26", "Entity Linking", "Link entities to knowledge bases", 6),
            ("T27", "Relationship Typing", "Type and classify relationships", 8),
            ("T28", "Graph Validation", "Validate graph consistency", 6),
            ("T29", "Graph Repair", "Repair graph inconsistencies", 5),
            ("T30", "Graph Export", "Export graphs to various formats", 7)
        ]
        
        for tool_id, name, description, priority in graph_tools:
            status = ImplementationStatus.IMPLEMENTED if tool_id in self._get_implemented_tools() else ImplementationStatus.NOT_STARTED
            registry[tool_id] = ToolRegistryEntry(
                tool_id=tool_id,
                name=name,
                description=description,
                category=ToolCategory.GRAPH,
                status=status,
                priority=priority,
                dependencies=self._get_tool_dependencies(tool_id),
                file_path=self._get_tool_file_path(tool_id),
                documentation_path=f"docs/tools/{tool_id.lower()}.md",
                test_coverage=self._get_test_coverage(tool_id),
                performance_benchmarks=self._get_performance_benchmarks(tool_id)
            )
        
        # Table Analysis Tools (T31-T60)
        # Vector Analysis Tools (T61-T90)  
        # Cross-Modal Tools (T91-T121)
        # ... (similar initialization for all categories)
        
        return registry
    
    def get_implementation_status(self) -> Dict[str, int]:
        """Get implementation status summary"""
        status_counts = {}
        for tool in self.tools.values():
            status = tool.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts
    
    def get_priority_queue(self) -> List[ToolRegistryEntry]:
        """Get tools ordered by implementation priority"""
        not_implemented = [
            tool for tool in self.tools.values() 
            if tool.status == ImplementationStatus.NOT_STARTED
        ]
        return sorted(not_implemented, key=lambda x: x.priority, reverse=True)
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Get tool dependency graph"""
        dep_graph = {}
        for tool in self.tools.values():
            dep_graph[tool.tool_id] = tool.dependencies
        return dep_graph
```

2. **Create Tool Documentation Template System**
```python
# scripts/generate_tool_docs.py
class ToolDocumentationGenerator:
    """Generate documentation for all 121 tools"""
    
    def generate_tool_docs(self, tool_id: str) -> str:
        """Generate comprehensive documentation for a tool"""
        registry_entry = self.tool_registry.tools[tool_id]
        
        doc_template = f"""# {tool_id}: {registry_entry.name}

## Overview
{registry_entry.description}

**Category**: {registry_entry.category.value}
**Priority**: {registry_entry.priority}/10
**Status**: {registry_entry.status.value}

## Tool Contract

### Input Schema
```json
{self._generate_input_schema(tool_id)}
```

### Output Schema
```json
{self._generate_output_schema(tool_id)}
```

### Performance Requirements
- **Max Execution Time**: {self._get_max_execution_time(tool_id)}s
- **Max Memory Usage**: {self._get_max_memory(tool_id)}MB
- **Min Accuracy**: {self._get_min_accuracy(tool_id)}

## Implementation Requirements

### Dependencies
{self._format_dependencies(registry_entry.dependencies)}

### Error Conditions
{self._get_error_conditions(tool_id)}

### Integration Points
{self._get_integration_points(tool_id)}

## Usage Examples

### Basic Usage
```python
{self._generate_basic_example(tool_id)}
```

### Advanced Usage
```python
{self._generate_advanced_example(tool_id)}
```

### Error Handling
```python
{self._generate_error_example(tool_id)}
```

## Testing Requirements

### Unit Tests
- Input validation testing
- Core functionality testing
- Error condition testing
- Performance testing

### Integration Tests
- Service integration testing
- Workflow integration testing
- Cross-tool compatibility testing

### Performance Tests
- Response time validation
- Memory usage validation
- Accuracy benchmarking

## Implementation Checklist

- [ ] Tool contract defined
- [ ] Core functionality implemented
- [ ] Error handling implemented
- [ ] Input validation implemented
- [ ] Unit tests written (>95% coverage)
- [ ] Integration tests written
- [ ] Performance tests written
- [ ] Documentation completed
- [ ] MCP integration added
- [ ] Contract validation passed

## Evidence Requirements

Before marking this tool as complete, create `Evidence_{tool_id}.md` with:

1. **Functionality Evidence**
   - Tool execution logs with various inputs
   - Output validation against schema
   - Error handling demonstration

2. **Performance Evidence**
   - Response time measurements
   - Memory usage tracking
   - Accuracy metrics

3. **Integration Evidence**
   - Service integration test results
   - Workflow execution results
   - Cross-tool compatibility results

4. **Test Evidence**
   - Unit test coverage report
   - Integration test results
   - Performance benchmark results
"""
        return doc_template
```

### Issue 3: Cross-Modal Tool Implementation

**Problem**: 0 of 31 cross-modal tools are implemented, blocking cross-modal analysis.

**Evidence Required**:
- Cross-modal conversion testing with real data
- Format integrity validation across conversions
- Performance measurements for large datasets

**Implementation Steps**:

1. **Create Cross-Modal Tool Framework**
```python
# src/tools/base_classes/cross_modal_tool.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from enum import Enum

class DataFormat(Enum):
    GRAPH = "graph"
    TABLE = "table"
    VECTOR = "vector"

@dataclass
class DataFormatSpec:
    """Specification for data format"""
    format_type: DataFormat
    schema: Dict[str, Any]
    sample_data: Any
    validation_rules: List[str]

class CrossModalTool(UnifiedTool):
    """Base class for cross-modal conversion tools"""
    
    @abstractmethod
    def get_source_format(self) -> DataFormatSpec:
        """Get source data format specification"""
        pass
    
    @abstractmethod
    def get_target_format(self) -> DataFormatSpec:
        """Get target data format specification"""
        pass
    
    @abstractmethod
    def convert(self, source_data: Any, context: Dict[str, Any] = None) -> Any:
        """Convert data from source to target format"""
        pass
    
    @abstractmethod
    def validate_conversion(self, source_data: Any, target_data: Any) -> bool:
        """Validate conversion maintains data integrity"""
        pass
```

2. **Implement Priority Cross-Modal Tools**

**T91: Graph to Table Converter**
```python
# src/tools/cross_modal/t91_graph_to_table.py
class GraphToTableConverter(CrossModalTool):
    """T91: Convert graph data to table format"""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(service_manager)
        self.tool_id = "T91_GRAPH_TO_TABLE"
    
    def get_contract(self) -> ToolContract:
        return ToolContract(
            tool_id=self.tool_id,
            name="Graph to Table Converter",
            description="Convert graph data to structured table format",
            category="cross_modal",
            input_schema={
                "type": "object",
                "properties": {
                    "graph_data": {
                        "type": "object",
                        "properties": {
                            "nodes": {"type": "array"},
                            "edges": {"type": "array"}
                        },
                        "required": ["nodes", "edges"]
                    },
                    "table_type": {
                        "type": "string",
                        "enum": ["adjacency", "edge_list", "node_attributes", "full"]
                    }
                },
                "required": ["graph_data", "table_type"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "table_data": {
                        "type": "object",
                        "properties": {
                            "columns": {"type": "array"},
                            "rows": {"type": "array"},
                            "metadata": {"type": "object"}
                        },
                        "required": ["columns", "rows"]
                    },
                    "conversion_stats": {"type": "object"}
                },
                "required": ["table_data", "conversion_stats"]
            },
            dependencies=["graph_analysis_service"],
            performance_requirements={
                "max_execution_time": 30.0,
                "max_memory_mb": 1000,
                "min_accuracy": 1.0  # Lossless conversion required
            },
            error_conditions=[
                "INVALID_GRAPH_FORMAT",
                "UNSUPPORTED_TABLE_TYPE",
                "CONVERSION_FAILED",
                "DATA_INTEGRITY_VIOLATION"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute graph to table conversion"""
        try:
            graph_data = request.input_data["graph_data"]
            table_type = request.input_data["table_type"]
            
            # Validate graph data format
            if not self._validate_graph_format(graph_data):
                return self._create_error_result(
                    request, "INVALID_GRAPH_FORMAT", 
                    "Graph data format validation failed"
                )
            
            # Convert based on table type
            if table_type == "adjacency":
                table_data = self._convert_to_adjacency_matrix(graph_data)
            elif table_type == "edge_list":
                table_data = self._convert_to_edge_list(graph_data)
            elif table_type == "node_attributes":
                table_data = self._convert_to_node_attributes(graph_data)
            elif table_type == "full":
                table_data = self._convert_to_full_table(graph_data)
            else:
                return self._create_error_result(
                    request, "UNSUPPORTED_TABLE_TYPE",
                    f"Table type '{table_type}' is not supported"
                )
            
            # Validate conversion integrity
            if not self.validate_conversion(graph_data, table_data):
                return self._create_error_result(
                    request, "DATA_INTEGRITY_VIOLATION",
                    "Conversion failed data integrity validation"
                )
            
            # Calculate conversion statistics
            conversion_stats = self._calculate_conversion_stats(graph_data, table_data)
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "table_data": table_data,
                    "conversion_stats": conversion_stats
                },
                metadata={
                    "source_format": "graph",
                    "target_format": "table",
                    "table_type": table_type
                },
                execution_time=time.time() - start_time,
                memory_used=self._get_memory_usage()
            )
            
        except Exception as e:
            return self._create_error_result(
                request, "CONVERSION_FAILED",
                f"Graph to table conversion failed: {str(e)}"
            )
```

### Issue 4: Tool Performance Monitoring and Optimization

**Problem**: No performance monitoring or optimization framework for tools.

**Evidence Required**:
- Performance benchmarks for all implemented tools
- Resource usage patterns under various loads
- Optimization results with before/after metrics

**Implementation Steps**:

1. **Create Tool Performance Framework**
```python
# src/tools/base_classes/tool_performance_monitor.py
import time
import psutil
import threading
from dataclasses import dataclass
from typing import Dict, List, Any
from contextlib import contextmanager

@dataclass
class ToolPerformanceMetrics:
    tool_id: str
    operation: str
    execution_time: float
    memory_used: int
    cpu_percent: float
    input_size: int
    output_size: int
    accuracy: Optional[float]
    timestamp: str

class ToolPerformanceMonitor:
    """Monitor performance of all tools"""
    
    def __init__(self):
        self.metrics = []
        self.benchmarks = {}
        self.performance_requirements = {}
    
    @contextmanager
    def monitor_tool_execution(self, tool_id: str, operation: str, input_data: Any):
        """Monitor tool execution performance"""
        process = psutil.Process()
        start_time = time.time()
        start_memory = process.memory_info().rss
        start_cpu = process.cpu_percent()
        
        try:
            yield
        finally:
            execution_time = time.time() - start_time
            end_memory = process.memory_info().rss
            memory_used = end_memory - start_memory
            cpu_percent = process.cpu_percent() - start_cpu
            
            input_size = self._calculate_data_size(input_data)
            
            metrics = ToolPerformanceMetrics(
                tool_id=tool_id,
                operation=operation,
                execution_time=execution_time,
                memory_used=memory_used,
                cpu_percent=cpu_percent,
                input_size=input_size,
                output_size=0,  # Set by tool after execution
                accuracy=None,   # Set by tool if applicable
                timestamp=datetime.now().isoformat()
            )
            
            self.metrics.append(metrics)
            self._check_performance_requirements(metrics)
    
    def register_performance_requirements(self, tool_id: str, requirements: Dict[str, Any]):
        """Register performance requirements for a tool"""
        self.performance_requirements[tool_id] = requirements
    
    def _check_performance_requirements(self, metrics: ToolPerformanceMetrics):
        """Check if metrics meet performance requirements"""
        requirements = self.performance_requirements.get(metrics.tool_id)
        if not requirements:
            return
        
        if metrics.execution_time > requirements.get("max_execution_time", float("inf")):
            logger.warning(f"{metrics.tool_id} exceeded execution time: {metrics.execution_time}s")
        
        if metrics.memory_used > requirements.get("max_memory_mb", float("inf")) * 1024 * 1024:
            logger.warning(f"{metrics.tool_id} exceeded memory usage: {metrics.memory_used} bytes")
        
        if metrics.accuracy and metrics.accuracy < requirements.get("min_accuracy", 0.0):
            logger.warning(f"{metrics.tool_id} below accuracy requirement: {metrics.accuracy}")
```

## Tool Testing Requirements

### Comprehensive Test Framework
```python
# tests/tools/test_tool_comprehensive.py
class TestToolComprehensive:
    """Comprehensive testing framework for all tools"""
    
    def test_all_tools_implement_contract(self):
        """Test all tools implement UnifiedTool interface"""
        for tool_class in self.get_all_tool_classes():
            assert issubclass(tool_class, UnifiedTool)
            tool = tool_class(self.service_manager)
            assert hasattr(tool, 'execute')
            assert hasattr(tool, 'get_contract')
            assert hasattr(tool, 'validate_input')
    
    def test_tool_contract_compliance(self):
        """Test each tool against its contract"""
        validator = ToolContractValidator()
        for tool in self.get_all_tools():
            assert validator.validate_tool_contract(tool)
    
    def test_tool_performance_requirements(self):
        """Test tools meet performance requirements"""
        monitor = ToolPerformanceMonitor()
        for tool in self.get_all_tools():
            contract = tool.get_contract()
            monitor.register_performance_requirements(
                tool.tool_id, 
                contract.performance_requirements
            )
            
            # Test with various input sizes
            for input_data in self.generate_test_inputs(contract):
                request = ToolRequest(
                    tool_id=tool.tool_id,
                    operation="test",
                    input_data=input_data,
                    parameters={}
                )
                
                with monitor.monitor_tool_execution(tool.tool_id, "test", input_data):
                    result = tool.execute(request)
                    assert result.status == "success"
    
    def test_cross_modal_integrity(self):
        """Test cross-modal tools maintain data integrity"""
        for tool in self.get_cross_modal_tools():
            # Test with real data samples
            for sample_data in self.get_cross_modal_test_data():
                source_data = sample_data["source"]
                expected_properties = sample_data["expected_properties"]
                
                request = ToolRequest(
                    tool_id=tool.tool_id,
                    operation="convert",
                    input_data={"data": source_data},
                    parameters={}
                )
                
                result = tool.execute(request)
                assert result.status == "success"
                
                # Validate data integrity
                assert tool.validate_conversion(source_data, result.data)
                
                # Check expected properties preserved
                for prop in expected_properties:
                    assert self._check_property_preserved(
                        source_data, result.data, prop
                    )
```

## Evidence Collection Requirements

### Tool Implementation Evidence
Create `Evidence_Tools.md` with:

1. **Tool Contract Compliance**
   - Contract validation results for all tools
   - Interface consistency verification
   - Input/output schema validation

2. **Performance Metrics**
   - Execution time measurements for all tools
   - Memory usage patterns under various loads
   - Accuracy benchmarks for applicable tools

3. **Cross-Modal Validation**
   - Data integrity testing results
   - Format conversion accuracy
   - Performance metrics for large datasets

4. **Integration Testing**
   - Service integration results
   - Workflow execution results
   - Agent orchestration testing

### Continuous Validation Process

1. **Update Verification Configuration**
```yaml
# gemini-review-tool/tools-review.yaml
claims_of_success:
  - "All 26 implemented tools use unified UnifiedTool interface"
  - "Tool registry documents all 121 tools with implementation status"
  - "Cross-modal tools maintain data integrity across conversions"
  - "Performance monitoring tracks all tool operations"
  - "All tools pass comprehensive test suites"

files_to_review:
  - "src/tools/**/*.py"
  - "src/tools/base_classes/*.py"
  - "src/tools/tool_registry.py"
  - "tests/tools/*.py"
  - "Evidence_Tools.md"
```

2. **Execute Validation Cycle**
```bash
# Run comprehensive tool tests
python -m pytest tests/tools/ -v --cov=src/tools --cov-report=html

# Validate tool contracts
python scripts/validate_all_tool_contracts.py

# Generate tool registry
python scripts/generate_tool_registry.py

# Run Gemini review
python gemini-review-tool/gemini_review.py --config gemini-review-tool/tools-review.yaml
```

## Success Criteria

Tools implementation is complete when:

1. **All tools implement unified interface** - Verified by contract validation tests
2. **Complete tool registry exists** - Verified by registry completeness check
3. **Cross-modal tools maintain integrity** - Verified by data integrity tests
4. **Performance meets requirements** - Verified by performance benchmark tests
5. **Gemini review finds no issues** - Verified by clean review report

Each criterion must be supported by evidence in `Evidence_Tools.md` before claiming success.