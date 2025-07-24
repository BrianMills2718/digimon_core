#!/usr/bin/env python3
"""
Bayesian Aggregation Service - Real LLM Implementation
Uses actual AI calls to analyze evidence and perform Bayesian updates
"""

import json
import numpy as np
import asyncio
import aiohttp
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Evidence:
    """Structure for holding evidence with metadata"""
    content: str
    source: str
    timestamp: datetime
    reliability: float  # 0-1
    evidence_type: str  # 'primary_source', 'peer_reviewed', etc.
    domain: str
    weight: Optional[float] = None
    likelihood: Optional[float] = None
    
class BayesianAggregationService:
    """
    Real LLM-powered Bayesian evidence aggregation
    Uses actual AI to assess evidence quality and likelihood
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required")
        
        self.evidence_history = []
        self.belief_updates = []
        self.api_base = "https://api.openai.com/v1"
        
    async def _make_llm_call(self, prompt: str, max_tokens: int = 500) -> str:
        """Make actual LLM API call"""
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
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_base}/chat/completions", 
                                  headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    logger.error(f"API call failed: {response.status}")
                    return ""
    
    async def assess_evidence_quality(self, evidence: Evidence) -> Dict[str, float]:
        """Use LLM to assess evidence quality and reliability"""
        
        prompt = f"""
        Analyze the following evidence for quality and reliability. Provide scores from 0.0 to 1.0:

        EVIDENCE CONTENT:
        {evidence.content[:1500]}...

        METADATA:
        - Source: {evidence.source}
        - Type: {evidence.evidence_type}
        - Domain: {evidence.domain}
        - Claimed Reliability: {evidence.reliability}

        Assess the following dimensions (respond with JSON format):
        {{
            "factual_accuracy": 0.0-1.0,
            "source_credibility": 0.0-1.0,
            "methodological_rigor": 0.0-1.0,
            "completeness": 0.0-1.0,
            "bias_level": 0.0-1.0 (where 1.0 = least biased),
            "relevance": 0.0-1.0,
            "supporting_evidence": 0.0-1.0,
            "logical_consistency": 0.0-1.0,
            "overall_quality": 0.0-1.0,
            "confidence_in_assessment": 0.0-1.0,
            "key_strengths": "brief description",
            "key_weaknesses": "brief description"
        }}
        """
        
        try:
            response = await self._make_llm_call(prompt, max_tokens=800)
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                quality_assessment = json.loads(json_str)
                return quality_assessment
            else:
                logger.warning("Could not parse LLM response as JSON")
                return self._default_quality_scores()
        except Exception as e:
            logger.error(f"Error in evidence quality assessment: {e}")
            return self._default_quality_scores()
    
    def _default_quality_scores(self) -> Dict[str, float]:
        """Fallback quality scores"""
        return {
            "factual_accuracy": 0.6,
            "source_credibility": 0.6,
            "methodological_rigor": 0.5,
            "completeness": 0.5,
            "bias_level": 0.6,
            "relevance": 0.7,
            "supporting_evidence": 0.5,
            "logical_consistency": 0.7,
            "overall_quality": 0.6,
            "confidence_in_assessment": 0.5,
            "key_strengths": "Default assessment",
            "key_weaknesses": "No detailed analysis available"
        }
    
    async def calculate_evidence_likelihood(self, evidence: Evidence, hypothesis: str) -> Dict[str, Any]:
        """Use LLM to calculate likelihood of evidence given hypothesis"""
        
        prompt = f"""
        Calculate the likelihood of the following evidence given the specified hypothesis.

        HYPOTHESIS:
        {hypothesis}

        EVIDENCE:
        {evidence.content[:2000]}

        Provide your analysis in JSON format:
        {{
            "likelihood_given_hypothesis": 0.0-1.0,
            "likelihood_given_not_hypothesis": 0.0-1.0,
            "diagnosticity": 0.0-1.0,
            "reasoning": "explanation of likelihood assessment",
            "key_supporting_points": ["point1", "point2", "point3"],
            "key_contradicting_points": ["point1", "point2"],
            "uncertainty_factors": ["factor1", "factor2"],
            "confidence_in_likelihood": 0.0-1.0
        }}

        Consider:
        1. How well does the evidence fit with the hypothesis?
        2. Could this evidence occur if the hypothesis were false?
        3. What are the alternative explanations?
        4. How diagnostic is this evidence (does it help distinguish between hypotheses)?
        """
        
        try:
            response = await self._make_llm_call(prompt, max_tokens=1000)
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                likelihood_analysis = json.loads(json_str)
                return likelihood_analysis
            else:
                logger.warning("Could not parse likelihood response as JSON")
                return self._default_likelihood_analysis()
        except Exception as e:
            logger.error(f"Error in likelihood calculation: {e}")
            return self._default_likelihood_analysis()
    
    def _default_likelihood_analysis(self) -> Dict[str, Any]:
        """Fallback likelihood analysis"""
        return {
            "likelihood_given_hypothesis": 0.5,
            "likelihood_given_not_hypothesis": 0.5,
            "diagnosticity": 0.3,
            "reasoning": "Default neutral assessment",
            "key_supporting_points": ["No detailed analysis available"],
            "key_contradicting_points": [],
            "uncertainty_factors": ["Insufficient analysis"],
            "confidence_in_likelihood": 0.3
        }
    
    def calculate_evidence_weight(self, evidence: Evidence, quality_scores: Dict[str, float]) -> float:
        """Calculate final evidence weight from quality assessment"""
        
        base_weight = 1.0
        
        # Quality-based weighting
        quality_weight = (
            0.25 * quality_scores.get("factual_accuracy", 0.6) +
            0.20 * quality_scores.get("source_credibility", 0.6) +
            0.15 * quality_scores.get("methodological_rigor", 0.5) +
            0.15 * quality_scores.get("logical_consistency", 0.7) +
            0.15 * quality_scores.get("bias_level", 0.6) +
            0.10 * quality_scores.get("completeness", 0.5)
        )
        
        # Temporal decay
        age_days = (datetime.now() - evidence.timestamp).days
        temporal_weight = np.exp(-age_days / 365.0)  # 1-year half-life
        
        # Evidence type multiplier
        type_weights = {
            'primary_source': 1.0,
            'peer_reviewed': 0.95,
            'government_document': 0.9,
            'secondary_source': 0.7,
            'tertiary_source': 0.5,
            'opinion': 0.3,
            'social_media': 0.2
        }
        type_weight = type_weights.get(evidence.evidence_type, 0.6)
        
        # Combine all factors
        final_weight = base_weight * quality_weight * (0.3 + 0.7 * temporal_weight) * type_weight
        
        return max(0.01, min(2.0, final_weight))
    
    def bayesian_update(self, prior_belief: float, likelihood_analysis: Dict[str, Any], 
                       evidence_weight: float) -> Dict[str, Any]:
        """Perform weighted Bayesian update"""
        
        # Extract likelihoods
        likelihood_h = likelihood_analysis.get("likelihood_given_hypothesis", 0.5)
        likelihood_not_h = likelihood_analysis.get("likelihood_given_not_hypothesis", 0.5)
        
        # Convert to log odds for numerical stability
        def prob_to_log_odds(p):
            return np.log(p / (1 - p + 1e-9))
        
        def log_odds_to_prob(log_odds):
            return 1 / (1 + np.exp(-log_odds))
        
        # Prior in log odds
        prior_log_odds = prob_to_log_odds(prior_belief)
        
        # Bayes factor
        if likelihood_not_h > 0:
            bayes_factor = likelihood_h / likelihood_not_h
            log_bayes_factor = np.log(bayes_factor)
        else:
            log_bayes_factor = 5.0  # Strong evidence for hypothesis
        
        # Weighted update
        weighted_log_bayes = evidence_weight * log_bayes_factor
        
        # Posterior calculation
        posterior_log_odds = prior_log_odds + weighted_log_bayes
        posterior_belief = log_odds_to_prob(posterior_log_odds)
        
        # Bound the result
        posterior_belief = max(0.01, min(0.99, posterior_belief))
        
        return {
            "posterior_belief": posterior_belief,
            "prior_belief": prior_belief,
            "bayes_factor": np.exp(log_bayes_factor),
            "evidence_weight": evidence_weight,
            "belief_change": posterior_belief - prior_belief,
            "log_odds_change": weighted_log_bayes,
            "diagnosticity": likelihood_analysis.get("diagnosticity", 0.5)
        }
    
    async def aggregate_evidence_batch(self, evidence_list: List[Evidence], 
                                     hypothesis: str, prior_belief: float = 0.5) -> Dict[str, Any]:
        """Process multiple pieces of evidence with real LLM analysis"""
        
        logger.info(f"Starting batch aggregation of {len(evidence_list)} evidence pieces")
        
        current_belief = prior_belief
        update_history = []
        total_diagnosticity = 0.0
        
        for i, evidence in enumerate(evidence_list):
            logger.info(f"Processing evidence {i+1}/{len(evidence_list)}")
            
            # Assess evidence quality
            quality_scores = await self.assess_evidence_quality(evidence)
            
            # Calculate likelihood given hypothesis
            likelihood_analysis = await self.calculate_evidence_likelihood(evidence, hypothesis)
            
            # Calculate evidence weight
            evidence_weight = self.calculate_evidence_weight(evidence, quality_scores)
            
            # Perform Bayesian update
            update_result = self.bayesian_update(current_belief, likelihood_analysis, evidence_weight)
            
            # Update belief
            current_belief = update_result["posterior_belief"]
            
            # Track diagnosticity
            total_diagnosticity += likelihood_analysis.get("diagnosticity", 0.5)
            
            # Record update
            update_record = {
                "evidence_id": i,
                "source": evidence.source,
                "prior": update_result["prior_belief"],
                "posterior": current_belief,
                "belief_change": update_result["belief_change"],
                "evidence_weight": evidence_weight,
                "bayes_factor": update_result["bayes_factor"],
                "diagnosticity": likelihood_analysis.get("diagnosticity", 0.5),
                "quality_overall": quality_scores.get("overall_quality", 0.6),
                "reasoning": likelihood_analysis.get("reasoning", "No reasoning available")
            }
            update_history.append(update_record)
            
            # Store for later analysis
            self.evidence_history.append({
                "evidence": evidence,
                "quality_scores": quality_scores,
                "likelihood_analysis": likelihood_analysis,
                "update_result": update_result
            })
        
        # Calculate aggregate statistics
        avg_diagnosticity = total_diagnosticity / len(evidence_list) if evidence_list else 0
        total_belief_change = current_belief - prior_belief
        
        # Calculate confidence in final belief
        confidence_factors = []
        for record in update_history:
            confidence_factors.append(record["diagnosticity"] * record["quality_overall"])
        
        avg_confidence = np.mean(confidence_factors) if confidence_factors else 0.5
        
        return {
            "final_belief": current_belief,
            "prior_belief": prior_belief,
            "total_belief_change": total_belief_change,
            "num_evidence_pieces": len(evidence_list),
            "average_diagnosticity": avg_diagnosticity,
            "confidence_in_result": avg_confidence,
            "update_history": update_history,
            "summary": {
                "strongest_evidence": max(update_history, key=lambda x: x["bayes_factor"]) if update_history else None,
                "most_diagnostic": max(update_history, key=lambda x: x["diagnosticity"]) if update_history else None,
                "largest_update": max(update_history, key=lambda x: abs(x["belief_change"])) if update_history else None
            }
        }
    
    def generate_analysis_report(self, aggregation_result: Dict[str, Any], hypothesis: str) -> str:
        """Generate human-readable analysis report"""
        
        report = f"""
