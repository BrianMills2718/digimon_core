# Tools Module - CLAUDE.md

## Overview
The `src/tools/` directory contains the complete ecosystem of analysis tools that enable KGAS's cross-modal analysis capabilities. Tools are organized by phases and implement the 121-tool vision for comprehensive graph, table, vector, and cross-modal analysis.

## Directory Structure

### Phase Organization
- **`phase1/`**: Foundation tools (PDF loading, entity extraction, basic graph construction)
- **`phase2/`**: Performance and reliability tools (async processing, optimization)
- **`phase3/`**: Advanced features (multi-document fusion, complex analysis)
- **Future phases**: Will contain remaining tools for complete 121-tool ecosystem

### Tool Numbering System
Tools follow a systematic numbering convention:
- **T01-T30**: Graph analysis tools (centrality, paths, communities)
- **T31-T60**: Relational/table analysis tools (statistics, SQL operations)
- **T61-T90**: Vector analysis tools (similarity, clustering, embeddings)
- **T91-T121**: Cross-modal integration tools (format conversion, source linking)

## Current Implementation Status

### Phase 1 Tools (Foundation) - 17 tools implemented
**Document Processing:**
- T01: PDF Loader (`t01_pdf_loader.py`)
- T15A: Text Chunker (`t15a_text_chunker.py`)
- T15B: Vector Embedder (`t15b_vector_embedder.py`)

**Entity Extraction:**
- T23A: spaCy NER (`t23a_spacy_ner.py`)
- T23C: LLM Entity Extractor (`t23c_llm_entity_extractor.py`) - Theory-aware
- T27: Relationship Extractor (`t27_relationship_extractor.py`)

**Graph Construction:**
- T31: Entity Builder (`t31_entity_builder.py`)
- T34: Edge Builder (`t34_edge_builder.py`)
- T41: Text Embedder (`t41_text_embedder.py`, `t41_async_text_embedder.py`)

**Analysis:**
- T49: Multi-hop Query (`t49_multihop_query.py`, `t49_enhanced_query.py`)
- T68: PageRank (`t68_pagerank.py`, `t68_pagerank_optimized.py`)

**Infrastructure:**
- Base classes and error handling (`base_neo4j_tool.py`, `neo4j_error_handler.py`)
- MCP integration (`phase1_mcp_tools.py`)
- Workflows (`vertical_slice_workflow.py`)

### Phase 2 Tools (Performance) - 6 tools implemented
- Async Multi-Document Processor (`async_multi_document_processor.py`)
- T23C: Ontology-Aware Extractor (`t23c_ontology_aware_extractor.py`)
- T31: Ontology Graph Builder (`t31_ontology_graph_builder.py`)
- Interactive Graph Visualizer (`interactive_graph_visualizer.py`)
- Enhanced Vertical Slice Workflow (`enhanced_vertical_slice_workflow.py`)

### Phase 3 Tools (Advanced) - 3 tools implemented
- T301: Multi-Document Fusion (`t301_multi_document_fusion.py`)
- Basic Multi-Document Workflow (`basic_multi_document_workflow.py`)

**Total**: 26 tools implemented out of 121 planned (21.5%)

## Tool Development Patterns

### Standard Tool Structure
```python
# Tool implementation pattern
from typing import Dict, Any, Optional
from src.core.service_manager import ServiceManager
from src.utils.references import ReferenceManager
import logging

class ToolImplementation:
    """
    Standard tool implementation pattern.
    """
    
    def __init__(self, service_manager: ServiceManager):
        self.services = service_manager
        self.identity = service_manager.identity_service
        self.provenance = service_manager.provenance_service
        self.quality = service_manager.quality_service
        self.logger = logging.getLogger(__name__)
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method - all tools should implement this pattern.
        """
        try:
            # Input validation
            self._validate_inputs(params)
            
            # Log execution start
            self.logger.info(f"Starting {self.__class__.__name__} execution")
            
            # Core processing
            result = self._process(params)
            
            # Quality assessment
            confidence = self._assess_quality(result)
            
            # Provenance tracking
            self.provenance.log_execution(
                tool_id=self.__class__.__name__,
                inputs=params,
                outputs=result,
                confidence=confidence
            )
            
            return {
                "status": "success",
                "data": result,
                "confidence": confidence,
                "tool_id": self.__class__.__name__
            }
            
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "tool_id": self.__class__.__name__
            }
    
    def _validate_inputs(self, params: Dict[str, Any]) -> None:
        """Validate input parameters against tool contract."""
        # Implement contract-based validation
        pass
    
    def _process(self, params: Dict[str, Any]) -> Any:
        """Core processing logic - implement in subclass."""
        raise NotImplementedError
    
    def _assess_quality(self, result: Any) -> float:
        """Assess result quality and return confidence score."""
        return self.quality.assess_confidence(result)
```

