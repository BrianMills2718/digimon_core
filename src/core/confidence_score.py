"""ConfidenceScore Implementation - ADR-004 Normative Confidence Score Ontology

Implements the normative confidence scoring system for KGAS tools according
to ADR-004 specifications with Bayesian evidence power as the default.

UPDATED: Supports uncertainty framework with confidence ranges and CERQual assessment.
"""

from pydantic import BaseModel, confloat, PositiveInt, Field
from typing import Literal, Dict, Any, Optional, Tuple, List, Callable
from enum import Enum
from datetime import datetime


class PropagationMethod(str, Enum):
    """Confidence propagation methods supported by the system."""
    BAYESIAN_EVIDENCE_POWER = "bayesian_evidence_power"
    DEMPSTER_SHAFER = "dempster_shafer"
    MIN_MAX = "min_max"


class ConfidenceScore(BaseModel):
    """Normative confidence score implementation per ADR-004.
    
    Provides a standardized approach to confidence measurement across
    all KGAS tools with mathematical rigor and propagation semantics.
    
    ENHANCED: Now supports uncertainty framework with confidence ranges,
    CERQual assessment, and advanced uncertainty propagation.
    """
    
    # Core confidence - now supports ranges
    value: confloat(ge=0.0, le=1.0) = Field(
        description="Primary confidence value between 0.0 (no confidence) and 1.0 (complete confidence)"
    )
    
    confidence_range: Optional[Tuple[float, float]] = Field(
        default=None,
        description="Confidence range [min, max] for uncertainty representation. If None, uses value ± 0.05"
    )
    
    evidence_weight: PositiveInt = Field(
        description="Number of independent evidence sources supporting this confidence"
    )
    
    # CERQual Assessment Dimensions
    methodological_limitations: Optional[float] = Field(
        default=None,
        description="CERQual: Quality of the extraction/analysis method (0.0-1.0)"
    )
    
    relevance: Optional[float] = Field(
        default=None,
        description="CERQual: Applicability of evidence to the context (0.0-1.0)"
    )
    
    coherence: Optional[float] = Field(
        default=None,
        description="CERQual: Internal consistency of the evidence (0.0-1.0)"
    )
    
    adequacy_of_data: Optional[float] = Field(
        default=None,
        description="CERQual: Sufficiency of supporting evidence (0.0-1.0)"
    )
    
    # Temporal aspects
    assessment_time: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="When this confidence was assessed"
    )
    
    validity_window: Optional[Tuple[datetime, Optional[datetime]]] = Field(
        default=None,
        description="Time window when this confidence is valid [start, end]. None end = indefinite"
    )
    
    temporal_decay_function: Optional[str] = Field(
        default=None,
        description="Function name for temporal confidence decay: 'linear', 'exponential', 'step', 'none'"
    )
    
    # Missing data handling
    measurement_type: Literal["measured", "imputed", "bounded", "unknown"] = Field(
        default="measured",
        description="Type of measurement: measured=direct, imputed=estimated, bounded=range, unknown=unclear"
    )
    
    data_coverage: float = Field(
        default=1.0,
        description="Fraction of needed data available (0.0-1.0)"
    )
    
    # Distribution information (for aggregates)
    is_aggregate: bool = Field(
        default=False,
        description="Whether this confidence represents an aggregate of multiple sources"
    )
    
    distribution_type: Optional[str] = Field(
        default=None,
        description="Distribution shape: 'unimodal', 'bimodal', 'uniform', 'polarized'"
    )
    
    subgroup_params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Parameters for subgroup distributions if aggregate"
    )
    
    # Dependencies
    depends_on: Optional[List[str]] = Field(
        default=None,
        description="List of other confidence IDs this depends on"
    )
    
    context_strength: Optional[float] = Field(
        default=None,
        description="Strength of contextual factors affecting confidence (0.0-1.0)"
    )
    
    propagation_method: PropagationMethod = Field(
        default=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
        description="Method used for confidence propagation in tool chains"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional context about confidence calculation"
    )
    
    @classmethod
    def create_high_confidence(cls, value: float = 0.9, evidence_weight: int = 5) -> "ConfidenceScore":
        """Create a high confidence score with strong evidence support."""
        return cls(
            value=min(value, 1.0),
            evidence_weight=evidence_weight,
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            metadata={"quality_tier": "HIGH"}
        )
    
    @classmethod
    def create_medium_confidence(cls, value: float = 0.7, evidence_weight: int = 3) -> "ConfidenceScore":
        """Create a medium confidence score with moderate evidence support."""
        return cls(
            value=value,
            evidence_weight=evidence_weight,
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            metadata={"quality_tier": "MEDIUM"}
        )
    
    @classmethod
    def create_low_confidence(cls, value: float = 0.4, evidence_weight: int = 1) -> "ConfidenceScore":
        """Create a low confidence score with minimal evidence support."""
        return cls(
            value=value,
            evidence_weight=evidence_weight,
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            metadata={"quality_tier": "LOW"}
        )
    
    def combine_with(self, other: "ConfidenceScore") -> "ConfidenceScore":
        """Combine this confidence score with another using the specified propagation method."""
        if self.propagation_method != other.propagation_method:
            # Convert both to Bayesian for combination
            return self._bayesian_combine(other)
        
        if self.propagation_method == PropagationMethod.BAYESIAN_EVIDENCE_POWER:
            return self._bayesian_combine(other)
        elif self.propagation_method == PropagationMethod.DEMPSTER_SHAFER:
            return self._dempster_shafer_combine(other)
        elif self.propagation_method == PropagationMethod.MIN_MAX:
            return self._min_max_combine(other)
        else:
            # Fallback to Bayesian
            return self._bayesian_combine(other)
    
    def _bayesian_combine(self, other: "ConfidenceScore") -> "ConfidenceScore":
        """Combine using Bayesian evidence power method."""
        # Bayesian update: P(H|E1,E2) = P(H|E1) * P(E2|H) / P(E2)
        # Simplified to weighted geometric mean with evidence weighting
        
        total_evidence = self.evidence_weight + other.evidence_weight
        self_weight = self.evidence_weight / total_evidence
        other_weight = other.evidence_weight / total_evidence
        
        # Geometric mean weighted by evidence
        combined_value = (self.value ** self_weight) * (other.value ** other_weight)
        
        return ConfidenceScore(
            value=combined_value,
            evidence_weight=total_evidence,
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            metadata={
                "combined_from": [self.metadata, other.metadata],
                "combination_method": "bayesian_evidence_power"
            }
        )
    
    def _dempster_shafer_combine(self, other: "ConfidenceScore") -> "ConfidenceScore":
        """Combine using Dempster-Shafer theory."""
        # Basic Dempster-Shafer combination rule
        # m12(A) = (m1(A)*m2(A) + m1(A)*m2(Θ) + m1(Θ)*m2(A)) / (1 - K)
        # Where K is the conflict mass
        
        # Convert confidence to basic probability assignment
        m1_belief = self.value
        m1_uncertainty = 1.0 - self.value
        m2_belief = other.value  
        m2_uncertainty = 1.0 - other.value
        
        # Calculate combined belief
        combined_belief = m1_belief * m2_belief + m1_belief * m2_uncertainty + m1_uncertainty * m2_belief
        conflict = m1_belief * (1.0 - m2_belief - m2_uncertainty)  # Simplified conflict calculation
        
        # Normalize by (1 - conflict)
        if conflict < 1.0:
            combined_value = combined_belief / (1.0 - conflict)
        else:
            combined_value = max(self.value, other.value)  # Fallback
        
        return ConfidenceScore(
            value=min(combined_value, 1.0),
            evidence_weight=max(self.evidence_weight, other.evidence_weight),
            propagation_method=PropagationMethod.DEMPSTER_SHAFER,
            metadata={
                "combined_from": [self.metadata, other.metadata],
                "combination_method": "dempster_shafer",
                "conflict_mass": conflict
            }
        )
    
    def _min_max_combine(self, other: "ConfidenceScore") -> "ConfidenceScore":
        """Combine using conservative min-max approach."""
        # Take minimum confidence (conservative) with maximum evidence
        combined_value = min(self.value, other.value)
        combined_evidence = max(self.evidence_weight, other.evidence_weight)
        
        return ConfidenceScore(
            value=combined_value,
            evidence_weight=combined_evidence,
            propagation_method=PropagationMethod.MIN_MAX,
            metadata={
                "combined_from": [self.metadata, other.metadata],
                "combination_method": "min_max"
            }
        )
    
    def decay(self, decay_factor: float = 0.95) -> "ConfidenceScore":
        """Apply confidence decay for temporal or chain propagation."""
        return ConfidenceScore(
            value=self.value * decay_factor,
            evidence_weight=max(1, self.evidence_weight - 1),  # Reduce evidence weight
            propagation_method=self.propagation_method,
            metadata={
                **self.metadata,
                "decay_applied": decay_factor,
                "original_value": self.value
            }
        )
    
    def to_quality_tier(self) -> str:
        """Convert confidence score to quality tier classification."""
        if self.value >= 0.8 and self.evidence_weight >= 3:
            return "HIGH"
        elif self.value >= 0.6 and self.evidence_weight >= 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def __str__(self) -> str:
        return f"ConfidenceScore(value={self.value:.3f}, evidence={self.evidence_weight}, method={self.propagation_method.value})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    # Enhanced methods for uncertainty framework
    
    def get_confidence_range(self) -> Tuple[float, float]:
        """Get confidence range - returns specified range or default around value"""
        if self.confidence_range:
            return self.confidence_range
        else:
            # Default range of ±0.05 around value
            margin = 0.05
            return (max(0.0, self.value - margin), min(1.0, self.value + margin))
    
    def get_cerqual_assessment(self) -> Dict[str, Optional[float]]:
        """Get CERQual 4-dimension assessment"""
        return {
            "methodological_limitations": self.methodological_limitations,
            "relevance": self.relevance,
            "coherence": self.coherence,
            "adequacy_of_data": self.adequacy_of_data
        }
    
    def calculate_cerqual_combined(self) -> float:
        """Calculate combined confidence from CERQual dimensions using geometric mean"""
        dimensions = [d for d in self.get_cerqual_assessment().values() if d is not None]
        if not dimensions:
            return self.value  # Fall back to original value
        
        # Geometric mean of available dimensions
        from math import pow
        product = 1.0
        for dim in dimensions:
            product *= dim
        return pow(product, 1.0 / len(dimensions))
    
    def apply_temporal_decay(self, current_time: Optional[datetime] = None) -> "ConfidenceScore":
        """Apply temporal decay based on assessment time and decay function"""
        if not self.temporal_decay_function or self.temporal_decay_function == "none":
            return self
        
        if current_time is None:
            current_time = datetime.now()
        
        if not self.assessment_time:
            return self  # No temporal information
        
        # Calculate time difference in days
        time_diff = (current_time - self.assessment_time).total_seconds() / (24 * 3600)
        
        # Apply decay function
        if self.temporal_decay_function == "linear":
            # Linear decay: 1% per day
            decay_factor = max(0.0, 1.0 - (time_diff * 0.01))
        elif self.temporal_decay_function == "exponential":
            # Exponential decay: half-life of 30 days
            import math
            decay_factor = math.exp(-time_diff / 30.0)
        elif self.temporal_decay_function == "step":
            # Step decay: sharp drop after validity window
            if self.validity_window and self.validity_window[1]:
                if current_time > self.validity_window[1]:
                    decay_factor = 0.1  # Sharp drop
                else:
                    decay_factor = 1.0  # No decay within window
            else:
                decay_factor = 1.0
        else:
            decay_factor = 1.0
        
        # Create new ConfidenceScore with temporal decay applied
        new_value = self.value * decay_factor
        new_range = None
        if self.confidence_range:
            new_range = (self.confidence_range[0] * decay_factor, 
                        self.confidence_range[1] * decay_factor)
        
        return ConfidenceScore(
            value=new_value,
            confidence_range=new_range,
            evidence_weight=self.evidence_weight,
            methodological_limitations=self.methodological_limitations,
            relevance=self.relevance,
            coherence=self.coherence,
            adequacy_of_data=self.adequacy_of_data,
            assessment_time=current_time,
            validity_window=self.validity_window,
            temporal_decay_function=self.temporal_decay_function,
            measurement_type=self.measurement_type,
            data_coverage=self.data_coverage,
            is_aggregate=self.is_aggregate,
            distribution_type=self.distribution_type,
            subgroup_params=self.subgroup_params,
            depends_on=self.depends_on,
            context_strength=self.context_strength,
            propagation_method=self.propagation_method,
            metadata={
                **self.metadata,
                "temporal_decay_applied": decay_factor,
                "decay_days": time_diff
            }
        )
    
    def add_cerqual_evidence(self, 
                           methodological_limitations: Optional[float] = None,
                           relevance: Optional[float] = None,
                           coherence: Optional[float] = None,
                           adequacy_of_data: Optional[float] = None) -> "ConfidenceScore":
        """Add CERQual evidence dimensions and recalculate combined confidence"""
        
        # Update CERQual dimensions
        new_ml = methodological_limitations if methodological_limitations is not None else self.methodological_limitations
        new_rel = relevance if relevance is not None else self.relevance
        new_coh = coherence if coherence is not None else self.coherence
        new_ad = adequacy_of_data if adequacy_of_data is not None else self.adequacy_of_data
        
        # Calculate new combined value from CERQual dimensions
        dimensions = [d for d in [new_ml, new_rel, new_coh, new_ad] if d is not None]
        if dimensions:
            from math import pow
            product = 1.0
            for dim in dimensions:
                product *= dim
            new_value = pow(product, 1.0 / len(dimensions))
        else:
            new_value = self.value
        
        return ConfidenceScore(
            value=new_value,
            confidence_range=self.confidence_range,
            evidence_weight=self.evidence_weight,
            methodological_limitations=new_ml,
            relevance=new_rel,
            coherence=new_coh,
            adequacy_of_data=new_ad,
            assessment_time=self.assessment_time,
            validity_window=self.validity_window,
            temporal_decay_function=self.temporal_decay_function,
            measurement_type=self.measurement_type,
            data_coverage=self.data_coverage,
            is_aggregate=self.is_aggregate,
            distribution_type=self.distribution_type,
            subgroup_params=self.subgroup_params,
            depends_on=self.depends_on,
            context_strength=self.context_strength,
            propagation_method=self.propagation_method,
            metadata={
                **self.metadata,
                "cerqual_updated": True
            }
        )
    
    def set_confidence_range(self, min_confidence: float, max_confidence: float) -> "ConfidenceScore":
        """Set explicit confidence range for uncertainty representation"""
        if not (0.0 <= min_confidence <= max_confidence <= 1.0):
            raise ValueError("Confidence range must be between 0.0 and 1.0 with min <= max")
        
        # Update value to be midpoint of range
        new_value = (min_confidence + max_confidence) / 2.0
        
        return ConfidenceScore(
            value=new_value,
            confidence_range=(min_confidence, max_confidence),
            evidence_weight=self.evidence_weight,
            methodological_limitations=self.methodological_limitations,
            relevance=self.relevance,
            coherence=self.coherence,
            adequacy_of_data=self.adequacy_of_data,
            assessment_time=self.assessment_time,
            validity_window=self.validity_window,
            temporal_decay_function=self.temporal_decay_function,
            measurement_type=self.measurement_type,
            data_coverage=self.data_coverage,
            is_aggregate=self.is_aggregate,
            distribution_type=self.distribution_type,
            subgroup_params=self.subgroup_params,
            depends_on=self.depends_on,
            context_strength=self.context_strength,
            propagation_method=self.propagation_method,
            metadata={
                **self.metadata,
                "range_explicitly_set": True
            }
        )
    
    def combine_with_range_preservation(self, other: "ConfidenceScore") -> "ConfidenceScore":
        """Combine confidence scores while preserving uncertainty ranges"""
        # Get ranges from both scores
        self_range = self.get_confidence_range()
        other_range = other.get_confidence_range()
        
        # Conservative range combination (intersection for high confidence, union for low)
        if self.value >= 0.7 and other.value >= 0.7:
            # High confidence: take intersection (conservative)
            combined_min = max(self_range[0], other_range[0])
            combined_max = min(self_range[1], other_range[1])
        else:
            # Lower confidence: take union (preserve uncertainty)
            combined_min = min(self_range[0], other_range[0])
            combined_max = max(self_range[1], other_range[1])
        
        # Ensure valid range
        if combined_min > combined_max:
            combined_min, combined_max = combined_max, combined_min
        
        # Combine using existing method
        base_combined = self.combine_with(other)
        
        # Override with range-aware combination
        return ConfidenceScore(
            value=(combined_min + combined_max) / 2.0,
            confidence_range=(combined_min, combined_max),
            evidence_weight=base_combined.evidence_weight,
            methodological_limitations=None,  # Would need sophisticated combination
            relevance=None,
            coherence=None,
            adequacy_of_data=None,
            assessment_time=datetime.now(),
            validity_window=None,
            temporal_decay_function=self.temporal_decay_function,
            measurement_type="measured",
            data_coverage=min(self.data_coverage, other.data_coverage),
            is_aggregate=True,
            distribution_type="combined",
            subgroup_params=None,
            depends_on=(self.depends_on or []) + (other.depends_on or []),
            context_strength=None,
            propagation_method=self.propagation_method,
            metadata={
                **base_combined.metadata,
                "range_preservation_used": True,
                "combined_from_ranges": (self_range, other_range)
            }
        )
    
    @classmethod
    def create_with_cerqual(cls, 
                          methodological_limitations: float,
                          relevance: float, 
                          coherence: float,
                          adequacy_of_data: float,
                          evidence_weight: int = 1,
                          confidence_range: Optional[Tuple[float, float]] = None) -> "ConfidenceScore":
        """Create ConfidenceScore directly from CERQual assessment"""
        
        # Calculate combined value from CERQual dimensions using geometric mean
        from math import pow
        combined_value = pow(methodological_limitations * relevance * coherence * adequacy_of_data, 0.25)
        
        # Set default range if not provided
        if confidence_range is None:
            margin = 0.1  # Larger margin for CERQual-based scores
            confidence_range = (max(0.0, combined_value - margin), min(1.0, combined_value + margin))
        
        return cls(
            value=combined_value,
            confidence_range=confidence_range,
            evidence_weight=evidence_weight,
            methodological_limitations=methodological_limitations,
            relevance=relevance,
            coherence=coherence,
            adequacy_of_data=adequacy_of_data,
            assessment_time=datetime.now(),
            measurement_type="measured",
            data_coverage=1.0,
            metadata={"created_from_cerqual": True}
        )


