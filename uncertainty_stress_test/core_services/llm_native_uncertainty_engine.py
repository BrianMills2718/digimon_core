#!/usr/bin/env python3
"""
LLM-Native Uncertainty Engine
Uses contextual LLM intelligence instead of hardcoded rules and parameters
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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContextualConfidenceScore:
    """Enhanced confidence score with contextual intelligence"""
    
    # Core confidence with contextual reasoning
    value: float  # 0-1
    reasoning: str  # LLM's reasoning for this confidence level
    
    # Contextually determined quality dimensions
    quality_assessment: Dict[str, float]  # LLM-determined relevant quality factors
    uncertainty_factors: Dict[str, float]  # LLM-identified uncertainty sources
    
    # Contextual metadata
    epistemic_prior: float  # LLM-determined appropriate prior
    prior_reasoning: str  # Why this prior was chosen
    
    # Evidence integration
    evidence_synthesis: str  # How evidence was integrated
    key_strengths: List[str]  # Most important supporting factors
    key_limitations: List[str]  # Most important limiting factors
    
    # Context and provenance
    assessment_context: Dict[str, Any]  # Full context used for assessment
    creation_timestamp: datetime
    last_updated: datetime
    evidence_count: int
    update_history: List[Dict] = None
    
    # Domain and type
    domain: str = "general"
    claim_type: str = "general"  # LLM-determined claim categorization
    
    def __post_init__(self):
        if self.update_history is None:
            self.update_history = []
    
    def get_overall_confidence(self) -> float:
        """Get the contextually-determined overall confidence"""
        return self.value
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['creation_timestamp'] = self.creation_timestamp.isoformat()
        result['last_updated'] = self.last_updated.isoformat()
        return result

class LLMNativeUncertaintyEngine:
    """
    LLM-Native Uncertainty Engine using contextual intelligence
    instead of hardcoded rules and parameters
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required")
        
        # Tracking
        self.assessment_history = []
        self.analysis_cache = {}
        self.api_base = "https://api.openai.com/v1"
        
        # Performance metrics
        self.api_calls_made = 0
        self.total_processing_time = 0
        self.cache_hits = 0
        
    async def _make_llm_call(self, prompt: str, max_tokens: int = 1000) -> str:
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
            "temperature": 0.0,  # Deterministic for reproducibility
            "seed": 42
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
    
    async def determine_epistemic_prior(self, text: str, claim: str, domain: str) -> Dict[str, Any]:
        """Use LLM to intelligently determine appropriate epistemic prior"""
        
        prompt = f"""
        As an expert in epistemology and evidence assessment, determine an appropriate 
        epistemic prior probability for this claim given the context.
        
        CLAIM TO ASSESS:
        {claim}
        
        DOMAIN CONTEXT:
        {domain}
        
        TEXT CONTEXT:
        {text[:2000]}
        
        Consider:
        1. Base rates of similar claims in this field
        2. Strength of theoretical foundations in this domain
        3. Historical success rates for this type of research question
        4. Whether this is an ordinary or extraordinary claim
        5. Existing evidence base and theoretical constraints
        6. Domain-specific standards and replication rates
        
        Provide your assessment in JSON format:
        {{
            "epistemic_prior": 0.0-1.0,
            "reasoning": "detailed explanation of why this prior is appropriate",
            "claim_type": "descriptive|causal|theoretical|predictive|normative",
            "extraordinariness": "ordinary|notable|extraordinary",
            "domain_base_rate": "assessment of typical success rates in this domain",
            "theoretical_constraints": "how much existing theory constrains this claim",
            "confidence_in_prior": 0.0-1.0
        }}
        
        Remember: This prior represents your best estimate of the claim's probability 
        before considering the specific evidence presented.
        """
        
        try:
            response = await self._make_llm_call(prompt, max_tokens=800)
            
            # Parse JSON response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                prior_assessment = json.loads(json_str)
                return prior_assessment
            else:
                logger.warning("Could not parse prior assessment response")
                return self._default_prior_assessment()
                
        except Exception as e:
            logger.error(f"Error in prior assessment: {e}")
            return self._default_prior_assessment()
    
    def _default_prior_assessment(self) -> Dict[str, Any]:
        """Default prior assessment when LLM fails"""
        return {
            "epistemic_prior": 0.5,
            "reasoning": "Default neutral prior due to assessment failure",
            "claim_type": "general",
            "extraordinariness": "ordinary",
            "domain_base_rate": "unknown",
            "theoretical_constraints": "unknown",
            "confidence_in_prior": 0.3
        }
    
    async def contextual_evidence_assessment(self, text: str, claim: str, 
                                           domain: str, prior_info: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to contextually assess evidence quality and relevance"""
        
        prompt = f"""
        As an expert in research methodology and evidence assessment, analyze this 
        evidence for the given claim. Use your expertise to determine what quality 
        dimensions are most relevant and how they should be weighted for this specific case.
        
        CLAIM TO ASSESS:
        {claim}
        
        EVIDENCE TEXT:
        {text[:3000]}
        
        DOMAIN: {domain}
        CLAIM TYPE: {prior_info.get('claim_type', 'general')}
        EPISTEMIC CONTEXT: {prior_info.get('reasoning', 'No prior context')}
        
        Provide a comprehensive assessment considering:
        
        1. What are the most relevant quality dimensions for THIS specific evidence and claim?
        2. How strong is the evidence on each relevant dimension?
        3. What uncertainty factors are most important to consider?
        4. How should different quality aspects be weighted given the context?
        5. What are the key strengths and limitations?
        
        Respond in JSON format:
        {{
            "evidence_strength": 0.0-1.0,
            "quality_dimensions": {{
                "dimension_name": {{
                    "score": 0.0-1.0,
                    "importance": 0.0-1.0,
                    "reasoning": "why this dimension matters for this case"
                }}
            }},
            "uncertainty_factors": {{
                "factor_name": {{
                    "magnitude": 0.0-1.0,
                    "importance": 0.0-1.0,
                    "description": "how this uncertainty affects confidence"
                }}
            }},
            "key_strengths": ["strength1", "strength2", "strength3"],
            "key_limitations": ["limitation1", "limitation2", "limitation3"],
            "methodological_assessment": "detailed analysis of research quality",
            "relevance_assessment": "how well evidence addresses the claim",
            "overall_reasoning": "synthesis of evidence quality and relevance",
            "confidence_in_assessment": 0.0-1.0
        }}
        
        Focus on what actually matters for THIS specific case rather than applying 
        generic frameworks rigidly.
        """
        
        try:
            response = await self._make_llm_call(prompt, max_tokens=1500)
            
            # Parse JSON response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                evidence_assessment = json.loads(json_str)
                return evidence_assessment
            else:
                logger.warning("Could not parse evidence assessment response")
                return self._default_evidence_assessment()
                
        except Exception as e:
            logger.error(f"Error in evidence assessment: {e}")
            return self._default_evidence_assessment()
    
    def _default_evidence_assessment(self) -> Dict[str, Any]:
        """Default evidence assessment when LLM fails"""
        return {
            "evidence_strength": 0.5,
            "quality_dimensions": {
                "general_quality": {
                    "score": 0.5,
                    "importance": 1.0,
                    "reasoning": "Default assessment due to analysis failure"
                }
            },
            "uncertainty_factors": {
                "analysis_failure": {
                    "magnitude": 0.7,
                    "importance": 1.0,
                    "description": "High uncertainty due to failed detailed analysis"
                }
            },
            "key_strengths": ["Assessment attempted"],
            "key_limitations": ["Detailed analysis failed"],
            "methodological_assessment": "Could not perform detailed analysis",
            "relevance_assessment": "Could not assess relevance",
            "overall_reasoning": "Default assessment due to system limitations",
            "confidence_in_assessment": 0.2
        }
    
    async def intelligent_confidence_synthesis(self, prior_assessment: Dict[str, Any], 
                                             evidence_assessment: Dict[str, Any],
                                             text: str, claim: str) -> Dict[str, Any]:
        """Use LLM to intelligently synthesize prior and evidence into final confidence"""
        
        prompt = f"""
        As an expert in Bayesian reasoning and evidence synthesis, determine the final 
        confidence level for this claim by intelligently combining the prior assessment 
        and evidence analysis.
        
        CLAIM: {claim}
        
        PRIOR ASSESSMENT:
        - Epistemic Prior: {prior_assessment.get('epistemic_prior', 0.5)}
        - Reasoning: {prior_assessment.get('reasoning', 'No reasoning')}
        - Claim Type: {prior_assessment.get('claim_type', 'general')}
        
        EVIDENCE ASSESSMENT:
        - Evidence Strength: {evidence_assessment.get('evidence_strength', 0.5)}
        - Key Strengths: {evidence_assessment.get('key_strengths', [])}
        - Key Limitations: {evidence_assessment.get('key_limitations', [])}
        - Quality Dimensions: {json.dumps(evidence_assessment.get('quality_dimensions', {}), indent=2)}
        - Uncertainty Factors: {json.dumps(evidence_assessment.get('uncertainty_factors', {}), indent=2)}
        
        Your task is to intelligently synthesize these inputs into a final confidence assessment.
        Consider:
        
        1. How much should the evidence update the prior belief?
        2. What are the most important factors affecting confidence?
        3. How do different sources of uncertainty interact?
        4. What is the appropriate confidence level given all considerations?
        5. How confident are you in this confidence assessment (meta-uncertainty)?
        
        Provide your synthesis in JSON format:
        {{
            "final_confidence": 0.0-1.0,
            "confidence_reasoning": "detailed explanation of how you arrived at this confidence",
            "prior_to_posterior_update": "how and why the evidence updated the prior",
            "key_factors": ["most important factors influencing confidence"],
            "uncertainty_synthesis": "how different uncertainty sources were integrated",
            "sensitivity_analysis": "how sensitive is this confidence to key assumptions",
            "meta_uncertainty": 0.0-1.0,
            "meta_reasoning": "uncertainty about the uncertainty estimate itself",
            "alternative_interpretations": ["other reasonable confidence levels and why"],
            "confidence_bounds": {{
                "lower_bound": 0.0-1.0,
                "upper_bound": 0.0-1.0,
                "reasoning": "why these bounds are appropriate"
            }}
        }}
        
        Be thoughtful about the interaction between prior beliefs and evidence strength.
        Strong evidence can substantially update weak priors, but extraordinary claims
        require extraordinary evidence even with strong methodology.
        """
        
        try:
            response = await self._make_llm_call(prompt, max_tokens=1200)
            
            # Parse JSON response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                synthesis = json.loads(json_str)
                return synthesis
            else:
                logger.warning("Could not parse confidence synthesis response")
                return self._default_confidence_synthesis(prior_assessment, evidence_assessment)
                
        except Exception as e:
            logger.error(f"Error in confidence synthesis: {e}")
            return self._default_confidence_synthesis(prior_assessment, evidence_assessment)
    
    def _default_confidence_synthesis(self, prior_assessment: Dict[str, Any], 
                                    evidence_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Default confidence synthesis when LLM fails"""
        
        # Simple fallback: average prior and evidence strength
        prior = prior_assessment.get('epistemic_prior', 0.5)
        evidence = evidence_assessment.get('evidence_strength', 0.5)
        fallback_confidence = (prior + evidence) / 2
        
        return {
            "final_confidence": fallback_confidence,
            "confidence_reasoning": "Fallback synthesis due to detailed analysis failure",
            "prior_to_posterior_update": f"Simple average of prior ({prior}) and evidence ({evidence})",
            "key_factors": ["System limitations prevented detailed analysis"],
            "uncertainty_synthesis": "High uncertainty due to analysis failure",
            "sensitivity_analysis": "Cannot assess sensitivity with failed analysis",
            "meta_uncertainty": 0.8,
            "meta_reasoning": "Very high uncertainty due to system limitations",
            "alternative_interpretations": ["Could range widely due to incomplete analysis"],
            "confidence_bounds": {
                "lower_bound": max(0.0, fallback_confidence - 0.3),
                "upper_bound": min(1.0, fallback_confidence + 0.3),
                "reasoning": "Wide bounds due to analysis limitations"
            }
        }
    
    async def assess_contextual_confidence(self, text: str, claim: str, 
                                         domain: str = "general") -> ContextualConfidenceScore:
        """Main method: Assess confidence using contextual LLM intelligence"""
        
        logger.info(f"Starting contextual confidence assessment for claim: {claim[:100]}...")
        
        # Step 1: Determine appropriate epistemic prior
        logger.info("Determining epistemic prior...")
        prior_assessment = await self.determine_epistemic_prior(text, claim, domain)
        
        # Step 2: Contextually assess evidence quality
        logger.info("Assessing evidence quality contextually...")
        evidence_assessment = await self.contextual_evidence_assessment(
            text, claim, domain, prior_assessment
        )
        
        # Step 3: Intelligently synthesize into final confidence
        logger.info("Synthesizing final confidence assessment...")
        confidence_synthesis = await self.intelligent_confidence_synthesis(
            prior_assessment, evidence_assessment, text, claim
        )
        
        # Create contextual confidence score
        contextual_score = ContextualConfidenceScore(
            value=confidence_synthesis.get("final_confidence", 0.5),
            reasoning=confidence_synthesis.get("confidence_reasoning", "No reasoning available"),
            quality_assessment=evidence_assessment.get("quality_dimensions", {}),
            uncertainty_factors=evidence_assessment.get("uncertainty_factors", {}),
            epistemic_prior=prior_assessment.get("epistemic_prior", 0.5),
            prior_reasoning=prior_assessment.get("reasoning", "No prior reasoning"),
            evidence_synthesis=confidence_synthesis.get("prior_to_posterior_update", "No synthesis"),
            key_strengths=evidence_assessment.get("key_strengths", []),
            key_limitations=evidence_assessment.get("key_limitations", []),
            assessment_context={
                "prior_assessment": prior_assessment,
                "evidence_assessment": evidence_assessment,
                "confidence_synthesis": confidence_synthesis
            },
            creation_timestamp=datetime.now(),
            last_updated=datetime.now(),
            evidence_count=1,
            domain=domain,
            claim_type=prior_assessment.get("claim_type", "general")
        )
        
        # Record assessment
        self.assessment_history.append(contextual_score)
        
        logger.info(f"Contextual assessment complete. Final confidence: {contextual_score.value:.3f}")
        
        return contextual_score
    
    async def update_confidence_with_new_evidence(self, 
                                                current_confidence: ContextualConfidenceScore,
                                                new_text: str,
                                                new_claim_context: str = None) -> ContextualConfidenceScore:
        """Update confidence with new evidence using contextual intelligence"""
        
        logger.info("Updating confidence with new evidence using contextual intelligence...")
        
        prompt = f"""
        As an expert in evidence synthesis, update the confidence assessment for this claim
        given new evidence. Use your expertise to determine how the new evidence should
        change the existing confidence level.
        
        ORIGINAL CLAIM: {new_claim_context or "Same as before"}
        
        CURRENT CONFIDENCE ASSESSMENT:
        - Current Confidence: {current_confidence.value}
        - Current Reasoning: {current_confidence.reasoning}
        - Key Current Strengths: {current_confidence.key_strengths}
        - Key Current Limitations: {current_confidence.key_limitations}
        - Evidence Count: {current_confidence.evidence_count}
        
        NEW EVIDENCE:
        {new_text[:3000]}
        
        Consider:
        1. How does this new evidence relate to existing evidence?
        2. Does it corroborate, contradict, or add new dimensions?
        3. What is the quality and relevance of this new evidence?
        4. How should it update the overall confidence assessment?
        5. What new strengths or limitations does it introduce?
        
        Provide updated assessment in JSON format:
        {{
            "updated_confidence": 0.0-1.0,
            "confidence_change": "increase|decrease|minimal_change",
            "change_magnitude": 0.0-1.0,
            "update_reasoning": "detailed explanation of how new evidence affected confidence",
            "new_evidence_quality": 0.0-1.0,
            "evidence_relationship": "corroborating|contradicting|orthogonal|extending",
            "updated_strengths": ["strength1", "strength2"],
            "updated_limitations": ["limitation1", "limitation2"],
            "synthesis_approach": "how you integrated old and new evidence",
            "confidence_trajectory": "direction and stability of confidence over evidence",
            "meta_uncertainty_change": 0.0-1.0
        }}
        
        Focus on intelligent synthesis rather than mechanical combination.
        """
        
        try:
            response = await self._make_llm_call(prompt, max_tokens=1000)
            
            # Parse JSON response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                update_assessment = json.loads(json_str)
                
                # Create updated confidence score
                updated_confidence = ContextualConfidenceScore(
                    value=update_assessment.get("updated_confidence", current_confidence.value),
                    reasoning=update_assessment.get("update_reasoning", current_confidence.reasoning),
                    quality_assessment=current_confidence.quality_assessment,  # Maintain quality assessment
                    uncertainty_factors=current_confidence.uncertainty_factors,  # Update if needed
                    epistemic_prior=current_confidence.epistemic_prior,  # Priors don't change
                    prior_reasoning=current_confidence.prior_reasoning,
                    evidence_synthesis=update_assessment.get("synthesis_approach", current_confidence.evidence_synthesis),
                    key_strengths=update_assessment.get("updated_strengths", current_confidence.key_strengths),
                    key_limitations=update_assessment.get("updated_limitations", current_confidence.key_limitations),
                    assessment_context={
                        **current_confidence.assessment_context,
                        "evidence_update": update_assessment
                    },
                    creation_timestamp=current_confidence.creation_timestamp,
                    last_updated=datetime.now(),
                    evidence_count=current_confidence.evidence_count + 1,
                    update_history=current_confidence.update_history.copy(),
                    domain=current_confidence.domain,
                    claim_type=current_confidence.claim_type
                )
                
                # Record update in history
                updated_confidence.update_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "contextual_evidence_update",
                    "confidence_change": update_assessment.get("change_magnitude", 0),
                    "evidence_relationship": update_assessment.get("evidence_relationship", "unknown"),
                    "reasoning": update_assessment.get("update_reasoning", "No reasoning")
                })
                
                return updated_confidence
                
        except Exception as e:
            logger.error(f"Error in contextual confidence update: {e}")
            # Return original confidence if update fails
            return current_confidence
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the contextual uncertainty engine"""
        
        return {
            "api_calls_made": self.api_calls_made,
            "total_processing_time": self.total_processing_time,
            "average_call_time": self.total_processing_time / max(1, self.api_calls_made),
            "cache_hits": self.cache_hits,
            "cache_hit_rate": self.cache_hits / max(1, len(self.analysis_cache)),
            "assessments_completed": len(self.assessment_history),
            "cached_analyses": len(self.analysis_cache)
        }
    
    def generate_contextual_report(self, confidence_score: ContextualConfidenceScore) -> str:
        """Generate comprehensive contextual assessment report"""
        
        report = f"""# Contextual Uncertainty Analysis Report

