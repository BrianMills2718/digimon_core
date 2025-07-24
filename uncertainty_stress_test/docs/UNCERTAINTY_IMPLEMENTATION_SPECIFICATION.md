# KGAS Uncertainty Implementation Specification

## Executive Summary

This document provides concrete mathematical formulas, algorithms, and implementation details for the KGAS uncertainty framework, filling the gaps identified in our documentation analysis. It serves as the definitive technical blueprint for implementing the complete uncertainty system.

## Architecture Overview

### Four-Layer Uncertainty Architecture

1. **Contextual Entity Resolution Layer**: Initial confidence from model outputs
2. **Temporal Knowledge Graph Layer**: Cross-modal uncertainty translation
3. **Bayesian Pipeline Layer**: Evidence aggregation and belief updates
4. **Distribution Preservation Layer**: Final uncertainty quantification

## Mathematical Specifications

### 1. Initial Confidence Calculation

#### 1.1 Named Entity Recognition (NER) Confidence

```python
def calculate_ner_confidence(model_logits, context_factors):
    """
    Calculate initial confidence for NER predictions
    
    Args:
        model_logits: Raw model output logits [batch_size, seq_len, num_labels]
        context_factors: Dict with contextual adjustment factors
    
    Returns:
        confidence_score: Float between 0 and 1
    """
    
    # Base confidence from softmax probability
    probabilities = softmax(model_logits, dim=-1)
    max_prob = torch.max(probabilities, dim=-1)[0]
    
    # Entropy-based uncertainty
    entropy = -torch.sum(probabilities * torch.log(probabilities + 1e-9), dim=-1)
    max_entropy = torch.log(torch.tensor(probabilities.shape[-1]))
    normalized_entropy = entropy / max_entropy
    
    # Uncertainty from entropy (lower is more confident)
    entropy_confidence = 1.0 - normalized_entropy
    
    # Combine probability and entropy
    base_confidence = 0.7 * max_prob + 0.3 * entropy_confidence
    
    # Contextual adjustments
    context_multiplier = 1.0
    
    # Domain familiarity adjustment
    if 'domain_familiarity' in context_factors:
        familiarity = context_factors['domain_familiarity']  # 0-1 scale
        context_multiplier *= (0.8 + 0.2 * familiarity)
    
    # Text quality adjustment
    if 'text_quality' in context_factors:
        quality = context_factors['text_quality']  # 0-1 scale
        context_multiplier *= (0.9 + 0.1 * quality)
    
    # Training data similarity
    if 'similarity_to_training' in context_factors:
        similarity = context_factors['similarity_to_training']  # 0-1 scale
        context_multiplier *= (0.85 + 0.15 * similarity)
    
    # Final confidence with bounds checking
    final_confidence = base_confidence * context_multiplier
    return max(0.1, min(0.95, final_confidence))  # Bound between 0.1 and 0.95
```

#### 1.2 Relation Extraction Confidence

```python
def calculate_relation_confidence(relation_logits, entity_confidences, context):
    """
    Calculate confidence for relation extraction
    
    Args:
        relation_logits: Model output for relation classification
        entity_confidences: Confidence scores for involved entities
        context: Contextual information
    """
    
    # Base relation confidence
    relation_probs = softmax(relation_logits)
    max_relation_prob = torch.max(relation_probs)
    
    # Entity confidence propagation (geometric mean)
    entity_conf_product = 1.0
    for conf in entity_confidences:
        entity_conf_product *= conf
    entity_contribution = entity_conf_product ** (1.0 / len(entity_confidences))
    
    # Distance penalty (closer entities are more reliable)
    if 'entity_distance' in context:
        distance = context['entity_distance']
        distance_penalty = 1.0 / (1.0 + 0.1 * distance)
    else:
        distance_penalty = 1.0
    
    # Combine all factors
    relation_confidence = (
        0.6 * max_relation_prob +
        0.3 * entity_contribution +
        0.1 * distance_penalty
    )
    
    return max(0.05, min(0.9, relation_confidence))
```

### 2. Bayesian Aggregation Formulas

#### 2.1 Evidence Weight Calculation

