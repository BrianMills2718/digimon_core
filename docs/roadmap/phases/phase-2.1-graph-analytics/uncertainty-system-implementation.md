# Uncertainty System Implementation Plan

**Phase**: 2.1 Graph Analytics Tools  
**Status**: PLANNED  
**Priority**: HIGH - Critical for multi-source claim aggregation  

## Overview

Implement the Bayesian uncertainty aggregation system designed in ADR-016 to handle multiple sources reporting the same claim with proper dependency modeling.

## Implementation Tasks

### Task 1: Core Bayesian Aggregation Service (Week 1)

#### 1.1 Create BayesianAggregationService
```python
# Location: src/core/bayesian_aggregation_service.py
class BayesianAggregationService:
    def __init__(self, llm_client, service_manager):
        self.llm = llm_client
        self.service_manager = service_manager
```

#### 1.2 Implement Structured Output Models
- BayesianAnalysisOutput (Pydantic model)
- AggregatedClaim model
- DependencyAnalysisOutput model

#### 1.3 Core Bayesian Update Logic
- Programmatic Bayesian update function
- Meta-uncertainty adjustment
- Audit trail creation

### Task 2: Claim Matching and Clustering (Week 1-2)

#### 2.1 Entity Resolution Enhancement
- Extend IdentityService for claim matching
- Handle predicate variations ("influenced_by" vs "cited")
- Temporal context matching

#### 2.2 Claim Clustering Algorithm
- Group claims about same relationships
- Handle entity variations ("Johnson" vs "Bob Johnson")
- Preserve source metadata

### Task 3: LLM Integration for Parameter Estimation (Week 2)

#### 3.1 Prompt Engineering
- Develop robust Bayesian analysis prompts
- Include domain context handling
- Support structured output format

#### 3.2 Dependency Analysis
- Citation network detection
- Temporal cascade identification
- Source independence assessment

### Task 4: Integration with Existing Systems (Week 2-3)

#### 4.1 Quality Service Integration
- Get base confidence from QualityService
- Apply degradation factors before aggregation
- Update quality tiers based on aggregated confidence

#### 4.2 Theory Repository Integration
- Use theory context for prior estimation
- Consider theory requirements in aggregation
- Update theory-specific confidence

#### 4.3 Provenance Service Integration
- Track complete aggregation process
- Store LLM reasoning
- Enable aggregation replay

### Task 5: Performance Optimization (Week 3)

#### 5.1 Caching Strategy
```python
class AggregationCache:
    def get_cached_analysis(self, claim_fingerprint: str) -> Optional[BayesianAnalysisOutput]
    def cache_analysis(self, claim_fingerprint: str, analysis: BayesianAnalysisOutput)
```

#### 5.2 Adaptive Processing
- Simple aggregation for ≤3 sources
- Full Bayesian analysis for complex cases
- Configurable thresholds

### Task 6: Testing and Validation (Week 3-4)

#### 6.1 Unit Tests
- Test Bayesian update mathematics
- Test LLM parameter estimation
- Test dependency detection

#### 6.2 Integration Tests
- End-to-end aggregation workflow
- Multiple source scenarios
- Theory integration tests

#### 6.3 Validation Studies
- Prepare for Mechanical Turk validation
- Create test scenarios with known dependencies
- Compare to expert human judgments

## Implementation Order

1. **Core Mathematics First**: Implement Bayesian update logic
2. **LLM Integration**: Add parameter estimation
3. **System Integration**: Connect to existing services
4. **Optimization**: Add caching and adaptive processing
5. **Validation**: Comprehensive testing

## Configuration

```yaml
uncertainty:
  aggregation:
    enabled: true
    method: "bayesian_llm"
    llm:
      model: "gpt-4"
      temperature: 0.0  # Deterministic
    optimization:
      simple_threshold: 3
      cache_ttl: 3600
    validation:
      mechanical_turk_enabled: false  # Enable after initial implementation
```

## Success Criteria

1. **Functionality**: Successfully aggregate multiple sources with dependencies
2. **Accuracy**: Posterior probabilities align with expert judgments
3. **Performance**: <2s for typical 3-5 source aggregation
4. **Transparency**: Complete audit trail with LLM reasoning
5. **Integration**: Seamless with existing quality/theory systems

## Risk Mitigation

### LLM Consistency
- Use temperature=0 for deterministic outputs
- Cache results by claim fingerprint
- Implement retry with validation

### Computational Cost
- Pre-filter simple cases
- Batch similar claims
- Implement progressive refinement

### Prior Sensitivity
- Develop domain-specific prior libraries
- Allow manual prior adjustment
- Track prior impact in audit trail

## Future Enhancements

1. **Domain Prior Libraries**: Pre-computed priors for common domains
2. **Ensemble LLMs**: Multiple models for robust estimation
3. **Active Learning**: Learn from user feedback
4. **Real-time Calibration**: Continuous improvement

## Dependencies

- ADR-010: Quality System (base confidence)
- ADR-016: Bayesian Aggregation Design
- Theory Repository: Context for priors
- LLM API: Parameter estimation

## Timeline

- **Week 1**: Core service and claim matching
- **Week 2**: LLM integration and dependency analysis
- **Week 3**: System integration and optimization
- **Week 4**: Testing and validation preparation

Total: 4 weeks to production-ready implementation