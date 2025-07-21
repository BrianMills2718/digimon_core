# Uncertainty Analysis Examples - Testing Our Approaches

## Example 1: CEO Coreference Resolution
**Analysis**: "The CEO announced layoffs. He said it was necessary."

### Transformation Chain
1. **Text → Entity Extraction**
   - Input: "The CEO announced layoffs"
   - Output: Entity("CEO", type="ROLE")
   - Uncertainty: Is this a specific person or generic role?

2. **Coreference Resolution**
   - Input: "He said it was necessary"
   - Transform: "He" → "CEO"
   - Uncertainty: Correct pronoun resolution?

3. **Context Enhancement**
   - Input: Entity("CEO") + document_context
   - Transform: "CEO" → "Tim Cook" (if Apple context detected)
   - Uncertainty: Right company? Right time period?

### Uncertainty Challenges Discovered
- **Cascading uncertainty**: If step 1 is uncertain, steps 2-3 compound it
- **Context dependency**: Same text has different confidence in different documents
- **Temporal validity**: "The CEO" meant different people at different times

### Proposed Approach
```python
{
    "entity": "Tim Cook",
    "confidence_interval": [0.3, 0.9],  # Wide range!
    "uncertainty_factors": {
        "role_ambiguity": 0.7,      # "CEO" is generic
        "coreference_confidence": 0.8,  # "He" likely refers to CEO
        "context_specificity": 0.5,  # Weak Apple indicators
        "temporal_ambiguity": 0.6    # No clear date markers
    },
    "reasoning": "Generic role reference with weak contextual indicators"
}
```

**Problem Discovered**: How do we handle when different uncertainty factors pull in opposite directions?

## Example 2: Sarcasm in Sentiment Analysis
**Analysis**: "Oh great, another 'brilliant' decision by management 🙄"

### Transformation Chain
1. **Surface Sentiment**
   - Words: "great", "brilliant" → Positive
   - Confidence: 0.9 (strong positive words)

2. **Sarcasm Detection**
   - Quotes around 'brilliant'
   - Eye-roll emoji
   - Context: "another" (implies pattern)
   - Sarcasm probability: 0.85

3. **Final Sentiment Assessment**
   - If sarcasm: Flip sentiment → Negative
   - If not sarcasm: Keep → Positive
   - But what if partially sarcastic?

### Uncertainty Challenges Discovered
- **Binary flip problem**: Sarcasm doesn't just flip sentiment, it modulates it
- **Partial sarcasm**: "Great product, 'amazing' customer service" (mixed)
- **Cultural context**: Sarcasm markers vary by culture/community

### Proposed Approach
```python
{
    "sentiment": {
        "positive": 0.15,  # Not zero! Some residual positivity
        "negative": 0.75,  # Strong but not complete negativity
        "neutral": 0.10    # Some hedging
    },
    "confidence_interval": [0.2, 0.4],  # Low confidence overall
    "modifiers": {
        "sarcasm_detected": 0.85,
        "sentiment_reversal_strength": 0.7,  # Not complete reversal
        "mixed_signals": True
    },
    "reasoning": "High sarcasm probability suggests negative sentiment, but sarcasm rarely creates pure negativity"
}
```

**Problem Discovered**: Our fuzzy categorization helps, but how do we aggregate mixed sentiments across many posts?

## Example 3: Multi-Community Member Classification
**Analysis**: User @PolicyWonk posts about vaccines, climate, and economics

### Transformation Chain
1. **Topic Detection per Post**
   - Post 1: "Vaccines save lives" → medical/vaccine topic (0.95)
   - Post 2: "Carbon tax now!" → climate policy (0.90)
   - Post 3: "MMT is the answer" → economics (0.85)

2. **Community Detection**
   - Medical community? Has vaccine posts
   - Climate community? Has climate posts
   - Economics community? Has econ posts
   - Political community? All are political topics

3. **Primary Community Assignment**
   - Need to pick one? Or allow multiple?
   - How to weight recent vs historical posts?

### Uncertainty Challenges Discovered
- **Multi-membership**: Real people belong to multiple communities
- **Community overlap**: Political/medical/climate communities intersect
- **Temporal dynamics**: Community membership changes over time
- **Sparse data**: 3 posts isn't enough for confident classification

