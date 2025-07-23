# Step 4: Theory Context Integration

## Theory Schema Definition

```python
# The researcher has specified a theory about Academic Influence Networks
theory_schema = {
    "name": "Academic Influence Network Theory",
    "version": "2.1",
    "core_constructs": {
        "intellectual_influence": {
            "definition": "Substantive impact on another researcher's thinking, methods, or research direction",
            "operationalization": [
                "Citation patterns",
                "Conceptual building/extension",
                "Methodological adoption",
                "Research trajectory changes"
            ],
            "requirements": {
                "type": "actual_influence",
                "not": "mere_citation_or_acknowledgment"
            }
        },
        "influence_strength": {
            "levels": ["weak", "moderate", "strong", "foundational"],
            "indicators": {
                "weak": "Single concept borrowed",
                "moderate": "Multiple concepts or methods adopted",
                "strong": "Research direction significantly shaped",
                "foundational": "Core framework adopted and extended"
            }
        }
    },
    "hypotheses": [
        "Strong influences persist across career stages",
        "Foundational influences generate citation clusters",
        "Disagreement can indicate deep engagement"
    ]
}
```

## Theory-Aware Analysis

```python
# LLM analyzes our Bayesian result in context of the theory
theory_integration = llm.integrate_with_theory(
    prompt="""Given this theory about Academic Influence Networks and our Bayesian 
    analysis result (posterior: 0.927, adjusted: 0.695), assess:
    
    1. Does the evidence support "actual influence" as required by the theory?
    2. What strength level of influence is indicated?
    3. How well does this case fit the theory's hypotheses?
    
    Theory requirements: Actual intellectual influence, not mere citation
    
    Evidence summary:
    - Extended Smith's framework in grant (1992)
    - Built directly on work (1995)
    - 47 citations over 8 years (23% of total)
    - Acknowledged influence despite later disagreement (1998)
    - Retrospective credit as "major influence" (2005)
    
    Bayesian posterior: 0.927 (high confidence in influence)""",
    
    theory_schema=theory_schema,
    response_format=TheoryIntegrationOutput
)

# LLM Response:
{
    "theory_fit_assessment": {
        "actual_influence_supported": True,
        "confidence": 0.88,
        "evidence_mapping": {
            "conceptual_building": ["extends framework", "builds directly on"],
            "methodological_adoption": ["grammar formalism adopted"],
            "research_trajectory": ["changed research direction per biography"],
            "sustained_engagement": ["47 citations over 8 years"]
        }
    },
    "influence_strength_classification": {
        "level": "strong",
        "confidence": 0.82,
        "reasoning": "Multiple indicators: framework extension, sustained citations (23%), explicit acknowledgment, career trajectory change. Not quite 'foundational' as Johnson later disagreed on implementations."
    },
    "hypothesis_evaluation": [
        {
            "hypothesis": "Strong influences persist across career stages",
            "supported": True,
            "evidence": "1992-2010 evidence shows 18+ year persistence"
        },
        {
            "hypothesis": "Foundational influences generate citation clusters",
            "supported": True,
            "evidence": "47 citations, 23% of total indicates clustering"
        },
        {
            "hypothesis": "Disagreement can indicate deep engagement",
            "supported": True,
            "evidence": "1998 interview shows influence despite disagreement"
        }
    ],
    "theory_contribution": "This case strengthens the theory by demonstrating how intellectual influence can persist despite later disagreements, supporting the 'deep engagement' hypothesis."
}
```

## Uncertainty Propagation to Theory Level

```python
# How does claim uncertainty affect theory-level conclusions?
theory_uncertainty_propagation = UncertaintyPropagator.propagate_to_theory(
    claim_confidence=0.695,
    theory_fit_confidence=0.88,
    influence_strength_confidence=0.82
)

# Result:
{
    "theory_instance_confidence": 0.61,  # 0.695 * 0.88
    "influence_classification_confidence": 0.57,  # 0.695 * 0.82
    "hypothesis_support_strength": {
        "persistence_hypothesis": 0.61,
        "citation_cluster_hypothesis": 0.61,
        "disagreement_engagement_hypothesis": 0.61
    },
    "aggregate_theory_update": {
        "direction": "strengthen",
        "magnitude": 0.045,  # Small positive update to theory confidence
        "reasoning": "Single case provides modest support for all three hypotheses"
    }
}
```

## Theory-Driven Confidence Adjustment

```python
# Does theory context suggest adjusting our confidence?
theory_adjustment = llm.assess_theory_driven_adjustment(
    prompt="""Given that our theory specifically requires 'actual influence' not just citation,
    and our evidence shows:
    - Framework extension (strong indicator)
    - Sustained engagement over 18 years
    - Career direction change
    - 23% citation concentration
    
    Should we adjust our Bayesian posterior (0.695) based on theory fit?""",
    
    response_format=TheoryAdjustmentOutput
)

# LLM Response:
{
    "adjustment_recommendation": "maintain",
    "reasoning": "The Bayesian analysis already incorporated the distinction between citation and influence. The evidence strongly supports 'actual influence' as defined by the theory. No additional adjustment needed.",
    "alternative_consideration": "If theory required 'exclusive influence' (Smith as PRIMARY influence), we would need to lower confidence as we lack counterfactual evidence about other influences."
}
```

## Knowledge Graph Entry with Theory Context

```python
knowledge_graph_entry = {
    "claim_id": "johnson_influenced_by_smith_001",
    "subject": "Bob Johnson",
    "predicate": "influenced_by",
    "object": "Alice Smith",
    "confidence": 0.695,
    "confidence_type": "bayesian_posterior_adjusted",
    "theory_context": {
        "theory": "Academic Influence Network Theory v2.1",
        "construct": "intellectual_influence",
        "strength_level": "strong",
        "theory_fit_confidence": 0.88
    },
    "evidence_summary": {
        "source_count": 5,
        "temporal_span": "1992-2010",
        "evidence_types": ["extension", "citation", "acknowledgment", "trajectory_change"],
        "dependency_adjusted": True
    },
    "hypotheses_supported": [
        "influence_persistence",
        "citation_clustering", 
        "disagreement_as_engagement"
    ],
    "audit_trail_ref": "bayesian_aggregation_001"
}
```

## Theory Feedback Loop

```python
# System tracks how well theory predictions match observations
theory_performance_tracker.record(
    theory="Academic Influence Network Theory",
    prediction="Strong influences show citation clustering",
    observation={
        "citation_percentage": 0.23,
        "citation_count": 47,
        "confirmed": True
    },
    case_confidence=0.695
)

# After many cases, system can:
# 1. Refine theory parameters
# 2. Adjust priors for similar cases
# 3. Identify theory limitations
```

## Key Insights from Theory Integration

1. **Theory Validation**: Evidence supports "actual influence" not just citation
2. **Strength Classification**: "Strong" influence with 0.82 confidence
3. **Hypothesis Support**: All three theory hypotheses supported by this case
4. **No Adjustment Needed**: Bayesian analysis already theory-aware
5. **Theory Contribution**: Case strengthens "disagreement as engagement" hypothesis

## Next Step
The claim with its theory context now enters the final knowledge graph...