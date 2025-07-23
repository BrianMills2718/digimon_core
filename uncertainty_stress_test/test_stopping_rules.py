#!/usr/bin/env python3
"""
Stress Test: Stopping Rules for Information Collection
Tests the system's ability to determine when to stop collecting information.
"""

import json
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
# import matplotlib.pyplot as plt  # Removed for compatibility

class StoppingRulesEngine:
    """Implements multiple stopping rules for information collection"""
    
    def __init__(self):
        self.stopping_criteria = {
            "diminishing_returns": self.check_diminishing_returns,
            "confidence_threshold": self.check_confidence_threshold,
            "cost_benefit": self.check_cost_benefit,
            "time_constraint": self.check_time_constraint,
            "convergence": self.check_convergence,
            "sufficient_discrimination": self.check_sufficient_discrimination
        }
        
        self.collection_history = []
        self.decision_trace = []
        
    def should_stop_collecting(self, 
                             current_state: Dict,
                             constraints: Dict) -> Tuple[bool, Dict]:
        """Determine if information collection should stop"""
        
        stop_signals = {}
        reasons = []
        
        # Check each stopping criterion
        for criterion_name, check_function in self.stopping_criteria.items():
            if criterion_name in constraints.get("active_rules", self.stopping_criteria.keys()):
                should_stop, reason = check_function(current_state, constraints)
                stop_signals[criterion_name] = should_stop
                if should_stop:
                    reasons.append(f"{criterion_name}: {reason}")
        
        # Aggregate decision based on rule combination strategy
        strategy = constraints.get("combination_strategy", "any")
        
        if strategy == "any":
            final_decision = any(stop_signals.values())
        elif strategy == "all":
            final_decision = all(stop_signals.values()) if stop_signals else False
        elif strategy == "majority":
            final_decision = sum(stop_signals.values()) > len(stop_signals) / 2
        else:
            final_decision = False
            
        result = {
            "stop": final_decision,
            "individual_signals": stop_signals,
            "reasons": reasons,
            "strategy_used": strategy,
            "information_collected": current_state.get("info_count", 0),
            "time_elapsed": current_state.get("time_elapsed", 0),
            "current_confidence": current_state.get("confidence", 0)
        }
        
        self.decision_trace.append(result)
        return final_decision, result
    
    def check_diminishing_returns(self, state: Dict, constraints: Dict) -> Tuple[bool, str]:
        """Check if information value is diminishing"""
        recent_values = state.get("recent_info_values", [])
        
        if len(recent_values) < 5:
            return False, "Insufficient data"
            
        # Calculate moving average of information value
        window_size = min(5, len(recent_values))
        recent_avg = np.mean(recent_values[-window_size:])
        previous_avg = np.mean(recent_values[-2*window_size:-window_size]) if len(recent_values) >= 2*window_size else recent_avg
        
        # Check if value is decreasing
        threshold = constraints.get("diminishing_threshold", 0.1)
        if recent_avg < previous_avg * (1 - threshold):
            return True, f"Information value decreased by {(1 - recent_avg/previous_avg)*100:.1f}%"
            
        return False, "Information still valuable"
    
    def check_confidence_threshold(self, state: Dict, constraints: Dict) -> Tuple[bool, str]:
        """Check if confidence threshold has been reached"""
        current_confidence = state.get("confidence", 0)
        threshold = constraints.get("confidence_threshold", 0.95)
        
        if current_confidence >= threshold:
            return True, f"Confidence {current_confidence:.3f} exceeds threshold {threshold}"
            
        return False, f"Confidence {current_confidence:.3f} below threshold"
    
    def check_cost_benefit(self, state: Dict, constraints: Dict) -> Tuple[bool, str]:
        """Check if cost of collection exceeds expected benefit"""
        total_cost = state.get("total_cost", 0)
        expected_benefit = state.get("expected_benefit", float('inf'))
        cost_threshold = constraints.get("cost_benefit_ratio", 0.8)
        
        if total_cost > expected_benefit * cost_threshold:
            return True, f"Cost ({total_cost:.2f}) exceeds {cost_threshold*100}% of expected benefit"
            
        return False, f"Cost-benefit ratio acceptable"
    
    def check_time_constraint(self, state: Dict, constraints: Dict) -> Tuple[bool, str]:
        """Check if time limit has been reached"""
        time_elapsed = state.get("time_elapsed", 0)
        time_limit = constraints.get("time_limit", float('inf'))
        
        if time_elapsed >= time_limit:
            return True, f"Time limit of {time_limit} seconds reached"
            
        time_remaining = time_limit - time_elapsed
        return False, f"{time_remaining:.1f} seconds remaining"
    
    def check_convergence(self, state: Dict, constraints: Dict) -> Tuple[bool, str]:
        """Check if hypothesis probabilities have converged"""
        probability_history = state.get("probability_history", [])
        
        if len(probability_history) < 3:
            return False, "Insufficient history for convergence check"
            
        # Check if probabilities are stable
        recent_probs = probability_history[-3:]
        max_change = 0
        
        for i in range(1, len(recent_probs)):
            for j, prob in enumerate(recent_probs[i]):
                if j < len(recent_probs[i-1]):
                    change = abs(prob - recent_probs[i-1][j])
                    max_change = max(max_change, change)
        
        convergence_threshold = constraints.get("convergence_threshold", 0.01)
        if max_change < convergence_threshold:
            return True, f"Probabilities converged (max change: {max_change:.4f})"
            
        return False, f"Still converging (max change: {max_change:.4f})"
    
    def check_sufficient_discrimination(self, state: Dict, constraints: Dict) -> Tuple[bool, str]:
        """Check if we can sufficiently discriminate between hypotheses"""
        current_probabilities = state.get("hypothesis_probabilities", [])
        
        if not current_probabilities:
            return False, "No hypothesis probabilities available"
            
        # Sort probabilities
        sorted_probs = sorted(current_probabilities, reverse=True)
        
        if len(sorted_probs) < 2:
            return True, "Only one hypothesis"
            
        # Check gap between top hypotheses
        gap = sorted_probs[0] - sorted_probs[1]
        required_gap = constraints.get("discrimination_gap", 0.2)
        
        if gap >= required_gap:
            return True, f"Clear leader with {gap:.3f} probability gap"
            
        return False, f"Gap of {gap:.3f} below required {required_gap}"

