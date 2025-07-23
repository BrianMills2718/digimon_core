# KGAS Documentation Guide

**For current project status and implementation progress, see [ROADMAP_OVERVIEW.md](../ROADMAP_OVERVIEW.md)**

## 📁 Documentation Structure

### Architecture (`/docs/architecture/`)
- **Target state** designs and specifications
- **DO NOT** add implementation progress here
- Only update when architectural goals change

### Roadmap (`/docs/roadmap/`)  
- **Current progress** and planning
- See [ROADMAP.md](./roadmap/CLAUDE.md) for detailed usage
- Update as work progresses

### Development/Operations/API
- Current practices and guides
- Update to reflect actual workflow

## 🔄 Quick Reference

**Check status**: `../ROADMAP_OVERVIEW.md`
**Plan work**: `roadmap/phases/` or `roadmap/initiatives/`  
**Review architecture**: `architecture/` (target state only)

## ⚠️ Key Rules

- Architecture = target design (stable)
- Roadmap = current progress (changes frequently)
- ROADMAP_OVERVIEW.md = single source of truth for status
- ❌ Adding architectural decisions to planning documentation
- ❌ Mixing current state with target state
- ❌ Updating architecture docs for implementation progress
- ❌ Adding temporary workarounds to permanent documentation

---

## 📊 Current Status & Progress

For the most up-to-date information on project status, current development phase, and future plans, please see the master roadmap.

- **[View Master Roadmap & Status →](../ROADMAP_OVERVIEW.md)**

## 📚 Documentation Sections

### 🚀 Getting Started
- [Getting Started](./getting-started/) - User guides, setup instructions, and tutorials.

### 🏛️ Architecture
- **[Architecture Home](./architecture/)** - High-level architectural overview.
- [Concepts](./architecture/concepts/) - Core concepts, theoretical frameworks, and design patterns.
- [Data](./architecture/data/) - Database schemas, data models, and ORM methodology.
- [Specifications](./architecture/specifications/) - Formal specifications, capability registries, and compatibility matrices.
- [Systems](./architecture/systems/) - Detailed design of major system components.
- [ADRs](./architecture/adrs/) - Architecture Decision Records.

### 📈 Planning
- **[Roadmap Overview](../ROADMAP_OVERVIEW.md)** - The master roadmap and current status dashboard.
- [Planning Home](./planning/) - Project planning, strategy, and initiatives.
- [Implementation Phases](./planning/phases/) - Detailed implementation plans for each development phase.
- [Strategy](./planning/strategy/) - High-level strategic and vision documents.
- [Initiatives](./planning/initiatives/) - Plans for specific workstreams (e.g., identity, performance).
- [Analysis](./planning/analysis/) - Initial codebase analysis and discovery.
- [Reports](./planning/reports/) - Project status reports and summaries.

### ⚙️ Development
- **[Development Home](./development/)** - Guides, standards, and practices for developers.
- [Contributing](./development/contributing/) - How to contribute to the project.
- [Guides](./development/guides/) - Development and reproducibility guides.
- [Standards](./development/standards/) - Coding standards, logging, and error handling.
- [Testing](./development/testing/) - Testing, evaluation, and verification procedures.

### 🛠️ Operations
- **[Operations Home](./operations/)** - Running and maintaining the system.
- [Governance](./operations/governance/) - Security, policies, and ethics.
- [Reports](./operations/reports/) - System audit and status reports.

### 📖 API
- [API Reference](./api/) - API documentation and standards.

### 📦 Archive
- [Archive](./archive/) - Historical and legacy documentation.
