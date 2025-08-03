"""
Confidence Aggregator

Aggregates confidence scores across dynamic executions with intelligent
handling of variable tool execution outcomes and uncertainty quantification.
"""

import logging
import asyncio
import math
from typing import Dict, List, Set, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)


class ConfidenceSource(Enum):
    """Sources of confidence information"""
    TOOL_OUTPUT = "tool_output"           # Direct tool confidence scores
    EXECUTION_SUCCESS = "execution_success"  # Success/failure of execution
    DATA_QUALITY = "data_quality"         # Quality of input/output data
    TEMPORAL_CONSISTENCY = "temporal_consistency"  # Consistency across time
    CROSS_VALIDATION = "cross_validation"  # Agreement between multiple tools
    STATISTICAL_SIGNIFICANCE = "statistical_significance"  # Statistical measures
    DOMAIN_EXPERTISE = "domain_expertise"  # Domain-specific confidence rules
    USER_FEEDBACK = "user_feedback"       # Historical user feedback


class AggregationMethod(Enum):
    """Methods for aggregating confidence scores"""
    WEIGHTED_AVERAGE = "weighted_average"     # Weighted by tool reliability
    BAYESIAN_FUSION = "bayesian_fusion"       # Bayesian confidence fusion
    MINIMUM_CONSENSUS = "minimum_consensus"   # Minimum agreement threshold
    MAXIMUM_LIKELIHOOD = "maximum_likelihood" # Maximum likelihood estimation
    ENSEMBLE_VOTING = "ensemble_voting"       # Ensemble-based voting
    UNCERTAINTY_WEIGHTED = "uncertainty_weighted"  # Weight by uncertainty
    DYNAMIC_WEIGHTING = "dynamic_weighting"   # Context-dependent weighting


@dataclass
class ConfidenceInput:
    """Individual confidence input from a tool or source"""
    source_id: str
    source_type: ConfidenceSource
    confidence_score: float  # 0.0 to 1.0
    uncertainty: float = 0.0  # 0.0 to 1.0 (0 = certain, 1 = highly uncertain)
    weight: float = 1.0      # Relative importance weight
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    data_volume: int = 0     # Amount of data processed
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfidenceMetrics:
    """Comprehensive confidence metrics"""
    overall_confidence: float
    confidence_variance: float
    uncertainty_level: float
    reliability_score: float
    consensus_strength: float
    
    # Detailed breakdowns
    tool_confidences: Dict[str, float] = field(default_factory=dict)
    source_type_confidences: Dict[ConfidenceSource, float] = field(default_factory=dict)
    uncertainty_sources: Dict[str, float] = field(default_factory=dict)
    
    # Statistical measures
    confidence_distribution: Dict[str, float] = field(default_factory=dict)
    outlier_scores: List[str] = field(default_factory=list)
    
    # Quality indicators
    data_quality_score: float = 0.0
    temporal_consistency_score: float = 0.0
    cross_validation_score: float = 0.0
    
    # Meta-information
    aggregation_method: AggregationMethod = AggregationMethod.WEIGHTED_AVERAGE
    inputs_processed: int = 0
    failed_inputs: int = 0
    processing_time: float = 0.0


@dataclass
class UncertaintyQuantification:
    """Quantification of different types of uncertainty"""
    aleatoric_uncertainty: float = 0.0    # Inherent data noise/randomness
    epistemic_uncertainty: float = 0.0    # Model/knowledge uncertainty  
    measurement_uncertainty: float = 0.0  # Measurement/observation errors
    systematic_uncertainty: float = 0.0   # Systematic biases or errors
    temporal_uncertainty: float = 0.0     # Time-related uncertainty
    
    # Combined measures
    total_uncertainty: float = 0.0
    reducible_uncertainty: float = 0.0    # Can be reduced with more data
    irreducible_uncertainty: float = 0.0  # Fundamental limitations