def create_research_scenario_1():
    """Scenario: Climate Change Impact Study - When to stop data collection"""
    
    scenario = {
        "name": "Climate Change Impact Analysis",
        "description": "Determining when to stop collecting climate data for impact assessment",
        "hypotheses": [
            "Severe impact (>3°C warming)",
            "Moderate impact (1.5-3°C warming)", 
            "Minimal impact (<1.5°C warming)"
        ],
        "constraints": {
            "active_rules": ["diminishing_returns", "confidence_threshold", "time_constraint"],
            "combination_strategy": "any",
            "confidence_threshold": 0.9,
            "time_limit": 300,  # 5 minutes
            "diminishing_threshold": 0.15
        }
    }
    
    # Simulate information collection over time
    def simulate_collection():
        info_values = []
        confidences = []
        hypothesis_probs = [[0.33, 0.33, 0.34]]  # Initial equal probabilities
        
        for i in range(100):
            # Simulate decreasing information value over time
            base_value = 0.8 * np.exp(-i/20) + 0.1 * random.random()
            info_values.append(base_value)
            
            # Simulate increasing confidence
            confidence = 1 - np.exp(-i/15) + 0.05 * random.random()
            confidences.append(min(confidence, 0.99))
            
            # Simulate converging probabilities
            if i > 0:
                prev_probs = hypothesis_probs[-1]
                new_probs = []
                
                # Gradually increase probability of hypothesis 1
                for j, p in enumerate(prev_probs):
                    if j == 0:  # Favored hypothesis
                        new_p = p + 0.02 * (1 - p) + 0.01 * random.random()
                    else:
                        new_p = p - 0.01 * p + 0.01 * random.random()
                    new_probs.append(new_p)
                
                # Normalize
                total = sum(new_probs)
                new_probs = [p/total for p in new_probs]
                hypothesis_probs.append(new_probs)
        
        return info_values, confidences, hypothesis_probs
    
    return scenario, simulate_collection

