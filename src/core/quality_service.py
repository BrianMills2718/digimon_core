"""T111: Quality Service - Minimal Implementation

Manages confidence scores and quality propagation through pipelines.
Provides quality assessment and tier assignment.

This is a MINIMAL implementation focusing on:
- Basic confidence tracking (0.0-1.0 scale)
- Simple propagation rules
- Quality tier assignment (HIGH/MEDIUM/LOW)
- Confidence degradation modeling

Deferred features:
- Complex aggregation algorithms
- Machine learning quality models
- Advanced uncertainty quantification
- Quality-based filtering optimizations
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import statistics
import math


class QualityTier(Enum):
    """Quality tier classification."""
    HIGH = "HIGH"        # confidence >= 0.8
    MEDIUM = "MEDIUM"    # confidence >= 0.5
    LOW = "LOW"         # confidence < 0.5


@dataclass
class QualityAssessment:
    """Quality assessment for an object."""
    object_ref: str
    confidence: float  # 0.0 to 1.0
    quality_tier: QualityTier
    factors: Dict[str, float]  # Contributing factors
    assessed_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityRule:
    """Rule for quality propagation."""
    rule_id: str
    source_type: str  # Type of operation/tool
    degradation_factor: float  # Factor to multiply confidence by
    min_confidence: float  # Minimum output confidence
    description: str


class QualityService:
    """T111: Quality Service - Confidence management and propagation."""
    
    def __init__(self):
        self.assessments: Dict[str, QualityAssessment] = {}
        self.quality_rules: Dict[str, QualityRule] = {}
        self.confidence_history: Dict[str, List[Tuple[datetime, float]]] = {}
        
        # Initialize default quality rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize standard quality degradation rules."""
        default_rules = [
            QualityRule(
                rule_id="text_extraction",
                source_type="pdf_loader",
                degradation_factor=0.95,  # 5% degradation
                min_confidence=0.1,
                description="Text extraction from PDF"
            ),
            QualityRule(
                rule_id="nlp_processing",
                source_type="spacy_ner", 
                degradation_factor=0.9,   # 10% degradation
                min_confidence=0.1,
                description="NLP entity extraction"
            ),
            QualityRule(
                rule_id="relationship_extraction",
                source_type="relationship_extractor",
                degradation_factor=0.85,  # 15% degradation
                min_confidence=0.1,
                description="Relationship extraction from text"
            ),
            QualityRule(
                rule_id="entity_linking",
                source_type="entity_builder",
                degradation_factor=0.9,   # 10% degradation
                min_confidence=0.1,
                description="Entity creation and linking"
            ),
            QualityRule(
                rule_id="graph_analysis",
                source_type="pagerank",
                degradation_factor=0.95,  # 5% degradation
                min_confidence=0.1,
                description="Graph analysis operations"
            )
        ]
        
        for rule in default_rules:
            self.quality_rules[rule.rule_id] = rule
    
    def assess_confidence(
        self,
        object_ref: str,
        base_confidence: float,
        factors: Dict[str, float] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Assess and record confidence for an object.
        
        Args:
            object_ref: Reference to object being assessed
            base_confidence: Base confidence score (0.0-1.0)
            factors: Contributing factors to confidence
            metadata: Additional assessment metadata
            
        Returns:
            Assessment result with confidence and quality tier
        """
        try:
            # Input validation
            if not (0.0 <= base_confidence <= 1.0):
                return {
                    "status": "error",
                    "error": "Confidence must be between 0.0 and 1.0",
                    "confidence": 0.0
                }
            
            if factors is None:
                factors = {}
            if metadata is None:
                metadata = {}
            
            # Adjust confidence based on factors
            adjusted_confidence = self._apply_confidence_factors(base_confidence, factors)
            
            # Determine quality tier
            quality_tier = self._determine_quality_tier(adjusted_confidence)
            
            # Create assessment
            assessment = QualityAssessment(
                object_ref=object_ref,
                confidence=adjusted_confidence,
                quality_tier=quality_tier,
                factors=factors.copy(),
                metadata=metadata.copy()
            )
            
            # Store assessment
            self.assessments[object_ref] = assessment
            
            # Update confidence history
            if object_ref not in self.confidence_history:
                self.confidence_history[object_ref] = []
            self.confidence_history[object_ref].append((datetime.now(), adjusted_confidence))
            
            # Keep only last 10 confidence values
            if len(self.confidence_history[object_ref]) > 10:
                self.confidence_history[object_ref] = self.confidence_history[object_ref][-10:]
            
            return {
                "status": "success",
                "object_ref": object_ref,
                "confidence": adjusted_confidence,
                "quality_tier": quality_tier.value,
                "factors": factors,
                "assessed_at": assessment.assessed_at.isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to assess confidence: {str(e)}",
                "confidence": 0.0
            }
    
    def _apply_confidence_factors(self, base_confidence: float, factors: Dict[str, float]) -> float:
        """Apply confidence factors to base confidence."""
        if not factors:
            return base_confidence
        
        # Simple weighted average approach
        total_weight = 1.0  # Base confidence has weight 1.0
        weighted_sum = base_confidence * 1.0
        
        for factor_name, factor_value in factors.items():
            # Each factor has weight 0.2
            factor_weight = 0.2
            # Ensure factor value is in valid range
            factor_value = max(0.0, min(1.0, factor_value))
            
            weighted_sum += factor_value * factor_weight
            total_weight += factor_weight
        
        adjusted = weighted_sum / total_weight
        return max(0.0, min(1.0, adjusted))
    
    def _determine_quality_tier(self, confidence: float) -> QualityTier:
        """Determine quality tier based on confidence."""
        if confidence >= 0.8:
            return QualityTier.HIGH
        elif confidence >= 0.5:
            return QualityTier.MEDIUM
        else:
            return QualityTier.LOW
    
    def propagate_confidence(
        self,
        input_refs: List[str],
        operation_type: str,
        boost_factor: float = 1.0
    ) -> float:
        """Propagate confidence from inputs through an operation.
        
        Args:
            input_refs: References to input objects
            operation_type: Type of operation being performed
            boost_factor: Factor to boost/reduce confidence
            
        Returns:
            Propagated confidence score
        """
        try:
            if not input_refs:
                return 0.5  # Default confidence for operations with no inputs
            
            # Get confidence scores for inputs
            input_confidences = []
            for ref in input_refs:
                assessment = self.assessments.get(ref)
                if assessment:
                    input_confidences.append(assessment.confidence)
                else:
                    # Default confidence for unknown objects
                    input_confidences.append(0.7)
            
            # Calculate base propagated confidence
            if len(input_confidences) == 1:
                base_confidence = input_confidences[0]
            else:
                # Use harmonic mean for multiple inputs (more conservative)
                harmonic_mean = len(input_confidences) / sum(1/c for c in input_confidences if c > 0)
                base_confidence = harmonic_mean
            
            # Apply operation-specific degradation
            degradation_factor = self._get_degradation_factor(operation_type)
            propagated_confidence = base_confidence * degradation_factor
            
            # Apply boost factor
            propagated_confidence *= boost_factor
            
            # Apply minimum confidence from rule
            min_confidence = self._get_min_confidence(operation_type)
            propagated_confidence = max(propagated_confidence, min_confidence)
            
            # Ensure valid range
            return max(0.0, min(1.0, propagated_confidence))
            
        except Exception as e:
            # Return conservative confidence on error
            return 0.3
    
    def _get_degradation_factor(self, operation_type: str) -> float:
        """Get degradation factor for operation type."""
        for rule in self.quality_rules.values():
            if rule.source_type == operation_type:
                return rule.degradation_factor
        
        # Default degradation for unknown operations
        return 0.9
    
    def _get_min_confidence(self, operation_type: str) -> float:
        """Get minimum confidence for operation type."""
        for rule in self.quality_rules.values():
            if rule.source_type == operation_type:
                return rule.min_confidence
        
        # Default minimum confidence
        return 0.1
    
    def get_quality_assessment(self, object_ref: str) -> Optional[Dict[str, Any]]:
        """Get quality assessment for an object."""
        try:
            assessment = self.assessments.get(object_ref)
            if not assessment:
                return None
            
            return {
                "object_ref": assessment.object_ref,
                "confidence": assessment.confidence,
                "quality_tier": assessment.quality_tier.value,
                "factors": assessment.factors,
                "assessed_at": assessment.assessed_at.isoformat(),
                "metadata": assessment.metadata
            }
            
        except Exception:
            return None
    
    def get_confidence_trend(self, object_ref: str) -> Dict[str, Any]:
        """Get confidence trend for an object."""
        try:
            if object_ref not in self.confidence_history:
                return {
                    "status": "not_found",
                    "object_ref": object_ref
                }
            
            history = self.confidence_history[object_ref]
            if not history:
                return {
                    "status": "no_data",
                    "object_ref": object_ref
                }
            
            # Calculate trend statistics
            confidences = [conf for _, conf in history]
            trend_data = {
                "object_ref": object_ref,
                "current_confidence": confidences[-1],
                "min_confidence": min(confidences),
                "max_confidence": max(confidences),
                "avg_confidence": statistics.mean(confidences),
                "confidence_std": statistics.stdev(confidences) if len(confidences) > 1 else 0.0,
                "trend_direction": self._calculate_trend_direction(confidences),
                "history_points": len(history),
                "history": [
                    {"timestamp": ts.isoformat(), "confidence": conf}
                    for ts, conf in history
                ]
            }
            
            return {
                "status": "success",
                **trend_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to get trend: {str(e)}"
            }
    
    def _calculate_trend_direction(self, confidences: List[float]) -> str:
        """Calculate trend direction from confidence history."""
        if len(confidences) < 2:
            return "stable"
        
        # Simple linear trend
        n = len(confidences)
        x_vals = list(range(n))
        
        # Calculate slope
        x_mean = statistics.mean(x_vals)
        y_mean = statistics.mean(confidences)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, confidences))
        denominator = sum((x - x_mean) ** 2 for x in x_vals)
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "declining"
        else:
            return "stable"
    
    def filter_by_quality(
        self,
        object_refs: List[str],
        min_tier: QualityTier = QualityTier.LOW,
        min_confidence: float = 0.0
    ) -> List[str]:
        """Filter objects by quality criteria."""
        try:
            filtered = []
            
            for ref in object_refs:
                assessment = self.assessments.get(ref)
                if not assessment:
                    continue
                
                # Check tier requirement
                tier_ok = False
                if min_tier == QualityTier.LOW:
                    tier_ok = True
                elif min_tier == QualityTier.MEDIUM:
                    tier_ok = assessment.quality_tier in [QualityTier.MEDIUM, QualityTier.HIGH]
                elif min_tier == QualityTier.HIGH:
                    tier_ok = assessment.quality_tier == QualityTier.HIGH
                
                # Check confidence requirement
                confidence_ok = assessment.confidence >= min_confidence
                
                if tier_ok and confidence_ok:
                    filtered.append(ref)
            
            return filtered
            
        except Exception:
            return []
    
    def get_quality_statistics(self) -> Dict[str, Any]:
        """Get quality service statistics."""
        try:
            if not self.assessments:
                return {
                    "status": "success",
                    "total_assessments": 0,
                    "quality_distribution": {},
                    "average_confidence": 0.0
                }
            
            # Calculate distribution
            tier_counts = {tier.value: 0 for tier in QualityTier}
            confidences = []
            
            for assessment in self.assessments.values():
                tier_counts[assessment.quality_tier.value] += 1
                confidences.append(assessment.confidence)
            
            return {
                "status": "success",
                "total_assessments": len(self.assessments),
                "quality_distribution": tier_counts,
                "average_confidence": statistics.mean(confidences),
                "confidence_std": statistics.stdev(confidences) if len(confidences) > 1 else 0.0,
                "min_confidence": min(confidences),
                "max_confidence": max(confidences),
                "total_rules": len(self.quality_rules)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to get statistics: {str(e)}"
            }