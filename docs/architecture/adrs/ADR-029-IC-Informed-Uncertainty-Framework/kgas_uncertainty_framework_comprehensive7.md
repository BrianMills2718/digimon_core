# KGAS Uncertainty Framework - Comprehensive Version 7
## Intelligence Community-Informed Architecture

## Executive Summary

The KGAS uncertainty framework quantifies and manages uncertainty throughout the analytical pipeline using proven Intelligence Community (IC) methodologies. This version integrates IC best practices with modern LLM capabilities, providing transparent uncertainty tracking while avoiding false precision and unsustainable overhead.

**Key Improvements from V6**:
- Integrated IC methodologies (ICD-203/206, Heuer's principles, ACH)
- Mathematically coherent propagation (no probability addition)
- Single consolidated LLM analysis (not fragmented calls)
- Realistic confidence ranges based on empirical evidence
- Sustainable tracking without comprehensive overhead

## Core Philosophy

**Primary Principle**: "Evidence-based uncertainty quantification with IC-proven methodologies and LLM intelligence"

The framework:
- **Applies** IC standards for uncertainty expression (ICD-203)
- **Evaluates** source quality systematically (ICD-206)
- **Mitigates** cognitive biases through structured techniques
- **Leverages** LLM capabilities for intelligent analysis
- **Maintains** mathematical rigor in propagation

## Foundational IC Principles

### 1. ICD-203 Probability and Confidence Standards

```python
# Standardized probability expressions
IC_PROBABILITY_BANDS = {
    "almost_no_chance": (0.01, 0.05),
    "very_unlikely": (0.05, 0.20),
    "unlikely": (0.20, 0.45),
    "roughly_even_chance": (0.45, 0.55),
    "likely": (0.55, 0.80),
    "very_likely": (0.80, 0.95),
    "almost_certain": (0.95, 0.99)
}

# Confidence levels (in the assessment, not the outcome)
IC_CONFIDENCE_LEVELS = {
    "low": "Questionable credibility, significant data gaps",
    "moderate": "Credible sources, some corroboration",
    "high": "Well-corroborated, consistent, plausible"
}
```

### 2. ICD-206 Source Quality Framework

```python
class SourceQualityAssessment:
    """ICD-206 compliant source evaluation"""
    
    def assess_source(self, source):
        return {
            "reliability": self._assess_reliability(source),  # A-F scale
            "credibility": self._assess_credibility(source),  # 1-6 scale
            "relevance": self._assess_relevance(source),
            "timeliness": self._assess_timeliness(source),
            "technical_quality": self._assess_technical_quality(source)
        }
```

### 3. Heuer's Information Paradox Awareness

**Key Insight**: More information increases confidence without necessarily improving accuracy.

```python
def track_information_paradox(self, assessment_history):
    """Monitor for false confidence from information quantity"""
    
    return {
        "information_quantity": len(assessment_history),
        "confidence_trend": self._calculate_confidence_trend(assessment_history),
        "accuracy_indicators": self._identify_accuracy_markers(assessment_history),
        "paradox_risk": self._assess_paradox_risk(assessment_history),
        "mitigation": "Focus on diagnostic value, not quantity"
    }
```

## Integrated LLM Analysis Architecture

### Single Consolidated Analysis Call

Instead of multiple fragmented LLM calls, use one comprehensive structured analysis:

```python
class IntegratedUncertaintyAnalysis:
    """Single LLM call for comprehensive IC-informed analysis"""
    
    def analyze_with_ic_methods(self, research_question, evidence, context):
        prompt = f"""
        Conduct a comprehensive uncertainty analysis following IC methodologies:
        
        1. KEY ASSUMPTIONS CHECK
        - List all assumptions underlying the analysis
        - Rate criticality: (low/moderate/high)
        - Identify which assumptions most affect conclusions
        
        2. DECISION-CRITICAL FACTORS
        - What factors would most change the conclusion if wrong?
        - What information gaps are most critical?
        - What monitoring would detect changes?
        
        3. ANALYSIS OF COMPETING HYPOTHESES (ACH)
        - Generate 3-5 plausible alternative explanations
        - Evaluate evidence AGAINST each hypothesis
        - Focus on disconfirming evidence
        - Avoid satisficing on first plausible explanation
        
        4. SOURCE QUALITY ASSESSMENT (ICD-206)
        - Reliability: Historical accuracy of source type
        - Credibility: Source expertise and access
        - Relevance: Direct vs indirect evidence
        - Corroboration: Independent confirmation
        
        5. COGNITIVE BIAS DETECTION
        - Confirmation bias indicators
        - Availability heuristic risks
        - Anchoring effects
        - Mirror imaging assumptions
        
        6. UNCERTAINTY EXPRESSION (ICD-203)
        - Express likelihood using standard terms
        - Separate confidence in assessment from probability
        - Provide reasoning transparency
        
        7. QUALITY CONTROL
        - Devil's Advocacy: Best argument against conclusion
        - What if Analysis: Key assumption violations
        - Alternative Futures: Different evolution paths
        
        Research Question: {research_question}
        Evidence: {evidence}
        Context: {context}
        
        Provide structured JSON output with all sections.
        """
        
        return self.llm.analyze(prompt, output_format="json")
```

## Mathematical Uncertainty Propagation

### Hard-Coded Propagation Rules

Uncertainty propagation uses rigorous mathematics, not LLM approximation:

```python
class UncertaintyPropagation:
    """Mathematically correct uncertainty propagation"""
    
    def propagate_independent_uncertainties(self, uncertainties):
        """For independent sources: Ã_total = (Ã² + Ã‚² + ... + Ã™²)"""
        
        # Convert confidence to uncertainty (variance)
        variances = [(1 - conf)**2 for conf in uncertainties]
        
        # Root sum of squares for independent uncertainties
        combined_variance = sum(variances)
        combined_uncertainty = math.sqrt(combined_variance)
        
        # Convert back to confidence
        return 1 - combined_uncertainty
    
    def propagate_dependent_uncertainties(self, uncertainties, correlation_matrix):
        """For dependent sources with known correlations"""
        
        n = len(uncertainties)
        combined_variance = 0
        
        # Full covariance calculation
        for i in range(n):
            for j in range(n):
                var_i = (1 - uncertainties[i])**2
                var_j = (1 - uncertainties[j])**2
                correlation = correlation_matrix[i, j]
                
                combined_variance += correlation * math.sqrt(var_i * var_j)
        
        return 1 - math.sqrt(combined_variance)
    
    def propagate_mixed_operations(self, operation_type, inputs):
        """Different propagation for different operations"""
        
        if operation_type == "multiplication":
            # For A * B, relative uncertainties add in quadrature
            relative_vars = [(inp['uncertainty']/inp['value'])**2 for inp in inputs]
            combined_relative = math.sqrt(sum(relative_vars))
            return combined_relative
            
        elif operation_type == "addition":
            # For A + B, absolute uncertainties add in quadrature
            absolute_vars = [inp['uncertainty']**2 for inp in inputs]
            return math.sqrt(sum(absolute_vars))
            
        elif operation_type == "division":
            # For A / B, similar to multiplication
            return self.propagate_mixed_operations("multiplication", inputs)
```

## Entity Resolution with IC Principles

### Evidence-Based Resolution (Not Format-Based)

```python
class EvidenceBasedEntityResolution:
    """Entity resolution based on evidence quality, not representation format"""
    
    def resolve_entity(self, reference, all_evidence):
        """Resolve entities using all available evidence regardless of format"""
        
        # Collect evidence from all sources
        evidence_items = []
        
        # Graph evidence
        if graph_evidence := all_evidence.get('graph'):
            evidence_items.extend(self._extract_graph_evidence(reference, graph_evidence))
        
        # Table evidence  
        if table_evidence := all_evidence.get('table'):
            evidence_items.extend(self._extract_table_evidence(reference, table_evidence))
            
        # Text evidence
        if text_evidence := all_evidence.get('text'):
            evidence_items.extend(self._extract_text_evidence(reference, text_evidence))
        
        # Evaluate each piece of evidence by quality, not source
        weighted_hypotheses = defaultdict(float)
        total_weight = 0
        
        for evidence in evidence_items:
            quality = self._assess_evidence_quality(evidence)  # ICD-206 based
            weight = self._quality_to_weight(quality)
            
            for hypothesis, support in evidence['hypotheses'].items():
                weighted_hypotheses[hypothesis] += weight * support
                
            total_weight += weight
        
        # Normalize to probability distribution
        if total_weight > 0:
            distribution = {
                entity: score / total_weight 
                for entity, score in weighted_hypotheses.items()
            }
        else:
            distribution = {"unknown": 1.0}
            
        return {
            "distribution": distribution,
            "most_likely": max(distribution.items(), key=lambda x: x[1])[0],
            "confidence": self._calculate_resolution_confidence(evidence_items),
            "evidence_count": len(evidence_items),
            "quality_assessment": self._summarize_evidence_quality(evidence_items)
        }
```

### Realistic LLM Confidence Ranges

Based on empirical evidence and IC standards:

```python
ENTITY_RESOLUTION_CONFIDENCE = {
    "explicit_named_entity": {
        "range": (0.90, 0.99),
        "factors": ["Clear proper noun", "Unambiguous reference"],
        "example": "'President Biden said...' -> Biden"
    },
    
    "contextual_pronoun": {
        "range": (0.70, 0.90),
        "factors": ["Recent antecedent", "Clear context", "LLM effectiveness"],
        "example": "'Biden spoke. He said...' -> Biden"
    },
    
    "ambiguous_group_reference": {
        "range": (0.50, 0.75),
        "factors": ["Multiple candidates", "Vague terms", "Cultural context"],
        "example": "'They opposed the bill' -> Multiple parties possible"
    },
    
    "strategic_ambiguity": {
        "range": (0.25, 0.50),
        "factors": ["Intentional vagueness", "Political hedging"],
        "example": "'Some members of congress' -> Deliberately vague"
    },
    
    "no_context": {
        "range": (0.10, 0.30),
        "factors": ["Isolated reference", "Missing context"],
        "example": "Pronoun at document start"
    }
}
```

## Structured Analytic Techniques Integration

### Key Assumptions Check

```python
def perform_key_assumptions_check(self, analysis):
    """Structured examination of underlying assumptions"""
    
    return {
        "assumptions": [
            {
                "assumption": "Political actors behave rationally",
                "criticality": "high",
                "confidence": 0.7,
                "violation_impact": "Major conclusion changes",
                "indicators": ["Emotional rhetoric", "Ideological actions"]
            },
            {
                "assumption": "Document sample is representative",
                "criticality": "moderate", 
                "confidence": 0.8,
                "violation_impact": "Bias in patterns",
                "indicators": ["Source diversity", "Time coverage"]
            }
        ],
        "overall_robustness": 0.75,
        "recommendation": "Monitor assumption indicators"
    }
```

### Analysis of Competing Hypotheses (ACH)

```python
def perform_ach_analysis(self, hypotheses, evidence):
    """Systematic evaluation of alternative explanations"""
    
    # Create hypothesis-evidence matrix
    matrix = {}
    
    for hypothesis in hypotheses:
        matrix[hypothesis] = {}
        
        for evidence_item in evidence:
            # Evaluate if evidence supports, contradicts, or is neutral
            assessment = self._evaluate_evidence_hypothesis_fit(
                evidence_item, hypothesis
            )
            matrix[hypothesis][evidence_item['id']] = assessment
    
    # Calculate diagnosticity scores
    diagnosticity = self._calculate_diagnosticity(matrix)
    
    # Identify least disproven hypothesis
    scores = self._calculate_hypothesis_scores(matrix, diagnosticity)
    
    return {
        "matrix": matrix,
        "diagnosticity": diagnosticity,
        "hypothesis_ranking": sorted(scores.items(), key=lambda x: x[1], reverse=True),
        "key_discriminators": self._identify_key_evidence(matrix, diagnosticity),
        "recommendation": "Focus on gathering discriminating evidence"
    }
```

## Quality Metrics Without Tracking Overhead

### Selective Quality Tracking

```python
class SelectiveQualityMetrics:
    """Track only decision-critical quality metrics"""
    
    def __init__(self):
        self.critical_metrics = {
            "entity_resolution_rate": None,
            "source_quality_distribution": None,
            "assumption_confidence": None,
            "cross_modal_agreement": None
        }
    
    def update_critical_metrics(self, stage, results):
        """Update only if it affects decision quality"""
        
        if stage == "entity_resolution":
            # Only track if below threshold
            resolution_rate = results['resolution_rate']
            if resolution_rate < 0.70:
                self.critical_metrics['entity_resolution_rate'] = resolution_rate
                self._trigger_quality_alert("Low entity resolution", resolution_rate)
                
        elif stage == "source_assessment":
            # Only track poor sources
            poor_sources = [s for s in results['sources'] if s['quality'] < 3]
            if poor_sources:
                self.critical_metrics['source_quality_distribution'] = len(poor_sources)
                
        # Don't track everything - only decision-critical issues
```

### Research Suitability Assessment

```python
def assess_research_suitability(self, quality_metrics, ic_analysis):
    """Determine appropriate research methods given uncertainty"""
    
    # Combine traditional metrics with IC assessment
    combined_confidence = (
        quality_metrics.get('resolution_confidence', 0.7) * 0.3 +
        ic_analysis['source_quality_score'] * 0.3 +
        ic_analysis['assumption_robustness'] * 0.2 +
        ic_analysis['hypothesis_differentiation'] * 0.2
    )
    
    if combined_confidence >= 0.80:
        return {
            "status": "HIGH_CONFIDENCE", 
            "methods": {
                "quantitative": "RECOMMENDED",
                "hypothesis_testing": "APPROPRIATE",
                "causal_inference": "POSSIBLE_WITH_CARE"
            },
            "confidence": combined_confidence,
            "note": "Suitable for confirmatory research"
        }
    
    elif combined_confidence >= 0.65:
        return {
            "status": "MODERATE_CONFIDENCE",
            "methods": {
                "mixed_methods": "RECOMMENDED",
                "exploratory": "APPROPRIATE", 
                "pattern_identification": "RECOMMENDED"
            },
            "confidence": combined_confidence,
            "note": "Suitable for exploratory research"
        }
    
    else:
        return {
            "status": "LOW_CONFIDENCE",
            "methods": {
                "qualitative": "RECOMMENDED",
                "theory_building": "APPROPRIATE",
                "case_study": "RECOMMENDED"  
            },
            "confidence": combined_confidence,
            "note": "Focus on understanding, not confirmation"
        }
```

## Practical Implementation Guidelines

### 1. Pipeline Integration

```python
class KGASPipelineWithIC:
    """Main pipeline with IC-informed uncertainty handling"""
    
    def __init__(self):
        self.propagation = UncertaintyPropagation()
        self.ic_analyzer = IntegratedUncertaintyAnalysis()
        self.quality_tracker = SelectiveQualityMetrics()
    
    def process_research_question(self, question, documents):
        # Stage 1: Theory extraction with IC assessment
        theory_extraction = self.extract_theory(documents)
        theory_confidence = self._assess_theory_quality(theory_extraction)
        
        # Stage 2: Entity extraction with single LLM call
        ic_analysis = self.ic_analyzer.analyze_with_ic_methods(
            question, documents, theory_extraction
        )
        
        # Stage 3: Entity resolution using all evidence
        entities = self.resolve_entities_evidence_based(
            documents, ic_analysis
        )
        
        # Stage 4: Propagate uncertainty mathematically
        stage_confidences = [
            theory_confidence,
            ic_analysis['overall_confidence'],
            entities['average_confidence']
        ]
        
        final_confidence = self.propagation.propagate_independent_uncertainties(
            stage_confidences
        )
        
        return {
            "results": {
                "theory": theory_extraction,
                "ic_analysis": ic_analysis,
                "entities": entities
            },
            "confidence": {
                "by_stage": stage_confidences,
                "final": final_confidence,
                "ic_factors": ic_analysis['confidence_factors']
            },
            "suitability": self.assess_research_suitability(
                entities['quality_metrics'], ic_analysis
            )
        }
```

### 2. Reporting Framework

```python
def generate_uncertainty_report(self, results):
    """Generate IC-compliant uncertainty report"""
    
    return {
        "executive_summary": {
            "bottom_line": results['key_findings'],
            "confidence": self._ic_confidence_term(results['confidence']['final']),
            "key_assumptions": results['ic_analysis']['key_assumptions'][:3],
            "main_uncertainties": results['ic_analysis']['critical_gaps']
        },
        
        "detailed_assessment": {
            "source_quality": results['ic_analysis']['source_assessment'],
            "competing_hypotheses": results['ic_analysis']['ach_results'],
            "assumption_analysis": results['ic_analysis']['assumptions'],
            "bias_detection": results['ic_analysis']['cognitive_biases']
        },
        
        "uncertainty_disclosure": {
            "quantitative": {
                "final_confidence": results['confidence']['final'],
                "stage_breakdown": results['confidence']['by_stage'],
                "propagation_method": "Independent uncertainties (root-sum-squares)"
            },
            "qualitative": {
                "major_limitations": results['ic_analysis']['limitations'],
                "information_gaps": results['ic_analysis']['critical_gaps'],
                "alternative_explanations": results['ic_analysis']['alternatives']
            }
        },
        
        "research_guidance": {
            "recommended_methods": results['suitability']['methods'],
            "confidence_level": results['suitability']['status'],
            "next_steps": self._generate_research_recommendations(results)
        }
    }
```

### 3. Common Patterns

```python
# Pattern 1: IC-Compliant Confidence Expression
def express_finding_confidence(self, finding, confidence):
    """Express confidence using IC standards"""
    
    probability_term = self._confidence_to_ic_term(finding['likelihood'])
    confidence_qualifier = self._get_confidence_qualifier(confidence)
    
    return f"We assess with {confidence_qualifier} confidence that {finding['statement']} is {probability_term}"

# Pattern 2: Evidence-Based Aggregation
def aggregate_with_quality_weighting(self, instances):
    """Weight by evidence quality, not source format"""
    
    weighted_sum = 0
    total_weight = 0
    
    for instance in instances:
        quality_score = self._assess_evidence_quality(instance)
        weight = self._quality_to_weight(quality_score)
        
        weighted_sum += instance['value'] * weight
        total_weight += weight
    
    return {
        "value": weighted_sum / total_weight if total_weight > 0 else None,
        "confidence": self._calculate_aggregate_confidence(instances),
        "evidence_quality": self._summarize_quality_distribution(instances)
    }

# Pattern 3: Structured Bias Mitigation
def mitigate_cognitive_biases(self, analysis):
    """Apply structured techniques to reduce bias"""
    
    mitigations = []
    
    # Devil's Advocacy
    mitigations.append({
        "technique": "Devil's Advocacy",
        "application": self._generate_counter_argument(analysis),
        "impact": "Challenges primary assumptions"
    })
    
    # What-If Analysis  
    mitigations.append({
        "technique": "What-If Analysis",
        "application": self._test_assumption_violations(analysis),
        "impact": "Tests conclusion robustness"
    })
    
    # Alternative Futures
    mitigations.append({
        "technique": "Alternative Futures",
        "application": self._generate_alternative_scenarios(analysis),
        "impact": "Explores different evolution paths"
    })
    
    return mitigations
```

## Key Improvements from V6

### 1. Eliminated False Precision
- No more claiming exact confidence to 2 decimal places
- Use IC probability bands instead of precise percentages
- Acknowledge irreducible uncertainties

### 2. Sustainable Tracking
- Track only decision-critical metrics
- Single integrated LLM analysis instead of many calls
- Focus on quality over quantity of tracking

### 3. Evidence-Based Assessment
- Evaluate evidence by quality, not representation format
- No assumption that cross-modal agreement = truth
- Focus on diagnostic value of evidence

### 4. Mathematical Coherence
- Proper uncertainty propagation (no probability addition)
- Separate frequency from confidence
- Preserve uncertainty distributions

### 5. IC Best Practices
- Structured analytic techniques built-in
- Standardized uncertainty expression
- Cognitive bias mitigation
- Focus on alternative hypotheses

## Conclusion

The KGAS Comprehensive7 uncertainty framework integrates proven Intelligence Community methodologies with modern LLM capabilities to provide:

1. **Rigorous** uncertainty quantification without false precision
2. **Sustainable** tracking focused on decision-critical factors
3. **Transparent** assessment using IC standards
4. **Practical** guidance for research methodology selection
5. **Integrated** analysis leveraging LLM intelligence efficiently

By learning from IC experience and avoiding common pitfalls, this framework enables researchers to understand and communicate uncertainty honestly while making informed decisions about their analytical approach.