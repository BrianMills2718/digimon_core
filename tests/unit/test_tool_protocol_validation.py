"""Test enhanced tool protocol validation

Tests the comprehensive input validation functionality added to tool protocol.
"""

import pytest
import sys
import os
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.tool_protocol import Tool, ToolValidationResult
from src.core.evidence_logger import EvidenceLogger


class TestToolProtocolValidation:
    """Test the enhanced tool protocol validation"""
    
    def test_comprehensive_validation_security(self):
        """Test security validation catches malicious inputs"""
        evidence_logger = EvidenceLogger()
        
        # Create a test tool implementation
        class TestTool(Tool):
            def execute(self, input_data: Dict[str, Any], context=None) -> Dict[str, Any]:
                return {"status": "success"}
            
            def get_tool_info(self) -> Dict[str, Any]:
                return {
                    "name": "TestTool",
                    "version": "1.0",
                    "description": "Test tool for validation"
                }
            
            def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
                # Basic validation
                errors = []
                if "test_field" not in input_data:
                    errors.append("test_field is required")
                
                return ToolValidationResult(
                    is_valid=len(errors) == 0,
                    validation_errors=errors,
                    method_signatures={},
                    execution_test_results={},
                    input_schema_validation={},
                    security_validation={},
                    performance_validation={}
                )
        
        tool = TestTool()
        
        # Test path traversal detection
        malicious_input = {
            "test_field": "value",
            "file_path": "../../../etc/passwd"
        }
        
        result = tool.validate_input_comprehensive(malicious_input)
        
        # Log the result
        evidence_logger.log_error_scenario_test(
            test_name="Tool Protocol - Path Traversal Detection",
            error_scenario="Input contains path traversal attempt",
            expected_behavior="Should detect and reject path traversal",
            actual_behavior=f"Valid: {result.is_valid}, Errors: {result.validation_errors}",
            error_handled_correctly=not result.is_valid and any("path traversal" in err for err in result.validation_errors)
        )
        
        assert not result.is_valid, "Should reject path traversal input"
        assert any("path traversal" in err for err in result.validation_errors), "Should identify path traversal"
        
        # Test oversized input detection
        oversized_input = {
            "test_field": "value",
            "large_data": "x" * 2_000_000  # 2MB string
        }
        
        result2 = tool.validate_input_comprehensive(oversized_input)
        
        evidence_logger.log_error_scenario_test(
            test_name="Tool Protocol - Oversized Input Detection",
            error_scenario="Input contains oversized string",
            expected_behavior="Should detect and reject oversized input",
            actual_behavior=f"Valid: {result2.is_valid}, Errors: {result2.validation_errors}",
            error_handled_correctly=not result2.is_valid and any("too large" in err for err in result2.validation_errors)
        )
        
        assert not result2.is_valid, "Should reject oversized input"
        assert any("too large" in err for err in result2.validation_errors), "Should identify oversized input"
    
    def test_comprehensive_validation_performance(self):
        """Test performance validation catches problematic inputs"""
        evidence_logger = EvidenceLogger()
        
        class TestTool(Tool):
            def execute(self, input_data: Dict[str, Any], context=None) -> Dict[str, Any]:
                return {"status": "success"}
            
            def get_tool_info(self) -> Dict[str, Any]:
                return {"name": "TestTool", "version": "1.0"}
            
            def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
                return ToolValidationResult(
                    is_valid=True,
                    validation_errors=[],
                    method_signatures={},
                    execution_test_results={},
                    input_schema_validation={},
                    security_validation={},
                    performance_validation={}
                )
        
        tool = TestTool()
        
        # Test deeply nested input
        deeply_nested = {"level1": {}}
        current = deeply_nested["level1"]
        for i in range(15):  # Create 15 levels of nesting
            current[f"level{i+2}"] = {}
            current = current[f"level{i+2}"]
        
        result = tool.validate_input_comprehensive(deeply_nested)
        
        evidence_logger.log_performance_boundary_test(
            component="Tool Protocol Validation",
            test_type="Deep Nesting Detection",
            input_size=len(str(deeply_nested)),
            processing_time=0.001,  # Rough estimate
            memory_usage=0.1,
            success=not result.is_valid,
            failure_reason="Should reject deeply nested input" if result.is_valid else None
        )
        
        assert not result.is_valid, "Should reject deeply nested input"
        assert any("nesting depth" in err for err in result.validation_errors), "Should identify nesting issue"
    
    def test_validation_result_completeness(self):
        """Test that validation results contain all required information"""
        evidence_logger = EvidenceLogger()
        
        class TestTool(Tool):
            def execute(self, input_data: Dict[str, Any], context=None) -> Dict[str, Any]:
                return {"status": "success"}
            
            def get_tool_info(self) -> Dict[str, Any]:
                return {"name": "TestTool", "version": "1.0"}
            
            def validate_input(self, input_data: Dict[str, Any]) -> ToolValidationResult:
                return ToolValidationResult(
                    is_valid=True,
                    validation_errors=[],
                    method_signatures={},
                    execution_test_results={},
                    input_schema_validation={},
                    security_validation={},
                    performance_validation={}
                )
        
        tool = TestTool()
        
        # Test with valid input
        valid_input = {"test_field": "value"}
        result = tool.validate_input_comprehensive(valid_input)
        
        # Verify all validation components are present
        assert hasattr(result, "is_valid")
        assert hasattr(result, "validation_errors")
        assert hasattr(result, "method_signatures")
        assert hasattr(result, "execution_test_results")
        assert hasattr(result, "input_schema_validation")
        assert hasattr(result, "security_validation")
        assert hasattr(result, "performance_validation")
        
        # Verify validation results contain expected fields
        assert "valid" in result.security_validation
        assert "errors" in result.security_validation
        assert "security_checks" in result.security_validation
        
        assert "valid" in result.performance_validation
        assert "metrics" in result.performance_validation
        
        # Log completeness check
        evidence_logger.log_detailed_execution(
            operation="TOOL_PROTOCOL_VALIDATION_COMPLETENESS",
            details={
                "all_fields_present": True,
                "security_validation_fields": list(result.security_validation.keys()),
                "performance_validation_fields": list(result.performance_validation.keys()),
                "method_signatures_count": len(result.method_signatures)
            }
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])