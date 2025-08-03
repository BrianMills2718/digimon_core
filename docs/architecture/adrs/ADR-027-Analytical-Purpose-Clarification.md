# ADR-027: Analytical Purpose Clarification

**Status**: ACCEPTED  
**Date**: 2025-01-29  
**Deciders**: Architecture Team  
**Related**: ADR-022, theoretical-framework.md, Thinking_out_loud/Analysis_Philosophy/*

## Context

Early architectural explorations revealed fundamental confusion about KGAS's analytical purpose:

1. **Analytical Tier Ambiguity**: Unclear whether KGAS should analyze text properties, use text to analyze world phenomena, or predict text effects on audiences
2. **Theory Application Confusion**: When applying theories like Prospect Theory to text, uncertainty about whether we're explaining text content, world phenomena, or predicting effects
3. **Mixed Analytical Claims**: Same analysis could be simultaneously descriptive (what's in text), explanatory (why it's there), predictive (what it will do), and prescriptive (how to improve it)
4. **Boundary Blurring**: No clear delineation between analyzing linguistic artifacts vs. using them as windows into external reality

This confusion risked unfocused analysis where finding theoretical patterns in text didn't translate to meaningful insights.

## Decision

We adopt a **hierarchical analytical approach with explicit human-driven tier selection**:

### Analytical Hierarchy
1. **Text Analysis** (Foundation): Analyze properties of linguistic artifacts
2. **World Analysis** (Primary Goal): Use text evidence to understand real-world phenomena  
3. **Effect Analysis** (Application): Predict how discourse affects readers/audiences

### Human Question-Driven Tier Selection
Analysis tier is explicitly determined by the human analyst's question type:

- **Descriptive Questions** → Text Analysis tier
  - "What linguistic patterns exist in this discourse?"
  - "How is this message structured?"
  
- **Explanatory Questions** → World Analysis tier
  - "What does this discourse reveal about political dynamics?"
  - "Why did the author choose this framing?"
  
- **Predictive Questions** → Effect Analysis tier
  - "How will this message affect voter behavior?"
  - "What psychological responses will this trigger?"
  
- **Prescriptive Questions** → Design Guidance (meta-tier)
  - "How should we craft messages for desired outcomes?"
  - "What framing would be more effective?"

### Integration with Two-Layer Architecture
This decision integrates with the two-layer architecture (ADR-022):
- **Layer 1**: Extracts theoretical structures (remains tier-agnostic)
- **Layer 2**: Applies structures based on human question (determines tier)

## Rationale

### Why Hierarchical Organization
- **Conceptual Clarity**: Clear progression from concrete (text) to abstract (world) to applied (effects)
- **Methodological Soundness**: Can't analyze effects without understanding world; can't understand world without analyzing text
- **Operational Efficiency**: Different tiers require different computational approaches

### Why Human-Driven Selection
- **Eliminates Ambiguity**: Explicit questions prevent mixed or unfocused analysis
- **Preserves Flexibility**: Same text can be analyzed at different tiers for different purposes
- **Enables Validation**: Clear analytical goals allow for appropriate success metrics

### Why This Resolves Confusion
- **Explicit Boundaries**: Clear what each tier analyzes and produces
- **Purposeful Analysis**: Human questions drive focused investigation
- **Theoretical Clarity**: Theories apply differently at each tier

## Consequences

### Positive
- **Analytical Focus**: Every analysis has clear purpose and success criteria
- **Methodological Rigor**: Appropriate methods selected for each tier
- **User Clarity**: Researchers understand what type of analysis they're requesting
- **Computational Efficiency**: Systems optimized for specific analytical tiers

### Negative
- **User Burden**: Requires explicit question formulation
- **Training Need**: Users must understand tier distinctions
- **Potential Misalignment**: Users might select inappropriate tier for their needs

### Mitigations
- **LLM Assistance**: Frontier LLMs help users formulate appropriate questions
- **Tier Suggestions**: System recommends analytical tier based on question patterns
- **Examples and Templates**: Provide clear examples of each question type

## Implementation

### Question Classification System
```python
QUESTION_PATTERNS = {
    "descriptive": [
        "what.*patterns", "how.*structured", "identify.*features",
        "list.*elements", "describe.*content"
    ],
    "explanatory": [
        "why.*choose", "what.*reveals", "how.*reflects",
        "explain.*dynamics", "understand.*context"
    ],
    "predictive": [
        "will.*affect", "predict.*response", "forecast.*impact",
        "anticipate.*reaction", "estimate.*effect"
    ],
    "prescriptive": [
        "should.*design", "how.*improve", "recommend.*approach",
        "optimize.*message", "enhance.*effectiveness"
    ]
}
```

### Integration Points
- **Theory Meta-Schema**: `telos` field specifies which tiers each theory supports
- **Pipeline Orchestrator**: Routes analysis based on identified tier
- **Analytics Service**: Selects appropriate cross-modal approach per tier
- **LLM Prompting**: Tier-specific prompts for optimal analysis

## Alternatives Considered

### Single Universal Analysis Mode
- **Approach**: One analytical approach for all purposes
- **Rejected Because**: Led to unfocused analysis and mixed claims

### Automatic Tier Detection
- **Approach**: System infers analytical tier from context
- **Rejected Because**: Too ambiguous, often led to misaligned analysis

### Fixed Theory-Tier Mappings
- **Approach**: Each theory locked to specific analytical tier
- **Rejected Because**: Reduces flexibility, theories often apply across tiers

## Related Documentation

- **[theoretical-framework.md](../concepts/theoretical-framework.md)**: Detailed tier definitions
- **[ADR-022](ADR-022-Theory-Selection-Architecture.md)**: Two-layer architecture
- **[Thinking_out_loud/Analysis_Philosophy/](../Thinking_out_loud/Analysis_Philosophy/)**: Original explorations

## Review and Updates

- **Next Review**: After 50+ analyses across all tiers
- **Success Metrics**: User satisfaction with analytical focus, result relevance
- **Evolution Triggers**: New analytical needs, user feedback patterns

---

**Bottom Line**: By making analytical purpose explicit through human questions, we eliminate confusion and enable focused, purposeful analysis. The hierarchical approach provides conceptual clarity while maintaining flexibility for diverse research needs.