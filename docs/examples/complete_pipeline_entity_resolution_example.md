# Complete Pipeline Example: Entity Resolution in KGAS

## End-to-End Example: Analyzing Political Polarization with Social Identity Theory

This document demonstrates how entity resolution works through all 5 stages of the KGAS pipeline using a realistic example.

## Stage 1: Theory Description → Theory Schema Translation

### Input: Social Identity Theory Description
```
Social Identity Theory posits that individuals derive part of their self-concept from their membership in social groups. This leads to in-group favoritism and out-group derogation. Key constructs include group identification (the extent to which individuals see themselves as group members), intergroup bias (differential treatment of in-group vs out-group), and group boundaries (who is considered part of "us" versus "them").
```

### Output: Theory Schema with Entity Requirements
```json
{
  "theory_name": "Social Identity Theory",
  "constructs": [
    {
      "name": "group_identification",
      "definition": "The extent to which individuals see themselves as group members",
      "boundary_specification": "Self-referential group membership claims",
      "observable_indicators": [
        "first-person plural pronouns (we, us, our)",
        "explicit group membership statements",
        "collective identity language"
      ],
      "requires_entity_resolution": true,
      "entity_type": "social_group"
    },
    {
      "name": "intergroup_bias",
      "definition": "Differential treatment of in-group vs out-group",
      "boundary_specification": "Comparative evaluations between groups",
      "observable_indicators": [
        "positive in-group characterizations",
        "negative out-group characterizations",
        "comparative statements"
      ],
      "requires_entity_resolution": true,
      "entity_type": "group_comparison"
    },
    {
      "name": "group_boundaries",
      "definition": "Distinctions between who is 'us' versus 'them'",
      "boundary_specification": "Explicit or implicit group demarcations",
      "observable_indicators": [
        "us/them dichotomies",
        "inclusion/exclusion language",
        "boundary-marking statements"
      ],
      "requires_entity_resolution": true,
      "entity_type": "boundary_marker"
    }
  ],
  "relationships": [
    {
      "from": "group_identification",
      "to": "intergroup_bias",
      "type": "leads_to",
      "strength": "theoretical_prediction"
    }
  ],
  "entity_constraints": [
    {
      "type": "mutual_exclusion",
      "description": "Same entity cannot be both in-group and out-group for same speaker"
    },
    {
      "type": "temporal_consistency",
      "description": "Group membership should remain consistent within discourse unit"
    }
  ],
  "confidence": 0.85,
  "reasoning": "Theory clearly defines constructs with observable indicators. Some ambiguity in operationalizing 'extent' of identification."
}
```

### Entity Resolution at Stage 1
- Defined which constructs require entity tracking
- Specified entity types and constraints
- No actual entity resolution yet - just requirements

## Stage 2: Data → Theoretical Construct Mapping

### Input: Congressional Debate Transcript
```
Sen. Smith (R): "We Republicans have always stood for fiscal responsibility. The Democrats' spending bill will bankrupt our nation."

Sen. Jones (D): "My colleague misrepresents our proposal. We Democrats are trying to help working families. They only care about their wealthy donors."

Sen. Smith (R): "That's rich coming from them. We know who really funds their campaigns."

Sen. Johnson (D): "The American people see through their tactics. We're the party that actually delivers results."
```

### Mapping Specification with Entity Patterns
```json
{
  "construct_mappings": {
    "group_identification": {
      "patterns": [
        {
          "pattern": "We Republicans",
          "extract_entity": true,
          "entity_type": "political_party",
          "confidence_boost": 0.2
        },
        {
          "pattern": "We Democrats", 
          "extract_entity": true,
          "entity_type": "political_party",
          "confidence_boost": 0.2
        },
        {
          "pattern": "we|us|our",
          "extract_entity": true,
          "entity_type": "implicit_group",
          "requires_context": true
        }
      ]
    },
    "intergroup_bias": {
      "patterns": [
        {
          "pattern": "[GROUP] + negative characterization",
          "extract_entities": ["in_group", "out_group"],
          "entity_relationship": "opposition"
        }
      ]
    },
    "group_boundaries": {
      "patterns": [
        {
          "pattern": "us vs them constructions",
          "extract_entities": ["in_group", "out_group"],
          "boundary_type": "explicit"
        }
      ]
    }
  },
  "mapping_confidence": 0.8,
  "reasoning": "Congressional debate provides clear partisan group identifications. Challenge is implicit references."
}
```

### Entity Resolution at Stage 2
- Patterns defined for entity extraction
- Context requirements specified
- Still no actual resolution - preparing extraction strategy

## Stage 3: Instance Extraction with Entity Resolution

### Processing Unit by Unit

