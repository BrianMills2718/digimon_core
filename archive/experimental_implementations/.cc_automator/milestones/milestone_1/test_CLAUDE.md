# Test Phase Instructions
- Use subagents to find existing test patterns
- Follow the project's test conventions
- Test edge cases and error conditions
- Keep tests focused and fast

## Milestone 1 Success Criteria:
- T107: Identity Service - Three-level identity management (Surface → Mention → Entity)
- T110: Provenance Service - Complete operation lineage tracking
- T111: Quality Service - Confidence assessment and propagation
- T121: Workflow State Service - Checkpoint/recovery for long operations
- Neo4j Docker container with proper schema and indices
- SQLite database with all required tables (provenance, quality_scores, mentions, etc.)
- FAISS index initialization and management
- Universal reference system implementation (storage://type/id format)
- BaseObject with quality tracking (confidence, quality_tier, warnings, evidence)
- Entity, Mention, Relationship, Chunk, Document models
- Reference resolver for cross-database operations
- Basic MCP server setup with tool registration
- Core services exposed as MCP tools
- Error handling and logging infrastructure
- All core services (T107, T110, T111, T121) operational and tested
- Databases connected and schemas created
- Reference system working across all three databases
- Quality tracking functional
- All tests pass with real database instances
