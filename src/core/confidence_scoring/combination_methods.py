"""
Confidence Combination Methods

Mathematical algorithms for combining confidence scores using different approaches:
Bayesian Evidence Power, Dempster-Shafer Theory, and Min-Max methods.
"""

import math
import logging
from typing import Dict, Any
from abc import ABC, abstractmethod

from .data_models import ConfidenceScore, PropagationMethod

logger = logging.getLogger(__name__)


class ConfidenceCombiner(ABC):
    """Abstract base class for confidence combination methods"""
    
    @abstractmethod
    def combine(self, conf1: ConfidenceScore, conf2: ConfidenceScore) -> ConfidenceScore:
        """Combine two confidence scores"""
        pass
    
    @abstractmethod
    def get_method_name(self) -> str:
        """Get the name of this combination method"""
        pass


class BayesianCombiner(ConfidenceCombiner):
    """Bayesian Evidence Power combination method"""
    
    def combine(self, conf1: ConfidenceScore, conf2: ConfidenceScore) -> ConfidenceScore:
        """Combine using Bayesian evidence power approach."""
        # Convert probabilities to odds, combine, then back to probabilities
        odds1 = conf1.value / (1 - conf1.value + 1e-10)  # Avoid division by zero
        odds2 = conf2.value / (1 - conf2.value + 1e-10)
        
        # Weight the evidence by evidence_weight
        weighted_odds1 = odds1 ** conf1.evidence_weight
        weighted_odds2 = odds2 ** conf2.evidence_weight
        
        # Combine weighted odds
        combined_odds = weighted_odds1 * weighted_odds2
        
        # Convert back to probability
        combined_probability = combined_odds / (1 + combined_odds)
        
        # Ensure result stays in [0,1]
        combined_probability = max(0.0, min(1.0, combined_probability))
        
        return ConfidenceScore(
            value=combined_probability,
            evidence_weight=conf1.evidence_weight + conf2.evidence_weight,
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            metadata={
                "combination_method": "bayesian_evidence_power",
                "source_confidences": [conf1.value, conf2.value],
                "source_evidence_weights": [conf1.evidence_weight, conf2.evidence_weight]
            }
        )
    
    def get_method_name(self) -> str:
        return "bayesian_evidence_power"


class DempsterShaferCombiner(ConfidenceCombiner):
    """Dempster-Shafer Theory combination method"""
    
    def combine(self, conf1: ConfidenceScore, conf2: ConfidenceScore) -> ConfidenceScore:
        """Combine using Dempster-Shafer theory."""
        # In D-S theory, we need to consider belief, doubt, and uncertainty
        # For simplicity, we'll use confidence as belief and map to basic probability assignments
        
        # Basic probability assignments
        m1_belief = conf1.value * (conf1.evidence_weight / 10.0)  # Scale evidence weight
        m1_doubt = (1 - conf1.value) * (conf1.evidence_weight / 10.0)
        m1_uncertainty = 1 - m1_belief - m1_doubt
        
        m2_belief = conf2.value * (conf2.evidence_weight / 10.0)
        m2_doubt = (1 - conf2.value) * (conf2.evidence_weight / 10.0)
        m2_uncertainty = 1 - m2_belief - m2_doubt
        
        # Dempster's rule of combination
        # Combined belief
        combined_belief = (m1_belief * m2_belief + 
                          m1_belief * m2_uncertainty + 
                          m1_uncertainty * m2_belief)
        
        # Combined doubt
        combined_doubt = (m1_doubt * m2_doubt + 
                         m1_doubt * m2_uncertainty + 
                         m1_uncertainty * m2_doubt)
        
        # Combined uncertainty
        combined_uncertainty = m1_uncertainty * m2_uncertainty
        
        # Normalization factor (avoid conflict)
        conflict = m1_belief * m2_doubt + m1_doubt * m2_belief
        normalization = 1 - conflict
        
        if normalization > 1e-10:  # Avoid division by zero
            combined_belief /= normalization
            combined_doubt /= normalization
            combined_uncertainty /= normalization
        
        # Convert back to confidence (belief / (belief + uncertainty))
        denominator = combined_belief + combined_uncertainty
        if denominator > 1e-10:
            final_confidence = combined_belief / denominator
        else:
            final_confidence = 0.5  # Neutral when no evidence
        
        # Ensure result stays in [0,1]
        final_confidence = max(0.0, min(1.0, final_confidence))
        
        return ConfidenceScore(
            value=final_confidence,
            evidence_weight=max(conf1.evidence_weight, conf2.evidence_weight) + 1,
            propagation_method=PropagationMethod.DEMPSTER_SHAFER,
            metadata={
                "combination_method": "dempster_shafer",
                "combined_belief": combined_belief,
                "combined_doubt": combined_doubt,
                "combined_uncertainty": combined_uncertainty,
                "conflict": conflict
            }
        )
    
    def get_method_name(self) -> str:
        return "dempster_shafer"


