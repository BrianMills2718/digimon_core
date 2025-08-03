# KGAS Uncertainty Flow: Comprehensive Analysis

## Overview

This document provides a complete picture of how uncertainty flows through the KGAS pipeline, from initial theory extraction through final research conclusions, with particular focus on entity resolution challenges.

## The 6-Stage Pipeline with Uncertainty Tracking

### Stage 1: Theory Schema Extraction
**Input**: Academic papers defining theories
**Output**: Formal schema with constructs, entities, relations

```json
{
  "uncertainty_sources": {
    "theory_ambiguity": "Concepts may be poorly defined",
    "extraction_accuracy": "LLM interpretation of academic text",
    "schema_completeness": "May miss implicit constructs"
  },
  "typical_confidence": 0.80,
  "mitigation": "High-quality source papers, multiple extraction runs"
}
```

### Stage 2: Theory-to-Discourse Mapping (Entity Extraction)
**Input**: Theory schema + document text
**Output**: Extracted instances with entity references

```json
{
  "uncertainty_sources": {
    "entity_ambiguity": {
      "pronouns": "we, they, them unclear",
      "context_dependency": "meaning shifts with speaker",
      "temporal_evolution": "entities change over time"
    },
    "operationalization": "Abstract concepts to concrete phrases",
    "llm_variance": "Different runs produce different extractions"
  },
  "typical_confidence": 0.60,
  "examples": {
    "high_certainty": {"text": "We Democrats", "confidence": 0.95},
    "medium_certainty": {"text": "Our coalition", "confidence": 0.70},
    "low_certainty": {"text": "They don't understand", "confidence": 0.40}
  }
}
```

### Stage 3: Instance Aggregation
**Input**: Extracted instances with entities
**Output**: Aggregated patterns and frequencies

```json
{
  "uncertainty_propagation": {
    "from_stage_2": "Inherits entity resolution uncertainty",
    "new_sources": {
      "aggregation_method": "How to combine uncertain instances",
      "speaker_perspective": "Different viewpoints on same entities",
      "temporal_gaps": "Missing time periods"
    }
  },
  "mathematical_approach": {
    "frequency": "Count all instances (certain and uncertain)",
    "confidence": "Track average and range",
    "distribution": "Preserve full probability distributions"
  },
  "typical_confidence": 0.55
}
```

### Stage 4: Multi-Modal Analysis
**Input**: Aggregated data
**Output**: Graph, table, and vector analyses

```json
{
  "modal_uncertainties": {
    "graph": {
      "edge_confidence": "Relationships between uncertain entities",
      "community_detection": "Fuzzy boundaries affect clustering",
      "centrality": "Important nodes may be ambiguous entities"
    },
    "table": {
      "classification": "Uncertain entities affect grouping",
      "statistics": "Confidence intervals widen",
      "correlations": "Weakened by classification uncertainty"
    },
    "vector": {
      "embedding_variance": "Same entity, different contexts",
      "similarity": "Uncertain entities create noise",
      "clustering": "Overlapping groups"
    }
  },
  "uncertainty_reduction": {
    "mechanism": "Cross-modal validation",
    "typical_reduction": 0.10-0.20,
    "when_effective": "High agreement across modes"
  },
  "typical_confidence": 0.65
}
```

### Stage 5: Cross-Modal Integration
**Input**: Results from three modalities
**Output**: Integrated findings

```json
{
  "integration_challenges": {
    "modal_conflicts": "Different modes may disagree",
    "weighting": "How to balance uncertain sources",
    "missing_data": "Some modes may fail on uncertain data"
  },
  "propagated_uncertainty": {
    "inherited": "From all previous stages",
    "new": "Integration complexity"
  },
  "typical_confidence": 0.60
}
```

### Stage 6: Research Application
**Input**: Integrated analysis
**Output**: Answers to research questions

```json
{
  "final_uncertainty": {
    "accumulated": "All previous stages",
    "context_specific": "Generalization limits",
    "interpretation": "Research question framing"
  },
  "impact_on_conclusions": {
    "high_confidence": "Strong claims possible",
    "medium_confidence": "Tentative findings",
    "low_confidence": "Exploratory only"
  },
  "typical_confidence": 0.55
}
```

