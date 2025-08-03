# Social Identity Theory Analysis: Complete Example with Entity Resolution

## Overview

This document demonstrates how the KGAS uncertainty framework and entity resolution system work together through a complete Social Identity Theory analysis of congressional hearing transcripts.

## Research Context

**Theory**: Social Identity Theory (Tajfel & Turner, 1979)  
**Research Question**: "How do political group identities influence discourse during congressional hearings?"  
**Data**: Transcript from House Committee hearing on election security (fictional but realistic)

## Stage 1: Theory Description → Theory Schema Translation

### Input: Academic Theory Description
```
Social Identity Theory posits that individuals derive part of their self-concept from 
their membership in social groups. This leads to in-group favoritism (positive bias 
toward one's own group) and out-group derogation (negative bias toward other groups), 
particularly under conditions of intergroup competition or threat.
```

### Output: Structured Theory Schema
```json
{
  "theory_id": "social_identity_theory_v1",
  "theory_name": "Social Identity Theory",
  
  "constructs": [
    {
      "name": "group_identity",
      "definition": "self-concept derived from perceived group membership",
      "boundary_specification": "includes explicit and implicit group identification, excludes individual traits",
      "observable_indicators": [
        "first-person plural pronouns with group reference",
        "explicit membership statements",
        "group-based self-categorization"
      ]
    },
    {
      "name": "in_group_favoritism",
      "definition": "positive bias toward members of one's own group",
      "boundary_specification": "includes differential positive treatment, excludes objective merit-based preferences",
      "observable_indicators": [
        "positive language about in-group",
        "credibility attribution to in-group",
        "support for in-group positions"
      ]
    },
    {
      "name": "out_group_derogation",
      "definition": "negative bias toward members of other groups",
      "boundary_specification": "includes differential negative treatment, excludes legitimate criticism",
      "observable_indicators": [
        "negative language about out-group",
        "skepticism of out-group claims",
        "opposition to out-group positions"
      ]
    }
  ],
  
  "relationships": [
    {
      "from": "group_identity",
      "to": "in_group_favoritism",
      "type": "leads_to",
      "conditions": ["group_salience", "intergroup_competition"]
    },
    {
      "from": "group_identity",
      "to": "out_group_derogation",
      "type": "leads_to",
      "conditions": ["group_threat", "zero_sum_perception"]
    }
  ],
  
  "confidence": 0.85,
  "reasoning": "Theory well-defined in source with clear constructs, though boundary between bias and legitimate criticism remains challenging"
}
```

**Stage 1 Uncertainty Properties**:
- `theory_translation_confidence`: 0.85
- `construct_definition_confidence`: {"group_identity": 0.9, "in_group_favoritism": 0.8, "out_group_derogation": 0.75}
- `boundary_specification_confidence`: 0.7 (bias vs legitimate criticism is subjective)
- `observable_indicators_confidence`: 0.8

## Stage 2: Data → Theoretical Construct Mapping

### Mapping Observable Discourse to Constructs

```json
{
  "mapping_id": "sit_congressional_discourse_map_v1",
  "theory_id": "social_identity_theory_v1",
  "discourse_type": "congressional_hearing_transcript",
  
  "construct_mappings": [
    {
      "construct": "group_identity",
      "discourse_indicators": [
        {
          "pattern": "we/us/our + [party name]",
          "example": "We Democrats", "Our Republican colleagues",
          "mapping_confidence": 0.9,
          "ambiguity_notes": "Clear when party explicitly named"
        },
        {
          "pattern": "we/us/our + [implicit reference]",
          "example": "We must protect our values",
          "mapping_confidence": 0.6,
          "ambiguity_notes": "Requires context to resolve group identity"
        },
        {
          "pattern": "as a [party] [role]",
          "example": "As a Republican senator",
          "mapping_confidence": 0.95,
          "ambiguity_notes": "Explicit self-identification"
        }
      ]
    },
    {
      "construct": "in_group_favoritism",
      "discourse_indicators": [
        {
          "pattern": "positive attribution + same party",
          "example": "My distinguished colleague from Texas [same party]",
          "mapping_confidence": 0.7,
          "ambiguity_notes": "Could be genuine respect or bias"
        },
        {
          "pattern": "credibility boosting + same party",
          "example": "reliable testimony from [same party witness]",
          "mapping_confidence": 0.75
        }
      ]
    },
    {
      "construct": "out_group_derogation",
      "discourse_indicators": [
        {
          "pattern": "skepticism markers + opposite party",
          "example": "Their so-called evidence",
          "mapping_confidence": 0.8,
          "ambiguity_notes": "Skepticism could be warranted"
        },
        {
          "pattern": "negative attribution + opposite party",
          "example": "partisan games by the other side",
          "mapping_confidence": 0.85
        }
      ]
    }
  ],
  
  "overall_mapping_confidence": 0.75,
  "reasoning": "Political discourse shows clear group dynamics, but distinguishing bias from legitimate policy disagreement remains challenging",
  "theory_data_fit_confidence": 0.8
}
```

