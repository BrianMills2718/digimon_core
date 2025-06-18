# CLAUDE.md

**Navigation Guide**: Quick context and pointers to documentation.

## 🎯 Current Status
- **Phase 1**: ✅ Working (484 entities, 228 relationships)
- **Phase 2**: ✅ Working (API compatibility fixed, uses standardized interface)
- **Phase 3**: 🔧 Standalone only (T301 multi-document fusion working)
- **Architecture**: ✅ All fixes complete (A1-A4)

## 🚨 Critical Configuration
**⚠️ GEMINI MODEL**: Must use `gemini-2.5-flash` (1000 RPM limit)
- DO NOT change to `gemini-2.0-flash-exp` (10 RPM limit) 
- DO NOT use experimental models - they have severe quota restrictions
- This is hardcoded in 4 files - search for "gemini-2.5-flash" before changing

**✅ FIXED**: Phase 1→2 integration (A1 complete)
- Changed `current_step` → `step_number` 
- Fixed OpenAI API compatibility
- Phase 2 now works but needs API keys

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

### Architecture Fixes ✅ COMPLETE
1. **A1**: ✅ Service compatibility - Fixed API parameter mismatch
2. **A2**: ✅ Phase interface contract - Standardized all phase interactions
3. **A3**: ✅ UI adapter pattern - Isolated UI from phase implementations
4. **A4**: ✅ Integration testing - Comprehensive test framework prevents future failures

## 🧪 Quick Test
```bash
# Legacy individual phase tests
python test_phase1_direct.py  # Phase 1: 484 entities
python test_phase2_integration_fix.py  # Phase 2: Fixed integration

# New standardized interface tests  
python test_interface_structure.py  # A2: Phase interface compliance
python test_ui_adapter.py  # A3: UI adapter functionality
python test_integration_a4.py  # A4: Full integration testing

# UI Options
python start_graphrag_ui.py  # Original UI (Phase 1 + Phase 2)
python start_graphrag_ui_v2.py  # New UI with standardized interface
```

---
**Details**: See [`TABLE_OF_CONTENTS.md`](docs/current/TABLE_OF_CONTENTS.md)