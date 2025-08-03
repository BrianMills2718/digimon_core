# Entity Resolution Uncertainty: Research Impact Scenarios

## Overview

These scenarios demonstrate how entity resolution uncertainty directly impacts research conclusions in real academic contexts, showing:
- How uncertainty affects different types of research questions
- When findings remain valid despite uncertainty
- When uncertainty invalidates conclusions
- How researchers should report uncertainty

## Scenario 1: Political Polarization Study

### Research Question
"How does political polarization manifest in congressional debates over time?"

### Data Sample
```
Congressional Records 2020:
Rep_A: "We Republicans stand for fiscal responsibility."
Dem_A: "We Democrats protect working families."
Rep_B: "They want to destroy the economy."
Dem_B: "They only care about the wealthy."

Congressional Records 2023:
Rep_C: "We need bipartisan solutions."
Dem_C: "We moderates can work together."
Rep_A: "They've abandoned conservative principles."
Dem_A: "Those centrists betray progressive values."
```

### Entity Resolution Results

```json
{
  "2020_entities": {
    "clear_partisan": {
      "Republicans": {"count": 25, "confidence": 0.92},
      "Democrats": {"count": 23, "confidence": 0.91}
    },
    "ambiguous_they": {
      "instances": 47,
      "avg_confidence": 0.65,
      "distribution": {
        "opposite_party": 0.7,
        "unclear": 0.3
      }
    }
  },
  "2023_entities": {
    "clear_partisan": {
      "Republicans": {"count": 18, "confidence": 0.88},
      "Democrats": {"count": 16, "confidence": 0.87}
    },
    "emerging_groups": {
      "Moderates": {"count": 8, "confidence": 0.72},
      "Bipartisan": {"count": 5, "confidence": 0.68}
    },
    "ambiguous_references": {
      "instances": 62,
      "avg_confidence": 0.58,
      "note": "Increased ambiguity with coalition emergence"
    }
  }
}
```

### Research Findings with Uncertainty

```json
{
  "finding_1": {
    "claim": "Clear partisan identification decreased from 2020 to 2023",
    "evidence": {
      "2020_clear": 48,
      "2023_clear": 34
    },
    "confidence": 0.85,
    "uncertainty_impact": "LOW",
    "validity": "ROBUST",
    "explanation": "Clear party mentions are highly confident"
  },
  "finding_2": {
    "claim": "Emergence of moderate coalition discourse in 2023",
    "evidence": {
      "moderate_mentions": 13,
      "confidence_avg": 0.70
    },
    "confidence": 0.70,
    "uncertainty_impact": "MODERATE",
    "validity": "TENTATIVE",
    "explanation": "New entities have moderate confidence"
  },
  "finding_3": {
    "claim": "Increased use of ambiguous 'they' references indicates growing polarization",
    "evidence": {
      "2020_ambiguous": 47,
      "2023_ambiguous": 62
    },
    "confidence": 0.58,
    "uncertainty_impact": "HIGH",
    "validity": "QUESTIONABLE",
    "explanation": "Cannot reliably determine if 'they' indicates polarization or coalition complexity"
  }
}
```

### How to Report This Research

```markdown
## Results

We analyzed congressional debates from 2020 and 2023 to assess changes in political polarization.

### High Confidence Findings (>0.8 confidence)
- Clear partisan self-identification (e.g., "We Republicans") decreased by 29% between 2020 and 2023 (confidence: 0.85)
- Both parties showed reduced explicit party-line rhetoric

### Moderate Confidence Findings (0.6-0.8 confidence)  
- Emergence of "moderate" and "bipartisan" group references in 2023 (n=13, confidence: 0.70)
- Suggests possible coalition formation across party lines

### Low Confidence Observations (<0.6 confidence)
- Ambiguous pronoun usage ("they") increased by 32%
- Due to entity resolution uncertainty (confidence: 0.58), we cannot determine if this indicates:
  - Increased polarization (us vs. them)
  - Complex coalition dynamics
  - Strategic ambiguity

### Limitations
Entity resolution confidence averaged 0.73 across the corpus. Ambiguous references comprising 41% of group mentions limits our ability to make strong claims about polarization trends.
```

## Scenario 2: Organizational Culture Study

### Research Question
"How do hierarchical relationships affect team identity in tech companies?"

### Data Sample
```
All-Hands Meeting Transcript:
CEO: "We at TechCorp are one family."
VP_Eng: "We in engineering need more resources."
Engineer_1: "When they say 'we,' they mean management."
VP_Sales: "Our department exceeded targets."
Engineer_2: "We're not really part of their 'we.'"
Sales_Rep: "We customer-facing folks understand the market."
CEO: "Let's remember we're all on the same team."
```

