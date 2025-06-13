# Super-Digimon Architecture Decisions

**Last Updated**: January 6, 2025  
**Status**: Authoritative Architecture Document

## Purpose

This document consolidates all architectural decisions for Super-Digimon into a single, authoritative source. It supersedes any conflicting information in other documents.

## Core Decisions

### 1. Project Scope & Status

**Decision**: Super-Digimon is a GraphRAG system specification with no current implementation.

**Rationale**: 
- Previous implementations (CC2, StructGPT, GraphRAG_fresh) were removed to start fresh
- Clean specification allows for better architecture without legacy constraints

**Implications**:
- All implementation will be from scratch
- Can incorporate best practices from removed projects
- No technical debt from previous attempts

### 2. Tool Architecture

**Decision**: 26 core GraphRAG tools (T01-T26), with vision for 106 total tools in future.

**Rationale**:
- 26 tools cover essential GraphRAG operations
- Based on JayLZhou paper and proven patterns
- Future expansion planned but not committed

**Implications**:
- Focus development on 26 core tools first
- Design with extensibility in mind
- Don't over-engineer for 106 tools initially

### 3. Storage Strategy

**Decision**: Neo4j as primary database, with tool-managed storage for other needs.

**Rationale**:
- Neo4j proven for graph operations
- Avoid premature optimization with multiple databases
- Tools can manage their own storage needs (vectors, metadata)

**Implications**:
- All graph data in Neo4j
- No separate FAISS or SQLite requirement initially
- Tools responsible for their storage optimization

### 4. Development Approach

**Decision**: Prototype-first, functionality over performance.

**Rationale**:
- Research prototype, not production system
- Need to validate GraphRAG approach first
- Optimization can come later

**Implications**:
- Simple, readable code preferred
- No premature optimization
- Focus on correctness over speed

### 5. Runtime Environment

**Decision**: Python tools exposed via MCP to Claude Code.

**Rationale**:
- Claude Code provides natural language understanding
- MCP is the standard protocol
- Python has best ML/graph libraries

**Implications**:
- All tools implemented in Python
- MCP server required for integration
- Claude Code handles orchestration

### 6. Implementation Language

**Decision**: Python 3.11+ with type hints (no PydanticAI).

**Rationale**:
- Python standard in ML/data science
- Type hints provide safety without overhead
- PydanticAI adds complexity without clear benefit

**Implications**:
- Use stdlib typing module
- Dataclasses for data structures
- No external validation frameworks initially

### 7. Deployment Strategy

**Decision**: Docker for services, local development for code.

**Rationale**:
- Neo4j easier to manage in Docker
- Local development faster for iteration
- Can dockerize everything later

**Implications**:
- docker-compose.yml for Neo4j
- Python code runs locally
- Simple deployment initially

### 8. Testing Strategy

**Decision**: Test with Celestial Council dataset first.

**Rationale**:
- Small, well-understood dataset
- Covers all GraphRAG operations
- Can validate against expected results

**Implications**:
- All tools must work with this dataset
- Use as integration test suite
- Expand to other datasets later

### 9. Documentation Strategy

**Decision**: Implementation guides over research documents.

**Rationale**:
- Need actionable documentation
- Too much theory without implementation
- Focus on helping developers build

**Implications**:
- Prioritize code examples
- Document as we build
- Remove purely theoretical docs

### 10. Success Criteria

**Decision**: Working system that can answer questions about graph data via natural language.

**Rationale**:
- Clear, measurable goal
- Demonstrates value proposition
- Can be achieved incrementally

**Implications**:
- Each tool must contribute to this goal
- Natural language is the interface
- Results must be explainable

## Non-Decisions (Explicitly Not Decided)

1. **Performance Targets**: No specific latency/throughput requirements
2. **Scalability**: Single-user system, no distributed architecture
3. **Security**: Trusted environment assumed
4. **Multi-tenancy**: Not supported
5. **Production Features**: No monitoring, alerting, or ops tools

## Decision Record

All architectural changes should be documented here with:
- Date of decision
- Rationale for change
- Impact on existing system
- Migration strategy if needed

## Superseded Documents

This document supersedes architectural decisions in:
- Various README files with conflicting information
- Research documents proposing complex architectures
- Planning documents with unrealistic scopes

## How to Use This Document

1. **For Developers**: Follow these decisions when implementing
2. **For Contributors**: Propose changes via issues/PRs
3. **For Users**: Understand system limitations and design choices

## Future Considerations

As the system evolves, we may need to revisit:
- Storage strategy if performance becomes issue
- Tool architecture if 26 tools insufficient
- Deployment if multi-user support needed

But these are **future** considerations, not current requirements.