```python
def calculate_evidence_weight(evidence_metadata):
    """
    Calculate weight for a piece of evidence based on source reliability,
    recency, and other factors.
    """
    
    base_weight = 1.0
    
    # Source reliability (0-1 scale)
    if 'source_reliability' in evidence_metadata:
        reliability = evidence_metadata['source_reliability']
        base_weight *= (0.5 + 0.5 * reliability)
    
    # Temporal decay (newer evidence weighted higher)
    if 'timestamp' in evidence_metadata:
        age_days = (datetime.now() - evidence_metadata['timestamp']).days
        decay_factor = np.exp(-age_days / 365.0)  # Half-life of 1 year
        base_weight *= (0.3 + 0.7 * decay_factor)
    
    # Evidence type multiplier
    evidence_type_weights = {
        'primary_source': 1.0,
        'peer_reviewed': 0.9,
        'secondary_source': 0.7,
        'tertiary_source': 0.5,
        'opinion': 0.3
    }
    
    if 'evidence_type' in evidence_metadata:
        type_weight = evidence_type_weights.get(
            evidence_metadata['evidence_type'], 0.6
        )
        base_weight *= type_weight
    
    return base_weight
```

#### 2.2 Bayesian Update Implementation

```python
def bayesian_update(prior_belief, evidence_likelihood, evidence_weight):
    """
    Perform Bayesian update with weighted evidence
    
    Args:
        prior_belief: Prior probability (0-1)
        evidence_likelihood: Likelihood of evidence given hypothesis (0-1)
        evidence_weight: Weight of the evidence (0-∞)
    
    Returns:
        posterior_belief: Updated probability
    """
    
    # Convert to log odds for numerical stability
    def prob_to_log_odds(p):
        return np.log(p / (1 - p + 1e-9))
    
    def log_odds_to_prob(log_odds):
        return 1 / (1 + np.exp(-log_odds))
    
    # Prior in log odds
    prior_log_odds = prob_to_log_odds(prior_belief)
    
    # Evidence contribution (weighted)
    evidence_log_odds = prob_to_log_odds(evidence_likelihood)
    weighted_evidence = evidence_weight * evidence_log_odds
    
    # Bayesian update in log odds space
    posterior_log_odds = prior_log_odds + weighted_evidence
    
    # Convert back to probability
    posterior_belief = log_odds_to_prob(posterior_log_odds)
    
    return max(0.01, min(0.99, posterior_belief))
```

### 3. Cross-Modal Uncertainty Translation

#### 3.1 Graph to Vector Space Translation

```python
def translate_graph_to_vector_uncertainty(graph_confidence, embedding_confidence, translation_context):
    """
    Translate uncertainty from knowledge graph to vector embedding space
    
    Args:
        graph_confidence: Confidence in graph structure/relations
        embedding_confidence: Confidence in vector representations
        translation_context: Context about the translation process
    """
    
    # Base translation uses harmonic mean (conservative)
    base_translated = 2 * graph_confidence * embedding_confidence / (
        graph_confidence + embedding_confidence + 1e-9
    )
    
    # Translation quality adjustment
    translation_quality = translation_context.get('quality', 0.8)
    quality_adjustment = 0.8 + 0.2 * translation_quality
    
    # Dimensionality consistency check
    if 'dimensionality_match' in translation_context:
        dim_match = translation_context['dimensionality_match']
        dim_adjustment = 0.9 + 0.1 * dim_match
    else:
        dim_adjustment = 1.0
    
    # Semantic preservation check
    if 'semantic_preservation' in translation_context:
        semantic = translation_context['semantic_preservation']
        semantic_adjustment = 0.85 + 0.15 * semantic
    else:
        semantic_adjustment = 1.0
    
    # Final translated confidence
    translated_confidence = (
        base_translated * 
        quality_adjustment * 
        dim_adjustment * 
        semantic_adjustment
    )
    
    return max(0.05, min(0.9, translated_confidence))
```

### 4. CERQual Assessment Implementation

#### 4.1 CERQual Dimensions