### Proposed Approach
```python
{
    "community_memberships": {
        "political_general": {
            "membership_strength": 0.8,
            "confidence_interval": [0.6, 0.9],
            "evidence_posts": 3
        },
        "medical_policy": {
            "membership_strength": 0.4,
            "confidence_interval": [0.2, 0.6],
            "evidence_posts": 1
        },
        "climate_activism": {
            "membership_strength": 0.4,
            "confidence_interval": [0.2, 0.6],
            "evidence_posts": 1
        }
    },
    "primary_community": "political_general",
    "primary_confidence": [0.5, 0.8],
    "classification_uncertainty": {
        "data_sparsity": 0.8,  # Only 3 posts
        "community_overlap": 0.7,  # Communities not distinct
        "temporal_coverage": 0.3   # Unknown time span
    }
}
```

**Problem Discovered**: How do we handle hierarchical/overlapping communities?

## Example 4: Emotion Detection in Multilingual Text
**Analysis**: "I'm so happy! 😢 Ik ben verdrietig. #confused"

### Transformation Chain
1. **Language Detection**
   - English: "I'm so happy"
   - Emoji: 😢 (crying)
   - Dutch: "Ik ben verdrietig" (I am sad)
   - Hashtag: #confused

2. **Emotion Extraction per Component**
   - English text → Happy (0.9)
   - Emoji → Sad (0.95)
   - Dutch text → Sad (0.85 if translator confidence high)
   - Hashtag → Confused (0.8)

3. **Emotion Reconciliation**
   - Conflicting signals: happy vs sad
   - Meta-emotion: confusion about emotions
   - Cultural context: Emoji usage varies

### Uncertainty Challenges Discovered
- **Cross-lingual confidence**: LLM confidence varies by language
- **Multimodal fusion**: How to weight text vs emoji vs hashtags?
- **Meta-emotions**: Confusion about emotions is itself an emotion
- **Translation uncertainty**: Propagates through analysis

### Proposed Approach
```python
{
    "emotions": {
        "happy": {"strength": 0.3, "confidence": [0.1, 0.5]},
        "sad": {"strength": 0.6, "confidence": [0.4, 0.8]},
        "confused": {"strength": 0.8, "confidence": [0.6, 0.9]}
    },
    "dominant_emotion": "confused",
    "emotional_conflict": True,
    "uncertainty_sources": {
        "language_mixing": 0.7,
        "signal_conflict": 0.9,  # Text vs emoji mismatch
        "translation_confidence": 0.75,
        "meta_emotion_detected": True
    },
    "reasoning": "Mixed language input with conflicting emotional signals suggests genuine confusion"
}
```

**Problem Discovered**: Should uncertainty about emotions be treated differently than uncertainty about facts?

## Example 5: Relationship Extraction with Negation
**Analysis**: "Bill Gates is no longer the CEO of Microsoft"

### Transformation Chain
1. **Entity Recognition**
   - "Bill Gates" → PERSON (0.99)
   - "Microsoft" → ORG (0.99)
   - "CEO" → ROLE (0.95)

2. **Relationship Extraction**
   - Detect: CEO_OF relationship
   - Detect: Negation ("no longer")
   - Temporal: Past relationship, not current

3. **Knowledge Graph Update**
   - Add relationship with temporal bounds?
   - Mark as explicitly terminated?
   - Confidence in termination vs never existed?

### Uncertainty Challenges Discovered
- **Temporal uncertainty**: When did it end? "No longer" is vague
- **Negation scope**: Does negation apply to role or entire relationship?
- **State change vs non-existence**: Different uncertainty profiles

### Proposed Approach
```python
{
    "relationship": {
        "type": "CEO_OF",
        "subject": "Bill Gates",
        "object": "Microsoft",
        "status": "terminated",
        "temporal_bounds": {
            "start": {"date": "unknown", "confidence": [0.0, 0.3]},
            "end": {"date": "unknown", "confidence": [0.7, 0.95]}
        }
    },
    "extraction_confidence": [0.8, 0.95],
    "uncertainty_factors": {
        "negation_detected": 1.0,
        "negation_scope_confidence": 0.85,
        "temporal_precision": 0.1,  # Very imprecise
        "relationship_existed": 0.9  # High confidence it existed before
    }
}
```

**Problem Discovered**: How do we represent uncertainty about absence/negation?

## Example 6: Academic Theory Application
**Analysis**: Applying "Social Capital Theory" to Twitter network data

