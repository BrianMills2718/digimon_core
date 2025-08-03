"""
ConfidenceScore Implementation - Main Interface

Streamlined confidence scoring interface using decomposed components.
Reduced from 912 lines to focused interface.

Implements the normative confidence scoring system for KGAS tools according
to ADR-004 specifications with Bayesian evidence power as the default.

UPDATED: Supports uncertainty framework with confidence ranges and CERQual assessment.
"""

import logging
from typing import Dict, Any, Optional, Tuple, List, Callable
from datetime import datetime

from .confidence_scoring import (
    PropagationMethod, ConfidenceScore as BaseConfidenceScore,
    ConfidenceCombiner, CombinationMethodFactory,
    TemporalRangeManager, CERQualProcessor,
    ConfidenceCalculator, DomainSpecificCalculator, ConfidenceFactory,
    create_high_confidence, create_medium_confidence, create_low_confidence
)

logger = logging.getLogger(__name__)


class ConfidenceScore(BaseConfidenceScore):
    """
    Main confidence score interface that extends the base implementation with convenience methods.
    
    Uses decomposed components for maintainability and testing:
    - CombinationMethodFactory: Mathematical combination algorithms
    - TemporalRangeManager: Time-based decay and uncertainty ranges
    - CERQualProcessor: Quality assessment framework
    - ConfidenceCalculator: Factory methods for different sources
    """
    
    def combine_with(self, other: "ConfidenceScore", 
                    method: Optional[PropagationMethod] = None) -> "ConfidenceScore":
        """Combine this confidence score with another using specified method."""
        try:
            result = CombinationMethodFactory.combine_scores(self, other, method)
            logger.debug(f"Combined {self.value:.3f} with {other.value:.3f} → {result.value:.3f}")
            return ConfidenceScore(**result.dict())
        except Exception as e:
            logger.error(f"Error combining confidence scores: {e}")
            # Fallback to simple average
            return ConfidenceScore(
                value=(self.value + other.value) / 2,
                evidence_weight=self.evidence_weight + other.evidence_weight,
                propagation_method=self.propagation_method,
                metadata={"combination_error": str(e), "fallback_used": True}
            )
    
    def decay(self, decay_factor: float = 0.95) -> "ConfidenceScore":
        """Apply simple decay factor to confidence score."""
        decayed_value = max(0.0, min(1.0, self.value * decay_factor))
        
        new_metadata = {**self.metadata}
        new_metadata.update({
            "decay_applied": True,
            "decay_factor": decay_factor,
            "original_value": self.value
        })
        
        return ConfidenceScore(
            **{**self.dict(), "value": decayed_value, "metadata": new_metadata}
        )
    
    def apply_temporal_decay(self, current_time: Optional[datetime] = None) -> "ConfidenceScore":
        """Apply temporal decay based on configured decay function."""
        try:
            manager = TemporalRangeManager()
            result = manager.temporal_processor.apply_temporal_decay(self, current_time)
            return ConfidenceScore(**result.dict())
        except Exception as e:
            logger.error(f"Error applying temporal decay: {e}")
            return self
    
    def add_cerqual_evidence(self, 
                           methodological_limitations: Optional[float] = None,
                           relevance: Optional[float] = None,
                           coherence: Optional[float] = None,
                           adequacy_of_data: Optional[float] = None,
                           evidence_description: str = "") -> "ConfidenceScore":
        """Add CERQual evidence dimensions to this confidence score."""
        try:
            result = CERQualProcessor.add_cerqual_evidence(
                self, methodological_limitations, relevance, coherence, 
                adequacy_of_data, evidence_description
            )
            return ConfidenceScore(**result.dict())
        except Exception as e:
            logger.error(f"Error adding CERQual evidence: {e}")
            return self
    
    def calculate_cerqual_combined(self) -> float:
        """Calculate combined CERQual confidence score."""
        try:
            return CERQualProcessor.calculate_cerqual_combined(self)
        except Exception as e:
            logger.error(f"Error calculating CERQual combined score: {e}")
            return self.value
    
    def set_confidence_range(self, min_confidence: float, max_confidence: float) -> "ConfidenceScore":
        """Set confidence range, adjusting main value if needed."""
        try:
            manager = TemporalRangeManager()
            result = manager.range_processor.set_confidence_range(self, min_confidence, max_confidence)
            return ConfidenceScore(**result.dict())
        except Exception as e:
            logger.error(f"Error setting confidence range: {e}")
            return self
    
    def combine_with_range_preservation(self, other: "ConfidenceScore") -> "ConfidenceScore":
        """Combine with another score while preserving uncertainty ranges."""
        try:
            manager = TemporalRangeManager()
            result = manager.range_processor.combine_with_range_preservation(self, other)
            return ConfidenceScore(**result.dict())
        except Exception as e:
            logger.error(f"Error combining with range preservation: {e}")
            return self.combine_with(other)
    
    @classmethod
    def create_with_cerqual(cls, 
                          methodological_limitations: float,
                          relevance: float,
                          coherence: float,
                          adequacy_of_data: float,
                          evidence_weight: int = 1,
                          base_confidence: Optional[float] = None,
                          source: str = "cerqual_assessment") -> "ConfidenceScore":
        """Create confidence score with CERQual assessment."""
        try:
            result = CERQualProcessor.create_with_cerqual(
                methodological_limitations, relevance, coherence, adequacy_of_data,
                evidence_weight, base_confidence, source
            )
            return ConfidenceScore(**result.dict())
        except Exception as e:
            logger.error(f"Error creating confidence with CERQual: {e}")
            # Fallback to basic confidence
            fallback_confidence = base_confidence or (methodological_limitations + relevance + coherence + adequacy_of_data) / 4.0
            return ConfidenceScore(
                value=max(0.0, min(1.0, fallback_confidence)),
                evidence_weight=evidence_weight,
                source=source,
                metadata={"cerqual_error": str(e), "fallback_used": True}
            )
    
    @classmethod
    def create_range_only(cls, min_confidence: float, max_confidence: float,
                         evidence_weight: int = 1, source: str = "range_estimate") -> "ConfidenceScore":
        """Create confidence score with only range information (no point estimate)."""
        try:
            manager = TemporalRangeManager()
            result = manager.range_processor.create_range_only(min_confidence, max_confidence, evidence_weight, source)
            return ConfidenceScore(**result.dict())
        except Exception as e:
            logger.error(f"Error creating range-only confidence: {e}")
            # Fallback to midpoint
            midpoint = (min_confidence + max_confidence) / 2.0
            return ConfidenceScore(
                value=midpoint,
                confidence_range=(min_confidence, max_confidence),
                evidence_weight=evidence_weight,
                source=source,
                metadata={"range_error": str(e), "fallback_used": True}
            )
    
    @classmethod
    def create_high_confidence(cls, evidence_weight: int = 3, source: str = "high_confidence") -> "ConfidenceScore":
        """Create high confidence score (0.8-0.9 range)."""
        base_score = create_high_confidence(evidence_weight=evidence_weight)
        return cls(**base_score.dict())
    
    @classmethod
    def create_medium_confidence(cls, evidence_weight: int = 2, source: str = "medium_confidence") -> "ConfidenceScore":
        """Create medium confidence score (0.5-0.7 range).""" 
        base_score = create_medium_confidence(evidence_weight=evidence_weight)
        return cls(**base_score.dict())
    
    @classmethod
    def create_low_confidence(cls, evidence_weight: int = 1, source: str = "low_confidence") -> "ConfidenceScore":
        """Create low confidence score (0.2-0.4 range)."""
        base_score = create_low_confidence(evidence_weight=evidence_weight)
        return cls(**base_score.dict())


