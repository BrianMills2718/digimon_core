"""
Confidence Scoring Module

Decomposed confidence scoring components implementing ADR-004 Normative Confidence Score Ontology.
Provides standardized confidence measurement with mathematical rigor and propagation semantics.
"""

from .data_models import (
    PropagationMethod,
    ConfidenceScore
)

from .combination_methods import (
    ConfidenceCombiner,
    BayesianCombiner,
    DempsterShaferCombiner,
    MinMaxCombiner,
    CombinationMethodFactory
)

from .temporal_range_methods import (
    TemporalDecayProcessor,
    RangeProcessor,
    TemporalRangeManager
)

from .cerqual_assessment import (
    CERQualProcessor,
    CERQualAssessment,
    CERQualCalculator
)

from .confidence_calculator import (
    ConfidenceCalculator,
    BaseCalculator,
    DomainSpecificCalculator
)

from .factory_methods import (
    ConfidenceFactory,
    create_high_confidence,
    create_medium_confidence,
    create_low_confidence
)

__all__ = [
    # Core data models
    "PropagationMethod",
    "ConfidenceScore",
    
    # Combination methods
    "ConfidenceCombiner",
    "BayesianCombiner",
    "DempsterShaferCombiner", 
    "MinMaxCombiner",
    "CombinationMethodFactory",
    
    # Temporal and range processing
    "TemporalDecayProcessor",
    "RangeProcessor",
    "TemporalRangeManager",
    
    # CERQual assessment
    "CERQualProcessor",
    "CERQualAssessment",
    "CERQualCalculator",
    
    # Calculators
    "ConfidenceCalculator",
    "BaseCalculator",
    "DomainSpecificCalculator",
    
    # Factory methods
    "ConfidenceFactory",
    "create_high_confidence",
    "create_medium_confidence", 
    "create_low_confidence"
]