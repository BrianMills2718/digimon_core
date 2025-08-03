# Entity Resolution: Practical Researcher's Guide

## What You'll Actually Get: A Realistic Example

### Your Research Question
"How do political coalitions form and transform during crisis negotiations?"

### Your Data
Three days of negotiation transcripts from a government shutdown crisis.

### Day 1 Transcript Sample
```
Sen_A (R): "We Republicans won't budge on spending cuts."
Sen_B (D): "We Democrats need to protect social programs."
Sen_C (R): "Some of us are willing to compromise."
Sen_D (D): "We moderates from both parties should talk."
Sen_A (R): "You're either with us or against us."
Sen_C (R): "We need a different approach. They're being too rigid."
Sen_B (D): "Who's 'they' - your own party?"
Sen_C (R): "Those who refuse to negotiate."
```

### What Our System Produces

#### Raw Entity Extractions
```json
{
  "entities_found": [
    {
      "speaker": "Sen_A",
      "text": "We Republicans",
      "value": "Republicans",
      "confidence": 0.95,
      "temporal": "present"
    },
    {
      "speaker": "Sen_C",
      "text": "Some of us",
      "value_distribution": {
        "Republicans": 0.6,
        "Moderate_Republicans": 0.4
      },
      "confidence": 0.6,
      "temporal": "present"
    },
    {
      "speaker": "Sen_C",
      "text": "They're being too rigid",
      "value_distribution": {
        "Republicans": 0.5,
        "Hardline_Republicans": 0.3,
        "UNKNOWN": 0.2
      },
      "confidence": 0.5,
      "note": "Ambiguous - could be own party"
    }
  ]
}
```

#### Aggregated Results
```json
{
  "by_speaker": {
    "Sen_A": {
      "primary_identity": "Republicans",
      "frequency": {"Republicans": 3, "us": 2},
      "stance": "hardline"
    },
    "Sen_C": {
      "primary_identity": "Republicans",
      "secondary_identity": "possible_moderate",
      "frequency": {"Republicans": 1, "us": 2, "they": 1},
      "stance": "shifting"
    }
  },
  "emerging_patterns": {
    "potential_split": "Republicans showing internal division",
    "cross_party_signal": "Moderates from both parties mentioned"
  }
}
```

#### Quality Metrics
```json
{
  "resolution_quality": {
    "overall_score": 0.73,
    "explicit_resolutions": 15,
    "ambiguous_references": 8,
    "unresolved": 3,
    "confidence_distribution": {
      "high": 15,
      "medium": 6,
      "low": 5
    }
  },
  "warnings": [
    "Internal party references may be ambiguous",
    "Emerging coalition patterns detected but not fully resolved"
  ]
}
```

### What You DON'T Get (But Might Want)

#### 1. Coalition Evolution Tracking
```
What happens:
Day 1: "We Republicans" vs "We Democrats"
Day 2: "We moderates from both parties"  
Day 3: "We in the compromise coalition"

What you get:
- Three separate entity sets
- No automatic linking showing evolution

What you need to do:
- Manual analysis of transformation
- Or use 'evolution' extension
```

#### 2. Power Dynamics
```
What happens:
Sen_A: "You're either with us or against us" (power move)
Sen_C: "We need a different approach" (resistance)

What you get:
- Entity identifications
- Frequency counts

What you're missing:
- Power assertion through group boundaries
- Resistance through redefinition
```

#### 3. Strategic Ambiguity
```
What happens:
Sen_D: "We moderates should talk"
(Intentionally vague about who counts as 'moderate')

What you get:
{"Moderates": 0.8, "Bipartisan_Group": 0.2}

What you're missing:
- Recognition that vagueness is strategic
- Allows multiple senators to project membership
```

### How to Work With These Limitations

#### 1. Supplement with Temporal Analysis
```python
# Manual tracking of coalition evolution
evolution_log = {
    "day_1": {
        "groups": ["Republicans", "Democrats"],
        "pattern": "partisan division"
    },
    "day_2": {
        "groups": ["Republicans", "Democrats", "Moderates"],
        "pattern": "cross-party emergence"
    },
    "day_3": {
        "groups": ["Compromise_Coalition", "Hardliners"],
        "pattern": "realignment"
    }
}
```

