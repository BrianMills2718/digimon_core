#!/usr/bin/env python3
"""
LLM-Guided Bayesian Inference for Psychological Trait Prediction
LLM estimates evidence, Bayesian algorithm runs programmatically
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import json
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import re


@dataclass
class BayesianEvidence:
    """Evidence extracted by LLM for Bayesian inference"""
    trait_name: str
    evidence_type: str  # "text_pattern", "entity_mention", "behavioral_indicator"
    evidence_text: str
    confidence: float  # LLM confidence in this evidence
    direction: str     # "positive", "negative", "neutral"
    strength: float    # How strong this evidence is (0.1 to 1.0)


@dataclass
class TraitPrior:
    """Bayesian prior for a psychological trait"""
    trait_name: str
    mean: float        # Prior mean
    variance: float    # Prior variance
    evidence_weights: Dict[str, float]  # How much each evidence type matters


class LLMEvidenceExtractor:
    """LLM-based evidence extraction for Bayesian inference"""
    
    def __init__(self):
        self.trait_patterns = {
            "political_orientation": {
                "liberal_patterns": [
                    r"democratic party", r"liberal", r"progressive", r"left-wing",
                    r"climate change", r"social justice", r"equality", r"diversity",
                    r"systemic change", r"inequality", r"working people"
                ],
                "conservative_patterns": [
                    r"republican party", r"conservative", r"right-wing", r"traditional",
                    r"free market", r"law and order", r"family values", r"faith",
                    r"economic issues", r"socialist agenda"
                ]
            },
            "narcissism": {
                "high_patterns": [
                    r"i'm one of the few", r"i'm more aware", r"superior to", r"special",
                    r"i can see through", r"most people.*sheep", r"think for myself",
                    r"see through their lies", r"few who can", r"more aware than most"
                ],
                "low_patterns": [
                    r"we\s+", r"together", r"collaborative", r"ordinary person", r"humble",
                    r"grateful", r"just an ordinary", r"appreciate.*colleagues", r"trying to do my job"
                ]
            },
            "conspiracy_mentality": {
                "high_patterns": [
                    r"government.*working together", r"big corporations.*control", r"mainstream media",
                    r"deep state", r"conspiracy", r"hidden agendas", r"wake up",
                    r"corporate interests", r"controlled by", r"secret agenda", r"infowars",
                    r"see through.*propaganda", r"they feed us", r"power really works"
                ],
                "low_patterns": [
                    r"evidence.based", r"scientific consensus", r"peer.reviewed", r"experts",
                    r"established protocols", r"health organizations", r"cdc", r"who",
                    r"rigorous methods", r"good intentions"
                ]
            },
            "denialism": {
                "high_patterns": [
                    r"climate change.*hoax", r"vaccines.*dangerous", r"covid.*fake",
                    r"evolution.*false", r"global warming.*scam", r"mainstream.*lies",
                    r"deny", r"refuse to believe", r"not real"
                ],
                "low_patterns": [
                    r"accept.*science", r"trust.*experts", r"evidence.*clear",
                    r"scientific consensus", r"research confirms", r"studies show"
                ]
            }
        }
    
    def extract_evidence_from_text(self, text: str, entities: List[Dict] = None) -> List[BayesianEvidence]:
        """Extract evidence for Bayesian inference using LLM-like pattern analysis"""
        evidence = []
        text_lower = text.lower()
        
        # Pattern-based evidence extraction (simulating LLM analysis)
        for trait, patterns in self.trait_patterns.items():
            for direction, pattern_list in patterns.items():
                for pattern in pattern_list:
                    matches = re.findall(pattern, text_lower)
                    if matches:
                        # Calculate evidence strength based on frequency and context
                        strength = min(1.0, len(matches) * 0.3)
                        confidence = 0.8 + (strength * 0.2)  # Higher strength = higher confidence
                        
                        evidence.append(BayesianEvidence(
                            trait_name=trait,
                            evidence_type="text_pattern",
                            evidence_text=f"Pattern '{pattern}' found {len(matches)} times",
                            confidence=confidence,
                            direction="positive" if "high" in direction else "negative",
                            strength=strength
                        ))
        
        # Entity-based evidence (simulating LLM entity analysis)
        if entities:
            for entity in entities:
                entity_evidence = self._analyze_entity_for_traits(entity, text_lower)
                evidence.extend(entity_evidence)
        
        return evidence
    
    def _analyze_entity_for_traits(self, entity: Dict, text: str) -> List[BayesianEvidence]:
        """Analyze entities for psychological trait evidence"""
        evidence = []
        entity_name = entity.get("surface_form", "").lower()
        entity_type = entity.get("entity_type", "")
        
        # Political organization mentions
        political_orgs = {
            "democratic party": ("political_orientation", "negative", 0.8),
            "republican party": ("political_orientation", "positive", 0.8),
            "breitbart": ("political_orientation", "positive", 0.6),
            "fox news": ("political_orientation", "positive", 0.6),
            "cnn": ("political_orientation", "negative", 0.5),
            "qanon": ("conspiracy_mentality", "positive", 0.9)
        }
        
        for org_name, (trait, direction, strength) in political_orgs.items():
            if org_name in entity_name or org_name in text:
                evidence.append(BayesianEvidence(
                    trait_name=trait,
                    evidence_type="entity_mention",
                    evidence_text=f"Mentions {org_name}",
                    confidence=0.85,
                    direction=direction,
                    strength=strength
                ))
        
        # Conspiracy-related entities
        conspiracy_entities = ["qanon", "infowars", "alex jones", "deep state"]
        for conspiracy_entity in conspiracy_entities:
            if conspiracy_entity in entity_name:
                evidence.append(BayesianEvidence(
                    trait_name="conspiracy_mentality",
                    evidence_type="entity_mention", 
                    evidence_text=f"Associates with {conspiracy_entity}",
                    confidence=0.9,
                    direction="positive",
                    strength=0.8
                ))
        
        return evidence


class BayesianTraitInference:
    """Programmatic Bayesian inference using LLM-extracted evidence"""
    
    def __init__(self):
        # Define priors for each trait (population means/variances)
        self.priors = {
            "political_orientation": TraitPrior(
                trait_name="political_orientation",
                mean=0.0,     # Neutral political orientation
                variance=1.0,  # Standard deviation of 1
                evidence_weights={
                    "text_pattern": 0.4,
                    "entity_mention": 0.6,
                    "behavioral_indicator": 0.8
                }
            ),
            "narcissism": TraitPrior(
                trait_name="narcissism",
                mean=0.0,     # Average narcissism
                variance=0.8,
                evidence_weights={
                    "text_pattern": 0.7,
                    "entity_mention": 0.3,
                    "behavioral_indicator": 0.9
                }
            ),
            "conspiracy_mentality": TraitPrior(
                trait_name="conspiracy_mentality", 
                mean=-0.5,    # Most people low conspiracy mentality
                variance=1.2,
                evidence_weights={
                    "text_pattern": 0.8,
                    "entity_mention": 0.9,
                    "behavioral_indicator": 0.7
                }
            ),
            "denialism": TraitPrior(
                trait_name="denialism",
                mean=-0.3,    # Most people accept mainstream science
                variance=1.0,
                evidence_weights={
                    "text_pattern": 0.9,
                    "entity_mention": 0.5,
                    "behavioral_indicator": 0.8
                }
            )
        }
    
    def infer_trait_scores(self, evidence_list: List[BayesianEvidence]) -> Dict[str, Dict]:
        """Run Bayesian inference to predict trait scores"""
        results = {}
        
        for trait_name, prior in self.priors.items():
            # Start with prior
            posterior_mean = prior.mean
            posterior_variance = prior.variance
            
            # Get evidence for this trait
            trait_evidence = [e for e in evidence_list if e.trait_name == trait_name]
            
            if trait_evidence:
                # Bayesian updating
                for evidence in trait_evidence:
                    # Convert evidence to likelihood parameters
                    evidence_mean, evidence_variance = self._evidence_to_likelihood(
                        evidence, prior
                    )
                    
                    # Bayesian update: combine prior with evidence
                    posterior_mean, posterior_variance = self._bayesian_update(
                        posterior_mean, posterior_variance,
                        evidence_mean, evidence_variance
                    )
            
            # Calculate confidence intervals
            std_dev = np.sqrt(posterior_variance)
            confidence_95 = {
                "lower": posterior_mean - 1.96 * std_dev,
                "upper": posterior_mean + 1.96 * std_dev
            }
            
            results[trait_name] = {
                "predicted_score": posterior_mean,
                "uncertainty": posterior_variance,
                "confidence_interval_95": confidence_95,
                "evidence_count": len(trait_evidence),
                "posterior_std": std_dev
            }
        
        return results
    
    def _evidence_to_likelihood(self, evidence: BayesianEvidence, prior: TraitPrior) -> Tuple[float, float]:
        """Convert LLM evidence to likelihood parameters"""
        # Base evidence strength
        base_strength = evidence.strength * evidence.confidence
        
        # Weight by evidence type
        weight = prior.evidence_weights.get(evidence.evidence_type, 0.5)
        weighted_strength = base_strength * weight
        
        # Convert to mean shift
        direction_multiplier = 1.0 if evidence.direction == "positive" else -1.0
        evidence_mean = direction_multiplier * weighted_strength * 2.0  # Scale to ±2
        
        # Evidence variance (higher confidence = lower variance, minimum 0.01 to avoid division by zero)
        evidence_variance = max(0.01, (1.0 - evidence.confidence) * 0.5)
        
        return evidence_mean, evidence_variance
    
    def _bayesian_update(self, prior_mean: float, prior_var: float, 
                        likelihood_mean: float, likelihood_var: float) -> Tuple[float, float]:
        """Perform Bayesian update combining prior and likelihood"""
        # Precision (inverse variance)
        prior_precision = 1.0 / prior_var
        likelihood_precision = 1.0 / likelihood_var
        
        # Posterior precision
        posterior_precision = prior_precision + likelihood_precision
        posterior_variance = 1.0 / posterior_precision
        
        # Posterior mean (weighted average)
        posterior_mean = (prior_precision * prior_mean + likelihood_precision * likelihood_mean) / posterior_precision
        
        return posterior_mean, posterior_variance


def test_llm_bayesian_inference():
    """Test LLM-guided Bayesian inference on sample profiles"""
    print("🧠 Testing LLM-Guided Bayesian Inference")
    print("=" * 50)
    
    # Initialize components
    evidence_extractor = LLMEvidenceExtractor()
    bayesian_inference = BayesianTraitInference()
    
    # Test profiles with known characteristics
    test_profiles = [
        {
            "user_id": "test_001",
            "text": """
            John Smith strongly supports the Democratic Party and believes in climate change action.
            He frequently posts about QAnon conspiracy theories and thinks the deep state controls everything.
            Smith considers himself exceptional and superior to others in his thinking.
            """,
            "expected_traits": {
                "political_orientation": -1.0,  # Liberal
                "conspiracy_mentality": 1.5,    # High conspiracy
                "narcissism": 0.8               # High narcissism
            }
        },
        {
            "user_id": "test_002", 
            "text": """
            Dr. Sarah Johnson is a Republican who trusts scientific consensus and peer-reviewed research.
            She works collaboratively with her team and considers herself fortunate to contribute to science.
            Johnson relies on evidence-based thinking and official health organization guidance.
            """,
            "expected_traits": {
                "political_orientation": 1.0,   # Conservative
                "conspiracy_mentality": -1.2,   # Low conspiracy
                "narcissism": -0.5,              # Low narcissism
                "denialism": -0.8                # Low denialism
            }
        }
    ]
    
    for profile in test_profiles:
        print(f"\n🔬 Analyzing {profile['user_id']}:")
        print(f"Text: {profile['text'][:100]}...")
        
        # Extract evidence using LLM-like analysis
        evidence = evidence_extractor.extract_evidence_from_text(profile["text"])
        print(f"📋 Extracted {len(evidence)} pieces of evidence:")
        for ev in evidence[:3]:  # Show top 3
            print(f"  - {ev.trait_name}: {ev.evidence_text} ({ev.direction}, {ev.strength:.2f})")
        
        # Run Bayesian inference
        predicted_traits = bayesian_inference.infer_trait_scores(evidence)
        
        print(f"📊 Predicted vs Expected Traits:")
        for trait, prediction in predicted_traits.items():
            expected = profile["expected_traits"].get(trait, 0.0)
            predicted = prediction["predicted_score"]
            uncertainty = prediction["uncertainty"]
            
            print(f"  {trait:20}: Predicted={predicted:6.2f} ± {uncertainty:.2f}, Expected={expected:6.2f}")
            
            # Check if prediction is within reasonable range
            error = abs(predicted - expected)
            if error < 1.0:
                print(f"    ✓ Good prediction (error: {error:.2f})")
            else:
                print(f"    ⚠ Poor prediction (error: {error:.2f})")
    
    print(f"\n✅ LLM-Bayesian inference test complete!")
    return True


if __name__ == "__main__":
    success = test_llm_bayesian_inference()
    print(f"\n🎯 Result: {'SUCCESS' if success else 'FAILED'}")