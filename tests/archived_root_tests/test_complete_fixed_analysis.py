#!/usr/bin/env python3
"""
Test complete end-to-end analysis with fixed execution
"""

import json
import time
from datetime import datetime
from src.theory_to_code.structured_extractor import StructuredParameterExtractor
from src.theory_to_code.simple_executor import SimpleExecutor

def test_complete_analysis():
    """Test the complete analysis pipeline with working functions"""
    
    print("COMPLETE ANALYSIS TEST")
    print("=" * 60)
    
    # Test text
    test_text = """
    The company faces two strategic options:
    
    Option A: Aggressive market entry with 70% probability of major gains 
    but 30% chance of substantial losses from regulatory pushback.
    
    Option B: Conservative partnership approach that's virtually certain 
    (95%) to deliver moderate returns with only 5% risk of minor setbacks.
    """
    
    # Load theory schema
    with open("config/schemas/prospect_theory_schema.json", "r") as f:
        theory_schema = json.load(f)
    
    # Step 1: Extract parameters
    print("\n1. Extracting parameters from text...")
    start_time = time.time()
    
    extractor = StructuredParameterExtractor()
    text_schema = extractor.extract_text_schema(test_text, theory_schema)
    resolved_params = extractor.resolve_parameters(text_schema)
    
    extraction_time = time.time() - start_time
    print(f"   ✓ Extracted {len(resolved_params)} prospects in {extraction_time:.2f}s")
    print(f"   ✓ Confidence: {text_schema.confidence:.0%}")
    
    for params in resolved_params:
        print(f"     - {params.prospect_name}: {params.outcomes} @ {params.probabilities}")
    
    # Step 2: Working module code (corrected from LLM output)
    working_module = '''
from typing import List
import numpy as np

def value_function(outcome_values: List[float], reference_point: float, alpha: float = 0.88, beta: float = 0.88, lambda_: float = 2.25) -> List[float]:
    """Calculate subjective values using Prospect Theory"""
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

def prospect_evaluation(outcome_values: List[float], probabilities: List[float], reference_point: float) -> float:
    """Calculate overall prospect value"""
    # Check lengths
    if len(outcome_values) != len(probabilities):
        raise ValueError("Lists must be same length")
    
    # Calculate subjective values
    subjective_values = value_function(outcome_values, reference_point)
    
    # Calculate decision weights  
    decision_weights = probability_weighting_function(probabilities)
    
    # Calculate weighted value
    prospect_value = sum(w * v for w, v in zip(decision_weights, subjective_values))
    
    return prospect_value
'''
    
    # Step 3: Execute analysis for each prospect
    print("\n2. Executing computational analysis...")
    executor = SimpleExecutor()
    
    results = {}
    for params in resolved_params:
        print(f"\n   Analyzing {params.prospect_name}:")
        
        # Calculate prospect value
        result = executor.execute_module_function(
            working_module,
            'prospect_evaluation',
            {
                'outcome_values': params.outcomes,
                'probabilities': params.probabilities,
                'reference_point': params.reference_point
            }
        )
        
        if result.success:
            prospect_value = result.result
            results[params.prospect_name] = {
                'prospect_value': prospect_value,
                'outcomes': params.outcomes,
                'probabilities': params.probabilities,
                'success': True
            }
            print(f"     ✓ Prospect Value: {prospect_value:.2f}")
        else:
            results[params.prospect_name] = {
                'error': result.error,
                'success': False
            }
            print(f"     ✗ Error: {result.error}")
    
    # Step 4: Generate insights
    print("\n3. Analysis Results:")
    print("-" * 40)
    
    successful_results = {name: data for name, data in results.items() if data['success']}
    
    if len(successful_results) >= 2:
        # Compare prospects
        sorted_prospects = sorted(successful_results.items(), 
                                key=lambda x: x[1]['prospect_value'], 
                                reverse=True)
        
        print(f"   Ranking (by prospect value):")
        for i, (name, data) in enumerate(sorted_prospects, 1):
            print(f"     {i}. {name}: {data['prospect_value']:.2f}")
        
        best_option = sorted_prospects[0]
        print(f"\n   🎯 Recommended: {best_option[0]}")
        print(f"   💡 Prospect Theory accounts for loss aversion and probability distortion")
        
        # Show detailed comparison
        print(f"\n   Detailed Analysis:")
        for name, data in successful_results.items():
            outcomes = data['outcomes']
            probs = data['probabilities']
            value = data['prospect_value']
            print(f"     {name}:")
            print(f"       Outcomes: {outcomes}")
            print(f"       Probabilities: {probs}")
            print(f"       Prospect Value: {value:.2f}")
    
    # Step 5: Summary
    total_time = time.time() - start_time
    print(f"\n4. Summary:")
    print(f"   ✓ Complete analysis in {total_time:.2f}s")
    print(f"   ✓ Parameter extraction: {extraction_time:.2f}s")
    print(f"   ✓ Computational analysis: {total_time - extraction_time:.2f}s")
    print(f"   ✓ Text-schema confidence: {text_schema.confidence:.0%}")
    print(f"   ✓ All computations successful: {all(r['success'] for r in results.values())}")
    
    # Save results
    output_file = f"analysis_outputs/complete_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'input_text': test_text,
        'text_schema_confidence': text_schema.confidence,
        'extraction_time': extraction_time,
        'total_time': total_time,
        'results': results,
        'recommendation': sorted_prospects[0][0] if successful_results else None
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"   ✓ Results saved to: {output_file}")
    
    return all(r['success'] for r in results.values())

if __name__ == "__main__":
    success = test_complete_analysis()
    print(f"\n{'✅ COMPLETE SUCCESS!' if success else '❌ SOME FAILURES'}")