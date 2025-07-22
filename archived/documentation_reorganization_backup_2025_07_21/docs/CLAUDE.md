# KGAS Documentation Hub

Welcome to the Knowledge Graph Analysis System (KGAS) documentation. This hub provides a central entry point to all documentation related to the project's architecture, planning, and operations.

## 📋 Documentation Management Guidelines

**CRITICAL: Read this section before accessing or editing any documentation.**

### 🏗️ Architecture Documentation (`/architecture/`)
- **Purpose**: Represents the **target/final architecture** - the goal state
- **Content**: System design, component relationships, interfaces, data flows, architectural decisions
- **Should NOT change** unless the architectural goals change
- **Should NOT contain** current implementation status, progress percentages, or known issues
- **Examples**: Component diagrams, interface specifications, data models, ADRs

### 📈 Planning Documentation (`/planning/`)
- **Purpose**: Represents the **current state and path to the goal**
- **Content**: Roadmap, implementation plan, current progress, issues, tasks, analysis
- **Should change** as implementation progresses and issues are discovered
- **Examples**: Roadmap status, implementation tasks, progress reports, issue tracking

### 🚀 Development Documentation (`/development/`)
- **Purpose**: Guides for developers working on the system
- **Content**: Contributing guidelines, coding standards, testing procedures
- **Should reflect** current development practices and requirements

### ⚙️ Operations Documentation (`/operations/`)
- **Purpose**: Guides for running and maintaining the system
- **Content**: Deployment, monitoring, governance, security
- **Should reflect** current operational requirements and procedures

### 📖 API Documentation (`/api/`)
- **Purpose**: Reference for system interfaces
- **Content**: API specifications, endpoints, data formats
- **Should reflect** the current API design and implementation

### 📦 Archive Documentation (`/archive/`)
- **Purpose**: Historical reference and legacy documentation
- **Content**: Previous versions, deprecated features, historical decisions
- **Should be preserved** for reference but not actively maintained

### 🔄 Documentation Update Process
1. **Identify the correct section** for your changes
2. **Verify the purpose** of the documentation you're editing
3. **Make changes** that align with the section's purpose
4. **Update cross-references** if your changes affect other documents
5. **Run verification** to ensure documentation accuracy

### ⚠️ Common Mistakes to Avoid
- ❌ Adding implementation status to architecture documentation
- ❌ Adding architectural decisions to planning documentation
- ❌ Mixing current state with target state
- ❌ Updating architecture docs for implementation progress
- ❌ Adding temporary workarounds to permanent documentation

---

## 📊 Current Status & Progress

For the most up-to-date information on project status, current development phase, and future plans, please see the master roadmap.

- **[View Master Roadmap & Status →](./planning/roadmap.md)**

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
- **[Planning Home](./planning/)** - Project planning, strategy, and initiatives.
- [Roadmap](./planning/roadmap.md) - The master roadmap and status dashboard.
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
