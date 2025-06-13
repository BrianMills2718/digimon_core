# Documentation Archive

## Purpose
This directory contains **historical documentation** that has been superseded by current specifications but is preserved for reference and context.

## ⚠️ Important Notice
**DO NOT USE** these documents for current development decisions. They contain outdated information that conflicts with canonical decisions.

## Archive Contents

### Historical Planning (`historical_planning/`)
Documents from various planning iterations that have been superseded:

#### Completed Documentation Work
- `DOCUMENTATION_CLEANUP_PLAN.md` - Original cleanup strategy (completed)
- `DOCUMENTATION_CLEANUP_SUMMARY.md` - Cleanup results (completed)
- `DOCUMENTATION_REORGANIZATION_PLAN.md` - File reorganization strategy (completed)
- `DOCUMENTATION_REVIEW_LOG.md` - Review process log (historical)
- `DOCUMENTATION_REVIEW_REPORT.md` - Review findings (historical)

#### Superseded Planning Documents
- `PRAGMATIC_ARCHITECTURE_REVISION.md` - Early architecture attempt (superseded)
- `PRAGMATIC_MVP_PLAN.md` - MVP planning (superseded by Prototype scope)
- `FINAL_SUPER_DIGIMON_ROADMAP.md` - Early roadmap (superseded by IMPLEMENTATION.md)
- `ATTRIBUTE_BASED_IMPLEMENTATION_PLAN.md` - Implementation approach (superseded)

#### Historical Analysis
- `SUPER_DIGIMON_CRITIQUES_AND_RESPONSES.md` - Early project analysis (historical)
- `SUPER_DIGIMON_AGENT_ARCHITECTURE.md` - Agent design exploration (historical)
- `SUPER_DIGIMON_DEVELOPMENT_CHECKPOINTS.md` - Early milestones (superseded)
- `SUPER_DIGIMON_IMPLEMENTATION_PRIORITIES.md` - Priority analysis (superseded)
- `SUPER_DIGIMON_NEXT_STEPS.md` - Early action items (superseded)

#### Deprecated Architectural Decisions
- `ARCHITECTURAL_DECISIONS_HISTORICAL.md` - Mixed current/superseded decisions (use CANONICAL_DECISIONS_2025.md instead)
- `DEPRECATED_DOCUMENTS.md` - List of deprecated documents (moved to archive)

#### Historical Context
- `CLAUDE_HISTORICAL.md` - Early Claude guidance (superseded by root CLAUDE.md)
- `UKRF_INTEGRATION_COORDINATION_PLAN_probably_oudated.md` - UKRF integration planning (outdated)

## Why These Documents Are Archived

### 1. Superseded by Canonical Decisions
Most planning documents were created during iterative decision-making. Final decisions are now in:
- `docs/decisions/CANONICAL_DECISIONS_2025.md` - **Use this for all decisions**

### 2. Completed Work
Documentation cleanup, reorganization, and review work has been completed. Results are reflected in current documentation structure.

### 3. Scope Changes
- **MVP → Prototype**: Early documents used "MVP" terminology, now "Prototype"
- **Tool Count Evolution**: Documents show progression from 26 → 102 → 106 tools
- **Architecture Changes**: Various MCP architectures explored, now settled on single server

### 4. Implementation Status Changes
Early documents assumed existing implementations (CC2, StructGPT). Current status is specification phase with 0/106 tools implemented.

## Historical Value

### Research Context
These documents show the evolution of thinking and decision-making process. Useful for understanding:
- Why certain decisions were made
- What alternatives were considered
- How the project scope evolved

### Lessons Learned
- Documentation consistency is critical
- Multiple planning iterations without consolidation create confusion
- Clear decision authority prevents contradictions

## For Current Development

### ✅ Use These Instead
- **Decisions**: `docs/decisions/CANONICAL_DECISIONS_2025.md`
- **Architecture**: Root `ARCHITECTURE.md`
- **Implementation**: Root `IMPLEMENTATION.md`
- **Development**: Root `CLAUDE.md`

### ❌ Don't Use Archive Documents
- They contain conflicting information
- Decisions have been superseded
- Tool counts and architectures are outdated
- Scope and terminology are incorrect

---

**Archive Date**: 2025-06-12  
**Reason**: Documentation consolidation and consistency improvement  
**Status**: Historical reference only