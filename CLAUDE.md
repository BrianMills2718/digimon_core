# CLAUDE.md

**Navigation Guide**: Quick context and pointers to documentation.

## 🎯 Current Status
- **Phase 1**: ⚠️ Extracts data (484 entities, 228 relationships) but PageRank fails
- **Phase 2**: ⚠️ API fixed but Gemini parsing issues  
- **Phase 3**: ✅ MCP tools working (5 fusion tools available)
- **Architecture**: ✅ All fixes complete (A1-A4) - Integration failures prevented

## 🚨 Critical Configuration
**⚠️ GEMINI MODEL**: Must use `gemini-2.5-flash` (1000 RPM limit)
- DO NOT change to `gemini-2.0-flash-exp` (10 RPM limit) 
- DO NOT use experimental models - they have severe quota restrictions
- This is hardcoded in 4 files - search for "gemini-2.5-flash" before changing

**✅ ARCHITECTURE COMPLETE**: All integration fixes done (A1-A4)
- A1: Service compatibility - API parameter mismatch resolved
- A2: Phase interface contract - Standardized all phase interactions
- A3: UI adapter pattern - UI isolated from phase implementations  
- A4: Integration testing - Framework prevents future failures

**⚠️ OPERATIONAL ISSUES**: Data extraction works, graph building fails
- Entity extraction: ✅ Working (484 entities, 228 relationships)
- PageRank error: "None cannot be a node" - needs debugging
- Gemini parsing: JSON response parsing failures

## 📚 Documentation
👉 **[`docs/current/TABLE_OF_CONTENTS.md`](docs/current/TABLE_OF_CONTENTS.md)** - All documentation

**Key Docs**:
- [`STATUS.md`](docs/current/STATUS.md) - What works/broken
- [`ARCHITECTURE.md`](docs/current/ARCHITECTURE.md) - Integration failure analysis
- [`ROADMAP_v2.md`](docs/current/ROADMAP_v2.md) - Fix plan

## ⭐ Immediate Priorities

### Pre-Steps: Directory Examination ✅ COMPLETE
See [`DIRECTORY_EXAMINATION_REPORT.md`](docs/current/DIRECTORY_EXAMINATION_REPORT.md)

**Key Finding**: Phase 2 calls `update_workflow_progress(current_step=9)` but service expects `step_number`

### ⭐ Next Priorities (Operational Debugging)

#### B1: Fix PageRank Graph Building 🔥 URGENT
- **Issue**: "None cannot be a node" error in Phase 1
- **Impact**: Blocks all end-to-end workflows  
- **Debug**: Check entity/relationship node creation in graph builder
- **Files**: `src/tools/phase1/t68_pagerank.py`, `src/tools/phase1/t31_entity_builder.py`

#### B2: Fix Gemini JSON Parsing 
- **Issue**: "Unterminated string" and "Invalid JSON" in Phase 2
- **Impact**: Ontology generation fails
- **Debug**: Check response cleaning and JSON validation
- **Files**: `src/ontology/gemini_ontology_generator.py`

#### B3: Complete MCP Tool Exposure
- **Issue**: Only 5/expected tools properly exposed
- **Impact**: Limited MCP functionality
- **Debug**: Check tool imports and registration
- **Files**: `src/tools/phase3/t301_multi_document_fusion_tools.py`

### Architecture Fixes ✅ COMPLETE
1. **A1**: ✅ Service compatibility - Fixed API parameter mismatch
2. **A2**: ✅ Phase interface contract - Standardized all phase interactions
3. **A3**: ✅ UI adapter pattern - Isolated UI from phase implementations
4. **A4**: ✅ Integration testing - Comprehensive test framework prevents future failures

## 🧪 Quick Test
```bash
# Current Status Testing
python test_end_to_end_real.py  # Real data processing (shows PageRank issue)
python test_phase1_direct.py  # Phase 1: 484 entities extracted, PageRank fails

# Architecture Verification (All Working)
python test_interface_structure.py  # A2: Phase interface compliance ✅
python test_ui_adapter.py  # A3: UI adapter functionality ✅
python test_integration_a4.py  # A4: Integration testing ✅

# MCP Tools
python start_t301_mcp_server.py  # Phase 3: 5 fusion tools available

# UI Options (Both Work but Affected by PageRank Issue)
python start_graphrag_ui.py  # Original UI 
python start_graphrag_ui_v2.py  # New UI with standardized interface ✅
```

---
**Details**: See [`TABLE_OF_CONTENTS.md`](docs/current/TABLE_OF_CONTENTS.md)