## Entity Resolution: The Critical Uncertainty Point

### Why Entity Resolution Matters

Entity resolution is often the largest source of uncertainty because:

1. **Ubiquitous Ambiguity**: Pronouns and group references appear constantly
2. **Cascading Effects**: Misidentified entities affect all downstream analysis
3. **Irreducible Uncertainty**: Some ambiguity is intentional or contextual

### Entity Resolution Uncertainty Patterns

```python
# Typical uncertainty levels by reference type
uncertainty_patterns = {
    "explicit_names": {
        "example": "The Democratic Party",
        "confidence": 0.90,
        "frequency": "20%"
    },
    "clear_group_refs": {
        "example": "We Republicans",
        "confidence": 0.85,
        "frequency": "15%"
    },
    "contextual_refs": {
        "example": "Our department",
        "confidence": 0.70,
        "frequency": "25%"
    },
    "ambiguous_pronouns": {
        "example": "They said",
        "confidence": 0.50,
        "frequency": "30%"
    },
    "contested_refs": {
        "example": "The real Americans",
        "confidence": 0.40,
        "frequency": "10%"
    }
}
```

### How Entity Uncertainty Propagates

```mermaid
graph TD
    A[Entity: "they" confidence: 0.5] --> B[Aggregation: Group frequency uncertain]
    B --> C[Graph: Weak edges, fuzzy communities]
    B --> D[Table: Wide confidence intervals]
    B --> E[Vector: Noisy embeddings]
    C --> F[Integration: Conflicting patterns]
    D --> F
    E --> F
    F --> G[Findings: Weak conclusions]
    
    style A fill:#ffcdd2
    style G fill:#ffcdd2
```

## Uncertainty Scenarios and Their Impact

### Scenario 1: Low Entity Uncertainty (0.8-1.0)
```json
{
  "example": "Congressional voting records with clear party labels",
  "characteristics": {
    "explicit_identification": "Senator Smith (R-TX)",
    "minimal_pronouns": "Formal register",
    "stable_entities": "Parties don't change mid-document"
  },
  "pipeline_flow": {
    "stage_2_confidence": 0.85,
    "stage_4_confidence": 0.80,
    "stage_6_confidence": 0.75
  },
  "research_impact": "Strong quantitative conclusions possible"
}
```

### Scenario 2: Moderate Entity Uncertainty (0.5-0.8)
```json
{
  "example": "Corporate meeting transcripts",
  "characteristics": {
    "mixed_references": "Names, titles, and pronouns",
    "hierarchical_ambiguity": "'We' at different org levels",
    "some_context": "Speaker roles provide clues"
  },
  "pipeline_flow": {
    "stage_2_confidence": 0.65,
    "stage_4_confidence": 0.60,
    "stage_6_confidence": 0.55
  },
  "research_impact": "Mixed methods recommended, validate key findings"
}
```

### Scenario 3: High Entity Uncertainty (0.0-0.5)
```json
{
  "example": "Anonymous online forums",
  "characteristics": {
    "no_identification": "Usernames only",
    "shifting_referents": "Groups form and dissolve",
    "strategic_ambiguity": "Intentional vagueness"
  },
  "pipeline_flow": {
    "stage_2_confidence": 0.35,
    "stage_4_confidence": 0.30,
    "stage_6_confidence": 0.25
  },
  "research_impact": "Quantitative analysis not recommended"
}
```

## Uncertainty Reduction Mechanisms

### 1. Multi-Source Validation (Stage 4)
```python
def reduce_uncertainty_stage_4(graph_result, table_result, vector_result):
    """Only uncertainty reduction point in pipeline"""
    
    # Check agreement across modes
    agreement = calculate_agreement(graph_result, table_result, vector_result)
    
    if agreement > 0.8:
        # High agreement reduces uncertainty
        confidence_boost = 0.15
    elif agreement > 0.6:
        # Moderate agreement provides some validation
        confidence_boost = 0.10
    else:
        # Low agreement maintains uncertainty
        confidence_boost = 0.0
    
    return original_confidence + confidence_boost
```

