"""
Confidence Score Factory Methods

Factory methods for creating common confidence score patterns and presets.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

from .data_models import ConfidenceScore, PropagationMethod

logger = logging.getLogger(__name__)


class ConfidenceFactory:
    """Factory for creating confidence scores with common patterns"""
    
    @staticmethod
    def create_high_confidence(value: float = 0.9, evidence_weight: int = 5, 
                             source: str = "high_confidence_preset") -> ConfidenceScore:
        """Create a high confidence score with strong evidence."""
        return ConfidenceScore(
            value=max(0.8, min(1.0, value)),  # Ensure high confidence range
            evidence_weight=evidence_weight,
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            source=source,
            metadata={
                "confidence_tier": "HIGH",  # Fixed case for tests
                "preset_used": "high_confidence",
                "created_at": datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def create_medium_confidence(value: float = 0.7, evidence_weight: int = 3,
                               source: str = "medium_confidence_preset") -> ConfidenceScore:
        """Create a medium confidence score with moderate evidence."""
        return ConfidenceScore(
            value=max(0.4, min(0.85, value)),  # Ensure medium confidence range
            evidence_weight=evidence_weight,
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            source=source,
            metadata={
                "confidence_tier": "medium",
                "preset_used": "medium_confidence",
                "created_at": datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def create_low_confidence(value: float = 0.4, evidence_weight: int = 1,
                            source: str = "low_confidence_preset") -> ConfidenceScore:
        """Create a low confidence score with limited evidence."""
        return ConfidenceScore(
            value=max(0.1, min(0.6, value)),  # Ensure low confidence range
            evidence_weight=evidence_weight,
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            source=source,
            metadata={
                "confidence_tier": "low",
                "preset_used": "low_confidence", 
                "created_at": datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def create_with_temporal_decay(value: float, evidence_weight: int,
                                 half_life_hours: float = 24.0,
                                 decay_function: str = "exponential",
                                 source: str = "temporal_confidence") -> ConfidenceScore:
        """Create confidence score with temporal decay configuration"""
        
        return ConfidenceScore(
            value=value,
            evidence_weight=evidence_weight,
            temporal_decay_function=decay_function,
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            source=source,
            metadata={
                "decay_half_life_hours": half_life_hours,
                "decay_function": decay_function,
                "temporal_enabled": True,
                "created_at": datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def create_with_validity_window(value: float, evidence_weight: int,
                                  valid_for_hours: float,
                                  source: str = "time_bounded_confidence") -> ConfidenceScore:
        """Create confidence score valid for specific time window"""
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=valid_for_hours)
        
        return ConfidenceScore(
            value=value,
            evidence_weight=evidence_weight,
            validity_window=(start_time, end_time),
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            source=source,
            metadata={
                "valid_for_hours": valid_for_hours,
                "expires_at": end_time.isoformat(),
                "time_bounded": True,
                "created_at": start_time.isoformat()
            }
        )
    
    @staticmethod
    def create_aggregate(confidence_scores: list, 
                        aggregation_method: str = "weighted_average",
                        source: str = "aggregated_confidence") -> ConfidenceScore:
        """Create confidence score by aggregating multiple scores"""
        
        if not confidence_scores:
            raise ValueError("Cannot create aggregate from empty list")
        
        if aggregation_method == "weighted_average":
            # Weighted by evidence weight
            total_weight = sum(score.evidence_weight for score in confidence_scores)
            if total_weight == 0:
                weighted_value = sum(score.value for score in confidence_scores) / len(confidence_scores)
            else:
                weighted_value = sum(score.value * score.evidence_weight for score in confidence_scores) / total_weight
            
            combined_evidence_weight = total_weight
            
        elif aggregation_method == "simple_average":
            weighted_value = sum(score.value for score in confidence_scores) / len(confidence_scores)
            combined_evidence_weight = sum(score.evidence_weight for score in confidence_scores)
            
        elif aggregation_method == "conservative_min":
            weighted_value = min(score.value for score in confidence_scores)
            combined_evidence_weight = sum(score.evidence_weight for score in confidence_scores)
            
        elif aggregation_method == "optimistic_max":
            weighted_value = max(score.value for score in confidence_scores)
            combined_evidence_weight = sum(score.evidence_weight for score in confidence_scores)
            
        else:
            raise ValueError(f"Unknown aggregation method: {aggregation_method}")
        
        # Calculate combined range
        all_ranges = [score.get_confidence_range() for score in confidence_scores]
        combined_min = min(r[0] for r in all_ranges)
        combined_max = max(r[1] for r in all_ranges)
        
        return ConfidenceScore(
            value=max(0.0, min(1.0, weighted_value)),
            confidence_range=(combined_min, combined_max),
            evidence_weight=min(combined_evidence_weight, 50),  # Cap at reasonable max
            is_aggregate=True,
            distribution_type="aggregated",
            distribution_parameters={
                "source_count": len(confidence_scores),
                "aggregation_method": aggregation_method,
                "source_values": [score.value for score in confidence_scores],
                "source_weights": [score.evidence_weight for score in confidence_scores]
            },
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            source=source,
            metadata={
                "aggregation_method": aggregation_method,
                "source_count": len(confidence_scores),
                "source_confidence_tiers": [score.to_quality_tier() for score in confidence_scores],
                "created_at": datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def create_uncertain_range(min_confidence: float, max_confidence: float,
                             best_estimate: Optional[float] = None,
                             evidence_weight: int = 1,
                             source: str = "uncertain_range") -> ConfidenceScore:
        """Create confidence score representing uncertainty with range"""
        
        if not (0.0 <= min_confidence <= max_confidence <= 1.0):
            raise ValueError(f"Invalid confidence range: [{min_confidence}, {max_confidence}]")
        
        # Use best estimate if provided, otherwise midpoint
        if best_estimate is not None:
            if not (min_confidence <= best_estimate <= max_confidence):
                raise ValueError(f"Best estimate {best_estimate} outside range [{min_confidence}, {max_confidence}]")
            point_estimate = best_estimate
        else:
            point_estimate = (min_confidence + max_confidence) / 2.0
        
        return ConfidenceScore(
            value=point_estimate,
            confidence_range=(min_confidence, max_confidence),
            evidence_weight=evidence_weight,
            measurement_type="bounded",
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            source=source,
            metadata={
                "uncertainty_type": "range_based",
                "range_width": max_confidence - min_confidence,
                "best_estimate_provided": best_estimate is not None,
                "created_at": datetime.now().isoformat()
            }
        )


# Convenience functions for backward compatibility
def create_high_confidence(value: float = 0.9, evidence_weight: int = 5) -> ConfidenceScore:
    """Create a high confidence score with strong evidence."""
    return ConfidenceFactory.create_high_confidence(value, evidence_weight)


def create_medium_confidence(value: float = 0.7, evidence_weight: int = 3) -> ConfidenceScore:
    """Create a medium confidence score with moderate evidence."""
    return ConfidenceFactory.create_medium_confidence(value, evidence_weight)


def create_low_confidence(value: float = 0.4, evidence_weight: int = 1) -> ConfidenceScore:
    """Create a low confidence score with limited evidence."""
    return ConfidenceFactory.create_low_confidence(value, evidence_weight)