### Multi-Level Entity Resolution

```json
{
  "entity_scales": {
    "company_level": {
      "TechCorp": {"count": 3, "confidence": 0.85}
    },
    "department_level": {
      "Engineering": {"count": 4, "confidence": 0.78},
      "Sales": {"count": 3, "confidence": 0.82}
    },
    "role_level": {
      "Management": {"count": 2, "confidence": 0.65},
      "Engineers": {"count": 3, "confidence": 0.72},
      "Customer_facing": {"count": 1, "confidence": 0.88}
    }
  },
  "scale_conflicts": {
    "conflicting_we": {
      "instances": 5,
      "explanation": "Same 'we' used at different organizational scales",
      "resolution_confidence": 0.62
    },
    "exclusion_patterns": {
      "they_management": {"count": 2, "confidence": 0.70},
      "their_we": {"count": 1, "confidence": 0.75}
    }
  }
}
```

### Network Analysis with Uncertainty

```json
{
  "graph_metrics": {
    "communities_detected": 4,
    "modularity": 0.38,
    "uncertainty_factors": {
      "edge_confidence_avg": 0.68,
      "node_classification_certainty": 0.71
    }
  },
  "hierarchy_analysis": {
    "vertical_distance": {
      "CEO_to_Engineer": 2.3,
      "confidence": 0.65,
      "uncertainty_impact": "Fuzzy boundaries affect distance calculations"
    },
    "horizontal_clusters": {
      "department_silos": "detected",
      "confidence": 0.72
    }
  }
}
```

### Research Impact Assessment

```json
{
  "hypothesis_1": {
    "statement": "Hierarchical distance correlates with exclusionary language",
    "statistical_result": {
      "correlation": 0.42,
      "p_value": 0.08,
      "confidence_interval": [0.21, 0.63]
    },
    "uncertainty_impact": {
      "effect": "Wide confidence interval due to entity classification uncertainty",
      "validity": "SUGGESTIVE_ONLY",
      "recommendation": "Requires qualitative validation"
    }
  },
  "hypothesis_2": {
    "statement": "Department-level identity stronger than company identity",
    "evidence": {
      "dept_mentions": 7,
      "company_mentions": 3,
      "ratio": 2.33
    },
    "uncertainty_impact": {
      "effect": "Scale ambiguity in 38% of 'we' references",
      "validity": "MODERATE",
      "caveat": "Some 'we' references could be either level"
    }
  }
}
```

## Scenario 3: Social Movement Research

### Research Question
"How do protest movements construct collective identity during mobilization?"

### Data Sample
```
Protest Organizer Meeting:
Organizer_A: "We the people demand justice."
Organizer_B: "We activists must stay united."
Participant_1: "Are we protesters or citizens?"
Organizer_A: "We're both. They try to divide us."
Media: "Who are 'they' you're referring to?"
Organizer_B: "Those who oppose change."
Participant_2: "We're whoever shows up."
```

### Fluid Entity Challenge

```json
{
  "entity_fluidity": {
    "stable_entities": {
      "activists": {"confidence": 0.75, "count": 2},
      "people": {"confidence": 0.70, "count": 1}
    },
    "fluid_entities": {
      "we_whoever_shows": {
        "type": "emergent",
        "confidence": 0.45,
        "explanation": "Membership defined by participation"
      },
      "they_opposers": {
        "type": "oppositional",
        "confidence": 0.55,
        "explanation": "Defined by opposition, not features"
      }
    },
    "identity_claims": {
      "multiple_simultaneous": true,
      "examples": ["protesters AND citizens"],
      "resolution_possible": false,
      "confidence": 0.50
    }
  }
}
```

### Theory Application Challenges

```json
{
  "collective_identity_theory": {
    "constructs": {
      "boundary_creation": {
        "detected": true,
        "confidence": 0.65,
        "challenge": "Boundaries intentionally fluid"
      },
      "shared_identity": {
        "detected": "partial",
        "confidence": 0.55,
        "challenge": "Multiple overlapping identities"
      },
      "oppositional_framing": {
        "detected": true,
        "confidence": 0.60,
        "challenge": "'They' never clearly specified"
      }
    }
  },
  "research_viability": {
    "quantitative_analysis": "LIMITED",
    "explanation": "Fluid boundaries resist quantification",
    "alternative_approach": "Combine with ethnographic methods",
    "confidence_threshold": "Below 0.7 for most entities"
  }
}
```

## Scenario 4: Literary Analysis

