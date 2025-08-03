#!/usr/bin/env python3
"""
Dynamic execution of LLM-generated code with sandboxing and safety measures.
"""

import ast
import sys
import io
import contextlib
import resource
import signal
import traceback
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass
import logging
import multiprocessing
import queue
import time

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of code execution"""
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    memory_used: int = 0
    stdout: str = ""
    stderr: str = ""


class SafeExecutor:
    """Executes code in a sandboxed environment with safety measures"""
    
    def __init__(self, 
                 timeout: int = 5,
                 memory_limit_mb: int = 100,
                 allowed_modules: Optional[List[str]] = None):
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb
        self.allowed_modules = allowed_modules or ['math', 'numpy', 'typing']
    
    def execute_code(self, code: str, inputs: Dict[str, Any], 
                    function_name: str) -> ExecutionResult:
        """Execute code safely with inputs and return result"""
        
        # First validate the code
        is_safe, error = self._validate_code_safety(code)
        if not is_safe:
            return ExecutionResult(
                success=False,
                result=None,
                error=f"Code validation failed: {error}"
            )
        
        # Execute in subprocess for true isolation
        return self._execute_in_subprocess(code, inputs, function_name)
    
    def _validate_code_safety(self, code: str) -> Tuple[bool, Optional[str]]:
        """Validate code for safety before execution"""
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        
        # Check for dangerous patterns
        class SafetyValidator(ast.NodeVisitor):
            def __init__(self):
                self.errors = []
            
            def visit_Import(self, node):
                for alias in node.names:
                    if alias.name not in self.allowed_modules:
                        self.errors.append(f"Import of '{alias.name}' not allowed")
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                if node.module and node.module.split('.')[0] not in self.allowed_modules:
                    self.errors.append(f"Import from '{node.module}' not allowed")
                self.generic_visit(node)
            
            def visit_Call(self, node):
                # Check for dangerous function calls
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', 'compile', '__import__', 'open']:
                        self.errors.append(f"Call to '{node.func.id}' not allowed")
                self.generic_visit(node)
            
            def visit_Attribute(self, node):
                # Check for dangerous attribute access
                if node.attr in ['__globals__', '__builtins__', '__import__']:
                    self.errors.append(f"Access to '{node.attr}' not allowed")
                self.generic_visit(node)
        
        validator = SafetyValidator()
        validator.allowed_modules = self.allowed_modules
        validator.visit(tree)
        
        if validator.errors:
            return False, "; ".join(validator.errors)
        
        return True, None
    
    def _execute_in_subprocess(self, code: str, inputs: Dict[str, Any], 
                              function_name: str) -> ExecutionResult:
        """Execute code in an isolated subprocess"""
        
        def worker(code: str, inputs: Dict[str, Any], function_name: str, 
                  result_queue: multiprocessing.Queue):
            """Worker function that runs in subprocess"""
            
            start_time = time.time()
            
            # Set resource limits
            if sys.platform != 'win32':
                # Memory limit (in bytes)
                resource.setrlimit(resource.RLIMIT_AS, 
                                 (self.memory_limit_mb * 1024 * 1024, 
                                  self.memory_limit_mb * 1024 * 1024))
            
            # Capture stdout/stderr
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            try:
                with contextlib.redirect_stdout(stdout_capture), \
                     contextlib.redirect_stderr(stderr_capture):
                    
                    # Create restricted namespace
                    # Note: In subprocess, we need to recreate the namespace
                    namespace = {
                        '__builtins__': {
                            'abs': abs, 'all': all, 'any': any, 'bool': bool,
                            'dict': dict, 'enumerate': enumerate, 'float': float,
                            'int': int, 'len': len, 'list': list, 'max': max,
                            'min': min, 'pow': pow, 'range': range, 'round': round,
                            'set': set, 'sorted': sorted, 'str': str, 'sum': sum,
                            'tuple': tuple, 'type': type, 'zip': zip,
                            'True': True, 'False': False, 'None': None,
                            '__import__': __import__
                        }
                    }
                    
                    # Add allowed modules
                    import math
                    namespace['math'] = math
                    
                    import typing
                    namespace['typing'] = typing
                    namespace['Union'] = typing.Union
                    namespace['List'] = typing.List
                    namespace['Dict'] = typing.Dict
                    namespace['Any'] = typing.Any
                    
                    # Execute the code
                    exec(code, namespace)
                    
                    # Find and call the function
                    if function_name not in namespace:
                        raise ValueError(f"Function '{function_name}' not found")
                    
                    func = namespace[function_name]
                    result = func(**inputs)
                    
                    execution_time = time.time() - start_time
                    
                    result_queue.put(ExecutionResult(
                        success=True,
                        result=result,
                        execution_time=execution_time,
                        stdout=stdout_capture.getvalue(),
                        stderr=stderr_capture.getvalue()
                    ))
                    
            except Exception as e:
                result_queue.put(ExecutionResult(
                    success=False,
                    result=None,
                    error=f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}",
                    execution_time=time.time() - start_time,
                    stdout=stdout_capture.getvalue(),
                    stderr=stderr_capture.getvalue()
                ))
        
        # Create queue for results
        result_queue = multiprocessing.Queue()
        
        # Create and start process
        process = multiprocessing.Process(
            target=worker, 
            args=(code, inputs, function_name, result_queue)
        )
        process.start()
        
        # Wait for completion with timeout
        process.join(timeout=self.timeout)
        
        if process.is_alive():
            # Timeout occurred
            process.terminate()
            process.join()
            return ExecutionResult(
                success=False,
                result=None,
                error=f"Execution timed out after {self.timeout} seconds"
            )
        
        # Get result
        try:
            return result_queue.get_nowait()
        except queue.Empty:
            return ExecutionResult(
                success=False,
                result=None,
                error="No result returned from subprocess"
            )
    
    def _create_safe_namespace(self) -> Dict[str, Any]:
        """Create a restricted namespace for code execution"""
        
        # Safe built-ins only
        safe_builtins = {
            'abs': abs, 'all': all, 'any': any, 'bool': bool,
            'dict': dict, 'enumerate': enumerate, 'float': float,
            'int': int, 'len': len, 'list': list, 'max': max,
            'min': min, 'pow': pow, 'range': range, 'round': round,
            'set': set, 'sorted': sorted, 'str': str, 'sum': sum,
            'tuple': tuple, 'type': type, 'zip': zip,
            'True': True, 'False': False, 'None': None
        }
        
        namespace = {'__builtins__': safe_builtins}
        
        # Add allowed modules with proper import
        namespace['__import__'] = __import__
        
        for module_name in self.allowed_modules:
            if module_name == 'math':
                import math
                namespace['math'] = math
            elif module_name == 'numpy':
                try:
                    import numpy as np
                    namespace['numpy'] = np
                    namespace['np'] = np
                except ImportError:
                    logger.warning("NumPy not available")
            elif module_name == 'typing':
                import typing
                namespace['typing'] = typing
                namespace['Union'] = typing.Union
                namespace['List'] = typing.List
                namespace['Dict'] = typing.Dict
                namespace['Any'] = typing.Any
                namespace['Optional'] = typing.Optional
        
        return namespace


class DynamicTheoryExecutor:
    """Executes theory computations using LLM-generated code"""
    
    def __init__(self, executor: Optional[SafeExecutor] = None):
        self.executor = executor or SafeExecutor()
        self.generated_modules = {}
    
    def load_generated_module(self, module_code: str, module_name: str) -> bool:
        """Load a generated module for execution"""
        
        # Validate the module
        is_safe, error = self.executor._validate_code_safety(module_code)
        if not is_safe:
            logger.error(f"Module validation failed: {error}")
            return False
        
        self.generated_modules[module_name] = module_code
        return True
    
    def execute_formula(self, module_name: str, function_name: str, 
                       inputs: Dict[str, Any]) -> ExecutionResult:
        """Execute a specific formula from a loaded module"""
        
        if module_name not in self.generated_modules:
            return ExecutionResult(
                success=False,
                result=None,
                error=f"Module '{module_name}' not loaded"
            )
        
        code = self.generated_modules[module_name]
        return self.executor.execute_code(code, inputs, function_name)
    
    def execute_theory_analysis(self, theory_name: str, 
                               formulas: List[str], 
                               parameters: Dict[str, Any]) -> Dict[str, ExecutionResult]:
        """Execute complete theory analysis with multiple formulas"""
        
        results = {}
        
        for formula_name in formulas:
            # Map parameters to formula inputs
            formula_inputs = self._map_parameters_to_inputs(formula_name, parameters)
            
            # Execute
            result = self.execute_formula(theory_name, formula_name, formula_inputs)
            results[formula_name] = result
            
            if result.success:
                logger.info(f"Successfully executed {formula_name}: {result.result}")
            else:
                logger.error(f"Failed to execute {formula_name}: {result.error}")
        
        return results
    
    def _map_parameters_to_inputs(self, formula_name: str, 
                                 parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Map extracted parameters to formula inputs"""
        
        # This would be more sophisticated in production
        # For now, simple mapping based on formula name
        
        if 'value' in formula_name.lower():
            # Value function typically needs outcome and reference point
            return {
                'x': parameters.get('outcome', 0),
                'reference_point': parameters.get('reference_point', 0)
            }
        
        elif 'probability' in formula_name.lower():
            # Probability weighting needs probability value
            return {
                'p': parameters.get('probability', 0.5)
            }
        
        elif 'prospect' in formula_name.lower():
            # Full prospect evaluation needs all parameters
            return {
                'outcomes': parameters.get('outcomes', [0]),
                'probabilities': parameters.get('probabilities', [1.0]),
                'reference_point': parameters.get('reference_point', 0)
            }
        
        # Default: pass all parameters
        return parameters


