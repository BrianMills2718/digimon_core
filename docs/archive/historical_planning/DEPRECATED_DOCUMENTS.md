# Deprecated Documents (2025-06-12)

## Purpose
This document lists documents that contain **conflicting information** and should not be used for current development decisions. They are preserved for historical context only.

## Deprecated Documents

### ❌ docs/specifications/OPTIMIZED_TOOL_SPECIFICATIONS.md
**Reason**: Proposes 102-tool optimization that conflicts with canonical 106-tool specification  
**Conflict**: Tool count (102 vs 106) and federated MCP architecture  
**Status**: Historical optimization attempt, rejected for complexity  

### ❌ docs/decisions/ARCHITECTURAL_DECISIONS.md  
**Reason**: Contains mix of current and superseded decisions  
**Conflict**: Multiple tool counts, MCP architecture decisions  
**Status**: Partially superseded by CANONICAL_DECISIONS_2025.md  

### ❌ docs/planning/PRAGMATIC_MVP_PLAN.md
**Reason**: Uses "MVP" terminology instead of canonical "Prototype"  
**Conflict**: Scope definition and terminology  
**Status**: Superseded by canonical scope decision  

### ❌ docs/reference/COMPARATIVE_ANALYSIS_REPORT.md
**Reason**: References archived implementations (CC2) as if they exist  
**Conflict**: Implementation status  
**Status**: Historical analysis, implementations no longer exist  

### ❌ docs/decisions/ARCHITECTURE_CLARIFICATIONS.md
**Reason**: Contains multiple conflicting tool counts and architectures  
**Conflict**: Tool count (26 vs 106), database architecture  
**Status**: Early clarification attempt, superseded  

### ❌ docs/planning/FINAL_SUPER_DIGIMON_ROADMAP.md  
**Reason**: Contains outdated tool counts and implementation assumptions  
**Conflict**: Implementation status, tool organization  
**Status**: Superseded by IMPLEMENTATION.md  

## How to Handle Deprecated Documents

### For Developers
- ❌ **Do NOT use** these documents for current architectural decisions
- ✅ **Use instead**: CANONICAL_DECISIONS_2025.md + core documents (README, ARCHITECTURE, IMPLEMENTATION)
- ⚠️ **Historical value**: May contain useful research or analysis

### For Updates
- Documents are **preserved** for historical context
- Should be marked with deprecation notices if referenced
- New decisions should be made in canonical documents only

## Canonical Documents (Use These)

### **Primary Authority**
1. `docs/decisions/CANONICAL_DECISIONS_2025.md` - All major decisions
2. `README.md` - Project overview
3. `ARCHITECTURE.md` - System architecture  
4. `IMPLEMENTATION.md` - Development roadmap

### **Specifications**
1. `docs/specifications/SUPER_DIGIMON_COMPLETE_TOOL_SPECIFICATIONS.md` - 106 tool specs
2. `docs/specifications/TOOL_ARCHITECTURE_SUMMARY.md` - Phase organization

### **Reference**
1. `docs/specifications/JAYZHOU_MCP_TOOL_MAPPING.md` - JayLZhou operator mapping

## Resolution Summary

**External Review Date**: 2025-06-12  
**Inconsistencies Identified**: 6 major contradictions  
**Resolution Method**: Canonical decisions established  
**Documents Updated**: Core architecture documents aligned  
**Documents Deprecated**: 6 conflicting documents marked as historical  

---

**Important**: When multiple documents conflict, **CANONICAL_DECISIONS_2025.md** takes precedence.