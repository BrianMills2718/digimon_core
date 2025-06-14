# Canonical Decisions for Super-Digimon (2025-06-12)

## Purpose
This document establishes the **single source of truth** for all major architectural and scope decisions, resolving documentation inconsistencies identified in external review.

## Critical Decisions (Final)

### 1. Tool Count: 106 Tools (Authoritative)
**Decision**: Super-Digimon consists of **106 tools** across 7 phases
**Rationale**: This is the complete, authoritative specification
**Status**: ✅ FINAL

**Tool Breakdown**:
- Phase 1 (Ingestion): T01-T12 (12 tools)
- Phase 2 (Processing): T13-T30 (18 tools) 
- Phase 3 (Construction): T31-T48 (18 tools)
- Phase 4 (Retrieval): T49-T67 (19 tools) - JayLZhou operators + infrastructure
- Phase 5 (Analysis): T68-T75 (8 tools)
- Phase 6 (Storage): T76-T81 (6 tools)
- Phase 7 (Interface): T82-T106 (25 tools)

**Deprecated References**:
- ❌ "102 tools" (optimization attempt, rejected for complexity)
- ❌ "26 tools" (historical reference, incomplete)
- ❌ "19 operators" (subset of Phase 4 only)
- ❌ "~110 tools" (estimation, superseded)

### 2. Implementation Status: Specification Phase
**Decision**: No current implementation exists, project is in specification phase
**Status**: ✅ FINAL

**Current State**:
- Implementation progress: 0 of 106 tools implemented
- Phase: Architecture and specification complete, ready for implementation
- Development approach: From-scratch implementation based on specifications

**Deprecated References**:
- ❌ "CC2 implementation exists" (archived/deleted projects)
- ❌ "Fork existing implementation" (no valid implementation to fork)
- ❌ Any references to working implementations

### 3. Database Architecture: Triple Database System
**Decision**: Neo4j + SQLite + FAISS mandatory architecture
**Status**: ✅ FINAL

**Architecture**:
- **Neo4j**: Graph storage (entities, relationships, communities)
- **SQLite**: Metadata storage (documents, configuration, lineage)
- **FAISS**: Vector search index (embeddings, similarity search)

**Rationale**: Each database optimized for its data type and access patterns

**Deprecated References**:
- ❌ "Neo4j first, others as needed" (incomplete architecture)
- ❌ "Tool-managed storage" (too vague)

### 4. MCP Server Architecture: Single Server
**Decision**: Single MCP server exposing all 106 tools
**Status**: ✅ FINAL

**Architecture**:
- One MCP server process
- All 106 tools exposed via single protocol endpoint
- Tools internally organized by phase but externally unified

**Rationale**: Simplicity over scalability for prototype phase

**Deprecated References**:
- ❌ "Federated 3-server architecture" (over-engineering for prototype)
- ❌ "Phase-specific MCP servers" (unnecessary complexity)

### 5. Project Scope: Prototype
**Decision**: Building a "Prototype" - functionally complete but not production-ready
**Status**: ✅ FINAL

**Definition**:
- **Prototype**: All 106 tools functional, demonstrates complete GraphRAG workflow
- **Not MVP**: Not minimum viable, but maximum prototype functionality
- **Not Production**: No scalability, security, or enterprise features

**Deprecated References**:
- ❌ "MVP" terminology (confusing scope)
- ❌ "Production system" references

### 6. Development Environment: Hybrid Workflow
**Decision**: Local Python development + Docker for stateful services
**Status**: ✅ FINAL

**Workflow**:
- **Local**: Python code, MCP server, tool development
- **Docker**: Neo4j, database services, isolated environments
- **Hybrid**: Best of both worlds for rapid development

**Deprecated References**:
- ❌ "Full Docker deployment" for development (too slow)
- ❌ "All local" development (database setup complexity)

## Implementation Priority

**Phase Order** (based on 106-tool specification):
1. **Phase 0**: Infrastructure setup (Docker, databases, MCP framework)
2. **Phase 1-3**: Data pipeline (T01-T48) - Ingestion through construction
3. **Phase 4**: Core GraphRAG (T49-T67) - JayLZhou operators
4. **Phase 5-7**: Advanced features (T68-T106) - Analysis and interface

## Authoritative Documents

**These documents are CANONICAL**:
- `docs/specifications/SUPER_DIGIMON_COMPLETE_TOOL_SPECIFICATIONS.md` - 106 tool specs
- `ARCHITECTURE.md` - System architecture
- `IMPLEMENTATION.md` - Development roadmap
- This document (`CANONICAL_DECISIONS_2025.md`)

**All other documents must align with these or be marked as deprecated.**

## Document Update Status

Following this decision, these documents need updates:
- [ ] Remove conflicting tool counts throughout documentation
- [ ] Remove references to existing implementations
- [ ] Standardize on triple database architecture
- [ ] Remove federated MCP references
- [ ] Standardize on "Prototype" terminology
- [ ] Clarify hybrid development workflow

---

**Last Updated**: 2025-06-12  
**Review Status**: External review completed, inconsistencies identified and resolved  
**Authority**: This document supersedes all conflicting architectural decisions