# ADR-016: Bayesian Uncertainty Aggregation System

**Status**: Accepted  
**Date**: 2025-07-23  
**Context**: KGAS needs to handle multiple sources reporting the same claim with potentially different confidence levels. The current degradation-only model (ADR-010) cannot account for evidence accumulation from multiple sources.

## Decision

We will implement a **Bayesian uncertainty aggregation system** that uses LLM intelligence to estimate parameters for proper Bayesian updating when multiple sources report the same claim.

### Core Architecture

```python
from pydantic import BaseModel

class BayesianAnalysisOutput(BaseModel):
    prior_H: float  # P(H) - prior probability
    joint_likelihood_given_H: float  # P(E₁,E₂,...,Eₙ|H)
    joint_likelihood_given_not_H: float  # P(E₁,E₂,...,Eₙ|¬H)
    reasoning: str  # Explanation of the analysis

class BayesianAggregationService:
    def aggregate_multiple_sources(
        self, 
        claims: List[ExtractedClaim],
        theory_context: TheorySchema
    ) -> AggregatedClaim:
        # 1. LLM analyzes dependencies and estimates parameters
        analysis = self.llm.perform_bayesian_analysis(
            claims=claims,
            prompt=self._create_bayesian_prompt(claims, theory_context),
            response_format=BayesianAnalysisOutput
        )
        
        # 2. Programmatic Bayesian update
        posterior = self._bayesian_update(analysis)
        
        # 3. Meta-uncertainty adjustment
        final_confidence = self._adjust_for_meta_uncertainty(
            posterior, analysis.reasoning
        )
        
        return AggregatedClaim(
            claim=claims[0].normalize(),
            confidence=final_confidence,
            method="bayesian_aggregation",
            source_count=len(claims),
            audit_trail=self._create_audit_trail(analysis, posterior)
        )
```

## Rationale

### Why Bayesian Aggregation?

**1. Mathematical Soundness**: Bayesian updating provides a principled framework for combining evidence while accounting for dependencies between sources.

**2. LLM Intelligence Leverage**: LLMs can assess complex factors like:
- Source independence (citation networks, temporal dependencies)
- Domain-specific evidence patterns
- Theory requirements (actual influence vs. perception)

**3. Evidence Accumulation**: Unlike degradation-only, this allows confidence to increase when multiple independent sources confirm a claim.

**4. Dependency Handling**: Proper joint likelihood estimation prevents overconfidence from dependent sources.

### Why LLM Parameter Estimation?

**1. Context-Aware Assessment**: LLMs can consider:
- Citation relationships between sources
- Temporal cascade effects (later sources influenced by earlier)
- Domain conventions (courtesy citations, grant strategies)
- Theory-specific requirements

**2. Flexible Intelligence**: No need for rigid rules about specific dependency types - LLM adapts to each situation.

**3. Transparent Reasoning**: LLM provides explanation for its parameter estimates, enabling audit and validation.

## Implementation Details

### Bayesian Update Formula

```python
def bayesian_update(analysis: BayesianAnalysisOutput) -> float:
    """Apply Bayes' theorem with LLM-estimated parameters"""
    numerator = analysis.prior_H * analysis.joint_likelihood_given_H
    denominator = (
        (analysis.prior_H * analysis.joint_likelihood_given_H) + 
        ((1 - analysis.prior_H) * analysis.joint_likelihood_given_not_H)
    )
    
    posterior = numerator / denominator
    return posterior
```

### LLM Prompt Strategy

```python
prompt = """You are an expert Bayesian analyst. Multiple sources report:
[source details with confidence levels]

Apply Bayesian reasoning to determine the posterior probability of this claim.

Remember that Bayesian updating requires:
- Prior probability P(H)
- Joint likelihood P(E₁,E₂,...,Eₙ|H) - probability of observing ALL evidence if H is true
- Joint likelihood P(E₁,E₂,...,Eₙ|¬H) - probability of observing ALL evidence if H is false

If sources are not independent, the joint likelihood is NOT simply the product 
of individual likelihoods. You must consider how evidence pieces relate.

Estimate these probabilities and explain your reasoning."""
```

### Integration with Existing Systems

