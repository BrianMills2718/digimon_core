**Doc status**: Living – auto-checked by doc-governance CI

# Project Consistency Framework

**Purpose**: Prevent future documentation/implementation inconsistencies  
**Scope**: All project documentation, code, and communications  
**Enforcement**: Automated checks and manual review processes

---

## Core Principles

### 1. Truth Before Aspiration
**Rule**: Never document features that don't exist  
**Standard**: Every claim must have verification command  
**Exception**: Clearly marked "Future Plans" or "Roadmap" sections

### 2. Single Source of Truth
**Rule**: One authoritative document per topic  
**Standard**: All other references link to authoritative source  
**Exception**: Summary versions clearly marked as derived

### 3. Verification-First Documentation
**Rule**: Include executable proof for all claims  
**Standard**: Working commands that demonstrate the feature  
**Exception**: Historical or conceptual information clearly marked

---

## Documentation Standards

### Feature Claims Format
```markdown
## Feature: [Name]
**Status**: [Implementation status to be determined]

**Verification**:
```bash
# Command to prove feature works
python test_specific_feature.py
```

**Evidence**: [Link to test results or screenshots]
```

### Performance Claims Format  
```markdown
## Performance: [Metric]
**Current**: [Actual measured value]
**Target**: [Goal value] 
**Last Measured**: [Date]

**Verification**:
```bash
# Command to reproduce measurement
python tests/performance/test_[metric].py
```

**Benchmark**: [Link to performance test results]
```

### Architecture Claims Format
```markdown
## Architecture: [Component]
**Implementation**: [Actual current state]
**Design**: [Intended design]
**Gap**: [What's missing]

**Verification**:
```bash
# Command to validate architecture
python tests/integration/test_[component]_integration.py
```
```

---

## Consistency Checks

### Automated Daily Checks
```bash
# Run all verification commands in documentation
./scripts/verify_all_documentation_claims.sh

# Check for conflicting statements
./scripts/check_documentation_consistency.sh

# Validate all performance claims
./scripts/verify_performance_claims.sh
```

### Weekly Manual Reviews
- [ ] Cross-reference all feature claims with test results
- [ ] Verify no contradictory vision statements
- [ ] Check that tool counts match actual implementations
- [ ] Validate performance numbers against latest benchmarks

### Monthly Architecture Reviews
- [ ] Ensure single implementation (no bifurcation)
- [ ] Validate API consistency across components
- [ ] Check integration test coverage
- [ ] Review technical debt and architectural gaps

---

## Change Control Process

### Documentation Updates
1. **Identify Change**: What claim needs updating?
2. **Verify Reality**: Run tests to confirm current state
3. **Update Documentation**: Change text to match reality
4. **Add Verification**: Include command to prove claim
5. **Review Consistency**: Check for ripple effects

### Feature Development
1. **Design Phase**: Document intended behavior
2. **Implementation**: Build feature to match design
3. **Testing**: Create verification tests
4. **Documentation**: Update claims with proof commands
5. **Integration**: Ensure no conflicts with existing features

### Performance Changes
1. **Measure Baseline**: Record current performance
2. **Implement Changes**: Make performance modifications
3. **Re-measure**: Confirm new performance numbers
4. **Update Claims**: Change all documentation to match
5. **Archive Old Data**: Preserve historical measurements

---

## Enforcement Mechanisms

### Automated Safeguards
```bash
# Git pre-commit hooks
.git/hooks/pre-commit:
- Run documentation verification
- Check for forbidden words ("will", "should", "plans to")
- Validate performance claims against tests
- Flag contradictory statements

# CI/CD Pipeline Checks
.github/workflows/consistency.yml:
- Daily documentation verification
- Performance regression detection  
- Architecture consistency validation
- Cross-reference checking
```

### Manual Review Gates
- **Documentation PRs**: Require verification commands for all claims
- **Feature PRs**: Must update documentation with proof
- **Performance PRs**: Must update all performance claims
- **Architecture PRs**: Must update architectural documentation

---

## Warning Signs System

### Red Flags (Immediate Action Required)
🚨 **Multiple implementations** of same functionality  
🚨 **Contradictory vision statements** in different documents  
🚨 **Performance claims without recent verification**  
🚨 **Feature claims without working tests**  
🚨 **Tool counts that don't match actual implementations**

### Yellow Flags (Monitor Closely)  
⚠️ **Aspirational language** in capability sections  
⚠️ **Outdated performance numbers** (>30 days old)  
⚠️ **Broken verification commands** in documentation  
⚠️ **Missing integration tests** for features  
⚠️ **API inconsistencies** between components

### Green Indicators (Healthy State)
**All verification commands work**  
**Performance claims within 7 days old**  
**Single authoritative source for each topic**  
**Feature claims match test results**  
**Consistent vision across all documents**

---

## Recovery Procedures

### When Inconsistency Detected
1. **Stop**: Halt development of affected area
2. **Assess**: Determine scope of inconsistency
3. **Truth Check**: Run verification commands to establish reality
4. **Document**: Record actual state in CURRENT_REALITY_AUDIT.md
5. **Align**: Update all documentation to match reality
6. **Verify**: Confirm consistency restored
7. **Resume**: Continue development with accurate baseline

### When Multiple Implementations Found
1. **Inventory**: List all implementations and their differences
2. **Evaluate**: Determine which implementation to keep
3. **Archive**: Move unused implementations to archive/
4. **Consolidate**: Ensure single active implementation
5. **Test**: Verify unified implementation works
6. **Document**: Update all references to point to single implementation

---

## Measurement and Monitoring

### Consistency Metrics
- **Verification Success Rate**: % of documentation claims that pass verification
- **Performance Accuracy**: % of performance claims within ±10% of actual
- **Vision Alignment Score**: Consistency of vision statements across documents
- **Implementation Unity**: Number of duplicate/conflicting implementations

### Monthly Consistency Report
```markdown
## Consistency Health Report - [Month/Year]

**Overall Score**: [X]/10

**Verification Success Rate**: [X]% (Target: >95%)
**Performance Accuracy**: [X]% (Target: >90%)  
**Vision Alignment**: [X]/10 (Target: >8)
**Implementation Unity**: [X] conflicts (Target: 0)

**Action Items**:
- [ ] [Specific fixes needed]
```

---

## Team Training

### Consistency Mindset
- **Reality First**: What actually works right now?
- **Proof Required**: How can we demonstrate this claim?
- **Single Truth**: Where is the authoritative source?
- **Integration Focus**: How does this fit with everything else?

### Daily Practices
- Run verification commands before making claims
- Check for existing implementations before creating new ones
- Update documentation immediately when functionality changes
- Cross-reference vision statements before writing

### Review Habits
- Question aspirational language in current-state sections
- Verify performance numbers before including them
- Check for architectural consistency in design decisions
- Ensure integration tests exist for all feature claims

---

**Implementation**: This framework should be adopted immediately to prevent recurrence of identified inconsistencies.-e 
<br><sup>See `docs/roadmap/ROADMAP_OVERVIEW.md` for master plan.</sup>