class MinMaxCombiner(ConfidenceCombiner):
    """Min-Max combination method (conservative approach)"""
    
    def combine(self, conf1: ConfidenceScore, conf2: ConfidenceScore) -> ConfidenceScore:
        """Combine using min-max approach (conservative)."""
        # Conservative approach: take minimum for combined confidence
        # But consider evidence weights for final decision
        
        if conf1.evidence_weight > conf2.evidence_weight * 2:
            # Much stronger evidence in first score
            combined_value = conf1.value * 0.8 + conf2.value * 0.2
        elif conf2.evidence_weight > conf1.evidence_weight * 2:
            # Much stronger evidence in second score  
            combined_value = conf1.value * 0.2 + conf2.value * 0.8
        else:
            # Similar evidence weights, use conservative minimum
            combined_value = min(conf1.value, conf2.value)
        
        return ConfidenceScore(
            value=combined_value,
            evidence_weight=conf1.evidence_weight + conf2.evidence_weight,
            propagation_method=PropagationMethod.MIN_MAX,
            metadata={
                "combination_method": "min_max",
                "conservative_minimum": min(conf1.value, conf2.value),
                "evidence_weight_ratio": conf1.evidence_weight / max(conf2.evidence_weight, 1)
            }
        )
    
    def get_method_name(self) -> str:
        return "min_max"


class CombinationMethodFactory:
    """Factory for creating confidence combination methods"""
    
    _combiners = {
        PropagationMethod.BAYESIAN_EVIDENCE_POWER: BayesianCombiner(),
        PropagationMethod.DEMPSTER_SHAFER: DempsterShaferCombiner(), 
        PropagationMethod.MIN_MAX: MinMaxCombiner()
    }
    
    @classmethod
    def get_combiner(cls, method: PropagationMethod) -> ConfidenceCombiner:
        """Get combiner for specified propagation method"""
        if method not in cls._combiners:
            logger.warning(f"Unknown propagation method {method}, using Bayesian")
            method = PropagationMethod.BAYESIAN_EVIDENCE_POWER
        
        return cls._combiners[method]
    
    @classmethod
    def combine_scores(cls, conf1: ConfidenceScore, conf2: ConfidenceScore, 
                      method: PropagationMethod = None) -> ConfidenceScore:
        """Combine two confidence scores using specified or default method"""
        
        # Use method from first score if not specified
        if method is None:
            method = conf1.propagation_method
        
        combiner = cls.get_combiner(method)
        
        try:
            result = combiner.combine(conf1, conf2)
            logger.debug(f"Combined {conf1.value:.3f} and {conf2.value:.3f} using {method} → {result.value:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Error combining confidence scores with {method}: {e}")
            # Fallback to simple average
            return ConfidenceScore(
                value=(conf1.value + conf2.value) / 2,
                evidence_weight=conf1.evidence_weight + conf2.evidence_weight,
                propagation_method=method,
                metadata={
                    "combination_method": "fallback_average",
                    "error": str(e)
                }
            )