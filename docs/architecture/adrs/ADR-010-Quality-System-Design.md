# ADR-010: Quality System Design

**Status**: Superseded by Comprehensive7 Framework  
**Date**: 2025-07-23  
**Updated**: 2025-07-29  
**Context**: Academic research requires systematic confidence tracking through multi-step processing pipelines while maintaining epistemic humility about extraction quality.

**Note**: This ADR has been superseded by the IC-informed uncertainty framework documented in `kgas_uncertainty_framework_comprehensive7.md`. The degradation-only approach described below has been replaced with mathematically coherent uncertainty propagation.

## Decision (Original - Now Superseded)

We originally implemented a **confidence degradation system** that models uncertainty accumulation through processing pipelines:

```python
# SUPERSEDED APPROACH - See Comprehensive7 for current approach
class QualityService:
    def __init__(self):
        self.quality_rules = {
            "pdf_loader": QualityRule(degradation_factor=0.95),
            "spacy_ner": QualityRule(degradation_factor=0.90),
            "relationship_extractor": QualityRule(degradation_factor=0.85),
            "entity_builder": QualityRule(degradation_factor=0.90)
        }
    
    def propagate_confidence(self, base_confidence: float, operation: str) -> float:
        """Apply degradation factor for processing step"""
        rule = self.quality_rules.get(operation)
        return base_confidence * rule.degradation_factor if rule else base_confidence
```

### **Original Core Principles (Now Updated)**

1. ~~**Degradation Modeling**: Confidence can only decrease or remain stable, never increase~~
   - **Updated**: Use IC-informed uncertainty propagation that can appropriately handle both uncertainty accumulation and reduction
2. **Epistemic Humility**: Each processing step introduces some uncertainty *(Still Valid)*
3. **Quality Tiers**: Use IC probability bands instead of arbitrary thresholds
4. **Provenance Integration**: Confidence tracked with complete processing history *(Still Valid)*

## Current Approach (Comprehensive7)

The current IC-informed approach uses:

### **Mathematical Uncertainty Propagation**
```python
class UncertaintyPropagation:
    def propagate_independent_uncertainties(self, stage_confidences):
        """Use root-sum-squares for independent uncertainties"""
        # Convert confidences to uncertainties
        uncertainties = [1 - conf for conf in stage_confidences]
        
        # Mathematical propagation: σ_total = √(σ₁² + σ₂² + ... + σₙ²)
        combined_variance = sum(u**2 for u in uncertainties)
        combined_uncertainty = math.sqrt(combined_variance)
        
        # Convert back to confidence
        return 1 - combined_uncertainty
```

### **IC Probability Bands**
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

### **Key Improvements**
1. **Mathematical Coherence**: Proper uncertainty propagation instead of arbitrary multiplication
2. **IC Standards**: Use proven Intelligence Community methodologies
3. **LLM Integration**: Single comprehensive analysis call
4. **Realistic Ranges**: Based on empirical LLM capabilities

## Rationale (Original - For Historical Context)

### **Why We Initially Chose Confidence Degradation**

**1. Academic Epistemic Standards**: 
Research requires acknowledging uncertainty accumulation. Each processing step (PDF extraction → NLP → entity linking) introduces potential errors that compound.

**2. Processing Pipeline Reality**:
- **PDF extraction**: OCR errors, formatting issues
- **NLP processing**: Language model limitations
- **Relationship extraction**: Context interpretation errors
- **Entity building**: Identity resolution mistakes

**3. Conservative Research Approach**:
Academic integrity demands conservative confidence estimates.

### **Why We Moved Beyond Simple Degradation**

**1. Mathematical Incorrectness**: Multiplication assumes complete dependence between stages, which isn't accurate
**2. Overly Pessimistic**: The degradation-only approach was too conservative
**3. IC Best Practices**: Intelligence Community has decades of experience with uncertainty
**4. LLM Capabilities**: Modern LLMs can provide nuanced confidence assessments

## Current Implementation

### **Quality Rules**
```python
QualityRule(
    rule_id="nlp_processing",
    source_type="spacy_ner", 
    degradation_factor=0.9,   # 10% degradation
    min_confidence=0.1,
    description="NLP entity extraction"
)
```

### **Confidence Assessment**
```python
def assess_confidence(
    self,
    object_ref: str,
    base_confidence: float,
    factors: Dict[str, float] = None
) -> Dict[str, Any]:
    # Input validation (0.0-1.0 range)
    # Factor application (multiplicative degradation)
    # Quality tier determination (HIGH/MEDIUM/LOW)
    # Assessment storage with timestamp
```

### **Quality Tiers**
- **HIGH**: confidence ≥ 0.8 (suitable for critical research analysis)
- **MEDIUM**: confidence ≥ 0.5 (suitable for exploratory research)  
- **LOW**: confidence < 0.5 (flagged for manual review)

## Alternatives Considered

