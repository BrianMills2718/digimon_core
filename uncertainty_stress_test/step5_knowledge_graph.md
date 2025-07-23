# Step 5: Final Knowledge Graph Construction

## Knowledge Graph Architecture

```python
# The knowledge graph stores the final, aggregated, theory-integrated claims
knowledge_graph = {
    "nodes": {
        "entities": [
            {
                "id": "person_001",
                "name": "Bob Johnson",
                "type": "Person",
                "attributes": {
                    "field": "computational_linguistics",
                    "active_period": "1990-2010"
                }
            },
            {
                "id": "person_002", 
                "name": "Alice Smith",
                "type": "Person",
                "attributes": {
                    "field": "computational_linguistics",
                    "active_period": "1985-2005"
                }
            }
        ]
    },
    "edges": {
        "relationships": [
            {
                "id": "rel_001",
                "source": "person_001",
                "target": "person_002",
                "type": "influenced_by",
                "properties": {
                    "confidence": 0.695,
                    "confidence_method": "bayesian_aggregation_with_dependencies",
                    "influence_strength": "strong",
                    "temporal_context": {
                        "influence_period": "1990-1999",
                        "evidence_period": "1992-2010"
                    },
                    "theory_context": {
                        "theory": "Academic Influence Network Theory v2.1",
                        "construct": "intellectual_influence",
                        "theory_fit": 0.88
                    }
                }
            }
        ]
    }
}
```

## Uncertainty Visualization Preparation

```python
# Prepare uncertainty data for visualization
uncertainty_visualization_data = {
    "edge_uncertainty": {
        "rel_001": {
            "base_confidence": 0.695,
            "uncertainty_components": {
                "extraction_uncertainty": 0.15,  # Average extraction uncertainty
                "aggregation_uncertainty": 0.08,  # From dependency modeling
                "theory_fit_uncertainty": 0.12,   # Theory alignment uncertainty
                "temporal_uncertainty": 0.05      # 18-year evidence span
            },
            "confidence_range": {
                "lower_bound": 0.55,  # Conservative estimate
                "point_estimate": 0.695,
                "upper_bound": 0.82   # Optimistic estimate
            },
            "visual_encoding": {
                "edge_opacity": 0.695,
                "edge_thickness": 2.78,  # 0.695 * 4 max thickness
                "edge_style": "solid",   # Solid for confidence > 0.6
                "uncertainty_glyph": "medium_confidence_icon"
            }
        }
    }
}
```

## Interactive Exploration Features

```python
# Configuration for interactive exploration interface
interactive_config = {
    "confidence_threshold_slider": {
        "min": 0.0,
        "max": 1.0, 
        "default": 0.5,
        "current": 0.5
    },
    "uncertainty_display_modes": [
        {
            "mode": "point_estimate",
            "description": "Show single confidence value"
        },
        {
            "mode": "confidence_interval",
            "description": "Show range with bounds"
        },
        {
            "mode": "component_breakdown",
            "description": "Show all uncertainty sources"
        }
    ],
    "perturbation_testing": {
        "enabled": True,
        "parameters": [
            {
                "name": "prior_probability",
                "current": 0.15,
                "range": [0.05, 0.30],
                "description": "Base rate of influence"
            },
            {
                "name": "dependency_factor",
                "current": 0.4,
                "range": [0.2, 0.8],
                "description": "Source independence level"
            }
        ]
    }
}
```

## Query Interface Examples

```python
# Example queries against the knowledge graph

# Query 1: High-confidence influences
query1 = KnowledgeGraph.query(
    """
    MATCH (person1)-[r:influenced_by]->(person2)
    WHERE r.confidence > 0.7
    RETURN person1.name, person2.name, r.confidence, r.influence_strength
    """
)
# Results: Would return Johnson->Smith if threshold was 0.69

# Query 2: Theory-specific queries
query2 = KnowledgeGraph.query(
    """
    MATCH (p1)-[r:influenced_by]->(p2)
    WHERE r.theory_context.theory = 'Academic Influence Network Theory v2.1'
    AND r.theory_context.theory_fit > 0.8
    RETURN p1, p2, r
    """
)
# Results: Johnson->Smith (theory_fit: 0.88)

# Query 3: Uncertainty-aware aggregation
query3 = KnowledgeGraph.aggregate_with_uncertainty(
    """
    MATCH (p:Person)-[r:influenced_by]->(influencer:Person)
    WHERE influencer.name = 'Alice Smith'
    RETURN COUNT(p) as influence_count,
           AVG(r.confidence) as avg_confidence,
           COLLECT(r.confidence) as confidence_distribution
    """
)
# Results: {influence_count: 1, avg_confidence: 0.695, distribution: [0.695]}
```

