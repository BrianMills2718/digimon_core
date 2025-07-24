#!/usr/bin/env python3
"""
Uncertainty Engine - Main orchestrator for uncertainty analysis
Integrates all uncertainty components with real LLM processing
"""

import json
import numpy as np
import asyncio
import aiohttp
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from collections import defaultdict

from bayesian_aggregation_service import BayesianAggregationService, Evidence

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConfidenceScore:
    """Enhanced confidence score with full uncertainty tracking"""
    
    # Core confidence
    value: float  # 0-1
    
    # CERQual dimensions
    methodological_quality: float
    relevance: float
    coherence: float
    adequacy: float
    
    # Meta-uncertainty
    estimation_uncertainty: float
    temporal_decay_factor: float
    cross_modal_consistency: float
    
    # Provenance
    creation_timestamp: datetime
    last_updated: datetime
    evidence_count: int
    update_history: List[Dict] = None
    
    # Context
    domain: str = "general"
    model_type: str = "general"
    confidence_type: str = "bayesian"  # 'bayesian', 'frequentist', 'subjective'
    
    def __post_init__(self):
        if self.update_history is None:
            self.update_history = []
    
    def get_overall_confidence(self) -> float:
        """Calculate overall confidence considering all factors"""
        
        # Base confidence weighted by quality dimensions
        quality_weighted = (
            self.value * 
            0.3 * self.methodological_quality +
            0.25 * self.relevance +
            0.25 * self.coherence +
            0.2 * self.adequacy
        )
        
        # Apply uncertainty penalties
        uncertainty_penalty = (
            0.7 * (1 - self.estimation_uncertainty) +
            0.2 * self.temporal_decay_factor +
            0.1 * self.cross_modal_consistency
        )
        
        final_confidence = quality_weighted * uncertainty_penalty
        return max(0.01, min(0.99, final_confidence))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        # Convert datetime objects to strings
        result['creation_timestamp'] = self.creation_timestamp.isoformat()
        result['last_updated'] = self.last_updated.isoformat()
        return result