class ConfidenceAggregator:
    """Aggregates confidence across dynamic executions with uncertainty quantification"""
    
    def __init__(self):
        """Initialize confidence aggregator"""
        self.logger = logger
        
        # Tool reliability weights (learned from historical performance)
        self.tool_reliability_weights = self._initialize_tool_weights()
        
        # Source type weights
        self.source_type_weights = self._initialize_source_weights()
        
        # Aggregation configuration
        self.aggregation_config = {
            'minimum_inputs': 1,
            'outlier_threshold': 2.0,  # Standard deviations for outlier detection
            'consensus_threshold': 0.7,  # Minimum agreement for strong consensus
            'uncertainty_penalty': 0.1,  # Penalty factor for high uncertainty
            'temporal_decay': 0.95      # Decay factor for older measurements
        }
        
        # Statistical tracking
        self.aggregation_history: List[ConfidenceMetrics] = []
        
        self.logger.info("Initialized confidence aggregator with uncertainty quantification")
    
    async def aggregate_confidence(self, confidence_inputs: List[ConfidenceInput],
                                 method: AggregationMethod = AggregationMethod.WEIGHTED_AVERAGE,
                                 context: Optional[Dict[str, Any]] = None) -> ConfidenceMetrics:
        """Aggregate confidence from multiple sources"""
        
        self.logger.info(f"Aggregating confidence from {len(confidence_inputs)} sources using {method.value}")
        
        start_time = asyncio.get_event_loop().time()
        
        # Validate and preprocess inputs
        valid_inputs = await self._preprocess_inputs(confidence_inputs)
        
        if not valid_inputs:
            return self._create_default_metrics("No valid confidence inputs")
        
        # Apply aggregation method
        if method == AggregationMethod.WEIGHTED_AVERAGE:
            metrics = await self._weighted_average_aggregation(valid_inputs, context)
        elif method == AggregationMethod.BAYESIAN_FUSION:
            metrics = await self._bayesian_fusion_aggregation(valid_inputs, context)
        elif method == AggregationMethod.MINIMUM_CONSENSUS:
            metrics = await self._minimum_consensus_aggregation(valid_inputs, context)
        elif method == AggregationMethod.UNCERTAINTY_WEIGHTED:
            metrics = await self._uncertainty_weighted_aggregation(valid_inputs, context)
        elif method == AggregationMethod.DYNAMIC_WEIGHTING:
            metrics = await self._dynamic_weighting_aggregation(valid_inputs, context)
        else:
            # Default to weighted average
            metrics = await self._weighted_average_aggregation(valid_inputs, context)
        
        # Calculate uncertainty quantification
        uncertainty_quantification = await self._quantify_uncertainty(valid_inputs, metrics)
        
        # Enhance metrics with additional analysis
        enhanced_metrics = await self._enhance_metrics(metrics, valid_inputs, uncertainty_quantification)
        
        # Set processing metadata
        enhanced_metrics.aggregation_method = method
        enhanced_metrics.inputs_processed = len(valid_inputs)
        enhanced_metrics.failed_inputs = len(confidence_inputs) - len(valid_inputs)
        enhanced_metrics.processing_time = asyncio.get_event_loop().time() - start_time
        
        # Store for historical analysis
        self.aggregation_history.append(enhanced_metrics)
        
        self.logger.info(f"Aggregated confidence: {enhanced_metrics.overall_confidence:.3f} "
                        f"(uncertainty: {enhanced_metrics.uncertainty_level:.3f})")
        
        return enhanced_metrics
    
    async def _preprocess_inputs(self, inputs: List[ConfidenceInput]) -> List[ConfidenceInput]:
        """Preprocess and validate confidence inputs"""
        
        valid_inputs = []
        
        for input_item in inputs:
            # Validate confidence score
            if not (0.0 <= input_item.confidence_score <= 1.0):
                self.logger.warning(f"Invalid confidence score {input_item.confidence_score} for {input_item.source_id}")
                continue
            
            # Validate uncertainty
            if not (0.0 <= input_item.uncertainty <= 1.0):
                input_item.uncertainty = 0.0  # Default to no uncertainty
            
            # Apply tool reliability weighting
            tool_weight = self.tool_reliability_weights.get(input_item.source_id, 1.0)
            source_weight = self.source_type_weights.get(input_item.source_type, 1.0)
            
            # Combine weights
            input_item.weight = input_item.weight * tool_weight * source_weight
            
            valid_inputs.append(input_item)
        
        return valid_inputs
    
    async def _weighted_average_aggregation(self, inputs: List[ConfidenceInput],
                                          context: Optional[Dict[str, Any]]) -> ConfidenceMetrics:
        """Aggregate using weighted average"""
        
        if not inputs:
            return self._create_default_metrics("No inputs for weighted average")
        
        # Calculate weighted average confidence
        total_weighted_confidence = 0.0
        total_weight = 0.0
        tool_confidences = {}
        source_confidences = defaultdict(list)
        
        for input_item in inputs:
            # Weight by reliability and inverse uncertainty
            effective_weight = input_item.weight * (1.0 - input_item.uncertainty * self.aggregation_config['uncertainty_penalty'])
            
            total_weighted_confidence += input_item.confidence_score * effective_weight
            total_weight += effective_weight
            
            # Track by tool and source type
            tool_confidences[input_item.source_id] = input_item.confidence_score
            source_confidences[input_item.source_type].append(input_item.confidence_score)
        
        overall_confidence = total_weighted_confidence / total_weight if total_weight > 0 else 0.0
        
        # Calculate variance
        variance = 0.0
        if len(inputs) > 1:
            for input_item in inputs:
                variance += (input_item.confidence_score - overall_confidence) ** 2
            variance /= len(inputs)
        
        # Calculate consensus strength
        consensus_strength = self._calculate_consensus_strength(inputs)
        
        # Calculate source type confidences
        source_type_confidences = {}
        for source_type, confidences in source_confidences.items():
            source_type_confidences[source_type] = statistics.mean(confidences)
        
        return ConfidenceMetrics(
            overall_confidence=overall_confidence,
            confidence_variance=variance,
            uncertainty_level=self._calculate_overall_uncertainty(inputs),
            reliability_score=self._calculate_reliability_score(inputs),
            consensus_strength=consensus_strength,
            tool_confidences=tool_confidences,
            source_type_confidences=source_type_confidences
        )
    
    async def _bayesian_fusion_aggregation(self, inputs: List[ConfidenceInput],
                                         context: Optional[Dict[str, Any]]) -> ConfidenceMetrics:
        """Aggregate using Bayesian fusion approach"""
        
        if not inputs:
            return self._create_default_metrics("No inputs for Bayesian fusion")
        
        # Bayesian fusion treats confidence as probability
        # Uses log-odds to combine evidence
        
        log_odds_sum = 0.0
        total_weight = 0.0
        
        for input_item in inputs:
            # Convert confidence to probability
            prob = max(0.001, min(0.999, input_item.confidence_score))  # Avoid log(0) issues
            
            # Calculate log-odds
            log_odds = math.log(prob / (1 - prob))
            
            # Weight by reliability and inverse uncertainty
            weight = input_item.weight * (1.0 - input_item.uncertainty)
            
            log_odds_sum += log_odds * weight
            total_weight += weight
        
        # Convert back to probability
        if total_weight > 0:
            avg_log_odds = log_odds_sum / total_weight
            fused_prob = 1.0 / (1.0 + math.exp(-avg_log_odds))
        else:
            fused_prob = 0.5  # Neutral probability
        
        # Calculate uncertainty from disagreement
        disagreement = self._calculate_disagreement(inputs)
        uncertainty_level = disagreement * 0.5  # Scale disagreement to uncertainty
        
        # Build metrics similar to weighted average but with Bayesian fusion
        tool_confidences = {inp.source_id: inp.confidence_score for inp in inputs}
        
        return ConfidenceMetrics(
            overall_confidence=fused_prob,
            confidence_variance=self._calculate_variance(inputs),
            uncertainty_level=uncertainty_level,
            reliability_score=self._calculate_reliability_score(inputs),
            consensus_strength=self._calculate_consensus_strength(inputs),
            tool_confidences=tool_confidences
        )
    
    async def _minimum_consensus_aggregation(self, inputs: List[ConfidenceInput],
                                           context: Optional[Dict[str, Any]]) -> ConfidenceMetrics:
        """Aggregate using minimum consensus approach"""
        
        if not inputs:
            return self._create_default_metrics("No inputs for consensus")
        
        confidences = [inp.confidence_score for inp in inputs]
        
        # Find groups of agreeing sources
        consensus_groups = self._find_consensus_groups(inputs)
        
        if not consensus_groups:
            # No consensus - use conservative estimate
            overall_confidence = min(confidences) * 0.8  # Penalty for no consensus
            consensus_strength = 0.0
        else:
            # Use confidence from largest consensus group
            largest_group = max(consensus_groups, key=len)
            group_confidences = [inp.confidence_score for inp in largest_group]
            overall_confidence = statistics.mean(group_confidences)
            consensus_strength = len(largest_group) / len(inputs)
        
        tool_confidences = {inp.source_id: inp.confidence_score for inp in inputs}
        
        return ConfidenceMetrics(
            overall_confidence=overall_confidence,
            confidence_variance=self._calculate_variance(inputs),
            uncertainty_level=1.0 - consensus_strength,  # High uncertainty if low consensus
            reliability_score=self._calculate_reliability_score(inputs),
            consensus_strength=consensus_strength,
            tool_confidences=tool_confidences
        )
    
    async def _uncertainty_weighted_aggregation(self, inputs: List[ConfidenceInput],
                                              context: Optional[Dict[str, Any]]) -> ConfidenceMetrics:
        """Aggregate with explicit uncertainty weighting"""
        
        if not inputs:
            return self._create_default_metrics("No inputs for uncertainty weighting")
        
        # Weight by inverse uncertainty (more certain = higher weight)
        total_weighted_confidence = 0.0
        total_weight = 0.0
        
        for input_item in inputs:
            # Weight inversely proportional to uncertainty
            certainty = 1.0 - input_item.uncertainty
            weight = input_item.weight * certainty * certainty  # Square for stronger effect
            
            total_weighted_confidence += input_item.confidence_score * weight
            total_weight += weight
        
        overall_confidence = total_weighted_confidence / total_weight if total_weight > 0 else 0.0
        
        # Calculate overall uncertainty as weighted average
        total_weighted_uncertainty = sum(inp.uncertainty * inp.weight for inp in inputs)
        total_weight_unc = sum(inp.weight for inp in inputs)
        overall_uncertainty = total_weighted_uncertainty / total_weight_unc if total_weight_unc > 0 else 0.5
        
        tool_confidences = {inp.source_id: inp.confidence_score for inp in inputs}
        uncertainty_sources = {inp.source_id: inp.uncertainty for inp in inputs}
        
        return ConfidenceMetrics(
            overall_confidence=overall_confidence,
            confidence_variance=self._calculate_variance(inputs),
            uncertainty_level=overall_uncertainty,
            reliability_score=self._calculate_reliability_score(inputs),
            consensus_strength=self._calculate_consensus_strength(inputs),
            tool_confidences=tool_confidences,
            uncertainty_sources=uncertainty_sources
        )
    
    async def _dynamic_weighting_aggregation(self, inputs: List[ConfidenceInput],
                                           context: Optional[Dict[str, Any]]) -> ConfidenceMetrics:
        """Aggregate with context-dependent dynamic weighting"""
        
        if not inputs:
            return self._create_default_metrics("No inputs for dynamic weighting")
        
        # Adjust weights based on context
        adjusted_inputs = []
        for input_item in inputs:
            adjusted_weight = self._calculate_dynamic_weight(input_item, context or {})
            
            # Create adjusted input
            adjusted_input = ConfidenceInput(
                source_id=input_item.source_id,
                source_type=input_item.source_type,
                confidence_score=input_item.confidence_score,
                uncertainty=input_item.uncertainty,
                weight=adjusted_weight,
                metadata=input_item.metadata,
                execution_time=input_item.execution_time,
                data_volume=input_item.data_volume,
                context=input_item.context
            )
            adjusted_inputs.append(adjusted_input)
        
        # Use weighted average with dynamic weights
        return await self._weighted_average_aggregation(adjusted_inputs, context)
    
    async def _quantify_uncertainty(self, inputs: List[ConfidenceInput],
                                  metrics: ConfidenceMetrics) -> UncertaintyQuantification:
        """Quantify different types of uncertainty"""
        
        # Aleatoric uncertainty (from data variability)
        confidence_scores = [inp.confidence_score for inp in inputs]
        aleatoric = statistics.stdev(confidence_scores) if len(confidence_scores) > 1 else 0.0
        
        # Epistemic uncertainty (from model/tool uncertainty)
        epistemic = statistics.mean([inp.uncertainty for inp in inputs])
        
        # Measurement uncertainty (from execution variations)
        execution_times = [inp.execution_time for inp in inputs if inp.execution_time > 0]
        measurement = statistics.stdev(execution_times) / statistics.mean(execution_times) if len(execution_times) > 1 and statistics.mean(execution_times) > 0 else 0.0
        measurement = min(1.0, measurement)  # Normalize to [0,1]
        
        # Systematic uncertainty (from tool reliability variations)
        reliability_scores = [self.tool_reliability_weights.get(inp.source_id, 1.0) for inp in inputs]
        systematic = 1.0 - statistics.mean(reliability_scores) if reliability_scores else 0.0
        
        # Temporal uncertainty (for now, set to 0 - could be enhanced with time-based analysis)
        temporal = 0.0
        
        # Total uncertainty (combination of all sources)
        total = min(1.0, math.sqrt(aleatoric**2 + epistemic**2 + measurement**2 + systematic**2 + temporal**2))
        
        # Reducible vs irreducible uncertainty
        reducible = min(total, epistemic + measurement)  # Can be reduced with better tools/more data
        irreducible = total - reducible
        
        return UncertaintyQuantification(
            aleatoric_uncertainty=aleatoric,
            epistemic_uncertainty=epistemic,
            measurement_uncertainty=measurement,
            systematic_uncertainty=systematic,
            temporal_uncertainty=temporal,
            total_uncertainty=total,
            reducible_uncertainty=reducible,
            irreducible_uncertainty=irreducible
        )
    
    async def _enhance_metrics(self, base_metrics: ConfidenceMetrics,
                             inputs: List[ConfidenceInput],
                             uncertainty_quantification: UncertaintyQuantification) -> ConfidenceMetrics:
        """Enhance metrics with additional analysis"""
        
        # Calculate additional quality indicators
        base_metrics.data_quality_score = self._calculate_data_quality_score(inputs)
        base_metrics.temporal_consistency_score = self._calculate_temporal_consistency(inputs)
        base_metrics.cross_validation_score = self._calculate_cross_validation_score(inputs)
        
        # Update uncertainty level with quantified uncertainty
        base_metrics.uncertainty_level = uncertainty_quantification.total_uncertainty
        
        # Calculate confidence distribution
        confidences = [inp.confidence_score for inp in inputs]
        if confidences:
            base_metrics.confidence_distribution = {
                'mean': statistics.mean(confidences),
                'median': statistics.median(confidences),
                'std': statistics.stdev(confidences) if len(confidences) > 1 else 0.0,
                'min': min(confidences),
                'max': max(confidences)
            }
        
        # Identify outliers
        base_metrics.outlier_scores = self._identify_outliers(inputs)
        
        return base_metrics
    
    def _calculate_consensus_strength(self, inputs: List[ConfidenceInput]) -> float:
        """Calculate strength of consensus among inputs"""
        
        if len(inputs) < 2:
            return 1.0  # Perfect consensus with single input
        
        confidences = [inp.confidence_score for inp in inputs]
        
        # Calculate pairwise agreement
        agreements = []
        for i in range(len(confidences)):
            for j in range(i + 1, len(confidences)):
                agreement = 1.0 - abs(confidences[i] - confidences[j])
                agreements.append(agreement)
        
        return statistics.mean(agreements) if agreements else 0.0
    
    def _calculate_overall_uncertainty(self, inputs: List[ConfidenceInput]) -> float:
        """Calculate overall uncertainty level"""
        
        if not inputs:
            return 1.0  # Maximum uncertainty with no inputs
        
        # Weighted average of uncertainties
        total_weighted_uncertainty = sum(inp.uncertainty * inp.weight for inp in inputs)
        total_weight = sum(inp.weight for inp in inputs)
        
        return total_weighted_uncertainty / total_weight if total_weight > 0 else 0.5
    
    def _calculate_reliability_score(self, inputs: List[ConfidenceInput]) -> float:
        """Calculate overall reliability score"""
        
        if not inputs:
            return 0.0
        
        # Based on tool reliability weights and execution success
        reliability_scores = []
        for inp in inputs:
            tool_reliability = self.tool_reliability_weights.get(inp.source_id, 1.0)
            execution_reliability = 1.0 if inp.confidence_score > 0 else 0.0
            uncertainty_penalty = 1.0 - inp.uncertainty
            
            combined_reliability = tool_reliability * execution_reliability * uncertainty_penalty
            reliability_scores.append(combined_reliability)
        
        return statistics.mean(reliability_scores)
    
    def _calculate_variance(self, inputs: List[ConfidenceInput]) -> float:
        """Calculate confidence variance"""
        
        if len(inputs) < 2:
            return 0.0
        
        confidences = [inp.confidence_score for inp in inputs]
        return statistics.variance(confidences)
    
    def _calculate_disagreement(self, inputs: List[ConfidenceInput]) -> float:
        """Calculate disagreement between inputs"""
        
        if len(inputs) < 2:
            return 0.0
        
        confidences = [inp.confidence_score for inp in inputs]
        
        # Calculate maximum pairwise disagreement
        max_disagreement = 0.0
        for i in range(len(confidences)):
            for j in range(i + 1, len(confidences)):
                disagreement = abs(confidences[i] - confidences[j])
                max_disagreement = max(max_disagreement, disagreement)
        
        return max_disagreement
    
    def _find_consensus_groups(self, inputs: List[ConfidenceInput]) -> List[List[ConfidenceInput]]:
        """Find groups of inputs that agree with each other"""
        
        threshold = self.aggregation_config['consensus_threshold']
        groups = []
        
        for inp in inputs:
            placed = False
            
            # Try to place in existing group
            for group in groups:
                if self._inputs_agree(inp, group[0], threshold):
                    group.append(inp)
                    placed = True
                    break
            
            # Create new group if not placed
            if not placed:
                groups.append([inp])
        
        # Return groups with at least 2 members
        return [group for group in groups if len(group) >= 2]
    
    def _inputs_agree(self, inp1: ConfidenceInput, inp2: ConfidenceInput, threshold: float) -> bool:
        """Check if two inputs agree within threshold"""
        return abs(inp1.confidence_score - inp2.confidence_score) <= (1.0 - threshold)
    
    def _calculate_dynamic_weight(self, input_item: ConfidenceInput, context: Dict[str, Any]) -> float:
        """Calculate dynamic weight based on context"""
        
        base_weight = input_item.weight
        
        # Adjust based on execution time (faster tools get slight bonus)
        if input_item.execution_time > 0:
            avg_time = context.get('average_execution_time', input_item.execution_time)
            time_factor = min(2.0, avg_time / input_item.execution_time)  # Cap at 2x bonus
            base_weight *= (1.0 + 0.1 * (time_factor - 1.0))  # Small bonus for speed
        
        # Adjust based on data volume (more data = higher weight)
        if input_item.data_volume > 0:
            avg_volume = context.get('average_data_volume', input_item.data_volume)
            volume_factor = min(2.0, input_item.data_volume / max(1, avg_volume))
            base_weight *= (1.0 + 0.2 * (volume_factor - 1.0))  # Moderate bonus for data volume
        
        # Adjust based on question complexity
        complexity = context.get('question_complexity', 'simple')
        if complexity == 'complex':
            # For complex questions, prefer more reliable tools
            tool_reliability = self.tool_reliability_weights.get(input_item.source_id, 1.0)
            base_weight *= tool_reliability
        
        return base_weight
    
    def _calculate_data_quality_score(self, inputs: List[ConfidenceInput]) -> float:
        """Calculate data quality score"""
        
        if not inputs:
            return 0.0
        
        # Based on data volume and execution success
        quality_scores = []
        for inp in inputs:
            volume_score = min(1.0, inp.data_volume / 1000.0) if inp.data_volume > 0 else 0.5
            confidence_score = inp.confidence_score
            uncertainty_penalty = 1.0 - inp.uncertainty
            
            quality = (volume_score + confidence_score + uncertainty_penalty) / 3.0
            quality_scores.append(quality)
        
        return statistics.mean(quality_scores)
    
    def _calculate_temporal_consistency(self, inputs: List[ConfidenceInput]) -> float:
        """Calculate temporal consistency score"""
        
        # For now, return neutral score
        # Could be enhanced with actual temporal analysis
        return 0.7
    
    def _calculate_cross_validation_score(self, inputs: List[ConfidenceInput]) -> float:
        """Calculate cross-validation score"""
        
        if len(inputs) < 2:
            return 0.5  # Neutral score with insufficient data
        
        # Calculate agreement between different source types
        source_type_confidences = defaultdict(list)
        for inp in inputs:
            source_type_confidences[inp.source_type].append(inp.confidence_score)
        
        if len(source_type_confidences) < 2:
            return 0.6  # Slight penalty for single source type
        
        # Calculate cross-source agreement
        source_averages = [statistics.mean(confidences) for confidences in source_type_confidences.values()]
        cross_validation_variance = statistics.variance(source_averages) if len(source_averages) > 1 else 0.0
        
        # Convert variance to agreement score (lower variance = higher agreement)
        cross_validation_score = max(0.0, 1.0 - cross_validation_variance * 4.0)  # Scale variance
        
        return cross_validation_score
    
    def _identify_outliers(self, inputs: List[ConfidenceInput]) -> List[str]:
        """Identify outlier confidence scores"""
        
        if len(inputs) < 3:
            return []  # Need at least 3 points to identify outliers
        
        confidences = [inp.confidence_score for inp in inputs]
        mean_conf = statistics.mean(confidences)
        std_conf = statistics.stdev(confidences)
        
        threshold = self.aggregation_config['outlier_threshold']
        outliers = []
        
        for inp in inputs:
            z_score = abs(inp.confidence_score - mean_conf) / std_conf if std_conf > 0 else 0
            if z_score > threshold:
                outliers.append(inp.source_id)
        
        return outliers
    
    def _create_default_metrics(self, reason: str) -> ConfidenceMetrics:
        """Create default metrics when aggregation fails"""
        
        self.logger.warning(f"Creating default confidence metrics: {reason}")
        
        return ConfidenceMetrics(
            overall_confidence=0.5,  # Neutral confidence
            confidence_variance=0.0,
            uncertainty_level=0.8,   # High uncertainty
            reliability_score=0.3,   # Low reliability
            consensus_strength=0.0   # No consensus
        )
    
    def _initialize_tool_weights(self) -> Dict[str, float]:
        """Initialize tool reliability weights"""
        
        # These would be learned from historical performance data
        return {
            'T01_PDF_LOADER': 0.95,
            'T15A_TEXT_CHUNKER': 0.98,
            'T23A_SPACY_NER': 0.90,
            'T27_RELATIONSHIP_EXTRACTOR': 0.85,
            'T31_ENTITY_BUILDER': 0.88,
            'T34_EDGE_BUILDER': 0.87,
            'T49_MULTI_HOP_QUERY': 0.82,
            'T68_PAGE_RANK': 0.93,
            'T85_TWITTER_EXPLORER': 0.80
        }
    
    def _initialize_source_weights(self) -> Dict[ConfidenceSource, float]:
        """Initialize source type weights"""
        
        return {
            ConfidenceSource.TOOL_OUTPUT: 1.0,
            ConfidenceSource.EXECUTION_SUCCESS: 0.8,
            ConfidenceSource.DATA_QUALITY: 0.9,
            ConfidenceSource.TEMPORAL_CONSISTENCY: 0.7,
            ConfidenceSource.CROSS_VALIDATION: 1.2,
            ConfidenceSource.STATISTICAL_SIGNIFICANCE: 1.1,
            ConfidenceSource.DOMAIN_EXPERTISE: 0.9,
            ConfidenceSource.USER_FEEDBACK: 1.0
        }
    
    def get_aggregation_statistics(self) -> Dict[str, Any]:
        """Get statistics about confidence aggregation performance"""
        
        if not self.aggregation_history:
            return {'total_aggregations': 0}
        
        recent_metrics = self.aggregation_history[-100:]  # Last 100 aggregations
        
        confidences = [m.overall_confidence for m in recent_metrics]
        uncertainties = [m.uncertainty_level for m in recent_metrics]
        reliabilities = [m.reliability_score for m in recent_metrics]
        
        return {
            'total_aggregations': len(self.aggregation_history),
            'recent_aggregations': len(recent_metrics),
            'average_confidence': statistics.mean(confidences),
            'average_uncertainty': statistics.mean(uncertainties),
            'average_reliability': statistics.mean(reliabilities),
            'confidence_std': statistics.stdev(confidences) if len(confidences) > 1 else 0.0,
            'method_usage': self._get_method_usage_stats()
        }
    
    def _get_method_usage_stats(self) -> Dict[str, int]:
        """Get usage statistics for different aggregation methods"""
        
        method_counts = defaultdict(int)
        for metrics in self.aggregation_history:
            method_counts[metrics.aggregation_method.value] += 1
        
        return dict(method_counts)
    
    def update_tool_reliability(self, tool_id: str, performance_score: float) -> None:
        """Update tool reliability based on observed performance"""
        
        current_weight = self.tool_reliability_weights.get(tool_id, 1.0)
        
        # Exponential moving average for reliability updates
        decay_factor = 0.1
        new_weight = (1 - decay_factor) * current_weight + decay_factor * performance_score
        
        self.tool_reliability_weights[tool_id] = max(0.1, min(1.0, new_weight))
        
        self.logger.debug(f"Updated reliability for {tool_id}: {current_weight:.3f} -> {new_weight:.3f}")