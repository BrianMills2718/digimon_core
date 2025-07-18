# Project Structure Guide

## Root Directory Organization

### 📋 Core Files
- `CLAUDE.md` - Quick navigation and current status
- `README.md` - Project overview and getting started
- `main.py` - Primary entry point
- `requirements*.txt` - Python dependencies

### 📁 Main Directories
- `src/` - Source code (tools, core services, MCP server)
- `docs/` - All documentation (current, planned, archive)
- `ui/` - User interface components (Streamlit apps)
- `examples/` - Sample PDFs and test documents
- `tests/` - Organized test suites
- `data/` - Runtime data (ignored by git)

### 🧪 Test Files in Root
**Why they're here**: Active development - frequently run for validation
- `test_phase1_direct.py` - Validates Phase 1 extraction
- `test_ui_real.py` - UI functionality tests
- `test_t301_*.py` - Phase 3 fusion tool tests
- Other `test_*.py` - Various integration tests

### 📦 Legacy/Reference Directories
- `archive/` - Old implementations and experiments
- `cc_automator4/` - Related automation tool
- `super_digimon_implementation/` - Original implementation reference

### 🚀 Launcher Scripts
- `start_graphrag_ui.py` - Main UI launcher
- `start_t301_mcp_server.py` - T301 tools server
- `simple_fastmcp_server.py` - Basic MCP server

## Future Cleanup (Post-Architecture Fix)
Once A1-A4 priorities are complete and integration is stable:
1. Move test files to `tests/` with proper imports
2. Archive legacy implementations
3. Consolidate launcher scripts

## Current Focus
Maintaining stability while fixing Phase 1→2 integration issues.
See [`docs/planning/roadmap.md`](planning/roadmap.md) for priorities.