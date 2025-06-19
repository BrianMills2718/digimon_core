# Implementation Roadmap v2 - HISTORICAL VISION ⚠️

## ⚠️ DOCUMENTATION NOTICE - VISION CONFLICT RESOLVED
**This document contains HISTORICAL VISION CONFLICT - NOW RESOLVED**  
**Historical Conflict**: This document claimed "Universal Analytical Platform" vs current "GraphRAG-First Universal Analytics"  
**Resolution**: Adopted hybrid "GraphRAG-First Universal Analytics" positioning per `docs/current/VISION_ALIGNMENT_PROPOSAL.md`  
**Current Status**: HISTORICAL REFERENCE - Vision conflict resolved, document kept for roadmap context  
**Active Vision**: GraphRAG system designed for extensibility into broader analytical workflows

**Updated**: 2025-06-17 - Reflects MCP ecosystem integration, LLM enhancement, and universal analytical platform vision

**Archived v1**: See `docs/archive/IMPLEMENTATION_ROADMAP_v1_vertical_slice.md` for original vertical slice strategy

## Current Status ✅

**Phase 0 + Phase 1 Complete**: Successfully implemented and tested
- ✅ **Core Services**: T107 Identity, T110 Provenance, T111 Quality, T121 Workflow State
- ✅ **Vertical Slice**: PDF → PageRank → Answer pipeline (8 tools working end-to-end)
- ✅ **LLM Integration**: Gemini 2.5 Flash + OpenAI embeddings working
- ✅ **Database Architecture**: Neo4j + SQLite + Qdrant operational
- ✅ **Adversarial Testing**: 21/21 tests passing, handles 1000+ entities

## Vision: Universal Analytical Platform

**Core Innovation**: Claude Code as intelligent analytical orchestrator that dynamically selects optimal data formats (graphs, tables, vectors) and seamlessly orchestrates analysis across 121 planned specialized tools + MCP server ecosystem. (Note: Currently 13 tools implemented - 11% of vision)

**Not GraphRAG**: This is a format-agnostic analytical platform that happens to include graph capabilities, not a graph-centric system.

## Phase 2: LLM-Driven Ontology System (Current Priority) 🎯

**Critical Insight**: spaCy NER produces low-quality entities that make GraphRAG testing meaningless. Instead, build an LLM-driven ontology system that generates domain-specific entities for real GraphRAG capabilities.

### 2A. Ontology Generation & UI (Weeks 1-2)

#### **Week 1: Ontology Chat Interface & Storage**
```python
# Streamlit UI for ontology conversation
class OntologyChat:
    def chat_interface(self):
        # "I'm analyzing climate research papers"
        # "What specific aspects are you interested in?"
        # "Focus on policies, renewable technologies, and environmental impacts"
        
    def generate_ontology_preview(self, conversation: List[Message]) -> OntologyPreview:
        # Use Gemini 2.5 Flash to suggest entity types and relationships
        # Show preview before finalizing

# Full TORC compliance - store everything
class OntologyStorage:
    def save_ontology_session(self, session: OntologySession) -> str:
        # Store: conversation, generated ontology, user modifications, timestamps
        # Enable complete reproducibility and examinability
```

#### **Week 2: Gemini Ontology Generation & Validation**
```python
# T120: Ontology Generator (New Core Service)
@dataclass
class DomainOntology:
    domain_name: str
    domain_description: str
    entity_types: List[EntityType]  # CLIMATE_POLICY, RENEWABLE_TECH, etc.
    relationship_types: List[RelationshipType]  # IMPLEMENTS, AFFECTS, etc.
    extraction_patterns: List[str]  # Guidance for LLM extraction
    created_by_conversation: str  # Full conversation provenance
    
class GeminiOntologyGenerator:
    def generate_from_conversation(self, messages: List[Message]) -> DomainOntology:
        # Use Gemini 2.5 Flash structured output
        # Convert natural language domain description → formal ontology
        
    def validate_ontology(self, ontology: DomainOntology, sample_text: str) -> ValidationReport:
        # Test extraction on sample text to validate ontology quality
```

