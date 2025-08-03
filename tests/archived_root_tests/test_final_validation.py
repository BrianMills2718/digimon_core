#!/usr/bin/env python3
"""
Final Validation Test - Honest Assessment of SymPy Integration

This test provides real, measurable results without exaggeration.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.mcp_tools.enhanced_formula_parser import EnhancedFormulaParser
from src.mcp_tools.hybrid_formula_parser import HybridFormulaParser
import json
import time
from typing import Union  # Fix the Union import issue


def execute_generated_code(code: str, test_inputs: list) -> dict:
    """Execute generated code with test inputs"""
    results = {
        'executable': False,
        'test_results': [],
        'error': None
    }
    
    try:
        # Create execution namespace
        namespace = {
            'Union': Union,
            'math': __import__('math'),
            'min': min,
            'max': max,
            'abs': abs
        }
        
        # Execute the code
        exec(code, namespace)
        
        # Find the generated function
        func_name = None
        for name in namespace:
            if callable(namespace[name]) and name not in ['Union', 'math', 'min', 'max', 'abs']:
                func_name = name
                break
        
        if func_name:
            func = namespace[func_name]
            results['executable'] = True
            
            # Test with provided inputs
            for test_input in test_inputs:
                try:
                    if isinstance(test_input, tuple):
                        result = func(*test_input)
                    else:
                        result = func(test_input)
                    
                    results['test_results'].append({
                        'input': test_input,
                        'output': result,
                        'success': True
                    })
                except Exception as e:
                    results['test_results'].append({
                        'input': test_input,
                        'error': str(e),
                        'success': False
                    })
        else:
            results['error'] = "No function found in generated code"
            
    except Exception as e:
        results['error'] = f"Code execution failed: {str(e)}"
    
    return results


def main():
    """Run final validation with honest metrics"""
    
    print("🔬 FINAL VALIDATION: SymPy Integration Assessment")
    print("="*80)
    print("Testing with real formulas and measuring actual improvements\n")
    
    # Initialize parsers
    enhanced_parser = EnhancedFormulaParser()
    hybrid_parser = HybridFormulaParser()
    
    # Critical test cases - the ones we claimed to fix
    critical_tests = [
        {
            'category': 'Statistical Functions',
            'formulas': [
                ("f(x,y) = max(x, y)", [(1, 2), (5, 3), (-1, -3)]),
                ("f(x,y) = min(x, y)", [(1, 2), (5, 3), (-1, -3)]),
                ("f(x,y) = max(x^2, y^2)", [(1, 2), (3, 2), (-2, 1)]),
                ("bounded(x,a,b) = min(max(x, a), b)", [(5, 0, 10), (-5, 0, 10), (15, 0, 10)]),
            ]
        },
        {
            'category': 'Nested Transcendental',
            'formulas': [
                ("f(x) = exp(sin(x))", [0, 1.57, 3.14]),  # 0, π/2, π
                ("g(x) = log(cos(x) + 2)", [0, 1.57, 3.14]),
                ("h(x) = sin(exp(x))", [0, 1, 2]),
            ]
        }
    ]
    
    # Test both parsers
    results = {
        'enhanced': {'total': 0, 'parsed': 0, 'executable': 0, 'categories': {}},
        'hybrid': {'total': 0, 'parsed': 0, 'executable': 0, 'categories': {}}
    }
    
    for test_category in critical_tests:
        category = test_category['category']
        print(f"\n📂 {category}")
        print("-" * 60)
        
        enhanced_cat = {'total': 0, 'parsed': 0, 'executable': 0}
        hybrid_cat = {'total': 0, 'parsed': 0, 'executable': 0}
        
        for formula, test_inputs in test_category['formulas']:
            print(f"\n  Formula: {formula}")
            
            # Test Enhanced Parser
            enhanced_result = enhanced_parser.parse_formula(formula)
            enhanced_cat['total'] += 1
            results['enhanced']['total'] += 1
            
            if enhanced_result.success:
                enhanced_cat['parsed'] += 1
                results['enhanced']['parsed'] += 1
                exec_result = execute_generated_code(enhanced_result.python_code, test_inputs)
                if exec_result['executable']:
                    enhanced_cat['executable'] += 1
                    results['enhanced']['executable'] += 1
                    print(f"    Enhanced: ✅ Parsed & Executable")
                else:
                    print(f"    Enhanced: ⚠️  Parsed but not executable: {exec_result['error']}")
            else:
                print(f"    Enhanced: ❌ Failed to parse")
            
            # Test Hybrid Parser
            hybrid_result = hybrid_parser.parse_formula(formula)
            hybrid_cat['total'] += 1
            results['hybrid']['total'] += 1
            
            if hybrid_result.success:
                hybrid_cat['parsed'] += 1
                results['hybrid']['parsed'] += 1
                exec_result = execute_generated_code(hybrid_result.python_code, test_inputs)
                if exec_result['executable']:
                    hybrid_cat['executable'] += 1
                    results['hybrid']['executable'] += 1
                    print(f"    Hybrid:   ✅ Parsed & Executable")
                    
                    # Show sample execution
                    if exec_result['test_results']:
                        sample = exec_result['test_results'][0]
                        if sample['success']:
                            print(f"    Sample:   f{sample['input']} = {sample['output']}")
                else:
                    print(f"    Hybrid:   ⚠️  Parsed but not executable: {exec_result['error']}")
            else:
                print(f"    Hybrid:   ❌ Failed to parse")
        
        results['enhanced']['categories'][category] = enhanced_cat
        results['hybrid']['categories'][category] = hybrid_cat
        
        print(f"\n  Category Summary:")
        print(f"    Enhanced: {enhanced_cat['executable']}/{enhanced_cat['total']} executable ({enhanced_cat['executable']/enhanced_cat['total']*100:.1f}%)")
        print(f"    Hybrid:   {hybrid_cat['executable']}/{hybrid_cat['total']} executable ({hybrid_cat['executable']/hybrid_cat['total']*100:.1f}%)")
    
    # Overall Summary
    print("\n" + "="*80)
    print("📊 OVERALL RESULTS")
    print("="*80)
    
    enhanced_exec_rate = results['enhanced']['executable'] / results['enhanced']['total'] * 100
    hybrid_exec_rate = results['hybrid']['executable'] / results['hybrid']['total'] * 100
    improvement = hybrid_exec_rate - enhanced_exec_rate
    
    print(f"\nEnhanced Parser:")
    print(f"  Parsed:     {results['enhanced']['parsed']}/{results['enhanced']['total']} ({results['enhanced']['parsed']/results['enhanced']['total']*100:.1f}%)")
    print(f"  Executable: {results['enhanced']['executable']}/{results['enhanced']['total']} ({enhanced_exec_rate:.1f}%)")
    
    print(f"\nHybrid Parser:")
    print(f"  Parsed:     {results['hybrid']['parsed']}/{results['hybrid']['total']} ({results['hybrid']['parsed']/results['hybrid']['total']*100:.1f}%)")
    print(f"  Executable: {results['hybrid']['executable']}/{results['hybrid']['total']} ({hybrid_exec_rate:.1f}%)")
    
    print(f"\nImprovement: {improvement:+.1f} percentage points")
    
    # Parser Usage Stats
    print("\n📈 PARSER USAGE STATISTICS")
    print("-" * 40)
    usage_stats = hybrid_parser.get_usage_stats()
    print(f"Total formulas processed: {usage_stats['total_parses']}")
    print(f"SymPy attempts: {usage_stats['sympy_attempts']}")
    print(f"SymPy successes: {usage_stats['sympy_success']}")
    print(f"SymPy fallbacks: {usage_stats['sympy_fallback']}")
    print(f"Enhanced-only: {usage_stats['enhanced_only']}")
    
    if usage_stats['total_parses'] > 0:
        print(f"\nSymPy success rate: {usage_stats.get('sympy_success_rate', 0)*100:.1f}%")
        print(f"SymPy usage: {usage_stats.get('sympy_usage_pct', 0):.1f}%")
        print(f"Enhanced usage: {usage_stats.get('enhanced_usage_pct', 0):.1f}%")
    
    # Honest Assessment
    print("\n" + "="*80)
    print("🎯 HONEST ASSESSMENT")
    print("="*80)
    
    # Check specific claims
    stat_results = results['hybrid']['categories'].get('Statistical Functions', {})
    stat_rate = stat_results.get('executable', 0) / stat_results.get('total', 1) * 100 if stat_results.get('total', 0) > 0 else 0
    
    print(f"\nClaim: '95%+ success rate on statistical functions'")
    print(f"Reality: {stat_rate:.1f}% executable statistical functions")
    print(f"Verdict: {'✅ VERIFIED' if stat_rate >= 95 else '❌ NOT ACHIEVED'}")
    
    print(f"\nClaim: 'Buy not build was successful'")
    print(f"Reality: {improvement:+.1f}% improvement in executable code")
    print(f"Verdict: {'✅ WORTHWHILE' if improvement > 10 else '⚠️  MARGINAL' if improvement > 0 else '❌ NO BENEFIT'}")
    
    # Time to implement
    print(f"\nClaim: '2 hours to implement'")
    print(f"Reality: Multiple iterations, bug fixes, and testing required")
    print(f"Verdict: ❌ UNDERESTIMATED")
    
    # Production readiness
    print(f"\nProduction Readiness:")
    if hybrid_exec_rate >= 90:
        print(f"✅ Ready for production use ({hybrid_exec_rate:.1f}% executable)")
    elif hybrid_exec_rate >= 70:
        print(f"⚠️  Needs more work ({hybrid_exec_rate:.1f}% executable)")
    else:
        print(f"❌ Not production ready ({hybrid_exec_rate:.1f}% executable)")
    
    # Save results
    final_results = {
        'timestamp': time.strftime('%Y%m%d_%H%M%S'),
        'enhanced_results': results['enhanced'],
        'hybrid_results': results['hybrid'],
        'improvement_percentage_points': improvement,
        'parser_usage_stats': usage_stats,
        'claims_verification': {
            'statistical_95_percent': stat_rate >= 95,
            'actual_statistical_rate': stat_rate,
            'worthwhile_improvement': improvement > 10,
            'actual_improvement': improvement,
            'production_ready': hybrid_exec_rate >= 90,
            'actual_executable_rate': hybrid_exec_rate
        }
    }
    
    with open('final_validation_results.json', 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"\n📁 Results saved to: final_validation_results.json")


if __name__ == "__main__":
    main()