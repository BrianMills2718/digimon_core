#!/usr/bin/env python3
"""
Algorithm Executor for Level 2 (ALGORITHMS)

Safely executes generated algorithm classes with proper isolation and monitoring.
"""

import os
import sys
import time
import traceback
import threading
import signal
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
import logging
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class AlgorithmExecutionResult:
    """Result of algorithm execution"""
    success: bool
    result: Any
    execution_time: float
    iterations: Optional[int]
    converged: Optional[bool]
    error: Optional[str]
    metadata: Dict[str, Any]


class TimeoutError(Exception):
    """Raised when algorithm execution times out"""
    pass


class AlgorithmExecutor:
    """Executes generated algorithm classes safely"""
    
    def __init__(self, timeout_seconds: int = 60):
        self.timeout_seconds = timeout_seconds
        self.execution_history = []
    
    def execute_algorithm(self, algorithm_code: str, algorithm_class: str,
                         inputs: Dict[str, Any], 
                         method_name: str = "calculate") -> AlgorithmExecutionResult:
        """
        Execute an algorithm class method with given inputs
        
        Args:
            algorithm_code: The generated algorithm source code
            algorithm_class: Name of the algorithm class
            inputs: Input parameters for the algorithm
            method_name: Method to call (default: 'calculate')
            
        Returns:
            AlgorithmExecutionResult with results and metadata
        """
        
        start_time = time.time()
        
        try:
            # Create safe execution environment
            namespace = self._create_safe_namespace()
            
            # Execute the algorithm code to define the class
            exec(algorithm_code, namespace)
            
            if algorithm_class not in namespace:
                return AlgorithmExecutionResult(
                    success=False,
                    result=None,
                    execution_time=time.time() - start_time,
                    iterations=None,
                    converged=None,
                    error=f"Algorithm class '{algorithm_class}' not found",
                    metadata={}
                )
            
            # Instantiate the algorithm class
            AlgorithmClass = namespace[algorithm_class]
            
            # Extract initialization parameters that match the class signature
            init_params = self._extract_init_params_for_class(inputs, algorithm_code)
            algorithm_instance = AlgorithmClass(**init_params)
            
            # Prepare method inputs (remove init params)
            method_inputs = {k: v for k, v in inputs.items() 
                           if k not in init_params}
            
            # Execute with timeout
            result = self._execute_with_timeout(
                algorithm_instance, method_name, method_inputs
            )
            
            execution_time = time.time() - start_time
            
            # Extract metadata from result if available
            metadata = {}
            iterations = None
            converged = None
            
            if isinstance(result, dict):
                metadata = result.copy()
                iterations = result.get('iterations')
                converged = result.get('converged')
                
                # Main result might be under 'value' or be the whole dict
                if 'value' in result:
                    result = result['value']
            
            return AlgorithmExecutionResult(
                success=True,
                result=result,
                execution_time=execution_time,
                iterations=iterations,
                converged=converged,
                error=None,
                metadata=metadata
            )
            
        except TimeoutError:
            return AlgorithmExecutionResult(
                success=False,
                result=None,
                execution_time=self.timeout_seconds,
                iterations=None,
                converged=False,
                error=f"Algorithm execution timed out after {self.timeout_seconds} seconds",
                metadata={}
            )
        except Exception as e:
            return AlgorithmExecutionResult(
                success=False,
                result=None,
                execution_time=time.time() - start_time,
                iterations=None,
                converged=None,
                error=f"Execution error: {str(e)}\n{traceback.format_exc()}",
                metadata={}
            )
    
    def _create_safe_namespace(self) -> Dict[str, Any]:
        """Create a safe execution namespace"""
        
        # Basic safe built-ins
        safe_builtins = {
            'abs': abs, 'min': min, 'max': max, 'sum': sum,
            'len': len, 'range': range, 'enumerate': enumerate,
            'int': int, 'float': float, 'str': str, 'bool': bool,
            'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
            'isinstance': isinstance, 'hasattr': hasattr, 'getattr': getattr,
            'round': round, 'sorted': sorted, 'reversed': reversed,
            'zip': zip, 'map': map, 'filter': filter,
            'any': any, 'all': all,
            'True': True, 'False': False, 'None': None,
            '__build_class__': __build_class__,  # Required for class definitions
            '__import__': __import__  # Required for import statements
        }
        
        namespace = {
            '__builtins__': safe_builtins,
            '__name__': '__main__',
            # Standard exceptions
            'ValueError': ValueError,
            'TypeError': TypeError,
            'RuntimeError': RuntimeError,
            'IndexError': IndexError,
            'KeyError': KeyError,
            'AttributeError': AttributeError,
            'ZeroDivisionError': ZeroDivisionError,
            # Built-in functions/decorators
            'property': property,
            'staticmethod': staticmethod,
            'classmethod': classmethod,
            'callable': callable,
            'super': super,
        }
        
        # Add safe imports
        try:
            import math
            namespace['math'] = math
        except ImportError:
            pass
        
        try:
            import numpy as np
            namespace['np'] = np
            namespace['numpy'] = np
        except ImportError:
            # Create minimal numpy-like interface
            namespace['np'] = self._create_minimal_numpy()
            namespace['numpy'] = namespace['np']
        
        try:
            from typing import Dict, List, Optional, Any, Union, Tuple, Callable
            namespace['Dict'] = Dict
            namespace['List'] = List  
            namespace['Optional'] = Optional
            namespace['Any'] = Any
            namespace['Union'] = Union
            namespace['Tuple'] = Tuple
            namespace['Callable'] = Callable
        except ImportError:
            # Create dummy typing objects for older Python
            namespace['Dict'] = dict
            namespace['List'] = list
            namespace['Optional'] = lambda x: x
            namespace['Any'] = object
            namespace['Union'] = lambda *args: object
            namespace['Tuple'] = tuple
            namespace['Callable'] = object
        
        try:
            import logging
            namespace['logging'] = logging
        except ImportError:
            pass
        
        return namespace
    
    def _create_minimal_numpy(self):
        """Create minimal numpy-like interface if numpy not available"""
        class MinimalNumPy:
            @staticmethod
            def array(data):
                if isinstance(data, list):
                    return data
                return data
            
            @staticmethod
            def ones(n):
                return [1.0] * n
            
            @staticmethod
            def zeros(n):
                return [0.0] * n
            
            @staticmethod
            def abs(arr):
                if hasattr(arr, '__len__'):
                    return [abs(x) for x in arr]
                return abs(arr)
            
            @staticmethod
            def max(arr):
                return max(arr) if hasattr(arr, '__len__') else arr
            
            @staticmethod
            def sum(arr):
                return sum(arr) if hasattr(arr, '__len__') else arr
            
            class linalg:
                @staticmethod
                def norm(arr):
                    if hasattr(arr, '__len__'):
                        return sum(x*x for x in arr) ** 0.5
                    return abs(arr)
            
            @staticmethod
            def clip(arr, min_val, max_val):
                if hasattr(arr, '__len__'):
                    return [max(min_val, min(max_val, x)) for x in arr]
                return max(min_val, min(max_val, arr))
            
            class random:
                @staticmethod
                def seed(s):
                    import random
                    random.seed(s)
                
                @staticmethod
                def normal(mean=0, std=1):
                    import random
                    return random.gauss(mean, std)
            
            @staticmethod
            def mean(arr):
                return sum(arr) / len(arr) if hasattr(arr, '__len__') else arr
            
            @staticmethod
            def std(arr):
                if not hasattr(arr, '__len__'):
                    return 0
                m = sum(arr) / len(arr)
                return (sum((x - m) ** 2 for x in arr) / len(arr)) ** 0.5
            
            @staticmethod
            def percentile(arr, q):
                if not hasattr(arr, '__len__'):
                    return arr
                sorted_arr = sorted(arr)
                n = len(sorted_arr)
                index = (q / 100) * (n - 1)
                if index == int(index):
                    return sorted_arr[int(index)]
                else:
                    lower = sorted_arr[int(index)]
                    upper = sorted_arr[int(index) + 1]
                    return lower + (upper - lower) * (index - int(index))
        
        return MinimalNumPy()
    
    def _extract_init_params(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract initialization parameters from inputs"""
        
        # Common initialization parameter names
        init_param_names = {
            'max_iterations', 'tolerance', 'damping_factor', 'learning_rate',
            'n_simulations', 'random_seed', 'step_size', 'track_history'
        }
        
        init_params = {}
        for param_name in init_param_names:
            if param_name in inputs:
                init_params[param_name] = inputs[param_name]
        
        return init_params
    
    def _extract_init_params_for_class(self, inputs: Dict[str, Any], algorithm_code: str) -> Dict[str, Any]:
        """Extract initialization parameters that match the class __init__ signature"""
        
        # Parse the algorithm code to find __init__ parameters
        import ast
        import re
        
        # Extract the __init__ method signature
        init_pattern = r'def __init__\(self[^)]*\):'
        init_match = re.search(init_pattern, algorithm_code)
        
        if not init_match:
            return {}
        
        # Get the parameter names from the signature
        init_line = init_match.group()
        # Extract parameter names (excluding 'self')
        param_pattern = r'(\w+):\s*\w+\s*=\s*[^,)]+'
        param_matches = re.findall(param_pattern, init_line)
        
        # Also try simpler pattern for parameters without type hints
        simple_pattern = r'(\w+)\s*=\s*[^,)]+'
        simple_matches = re.findall(simple_pattern, init_line)
        
        valid_params = set(param_matches + simple_matches)
        valid_params.discard('self')  # Remove 'self' if somehow captured
        
        # Extract matching parameters from inputs
        init_params = {}
        for param_name in valid_params:
            if param_name in inputs:
                init_params[param_name] = inputs[param_name]
        
        return init_params
    
    def _execute_with_timeout(self, algorithm_instance: Any, method_name: str,
                             inputs: Dict[str, Any]) -> Any:
        """Execute algorithm method with timeout protection"""
        
        if not hasattr(algorithm_instance, method_name):
            # Try alternative method names
            alternative_methods = ['run', 'execute', 'compute', 'process']
            found_method = None
            for alt_method in alternative_methods:
                if hasattr(algorithm_instance, alt_method):
                    found_method = alt_method
                    break
            
            if found_method:
                method_name = found_method
            else:
                raise AttributeError(f"Algorithm does not have method '{method_name}' or alternatives {alternative_methods}")
        
        method = getattr(algorithm_instance, method_name)
        
        # Set up timeout using threading
        result = []
        exception = []
        
        def target():
            try:
                result.append(method(**inputs))
            except Exception as e:
                exception.append(e)
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout=self.timeout_seconds)
        
        if thread.is_alive():
            # Timeout occurred
            raise TimeoutError(f"Algorithm execution exceeded {self.timeout_seconds} seconds")
        
        if exception:
            raise exception[0]
        
        if result:
            return result[0]
        else:
            raise RuntimeError("Algorithm execution completed but returned no result")
    
    def validate_algorithm_inputs(self, inputs: Dict[str, Any], 
                                 expected_inputs: List[str]) -> Tuple[bool, Optional[str]]:
        """Validate that required inputs are present"""
        
        missing_inputs = []
        for required_input in expected_inputs:
            if required_input not in inputs:
                missing_inputs.append(required_input)
        
        if missing_inputs:
            return False, f"Missing required inputs: {missing_inputs}"
        
        return True, None
    
    def benchmark_algorithm(self, algorithm_code: str, algorithm_class: str,
                           test_cases: List[Dict[str, Any]], 
                           method_name: str = "calculate") -> Dict[str, Any]:
        """Benchmark algorithm performance across multiple test cases"""
        
        results = []
        total_time = 0
        successful_runs = 0
        
        for i, test_case in enumerate(test_cases):
            result = self.execute_algorithm(
                algorithm_code, algorithm_class, test_case, method_name
            )
            
            results.append({
                'test_case': i,
                'inputs': test_case,
                'result': result
            })
            
            total_time += result.execution_time
            if result.success:
                successful_runs += 1
        
        return {
            'total_test_cases': len(test_cases),
            'successful_runs': successful_runs,
            'success_rate': successful_runs / len(test_cases) if test_cases else 0,
            'total_execution_time': total_time,
            'average_execution_time': total_time / len(test_cases) if test_cases else 0,
            'results': results
        }


def test_algorithm_executor():
    """Test the algorithm executor with sample algorithm"""
    
    # Sample algorithm code (simple iterative algorithm)
    sample_algorithm = '''
class TestAlgorithm:
    def __init__(self, max_iterations: int = 10, tolerance: float = 0.01):
        self.max_iterations = max_iterations
        self.tolerance = tolerance
    
    def calculate(self, data):
        """Simple convergence test"""
        x = 1.0
        
        for i in range(self.max_iterations):
            x_new = 0.5 * (x + 2.0 / x)  # Newton's method for sqrt(2)
            
            if abs(x_new - x) < self.tolerance:
                return {
                    'value': x_new,
                    'converged': True,
                    'iterations': i + 1
                }
            x = x_new
        
        return {
            'value': x,
            'converged': False,
            'iterations': self.max_iterations
        }
'''
    
    executor = AlgorithmExecutor()
    
    print("=" * 50)
    print("ALGORITHM EXECUTOR TEST")
    print("=" * 50)
    
    # Test case
    test_inputs = {
        'data': [1, 2, 3],
        'max_iterations': 20,
        'tolerance': 1e-6
    }
    
    print(f"Executing TestAlgorithm with inputs: {test_inputs}")
    
    result = executor.execute_algorithm(
        sample_algorithm, 
        'TestAlgorithm',
        test_inputs
    )
    
    print(f"\nResults:")
    print(f"Success: {result.success}")
    print(f"Result: {result.result}")
    print(f"Execution time: {result.execution_time:.4f}s")
    print(f"Converged: {result.converged}")
    print(f"Iterations: {result.iterations}")
    
    if result.error:
        print(f"Error: {result.error}")
    
    # Test benchmark
    print(f"\n" + "=" * 50)
    print("BENCHMARK TEST")
    print("=" * 50)
    
    test_cases = [
        {'data': [1], 'max_iterations': 10, 'tolerance': 0.01},
        {'data': [1, 2], 'max_iterations': 15, 'tolerance': 0.001},
        {'data': [1, 2, 3], 'max_iterations': 20, 'tolerance': 0.0001}
    ]
    
    benchmark_results = executor.benchmark_algorithm(
        sample_algorithm, 'TestAlgorithm', test_cases
    )
    
    print(f"Benchmark Results:")
    print(f"Total test cases: {benchmark_results['total_test_cases']}")
    print(f"Success rate: {benchmark_results['success_rate']:.1%}")
    print(f"Average execution time: {benchmark_results['average_execution_time']:.4f}s")


if __name__ == "__main__":
    test_algorithm_executor()