### **1. Bayesian Confidence Updates**
```python
# Rejected approach
def bayesian_update(prior_confidence, evidence_likelihood, evidence_strength):
    posterior = (evidence_likelihood * prior_confidence) / normalization_factor
    return min(1.0, posterior * evidence_strength)
```

**Rejected because**:
- **Calibration complexity**: Requires extensive calibration data for each operation type
- **Evidence correlation**: Multiple extractions from same source are not independent
- **Engineering overhead**: Significant complexity for uncertain academic research benefit
- **Domain expertise required**: Requires deep understanding of Bayesian inference for maintenance

### **2. Machine Learning Confidence Models**
```python
# Rejected approach  
class MLConfidencePredictor:
    def predict_confidence(self, extraction_features, context_features):
        return self.trained_model.predict([extraction_features, context_features])
```

**Rejected because**:
- **Training data requirements**: Requires large labeled dataset of extraction quality
- **Model maintenance**: ML models require retraining and performance monitoring
- **Explainability**: Academic researchers need interpretable confidence estimates
- **Generalization**: Models may not generalize across different research domains

### **3. Static Confidence (No Degradation)**
```python
# Rejected approach
def static_confidence(base_confidence):
    return base_confidence  # No change through pipeline
```

**Rejected because**:
- **Unrealistic**: Ignores error accumulation through processing pipelines
- **Academic standards**: Fails to acknowledge uncertainty introduction
- **Quality control**: Cannot distinguish between high-quality and degraded extractions

### **4. Expert-Defined Confidence Rules**
```python
# Rejected approach
def expert_confidence_rules(extraction_type, source_quality, context_factors):
    # Complex rule-based system with expert knowledge
    return calculate_confidence_from_rules(extraction_type, source_quality, context_factors)
```

**Rejected because**:
- **Maintenance complexity**: Requires domain expert involvement for rule updates
- **Rule interaction**: Complex interactions between rules difficult to predict
- **Scalability**: Cannot scale across different research domains and use cases

## Consequences

### **Positive**
- **Simple and interpretable**: Researchers can understand confidence degradation
- **Conservative approach**: Prevents overconfidence in automated extractions
- **Quality filtering**: Enables researchers to work with high-confidence data only
- **Minimal maintenance**: Simple degradation factors require minimal tuning

### **Negative**  
- **No confidence recovery**: Cannot account for confirming evidence from multiple sources
- **Linear degradation**: May not accurately model non-linear uncertainty interactions
- **Domain agnostic**: Same degradation factors across different research domains
- **Static factors**: Degradation factors not adaptive to actual extraction quality

## Future Evolution Considerations

**Note**: This ADR documents the current approach. Future enhancements could include:

1. **Evidence-based confidence adjustment**: Allow confidence increases with multiple confirming sources
2. **Domain-specific degradation**: Different factors for different research domains
3. **Adaptive factors**: Degradation factors based on actual extraction performance
4. **Hybrid approaches**: Combine degradation with limited Bayesian updates for specific cases

**However, any changes require**:
- Careful analysis of academic research requirements
- Validation that complexity increase provides meaningful research value
- Preservation of interpretability and maintainability
- Extensive testing to prevent confidence inflation

## Implementation Requirements

### **Degradation Factor Calibration**
- Factors based on empirical analysis of processing step error rates
- Regular validation against manual quality assessment
- Domain-specific adjustment capabilities

### **Quality Tier Thresholds**
- HIGH (≥0.8): Suitable for publication-quality research analysis
- MEDIUM (≥0.5): Suitable for exploratory research and hypothesis generation
- LOW (<0.5): Requires manual review before use in research

### **Confidence History Tracking**
- Complete audit trail of confidence changes through pipeline
- Integration with provenance service for full traceability
- Support for confidence-based filtering in research workflows

## Validation Criteria

- [ ] Confidence values remain within 0.0-1.0 range through all operations
- [ ] Quality tiers correctly classify extraction reliability for research use
- [ ] Degradation factors reflect empirical processing step error rates
- [ ] Confidence history provides complete audit trail
- [ ] Quality-based filtering enables reliable research workflows
- [ ] System prevents confidence inflation while acknowledging uncertainty

## Related ADRs

- **ADR-008**: Core Service Architecture (quality service integration)
- **ADR-009**: Bi-Store Database Strategy (confidence storage in SQLite)
- **ADR-004**: Normative Confidence Score Ontology (confidence score implementation)
- **ADR-016**: Bayesian Uncertainty Aggregation (alternative approach - also superseded)
- **ADR-022**: IC-Informed Uncertainty Framework (recommended - to be created)

## Migration Path

1. **Update QualityService** to use uncertainty propagation instead of multiplication
2. **Integrate IC standards** for confidence expression
3. **Implement single LLM analysis** for comprehensive uncertainty assessment
4. **Update quality tiers** to use IC probability bands

See `adrs/ADR-029/kgas_uncertainty_framework_comprehensive7.md` for complete implementation details.