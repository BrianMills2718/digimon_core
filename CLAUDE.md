# CLAUDE.md

**Navigation Guide**: Quick context and pointers to documentation.

## 🎯 Current Status
- **Phase 1**: ✅ Working (484 entities, 228 relationships)
- **Phase 2**: ✅ Fixed (A1 complete - API compatibility resolved)
- **Phase 3**: 🔧 Standalone only

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

### Architecture Fixes
1. **A1**: ✅ Fix service compatibility (COMPLETE)
2. **A2**: Design phase interface (Next)
3. **A3**: Build UI adapter  
4. **A4**: Integration testing

## 🧪 Quick Test
```bash
python test_phase1_direct.py  # Works: 484 entities
python test_phase2_integration_fix.py  # Works with gemini-2.5-flash
python start_graphrag_ui.py   # Phase 2 now selectable!
```

---
**Details**: See [`TABLE_OF_CONTENTS.md`](docs/current/TABLE_OF_CONTENTS.md)