#### **Success Criteria Week 1-2:**
- [ ] Streamlit UI allows natural conversation about domain ontology
- [ ] Gemini 2.5 Flash generates structured ontologies from conversation
- [ ] Full conversation and ontology provenance stored for TORC compliance
- [ ] Users can preview and modify generated ontologies before applying
- [ ] Ontology validation works on sample text

### 2B. Ontology-Driven Extraction & Graph Building (Weeks 3-4)

#### **Week 3: Quality Entity & Relationship Extraction**
```python
# T23c: Ontology-Aware Entity Extractor (replaces spaCy)
class OntologyAwareExtractor:
    def extract_entities(self, text: str, ontology: DomainOntology) -> List[Entity]:
        # Use Gemini 2.5 Flash with custom ontology as context
        # "Extract CLIMATE_POLICY, RENEWABLE_TECH, ENVIRONMENTAL_IMPACT entities"
        # → Domain-specific, high-quality entities
        
    def extract_relationships(self, text: str, entities: List[Entity], 
                            ontology: DomainOntology) -> List[Relationship]:
        # Use ontology relationship types for guided extraction
        # Much better than pattern matching

# Enhanced with OpenAI embeddings
class EntityEmbedder:
    def embed_with_context(self, entity: Entity, ontology: DomainOntology) -> np.ndarray:
        # Use entity + ontology context for better embeddings
        # "CLIMATE_POLICY: Paris Agreement - An international climate policy framework"
```

#### **Week 4: Graph Building & Visualization**
```python
# T31c: Ontology-Aware Graph Builder
class OntologyGraphBuilder:
    def build_domain_graph(self, entities: List[Entity], 
                          relationships: List[Relationship],
                          ontology: DomainOntology) -> DomainGraph:
        # Build graph with ontology-aware node/edge types
        # Better clustering and organization
        
# Graph Visualization (requested feature)
class GraphVisualizer:
    def visualize_ontology_graph(self, graph: DomainGraph) -> InteractiveViz:
        # Use pyvis/plotly for interactive graph visualization
        # Color-code by ontology entity types
        # Show relationship types clearly
```

#### **Success Criteria Week 3-4:**
- [ ] Ontology-driven extraction produces domain-specific entities (not generic spaCy types)
- [ ] Quality embeddings generated with ontological context
- [ ] Graph visualization shows ontology-structured networks
- [ ] Full extraction and graph building provenance tracked for TORC
- [ ] Dramatic improvement in entity/relationship quality vs spaCy baseline

## Phase 2C: Real GraphRAG Testing & Optimization (Weeks 5-6)

### **Week 5: Ontology-Driven GraphRAG Implementation**
```python
# T49c: Ontology-Aware Multi-hop Query (the real GraphRAG test)
class OntologyGraphRAG:
    def ontology_aware_query(self, query: str, ontology: DomainOntology, 
                           graph: DomainGraph) -> GraphRAGResponse:
        # Use ontology to understand query intent
        # "What climate policies affect renewable energy?" 
        # → Search for CLIMATE_POLICY → AFFECTS → RENEWABLE_TECH paths
        
    def multi_hop_reasoning(self, start_entities: List[Entity], 
                          relationship_types: List[str], max_hops: int) -> ReasoningPath:
        # Use domain-specific relationship types for better path finding
        # Much more meaningful than generic relationships
        
# T68c: Ontology-Aware PageRank
class OntologyPageRank:
    def calculate_domain_importance(self, graph: DomainGraph, 
                                  ontology: DomainOntology) -> EntityRankings:
        # Weight PageRank by ontology entity type importance
        # Different importance for different domains
```

