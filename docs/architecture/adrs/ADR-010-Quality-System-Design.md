# ADR-010: Quality System Design

**Status**: Accepted  
**Date**: 2025-07-23  
**Context**: Academic research requires systematic confidence tracking through multi-step processing pipelines while maintaining epistemic humility about extraction quality.

## Decision

We will implement a **confidence degradation system** that models uncertainty accumulation through processing pipelines:

```python
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

### **Core Principles**

1. **Epistemic Humility**: Each processing step introduces some uncertainty
2. **Degradation Modeling**: Confidence can only decrease or remain stable, never increase
3. **Quality Tiers**: HIGH (≥0.8), MEDIUM (≥0.5), LOW (<0.5) for filtering
4. **Provenance Integration**: Confidence tracked with complete processing history

## Rationale

### **Why Confidence Degradation?**

**1. Academic Epistemic Standards**: 
Research requires acknowledging uncertainty accumulation. Each processing step (PDF extraction → NLP → entity linking) introduces potential errors that compound.

**2. Processing Pipeline Reality**:
- **PDF extraction**: OCR errors, formatting issues (5% confidence loss)
- **NLP processing**: Language model limitations (10% confidence loss)  
- **Relationship extraction**: Context interpretation errors (15% confidence loss)
- **Entity building**: Identity resolution mistakes (10% confidence loss)

**3. Conservative Research Approach**:
Academic integrity demands conservative confidence estimates. Better to underestimate confidence than overestimate and produce false research conclusions.

**4. Filtering and Quality Control**:
Degraded confidence enables quality-based filtering. Researchers can choose to work only with HIGH confidence extractions (≥0.8) for critical analysis.

### **Why Not Bayesian Updates/Confidence Increases?**

**Current Decision Rationale**:

**1. Complexity vs. Benefit**: Bayesian updating requires:
- Prior probability distributions for each operation type
- Likelihood functions for evidence integration  
- Posterior calculation frameworks
- Extensive calibration on academic research data

**Academic research tool complexity tradeoff**: Simple degradation model provides adequate uncertainty tracking without the engineering complexity of full Bayesian inference.

**2. Evidence Integration Challenges**:
- **Different evidence types**: How do you combine NER confidence, relationship extraction confidence, and external validation?
- **Correlation issues**: Multiple extractions from same document are not independent evidence
- **Calibration requirements**: Bayesian updates require well-calibrated probability estimates

**3. Academic Use Case Alignment**:
Academic researchers primarily need to:
- Identify high-confidence extractions for analysis
- Understand uncertainty accumulation through pipelines  
- Filter low-confidence results from critical research

Simple degradation model serves these needs effectively.

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

**Important Note**: This ADR documents the current confidence degradation approach. The design decision to use degradation vs. Bayesian updates remains open for future reconsideration based on academic research requirements and complexity/benefit analysis.