def test_dynamic_execution():
    """Test dynamic code execution"""
    
    # Example generated code
    generated_code = '''
import math
from typing import List

def calculate_prospect_value(outcomes: List[float], 
                           probabilities: List[float], 
                           reference_point: float = 0) -> float:
    """Calculate prospect value using Prospect Theory"""
    
    def value_function(x: float) -> float:
        relative = x - reference_point
        if relative >= 0:
            return relative ** 0.88
        else:
            return -2.25 * ((-relative) ** 0.88)
    
    def weight_probability(p: float) -> float:
        if p == 0:
            return 0
        elif p == 1:
            return 1
        else:
            gamma = 0.61
            return (p ** gamma) / ((p ** gamma + (1-p) ** gamma) ** (1/gamma))
    
    total_value = 0
    for outcome, prob in zip(outcomes, probabilities):
        weighted_prob = weight_probability(prob)
        subj_value = value_function(outcome)
        total_value += weighted_prob * subj_value
    
    return total_value
'''
    
    # Create executor
    executor = SafeExecutor()
    
    # Test inputs
    inputs = {
        'outcomes': [100, -50],
        'probabilities': [0.7, 0.3],
        'reference_point': 0
    }
    
    print("Testing Dynamic Execution")
    print("=" * 40)
    
    # Execute the code
    result = executor.execute_code(generated_code, inputs, 'calculate_prospect_value')
    
    print(f"Success: {result.success}")
    if result.success:
        print(f"Result: {result.result:.2f}")
        print(f"Execution time: {result.execution_time:.3f}s")
    else:
        print(f"Error: {result.error}")
    
    if result.stdout:
        print(f"Stdout: {result.stdout}")
    
    # Test with dangerous code
    print("\nTesting Safety Measures")
    print("=" * 40)
    
    dangerous_code = '''
import os
def malicious():
    return os.system("echo 'This should not run'")
'''
    
    result2 = executor.execute_code(dangerous_code, {}, 'malicious')
    print(f"Dangerous code blocked: {not result2.success}")
    if not result2.success:
        print(f"Error: {result2.error}")


if __name__ == "__main__":
    test_dynamic_execution()