## Robustness Analysis

```python
# Test robustness of the influence claim under perturbations
robustness_test = RobustnessAnalyzer.test_claim(
    claim_id="rel_001",
    perturbations=[
        {"parameter": "prior_probability", "range": [0.05, 0.30]},
        {"parameter": "dependency_factor", "range": [0.2, 0.8]},
        {"parameter": "likelihood_ratios", "variation": 0.2}
    ]
)

# Results:
{
    "claim": "Johnson influenced_by Smith",
    "base_confidence": 0.695,
    "robustness_score": 0.78,
    "sensitivity_analysis": {
        "most_sensitive_to": "dependency_factor",
        "stable_above": 0.60,  # Confidence stays above 0.6 in 78% of perturbations
        "breaks_below": 0.50   # Only drops below 0.5 in extreme scenarios
    },
    "perturbation_results": [
        {"prior": 0.05, "dependency": 0.2, "result": 0.61},
        {"prior": 0.30, "dependency": 0.8, "result": 0.74},
        # ... more combinations
    ]
}
```

## Explanation Generation

```python
# Generate human-readable explanation of the confidence
explanation = ExplanationGenerator.generate(
    claim_id="rel_001",
    detail_level="summary"
)

# Output:
"""
Bob Johnson was influenced by Alice Smith (Confidence: 70%)

This conclusion is based on 5 pieces of evidence spanning 1992-2010:
- Johnson extended Smith's framework in a 1992 grant proposal
- A 1995 conference paper states Johnson's work "builds directly on" Smith's
- Johnson cited Smith 47 times (23% of his citations) from 1991-1999
- In a 1998 interview, Johnson acknowledged Smith's influence
- A 2005 biography credits Smith as a "major influence" on Johnson

The confidence accounts for:
- Dependencies between sources (biography cites earlier paper)
- Domain context (1990s computational linguistics was a small field)
- Mixed signals (Johnson acknowledged influence but noted disagreements)

This represents a "strong" influence according to Academic Influence Network Theory,
as evidenced by framework extension, sustained citations, and career trajectory change.
"""
```

## Final System State

```python
system_state = {
    "claims_processed": 1,
    "total_evidence_sources": 5,
    "aggregation_method": "bayesian_with_dependencies",
    "final_confidence": 0.695,
    "uncertainty_breakdown": {
        "extraction": 0.15,
        "aggregation": 0.08,
        "theory_fit": 0.12,
        "temporal": 0.05
    },
    "robustness": {
        "score": 0.78,
        "stable_above": 0.60
    },
    "theory_integration": {
        "theory_applied": "Academic Influence Network Theory v2.1",
        "influence_strength": "strong",
        "hypotheses_supported": 3
    },
    "audit_complete": True,
    "explanation_available": True
}
```

## Key Insights from Complete Pipeline

1. **Successful Aggregation**: Multiple weak-to-moderate signals → strong conclusion
2. **Dependency Handling**: Proper Bayesian approach prevented overconfidence
3. **Theory Integration**: Evidence mapped well to theoretical constructs
4. **Robustness**: Claim stable under reasonable perturbations
5. **Transparency**: Full audit trail from raw documents to final graph
6. **Uncertainty Preservation**: Multi-faceted uncertainty tracked throughout

## Visualization Output

The final knowledge graph visualization would show:
- **Node**: Bob Johnson (full opacity)
- **Node**: Alice Smith (full opacity)
- **Edge**: Influenced_by (70% opacity, thick solid line)
- **Uncertainty glyph**: Medium-high confidence indicator
- **Interactive features**: Hover for details, click for evidence breakdown