"""
Temporal and Range Processing Methods

Handles temporal decay of confidence scores and uncertainty range operations.
"""

import math
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Callable, Dict, Any

from .data_models import ConfidenceScore, PropagationMethod

logger = logging.getLogger(__name__)


class TemporalDecayProcessor:
    """Processes temporal decay of confidence scores"""
    
    @staticmethod
    def apply_temporal_decay(score: ConfidenceScore, current_time: Optional[datetime] = None) -> ConfidenceScore:
        """Apply temporal decay to confidence score based on its temporal configuration"""
        
        if current_time is None:
            current_time = datetime.now()
        
        # If no assessment time, no decay
        if score.assessment_time is None:
            return score
        
        # Check validity window first
        if score.validity_window is not None:
            start_time, end_time = score.validity_window
            
            if current_time < start_time:
                # Not yet valid
                return ConfidenceScore(
                    value=0.0,
                    evidence_weight=score.evidence_weight,
                    propagation_method=score.propagation_method,
                    metadata={**score.metadata, "decay_reason": "not_yet_valid"}
                )
            
            if end_time is not None and current_time > end_time:
                # Expired
                return ConfidenceScore(
                    value=0.0,
                    evidence_weight=score.evidence_weight,
                    propagation_method=score.propagation_method,
                    metadata={**score.metadata, "decay_reason": "expired"}
                )
        
        # Calculate time since assessment
        time_delta = current_time - score.assessment_time
        hours_elapsed = time_delta.total_seconds() / 3600
        
        # Apply decay function if specified
        decay_function = score.temporal_decay_function
        if decay_function is None or decay_function == "none":
            return score
        
        decay_factor = TemporalDecayProcessor._calculate_decay_factor(
            decay_function, hours_elapsed, score.metadata
        )
        
        # Apply decay
        decayed_value = score.value * decay_factor
        decayed_value = max(0.0, min(1.0, decayed_value))
        
        # Create new score with decay applied
        new_metadata = {**score.metadata}
        new_metadata.update({
            "decay_applied": True,
            "decay_function": decay_function,
            "hours_elapsed": hours_elapsed,
            "decay_factor": decay_factor,
            "original_value": score.value
        })
        
        return ConfidenceScore(
            value=decayed_value,
            confidence_range=score.confidence_range,
            evidence_weight=score.evidence_weight,
            methodological_limitations=score.methodological_limitations,
            relevance=score.relevance,
            coherence=score.coherence,
            adequacy_of_data=score.adequacy_of_data,
            assessment_time=current_time,  # Update assessment time
            validity_window=score.validity_window,
            temporal_decay_function=score.temporal_decay_function,
            measurement_type=score.measurement_type,
            data_coverage=score.data_coverage,
            is_aggregate=score.is_aggregate,
            distribution_type=score.distribution_type,
            distribution_parameters=score.distribution_parameters,
            source=score.source,
            propagation_method=score.propagation_method,
            metadata=new_metadata
        )
    
    @staticmethod
    def _calculate_decay_factor(decay_function: str, hours_elapsed: float, metadata: Dict[str, Any]) -> float:
        """Calculate decay factor based on function type and elapsed time"""
        
        # Get decay parameters from metadata or use defaults
        half_life_hours = metadata.get("decay_half_life_hours", 24.0)  # 24 hour default
        decay_rate = metadata.get("decay_rate", 0.1)  # 10% per period default
        
        if decay_function == "linear":
            # Linear decay: factor = 1 - (time / half_life) * decay_rate
            factor = 1.0 - (hours_elapsed / half_life_hours) * decay_rate
            return max(0.0, factor)
        
        elif decay_function == "exponential":
            # Exponential decay: factor = exp(-λt) where λ = ln(2) / half_life
            lambda_val = math.log(2) / half_life_hours
            factor = math.exp(-lambda_val * hours_elapsed)
            return factor
        
        elif decay_function == "step":
            # Step decay: full confidence until half_life, then drop by decay_rate
            if hours_elapsed < half_life_hours:
                return 1.0
            else:
                steps = int(hours_elapsed / half_life_hours)
                factor = (1.0 - decay_rate) ** steps
                return max(0.0, factor)
        
        else:
            logger.warning(f"Unknown decay function: {decay_function}, using exponential")
            lambda_val = math.log(2) / half_life_hours
            factor = math.exp(-lambda_val * hours_elapsed)
            return factor


