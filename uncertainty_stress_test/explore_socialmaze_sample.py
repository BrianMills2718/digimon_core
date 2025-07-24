#!/usr/bin/env python3
"""
Sample exploration of SocialMaze dataset for Bayesian uncertainty testing
"""

import os
import json
from datasets import load_dataset
import pandas as pd
from typing import Dict, List, Any

def explore_socialmaze_sample():
    """Load just a small sample to understand structure"""
    print("🔄 Loading SocialMaze sample...")
    
    try:
        # Load just first few examples to understand structure
        dataset = load_dataset("MBZUAI/SocialMaze", split="train[:10]")
        
        print(f"✅ Sample loaded successfully!")
        print(f"📊 Sample size: {len(dataset)} examples")
        
        # Examine structure
        if len(dataset) > 0:
            first_example = dataset[0]
            print(f"\n📋 Example structure:")
            print(f"Keys: {list(first_example.keys())}")
            
            for key, value in first_example.items():
                if isinstance(value, str):
                    print(f"  {key}: {value[:100]}{'...' if len(value) > 100 else ''}")
                elif isinstance(value, list):
                    print(f"  {key}: [{value[0] if value else 'empty'}{'...' if len(value) > 1 else ''}] (len: {len(value)})")
                else:
                    print(f"  {key}: {value} ({type(value).__name__})")
        
        return dataset
        
    except Exception as e:
        print(f"❌ Error loading sample: {e}")
        print("Trying alternative approach...")
        
        try:
            # Try loading full dataset info first
            dataset_info = load_dataset("MBZUAI/SocialMaze", streaming=True)
            
            # Get first example from stream
            for i, example in enumerate(dataset_info['train']):
                if i == 0:
                    print(f"\n📋 Streaming example structure:")
                    print(f"Keys: {list(example.keys())}")
                    
                    for key, value in example.items():
                        if isinstance(value, str):
                            print(f"  {key}: {value[:100]}{'...' if len(value) > 100 else ''}")
                        elif isinstance(value, list):
                            print(f"  {key}: [{value[0] if value else 'empty'}{'...' if len(value) > 1 else ''}] (len: {len(value)})")
                        else:
                            print(f"  {key}: {value} ({type(value).__name__})")
                    
                    return [example]  # Return single example as list
                    
                if i >= 2:  # Just get first 3 examples
                    break
                    
        except Exception as e2:
            print(f"❌ Streaming also failed: {e2}")
            return None

def identify_uncertainty_opportunities(sample_data):
    """Identify opportunities for Bayesian uncertainty analysis"""
    print("\n🎯 Identifying Bayesian uncertainty opportunities...")
    
    if not sample_data:
        print("❌ No data to analyze")
        return []
    
    opportunities = []
    
    # If it's a single example, wrap in list
    if isinstance(sample_data, dict):
        sample_data = [sample_data]
    
    for i, example in enumerate(sample_data):
        print(f"\n📊 Example {i+1} analysis:")
        
        for key, value in example.items():
            # Look for uncertainty-related fields
            key_lower = key.lower()
            
            if any(term in key_lower for term in ['prob', 'confidence', 'uncertainty', 'belief', 'likelihood']):
                opportunities.append({
                    'type': 'explicit_probability',
                    'field': key,
                    'sample_value': value,
                    'bayesian_application': 'Direct probability assessment and calibration analysis'
                })
                print(f"  🎲 EXPLICIT PROBABILITY: {key}")
                
            elif any(term in key_lower for term in ['intent', 'mental', 'theory', 'mind', 'goal', 'belief']):
                opportunities.append({
                    'type': 'theory_of_mind',
                    'field': key,
                    'sample_value': value,
                    'bayesian_application': 'Hierarchical Bayesian theory of mind modeling'
                })
                print(f"  🧠 THEORY OF MIND: {key}")
                
            elif any(term in key_lower for term in ['choice', 'action', 'decision', 'option', 'predict']):
                opportunities.append({
                    'type': 'decision_prediction',
                    'field': key,
                    'sample_value': value,
                    'bayesian_application': 'Bayesian decision theory and action prediction'
                })
                print(f"  ⚖️ DECISION PREDICTION: {key}")
                
            elif any(term in key_lower for term in ['social', 'interaction', 'relationship', 'context']):
                opportunities.append({
                    'type': 'social_context',
                    'field': key,
                    'sample_value': value,
                    'bayesian_application': 'Social context uncertainty and interaction dynamics'
                })
                print(f"  👥 SOCIAL CONTEXT: {key}")
                
            elif any(term in key_lower for term in ['scenario', 'situation', 'story', 'narrative']):
                opportunities.append({
                    'type': 'narrative_understanding',
                    'field': key,
                    'sample_value': value,
                    'bayesian_application': 'Narrative coherence and understanding uncertainty'
                })
                print(f"  📖 NARRATIVE: {key}")
    
    print(f"\n🔍 Found {len(opportunities)} uncertainty analysis opportunities")
    return opportunities