## Claim Assessment
**Claim**: {confidence_score.assessment_context.get('claim', 'Not specified')[:200]}...
**Domain**: {confidence_score.domain}
**Claim Type**: {confidence_score.claim_type}

## Final Confidence Assessment
**Confidence Level**: {confidence_score.value:.3f}
**Confidence Bounds**: {confidence_score.assessment_context.get('confidence_synthesis', {}).get('confidence_bounds', {})}

### Reasoning
{confidence_score.reasoning}

## Epistemic Foundation
**Prior Probability**: {confidence_score.epistemic_prior:.3f}
**Prior Reasoning**: {confidence_score.prior_reasoning}

## Evidence Analysis
**Evidence Synthesis**: {confidence_score.evidence_synthesis}

### Key Strengths
{chr(10).join(['- ' + strength for strength in confidence_score.key_strengths])}

### Key Limitations  
{chr(10).join(['- ' + limitation for limitation in confidence_score.key_limitations])}

## Quality Dimensions
"""
        
        for dimension, details in confidence_score.quality_assessment.items():
            if isinstance(details, dict):
                score = details.get('score', 'N/A')
                importance = details.get('importance', 'N/A')
                reasoning = details.get('reasoning', 'N/A')
                report += f"**{dimension.replace('_', ' ').title()}**: {score} (importance: {importance})\n"
                report += f"- {reasoning}\n\n"
        
        report += "## Uncertainty Factors\n"
        
        for factor, details in confidence_score.uncertainty_factors.items():
            if isinstance(details, dict):
                magnitude = details.get('magnitude', 'N/A')
                importance = details.get('importance', 'N/A')
                description = details.get('description', 'N/A')
                report += f"**{factor.replace('_', ' ').title()}**: {magnitude} (importance: {importance})\n"
                report += f"- {description}\n\n"
        
        # Meta-analysis
        synthesis = confidence_score.assessment_context.get('confidence_synthesis', {})
        report += f"""
