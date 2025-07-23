# T91: Analysis of Competing Hypotheses (ACH) Tool Implementation

**Phase**: 2.2 Statistical Analysis Tools  
**Tool ID**: T91  
**Status**: PLANNED  
**Priority**: HIGH - Revolutionary for systematic theory comparison  

## Overview

Implement the Analysis of Competing Hypotheses (ACH) methodology adapted from CIA techniques for academic theory evaluation. This tool leverages frontier LLMs to apply ACH with human-like intelligence and flexibility, adapting the methodology to research contexts rather than following rigid rules.

## LLM-Driven Implementation Philosophy

Rather than hard-coding ACH procedures, T91 uses LLMs as intelligent research analysts who:

1. **Adapt complexity to context**: Full matrix for 5 theories, simplified comparison for 50
2. **Handle evolving hypotheses**: Track conceptual evolution, not just text changes
3. **Exercise judgment**: Know when to simplify, when to caveat, when to seek help
4. **Provide transparent reasoning**: Always explain analytical decisions
5. **Degrade gracefully**: Never fail - always provide useful analysis with appropriate limitations

## Tool Design

### Core Functionality - LLM as Intelligent Analyst

```python
class T91_ACHAnalyzer(BaseTool):
    """
    LLM applies ACH methodology with human-like flexibility and judgment
    Adapts analysis to research context rather than following rigid rules
    """
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(service_manager)
        self.tool_id = "T91"
        self.name = "ACH Theory Competition Analyzer"
        self.category = "advanced_analytics"
        self.llm_analyst = LLMAnalyst()  # Frontier LLM as intelligent analyst
        
    def execute(self, request: ToolRequest) -> ToolResult:
        """
        LLM intelligently applies ACH based on research context
        
        Input:
            theories: List[Theory] - Competing theories (can evolve during analysis)
            evidence: List[Evidence] - Available evidence  
            context: ResearchContext - Domain, stage, constraints
            
        Output:
            Adaptive based on context:
            - Full ACH matrix for manageable cases
            - Simplified comparison for complex cases
            - Phased analysis for evolving research
            - Always includes reasoning and limitations
        """
        # LLM determines appropriate approach
        approach = self.llm_analyst.assess_situation(
            theories, evidence, context
        )
        
        if approach.can_do_full_ach:
            return self.full_ach_analysis(theories, evidence)
        else:
            return self.adaptive_analysis(theories, evidence, approach)
```

### Key Components with LLM Intelligence

#### 1. Intelligent Theory-Evidence Assessment
```python
class LLMTheoryEvidenceAnalyzer:
    """LLM assesses theory-evidence relationships like expert researcher"""
    
    def assess_consistency(self, theory: Theory, evidence: Evidence) -> ConsistencyAnalysis:
        """LLM reasons about consistency like human expert"""
        return self.llm.analyze(f"""
        As an expert in {theory.domain}, assess how this evidence relates to the theory:
        Theory: {theory}
        Evidence: {evidence}
        
        Consider:
        - Is this evidence consistent, inconsistent, or irrelevant?
        - How strong is the support/contradiction?
        - Are there alternative interpretations?
        - What caveats should we note?
        
        Reason step-by-step as a domain expert would.
        """)
    
    def handle_evolving_theory(self, original: Theory, refined: Theory):
        """LLM handles theory evolution intelligently"""
        return self.llm.determine_continuity(original, refined)
```

#### 2. Adaptive Disconfirmation Analysis
```python
class AdaptiveDisconfirmationAnalyzer:
    """LLM applies disconfirmation principle flexibly"""
    
    def analyze_based_on_context(self, theories: List[Theory], 
                                evidence: List[Evidence],
                                constraints: ResearchConstraints):
        """Adapt analysis to research situation"""
        if len(theories) * len(evidence) > 500:
            # Too complex for full matrix
            return self.llm.simplified_disconfirmation_analysis(
                top_theories=self.select_most_promising(theories, n=5),
                critical_evidence=self.find_most_diagnostic(evidence, n=20)
            )
        else:
            return self.full_disconfirmation_matrix(theories, evidence)
```

