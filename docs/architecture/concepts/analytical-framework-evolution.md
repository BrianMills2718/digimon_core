# Analytical Framework Evolution

**Status**: Reference Document  
**Purpose**: Links to exploratory thinking about KGAS analytical framework

---

## Current Status

The analytical framework for KGAS is still evolving. Key philosophical questions about the system's analytical purpose are being explored in the Thinking_out_loud directory.

## Related Exploratory Documents

### Analysis Philosophy Questions
The following documents in `/Thinking_out_loud/Analysis_Philosophy/` explore fundamental questions about what type of analysis KGAS should perform:

- **[ANALYTIC_TIER_BOUNDARY_CONFUSION.md](../Thinking_out_loud/Analysis_Philosophy/ANALYTIC_TIER_BOUNDARY_CONFUSION.md)** - Explores the core confusion between analyzing text vs. analyzing the world vs. analyzing effects
- **[ANALYTIC_TIER_MULTIPLE_MEANINGS.md](../Thinking_out_loud/Analysis_Philosophy/ANALYTIC_TIER_MULTIPLE_MEANINGS.md)** - Shows how each analytic tier has different meanings for text-internal vs. text-external analysis
- **[SYSTEMATIC_TEXT_ANALYSIS_FRAMEWORK.md](../Thinking_out_loud/Analysis_Philosophy/SYSTEMATIC_TEXT_ANALYSIS_FRAMEWORK.md)** - First principles approach to understanding text analysis dimensions

### Key Questions to Resolve

1. **Primary Analytical Purpose**: 
   - Text analysis (properties of linguistic artifacts)
   - World analysis (using text as evidence about reality)
   - Effect analysis (how text affects people)
   - Design analysis (how to craft effective text)

2. **Analysis Tier Meaning**:
   - Should descriptive/explanatory/predictive/prescriptive tiers apply to text-internal or text-external analysis?
   - How do we handle cases where both dimensions are relevant?

3. **Theory Integration**:
   - How do theories map to different analysis types?
   - Should theories specify which analysis dimensions they address?

## Integration with Stable Architecture

### Current Stable Documents
- **[theoretical-framework.md](theoretical-framework.md)** - Current theory integration approach
- **[cross-modal-philosophy.md](cross-modal-philosophy.md)** - Cross-modal analysis philosophy

### Needed Resolution
The analytical framework questions need resolution before:
- Finalizing component specifications in `/systems/`
- Completing cross-modal analysis architecture
- Stabilizing theory integration approach

## Decision Required

**Architecture Decision Needed**: Choose primary analytical purpose and resolve tier meaning ambiguity.

**Impact**: This decision affects:
- Tool development priorities
- User interface design  
- Theory integration architecture
- Cross-modal analysis workflows

**Timeline**: Should be resolved before Phase 2 implementation begins.