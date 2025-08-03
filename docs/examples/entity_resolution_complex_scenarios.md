# Complex Entity Resolution Scenarios

## Scenario 1: Multi-Scale Organizational Identity

### Context: University Department Meeting

```
Meeting Transcript:

Dean: "We at the university need to increase research output."

Prof_A: "We in the sciences are already overwhelmed."

Prof_B: "But we in computer science specifically have unique challenges."

Prof_C: "When we talk to the administration, they don't understand."

Grad_Student: "We students feel caught in the middle."

Prof_A: "We need to remember we're all part of the same institution."

Prof_B: "Yes, but we in our department have specific needs. When we meet with them next week, we should present a united front."

Dean: "Who is 'them' in this context?"

Prof_B: "The budget committee. Though aren't you on that committee?"

Dean: "I am, but in that context, I represent them, not us."
```

### Multi-Scale Challenge

```python
# Same individuals belong to nested groups:
Person: Prof_B
Groups: [
    "University",          # Largest scale
    "Sciences",           # College level
    "Computer_Science",   # Department level
    "Budget_Committee",   # Cross-cutting
    "Meeting_Attendees"   # Immediate context
]

# "We" shifts scales within same conversation
"we at the university" → University level
"we in the sciences" → College level  
"we in computer science" → Department level
```

### Framework Limitations

1. **Scale-Hopping**: Same speaker uses "we" at different organizational scales
2. **Role-Based Identity**: Dean represents different groups in different contexts
3. **Nested Membership**: Can't represent hierarchical containment

### What Actually Happens

```python
# Our framework treats each separately
prof_b_utterances = [
    {"we": {"Computer_Science": 0.8}},
    {"we": {"Computer_Science": 0.7}},
    {"we": {"Meeting_Attendees": 0.6}}
]
# Loses the multi-scale navigation
```

## Scenario 2: Affective Group Formation

### Context: Online Support Group

```
Day 1:
User_123: "Does anyone else feel lost after the diagnosis?"
User_456: "I do. We're all struggling here."
User_789: "We who understand should support each other."

Day 7:
User_123: "We've become like family."
User_456: "When outsiders ask what we are, I can't explain."
NewUser: "Can I be part of 'we'?"
User_789: "You already are. We don't have membership cards."

Day 30:
User_123: "We've helped me more than they (doctors) ever did."
User_456: "We exist because we need each other."
External_Researcher: "How many people are in your group?"
User_789: "We aren't a number. We're a feeling."
```

### Affective Challenge

1. **Emotion-Based Membership**: Belonging based on shared feeling
2. **No Formal Boundaries**: Can't count members
3. **Exists in Relating**: Group exists through mutual support, not structure

### Framework Behavior

```python
"we" → {"Support_Group": 0.9}  # Treats as normal group
count: 4  # Based on speakers
# Completely misses the affective, unbounded nature
```

## Scenario 3: Historical Entities in Present Discourse

### Context: Political Heritage Claims

```
Speaker_A: "We Republicans are the party of Lincoln."
Speaker_B: "But we Democrats were the ones who passed Civil Rights."
Speaker_A: "They weren't the same Democrats. The parties switched."
Speaker_B: "We've evolved, but we're still the same party."
Speaker_A: "How can you be 'we' with segregationists?"
Speaker_B: "How can you be 'we' with Lincoln while opposing everything he stood for?"
Speaker_A: "We honor our heritage."
Speaker_B: "We learn from our mistakes."
```

### Temporal Challenge

1. **Historical Continuity Claims**: Claiming identity with past entities
2. **Changed Entities**: Parties fundamentally different than historical versions
3. **Selective Heritage**: Choosing which parts of history to claim

### Framework Behavior

```python
"we Republicans" → {"Republican_Party": 0.95}
"we Democrats" → {"Democratic_Party": 0.95}
# No distinction between current and historical versions
# Can't handle the identity-over-time philosophical question
```

## Scenario 4: Deliberately Ambiguous Strategic Communication

### Context: Corporate Merger Negotiations

