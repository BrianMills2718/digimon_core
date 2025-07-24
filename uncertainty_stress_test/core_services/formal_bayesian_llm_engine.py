#!/usr/bin/env python3
"""
Formal Bayesian LLM Engine
Combines rigorous Bayesian mathematics with LLM-determined parameters
"""

import json
import numpy as np
import asyncio
import aiohttp
import os
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import math

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BayesianParameters:
    """Formally specified Bayesian parameters determined by LLM"""
    
    # Prior specification
    prior_belief: float  # P(H) - prior probability of hypothesis
    prior_confidence: float  # Concentration parameter for Beta prior
    
    # Likelihood specification  
    likelihood_given_h: float  # P(E|H) - probability of evidence given hypothesis true
    likelihood_given_not_h: float  # P(E|¬H) - probability of evidence given hypothesis false
    
    # Evidence strength
    evidence_weight: float  # How much evidence to consider (0-1, for partial updating)
    evidence_quality: float  # Quality adjustment factor
    
    # Meta-parameters
    update_confidence: float  # Confidence in the likelihood assessments
    
    # LLM reasoning
    parameter_reasoning: Dict[str, str]  # Explanations for each parameter choice
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass 
class BayesianUpdate:
    """Complete Bayesian update with formal mathematics"""
    
    # Input parameters
    prior: float
    likelihood_h: float
    likelihood_not_h: float
    evidence_weight: float
    
    # Calculated values
    bayes_factor: float  # BF = P(E|H) / P(E|¬H)
    log_bayes_factor: float  # log(BF) for numerical stability
    marginal_likelihood: float  # P(E) = P(E|H)P(H) + P(E|¬H)P(¬H)
    
    # Posterior results
    posterior_belief: float  # P(H|E) - updated probability
    posterior_odds: float  # P(H|E) / P(¬H|E)
    prior_odds: float  # P(H) / P(¬H)
    
    # Update magnitude
    belief_change: float  # |posterior - prior|
    odds_ratio: float  # posterior_odds / prior_odds
    
    # Confidence bounds (using Beta distribution approximation)
    posterior_lower_bound: float
    posterior_upper_bound: float
    
    def to_dict(self) -> Dict:
        return asdict(self)

