# Core Services Foundation Implementation Plan

## Overview

This plan outlines the implementation of Milestone 1: Core Services Foundation for the Super-Digimon GraphRAG system. This milestone establishes the critical infrastructure required by all 121 tools.

## Critical Dependencies

The following core services MUST be implemented first as they are blocking dependencies for all other tools:

- **T107: Identity Service** - Three-level identity management (Surface → Mention → Entity)
- **T110: Provenance Service** - Complete operation lineage tracking  
- **T111: Quality Service** - Confidence assessment and propagation
- **T121: Workflow State Service** - Checkpoint/recovery for long operations

## Implementation Tasks

### Task 1: Database Infrastructure Setup

**Priority**: CRITICAL - Foundation for all data storage
**Dependencies**: None
**Estimated Time**: 2-3 days

#### Deliverables:
1. **Docker Compose Configuration**
   - Neo4j 5.x container with proper configuration
   - Redis container for caching (optional for MVP)
   - Environment variable management (.env file)
   - Health checks and restart policies

2. **Neo4j Schema Setup**
   ```cypher
   // Core node types
   CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;
   CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE;
   CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;
   
   // Performance indices
   CREATE INDEX entity_canonical_name IF NOT EXISTS FOR (e:Entity) ON (e.canonical_name);
   CREATE INDEX chunk_document_ref IF NOT EXISTS FOR (c:Chunk) ON (c.document_ref);
   CREATE INDEX entity_type_confidence IF NOT EXISTS FOR (e:Entity) ON (e.entity_type, e.confidence);
   ```

3. **SQLite Schema Setup**
   - Workflow states table
   - Provenance tracking table
   - Quality scores table
   - Object versions table
   - Reference registry table
   - Mentions table (three-level identity)

4. **FAISS Index Initialization**
   - Vector dimension configuration (384 for sentence-transformers)
   - Index type selection (IndexFlatIP for MVP)
   - Memory management and persistence

#### Acceptance Criteria:
- [ ] All databases start successfully via docker-compose
- [ ] Schemas are created with proper constraints and indices
- [ ] Connection pooling works for all databases
- [ ] Health checks pass for all services
- [ ] Test data can be inserted and retrieved from all databases

### Task 2: Universal Reference System

**Priority**: CRITICAL - Enables cross-database operations
**Dependencies**: Task 1 (Database Infrastructure)
**Estimated Time**: 1-2 days

#### Deliverables:

1. **Reference Format Implementation**
   ```python
   # Universal reference format: storage://type/id
   "neo4j://entity/ent_123"
   "sqlite://mention/mention_456"
   "faiss://embedding/emb_789"
   ```

2. **Reference Parser and Validator**
   ```python
   class ReferenceParser:
       def parse_reference(self, ref: str) -> Reference
       def validate_reference(self, ref: str) -> bool
       def build_reference(self, storage: str, obj_type: str, obj_id: str) -> str
   ```

3. **Reference Resolver**
   ```python
   class ReferenceResolver:
       async def resolve_single(self, ref: str, fields: Optional[List[str]] = None) -> Dict
       async def resolve_batch(self, refs: List[str]) -> Dict[str, Dict]
       async def check_integrity(self, refs: List[str]) -> Dict[str, bool]
   ```

#### Acceptance Criteria:
- [ ] References can be parsed and validated correctly
- [ ] Single object resolution works across all databases
- [ ] Batch resolution optimizes database queries
- [ ] Missing references are handled gracefully
- [ ] Reference integrity checking works

### Task 3: Data Models Implementation

**Priority**: HIGH - Foundation for all data objects
**Dependencies**: Task 2 (Reference System)
**Estimated Time**: 2-3 days

#### Deliverables:

