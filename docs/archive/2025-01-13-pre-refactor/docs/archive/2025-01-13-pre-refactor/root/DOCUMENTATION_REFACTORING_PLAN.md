# Documentation Refactoring Plan

**Objective:** Reduce 87+ documentation files to <20 core files while preserving all content in archives.

## Phase 1: Archive Everything (Preserve Current State)

```bash
# Create timestamped archive
mkdir -p docs/archive/2025-01-13-pre-refactor

# Copy entire current state
cp -r docs/* docs/archive/2025-01-13-pre-refactor/
cp *.md docs/archive/2025-01-13-pre-refactor/root-level/

# Create archive index
touch docs/archive/2025-01-13-pre-refactor/ARCHIVE_INDEX.md
```

## Phase 2: Identify Consolidation Targets

### Target Structure (<20 files total):

```
/home/brian/Digimons/
├── README.md                    # Project overview
├── CLAUDE.md                    # Claude Code instructions
├── IMPLEMENTATION_ROADMAP.md    # Development plan
└── docs/
    ├── core/                    # 5-7 essential docs
    │   ├── ARCHITECTURE.md      # Unified architecture
    │   ├── SPECIFICATIONS.md    # All 106 tools
    │   ├── DEVELOPMENT_GUIDE.md # Getting started + setup
    │   ├── DESIGN_PATTERNS.md   # Key patterns/decisions
    │   └── API_REFERENCE.md     # Tool API documentation
    ├── project/                 # 3-4 project docs
    │   ├── HISTORY.md          # Project evolution
    │   ├── CONTRIBUTING.md     # Contribution guidelines
    │   └── TROUBLESHOOTING.md  # Common issues
    └── archive/                # All historical content
```

## Phase 3: Consolidation Map

### 1. ARCHITECTURE.md (Merge these files):
- `/ARCHITECTURE.md`
- `docs/architecture/CANONICAL_ARCHITECTURE.md`
- Architecture sections from `MASTER_PLAN.md`
- Architecture sections from `IMPLEMENTATION.md`
- Relevant parts of `docs/decisions/CANONICAL_DECISIONS_2025.md`

### 2. SPECIFICATIONS.md (Merge these files):
- `docs/specifications/SUPER_DIGIMON_COMPLETE_TOOL_SPECIFICATIONS.md` (primary)
- `docs/specifications/TOOL_ARCHITECTURE_SUMMARY.md`
- `docs/specifications/PHASE_4_RETRIEVAL_TOOLS_T49_T67.md`
- `docs/specifications/JAYZHOU_MCP_TOOL_MAPPING.md`
- Remove/archive: `OPTIMIZED_TOOL_SPECIFICATIONS.md` (102-tool version)

### 3. DEVELOPMENT_GUIDE.md (Merge these files):
- `GETTING_STARTED.md`
- `docs/development/DOCKER_WORKFLOW.md`
- `docs/development/QUICKSTART_GUIDE.md`
- `docs/reference/DEPLOYMENT_GUIDE.md`
- Setup sections from `CLAUDE.md`

### 4. DESIGN_PATTERNS.md (Extract patterns from):
- `docs/reference/CLAUDE_CODE_DEEP_INSIGHTS.md`
- `docs/reference/SUPER_DIGIMON_CRITIQUES_AND_RESPONSES.md`
- `docs/decisions/PYDANTICAI_DECISION.md`
- `docs/reference/CRITICAL_ANALYSIS_SUPER_DIGIMON.md`
- Key insights from `misc/` folder

### 5. HISTORY.md (Create from):
- Evolution story from various planning docs
- Clear note about CC2/StructGPT being historical only
- Timeline of major decisions
- Why certain approaches were abandoned

## Phase 4: Content Migration Rules

### What to Keep:
1. **Current, canonical decisions only**
2. **Active specifications** (106-tool system)
3. **Practical implementation guidance**
4. **Essential architectural diagrams**
5. **Core design patterns** (condensed to bullet points)

### What to Archive:
1. **All planning documents** (docs/planning/*)
2. **Historical analyses** (COMPARATIVE_ANALYSIS_REPORT.md)
3. **Rejected proposals** (102-tool optimization)
4. **Philosophical discussions** (unless distilled to patterns)
5. **Duplicate content** (multiple versions of same info)
6. **Any document that required "fixing"** during audits

## Phase 5: Execution Steps

### Step 1: Create Archive
```bash
# Full backup
mkdir -p docs/archive/2025-01-13-pre-refactor/{root,docs,misc}
cp *.md docs/archive/2025-01-13-pre-refactor/root/
cp -r docs/* docs/archive/2025-01-13-pre-refactor/docs/
cp -r misc docs/archive/2025-01-13-pre-refactor/ 2>/dev/null || true
```

### Step 2: Create New Structure
```bash
# New clean structure
mkdir -p docs/{core,project}
```

### Step 3: Consolidate Core Documents
1. **ARCHITECTURE.md** - Single source of truth for system design
2. **SPECIFICATIONS.md** - All 106 tools in one place
3. **DEVELOPMENT_GUIDE.md** - Everything needed to start coding
4. **DESIGN_PATTERNS.md** - Distilled wisdom, no philosophy

### Step 4: Clean Root Directory
- Keep only: README.md, CLAUDE.md, IMPLEMENTATION_ROADMAP.md
- Archive everything else

### Step 5: Update References
- Update CLAUDE.md with new file locations
- Ensure all internal links work
- Add clear warnings on archived content

## Phase 6: Quality Checks

### Before Declaring Complete:
1. **Verify <20 active files** (excluding archives)
2. **Check for contradictions** in consolidated docs
3. **Ensure no broken references**
4. **Confirm all 106 tools are documented**
5. **Test that key information is findable**

### Success Metrics:
- [ ] Active documentation reduced by >75%
- [ ] No duplicate information
- [ ] Clear navigation path
- [ ] All historical content preserved
- [ ] New developer can understand project in <1 hour

## Implementation Order

1. **Today**: Create full archive backup
2. **Next**: Consolidate architecture documents
3. **Then**: Merge specifications
4. **Then**: Create unified development guide
5. **Finally**: Extract patterns and create indexes

## Notes

- **Use git commits** between each major consolidation
- **Tag the pre-refactor state** for easy reference
- **Create clear redirects** from old locations
- **Document what was merged where** in archive index