### 2. Context Windows (Stage 2)
```python
def entity_extraction_with_context(text, window_size=5):
    """Limited uncertainty reduction through context"""
    
    # Recent mentions provide disambiguation
    if recent_clear_reference_exists(window_size):
        confidence_boost = 0.10
    else:
        confidence_boost = 0.0
    
    return base_confidence + confidence_boost
```

## Quality Metrics Throughout Pipeline

### Stage-by-Stage Quality Tracking
```json
{
  "quality_metrics": {
    "stage_1": {
      "schema_completeness": 0.85,
      "construct_clarity": 0.80
    },
    "stage_2": {
      "extraction_coverage": 0.75,
      "entity_resolution_rate": 0.65,
      "confidence_distribution": {
        "high": 0.30,
        "medium": 0.45,
        "low": 0.25
      }
    },
    "stage_3": {
      "aggregation_completeness": 0.90,
      "perspective_balance": 0.70
    },
    "stage_4": {
      "modal_agreement": 0.65,
      "retrieval_relevance": 0.75
    },
    "stage_5": {
      "integration_coherence": 0.60,
      "conflict_resolution": 0.55
    },
    "stage_6": {
      "conclusion_confidence": 0.55,
      "generalizability": 0.50
    }
  }
}
```

## Best Practices for Managing Uncertainty

### 1. Set Confidence Thresholds
```python
CONFIDENCE_THRESHOLDS = {
    "include_in_analysis": 0.5,
    "quantitative_analysis": 0.7,
    "strong_claims": 0.8,
    "publication_ready": 0.85
}
```

### 2. Uncertainty-Aware Analysis
```python
def analyze_with_uncertainty(data, confidence_scores):
    """Weight analysis by confidence"""
    
    # Filter by minimum confidence
    filtered_data = data[confidence_scores > CONFIDENCE_THRESHOLDS["include_in_analysis"]]
    
    # Weight by confidence in aggregations
    weighted_mean = np.average(filtered_data, weights=confidence_scores)
    
    # Report confidence intervals
    ci_lower = np.percentile(filtered_data, 2.5)
    ci_upper = np.percentile(filtered_data, 97.5)
    
    return {
        "estimate": weighted_mean,
        "confidence_interval": [ci_lower, ci_upper],
        "average_confidence": np.mean(confidence_scores)
    }
```

### 3. Transparent Reporting
```markdown
## Uncertainty Disclosure

### Entity Resolution Performance
- Clear entities identified: 156 (confidence > 0.8)
- Ambiguous entities: 89 (confidence 0.5-0.8)
- Unresolved references: 45 (confidence < 0.5)
- Overall resolution rate: 71%

### Impact on Analysis
- Network analysis includes only high-confidence entities
- Statistical tests weighted by entity confidence
- 23% of potential relationships excluded due to uncertainty

### Limitations
- Coalition membership remains ambiguous for emerging groups
- Temporal entity evolution could not be tracked reliably
- Cross-document entity linking was not attempted due to uncertainty
```

## Key Insights

1. **Entity Resolution is the Bottleneck**: Most uncertainty enters at Stage 2 through ambiguous entity references

2. **Uncertainty Accumulates**: Each stage adds new uncertainty while carrying forward previous uncertainty

3. **Limited Reduction Opportunities**: Only Stage 4 multi-modal validation significantly reduces uncertainty

4. **Different Research Needs**: Some questions tolerate high uncertainty, others require high confidence

5. **Transparency is Critical**: Honest uncertainty reporting enables appropriate use of findings

## Conclusion

The KGAS pipeline's strength lies not in eliminating uncertainty but in tracking it transparently throughout analysis. By quantifying confidence at each stage and understanding how entity resolution uncertainty propagates, researchers can:

- Choose appropriate analytical methods
- Make claims proportional to confidence
- Identify when supplementary methods are needed
- Advance knowledge even with imperfect data

The system transforms uncertainty from an invisible threat to validity into a measured, managed aspect of computational social science research.