1. **Base Data Models**
   ```python
   @dataclass
   class BaseObject:
       id: str
       confidence: float
       quality_tier: str  # "high", "medium", "low"
       warnings: List[str]
       evidence: List[str]
       created_by: str
       created_at: datetime
   
   @dataclass
   class Entity(BaseObject):
       canonical_name: str
       entity_type: str
       surface_forms: List[str]
       mention_refs: List[str]
   
   @dataclass
   class Mention(BaseObject):
       surface_text: str
       document_ref: str
       position: int
       context_window: str
       entity_candidates: List[Dict]
       selected_entity: Optional[str]
   
   @dataclass
   class Relationship(BaseObject):
       source_entity: str
       target_entity: str
       relationship_type: str
       weight: float
       mention_refs: List[str]
   ```

2. **Database Adapters**
   ```python
   class Neo4jAdapter:
       async def create_entity(self, entity: Entity) -> str
       async def get_entity(self, entity_id: str) -> Entity
       async def update_entity(self, entity: Entity) -> bool
   
   class SQLiteAdapter:
       async def create_mention(self, mention: Mention) -> str
       async def get_mention(self, mention_id: str) -> Mention
       async def update_mention(self, mention: Mention) -> bool
   
   class FAISSAdapter:
       async def add_embedding(self, obj_id: str, vector: np.ndarray) -> str
       async def search_similar(self, vector: np.ndarray, k: int) -> List[Tuple[str, float]]
   ```

#### Acceptance Criteria:
- [ ] All data models have proper type hints and validation
- [ ] Database adapters work with real database instances
- [ ] CRUD operations work for all object types
- [ ] Quality tracking fields are properly handled
- [ ] Reference fields are validated

### Task 4: T107 Identity Service Implementation

**Priority**: CRITICAL - Required by all entity-related tools
**Dependencies**: Task 3 (Data Models)
**Estimated Time**: 3-4 days

#### Deliverables:

1. **Three-Level Identity Management**
   ```python
   class IdentityService:
       async def create_mention(
           self, 
           surface_text: str, 
           context: Dict, 
           entity_candidates: List[Dict]
       ) -> str
       
       async def resolve_mention(
           self, 
           mention_id: str, 
           selected_entity: str
       ) -> bool
       
       async def create_entity(
           self, 
           canonical_name: str, 
           entity_type: str, 
           surface_forms: List[str]
       ) -> str
       
       async def merge_entities(
           self, 
           primary_entity: str, 
           secondary_entities: List[str]
       ) -> str
   ```

2. **Entity Resolution Logic**
   - Exact match detection
   - Fuzzy matching with confidence scoring
   - Entity deduplication strategies
   - Canonical name assignment rules

3. **MCP Tool Interface**
   ```python
   @mcp_tool
   async def identity_service(
       operation: str,
       surface_text: Optional[str] = None,
       context: Optional[Dict] = None,
       entity_candidates: Optional[List[Dict]] = None
   ) -> Dict
   ```

#### Acceptance Criteria:
- [ ] Mentions can be created with proper context tracking
- [ ] Entity resolution works with confidence scoring
- [ ] Entity merging preserves all surface forms and mentions
- [ ] Canonical names are assigned consistently
- [ ] MCP tool interface works correctly
- [ ] All operations are recorded in provenance

### Task 5: T110 Provenance Service Implementation

**Priority**: CRITICAL - Required by ALL tools for auditing
**Dependencies**: Task 3 (Data Models)
**Estimated Time**: 2-3 days

#### Deliverables:

1. **Provenance Tracking System**
   ```python
   class ProvenanceService:
       async def record_operation(
           self,
           tool_id: str,
           operation: str,
           inputs: List[str],
           outputs: List[str],
           parameters: Dict
       ) -> str
       
       async def trace_lineage(
           self,
           object_id: str,
           max_depth: int = 10
       ) -> Dict
       
       async def find_affected(
           self,
           changed_object: str
       ) -> List[str]
   ```

2. **Operation Recording**
   - Automatic recording of all tool operations
   - Input/output reference tracking
   - Parameter serialization
   - Execution time measurement

3. **Lineage Analysis**
   - Backward tracing (what created this?)
   - Forward tracing (what does this affect?)
   - Impact analysis for changes
   - Dependency graph construction