**1. Claim Matching**: System first identifies claims about the same relationship
**2. Dependency Analysis**: LLM analyzes source relationships
**3. Bayesian Aggregation**: Apply proper updating with dependencies
**4. Theory Integration**: Consider theory requirements in prior estimation
**5. Audit Trail**: Complete record of aggregation process

## Alternatives Considered

### 1. Simple Averaging
**Rejected**: Ignores evidence strength differences and dependencies

### 2. Maximum Confidence
**Rejected**: Discards valuable corroborating evidence

### 3. Hardcoded Dependency Rules
**Rejected**: Cannot handle complex, context-specific dependencies

### 4. Full Bayesian Network
**Rejected**: Too complex for dynamic claim aggregation

## Consequences

### Positive
- **Mathematically Sound**: Proper handling of dependent evidence
- **Context-Aware**: Adapts to domain and theory requirements
- **Evidence Accumulation**: Multiple sources can strengthen claims
- **Audit Trail**: Transparent reasoning for all aggregations
- **Flexible**: Handles various dependency types without rigid rules

### Negative
- **Computational Cost**: LLM analysis for each multi-source claim
- **Consistency**: LLM estimates may vary between runs
- **Complexity**: More complex than simple degradation
- **Calibration Need**: Requires validation against human judgments

## Performance Considerations

### Optimization Strategies

```python
class OptimizedBayesianAggregation:
    def should_use_full_analysis(self, claims: List[Claim]) -> bool:
        # Use full Bayesian analysis for complex cases
        if len(claims) > 3 or self._has_complex_dependencies(claims):
            return True
        # Use simple aggregation for straightforward cases
        return False
    
    def aggregate(self, claims: List[Claim]) -> AggregatedClaim:
        if self.should_use_full_analysis(claims):
            return self._full_bayesian_analysis(claims)
        else:
            return self._simple_aggregation(claims)
```

### Caching Strategy
- Cache Bayesian analyses by claim fingerprint
- Reuse analyses for identical claim sets
- Expire cache based on theory context changes

## Validation and Calibration

### Validation Methods
1. **Mechanical Turk Studies**: Compare to human expert aggregations
2. **Consistency Testing**: Ensure similar cases get similar treatment
3. **Perturbation Analysis**: Test robustness to parameter variations
4. **Theory Alignment**: Verify aggregations align with theory requirements

### Calibration Process
```python
class CalibrationService:
    def calibrate_priors(self, domain: str, validation_data: List[ValidationCase]):
        # Learn domain-specific priors from validated cases
        # Store in prior library for future use
        
    def validate_aggregation(self, aggregated: AggregatedClaim, expert_judgment: float):
        # Track accuracy of Bayesian aggregations
        # Adjust meta-uncertainty factors based on performance
```

## Related Systems

### Integration Points
- **ADR-010**: Quality System (provides base confidences)
- **ADR-004**: Confidence Score Ontology (defines confidence semantics)
- **Theory Repository**: Provides context for prior estimation
- **Audit Service**: Records complete aggregation process

### Configuration
```yaml
uncertainty:
  aggregation:
    method: "bayesian_llm"
    llm_model: "gpt-4"
    cache_enabled: true
    optimization:
      simple_threshold: 3  # Use simple method for ≤3 sources
      cache_ttl: 3600     # Cache for 1 hour
    calibration:
      mechanical_turk_enabled: true
      domain_priors:
        academic_influence: 0.15
        cross_field_influence: 0.05
```

## Migration Path

1. **Phase 1**: Implement alongside existing degradation system
2. **Phase 2**: A/B test on subset of multi-source claims  
3. **Phase 3**: Gradual rollout based on validation results
4. **Phase 4**: Full deployment with monitoring

## Future Enhancements

1. **Domain-Specific Prior Libraries**: Pre-computed priors for common domains
2. **Adaptive Meta-Uncertainty**: Learn uncertainty in LLM estimates
3. **Ensemble Methods**: Multiple LLMs for robust parameter estimation
4. **Real-time Calibration**: Continuous improvement from user feedback

This ADR establishes Bayesian aggregation as the primary method for handling multiple sources reporting the same claim, replacing simple degradation with mathematically sound evidence accumulation.