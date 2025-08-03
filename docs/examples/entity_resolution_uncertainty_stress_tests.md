# Entity Resolution Uncertainty Stress Tests for KGAS

## Overview

These stress tests demonstrate how the KGAS system tracks and propagates uncertainty through entity resolution, focusing on:
1. How LLMs handle ambiguous entity references
2. How uncertainty is quantified and tracked
3. How uncertainty propagates through the analysis pipeline
4. How uncertainty affects research conclusions

## Stress Test 1: Political Coalition Formation

### Input Text
```
Congressional Hearing Transcript - Day 1:
Sen_A (R): "We Republicans demand fiscal responsibility."
Sen_B (D): "We Democrats will protect social programs."
Sen_C (R): "Some of us are willing to negotiate."
Sen_D (D): "We moderates from both parties should find common ground."
Sen_E (R): "They don't speak for all of us."
Sen_F (D): "When they say 'moderates,' who exactly do they mean?"

Day 3:
Sen_C (R): "We've formed a bipartisan working group."
Sen_D (D): "Our coalition includes members from both parties."
Sen_A (R): "They've betrayed conservative principles."
Sen_B (D): "Those turncoats have abandoned progressive values."
```

### Stage 1: Theory Schema Extraction

```json
{
  "theory": "Social Movement Coalition Theory",
  "schema": {
    "entities": ["Political_Actor", "Coalition", "Party"],
    "relations": ["belongs_to", "opposes", "forms_coalition"],
    "properties": ["ideology", "negotiation_stance", "coalition_membership"]
  },
  "extraction_uncertainty": {
    "confidence": 0.85,
    "factors": {
      "schema_completeness": 0.9,
      "construct_clarity": 0.8
    },
    "uncertainty_type": "epistemic",
    "explanation": "Theory provides clear coalition concepts but may miss emergent dynamics"
  }
}
```

### Stage 2: Entity Extraction with Uncertainty

```json
{
  "extractions": [
    {
      "text": "We Republicans",
      "speaker": "Sen_A",
      "entity": {
        "type": "Political_Actor",
        "value": "Republicans",
        "confidence": 0.95
      },
      "uncertainty": {
        "factors": ["clear_party_identification"],
        "confidence": 0.95,
        "distribution": {"Republicans": 0.95, "other": 0.05}
      }
    },
    {
      "text": "Some of us",
      "speaker": "Sen_C",
      "entity": {
        "type": "Political_Actor",
        "value_distribution": {
          "Republicans": 0.6,
          "Moderate_Republicans": 0.35,
          "UNKNOWN": 0.05
        }
      },
      "uncertainty": {
        "factors": ["ambiguous_subset", "speaker_context"],
        "confidence": 0.6,
        "explanation": "Unclear if referring to all Republicans or a subset"
      }
    },
    {
      "text": "We moderates from both parties",
      "speaker": "Sen_D",
      "entity": {
        "type": "Coalition",
        "value": "Bipartisan_Moderates",
        "confidence": 0.8
      },
      "uncertainty": {
        "factors": ["emerging_group", "undefined_membership"],
        "confidence": 0.8,
        "explanation": "New coalition being formed, membership not fully defined"
      }
    },
    {
      "text": "They don't speak for all of us",
      "speaker": "Sen_E",
      "entity": {
        "type": "Political_Actor",
        "value_distribution": {
          "Moderate_Republicans": 0.7,
          "Sen_C": 0.2,
          "UNKNOWN": 0.1
        }
      },
      "uncertainty": {
        "factors": ["pronoun_ambiguity", "contextual_inference"],
        "confidence": 0.7,
        "explanation": "Likely refers to moderates based on context"
      }
    }
  ]
}
```

### Stage 3: Aggregation with Uncertainty Tracking

```json
{
  "aggregated_entities": {
    "by_speaker": {
      "Sen_A": {
        "primary_identity": "Republicans",
        "confidence": 0.95,
        "stance": "hardline"
      },
      "Sen_C": {
        "primary_identity": "Republicans",
        "secondary_identity": {
          "value": "Moderate_Republicans",
          "confidence": 0.7
        },
        "stance_evolution": "shifting"
      }
    },
    "entity_frequencies": {
      "Republicans": {
        "count": 5,
        "avg_confidence": 0.82,
        "confidence_range": [0.6, 0.95]
      },
      "Democrats": {
        "count": 4,
        "avg_confidence": 0.91,
        "confidence_range": [0.85, 0.95]
      },
      "Bipartisan_Moderates": {
        "count": 3,
        "avg_confidence": 0.75,
        "confidence_range": [0.7, 0.8],
        "note": "Emerging entity"
      }
    }
  },
  "aggregation_uncertainty": {
    "overall_confidence": 0.73,
    "factors": {
      "entity_resolution_clarity": 0.8,
      "temporal_consistency": 0.65,
      "speaker_consistency": 0.75
    },
    "challenges": [
      "Coalition membership evolves between Day 1 and Day 3",
      "Same speakers refer to different group configurations",
      "Emergent groups lack clear boundaries"
    ]
  }
}
```