### Transformation Chain
1. **Theory Loading**
   - Load theory definition, concepts, relationships
   - Map theory concepts to extractable entities
   - Uncertainty: Theory interpretation correctness?

2. **Theory-Guided Extraction**
   - Extract "bridging capital" from retweet patterns
   - Extract "bonding capital" from reply patterns
   - Uncertainty: Operational definition validity?

3. **Theory-Based Analysis**
   - Calculate social capital metrics
   - Compare communities
   - Uncertainty: Theory applicability to Twitter?

### Uncertainty Challenges Discovered
- **Theory interpretation**: Academic theories have multiple interpretations
- **Operationalization validity**: Do retweets really measure bridging capital?
- **Domain transfer**: Theory developed for face-to-face may not apply to Twitter
- **Measurement validity**: Proxy measures introduce uncertainty

### Proposed Approach
```python
{
    "theory_application": {
        "theory": "Social Capital Theory (Putnam, 2000)",
        "confidence_interval": [0.4, 0.7],
        "validity_concerns": {
            "construct_validity": 0.6,  # Do we measure what we think?
            "external_validity": 0.5,   # Does theory apply to Twitter?
            "interpretation_consensus": 0.7  # Agreement on theory meaning
        }
    },
    "measurements": {
        "bridging_capital": {
            "value": 0.65,
            "confidence": [0.4, 0.8],
            "operationalization": "retweet_diversity",
            "validity_confidence": 0.6
        }
    },
    "uncertainty_propagation": {
        "theory_uncertainty": 0.5,
        "measurement_uncertainty": 0.3,
        "combined_uncertainty": 0.65  # How to combine?
    }
}
```

**Problem Discovered**: How do we handle uncertainty about theoretical constructs vs empirical measurements?

## Cross-Cutting Issues Discovered

### 1. **Uncertainty Composition**
- When multiple uncertainty types combine, how do we aggregate?
- Multiplication assumes independence (often false)
- Addition can exceed 1.0 (nonsensical)
- Need context-aware composition rules

### 2. **Uncertainty Types Interaction**
- Linguistic uncertainty (sarcasm, ambiguity)
- Factual uncertainty (which CEO, when)
- Theoretical uncertainty (construct validity)
- These interact in complex ways

### 3. **Confidence Calibration Across Domains**
- LLM confidence on persons/orgs (high) vs emotions (medium) vs theory (low)
- Need domain-specific calibration curves?

### 4. **Temporal Uncertainty**
- Many analyses have implicit temporal assumptions
- "Current CEO" vs "Historical CEO" have different uncertainty profiles
- How to represent time-varying confidence?

### 5. **Aggregation Challenges**
- Individual tweet sentiment → User sentiment → Community sentiment
- Each aggregation step modifies uncertainty
- Simple averaging loses information about distribution

### 6. **Missing Data Uncertainty**
- Sparse user profiles
- Incomplete conversation threads
- How to represent "uncertainty due to missing information"?

### 7. **Reference Resolution**
- Same entity, different confidence in different contexts
- "The CEO" vs "Tim Cook" vs "Apple's CEO"
- Context provides constraints that modify confidence

## Recommendations Based on Examples

### 1. **Structured Uncertainty Representation**
```python
@dataclass
class StructuredUncertainty:
    # Core uncertainty
    confidence_interval: Tuple[float, float]
    
    # Uncertainty sources (standardized)
    linguistic_uncertainty: float  # Ambiguity, sarcasm, etc.
    factual_uncertainty: float     # Entity resolution, facts
    temporal_uncertainty: float    # Time-sensitive aspects
    theoretical_uncertainty: float # Construct validity
    
    # Composition metadata
    aggregation_level: int  # 0=atomic, 1=first aggregation, etc.
    evidence_count: int     # How many data points support this
    
    # Reasoning (required)
    reasoning: str
    uncertainty_type: str  # "epistemic" or "aleatoric"
```

### 2. **Context-Aware Confidence Adjustment**
- Base confidence from LLM
- Adjust based on context strength
- Adjust based on domain-specific calibration
- Document each adjustment

### 3. **Uncertainty Propagation Rules**
- Define composition rules for each analysis type
- Track uncertainty amplification through chains
- Set thresholds for "too uncertain to use"

### 4. **Validation Requirements**
- Compare with human expert assessments
- Test calibration within specific domains
- Validate aggregation preserves information

These examples reveal the complexity of uncertainty in real analyses and the need for sophisticated, context-aware approaches.