# Project Structure Guide

## Root Directory Organization

### 📋 Core Files
- `CLAUDE.md` - Quick navigation and current status
- `README.md` - Project overview and getting started
- `main.py` - Primary entry point
- `requirements*.txt` - Python dependencies

### 📁 Main Directories
- `src/` - **Core KGAS source code** (tools, services, ontology library, MCP server)
- `docs/` - **All documentation** (architecture, planning, development, operations)
- `tests/` - **All test suites** and validation frameworks
- `examples/` - Sample documents and demonstration workflows
- `data/` - Runtime data (ignored by git)
- `config/` - Configuration files and environment settings
- `docker/` - Containerization and deployment configurations

### 🔬 **Production Integration: Automated Theory Extraction**
- `lit_review/` - **Validated theory extraction system** - `src/schema_creation/` - 3-phase extraction pipeline (0.67s response time)
  - `src/schema_application/` - Theory schema application workflows  
  - `evidence/phase6_production_validation/` - Production certification (0.910 score)
  - `examples/` - Working theory extractions (Young 1996, Social Identity Theory)
  - `schemas/` - Generated theory schemas with DOLCE validation

### 🏛️ **KGAS Core Architecture**
- `src/ontology_library/` - **Master Concept Library with DOLCE alignment** - `prototype_mcl.yaml` - DOLCE-validated social science concepts with FOAF/SIOC extensions
  - `prototype_validation.py` - Automated ontological consistency checking
  - `example_theory_schemas/` - Working theory implementations (Social Identity Theory)
- `src/core/` - Core services (orchestration, analytics, identity, provenance)
- `src/tools/` - Phase-based processing tools (Phase 1-3 implementations)
- `src/mcp_server.py` - **Model Context Protocol server** - External tool access for LLM clients (Claude Desktop, ChatGPT)
  - Core service tools (T107: Identity, T110: Provenance, T111: Quality, T121: Workflow)
  - Theory schema application through conversational interfaces

### 🔄 **Integration Architecture**
The project integrates three major systems:
1. **KGAS Core**: Cross-modal analysis with DOLCE validation and MCP protocol access
2. **Theory Extraction**: Validated automated schema generation (0.910 operational score)
3. **MCP Integration**: External tool access enabling natural language orchestration
4. **Integration Bridges**: 
   - Concept mapping and FOAF/SIOC extensions (Complete)
   - Automated theory extraction → MCL integration (In Development)
   - Cross-system quality assurance and governance (Complete)

### 📦 Legacy/Reference Directories  
- `archived/` - Historical implementations and experiments
- `gemini-review-tool/` - External validation and review tools

### 🚀 Launcher Scripts
- `start_graphrag_ui.py` - Main UI launcher
- `start_t301_mcp_server.py` - T301 tools server
- `simple_fastmcp_server.py` - Basic MCP server

## Current Status: Integrated Production System

### **Validated Components** 1. **Automated Theory Extraction**: 0.910 operational score, perfect analytical balance
2. **DOLCE-Aligned MCL**: 16 core concepts with ontological validation
3. **Theory Schema Examples**: Working implementations (Social Identity, Cognitive Mapping)
4. **Integration Architecture**: Clear pathways between extraction and analysis systems

### **Development Priorities** 🚧
1. **Integration Bridge**: Complete cross-system concept mapping and validation
2. **API Integration**: Unified interface for theory extraction and analysis
3. **UI Enhancement**: Integrated user interface for complete workflow
4. **Production Deployment**: Complete integration deployment and scaling

### **Research Innovation** 🎓
The integrated system represents a breakthrough in computational social science:
- **First automated theory extraction** with perfect analytical balance
- **DOLCE-grounded social science** ontology and concept library  
- **Cross-modal intelligence** with theory-aware orchestration
- **Production-grade quality** with comprehensive testing and validation

See [Theory Extraction Integration](./systems/theory-extraction-integration.md) for detailed integration specifications.