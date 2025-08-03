"""
Confidence Calculator

Utility classes for calculating confidence scores from various inputs and sources.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .data_models import ConfidenceScore, PropagationMethod

logger = logging.getLogger(__name__)


class BaseCalculator:
    """Base calculator with common utility methods"""
    
    @staticmethod
    def _normalize_score(score: float) -> float:
        """Normalize score to [0,1] range"""
        return max(0.0, min(1.0, score))
    
    @staticmethod
    def _calculate_evidence_weight(count: int, max_weight: int = 5) -> int:
        """Calculate evidence weight from count, capped at max_weight"""
        return min(max_weight, max(1, count))
    
    @staticmethod
    def _create_metadata(source: str, **kwargs) -> Dict[str, Any]:
        """Create metadata dictionary with source and additional info"""
        metadata = {"source": source, "created_at": datetime.now().isoformat()}
        metadata.update(kwargs)
        return metadata


class ConfidenceCalculator(BaseCalculator):
    """Main calculator for confidence scores from various technical sources"""
    
    @staticmethod
    def from_spacy_confidence(spacy_score: float, entity_count: int = 1) -> ConfidenceScore:
        """Create confidence score from SpaCy NER confidence."""
        normalized_score = BaseCalculator._normalize_score(spacy_score)
        evidence_weight = BaseCalculator._calculate_evidence_weight(entity_count)
        
        return ConfidenceScore(
            value=normalized_score,
            evidence_weight=evidence_weight,
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            source="spacy_ner",
            metadata=BaseCalculator._create_metadata(
                "spacy_ner",
                entity_count=entity_count,
                original_score=spacy_score
            )
        )
    
    @staticmethod
    def from_llm_response(llm_confidence: Optional[float], token_count: int, model_name: str) -> ConfidenceScore:
        """Create confidence score from LLM response."""
        
        # If no explicit confidence provided, estimate from token count and model
        if llm_confidence is None:
            # Heuristic: longer responses tend to be more confident
            estimated_confidence = min(0.8, 0.3 + (token_count / 1000) * 0.5)
        else:
            estimated_confidence = BaseCalculator._normalize_score(llm_confidence)
        
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
            source="llm_response",
            metadata=BaseCalculator._create_metadata(
                "llm_response",
                model_name=model_name,
                token_count=token_count,
                explicit_confidence=llm_confidence is not None,
                original_confidence=llm_confidence
            )
        )
    
    @staticmethod
    def from_vector_similarity(similarity_score: float, vector_dimension: int) -> ConfidenceScore:
        """Create confidence score from vector similarity."""
        normalized_score = BaseCalculator._normalize_score(similarity_score)
        
        # Higher dimensional vectors tend to be more reliable
        evidence_weight = BaseCalculator._calculate_evidence_weight(vector_dimension // 100)
        
        return ConfidenceScore(
            value=normalized_score,
            evidence_weight=evidence_weight,
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            source="vector_similarity",
            metadata=BaseCalculator._create_metadata(
                "vector_similarity",
                vector_dimension=vector_dimension,
                similarity_score=similarity_score
            )
        )
    
    @staticmethod
    def from_graph_centrality(centrality_score: float, node_degree: int) -> ConfidenceScore:
        """Create confidence score from graph centrality measures."""
        normalized_score = BaseCalculator._normalize_score(centrality_score)
        
        # Higher degree nodes in graph tend to be more reliable
        evidence_weight = BaseCalculator._calculate_evidence_weight(node_degree // 3)
        
        return ConfidenceScore(
            value=normalized_score,
            evidence_weight=evidence_weight,
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            source="graph_centrality",
            metadata=BaseCalculator._create_metadata(
                "graph_centrality",
                centrality_score=centrality_score,
                node_degree=node_degree
            )
        )
    
    @staticmethod
    def from_statistical_test(p_value: float, effect_size: float, sample_size: int) -> ConfidenceScore:
        """Create confidence score from statistical test results"""
        
        # Convert p-value to confidence (1 - p_value, with floor)
        p_confidence = max(0.1, 1.0 - p_value) if p_value <= 1.0 else 0.1
        
        # Adjust based on effect size and sample size
        effect_adjustment = min(1.0, effect_size) if effect_size >= 0 else 0.1
        sample_adjustment = min(1.0, 0.5 + (sample_size / 1000) * 0.5)
        
        # Combined confidence
        combined_confidence = (p_confidence * 0.5) + (effect_adjustment * 0.3) + (sample_adjustment * 0.2)
        combined_confidence = BaseCalculator._normalize_score(combined_confidence)
        
        # Evidence weight based on sample size
        evidence_weight = BaseCalculator._calculate_evidence_weight(sample_size // 10)
        
        return ConfidenceScore(
            value=combined_confidence,
            evidence_weight=evidence_weight,
            propagation_method=PropagationMethod.BAYESIAN_EVIDENCE_POWER,
            source="statistical_test",
            metadata=BaseCalculator._create_metadata(
                "statistical_test",
                p_value=p_value,
                effect_size=effect_size,
                sample_size=sample_size,
                p_confidence=p_confidence,
                effect_adjustment=effect_adjustment,
                sample_adjustment=sample_adjustment
            )
        )


class DomainSpecificCalculator(BaseCalculator):
    """Calculator for domain-specific confidence assessments"""
    
    @staticmethod
    def for_text_to_argument_extraction(claim_confidence: float, 
                                      warrant_confidence: float,
                                      data_confidence: float,
                                      method_quality: float = 0.8) -> ConfidenceScore:
        """Calculate confidence for text → Toulmin argument extraction"""
        
        # CERQual assessment for argument extraction
        from .cerqual_assessment import CERQualProcessor
        
        methodological_limitations = method_quality  # Quality of NLP/extraction method
        relevance = BaseCalculator._normalize_score(claim_confidence)  # How relevant is extracted claim
        coherence = (warrant_confidence + data_confidence) / 2.0  # Internal consistency
        adequacy_of_data = BaseCalculator._normalize_score((claim_confidence + warrant_confidence + data_confidence) / 3.0)
        
        return CERQualProcessor.create_with_cerqual(
            methodological_limitations=methodological_limitations,
            relevance=relevance,
            coherence=coherence,
            adequacy_of_data=adequacy_of_data,
            evidence_weight=3,
            source="text_to_argument_extraction"
        )
    
    @staticmethod
    def for_sentiment_attitude_mapping(sentiment_strength: float,
                                     attitude_clarity: float,
                                     context_relevance: float = 0.8,
                                     method_quality: float = 0.7) -> ConfidenceScore:
        """Calculate confidence for sentiment → attitude mapping"""
        
        from .cerqual_assessment import CERQualProcessor
        
        # Combine sentiment and attitude information
        combined_confidence = (sentiment_strength * 0.6) + (attitude_clarity * 0.4)
        combined_confidence = BaseCalculator._normalize_score(combined_confidence)
        
        return CERQualProcessor.create_with_cerqual(
            methodological_limitations=method_quality,
            relevance=context_relevance,
            coherence=attitude_clarity,
            adequacy_of_data=sentiment_strength,
            evidence_weight=2,
            base_confidence=combined_confidence,
            source="sentiment_attitude_mapping"
        )
    
    @staticmethod
    def for_belief_network_extraction(belief_clarity: float,
                                    network_completeness: float,
                                    method_sophistication: float = 0.6,
                                    data_quality: float = 0.7) -> ConfidenceScore:
        """Calculate confidence for belief network extraction"""
        
        from .cerqual_assessment import CERQualProcessor
        
        # Combine belief and network information
        combined_confidence = (belief_clarity * 0.7) + (network_completeness * 0.3)
        combined_confidence = BaseCalculator._normalize_score(combined_confidence)
        
        return CERQualProcessor.create_with_cerqual(
            methodological_limitations=method_sophistication,
            relevance=belief_clarity,
            coherence=network_completeness,
            adequacy_of_data=data_quality,
            evidence_weight=2,
            base_confidence=combined_confidence,
            source="belief_network_extraction"
        )
    
    @staticmethod
    def for_individual_to_community_aggregation(sample_size: int,
                                               representation_quality: float,
                                               aggregation_method_quality: float = 0.8,
                                               data_coverage: float = 1.0) -> ConfidenceScore:
        """Calculate confidence for individual → community aggregation"""
        
        from .cerqual_assessment import CERQualProcessor
        
        # Sample size effect on confidence
        sample_effect = min(1.0, 0.3 + (sample_size / 100) * 0.7)  # Asymptotic to 1.0
        
        # Combined confidence
        combined_confidence = (sample_effect * 0.5) + (representation_quality * 0.5)
        combined_confidence = BaseCalculator._normalize_score(combined_confidence)
        
        evidence_weight = BaseCalculator._calculate_evidence_weight(sample_size // 5)
        
        return CERQualProcessor.create_with_cerqual(
            methodological_limitations=aggregation_method_quality,
            relevance=representation_quality,
            coherence=sample_effect,
            adequacy_of_data=data_coverage,
            evidence_weight=evidence_weight,
            base_confidence=combined_confidence,
            source="individual_to_community_aggregation"
        )
    
    @staticmethod
    def for_psychological_state_inference(explicit_indicators: int,
                                        implicit_signals: int,
                                        context_clarity: float = 0.7,
                                        inference_method_quality: float = 0.6) -> ConfidenceScore:
        """Calculate confidence for psychological state inference"""
        
        from .cerqual_assessment import CERQualProcessor
        
        # Evidence strength from indicators
        total_indicators = explicit_indicators + implicit_signals
        indicator_strength = min(1.0, 0.2 + (total_indicators / 10) * 0.8)
        
        # Weight explicit indicators more heavily
        explicit_weight = min(1.0, 0.3 + (explicit_indicators / 5) * 0.7)
        
        # Combined confidence
        combined_confidence = (indicator_strength * 0.6) + (explicit_weight * 0.4)
        combined_confidence = BaseCalculator._normalize_score(combined_confidence)
        
        evidence_weight = BaseCalculator._calculate_evidence_weight(explicit_indicators + (implicit_signals // 2))
        
        return CERQualProcessor.create_with_cerqual(
            methodological_limitations=inference_method_quality,
            relevance=context_clarity,
            coherence=explicit_weight,
            adequacy_of_data=indicator_strength,
            evidence_weight=evidence_weight,
            base_confidence=combined_confidence,
            source="psychological_state_inference"
        )