class UncertaintyEngine:
    """
    Main uncertainty processing engine with real LLM integration
    Orchestrates all uncertainty assessment components
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required")
        
        # Initialize services
        self.bayesian_service = BayesianAggregationService(self.api_key)
        
        # Tracking
        self.confidence_history = []
        self.analysis_cache = {}
        self.api_base = "https://api.openai.com/v1"
        
        # Performance metrics
        self.api_calls_made = 0
        self.total_processing_time = 0
        self.cache_hits = 0
        
    async def _make_llm_call(self, prompt: str, max_tokens: int = 500) -> str:
        """Make LLM API call with tracking"""
        self.api_calls_made += 1
        start_time = datetime.now()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.1
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_base}/chat/completions", 
                                      headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Track timing
                        self.total_processing_time += (datetime.now() - start_time).total_seconds()
                        
                        return result["choices"][0]["message"]["content"]
                    else:
                        logger.error(f"API call failed: {response.status}")
                        return ""
        except Exception as e:
            logger.error(f"LLM API call error: {e}")
            return ""
    
    async def extract_claims_and_evidence(self, text: str, domain: str = "general") -> Dict[str, Any]:
        """Extract claims and supporting evidence from text using LLM"""
        
        # Check cache first
        cache_key = f"claims_{hash(text[:1000])}_{domain}"
        if cache_key in self.analysis_cache:
            self.cache_hits += 1
            return self.analysis_cache[cache_key]
        
        prompt = f"""
        Analyze the following text to extract CLAIMS and their supporting EVIDENCE.
        
        TEXT TO ANALYZE:
        {text[:3000]}
        
        DOMAIN: {domain}
        
        Extract and structure the information as JSON:
        {{
            "main_claims": [
                {{
                    "claim": "specific factual claim",
                    "confidence_indicators": ["indicator1", "indicator2"],
                    "uncertainty_markers": ["maybe", "possibly", "unclear"],
                    "supporting_evidence": ["evidence1", "evidence2"],
                    "contradicting_evidence": ["contra1"],
                    "claim_type": "factual|interpretive|predictive|normative",
                    "scope": "specific|general|universal",
                    "temporal_context": "past|present|future|timeless"
                }}
            ],
            "evidence_quality_indicators": [
                {{
                    "evidence_text": "specific evidence",
                    "evidence_type": "empirical|testimonial|documentary|statistical",
                    "strength_indicators": ["strong word", "precise number"],
                    "weakness_indicators": ["hedge", "qualification"],
                    "source_reliability_clues": ["expert source", "first-hand"]
                }}
            ],
            "overall_certainty_level": "high|moderate|low|very_low",
            "uncertainty_sources": ["methodological", "temporal", "scope", "measurement"],
            "confidence_calibration_clues": ["overconfident phrases", "appropriate hedging"]
        }}
        
        Focus on:
        1. Explicit confidence statements ("we are certain that...")
        2. Hedging language ("it appears that...", "possibly...")
        3. Statistical claims with error bars or confidence intervals
        4. Source citations and their reliability indicators
        5. Methodological limitations mentioned
        """
        
        try:
            response = await self._make_llm_call(prompt, max_tokens=1500)
            
            # Parse JSON response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                extraction_result = json.loads(json_str)
                
                # Cache result
                self.analysis_cache[cache_key] = extraction_result
                return extraction_result
            else:
                logger.warning("Could not parse claim extraction response")
                return self._default_extraction()
                
        except Exception as e:
            logger.error(f"Error in claim extraction: {e}")
            return self._default_extraction()
    
    def _default_extraction(self) -> Dict[str, Any]:
        """Default extraction when LLM fails"""
        return {
            "main_claims": [],
            "evidence_quality_indicators": [],
            "overall_certainty_level": "moderate",
            "uncertainty_sources": ["analysis_failure"],
            "confidence_calibration_clues": []
        }
    
    async def assess_initial_confidence(self, text: str, claim: str, domain: str = "general") -> ConfidenceScore:
        """Assess initial confidence for a claim using LLM analysis"""
        
        prompt = f"""
        Assess the confidence level for the following CLAIM based on the provided TEXT evidence.
        
        CLAIM TO ASSESS:
        {claim}
        
        SUPPORTING TEXT:
        {text[:2500]}
        
        DOMAIN: {domain}
        
        Provide assessment in JSON format:
        {{
            "confidence_value": 0.0-1.0,
            "methodological_quality": 0.0-1.0,
            "relevance_to_claim": 0.0-1.0,
            "coherence_of_evidence": 0.0-1.0,
            "adequacy_of_evidence": 0.0-1.0,
            "estimation_uncertainty": 0.0-1.0,
            "temporal_stability": 0.0-1.0,
            "reasoning": "detailed explanation",
            "key_supporting_factors": ["factor1", "factor2"],
            "key_limiting_factors": ["limitation1", "limitation2"],
            "confidence_in_assessment": 0.0-1.0
        }}
        
        Consider:
        1. Quality and quantity of supporting evidence
        2. Methodological rigor of the source
        3. Consistency with established knowledge
        4. Potential biases or limitations
        5. Temporal relevance and stability
        6. Scope and generalizability
        """
        
        try:
            response = await self._make_llm_call(prompt, max_tokens=1000)
            
            # Parse response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                assessment = json.loads(json_str)
                
                # Create ConfidenceScore object
                confidence_score = ConfidenceScore(
                    value=assessment.get("confidence_value", 0.5),
                    methodological_quality=assessment.get("methodological_quality", 0.6),
                    relevance=assessment.get("relevance_to_claim", 0.7),
                    coherence=assessment.get("coherence_of_evidence", 0.6),
                    adequacy=assessment.get("adequacy_of_evidence", 0.5),
                    estimation_uncertainty=assessment.get("estimation_uncertainty", 0.4),
                    temporal_decay_factor=assessment.get("temporal_stability", 0.8),
                    cross_modal_consistency=0.7,  # Default for single-modal
                    creation_timestamp=datetime.now(),
                    last_updated=datetime.now(),
                    evidence_count=1,
                    domain=domain,
                    confidence_type="llm_assessed"
                )
                
                # Add reasoning to history
                confidence_score.update_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "initial_assessment",
                    "reasoning": assessment.get("reasoning", ""),
                    "supporting_factors": assessment.get("key_supporting_factors", []),
                    "limiting_factors": assessment.get("key_limiting_factors", [])
                })
                
                return confidence_score
                
        except Exception as e:
            logger.error(f"Error in confidence assessment: {e}")
        
        # Fallback confidence score
        return ConfidenceScore(
            value=0.5,
            methodological_quality=0.5,
            relevance=0.6,
            coherence=0.5,
            adequacy=0.4,
            estimation_uncertainty=0.6,
            temporal_decay_factor=0.7,
            cross_modal_consistency=0.6,
            creation_timestamp=datetime.now(),
            last_updated=datetime.now(),
            evidence_count=1,
            domain=domain
        )
    
    async def update_confidence_with_new_evidence(self, 
                                                current_confidence: ConfidenceScore,
                                                new_evidence: List[Evidence],
                                                claim: str) -> ConfidenceScore:
        """Update confidence score with new evidence using Bayesian aggregation"""
        
        logger.info(f"Updating confidence with {len(new_evidence)} new evidence pieces")
        
        # Use Bayesian service for evidence aggregation
        aggregation_result = await self.bayesian_service.aggregate_evidence_batch(
            new_evidence, claim, prior_belief=current_confidence.value
        )
        
        # Calculate new confidence dimensions
        new_methodological = self._update_methodological_quality(
            current_confidence.methodological_quality,
            aggregation_result
        )
        
        new_coherence = self._update_coherence(
            current_confidence.coherence,
            aggregation_result
        )
        
        new_adequacy = self._update_adequacy(
            current_confidence.adequacy,
            len(new_evidence),
            current_confidence.evidence_count
        )
        
        # Create updated confidence score
        updated_confidence = ConfidenceScore(
            value=aggregation_result["final_belief"],
            methodological_quality=new_methodological,
            relevance=current_confidence.relevance,  # Assume relevance stable
            coherence=new_coherence,
            adequacy=new_adequacy,
            estimation_uncertainty=max(0.1, current_confidence.estimation_uncertainty - 0.1),  # Reduce with more evidence
            temporal_decay_factor=current_confidence.temporal_decay_factor,
            cross_modal_consistency=current_confidence.cross_modal_consistency,
            creation_timestamp=current_confidence.creation_timestamp,
            last_updated=datetime.now(),
            evidence_count=current_confidence.evidence_count + len(new_evidence),
            update_history=current_confidence.update_history.copy(),
            domain=current_confidence.domain,
            model_type=current_confidence.model_type,
            confidence_type=current_confidence.confidence_type
        )
        
        # Record update
        updated_confidence.update_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "bayesian_update",
            "new_evidence_count": len(new_evidence),
            "belief_change": aggregation_result["total_belief_change"],
            "average_diagnosticity": aggregation_result["average_diagnosticity"],
            "confidence_in_update": aggregation_result["confidence_in_result"]
        })
        
        return updated_confidence
    
    def _update_methodological_quality(self, current_quality: float, aggregation_result: Dict) -> float:
        """Update methodological quality based on new evidence"""
        
        # Get quality scores from evidence updates
        quality_scores = []
        for update in aggregation_result.get("update_history", []):
            quality_scores.append(update.get("quality_overall", 0.6))
        
        if quality_scores:
            new_evidence_quality = np.mean(quality_scores)
            # Weighted average with current quality
            updated_quality = 0.7 * current_quality + 0.3 * new_evidence_quality
            return max(0.1, min(1.0, updated_quality))
        
        return current_quality
    
    def _update_coherence(self, current_coherence: float, aggregation_result: Dict) -> float:
        """Update coherence based on consistency of new evidence"""
        
        # Measure consistency of belief changes
        belief_changes = []
        for update in aggregation_result.get("update_history", []):
            belief_changes.append(update.get("belief_change", 0))
        
        if belief_changes:
            # High consistency = similar direction of belief changes
            if len(belief_changes) > 1:
                consistency = 1 - (np.std(belief_changes) / (np.mean(np.abs(belief_changes)) + 0.1))
                consistency = max(0, min(1, consistency))
            else:
                consistency = 0.7  # Neutral for single evidence
            
            # Update coherence
            updated_coherence = 0.6 * current_coherence + 0.4 * consistency
            return max(0.1, min(1.0, updated_coherence))
        
        return current_coherence
    
    def _update_adequacy(self, current_adequacy: float, new_evidence_count: int, 
                        total_evidence_count: int) -> float:
        """Update adequacy based on evidence quantity"""
        
        # Evidence adequacy increases with more evidence but with diminishing returns
        total_after_update = total_evidence_count + new_evidence_count
        
        # Logarithmic scaling - more evidence increases adequacy but levels off
        adequacy_from_quantity = min(1.0, 0.3 + 0.1 * np.log(total_after_update + 1))
        
        # Weighted average
        updated_adequacy = 0.7 * current_adequacy + 0.3 * adequacy_from_quantity
        return max(0.1, min(1.0, updated_adequacy))
    
    async def cross_modal_uncertainty_translation(self, 
                                                confidence_score: ConfidenceScore,
                                                source_modality: str,
                                                target_modality: str,
                                                translation_context: Dict = None) -> ConfidenceScore:
        """Translate uncertainty across different modalities (text, graph, embeddings)"""
        
        if translation_context is None:
            translation_context = {}
        
        prompt = f"""
        Assess how uncertainty should be translated from {source_modality} to {target_modality}.
        
        CURRENT CONFIDENCE INFORMATION:
        - Value: {confidence_score.value}
        - Methodological Quality: {confidence_score.methodological_quality}
        - Domain: {confidence_score.domain}
        - Evidence Count: {confidence_score.evidence_count}
        
        TRANSLATION CONTEXT:
        {json.dumps(translation_context, indent=2)}
        
        Provide translation assessment in JSON:
        {{
            "translation_quality": 0.0-1.0,
            "information_preservation": 0.0-1.0,
            "modality_compatibility": 0.0-1.0,
            "expected_uncertainty_increase": 0.0-1.0,
            "confidence_adjustment_factor": 0.5-1.5,
            "cross_modal_consistency": 0.0-1.0,
            "translation_reasoning": "explanation",
            "key_preservation_factors": ["factor1", "factor2"],
            "key_loss_factors": ["loss1", "loss2"]
        }}
        
        Consider:
        1. Information loss in modality conversion
        2. Representation compatibility
        3. Semantic preservation
        4. Structural consistency
        5. Domain-specific factors
        """
        
        try:
            response = await self._make_llm_call(prompt, max_tokens=800)
            
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                translation_assessment = json.loads(json_str)
                
                # Apply translation
                adjustment_factor = translation_assessment.get("confidence_adjustment_factor", 1.0)
                new_consistency = translation_assessment.get("cross_modal_consistency", 0.7)
                
                translated_confidence = ConfidenceScore(
                    value=max(0.01, min(0.99, confidence_score.value * adjustment_factor)),
                    methodological_quality=confidence_score.methodological_quality,
                    relevance=confidence_score.relevance,
                    coherence=confidence_score.coherence,
                    adequacy=confidence_score.adequacy,
                    estimation_uncertainty=min(0.9, confidence_score.estimation_uncertainty + 
                                             translation_assessment.get("expected_uncertainty_increase", 0.1)),
                    temporal_decay_factor=confidence_score.temporal_decay_factor,
                    cross_modal_consistency=new_consistency,
                    creation_timestamp=confidence_score.creation_timestamp,
                    last_updated=datetime.now(),
                    evidence_count=confidence_score.evidence_count,
                    update_history=confidence_score.update_history.copy(),
                    domain=confidence_score.domain,
                    model_type=target_modality,
                    confidence_type=confidence_score.confidence_type
                )
                
                # Record translation
                translated_confidence.update_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "cross_modal_translation",
                    "source_modality": source_modality,
                    "target_modality": target_modality,
                    "adjustment_factor": adjustment_factor,
                    "translation_quality": translation_assessment.get("translation_quality", 0.7),
                    "reasoning": translation_assessment.get("translation_reasoning", "")
                })
                
                return translated_confidence
                
        except Exception as e:
            logger.error(f"Error in cross-modal translation: {e}")
        
        # Fallback: conservative translation
        return ConfidenceScore(
            value=confidence_score.value * 0.8,  # Conservative reduction
            methodological_quality=confidence_score.methodological_quality,
            relevance=confidence_score.relevance,
            coherence=confidence_score.coherence,
            adequacy=confidence_score.adequacy,
            estimation_uncertainty=min(0.9, confidence_score.estimation_uncertainty + 0.2),
            temporal_decay_factor=confidence_score.temporal_decay_factor,
            cross_modal_consistency=0.6,  # Lower consistency for failed translation
            creation_timestamp=confidence_score.creation_timestamp,
            last_updated=datetime.now(),
            evidence_count=confidence_score.evidence_count,
            update_history=confidence_score.update_history.copy(),
            domain=confidence_score.domain,
            model_type=target_modality
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the uncertainty engine"""
        
        return {
            "api_calls_made": self.api_calls_made,
            "total_processing_time": self.total_processing_time,
            "average_call_time": self.total_processing_time / max(1, self.api_calls_made),
            "cache_hits": self.cache_hits,
            "cache_hit_rate": self.cache_hits / max(1, len(self.analysis_cache)),
            "confidence_scores_generated": len(self.confidence_history),
            "cached_analyses": len(self.analysis_cache)
        }
    
    def generate_uncertainty_report(self, confidence_score: ConfidenceScore) -> str:
        """Generate comprehensive uncertainty analysis report"""
        
        overall_confidence = confidence_score.get_overall_confidence()
        
        report = f"""
# Uncertainty Analysis Report

## Overall Assessment
- **Final Confidence**: {overall_confidence:.3f}
- **Raw Confidence**: {confidence_score.value:.3f}
- **Domain**: {confidence_score.domain}
- **Model Type**: {confidence_score.model_type}
- **Evidence Count**: {confidence_score.evidence_count}

## CERQual Dimensions
- **Methodological Quality**: {confidence_score.methodological_quality:.3f}
- **Relevance**: {confidence_score.relevance:.3f}
- **Coherence**: {confidence_score.coherence:.3f}
- **Adequacy**: {confidence_score.adequacy:.3f}

## Uncertainty Factors
- **Estimation Uncertainty**: {confidence_score.estimation_uncertainty:.3f}
- **Temporal Decay**: {1 - confidence_score.temporal_decay_factor:.3f}
- **Cross-Modal Consistency**: {confidence_score.cross_modal_consistency:.3f}

## Timeline
- **Created**: {confidence_score.creation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}
- **Last Updated**: {confidence_score.last_updated.strftime('%Y-%m-%d %H:%M:%S')}
- **Age**: {(datetime.now() - confidence_score.creation_timestamp).days} days

## Update History
"""
        
        for i, update in enumerate(confidence_score.update_history):
            report += f"\n### Update {i+1}: {update.get('action', 'Unknown')}\n"
            report += f"- **Timestamp**: {update.get('timestamp', 'Unknown')}\n"
            
            if 'reasoning' in update:
                report += f"- **Reasoning**: {update['reasoning'][:200]}...\n"
            
            if 'belief_change' in update:
                report += f"- **Belief Change**: {update['belief_change']:+.3f}\n"
            
            if 'supporting_factors' in update:
                report += f"- **Supporting Factors**: {', '.join(update['supporting_factors'][:3])}\n"
        
        return report