# Alias for the decomposed ConfidenceCalculator
class ConfidenceCalculator:
    """
    Utility class for calculating confidence scores from various inputs.
    
    Uses decomposed calculator components for focused functionality.
    """
    
    # Re-export main calculator methods
    from_spacy_confidence = staticmethod(ConfidenceCalculator.from_spacy_confidence)
    from_llm_response = staticmethod(ConfidenceCalculator.from_llm_response)
    from_vector_similarity = staticmethod(ConfidenceCalculator.from_vector_similarity)
    from_graph_centrality = staticmethod(ConfidenceCalculator.from_graph_centrality)
    
    # Re-export domain-specific methods
    for_text_to_argument_extraction = staticmethod(DomainSpecificCalculator.for_text_to_argument_extraction)
    for_sentiment_attitude_mapping = staticmethod(DomainSpecificCalculator.for_sentiment_attitude_mapping)
    for_belief_network_extraction = staticmethod(DomainSpecificCalculator.for_belief_network_extraction)
    for_individual_to_community_aggregation = staticmethod(DomainSpecificCalculator.for_individual_to_community_aggregation)
    for_psychological_state_inference = staticmethod(DomainSpecificCalculator.for_psychological_state_inference)


def get_confidence_scoring_info() -> Dict[str, Any]:
    """Get information about the confidence scoring system."""
    return {
        "module": "confidence_score",
        "version": "2.0.0",
        "architecture": "decomposed_components",
        "adr_compliance": "ADR-004",
        "capabilities": [
            "normative_confidence_measurement",
            "bayesian_evidence_power",
            "dempster_shafer_theory",
            "min_max_combination",
            "temporal_decay",
            "cerqual_assessment",
            "uncertainty_ranges",
            "domain_specific_calculators"
        ],
        "components": {
            "data_models": "PropagationMethod, ConfidenceScore",
            "combination_methods": "BayesianCombiner, DempsterShaferCombiner, MinMaxCombiner",
            "temporal_range": "TemporalDecayProcessor, RangeProcessor",
            "cerqual": "CERQualProcessor, CERQualCalculator",
            "calculators": "ConfidenceCalculator, DomainSpecificCalculator",
            "factory": "ConfidenceFactory"
        },
        "propagation_methods": [method.value for method in PropagationMethod],
        "decomposed": True,
        "file_count": 7,  # Main file + 6 component files
        "total_lines": 220  # This main file line count
    }


# Export main classes and functions for backward compatibility
__all__ = [
    "PropagationMethod",
    "ConfidenceScore", 
    "ConfidenceCalculator",
    "create_high_confidence",
    "create_medium_confidence",
    "create_low_confidence",
    "get_confidence_scoring_info"
]