## Meta-Analysis
**Meta-Uncertainty**: {synthesis.get('meta_uncertainty', 'N/A')}
**Sensitivity**: {synthesis.get('sensitivity_analysis', 'N/A')}

## Assessment Timeline
- **Created**: {confidence_score.creation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}
- **Last Updated**: {confidence_score.last_updated.strftime('%Y-%m-%d %H:%M:%S')}
- **Evidence Pieces**: {confidence_score.evidence_count}
- **Updates**: {len(confidence_score.update_history)}

---
*Report generated by LLM-Native Uncertainty Engine*
"""
        
        return report

# Example usage and testing
async def test_llm_native_engine():
    """Test the LLM-native uncertainty engine"""
    
    import os
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No API key available for testing")
        return
    
    engine = LLMNativeUncertaintyEngine(api_key)
    
    # Test with different types of claims
    test_cases = [
        {
            "text": """
            A randomized controlled trial (N=500) published in Nature Medicine found that 
            a new drug reduces heart attack risk by 40% (p<0.001). The study was double-blinded,
            multi-center, and had independent data monitoring. All patients were followed for 
            2 years with no significant adverse effects reported.
            """,
            "claim": "The new drug significantly reduces heart attack risk",
            "domain": "medical_research"
        },
        {
            "text": """
            A single study (N=20) from an unknown university suggests that drinking coffee
            while standing on one foot improves memory by 500%. The study had no control group
            and used self-reported memory assessments. The lead author has published similar
            extraordinary claims before.
            """,
            "claim": "Standing on one foot while drinking coffee dramatically improves memory",
            "domain": "cognitive_science"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases):
        print(f"\n{'='*60}")
        print(f"Testing Case {i+1}: {test_case['claim'][:50]}...")
        print(f"{'='*60}")
        
        confidence_score = await engine.assess_contextual_confidence(
            test_case["text"], 
            test_case["claim"], 
            test_case["domain"]
        )
        
        print(f"Final Confidence: {confidence_score.value:.3f}")
        print(f"Epistemic Prior: {confidence_score.epistemic_prior:.3f}")
        print(f"Key Strengths: {confidence_score.key_strengths}")
        print(f"Key Limitations: {confidence_score.key_limitations}")
        
        results.append({
            "case": i+1,
            "confidence": confidence_score.value,
            "prior": confidence_score.epistemic_prior,
            "reasoning": confidence_score.reasoning[:200] + "...",
            "full_assessment": confidence_score.to_dict()
        })
    
    # Performance metrics
    metrics = engine.get_performance_metrics()
    print(f"\n{'='*60}")
    print("PERFORMANCE METRICS")
    print(f"{'='*60}")
    print(f"API Calls Made: {metrics['api_calls_made']}")
    print(f"Total Processing Time: {metrics['total_processing_time']:.2f}s")
    print(f"Average Call Time: {metrics['average_call_time']:.2f}s")
    
    return results, metrics

if __name__ == "__main__":
    # Run test
    results, metrics = asyncio.run(test_llm_native_engine())
    
    # Save results
    output_path = "/home/brian/projects/Digimons/uncertainty_stress_test/validation/llm_native_test_results.json"
    with open(output_path, "w") as f:
        json.dump({
            "test_results": results,
            "performance_metrics": metrics,
            "test_timestamp": datetime.now().isoformat()
        }, f, indent=2, default=str)
    
    print(f"\nResults saved to: {output_path}")