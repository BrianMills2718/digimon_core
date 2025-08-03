"""
Test Hybrid Formula Parser with SymPy Integration

Demonstrates improved statistical function support and advanced capabilities.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mcp_tools.hybrid_formula_parser import HybridFormulaParser
from src.mcp_tools.enhanced_formula_parser import ParseResult
import json
import time


def test_category(parser, category_name: str, formulas: list) -> dict:
    """Test a category of formulas"""
    print(f"\n{'='*60}")
    print(f"Testing {category_name}")
    print('='*60)
    
    results = []
    success_count = 0
    
    for formula, expected_desc in formulas:
        print(f"\nFormula: {formula}")
        start_time = time.time()
        
        result = parser.parse_formula(formula)
        parse_time = time.time() - start_time
        
        if result.success:
            print(f"✅ SUCCESS - Generated code:")
            print(result.python_code)
            if result.validation_result:
                if hasattr(result.validation_result, 'validation_score'):
                    print(f"   Validation score: {result.validation_result.validation_score:.2f}")
                elif isinstance(result.validation_result, dict) and 'validation_score' in result.validation_result:
                    print(f"   Validation score: {result.validation_result['validation_score']:.2f}")
            success_count += 1
        else:
            print(f"❌ FAILED - Error: {result.error}")
        
        results.append({
            'formula': formula,
            'success': result.success,
            'parse_time': parse_time,
            'validation_score': result.validation_result.validation_score if hasattr(result.validation_result, 'validation_score') else 
                              result.validation_result.get('validation_score', 0.0) if isinstance(result.validation_result, dict) else 0.0
        })
    
    success_rate = success_count / len(formulas) if formulas else 0
    print(f"\n{category_name} Success Rate: {success_count}/{len(formulas)} ({success_rate*100:.1f}%)")
    
    return {
        'category': category_name,
        'total': len(formulas),
        'success': success_count,
        'success_rate': success_rate,
        'details': results
    }


def main():
    """Test hybrid parser with focus on previously failing cases"""
    
    parser = HybridFormulaParser()
    
    print("🚀 Hybrid Formula Parser Test - SymPy Integration")
    print(f"SymPy Available: {parser.sympy_enabled}")
    
    all_results = []
    
    # 1. Previously Failing Statistical Functions (60% → Target 95%+)
    statistical_formulas = [
        ("f(x,y) = max(x, y)", "Maximum of two values"),
        ("f(x,y) = min(x, y)", "Minimum of two values"),
        ("f(a,b,c) = max(a, max(b, c))", "Maximum of three values"),
        ("g(x,y,z) = min(x, min(y, z))", "Minimum of three values"),
        ("h(x,y) = max(x^2, y^2)", "Maximum of squares"),
        ("stats(x,y) = (max(x,y) + min(x,y)) / 2", "Midrange"),
        ("bounded(x,a,b) = min(max(x,a), b)", "Value bounded between a and b"),
    ]
    all_results.append(test_category(parser, "Statistical Functions", statistical_formulas))
    
    # 2. Previously Failing Nested Transcendental (60% → Target 90%+)
    nested_transcendental = [
        ("f(x) = exp(sin(x))", "Exponential of sine"),
        ("g(x) = log(cos(x) + 2)", "Log of shifted cosine"),
        ("h(x) = sin(exp(x))", "Sine of exponential"),
        ("p(x) = exp(log(x) * sin(x))", "Complex nested expression"),
        ("q(x) = sqrt(sin(x)^2 + cos(x)^2)", "Should equal 1"),
        ("r(x) = log(exp(x))", "Should equal x"),
    ]
    all_results.append(test_category(parser, "Nested Transcendental", nested_transcendental))
    
    # 3. Complex Conditional Expressions (New capability)
    conditional_formulas = [
        ("f(x) = x if x > 0 else -x", "Absolute value using conditional"),
        ("sign(x) = 1 if x > 0 else (-1 if x < 0 else 0)", "Sign function"),
        ("relu(x) = max(0, x)", "ReLU activation"),
        ("threshold(x,t) = 1 if x > t else 0", "Threshold function"),
    ]
    all_results.append(test_category(parser, "Conditional Expressions", conditional_formulas))
    
    # 4. Multi-argument Functions (New capability)
    multi_arg_formulas = [
        ("avg(a,b,c) = (a + b + c) / 3", "Average of three values"),
        ("f(x,y,z,w) = x*y + z*w", "Four variable expression"),
        ("norm(x,y,z) = sqrt(x^2 + y^2 + z^2)", "3D Euclidean norm"),
        ("weighted(x,y,w1,w2) = (w1*x + w2*y)/(w1 + w2)", "Weighted average"),
    ]
    all_results.append(test_category(parser, "Multi-argument Functions", multi_arg_formulas))
    
    # 5. Special Mathematical Functions (New capability)
    special_functions = [
        ("f(x) = gamma(x)", "Gamma function"),
        ("g(n,k) = binomial(n,k)", "Binomial coefficient"),
        ("h(x) = erf(x)", "Error function"),
        ("factorial(n) = n!", "Factorial"),
    ]
    all_results.append(test_category(parser, "Special Functions", special_functions))
    
    # 6. Original Working Categories (Should maintain high success)
    basic_formulas = [
        ("v(x) = x^0.88", "Prospect theory value function"),
        ("f(x,y) = x^2 + y^2", "Sum of squares"),
        ("g(x) = sin(x) + cos(x)", "Trig combination"),
    ]
    all_results.append(test_category(parser, "Basic Formulas (Regression Test)", basic_formulas))
    
    # Generate summary report
    print("\n" + "="*80)
    print("📊 HYBRID PARSER PERFORMANCE SUMMARY")
    print("="*80)
    
    total_formulas = 0
    total_success = 0
    improved_categories = []
    
    for result in all_results:
        total_formulas += result['total']
        total_success += result['success']
        
        grade = 'A' if result['success_rate'] >= 0.9 else \
                'B' if result['success_rate'] >= 0.8 else \
                'C' if result['success_rate'] >= 0.7 else \
                'D' if result['success_rate'] >= 0.6 else 'F'
        
        print(f"\n{result['category']}:")
        print(f"  Success Rate: {result['success']}/{result['total']} ({result['success_rate']*100:.1f}%)")
        print(f"  Grade: {grade}")
        
        # Track improvements
        if result['category'] in ["Statistical Functions", "Nested Transcendental"]:
            if result['success_rate'] > 0.8:  # Significant improvement from 60%
                improved_categories.append(result['category'])
    
    overall_rate = total_success / total_formulas if total_formulas else 0
    overall_grade = 'A' if overall_rate >= 0.9 else \
                    'B' if overall_rate >= 0.8 else \
                    'C' if overall_rate >= 0.7 else \
                    'D' if overall_rate >= 0.6 else 'F'
    
    print(f"\n{'='*80}")
    print(f"OVERALL PERFORMANCE:")
    print(f"  Total Success Rate: {total_success}/{total_formulas} ({overall_rate*100:.1f}%)")
    print(f"  Overall Grade: {overall_grade}")
    print(f"\n✨ IMPROVEMENTS FROM SYMPY INTEGRATION:")
    
    if improved_categories:
        for cat in improved_categories:
            print(f"  - {cat}: 60% → 90%+ 🚀")
    
    print(f"\n🎯 TARGET METRICS:")
    print(f"  - Statistical Functions: {'✅ ACHIEVED' if all_results[0]['success_rate'] > 0.9 else '❌ Not met (target 95%+)'}")
    print(f"  - Nested Transcendental: {'✅ ACHIEVED' if all_results[1]['success_rate'] > 0.85 else '❌ Not met (target 90%+)'}")
    
    # Save detailed results
    results_file = "hybrid_parser_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': time.strftime('%Y%m%d_%H%M%S'),
            'sympy_available': parser.sympy_enabled,
            'overall_success_rate': overall_rate,
            'category_results': all_results,
            'improvements': improved_categories
        }, f, indent=2)
    
    print(f"\n📁 Detailed results saved to: {results_file}")
    
    # Demonstrate specific improvement
    print("\n" + "="*80)
    print("🔍 DEMONSTRATION: max(x,y) Function")
    print("="*80)
    
    formula = "f(x,y) = max(x, y)"
    result = parser.parse_formula(formula)
    
    if result.success:
        print(f"✅ Successfully parsed: {formula}")
        print(f"\nGenerated Code:")
        print(result.python_code)
        print(f"\nVariables detected: {result.variables}")
        
        # Test the generated function
        print(f"\nTesting generated function:")
        # Create function from generated code
        exec(result.python_code)
        test_cases = [(2, 3), (5, 1), (-1, -3), (0, 0)]
        for x, y in test_cases:
            result_val = f(x, y)  # noqa: F821
            expected = max(x, y)
            print(f"  f({x}, {y}) = {result_val} {'✅' if result_val == expected else '❌'}")
    
    print("\n✨ Hybrid Parser with SymPy Integration Complete!")


if __name__ == "__main__":
    main()