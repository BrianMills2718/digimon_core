"""
Interface Validator

Validates that tool implementations match their declared interfaces.
"""

import inspect
from typing import Dict, List, Any


class InterfaceValidator:
    """Validates tool interface compliance with contracts"""
    
    def validate_tool_interface(self, tool_instance: Any, contract: Dict[str, Any]) -> List[str]:
        """
        Validate that a tool instance matches its contract interface
        
        Args:
            tool_instance: Tool instance to validate
            contract: Tool contract to validate against
            
        Returns:
            List of validation errors
        """
        errors = []
        tool_id = contract.get('tool_id', 'UNKNOWN')
        
        # Check if tool has required methods
        if hasattr(tool_instance, 'execute'):
            # Check execute method signature
            execute_errors = self._validate_execute_method(tool_instance, contract)
            errors.extend(execute_errors)
        else:
            errors.append(f"Tool {tool_id} missing required 'execute' method")
        
        # Check for other standard methods
        standard_methods = ['validate_input', 'get_info']
        for method_name in standard_methods:
            if not hasattr(tool_instance, method_name):
                errors.append(f"Tool {tool_id} missing recommended method: {method_name}")
        
        return errors
    
    def _validate_execute_method(self, tool_instance: Any, contract: Dict[str, Any]) -> List[str]:
        """Validate the execute method signature and behavior"""
        errors = []
        tool_id = contract.get('tool_id', 'UNKNOWN')
        
        execute_method = getattr(tool_instance, 'execute')
        if not callable(execute_method):
            errors.append(f"Tool {tool_id} 'execute' is not callable")
            return errors
        
        # Check method signature
        sig = inspect.signature(execute_method)
        params = list(sig.parameters.keys())
        
        # Remove 'self' if present
        if params and params[0] == 'self':
            params = params[1:]
        
        # Basic signature validation
        if not params:
            errors.append(f"Tool {tool_id} execute method has no parameters")
        
        # Validate parameter types if specified in contract
        expected_params = contract.get('interface', {}).get('execute_parameters', [])
        for expected_param in expected_params:
            param_name = expected_param.get('name')
            param_type = expected_param.get('type')
            required = expected_param.get('required', True)
            
            if param_name not in params:
                if required:
                    errors.append(f"Tool {tool_id} execute method missing required parameter: {param_name}")
            else:
                # Check parameter annotation if available
                param_obj = sig.parameters.get(param_name)
                if param_obj and param_obj.annotation != inspect.Parameter.empty:
                    # Could add type checking here if needed
                    pass
        
        return errors
    
    def validate_method_signatures(self, tool_instance: Any, contract: Dict[str, Any]) -> List[str]:
        """Validate all method signatures against contract specifications"""
        errors = []
        tool_id = contract.get('tool_id', 'UNKNOWN')
        
        interface_spec = contract.get('interface', {})
        methods_spec = interface_spec.get('methods', [])
        
        for method_spec in methods_spec:
            method_name = method_spec.get('name')
            required = method_spec.get('required', True)
            
            if not hasattr(tool_instance, method_name):
                if required:
                    errors.append(f"Tool {tool_id} missing required method: {method_name}")
                continue
            
            method = getattr(tool_instance, method_name)
            if not callable(method):
                errors.append(f"Tool {tool_id} method '{method_name}' is not callable")
                continue
            
            # Validate method signature
            sig = inspect.signature(method)
            params = list(sig.parameters.keys())
            
            # Remove 'self' if present
            if params and params[0] == 'self':
                params = params[1:]
            
            # Check expected parameters
            expected_params = method_spec.get('parameters', [])
            for expected_param in expected_params:
                param_name = expected_param.get('name')
                param_required = expected_param.get('required', True)
                
                if param_name not in params and param_required:
                    errors.append(f"Tool {tool_id} method '{method_name}' missing required parameter: {param_name}")
        
        return errors
    
    def validate_return_types(self, tool_instance: Any, contract: Dict[str, Any]) -> List[str]:
        """Validate method return type annotations if available"""
        errors = []
        tool_id = contract.get('tool_id', 'UNKNOWN')
        
        interface_spec = contract.get('interface', {})
        methods_spec = interface_spec.get('methods', [])
        
        for method_spec in methods_spec:
            method_name = method_spec.get('name')
            expected_return_type = method_spec.get('return_type')
            
            if not expected_return_type:
                continue
            
            if not hasattr(tool_instance, method_name):
                continue  # Already handled in signature validation
            
            method = getattr(tool_instance, method_name)
            sig = inspect.signature(method)
            
            # Check return annotation
            if sig.return_annotation != inspect.Signature.empty:
                # Could add more sophisticated type checking here
                pass
        
        return errors
    
    def check_class_inheritance(self, tool_instance: Any, contract: Dict[str, Any]) -> List[str]:
        """Check if tool inherits from expected base classes"""
        errors = []
        tool_id = contract.get('tool_id', 'UNKNOWN')
        
        expected_base_classes = contract.get('interface', {}).get('base_classes', [])
        
        for base_class_name in expected_base_classes:
            # This would require importing the actual base class
            # For now, just check if it's in the MRO as a string
            class_names = [cls.__name__ for cls in tool_instance.__class__.__mro__]
            if base_class_name not in class_names:
                errors.append(f"Tool {tool_id} does not inherit from expected base class: {base_class_name}")
        
        return errors
