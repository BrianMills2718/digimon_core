# Conceptual to Implementation Mapping

**Status**: Target Architecture  
**Purpose**: Bridge conceptual architecture with actual system implementation  
**Audience**: Developers, architects, implementers

## Overview

This document provides the essential mapping between KGAS conceptual architecture and its concrete implementation, enabling developers to understand how theoretical designs translate into actual code, services, and deployment configurations.

## Architectural Component Mapping

### 1. Cross-Modal Analysis Implementation

#### **Conceptual Design**
- **Philosophy**: Fluid movement between Graph, Table, Vector representations
- **Documentation**: [`cross-modal-philosophy.md`](cross-modal-philosophy.md)

#### **Implementation Mapping**
| Conceptual Component | Implementation Location | Service/Tool |
|---------------------|------------------------|--------------|
| **Cross-Modal Entity** | `src/core/cross_modal_entity.py` | Core Service |
| **Graph Analysis Mode** | `src/tools/t01_knowledge_graph_analysis.py` | T01 Tool |
| **Table Analysis Mode** | `src/tools/t02_structured_data_analysis.py` | T02 Tool |
| **Vector Analysis Mode** | `src/tools/t03_semantic_similarity.py` | T03 Tool |
| **Mode Conversion** | `src/core/format_converters/` | AnalyticsService |
| **Provenance Tracking** | `src/core/provenance_service.py` | ProvenanceService |

#### **Deployment Configuration**
```yaml
# Cross-modal services
cross_modal_service:
  image: kgas/cross-modal-service:latest
  environment:
    - ENABLE_GRAPH_MODE=true
    - ENABLE_TABLE_MODE=true  
    - ENABLE_VECTOR_MODE=true
    - PROVENANCE_TRACKING=enabled
```

### 2. Master Concept Library (MCL) Implementation

#### **Conceptual Design**
- **Philosophy**: Standardized vocabulary for semantic precision
- **Documentation**: [`master-concept-library.md`](master-concept-library.md)

#### **Implementation Mapping**
| Conceptual Component | Implementation Location | Service/Tool |
|---------------------|------------------------|--------------|
| **MCL Repository** | `src/ontology_library/mcl/` | TheoryRepository |
| **Concept Validation** | `src/ontology_library/validators.py` | QualityService |
| **DOLCE Alignment** | `src/ontology_library/dolce_integration.py` | TheoryRepository |
| **Concept Mapping** | `src/tools/t04_entity_extraction.py` | T04 Tool |
| **Schema Storage** | Neo4j + `mcl_concepts` table | Bi-Store |
| **API Endpoints** | `src/api/mcl_endpoints.py` | MCP Server |

#### **Database Schema**
```cypher
// Neo4j MCL concept storage
(:Concept {
    canonical_name: string,
    type: "Entity|Connection|Property|Modifier",
    upper_parent: string,    // DOLCE IRI
    description: string,
    validation_rules: [string],
    version: string
})

// Concept relationships
(:Concept)-[:SUBTYPE_OF]->(:Concept)
(:Concept)-[:RELATES_TO]->(:Concept)
```

### 3. Uncertainty Architecture Implementation

#### **Conceptual Design** 
- **Philosophy**: Four-layer uncertainty quantification
- **Documentation**: [`uncertainty-architecture.md`](uncertainty-architecture.md)

#### **Implementation Mapping**
| Conceptual Layer | Implementation Location | Service/Tool |
|------------------|------------------------|--------------|
| **Contextual Entity Resolution** | `src/core/identity_service.py` | IdentityService |
| **Temporal Knowledge Graph** | `src/core/temporal_graph.py` | AnalyticsService |
| **Bayesian Pipeline** | `src/core/uncertainty/bayesian.py` | QualityService |
| **Distribution Preservation** | `src/core/confidence_score.py` | All Tools (see ADR-007) |
| **Uncertainty Propagation** | `src/core/uncertainty/propagator.py` | PipelineOrchestrator |

#### **Uncertainty Integration Pattern**
```python
# Every tool implements uncertainty
class ToolWithUncertainty:
    def __init__(self):
        self.confidence_scorer = ConfidenceScore()
        
    def process(self, input_data):
        result = self.core_processing(input_data)
        uncertainty = self.confidence_scorer.assess(result, input_data)
        return UncertainResult(result, uncertainty)
```

### 4. Theory-Aware Processing Implementation

#### **Conceptual Design**
- **Philosophy**: Domain ontology guided analysis
- **Documentation**: [`theoretical-framework.md`](theoretical-framework.md)

