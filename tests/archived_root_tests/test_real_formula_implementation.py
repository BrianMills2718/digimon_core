#!/usr/bin/env python3
"""
Test actual formula parsing and implementation for FORMULAS category.
This tests whether we can convert mathematical expressions to executable code.
"""

import json
import re
import ast
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import traceback

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_tools.algorithm_tools import AlgorithmImplementationTools

class FormulaParser:
    """Parse mathematical formulas into executable Python code"""
    
    def __init__(self):
        self.variable_patterns = {
            'x': 'x',
            'y': 'y', 
            'z': 'z',
            'v(x)': 'x',
            'p(x)': 'x',
            'outcome': 'outcome',
            'probability': 'probability',
            'value': 'value'
        }
        
    def parse_formula(self, formula_text: str, description: str = "") -> Optional[str]:
        """
        Parse a mathematical formula into executable Python code.
        
        Args:
            formula_text: Mathematical formula as string (e.g., "v(x) = x^0.88")
            description: Description for context
            
        Returns:
            Python code string or None if parsing fails
        """
        try:
            # Clean and normalize the formula
            formula = formula_text.strip()
            
            # Handle common formula patterns
            if '=' in formula:
                left, right = formula.split('=', 1)
                left = left.strip()
                right = right.strip()
                
                # Extract function name and parameter
                if '(' in left and ')' in left:
                    func_match = re.match(r'(\w+)\((\w+)\)', left)
                    if func_match:
                        func_name, param = func_match.groups()
                        # Convert mathematical notation to Python
                        python_expr = self._convert_math_to_python(right, param)
                        if python_expr:
                            return f"return {python_expr}"
                            
                # Handle direct variable assignments
                else:
                    var_name = self._extract_main_variable(left)
                    if var_name:
                        python_expr = self._convert_math_to_python(right, var_name)
                        if python_expr:
                            return f"return {python_expr}"
                            
            # Handle direct expressions without equals
            else:
                python_expr = self._convert_math_to_python(formula, 'x')
                if python_expr:
                    return f"return {python_expr}"
                    
            return None
            
        except Exception as e:
            print(f"Formula parsing error: {e}")
            return None
    
    def _convert_math_to_python(self, expr: str, main_var: str) -> Optional[str]:
        """Convert mathematical expression to Python code"""
        try:
            # Replace common mathematical notation
            python_expr = expr
            
            # Power notation: x^0.88 -> x ** 0.88
            python_expr = re.sub(r'(\w+)\^([0-9.]+)', r'\1 ** \2', python_expr)
            
            # Function calls: log(x) -> math.log(x), sqrt(x) -> math.sqrt(x)
            python_expr = re.sub(r'\blog\(', 'math.log(', python_expr)
            python_expr = re.sub(r'\bsqrt\(', 'math.sqrt(', python_expr)
            python_expr = re.sub(r'\bexp\(', 'math.exp(', python_expr)
            python_expr = re.sub(r'\babs\(', 'abs(', python_expr)
            
            # Handle negative powers: x^-0.88 -> x ** -0.88
            python_expr = re.sub(r'(\w+)\^-([0-9.]+)', r'\1 ** -\2', python_expr)
            
            # Handle complex expressions with parentheses: (-x)^0.88 -> ((-x) ** 0.88)
            python_expr = re.sub(r'\(([^)]+)\)\^([0-9.]+)', r'((\1) ** \2)', python_expr)
            
            # Replace variables with the main parameter name for consistency
            # Always use 'x' as the function parameter name
            python_expr = re.sub(r'\bp\b', 'x', python_expr)  # p -> x for probability functions
                
            # Replace common constants
            python_expr = re.sub(r'\bpi\b', 'math.pi', python_expr)
            python_expr = re.sub(r'\be\b', 'math.e', python_expr)
            
            # Validate the expression by parsing it
            try:
                # Replace main variable with a test value to validate syntax
                test_expr = python_expr.replace(main_var, '1.0')
                test_expr = python_expr.replace('x', '1.0')  # Also replace x
                if 'math.' in test_expr:
                    test_expr = f"import math; {test_expr}"
                    # Use eval to test (in controlled environment)
                    exec(f"result = {test_expr.split(';', 1)[1] if ';' in test_expr else test_expr}")
                else:
                    eval(test_expr)
                return python_expr
            except Exception as e:
                return None
                
        except Exception:
            return None
            
    def _extract_main_variable(self, expr: str) -> Optional[str]:
        """Extract the main variable from an expression"""
        for var in ['x', 'y', 'z', 'outcome', 'value']:
            if var in expr:
                return var
        return 'x'  # Default