```python
class CERQualDimensions:
    """
    Implementation of CERQual (Confidence in Evidence from Reviews) framework
    """
    
    @staticmethod
    def assess_methodological_limitations(study_metadata):
        """Assess methodological quality (0-1 scale, 1 = highest quality)"""
        
        score = 1.0
        
        # Sample size adequacy
        if 'sample_size' in study_metadata:
            n = study_metadata['sample_size']
            if n < 30:
                score *= 0.6
            elif n < 100:
                score *= 0.8
            elif n < 500:
                score *= 0.9
            # else: score *= 1.0 (adequate)
        
        # Study design quality
        design_scores = {
            'randomized_controlled': 1.0,
            'cohort': 0.85,
            'case_control': 0.75,
            'cross_sectional': 0.65,
            'case_series': 0.5,
            'case_report': 0.3
        }
        
        if 'study_design' in study_metadata:
            design = study_metadata['study_design']
            score *= design_scores.get(design, 0.7)
        
        # Bias assessment
        if 'bias_risk' in study_metadata:
            bias_risk = study_metadata['bias_risk']  # 'low', 'moderate', 'high'
            bias_multipliers = {'low': 1.0, 'moderate': 0.8, 'high': 0.5}
            score *= bias_multipliers.get(bias_risk, 0.7)
        
        return max(0.1, min(1.0, score))
    
    @staticmethod
    def assess_relevance(study_metadata, research_question):
        """Assess how relevant the study is to the research question"""
        
        # Population relevance
        pop_relevance = study_metadata.get('population_relevance', 0.8)
        
        # Intervention/exposure relevance
        intervention_relevance = study_metadata.get('intervention_relevance', 0.8)
        
        # Outcome relevance
        outcome_relevance = study_metadata.get('outcome_relevance', 0.8)
        
        # Setting relevance
        setting_relevance = study_metadata.get('setting_relevance', 0.8)
        
        # Weighted average
        relevance_score = (
            0.3 * pop_relevance +
            0.3 * intervention_relevance +
            0.25 * outcome_relevance +
            0.15 * setting_relevance
        )
        
        return max(0.1, min(1.0, relevance_score))
    
    @staticmethod
    def assess_coherence(evidence_set):
        """Assess coherence across multiple studies"""
        
        if len(evidence_set) < 2:
            return 0.5  # Single study - moderate coherence by default
        
        # Calculate effect size consistency
        effect_sizes = [study.get('effect_size', 0) for study in evidence_set]
        if len(effect_sizes) > 1:
            effect_std = np.std(effect_sizes)
            effect_mean = np.mean(np.abs(effect_sizes))
            
            if effect_mean > 0:
                consistency = 1 - min(1.0, effect_std / effect_mean)
            else:
                consistency = 0.5
        else:
            consistency = 0.5
        
        # Direction consistency
        directions = [1 if study.get('effect_size', 0) > 0 else -1 
                     for study in evidence_set]
        direction_consistency = abs(sum(directions)) / len(directions)
        
        # Combine measures
        coherence = 0.6 * consistency + 0.4 * direction_consistency
        
        return max(0.1, min(1.0, coherence))
    
    @staticmethod
    def assess_adequacy(evidence_set, effect_size_threshold=0.1):
        """Assess whether there's adequate data to support conclusions"""
        
        # Number of studies
        n_studies = len(evidence_set)
        study_adequacy = min(1.0, n_studies / 5)  # Ideal: 5+ studies
        
        # Total sample size
        total_n = sum(study.get('sample_size', 0) for study in evidence_set)
        sample_adequacy = min(1.0, total_n / 1000)  # Ideal: 1000+ total participants
        
        # Effect size detectability
        mean_effect = np.mean([abs(study.get('effect_size', 0)) for study in evidence_set])
        effect_adequacy = 1.0 if mean_effect >= effect_size_threshold else mean_effect / effect_size_threshold
        
        # Weighted average
        adequacy = (
            0.4 * study_adequacy +
            0.4 * sample_adequacy +
            0.2 * effect_adequacy
        )
        
        return max(0.1, min(1.0, adequacy))
```

#### 4.2 Overall CERQual Assessment

