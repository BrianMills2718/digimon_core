# Documentation Reorganization Plan

**Date**: 2025-07-21  
**Purpose**: Clean separation between architecture (what we're building) and roadmap (how we're getting there)  
**Status**: DRAFT - Pending Approval

---

## 🎯 **Core Principle**

**Two distinct documentation domains with different purposes and stability:**

1. **Architecture Documentation** = Sole source of truth for the **final product design**
2. **Roadmap Documentation** = Sole source of truth for **current development status**

---

## 📚 **Target Documentation Structure**

### **Architecture Documentation Domain**
```
docs/architecture/
├── ARCHITECTURE_OVERVIEW.md           # Complete final system vision
├── concepts/                           # Detailed concept specifications
│   ├── cross-modal-philosophy.md
│   ├── uncertainty-architecture.md
│   └── theoretical-framework.md
├── data/                              # Data architecture specs
│   ├── theory-meta-schema-v10.md
│   └── schemas.md
├── systems/                           # System component specs
│   └── pipeline-orchestration.md
└── adrs/                              # Architecture Decision Records
    ├── ADR-001-tool-contracts.md
    ├── ADR-004-uncertainty-metrics/
    │   ├── adr-004.md                 # The decision
    │   ├── research/                  # Research supporting the decision
    │   └── validation/                # Evidence the decision is sound
    │       └── stress-test-evidence.md
    └── ...
```

### **Roadmap Documentation Domain**
```
docs/roadmap/
├── ROADMAP_OVERVIEW.md                # ONLY place with status updates
├── phases/                            # Development phase details
│   ├── phase-5/
│   │   ├── phase-5-plan.md
│   │   └── evidence/
│   │       └── async-migration-evidence.md
│   ├── phase-6/
│   │   ├── phase-6-plan.md
│   │   └── evidence/
│   │       └── cross-modal-implementation-evidence.md
│   └── ...
└── methodology/                       # How we develop and validate
    ├── validation-approach.md
    └── testing-standards.md
```

---

## 🧹 **Cleanup Tasks Required**

### **Priority 1: Remove Development Status from Architecture**

#### **Files to Clean**:
1. **`docs/architecture/ARCHITECTURE_OVERVIEW.md`**
   - ❌ Remove: "Validated Architecture Components (2025-07-21)"
   - ❌ Remove: "Core Integration Status - PRODUCTION READY"
   - ❌ Remove: All ✅ status indicators with dates
   - ❌ Remove: "Implementation Evidence" section
   - ❌ Remove: "Architecture Validation Methodology" section
   - ✅ Keep: System vision, principles, component relationships, ADR references

2. **`docs/architecture/data/theory-meta-schema-v10.md`**
   - ❌ Remove: "Status: Active Development"
   - ❌ Remove: "Implementation Status - OPERATIONAL" section
   - ❌ Remove: "Validated Capabilities (2025-07-21)" section
   - ❌ Remove: "Validation Evidence" with specific dates/metrics
   - ❌ Remove: "Security Requirements (CRITICAL)" section
   - ✅ Keep: Schema specifications, technical requirements, examples

3. **`docs/architecture/concepts/cross-modal-philosophy.md`**
   - ❌ Remove: "Philosophy Validation (2025-07-21)" section
   - ❌ Remove: Implementation evidence file references
   - ✅ Keep: Core philosophy, principles, patterns

4. **`docs/architecture/concepts/uncertainty-architecture.md`**
   - ❌ Remove: "Framework Validation (2025-07-20/21)" section
   - ❌ Remove: Research file references with dates
   - ✅ Keep: Architecture specifications, technical approach

5. **`docs/architecture/cross-modal-analysis.md`**
   - ❌ Remove: "Cross-Modal Semantic Preservation - IMPLEMENTATION VALIDATED"
   - ❌ Remove: "Implementation Evidence and Validation" section
   - ❌ Remove: All validation dates and status indicators
   - ✅ Keep: Technical architecture, requirements, component specs