#### Unit 1: Sen. Smith (R) First Statement
```json
{
  "speaker": "Sen. Smith",
  "party": "R",
  "text": "We Republicans have always stood for fiscal responsibility. The Democrats' spending bill will bankrupt our nation.",
  "extracted_instances": [
    {
      "text": "We Republicans",
      "position": 0,
      "construct": "group_identification",
      "value": "Republicans",
      "confidence": 0.95,
      "evidence": {
        "quote": "We Republicans have always stood",
        "reasoning": "Explicit group identification with party name"
      }
    },
    {
      "text": "The Democrats' spending bill will bankrupt",
      "position": 45,
      "construct": "intergroup_bias",
      "in_group": "Republicans",
      "out_group": "Democrats",
      "bias_type": "negative_outgroup",
      "confidence": 0.9,
      "evidence": {
        "quote": "Democrats' spending bill will bankrupt our nation",
        "reasoning": "Negative characterization of out-group policy"
      }
    }
  ]
}
```

#### Unit 2: Sen. Jones (D) Response
```json
{
  "speaker": "Sen. Jones", 
  "party": "D",
  "text": "My colleague misrepresents our proposal. We Democrats are trying to help working families. They only care about their wealthy donors.",
  "extracted_instances": [
    {
      "text": "our proposal",
      "position": 28,
      "construct": "group_identification",
      "value_distribution": {
        "Democrats": 0.8,
        "Legislative_Coalition": 0.2
      },
      "confidence": 0.8,
      "evidence": {
        "quote": "misrepresents our proposal",
        "reasoning": "Implicit group reference, likely Democrats based on speaker party"
      }
    },
    {
      "text": "We Democrats",
      "position": 42,
      "construct": "group_identification", 
      "value": "Democrats",
      "confidence": 0.95,
      "evidence": {
        "quote": "We Democrats are trying to help",
        "reasoning": "Explicit group identification"
      }
    },
    {
      "text": "They only care about their wealthy donors",
      "position": 80,
      "construct": "intergroup_bias",
      "in_group": "Democrats",
      "out_group": "Republicans",
      "bias_type": "negative_outgroup",
      "confidence": 0.85,
      "evidence": {
        "quote": "They only care about their wealthy donors",
        "reasoning": "Negative characterization, 'they' refers to Republicans from context"
      }
    }
  ]
}
```

#### Unit 3: Sen. Smith (R) Rebuttal
```json
{
  "speaker": "Sen. Smith",
  "party": "R", 
  "text": "That's rich coming from them. We know who really funds their campaigns.",
  "extracted_instances": [
    {
      "text": "them",
      "position": 25,
      "construct": "group_boundaries",
      "value_distribution": {
        "Democrats": 0.9,
        "Sen_Jones": 0.1
      },
      "confidence": 0.9,
      "evidence": {
        "quote": "That's rich coming from them",
        "reasoning": "Response to Jones, 'them' likely Democrats"
      }
    },
    {
      "text": "We",
      "position": 31,
      "construct": "group_identification",
      "value_distribution": {
        "Republicans": 0.85,
        "General_Public": 0.15
      },
      "confidence": 0.85,
      "evidence": {
        "quote": "We know who really funds",
        "reasoning": "Speaker is Republican, likely partisan 'we'"
      }
    },
    {
      "text": "their campaigns",
      "position": 50,
      "construct": "intergroup_bias",
      "out_group_distribution": {
        "Democrats": 0.9,
        "Politicians_Generally": 0.1
      },
      "confidence": 0.85
    }
  ]
}
```

#### Unit 4: Sen. Johnson (D) Statement
```json
{
  "speaker": "Sen. Johnson",
  "party": "D",
  "text": "The American people see through their tactics. We're the party that actually delivers results.",
  "extracted_instances": [
    {
      "text": "their tactics",
      "position": 32,
      "construct": "intergroup_bias",
      "out_group_distribution": {
        "Republicans": 0.85,
        "Political_Opposition": 0.15
      },
      "confidence": 0.85,
      "evidence": {
        "quote": "see through their tactics",
        "reasoning": "Following partisan exchange, 'their' likely Republicans"
      }
    },
    {
      "text": "We're the party",
      "position": 47,
      "construct": "group_identification",
      "value": "Democrats",
      "confidence": 0.9,
      "evidence": {
        "quote": "We're the party that actually delivers",
        "reasoning": "Speaker is Democrat, 'the party' indicates Democrats"
      }
    }
  ]
}
```

### Stage 3 Entity Resolution Summary
- Extracted 11 instances with entity references
- Mixed certain values and probability distributions
- No retroactive updates needed
- Context window helped disambiguate "they/them" references

## Stage 4: Theory-Required Analysis Execution