### MCP Tool Wrapper Pattern
```python
# MCP integration pattern
from fastmcp import FastMCP

app = FastMCP("Tool Name")

@app.tool()
def tool_name(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """
    Tool description for MCP protocol.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (optional)
    
    Returns:
        Result dictionary with status and data
    """
    # Get service manager
    service_manager = ServiceManager()
    
    # Create tool instance
    tool = ToolImplementation(service_manager)
    
    # Execute with parameters
    return tool.execute({"param1": param1, "param2": param2})
```

## Cross-Modal Tool Categories

### Graph Analysis Tools (T1-T30)
**Current Status**: 5 implemented, 25 remaining
**Purpose**: Analyze graph structure, calculate metrics, find patterns

**Implemented:**
- T49: Multi-hop Query
- T68: PageRank

**Planned High Priority:**
- T01-T05: Centrality metrics (degree, betweenness, closeness, eigenvector)
- T06-T10: Community detection (Louvain, modularity, label propagation)
- T11-T15: Path analysis (shortest paths, all paths, path patterns)
- T16-T20: Subgraph operations (ego networks, k-hop neighborhoods)

### Table Analysis Tools (T31-T60)
**Current Status**: 2 implemented, 28 remaining
**Purpose**: Statistical analysis, aggregations, relational operations

**Implemented:**
- T31: Entity Builder (creates entities for graph from table data)

**Planned High Priority:**
- T32-T35: Graph to table conversion
- T36-T40: Statistical analysis (correlation, regression, hypothesis testing)
- T41-T45: Data manipulation (joins, pivots, aggregations)
- T46-T50: Time series analysis (if temporal data present)

### Vector Analysis Tools (T61-T90)
**Current Status**: 2 implemented, 28 remaining
**Purpose**: Similarity search, clustering, embeddings analysis

**Implemented:**
- T15B: Vector Embedder
- T41: Text Embedder (async version available)

**Planned High Priority:**
- T61-T65: Similarity search (cosine, euclidean, semantic search)
- T66-T70: Clustering (K-means, DBSCAN, hierarchical)
- T71-T75: Dimensionality reduction (PCA, t-SNE, UMAP)
- T76-T80: Vector operations (vector arithmetic, concept algebra)

### Cross-Modal Integration Tools (T91-T121)
**Current Status**: 0 implemented, 31 remaining
**Purpose**: Format conversion, orchestration, source linking

**Planned High Priority:**
- T91-T95: Format converters (graph↔table, table↔vector, vector↔graph)
- T96-T100: Source linking (any result → original documents)
- T101-T105: Cross-modal validation and consistency
- T106-T110: Intelligent format selection and optimization
- T111-T121: Advanced orchestration and workflow management

## Tool Implementation Workflow

### 1. Design Phase
```bash
# Create tool contract
cp contracts/tools/T01_PDF_LOADER.yaml contracts/tools/T_NEW_TOOL.yaml
# Edit contract to match new tool requirements

# Validate contract
python contracts/validation/theory_validator.py contracts/tools/T_NEW_TOOL.yaml
```

### 2. Implementation Phase
```bash
# Create tool implementation
cp src/tools/phase1/t01_pdf_loader.py src/tools/phase1/t_new_tool.py
# Implement tool following standard pattern

# Create MCP wrapper if needed
# Add to appropriate phase MCP tools file
```

### 3. Testing Phase
```bash
# Create unit tests
cp tests/unit/test_tool_template.py tests/unit/test_t_new_tool.py

# Run tests
python -m pytest tests/unit/test_t_new_tool.py

# Integration testing
python -m pytest tests/integration/ -k "new_tool"
```

