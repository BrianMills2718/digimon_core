#!/usr/bin/env python3
"""
Baseline Tests for Formula Parsers

Establishes actual performance metrics before making any claims.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.mcp_tools.enhanced_formula_parser import EnhancedFormulaParser
from src.mcp_tools.hybrid_formula_parser import HybridFormulaParser
import json
import time
from typing import Dict, List, Tuple


# Test categories with formulas
TEST_CATEGORIES = {
    "Basic Power Functions": [
        ("v(x) = x^0.88", "Prospect theory value function"),
        ("w(p) = p^0.61", "Probability weighting"),
        ("f(x) = x^2", "Simple square"),
        ("g(x) = x^(-1)", "Reciprocal"),
        ("h(x) = x^0", "Constant function"),
    ],
    
    "Multi-Variable Functions": [
        ("f(x,y) = x + y", "Simple addition"),
        ("f(x,y) = x^2 + y^2", "Sum of squares"),
        ("f(x,y) = x * y", "Product"),
        ("f(x,y) = x / y", "Division"),
        ("f(x,y) = (x + y) / 2", "Average"),
    ],
    
    "Trigonometric Functions": [
        ("f(x) = sin(x)", "Sine"),
        ("f(x) = cos(x)", "Cosine"),
        ("f(x) = tan(x)", "Tangent"),
        ("f(x) = sin(x) + cos(x)", "Trig combination"),
        ("f(x) = sin(x)^2 + cos(x)^2", "Pythagorean identity"),
    ],
    
    "Transcendental Functions": [
        ("f(x) = log(x)", "Natural logarithm"),
        ("f(x) = exp(x)", "Exponential"),
        ("f(x) = sqrt(x)", "Square root"),
        ("f(x) = abs(x)", "Absolute value"),
        ("f(x) = log(x + 1)", "Shifted logarithm"),
    ],
    
    "Statistical Functions": [
        ("f(x,y) = max(x, y)", "Maximum"),
        ("f(x,y) = min(x, y)", "Minimum"),
        ("f(x,y,z) = max(x, max(y, z))", "Max of three"),
        ("f(x,y,z) = min(x, min(y, z))", "Min of three"),
        ("f(x,y) = max(x^2, y^2)", "Max of squares"),
    ],
    
    "Nested Functions": [
        ("f(x) = exp(sin(x))", "Exponential of sine"),
        ("f(x) = log(cos(x) + 2)", "Log of shifted cosine"),
        ("f(x) = sin(exp(x))", "Sine of exponential"),
        ("f(x) = sqrt(log(x))", "Square root of log"),
        ("f(x) = abs(sin(x))", "Absolute sine"),
    ],
    
    "Complex Expressions": [
        ("f(x) = (x^2 + 1) / (x + 1)", "Rational function"),
        ("f(x) = sqrt(x^2 + 1)", "Hyperbolic"),
        ("f(x,y) = sqrt(x^2 + y^2)", "2D distance"),
        ("f(x,y,z) = sqrt(x^2 + y^2 + z^2)", "3D distance"),
        ("f(x) = x * exp(-x^2)", "Gaussian-like"),
    ],
}


def test_parser(parser, name: str) -> Dict:
    """Test a parser and return comprehensive results"""
    print(f"\n{'='*80}")
    print(f"Testing {name}")
    print('='*80)
    
    results = {
        'parser': name,
        'categories': {},
        'overall_success': 0,
        'overall_total': 0,
        'execution_success': 0,
        'parse_times': [],
    }
    
    for category, formulas in TEST_CATEGORIES.items():
        print(f"\n{category}:")
        category_results = {
            'success': 0,
            'total': len(formulas),
            'formulas': []
        }
        
        for formula, description in formulas:
            start_time = time.time()
            result = parser.parse_formula(formula)
            parse_time = time.time() - start_time
            
            results['parse_times'].append(parse_time)
            
            formula_result = {
                'formula': formula,
                'description': description,
                'success': result.success,
                'parse_time': parse_time,
                'error': result.error if not result.success else None,
                'execution_tested': False,
                'execution_success': False
            }
            
            if result.success:
                category_results['success'] += 1
                results['overall_success'] += 1
                print(f"  ✅ {formula}")
                
                # Try to execute the generated code
                try:
                    namespace = {'Union': Union, 'math': __import__('math')}
                    exec(result.python_code, namespace)
                    
                    # Find the function
                    func_name = None
                    for name in namespace:
                        if callable(namespace[name]) and name not in ['Union', 'math']:
                            func_name = name
                            break
                    
                    if func_name:
                        func = namespace[func_name]
                        # Simple execution test
                        if 'y' in formula:
                            test_result = func(1.0, 2.0)
                        elif 'z' in formula:
                            test_result = func(1.0, 2.0, 3.0)
                        else:
                            test_result = func(1.0)
                        
                        formula_result['execution_tested'] = True
                        formula_result['execution_success'] = True
                        results['execution_success'] += 1
                        
                except Exception as e:
                    formula_result['execution_error'] = str(e)
                    
            else:
                print(f"  ❌ {formula} - {result.error}")
            
            category_results['formulas'].append(formula_result)
            
        results['overall_total'] += category_results['total']
        results['categories'][category] = category_results
        
        print(f"  Category: {category_results['success']}/{category_results['total']} "
              f"({category_results['success']/category_results['total']*100:.1f}%)")
    
    # Calculate overall metrics
    results['overall_success_rate'] = results['overall_success'] / results['overall_total']
    results['execution_success_rate'] = results['execution_success'] / results['overall_success'] if results['overall_success'] > 0 else 0
    results['avg_parse_time'] = sum(results['parse_times']) / len(results['parse_times']) if results['parse_times'] else 0
    
    return results


def compare_parsers():
    """Run baseline tests on both parsers"""
    
    print("🔬 Formula Parser Baseline Tests")
    print("Establishing real performance metrics...")
    
    # Test enhanced parser
    enhanced_parser = EnhancedFormulaParser()
    enhanced_results = test_parser(enhanced_parser, "EnhancedFormulaParser")
    
    # Test hybrid parser
    hybrid_parser = HybridFormulaParser()
    hybrid_results = test_parser(hybrid_parser, "HybridFormulaParser (with SymPy)")
    
    # Generate comparison report
    print("\n" + "="*80)
    print("📊 BASELINE COMPARISON REPORT")
    print("="*80)
    
    print(f"\nOverall Success Rates:")
    print(f"  Enhanced Parser: {enhanced_results['overall_success']}/{enhanced_results['overall_total']} "
          f"({enhanced_results['overall_success_rate']*100:.1f}%)")
    print(f"  Hybrid Parser:   {hybrid_results['overall_success']}/{hybrid_results['overall_total']} "
          f"({hybrid_results['overall_success_rate']*100:.1f}%)")
    
    improvement = hybrid_results['overall_success'] - enhanced_results['overall_success']
    improvement_pct = (hybrid_results['overall_success_rate'] - enhanced_results['overall_success_rate']) * 100
    
    print(f"\n  Improvement: +{improvement} formulas ({improvement_pct:+.1f}%)")
    
    print(f"\nExecution Success Rates (of parsed formulas):")
    print(f"  Enhanced Parser: {enhanced_results['execution_success_rate']*100:.1f}%")
    print(f"  Hybrid Parser:   {hybrid_results['execution_success_rate']*100:.1f}%")
    
    print(f"\nAverage Parse Time:")
    print(f"  Enhanced Parser: {enhanced_results['avg_parse_time']*1000:.1f}ms")
    print(f"  Hybrid Parser:   {hybrid_results['avg_parse_time']*1000:.1f}ms")
    
    # Category breakdown
    print("\n📈 Category Performance Comparison:")
    print(f"{'Category':<25} {'Enhanced':<15} {'Hybrid':<15} {'Improvement':<15}")
    print("-" * 70)
    
    for category in TEST_CATEGORIES:
        enhanced_cat = enhanced_results['categories'][category]
        hybrid_cat = hybrid_results['categories'][category]
        
        enhanced_pct = enhanced_cat['success'] / enhanced_cat['total'] * 100
        hybrid_pct = hybrid_cat['success'] / hybrid_cat['total'] * 100
        improvement = hybrid_pct - enhanced_pct
        
        print(f"{category:<25} {enhanced_pct:>6.1f}% ({enhanced_cat['success']}/{enhanced_cat['total']})  "
              f"{hybrid_pct:>6.1f}% ({hybrid_cat['success']}/{hybrid_cat['total']})  "
              f"{improvement:>+6.1f}%")
    
    # Find specific improvements
    print("\n🎯 Specific Formulas Fixed by Hybrid Parser:")
    for category in TEST_CATEGORIES:
        for i, formula_data in enumerate(enhanced_results['categories'][category]['formulas']):
            enhanced_success = formula_data['success']
            hybrid_success = hybrid_results['categories'][category]['formulas'][i]['success']
            
            if not enhanced_success and hybrid_success:
                print(f"  ✅ {formula_data['formula']} - {formula_data['description']}")
    
    # Save detailed results
    results = {
        'timestamp': time.strftime('%Y%m%d_%H%M%S'),
        'enhanced_results': enhanced_results,
        'hybrid_results': hybrid_results,
        'comparison': {
            'overall_improvement': improvement,
            'overall_improvement_pct': improvement_pct,
            'categories_improved': sum(1 for cat in TEST_CATEGORIES 
                                     if hybrid_results['categories'][cat]['success'] > 
                                        enhanced_results['categories'][cat]['success'])
        }
    }
    
    with open('parser_baseline_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Detailed results saved to: parser_baseline_results.json")
    
    # Final verdict
    print("\n🏁 FINAL VERDICT:")
    if improvement > 0:
        print(f"  ✅ Hybrid parser shows measurable improvement: +{improvement} formulas")
        print(f"  ✅ Success rate increased by {improvement_pct:.1f} percentage points")
    else:
        print(f"  ❌ No improvement detected")
    
    # Honest assessment
    print("\n📝 HONEST ASSESSMENT:")
    if hybrid_results['overall_success_rate'] >= 0.9:
        print("  - Hybrid parser achieves >90% success rate")
    elif hybrid_results['overall_success_rate'] >= 0.8:
        print("  - Hybrid parser achieves good but not excellent results")
    else:
        print("  - Hybrid parser needs more work")
    
    # Check specific claims
    stat_success = hybrid_results['categories'].get('Statistical Functions', {}).get('success', 0)
    stat_total = hybrid_results['categories'].get('Statistical Functions', {}).get('total', 1)
    stat_rate = stat_success / stat_total * 100
    
    print(f"\n  Statistical Functions: {stat_rate:.1f}% "
          f"({'✅ Meets 95% claim' if stat_rate >= 95 else '❌ Does not meet 95% claim'})")


if __name__ == "__main__":
    compare_parsers()