class RealFormulaImplementation:
    """Test real formula implementation with actual mathematical parsing"""
    
    def __init__(self):
        self.parser = FormulaParser()
        self.algo_tools = AlgorithmImplementationTools()
        
    def test_prospect_theory_formulas(self) -> Dict[str, Any]:
        """Test real implementation of Prospect Theory formulas"""
        
        # Real Prospect Theory formulas
        formulas = [
            {
                "name": "Value Function for Gains",
                "category": "FORMULAS",
                "description": "Value function for gains in prospect theory: v(x) = x^0.88",
                "formula": "v(x) = x^0.88",
                "test_cases": [
                    {"input": 100, "expected": 100 ** 0.88},
                    {"input": 50, "expected": 50 ** 0.88},
                    {"input": 1, "expected": 1}
                ]
            },
            {
                "name": "Value Function for Losses", 
                "category": "FORMULAS",
                "description": "Value function for losses: v(x) = -2.25 * (-x)^0.88",
                "formula": "v(x) = -2.25 * (-x)^0.88",
                "test_cases": [
                    {"input": -100, "expected": -2.25 * (100 ** 0.88)},
                    {"input": -50, "expected": -2.25 * (50 ** 0.88)},
                    {"input": -1, "expected": -2.25}
                ]
            },
            {
                "name": "Probability Weighting",
                "category": "FORMULAS", 
                "description": "Probability weighting function: w(p) = p^0.61",
                "formula": "w(p) = p^0.61",
                "test_cases": [
                    {"input": 0.5, "expected": 0.5 ** 0.61},
                    {"input": 0.25, "expected": 0.25 ** 0.61},
                    {"input": 1.0, "expected": 1.0}
                ]
            }
        ]
        
        results = {
            "formulas_tested": len(formulas),
            "successful_parsing": 0,
            "working_implementations": 0,
            "test_results": []
        }
        
        for formula in formulas:
            print(f"\n--- Testing {formula['name']} ---")
            
            # Parse the formula
            implementation = self.parser.parse_formula(
                formula['formula'], 
                formula['description']
            )
            
            if implementation:
                results["successful_parsing"] += 1
                print(f"✅ Parsed: {implementation}")
                
                # Generate complete function
                func_code = self._generate_complete_function(
                    formula['name'],
                    implementation,
                    formula['description']
                )
                
                # Test the function
                test_result = self._test_function(func_code, formula['test_cases'])
                
                if test_result["success"]:
                    results["working_implementations"] += 1
                    print(f"✅ Working implementation")
                else:
                    error_msg = test_result.get('error', 'Unknown error')
                    print(f"❌ Implementation failed: {error_msg}")
                    
                results["test_results"].append({
                    "name": formula['name'],
                    "formula": formula['formula'],
                    "parsed": True,
                    "implementation": implementation,
                    "working": test_result["success"],
                    "error": test_result.get("error"),
                    "test_details": test_result
                })
            else:
                print(f"❌ Failed to parse formula: {formula['formula']}")
                results["test_results"].append({
                    "name": formula['name'],
                    "formula": formula['formula'], 
                    "parsed": False,
                    "working": False,
                    "error": "Formula parsing failed"
                })
        
        return results
    
    def _generate_complete_function(self, name: str, implementation: str, description: str) -> str:
        """Generate complete Python function with imports"""
        func_name = name.lower().replace(" ", "_").replace("-", "_")
        
        needs_math = 'math.' in implementation
        imports = "import math\n" if needs_math else ""
        
        return f'''{imports}
def {func_name}(x):
    """
    {description}
    """
    {implementation}

# Test function
if __name__ == "__main__":
    # Basic test
    result = {func_name}(100)
    print(f"Test result for {func_name}(100): {{result}}")
'''
    
    def _test_function(self, func_code: str, test_cases: list) -> Dict[str, Any]:
        """Test a generated function against test cases"""
        try:
            # Execute the function code
            namespace = {}
            exec(func_code, namespace)
            
            # Find the function
            func = None
            for name, obj in namespace.items():
                if callable(obj) and not name.startswith('_'):
                    func = obj
                    break
                    
            if not func:
                return {"success": False, "error": "No function found in generated code"}
                
            # Run test cases
            passed_tests = 0
            for test_case in test_cases:
                try:
                    result = func(test_case["input"])
                    expected = test_case["expected"]
                    
                    # Allow small floating point differences
                    if abs(result - expected) < 0.001:
                        passed_tests += 1
                    else:
                        print(f"  Test failed: f({test_case['input']}) = {result}, expected {expected}")
                        
                except Exception as e:
                    print(f"  Test error: f({test_case['input']}) -> {e}")
                    
            success = passed_tests == len(test_cases)
            return {
                "success": success,
                "passed_tests": passed_tests,
                "total_tests": len(test_cases),
                "pass_rate": passed_tests / len(test_cases) if test_cases else 0
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    """Run the real formula implementation test"""
    print("=== REAL Formula Implementation Test ===")
    print("Testing actual mathematical formula parsing and code generation")
    
    tester = RealFormulaImplementation()
    results = tester.test_prospect_theory_formulas()
    
    print(f"\n=== RESULTS ===")
    print(f"Formulas tested: {results['formulas_tested']}")
    print(f"Successfully parsed: {results['successful_parsing']}")
    print(f"Working implementations: {results['working_implementations']}")
    print(f"Success rate: {results['working_implementations']}/{results['formulas_tested']}")
    
    # Save detailed results
    with open("real_formula_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Detailed results saved to real_formula_results.json")
    
    if results['working_implementations'] > 0:
        print(f"\n✅ SUCCESS: {results['working_implementations']} real formula implementations working!")
        return True
    else:
        print(f"\n❌ FAILURE: No working implementations generated")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)