```
CEO_A: "We're interested in collaboration."
CEO_B: "We would need to maintain autonomy."
CEO_A: "When we merge, we'll be stronger."
CEO_B: "Who is 'we' after a merger?"
CEO_A: "We'll be a new entity."
CEO_B: "Or we'll be absorbed into you."
Analyst: "They're talking past each other. Each 'we' means something different."
CEO_A: "We prefer strategic ambiguity at this stage."
```

### Strategic Challenge

1. **Intentional Ambiguity**: Vagueness is strategic, not accidental
2. **Future Entity**: "We" after merger doesn't exist yet
3. **Competing Visions**: Same future "we" imagined differently

### Framework Behavior

```python
CEO_A "we" → {"Company_A": 0.6, "Merged_Entity": 0.4}
CEO_B "we" → {"Company_B": 0.7, "Merged_Entity": 0.3}
# Treats ambiguity as uncertainty to resolve
# Misses that ambiguity is intentional strategy
```

## Scenario 5: Digital vs Physical Identity Splits

### Context: Hybrid Conference

```
Physical Room:
Moderator: "We here in Boston welcome our virtual participants."
Virtual Participant: "Thanks. We online actually outnumber you."
Physical Participant: "But we're the ones really here."
Virtual: "What makes us less real?"
Physical: "When we break for coffee, you can't join us."
Virtual: "We have our own breakout rooms."
Hybrid Participant (physical but also in chat): "I'm part of both 'we's simultaneously."
```

### Digital Challenge

1. **Spatial Splits**: Same event, different "we" based on medium
2. **Reality Claims**: Whose presence is "real"?
3. **Simultaneous Membership**: Can be in both groups at once

### Framework Behavior

```python
"we" (physical) → {"Boston_Attendees": 0.9}
"we" (virtual) → {"Online_Attendees": 0.9}
"we" (hybrid) → {"Boston_Attendees": 0.5, "Online_Attendees": 0.5}
# But hybrid person is 100% in both, not 50% in each
```

## Complete End-to-End Example: Academic Conference Panel

### Stage 1: Theory Schema

```json
{
  "theory_name": "Academic Discourse Analysis",
  "constructs": [
    {
      "name": "disciplinary_identity",
      "definition": "Identification with academic field",
      "observable_indicators": ["we in [field]", "our discipline", "we scholars"],
      "requires_entity_resolution": true
    },
    {
      "name": "paradigm_conflict",
      "definition": "Competing schools of thought",
      "observable_indicators": ["they claim", "their approach", "we argue"],
      "requires_entity_resolution": true
    }
  ]
}
```

### Stage 2: Complex Discourse

```
Panel: "Interdisciplinarity in Social Sciences"

Moderator: "We've assembled experts from various fields."

Sociologist: "We sociologists have always been interdisciplinary."

Economist: "We would dispute that. You borrow our methods."

Anthropologist: "We find both your approaches limiting."

Sociologist: "When we say 'interdisciplinary,' we mean genuine integration."

Economist: "But we've mathematized social science. They haven't."

Anthropologist: "Your 'we' excludes us qualitative researchers."

Audience_Member_1: "As practitioners, we need both approaches."

Audience_Member_2: "We who fund research care about impact, not disciplinary boundaries."

Sociologist: "We're all social scientists here."

Economist: "Are we though? Our methods differ fundamentally."

Anthropologist: "We each think we're the real social scientists."
```

### Stage 3: Entity Extraction Challenges

```python
# Multiple overlapping "we" groups:
instances = [
    {
        "speaker": "Sociologist",
        "text": "We sociologists",
        "value": "Sociologists",
        "confidence": 0.95
    },
    {
        "speaker": "Sociologist",  
        "text": "We're all social scientists",
        "value_distribution": {
            "Social_Scientists": 0.7,
            "Panel_Members": 0.3
        }
    },
    {
        "speaker": "Economist",
        "text": "We would dispute",
        "value_distribution": {
            "Economists": 0.8,
            "Quantitative_Researchers": 0.2
        }
    },
    {
        "speaker": "Economist",
        "text": "We've mathematized",
        "value": "Economists",
        "confidence": 0.9,
        "claim_type": "paradigm_superiority"  # Lost by framework
    }
]
```

