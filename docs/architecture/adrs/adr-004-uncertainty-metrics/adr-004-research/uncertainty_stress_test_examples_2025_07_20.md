# Uncertainty Stress Test Examples - Revealing Design Issues

## Example 1: Dependent Uncertainty Composition
**Scenario**: Analyzing a political discussion where entity recognition affects sentiment analysis

### The Analysis Chain
```
Text: "The president's new policy is destroying small businesses"
```

1. **Entity Recognition**
   - "The president" → Could be Biden (0.7) or generic role (0.3)
   - Uncertainty: [0.5, 0.9] (ambiguous without more context)

2. **Policy Attribution**
   - If Biden: Likely refers to specific 2024 policy (0.8)
   - If generic: Could be any policy (0.2)
   - **Dependency**: Policy identification depends on entity resolution

3. **Sentiment Analysis**
   - "destroying" → Negative (0.95)
   - But sentiment TARGET depends on entity
   - If Biden: Sentiment toward Biden
   - If generic: Sentiment toward presidency as institution

### Problem Revealed: Dependent Uncertainty Propagation

Our current approach might do:
```python
entity_confidence = [0.5, 0.9]
policy_confidence = [0.3, 0.8]
sentiment_confidence = [0.9, 0.95]

# Naive combination (WRONG - assumes independence)
combined_confidence = [
    entity_confidence[0] * policy_confidence[0] * sentiment_confidence[0],
    entity_confidence[1] * policy_confidence[1] * sentiment_confidence[1]
]
# Result: [0.135, 0.684] - Too wide and potentially misleading
```

But these aren't independent! If we're confident about the entity, we should be more confident about the policy. The real calculation needs conditional probabilities:

```python
# More accurate but complex
if entity == "Biden":
    policy_confidence = [0.7, 0.9]  # Higher when entity is specific
else:
    policy_confidence = [0.1, 0.3]  # Lower when entity is generic

# But how do we represent this dependency in our ConfidenceScore?
```

**Issue**: Our ConfidenceScore doesn't capture conditional dependencies between analysis steps.

## Example 2: Temporal Validity Cascade
**Scenario**: Analyzing corporate leadership statements over time

### The Document Set
```
Doc1 (2020): "Our CEO announced record profits"
Doc2 (2022): "The CEO pivoted to focus on AI"
Doc3 (2024): "CEO's strategy proves successful"
```

### Temporal Uncertainty Challenge

1. **Same Role, Different People**
   - 2020 CEO: Bob Smith (left in 2021)
   - 2022-2024 CEO: Jane Doe
   - But all documents just say "CEO"

2. **Retroactive Analysis Confusion**
   - User asks: "What has the CEO said about AI?"
   - System finds all three documents
   - Incorrectly attributes 2020 statement to current CEO

3. **Confidence Decay Over Time**
   ```python
   # Current system might give equal confidence
   ceo_statements = [
       {"year": 2020, "statement": "record profits", "confidence": 0.9},
       {"year": 2022, "statement": "pivot to AI", "confidence": 0.9},
       {"year": 2024, "statement": "strategy successful", "confidence": 0.9}
   ]
   
   # But temporal validity should affect confidence
   # 2020 statement about "the CEO" has different validity in 2024 context
   ```

### Problem Revealed: No Temporal Confidence Model

```python
# What we need but don't have
@dataclass
class TemporalConfidence:
    point_in_time_confidence: float  # Confidence at document date
    current_validity_confidence: float  # Confidence for current analysis
    temporal_decay_function: Callable  # How confidence changes over time
    validity_window: Tuple[datetime, datetime]  # When is this claim valid?
```

**Issue**: ConfidenceScore is timeless but many claims have temporal validity windows.

## Example 3: Distribution Loss in Hierarchical Aggregation
**Scenario**: Community sentiment analysis with bimodal distribution