#### 2. Add Qualitative Coding
```python
# Code for power dynamics our system misses
power_dynamics = {
    "boundary_enforcement": [
        {"speaker": "Sen_A", "text": "with us or against us", "type": "ultimatum"}
    ],
    "boundary_crossing": [
        {"speaker": "Sen_D", "text": "moderates from both parties", "type": "bridge"}
    ]
}
```

#### 3. Track Strategic Ambiguity
```python
# Note where ambiguity seems intentional
strategic_ambiguity = [
    {
        "speaker": "Sen_D",
        "text": "we moderates",
        "likely_purpose": "allow multiple interpretations",
        "effect": "creates space for coalition"
    }
]
```

### Practical Workflow

#### Step 1: Run Entity Resolution
```python
resolver = BaseEntityResolver(config)
results = resolver.process_document(transcripts)
print(f"Quality score: {results.quality_metrics['overall_score']}")
```

#### Step 2: Check Suitability
```python
if results.suitability.score < 0.7:
    print("Warnings:", results.suitability.warnings)
    # Consider: Different approach? Manual analysis? Extensions?
```

#### Step 3: Identify Gaps
```python
# What patterns do you see that the system doesn't capture?
gaps = identify_gaps(results, transcripts)
```

#### Step 4: Supplement Analysis
```python
# Add manual coding for important patterns
supplemented = {
    "entity_resolution": results,
    "coalition_evolution": track_evolution_manually(),
    "power_dynamics": code_power_moves(),
    "strategic_communication": identify_strategic_ambiguity()
}
```

#### Step 5: Integrated Analysis
```python
# Combine automated and manual insights
final_analysis = integrate_analyses(supplemented)
```

### Reporting Your Results

#### Good Practice
```markdown
## Methods
Entity resolution was performed using KGAS balanced framework with:
- Speaker context tracking (5-unit window)
- Basic temporal markers
- Two-level aggregation

Quality score: 0.73 (acceptable for political discourse)

### Limitations
- Coalition evolution tracked manually due to framework limitations
- Power dynamics supplemented with qualitative coding
- Strategic ambiguity noted but not automatically detected

### Findings
Automated entity resolution identified 6 primary groups...
Manual analysis revealed coalition transformation pattern...
```

#### Bad Practice
```markdown
## Methods
Used AI to identify all groups in transcripts.

### Findings  
Found 6 groups. Republicans split into moderates.
```

### Decision Tree: Should You Use This Framework?

```
Is your document...
├── Contemporary (not historical)? → Yes
│   ├── Under 10k words? → Yes
│   │   ├── Clear group identities? → Yes
│   │   │   ├── Literal references? → Yes → USE IT ✓
│   │   │   └── Metaphorical? → No → Manual analysis
│   │   └── Fluid groups? → No → Consider alternatives
│   └── Over 10k words? → Marginal → Check quality metrics
└── Historical? → No → Need evolution extension or different approach
```

### Common Scenarios and Solutions

#### Scenario 1: "It worked great!"
- Document: Congressional debate
- Groups: Clear party identities
- Quality: 0.85
- Action: Use results with confidence

#### Scenario 2: "Partial success"
- Document: Town hall meeting
- Groups: Some clear, some emergent
- Quality: 0.70
- Action: Supplement with manual coding

#### Scenario 3: "Not suitable"
- Document: Literary dialogue
- Groups: Metaphorical, fluid
- Quality: 0.45
- Action: Use different approach entirely

### Tips from Real Usage

1. **Run on a sample first** - Check quality before processing everything
2. **Look for systematic patterns** - If certain speakers always ambiguous, note it
3. **Use speaker breakdown** - Often more insightful than overall counts
4. **Check contested entities** - These often signal important dynamics
5. **Don't over-interpret** - Frequency ≠ importance

### Integration with Your Research

#### For Publication
- Report quality metrics
- Acknowledge limitations explicitly
- Describe supplementary analysis
- Make data and code available

#### For Analysis
- Use as first pass to identify patterns
- Focus manual effort on ambiguous cases
- Look for what's missing as much as what's found
- Combine with other methods

### The Bottom Line

Our entity resolution framework is a tool, not magic. It works well for:
- Getting a quick overview of group references
- Processing large amounts of clear discourse
- Identifying patterns worth deeper analysis
- Saving time on obvious identifications

It requires supplementation for:
- Tracking group evolution
- Understanding power dynamics
- Catching strategic communication
- Handling metaphorical language

Use it as part of your toolkit, not your only tool.