```python
def calculate_cerqual_confidence(evidence_set, research_question):
    """
    Calculate overall CERQual confidence assessment
    
    Returns confidence level: 'high', 'moderate', 'low', 'very_low'
    """
    
    # Assess each dimension
    methodology_scores = []
    relevance_scores = []
    
    for study in evidence_set:
        methodology_scores.append(
            CERQualDimensions.assess_methodological_limitations(study)
        )
        relevance_scores.append(
            CERQualDimensions.assess_relevance(study, research_question)
        )
    
    # Average across studies
    avg_methodology = np.mean(methodology_scores)
    avg_relevance = np.mean(relevance_scores)
    
    # Assess coherence and adequacy across the set
    coherence = CERQualDimensions.assess_coherence(evidence_set)
    adequacy = CERQualDimensions.assess_adequacy(evidence_set)
    
    # Calculate overall score (weighted average)
    overall_score = (
        0.3 * avg_methodology +
        0.25 * avg_relevance +
        0.25 * coherence +
        0.2 * adequacy
    )
    
    # Convert to categorical confidence level
    if overall_score >= 0.8:
        confidence_level = 'high'
        numeric_confidence = 0.9
    elif overall_score >= 0.6:
        confidence_level = 'moderate'
        numeric_confidence = 0.75
    elif overall_score >= 0.4:
        confidence_level = 'low'
        numeric_confidence = 0.5
    else:
        confidence_level = 'very_low'
        numeric_confidence = 0.25
    
    return {
        'confidence_level': confidence_level,
        'numeric_confidence': numeric_confidence,
        'overall_score': overall_score,
        'dimension_scores': {
            'methodology': avg_methodology,
            'relevance': avg_relevance,
            'coherence': coherence,
            'adequacy': adequacy
        }
    }
```

### 5. Temporal Decay Implementation

```python
def calculate_temporal_decay(base_confidence, timestamp, decay_params):
    """
    Calculate how confidence decays over time
    
    Args:
        base_confidence: Initial confidence score
        timestamp: When the information was created
        decay_params: Parameters controlling decay behavior
    """
    
    age_days = (datetime.now() - timestamp).days
    
    # Different decay functions for different types of information
    decay_type = decay_params.get('type', 'exponential')
    
    if decay_type == 'exponential':
        # Exponential decay with configurable half-life
        half_life_days = decay_params.get('half_life_days', 365)
        decay_factor = 0.5 ** (age_days / half_life_days)
        
    elif decay_type == 'linear':
        # Linear decay to minimum
        decay_days = decay_params.get('decay_days', 1095)  # 3 years
        min_confidence = decay_params.get('min_confidence', 0.1)
        
        if age_days >= decay_days:
            decay_factor = min_confidence / base_confidence
        else:
            decay_factor = 1 - (1 - min_confidence/base_confidence) * (age_days / decay_days)
            
    elif decay_type == 'step':
        # Step function decay
        thresholds = decay_params.get('thresholds', [
            (30, 1.0),    # 30 days: no decay
            (365, 0.8),   # 1 year: 80%
            (1095, 0.5),  # 3 years: 50%
            (float('inf'), 0.2)  # Beyond: 20%
        ])
        
        decay_factor = 0.2  # Default
        for threshold_days, factor in thresholds:
            if age_days <= threshold_days:
                decay_factor = factor
                break
    
    else:
        # No decay
        decay_factor = 1.0
    
    # Apply domain-specific modifiers
    if 'domain_stability' in decay_params:
        # More stable domains decay slower
        stability = decay_params['domain_stability']  # 0-1
        decay_factor = decay_factor ** (1 - 0.5 * stability)
    
    decayed_confidence = base_confidence * decay_factor
    return max(0.01, min(0.99, decayed_confidence))
```

### 6. Meta-Uncertainty Quantification

