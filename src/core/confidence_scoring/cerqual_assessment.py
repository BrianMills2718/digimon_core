"""
CERQual Assessment Methods

Implements Confidence in the Evidence from Reviews of Qualitative research (CERQual) 
assessment framework for confidence scoring.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .data_models import ConfidenceScore, PropagationMethod

logger = logging.getLogger(__name__)


class CERQualAssessment:
    """Data structure for CERQual assessment dimensions"""
    
    def __init__(self, 
                 methodological_limitations: float,
                 relevance: float, 
                 coherence: float,
                 adequacy_of_data: float):
        self.methodological_limitations = methodological_limitations
        self.relevance = relevance
        self.coherence = coherence
        self.adequacy_of_data = adequacy_of_data
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary format"""
        return {
            "methodological_limitations": self.methodological_limitations,
            "relevance": self.relevance,
            "coherence": self.coherence,
            "adequacy_of_data": self.adequacy_of_data
        }
    
    def calculate_combined_score(self) -> float:
        """Calculate combined CERQual confidence score"""
        # Weighted combination: all dimensions are important but methodological limitations 
        # and adequacy of data are slightly more critical
        weights = {
            "methodological_limitations": 0.3,
            "relevance": 0.2,
            "coherence": 0.2,
            "adequacy_of_data": 0.3
        }
        
        weighted_sum = (
            self.methodological_limitations * weights["methodological_limitations"] +
            self.relevance * weights["relevance"] +
            self.coherence * weights["coherence"] +
            self.adequacy_of_data * weights["adequacy_of_data"]
        )
        
        return min(1.0, max(0.0, weighted_sum))


class CERQualProcessor:
    """Processor for CERQual assessment operations"""
    
    @staticmethod
    def add_cerqual_evidence(score: ConfidenceScore,
                           methodological_limitations: Optional[float] = None,
                           relevance: Optional[float] = None,
                           coherence: Optional[float] = None,
                           adequacy_of_data: Optional[float] = None,
                           evidence_description: str = "") -> ConfidenceScore:
        """Add CERQual evidence dimensions to existing confidence score"""
        
        # Update only provided dimensions, keep existing ones
        new_method_lim = methodological_limitations if methodological_limitations is not None else score.methodological_limitations
        new_relevance = relevance if relevance is not None else score.relevance
        new_coherence = coherence if coherence is not None else score.coherence
        new_adequacy = adequacy_of_data if adequacy_of_data is not None else score.adequacy_of_data
        
        # Update metadata with evidence description
        new_metadata = {**score.metadata}
        if evidence_description:
            evidence_log = new_metadata.get("cerqual_evidence_log", [])
            evidence_log.append({
                "timestamp": datetime.now().isoformat(),
                "description": evidence_description,
                "dimensions_updated": {
                    "methodological_limitations": methodological_limitations,
                    "relevance": relevance,
                    "coherence": coherence,
                    "adequacy_of_data": adequacy_of_data
                }
            })
            new_metadata["cerqual_evidence_log"] = evidence_log
        
        return ConfidenceScore(
            value=score.value,
            confidence_range=score.confidence_range,
            evidence_weight=score.evidence_weight,
            methodological_limitations=new_method_lim,
            relevance=new_relevance,
            coherence=new_coherence,
            adequacy_of_data=new_adequacy,
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
            metadata=new_metadata
        )
    
    @staticmethod
    def calculate_cerqual_combined(score: ConfidenceScore) -> float:
        """Calculate combined CERQual confidence score from dimensions"""
        
        # Get CERQual dimensions
        assessment = score.get_cerqual_assessment()
        
        # Check if we have any CERQual dimensions
        cerqual_values = [v for v in assessment.values() if v is not None]
        if not cerqual_values:
            # No CERQual data, return base confidence
            return score.value
        
        # If we have partial CERQual data, use defaults for missing dimensions
        method_lim = assessment["methodological_limitations"] or 0.7  # Moderate quality default
        relevance = assessment["relevance"] or 0.8  # High relevance default
        coherence = assessment["coherence"] or 0.7  # Moderate coherence default
        adequacy = assessment["adequacy_of_data"] or 0.6  # Moderate adequacy default
        
        cerqual_assessment = CERQualAssessment(method_lim, relevance, coherence, adequacy)
        cerqual_score = cerqual_assessment.calculate_combined_score()
        
        # Combine with base confidence using weighted average
        # CERQual provides quality assessment, base confidence provides magnitude
        combined_score = (score.value * 0.6) + (cerqual_score * 0.4)
        
        return min(1.0, max(0.0, combined_score))
    
    @staticmethod
    def create_with_cerqual(methodological_limitations: float,
                          relevance: float,
                          coherence: float,
                          adequacy_of_data: float,
                          evidence_weight: int = 1,
                          base_confidence: Optional[float] = None,
                          source: str = "cerqual_assessment") -> ConfidenceScore:
        """Create confidence score with CERQual assessment"""
        
        # Calculate CERQual combined score
        cerqual_assessment = CERQualAssessment(
            methodological_limitations, relevance, coherence, adequacy_of_data
        )
        cerqual_score = cerqual_assessment.calculate_combined_score()
        
        # Use CERQual score as base confidence if not provided
        final_confidence = base_confidence if base_confidence is not None else cerqual_score
        
        return ConfidenceScore(
            value=final_confidence,
            evidence_weight=evidence_weight,
            methodological_limitations=methodological_limitations,
            relevance=relevance,
            coherence=coherence,
            adequacy_of_data=adequacy_of_data,
            source=source,
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            metadata={
                "cerqual_combined_score": cerqual_score,
                "cerqual_dimensions": cerqual_assessment.to_dict(),
                "created_with_cerqual": True
            }
        )