## Stage 3: Instance Extraction with Entity Resolution

### Input: Congressional Hearing Transcript Excerpt

```
SPEAKER_012 (Rep. Johnson): Thank you, Mr. Chairman. We need to address the 
serious threats to our election systems. They have repeatedly blocked our 
efforts to secure our democracy. As Democrats, we have proposed multiple 
bills to protect voting rights, but they claim these are partisan power grabs.

SPEAKER_015 (Rep. Smith): Will the gentleman yield? Your party's proposals 
would federalize our elections. We believe in state sovereignty. Our 
constituents don't trust Washington bureaucrats with their ballots.

SPEAKER_012: I reclaim my time. We're not trying to federalize anything. 
We simply want to ensure every American can vote. Their rhetoric about 
states' rights is a smokescreen for voter suppression.
```

### Extracted Instances with Entity Resolution

```json
{
  "extraction_session": "hearing_2024_01_15_election_security",
  "speakers": {
    "speaker_012": {"name": "Rep. Johnson", "party": "UNRESOLVED"},
    "speaker_015": {"name": "Rep. Smith", "party": "UNRESOLVED"}
  },
  
  "instances": [
    {
      "instance_id": "inst_001",
      "speaker": "speaker_012",
      "text": "We need to address the serious threats",
      "construct": "group_identity",
      "value": "UNKNOWN_GROUP_A",
      "confidence": 0.7,
      "evidence": {
        "quote": "We need to address the serious threats",
        "reasoning": "First-person plural indicates group membership, specific group unknown"
      },
      "entity_reference": {
        "ref_id": "hearing_2024:speaker_012:ingroup:ref_001",
        "status": "unresolved",
        "candidates": [
          {"entity": "Democrat", "probability": 0.4},
          {"entity": "Committee_Members", "probability": 0.3},
          {"entity": "Congress", "probability": 0.2},
          {"entity": "Unknown", "probability": 0.1}
        ]
      }
    },
    {
      "instance_id": "inst_002",
      "speaker": "speaker_012",
      "text": "They have repeatedly blocked our efforts",
      "construct": "out_group_derogation",
      "value": "negative_attribution",
      "confidence": 0.8,
      "evidence": {
        "quote": "They have repeatedly blocked our efforts",
        "reasoning": "Negative attribution to out-group with blame assignment"
      },
      "entity_references": [
        {
          "ref_id": "hearing_2024:speaker_012:outgroup:ref_002",
          "text": "They",
          "status": "unresolved",
          "candidates": [
            {"entity": "Republican", "probability": 0.6},
            {"entity": "Unknown_Opposition", "probability": 0.4}
          ],
          "constraints": ["different_from:ref_001"]
        },
        {
          "ref_id": "hearing_2024:speaker_012:ingroup:ref_003",
          "text": "our",
          "status": "unresolved",
          "candidates": [
            {"entity": "Democrat", "probability": 0.5},
            {"entity": "Committee_Members", "probability": 0.3},
            {"entity": "Unknown", "probability": 0.2}
          ],
          "constraints": ["same_as:ref_001"]
        }
      ]
    },
    {
      "instance_id": "inst_003",
      "speaker": "speaker_012",
      "text": "As Democrats, we have proposed multiple bills",
      "construct": "group_identity",
      "value": "Democrat",
      "confidence": 0.95,
      "evidence": {
        "quote": "As Democrats, we have proposed multiple bills",
        "reasoning": "Explicit party identification with first-person plural"
      },
      "entity_reference": {
        "ref_id": "hearing_2024:speaker_012:ingroup:ref_004",
        "status": "resolved",
        "value": "Democrat",
        "resolution_evidence": "Explicit identification: 'As Democrats'"
      }
    }
  ],
  
  "entity_resolution_updates": [
    {
      "update_trigger": "inst_003",
      "resolved_entities": [
        {
          "ref_id": "hearing_2024:speaker_012:ingroup:ref_001",
          "resolved_to": "Democrat",
          "confidence": 0.9,
          "reasoning": "Retroactive resolution based on explicit identification in ref_004"
        },
        {
          "ref_id": "hearing_2024:speaker_012:ingroup:ref_003",
          "resolved_to": "Democrat",
          "confidence": 0.9,
          "reasoning": "Coreference chain with ref_001"
        },
        {
          "ref_id": "hearing_2024:speaker_012:outgroup:ref_002",
          "updated_candidates": [
            {"entity": "Republican", "probability": 0.85},
            {"entity": "Unknown_Opposition", "probability": 0.15}
          ],
          "reasoning": "Constraint propagation: if speaker is Democrat, 'they' likely Republicans"
        }
      ]
    }
  ],
  
  "speaker_015_instances": [
    {
      "instance_id": "inst_010",
      "speaker": "speaker_015",
      "text": "Your party's proposals would federalize our elections",
      "constructs": ["out_group_derogation", "group_identity"],
      "evidence": {
        "quote": "Your party's proposals would federalize our elections",
        "reasoning": "Negative characterization of out-group policy; 'our' indicates in-group"
      },
      "entity_references": [
        {
          "ref_id": "hearing_2024:speaker_015:outgroup:ref_010",
          "text": "Your party",
          "status": "resolved",
          "value": "Democrat",
          "reasoning": "Addressing speaker_012 who identified as Democrat"
        },
        {
          "ref_id": "hearing_2024:speaker_015:ingroup:ref_011",
          "text": "our elections",
          "status": "partially_resolved",
          "candidates": [
            {"entity": "Republican", "probability": 0.8},
            {"entity": "States_Rights_Advocates", "probability": 0.2}
          ],
          "reasoning": "Opposition to Democrat speaker suggests Republican, confirmed by states' rights rhetoric"
        }
      ]
    }
  ],
  
  "coreference_chains": [
    {
      "chain_id": "chain_001",
      "speaker": "speaker_012",
      "likely_same_entity": ["ref_001", "ref_003", "ref_004"],
      "resolved_value": "Democrat",
      "confidence": 0.9
    },
    {
      "chain_id": "chain_002",
      "speaker": "speaker_012",
      "likely_same_entity": ["ref_002", "they in inst_004"],
      "resolved_value": "Republican",
      "confidence": 0.85
    }
  ]
}
```

