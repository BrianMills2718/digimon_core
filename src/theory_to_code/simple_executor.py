#!/usr/bin/env python3
"""
Simplified dynamic executor that handles imports properly.
Uses threading for timeout instead of subprocess for simplicity.
"""

import ast
import threading
import queue
import time
import traceback
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of code execution"""
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    timeout: bool = False


class SimpleExecutor:
    """Executes dynamically generated code with proper import handling"""
    
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
    
    def execute_module_function(self, module_code: str, function_name: str, 
                               inputs: Dict[str, Any]) -> ExecutionResult:
        """Execute a function from a module string"""
        
        start_time = time.time()
        
        # First, handle imports by executing them separately
        prepared_code = self._prepare_code(module_code)
        
        # Create execution namespace with safe built-ins and imports
        namespace = self._create_namespace()
        
        # Use a queue to get results from thread
        result_queue = queue.Queue()
        
        def run_code():
            try:
                # Execute the prepared code
                exec(prepared_code, namespace)
                
                # Find and call the function
                if function_name not in namespace:
                    result_queue.put(ExecutionResult(
                        success=False,
                        result=None,
                        error=f"Function '{function_name}' not found in module"
                    ))
                    return
                
                func = namespace[function_name]
                result = func(**inputs)
                
                result_queue.put(ExecutionResult(
                    success=True,
                    result=result,
                    error=None,
                    execution_time=time.time() - start_time
                ))
                
            except Exception as e:
                result_queue.put(ExecutionResult(
                    success=False,
                    result=None,
                    error=f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}",
                    execution_time=time.time() - start_time
                ))
        
        # Run in thread with timeout
        thread = threading.Thread(target=run_code)
        thread.daemon = True
        thread.start()
        thread.join(timeout=self.timeout)
        
        if thread.is_alive():
            # Timeout occurred
            return ExecutionResult(
                success=False,
                result=None,
                error=f"Execution timed out after {self.timeout} seconds",
                timeout=True,
                execution_time=self.timeout
            )
        
        # Get result from queue
        try:
            return result_queue.get_nowait()
        except queue.Empty:
            return ExecutionResult(
                success=False,
                result=None,
                error="No result returned from execution",
                execution_time=time.time() - start_time
            )
    
    def _prepare_code(self, module_code: str) -> str:
        """Prepare code by handling imports properly"""
        
        lines = module_code.split('\n')
        prepared_lines = []
        import_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Collect imports separately
            if stripped.startswith(('import ', 'from ')):
                # Skip duplicate imports
                if stripped not in import_lines:
                    import_lines.append(stripped)
            elif stripped and not stripped.startswith('#'):
                # Non-import, non-comment line
                prepared_lines.append(line)
            elif not stripped or stripped.startswith('#'):
                # Keep empty lines and comments for structure
                prepared_lines.append(line)
        
        # Combine with imports first
        return '\n'.join(import_lines + [''] + prepared_lines)
    
    def _create_namespace(self) -> Dict[str, Any]:
        """Create a namespace with necessary imports and safe built-ins"""
        
        # Import commonly needed modules
        import math
        import typing
        from typing import List, Dict, Any, Optional, Union, Tuple
        
        # Try to import optional modules
        try:
            import numpy as np
            has_numpy = True
        except ImportError:
            has_numpy = False
            np = None
        
        # Create namespace with imports
        namespace = {
            # Built-ins
            '__builtins__': {
                'abs': abs, 'all': all, 'any': any, 'bool': bool,
                'dict': dict, 'enumerate': enumerate, 'float': float,
                'int': int, 'len': len, 'list': list, 'max': max,
                'min': min, 'pow': pow, 'range': range, 'round': round,
                'set': set, 'sorted': sorted, 'str': str, 'sum': sum,
                'tuple': tuple, 'type': type, 'zip': zip,
                'isinstance': isinstance, 'hasattr': hasattr, 'getattr': getattr,
                'True': True, 'False': False, 'None': None,
                '__import__': __import__
            },
            # Math module
            'math': math,
            # Typing support
            'typing': typing,
            'List': List,
            'Dict': Dict,
            'Any': Any,
            'Optional': Optional,
            'Union': Union,
            'Tuple': Tuple,
        }
        
        # Add numpy if available
        if has_numpy:
            namespace['numpy'] = np
            namespace['np'] = np
        
        return namespace
    
    def validate_code_safety(self, code: str) -> Tuple[bool, Optional[str]]:
        """Basic safety validation"""
        
        # Check for dangerous imports
        dangerous_modules = ['os', 'subprocess', 'sys', 'shutil', 'socket']
        for module in dangerous_modules:
            if f'import {module}' in code or f'from {module}' in code:
                return False, f"Import of '{module}' not allowed"
        
        # Check for dangerous functions
        dangerous_patterns = ['eval(', 'exec(', 'compile(', '__import__', 'open(']
        for pattern in dangerous_patterns:
            if pattern in code and pattern != '__import__':  # Allow __import__ in namespace
                return False, f"Use of '{pattern}' not allowed"
        
        # Try to parse the code
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error: {e}"


def test_simple_executor():
    """Test the simple executor with generated code"""
    
    # Example generated module code
    module_code = '''
"""Auto-generated module for Prospect Theory"""

# Imports
from typing import List
import math

# value_function
def calculate_value(x: float, reference_point: float = 0,
                   alpha: float = 0.88, beta: float = 0.88,
                   lambda_: float = 2.25) -> float:
    """Calculate subjective value using Prospect Theory"""
    relative_outcome = x - reference_point
    
    if relative_outcome >= 0:  # Gain
        return relative_outcome ** alpha
    else:  # Loss
        return -lambda_ * (abs(relative_outcome) ** beta)

# prospect_evaluation  
def evaluate_prospect(outcomes: List[float], probabilities: List[float],
                     reference_point: float = 0) -> float:
    """Evaluate complete prospect value"""
    
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
        subj_value = calculate_value(outcome, reference_point)
        total_value += weighted_prob * subj_value
    
    return total_value
'''
    
    executor = SimpleExecutor(timeout=2)
    
    print("Testing Simple Executor")
    print("=" * 60)
    
    # Test 1: Value function
    print("\n1. Testing value_function:")
    result = executor.execute_module_function(
        module_code, 
        'calculate_value',
        {'x': 100, 'reference_point': 0}
    )
    print(f"   Success: {result.success}")
    if result.success:
        print(f"   Result: {result.result:.2f}")
    else:
        print(f"   Error: {result.error}")
    
    # Test 2: Prospect evaluation
    print("\n2. Testing prospect_evaluation:")
    result = executor.execute_module_function(
        module_code,
        'evaluate_prospect',
        {
            'outcomes': [100, -50],
            'probabilities': [0.7, 0.3],
            'reference_point': 0
        }
    )
    print(f"   Success: {result.success}")
    if result.success:
        print(f"   Result: {result.result:.2f}")
        print(f"   Execution time: {result.execution_time:.3f}s")
    else:
        print(f"   Error: {result.error}")
    
    # Test 3: Safety validation
    print("\n3. Testing safety validation:")
    dangerous_code = '''
import os
def malicious():
    return os.system("echo 'bad'")
'''
    
    is_safe, error = executor.validate_code_safety(dangerous_code)
    print(f"   Dangerous code blocked: {not is_safe}")
    print(f"   Reason: {error}")
    
    print("\n✅ Simple executor test complete!")


if __name__ == "__main__":
    test_simple_executor()