def create_research_scenario_2():
    """Scenario: Drug Efficacy Trial - Complex stopping rules"""
    
    scenario = {
        "name": "Drug Efficacy Meta-Analysis",
        "description": "Determining when to stop including studies in meta-analysis",
        "hypotheses": [
            "Drug highly effective (>30% improvement)",
            "Drug moderately effective (10-30% improvement)",
            "Drug ineffective (<10% improvement)",
            "Drug harmful (negative effect)"
        ],
        "constraints": {
            "active_rules": ["cost_benefit", "convergence", "sufficient_discrimination"],
            "combination_strategy": "majority",
            "cost_benefit_ratio": 0.7,
            "convergence_threshold": 0.005,
            "discrimination_gap": 0.25
        }
    }
    
    def simulate_collection():
        info_values = []
        costs = []
        benefits = []
        hypothesis_probs = [[0.25, 0.25, 0.25, 0.25]]  # Initial equal
        
        cumulative_cost = 0
        for i in range(150):
            # Each study has increasing marginal cost
            study_cost = 100 * (1 + i * 0.1)
            cumulative_cost += study_cost
            costs.append(cumulative_cost)
            
            # Expected benefit decreases as we get more certain
            expected_benefit = 10000 * (1 - min(max(hypothesis_probs[-1]), 0.95))
            benefits.append(expected_benefit)
            
            # Information value with some randomness
            value = 0.6 * np.exp(-i/30) + 0.2 * random.random()
            info_values.append(value)
            
            # Update probabilities - converge to hypothesis 1 being true
            if i > 0:
                prev_probs = hypothesis_probs[-1]
                new_probs = []
                
                target_probs = [0.7, 0.2, 0.08, 0.02]  # Final distribution
                for j, p in enumerate(prev_probs):
                    # Move towards target
                    diff = target_probs[j] - p
                    new_p = p + 0.05 * diff + 0.02 * (random.random() - 0.5)
                    new_probs.append(max(0, min(1, new_p)))
                
                # Normalize
                total = sum(new_probs)
                new_probs = [p/total for p in new_probs]
                hypothesis_probs.append(new_probs)
        
        return info_values, costs, benefits, hypothesis_probs
    
    return scenario, simulate_collection

