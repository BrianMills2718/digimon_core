"""
Confidence Scoring Data Models

Core data structures for confidence scoring including the main ConfidenceScore class
and supporting enums and models.
"""

from pydantic import BaseModel, confloat, PositiveInt, Field, validator
from typing import Literal, Dict, Any, Optional, Tuple, List
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
        description="Type of distribution if aggregate: 'normal', 'beta', 'uniform', 'custom'"
    )
    
    distribution_parameters: Optional[Dict[str, float]] = Field(
        default=None,
        description="Parameters for the distribution (e.g., {'mean': 0.7, 'std': 0.1})"
    )
    
    # Provenance and context
    source: Optional[str] = Field(
        default=None,
        description="Source of this confidence assessment"
    )
    
    propagation_method: PropagationMethod = Field(
        default=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
        description="Method to use when combining this confidence with others"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for this confidence assessment"
    )
    
    @validator('confidence_range')
    def validate_confidence_range(cls, v, values):
        """Validate that confidence range is properly ordered and within bounds."""
        if v is not None:
            min_val, max_val = v
            if not (0.0 <= min_val <= max_val <= 1.0):
                raise ValueError("Confidence range must be [min, max] where 0 <= min <= max <= 1")
            
            # Check that main value falls within range if both are provided
            if 'value' in values and values['value'] is not None:
                main_value = values['value']
                if not (min_val <= main_value <= max_val):
                    raise ValueError(f"Main confidence value {main_value} must fall within range [{min_val}, {max_val}]")
        
        return v
    
    @validator('data_coverage')
    def validate_data_coverage(cls, v):
        """Validate data coverage is between 0 and 1."""
        if not (0.0 <= v <= 1.0):
            raise ValueError("Data coverage must be between 0.0 and 1.0")
        return v
    
    def get_confidence_range(self) -> Tuple[float, float]:
        """Get confidence range, using default if not specified."""
        if self.confidence_range is not None:
            return self.confidence_range
        
        # Default range: ±0.05 around main value, clamped to [0,1]
        margin = 0.05
        min_val = max(0.0, self.value - margin)
        max_val = min(1.0, self.value + margin)
        return (min_val, max_val)
    
    def get_cerqual_assessment(self) -> Dict[str, Optional[float]]:
        """Get CERQual assessment dimensions."""
        return {
            "methodological_limitations": self.methodological_limitations,
            "relevance": self.relevance,
            "coherence": self.coherence,
            "adequacy_of_data": self.adequacy_of_data
        }
    
    def to_quality_tier(self) -> str:
        """Convert confidence to quality tier."""
        if self.value >= 0.8:
            return "high"
        elif self.value >= 0.6:
            return "medium"
        else:
            return "low"
    
    def __str__(self) -> str:
        range_min, range_max = self.get_confidence_range()
        return f"ConfidenceScore(value={self.value:.3f}, range=[{range_min:.3f}, {range_max:.3f}], evidence_weight={self.evidence_weight})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }