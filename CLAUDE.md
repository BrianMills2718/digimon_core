# CLAUDE.md

**Navigation Guide**: Quick context and pointers to documentation.

## 🎯 Current Status
- **Phase 1**: ✅ Working (484 entities, 228 relationships)
- **Phase 2**: ❌ Broken (API incompatibility)  
- **Phase 3**: 🔧 Standalone only

## 🚨 Critical Issue
**Phase 1→2 Integration Failed**: `current_step` vs `step_number` API mismatch

**Root Cause**: Two parallel implementations diverged:
- Main `/src/` (original, Phase 1 works)
- `super_digimon_implementation/` (attempted rewrite)
- APIs evolved differently, causing integration failure

**⚠️ CRITICAL**: Use only `/src/` - no parallel implementations!

## 📚 Documentation
👉 **[`docs/current/TABLE_OF_CONTENTS.md`](docs/current/TABLE_OF_CONTENTS.md)** - All documentation

**Key Docs**:
- [`STATUS.md`](docs/current/STATUS.md) - What works/broken
- [`ARCHITECTURE.md`](docs/current/ARCHITECTURE.md) - Integration failure analysis
- [`ROADMAP_v2.md`](docs/current/ROADMAP_v2.md) - Fix plan

## ⭐ Immediate Priorities

### Pre-Steps: Directory Examination (Do First!)
Before fixing anything, examine each directory to understand dependencies:
1. **P1**: Examine `/data/` - Runtime data, checkpoints, test results
2. **P2**: Examine `/examples/` - Test documents, sample queries
3. **P3**: Examine `/scripts/` - Utility scripts, setup tools
4. **P4**: Examine `/tests/` - Test infrastructure, integration tests
5. **P5**: Examine `/ui/` - UI implementation, dependencies

Purpose: Identify hidden dependencies, parallel implementations, or integration points before making changes.

### Architecture Fixes (After P1-P5)
1. **A1**: Fix service compatibility
2. **A2**: Design phase interface  
3. **A3**: Build UI adapter
4. **A4**: Integration testing

## 🧪 Quick Test
```bash
python test_phase1_direct.py  # Works: 484 entities
python start_graphrag_ui.py   # Phase 2 selection fails
```

---
**Details**: See [`TABLE_OF_CONTENTS.md`](docs/current/TABLE_OF_CONTENTS.md)