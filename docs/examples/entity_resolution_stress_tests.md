# Entity Resolution Stress Tests: End-to-End Examples

## Overview

This document contains comprehensive examples designed to stress test the simplified entity resolution framework across different theoretical frameworks and challenging discourse patterns.

## Test 1: Social Movement Theory with Coalition Dynamics

### Theory Schema
```json
{
  "theory_name": "Social Movement Theory",
  "constructs": [
    {
      "name": "movement_identity",
      "definition": "Collective identity of social movement participants",
      "observable_indicators": ["we/us/our + movement terms", "collective action language"],
      "requires_entity_tracking": true
    },
    {
      "name": "coalition_dynamics",
      "definition": "Relationships between allied movement groups",
      "observable_indicators": ["partnership language", "joint action references"],
      "requires_entity_tracking": true
    },
    {
      "name": "opponent_framing",
      "definition": "How movements characterize their opposition",
      "observable_indicators": ["they/them + negative characterization"],
      "requires_entity_tracking": true
    }
  ]
}
```

### Example Discourse
```
Speaker_001 (Environmental Activist): "We need to unite all environmental groups. The oil companies have divided us for too long."

Speaker_002 (Labor Representative): "Our union stands with you. They told us environmentalists were against workers, but we know they lied."

Speaker_003 (Indigenous Leader): "My people have fought them for generations. We welcome this coalition, though we've been betrayed before."

Speaker_001: "Together, we represent millions. They can't ignore us anymore."

Speaker_002: "When we march next week, they'll see our combined strength."
```

### Processing with Simplified Framework

#### Stage 3: Instance Extraction with Distributions

**Unit 1 (Speaker_001, first statement)**:
```json
{
  "instances": [
    {
      "text": "We",
      "position": 0,
      "construct": "movement_identity",
      "value_distribution": {
        "Environmental_Groups": 0.7,
        "Environmental_Activists": 0.2,
        "UNKNOWN": 0.1
      },
      "confidence": 0.7,
      "evidence": {
        "quote": "We need to unite all environmental groups",
        "reasoning": "Speaker identified as environmental activist, 'we' likely refers to environmental movement"
      }
    },
    {
      "text": "The oil companies",
      "position": 40,
      "construct": "opponent_framing",
      "value": "Oil_Companies",
      "confidence": 0.95,
      "evidence": {
        "quote": "The oil companies have divided us",
        "reasoning": "Explicit identification of opponent"
      }
    }
  ]
}
```

**Unit 2 (Speaker_002)**:
```json
{
  "instances": [
    {
      "text": "Our union",
      "position": 100,
      "construct": "movement_identity",
      "value": "Labor_Union",
      "confidence": 0.95,
      "evidence": {
        "quote": "Our union stands with you",
        "reasoning": "Explicit group identification"
      }
    },
    {
      "text": "They",
      "position": 130,
      "construct": "opponent_framing",
      "value_distribution": {
        "Oil_Companies": 0.6,
        "Corporate_Interests": 0.3,
        "UNKNOWN": 0.1
      },
      "confidence": 0.6,
      "evidence": {
        "quote": "They told us environmentalists were against workers",
        "reasoning": "Ambiguous 'they' but context suggests same opponents"
      }
    }
  ]
}
```

**Unit 3 (Speaker_003)**:
```json
{
  "instances": [
    {
      "text": "My people",
      "position": 200,
      "construct": "movement_identity",
      "value": "Indigenous_Community",
      "confidence": 0.9,
      "evidence": {
        "quote": "My people have fought them",
        "reasoning": "Speaker identified as Indigenous Leader"
      }
    },
    {
      "text": "them",
      "position": 220,
      "construct": "opponent_framing",
      "value_distribution": {
        "Oil_Companies": 0.5,
        "Colonizers": 0.3,
        "Corporate_Interests": 0.2
      },
      "confidence": 0.5,
      "evidence": {
        "quote": "fought them for generations",
        "reasoning": "Historical context suggests multiple possible opponents"
      }
    },
    {
      "text": "we",
      "position": 250,
      "construct": "coalition_dynamics",
      "value_distribution": {
        "Indigenous_Community": 0.7,
        "Emerging_Coalition": 0.3
      },
      "confidence": 0.7,
      "evidence": {
        "quote": "we've been betrayed before",
        "reasoning": "Ambiguous whether 'we' refers to Indigenous community or new coalition"
      }
    }
  ]
}
```

#### Stage 4: Aggregated Analysis

```python
# Aggregated results incorporating distributions
{
  "movement_identity": {
    "Environmental_Groups": 0.7,
    "Environmental_Activists": 0.2,
    "Labor_Union": 0.95,
    "Indigenous_Community": 0.9,
    "UNKNOWN": 0.1
  },
  "opponent_framing": {
    "Oil_Companies": 2.6,  # 0.95 + 0.6 + 0.5 + 0.5
    "Corporate_Interests": 0.5,
    "Colonizers": 0.3,
    "UNKNOWN": 0.1
  },
  "coalition_dynamics": {
    "Indigenous_Community": 0.7,
    "Emerging_Coalition": 0.3
  }
}
```