### 4. Integration Phase
```bash
# Register with service manager
# Add to tool registry
# Update documentation
# Commit with evidence
```

## Theory-Aware Tools

### LLM-Ontology Integration
Tools marked as theory-aware integrate with the LLM-ontology system:

```python
# Theory-aware tool pattern
class TheoryAwareExtractor:
    def __init__(self, service_manager: ServiceManager):
        self.ontology_service = service_manager.ontology_service
        self.theory_repository = service_manager.theory_repository
    
    def extract_with_theory(self, text: str, theory_id: str) -> List[Entity]:
        """Extract entities using domain-specific ontology."""
        # Get theory ontology
        ontology = self.theory_repository.get_ontology(theory_id)
        
        # Use LLM with ontology context
        entities = self.ontology_service.extract_entities(text, ontology)
        
        return entities
```

### Ontology-Driven Processing
Key theory-aware tools:
- **T23C**: LLM Entity Extractor with domain ontologies
- **T31**: Ontology Graph Builder for theory-aware graphs
- **Future tools**: Will support theory-specific analysis patterns

## Performance Considerations

### Tool Execution
- **Async Support**: Phase 2 tools support async execution
- **Caching**: Frequently used results are cached
- **Resource Management**: Tools monitor memory and CPU usage
- **Error Recovery**: Graceful degradation and retry logic

### Cross-Modal Optimization
- **Format Selection**: Tools suggest optimal data formats
- **Conversion Efficiency**: Minimize unnecessary format conversions
- **Pipeline Optimization**: Tools can be chained efficiently
- **Source Traceability**: All operations maintain provenance

## Common Commands

### Tool Discovery
```bash
# List all implemented tools
find src/tools -name "t*.py" | sort

# Count tools by phase
echo "Phase 1: $(ls src/tools/phase1/t*.py | wc -l)"
echo "Phase 2: $(ls src/tools/phase2/t*.py | wc -l)"
echo "Phase 3: $(ls src/tools/phase3/t*.py | wc -l)"

# Check tool contract coverage
python scripts/verify_tool_success_rate.py
```

### Tool Testing
```bash
# Test specific tool
python -c "
from src.tools.phase1.t01_pdf_loader import T01_PDFLoader
from src.core.service_manager import ServiceManager
tool = T01_PDFLoader(ServiceManager())
result = tool.execute({'file_path': 'test_data/sample.pdf'})
print(result['status'])
"

# Run all tool tests
python -m pytest tests/ -k "tool" -v
```

### MCP Integration
```bash
# Test MCP tool access
python src/tools/phase1/phase1_mcp_tools.py

# List available MCP tools
python -c "
from src.tools.phase1.phase1_mcp_tools import app
print([tool.name for tool in app.get_tools()])
"
```

## Development Priorities

### Immediate (MVRT - 2 weeks)
1. **T02**: Word Document Loader
2. **T04**: Markdown Document Loader  
3. **T91-T93**: Basic cross-modal converters
4. **T115**: Graph to Table Converter
5. **T120**: Source Document Linker

### Short-term (Cross-Modal Expansion - 1 month)
1. **T06-T10**: Community detection tools
2. **T36-T40**: Statistical analysis tools
3. **T61-T65**: Similarity search tools
4. **T94-T98**: Advanced cross-modal tools

### Long-term (Complete Ecosystem - 3-6 months)
1. Complete all 121 tools
2. Advanced orchestration capabilities
3. Intelligent format selection
4. Theory-aware tool ecosystem

## Quality Standards

### Code Quality
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Include comprehensive docstrings
- Implement proper error handling
- Add logging for debugging

### Testing Requirements
- Unit tests for all tools (>90% coverage)
- Integration tests for tool chains
- Performance tests for resource usage
- Contract compliance verification
- Theory integration validation

### Documentation Standards
- Tool purpose and capabilities
- Input/output specifications
- Usage examples and patterns
- Integration points
- Performance characteristics

The tools module is the heart of KGAS's analytical capabilities. Focus on building robust, well-tested tools that support the cross-modal analysis vision while maintaining high quality and performance standards.