# Configurable Uncertainty Framework

## Uncertainty Configuration Types

### 1. **Dependency Handling Configuration**
```python
@dataclass
class DependencyConfig:
    mode: Literal["independent", "conditional", "full_bayesian"]
    
    # Independent (fastest, least accurate)
    # - Multiply confidence scores
    # - Ignore dependencies
    
    # Conditional (balanced)
    # - Track direct dependencies between adjacent steps
    # - Use conditional probability for immediate predecessors
    
    # Full Bayesian (slowest, most accurate)  
    # - Model full dependency network
    # - Joint probability distributions
```

**Recommendation**: Default to "conditional" - captures most dependencies without computational explosion.

### 2. **Temporal Handling Configuration**
```python
@dataclass  
class TemporalConfig:
    enabled: bool = True
    decay_function: Literal["linear", "exponential", "step", "none"]
    validity_window_tracking: bool = True
    
    # Linear: confidence decreases steadily over time
    # Exponential: rapid decay initially, then slower
    # Step: confidence drops at specific time boundaries
    # None: no temporal decay
```

**Recommendation**: Enable with "exponential" decay - most claims become less reliable over time at decreasing rates.

### 3. **Aggregation Preservation Configuration**
```python
@dataclass
class AggregationConfig:
    preserve_distribution: bool = True
    max_subgroups: int = 10  # Computational limit
    polarization_detection: bool = True
    consensus_metrics: bool = True
    
    # When preserve_distribution=True:
    # - Keep full distributions up to max_subgroups
    # - Calculate modality, skewness, polarization indices
    # - Preserve minority opinions
```

**Recommendation**: Always preserve_distribution=True - critical information loss otherwise.

### 4. **Missing Data Handling Configuration**
```python
@dataclass
class MissingDataConfig:
    distinguish_absence_types: bool = True
    imputation_method: Literal["none", "mean", "model_based", "bounds"]
    missing_data_impact_tracking: bool = True
    
    # distinguish_absence_types:
    # - "measured_absent" vs "unmeasured" vs "partially_observed"
    
    # imputation_method:
    # - none: don't fill missing values
    # - bounds: provide min/max possible range
```

**Recommendation**: distinguish_absence_types=True, imputation_method="bounds" - preserves uncertainty about missing data.

### 5. **Context Sensitivity Configuration**
```python
@dataclass
class ContextConfig:
    dynamic_entity_resolution: bool = True
    context_window_size: int = 500  # tokens
    cross_document_context: bool = False  # Expensive
    context_confidence_adjustment: bool = True
```

**Recommendation**: Enable dynamic_entity_resolution and context_confidence_adjustment - essential for disambiguation.

## Examples of Partially True and Time-Dependent Atoms

### Partially True Atoms

**Example 1: Sentiment Atom**
```python
# Instead of binary true/false
atom_binary = {
    "claim": "Tweet expresses positive sentiment",
    "truth_value": True,  # Binary - loses information
    "confidence": 0.7
}

# Partially true representation
atom_partial = {
    "claim": "Tweet expresses positive sentiment", 
    "truth_distribution": {
        "positive": 0.6,
        "negative": 0.3, 
        "neutral": 0.1
    },
    "confidence": 0.8,  # Confidence in the distribution itself
    "reasoning": "Positive words but sarcastic tone indicators"
}
```

**Example 2: Community Membership Atom**
```python
# Binary version loses multimodal reality
atom_binary = {
    "claim": "User belongs to climate activist community",
    "truth_value": True,
    "confidence": 0.5  # Low because they also post about other topics
}

# Partial truth captures multiple memberships
atom_partial = {
    "claim": "User community affiliations",
    "truth_distribution": {
        "climate_activist": 0.4,
        "political_general": 0.8,
        "science_enthusiast": 0.3,
        "technology": 0.2
    },
    "confidence": 0.85,  # High confidence in the distribution
    "reasoning": "Posts span multiple topics with political/climate overlap"
}
```

### Time-Dependent Atoms

**Example 1: Role Attribution Atom**
```python
# Time-independent version loses critical information
atom_static = {
    "claim": "Tim Cook is CEO of Apple",
    "truth_value": True,
    "confidence": 0.95
}

# Time-dependent version
atom_temporal = {
    "claim": "Tim Cook is CEO of Apple",
    "temporal_truth": {
        "2011-08-24": {"truth": 1.0, "confidence": 0.99},  # Started
        "2020-01-01": {"truth": 1.0, "confidence": 0.95},  # Ongoing
        "2025-01-01": {"truth": 0.8, "confidence": 0.7},   # Likely but uncertain
        "2030-01-01": {"truth": 0.3, "confidence": 0.5}    # Very uncertain
    },
    "validity_window": ("2011-08-24", None),  # Open-ended
    "assessment_date": "2025-01-01"
}
```

