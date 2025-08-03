# ADR-007: CERQual-Based Uncertainty Architecture

**Status**: Superseded by [ADR-029](ADR-029-IC-Informed-Uncertainty-Framework/ADR-029-IC-Informed-Uncertainty-Framework.md)  
**Related**: [ADR-004](ADR-004-Normative-Confidence-Score-Ontology.md) (Superseded), [ADR-010](ADR-010-Quality-System-Design.md) (Superseded), [ADR-025](ADR-025-Entity-Resolution-Architecture.md) (Entity resolution uncertainty), [ADR-029](ADR-029-IC-Informed-Uncertainty-Framework/ADR-029-IC-Informed-Uncertainty-Framework.md) (Current Implementation)  
**Date**: 2025-07-20  
**Context**: Need for principled uncertainty quantification in academic social science research

## Context

Academic social science research requires rigorous uncertainty quantification to ensure research validity and reproducibility. LLM-based analysis tools introduce multiple sources of uncertainty (epistemic, aleatoric, model-based) that must be quantified and propagated through analytical pipelines. Standard software engineering confidence scores are insufficient for academic rigor.

## Decision

**This ADR has been superseded by [ADR-029: IC-Informed Uncertainty Framework](ADR-029-IC-Informed-Uncertainty-Framework/ADR-029-IC-Informed-Uncertainty-Framework.md).**

The original decision was to implement a **CERQual-based uncertainty quantification framework** with four-layer architecture and configurable complexity. However, this approach has been replaced by the IC-Informed framework which provides:

- **Intelligence Community methodologies** (ICD-203/206 standards)
- **Mathematical uncertainty propagation** (root-sum-squares)
- **Single integrated LLM analysis** (comprehensive IC assessment)
- **Sustainable tracking** (decision-critical metrics only)

### Original Framework Choice: CERQual (Superseded)
- **CERQual**: Confidence in the Evidence from Reviews of Qualitative research
- **Academic Standard**: Established methodology for social science uncertainty assessment
- **Domain Fit**: Specifically designed for discourse analysis and qualitative research

### Original Four-Layer Architecture (Superseded)

1. **Contextual Entity Resolution**: Dynamic disambiguation with uncertainty
2. **Temporal Knowledge Graph**: Time-bounded confidence decay
3. **Bayesian Pipeline**: Dependency modeling and uncertainty propagation
4. **Distribution Preservation**: Full uncertainty distribution maintenance

## Rationale

### CERQual Framework Benefits
- **Academic Recognition**: Established methodology accepted in social science journals
- **Domain Appropriate**: Designed specifically for qualitative discourse analysis
- **Quality Assessment**: Provides structured approach to evidence quality evaluation
- **Research Validity**: Enhances reproducibility and research rigor

### Four-Layer Approach Benefits
- **Comprehensive Coverage**: Addresses all major uncertainty sources
- **Propagation Tracking**: Maintains uncertainty through complex analytical chains
- **Configurable Detail**: Researchers can choose appropriate complexity level
- **Academic Standards**: Meets requirements for academic publication

### Alternative Approaches Rejected
- **Simple Confidence Scores**: Insufficient for academic rigor
- **Engineering Reliability Metrics**: Not aligned with social science methodology
- **Single-Layer Uncertainty**: Fails to capture uncertainty propagation complexity

## Consequences

### Positive
- Academic research meets publication standards for uncertainty reporting
- Configurable complexity allows adaptation to research needs
- Comprehensive uncertainty propagation through analytical pipelines
- Integration with established academic methodologies

### Negative
- Increased computational complexity for advanced uncertainty modes
- Additional metadata storage requirements
- Learning curve for researchers unfamiliar with uncertainty quantification

### Neutral
- Requires calibration for different domains and LLM models
- Performance trade-offs between uncertainty detail and processing speed

## Implementation Requirements

### Technical Requirements
- CERQual framework integration with all analytical components
- Three-tier uncertainty taxonomy (data-level, extraction-level, analytical)
- Configurable complexity levels (simple to advanced)
- Uncertainty-aware tool contracts for all operations

### Quality Targets
- ≥99% statistical robustness through integration pipelines
- Proper calibration for social science discourse analysis
- Uncertainty propagation without significant degradation
- Academic standards compliance for research publication

## Implementation Specification

### Superseded by IC-Informed Framework

**Current Implementation**: The **[IC-Informed Uncertainty Framework](ADR-029-IC-Informed-Uncertainty-Framework/ADR-029-IC-Informed-Uncertainty-Framework.md)** is the authoritative implementation specification, superseding this ADR's original CERQual approach.

**Refer to ADR-029 for current implementation details including**:
- **IC-Informed Methodologies**: Integration of ICD-203/206 standards, Heuer's principles, and ACH
- **Mathematical Uncertainty Propagation**: Root-sum-squares for independent uncertainties
- **Realistic LLM Confidence Ranges**: Based on empirical capabilities with IC probability bands
- **Evidence-Based Assessment**: Quality over quantity, avoiding Heuer's information paradox
- **Single Integrated LLM Analysis**: Comprehensive IC-informed analysis in one call
- **Sustainable Tracking**: Focus on decision-critical metrics only

**Implementation Reference**: All uncertainty-related tools and services implement the IC-informed patterns and mathematical propagation specified in ADR-029.

## Validation Evidence

**This ADR has been superseded. For current validation evidence, see [ADR-029](ADR-029-IC-Informed-Uncertainty-Framework/ADR-029-IC-Informed-Uncertainty-Framework.md).**

Original validation research contributed to the IC-Informed framework development:

**See**: [IC-Informed Uncertainty Framework](ADR-029-IC-Informed-Uncertainty-Framework/kgas_uncertainty_framework_comprehensive7.md) and supporting IC documentation:
- [IC Uncertainty Review](ADR-029-IC-Informed-Uncertainty-Framework/IC_UNCERTAINITY_NOTES_2025.0728.md)
- [Entity Resolution Stress Tests](../../examples/entity_resolution_uncertainty_stress_tests.md)
- [Research Impact Scenarios](../../examples/entity_resolution_research_impact_scenarios.md)

Key findings that informed ADR-029:
- IC methodologies proven through decades of intelligence analysis
- Mathematical propagation verified for coherence and accuracy
- LLM confidence ranges aligned with empirical capabilities
- Heuer's information paradox addressed through evidence quality focus
- Single integrated analysis approach validated for efficiency
- Sustainable tracking demonstrated through selective metrics