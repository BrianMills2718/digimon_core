# Foundational Discourse Transformation Uncertainty

## Basic Transformations at the Core of KGAS

### 1. **Text → Argument Structure Extraction**
**Transformation**: Raw discourse → Toulmin argument networks

```python
# Example: "Vaccines are dangerous because my friend got sick after getting one, 
#          and the government can't be trusted anyway"

toulmin_extraction = {
    "claim": "Vaccines are dangerous",
    "warrant": "Personal anecdotes indicate systematic risk",
    "backing": "Government institutions are untrustworthy",
    "data": "Friend got sick after vaccination",
    "qualifier": "implied_certainty",
    "rebuttal": "not_acknowledged"
}

# Uncertainty in extraction:
extraction_confidence = {
    "claim_identification": 0.9,      # High confidence - explicitly stated
    "warrant_identification": 0.6,    # Moderate - implied connection
    "backing_identification": 0.7,    # Moderate - inferred from context
    "data_identification": 0.85,      # High - explicitly provided
    "qualifier_identification": 0.4,  # Low - not explicit
    "rebuttal_identification": 0.3    # Low - absence vs not mentioned
}
```

**Core Uncertainty**: How confident are we in correctly identifying argument components?

### 2. **Text → Sentiment-Attitude Object Mapping**
**Transformation**: Discourse → Person/Community sentiment toward specific concepts

```python
# Example: "I'm so tired of these pharma shills pushing their poison on our kids"

sentiment_extraction = {
    "attitude_objects": {
        "pharmaceutical_companies": {
            "sentiment": -0.9,
            "confidence": 0.85,
            "indicators": ["shills", "poison"]
        },
        "vaccines": {
            "sentiment": -0.8,
            "confidence": 0.75,
            "indicators": ["poison", "pushing"]
        },
        "children": {
            "sentiment": 0.7,  # Protective sentiment
            "confidence": 0.6,
            "indicators": ["our kids"]
        }
    }
}

# Uncertainty in mapping:
mapping_confidence = {
    "attitude_object_identification": 0.8,  # Did we identify the right targets?
    "sentiment_direction": 0.9,             # Clear negative sentiment
    "sentiment_intensity": 0.7,             # How strong is the sentiment?
    "sentiment_attribution": 0.6            # Is this the author's sentiment or reported?
}
```

**Core Uncertainty**: How confident are we that Person X has Sentiment Y toward Concept Z?

### 3. **Text → Belief Relationship Networks**
**Transformation**: Discourse → Belief dependency structures

```python
# Example: "Since the mainstream media lies about everything, 
#          we can't trust what they say about vaccine safety"

belief_network = {
    "beliefs": {
        "B1": "Mainstream media lies about everything",
        "B2": "Mainstream media reports on vaccine safety", 
        "B3": "We can't trust vaccine safety reports"
    },
    "relationships": {
        "B1 → B3": {
            "relationship_type": "causal_warrant",
            "strength": 0.8,
            "confidence": 0.7
        },
        "B2 + B1 → B3": {
            "relationship_type": "logical_inference", 
            "strength": 0.9,
            "confidence": 0.8
        }
    }
}

# Uncertainty in belief extraction:
belief_extraction_confidence = {
    "belief_identification": 0.8,      # Did we correctly identify discrete beliefs?
    "belief_relationship": 0.6,        # Did we correctly identify logical connections?
    "causal_vs_correlational": 0.5,    # Is this causation or correlation?
    "strength_assessment": 0.4         # How strong is the logical connection?
}
```

**Core Uncertainty**: How confident are we in the logical structure of someone's belief system?

### 4. **Individual → Community Aggregation**
**Transformation**: Individual discourse patterns → Community-level patterns

```python
# Example: Aggregating 1000 individual anti-vaccine posts into community beliefs

community_aggregation = {
    "individual_beliefs": [
        {"person": "user1", "vaccine_safety": -0.8, "confidence": 0.7},
        {"person": "user2", "vaccine_safety": -0.6, "confidence": 0.9},
        # ... 998 more
    ],
    "community_pattern": {
        "central_tendency": -0.7,
        "variance": 0.3,
        "consensus_level": 0.8,
        "outlier_proportion": 0.1
    }
}

# Uncertainty in aggregation:
aggregation_confidence = {
    "representativeness": 0.6,          # Do these users represent the community?
    "sampling_bias": 0.7,               # Are active posters representative?
    "temporal_stability": 0.5,          # Is this pattern stable over time?
    "consensus_measurement": 0.8        # Are we measuring consensus correctly?
}
```

**Core Uncertainty**: How confident are we that individual patterns reflect community patterns?