# Bayesian Evidence Aggregation Report

## Hypothesis
{hypothesis}

## Summary Results
- **Final Belief**: {aggregation_result['final_belief']:.3f}
- **Prior Belief**: {aggregation_result['prior_belief']:.3f}
- **Total Change**: {aggregation_result['total_belief_change']:+.3f}
- **Evidence Pieces**: {aggregation_result['num_evidence_pieces']}
- **Average Diagnosticity**: {aggregation_result['average_diagnosticity']:.3f}
- **Confidence in Result**: {aggregation_result['confidence_in_result']:.3f}

## Key Findings
"""
        
        if aggregation_result.get('summary'):
            summary = aggregation_result['summary']
            
            if summary.get('strongest_evidence'):
                strongest = summary['strongest_evidence']
                report += f"- **Strongest Evidence**: {strongest['source']} (Bayes Factor: {strongest['bayes_factor']:.2f})\n"
            
            if summary.get('most_diagnostic'):
                diagnostic = summary['most_diagnostic']
                report += f"- **Most Diagnostic**: {diagnostic['source']} (Diagnosticity: {diagnostic['diagnosticity']:.3f})\n"
            
            if summary.get('largest_update'):
                largest = summary['largest_update']
                report += f"- **Largest Update**: {largest['source']} (Change: {largest['belief_change']:+.3f})\n"
        
        report += "\n## Evidence Analysis\n"
        
        for i, record in enumerate(aggregation_result.get('update_history', [])):
            report += f"""
