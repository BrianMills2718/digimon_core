# Extreme Stress Tests: Entity Resolution Edge Cases

## Overview

These examples explore scenarios that push the boundaries of entity resolution, revealing fundamental challenges in how we conceptualize "entities" in social science discourse.

## Test 1: Performative Entity Creation

### Theory: Speech Act Theory
```json
{
  "theory_name": "Speech Act Theory",
  "constructs": [
    {
      "name": "performative_group_creation",
      "definition": "Groups brought into existence through declarative speech",
      "observable_indicators": ["we hereby form", "I declare us", "from now on we"]
    },
    {
      "name": "illocutionary_force",
      "definition": "The force that creates new social reality",
      "observable_indicators": ["hereby", "declare", "proclaim", "establish"]
    }
  ]
}
```

### Discourse Example
```
Meeting Transcript, Time 14:00:
Facilitator: "We need to form working groups."
Participant_A: "I propose we create three teams."
Facilitator: "Good. I hereby establish Team Alpha. You five are now Team Alpha."
Participant_B: "We accept this designation."
Participant_C: "But we were already part of the steering committee."
Facilitator: "You can be both. Team Alpha, we need you to report by Friday."
Participant_A: "When we meet tomorrow, should we include the others?"
Facilitator: "Team Alpha is just you five. We'll form Team Beta next."

Time 14:30:
Participant_B: "We in Team Alpha have concerns..."
Participant_D: "As do we in the steering committee..."
Participant_B: "But we're the same people!"
```

### What Breaks

1. **Entity Creation Moment**: "We" doesn't exist before the performative act
2. **Dual Membership**: Same individuals are simultaneously "Team Alpha" and "steering committee"
3. **Temporal Validity**: "We" (Team Alpha) only exists after 14:00
4. **Reference Ambiguity**: "We" could mean either group from same speaker

### Framework Behavior
```python
# Before performative act
"we" @ 14:00 → {"UNKNOWN": 1.0}  # Can't reference entity that doesn't exist yet

# After performative act  
"we" @ 14:30 → {
    "Team_Alpha": 0.5,
    "Steering_Committee": 0.5
}  # Can't handle same people = two groups
```

### Fundamental Challenge
Our framework assumes entities exist independently of discourse, but performative speech acts CREATE entities through discourse itself.

## Test 2: Negation-Defined Entities

### Theory: Boundary Work Theory
```json
{
  "theory_name": "Boundary Work Theory",
  "constructs": [
    {
      "name": "boundary_definition",
      "definition": "Groups defined by what they are NOT",
      "observable_indicators": ["not them", "unlike those", "different from"]
    }
  ]
}
```

### Discourse Example
```
"We are not like them - those who sold out to corporate interests. We're not the establishment. We're not the radicals either. We are something new. They'll call us populists, but we're not that either. When they try to define us, we resist. We define ourselves by what we refuse to be."
```

### What Breaks

1. **Negative Space Identity**: "We" is defined entirely by what it's NOT
2. **Infinite Regress**: Each "not X" could spawn tracking X as an entity
3. **No Positive Identity**: Never says what "we" IS, only what it ISN'T

### Framework Behavior
```python
"we" → {"UNKNOWN_GROUP": 1.0}  # Can't determine positive identity
"them" → {"Corporate_Sellouts": 0.9}
# But "we" is defined as NOT "them" - how to represent?
```

### Fundamental Challenge
Entities defined through negation have no positive features to track. Our probability distributions assume positive identification.

## Test 3: Probabilistic Entity References

### Discourse Example
```
Intelligence Briefing:
"They are probably the same group that attacked last month. We think they're connected to them, but we're not certain. It's likely they have ties to the organization, though they might be a splinter group. We believe they're responsible, but they could be copycats. When we say 'they,' we mean probably the insurgents, possibly the militia, but unlikely to be the cartel."
```

### What Breaks

1. **Nested Uncertainty**: Uncertainty about uncertainty
2. **Conditional Probabilities**: "If they are X, then probably Y"
3. **Explicitly Probabilistic Language**: "probably", "likely", "possibly"

