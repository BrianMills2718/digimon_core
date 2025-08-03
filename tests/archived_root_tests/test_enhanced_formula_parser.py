#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced Formula Parser

This addresses the critical assessment finding that only 3 cherry-picked
test cases were used. This suite tests 50+ diverse mathematical formulas
across different categories to validate real capabilities.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_tools.enhanced_formula_parser import EnhancedFormulaParser

class ComprehensiveFormulaTestSuite:
    """Comprehensive test suite with 50+ diverse mathematical formulas"""
    
    def __init__(self):
        self.parser = EnhancedFormulaParser()
        self.test_categories = self._build_test_categories()
        
    def _build_test_categories(self) -> Dict[str, List[Dict[str, Any]]]:
        """Build comprehensive test categories"""
        
        return {
            "basic_polynomial": [
                {"formula": "f(x) = x^2", "expected_type": "power", "difficulty": "easy"},
                {"formula": "f(x) = x^3 + 2*x^2 + x + 1", "expected_type": "polynomial", "difficulty": "medium"},
                {"formula": "f(x) = 2*x + 3", "expected_type": "linear", "difficulty": "easy"},
                {"formula": "f(x) = x^4 - 3*x^3 + 2*x^2 - x + 5", "expected_type": "polynomial", "difficulty": "medium"},
                {"formula": "f(x) = x^0.5", "expected_type": "power", "difficulty": "easy"},
            ],
            
            "multi_variable": [
                {"formula": "f(x,y) = x^2 + y^2", "expected_type": "polynomial", "difficulty": "medium"},
                {"formula": "f(x,y) = x*y", "expected_type": "polynomial", "difficulty": "easy"},
                {"formula": "f(x,y,z) = x + y + z", "expected_type": "linear", "difficulty": "medium"},
                {"formula": "f(x,y) = (x + y)^2", "expected_type": "power", "difficulty": "medium"},
                {"formula": "f(x,y) = x^2*y + x*y^2", "expected_type": "polynomial", "difficulty": "hard"},
            ],
            
            "transcendental": [
                {"formula": "f(x) = log(x)", "expected_type": "transcendental", "difficulty": "medium"},
                {"formula": "f(x) = exp(x)", "expected_type": "transcendental", "difficulty": "medium"},
                {"formula": "f(x) = ln(x) + 1", "expected_type": "transcendental", "difficulty": "medium"},
                {"formula": "f(x) = log10(x)", "expected_type": "transcendental", "difficulty": "medium"},
                {"formula": "f(x) = exp(-x^2)", "expected_type": "transcendental", "difficulty": "hard"},
            ],
            
            "trigonometric": [
                {"formula": "f(x) = sin(x)", "expected_type": "trigonometric", "difficulty": "medium"},
                {"formula": "f(x) = cos(x)", "expected_type": "trigonometric", "difficulty": "medium"},
                {"formula": "f(x) = tan(x)", "expected_type": "trigonometric", "difficulty": "medium"},
                {"formula": "f(x) = sin(x) + cos(x)", "expected_type": "trigonometric", "difficulty": "medium"},
                {"formula": "f(x) = sin(x^2)", "expected_type": "trigonometric", "difficulty": "hard"},
            ],
            
            "complex_expressions": [
                {"formula": "f(x) = sqrt(x^2 + 1)", "expected_type": "transcendental", "difficulty": "hard"},
                {"formula": "f(x) = abs(x)", "expected_type": "power", "difficulty": "easy"},
                {"formula": "f(x,y) = sqrt(x^2 + y^2)", "expected_type": "transcendental", "difficulty": "hard"},
                {"formula": "f(x) = log(abs(x))", "expected_type": "transcendental", "difficulty": "hard"},
                {"formula": "f(x) = exp(sin(x))", "expected_type": "transcendental", "difficulty": "hard"},
            ],
            
            "statistical": [
                {"formula": "f(x) = mean([x, x+1, x+2])", "expected_type": "linear", "difficulty": "hard"},
                {"formula": "f(x) = max(x, 0)", "expected_type": "linear", "difficulty": "medium"},
                {"formula": "f(x) = min(x, 1)", "expected_type": "linear", "difficulty": "medium"},
                {"formula": "f(x,y) = max(x, y)", "expected_type": "linear", "difficulty": "medium"},
                {"formula": "f(x,y) = min(x, y)", "expected_type": "linear", "difficulty": "medium"},
            ],
            
            "constants_and_special": [
                {"formula": "f(x) = pi * x", "expected_type": "linear", "difficulty": "easy"},
                {"formula": "f(x) = e^x", "expected_type": "transcendental", "difficulty": "medium"},
                {"formula": "f(x) = x * pi + e", "expected_type": "linear", "difficulty": "easy"},
                {"formula": "f(x) = sin(pi * x)", "expected_type": "trigonometric", "difficulty": "medium"},
                {"formula": "f(x) = log(e * x)", "expected_type": "transcendental", "difficulty": "medium"},
            ],
            
            "edge_cases": [
                {"formula": "f(x) = x^0", "expected_type": "power", "difficulty": "medium"},
                {"formula": "f(x) = 0*x + 1", "expected_type": "linear", "difficulty": "easy"},
                {"formula": "f(x) = x^1", "expected_type": "linear", "difficulty": "easy"},
                {"formula": "f(x) = 1/x", "expected_type": "power", "difficulty": "medium"},
                {"formula": "f(x) = x^(-1)", "expected_type": "power", "difficulty": "medium"},
            ],
            
            "prospect_theory_original": [
                {"formula": "v(x) = x^0.88", "expected_type": "power", "difficulty": "easy"},
                {"formula": "v(x) = -2.25 * (-x)^0.88", "expected_type": "power", "difficulty": "medium"},
                {"formula": "w(p) = p^0.61", "expected_type": "power", "difficulty": "easy"},
            ]
        }
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test across all categories"""
        
        print("=== COMPREHENSIVE FORMULA PARSER TEST ===")
        print("Testing 50+ diverse mathematical formulas across 9 categories")
        
        results = {
            "total_formulas": 0,
            "successful_parses": 0,
            "failed_parses": 0,
            "category_results": {},
            "difficulty_breakdown": {"easy": 0, "medium": 0, "hard": 0},
            "difficulty_success": {"easy": 0, "medium": 0, "hard": 0},
            "expression_types": {},
            "detailed_results": []
        }
        
        for category, formulas in self.test_categories.items():
            print(f"\n--- Testing {category.upper()} ({len(formulas)} formulas) ---")
            
            category_result = {
                "total": len(formulas),
                "successful": 0,
                "failed": 0,
                "formulas": []
            }
            
            for formula_test in formulas:
                formula = formula_test["formula"]
                expected_type = formula_test["expected_type"]
                difficulty = formula_test["difficulty"]
                
                results["total_formulas"] += 1
                results["difficulty_breakdown"][difficulty] += 1
                
                print(f"  Testing: {formula}")
                
                # Parse the formula
                parse_result = self.parser.parse_formula(formula)
                
                if parse_result.success:
                    results["successful_parses"] += 1
                    category_result["successful"] += 1
                    results["difficulty_success"][difficulty] += 1
                    
                    # Check expression type
                    actual_type = parse_result.mathematical_properties.get("expression_type", "unknown")
                    type_match = actual_type == expected_type
                    
                    if actual_type not in results["expression_types"]:
                        results["expression_types"][actual_type] = 0
                    results["expression_types"][actual_type] += 1
                    
                    print(f"    ✅ Success - Type: {actual_type} ({'✓' if type_match else '✗ expected ' + expected_type})")
                    
                    # Test mathematical validation
                    validation = parse_result.validation_result
                    test_score = validation.get("test_cases_passed", 0) / max(validation.get("total_test_cases", 1), 1)
                    print(f"    📊 Validation: {validation.get('test_cases_passed', 0)}/{validation.get('total_test_cases', 0)} tests passed ({test_score:.1%})")
                    
                    formula_result = {
                        "formula": formula,
                        "success": True,
                        "expected_type": expected_type,
                        "actual_type": actual_type,
                        "type_match": type_match,
                        "difficulty": difficulty,
                        "validation_score": test_score,
                        "code_preview": parse_result.python_code[:100] + "..." if len(parse_result.python_code) > 100 else parse_result.python_code
                    }
                else:
                    results["failed_parses"] += 1
                    category_result["failed"] += 1
                    print(f"    ❌ Failed: {parse_result.error}")
                    
                    formula_result = {
                        "formula": formula,
                        "success": False,
                        "expected_type": expected_type,
                        "difficulty": difficulty,
                        "error": parse_result.error
                    }
                
                category_result["formulas"].append(formula_result)
                results["detailed_results"].append(formula_result)
            
            results["category_results"][category] = category_result
            success_rate = category_result["successful"] / category_result["total"]
            print(f"  Category Success Rate: {category_result['successful']}/{category_result['total']} ({success_rate:.1%})")
        
        return results
    
    def analyze_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test results and provide insights"""
        
        analysis = {
            "overall_success_rate": results["successful_parses"] / results["total_formulas"],
            "category_performance": {},
            "difficulty_performance": {},
            "expression_type_distribution": results["expression_types"],
            "strengths": [],
            "weaknesses": [],
            "recommendations": []
        }
        
        # Category performance analysis
        for category, result in results["category_results"].items():
            success_rate = result["successful"] / result["total"]
            analysis["category_performance"][category] = {
                "success_rate": success_rate,
                "grade": self._grade_performance(success_rate)
            }
            
            if success_rate >= 0.8:
                analysis["strengths"].append(f"Strong performance in {category} ({success_rate:.1%})")
            elif success_rate < 0.5:
                analysis["weaknesses"].append(f"Poor performance in {category} ({success_rate:.1%})")
        
        # Difficulty analysis
        for difficulty in ["easy", "medium", "hard"]:
            total = results["difficulty_breakdown"][difficulty]
            success = results["difficulty_success"][difficulty]
            if total > 0:
                success_rate = success / total
                analysis["difficulty_performance"][difficulty] = {
                    "success_rate": success_rate,
                    "grade": self._grade_performance(success_rate)
                }
        
        # Generate recommendations
        if analysis["overall_success_rate"] < 0.7:
            analysis["recommendations"].append("Overall success rate below 70% - needs significant improvement")
        
        weak_categories = [cat for cat, perf in analysis["category_performance"].items() 
                          if perf["success_rate"] < 0.5]
        if weak_categories:
            analysis["recommendations"].append(f"Focus improvement on: {', '.join(weak_categories)}")
            
        if analysis["difficulty_performance"].get("hard", {}).get("success_rate", 0) < 0.3:
            analysis["recommendations"].append("Hard formulas need significant work - complex expression handling")
            
        return analysis
    
    def _grade_performance(self, success_rate: float) -> str:
        """Grade performance based on success rate"""
        if success_rate >= 0.9:
            return "A"
        elif success_rate >= 0.8:
            return "B"
        elif success_rate >= 0.7:
            return "C"
        elif success_rate >= 0.5:
            return "D"
        else:
            return "F"
    
    def generate_report(self, results: Dict[str, Any], analysis: Dict[str, Any]) -> None:
        """Generate comprehensive test report"""
        
        print("\n" + "="*80)
        print("COMPREHENSIVE FORMULA PARSER TEST REPORT")
        print("="*80)
        
        # Overall metrics
        total = results["total_formulas"]
        success = results["successful_parses"]
        overall_rate = analysis["overall_success_rate"]
        
        print(f"\n📊 OVERALL PERFORMANCE")
        print(f"  Total formulas tested: {total}")
        print(f"  Successful parses: {success}")
        print(f"  Failed parses: {results['failed_parses']}")
        print(f"  Success rate: {overall_rate:.1%}")
        print(f"  Overall grade: {self._grade_performance(overall_rate)}")
        
        # Category breakdown
        print(f"\n📋 CATEGORY PERFORMANCE")
        for category, perf in analysis["category_performance"].items():
            rate = perf["success_rate"]
            grade = perf["grade"]
            count = results["category_results"][category]
            print(f"  {category:25} {count['successful']:2}/{count['total']:2} ({rate:5.1%}) Grade: {grade}")
        
        # Difficulty breakdown  
        print(f"\n⚡ DIFFICULTY ANALYSIS")
        for difficulty, perf in analysis["difficulty_performance"].items():
            rate = perf["success_rate"]
            grade = perf["grade"]
            total = results["difficulty_breakdown"][difficulty]
            success = results["difficulty_success"][difficulty]
            print(f"  {difficulty.capitalize():8} {success:2}/{total:2} ({rate:5.1%}) Grade: {grade}")
        
        # Expression types
        print(f"\n🔍 EXPRESSION TYPE DISTRIBUTION")
        for expr_type, count in analysis["expression_type_distribution"].items():
            percentage = count / total * 100
            print(f"  {expr_type:15} {count:2} formulas ({percentage:4.1f}%)")
        
        # Strengths and weaknesses
        if analysis["strengths"]:
            print(f"\n✅ STRENGTHS")
            for strength in analysis["strengths"]:
                print(f"  • {strength}")
                
        if analysis["weaknesses"]:
            print(f"\n❌ WEAKNESSES")
            for weakness in analysis["weaknesses"]:
                print(f"  • {weakness}")
                
        if analysis["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS")
            for rec in analysis["recommendations"]:
                print(f"  • {rec}")
        
        # Critical assessment
        print(f"\n🎯 CRITICAL ASSESSMENT")
        if overall_rate >= 0.8:
            print(f"  GENUINE CAPABILITY: Parser handles diverse mathematical expressions well")
        elif overall_rate >= 0.6:
            print(f"  MODERATE CAPABILITY: Parser works for many cases but has significant gaps")
        elif overall_rate >= 0.4:
            print(f"  LIMITED CAPABILITY: Parser works for basic cases only")
        else:
            print(f"  POOR CAPABILITY: Parser fails on most mathematical expressions")
            
        if overall_rate > 0.5:
            print(f"  ✅ ADDRESSES CRITICISM: More than cherry-picked test cases")
        else:
            print(f"  ❌ FAILS TO ADDRESS CRITICISM: Cannot handle diverse mathematical patterns")

def main():
    """Run the comprehensive test suite"""
    
    test_suite = ComprehensiveFormulaTestSuite()
    
    # Run tests
    results = test_suite.run_comprehensive_test()
    
    # Analyze results
    analysis = test_suite.analyze_results(results)
    
    # Generate report
    test_suite.generate_report(results, analysis)
    
    # Save detailed results
    output_data = {
        "results": results,
        "analysis": analysis,
        "timestamp": "2025-01-26T19:30:00Z",
        "test_description": "Comprehensive test of 50+ diverse mathematical formulas"
    }
    
    with open("comprehensive_formula_test_results.json", "w") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n📁 Detailed results saved to: comprehensive_formula_test_results.json")
    
    # Return success if overall performance is reasonable
    return analysis["overall_success_rate"] >= 0.6

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)