### **Priority 2: Create ADR Validation Evidence Structure**

#### **Preserve Design Validation Evidence**:
1. **Create `docs/architecture/adrs/adr-003-cross-modal-analysis/`**
   - Move CrossModalEntity stress testing evidence
   - Move semantic preservation validation research
   - Keep as proof the architectural decision is sound

2. **Create `docs/architecture/adrs/adr-004-uncertainty-metrics/validation/`**
   - Move 18 uncertainty research files
   - Move CERQual framework validation research
   - Keep as proof the architectural decision is sound

3. **Update ADR files to reference validation subdirectories**

### **Priority 3: Move Implementation Status to Roadmap**

#### **Create Implementation Evidence in Roadmap**:
1. **`docs/roadmap/phases/phase-6/evidence/cross-modal-implementation.md`**
   - "100% semantic preservation achieved on 2025-07-21"
   - "45 rule evaluations with 100% execution success"
   - Third-party Gemini AI validation results
   - Implementation file references (src/core/cross_modal_entity.py)

2. **Update `docs/roadmap/ROADMAP_OVERVIEW.md`**
   - Move all status indicators and completion dates
   - Add references to phase evidence files
   - Maintain as single source of development truth

### **Priority 4: Security Considerations Handling**

#### **Security Information Organization**:
- **Architecture Domain**: Security requirements and constraints as design specs
- **Roadmap Domain**: Current security vulnerabilities and remediation status
- **Example**: "eval() security constraint" = architecture requirement, "eval() currently used in code" = roadmap status

---

## 📋 **Implementation Steps**

### **Step 1: Backup Current State**
- Create `archived/documentation_reorganization_backup_2025_07_21/`
- Copy current docs structure before changes

### **Step 2: Architecture Cleanup**
- Remove all status/validation sections from architecture files
- Keep only design specifications and requirements
- Update file headers to remove development status

### **Step 3: ADR Evidence Preservation**
- Create ADR validation subdirectories
- Move design validation evidence to appropriate ADRs
- Update ADR files to reference validation evidence

### **Step 4: Roadmap Evidence Creation**
- Create phase evidence directories
- Move implementation status evidence to roadmap domain
- Update roadmap overview with proper status tracking

### **Step 5: Cross-Reference Updates**
- Update all internal links between architecture and roadmap
- Ensure clear separation is maintained
- Update CLAUDE.md documentation guidelines

### **Step 6: Validation**
- Run focused Gemini consistency reviews on cleaned architecture
- Verify no development status leaked into architecture domain
- Confirm roadmap properly tracks implementation progress

---

## ✅ **Success Criteria**

### **Architecture Documentation**:
- [ ] No dates, status indicators, or implementation progress
- [ ] Only design specifications and requirements
- [ ] ADRs contain validation evidence proving design soundness
- [ ] Stable reference for final product vision

### **Roadmap Documentation**:
- [ ] Single source of truth for development progress
- [ ] Contains all implementation evidence and validation results
- [ ] Clear phase-by-phase development tracking
- [ ] References architecture but doesn't duplicate it

### **Clean Separation**:
- [ ] Architecture answers "What are we building?"
- [ ] Roadmap answers "How are we getting there?" and "Where are we now?"
- [ ] No overlap or duplication between domains
- [ ] Clear cross-references where appropriate

---

## 🚨 **Critical Considerations**

### **Information Preservation**:
- All current validation evidence must be preserved
- ADR research and validation must remain accessible
- Implementation progress tracking must be maintained
- No loss of institutional knowledge

### **User Impact**:
- Architecture becomes stable reference
- Development status clearly separated
- ADR evidence proves design decisions
- Roadmap tracks actual progress

### **Maintenance**:
- Architecture changes only when goals change
- Roadmap updates reflect development progress
- Clear guidelines for contributors on where information belongs

---

*This plan ensures clean separation between design intent (architecture) and development progress (roadmap) while preserving all validation evidence and maintaining clear documentation purpose.*