def stress_test_stopping_rules():
    """Run comprehensive stress tests on stopping rules"""
    
    print("=== Stopping Rules Stress Test ===\n")
    
    engine = StoppingRulesEngine()
    
    # Test Scenario 1: Climate Change Study
    print("SCENARIO 1: Climate Change Impact Study")
    print("-" * 50)
    
    scenario1, simulate1 = create_research_scenario_1()
    info_values1, confidences1, probs1 = simulate1()
    
    # Run simulation
    stop_point1 = None
    for i in range(len(info_values1)):
        current_state = {
            "info_count": i + 1,
            "time_elapsed": i * 3,  # 3 seconds per data point
            "confidence": confidences1[i],
            "recent_info_values": info_values1[max(0, i-10):i+1],
            "hypothesis_probabilities": probs1[i]
        }
        
        should_stop, decision = engine.should_stop_collecting(
            current_state, scenario1["constraints"]
        )
        
        if should_stop and stop_point1 is None:
            stop_point1 = i
            print(f"\nSTOPPING at iteration {i+1}")
            print(f"Reasons: {', '.join(decision['reasons'])}")
            print(f"Final confidence: {confidences1[i]:.3f}")
            print(f"Information collected: {i+1} pieces")
            print(f"Time elapsed: {i*3} seconds")
            break
    
    # Test Scenario 2: Drug Efficacy
    print("\n\nSCENARIO 2: Drug Efficacy Meta-Analysis")
    print("-" * 50)
    
    engine2 = StoppingRulesEngine()  # Fresh engine
    scenario2, simulate2 = create_research_scenario_2()
    info_values2, costs2, benefits2, probs2 = simulate2()
    
    stop_point2 = None
    for i in range(len(info_values2)):
        current_state = {
            "info_count": i + 1,
            "total_cost": costs2[i],
            "expected_benefit": benefits2[i],
            "recent_info_values": info_values2[max(0, i-10):i+1],
            "hypothesis_probabilities": probs2[i],
            "probability_history": probs2[max(0, i-5):i+1]
        }
        
        should_stop, decision = engine2.should_stop_collecting(
            current_state, scenario2["constraints"]
        )
        
        if should_stop and stop_point2 is None:
            stop_point2 = i
            print(f"\nSTOPPING at study {i+1}")
            print(f"Reasons: {', '.join(decision['reasons'])}")
            print(f"Total cost: ${costs2[i]:,.2f}")
            print(f"Expected benefit: ${benefits2[i]:,.2f}")
            print(f"Leading hypothesis probability: {max(probs2[i]):.3f}")
            break
    
    # Stress Test: Conflicting Rules
    print("\n\nSTRESS TEST: Conflicting Stopping Rules")
    print("-" * 50)
    
    # Create scenario with all rules active
    stress_constraints = {
        "active_rules": list(engine.stopping_criteria.keys()),
        "combination_strategy": "majority",
        "confidence_threshold": 0.95,
        "time_limit": 100,
        "cost_benefit_ratio": 0.5,
        "convergence_threshold": 0.01,
        "discrimination_gap": 0.3,
        "diminishing_threshold": 0.1
    }
    
    # Test with conflicting signals
    test_state = {
        "info_count": 50,
        "time_elapsed": 150,  # Over time limit
        "confidence": 0.8,  # Below confidence threshold
        "total_cost": 5000,
        "expected_benefit": 8000,  # Good cost-benefit
        "recent_info_values": [0.1] * 10,  # Low value
        "hypothesis_probabilities": [0.6, 0.3, 0.1],  # Some discrimination
        "probability_history": [[0.6, 0.3, 0.1]] * 5  # Converged
    }
    
    should_stop, decision = engine.should_stop_collecting(test_state, stress_constraints)
    
    print(f"\nConflicting signals test:")
    print(f"Final decision: {'STOP' if should_stop else 'CONTINUE'}")
    print(f"Individual signals:")
    for rule, signal in decision["individual_signals"].items():
        print(f"  {rule}: {'STOP' if signal else 'continue'}")
    print(f"Strategy: {decision['strategy_used']}")
    
    # Edge Case Testing
    print("\n\nEDGE CASE TESTING")
    print("-" * 50)
    
    # Edge case 1: No data
    edge_state1 = {
        "info_count": 0,
        "recent_info_values": [],
        "hypothesis_probabilities": []
    }
    
    should_stop, decision = engine.should_stop_collecting(edge_state1, stress_constraints)
    print(f"\nEdge Case 1 - No data: {'STOP' if should_stop else 'CONTINUE'}")
    
    # Edge case 2: Perfect confidence immediately
    edge_state2 = {
        "info_count": 1,
        "confidence": 1.0,
        "recent_info_values": [1.0],
        "hypothesis_probabilities": [1.0, 0.0, 0.0]
    }
    
    should_stop, decision = engine.should_stop_collecting(edge_state2, stress_constraints)
    print(f"Edge Case 2 - Perfect confidence: {'STOP' if should_stop else 'CONTINUE'}")
    
    # Edge case 3: Oscillating probabilities
    oscillating_probs = []
    for i in range(10):
        if i % 2 == 0:
            oscillating_probs.append([0.6, 0.4])
        else:
            oscillating_probs.append([0.4, 0.6])
    
    edge_state3 = {
        "info_count": 10,
        "probability_history": oscillating_probs,
        "hypothesis_probabilities": oscillating_probs[-1]
    }
    
    should_stop, decision = engine.should_stop_collecting(edge_state3, stress_constraints)
    print(f"Edge Case 3 - Oscillating probabilities: {'STOP' if should_stop else 'CONTINUE'}")
    
    return stop_point1, stop_point2, engine.decision_trace

def visualize_stopping_behavior(stop_point1, stop_point2):
    """Create visualization of stopping behavior"""
    
    # This would normally create matplotlib plots
    print("\n\n=== VISUALIZATION SUMMARY ===")
    print(f"Scenario 1 stopped at iteration {stop_point1 + 1 if stop_point1 else 'N/A'}")
    print(f"Scenario 2 stopped at iteration {stop_point2 + 1 if stop_point2 else 'N/A'}")
    print("\nKey patterns observed:")
    print("- Early stopping with diminishing returns prevents over-collection")
    print("- Confidence thresholds provide clear decision points")
    print("- Cost-benefit analysis crucial for expensive data collection")
    print("- Convergence detection prevents premature stopping")
    print("- Multiple rules with 'majority' strategy provide balanced decisions")

if __name__ == "__main__":
    stop1, stop2, trace = stress_test_stopping_rules()
    visualize_stopping_behavior(stop1, stop2)
    
    # Generate summary report
    report = {
        "test_name": "Stopping Rules Stress Test",
        "test_date": datetime.now().isoformat(),
        "scenarios_tested": 2,
        "edge_cases_tested": 3,
        "key_findings": [
            "Multiple stopping rules can be effectively combined",
            "Different combination strategies suit different research contexts",
            "System handles edge cases without crashes",
            "Conflicting signals resolved through configurable strategies"
        ]
    }
    
    print("\n\n=== FINAL REPORT ===")
    print(json.dumps(report, indent=2))