#### Acceptance Criteria:
- [ ] All tool operations are automatically recorded
- [ ] Lineage tracing works backward and forward
- [ ] Impact analysis identifies affected objects
- [ ] Performance is acceptable for complex graphs
- [ ] Provenance data is queryable

### Task 6: T111 Quality Service Implementation

**Priority**: CRITICAL - Required by ALL tools for confidence tracking
**Dependencies**: Task 3 (Data Models)
**Estimated Time**: 2-3 days

#### Deliverables:

1. **Quality Assessment System**
   ```python
   class QualityService:
       async def assess_quality(
           self,
           obj: BaseObject,
           method: str = "default"
       ) -> Dict
       
       async def propagate_quality(
           self,
           upstream_scores: List[float],
           operation_confidence: float = 1.0
       ) -> float
       
       async def aggregate_quality(
           self,
           object_scores: List[Dict]
       ) -> Dict
   ```

2. **Confidence Scoring Methods**
   - Frequency-based scoring for entities
   - Context coherence analysis
   - Source reliability weighting
   - Uncertainty propagation formulas

3. **Quality Tier Assignment**
   - High: confidence >= 0.8
   - Medium: 0.5 <= confidence < 0.8  
   - Low: confidence < 0.5

#### Acceptance Criteria:
- [ ] Quality assessment works for all object types
- [ ] Confidence propagation maintains mathematical consistency
- [ ] Quality tiers are assigned correctly
- [ ] Warnings are generated for low-quality objects
- [ ] Evidence tracking supports quality decisions

### Task 7: T121 Workflow State Service Implementation

**Priority**: CRITICAL - Required for MCP server orchestration
**Dependencies**: Task 3 (Data Models)
**Estimated Time**: 2-3 days

#### Deliverables:

1. **Workflow State Management**
   ```python
   class WorkflowStateService:
       async def create_checkpoint(
           self,
           workflow_id: str,
           state_data: Dict,
           tool_sequence: List[str]
       ) -> str
       
       async def restore_checkpoint(
           self,
           workflow_id: str,
           checkpoint_id: str
       ) -> Dict
       
       async def list_checkpoints(
           self,
           workflow_id: str
       ) -> List[Dict]
   ```

2. **State Serialization**
   - Lightweight reference-based state storage
   - Compression for large state objects
   - Incremental checkpoint support
   - State validation on restore

3. **Recovery Mechanisms**
   - Automatic checkpoint creation every 100 operations
   - Manual checkpoint triggers
   - State restoration with validation
   - Cleanup of old checkpoints

#### Acceptance Criteria:
- [ ] Checkpoints can be created and restored
- [ ] State compression works efficiently
- [ ] Recovery handles partial failures gracefully
- [ ] Checkpoint cleanup prevents storage bloat
- [ ] Performance impact is minimal

### Task 8: MCP Server Framework

**Priority**: CRITICAL - Exposes all tools via MCP protocol
**Dependencies**: Tasks 4-7 (All Core Services)
**Estimated Time**: 3-4 days

#### Deliverables:

1. **MCP Server Implementation**
   ```python
   class SuperDigimonMCPServer:
       def __init__(self):
           self.identity_service = IdentityService()
           self.provenance_service = ProvenanceService()
           self.quality_service = QualityService()
           self.workflow_service = WorkflowStateService()
       
       async def handle_tool_call(self, tool_name: str, arguments: Dict) -> Dict
       async def list_tools(self) -> List[str]
       async def get_tool_schema(self, tool_name: str) -> Dict
   ```

2. **Tool Registration System**
   - Automatic tool discovery
   - Schema validation
   - Error handling and logging
   - Performance monitoring

3. **Main Entry Point**
   ```python
   # main.py
   async def main():
       server = SuperDigimonMCPServer()
       await server.start()
   
   if __name__ == "__main__":
       asyncio.run(main())
   ```