### **Week 6: Academic Traceability & Visualization**
```python
# Full TORC Compliance for Academic Use
class AcademicProvenance:
    def track_complete_analysis_chain(self, session: AnalysisSession) -> ProvenanceChain:
        # Conversation → Ontology → Extraction → Graph → GraphRAG → Results
        # Every step traceable and reproducible
        
    def generate_academic_report(self, analysis: Analysis) -> AcademicReport:
        # Methodology section, data provenance, reproducibility instructions
        # Ready for academic paper inclusion
        
# Enhanced Graph Visualization
class AcademicGraphViz:
    def create_interactive_graph(self, graph: DomainGraph, ontology: DomainOntology) -> InteractiveViz:
        # Color-coded by entity types from ontology
        # Interactive exploration of GraphRAG results
        # Export capabilities for academic publications
```

#### **Success Criteria Week 5-6:**
- [ ] Real GraphRAG working with ontology-driven entities and relationships
- [ ] Multi-hop reasoning produces meaningful, domain-specific results
- [ ] Graph visualization shows clear ontological structure
- [ ] Complete academic traceability from conversation to results
- [ ] Quality improvement measurable vs generic spaCy-based approach

## Phase 2D: MCP Ecosystem Integration (Weeks 7-8)

### Essential MCP Servers (Delayed Priority)

#### **T115: Graph→Table Converter** 
```python
# Convert graph data for statistical analysis
def graph_to_table(self, graph_ref: str, analysis_type: str) -> DataFrame:
    # Entity attributes → rows, relationships → columns
    # Enable statistical analysis of graph properties
```

#### **T116: Table→Graph Builder**
```python  
# Convert structured data into graph format
def table_to_graph(self, df: DataFrame, entity_cols: List[str], 
                  relationship_cols: List[str]) -> GraphRef:
    # CSV/Excel → Graph for relationship analysis
```

#### **T117: Format Auto-Selector**
```python
# Claude Code intelligence for optimal format selection
def select_optimal_format(self, data_ref: str, analysis_goal: str) -> FormatChoice:
    # "Find influential entities" → Graph format + PageRank
    # "Calculate correlations" → Table format + statistical analysis
    # "Find similar documents" → Vector format + similarity search
```

### PyWhy Causal Analysis Integration

#### **T118: Causal Discovery**
```python
# Integrate PyWhy for causal analysis
def discover_causal_relationships(self, data_ref: str) -> CausalGraph:
    # Use PyWhy algorithms to find causal relationships in data
    # Complement correlation analysis with causal understanding
```

## Phase 3: Horizontal Tool Expansion (Months 3-4)

### 3A. Complete Core Services (T108, T109, T112-T120)
- T108: Version Service - Four-level versioning (schema, data, graph, analysis)  
- T109: Entity Normalizer - Advanced entity resolution with embeddings
- T112-T120: Remaining infrastructure services

### 3B. Ingestion Expansion (T02-T12)
- T02: Word/HTML/Markdown loaders
- T03-T05: CSV, JSON, Excel loaders
- T06-T09: API connectors  
- T10-T12: Stream processing

### 3C. Advanced Processing (T14-T30)
- T25: Coreference resolution
- T26: Entity linking and disambiguation
- T28-T30: Advanced NLP capabilities

### 3D. Construction & Storage (T35-T48, T76-T81)
- Complete graph construction tools
- Advanced embedding strategies
- Comprehensive storage management

### 3E. Analysis & Interface (T68-T106)
- Advanced graph algorithms
- Natural language interfaces
- Monitoring and export capabilities

## Key Architecture Principles

### 1. MCP-First Integration
- **Leverage Ecosystem**: Use existing MCP servers before building custom tools
- **Standardized Interface**: All capabilities accessible through MCP protocol
- **Claude Code Orchestration**: Intelligent selection and coordination of MCP servers

### 2. LLM-Enhanced Capabilities  
- **Gemini 2.5 Flash**: Structured output for ontology generation and entity extraction
- **OpenAI Embeddings**: text-embedding-3-small for contextual entity similarity
- **Quality Over Speed**: Domain-specific extraction vs generic spaCy entities