class RangeProcessor:
    """Processes confidence ranges and uncertainty operations"""
    
    @staticmethod
    def set_confidence_range(score: ConfidenceScore, min_confidence: float, max_confidence: float) -> ConfidenceScore:
        """Set confidence range, adjusting main value if needed"""
        
        # Validate range
        if not (0.0 <= min_confidence <= max_confidence <= 1.0):
            raise ValueError(f"Invalid confidence range: [{min_confidence}, {max_confidence}]")
        
        # Adjust main value to be within range
        adjusted_value = max(min_confidence, min(max_confidence, score.value))
        
        return ConfidenceScore(
            value=adjusted_value,
            confidence_range=(min_confidence, max_confidence),
            evidence_weight=score.evidence_weight,
            methodological_limitations=score.methodological_limitations,
            relevance=score.relevance,
            coherence=score.coherence,
            adequacy_of_data=score.adequacy_of_data,
            assessment_time=score.assessment_time,
            validity_window=score.validity_window,
            temporal_decay_function=score.temporal_decay_function,
            measurement_type=score.measurement_type,
            data_coverage=score.data_coverage,
            is_aggregate=score.is_aggregate,
            distribution_type=score.distribution_type,
            distribution_parameters=score.distribution_parameters,
            source=score.source,
            propagation_method=score.propagation_method,
            metadata={**score.metadata, "range_adjusted": adjusted_value != score.value}
        )
    
    @staticmethod
    def combine_with_range_preservation(score1: ConfidenceScore, score2: ConfidenceScore) -> ConfidenceScore:
        """Combine scores while preserving and combining uncertainty ranges"""
        
        # Get ranges for both scores
        range1 = score1.get_confidence_range()
        range2 = score2.get_confidence_range()
        
        # Use combination method from first score
        from .combination_methods import CombinationMethodFactory
        
        # Combine point estimates
        combined_point = CombinationMethodFactory.combine_scores(score1, score2)
        
        # Combine ranges conservatively
        # Min of combined range = min of both mins
        # Max of combined range = max of both maxs
        combined_min = min(range1[0], range2[0])
        combined_max = max(range1[1], range2[1])
        
        # Ensure combined point estimate falls within combined range
        adjusted_value = max(combined_min, min(combined_max, combined_point.value))
        
        return ConfidenceScore(
            value=adjusted_value,
            confidence_range=(combined_min, combined_max),
            evidence_weight=combined_point.evidence_weight,
            methodological_limitations=score1.methodological_limitations,  # Take from first
            relevance=score1.relevance,
            coherence=score1.coherence,
            adequacy_of_data=score1.adequacy_of_data,
            assessment_time=datetime.now(),
            validity_window=None,  # Reset validity window for combined score
            temporal_decay_function=score1.temporal_decay_function,
            measurement_type="measured",  # Combined scores are measured
            data_coverage=min(score1.data_coverage, score2.data_coverage),  # Conservative
            is_aggregate=True,  # Combined scores are aggregates
            distribution_type="combined",
            distribution_parameters={
                "source_ranges": [range1, range2],
                "combination_method": score1.propagation_method.value
            },
            source="range_preserved_combination",
            propagation_method=score1.propagation_method,
            metadata={
                "combination_method": "range_preserved",
                "source_confidences": [score1.value, score2.value],
                "source_ranges": [range1, range2],
                "combined_range": (combined_min, combined_max)
            }
        )
    
    @staticmethod
    def create_range_only(min_confidence: float, max_confidence: float, 
                         evidence_weight: int = 1, source: str = "range_estimate") -> ConfidenceScore:
        """Create confidence score with only range information (no point estimate)"""
        
        if not (0.0 <= min_confidence <= max_confidence <= 1.0):
            raise ValueError(f"Invalid confidence range: [{min_confidence}, {max_confidence}]")
        
        # Use midpoint as point estimate
        midpoint = (min_confidence + max_confidence) / 2.0
        
        return ConfidenceScore(
            value=midpoint,
            confidence_range=(min_confidence, max_confidence),
            evidence_weight=evidence_weight,
            measurement_type="bounded",  # This is a bounded estimate
            source=source,
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            metadata={
                "range_only": True,
                "range_width": max_confidence - min_confidence,
                "range_midpoint": midpoint
            }
        )


class TemporalRangeManager:
    """Combined manager for temporal and range operations"""
    
    def __init__(self):
        self.temporal_processor = TemporalDecayProcessor()
        self.range_processor = RangeProcessor()
    
    def process_with_temporal_and_range(self, score: ConfidenceScore, 
                                      current_time: Optional[datetime] = None,
                                      new_range: Optional[Tuple[float, float]] = None) -> ConfidenceScore:
        """Apply both temporal decay and range adjustment"""
        
        # First apply temporal decay
        decayed_score = self.temporal_processor.apply_temporal_decay(score, current_time)
        
        # Then apply range adjustment if specified
        if new_range is not None:
            min_conf, max_conf = new_range
            final_score = self.range_processor.set_confidence_range(decayed_score, min_conf, max_conf)
        else:
            final_score = decayed_score
        
        return final_score