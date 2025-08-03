"""
Data Flow Validator

Validates data flow through tools and ensures input/output compliance.
"""

from typing import Dict, List, Any, Tuple

try:
    from ..data_models import (
        BaseObject, Document, Chunk, Entity, Relationship, 
        WorkflowState, TextForLLMProcessing,
        ObjectType, QualityTier
    )
except ImportError:
    # For standalone execution
    from data_models import (
        BaseObject, Document, Chunk, Entity, Relationship, 
        WorkflowState, TextForLLMProcessing,
        ObjectType, QualityTier
    )


class DataFlowValidator:
    """Validates data flow through tools"""
    
    def __init__(self):
        # Data type mapping
        self.data_type_mapping = {
            "Document": Document,
            "Chunk": Chunk,
            "Entity": Entity,
            "Relationship": Relationship,
            "WorkflowState": WorkflowState,
            "TextForLLMProcessing": TextForLLMProcessing
        }
    
    def validate_data_flow(self, tool_instance: Any, contract: Dict[str, Any], 
                          test_input: Dict[str, Any]) -> Tuple[bool, List[str], Any]:
        """
        Validate data flow through a tool using test input
        
        Args:
            tool_instance: Tool to test
            contract: Tool contract
            test_input: Test input data
            
        Returns:
            Tuple of (success, errors, output)
        """
        errors = []
        tool_id = contract.get('tool_id', 'UNKNOWN')
        
        try:
            # Validate input against contract
            input_errors = self._validate_input_data(test_input, contract)
            if input_errors:
                errors.extend(input_errors)
                return False, errors, None
            
            # Execute tool
            if hasattr(tool_instance, 'execute'):
                output = tool_instance.execute(**test_input)
            else:
                errors.append(f"Tool {tool_id} has no execute method")
                return False, errors, None
            
            # Validate output against contract
            output_errors = self._validate_output_data(output, contract)
            if output_errors:
                errors.extend(output_errors)
                return False, errors, output
            
            return True, [], output
            
        except Exception as e:
            errors.append(f"Tool {tool_id} execution failed: {str(e)}")
            return False, errors, None
    
    def _validate_input_data(self, input_data: Dict[str, Any], contract: Dict[str, Any]) -> List[str]:
        """Validate input data against contract requirements"""
        errors = []
        input_contract = contract.get('input_contract', {})
        required_data_types = input_contract.get('required_data_types', [])
        
        # Check required data types are present
        for data_type_spec in required_data_types:
            data_type = data_type_spec['type']
            required_attrs = data_type_spec.get('attributes', [])
            
            # Look for data of this type in input
            type_found = False
            for key, value in input_data.items():
                if self._is_data_type(value, data_type):
                    type_found = True
                    # Validate required attributes
                    attr_errors = self._validate_object_attributes(value, required_attrs, data_type)
                    errors.extend(attr_errors)
                    break
            
            if not type_found:
                errors.append(f"Required data type {data_type} not found in input")
        
        return errors
    
    def _validate_output_data(self, output_data: Any, contract: Dict[str, Any]) -> List[str]:
        """Validate output data against contract specifications"""
        errors = []
        output_contract = contract.get('output_contract', {})
        produced_data_types = output_contract.get('produced_data_types', [])
        
        # Handle different output formats
        if isinstance(output_data, dict):
            output_items = output_data.values()
        elif isinstance(output_data, (list, tuple)):
            output_items = output_data
        else:
            output_items = [output_data]
        
        # Check each produced data type
        for data_type_spec in produced_data_types:
            data_type = data_type_spec['type']
            required_attrs = data_type_spec.get('attributes', [])
            validation_rules = data_type_spec.get('validation', {})
            
            # Look for objects of this type in output
            type_found = False
            for item in output_items:
                if self._is_data_type(item, data_type):
                    type_found = True
                    # Validate attributes
                    attr_errors = self._validate_object_attributes(item, required_attrs, data_type)
                    errors.extend(attr_errors)
                    break
            
            if not type_found:
                errors.append(f"Expected data type {data_type} not found in output")
        
        return errors
    
    def _is_data_type(self, obj: Any, data_type: str) -> bool:
        """Check if an object is of the specified data type"""
        expected_class = self.data_type_mapping.get(data_type)
        if expected_class is None:
            return False
        
        # Check if it's an instance of the expected class
        if isinstance(obj, expected_class):
            return True
        
        # Check if it's a dict with correct object_type
        if isinstance(obj, dict):
            obj_type = obj.get('object_type')
            if obj_type == data_type or (hasattr(ObjectType, data_type.upper()) and obj_type == getattr(ObjectType, data_type.upper())):
                return True
        
        return False
    
    def _validate_object_attributes(self, obj: Any, required_attrs: List[str], data_type: str) -> List[str]:
        """Validate that an object has required attributes"""
        errors = []
        
        for attr in required_attrs:
            if isinstance(obj, dict):
                if attr not in obj:
                    errors.append(f"{data_type} object missing required attribute: {attr}")
            elif hasattr(obj, attr):
                if getattr(obj, attr) is None:
                    errors.append(f"{data_type} object has null value for required attribute: {attr}")
            else:
                errors.append(f"{data_type} object missing required attribute: {attr}")
        
        return errors
    
    def validate_data_transformation(self, input_data: Any, output_data: Any, 
                                   transformation_rules: Dict[str, Any]) -> List[str]:
        """Validate that data transformation follows specified rules"""
        errors = []
        
        # Check if required transformations occurred
        required_transformations = transformation_rules.get('required', [])
        for transformation in required_transformations:
            transform_type = transformation.get('type')
            
            if transform_type == 'entity_extraction':
                # Check if entities were extracted
                if not self._has_entities(output_data):
                    errors.append("Required entity extraction did not occur")
            
            elif transform_type == 'relationship_creation':
                # Check if relationships were created
                if not self._has_relationships(output_data):
                    errors.append("Required relationship creation did not occur")
            
            elif transform_type == 'content_chunking':
                # Check if content was chunked
                if not self._has_chunks(output_data):
                    errors.append("Required content chunking did not occur")
        
        # Check prohibited transformations
        prohibited_transformations = transformation_rules.get('prohibited', [])
        for transformation in prohibited_transformations:
            transform_type = transformation.get('type')
            
            if transform_type == 'data_loss' and self._has_data_loss(input_data, output_data):
                errors.append("Prohibited data loss detected")
        
        return errors
    
    def _has_entities(self, data: Any) -> bool:
        """Check if data contains entities"""
        if isinstance(data, dict):
            return any(self._is_data_type(value, "Entity") for value in data.values())
        elif isinstance(data, (list, tuple)):
            return any(self._is_data_type(item, "Entity") for item in data)
        return self._is_data_type(data, "Entity")
    
    def _has_relationships(self, data: Any) -> bool:
        """Check if data contains relationships"""
        if isinstance(data, dict):
            return any(self._is_data_type(value, "Relationship") for value in data.values())
        elif isinstance(data, (list, tuple)):
            return any(self._is_data_type(item, "Relationship") for item in data)
        return self._is_data_type(data, "Relationship")
    
    def _has_chunks(self, data: Any) -> bool:
        """Check if data contains chunks"""
        if isinstance(data, dict):
            return any(self._is_data_type(value, "Chunk") for value in data.values())
        elif isinstance(data, (list, tuple)):
            return any(self._is_data_type(item, "Chunk") for item in data)
        return self._is_data_type(data, "Chunk")
    
    def _has_data_loss(self, input_data: Any, output_data: Any) -> bool:
        """Check if significant data loss occurred during transformation"""
        # Simple heuristic: compare content lengths
        input_content = self._extract_content(input_data)
        output_content = self._extract_content(output_data)
        
        if input_content and output_content:
            loss_ratio = (len(input_content) - len(output_content)) / len(input_content)
            return loss_ratio > 0.5  # More than 50% content loss
        
        return False
    
    def _extract_content(self, data: Any) -> str:
        """Extract textual content from data for comparison"""
        if isinstance(data, str):
            return data
        elif isinstance(data, dict):
            content_fields = ['content', 'text', 'description', 'canonical_name']
            for field in content_fields:
                if field in data and isinstance(data[field], str):
                    return data[field]
        elif hasattr(data, 'content'):
            return str(data.content)
        
        return ""