```python
def calculate_meta_uncertainty(confidence_estimates, estimation_context):
    """
    Calculate uncertainty about the uncertainty estimate itself
    
    Args:
        confidence_estimates: List of confidence estimates from different sources
        estimation_context: Context about how estimates were made
    """
    
    if len(confidence_estimates) < 2:
        # Single estimate: high meta-uncertainty
        return 0.7
    
    # Dispersion-based meta-uncertainty
    estimates_array = np.array(confidence_estimates)
    dispersion = np.std(estimates_array)
    
    # Higher dispersion = higher meta-uncertainty
    dispersion_component = min(0.5, dispersion * 2)
    
    # Model agreement component
    agreement = 1 - (np.max(estimates_array) - np.min(estimates_array))
    agreement_component = 0.3 * (1 - agreement)
    
    # Estimation quality component
    quality_factors = estimation_context.get('quality_factors', {})
    
    # Data quality
    data_quality = quality_factors.get('data_quality', 0.7)
    data_component = 0.2 * (1 - data_quality)
    
    # Model calibration
    model_calibration = quality_factors.get('model_calibration', 0.7)
    calibration_component = 0.2 * (1 - model_calibration)
    
    # Domain expertise
    domain_expertise = quality_factors.get('domain_expertise', 0.7)
    expertise_component = 0.1 * (1 - domain_expertise)
    
    # Combine all components
    meta_uncertainty = (
        dispersion_component +
        agreement_component +
        data_component +
        calibration_component +
        expertise_component
    )
    
    return max(0.1, min(0.9, meta_uncertainty))
```

## Performance Specifications

### Computational Complexity Targets

- **Initial Confidence Calculation**: O(1) per prediction
- **Bayesian Update**: O(1) per evidence piece
- **CERQual Assessment**: O(n) where n = number of studies
- **Cross-Modal Translation**: O(1) per translation
- **Temporal Decay**: O(1) per confidence score

### Memory Usage Targets

- **Maximum memory per confidence calculation**: 1MB
- **Evidence history storage**: 100MB for 10,000 pieces of evidence
- **Calibration data**: 50MB for 1 million predictions

### Response Time Targets

- **Real-time confidence updates**: < 10ms
- **Batch uncertainty recalculation**: < 1s for 1,000 items
- **CERQual assessment**: < 100ms for 20 studies
- **Cross-modal translation**: < 5ms per translation

## Integration Points

### With Existing KGAS Services

1. **IdentityService**: Receives initial confidence scores
2. **ProvenanceService**: Provides evidence weights and metadata
3. **QualityService**: Uses uncertainty for quality assessment
4. **Neo4jManager**: Stores confidence scores in graph
5. **MemoryManager**: Handles confidence score caching

### API Specifications

```python
# Core uncertainty service interface
class UncertaintyEngine:
    async def calculate_initial_confidence(self, prediction_data: Dict) -> float
    async def update_confidence_bayesian(self, evidence: List[Dict]) -> float
    async def assess_cerqual(self, evidence_set: List[Dict], question: str) -> Dict
    async def translate_cross_modal(self, confidence: float, context: Dict) -> float
    async def calculate_temporal_decay(self, confidence: float, timestamp: datetime) -> float
    async def get_meta_uncertainty(self, estimates: List[float], context: Dict) -> float
```

## Validation Procedures

### 1. Synthetic Data Testing

- Generate ground truth datasets with known confidence levels
- Test all mathematical formulas against expected outputs
- Validate edge cases and boundary conditions

### 2. Calibration Testing

- Use historical predictions with known outcomes
- Measure calibration curves and identify bias patterns
- Test different confidence ranges and domains

### 3. Performance Benchmarking

- Load testing with various data volumes
- Memory usage profiling
- Response time measurement across different scenarios

### 4. Cross-Validation

- Compare uncertainty estimates across different methods
- Validate consistency of cross-modal translations
- Test temporal decay accuracy with longitudinal data

## Implementation Checklist

- [ ] Core mathematical functions implemented
- [ ] Unit tests for all formulas
- [ ] Integration tests with existing services
- [ ] Performance benchmarks completed
- [ ] Calibration validation performed
- [ ] Documentation and examples created
- [ ] Edge case handling verified
- [ ] Memory usage optimized
- [ ] Response time targets met
- [ ] Cross-modal translation validated

This specification provides the complete mathematical foundation needed to implement the KGAS uncertainty framework with precision and reliability.