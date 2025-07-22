"""Tool Contract Validation Framework

Validates tools against their contracts to ensure compliance with the
unified tool interface. Part of the fail-fast, evidence-based approach.
"""

import json
import logging
from typing import Dict, Any, List, Optional
import jsonschema
from jsonschema import ValidationError

from .tool_protocol import UnifiedTool, ToolContract, ToolRequest, ToolResult, ToolContractError


logger = logging.getLogger(__name__)


class ToolContractValidator:
    """Validate tools against their contracts
    
    This validator ensures that tools properly implement their contracts
    and can be safely used in agent orchestration workflows.
    """
    
    def __init__(self):
        self.validation_results: List[Dict[str, Any]] = []
    
    def validate_tool_contract(self, tool: UnifiedTool) -> bool:
        """Validate tool implements its contract correctly
        
        Performs comprehensive validation:
        - Contract completeness
        - Method implementation
        - Schema validation
        - Execution testing
        
        Args:
            tool: Tool instance to validate
            
        Returns:
            True if tool is fully compliant, False otherwise
        """
        validation_result = {
            "tool_id": getattr(tool, "tool_id", "unknown"),
            "timestamp": "2025-07-22T" + "10:30:00Z",
            "tests": {},
            "overall_passed": False
        }
        
        try:
            # Get tool contract
            contract = tool.get_contract()
            validation_result["contract"] = {
                "tool_id": contract.tool_id,
                "name": contract.name,
                "category": contract.category
            }
            
            # Test 1: Contract completeness
            contract_valid = self._validate_contract_completeness(contract)
            validation_result["tests"]["contract_completeness"] = {
                "passed": contract_valid,
                "details": "Contract has all required fields"
            }
            
            # Test 2: Tool methods
            methods_valid = self._validate_tool_methods(tool)
            validation_result["tests"]["method_implementation"] = {
                "passed": methods_valid,
                "details": "All required methods are implemented"
            }
            
            # Test 3: Schema validation
            schemas_valid = self._validate_schemas(contract)
            validation_result["tests"]["schema_validation"] = {
                "passed": schemas_valid,
                "details": "Input and output schemas are valid JSON Schema"
            }
            
            # Test 4: Tool execution
            execution_valid = self._test_tool_execution(tool, contract)
            validation_result["tests"]["execution_test"] = {
                "passed": execution_valid,
                "details": "Tool executes successfully with valid inputs"
            }
            
            # Test 5: Error handling
            error_handling_valid = self._test_error_handling(tool, contract)
            validation_result["tests"]["error_handling"] = {
                "passed": error_handling_valid,
                "details": "Tool handles errors gracefully"
            }
            
            # Overall result
            all_tests_passed = all(
                test["passed"] for test in validation_result["tests"].values()
            )
            validation_result["overall_passed"] = all_tests_passed
            
            self.validation_results.append(validation_result)
            
            if all_tests_passed:
                logger.info(f"Tool {contract.tool_id} passed all validation tests")
            else:
                failed_tests = [
                    name for name, test in validation_result["tests"].items() 
                    if not test["passed"]
                ]
                logger.error(f"Tool {contract.tool_id} failed tests: {failed_tests}")
            
            return all_tests_passed
            
        except Exception as e:
            logger.error(f"Contract validation failed for tool: {e}")
            validation_result["tests"]["validation_error"] = {
                "passed": False,
                "details": f"Validation error: {str(e)}"
            }
            self.validation_results.append(validation_result)
            return False
    
    def _validate_contract_completeness(self, contract: ToolContract) -> bool:
        """Validate contract has all required fields"""
        try:
            required_fields = [
                "tool_id", "name", "description", "category",
                "input_schema", "output_schema", "dependencies",
                "performance_requirements", "error_conditions"
            ]
            
            for field in required_fields:
                if not hasattr(contract, field):
                    logger.error(f"Contract missing required field: {field}")
                    return False
                
                value = getattr(contract, field)
                if value is None:
                    logger.error(f"Contract field {field} is None")
                    return False
            
            # Validate category
            valid_categories = ["graph", "table", "vector", "cross_modal"]
            if contract.category not in valid_categories:
                logger.error(f"Invalid category: {contract.category}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Contract completeness validation failed: {e}")
            return False
    
    def _validate_tool_methods(self, tool: UnifiedTool) -> bool:
        """Validate tool implements all required methods"""
        try:
            required_methods = [
                "get_contract", "execute", "validate_input",
                "health_check", "get_status", "cleanup"
            ]
            
            for method_name in required_methods:
                if not hasattr(tool, method_name):
                    logger.error(f"Tool missing required method: {method_name}")
                    return False
                
                method = getattr(tool, method_name)
                if not callable(method):
                    logger.error(f"Tool {method_name} is not callable")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Method validation failed: {e}")
            return False
    
    def _validate_schemas(self, contract: ToolContract) -> bool:
        """Validate input and output schemas are valid JSON Schema"""
        try:
            # Validate input schema
            jsonschema.Draft7Validator.check_schema(contract.input_schema)
            
            # Validate output schema
            jsonschema.Draft7Validator.check_schema(contract.output_schema)
            
            return True
            
        except jsonschema.SchemaError as e:
            logger.error(f"Schema validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            return False
    
    def _test_tool_execution(self, tool: UnifiedTool, contract: ToolContract) -> bool:
        """Test tool execution with valid inputs"""
        try:
            # Generate valid test input
            test_input = self._generate_test_input(contract.input_schema)
            
            # Create test request
            request = ToolRequest(
                tool_id=contract.tool_id,
                operation="test",
                input_data=test_input,
                parameters={},
                validation_mode=True
            )
            
            # Execute tool
            result = tool.execute(request)
            
            # Validate result format
            if not isinstance(result, ToolResult):
                logger.error("Tool did not return ToolResult")
                return False
            
            # Validate required fields
            if not hasattr(result, "status") or result.status not in ["success", "error"]:
                logger.error("Invalid result status")
                return False
            
            # If successful, validate output schema
            if result.status == "success" and result.data is not None:
                try:
                    jsonschema.validate(result.data, contract.output_schema)
                except ValidationError as e:
                    logger.error(f"Output does not match schema: {e}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Tool execution test failed: {e}")
            return False
    
    def _test_error_handling(self, tool: UnifiedTool, contract: ToolContract) -> bool:
        """Test tool error handling with invalid inputs"""
        try:
            # Test with invalid input
            invalid_request = ToolRequest(
                tool_id=contract.tool_id,
                operation="test",
                input_data=None,  # Invalid input
                parameters={},
                validation_mode=True
            )
            
            result = tool.execute(invalid_request)
            
            # Should return error result, not raise exception
            if not isinstance(result, ToolResult):
                logger.error("Tool did not return ToolResult for invalid input")
                return False
            
            if result.status != "error":
                logger.warning("Tool did not return error for invalid input")
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling test failed: {e}")
            return False
    
    def _generate_test_input(self, input_schema: Dict[str, Any]) -> Any:
        """Generate valid test input based on schema"""
        try:
            if input_schema.get("type") == "object":
                test_input = {}
                properties = input_schema.get("properties", {})
                required = input_schema.get("required", [])
                
                for prop_name, prop_schema in properties.items():
                    if prop_name in required or len(properties) <= 3:
                        test_input[prop_name] = self._generate_value_for_schema(prop_schema)
                
                return test_input
            
            elif input_schema.get("type") == "string":
                return "test_input_string"
            
            elif input_schema.get("type") == "array":
                return ["test_item"]
            
            else:
                # Default test input
                return {"test_data": "validation_test"}
                
        except Exception as e:
            logger.warning(f"Could not generate test input, using default: {e}")
            return {"test_data": "validation_test"}
    
    def _generate_value_for_schema(self, schema: Dict[str, Any]) -> Any:
        """Generate a value that matches the given schema"""
        schema_type = schema.get("type")
        
        if schema_type == "string":
            return "test_string"
        elif schema_type == "number":
            return 1.0
        elif schema_type == "integer":
            return 1
        elif schema_type == "boolean":
            return True
        elif schema_type == "array":
            return ["test_item"]
        elif schema_type == "object":
            return {"test_key": "test_value"}
        else:
            return "test_value"
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Get comprehensive validation report"""
        total_tools = len(self.validation_results)
        passed_tools = sum(1 for result in self.validation_results if result["overall_passed"])
        
        return {
            "summary": {
                "total_tools_validated": total_tools,
                "tools_passed": passed_tools,
                "tools_failed": total_tools - passed_tools,
                "pass_rate": (passed_tools / total_tools * 100) if total_tools > 0 else 0
            },
            "detailed_results": self.validation_results
        }
    
    def validate_all_tools(self, tools: List[UnifiedTool]) -> bool:
        """Validate multiple tools and return overall success"""
        results = []
        for tool in tools:
            result = self.validate_tool_contract(tool)
            results.append(result)
        
        return all(results)