class CERQualCalculator:
    """Calculator for domain-specific CERQual assessments"""
    
    @staticmethod
    def for_text_analysis(extraction_method_quality: float,
                         text_relevance: float,
                         result_consistency: float,
                         data_sufficiency: float) -> CERQualAssessment:
        """CERQual assessment for text analysis tasks"""
        
        return CERQualAssessment(
            methodological_limitations=extraction_method_quality,
            relevance=text_relevance,
            coherence=result_consistency,
            adequacy_of_data=data_sufficiency
        )
    
    @staticmethod
    def for_entity_extraction(nlp_model_quality: float,
                            entity_context_relevance: float,
                            entity_consistency: float,
                            entity_coverage: float) -> CERQualAssessment:
        """CERQual assessment for entity extraction"""
        
        return CERQualAssessment(
            methodological_limitations=nlp_model_quality,
            relevance=entity_context_relevance,
            coherence=entity_consistency,
            adequacy_of_data=entity_coverage
        )
    
    @staticmethod
    def for_relationship_extraction(method_sophistication: float,
                                  relationship_relevance: float,
                                  relationship_coherence: float,
                                  relationship_evidence: float) -> CERQualAssessment:
        """CERQual assessment for relationship extraction"""
        
        return CERQualAssessment(
            methodological_limitations=method_sophistication,
            relevance=relationship_relevance,
            coherence=relationship_coherence,
            adequacy_of_data=relationship_evidence
        )
    
    @staticmethod
    def for_sentiment_analysis(model_appropriateness: float,
                             context_relevance: float,
                             sentiment_consistency: float,
                             data_representativeness: float) -> CERQualAssessment:
        """CERQual assessment for sentiment analysis"""
        
        return CERQualAssessment(
            methodological_limitations=model_appropriateness,
            relevance=context_relevance,
            coherence=sentiment_consistency,
            adequacy_of_data=data_representativeness
        )
    
    @staticmethod
    def for_graph_analysis(algorithm_quality: float,
                          graph_relevance: float,
                          result_coherence: float,
                          graph_completeness: float) -> CERQualAssessment:
        """CERQual assessment for graph analysis"""
        
        return CERQualAssessment(
            methodological_limitations=algorithm_quality,
            relevance=graph_relevance,
            coherence=result_coherence,
            adequacy_of_data=graph_completeness
        )