#### Acceptance Criteria:
- [ ] MCP server starts successfully
- [ ] All core services are exposed as tools
- [ ] Tool schemas are valid
- [ ] Error handling works correctly
- [ ] Logging captures all operations
- [ ] Performance monitoring is functional

### Task 9: Testing Infrastructure

**Priority**: HIGH - Ensures system reliability
**Dependencies**: Task 8 (MCP Server)
**Estimated Time**: 2-3 days

#### Deliverables:

1. **Test Database Setup**
   ```python
   # Use testcontainers for real database testing
   @pytest.fixture
   def neo4j_container():
       with Neo4jContainer("neo4j:5-community") as container:
           yield container
   
   @pytest.fixture
   def test_databases(neo4j_container):
       # Setup test schemas and data
       yield (neo4j_container, sqlite_db, faiss_index)
   ```

2. **Unit Tests for Core Services**
   - T107 Identity Service tests
   - T110 Provenance Service tests
   - T111 Quality Service tests
   - T121 Workflow State Service tests

3. **Integration Tests**
   - Cross-service interactions
   - Database consistency checks
   - Reference resolution validation
   - Quality propagation testing

#### Acceptance Criteria:
- [ ] All unit tests pass with real databases
- [ ] Integration tests validate cross-service interactions
- [ ] Test coverage >= 85% for core services
- [ ] Performance tests establish baselines
- [ ] Tests run reliably in CI/CD

### Task 10: Documentation and Validation

**Priority**: MEDIUM - Important for future development
**Dependencies**: Task 9 (Testing)
**Estimated Time**: 1-2 days

#### Deliverables:

1. **API Documentation**
   - Core service interfaces
   - MCP tool schemas
   - Usage examples
   - Error handling guide

2. **Integration Testing**
   - End-to-end workflow tests
   - Performance benchmarks
   - Stress testing
   - Error recovery testing

3. **Developer Guide Updates**
   - Setup instructions
   - Development workflows
   - Testing procedures
   - Troubleshooting guide

#### Acceptance Criteria:
- [ ] All APIs are documented with examples
- [ ] Integration tests pass consistently
- [ ] Performance meets baseline requirements
- [ ] Documentation is complete and accurate

## Timeline

**Week 1**: Tasks 1-3 (Infrastructure, References, Data Models)
**Week 2**: Tasks 4-6 (Core Services Implementation)  
**Week 3**: Tasks 7-8 (Workflow State, MCP Server)
**Week 4**: Tasks 9-10 (Testing, Documentation)

## Success Criteria

Upon completion of this milestone:

1. **All Core Services Operational**
   - T107, T110, T111, T121 fully implemented and tested
   - All tools accessible via MCP protocol
   - Quality tracking functional end-to-end

2. **Database Infrastructure Ready**
   - Neo4j, SQLite, FAISS all connected and operational
   - Schemas created with proper indices
   - Reference system working across all databases

3. **Testing Framework Complete**
   - Unit tests for all core services (85%+ coverage)
   - Integration tests for cross-service interactions
   - Performance baselines established

4. **Foundation for Vertical Slice**
   - All blocking dependencies resolved
   - Ready to implement T01, T15a, T23a, etc.
   - MCP server can orchestrate tool execution

## Risk Mitigation

1. **Database Compatibility Issues**
   - Use containerized databases for consistency
   - Implement comprehensive schema validation
   - Test with realistic data volumes

2. **Performance Bottlenecks**
   - Implement connection pooling early
   - Add performance monitoring to all operations
   - Use batch operations where possible

3. **Reference Integrity Problems**
   - Implement reference validation at all levels
   - Add automated integrity checking
   - Design graceful degradation for missing references

4. **Quality Score Inconsistencies**
   - Define clear mathematical formulas for propagation
   - Implement extensive unit tests for edge cases
   - Add validation checks for score consistency

This plan provides a comprehensive roadmap for implementing the Core Services Foundation, ensuring all critical infrastructure is in place before proceeding to the Vertical Slice implementation.