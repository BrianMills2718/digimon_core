# Super-Digimon Documentation Guide

## For New Developers - Start Here

This guide helps you navigate the documentation and get oriented quickly.

### 🚀 Essential Reading (Read First)
1. **[Project Overview](../README.md)** - What Super-Digimon is and current status
2. **[Development Guidance](../CLAUDE.md)** - Claude Code development instructions
3. **[System Architecture](../ARCHITECTURE.md)** - Technical architecture and decisions
4. **[Implementation Roadmap](../IMPLEMENTATION.md)** - Development phases and approach

### 📋 Authoritative Specifications (Implementation Reference)
- **[Complete Tool Specifications](specifications/SUPER_DIGIMON_COMPLETE_TOOL_SPECIFICATIONS.md)** - All 106 tools detailed
- **[Tool Architecture Summary](specifications/TOOL_ARCHITECTURE_SUMMARY.md)** - Phase organization and breakdown
- **[Canonical Decisions](decisions/CANONICAL_DECISIONS_2025.md)** - Final architectural decisions

### 🔧 Implementation Guidance
- **[JayLZhou Mapping](specifications/JAYZHOU_MCP_TOOL_MAPPING.md)** - Core GraphRAG operators
- **[Graph Attributes](specifications/GRAPH_ATTRIBUTES_SPECIFICATION.md)** - Data structures
- **[Advanced Features](specifications/ADVANCED_FEATURES_SPECIFICATION.md)** - Future capabilities

### 📚 Reference Materials (Optional Reading)
- **[Reference Directory](reference/)** - Analysis reports, deployment guides, examples
- **[Planning History](../docs/archive/historical_planning/)** - Historical planning documents

## Quick Orientation

### What is Super-Digimon?
- **System**: 106 tools across 7 phases for GraphRAG analysis
- **Scope**: Prototype (functionally complete, not production-ready)
- **Status**: Specification phase, ready for implementation
- **Architecture**: Single MCP server + Triple database (Neo4j + SQLite + FAISS)

### Implementation Status
- **Super-Digimon Tools**: 0 of 106 implemented (target system)
- **CC_Automator**: Separate development/testing tool (not the target system)
- **Next**: Begin Phase 0 infrastructure setup

### Development Approach
1. **Phase 0**: Infrastructure (Docker, databases, MCP framework)
2. **Phase 1-3**: Data pipeline (T01-T48) - Ingestion through construction
3. **Phase 4**: Core GraphRAG (T49-T67) - JayLZhou operators
4. **Phase 5-7**: Advanced features (T68-T106) - Analysis and interface

### Technology Stack
- **Language**: Python 3.11+
- **Protocol**: Model Context Protocol (MCP) - Single server
- **Databases**: Neo4j (graphs) + SQLite (metadata) + FAISS (vectors)
- **Development**: Hybrid workflow (local code + Docker services)
- **Runtime**: Claude Code (claude.ai/code)

## Documentation Organization

### Current Documents (Use These)
```
docs/
├── README.md                    # This navigation guide
├── specifications/              # Technical specifications and tool details
├── decisions/                   # Current architectural decisions
├── reference/                   # Analysis reports and guides
└── archive/                     # Historical documents (reference only)
```

### Root Documents (Essential)
```
/
├── README.md                    # Project overview
├── CLAUDE.md                    # Development guidance
├── ARCHITECTURE.md              # System architecture
└── IMPLEMENTATION.md            # Development roadmap
```

## Common Questions

### Q: Which documents are authoritative?
**A**: Follow this hierarchy:
1. `docs/decisions/CANONICAL_DECISIONS_2025.md` - Final decisions
2. Root documents (README, CLAUDE, ARCHITECTURE, IMPLEMENTATION)
3. `docs/specifications/` - Technical specifications
4. Everything else is reference or historical

### Q: What's the difference between Super-Digimon and CC_Automator?
**A**: 
- **Super-Digimon**: The target system (106 tools, 0 implemented)
- **CC_Automator**: Separate development/testing tool with existing code

### Q: What should I implement first?
**A**: Follow `IMPLEMENTATION.md` - Start with Phase 0 infrastructure setup

### Q: Which architectural decisions are current?
**A**: Use `docs/decisions/CANONICAL_DECISIONS_2025.md` only. Other decision documents are historical.

### Q: How do I know if a document is outdated?
**A**: If it's in `docs/archive/`, it's historical. If it contradicts CANONICAL_DECISIONS_2025.md, report the inconsistency.

## Getting Started Checklist

- [ ] Read project overview (README.md)
- [ ] Understand development approach (CLAUDE.md)
- [ ] Review system architecture (ARCHITECTURE.md)
- [ ] Check implementation roadmap (IMPLEMENTATION.md)
- [ ] Review canonical decisions (docs/decisions/CANONICAL_DECISIONS_2025.md)
- [ ] Examine tool specifications (docs/specifications/)
- [ ] Set up development environment (follow CLAUDE.md guidance)

---

**Last Updated**: 2025-06-12  
**Purpose**: Navigation guide for Super-Digimon documentation  
**Audience**: New developers and contributors