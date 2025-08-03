#!/usr/bin/env python3
"""
Test the executor with fixed code
"""

from src.theory_to_code.simple_executor import SimpleExecutor
import numpy as np

# Test the generated prospect_evaluation function
module_code = '''
from typing import List
import numpy as np

def prospect_evaluation(outcome_values: List[float], probabilities: List[float], reference_point: float) -> float:
    """Calculate prospect value"""
    # Check lengths
    if len(outcome_values) != len(probabilities):
        raise ValueError("Lists must be same length")
    
    # Define functions
    v = lambda x: x if x >= reference_point else 2 * x - x ** 2
    w = lambda p: p ** 0.61 / ((p ** 0.61) + ((1 - p) ** 0.61))
    
    # Calculate value
    V = sum(w(p) * v(x) for x, p in zip(outcome_values, probabilities))
    return V

def value_function(outcome_values: List[float], reference_point: float, alpha: float = 0.88, beta: float = 0.88, lambda_: float = 2.25) -> List[float]:
    """Calculate subjective values"""
    subjective_values = []
    for x in outcome_values:
        x_relative = x - reference_point
        if x_relative >= 0:
            subjective_value = x_relative ** alpha
        else:
            subjective_value = -lambda_ * (-x_relative) ** beta
        subjective_values.append(subjective_value)
    return subjective_values

def probability_weighting_function(objective_probabilities: List[float], gamma: float = 0.61) -> List[float]:
    """Calculate decision weights"""
    decision_weights = []
    for p in objective_probabilities:
        if not (0 <= p <= 1):
            raise ValueError("Each probability should be in the range [0, 1].")
        
        try:
            weight = p**gamma / (p**gamma + (1-p)**gamma)**(1/gamma)
        except ZeroDivisionError:
            weight = 0 if p == 0 else 1
        decision_weights.append(weight)
    
    return decision_weights
'''

def test_all_functions():
    """Test all three functions"""
    
    executor = SimpleExecutor()
    
    print("Testing Fixed Executor")
    print("=" * 50)
    
    # Test 1: Value function
    print("\n1. Testing value_function:")
    result = executor.execute_module_function(
        module_code, 
        'value_function',
        {'outcome_values': [95.0, -74.5], 'reference_point': 0.0}
    )
    print(f"   Success: {result.success}")
    if result.success:
        print(f"   Result: {result.result}")
    else:
        print(f"   Error: {result.error}")
    
    # Test 2: Probability weighting
    print("\n2. Testing probability_weighting_function:")
    result = executor.execute_module_function(
        module_code,
        'probability_weighting_function',
        {'objective_probabilities': [0.6, 0.4]}
    )
    print(f"   Success: {result.success}")
    if result.success:
        print(f"   Result: {result.result}")
    else:
        print(f"   Error: {result.error}")
    
    # Test 3: Prospect evaluation
    print("\n3. Testing prospect_evaluation:")
    result = executor.execute_module_function(
        module_code,
        'prospect_evaluation',
        {
            'outcome_values': [95.0, -74.5],
            'probabilities': [0.6, 0.4],
            'reference_point': 0.0
        }
    )
    print(f"   Success: {result.success}")
    if result.success:
        print(f"   Result: {result.result}")
        print(f"   Execution time: {result.execution_time:.3f}s")
    else:
        print(f"   Error: {result.error}")
    
    print("\n✅ All tests complete!")

if __name__ == "__main__":
    test_all_functions()