#### **Implementation Mapping** 
| Conceptual Component | Implementation Location | Service/Tool |
|---------------------|------------------------|--------------|
| **Theory Repository** | `src/theory_repository/` | TheoryRepository |
| **Theory Extraction** | `src/tools/t05_theory_extraction.py` | T05 Tool |
| **Schema Validation** | `src/theory_repository/validators.py` | QualityService |
| **LLM Integration** | `src/core/llm_orchestrator.py` | WorkflowEngine |
| **Theory Application** | `src/core/theory_guided_analysis.py` | AnalyticsService |

## Service Architecture Implementation

### Core Services Mapping

| Architectural Service | Implementation Path | Primary Responsibilities |
|-----------------------|-------------------|-------------------------|
| **PipelineOrchestrator** | `src/core/pipeline_orchestrator.py` | Workflow coordination, service integration |
| **IdentityService** | `src/core/identity_service.py` | Entity resolution, cross-modal entity tracking |
| **AnalyticsService** | `src/core/analytics_service.py` | Cross-modal analysis orchestration |
| **TheoryRepository** | `src/theory_repository/repository.py` | Theory schema management, validation |
| **ProvenanceService** | `src/core/provenance_service.py` | Complete audit trail, reproducibility |
| **QualityService** | `src/core/quality_service.py` | Data validation, confidence scoring |
| **WorkflowEngine** | `src/core/workflow_engine.py` | YAML workflow execution |
| **SecurityMgr** | `src/core/security_manager.py` | PII encryption, credential management |
| **PiiService** | `src/core/pii_service.py` | Sensitive data handling, encryption |

### Service Integration Pattern
```python
# All services follow this integration pattern
class KGASService:
    def __init__(self, service_manager: ServiceManager):
        # Access to all core services
        self.identity = service_manager.identity_service
        self.provenance = service_manager.provenance_service
        self.quality = service_manager.quality_service
        self.theory = service_manager.theory_repository
        
    async def process_with_full_integration(self, data):
        # 1. Identity resolution
        entities = await self.identity.resolve_entities(data)
        # 2. Quality assessment  
        quality = await self.quality.assess_data_quality(data)
        # 3. Provenance tracking
        provenance = await self.provenance.track_operation(self, data)
        # 4. Theory application
        theory_context = await self.theory.get_applicable_theories(data)
        
        return IntegratedResult(entities, quality, provenance, theory_context)
```

## Data Architecture Implementation

### Bi-Store Architecture Mapping

| Conceptual Layer | Implementation Technology | Storage Purpose |
|------------------|--------------------------|------------------|
| **Graph & Vector Store** | Neo4j v5.13+ with native vectors | Entity relationships, semantic search |
| **Metadata Store** | SQLite with FTS5 | Workflow state, provenance, system metadata |
| **PII Vault** | SQLite with AES-GCM encryption | Secure sensitive data storage |

### Data Flow Implementation
```python
# Data flow through bi-store architecture
class BiStoreManager:
    def __init__(self):
        self.neo4j = Neo4jManager()      # Graph + Vector storage
        self.sqlite = SQLiteManager()    # Metadata + PII storage
        
    async def store_research_data(self, data: ResearchData):
        # 1. Graph relationships → Neo4j
        await self.neo4j.store_graph(data.entities, data.relationships)
        
        # 2. Vector embeddings → Neo4j native vectors
        await self.neo4j.store_vectors(data.embeddings)
        
        # 3. Metadata → SQLite
        await self.sqlite.store_metadata(data.provenance, data.workflow_state)
        
        # 4. PII → Encrypted SQLite
        await self.sqlite.store_pii_encrypted(data.sensitive_info)
```

## Tool Ecosystem Implementation

### T-Numbered Tools Mapping

| Tool Category | Implementation Range | Example Tools |
|---------------|---------------------|---------------|
| **Phase 1 Tools** | T01-T30 | T01: Knowledge Graph Analysis |
| **Cross-Modal Tools** | T31-T90 | T45: Graph-to-Table Converter |
| **Advanced Analytics** | T91-T121 | T95: Multi-Theory Synthesis |

