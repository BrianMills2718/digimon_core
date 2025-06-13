# Documentation Reorganization Plan

## Problem
**45 markdown files in root directory** - This is unmanageable and makes the project impossible to navigate.

## Target Structure
```
/
├── README.md                    # Main project overview
├── CLAUDE.md                    # Claude Code guidance  
├── ARCHITECTURE.md              # Core architecture (consolidated)
├── IMPLEMENTATION.md            # Implementation roadmap
├── docs/
│   ├── decisions/              # Architectural decisions
│   ├── specifications/         # Technical specs
│   ├── planning/              # Historical planning docs
│   └── reference/             # Supporting materials
├── new_docs/                   # Keep - authoritative tool specs
├── config/                    # Keep - configuration files
├── test_data/                 # Keep - test datasets
├── tools/                     # Keep - implementation code
└── [other non-md directories] # Keep as-is
```

## Consolidation Plan

### **Keep in Root (4 files max)**
1. **README.md** - Project overview and quick start
2. **CLAUDE.md** - Claude Code guidance (already good)
3. **ARCHITECTURE.md** - Consolidated from SUPER_DIGIMON_CANONICAL_ARCHITECTURE.md + key architecture docs
4. **IMPLEMENTATION.md** - From IMPLEMENTATION_ROADMAP.md

### **Move to docs/decisions/**
- ARCHITECTURAL_DECISIONS.md
- Key architecture decision documents

### **Move to docs/specifications/**
- OPTIMIZED_TOOL_SPECIFICATIONS.md
- TECHNICAL_OPTIMIZATION_ANALYSIS.md
- Core technical specifications

### **Move to docs/planning/**
- All the planning and analysis documents
- Historical roadmaps and critiques
- Review documents

### **Delete/Archive**
- Duplicate documents
- Outdated planning documents  
- Documents that have been superseded

## Implementation Steps

1. **Create docs/ structure**
2. **Create consolidated README.md**
3. **Create consolidated ARCHITECTURE.md**
4. **Move files to appropriate locations**
5. **Delete duplicates and outdated files**
6. **Update any cross-references**
7. **Commit the cleanup**

## Success Criteria
- **Root directory**: ≤ 6 .md files total
- **Clear navigation**: Easy to find what you need
- **No duplicates**: Single source of truth for each topic
- **Logical organization**: Related files grouped together