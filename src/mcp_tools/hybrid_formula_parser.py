"""
Hybrid Formula Parser with SymPy Integration

Combines SymPy's powerful parsing capabilities with our custom validation
and mathematical correctness testing approach.
"""

import re
import math
import logging
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass

try:
    from sympy import sympify, lambdify, symbols
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    logging.warning("SymPy not available - falling back to enhanced parser only")

from .enhanced_formula_parser import EnhancedFormulaParser, ParseResult

@dataclass 
class ValidationResult:
    """Result of mathematical validation"""
    is_valid: bool
    test_results: List[Dict[str, Any]]
    mathematical_properties: Dict[str, Any]
    validation_score: float = 0.0

logger = logging.getLogger(__name__)


class HybridFormulaParser:
    """
    Hybrid parser that leverages SymPy for complex expressions
    while maintaining our validation approach.
    """
    
    def __init__(self):
        self.enhanced_parser = EnhancedFormulaParser()
        self.sympy_enabled = SYMPY_AVAILABLE
        self._parser_usage_stats = {
            'sympy_attempts': 0,
            'sympy_success': 0,
            'sympy_fallback': 0,
            'enhanced_only': 0,
            'total_parses': 0
        }
        self._complex_indicators = [
            'max(', 'min(', 'Max(', 'Min(',  # Min/max functions
            'where(', 'if(', 'when(',  # Conditional expressions
            'sum(', 'prod(', 'mean(',  # Aggregation functions
            'exp(sin(', 'log(cos(',  # Nested transcendental
            'gamma(', 'beta(', 'erf(',  # Special functions
            'integrate(', 'diff(',  # Calculus operations
            'binomial(', 'factorial(',  # Combinatorial
        ]
        
    def parse_formula(self, formula_text: str) -> ParseResult:
        """
        Parse mathematical formula using SymPy for complex expressions,
        falling back to enhanced parser for simpler ones.
        
        Args:
            formula_text: Mathematical formula string
            
        Returns:
            ParseResult with generated code and validation
        """
        try:
            # Clean the formula
            formula_text = formula_text.strip()
            self._parser_usage_stats['total_parses'] += 1
            
            # Determine if we should use SymPy
            use_sympy = self._should_use_sympy(formula_text)
            
            if use_sympy and self.sympy_enabled:
                logger.info(f"Using SymPy for complex formula: {formula_text}")
                self._parser_usage_stats['sympy_attempts'] += 1
                try:
                    result = self._parse_with_sympy(formula_text)
                    self._parser_usage_stats['sympy_success'] += 1
                    return result
                except Exception as e:
                    logger.warning(f"SymPy parsing failed, falling back: {e}")
                    self._parser_usage_stats['sympy_fallback'] += 1
                    # Fall back to enhanced parser
            else:
                self._parser_usage_stats['enhanced_only'] += 1
                    
            # Use enhanced parser for simple expressions or as fallback
            return self.enhanced_parser.parse_formula(formula_text)
            
        except Exception as e:
            logger.error(f"Hybrid parsing failed: {e}")
            return ParseResult(
                success=False,
                python_code="",
                validation_result=None,
                error=str(e),
                mathematical_properties=None
            )
    
    def _should_use_sympy(self, formula: str) -> bool:
        """
        Determine if formula is complex enough to warrant SymPy parsing.
        
        Args:
            formula: Formula text
            
        Returns:
            True if SymPy should be used
        """
        # Check for complex indicators
        for indicator in self._complex_indicators:
            if indicator in formula:
                return True
                
        # Check for nested parentheses (complexity indicator)
        paren_depth = 0
        max_depth = 0
        for char in formula:
            if char == '(':
                paren_depth += 1
                max_depth = max(max_depth, paren_depth)
            elif char == ')':
                paren_depth -= 1
                
        if max_depth > 3:  # Deeply nested expressions
            return True
            
        # Check for multiple operations
        operators = re.findall(r'[\+\-\*/\^]', formula)
        if len(operators) > 5:  # Many operations
            return True
            
        return False
    
    def _parse_with_sympy(self, formula_text: str) -> ParseResult:
        """
        Parse formula using SymPy with enhanced error handling.
        
        Args:
            formula_text: Mathematical formula
            
        Returns:
            ParseResult with SymPy-generated code
        """
        try:
            # Extract left/right sides if equation
            if '=' in formula_text and not any(op in formula_text for op in ['<=', '>=', '==']):
                left, right = formula_text.split('=', 1)
                left = left.strip()
                right = right.strip()
                
                # Extract function signature if present
                func_match = re.match(r'(\w+)\(([^)]+)\)', left)
                if func_match:
                    func_name, params = func_match.groups()
                    variables = [p.strip() for p in params.split(',')]
                else:
                    # Try to extract variables from the expression
                    variables = self._extract_variables_from_expression(right)
                    func_name = left.strip()
            else:
                # Direct expression
                right = formula_text
                variables = self._extract_variables_from_expression(right)
                func_name = 'f'
            
            # Create symbols for all variables
            if not variables:
                variables = ['x']  # Default variable
                
            sym_vars = symbols(' '.join(variables))
            if len(variables) == 1:
                sym_vars = [sym_vars]  # Make it a list for consistency
                
            # Convert ^ to ** before parsing (SymPy expects Python syntax)
            right_python = right.replace('^', '**')
            
            # Parse the expression with enhanced transformations
            transformations = standard_transformations + (implicit_multiplication_application,)
            expr = parse_expr(right_python, transformations=transformations)
            
            # Generate lambda function
            func = lambdify(sym_vars, expr, modules=['numpy', 'sympy', 'math'])
            
            # Generate clean Python code
            python_code = self._generate_python_code_from_sympy(
                func_name, variables, expr, func
            )
            
            # Validate the generated function
            validation_result = self._validate_sympy_function(func, variables)
            
            return ParseResult(
                success=True,
                python_code=python_code,
                validation_result=validation_result,
                error=None,
                mathematical_properties=validation_result.mathematical_properties
            )
            
        except Exception as e:
            logger.error(f"SymPy parsing error: {e}")
            raise
    
    def _extract_variables_from_expression(self, expr: str) -> List[str]:
        """
        Extract variable names from an expression.
        
        Args:
            expr: Mathematical expression
            
        Returns:
            List of variable names
        """
        # Common variable patterns
        var_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        potential_vars = re.findall(var_pattern, expr)
        
        # Filter out function names and constants
        excluded = {
            'sin', 'cos', 'tan', 'exp', 'log', 'ln', 'sqrt', 'abs',
            'max', 'min', 'sum', 'prod', 'mean', 'std', 'var',
            'pi', 'e', 'gamma', 'beta', 'erf', 'erfc',
            'ceil', 'floor', 'round', 'sign',
            'sinh', 'cosh', 'tanh', 'asin', 'acos', 'atan',
            'True', 'False', 'None'
        }
        
        variables = []
        for var in potential_vars:
            if var not in excluded and var not in variables:
                variables.append(var)
                
        # If no variables found, check for common patterns
        if not variables:
            if 'x' in expr:
                variables = ['x']
            elif 'p' in expr:
                variables = ['p']
            elif 't' in expr:
                variables = ['t']
                
        return variables if variables else ['x']  # Default to 'x'
    
    def _generate_python_code_from_sympy(
        self,
        func_name: str,
        variables: List[str],
        expr: Any,  # SymPy expression
        func: Callable
    ) -> str:
        """
        Generate clean Python code from SymPy expression.
        
        Args:
            func_name: Function name
            variables: Variable names
            expr: SymPy expression
            func: Lambdified function
            
        Returns:
            Python code string
        """
        # Convert SymPy expression to Python code
        expr_str = str(expr)
        
        # Clean up SymPy notation - handle special cases first
        # Direct replacements without regex (to avoid special char issues)
        simple_replacements = {
            'Max': 'max',  # SymPy Max -> Python max
            'Min': 'min',  # SymPy Min -> Python min
            'Abs': 'abs',  # SymPy Abs -> Python abs
        }
        
        for old, new in simple_replacements.items():
            expr_str = expr_str.replace(old, new)
        
        # Math function replacements with word boundaries
        math_replacements = {
            'log': 'math.log',
            'exp': 'math.exp',
            'sin': 'math.sin',
            'cos': 'math.cos',
            'tan': 'math.tan',
            'sqrt': 'math.sqrt',
            'pi': 'math.pi',
            'e': 'math.e',  # lowercase e for Euler's number
        }
        
        for old, new in math_replacements.items():
            # Only use regex for simple alphanumeric patterns
            expr_str = re.sub(rf'\b{old}\b', new, expr_str)
        
        # Generate function signature
        var_list = ', '.join(variables)
        type_hints = ', '.join(f"{v}: Union[float, int]" for v in variables)
        
        # Build the function
        code = f'''def {func_name}({type_hints}) -> float:
    """
    Generated mathematical function
    Variables: {', '.join(variables)}
    Expression: {str(expr)}
    """
    return {expr_str}'''
        
        return code
    
    def _validate_sympy_function(
        self,
        func: Callable,
        variables: List[str]
    ) -> ValidationResult:
        """
        Validate SymPy-generated function with test cases.
        
        Args:
            func: Lambdified function
            variables: Variable names
            
        Returns:
            ValidationResult with test outcomes
        """
        # Generate test cases based on number of variables
        test_cases = self._generate_test_cases_for_variables(len(variables))
        test_results = []
        
        for test_case in test_cases:
            try:
                # Handle both single and multiple arguments
                if len(variables) == 1:
                    result = func(test_case[0])
                else:
                    result = func(*test_case)
                    
                test_results.append({
                    'input': test_case,
                    'output': float(result),
                    'success': True
                })
            except Exception as e:
                test_results.append({
                    'input': test_case,
                    'error': str(e),
                    'success': False
                })
        
        # Calculate validation score
        success_count = sum(1 for r in test_results if r['success'])
        validation_score = success_count / len(test_results) if test_results else 0.0
        
        # Analyze mathematical properties
        properties = self._analyze_mathematical_properties_from_results(test_results)
        
        return ValidationResult(
            is_valid=validation_score > 0.8,
            test_results=test_results,
            mathematical_properties=properties,
            validation_score=validation_score
        )
    
    def _generate_test_cases_for_variables(self, num_vars: int) -> List[tuple]:
        """
        Generate comprehensive test cases for n variables.
        
        Args:
            num_vars: Number of variables
            
        Returns:
            List of test case tuples
        """
        if num_vars == 1:
            # Single variable test cases
            return [
                (0.0,), (1.0,), (2.0,), (10.0,), (0.5,),
                (-1.0,), (-2.0,), (100.0,), (0.1,), (0.01,)
            ]
        elif num_vars == 2:
            # Two variable test cases
            base_values = [0.0, 1.0, 2.0, -1.0, 0.5]
            test_cases = []
            for v1 in base_values:
                for v2 in base_values[:3]:  # Limit combinations
                    test_cases.append((v1, v2))
            return test_cases
        else:
            # Multi-variable test cases (limited for performance)
            import itertools
            base_values = [0.0, 1.0, -1.0]
            combinations = list(itertools.product(base_values, repeat=num_vars))
            return combinations[:15]  # Limit to 15 test cases
    
    def _analyze_mathematical_properties_from_results(
        self,
        test_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze mathematical properties from test results.
        
        Args:
            test_results: List of test results
            
        Returns:
            Dictionary of mathematical properties
        """
        valid_results = [r for r in test_results if r.get('success')]
        
        if not valid_results:
            return {
                'domain_restrictions': ['Unable to determine - all tests failed'],
                'range_estimate': None,
                'special_values': {}
            }
        
        # Extract outputs
        outputs = [r['output'] for r in valid_results]
        
        # Analyze range
        range_estimate = (min(outputs), max(outputs)) if outputs else None
        
        # Check for special values
        special_values = {}
        for r in valid_results:
            input_val = r['input']
            output_val = r['output']
            
            # Check for identity (f(x) = x)
            if len(input_val) == 1 and abs(input_val[0] - output_val) < 1e-10:
                special_values['identity_point'] = input_val[0]
                
            # Check for zero output
            if abs(output_val) < 1e-10:
                special_values['zero_point'] = input_val
                
        # Domain restrictions based on failures
        failed_inputs = [r['input'] for r in test_results if not r.get('success')]
        domain_restrictions = []
        if failed_inputs:
            # Analyze patterns in failures
            if any(inp[0] < 0 for inp in failed_inputs if len(inp) > 0):
                domain_restrictions.append("Possible restriction on negative values")
                
        return {
            'domain_restrictions': domain_restrictions or ['No restrictions found'],
            'range_estimate': range_estimate,
            'special_values': special_values,
            'success_rate': len(valid_results) / len(test_results) if test_results else 0
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get parser capabilities including SymPy status"""
        base_capabilities = self.enhanced_parser.get_capabilities()
        
        return {
            **base_capabilities,
            'sympy_available': self.sympy_enabled,
            'advanced_functions': [
                'min/max with multiple arguments',
                'conditional expressions (where, if)',
                'aggregation functions (sum, prod, mean)',
                'nested transcendental functions',
                'special functions (gamma, beta, erf)',
                'symbolic operations (when SymPy available)'
            ] if self.sympy_enabled else [],
            'parser_mode': 'hybrid' if self.sympy_enabled else 'enhanced_only',
            'usage_stats': self._parser_usage_stats
        }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get detailed usage statistics"""
        stats = self._parser_usage_stats.copy()
        if stats['total_parses'] > 0:
            stats['sympy_success_rate'] = stats['sympy_success'] / stats['sympy_attempts'] if stats['sympy_attempts'] > 0 else 0
            stats['enhanced_usage_pct'] = stats['enhanced_only'] / stats['total_parses'] * 100
            stats['sympy_usage_pct'] = stats['sympy_success'] / stats['total_parses'] * 100
            stats['fallback_rate'] = stats['sympy_fallback'] / stats['sympy_attempts'] if stats['sympy_attempts'] > 0 else 0
        return stats