### The Data
1000 users discussing climate policy:
- 400 users: Strongly negative (confidence: 0.9 each)
- 100 users: Neutral (confidence: 0.5 each)
- 500 users: Strongly positive (confidence: 0.85 each)

### Current Aggregation Approach
```python
# Level 1: Individual sentiments
sentiments = [
    *[{"sentiment": -0.9, "confidence": 0.9} for _ in range(400)],
    *[{"sentiment": 0.0, "confidence": 0.5} for _ in range(100)],
    *[{"sentiment": 0.8, "confidence": 0.85} for _ in range(500)]
]

# Level 2: Community average (current approach)
avg_sentiment = sum(s["sentiment"] for s in sentiments) / len(sentiments)
avg_confidence = sum(s["confidence"] for s in sentiments) / len(sentiments)

# Result: sentiment=0.04, confidence=0.82
# This suggests "neutral community with high confidence"
# BUT THIS IS WRONG! The community is polarized, not neutral!
```

### The Real Distribution
```python
# What actually exists: bimodal distribution
# 40% strongly negative, 50% strongly positive, 10% neutral
# Average of 0.04 completely misrepresents this polarization
```

### Problem Revealed: Aggregation Destroys Critical Information

Our current ConfidenceScore + single value approach cannot represent:
- Bimodal or multimodal distributions
- Polarization vs consensus
- Subgroup disagreement

```python
# What we need but don't have
@dataclass
class DistributionPreservingAggregate:
    summary_statistic: float  # Mean/median/mode
    distribution_shape: str  # "unimodal", "bimodal", "uniform"
    subgroup_analysis: Dict[str, Any]  # Preserve subgroup info
    consensus_score: float  # How much agreement exists?
    confidence_interval: Tuple[float, float]  # For the aggregate
    
    # Critical: this is fundamentally different information than just mean + confidence
```

**Issue**: Single-value + confidence destroys distribution information needed for correct interpretation.

## Example 4: Cascading Missing Data Uncertainty
**Scenario**: Social network analysis with incomplete data

### The Network
- 1000 users identified
- 600 users: Full tweet history available
- 300 users: Partial history (API limits)
- 100 users: Only retweets visible (private accounts)

### Analysis Task: "Identify opinion leaders in the network"

1. **Influence Metrics**
   ```python
   # For users with full data
   user_A = {
       "follower_count": 5000,
       "retweet_rate": 0.3,
       "mention_influence": 0.7,
       "confidence": 0.9  # High confidence, full data
   }
   
   # For users with partial data
   user_B = {
       "follower_count": "unknown",  # Private
       "retweet_rate": 0.5,  # Based on visible retweets only
       "mention_influence": "unknown",
       "confidence": 0.3  # Low confidence, missing data
   }
   ```

2. **Network-Level Problem**
   ```python
   # If influential users are disproportionately private
   # Our "top influencers" list might be completely wrong
   # But how do we represent "confidence in the absence"?
   ```

### Problem Revealed: Missing Data Isn't Just Low Confidence

```python
# Current approach
missing_data_confidence = 0.0  # Treat as no confidence

# But this is wrong! We need to distinguish:
# 1. "We measured and found no influence" (confidence: 0.9, influence: 0.1)
# 2. "We couldn't measure influence" (confidence: N/A, influence: unknown)
# 3. "We partially measured" (confidence: 0.3, influence: 0.5±0.3)

# What we need
@dataclass
class DataCompleteness:
    measurement_coverage: float  # What % of data did we see?
    missing_pattern: str  # "random", "systematic", "biased"
    missingness_impact: float  # How much could missing data change results?
    confidence_type: str  # "measured", "imputed", "unknown"
```

**Issue**: Can't distinguish "measured absence" from "unmeasured unknown".

## Example 5: Context-Dependent Entity Confidence
**Scenario**: Same entity, radically different confidence based on context