### Entity Resolution Through Context Accumulation

```json
{
  "bayesian_update_sequence": [
    {
      "step": 1,
      "evidence": "We need to address",
      "prior": {"Democrat": 0.4, "Republican": 0.4, "Other": 0.2},
      "posterior": {"Democrat": 0.4, "Republican": 0.4, "Other": 0.2},
      "reasoning": "No distinguishing information yet"
    },
    {
      "step": 2,
      "evidence": "They have blocked our efforts",
      "prior": {"Democrat": 0.4, "Republican": 0.4, "Other": 0.2},
      "posterior": {"Democrat": 0.5, "Republican": 0.3, "Other": 0.2},
      "reasoning": "Oppositional framing slightly favors Democrat speaking about Republicans"
    },
    {
      "step": 3,
      "evidence": "As Democrats, we have proposed",
      "prior": {"Democrat": 0.5, "Republican": 0.3, "Other": 0.2},
      "posterior": {"Democrat": 1.0, "Republican": 0.0, "Other": 0.0},
      "reasoning": "Explicit identification resolves all uncertainty"
    },
    {
      "step": 4,
      "retroactive_update": "Apply resolution to previous references",
      "updated_refs": {
        "ref_001": {"value": "Democrat", "confidence": 0.9},
        "ref_002": {"value": "Republican", "confidence": 0.85},
        "ref_003": {"value": "Democrat", "confidence": 0.9}
      }
    }
  ]
}
```

## Stage 4: Theory-Required Analysis Execution