# Example usage and testing
async def test_uncertainty_engine():
    """Test the uncertainty engine with real text data"""
    
    engine = UncertaintyEngine()
    
    # Load test text
    test_text = open("/home/brian/projects/Digimons/lit_review/data/test_texts/carter_speech_excerpt.txt").read()
    
    # Extract claims
    extraction_result = await engine.extract_claims_and_evidence(test_text, domain="political_science")
    
    # Assess confidence for first claim
    if extraction_result.get("main_claims"):
        first_claim = extraction_result["main_claims"][0]["claim"]
        
        initial_confidence = await engine.assess_initial_confidence(
            test_text, first_claim, domain="political_science"
        )
        
        # Generate report
        report = engine.generate_uncertainty_report(initial_confidence)
        
        # Get performance metrics
        metrics = engine.get_performance_metrics()
        
        return {
            "extraction_result": extraction_result,
            "confidence_score": initial_confidence.to_dict(),
            "report": report,
            "performance_metrics": metrics
        }
    
    return {"error": "No claims extracted"}

if __name__ == "__main__":
    # Run test
    result = asyncio.run(test_uncertainty_engine())
    
    # Save results
    with open("/home/brian/projects/Digimons/uncertainty_stress_test/validation/uncertainty_engine_test.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    print("Uncertainty Engine Test Results:")
    print(f"Claims extracted: {len(result.get('extraction_result', {}).get('main_claims', []))}")
    print(f"Overall confidence: {result.get('confidence_score', {}).get('value', 0):.3f}")
    print(f"API calls made: {result.get('performance_metrics', {}).get('api_calls_made', 0)}")