**Example 2: Policy Position Atom**
```python
atom_temporal = {
    "claim": "Biden supports student loan forgiveness",
    "temporal_truth": {
        "2019-01-01": {"truth": 0.3, "confidence": 0.8},  # Campaign evolution
        "2020-10-01": {"truth": 0.7, "confidence": 0.9},  # Campaign promise
        "2021-01-20": {"truth": 0.9, "confidence": 0.95}, # Presidential policy
        "2023-06-30": {"truth": 0.6, "confidence": 0.8}   # After court ruling
    },
    "change_points": ["2020-10-01", "2021-01-20", "2023-06-30"],
    "reasoning": "Position evolved during campaign and faced legal challenges"
}
```

## 80/20 Recommendations by Impact

### **Tier 1: Essential (80% of value)**

1. **Aggregation Distribution Preservation** - Highest impact
   - Prevents "polarization appears neutral" errors
   - Critical for community analysis
   - Relatively straightforward to implement

2. **Context-Dependent Entity Resolution** - High impact  
   - Solves "Apple company vs fruit" confusion
   - Essential for multi-domain analysis
   - Moderate complexity

3. **Missing Data Type Distinction** - High impact
   - Prevents "absence = low confidence" errors
   - Critical for network analysis with sparse data
   - Low complexity addition

### **Tier 2: Important (15% additional value)**

4. **Basic Dependency Tracking** - Medium impact
   - Improves confidence propagation accuracy
   - Useful for debugging analysis chains
   - Medium complexity

5. **Temporal Validity Windows** - Medium impact  
   - Prevents anachronistic claims
   - Important for longitudinal studies
   - Medium complexity

### **Tier 3: Advanced (5% additional value)**

6. **Full Bayesian Dependency Networks** - Low marginal impact
   - Theoretically optimal but computationally expensive
   - Diminishing returns over conditional tracking
   - High complexity

## Registry-Based Configuration Approach

```python
@dataclass
class UncertaintyRegistry:
    aggregation_methods: Dict[str, Callable] = field(default_factory=dict)
    propagation_rules: Dict[str, Callable] = field(default_factory=dict)
    temporal_models: Dict[str, Callable] = field(default_factory=dict)
    
    def register_aggregation(self, name: str, method: Callable, 
                           complexity: int, use_cases: List[str]):
        """Register aggregation technique with metadata"""
        self.aggregation_methods[name] = {
            "method": method,
            "complexity": complexity,  # 1-5 scale
            "use_cases": use_cases,
            "preserves_distribution": bool,
            "handles_polarization": bool
        }
    
    def recommend_configuration(self, analysis_type: str, 
                              data_characteristics: Dict,
                              performance_requirements: Dict) -> UncertaintyConfig:
        """LLM-powered configuration recommendation"""
        # Let LLM assess:
        # - Analysis type (sentiment, network, temporal)
        # - Data characteristics (size, sparsity, domains)  
        # - Performance requirements (speed vs accuracy)
        # Return optimized configuration
        pass

# Example registrations
registry.register_aggregation(
    "distribution_preserving_mean",
    method=preserve_distribution_aggregate,
    complexity=3,
    use_cases=["community_analysis", "sentiment_aggregation"],
    preserves_distribution=True,
    handles_polarization=True
)

registry.register_aggregation(
    "simple_average", 
    method=numpy.mean,
    complexity=1,
    use_cases=["quick_summaries"],
    preserves_distribution=False,
    handles_polarization=False
)
```

## LLM Configuration Intelligence

Instead of hardcoding rules, let the LLM assess:

```python
def llm_configure_uncertainty(analysis_request: AnalysisRequest) -> UncertaintyConfig:
    """
    LLM prompt: Given this analysis type, data characteristics, and research goals,
    recommend uncertainty configuration that balances accuracy with computational cost.
    
    Consider:
    - Will polarization matter for this analysis?
    - Are temporal factors important?
    - How sparse is the data?
    - What's the accuracy vs speed preference?
    """
    prompt = f"""
    Analysis: {analysis_request.description}
    Data: {analysis_request.data_summary}
    Goals: {analysis_request.research_questions}
    
    Recommend uncertainty configuration focusing on what will most impact research validity.
    """
    # LLM returns structured configuration
```

This approach puts the intelligence in the LLM's assessment of trade-offs rather than hardcoded heuristics, which aligns perfectly with your thesis approach of leveraging LLM capabilities for complex analytical decisions.