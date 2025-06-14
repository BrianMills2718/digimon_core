# Super-Digimon Documentation

Welcome to the Super-Digimon GraphRAG system documentation.

## Quick Navigation

### Getting Started
- [Implementation Roadmap](/IMPLEMENTATION_ROADMAP.md) - Start here!
- [Development Guide](core/DEVELOPMENT_GUIDE.md) - Set up your environment
- [Architecture Overview](core/ARCHITECTURE.md) - Understand the system

### Core Documentation
Located in `docs/core/`:
- **[ARCHITECTURE.md](core/ARCHITECTURE.md)** - System design and technology stack
- **[SPECIFICATIONS.md](core/SPECIFICATIONS.md)** - All 106 tool specifications
- **[DEVELOPMENT_GUIDE.md](core/DEVELOPMENT_GUIDE.md)** - How to build the system
- **[DESIGN_PATTERNS.md](core/DESIGN_PATTERNS.md)** - Key patterns and best practices

### Project Information
Located in `docs/project/`:
- **[HISTORY.md](project/HISTORY.md)** - Project evolution and decisions
- **[DOCUMENTATION_REFACTORING_PLAN.md](project/DOCUMENTATION_REFACTORING_PLAN.md)** - How we consolidated docs
- **[reviews/](project/reviews/)** - Documentation review findings

### Historical Archive
Located in `docs/archive/`:
- **[2025-01-13-pre-refactor/](archive/2025-01-13-pre-refactor/)** - All original documentation (87 files)
- Contains historical planning, deprecated approaches, and earlier versions

## Documentation Structure

```
docs/
├── core/               # Essential technical documentation
├── project/            # Project management and history
└── archive/            # Historical documentation
```

## Key Facts

- **106 tools** organized in **7 phases**
- **Single MCP server** architecture
- **Triple database**: Neo4j + FAISS + SQLite
- **0% implemented** - Starting fresh with clean specifications

## Where to Start

1. **New Developer?** Read [IMPLEMENTATION_ROADMAP.md](/IMPLEMENTATION_ROADMAP.md)
2. **Setting Up?** Follow [DEVELOPMENT_GUIDE.md](core/DEVELOPMENT_GUIDE.md)
3. **Understanding Architecture?** Study [ARCHITECTURE.md](core/ARCHITECTURE.md)
4. **Implementing Tools?** Reference [SPECIFICATIONS.md](core/SPECIFICATIONS.md)
5. **Best Practices?** Apply [DESIGN_PATTERNS.md](core/DESIGN_PATTERNS.md)

## Documentation Status

**Consolidation Complete** (January 13, 2025):
- Reduced from 87 files to <20 active files
- All historical content preserved in archive
- Single source of truth for each topic
- Ready for implementation to begin

---

**Last Updated**: January 13, 2025  
**Purpose**: Central navigation for Super-Digimon documentation  
**Next Step**: Begin Phase 0 implementation (see roadmap)