### Research Question
"How do postmodern novels deconstruct group identity?"

### Data Sample
```
Novel Excerpt:
"We were the forgotten ones, until we forgot ourselves. They called us remnants, but we were the whole. We spoke in their voices until they spoke in ours. Now we are they and they are we, and the distinction matters only to those who insist on counting."
```

### Framework Breakdown

```json
{
  "extraction_attempts": {
    "attempt_1": {
      "entities_found": 4,
      "confidence": 0.30,
      "failure": "Temporal shifts conflated"
    },
    "attempt_2": {
      "entities_found": 2,
      "confidence": 0.25,
      "failure": "Lost metaphorical meaning"
    },
    "attempt_3": {
      "entities_found": 0,
      "confidence": 0.0,
      "failure": "Recognized futility"
    }
  },
  "system_recommendation": {
    "status": "ABORT_QUANTITATIVE_ANALYSIS",
    "explanation": "Text deliberately deconstructs entity boundaries",
    "confidence": 0.20,
    "alternative": "Literary close reading required"
  }
}
```

## Impact on Different Research Types

### 1. Quantitative Studies

```json
{
  "high_impact_scenarios": {
    "network_analysis": {
      "uncertainty_threshold": 0.3,
      "impact": "False communities, meaningless centrality",
      "mitigation": "Require confidence >0.7 for inclusion"
    },
    "statistical_testing": {
      "uncertainty_threshold": 0.4,
      "impact": "Inflated p-values, wide confidence intervals",
      "mitigation": "Bootstrap with uncertainty weights"
    },
    "predictive_modeling": {
      "uncertainty_threshold": 0.5,
      "impact": "Poor model performance, unreliable predictions",
      "mitigation": "Include uncertainty as feature"
    }
  }
}
```

### 2. Qualitative Studies

```json
{
  "moderate_impact_scenarios": {
    "thematic_analysis": {
      "uncertainty_threshold": 0.5,
      "impact": "Themes identifiable despite ambiguity",
      "enhancement": "Uncertainty reveals strategic ambiguity"
    },
    "discourse_analysis": {
      "uncertainty_threshold": 0.6,
      "impact": "Ambiguity itself becomes finding",
      "enhancement": "Power dynamics in unclear references"
    }
  }
}
```

### 3. Mixed Methods

```json
{
  "adaptive_strategies": {
    "confidence_based_routing": {
      "high_confidence": "Quantitative analysis",
      "medium_confidence": "Mixed methods",
      "low_confidence": "Qualitative only"
    },
    "uncertainty_as_data": {
      "approach": "Analyze patterns in uncertainty itself",
      "example": "Strategic ambiguity in negotiations"
    }
  }
}
```

## Best Practices for Researchers

### 1. Uncertainty Reporting Template

```markdown
## Entity Resolution Quality

- Overall confidence: [X.XX]
- Clear entities: [N] (confidence > 0.8)
- Ambiguous entities: [N] (confidence 0.5-0.8)  
- Unresolved references: [N] (confidence < 0.5)

## Impact on Findings

### High Confidence Claims (entity confidence > 0.8)
- [Finding with specific evidence]

### Moderate Confidence Claims (entity confidence 0.6-0.8)
- [Finding with caveats noted]

### Exploratory Observations (entity confidence < 0.6)
- [Pattern noted but requiring validation]

## Limitations

Entity resolution uncertainty affects approximately [X]% of our analysis. Key limitations include:
- [Specific ambiguities]
- [Their impact on conclusions]
- [Required supplementary methods]
```

### 2. Decision Tree for Research Viability

```
Average Entity Confidence
         |
    < 0.5: Consider abandoning entity-based analysis
         |
  0.5-0.7: Mixed methods required
         |
    > 0.7: Quantitative analysis viable
         |
    > 0.85: High confidence in findings
```

### 3. Uncertainty-Aware Analysis Guidelines

1. **Always report confidence ranges**, not just point estimates
2. **Weight analyses by confidence** when aggregating
3. **Treat uncertainty patterns as potential findings** (strategic ambiguity)
4. **Validate low-confidence findings** with other methods
5. **Set minimum confidence thresholds** before analysis

## Conclusion

Entity resolution uncertainty is not merely a technical challenge but fundamentally shapes what research questions can be answered with automated analysis. The KGAS system's transparent uncertainty tracking enables researchers to:

1. Make informed decisions about analytical approaches
2. Report findings with appropriate caveats
3. Identify when qualitative methods are necessary
4. Treat ambiguity as data rather than just noise

Successful research with KGAS requires embracing uncertainty as an integral part of the analytical process, not an obstacle to be eliminated.