### Theory Requirements and Available Analyses

```json
{
  "theory_requirements": {
    "social_identity_theory": {
      "required_analyses": [
        {
          "analysis": "group_membership_network",
          "purpose": "identify group boundaries and membership",
          "data_format": "graph"
        },
        {
          "analysis": "bias_measurement",
          "purpose": "quantify in-group favoritism and out-group derogation",
          "data_format": "table"
        },
        {
          "analysis": "discourse_similarity",
          "purpose": "measure linguistic similarity within groups",
          "data_format": "vector"
        }
      ]
    }
  },
  
  "executed_analyses": [
    {
      "analysis_type": "group_membership_network",
      "results": {
        "groups_identified": ["Democrat", "Republican"],
        "speaker_assignments": {
          "speaker_012": "Democrat",
          "speaker_015": "Republican"
        },
        "cross_group_interactions": 15,
        "within_group_interactions": 45
      },
      "confidence": 0.85,
      "uncertainty_factors": ["some_speakers_unresolved", "implicit_references"]
    },
    {
      "analysis_type": "bias_measurement",
      "results": {
        "in_group_favoritism_score": {
          "Democrats_to_Democrats": 0.72,
          "Republicans_to_Republicans": 0.68
        },
        "out_group_derogation_score": {
          "Democrats_to_Republicans": -0.45,
          "Republicans_to_Democrats": -0.52
        }
      },
      "confidence": 0.75,
      "uncertainty_factors": ["bias_vs_policy_disagreement", "sampling_limitations"]
    },
    {
      "analysis_type": "discourse_similarity",
      "results": {
        "within_group_similarity": {
          "Democrat": 0.82,
          "Republican": 0.79
        },
        "between_group_similarity": 0.43,
        "distinctive_phrases": {
          "Democrat": ["voting rights", "protect democracy", "every American"],
          "Republican": ["states' rights", "election integrity", "local control"]
        }
      },
      "confidence": 0.8
    }
  ],
  
  "theoretical_coverage": 0.9,
  "missing_analyses": [],
  "analysis_execution_confidence": 0.8,
  "evidence_convergence": {
    "all_analyses_consistent": true,
    "convergence_benefit": 0.1,
    "reasoning": "Multiple analyses confirm group-based behavioral patterns"
  }
}
```

### Multi-Instance Aggregation with Entity Resolution

```json
{
  "construct": "group_identity",
  "speaker": "speaker_012",
  "instances": [
    {
      "instance_id": "inst_001",
      "text": "We need to address",
      "initial_confidence": 0.7,
      "resolved_confidence": 0.9,
      "entity": "Democrat"
    },
    {
      "instance_id": "inst_003",
      "text": "As Democrats, we",
      "initial_confidence": 0.95,
      "resolved_confidence": 0.95,
      "entity": "Democrat"
    },
    {
      "instance_id": "inst_007",
      "text": "our Democratic values",
      "initial_confidence": 0.9,
      "resolved_confidence": 0.9,
      "entity": "Democrat"
    }
  ],
  
  "aggregation_method": "contextual_bayesian",
  "aggregate_confidence": 0.93,
  "reasoning": "Multiple consistent references with explicit identification provide high confidence. Context accumulation strengthened initially ambiguous references.",
  
  "entity_consistency": {
    "all_instances_same_entity": true,
    "resolution_impact": "Early ambiguous references resolved by later explicit identification"
  }
}
```

## Stage 5: Research Application

### Research Question: "How do political group identities influence discourse during congressional hearings?"