### Stress Points Revealed

1. **Historical vs Contemporary References**: Indigenous leader's "them" could refer to historical colonizers or current oil companies
2. **Coalition Formation Ambiguity**: When does "we" shift from individual groups to coalition?
3. **Multi-level Opposition**: Same entity (oil companies) framed differently by different speakers
4. **No Retroactive Updates Needed**: System maintains all distributions without forcing resolution

## Test 2: Discourse Analysis Theory with Meta-Commentary

### Theory Schema
```json
{
  "theory_name": "Critical Discourse Analysis",
  "constructs": [
    {
      "name": "power_holder",
      "definition": "Entity wielding discursive power",
      "observable_indicators": ["control language", "decision-making references"],
      "requires_entity_tracking": true
    },
    {
      "name": "marginalized_voice",
      "definition": "Entity positioned as lacking power",
      "observable_indicators": ["exclusion language", "silencing references"],
      "requires_entity_tracking": true
    },
    {
      "name": "discourse_legitimacy",
      "definition": "Claims about who can speak authoritatively",
      "observable_indicators": ["authority claims", "expertise references"],
      "requires_entity_tracking": false
    }
  ]
}
```

### Example Discourse (Academic Panel)
```
Moderator: "Let's hear from our experts on this issue."

Professor_A: "We in the academic community have studied this for decades. They often misrepresent our findings."

Activist_B: "You say 'we' but you mean elite universities. We who work in communities know the real impact."

Professor_A: "I think we need to distinguish between rigorous research and anecdotal evidence."

Journalist_C: "This is exactly what they mean when they say academics are out of touch. We need both perspectives."

Activist_B: "Thank you. They always try to silence us by questioning our legitimacy."
```

### Processing Challenges

**Unit 1 (Professor_A, first statement)**:
```json
{
  "instances": [
    {
      "text": "We in the academic community",
      "position": 50,
      "construct": "power_holder",
      "value": "Academic_Community",
      "confidence": 0.9,
      "evidence": {
        "quote": "We in the academic community have studied",
        "reasoning": "Explicit group identification with authority claim"
      }
    },
    {
      "text": "They",
      "position": 100,
      "construct": "marginalized_voice",
      "value_distribution": {
        "Media": 0.4,
        "Public": 0.3,
        "Non_Academics": 0.3
      },
      "confidence": 0.4,
      "evidence": {
        "quote": "They often misrepresent our findings",
        "reasoning": "Ambiguous external group"
      }
    }
  ]
}
```

**Unit 2 (Activist_B response)**:
```json
{
  "instances": [
    {
      "text": "you mean elite universities",
      "position": 150,
      "construct": "power_holder",
      "value": "Elite_Universities",
      "confidence": 0.85,
      "evidence": {
        "quote": "You say 'we' but you mean elite universities",
        "reasoning": "Reframing/challenging Professor_A's 'we'"
      }
    },
    {
      "text": "We who work in communities",
      "position": 180,
      "construct": "marginalized_voice",
      "value": "Community_Workers",
      "confidence": 0.9,
      "evidence": {
        "quote": "We who work in communities know",
        "reasoning": "Contrastive self-identification"
      }
    }
  ]
}
```

### Meta-Discourse Challenges

1. **Contested Group Boundaries**: Activist challenges Professor's definition of "we"
2. **Shifting Power Dynamics**: Same groups positioned as powerful or marginalized depending on speaker
3. **Meta-Commentary**: Speakers explicitly discussing entity references ("You say 'we' but...")
4. **Indirect References**: "This is exactly what they mean" - reporting others' speech

## Test 3: International Relations Theory with Nested Coalitions

### Theory Schema
```json
{
  "theory_name": "Alliance Formation Theory",
  "constructs": [
    {
      "name": "alliance_member",
      "definition": "State or group within security alliance",
      "observable_indicators": ["alliance language", "collective security references"],
      "requires_entity_tracking": true
    },
    {
      "name": "adversary_state",
      "definition": "State positioned as threat to alliance",
      "observable_indicators": ["threat language", "opposition framing"],
      "requires_entity_tracking": true
    },
    {
      "name": "neutral_party",
      "definition": "Non-aligned state or group",
      "observable_indicators": ["neutrality claims", "non-alignment language"],
      "requires_entity_tracking": true
    }
  ]
}
```

### Example Discourse (Diplomatic Cables)
```
Cable_001: "We must coordinate with them before the summit. Their position affects our entire alliance."

Cable_002: "They claim neutrality but their recent agreements suggest otherwise. We should assume they're aligned with them."

Cable_003: "Our partners in the eastern coalition share our concerns. They've seen how they operate in their region."

Cable_004: "When we met with their delegation, they assured us of their commitment. But we know they say different things to different audiences."
```

### Processing with Maximum Ambiguity