### 5. **Text → Cognitive/Emotional State Inference**
**Transformation**: Discourse → Psychological state indicators

```python
# Example: "I'm just so confused and scared about what to believe anymore"

psychological_inference = {
    "cognitive_state": {
        "uncertainty": 0.9,
        "confusion": 0.85,
        "cognitive_load": 0.7
    },
    "emotional_state": {
        "anxiety": 0.8,
        "fear": 0.75,
        "helplessness": 0.6
    },
    "confidence_in_inference": {
        "uncertainty_detection": 0.9,      # Explicitly stated
        "confusion_detection": 0.85,       # Explicitly stated  
        "anxiety_detection": 0.7,          # Inferred from "scared"
        "helplessness_detection": 0.5      # Inferred from context
    }
}
```

**Core Uncertainty**: How confident are we in inferring psychological states from discourse?

## What We Still Need to Resolve

### 1. **Argument Component Boundary Detection**
```python
# Problem: Where does one argument end and another begin?
text = "Vaccines cause autism because my son changed after his shots. 
        Plus, the CDC has been lying about this for years. 
        Also, natural immunity is better anyway."

# How many arguments? Where are the boundaries?
boundary_uncertainty = {
    "argument_count": [1, 3],           # Could be 1 complex or 3 simple arguments
    "component_attribution": 0.6,       # Which data goes with which claim?
    "implicit_vs_explicit": 0.4        # Are there unstated components?
}
```

### 2. **Attitude Object Granularity**
```python
# Problem: What's the right level of granularity for attitude objects?
text = "I hate Big Pharma but my doctor is okay"

attitude_granularity = {
    "pharmaceutical_industry": -0.8,    # General industry
    "pfizer": -0.7,                     # Specific company  
    "my_doctor": 0.3,                   # Individual practitioner
    "local_pharmacy": 0.1               # Local business
}

# Uncertainty: Which level of granularity captures the actual attitude?
granularity_confidence = 0.5  # Low confidence in correct level
```

### 3. **Implicit vs Explicit Belief Extraction**
```python
# Problem: How to handle unstated beliefs that underlie explicit statements?
text = "I'm not anti-vaccine, I'm just asking questions"

explicit_beliefs = {
    "vaccine_questioning": 0.8,
    "self_identification_as_non_antivax": 0.9
}

implicit_beliefs = {
    "vaccine_skepticism": 0.7,          # Inferred from "just asking questions"
    "mistrust_of_authorities": 0.6,     # Inferred from questioning frame
    "identity_protection": 0.8          # Inferred from explicit denial
}

# Uncertainty: Should we extract implicit beliefs? How confident are we?
implicit_extraction_confidence = 0.4  # Low confidence in implicit extraction
```

### 4. **Sentiment Context Dependency**
```python
# Problem: Sentiment toward same object varies by context
contexts = {
    "discussing_children": {
        "vaccines": -0.8,               # Negative when discussing kids
        "confidence": 0.7
    },
    "discussing_elderly": {
        "vaccines": -0.2,               # Less negative for elderly
        "confidence": 0.4
    },
    "discussing_covid": {
        "vaccines": -0.9,               # Very negative for COVID vaccines
        "confidence": 0.8
    }
}

# Uncertainty: Which context-specific sentiment is "true"?
context_resolution_confidence = 0.3   # Low confidence in resolution
```

### 5. **Temporal Belief Consistency**
```python
# Problem: Beliefs change over time - which time point represents "true" belief?
belief_timeline = {
    "2020-03": {"vaccine_hesitancy": 0.2, "confidence": 0.8},  # Pre-COVID
    "2021-06": {"vaccine_hesitancy": 0.7, "confidence": 0.9},  # During pandemic
    "2022-12": {"vaccine_hesitancy": 0.4, "confidence": 0.6}   # After experience
}

# Uncertainty: How to represent belief trajectory vs point-in-time belief?
temporal_representation_confidence = 0.4  # Low confidence in approach
```

## Core Unresolved Questions

1. **Granularity Selection**: What's the right level of detail for argument components, attitude objects, and belief networks?

2. **Implicit Content Handling**: Should we extract unstated beliefs/arguments? How confident can we be?

3. **Context Dependency Resolution**: How to handle context-dependent sentiment/beliefs?

4. **Temporal Representation**: How to represent changing beliefs over time?

5. **Aggregation Validity**: When is it valid to aggregate individual discourse into community patterns?

6. **Inference Depth**: How deep should we go in psychological state inference from text?

These are the foundational uncertainties that affect all downstream theoretical applications - we need to resolve confidence in these basic transformations before we can confidently apply social theories.