#### 3. Intelligent Evidence Prioritization
```python
class LLMEvidencePrioritizer:
    """LLM identifies most valuable evidence like experienced researcher"""
    
    def suggest_next_evidence(self, current_state: ACHState) -> EvidenceRecommendations:
        """What would an expert look for next?"""
        return self.llm.analyze(f"""
        Current ACH state:
        - Leading theories: {current_state.top_theories}
        - Key uncertainties: {current_state.uncertainties}
        - Available resources: {current_state.resources}
        
        As a senior researcher, what evidence would you seek next to:
        1. Best distinguish between leading theories?
        2. Test critical assumptions?
        3. Resolve key uncertainties?
        
        Consider feasibility and value of different evidence types.
        """)
```

## Implementation Plan

### Week 1: Core ACH Engine

1. **Matrix Management**
   - Theory-evidence consistency matrix
   - Bayesian probability tracking
   - Dependency handling

2. **Consistency Assessment**
   - LLM-based consistency evaluation
   - Structured reasoning capture
   - Confidence scoring

### Week 2: Disconfirmation Logic

1. **Disconfirmation Focus**
   - Identify contradictory evidence
   - Weight disconfirming evidence appropriately
   - Resistance scoring algorithm

2. **Theory Ranking**
   - Survivability calculation
   - Sensitivity analysis
   - Confidence bounds

### Week 3: Academic Adaptations

1. **Literature Integration**
   - Import theories from papers
   - Extract evidence from sources
   - Citation network awareness

2. **Academic Output**
   - LaTeX table generation
   - Visualization exports
   - Publication-ready reports

### Week 4: Testing and Validation

1. **Scenario Testing**
   - Historical theory competitions
   - Known outcomes validation
   - Edge case handling

2. **User Studies**
   - Academic researcher feedback
   - Workflow integration testing
   - Documentation completion

## Integration Points

### With Uncertainty System (Phase 2.1)
- Use calibrated confidence scores
- Apply information value assessment
- Integrate Bayesian aggregation

### With Graph Analytics (T50-T60)
- Theory networks visualization
- Evidence flow analysis
- Citation influence mapping

### With Statistical Tools (T61-T70)
- Statistical significance of evidence
- Meta-analysis integration
- Hypothesis testing support

## Academic Use Cases

### 1. Literature Review
- Compare competing explanations systematically
- Identify critical experiments needed
- Avoid confirmation bias in review

### 2. Theory Development
- Test new theory against established ones
- Identify weaknesses in current theory
- Find anomalous evidence requiring new theories

### 3. Research Planning
- Determine most diagnostic experiments
- Prioritize evidence collection
- Justify research directions

### 4. Peer Review
- Systematic evaluation of claims
- Transparent reasoning process
- Identification of critical assumptions

## Success Metrics

1. **Accuracy**: Correctly identifies strongest theories in test cases
2. **Diagnosticity**: Successfully identifies discriminating evidence
3. **Usability**: Researchers can input theories without extensive training
4. **Transparency**: Clear explanation of rankings and reasoning
5. **Performance**: Handle 50+ theories with 100+ evidence pieces

## Configuration

```yaml
ach:
  enabled: true
  llm:
    model: "gpt-4"
    temperature: 0.0
  limits:
    max_theories: 100
    max_evidence: 1000
  output:
    formats: ["json", "latex", "markdown"]
    visualizations: ["matrix", "network", "ranking"]
  integration:
    use_calibration: true
    use_information_value: true
```

## Future Enhancements

1. **Dynamic ACH**: Real-time updates as new evidence arrives
2. **Collaborative ACH**: Multi-researcher theory evaluation
3. **Automated Theory Generation**: LLM suggests missing theories
4. **Cross-Domain ACH**: Compare theories across disciplines

## Academic Impact

ACH brings intelligence-grade analytical rigor to academic theory evaluation:
- **Reduces Confirmation Bias**: Forces consideration of disconfirming evidence
- **Systematic Comparison**: All theories evaluated against all evidence
- **Transparent Process**: Clear audit trail of reasoning
- **Diagnostic Focus**: Identifies most valuable future research

This tool represents a paradigm shift in how academic theories are compared and evaluated, bringing 50+ years of IC analytical refinement to scholarly research.