### Aggregated Entity Analysis
```python
# Aggregate all instances by construct and entity
aggregated_results = {
    "group_identification": {
        "Republicans": 2.8,  # 0.95 + 0.85 + contributions from distributions
        "Democrats": 3.7,    # 0.95 + 0.9 + 0.8 + contributions
        "Legislative_Coalition": 0.2,
        "General_Public": 0.15
    },
    
    "intergroup_bias": {
        "Republican_to_Democrat": [
            {"type": "negative", "confidence": 0.9, "topic": "spending"},
            {"type": "negative", "confidence": 0.85, "topic": "campaign_funding"}
        ],
        "Democrat_to_Republican": [
            {"type": "negative", "confidence": 0.85, "topic": "donor_priorities"},
            {"type": "negative", "confidence": 0.85, "topic": "tactics"}
        ]
    },
    
    "group_boundaries": {
        "us_them_instances": 4,
        "explicit_boundaries": 2,  # "We Republicans", "We Democrats"
        "implicit_boundaries": 2   # "them", "their"
    }
}
```

### Theory-Required Analyses
```json
{
  "analyses_executed": [
    {
      "analysis": "Group Identification Strength",
      "method": "Frequency and explicitness of group references",
      "results": {
        "Republicans": {
          "identification_score": 0.88,
          "explicit_claims": 1,
          "implicit_claims": 2
        },
        "Democrats": {
          "identification_score": 0.92,
          "explicit_claims": 2,
          "implicit_claims": 2
        }
      },
      "confidence": 0.85,
      "entity_resolution_impact": "High confidence due to explicit party identifications"
    },
    {
      "analysis": "Intergroup Bias Measurement",
      "method": "Sentiment analysis of cross-group references",
      "results": {
        "bias_symmetry": "bidirectional_negative",
        "bias_intensity": 0.87,
        "bias_topics": ["fiscal_policy", "campaign_ethics"]
      },
      "confidence": 0.82,
      "entity_resolution_impact": "Some uncertainty in pronoun references reduced confidence slightly"
    },
    {
      "analysis": "Boundary Rigidity Assessment",
      "method": "Explicitness and consistency of group boundaries",
      "results": {
        "boundary_rigidity_score": 0.91,
        "evidence": "Clear us/them language, no boundary crossing observed"
      },
      "confidence": 0.88
    }
  ],
  
  "convergent_evidence": {
    "multiple_speakers_same_pattern": true,
    "consistent_group_references": true,
    "theoretical_predictions_confirmed": true
  },
  
  "overall_analysis_confidence": 0.85
}
```

### Stage 4 Entity Resolution Impact
- Entity distributions incorporated into analysis
- Confidence adjusted based on resolution certainty
- Patterns clear despite some ambiguous references

## Stage 5: Research Application

### Research Question
"How does partisan social identity manifest in congressional debates?"

### Findings with Entity Resolution Transparency
```json
{
  "research_findings": {
    "primary_finding": "Strong partisan social identity exhibited by both parties",
    "supporting_evidence": [
      {
        "evidence": "Explicit group identification",
        "strength": "strong",
        "examples": ["We Republicans", "We Democrats"],
        "entity_certainty": "high"
      },
      {
        "evidence": "Symmetric negative intergroup bias",
        "strength": "strong", 
        "examples": ["bankruptcy accusations", "donor criticism"],
        "entity_certainty": "moderate_to_high"
      },
      {
        "evidence": "Rigid group boundaries",
        "strength": "strong",
        "examples": ["consistent us/them framing"],
        "entity_certainty": "moderate"
      }
    ],
    
    "entity_resolution_summary": {
      "total_entity_references": 15,
      "fully_resolved": 8,
      "distribution_based": 7,
      "resolution_methods": {
        "explicit_identification": 4,
        "contextual_inference": 7,
        "speaker_party_inference": 4
      },
      "average_confidence": 0.87
    },
    
    "caveats": [
      "Some pronoun references ('they', 'them') relied on contextual inference",
      "Assumed party alignment for implicit 'we' references",
      "No instances of boundary crossing or coalition formation observed"
    ],
    
    "application_confidence": 0.83,
    "reasoning": "High confidence despite some entity ambiguity due to consistent patterns across speakers and explicit party identifications anchoring the analysis."
  }
}
```

## Complete Pipeline Summary

### Entity Resolution Contributions by Stage

1. **Stage 1**: Defined entity tracking requirements in theory schema
2. **Stage 2**: Created mapping patterns for entity extraction  
3. **Stage 3**: Extracted entities with distributions for ambiguous references
4. **Stage 4**: Aggregated entities and incorporated uncertainty into analysis
5. **Stage 5**: Reported findings with entity resolution transparency

### Key Success Factors

1. **Natural Processing**: Sliding context window provided sufficient disambiguation
2. **Distribution Preservation**: Ambiguous references maintained as distributions
3. **Transparent Aggregation**: Weighted counting preserved uncertainty information
4. **Theory-Driven Focus**: Only tracked entities relevant to Social Identity Theory

### Validation of Simplified Approach

This example demonstrates that the simplified entity resolution framework:
- Handles real political discourse effectively
- Maintains appropriate uncertainty for ambiguous references
- Produces meaningful analysis despite incomplete resolution
- Scales linearly without complex tracking overhead

The framework successfully bridges the gap between theoretical requirements and practical discourse analysis, providing researchers with transparent, uncertainty-aware entity handling throughout the analytical pipeline.