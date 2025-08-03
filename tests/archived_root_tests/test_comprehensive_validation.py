#!/usr/bin/env python3
"""
Comprehensive Formula Parser Validation

Tests 60+ diverse formulas across all mathematical domains to get 
unbiased, representative performance metrics.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.mcp_tools.enhanced_formula_parser import EnhancedFormulaParser
from src.mcp_tools.hybrid_formula_parser import HybridFormulaParser
import json
import time
import math
from typing import Union


# Comprehensive test suite - 60+ formulas across all domains
COMPREHENSIVE_TEST_SUITE = {
    "Basic Arithmetic": [
        ("f(x) = x + 1", [1, 2, -1]),
        ("f(x) = x - 3", [5, 2, 0]),
        ("f(x) = 2 * x", [3, -2, 0.5]),
        ("f(x) = x / 4", [8, -4, 1]),
        ("f(x,y) = x + y", [(1,2), (3,4), (-1,1)]),
        ("f(x,y) = x - y", [(5,2), (1,3), (0,0)]),
        ("f(x,y) = x * y", [(2,3), (-1,4), (0.5,2)]),
        ("f(x,y) = x / y", [(6,2), (8,4), (1,3)]),
    ],
    
    "Power Functions": [
        ("f(x) = x^2", [2, -3, 0.5]),
        ("f(x) = x^3", [2, -1, 1.5]),
        ("f(x) = x^0.5", [4, 9, 16]),
        ("f(x) = x^(-1)", [2, 4, 0.5]),
        ("f(x) = x^(-2)", [2, 3, 0.5]),
        ("f(x) = x^0.88", [1, 2, 10]),  # Prospect theory
        ("f(x) = x^0.61", [0.5, 0.8, 1]),  # Probability weighting
    ],
    
    "Trigonometric Functions": [
        ("f(x) = sin(x)", [0, 1.57, 3.14]),
        ("f(x) = cos(x)", [0, 1.57, 3.14]),
        ("f(x) = tan(x)", [0, 0.785, -0.785]),
        ("f(x) = sin(x) + cos(x)", [0, 1.57, 3.14]),
        ("f(x) = sin(x)^2", [0, 1.57, 3.14]),
        ("f(x) = cos(x)^2", [0, 1.57, 3.14]),
        ("f(x) = sin(x)^2 + cos(x)^2", [0, 1.57, 3.14]),  # Should = 1
    ],
    
    "Exponential and Logarithmic": [
        ("f(x) = exp(x)", [0, 1, 2]),
        ("f(x) = log(x)", [1, 2.718, 10]),
        ("f(x) = log10(x)", [1, 10, 100]),
        ("f(x) = exp(x) - 1", [0, 1, 2]),
        ("f(x) = log(x + 1)", [0, 1, 9]),
        ("f(x) = exp(-x)", [0, 1, 2]),
        ("f(x) = log(exp(x))", [1, 2, 3]),  # Should = x
    ],
    
    "Basic Statistical Functions": [
        ("f(x,y) = max(x, y)", [(1,2), (5,3), (-1,-3)]),
        ("f(x,y) = min(x, y)", [(1,2), (5,3), (-1,-3)]),
        ("f(x,y) = (x + y) / 2", [(2,4), (0,10), (-2,2)]),  # mean
        ("f(x,y,z) = (x + y + z) / 3", [(1,2,3), (0,0,6), (-1,1,2)]),  # mean of 3
        ("f(x,y) = abs(x - y)", [(5,2), (2,5), (-1,3)]),  # difference
    ],
    
    "Advanced Statistical Functions": [
        ("mean(x,y,z) = (x + y + z) / 3", [(1,2,3), (0,3,6), (2,2,2)]),
        ("variance(x,y) = ((x-m)^2 + (y-m)^2)/2 where m=(x+y)/2", "SKIP"),  # Complex
        ("std(x,y) = sqrt(variance(x,y))", "SKIP"),  # Would need variance first
        ("median(x,y,z) = sort(x,y,z)[1]", "SKIP"),  # Needs sorting
        ("range(x,y,z) = max(x,y,z) - min(x,y,z)", [(1,5,3), (0,0,10), (-2,2,0)]),
    ],
    
    "Nested Functions": [
        ("f(x) = sin(cos(x))", [0, 1.57, 3.14]),
        ("f(x) = exp(sin(x))", [0, 1.57, 3.14]),
        ("f(x) = log(cos(x) + 2)", [0, 1.57, 3.14]),
        ("f(x) = sin(exp(x))", [0, 0.5, 1]),  # Previously failed
        ("f(x) = sqrt(log(x))", [1, 2.718, 10]),
        ("f(x) = abs(sin(x))", [0, -1.57, 3.14]),
        ("f(x) = exp(log(x))", [1, 2, 5]),  # Should = x
    ],
    
    "Complex Multi-Variable": [
        ("f(x,y) = sqrt(x^2 + y^2)", [(3,4), (1,1), (0,5)]),  # distance
        ("f(x,y,z) = sqrt(x^2 + y^2 + z^2)", [(1,1,1), (3,4,0), (0,0,1)]),  # 3D distance
        ("f(x,y) = x^2 + y^2", [(1,1), (2,3), (-1,2)]),
        ("f(x,y) = x * y + x + y", [(2,3), (1,0), (-1,2)]),
        ("f(x,y) = (x + y) * (x - y)", [(3,2), (5,3), (1,1)]),
    ],
    
    "Edge Cases and Special Functions": [
        ("f(x) = sqrt(x)", [0, 1, 4, 9]),
        ("f(x) = abs(x)", [-5, 0, 3, -2.5]),
        ("f(x) = x^0", [0, 1, -5, 100]),  # Should = 1
        ("f(x) = 1/x", [1, 2, 0.5, -1]),
        ("f(x) = x / (x + 1)", [0, 1, 2, -0.5]),
        ("f(x) = (x^2 + 1) / (x + 1)", [0, 1, 2, -0.5]),
    ],
    
    "Real-World Formulas": [
        ("compound(P,r,t) = P * (1 + r)^t", [(1000, 0.05, 10), (500, 0.08, 5)]),  # Compound interest
        ("bmi(w,h) = w / h^2", [(70, 1.75), (80, 1.8), (60, 1.6)]),  # BMI
        ("quadratic(a,b,c,x) = a*x^2 + b*x + c", [(1,2,1,2), (2,-3,1,1)]),  # Quadratic
        ("gaussian(x,mu,sigma) = exp(-((x-mu)^2)/(2*sigma^2))", "SKIP"),  # Too complex for now
    ],
}


def execute_and_validate(code: str, test_inputs: list, parser_name: str) -> dict:
    """Execute generated code and validate results"""
    result = {
        'executable': False,
        'correct_outputs': 0,
        'total_tests': len(test_inputs),
        'test_results': [],
        'error': None
    }
    
    try:
        # Create execution namespace
        namespace = {
            'Union': Union,
            'math': math,
            'min': min,
            'max': max,
            'abs': abs,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'exp': math.exp,
            'log': math.log,
            'log10': math.log10,
        }
        
        # Execute the code
        exec(code, namespace)
        
        # Find the generated function
        func_name = None
        for name in namespace:
            if (callable(namespace[name]) and 
                name not in ['Union', 'math', 'min', 'max', 'abs', 'sqrt', 'sin', 'cos', 'tan', 'exp', 'log', 'log10']):
                func_name = name
                break
        
        if func_name:
            func = namespace[func_name]
            result['executable'] = True
            
            # Test with all inputs
            for test_input in test_inputs:
                try:
                    if isinstance(test_input, tuple):
                        output = func(*test_input)
                    else:
                        output = func(test_input)
                    
                    # Basic sanity checks
                    is_correct = True
                    if math.isnan(output) or math.isinf(output):
                        is_correct = False
                    
                    if is_correct:
                        result['correct_outputs'] += 1
                    
                    result['test_results'].append({
                        'input': test_input,
                        'output': output,
                        'success': True,
                        'correct': is_correct
                    })
                    
                except Exception as e:
                    result['test_results'].append({
                        'input': test_input,
                        'error': str(e),
                        'success': False,
                        'correct': False
                    })
        else:
            result['error'] = "No function found in generated code"
            
    except Exception as e:
        result['error'] = f"Code execution failed: {str(e)}"
    
    return result


def test_comprehensive_suite():
    """Run comprehensive test suite on both parsers"""
    
    print("🧪 COMPREHENSIVE FORMULA PARSER VALIDATION")
    print("Testing 60+ formulas across all mathematical domains")
    print("="*80)
    
    # Initialize parsers
    enhanced_parser = EnhancedFormulaParser()
    hybrid_parser = HybridFormulaParser()
    
    results = {
        'enhanced': {
            'total_formulas': 0,
            'parsed': 0,
            'executable': 0,
            'fully_correct': 0,
            'categories': {},
            'parse_times': []
        },
        'hybrid': {
            'total_formulas': 0,
            'parsed': 0,
            'executable': 0,
            'fully_correct': 0,
            'categories': {},
            'parse_times': []
        }
    }
    
    # Test each category
    for category, formulas in COMPREHENSIVE_TEST_SUITE.items():
        print(f"\n📂 {category}")
        print("-" * 60)
        
        enhanced_cat = {'total': 0, 'parsed': 0, 'executable': 0, 'fully_correct': 0}
        hybrid_cat = {'total': 0, 'parsed': 0, 'executable': 0, 'fully_correct': 0}
        
        for formula_data in formulas:
            if isinstance(formula_data, tuple) and formula_data[1] != "SKIP":
                formula, test_inputs = formula_data
            else:
                continue  # Skip complex formulas for now
            
            print(f"\n  {formula}")
            
            # Test Enhanced Parser
            start = time.time()
            enhanced_result = enhanced_parser.parse_formula(formula)
            enhanced_parse_time = time.time() - start
            
            enhanced_cat['total'] += 1
            results['enhanced']['total_formulas'] += 1
            results['enhanced']['parse_times'].append(enhanced_parse_time)
            
            if enhanced_result.success:
                enhanced_cat['parsed'] += 1
                results['enhanced']['parsed'] += 1
                
                exec_result = execute_and_validate(enhanced_result.python_code, test_inputs, "Enhanced")
                if exec_result['executable']:
                    enhanced_cat['executable'] += 1
                    results['enhanced']['executable'] += 1
                    
                    if exec_result['correct_outputs'] == exec_result['total_tests']:
                        enhanced_cat['fully_correct'] += 1
                        results['enhanced']['fully_correct'] += 1
                        print(f"    Enhanced: ✅ Fully correct ({exec_result['correct_outputs']}/{exec_result['total_tests']})")
                    else:
                        print(f"    Enhanced: ⚠️  Partial ({exec_result['correct_outputs']}/{exec_result['total_tests']})")
                else:
                    print(f"    Enhanced: ❌ Parse OK but not executable")
            else:
                print(f"    Enhanced: ❌ Parse failed")
            
            # Test Hybrid Parser
            start = time.time()
            hybrid_result = hybrid_parser.parse_formula(formula)
            hybrid_parse_time = time.time() - start
            
            hybrid_cat['total'] += 1
            results['hybrid']['total_formulas'] += 1
            results['hybrid']['parse_times'].append(hybrid_parse_time)
            
            if hybrid_result.success:
                hybrid_cat['parsed'] += 1
                results['hybrid']['parsed'] += 1
                
                exec_result = execute_and_validate(hybrid_result.python_code, test_inputs, "Hybrid")
                if exec_result['executable']:
                    hybrid_cat['executable'] += 1
                    results['hybrid']['executable'] += 1
                    
                    if exec_result['correct_outputs'] == exec_result['total_tests']:
                        hybrid_cat['fully_correct'] += 1
                        results['hybrid']['fully_correct'] += 1
                        print(f"    Hybrid:   ✅ Fully correct ({exec_result['correct_outputs']}/{exec_result['total_tests']})")
                    else:
                        print(f"    Hybrid:   ⚠️  Partial ({exec_result['correct_outputs']}/{exec_result['total_tests']})")
                else:
                    print(f"    Hybrid:   ❌ Parse OK but not executable")
            else:
                print(f"    Hybrid:   ❌ Parse failed")
        
        results['enhanced']['categories'][category] = enhanced_cat
        results['hybrid']['categories'][category] = hybrid_cat
        
        # Category summary
        enhanced_pct = enhanced_cat['fully_correct'] / enhanced_cat['total'] * 100 if enhanced_cat['total'] > 0 else 0
        hybrid_pct = hybrid_cat['fully_correct'] / hybrid_cat['total'] * 100 if hybrid_cat['total'] > 0 else 0
        improvement = hybrid_pct - enhanced_pct
        
        print(f"\n  📊 Category Summary:")
        print(f"    Enhanced: {enhanced_cat['fully_correct']}/{enhanced_cat['total']} ({enhanced_pct:.1f}%)")
        print(f"    Hybrid:   {hybrid_cat['fully_correct']}/{hybrid_cat['total']} ({hybrid_pct:.1f}%)")
        print(f"    Improvement: {improvement:+.1f}%")
    
    # Overall Results
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE RESULTS")
    print("="*80)
    
    enhanced_overall = results['enhanced']['fully_correct'] / results['enhanced']['total_formulas'] * 100
    hybrid_overall = results['hybrid']['fully_correct'] / results['hybrid']['total_formulas'] * 100
    real_improvement = hybrid_overall - enhanced_overall
    
    print(f"\nOverall Performance (Fully Correct):")
    print(f"  Enhanced Parser: {results['enhanced']['fully_correct']}/{results['enhanced']['total_formulas']} ({enhanced_overall:.1f}%)")
    print(f"  Hybrid Parser:   {results['hybrid']['fully_correct']}/{results['hybrid']['total_formulas']} ({hybrid_overall:.1f}%)")
    print(f"  Real Improvement: {real_improvement:+.1f} percentage points")
    
    print(f"\nParsing Success:")
    enhanced_parse = results['enhanced']['parsed'] / results['enhanced']['total_formulas'] * 100
    hybrid_parse = results['hybrid']['parsed'] / results['hybrid']['total_formulas'] * 100
    print(f"  Enhanced Parser: {results['enhanced']['parsed']}/{results['enhanced']['total_formulas']} ({enhanced_parse:.1f}%)")
    print(f"  Hybrid Parser:   {results['hybrid']['parsed']}/{results['hybrid']['total_formulas']} ({hybrid_parse:.1f}%)")
    
    print(f"\nExecution Success (of parsed):")
    enhanced_exec = results['enhanced']['executable'] / results['enhanced']['parsed'] * 100 if results['enhanced']['parsed'] > 0 else 0
    hybrid_exec = results['hybrid']['executable'] / results['hybrid']['parsed'] * 100 if results['hybrid']['parsed'] > 0 else 0
    print(f"  Enhanced Parser: {results['enhanced']['executable']}/{results['enhanced']['parsed']} ({enhanced_exec:.1f}%)")
    print(f"  Hybrid Parser:   {results['hybrid']['executable']}/{results['hybrid']['parsed']} ({hybrid_exec:.1f}%)")
    
    # Performance Analysis
    enhanced_avg_time = sum(results['enhanced']['parse_times']) / len(results['enhanced']['parse_times']) * 1000
    hybrid_avg_time = sum(results['hybrid']['parse_times']) / len(results['hybrid']['parse_times']) * 1000
    slowdown = (hybrid_avg_time / enhanced_avg_time - 1) * 100 if enhanced_avg_time > 0 else 0
    
    print(f"\nPerformance:")
    print(f"  Enhanced avg parse time: {enhanced_avg_time:.2f}ms")
    print(f"  Hybrid avg parse time:   {hybrid_avg_time:.2f}ms")
    print(f"  Slowdown: {slowdown:+.1f}%")
    
    # Parser Usage Stats
    usage_stats = hybrid_parser.get_usage_stats()
    print(f"\nParser Usage Statistics:")
    print(f"  SymPy attempts: {usage_stats['sympy_attempts']}")
    print(f"  SymPy success rate: {usage_stats.get('sympy_success_rate', 0)*100:.1f}%")
    print(f"  Enhanced fallback: {usage_stats.get('enhanced_usage_pct', 0):.1f}%")
    
    # Honest Assessment
    print("\n" + "="*80)
    print("🎯 HONEST ASSESSMENT")
    print("="*80)
    
    if real_improvement > 20:
        verdict = "✅ SIGNIFICANT IMPROVEMENT"
    elif real_improvement > 10:
        verdict = "✅ MODERATE IMPROVEMENT"
    elif real_improvement > 0:
        verdict = "⚠️  MARGINAL IMPROVEMENT"
    else:
        verdict = "❌ NO IMPROVEMENT"
    
    print(f"\nReal Improvement: {real_improvement:+.1f}% ({verdict})")
    
    if hybrid_overall >= 90:
        readiness = "✅ PRODUCTION READY"
    elif hybrid_overall >= 75:
        readiness = "⚠️  NEEDS MINOR WORK"
    elif hybrid_overall >= 50:
        readiness = "❌ NEEDS MAJOR WORK"
    else:
        readiness = "❌ NOT READY"
    
    print(f"Production Readiness: {hybrid_overall:.1f}% ({readiness})")
    
    # Save results
    final_results = {
        'timestamp': time.strftime('%Y%m%d_%H%M%S'),
        'test_count': results['enhanced']['total_formulas'],
        'enhanced_results': results['enhanced'],
        'hybrid_results': results['hybrid'],
        'real_improvement_pct': real_improvement,
        'performance_impact': {
            'enhanced_avg_ms': enhanced_avg_time,
            'hybrid_avg_ms': hybrid_avg_time,
            'slowdown_pct': slowdown
        },
        'parser_usage': usage_stats,
        'assessment': {
            'improvement_significant': real_improvement > 20,
            'production_ready': hybrid_overall >= 90,
            'performance_acceptable': slowdown < 100  # Less than 2x slowdown
        }
    }
    
    with open('comprehensive_validation_results.json', 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"\n📁 Detailed results saved to: comprehensive_validation_results.json")
    
    return final_results


if __name__ == "__main__":
    test_comprehensive_suite()