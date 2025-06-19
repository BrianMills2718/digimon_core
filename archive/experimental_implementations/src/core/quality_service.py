"""T111: Quality Service - Confidence assessment and propagation."""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from statistics import mean, stdev

from ..models import BaseObject, Reference, QualityTier
from ..utils.database import DatabaseManager


logger = logging.getLogger(__name__)


@dataclass
class QualityAssessment:
    """Result of quality assessment."""
    
    confidence: float
    quality_tier: QualityTier
    warnings: List[str]
    recommendations: List[str]
    component_scores: Dict[str, float]


class QualityService:
    """
    T111: Quality Service
    
    Manages confidence scores and quality assessment throughout the system.
    Tracks quality degradation and provides recommendations.
    """
    
    def __init__(
        self, 
        db_manager: DatabaseManager,
        # Quality tier thresholds
        high_quality_threshold: float = 0.8,
        medium_quality_threshold: float = 0.5,
        # Warning thresholds
        low_confidence_threshold: float = 0.5,
        provenance_warning_threshold: float = 0.6,
        consistency_warning_threshold: float = 0.7,
        completeness_warning_threshold: float = 0.8,
        # Consistency check thresholds
        variance_warning_threshold: float = 0.2,
        max_attributes_warning: int = 50,
        max_warnings_warning: int = 5
    ):
        self.db = db_manager
        
        # Store thresholds
        self.high_quality_threshold = high_quality_threshold
        self.medium_quality_threshold = medium_quality_threshold
        self.low_confidence_threshold = low_confidence_threshold
        self.provenance_warning_threshold = provenance_warning_threshold
        self.consistency_warning_threshold = consistency_warning_threshold
        self.completeness_warning_threshold = completeness_warning_threshold
        self.variance_warning_threshold = variance_warning_threshold
        self.max_attributes_warning = max_attributes_warning
        self.max_warnings_warning = max_warnings_warning
        
        self._quality_rules: Dict[str, float] = {
            "exact_match": 1.0,
            "fuzzy_match": 0.8,
            "ml_extraction": 0.7,
            "heuristic": 0.6,
            "manual": 0.9,
            "merge_operation": 0.95,
            "transformation": 0.98,
        }
        self._degradation_factors: Dict[str, float] = {
            "missing_context": 0.9,
            "partial_data": 0.85,
            "low_confidence_input": 0.8,
            "multiple_candidates": 0.9,
            "conflicting_data": 0.7,
        }
    
    def assess_quality(
        self,
        object_ref: str,
        method: str = "automatic"
    ) -> QualityAssessment:
        """Assess the quality of an object."""
        # Parse reference
        ref = Reference.from_string(object_ref)
        
        # Get object and its provenance
        obj = self._get_object(ref)
        if not obj:
            return QualityAssessment(
                confidence=0.0,
                quality_tier="low",
                warnings=["Object not found"],
                recommendations=["Verify object existence"],
                component_scores={}
            )
        
        # Calculate component scores
        component_scores = {}
        
        # 1. Inherent confidence
        component_scores["inherent"] = obj.confidence
        
        # 2. Provenance-based confidence
        prov_confidence = self._assess_provenance_quality(object_ref)
        component_scores["provenance"] = prov_confidence
        
        # 3. Consistency check
        consistency = self._assess_consistency(obj, ref)
        component_scores["consistency"] = consistency
        
        # 4. Completeness check
        completeness = self._assess_completeness(obj, ref)
        component_scores["completeness"] = completeness
        
        # Calculate overall confidence
        if method == "automatic":
            # Weighted average
            weights = {
                "inherent": 0.4,
                "provenance": 0.3,
                "consistency": 0.2,
                "completeness": 0.1
            }
            confidence = sum(
                component_scores.get(k, 0) * v 
                for k, v in weights.items()
            )
        elif method == "minimum":
            # Most conservative
            confidence = min(component_scores.values()) if component_scores else 0.0
        else:
            # Simple average
            confidence = mean(component_scores.values()) if component_scores else 0.0
        
        # Determine quality tier
        if confidence >= self.high_quality_threshold:
            quality_tier = "high"
        elif confidence >= self.medium_quality_threshold:
            quality_tier = "medium"
        else:
            quality_tier = "low"
        
        # Generate warnings and recommendations
        warnings = []
        recommendations = []
        
        if confidence < self.low_confidence_threshold:
            warnings.append(f"Low overall confidence (< {self.low_confidence_threshold})")
            recommendations.append("Manual review recommended")
        
        if component_scores.get("provenance", 1.0) < self.provenance_warning_threshold:
            warnings.append(f"Weak provenance chain (< {self.provenance_warning_threshold})")
            recommendations.append("Verify source data")
        
        if component_scores.get("consistency", 1.0) < self.consistency_warning_threshold:
            warnings.append(f"Consistency issues detected (< {self.consistency_warning_threshold})")
            recommendations.append("Resolve data conflicts")
        
        if component_scores.get("completeness", 1.0) < self.completeness_warning_threshold:
            warnings.append(f"Incomplete data (< {self.completeness_warning_threshold})")
            recommendations.append("Gather additional information")
        
        # Add object warnings
        warnings.extend(obj.warnings)
        
        return QualityAssessment(
            confidence=confidence,
            quality_tier=quality_tier,
            warnings=warnings,
            recommendations=recommendations,
            component_scores=component_scores
        )
    
    def propagate_quality(
        self,
        input_refs: List[str],
        operation_type: str,
        parameters: Dict[str, Any]
    ) -> Tuple[float, List[str]]:
        """Calculate output quality based on inputs and operation."""
        if not input_refs:
            return 1.0, []
        
        # Get input qualities
        input_qualities = []
        warnings = []
        
        for ref in input_refs:
            assessment = self.assess_quality(ref)
            input_qualities.append(assessment.confidence)
            warnings.extend(assessment.warnings)
        
        # Base confidence is minimum of inputs
        base_confidence = min(input_qualities) if input_qualities else 1.0
        
        # Apply operation-specific factor
        operation_factor = self._quality_rules.get(operation_type, 0.9)
        
        # Apply degradation factors based on parameters
        degradation = 1.0
        
        if parameters.get("partial_results"):
            degradation *= self._degradation_factors["partial_data"]
            warnings.append("Partial results may affect quality")
        
        if parameters.get("multiple_candidates"):
            degradation *= self._degradation_factors["multiple_candidates"]
            warnings.append("Multiple candidates resolved")
        
        if len(input_qualities) > 1 and stdev(input_qualities) > self.variance_warning_threshold:
            degradation *= self._degradation_factors["conflicting_data"]
            warnings.append(f"Input quality variance detected (> {self.variance_warning_threshold})")
        
        # Calculate final confidence
        confidence = base_confidence * operation_factor * degradation
        
        # Ensure bounds
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence, warnings
    
    def update_quality(
        self,
        object_ref: str,
        confidence: float,
        warnings: Optional[List[str]] = None,
        reason: str = "manual_update"
    ) -> None:
        """Update the quality of an object."""
        ref = Reference.from_string(object_ref)
        obj = self._get_object(ref)
        
        if not obj:
            logger.warning(f"Cannot update quality for non-existent object: {object_ref}")
            return
        
        # Update confidence
        old_confidence = obj.confidence
        obj.confidence = confidence
        
        # Update quality tier
        if confidence >= self.high_quality_threshold:
            obj.quality_tier = "high"
        elif confidence >= self.medium_quality_threshold:
            obj.quality_tier = "medium"
        else:
            obj.quality_tier = "low"
        
        # Add warnings
        if warnings:
            obj.warnings.extend(warnings)
        
        # Add audit trail
        obj.evidence.append(
            f"Quality updated: {old_confidence:.2f} → {confidence:.2f} ({reason})"
        )
        
        # Save updated object
        self._save_object(obj, ref)
        
        logger.info(
            f"Updated quality for {object_ref}: "
            f"{old_confidence:.2f} → {confidence:.2f}"
        )
    
    def get_quality_report(
        self,
        object_refs: List[str]
    ) -> Dict[str, Any]:
        """Generate a quality report for a set of objects."""
        assessments = []
        
        for ref in object_refs:
            assessment = self.assess_quality(ref)
            assessments.append({
                "reference": ref,
                "confidence": assessment.confidence,
                "quality_tier": assessment.quality_tier,
                "warnings": assessment.warnings,
                "recommendations": assessment.recommendations
            })
        
        # Calculate statistics
        confidences = [a["confidence"] for a in assessments]
        
        high_quality = sum(1 for a in assessments if a["quality_tier"] == "high")
        medium_quality = sum(1 for a in assessments if a["quality_tier"] == "medium")
        low_quality = sum(1 for a in assessments if a["quality_tier"] == "low")
        
        # Aggregate warnings
        all_warnings = []
        for a in assessments:
            all_warnings.extend(a["warnings"])
        
        warning_counts = {}
        for w in all_warnings:
            warning_counts[w] = warning_counts.get(w, 0) + 1
        
        return {
            "total_objects": len(assessments),
            "average_confidence": mean(confidences) if confidences else 0.0,
            "min_confidence": min(confidences) if confidences else 0.0,
            "max_confidence": max(confidences) if confidences else 0.0,
            "quality_distribution": {
                "high": high_quality,
                "medium": medium_quality,
                "low": low_quality
            },
            "common_warnings": sorted(
                warning_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "assessments": assessments
        }
    
    def _get_object(self, ref: Reference) -> Optional[BaseObject]:
        """Get object from appropriate database."""
        if ref.storage == "neo4j":
            if ref.type == "entity":
                return self.db.neo4j.get_entity(ref.id)
            elif ref.type == "relationship":
                return self.db.neo4j.get_relationship(ref.id)
        elif ref.storage == "sqlite":
            if ref.type == "document":
                return self.db.sqlite.get_document(ref.id)
            elif ref.type == "chunk":
                return self.db.sqlite.get_chunk(ref.id)
            elif ref.type == "mention":
                return self.db.sqlite.get_mention(ref.id)
        
        return None
    
    def _save_object(self, obj: BaseObject, ref: Reference) -> None:
        """Save object to appropriate database."""
        if ref.storage == "neo4j":
            if ref.type == "entity":
                self.db.neo4j.update_entity(obj)
            elif ref.type == "relationship":
                self.db.neo4j.update_relationship(obj)
        elif ref.storage == "sqlite":
            if ref.type == "document":
                self.db.sqlite.update_document(obj)
            elif ref.type == "chunk":
                self.db.sqlite.update_chunk(obj)
            elif ref.type == "mention":
                self.db.sqlite.update_mention(obj)
    
    def _assess_provenance_quality(self, object_ref: str) -> float:
        """Assess quality based on provenance chain."""
        provenance_service = self.db.get_provenance_service()
        confidence = provenance_service.calculate_derived_confidence(object_ref)
        return confidence
    
    def _assess_consistency(self, obj: BaseObject, ref: Reference) -> float:
        """Assess internal consistency of object."""
        score = 1.0
        
        # Check for conflicting attributes
        if hasattr(obj, "attributes") and obj.attributes:
            # Simple heuristic: penalize if too many attributes
            if len(obj.attributes) > self.max_attributes_warning:
                score *= 0.9
        
        # Check for excessive warnings
        if len(obj.warnings) > self.max_warnings_warning:
            score *= 0.8
        
        # Type-specific checks
        if ref.type == "entity" and hasattr(obj, "surface_forms"):
            # Check for duplicate surface forms
            if len(obj.surface_forms) != len(set(obj.surface_forms)):
                score *= 0.95
        
        return score
    
    def _assess_completeness(self, obj: BaseObject, ref: Reference) -> float:
        """Assess completeness of object data."""
        score = 1.0
        
        # Type-specific completeness checks
        if ref.type == "entity":
            if not getattr(obj, "canonical_name", None):
                score *= 0.8
            if not getattr(obj, "entity_type", None):
                score *= 0.9
            if not getattr(obj, "surface_forms", []):
                score *= 0.7
        
        elif ref.type == "relationship":
            if not getattr(obj, "relationship_type", None):
                score *= 0.8
        
        elif ref.type == "document":
            if not getattr(obj, "title", None):
                score *= 0.9
            if not getattr(obj, "content_hash", None):
                score *= 0.95
        
        return score