**Doc status**: Living – auto-checked by doc-governance CI

# Tool Count Clarification

**Status**: ✅ CLARIFIED - Consistent tool count accounting established  
**Issue**: Multiple conflicting tool counts across documentation  
**Resolution**: Clear categorization and counting methodology

## 🔢 Official Tool Count

### Core GraphRAG Tools: 13
These are the fundamental tools implementing the core GraphRAG pipeline:
- **Phase 1**: PDF loading, chunking, entity/relationship extraction, graph building, PageRank, queries
- **Phase 2**: Ontology generation and ontology-aware extraction
- **Phase 3**: Multi-document fusion capabilities

### MCP Server Tools: 20
Additional tools exposed through the Model Context Protocol (MCP):
- Pipeline control tools
- Graph manipulation tools
- Query and visualization tools
- Administrative tools

### Total Available Tools: 33
**13 core tools + 20 MCP tools = 33 total tools**

## 📊 Tool Implementation Progress

### Against Original Vision
- **Planned**: 121 universal analytics tools (aspirational vision)
- **Implemented**: 13 core GraphRAG tools
- **Progress**: 11% of original universal analytics vision

### Current Reality
- **Functional**: 13 core tools (verified working)
- **MCP Exposed**: 20 additional tools via MCP protocol
- **Total Accessible**: 33 tools for users

## 🎯 Why the Confusion?

1. **Evolution of Scope**: Project evolved from universal analytics (121 tools) to focused GraphRAG (13 tools)
2. **MCP Addition**: 20 MCP tools added later, creating multiple counting methods
3. **Documentation Lag**: Different documents updated at different times

## ✅ Standard Reporting

When reporting tool counts, use:
- **"13 core GraphRAG tools"** - for core functionality
- **"33 total tools (13 core + 20 MCP)"** - for total available tools
- **"11% of original 121-tool vision"** - for historical context

## 📋 Verification Commands

```bash
# Count core tools
ls -la src/tools/phase*/t*.py | wc -l

# List MCP tools
python -c "from src.mcp_server import list_tools; print(f'MCP tools: {len(list_tools())}')"

# Verify functional tools
python tests/functional/test_tool_verification.py
```

---

**Last Updated**: 2025-06-19  
**Purpose**: Eliminate tool count confusion across documentation-e 
<br><sup>See `docs/planning/roadmap.md` for master plan.</sup>