### Stage 4: Cross-Modal Analysis with Uncertainty

```json
{
  "graph_analysis": {
    "communities_detected": 3,
    "modularity": 0.42,
    "uncertainty": {
      "confidence": 0.7,
      "factors": ["ambiguous_edges", "evolving_structure"],
      "explanation": "Coalition edges have varying strengths due to uncertain membership"
    }
  },
  "table_analysis": {
    "party_alignment_correlation": 0.35,
    "p_value": 0.08,
    "uncertainty": {
      "confidence": 0.6,
      "factors": ["small_sample", "classification_uncertainty"],
      "explanation": "Statistical significance marginal due to entity classification uncertainty"
    }
  },
  "vector_analysis": {
    "semantic_clusters": 4,
    "cluster_stability": 0.68,
    "uncertainty": {
      "confidence": 0.65,
      "factors": ["embedding_variance", "context_dependency"],
      "explanation": "Political language shifts meaning based on speaker context"
    }
  },
  "cross_modal_convergence": {
    "agreement_score": 0.72,
    "uncertainty_reduction": 0.15,
    "explanation": "Moderate agreement across modes slightly reduces uncertainty"
  }
}
```

### Stage 5: Research Conclusions with Uncertainty

```json
{
  "findings": {
    "primary": "Coalition formation occurs through ideological alignment crossing party lines",
    "confidence": 0.68,
    "supporting_evidence": {
      "graph": "Bipartisan cluster detected",
      "table": "Weak party correlation",
      "vector": "Semantic similarity across parties"
    }
  },
  "uncertainty_impact": {
    "entity_resolution_effect": "Ambiguous group references reduce coalition identification confidence by ~20%",
    "temporal_effect": "Evolution between days adds ~15% uncertainty",
    "overall_confidence": 0.68,
    "research_implications": "Findings suggest coalition formation but require additional data for strong claims"
  },
  "quality_assessment": {
    "strengths": ["Multiple convergent indicators", "Clear party identifications"],
    "limitations": ["Ambiguous moderate definitions", "Small sample size", "Temporal gaps"],
    "recommended_actions": ["Collect more temporal data", "Clarify coalition membership", "Interview participants"]
  }
}
```

## Stress Test 2: Organizational Identity Boundaries

### Input Text
```
Corporate Meeting Transcript:
CEO: "We at TechCorp believe in innovation."
VP_Engineering: "We in engineering have concerns about the timeline."
VP_Sales: "Our team thinks we can meet the targets."
Engineer_1: "When they say 'we can meet targets,' they don't include us."
Sales_Rep_1: "We on the ground know what customers want."
CEO: "We need unity. We're all TechCorp."
Engineer_2: "Easy for them to say from the C-suite."
VP_Engineering: "My team and I represent the technical perspective."
```

### Entity Resolution Challenges

```json
{
  "scale_hopping": {
    "example": "CEO uses 'we' for company, VP uses 'we' for department",
    "uncertainty": {
      "confidence": 0.6,
      "explanation": "Same pronoun at different organizational scales"
    }
  },
  "contested_membership": {
    "example": "Engineer disputes Sales' inclusive 'we'",
    "uncertainty": {
      "confidence": 0.5,
      "explanation": "Disagreement about group boundaries"
    }
  },
  "power_dynamics": {
    "example": "'Them' (C-suite) vs 'us' (workers)",
    "uncertainty": {
      "confidence": 0.7,
      "explanation": "Hierarchical division affects entity interpretation"
    }
  }
}
```

## Stress Test 3: Academic Discourse Meta-References

### Input Text
```
Panel Discussion on Methodology:
Researcher_A: "We quantitative researchers value objectivity."
Researcher_B: "But we must ask - who is this 'we' you speak of?"
Researcher_C: "When they say 'objectivity,' they mean their narrow definition."
Researcher_A: "You qualitative folks always question our methods."
Researcher_B: "Notice how 'our' excludes us from the scientific community."
Researcher_D: "We're all scholars here, regardless of methodology."
```

### Meta-Discourse Uncertainty

```json
{
  "meta_references": {
    "questioning_reference": {
      "text": "who is this 'we' you speak of?",
      "uncertainty": {
        "confidence": 0.3,
        "explanation": "Meta-commentary about entity boundaries themselves"
      }
    },
    "contested_definitions": {
      "text": "their narrow definition",
      "uncertainty": {
        "confidence": 0.4,
        "explanation": "Dispute about what constitutes group membership"
      }
    }
  },
  "boundary_work": {
    "inclusion_claims": ["We're all scholars"],
    "exclusion_claims": ["You qualitative folks"],
    "uncertainty": {
      "overall_confidence": 0.5,
      "explanation": "Active negotiation of group boundaries during discourse"
    }
  }
}
```

