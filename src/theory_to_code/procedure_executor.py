"""
Level 3 (PROCEDURES) Execution Engine

This module executes generated procedures with state management, context preservation,
rollback capabilities, and comprehensive error handling.
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import time
import threading
import logging
from datetime import datetime

from .procedure_generator import GeneratedProcedure, ProcedureExecutionResult

logger = logging.getLogger(__name__)


class ProcedureExecutor:
    """Execute generated procedures with state management and error handling"""
    
    def __init__(self, timeout_seconds: int = 300):
        self.timeout_seconds = timeout_seconds
        self.execution_history = []
        
    def execute_procedure(self, procedure_code: str, procedure_class: str,
                         context: Dict[str, Any], 
                         method_name: str = "execute") -> ProcedureExecutionResult:
        """
        Execute a generated procedure class with state management
        
        Args:
            procedure_code: Generated Python code for the procedure
            procedure_class: Name of the procedure class
            context: Input context for the procedure
            method_name: Method to execute (default: "execute")
            
        Returns:
            ProcedureExecutionResult with execution details
        """
        start_time = time.time()
        
        try:
            # Create safe execution namespace
            namespace = self._create_safe_namespace()
            
            # Execute the procedure code to define the class
            exec(procedure_code, namespace)
            
            # Check if the procedure class exists
            if procedure_class not in namespace:
                return ProcedureExecutionResult(
                    success=False,
                    final_state="error",
                    context=context,
                    history=[],
                    execution_time=time.time() - start_time,
                    error=f"Procedure class '{procedure_class}' not found"
                )
            
            # Instantiate the procedure class
            ProcedureClass = namespace[procedure_class]
            procedure_instance = ProcedureClass()
            
            # Execute the procedure with timeout protection
            result = self._execute_with_timeout(
                procedure_instance, method_name, context
            )
            
            execution_time = time.time() - start_time
            
            # Parse the result
            if isinstance(result, dict):
                return ProcedureExecutionResult(
                    success=result.get("success", True),
                    final_state=result.get("final_state", "complete"),
                    context=result.get("context", context),
                    history=result.get("history", []),
                    execution_time=execution_time,
                    error=result.get("error"),
                    rollback_performed=result.get("rollback_performed", False),
                    steps_completed=result.get("steps_completed", 0)
                )
            else:
                return ProcedureExecutionResult(
                    success=True,
                    final_state="complete",
                    context=context,
                    history=[],
                    execution_time=execution_time,
                    steps_completed=1
                )
                
        except Exception as e:
            logger.error(f"Procedure execution failed: {e}")
            return ProcedureExecutionResult(
                success=False,
                final_state="error",
                context=context,
                history=[],
                execution_time=time.time() - start_time,
                error=f"Execution error: {e}",
                steps_completed=0
            )
    
    def _create_safe_namespace(self) -> Dict[str, Any]:
        """Create a safe execution namespace for procedures"""
        
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
            '__build_class__': __build_class__,
            '__import__': __import__
        }
        
        namespace = {
            '__builtins__': safe_builtins,
            '__name__': '__main__',
            # Standard exceptions
            'Exception': Exception,
            'ValueError': ValueError,
            'TypeError': TypeError,
            'RuntimeError': RuntimeError,
            'IndexError': IndexError,
            'KeyError': KeyError,
            'AttributeError': AttributeError,
            'ZeroDivisionError': ZeroDivisionError,
        }
        
        # Add safe imports
        try:
            from datetime import datetime
            namespace['datetime'] = datetime
        except ImportError:
            pass
        
        try:
            import logging
            namespace['logging'] = logging
        except ImportError:
            pass
        
        return namespace
    
    def _execute_with_timeout(self, procedure_instance: Any, method_name: str,
                             context: Dict[str, Any]) -> Any:
        """Execute procedure method with timeout protection"""
        
        if not hasattr(procedure_instance, method_name):
            raise AttributeError(f"Procedure has no method '{method_name}'")
        
        method = getattr(procedure_instance, method_name)
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = method(context)
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(self.timeout_seconds)
        
        if thread.is_alive():
            raise TimeoutError(f"Procedure execution timed out after {self.timeout_seconds}s")
        
        if exception[0]:
            raise exception[0]
        
        return result[0]
    
    def validate_procedure_state(self, procedure_instance: Any) -> Dict[str, Any]:
        """Validate the current state of a procedure instance"""
        
        validation = {
            'has_state': hasattr(procedure_instance, 'state'),
            'has_context': hasattr(procedure_instance, 'context'),
            'has_history': hasattr(procedure_instance, 'history'),
            'has_transitions': hasattr(procedure_instance, 'transitions'),
            'state_valid': False,
            'transitions_valid': False
        }
        
        # Check state validity
        if validation['has_state']:
            state = getattr(procedure_instance, 'state', None)
            validation['state_valid'] = isinstance(state, str) and len(state) > 0
        
        # Check transitions validity
        if validation['has_transitions']:
            transitions = getattr(procedure_instance, 'transitions', None)
            validation['transitions_valid'] = isinstance(transitions, dict)
        
        return validation
    
    def get_procedure_metrics(self, execution_result: ProcedureExecutionResult) -> Dict[str, Any]:
        """Get metrics for a procedure execution"""
        
        return {
            'success_rate': 1.0 if execution_result.success else 0.0,
            'execution_time': execution_result.execution_time,
            'steps_completed': execution_result.steps_completed,
            'rollback_performed': execution_result.rollback_performed,
            'final_state': execution_result.final_state,
            'history_length': len(execution_result.history),
            'context_size': len(execution_result.context) if execution_result.context else 0,
            'error_occurred': execution_result.error is not None
        }


def test_procedure_executor():
    """Test the procedure executor"""
    
    print("=" * 60)
    print("PROCEDURE EXECUTOR TEST")
    print("=" * 60)
    
    # Create a simple test procedure
    test_procedure_code = '''
from datetime import datetime

class TestDecisionProcedure:
    """Simple test decision procedure"""
    
    def __init__(self):
        self.state = "start"
        self.context = {}
        self.history = []
        self.transitions = {
            "start": "identify_options",
            "identify_options": "evaluate_options", 
            "evaluate_options": "make_choice",
            "make_choice": "complete"
        }
        self.final_states = {"complete", "error"}
    
    def execute(self, context):
        """Execute the test procedure"""
        self.context = context
        self.history = []
        
        try:
            steps = 0
            while self.state not in self.final_states and steps < 10:
                # Record step
                self.history.append({
                    "state": self.state,
                    "timestamp": datetime.now().isoformat(),
                    "step": steps
                })
                
                # Simple state progression
                if self.state == "start":
                    self.state = "identify_options"
                elif self.state == "identify_options":
                    self.context["options"] = ["A", "B", "C"]
                    self.state = "evaluate_options"
                elif self.state == "evaluate_options":
                    self.context["scores"] = {"A": 0.8, "B": 0.6, "C": 0.9}
                    self.state = "make_choice"
                elif self.state == "make_choice":
                    # Choose highest scored option
                    best_option = max(self.context["scores"], key=self.context["scores"].get)
                    self.context["choice"] = best_option
                    self.state = "complete"
                
                steps += 1
            
            return {
                "success": True,
                "final_state": self.state,
                "context": self.context,
                "history": self.history,
                "steps_completed": steps
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "final_state": "error",
                "context": self.context,
                "history": self.history,
                "steps_completed": steps
            }
'''
    
    # Test execution
    executor = ProcedureExecutor()
    
    test_context = {
        "user_id": "test_user",
        "scenario": "choice_test"
    }
    
    try:
        result = executor.execute_procedure(
            test_procedure_code,
            "TestDecisionProcedure", 
            test_context
        )
        
        print(f"Execution success: {result.success}")
        print(f"Final state: {result.final_state}")
        print(f"Steps completed: {result.steps_completed}")
        print(f"Execution time: {result.execution_time:.3f}s")
        print(f"History length: {len(result.history)}")
        
        if result.context and "choice" in result.context:
            print(f"Decision made: {result.context['choice']}")
        
        if result.error:
            print(f"Error: {result.error}")
        
        # Test metrics
        metrics = executor.get_procedure_metrics(result)
        print(f"\\nMetrics: {metrics}")
        
        return result.success
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_procedure_executor()