class FormalBayesianLLMEngine:
    """
    Formal Bayesian Engine using LLM-determined parameters
    Implements rigorous Bayesian mathematics with AI parameter estimation
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required")
        
        self.assessment_history = []
        self.api_base = "https://api.openai.com/v1"
        self.api_calls_made = 0
    
    async def _make_llm_call(self, prompt: str, max_tokens: int = 1000) -> str:
        """Make LLM API call for parameter determination"""
        self.api_calls_made += 1
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.1,  # Low but not zero for methodological variation
            "seed": 42
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_base}/chat/completions", 
                                      headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        logger.error(f"API call failed: {response.status}")
                        return ""
        except Exception as e:
            logger.error(f"LLM API call error: {e}")
            return ""
    
    async def determine_bayesian_parameters(self, text: str, claim: str, 
                                          domain: str) -> BayesianParameters:
        """Use LLM to determine parameters for formal Bayesian analysis"""
        
        prompt = f"""
        As an expert in Bayesian statistics and evidence assessment, determine the 
        parameters for formal Bayesian analysis of this claim and evidence.
        
        CLAIM (Hypothesis H):
        {claim}
        
        EVIDENCE (E):
        {text[:2500]}
        
        DOMAIN: {domain}
        
        Determine these Bayesian parameters with rigorous reasoning:
        
        1. PRIOR BELIEF P(H): What is the prior probability this claim is true?
           Consider base rates, domain knowledge, claim extraordinariness.
        
        2. PRIOR CONFIDENCE: How confident are you in this prior? 
           (Higher = more concentrated Beta prior, lower = more diffuse)
        
        3. LIKELIHOOD P(E|H): If the claim were TRUE, what's the probability 
           of observing exactly this evidence?
        
        4. LIKELIHOOD P(E|¬H): If the claim were FALSE, what's the probability 
           of observing exactly this evidence?
        
        5. EVIDENCE WEIGHT: How much of the evidence should update beliefs?
           (1.0 = full evidence, <1.0 = partial/uncertain evidence)
        
        6. EVIDENCE QUALITY: Overall quality multiplier for evidence strength.
        
        7. UPDATE CONFIDENCE: How confident are you in your likelihood assessments?
        
        Provide your assessment in JSON format:
        {{
            "prior_belief": 0.0-1.0,
            "prior_confidence": 0.1-10.0,
            "likelihood_given_h": 0.0-1.0,
            "likelihood_given_not_h": 0.0-1.0,
            "evidence_weight": 0.0-1.0,
            "evidence_quality": 0.0-2.0,
            "update_confidence": 0.0-1.0,
            "parameter_reasoning": {{
                "prior_belief": "why this prior probability",
                "likelihood_given_h": "why this likelihood if claim true",
                "likelihood_given_not_h": "why this likelihood if claim false",
                "evidence_weight": "why this evidence weight",
                "bayes_factor_interpretation": "what the likelihood ratio means"
            }}
        }}
        
        CRITICAL: Think carefully about likelihood assessments. 
        - If evidence strongly supports the claim: P(E|H) >> P(E|¬H)
        - If evidence contradicts the claim: P(E|H) << P(E|¬H)  
        - If evidence is neutral: P(E|H) ≈ P(E|¬H)
        
        Remember: The Bayes factor P(E|H)/P(E|¬H) determines update strength.
        """
        
        try:
            response = await self._make_llm_call(prompt, max_tokens=1200)
            
            # Parse JSON response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                params_dict = json.loads(json_str)
                
                return BayesianParameters(
                    prior_belief=params_dict.get("prior_belief", 0.5),
                    prior_confidence=params_dict.get("prior_confidence", 1.0),
                    likelihood_given_h=params_dict.get("likelihood_given_h", 0.5),
                    likelihood_given_not_h=params_dict.get("likelihood_given_not_h", 0.5),
                    evidence_weight=params_dict.get("evidence_weight", 1.0),
                    evidence_quality=params_dict.get("evidence_quality", 1.0),
                    update_confidence=params_dict.get("update_confidence", 0.5),
                    parameter_reasoning=params_dict.get("parameter_reasoning", {})
                )
                
        except Exception as e:
            logger.error(f"Error determining Bayesian parameters: {e}")
        
        # Fallback parameters
        return BayesianParameters(
            prior_belief=0.5,
            prior_confidence=1.0,
            likelihood_given_h=0.6,
            likelihood_given_not_h=0.4,
            evidence_weight=0.8,
            evidence_quality=0.6,
            update_confidence=0.3,
            parameter_reasoning={
                "fallback": "Default parameters due to LLM parameter determination failure"
            }
        )
    
    def formal_bayesian_update(self, parameters: BayesianParameters) -> BayesianUpdate:
        """
        Perform formal Bayesian update using rigorous mathematics
        
        Implements:
        - Bayes' Theorem: P(H|E) = P(E|H) * P(H) / P(E)
        - Bayes Factor: BF = P(E|H) / P(E|¬H)  
        - Posterior Odds: P(H|E) / P(¬H|E) = BF * P(H) / P(¬H)
        - Evidence weighting for partial updates
        """
        
        # Extract parameters
        prior = parameters.prior_belief
        likelihood_h = parameters.likelihood_given_h
        likelihood_not_h = parameters.likelihood_given_not_h
        evidence_weight = parameters.evidence_weight
        quality = parameters.evidence_quality
        
        # Numerical stability bounds
        likelihood_h = max(0.001, min(0.999, likelihood_h))
        likelihood_not_h = max(0.001, min(0.999, likelihood_not_h))
        prior = max(0.001, min(0.999, prior))
        
        # Calculate Bayes factor
        bayes_factor = likelihood_h / likelihood_not_h
        log_bayes_factor = np.log(bayes_factor)
        
        # Apply evidence weighting and quality adjustment
        # Weighted update: move partway toward full Bayesian update
        effective_log_bf = log_bayes_factor * evidence_weight * quality
        effective_bf = np.exp(effective_log_bf)
        
        # Calculate marginal likelihood P(E)
        marginal_likelihood = likelihood_h * prior + likelihood_not_h * (1 - prior)
        
        # Prior odds
        prior_odds = prior / (1 - prior)
        
        # Posterior odds = Prior odds × Effective Bayes factor
        posterior_odds = prior_odds * effective_bf
        
        # Convert posterior odds back to probability
        posterior_belief = posterior_odds / (1 + posterior_odds)
        
        # Ensure valid probability bounds
        posterior_belief = max(0.001, min(0.999, posterior_belief))
        
        # Calculate belief change
        belief_change = abs(posterior_belief - prior)
        odds_ratio = posterior_odds / prior_odds
        
        # Calculate confidence bounds using simple normal approximation
        # Use effective sample size based on evidence weight and quality
        effective_n = parameters.prior_confidence * evidence_weight * quality
        
        # Normal approximation for confidence bounds
        if effective_n > 1:
            # Standard error approximation for binomial proportion
            se = math.sqrt(posterior_belief * (1 - posterior_belief) / effective_n)
            
            # 95% confidence interval (±1.96 * SE)
            margin = 1.96 * se
            lower_bound = max(0.001, posterior_belief - margin)
            upper_bound = min(0.999, posterior_belief + margin)
        else:
            # Wide bounds if insufficient effective evidence
            lower_bound = max(0.001, posterior_belief - 0.4)
            upper_bound = min(0.999, posterior_belief + 0.4)
        
        return BayesianUpdate(
            prior=prior,
            likelihood_h=likelihood_h,
            likelihood_not_h=likelihood_not_h,
            evidence_weight=evidence_weight,
            bayes_factor=bayes_factor,
            log_bayes_factor=log_bayes_factor,
            marginal_likelihood=marginal_likelihood,
            posterior_belief=posterior_belief,
            posterior_odds=posterior_odds,
            prior_odds=prior_odds,
            belief_change=belief_change,
            odds_ratio=odds_ratio,
            posterior_lower_bound=lower_bound,
            posterior_upper_bound=upper_bound
        )
    
    async def assess_claim_with_formal_bayesian(self, text: str, claim: str, 
                                              domain: str = "general") -> Dict[str, Any]:
        """
        Complete formal Bayesian assessment combining LLM parameter determination 
        with rigorous mathematical updating
        """
        
        logger.info(f"Starting formal Bayesian assessment for: {claim[:100]}...")
        
        # Step 1: LLM determines Bayesian parameters
        logger.info("LLM determining Bayesian parameters...")
        parameters = await self.determine_bayesian_parameters(text, claim, domain)
        
        # Step 2: Formal mathematical Bayesian update
        logger.info("Performing formal Bayesian update...")
        update = self.formal_bayesian_update(parameters)
        
        # Step 3: Compile comprehensive assessment
        assessment = {
            "claim": claim,
            "domain": domain,
            
            # Final results
            "posterior_belief": update.posterior_belief,
            "confidence_bounds": [update.posterior_lower_bound, update.posterior_upper_bound],
            "belief_change": update.belief_change,
            
            # Bayesian mathematics
            "bayesian_update": update.to_dict(),
            "parameters": parameters.to_dict(),
            
            # Interpretation
            "bayes_factor": update.bayes_factor,
            "bayes_factor_interpretation": self._interpret_bayes_factor(update.bayes_factor),
            "evidence_strength": self._interpret_evidence_strength(update.odds_ratio),
            
            # Meta-analysis
            "update_magnitude": self._classify_update_magnitude(update.belief_change),
            "parameter_confidence": parameters.update_confidence,
            
            # Methodology
            "methodology": "formal_bayesian_with_llm_parameters",
            "mathematical_specification": {
                "bayes_theorem": "P(H|E) = P(E|H) × P(H) / P(E)",
                "bayes_factor": "BF = P(E|H) / P(E|¬H)",
                "posterior_odds": "P(H|E) / P(¬H|E) = BF × P(H) / P(¬H)",
                "evidence_weighting": "Effective BF = BF^(weight × quality)"
            },
            
            # Audit trail
            "assessment_timestamp": datetime.now().isoformat(),
            "api_calls_made": 1,
            "llm_reasoning": parameters.parameter_reasoning
        }
        
        self.assessment_history.append(assessment)
        
        logger.info(f"Formal Bayesian assessment complete. Posterior: {update.posterior_belief:.3f} "
                   f"(95% CI: {update.posterior_lower_bound:.3f}-{update.posterior_upper_bound:.3f})")
        
        return assessment
    
    def _interpret_bayes_factor(self, bf: float) -> str:
        """Interpret Bayes factor using Jeffreys' scale"""
        
        if bf > 100:
            return "Extreme evidence for hypothesis"
        elif bf > 30:
            return "Very strong evidence for hypothesis"
        elif bf > 10:
            return "Strong evidence for hypothesis"
        elif bf > 3:
            return "Moderate evidence for hypothesis"
        elif bf > 1:
            return "Weak evidence for hypothesis"
        elif bf == 1:
            return "No evidence either way"
        elif bf > 1/3:
            return "Weak evidence against hypothesis"
        elif bf > 1/10:
            return "Moderate evidence against hypothesis"
        elif bf > 1/30:
            return "Strong evidence against hypothesis"
        elif bf > 1/100:
            return "Very strong evidence against hypothesis"
        else:
            return "Extreme evidence against hypothesis"
    
    def _interpret_evidence_strength(self, odds_ratio: float) -> str:
        """Interpret the strength of belief update"""
        
        if odds_ratio > 10:
            return "Very strong positive update"
        elif odds_ratio > 3:
            return "Strong positive update"
        elif odds_ratio > 1.5:
            return "Moderate positive update"
        elif odds_ratio > 1.1:
            return "Weak positive update"
        elif 0.9 <= odds_ratio <= 1.1:
            return "Minimal update"
        elif odds_ratio > 0.67:
            return "Weak negative update"
        elif odds_ratio > 0.33:
            return "Moderate negative update"
        elif odds_ratio > 0.1:
            return "Strong negative update"
        else:
            return "Very strong negative update"
    
    def _classify_update_magnitude(self, belief_change: float) -> str:
        """Classify the magnitude of belief change"""
        
        if belief_change > 0.4:
            return "Major belief revision"
        elif belief_change > 0.2:
            return "Substantial belief change"
        elif belief_change > 0.1:
            return "Moderate belief change"
        elif belief_change > 0.05:
            return "Minor belief change"
        else:
            return "Minimal belief change"
    
    async def multi_evidence_bayesian_chain(self, claim: str, evidence_list: List[Dict], 
                                          domain: str = "general") -> Dict[str, Any]:
        """
        Chain multiple pieces of evidence through sequential Bayesian updates
        Each piece of evidence updates the posterior, which becomes the prior for the next
        """
        
        logger.info(f"Starting Bayesian evidence chain with {len(evidence_list)} pieces")
        
        current_belief = 0.5  # Start with neutral prior
        update_chain = []
        
        for i, evidence in enumerate(evidence_list):
            logger.info(f"Processing evidence {i+1}/{len(evidence_list)}")
            
            # Determine parameters for this evidence
            parameters = await self.determine_bayesian_parameters(
                evidence["text"], claim, domain
            )
            
            # Override prior with current belief from previous updates
            parameters.prior_belief = current_belief
            
            # Perform Bayesian update
            update = self.formal_bayesian_update(parameters)
            
            # Update current belief for next iteration
            current_belief = update.posterior_belief
            
            # Record this update
            update_record = {
                "evidence_id": i + 1,
                "evidence_source": evidence.get("source", f"Evidence {i+1}"),
                "prior": update.prior,
                "posterior": update.posterior_belief,
                "bayes_factor": update.bayes_factor,
                "belief_change": update.belief_change,
                "update": update.to_dict(),
                "parameters": parameters.to_dict()
            }
            update_chain.append(update_record)
        
        # Calculate final assessment
        final_assessment = {
            "claim": claim,
            "domain": domain,
            "evidence_count": len(evidence_list),
            
            # Final results
            "final_belief": current_belief,
            "initial_belief": 0.5,
            "total_belief_change": current_belief - 0.5,
            
            # Chain analysis
            "update_chain": update_chain,
            "cumulative_bayes_factor": np.prod([u["bayes_factor"] for u in update_chain]),
            "average_individual_update": np.mean([u["belief_change"] for u in update_chain]),
            
            # Final confidence bounds (from last update)
            "confidence_bounds": [
                update_chain[-1]["update"]["posterior_lower_bound"],
                update_chain[-1]["update"]["posterior_upper_bound"]
            ] if update_chain else [current_belief - 0.3, current_belief + 0.3],
            
            # Methodology
            "methodology": "sequential_bayesian_updates",
            "mathematical_specification": {
                "sequential_updating": "P(H|E1,E2,...,En) = P(H|E1,E2,...,En-1) × BF_n / Z_n",
                "evidence_independence": "Assumes conditional independence of evidence pieces",
                "prior_propagation": "Posterior from step i becomes prior for step i+1"
            },
            
            "assessment_timestamp": datetime.now().isoformat()
        }
        
        return final_assessment
    
    def generate_formal_report(self, assessment: Dict[str, Any]) -> str:
        """Generate formal Bayesian analysis report"""
        
        report = f"""# Formal Bayesian Analysis Report

## Claim Assessment
**Claim**: {assessment['claim']}
**Domain**: {assessment['domain']}
**Methodology**: {assessment['methodology']}

## Bayesian Results
**Posterior Belief**: {assessment['posterior_belief']:.4f}
**95% Confidence Interval**: [{assessment['confidence_bounds'][0]:.4f}, {assessment['confidence_bounds'][1]:.4f}]
**Belief Change**: {assessment['belief_change']:+.4f}

## Mathematical Analysis
**Bayes Factor**: {assessment['bayes_factor']:.4f} ({assessment['bayes_factor_interpretation']})
**Evidence Strength**: {assessment['evidence_strength']}
**Update Magnitude**: {assessment['update_magnitude']}

## Bayesian Parameters (LLM-Determined)
**Prior Belief P(H)**: {assessment['parameters']['prior_belief']:.4f}
**Likelihood P(E|H)**: {assessment['parameters']['likelihood_given_h']:.4f}
**Likelihood P(E|¬H)**: {assessment['parameters']['likelihood_given_not_h']:.4f}
**Evidence Weight**: {assessment['parameters']['evidence_weight']:.4f}
**Evidence Quality**: {assessment['parameters']['evidence_quality']:.4f}

## LLM Reasoning for Parameters
"""
        
        for param, reasoning in assessment['parameters']['parameter_reasoning'].items():
            report += f"**{param.replace('_', ' ').title()}**: {reasoning}\n\n"
        
        report += f"""
## Mathematical Specification
The analysis follows formal Bayesian updating:

1. **Bayes' Theorem**: P(H|E) = P(E|H) × P(H) / P(E)
2. **Bayes Factor**: BF = P(E|H) / P(E|¬H) = {assessment['bayes_factor']:.4f}
3. **Posterior Odds**: P(H|E) / P(¬H|E) = BF × P(H) / P(¬H)
4. **Evidence Weighting**: Effective BF = BF^(weight × quality)

## Bayesian Update Details
- **Prior Odds**: {assessment['bayesian_update']['prior_odds']:.4f}
- **Posterior Odds**: {assessment['bayesian_update']['posterior_odds']:.4f}
- **Odds Ratio**: {assessment['bayesian_update']['odds_ratio']:.4f}
- **Log Bayes Factor**: {assessment['bayesian_update']['log_bayes_factor']:.4f}
- **Marginal Likelihood P(E)**: {assessment['bayesian_update']['marginal_likelihood']:.4f}

## Methodological Notes
- **Parameter Determination**: LLM-based assessment of Bayesian parameters
- **Mathematical Rigor**: Formal Bayesian updating with confidence bounds
- **Evidence Weighting**: Partial updating based on evidence quality and weight
- **Reproducibility**: Same methodology with potential parameter variation (like human analysts)

---
*Report generated by Formal Bayesian LLM Engine*
*Assessment timestamp: {assessment['assessment_timestamp']}*
"""
        
        return report