### Framework Behavior
```python
"they" → {
    "Insurgents": 0.6,
    "Militia": 0.3,
    "Cartel": 0.1
}
# But this loses that speaker EXPLICITLY expressed uncertainty
# Not the same as inferring uncertainty from ambiguous text
```

### Fundamental Challenge
Difference between inferred uncertainty (our framework) and explicit uncertainty (speaker's hedge).

## Test 4: Fluid Collective Identity

### Theory: Assemblage Theory
```json
{
  "theory_name": "Assemblage Theory",
  "constructs": [
    {
      "name": "fluid_assemblage",
      "definition": "Temporary collections that form and dissolve dynamically",
      "observable_indicators": ["whoever shows up", "all who care", "those present"]
    }
  ]
}
```

### Discourse Example
```
Protest Organizer Log:
Day 1: "We who gathered today numbered about 50."
Day 2: "We grew to 200. Some from yesterday, many new."
Day 3: "We are now thousands. We are whoever shows up."
Day 4: "When we march, we are united. When we disperse, we dissolve."
Day 5: "We are not an organization. We are a moment."
```

### What Breaks

1. **Fluid Boundaries**: "We" changes composition daily
2. **Non-Persistent Entity**: Exists only when assembled
3. **Self-Referential Definition**: "We are whoever shows up"

### Framework Behavior
```python
# Treats each day's "we" as potentially same entity
Day_1_we: {"Protesters": 0.8}
Day_2_we: {"Protesters": 0.8}  # But it's different people!
```

### Fundamental Challenge
Assumes entities have stable membership. Can't model fluid assemblages that exist only in action.

## Test 5: Metaphorical vs Literal Entities

### Discourse Example
```
Corporate Email:
"We need to kill the competition. They're eating our lunch. We'll crush them in Q4. But we also need to partner with them on the standards committee. When we meet with them next week, we should appear friendly. They're both our biggest threat and our necessary partners."
```

### What Breaks

1. **Metaphorical Violence**: "kill", "crush" aren't literal
2. **Same Entity, Different Frames**: Competitor AND partner
3. **Context Switching**: Hostile in market, collaborative in standards

### Framework Behavior
```python
"them" → {"Competitor_Corp": 0.9}  # Same entity throughout
# But misses the frame switching between adversarial and collaborative
```

## Test 6: Recursive Self-Reference

### Discourse Example
```
"We are studying how we talk about ourselves. When we say 'we,' we mean both we-the-researchers and we-the-community we're studying. We find that we often confuse ourselves when we analyze how we use 'we.'"
```

### What Breaks

1. **Meta-Level Confusion**: Studying the act of studying
2. **Recursive Reference**: "We" analyzing "we" saying "we"
3. **Dual Roles**: Researcher AND subject simultaneously

### Framework Behavior
```python
# Every "we" gets different distribution despite recursive structure
we_1: {"Researchers": 0.8}
we_2: {"Researchers": 0.5, "Community": 0.5}
we_3: {"Researchers": 0.7}
# Loses the recursive, self-referential structure
```

## Test 7: Counterfactual Group Identity

### Discourse Example
```
"If we had won the election, we would be implementing our policies now. They wouldn't be able to stop us. In that world, we control the agenda. But since we lost, they dictate terms. The we-that-could-have-been haunts the we-that-is."
```

### What Breaks

1. **Counterfactual Entities**: Groups in alternate timelines
2. **Modal References**: "would be", "could have been"
3. **Parallel Identities**: Actual vs potential versions of same group

### Framework Behavior
```python
"we" → {"Opposition_Party": 0.9}  # Same for all instances
# Loses distinction between actual and counterfactual versions
```

## Test 8: Culturally Embedded References

### Discourse Example (Japanese Political Speech)
```
"Ware-ware nihonjin wa..." (We Japanese...)
"Watashi-tachi wa..." (We [humble]...)
"Uchi no mono wa..." (Our/inside people...)
"Soto no hito wa..." (Outside people...)
"Kata-gata wa..." (Those honored persons...)
```

### What Breaks

1. **Cultural Encoding**: Pronouns carry social hierarchy info
2. **In-group/Out-group Built In**: "uchi/soto" fundamentally different from "we/they"
3. **Honorific Levels**: Same referent, different social positioning

### Framework Behavior
```python
# Treats all as simple group references
"ware-ware" → {"Japanese": 0.9}
"watashi-tachi" → {"Japanese": 0.9}
# Loses crucial social positioning information
```

## Test 9: Emergence Through Interaction

### Discourse Example
```
Online Forum Thread:
User_A: "Anyone else think we should do something?"
User_B: "We who care should act."
User_C: "Count me in with 'we'."
User_D: "We're becoming a movement."
User_E: "Are we 'we' yet?"
User_A: "We are now."
```

### What Breaks

1. **Emergent Identity**: "We" forms through the conversation
2. **Self-Aware Formation**: Explicitly discussing becoming "we"
3. **Voluntary Affiliation**: Individuals choosing to join "we"

### Framework Behavior
```python
# Treats early and late "we" as same uncertainty
User_A_we: {"UNKNOWN": 1.0}
User_A_we_later: {"Movement": 0.7}
# Misses the formation process
```

## Test 10: Intersectional Complexity

### Discourse Example
```
"We Black women in STEM face unique challenges. When they - the white women - talk about gender issues, they don't include us. And when they - the Black men - discuss racial barriers, they forget us. We're invisible to both. But we who sit at these intersections see things they cannot."
```

### What Breaks

1. **Multiple "They"**: Different groups from same speaker
2. **Intersectional Identity**: Not sum of parts
3. **Exclusion Patterns**: Defined by what others miss

### Framework Behavior
```python
"we" → {"Black_Women_STEM": 0.9}
"they_1" → {"White_Women": 0.8}
"they_2" → {"Black_Men": 0.8}
# But loses the intersectional critique structure
```

## Analysis: What These Tests Reveal

### Fundamental Assumptions We Make

1. **Entities Pre-Exist Reference**: We assume entities exist before being mentioned
2. **Stable Membership**: We assume group membership is relatively fixed
3. **Positive Identity**: We assume entities defined by what they ARE
4. **Literal Reference**: We assume references are meant literally
5. **Single Timeline**: We assume one factual timeline
6. **Binary Membership**: In or out, not gradient membership

### Types of Entities We Can't Handle

1. **Performative Entities**: Created through speech acts
2. **Negative Entities**: Defined only by what they're NOT
3. **Fluid Entities**: Membership changes constantly
4. **Counterfactual Entities**: Exist in alternate timelines
5. **Emergent Entities**: Form through discourse itself
6. **Gradient Entities**: Partial or fuzzy membership

### Deeper Issues

1. **Ontological Assumptions**: We assume entities have independent existence
2. **Western Bias**: Our pronoun model fits English, not all languages
3. **Literal Interpretation**: Can't handle metaphor, irony, performance
4. **Time as Linear**: Can't handle complex temporalities
5. **Identity as Fixed**: Can't handle fluid, emergent identities

## Recommendations

### 1. Document Limitations Clearly

Our framework works for:
- Groups with stable membership
- Literal references to actual entities
- Single timeline, factual discourse
- Western-style pronoun systems

It fails for:
- Performative entity creation
- Fluid assemblages
- Counterfactual reasoning
- Non-Western pronoun systems

### 2. Consider Theory-Specific Extensions

Some theories may need:
- Performative entity tracking
- Negative identity representation
- Fluid membership models
- Counterfactual handling

### 3. Add Metadata Flags

```python
class EnhancedEntity:
    # Existing
    value_distribution: Dict[str, float]
    
    # Additional metadata
    reference_type: Literal["literal", "metaphorical", "counterfactual", "performative"]
    identity_type: Literal["positive", "negative", "emergent", "fluid"]
    certainty_type: Literal["inferred", "explicit", "hedged"]
```

### 4. Recognize Fundamental Limits

Some discourse requires:
- Human interpretation
- Cultural knowledge
- Philosophical frameworks
- Different ontologies

Our framework should acknowledge when it reaches these limits.

## Conclusion

These extreme stress tests reveal that entity resolution in social science discourse involves deep questions about:
- What constitutes an entity
- How entities come into being
- Whether membership is binary
- How time and modality affect reference
- Cultural variations in conceptualizing groups

Our balanced framework handles mainstream cases well, but users must understand it embodies particular assumptions about entities that may not fit all discourse types or theoretical frameworks. The key is transparency about these limitations.