def create_socialmaze_uncertainty_test():
    """Create a specific test for SocialMaze with uncertainty framework"""
    print("\n🧪 Creating SocialMaze uncertainty test...")
    
    test_code = '''#!/usr/bin/env python3
"""
SocialMaze Bayesian Uncertainty Analysis Test
Tests the uncertainty framework on social reasoning tasks
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_services.uncertainty_engine import UncertaintyEngine, ConfidenceScore
from core_services.bayesian_aggregation_service import BayesianAggregationService, Evidence
from validation.bias_analyzer import BiasAnalyzer

class SocialMazeUncertaintyTest:
    """Test uncertainty analysis on social reasoning scenarios"""
    
    def __init__(self):
        # Initialize with OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key required for testing")
            
        self.uncertainty_engine = UncertaintyEngine(api_key)
        self.bayesian_service = BayesianAggregationService(api_key)
        self.bias_analyzer = BiasAnalyzer()
        
    async def test_social_intent_inference(self):
        """Test Bayesian inference of social intentions"""
        print("\\n🧠 Testing Social Intent Inference...")
        
        # Example social scenario (synthetic, based on SocialMaze structure)
        social_scenario = {
            "context": "Alice and Bob are colleagues working on a project. Alice has been consistently late to meetings and hasn't submitted her parts on time.",
            "action": "Alice sends Bob a message saying 'Sorry, I've been really busy with personal stuff. Can we push the deadline back a week?'",
            "question": "What is Alice's likely intention?",
            "options": [
                "A) Alice is genuinely overwhelmed and needs help",
                "B) Alice is avoiding responsibility and making excuses", 
                "C) Alice is testing Bob's patience and flexibility",
                "D) Alice is planning to quit and doesn't want to say it directly"
            ]
        }
        
        # Extract claim for uncertainty analysis
        claim = "Alice is genuinely overwhelmed and needs help with the project deadline"
        full_text = f"{social_scenario['context']} {social_scenario['action']}"
        
        # Assess initial confidence
        confidence_score = await self.uncertainty_engine.assess_initial_confidence(
            text=full_text,
            claim=claim,
            domain="social_cognition"
        )
        
        print(f"   Initial confidence in intent: {confidence_score.get_overall_confidence():.3f}")
        print(f"   Methodological quality: {confidence_score.methodological_quality:.3f}")
        print(f"   Relevance: {confidence_score.relevance:.3f}")
        print(f"   Coherence: {confidence_score.coherence:.3f}")
        
        return {
            "test_name": "social_intent_inference",
            "confidence": confidence_score.get_overall_confidence(),
            "dimensions": {
                "methodological_quality": confidence_score.methodological_quality,
                "relevance": confidence_score.relevance,
                "coherence": confidence_score.coherence,
                "adequacy": confidence_score.adequacy
            },
            "scenario": social_scenario,
            "claim": claim
        }
    
    async def test_bayesian_social_updates(self):
        """Test Bayesian updating with social evidence"""
        print("\\n📊 Testing Bayesian Social Evidence Updates...")
        
        # Base claim about social relationship
        claim = "Alice and Bob have a collaborative and trusting working relationship"
        prior = 0.6  # Neutral prior
        
        # Multiple pieces of social evidence
        evidence_pieces = [
            Evidence(
                content="Alice consistently asks Bob for advice on technical issues and implements his suggestions",
                source="workplace_observation",
                source_type="behavioral",
                reliability=0.85,
                timestamp=datetime.now()
            ),
            Evidence(
                content="Bob defended Alice's approach in the team meeting when others criticized it",
                source="meeting_transcript", 
                source_type="verbal",
                reliability=0.90,
                timestamp=datetime.now()
            ),
            Evidence(
                content="Alice and Bob often work late together and are seen having friendly conversations",
                source="colleague_report",
                source_type="observational",
                reliability=0.75,
                timestamp=datetime.now()
            )
        ]
        
        # Update belief with evidence
        updated_belief = await self.bayesian_service.update_belief(
            prior_belief=prior,
            claim=claim,
            evidence_list=evidence_pieces,
            domain="social_relationships"
        )
        
        print(f"   Prior belief: {prior:.3f}")
        print(f"   Updated belief: {updated_belief:.3f}")
        print(f"   Evidence pieces: {len(evidence_pieces)}")
        print(f"   Belief change: {updated_belief - prior:+.3f}")
        
        return {
            "test_name": "bayesian_social_updates",
            "prior": prior,
            "updated_belief": updated_belief,
            "belief_change": updated_belief - prior,
            "evidence_count": len(evidence_pieces),
            "claim": claim
        }
    
    async def test_social_bias_detection(self):
        """Test bias detection in social reasoning"""
        print("\\n🔍 Testing Social Bias Detection...")
        
        # Create scenarios with potential biases
        scenarios = [
            {
                "context": "Sarah (CEO, expensive suit, confident demeanor) and Mike (janitor, casual clothes, quiet)",
                "situation": "Both suggest the same cost-cutting idea in a meeting",
                "question": "Whose idea is more likely to be implemented?",
                "bias_type": "authority_bias"
            },
            {
                "context": "Team of 8 people, 7 agree on approach A, 1 person suggests approach B",
                "situation": "Approach B is actually more innovative and efficient", 
                "question": "What will the team likely decide?",
                "bias_type": "conformity_bias"
            },
            {
                "context": "Alex has been working here for 10 years and usually makes good decisions",
                "situation": "Alex makes a clearly poor decision on this project",
                "question": "How will others perceive this decision?",
                "bias_type": "halo_effect"
            }
        ]
        
        bias_results = []
        
        for scenario in scenarios:
            # Test for bias in reasoning
            full_scenario = f"{scenario['context']} {scenario['situation']} Question: {scenario['question']}"
            
            # Analyze for potential biases
            bias_analysis = await self.bias_analyzer.analyze_reasoning_biases(
                text=full_scenario,
                domain="social_reasoning"
            )
            
            bias_results.append({
                "scenario": scenario,
                "detected_biases": bias_analysis.get("detected_biases", []),
                "bias_severity": bias_analysis.get("overall_bias_score", 0.0),
                "expected_bias": scenario["bias_type"]
            })
            
            print(f"   Scenario: {scenario['bias_type']}")
            print(f"   Bias severity: {bias_analysis.get('overall_bias_score', 0.0):.3f}")
            print(f"   Detected: {bias_analysis.get('detected_biases', [])}")
        
        return {
            "test_name": "social_bias_detection",
            "scenarios_tested": len(scenarios),
            "bias_results": bias_results
        }
    
    async def test_calibration_on_social_predictions(self):
        """Test confidence calibration on social prediction tasks"""
        print("\\n🎯 Testing Social Prediction Calibration...")
        
        # Social prediction scenarios with known outcomes (for calibration testing)
        prediction_scenarios = [
            {
                "scenario": "Team member consistently misses deadlines, team has important project due",
                "prediction": "Team member will miss the next deadline",
                "confidence_estimate": 0.85,
                "actual_outcome": True,  # They did miss it
                "outcome_probability": 0.90  # Ground truth probability
            },
            {
                "scenario": "Two departments have been collaborating well, budget cuts announced",
                "prediction": "Departments will maintain collaborative relationship", 
                "confidence_estimate": 0.40,
                "actual_outcome": False,  # They became competitive
                "outcome_probability": 0.30  # Ground truth probability
            },
            {
                "scenario": "Employee gets promotion, has young children, long commute",
                "prediction": "Employee will accept the promotion",
                "confidence_estimate": 0.65,
                "actual_outcome": True,  # They accepted
                "outcome_probability": 0.70  # Ground truth probability
            }
        ]
        
        calibration_results = []
        
        for scenario in prediction_scenarios:
            # Get model's confidence assessment
            model_confidence = await self.uncertainty_engine.assess_initial_confidence(
                text=scenario["scenario"],
                claim=scenario["prediction"],
                domain="social_prediction"
            )
            
            # Calculate calibration metrics
            predicted_prob = model_confidence.get_overall_confidence()
            actual_prob = scenario["outcome_probability"]
            
            # Brier score (lower is better)
            brier_score = (predicted_prob - actual_prob) ** 2
            
            # Calibration error
            calibration_error = abs(predicted_prob - actual_prob)
            
            calibration_results.append({
                "scenario": scenario["scenario"],
                "predicted_probability": predicted_prob,
                "actual_probability": actual_prob,
                "brier_score": brier_score,
                "calibration_error": calibration_error
            })
            
            print(f"   Prediction: {scenario['prediction'][:50]}...")
            print(f"   Model confidence: {predicted_prob:.3f}")
            print(f"   Actual probability: {actual_prob:.3f}")
            print(f"   Brier score: {brier_score:.3f}")
            print(f"   Calibration error: {calibration_error:.3f}")
        
        # Overall calibration metrics
        mean_brier = sum(r["brier_score"] for r in calibration_results) / len(calibration_results)
        mean_calibration_error = sum(r["calibration_error"] for r in calibration_results) / len(calibration_results)
        
        print(f"\\n📊 Overall Calibration Results:")
        print(f"   Mean Brier Score: {mean_brier:.3f}")
        print(f"   Mean Calibration Error: {mean_calibration_error:.3f}")
        
        return {
            "test_name": "social_prediction_calibration",
            "scenarios": calibration_results,
            "mean_brier_score": mean_brier,
            "mean_calibration_error": mean_calibration_error,
            "calibration_quality": "good" if mean_calibration_error < 0.1 else "needs_improvement"
        }
    
    async def run_all_tests(self):
        """Run complete SocialMaze uncertainty test suite"""
        print("🚀 Starting SocialMaze Uncertainty Analysis Tests")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Run all tests
            intent_results = await self.test_social_intent_inference()
            bayesian_results = await self.test_bayesian_social_updates()
            bias_results = await self.test_social_bias_detection()
            calibration_results = await self.test_calibration_on_social_predictions()
            
            # Compile final results
            final_results = {
                "test_suite": "SocialMaze_Uncertainty_Analysis",
                "timestamp": start_time.isoformat(),
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
                "tests": {
                    "social_intent_inference": intent_results,
                    "bayesian_social_updates": bayesian_results,
                    "social_bias_detection": bias_results,
                    "social_prediction_calibration": calibration_results
                },
                "summary": {
                    "total_tests": 4,
                    "avg_confidence": (intent_results["confidence"] + bayesian_results["updated_belief"]) / 2,
                    "calibration_quality": calibration_results["calibration_quality"],
                    "bias_detection_tested": len(bias_results["bias_results"])
                }
            }
            
            # Save results
            os.makedirs("validation/socialmaze_results", exist_ok=True)
            timestamp = start_time.strftime("%Y%m%d_%H%M%S")
            results_file = f"validation/socialmaze_results/socialmaze_uncertainty_test_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump(final_results, f, indent=2)
            
            print(f"\\n✅ All tests completed successfully!")
            print(f"📁 Results saved to: {results_file}")
            print(f"⏱️  Total duration: {final_results['duration_seconds']:.1f} seconds")
            print(f"🎯 Calibration quality: {final_results['summary']['calibration_quality']}")
            
            return final_results
            
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            import traceback
            traceback.print_exc()
            return None

async def main():
    """Main test execution"""
    tester = SocialMazeUncertaintyTest()
    results = await tester.run_all_tests()
    
    if results:
        print("\\n🎉 SocialMaze uncertainty testing completed!")
        print("🔬 This demonstrates how intelligence community analytical techniques")
        print("   can be applied to social cognition and theory of mind tasks.")
    else:
        print("❌ Testing failed - check configuration and API keys")

if __name__ == "__main__":
    asyncio.run(main())
'''

    # Save the test file
    test_file = "test_socialmaze_uncertainty.py"
    with open(test_file, 'w') as f:
        f.write(test_code)
    
    print(f"✅ SocialMaze uncertainty test created: {test_file}")
    return test_file

if __name__ == "__main__":
    print("🚀 SocialMaze Sample Analysis for Bayesian Uncertainty Testing")
    print("=" * 60)
    
    # Load sample data
    sample_data = explore_socialmaze_sample()
    
    if sample_data:
        # Identify opportunities
        opportunities = identify_uncertainty_opportunities(sample_data)
        
        # Create test
        test_file = create_socialmaze_uncertainty_test()
        
        print(f"\n🎉 SocialMaze analysis complete!")
        print(f"🔍 Found {len(opportunities)} uncertainty analysis opportunities")
        print(f"🧪 Created test file: {test_file}")
        print("\nNext steps:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Run: python test_socialmaze_uncertainty.py")
        print("3. Analyze results for social cognition uncertainty patterns")
    
    else:
        print("❌ Could not load SocialMaze data - using synthetic examples in test")
        test_file = create_socialmaze_uncertainty_test()
        print(f"🧪 Created synthetic test file: {test_file}")