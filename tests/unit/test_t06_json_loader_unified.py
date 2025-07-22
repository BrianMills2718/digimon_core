"""
TDD tests for T06 JSON Loader - Unified Interface Migration

Write these tests FIRST before implementing the unified interface.
These tests MUST fail initially (Red phase).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from typing import Dict, Any
import time
from pathlib import Path
import json

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus
from src.core.service_manager import ServiceManager


class TestT06JSONLoaderUnified:
    """Test-driven development for T06 JSON Loader unified interface"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_services = Mock(spec=ServiceManager)
        self.mock_identity = Mock()
        self.mock_provenance = Mock()
        self.mock_quality = Mock()
        
        self.mock_services.identity_service = self.mock_identity
        self.mock_services.provenance_service = self.mock_provenance
        self.mock_services.quality_service = self.mock_quality
        
        # Import will fail initially - this is expected in TDD
        from src.tools.phase1.t06_json_loader_unified import T06JSONLoaderUnified
        self.tool = T06JSONLoaderUnified(self.mock_services)
    
    # ===== CONTRACT TESTS (MANDATORY) =====
    
    def test_tool_initialization(self):
        """Tool initializes with required services"""
        assert self.tool is not None
        assert self.tool.tool_id == "T06"
        assert self.tool.services == self.mock_services
        assert isinstance(self.tool, BaseTool)
    
    def test_get_contract(self):
        """Tool provides complete contract specification"""
        contract = self.tool.get_contract()
        
        assert isinstance(contract, ToolContract)
        assert contract.tool_id == "T06"
        assert contract.name == "JSON Document Loader"
        assert contract.category == "document_processing"
        assert contract.description == "Load and process JSON documents with schema validation"
        
        # Verify input schema
        assert "file_path" in contract.input_schema["properties"]
        assert "workflow_id" in contract.input_schema["properties"]
        assert contract.input_schema["required"] == ["file_path"]
        
        # Verify output schema
        assert "document" in contract.output_schema["properties"]
        assert "data" in contract.output_schema["properties"]["document"]["properties"]
        assert "schema" in contract.output_schema["properties"]["document"]["properties"]
        assert "confidence" in contract.output_schema["properties"]["document"]["properties"]
        
        # Verify dependencies
        assert "identity_service" in contract.dependencies
        assert "provenance_service" in contract.dependencies
        assert "quality_service" in contract.dependencies
        
        # Verify performance requirements
        assert contract.performance_requirements["max_execution_time"] == 10.0
        assert contract.performance_requirements["max_memory_mb"] == 1024
    
    def test_input_contract_validation(self):
        """Tool validates inputs according to contract"""
        # Invalid inputs should be rejected
        invalid_inputs = [
            {},  # Empty input
            {"wrong_field": "value"},  # Wrong fields
            None,  # Null input
            {"file_path": ""},  # Empty file path
            {"file_path": 123},  # Wrong type
            {"file_path": "/etc/passwd"},  # Security risk
            {"file_path": "test.pdf"},  # Wrong extension
            {"file_path": "test.xml"},  # XML not JSON
        ]
        
        for invalid_input in invalid_inputs:
            request = ToolRequest(
                tool_id="T06",
                operation="load",
                input_data=invalid_input,
                parameters={}
            )
            result = self.tool.execute(request)
            assert result.status == "error"
            assert result.error_code in ["INVALID_INPUT", "VALIDATION_FAILED", "INVALID_FILE_TYPE", "FILE_NOT_FOUND"]
    
    def test_output_contract_compliance(self):
        """Tool output matches contract specification"""
        # Mock JSON data
        json_data = {
            "name": "Test Document",
            "version": "1.0",
            "data": {
                "items": [
                    {"id": 1, "value": "test1"},
                    {"id": 2, "value": "test2"}
                ]
            }
        }
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=json.dumps(json_data))), \
             patch('json.load', return_value=json_data):
            
            # Setup mocks
            mock_stat.return_value.st_size = 1024
            
            # Mock service responses
            self.mock_provenance.start_operation.return_value = "op123"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.95,
                "quality_tier": "HIGH"
            }
            
            valid_input = {
                "file_path": "test.json",
                "workflow_id": "wf_123"
            }
            
            request = ToolRequest(
                tool_id="T06",
                operation="load",
                input_data=valid_input,
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Verify output structure
            assert result.status == "success"
            assert result.tool_id == "T06"
            assert "document" in result.data
            
            # Verify document structure
            document = result.data["document"]
            assert "document_id" in document
            assert "data" in document
            assert "schema" in document
            assert "confidence" in document
            assert "file_path" in document
            assert "file_size" in document
            assert "json_type" in document
            assert "key_count" in document
            
            # Verify metadata
            assert result.execution_time > 0
            assert result.memory_used >= 0
            assert "operation_id" in result.metadata
    
    # ===== FUNCTIONALITY TESTS (MANDATORY) =====
    
    def test_json_object_loading(self):
        """Tool loads JSON objects correctly"""
        json_data = {
            "product": {
                "id": "12345",
                "name": "Widget",
                "price": 29.99,
                "categories": ["electronics", "gadgets"],
                "specifications": {
                    "weight": "100g",
                    "dimensions": "10x5x2cm",
                    "battery": True
                },
                "inStock": True,
                "rating": 4.5
            }
        }
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=json.dumps(json_data, indent=2))), \
             patch('json.load', return_value=json_data):
            
            mock_stat.return_value.st_size = 2048
            
            # Mock services
            self.mock_provenance.start_operation.return_value = "op123"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.94,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T06",
                operation="load",
                input_data={"file_path": "product.json"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert result.data["document"]["json_type"] == "object"
            assert result.data["document"]["key_count"] == 1  # root key "product"
            assert result.data["document"]["data"] == json_data
            assert result.data["document"]["confidence"] >= 0.9
            
            # Verify schema inference
            schema = result.data["document"]["schema"]
            assert schema["type"] == "object"
            assert "properties" in schema
    
    def test_json_array_loading(self):
        """Tool loads JSON arrays correctly"""
        json_data = [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25},
            {"id": 3, "name": "Charlie", "age": 35}
        ]
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=json.dumps(json_data))), \
             patch('json.load', return_value=json_data):
            
            mock_stat.return_value.st_size = 1024
            
            self.mock_provenance.start_operation.return_value = "op124"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.92,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T06",
                operation="load",
                input_data={"file_path": "users.json"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert result.data["document"]["json_type"] == "array"
            assert result.data["document"]["array_length"] == 3
            assert len(result.data["document"]["data"]) == 3
    
    def test_nested_json_loading(self):
        """Tool handles deeply nested JSON structures"""
        json_data = {
            "company": {
                "name": "TechCorp",
                "departments": [
                    {
                        "name": "Engineering",
                        "teams": [
                            {
                                "name": "Backend",
                                "members": [
                                    {"name": "John", "role": "Lead"},
                                    {"name": "Jane", "role": "Developer"}
                                ]
                            }
                        ]
                    }
                ],
                "metadata": {
                    "founded": 2020,
                    "location": {
                        "city": "San Francisco",
                        "country": "USA"
                    }
                }
            }
        }
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=json.dumps(json_data))), \
             patch('json.load', return_value=json_data):
            
            mock_stat.return_value.st_size = 1536
            
            self.mock_provenance.start_operation.return_value = "op125"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.91,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T06",
                operation="load",
                input_data={"file_path": "company.json"},
                parameters={"analyze_depth": True}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert result.data["document"]["depth"] >= 5  # Nested depth
            assert "statistics" in result.data["document"]
            stats = result.data["document"]["statistics"]
            assert stats["total_keys"] > 10
            assert stats["total_arrays"] >= 3
            assert stats["total_objects"] >= 5
    
    def test_edge_case_empty_json(self):
        """Tool handles empty JSON files gracefully"""
        # Test empty object
        empty_obj = {}
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=json.dumps(empty_obj))), \
             patch('json.load', return_value=empty_obj):
            
            mock_stat.return_value.st_size = 2
            
            self.mock_provenance.start_operation.return_value = "op126"
            
            request = ToolRequest(
                tool_id="T06",
                operation="load",
                input_data={"file_path": "empty.json"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Should handle gracefully
            assert result.status in ["success", "error"]
            if result.status == "success":
                assert result.data["document"]["json_type"] == "object"
                assert result.data["document"]["key_count"] == 0
    
    def test_edge_case_large_json(self):
        """Tool handles large JSON files efficiently"""
        # Create large JSON data
        large_data = {
            f"key_{i}": {
                "data": [{"id": j, "value": f"value_{j}"} for j in range(100)]
            } for i in range(100)
        }
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=json.dumps(large_data))), \
             patch('json.load', return_value=large_data):
            
            # 10MB file
            mock_stat.return_value.st_size = 10 * 1024 * 1024
            
            self.mock_provenance.start_operation.return_value = "op127"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.95,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T06",
                operation="load",
                input_data={"file_path": "large.json"},
                parameters={"memory_limit_mb": 500}
            )
            
            start_time = time.time()
            result = self.tool.execute(request)
            execution_time = time.time() - start_time
            
            assert result.status == "success"
            assert result.data["document"]["key_count"] == 100
            assert execution_time < 10.0  # Performance requirement
    
    def test_json_with_schema_validation(self):
        """Tool validates JSON against provided schema"""
        json_data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com"
        }
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0},
                "email": {"type": "string", "format": "email"}
            },
            "required": ["name", "age"]
        }
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=json.dumps(json_data))), \
             patch('json.load', return_value=json_data):
            
            mock_stat.return_value.st_size = 512
            
            self.mock_provenance.start_operation.return_value = "op128"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.96,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T06",
                operation="load",
                input_data={"file_path": "person.json"},
                parameters={"validate_schema": schema}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert result.data["document"]["schema_valid"] == True
            assert "validation_details" in result.data["document"]
    
    def test_json_special_types(self):
        """Tool handles special JSON types correctly"""
        json_data = {
            "null_value": None,
            "bool_true": True,
            "bool_false": False,
            "number_int": 42,
            "number_float": 3.14159,
            "empty_string": "",
            "empty_array": [],
            "empty_object": {},
            "unicode": "Hello 世界 🌍"
        }
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=json.dumps(json_data))), \
             patch('json.load', return_value=json_data):
            
            mock_stat.return_value.st_size = 512
            
            self.mock_provenance.start_operation.return_value = "op129"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.93,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T06",
                operation="load",
                input_data={"file_path": "special_types.json"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            data = result.data["document"]["data"]
            assert data["null_value"] is None
            assert data["bool_true"] is True
            assert data["bool_false"] is False
            assert isinstance(data["number_int"], int)
            assert isinstance(data["number_float"], float)
            assert data["unicode"] == "Hello 世界 🌍"
    
    # ===== INTEGRATION TESTS (MANDATORY) =====
    
    def test_identity_service_integration(self):
        """Tool integrates with IdentityService correctly"""
        json_data = {"test": "data"}
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=json.dumps(json_data))), \
             patch('json.load', return_value=json_data):
            
            mock_stat.return_value.st_size = 100
            
            self.mock_provenance.start_operation.return_value = "op130"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.90,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T06",
                operation="load",
                input_data={"file_path": "test.json", "workflow_id": "wf_123"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            # Verify document ID follows pattern
            assert result.data["document"]["document_id"].startswith("wf_123_")
    
    def test_provenance_tracking(self):
        """Tool tracks provenance correctly"""
        json_data = {"key": "value"}
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=json.dumps(json_data))), \
             patch('json.load', return_value=json_data):
            
            mock_stat.return_value.st_size = 50
            
            # Setup provenance mock
            self.mock_provenance.start_operation.return_value = "op131"
            self.mock_provenance.complete_operation.return_value = {
                "status": "success",
                "operation_id": "op131"
            }
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.85,
                "quality_tier": "MEDIUM"
            }
            
            request = ToolRequest(
                tool_id="T06",
                operation="load",
                input_data={"file_path": "test.json"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Verify provenance was tracked
            self.mock_provenance.start_operation.assert_called_once()
            call_args = self.mock_provenance.start_operation.call_args[1]
            assert call_args["tool_id"] == "T06"
            assert call_args["operation_type"] == "load_document"
            
            self.mock_provenance.complete_operation.assert_called_once()
            complete_args = self.mock_provenance.complete_operation.call_args[1]
            assert complete_args["operation_id"] == "op131"
            assert complete_args["success"] == True
    
    def test_quality_service_integration(self):
        """Tool integrates with quality service for confidence scoring"""
        complex_data = {
            "metadata": {
                "version": "2.0",
                "created": "2024-01-01"
            },
            "records": [{"id": i, "data": f"record_{i}"} for i in range(50)]
        }
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=json.dumps(complex_data))), \
             patch('json.load', return_value=complex_data):
            
            mock_stat.return_value.st_size = 2048
            
            self.mock_provenance.start_operation.return_value = "op132"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            
            # Mock quality assessment
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.96,
                "quality_tier": "HIGH",
                "factors": {
                    "structure": 1.0,
                    "completeness": 0.95
                }
            }
            
            request = ToolRequest(
                tool_id="T06",
                operation="load",
                input_data={"file_path": "quality_test.json"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Verify quality service was used
            self.mock_quality.assess_confidence.assert_called_once()
            quality_args = self.mock_quality.assess_confidence.call_args[1]
            assert quality_args["base_confidence"] > 0.8
            assert "factors" in quality_args
            
            # Result should have quality-adjusted confidence
            assert result.data["document"]["confidence"] == 0.96
            assert result.data["document"]["quality_tier"] == "HIGH"
    
    # ===== PERFORMANCE TESTS (MANDATORY) =====
    
    @pytest.mark.performance
    def test_performance_requirements(self):
        """Tool meets performance benchmarks"""
        # Create moderately complex JSON
        test_data = {
            "sections": [
                {
                    "id": f"section_{i}",
                    "title": f"Section {i}",
                    "items": [
                        {"id": f"item_{i}_{j}", "value": f"value_{i}_{j}"}
                        for j in range(50)
                    ]
                }
                for i in range(20)
            ]
        }
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=json.dumps(test_data))), \
             patch('json.load', return_value=test_data):
            
            # 5MB file
            mock_stat.return_value.st_size = 5 * 1024 * 1024
            
            self.mock_provenance.start_operation.return_value = "op133"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.93,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T06",
                operation="load",
                input_data={"file_path": "performance_test.json"},
                parameters={}
            )
            
            # Measure performance
            start_time = time.time()
            result = self.tool.execute(request)
            execution_time = time.time() - start_time
            
            # Performance assertions
            assert result.status == "success"
            assert execution_time < 10.0  # Max 10 seconds
            assert result.execution_time < 10.0
            assert result.memory_used < 1024 * 1024 * 1024  # Max 1GB
    
    # ===== ERROR HANDLING TESTS =====
    
    def test_handles_malformed_json(self):
        """Tool handles malformed JSON files gracefully"""
        malformed_json = '{"key": "value", "missing_quote: true}'
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=malformed_json)):
            
            mock_stat.return_value.st_size = 100
            
            self.mock_provenance.start_operation.return_value = "op134"
            
            request = ToolRequest(
                tool_id="T06",
                operation="load",
                input_data={"file_path": "malformed.json"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code in ["JSON_MALFORMED", "PARSING_FAILED"]
            assert "json" in result.error_message.lower() or "parse" in result.error_message.lower()
    
    def test_handles_encoding_errors(self):
        """Tool handles encoding errors appropriately"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')):
            
            mock_stat.return_value.st_size = 100
            
            self.mock_provenance.start_operation.return_value = "op135"
            
            request = ToolRequest(
                tool_id="T06",
                operation="load",
                input_data={"file_path": "bad_encoding.json"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code in ["ENCODING_ERROR", "EXTRACTION_FAILED"]
            assert "encoding" in result.error_message.lower() or "decode" in result.error_message.lower()
    
    def test_handles_file_not_found(self):
        """Tool handles missing files appropriately"""
        with patch('pathlib.Path.exists', return_value=False):
            
            request = ToolRequest(
                tool_id="T06",
                operation="load",
                input_data={"file_path": "nonexistent.json"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code == "FILE_NOT_FOUND"
            assert "not found" in result.error_message.lower()
    
    def test_handles_schema_validation_failure(self):
        """Tool handles schema validation failures"""
        json_data = {
            "name": "John Doe",
            "age": "thirty"  # Should be integer
        }
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=json.dumps(json_data))), \
             patch('json.load', return_value=json_data):
            
            mock_stat.return_value.st_size = 100
            
            self.mock_provenance.start_operation.return_value = "op136"
            
            request = ToolRequest(
                tool_id="T06",
                operation="load",
                input_data={"file_path": "invalid_schema.json"},
                parameters={"validate_schema": schema, "strict_validation": True}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code == "SCHEMA_VALIDATION_FAILED"
            assert "schema" in result.error_message.lower()
    
    # ===== UNIFIED INTERFACE TESTS =====
    
    def test_tool_status_management(self):
        """Tool manages status correctly"""
        assert self.tool.get_status() == ToolStatus.READY
        
        # During execution, status should change
        # This would need proper async handling in real implementation
        
    def test_health_check(self):
        """Tool health check works correctly"""
        result = self.tool.health_check()
        
        assert isinstance(result, ToolResult)
        assert result.tool_id == "T06"
        assert result.status in ["success", "error"]
        
        if result.status == "success":
            assert result.data["healthy"] == True
            assert "supported_formats" in result.data
            assert ".json" in result.data["supported_formats"]
    
    def test_cleanup(self):
        """Tool cleans up resources properly"""
        # Setup some mock resources
        self.tool._temp_files = ["temp1.json", "temp2.json"]
        
        success = self.tool.cleanup()
        
        assert success == True
        assert len(self.tool._temp_files) == 0