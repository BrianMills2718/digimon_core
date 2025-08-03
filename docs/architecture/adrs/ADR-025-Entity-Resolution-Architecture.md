# ADR-025: Entity Resolution Architecture Decision

**Status**: Accepted  
**Date**: 2025-01-29  
**Related**: [ADR-007](ADR-007-uncertainty-metrics.md) (Superseded uncertainty framework), [ADR-029](ADR-029-IC-Informed-Uncertainty-Framework/ADR-029-IC-Informed-Uncertainty-Framework.md) (Current uncertainty framework), [ADR-008](ADR-008-Core-Service-Architecture.md) (Identity service)  
**Context**: Need for balanced entity resolution approach in KGAS leveraging modern LLM capabilities while maintaining mathematical coherence

## Context

KGAS requires sophisticated entity resolution to handle referential uncertainty in discourse analysis. Previous approaches ranged from overly simplistic point estimates to over-engineered Bayesian network systems. The challenge is finding the right balance between sophistication and practicality while leveraging modern LLM capabilities.

**Key Requirements**:
- Handle pronouns, group references, and strategic ambiguity in discourse
- Leverage modern LLM intelligence for context-aware disambiguation
- Maintain mathematical coherence in uncertainty aggregation  
- Provide research-focused guidance on methodology selection
- Scale to large document collections for academic research

## Decision

We will implement a **Balanced Entity Resolution Architecture** based on the IC-Informed uncertainty framework ([ADR-029](ADR-029-IC-Informed-Uncertainty-Framework/ADR-029-IC-Informed-Uncertainty-Framework.md)), emphasizing LLM-intelligent disambiguation with realistic confidence ranges and mathematical coherence.

### Core Architectural Decisions

#### 1. LLM-Intelligent Resolution with Realistic Confidence Ranges
- **Modern LLM Capabilities**: Leverage context-aware LLM intelligence achieving 0.75-0.95 confidence for most entity resolution
- **Evidence-Based Calibration**: Confidence ranges based on actual LLM performance rather than theoretical assumptions
- **Strategic Ambiguity Recognition**: Distinguish intentional vagueness (0.40-0.60 confidence) from lack of information

#### 2. Mathematical Coherence in Aggregation
- **Frequency ≠ Confidence**: Strict separation between entity occurrence counts and resolution confidence scores
- **No Probability Addition**: Avoid mathematical errors of adding probabilities across instances
- **Distribution Preservation**: Maintain probability distributions for genuine uncertainty cases

#### 3. Three-Tier Processing Architecture
- **Context Assessment**: Evaluate context strength and ambiguity type before resolution
- **Intelligent Resolution**: Apply appropriate resolution strategy based on context assessment
- **Uncertainty Preservation**: Preserve uncertainty when genuine, resolve when supported by evidence

#### 4. Research Impact Focus
- **Methodology Guidance**: Provide clear guidance on appropriate research methods given uncertainty levels
- **Quality Thresholds**: Define confidence thresholds for different analytical approaches
- **Transparent Reporting**: Enable researchers to understand and report uncertainty appropriately

## Rationale

### Advantages of Balanced Approach

#### Over Simple Point Estimates
- **Information Preservation**: Maintains uncertainty information crucial for research decisions
- **Mathematical Accuracy**: Avoids false precision and probability errors
- **Research Transparency**: Enables appropriate uncertainty disclosure

#### Over Complex Tracking Systems
- **Practical Scalability**: Linear complexity suitable for large document collections
- **Implementation Simplicity**: Easier to implement and maintain than complex coreference systems
- **Focused Sophistication**: Sophistication where it matters most (LLM intelligence, uncertainty preservation)

#### Over Overly-Engineered Bayesian Networks
- **Mathematical Coherence**: Avoids probabilistic errors while maintaining sophistication
- **Realistic Assessment**: Based on actual LLM capabilities rather than theoretical complexity
- **Research Usability**: Provides actionable guidance rather than technical complexity for its own sake

### Modern LLM Intelligence Leverage

**Context-Aware Disambiguation**: Modern LLMs with context excel at entity resolution:
- **Explicit identification**: "As Democrats, we..." → 90-95% confidence
- **Contextual inference**: "We" with supporting context → 80-90% confidence  
- **Strategic ambiguity detection**: Recognizes intentional vagueness → 40-60% confidence

**Intelligent Processing**: LLMs can:
- Assess context strength and determine appropriate resolution strategy
- Generate realistic probability distributions for uncertain cases
- Recognize patterns indicating strategic ambiguity vs information lack

### Research-Focused Design

**Quality Assessment**: Provides composite quality scores guiding methodology selection:
- **High quality** (≥0.80): Quantitative analysis suitable
- **Moderate quality** (0.65-0.80): Mixed methods recommended
- **Low quality** (<0.65): Qualitative/exploratory approaches recommended

**Transparent Uncertainty**: Enables researchers to:
- Understand sources and levels of uncertainty
- Make informed decisions about analytical approaches
- Report findings with appropriate confidence levels

## Consequences

### Positive

- **Realistic Confidence Assessment**: Reflects actual LLM capabilities with context
- **Mathematical Coherence**: Prevents probabilistic errors in aggregation
- **Research Transparency**: Enables appropriate uncertainty disclosure and methodology selection
- **Scalable Processing**: Linear complexity suitable for academic research scale
- **Implementation Practicality**: Balances sophistication with maintainability
- **Evidence-Based Design**: Based on extensive stress testing and validation

### Negative