### Evidence {i+1}: {record['source']}
- **Belief Change**: {record['prior']:.3f} → {record['posterior']:.3f} ({record['belief_change']:+.3f})
- **Evidence Weight**: {record['evidence_weight']:.3f}
- **Bayes Factor**: {record['bayes_factor']:.3f}
- **Diagnosticity**: {record['diagnosticity']:.3f}
- **Quality**: {record['quality_overall']:.3f}
- **Reasoning**: {record['reasoning'][:200]}...
"""
        
        return report

# Example usage and testing
async def test_with_real_data():
    """Test the service with real text data"""
    
    # Load test texts
    test_texts_dir = "/home/brian/projects/Digimons/lit_review/data/test_texts"
    
    service = BayesianAggregationService()
    
    # Create evidence from test texts
    evidence_list = []
    
    # Carter speech evidence
    carter_content = open(f"{test_texts_dir}/carter_speech_excerpt.txt").read()
    evidence_list.append(Evidence(
        content=carter_content,
        source="Carter Presidential Speech 1977",
        timestamp=datetime(1977, 7, 21),
        reliability=0.9,
        evidence_type="primary_source",
        domain="political_science"
    ))
    
    # UAP testimony evidence  
    try:
        grusch_content = open(f"{test_texts_dir}/texts/grusch_testimony.txt").read()[:3000]
        evidence_list.append(Evidence(
            content=grusch_content,
            source="Congressional UAP Hearing 2023",
            timestamp=datetime(2023, 7, 26),
            reliability=0.85,
            evidence_type="government_document",
            domain="national_security"
        ))
    except:
        logger.warning("Could not load Grusch testimony")
    
    # Test hypothesis
    hypothesis = "Government transparency in national security matters has increased over time"
    
    # Run aggregation
    result = await service.aggregate_evidence_batch(evidence_list, hypothesis, prior_belief=0.5)
    
    # Generate report
    report = service.generate_analysis_report(result, hypothesis)
    
    return result, report

if __name__ == "__main__":
    # Run test
    result, report = asyncio.run(test_with_real_data())
    print(report)
    
    # Save results
    with open("/home/brian/projects/Digimons/uncertainty_stress_test/validation/bayesian_test_results.json", "w") as f:
        json.dump(result, f, indent=2, default=str)