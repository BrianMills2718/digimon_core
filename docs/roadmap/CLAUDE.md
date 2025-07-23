# KGAS Roadmap Documentation Guide

## 📍 Current Status Location
**ALWAYS check [ROADMAP_OVERVIEW.md](./ROADMAP_OVERVIEW.md) first** - this is the single source of truth for project status.

## 📁 Directory Structure

### `/phases/`
Implementation phases organized by status and timeline:
- `phase-X-implementation-plan.md` = What we planned to do
- `phase-X-implementation.md` = What we actually did/results
- `phase-X-tasks/` = Individual task breakdowns
- `phase-tdd/` = Current active TDD implementation phase

### `/initiatives/`
Cross-cutting workstreams and specialized plans:
- `clear-implementation-roadmap.md` = Master implementation plan
- `tdd-implementation-plan.md` = TDD methodology details
- `tooling/` = Tool-specific planning and tracking

### `/analysis/`
Codebase analysis and discovery work:
- `completed/` = Historical analysis
- Current analysis files for ongoing investigations

### `/performance/`
Performance benchmarks and optimization plans

## 🔄 File Naming Conventions

### Phase Files
- **Planning**: `phase-X-implementation-plan.md` (what we intend to do)
- **Results**: `phase-X-implementation.md` (what we actually accomplished)
- **Tasks**: `phase-X-tasks/task-X.Y-description.md`

### Task Numbering
- Use letter suffixes for duplicates: `task-1.1a-`, `task-1.1b-`
- Phase 5 tasks use sub-versions: `task-5.2.1-`, `task-5.3.1-`

## ⚠️ Update Guidelines

### ✅ DO Update These Files
- Phase implementation files (results/progress)  
- Task status and completion
- Initiative progress tracking
- Analysis findings

### ❌ DON'T Update These Files
- Completed phase plans (historical record)
- Architecture files in this directory (belongs in `/architecture/`)
- Implementation details that belong in code comments

## 🚀 Quick Commands

```bash
# Check current status
cat ROADMAP_OVERVIEW.md

# View active TDD progress  
cat phases/phase-tdd/tdd-implementation-progress.md

# Review master plan
cat initiatives/clear-implementation-roadmap.md
```

## 📋 Common Tasks

### Adding New Phase
1. Create `phase-X-implementation-plan.md` with objectives
2. Create `phase-X-tasks/` directory for task breakdowns
3. Update `ROADMAP_OVERVIEW.md` with phase status
4. When complete, create `phase-X-implementation.md` with results

### Tracking Task Progress
1. Update task status in individual task files
2. Update phase summary files
3. Update `ROADMAP_OVERVIEW.md` if major milestone reached

### Moving Between Phases
1. Mark current phase as complete in `ROADMAP_OVERVIEW.md`
2. Create implementation results file
3. Update next phase status to active
4. Create any new task breakdown files needed

## 🎯 Remember
- ROADMAP_OVERVIEW.md = definitive status
- Implementation-plan files = what we planned
- Implementation files = what we accomplished
- Keep historical record intact, don't delete completed work