class ConfidenceCalculator:
    """Utility class for calculating confidence scores from various inputs."""
    
    @staticmethod
    def from_spacy_confidence(spacy_score: float, entity_count: int = 1) -> ConfidenceScore:
        """Create confidence score from SpaCy NER confidence."""
        return ConfidenceScore(
            value=spacy_score,
            evidence_weight=min(entity_count, 5),  # Cap at 5 for evidence weight
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            metadata={"source": "spacy_ner", "entity_count": entity_count}
        )
    
    @staticmethod
    def from_llm_response(llm_confidence: Optional[float], token_count: int, model_name: str) -> ConfidenceScore:
        """Create confidence score from LLM response."""
        # If no explicit confidence provided, estimate from token count and model
        if llm_confidence is None:
            # Heuristic: longer responses tend to be more confident
            estimated_confidence = min(0.8, 0.3 + (token_count / 1000) * 0.5)
        else:
            estimated_confidence = llm_confidence
        
        # Evidence weight based on model capability and response length
        evidence_weight = 1
        if "gpt-4" in model_name.lower() or "gemini" in model_name.lower():
            evidence_weight = 3
        elif token_count > 100:
            evidence_weight = 2
        
        return ConfidenceScore(
            value=estimated_confidence,
            evidence_weight=evidence_weight,
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            metadata={
                "source": "llm_response",
                "model_name": model_name,
                "token_count": token_count,
                "explicit_confidence": llm_confidence is not None
            }
        )
    
    @staticmethod
    def from_vector_similarity(similarity_score: float, vector_dimension: int) -> ConfidenceScore:
        """Create confidence score from vector similarity."""
        # Higher dimensional vectors tend to be more reliable
        evidence_weight = min(5, max(1, vector_dimension // 100))
        
        return ConfidenceScore(
            value=similarity_score,
            evidence_weight=evidence_weight,
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            metadata={
                "source": "vector_similarity",
                "vector_dimension": vector_dimension,
                "similarity_score": similarity_score
            }
        )
    
    @staticmethod
    def from_graph_centrality(centrality_score: float, node_degree: int) -> ConfidenceScore:
        """Create confidence score from graph centrality measures."""
        # Higher degree nodes in graph tend to be more reliable
        evidence_weight = min(5, max(1, node_degree // 3))
        
        # Normalize centrality to [0,1] if needed
        normalized_score = min(1.0, centrality_score)
        
        return ConfidenceScore(
            value=normalized_score,
            evidence_weight=evidence_weight,
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            metadata={
                "source": "graph_centrality",
                "centrality_score": centrality_score,
                "node_degree": node_degree
            }
        )
    
    # Transformation-specific uncertainty calculators
    
    @staticmethod
    def for_text_to_argument_extraction(claim_confidence: float, 
                                      warrant_confidence: float,
                                      data_confidence: float,
                                      method_quality: float = 0.8) -> ConfidenceScore:
        """Calculate confidence for text → Toulmin argument extraction"""
        
        # CERQual assessment for argument extraction
        methodological_limitations = method_quality  # Quality of NLP/extraction method
        relevance = min(claim_confidence, 1.0)  # How relevant is extracted claim
        coherence = (warrant_confidence + data_confidence) / 2.0  # Internal consistency
        adequacy_of_data = min(1.0, (claim_confidence + warrant_confidence + data_confidence) / 3.0)
        
        return ConfidenceScore.create_with_cerqual(
            methodological_limitations=methodological_limitations,
            relevance=relevance,
            coherence=coherence,
            adequacy_of_data=adequacy_of_data,
            evidence_weight=3,  # Argument extraction uses multiple evidence sources
            confidence_range=(
                max(0.0, adequacy_of_data - 0.15),
                min(1.0, adequacy_of_data + 0.1)
            )
        )
    
    @staticmethod
    def for_sentiment_attitude_mapping(sentiment_strength: float,
                                     attitude_object_clarity: float,
                                     linguistic_indicators: int,
                                     context_ambiguity: float = 0.2) -> ConfidenceScore:
        """Calculate confidence for text → sentiment-attitude object mapping"""
        
        # CERQual assessment for sentiment mapping
        methodological_limitations = 0.85 - context_ambiguity  # Affected by ambiguity
        relevance = attitude_object_clarity  # How clearly is attitude object identified
        coherence = min(1.0, sentiment_strength)  # Consistency of sentiment indicators
        adequacy_of_data = min(1.0, linguistic_indicators / 3.0)  # Sufficient indicators
        
        return ConfidenceScore.create_with_cerqual(
            methodological_limitations=methodological_limitations,
            relevance=relevance,
            coherence=coherence,
            adequacy_of_data=adequacy_of_data,
            evidence_weight=max(1, linguistic_indicators),
            confidence_range=(
                max(0.0, sentiment_strength - 0.2),
                min(1.0, sentiment_strength + 0.1)
            )
        )
    
    @staticmethod
    def for_belief_network_extraction(belief_clarity: float,
                                    relationship_strength: float,
                                    logical_consistency: float,
                                    implicit_content_ratio: float = 0.3) -> ConfidenceScore:
        """Calculate confidence for text → belief relationship networks"""
        
        # CERQual assessment for belief extraction
        methodological_limitations = 0.8 - (implicit_content_ratio * 0.3)  # Implicit content reduces reliability
        relevance = belief_clarity  # How clearly are beliefs stated
        coherence = logical_consistency  # Internal logical consistency
        adequacy_of_data = relationship_strength  # Strength of relationship evidence
        
        return ConfidenceScore.create_with_cerqual(
            methodological_limitations=methodological_limitations,
            relevance=relevance,
            coherence=coherence,
            adequacy_of_data=adequacy_of_data,
            evidence_weight=2,  # Belief extraction is moderately evidenced
            confidence_range=(
                max(0.0, logical_consistency - 0.25),
                min(1.0, logical_consistency + 0.15)
            )
        )
    
    @staticmethod
    def for_individual_to_community_aggregation(sample_size: int,
                                              representativeness: float,
                                              temporal_stability: float,
                                              consensus_level: float) -> ConfidenceScore:
        """Calculate confidence for individual → community pattern aggregation"""
        
        # Sample size affects adequacy
        sample_adequacy = min(1.0, sample_size / 100.0)  # 100+ for full adequacy
        
        # CERQual assessment for aggregation
        methodological_limitations = 0.9  # Aggregation methods are well-established
        relevance = representativeness  # How representative is the sample
        coherence = temporal_stability  # Consistency over time
        adequacy_of_data = sample_adequacy  # Sufficient sample size
        
        return ConfidenceScore.create_with_cerqual(
            methodological_limitations=methodological_limitations,
            relevance=relevance,
            coherence=coherence,
            adequacy_of_data=adequacy_of_data,
            evidence_weight=min(5, max(1, sample_size // 20)),  # Evidence weight from sample size
            confidence_range=(
                max(0.0, consensus_level - 0.2),
                min(1.0, consensus_level + 0.1)
            )
        )
    
    @staticmethod
    def for_psychological_state_inference(explicit_indicators: int,
                                        context_richness: float,
                                        inference_depth: int,
                                        cultural_familiarity: float = 0.8) -> ConfidenceScore:
        """Calculate confidence for text → cognitive/emotional state inference"""
        
        # Inference depth affects reliability (deeper = less reliable)
        depth_penalty = max(0.0, 1.0 - (inference_depth * 0.2))
        
        # CERQual assessment for psychological inference
        methodological_limitations = 0.7 * cultural_familiarity * depth_penalty  # Cultural and depth limitations
        relevance = context_richness  # Richness of contextual information
        coherence = min(1.0, explicit_indicators / 2.0)  # Explicit indicators provide coherence
        adequacy_of_data = min(1.0, (explicit_indicators + context_richness) / 2.0)
        
        return ConfidenceScore.create_with_cerqual(
            methodological_limitations=methodological_limitations,
            relevance=relevance,
            coherence=coherence,
            adequacy_of_data=adequacy_of_data,
            evidence_weight=explicit_indicators,
            confidence_range=(
                max(0.0, adequacy_of_data - 0.3),  # Large uncertainty for psychological inference
                min(1.0, adequacy_of_data + 0.2)
            )
        )
    
    @staticmethod
    def create_range_only(min_confidence: float, max_confidence: float,
                         measurement_type: str = "bounded",
                         evidence_weight: int = 1) -> ConfidenceScore:
        """Create ConfidenceScore with only range information (for bounded/imputed data)"""
        if not (0.0 <= min_confidence <= max_confidence <= 1.0):
            raise ValueError("Confidence range must be between 0.0 and 1.0 with min <= max")
        
        midpoint = (min_confidence + max_confidence) / 2.0
        
        return ConfidenceScore(
            value=midpoint,
            confidence_range=(min_confidence, max_confidence),
            evidence_weight=evidence_weight,
            measurement_type=measurement_type,
            data_coverage=0.5 if measurement_type == "imputed" else 1.0,
            metadata={
                "range_based_creation": True,
                "range_width": max_confidence - min_confidence
            }
        )


# Utility functions for common confidence operations
def combine_confidence_scores(*scores: ConfidenceScore) -> ConfidenceScore:
    """Combine multiple confidence scores into a single score."""
    if not scores:
        return ConfidenceScore.create_low_confidence()
    
    if len(scores) == 1:
        return scores[0]
    
    result = scores[0]
    for score in scores[1:]:
        result = result.combine_with(score)
    
    return result


def weighted_confidence_average(confidence_scores: list[ConfidenceScore], weights: list[float]) -> ConfidenceScore:
    """Calculate weighted average of confidence scores with range preservation."""
    if not confidence_scores or not weights or len(confidence_scores) != len(weights):
        return ConfidenceScore.create_low_confidence()
    
    # Normalize weights
    total_weight = sum(weights)
    if total_weight == 0:
        return ConfidenceScore.create_low_confidence()
    
    normalized_weights = [w / total_weight for w in weights]
    
    # Calculate weighted average of values
    weighted_value = sum(score.value * weight for score, weight in zip(confidence_scores, normalized_weights))
    
    # Calculate weighted average of ranges
    weighted_ranges = [score.get_confidence_range() for score in confidence_scores]
    weighted_min = sum(range_tuple[0] * weight for range_tuple, weight in zip(weighted_ranges, normalized_weights))
    weighted_max = sum(range_tuple[1] * weight for range_tuple, weight in zip(weighted_ranges, normalized_weights))
    
    total_evidence = sum(score.evidence_weight for score in confidence_scores)
    
    return ConfidenceScore(
        value=weighted_value,
        confidence_range=(weighted_min, weighted_max),
        evidence_weight=total_evidence,
        is_aggregate=True,
        distribution_type="weighted_average",
        propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
        metadata={
            "source": "weighted_average",
            "weights": weights,
            "component_scores": len(confidence_scores),
            "range_preserved": True
        }
    )


def create_distribution_preserving_aggregate(confidence_scores: list[ConfidenceScore], 
                                           preserve_polarization: bool = True) -> ConfidenceScore:
    """Create aggregate that preserves distributional information"""
    if not confidence_scores:
        return ConfidenceScore.create_low_confidence()
    
    if len(confidence_scores) == 1:
        return confidence_scores[0]
    
    # Calculate distribution statistics
    values = [score.value for score in confidence_scores]
    ranges = [score.get_confidence_range() for score in confidence_scores]
    
    # Central tendency
    mean_value = sum(values) / len(values)
    
    # Distribution shape analysis
    from statistics import stdev, median
    if len(values) > 1:
        variance = stdev(values) ** 2
        median_value = median(values)
    else:
        variance = 0.0
        median_value = values[0]
    
    # Detect polarization (bimodal distribution)
    polarization_detected = False
    if preserve_polarization and len(values) >= 4:
        # Simple polarization detection: check for values clustering at extremes
        low_cluster = [v for v in values if v < 0.4]
        high_cluster = [v for v in values if v > 0.6]
        middle_cluster = [v for v in values if 0.4 <= v <= 0.6]
        
        if len(low_cluster) > 0 and len(high_cluster) > 0 and len(middle_cluster) < len(values) * 0.3:
            polarization_detected = True
    
    # Determine distribution type
    if polarization_detected:
        distribution_type = "bimodal"
        # For bimodal, use median instead of mean
        aggregate_value = median_value
    elif variance < 0.01:
        distribution_type = "concentrated"
        aggregate_value = mean_value
    elif variance > 0.2:
        distribution_type = "dispersed"
        aggregate_value = mean_value
    else:
        distribution_type = "unimodal"
        aggregate_value = mean_value
    
    # Calculate aggregate range (conservative bounds)
    all_mins = [r[0] for r in ranges]
    all_maxs = [r[1] for r in ranges]
    aggregate_range = (min(all_mins), max(all_maxs))
    
    # Subgroup parameters for bimodal distributions
    subgroup_params = None
    if polarization_detected:
        subgroup_params = {
            "low_cluster": {"mean": sum(low_cluster) / len(low_cluster), "size": len(low_cluster)} if low_cluster else None,
            "high_cluster": {"mean": sum(high_cluster) / len(high_cluster), "size": len(high_cluster)} if high_cluster else None,
            "polarization_index": (len(low_cluster) + len(high_cluster)) / len(values)
        }
    
    total_evidence = sum(score.evidence_weight for score in confidence_scores)
    
    return ConfidenceScore(
        value=aggregate_value,
        confidence_range=aggregate_range,
        evidence_weight=total_evidence,
        is_aggregate=True,
        distribution_type=distribution_type,
        subgroup_params=subgroup_params,
        propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
        metadata={
            "source": "distribution_preserving_aggregate",
            "component_count": len(confidence_scores),
            "variance": variance,
            "polarization_detected": polarization_detected,
            "original_values": values[:10] if len(values) <= 10 else values[:10] + ["...truncated"]
        }
    )