### 3. Academic Traceability (TORC Compliance)
- **Complete Provenance**: Every conversation, ontology, extraction, and graph operation stored
- **Reproducibility**: Full session replay capabilities with identical results
- **Examinability**: Clear methodology documentation for academic scrutiny
- **Transparency**: All LLM prompts, responses, and reasoning chains preserved

### 4. Format-Agnostic Processing
- **Dynamic Format Selection**: Claude Code chooses optimal data structures
- **Seamless Conversion**: Tools enable mid-workflow format transformations
- **Universal Capabilities**: Any data format → optimal analytical approach

### 5. Universal Platform Vision
- **Not GraphRAG**: General analytical platform with graph capabilities
- **Analytical Intelligence**: Claude Code as the reasoning orchestrator
- **Ecosystem Integration**: MCP servers + PyWhy + statistical libraries + visualization

## Success Criteria

### Phase 2 Success (2 months)
- [ ] LLM-driven ontology system working end-to-end
- [ ] Domain-specific entity extraction dramatically better than spaCy
- [ ] Real GraphRAG capabilities with meaningful multi-hop reasoning
- [ ] Interactive graph visualization with ontological structure
- [ ] Complete academic traceability (TORC compliance) implemented
- [ ] Quality improvement measurably demonstrated

### Phase 3 Success (4 months)
- [ ] 50+ tools implemented (custom + MCP)
- [ ] Universal analytical capabilities demonstrated
- [ ] Complex multi-format workflows operational
- [ ] Ready for thesis defense as universal analytical platform

## Risk Mitigation

### 1. MCP Server Dependencies
- **Mitigation**: Identify critical servers early, have fallback implementations
- **Testing**: Docker-based integration tests for each MCP server

### 2. LLM API Costs
- **Mitigation**: Smart caching, hybrid approaches (deterministic + LLM when needed)
- **Monitoring**: Track API usage and costs

### 3. Complexity Management
- **Mitigation**: Maintain modularity, clear interfaces between components
- **Documentation**: Keep architecture decisions documented and rationale clear

## Implementation Notes

### Docker Compose Updates Needed
```yaml
services:
  # Existing
  neo4j:
    image: neo4j:5-community
  qdrant:
    image: qdrant/qdrant
    
  # New MCP Servers
  mcp-anyquery:
    image: julien040/anyquery
  mcp-jupyter:
    image: jupyter-mcp-server
  mcp-qdrant:
    image: qdrant/mcp-server-qdrant
  # ... additional MCP servers
```

### Environment Variables Updates
```bash
# LLM APIs (already configured)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

# MCP Server Endpoints
ANYQUERY_MCP_URL=http://localhost:8001
JUPYTER_MCP_URL=http://localhost:8002
QDRANT_MCP_URL=http://localhost:8003
```

## Next Immediate Actions

1. **Week 1 Focus**: Build Streamlit ontology chat interface with Gemini 2.5 Flash integration
2. **Academic Storage**: Implement full provenance tracking for TORC compliance
3. **Ontology Generation**: Get structured domain ontologies working from natural conversation
4. **Quality Baseline**: Measure current spaCy entity quality to establish improvement metrics

## Key Benefits of This Approach

### **Solves Core Testing Problem**
- **Before**: Generic spaCy entities (PERSON, ORG) → meaningless GraphRAG testing
- **After**: Domain-specific entities (CLIMATE_POLICY, RENEWABLE_TECH) → real GraphRAG evaluation

### **Academic Requirements Met**
- **TORC Compliance**: Complete traceability for academic scrutiny
- **Reproducibility**: Session replay with identical results
- **Methodology**: Clear documentation of ontology-driven approach

### **Real GraphRAG Finally Possible**
- **Quality Entities**: Domain-specific extraction using LLM + ontology
- **Meaningful Relationships**: Ontology-guided relationship types
- **Proper Embeddings**: Contextual embeddings with ontological information
- **Visual Validation**: Interactive graph visualization for result examination

This roadmap prioritizes getting **real GraphRAG working** with quality data over ecosystem expansion, enabling proper testing and academic validation of the approach.