### Tool Implementation Pattern
```python
# Standard tool implementation pattern
class KGASTool:
    def __init__(self, tool_id: str):
        self.tool_id = tool_id
        self.confidence_scorer = ConfidenceScore()  # see ADR-007 for uncertainty metrics
        self.service_manager = ServiceManager()
        
    async def execute(self, inputs: ToolInputs) -> ToolResult:
        # 1. Input validation
        validated_inputs = self.validate_inputs(inputs)
        
        # 2. Core processing with service integration
        result = await self.core_process(validated_inputs)
        
        # 3. Confidence scoring (required for all tools)
        confidence = self.confidence_scorer.assess(result, validated_inputs)
        
        # 4. Provenance tracking
        provenance = await self.service_manager.provenance_service.track_execution(
            self.tool_id, validated_inputs, result
        )
        
        return ToolResult(result, confidence, provenance)
```

## MCP Integration Implementation

### MCP Server Architecture

| Component | Implementation | Purpose |
|-----------|---------------|---------|
| **MCP Server** | `src/mcp_server/server.py` using FastMCP | Tool exposure to external clients |
| **Tool Registry** | `src/mcp_server/tool_registry.py` | Dynamic tool discovery and registration |
| **Security Layer** | `src/mcp_server/security.py` | Authentication and authorization |
| **Protocol Handler** | `src/mcp_server/protocol_handler.py` | MCP protocol compliance |

### Tool Exposure Configuration
```python
# MCP tool exposure
mcp_config = {
    "server_name": "kgas-mcp-server",
    "tools_exposed": 121,
    "security": {
        "authentication": "required",
        "rate_limiting": True,
        "tool_permissions": "role_based"
    },
    "performance": {
        "concurrent_requests": 10,
        "timeout": 300,
        "caching": "enabled"
    }
}
```

## Deployment Architecture Implementation

### Container Architecture
```dockerfile
# Core KGAS service container
FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy implementation
COPY src/ ./src/
COPY docs/ ./docs/

# Service configuration
ENV SERVICE_MODE=production
ENV MCP_SERVER_ENABLED=true
ENV UNCERTAINTY_LEVEL=full

CMD ["python", "src/main.py"]
```

### Production Configuration
```yaml
# docker-compose.production.yml
services:
  kgas-core:
    build: .
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - SQLITE_PATH=/data/kgas.db
      - MCP_SERVER_PORT=8000
    depends_on:
      - neo4j
      - monitoring
    
  neo4j:
    image: neo4j:5.13-enterprise
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_PLUGINS=["apoc", "graph-data-science"]
      
  monitoring:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## Performance Optimization Implementation

### Async Concurrency Pattern
```python
# AnyIO structured concurrency implementation
import anyio

class PerformanceOptimizedService:
    async def concurrent_processing(self, documents: List[Document]):
        async with anyio.create_task_group() as tg:
            results = []
            
            for doc in documents:
                # Parallel processing with resource management
                async def process_document(document):
                    # Theory extraction
                    theory = await self.theory_service.extract(document)
                    # Cross-modal analysis
                    analysis = await self.analytics_service.analyze(document, theory)
                    # Uncertainty assessment
                    confidence = await self.quality_service.assess(analysis)
                    return IntegratedResult(analysis, confidence)
                
                tg.start_soon(process_document, doc)
            
            return results
```

## Quality Assurance Implementation

### Testing Architecture
```python
# Comprehensive testing pattern
class ArchitectureValidationTests:
    def test_conceptual_implementation_alignment(self):
        """Verify conceptual design matches implementation"""
        # Test cross-modal analysis workflow
        # Test MCL concept validation
        # Test uncertainty propagation
        # Test theory integration
        
    def test_service_integration_contracts(self):
        """Verify service contracts match architectural specifications"""
        # Test service interfaces
        # Test data flow patterns  
        # Test error handling
        
    def test_performance_requirements(self):
        """Verify performance meets architectural targets"""
        # Test concurrent processing
        # Test resource utilization
        # Test scalability patterns
```

## Migration and Evolution

### Architecture Evolution Process
```python
def evolve_architecture(current_version: str, target_version: str):
    """Systematic architecture evolution with implementation alignment"""
    
    # 1. Conceptual design updates
    update_conceptual_documents()
    
    # 2. Implementation migration plan
    migration_plan = generate_migration_plan(current_version, target_version)
    
    # 3. Service-by-service migration
    for service in migration_plan.services:
        migrate_service(service, target_version)
        
    # 4. Integration testing
    validate_post_migration_integration()
    
    # 5. Documentation synchronization
    synchronize_conceptual_and_implementation_docs()
```

This mapping ensures that KGAS conceptual architecture translates directly into concrete, maintainable, and scalable implementation while preserving the system's academic research focus and cross-modal analysis capabilities.