- **Context Window Limitations**: Limited to sliding window context (not cross-document)
- **Single Document Scope**: No cross-document entity linking capability
- **Strategic Ambiguity Challenges**: May mis-categorize some intentional vagueness
- **Cultural/Linguistic Scope**: Primarily optimized for English-language discourse
- **Temporal Limitations**: Basic temporal awareness only

### Neutral

- **Trade-off Acceptance**: Acknowledges limitations while maximizing benefits within scope
- **Enhancement Pathway**: Provides clear path for future improvements
- **Research Focus**: Prioritizes research utility over technical completeness

## Alternative Approaches Considered

### Complex Coreference Tracking Systems
- **Rejected**: Complexity doesn't justify benefits for academic research use case
- **Issues**: Over-engineering, scalability challenges, maintenance complexity

### Over-Engineered Bayesian Networks
- **Rejected**: Mathematical errors, unrealistic assumptions about LLM capabilities
- **Issues**: Probability addition errors, complexity without practical benefit

### Simple Point Estimates  
- **Rejected**: Information loss, false precision, inadequate for research transparency
- **Issues**: Hides uncertainty, prevents informed methodology decisions

### Pre-LLM Pattern Matching
- **Rejected**: Doesn't leverage modern LLM intelligence and context awareness
- **Issues**: Underestimates actual LLM disambiguation capabilities

## Implementation Requirements

### Technical Architecture

#### Core Components
1. **IntelligentEntityResolver**: Context-aware LLM-based entity resolution
2. **CoherentEntityAggregation**: Mathematically sound aggregation preserving uncertainty  
3. **ContextAwareProcessor**: Document processing with sliding context windows
4. **ResearchSuitabilityAssessor**: Quality assessment and methodology guidance

#### Integration Points
- **Stage 2 Integration**: Entity resolution during construct extraction
- **Stage 3 Integration**: Uncertainty-preserving aggregation
- **Quality Assessment**: Research suitability evaluation and reporting

### Quality Standards

#### Confidence Range Calibration
- **High confidence** (0.85-0.95): Explicit identification, clear contextual references
- **Moderate confidence** (0.70-0.85): Contextual inference, speaker-based resolution
- **Uncertain cases** (0.50-0.70): Ambiguous pronouns, degraded context
- **Low confidence** (0.30-0.50): Strategic ambiguity, no context

#### Mathematical Coherence Requirements
- **Frequency Counts**: Simple counting, no probability addition
- **Confidence Scores**: Average confidence per entity, separate from frequency
- **Distribution Preservation**: Maintain uncertainty distributions for unresolved cases
- **Quality Metrics**: Composite scores for research methodology guidance

### Validation Requirements

#### Calibration Validation
- Confidence ranges must reflect actual LLM performance with context
- Test cases spanning different ambiguity types and context levels
- Validation against human expert assessments

#### Mathematical Validation  
- Aggregation must preserve mathematical coherence
- No addition of probabilities across instances
- Proper separation of frequency counts from confidence scores

#### Research Impact Validation
- Quality thresholds must correlate with appropriate methodology selection
- Uncertainty reporting must enable informed research decisions
- Validation against real research scenarios and requirements

## Implementation Timeline

### Phase 1: Core Architecture (Immediate)
- Implement IntelligentEntityResolver with realistic confidence ranges
- Create CoherentEntityAggregation with mathematical coherence
- Integrate with existing KGAS pipeline stages

### Phase 2: Quality Assessment (Near-term) 
- Implement ResearchSuitabilityAssessor
- Create quality dashboards and uncertainty reporting
- Validate against research scenarios

### Phase 3: Enhancement (Future)
- Cross-document entity linking capabilities
- Enhanced strategic ambiguity detection
- Multi-lingual and cross-cultural support

## Success Metrics

### Technical Metrics
- **Calibration Accuracy**: Confidence ranges reflect actual performance (±5%)
- **Mathematical Coherence**: Zero probability addition errors in aggregation
- **Processing Performance**: Linear complexity maintained for large document sets

### Research Impact Metrics
- **Methodology Guidance Accuracy**: Quality assessments correlate with appropriate methods
- **Uncertainty Transparency**: Researchers can understand and report uncertainty sources
- **Research Utility**: Enables informed decisions about analytical approaches

### Quality Metrics
- **Resolution Rate**: Percentage of entities successfully resolved (target: context-dependent)
- **Average Confidence**: Mean confidence of resolved entities (target: 0.75-0.85)
- **Uncertainty Mass**: Proportion of genuinely uncertain cases preserved appropriately

## Related Decisions

- **[ADR-007: CERQual-Based Uncertainty Architecture](ADR-007-uncertainty-metrics.md)**: Overall uncertainty framework
- **[Comprehensive6 Framework](../kgas_uncertainty_framework_comprehensive6.md)**: Authoritative uncertainty implementation
- **[Entity Resolution Architecture](../entity_resolution_under_uncertainty.md)**: Detailed implementation specification

## References

### Validation Documentation
- **[Entity Resolution Stress Tests](../../examples/entity_resolution_uncertainty_stress_tests.md)**: Comprehensive validation scenarios
- **[Research Impact Scenarios](../../examples/entity_resolution_research_impact_scenarios.md)**: Real research impact assessment
- **[Uncertainty Flow Documentation](../../examples/kgas_uncertainty_flow_comprehensive.md)**: Pipeline uncertainty tracking

### Technical Specifications  
- **[Uncertainty Architecture](../concepts/uncertainty-architecture.md)**: Technical architecture details
- **[Entity Resolution Implementation](../entity_resolution_under_uncertainty.md)**: Complete implementation guide

---

This architectural decision establishes the foundation for realistic, mathematically coherent, and research-focused entity resolution in KGAS, enabling transparent uncertainty handling that enhances rather than hinders research quality.