### The Texts
```
Text A (Tech blog): "Apple's latest innovation changes everything"
Text B (Grocery list): "Buy apple, banana, orange"
Text C (News): "Apple faces lawsuit over privacy"
Text D (Recipe): "Apple pie requires 6 apples"
```

### Entity Recognition Challenge

All contain "apple/Apple" but context radically changes confidence:

```python
# Current system might do:
entity_extractions = [
    {"text": "Apple", "type": "ORG", "confidence": 0.9},  # Text A
    {"text": "apple", "type": "FOOD", "confidence": 0.9},  # Text B
    {"text": "Apple", "type": "ORG", "confidence": 0.9},  # Text C
    {"text": "apple", "type": "FOOD", "confidence": 0.9},  # Text D
]

# But this misses the ambiguity in isolation
# "Apple" alone could be ORG or FOOD
# Context CREATES the confidence, it doesn't just modify it
```

### Cross-Document Problem

When analyzing across documents:
```python
# User query: "Extract all mentions of Apple"
# Should we include the fruit references?
# How do we handle context-dependent disambiguation?

# Current: Binary decision per instance
# Reality: Probability distribution that shifts with context
```

### Problem Revealed: Context Doesn't Just Modify Confidence, It Creates It

```python
# What we need
@dataclass
class ContextualConfidence:
    base_ambiguity: Dict[str, float]  # {"ORG": 0.5, "FOOD": 0.5} without context
    context_modifiers: Dict[str, Dict[str, float]]  # How each context type affects probs
    final_distribution: Dict[str, float]  # After context applied
    context_strength: float  # How definitive is the context?
    
    def apply_context(self, context_type: str):
        # Context dramatically reshapes probability distribution
        pass
```

**Issue**: Our confidence model assumes entity identity is fixed and context just adjusts confidence, but context actually determines identity.

## Synthesis: Fundamental Issues Revealed

### 1. **Independence Assumption**
Our confidence propagation assumes independence, but most analytical steps are deeply dependent.

### 2. **Temporal Blindness**
ConfidenceScore has no temporal dimension, but many claims are time-bound.

### 3. **Distribution Destruction**
Single value + confidence can't represent multimodal distributions or polarization.

### 4. **Missing vs Measured**
Can't distinguish "we measured X and found nothing" from "we couldn't measure X".

### 5. **Context Creates Identity**
Context doesn't just modify confidence in an entity; it determines what the entity IS.

## Proposed Framework Extensions

### 1. **Conditional Confidence Networks**
```python
@dataclass
class ConditionalConfidence:
    base_confidence: ConfidenceScore
    dependencies: Dict[str, Callable]  # Other variables this depends on
    joint_distribution: Optional[Any]  # For dependent variables
```

### 2. **Temporal Confidence**
```python
@dataclass 
class TemporalConfidenceScore(ConfidenceScore):
    valid_from: datetime
    valid_until: Optional[datetime]
    temporal_decay: Callable
    assessment_time: datetime
```

### 3. **Distribution-Preserving Aggregates**
```python
@dataclass
class DistributionAwareAggregate:
    summary: float
    full_distribution: Union[List[float], Callable]
    shape_metrics: Dict[str, float]  # skewness, kurtosis, modality
    subgroup_breakdowns: Dict[str, Any]
```

### 4. **Missing Data Representation**
```python
@dataclass
class MeasurementCompleteness:
    value: Optional[float]
    measurement_type: Literal["measured", "imputed", "absent", "unknown"]
    coverage: float  # What fraction of needed data was available
    confidence_given_coverage: ConfidenceScore
```

### 5. **Contextual Identity**
```python
@dataclass
class ContextualEntity:
    surface_form: str
    possible_identities: Dict[str, float]  # Distribution over possibilities
    context_embedding: Any  # Representation of context
    resolved_identity: Optional[str]
    resolution_confidence: ConfidenceScore
```

These examples reveal that our current uncertainty framework, while sophisticated, has fundamental limitations when dealing with complex, real-world analytical scenarios.