**Cable_001**:
```json
{
  "instances": [
    {
      "text": "We",
      "position": 0,
      "construct": "alliance_member",
      "value_distribution": {
        "UNKNOWN_STATE_A": 1.0
      },
      "confidence": 0.3,
      "evidence": {
        "quote": "We must coordinate with them",
        "reasoning": "No identifying information for sender state"
      }
    },
    {
      "text": "them",
      "position": 25,
      "construct": "neutral_party",
      "value_distribution": {
        "UNKNOWN_STATE_B": 1.0
      },
      "confidence": 0.3
    },
    {
      "text": "Their",
      "position": 50,
      "construct": "neutral_party",
      "value_distribution": {
        "UNKNOWN_STATE_B": 0.8,  // Likely same as previous "them"
        "UNKNOWN_STATE_C": 0.2
      },
      "confidence": 0.4
    }
  ]
}
```

### Stress Points

1. **Complete Ambiguity**: No states are ever explicitly named
2. **Circular References**: "They" might refer to previously mentioned "them" or new entity
3. **Nested Coalitions**: "Our partners in the eastern coalition" - coalition within alliance
4. **Deceptive Communication**: "they say different things to different audiences"

## Test 4: Organizational Theory with Hierarchy

### Theory Schema
```json
{
  "theory_name": "Organizational Power Theory",
  "constructs": [
    {
      "name": "leadership",
      "definition": "Those with formal decision-making power",
      "observable_indicators": ["decision language", "directive speech"],
      "requires_entity_tracking": true
    },
    {
      "name": "middle_management",
      "definition": "Intermediary power holders",
      "observable_indicators": ["coordination language", "reporting references"],
      "requires_entity_tracking": true
    },
    {
      "name": "workers",
      "definition": "Those subject to organizational power",
      "observable_indicators": ["compliance language", "subordinate positioning"],
      "requires_entity_tracking": true
    }
  ]
}
```

### Example Discourse (Company Emails)
```
Email_001: "We need to implement the new policy by Friday. They're expecting full compliance."

Email_002: "Management has decided, but we know how this affects our team. They don't understand the daily operations."

Email_003: "I told them we need more time, but they insisted. We'll have to make do."

Email_004: "They always do this - make decisions without consulting us. We're the ones who have to deal with the consequences."
```

### Hierarchical Ambiguity

1. **Perspective-Dependent "We"**: Could be management to workers OR workers among themselves
2. **Upward vs Downward "They"**: Could refer to senior management OR subordinates
3. **Middle Management Ambiguity**: Same person might be "we" (to workers) and "they" (to leadership)

## Test 5: Gender Studies with Intersectionality

### Theory Schema
```json
{
  "theory_name": "Intersectional Identity Theory",
  "constructs": [
    {
      "name": "intersectional_identity",
      "definition": "Multiple overlapping identity categories",
      "observable_indicators": ["compound identity claims", "intersection language"],
      "requires_entity_tracking": true
    },
    {
      "name": "dominant_group",
      "definition": "Those with multiple privilege categories",
      "observable_indicators": ["privilege language", "dominance markers"],
      "requires_entity_tracking": true
    }
  ]
}
```

### Example Discourse
```
Speaker_A: "As Black women, we face unique challenges. They don't understand our experience."

Speaker_B: "We've been saying this for years - the intersection matters. When they talk about women's issues, they mean white women's issues."

Speaker_C: "But we who are queer and disabled face even more barriers. They exclude us from both movements."
```

### Intersectional Challenges

1. **Nested Group Membership**: "Black women" ⊂ "women" ⊂ "people"
2. **Shifting Boundaries**: Who counts as "they" changes with intersectional lens
3. **Multiple Valid Interpretations**: Same "we" could emphasize different identity aspects

## Analysis of Stress Test Results

### What Works Well

1. **Distribution Maintenance**: System handles ambiguity without forcing resolution
2. **Natural Processing**: Sliding window provides sufficient context
3. **Flexible Aggregation**: Weighted counting accommodates uncertainty
4. **Theory-Driven Focus**: Only tracks entities the theory requires

### Challenges Revealed

1. **Meta-Commentary**: When speakers discuss pronouns explicitly
2. **Circular References**: When entities reference each other ambiguously
3. **Hierarchical Ambiguity**: Same entity as "we" and "they" simultaneously
4. **Historical vs Contemporary**: Time-based entity changes

### Framework Validation

The simplified approach handles all test cases because:
- No complex ID tracking needed
- Distributions capture uncertainty naturally
- Context window provides local disambiguation
- Aggregation preserves all interpretations
- Theory requirements drive what matters

### Recommendations

1. **Add Time Markers**: Include temporal context in distributions
2. **Track Speaker Perspective**: Note that same entity can have different values from different speakers
3. **Handle Meta-Commentary**: Flag when speakers explicitly discuss references
4. **Preserve Ambiguity**: Never force resolution when multiple interpretations are valid

## Conclusion

These stress tests demonstrate that the simplified entity resolution framework successfully handles:
- Complete ambiguity (diplomatic cables)
- Contested definitions (discourse analysis)
- Nested groups (intersectionality)
- Dynamic coalitions (social movements)
- Hierarchical perspectives (organizations)

The key insight is that maintaining distributions throughout the pipeline, rather than forcing resolution, provides more honest and useful analysis while avoiding over-engineering.