## Stress Test 4: Strategic Ambiguity in Negotiations

### Input Text
```
Merger Negotiation:
Company_A_CEO: "We're interested in collaboration."
Company_B_CEO: "We need to maintain our independence."
Company_A_CEO: "When we join forces, we'll dominate the market."
Company_B_CEO: "But who is 'we' after a merger?"
Analyst: "They're both using 'we' strategically to avoid commitment."
Company_A_CEO: "Our combined entity would benefit everyone."
Company_B_CEO: "Your 'our' assumes an acquisition, not a merger."
```

### Strategic Ambiguity Analysis

```json
{
  "intentional_ambiguity": {
    "examples": [
      {
        "text": "We're interested in collaboration",
        "interpretations": {
          "Company_A_alone": 0.3,
          "Future_merged_entity": 0.4,
          "Strategic_ambiguity": 0.3
        },
        "uncertainty": {
          "confidence": 0.4,
          "explanation": "Deliberately vague to keep options open"
        }
      }
    ]
  },
  "conflicting_visions": {
    "Company_A_vision": "Single merged entity",
    "Company_B_vision": "Independent collaboration",
    "uncertainty": {
      "confidence": 0.3,
      "explanation": "Same words, fundamentally different entity concepts"
    }
  }
}
```

## Stress Test 5: Cultural and Linguistic Variations

### Input Text
```
International Team Meeting:
Japanese_Manager: "Watashitachi (我々) must work harmoniously."
American_Manager: "We need individual accountability."
German_Manager: "Wir should follow the established process."
Indian_Manager: "Our team values both collective and individual contributions."
Japanese_Manager: "When you say 'we,' it's different from our 'watashitachi.'"
Facilitator: "Let's clarify what each of us means by team identity."
```

### Cross-Cultural Entity Resolution

```json
{
  "cultural_variations": {
    "watashitachi": {
      "literal": "we",
      "cultural_meaning": "harmonious collective including speaker",
      "uncertainty": {
        "confidence": 0.5,
        "explanation": "Japanese collective concepts don't map directly to English"
      }
    },
    "we_american": {
      "meaning": "collection of individuals",
      "uncertainty": {
        "confidence": 0.7,
        "explanation": "Individualistic interpretation of collective"
      }
    }
  },
  "translation_uncertainty": {
    "overall_confidence": 0.6,
    "factors": ["cultural_concepts", "linguistic_structures", "pragmatic_differences"],
    "impact": "Entity boundaries vary by cultural framework"
  }
}
```

## Uncertainty Propagation Summary

### How Uncertainty Compounds

1. **Entity Extraction** (Stage 2)
   - Base uncertainty from ambiguous references: 0.3-0.5
   - LLM interpretation variance: +0.1-0.2
   - Context availability: +/- 0.1

2. **Aggregation** (Stage 3)
   - Speaker inconsistency: +0.1-0.2
   - Temporal evolution: +0.1-0.3
   - Conflicting perspectives: +0.2-0.3

3. **Cross-Modal Analysis** (Stage 4)
   - Modal disagreement: +0.1-0.2
   - Partial convergence: -0.1-0.2 (reduction)
   - Integration complexity: +0.1

4. **Research Conclusions** (Stage 5-6)
   - Accumulated uncertainty: 0.5-0.8 typical
   - Context specificity: +0.1-0.2
   - Generalization limits: +0.1-0.2

### Key Insights

1. **Uncertainty Sources**
   - Linguistic ambiguity (pronouns, context-dependent meaning)
   - Social ambiguity (contested boundaries, power dynamics)
   - Temporal ambiguity (evolving entities, unstable membership)
   - Cultural ambiguity (different conceptual frameworks)

2. **LLM Handling**
   - LLMs can identify and quantify these uncertainties
   - Probability distributions capture ambiguity without forcing resolution
   - Context windows help but don't eliminate uncertainty

3. **Research Impact**
   - High entity uncertainty (>0.7) significantly weakens conclusions
   - Multiple convergent sources can reduce but not eliminate uncertainty
   - Some research questions require accepting irreducible uncertainty

4. **System Strengths**
   - Transparent uncertainty tracking throughout pipeline
   - No forced resolution of genuinely ambiguous references
   - Enables researchers to make informed decisions about findings

5. **System Limitations**
   - Cannot resolve strategic ambiguity (intentionally vague)
   - Cultural concepts may not translate
   - Meta-discourse about entities challenges the framework
   - Some uncertainty is irreducible and must be accepted