```json
{
  "research_application": {
    "findings": [
      {
        "finding": "Strong political party-based group identities evident",
        "confidence": 0.9,
        "evidence": [
          "Explicit party identification by multiple speakers",
          "Consistent use of we/they pronouns along party lines",
          "Entity resolution confirmed party-based groupings"
        ]
      },
      {
        "finding": "In-group favoritism present in both parties",
        "confidence": 0.75,
        "evidence": [
          "Positive attribution scores within party (D:0.72, R:0.68)",
          "Linguistic similarity higher within groups (0.8) than between (0.43)",
          "Credibility attribution patterns favor same-party speakers"
        ],
        "caveats": ["Difficult to separate from legitimate policy alignment"]
      },
      {
        "finding": "Out-group derogation observed symmetrically",
        "confidence": 0.7,
        "evidence": [
          "Negative attribution scores across parties (D→R:-0.45, R→D:-0.52)",
          "Skepticism markers used for opposite party claims",
          "Delegitimizing language ('so-called', 'partisan games')"
        ],
        "caveats": ["Cannot definitively separate from substantive criticism"]
      },
      {
        "finding": "Group identity influences discourse patterns",
        "confidence": 0.85,
        "evidence": [
          "Distinctive vocabulary by party affiliation",
          "Interaction patterns show party-based clustering",
          "Entity resolution revealed consistent party-aligned references"
        ]
      }
    ],
    
    "answer_to_research_question": {
      "summary": "Political group identities strongly influence congressional discourse through party-based in-group favoritism, out-group derogation, and distinctive communication patterns",
      "confidence": 0.82,
      "key_uncertainty": "Distinguishing identity-driven bias from legitimate policy disagreement"
    },
    
    "methodological_strengths": [
      "Entity resolution clarified ambiguous group references",
      "Multiple analysis types provided convergent evidence",
      "Bayesian updating allowed context accumulation"
    ],
    
    "limitations": [
      {
        "limitation": "Single hearing snapshot",
        "impact": "Cannot assess temporal dynamics",
        "confidence_impact": -0.1
      },
      {
        "limitation": "Bias vs legitimate criticism ambiguity",
        "impact": "Some behaviors could be justified",
        "confidence_impact": -0.15
      }
    ],
    
    "application_confidence": 0.82
  }
}
```

## Uncertainty Propagation Through Pipeline

```json
{
  "uncertainty_propagation": {
    "stage_confidences": {
      "stage_1_theory_translation": 0.85,
      "stage_2_construct_mapping": 0.75,
      "stage_3_instance_extraction": 0.83,
      "stage_4_analysis_execution": 0.8,
      "stage_5_research_application": 0.82
    },
    
    "propagation_method": "hybrid_llm_assessment",
    "propagation_reasoning": "Theory translation uncertainty (0.85) affects construct mapping (0.75), but entity resolution in Stage 3 (0.83) reduces ambiguity. Analysis execution (0.8) benefits from resolved entities. Final application confidence (0.82) reflects both strengths and persistent uncertainties.",
    
    "major_uncertainty_sources": [
      {
        "source": "bias_vs_criticism_distinction",
        "stages_affected": [2, 3, 5],
        "impact": "Cannot definitively separate motivated bias from legitimate disagreement"
      },
      {
        "source": "entity_resolution_ambiguity", 
        "stages_affected": [3, 4],
        "impact": "Some references remained probabilistic rather than certain"
      }
    ],
    
    "uncertainty_reduction_achieved": [
      {
        "mechanism": "entity_resolution",
        "reduction": 0.15,
        "explanation": "Contextual resolution clarified initially ambiguous references"
      },
      {
        "mechanism": "convergent_evidence",
        "reduction": 0.1,
        "explanation": "Multiple analyses confirmed patterns"
      }
    ],
    
    "final_propagated_confidence": 0.82
  }
}
```

## Key Insights from Entity Resolution Integration

1. **Context Accumulation**: Early ambiguous references ("we", "they") gained clarity through later explicit identification
2. **Constraint Propagation**: Knowing speaker's party identity constrained interpretation of oppositional references
3. **Retroactive Updates**: Bayesian framework allowed updating earlier instances based on later evidence
4. **Partial Resolution Value**: Even unresolved entities (UNKNOWN_GROUP_A vs UNKNOWN_GROUP_B) provided analytical value
5. **Speaker Consistency**: Same speaker's references formed coreference chains, improving overall confidence

## Conclusion

This example demonstrates how entity resolution significantly enhances Social Identity Theory analysis by:
- Tracking and resolving ambiguous group references throughout discourse
- Using Bayesian updating to accumulate context and improve interpretations
- Maintaining uncertainty for unresolved references while maximizing analytical value
- Providing transparent audit trail of resolution decisions
- Enabling more confident research conclusions through systematic reference tracking

The integration of entity resolution with the uncertainty framework ensures that referential ambiguity—a major source of uncertainty in discourse analysis—is properly quantified and managed throughout the analytical pipeline.