### Stage 4: Aggregation Problems

```python
# Our framework produces:
aggregated = {
    "by_speaker": {
        "Sociologist": {
            "frequency": {"Sociologists": 1, "Social_Scientists": 0.7},
            "paradigm": "integrative"  # Can't capture
        },
        "Economist": {
            "frequency": {"Economists": 1.8, "Quantitative_Researchers": 0.2},
            "paradigm": "mathematical"  # Can't capture
        }
    },
    "overall": {
        "consensus_entities": [],  # No consensus!
        "contested_entities": ["Social_Scientists"]  # Everyone claims it
    }
}
```

### What We Miss

1. **Paradigm Positioning**: Each "we" implies a different vision of social science
2. **Exclusion Patterns**: Who each "we" implicitly excludes
3. **Meta-Debate**: They're debating what counts as legitimate social science
4. **Power Dynamics**: Economists claiming superiority through "mathematization"
5. **Audience Intervention**: Practitioners and funders reframe the debate

### Stage 5: Research Conclusions

```python
# What our framework produces:
findings = {
    "identified_groups": ["Sociologists", "Economists", "Anthropologists", 
                         "Practitioners", "Funders"],
    "group_frequency": {"Economists": 3.2, "Sociologists": 2.1, ...},
    "conflict_indicators": "High use of we/they distinctions"
}

# What we miss:
missed_insights = {
    "paradigm_conflict": "Competing visions of social science legitimacy",
    "boundary_work": "Each discipline defining social science to include themselves",
    "power_dynamics": "Quantitative methods as claim to scientific status",
    "meta_discourse": "Debate about the debate itself"
}
```

## Synthesis: Unhandled Phenomena

### 1. Scale Navigation
- Entities exist at multiple scales simultaneously
- Speakers navigate between scales strategically
- Same person represents different scales in different contexts

### 2. Affective Formation
- Groups formed through emotion/experience
- No formal membership boundaries
- Exist through relating, not structure

### 3. Temporal Complexity
- Historical continuity claims
- Future/potential entities
- Entities that change fundamentally but claim continuity

### 4. Strategic Ambiguity
- Intentional vagueness for negotiation
- Multiple possible futures held open
- Ambiguity as resource, not problem

### 5. Medium-Based Splitting
- Same event, different groups by medium
- Simultaneous membership in split groups
- Reality/presence claims

### 6. Meta-Level Discourse
- Debating the nature of groups themselves
- Boundary work through discourse
- Power dynamics in defining legitimate membership

## Recommendations for Users

### 1. Know Your Discourse Type

**Good Fit**:
- Clear institutional identities
- Stable group membership
- Contemporary timeframe
- Literal references

**Poor Fit**:
- Fluid/emergent groups
- Historical continuity claims
- Strategic ambiguity
- Meta-level debates

### 2. Consider Extensions Needed

- **Scale Extension**: For multi-level organizations
- **Temporal Extension**: For historical claims
- **Affective Extension**: For emotion-based groups
- **Strategic Extension**: For intentional ambiguity

### 3. Supplement with Qualitative Analysis

Some phenomena require:
- Discourse analysis
- Ethnographic insight  
- Historical knowledge
- Cultural understanding

### 4. Report Appropriately

Always note:
- What types of entities were resolved
- What phenomena were not captured
- How limitations might affect conclusions
- Where qualitative analysis is needed

## Conclusion

These complex scenarios reveal that entity resolution in social science discourse involves more than identifying who "we" and "they" refer to. It involves understanding:

- How groups form and transform
- Power dynamics in claiming identity
- Strategic uses of ambiguity
- Multiple simultaneous scales
- Affective and emergent formations
- Historical and future orientations

Our framework provides valuable automation for clear cases, but users must understand its ontological assumptions and supplement with appropriate qualitative methods for complex social phenomena.