# Example usage and testing
async def test_formal_bayesian_engine():
    """Test the formal Bayesian engine with real examples"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No API key available for testing")
        return
    
    engine = FormalBayesianLLMEngine(api_key)
    
    # Test case: Strong medical evidence
    test_case = {
        "text": """
        A large randomized controlled trial (N=2,847) published in New England Journal of Medicine 
        found that treatment X reduces mortality by 35% (95% CI: 28-42%, p<0.001). The study was 
        conducted across 15 medical centers with rigorous inclusion criteria, double-blinding, and 
        independent data monitoring. Follow-up was complete for 98% of participants over 3 years.
        """,
        "claim": "Treatment X significantly reduces mortality compared to standard care",
        "domain": "medical_research"
    }
    
    print("🧮 Testing Formal Bayesian Analysis")
    print("=" * 50)
    
    # Perform formal Bayesian assessment
    assessment = await engine.assess_claim_with_formal_bayesian(
        test_case["text"], test_case["claim"], test_case["domain"]
    )
    
    # Generate report
    report = engine.generate_formal_report(assessment)
    
    print(f"Posterior Belief: {assessment['posterior_belief']:.4f}")
    print(f"95% CI: [{assessment['confidence_bounds'][0]:.4f}, {assessment['confidence_bounds'][1]:.4f}]")
    print(f"Bayes Factor: {assessment['bayes_factor']:.4f}")
    print(f"Evidence Interpretation: {assessment['bayes_factor_interpretation']}")
    
    return assessment, report

if __name__ == "__main__":
    # Run test
    assessment, report = asyncio.run(test_formal_bayesian_engine())
    
    # Save results
    output_dir = "/home/brian/projects/Digimons/uncertainty_stress_test/validation"
    
    with open(f"{output_dir}/formal_bayesian_test_results.json", "w") as f:
        json.dump(assessment, f, indent=2, default=str)
    
    with open(f"{output_dir}/formal_bayesian_report.md", "w") as f:
        f.write(report)
    
    print(f"\nResults saved to {output_dir}/")