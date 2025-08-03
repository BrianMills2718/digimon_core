# ADR-029: IC-Informed Uncertainty Framework

**Status**: Accepted  
**Date**: 2025-07-29  
**Related**: [ADR-007](ADR-007-uncertainty-metrics.md) (CERQual Architecture), [ADR-010](ADR-010-Quality-System-Design.md) (Superseded), [ADR-016](ADR-016-Bayesian-Uncertainty-Aggregation.md) (Superseded)  
**Context**: Need for mathematically coherent, sustainable uncertainty quantification that leverages proven Intelligence Community methodologies

## Context

KGAS requires robust uncertainty quantification throughout its analytical pipeline. Previous approaches (degradation-only in ADR-010, Bayesian aggregation in ADR-016) had significant limitations:

- **ADR-010**: Overly pessimistic multiplication of degradation factors
- **ADR-016**: Computationally expensive per-aggregation LLM calls for probability estimation
- **Both**: Lacked grounding in proven analytical methodologies

The Intelligence Community has decades of experience with uncertainty in analytical judgments, codified in standards like ICD-203 and ICD-206, and research by Richards Heuer on cognitive biases.

## Decision

We will implement an **IC-informed uncertainty framework** based on the Comprehensive7 specification that integrates:

1. **ICD-203 Probability Standards**: Standardized probability bands and confidence levels
2. **ICD-206 Source Quality Assessment**: Systematic evaluation of evidence quality
3. **Heuer's Principles**: Awareness of information paradox and cognitive biases
4. **Mathematical Propagation**: Root-sum-squares for independent uncertainties
5. **Single Integrated LLM Analysis**: Comprehensive IC methodologies in one call

### Core Architecture

```python
class ICInformedUncertaintyFramework:
    def __init__(self):
        self.propagation = UncertaintyPropagation()
        self.ic_analyzer = IntegratedUncertaintyAnalysis()
        self.quality_tracker = SelectiveQualityMetrics()
    
    def analyze_with_ic_methods(self, research_question, evidence, context):
        # Single comprehensive LLM call
        ic_analysis = self.ic_analyzer.analyze_with_ic_methods(
            research_question, evidence, context
        )
        
        # Mathematical propagation (hard-coded, not LLM)
        final_uncertainty = self.propagation.propagate_uncertainties(
            ic_analysis['stage_confidences']
        )
        
        return {
            'analysis': ic_analysis,
            'final_confidence': final_uncertainty,
            'ic_assessment': self._format_ic_assessment(ic_analysis)
        }
```

## Rationale

### Why IC Methodologies?

**1. Proven Track Record**: Decades of successful application in high-stakes analysis
**2. Standardization**: Common vocabulary and methods across analysts
**3. Bias Mitigation**: Structured techniques to reduce cognitive biases
**4. LLM Compatibility**: IC methods align with LLM strengths (assessment) not weaknesses (precise probability)

### Why Mathematical Propagation?

**1. Correctness**: Root-sum-squares correctly handles independent uncertainties
**2. Efficiency**: Hard-coded math is deterministic and fast
**3. Transparency**: Clear mathematical model vs. opaque LLM reasoning
**4. Consistency**: Same propagation every time, no LLM variability

### Why Single Integrated Analysis?

**1. Efficiency**: One LLM call vs. many for Bayesian parameters
**2. Coherence**: All IC methods applied together
**3. Context**: Full context available for all assessments
**4. Cost**: Reduced API calls and processing time

## Implementation Specification

### ICD-203 Integration

```python
IC_PROBABILITY_BANDS = {
    "almost_no_chance": (0.01, 0.05),
    "very_unlikely": (0.05, 0.20),
    "unlikely": (0.20, 0.45),
    "roughly_even_chance": (0.45, 0.55),
    "likely": (0.55, 0.80),
    "very_likely": (0.80, 0.95),
    "almost_certain": (0.95, 0.99)
}
```

### Mathematical Propagation

```python
def propagate_independent_uncertainties(self, uncertainties):
    """For independent sources: σ_total = √(σ₁² + σ₂² + ... + σₙ²)"""
    combined_variance = sum(u**2 for u in uncertainties)
    return math.sqrt(combined_variance)
```

### Heuer's Information Paradox

```python
def assess_evidence_quality_not_quantity(self, evidence_items):
    """Focus on diagnostic value, not count"""
    return {
        'diagnostic_value': self._assess_diagnosticity(evidence_items),
        'quantity': len(evidence_items),
        'warning': 'More evidence may increase confidence without improving accuracy'
    }
```

## Consequences

### Positive

- **Mathematical Coherence**: Proper uncertainty propagation
- **Proven Methodologies**: Leverages decades of IC experience
- **LLM Optimization**: Uses LLMs for what they do well
- **Sustainable**: Focused tracking without overhead
- **Transparent**: Clear standards and methods

### Negative

- **Learning Curve**: Researchers need to understand IC methods
- **Cultural Shift**: Move from precision to probability bands
- **Legacy Compatibility**: Existing code using old approaches needs updating

### Neutral

- **Different Philosophy**: Evidence quality over quantity
- **New Vocabulary**: IC terminology in academic context

## Migration Path

1. **Update Core Services**: Implement new propagation mathematics
2. **Integrate IC Standards**: Add ICD-203/206 throughout pipeline
3. **Single LLM Analysis**: Replace fragmented calls with integrated approach
4. **Update Documentation**: Ensure all docs reference Comprehensive7
5. **Training**: Educate users on IC methodologies

## Validation Criteria

- [ ] Mathematical propagation correctly implements root-sum-squares
- [ ] IC probability bands used instead of point estimates
- [ ] Single LLM call performs all IC analyses
- [ ] Heuer's paradox addressed in evidence aggregation
- [ ] Sustainable tracking with selective metrics
- [ ] Documentation updated to reference Comprehensive7

## Related Documents

- **Implementation**: [kgas_uncertainty_framework_comprehensive7.md](../kgas_uncertainty_framework_comprehensive7.md)
- **IC Review**: [IC_UNCERTAINITY_NOTES_2025.0728.md](../IC_UNCERTAINITY_NOTES_2025.0728.md)
- **Superseded**: ADR-010 (degradation-only), ADR-016 (Bayesian aggregation)

This ADR establishes the IC-informed approach as the standard for uncertainty handling in KGAS, replacing previous approaches with a more sophisticated, sustainable, and mathematically coherent framework.