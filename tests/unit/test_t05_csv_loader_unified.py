"""
TDD tests for T05 CSV Loader - Unified Interface Migration

Write these tests FIRST before implementing the unified interface.
These tests MUST fail initially (Red phase).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from typing import Dict, Any
import time
from pathlib import Path
import pandas as pd
import io

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus
from src.core.service_manager import ServiceManager


class TestT05CSVLoaderUnified:
    """Test-driven development for T05 CSV Loader unified interface"""
    
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
        from src.tools.phase1.t05_csv_loader_unified import T05CSVLoaderUnified
        self.tool = T05CSVLoaderUnified(self.mock_services)
    
    # ===== CONTRACT TESTS (MANDATORY) =====
    
    def test_tool_initialization(self):
        """Tool initializes with required services"""
        assert self.tool is not None
        assert self.tool.tool_id == "T05"
        assert self.tool.services == self.mock_services
        assert isinstance(self.tool, BaseTool)
    
    def test_get_contract(self):
        """Tool provides complete contract specification"""
        contract = self.tool.get_contract()
        
        assert isinstance(contract, ToolContract)
        assert contract.tool_id == "T05"
        assert contract.name == "CSV Data Loader"
        assert contract.category == "document_processing"
        assert contract.description == "Load and process structured data from CSV files"
        
        # Verify input schema
        assert "file_path" in contract.input_schema["properties"]
        assert "workflow_id" in contract.input_schema["properties"]
        assert contract.input_schema["required"] == ["file_path"]
        
        # Verify output schema
        assert "dataset" in contract.output_schema["properties"]
        assert "rows" in contract.output_schema["properties"]["dataset"]["properties"]
        assert "columns" in contract.output_schema["properties"]["dataset"]["properties"]
        assert "confidence" in contract.output_schema["properties"]["dataset"]["properties"]
        
        # Verify dependencies
        assert "identity_service" in contract.dependencies
        assert "provenance_service" in contract.dependencies
        assert "quality_service" in contract.dependencies
        
        # Verify performance requirements
        assert contract.performance_requirements["max_execution_time"] == 15.0
        assert contract.performance_requirements["max_memory_mb"] == 2048
    
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
            {"file_path": "test.xlsx"},  # Excel not CSV
        ]
        
        for invalid_input in invalid_inputs:
            request = ToolRequest(
                tool_id="T05",
                operation="load",
                input_data=invalid_input,
                parameters={}
            )
            result = self.tool.execute(request)
            assert result.status == "error"
            assert result.error_code in ["INVALID_INPUT", "VALIDATION_FAILED", "INVALID_FILE_TYPE", "FILE_NOT_FOUND"]
    
    def test_output_contract_compliance(self):
        """Tool output matches contract specification"""
        # Mock CSV data
        csv_content = """name,age,city
John,30,New York
Jane,25,Los Angeles
Bob,35,Chicago"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=csv_content)), \
             patch('pandas.read_csv') as mock_read_csv:
            
            # Setup mocks
            mock_stat.return_value.st_size = 1024
            
            # Create mock DataFrame
            mock_df = pd.DataFrame({
                'name': ['John', 'Jane', 'Bob'],
                'age': [30, 25, 35],
                'city': ['New York', 'Los Angeles', 'Chicago']
            })
            mock_read_csv.return_value = mock_df
            
            # Mock service responses
            self.mock_provenance.start_operation.return_value = "op123"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.95,
                "quality_tier": "HIGH"
            }
            
            valid_input = {
                "file_path": "test.csv",
                "workflow_id": "wf_123"
            }
            
            request = ToolRequest(
                tool_id="T05",
                operation="load",
                input_data=valid_input,
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Verify output structure
            assert result.status == "success"
            assert result.tool_id == "T05"
            assert "dataset" in result.data
            
            # Verify dataset structure
            dataset = result.data["dataset"]
            assert "dataset_id" in dataset
            assert "rows" in dataset
            assert "columns" in dataset
            assert "data" in dataset
            assert "confidence" in dataset
            assert "file_path" in dataset
            assert "file_size" in dataset
            assert "column_types" in dataset
            
            # Verify metadata
            assert result.execution_time > 0
            assert result.memory_used >= 0
            assert "operation_id" in result.metadata
    
    # ===== FUNCTIONALITY TESTS (MANDATORY) =====
    
    def test_csv_loading_functionality(self):
        """Tool loads CSV files correctly"""
        csv_content = """product,price,quantity,category
Apple,1.50,100,Fruit
Banana,0.75,150,Fruit
Carrot,2.00,80,Vegetable
Broccoli,3.50,60,Vegetable"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=csv_content)), \
             patch('pandas.read_csv') as mock_read_csv:
            
            mock_stat.return_value.st_size = 2048
            
            # Create mock DataFrame
            mock_df = pd.DataFrame({
                'product': ['Apple', 'Banana', 'Carrot', 'Broccoli'],
                'price': [1.50, 0.75, 2.00, 3.50],
                'quantity': [100, 150, 80, 60],
                'category': ['Fruit', 'Fruit', 'Vegetable', 'Vegetable']
            })
            mock_read_csv.return_value = mock_df
            
            # Mock services
            self.mock_provenance.start_operation.return_value = "op123"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.93,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T05",
                operation="load",
                input_data={"file_path": "products.csv"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert result.data["dataset"]["rows"] == 4
            assert result.data["dataset"]["columns"] == 4
            assert len(result.data["dataset"]["data"]) == 4
            assert result.data["dataset"]["confidence"] >= 0.9
            
            # Verify column types detected
            column_types = result.data["dataset"]["column_types"]
            assert column_types["product"] == "string"
            assert column_types["price"] == "float"
            assert column_types["quantity"] == "integer"
            assert column_types["category"] == "string"
    
    def test_csv_with_different_delimiters(self):
        """Tool handles CSVs with different delimiters"""
        # Test semicolon delimiter
        csv_content = """name;age;department
Alice;28;Engineering
Bob;32;Marketing
Charlie;29;Sales"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=csv_content)), \
             patch('pandas.read_csv') as mock_read_csv:
            
            mock_stat.return_value.st_size = 1024
            
            # Mock DataFrame
            mock_df = pd.DataFrame({
                'name': ['Alice', 'Bob', 'Charlie'],
                'age': [28, 32, 29],
                'department': ['Engineering', 'Marketing', 'Sales']
            })
            mock_read_csv.return_value = mock_df
            
            self.mock_provenance.start_operation.return_value = "op124"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.92,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T05",
                operation="load",
                input_data={"file_path": "employees.csv"},
                parameters={"delimiter": ";"}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert result.data["dataset"]["rows"] == 3
            assert result.data["dataset"]["columns"] == 3
    
    def test_csv_with_missing_values(self):
        """Tool handles CSV files with missing values"""
        csv_content = """id,value,status
1,100,active
2,,inactive
3,200,
4,150,active"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=csv_content)), \
             patch('pandas.read_csv') as mock_read_csv:
            
            mock_stat.return_value.st_size = 512
            
            # Mock DataFrame with NaN values
            mock_df = pd.DataFrame({
                'id': [1, 2, 3, 4],
                'value': [100.0, None, 200.0, 150.0],
                'status': ['active', 'inactive', None, 'active']
            })
            mock_read_csv.return_value = mock_df
            
            self.mock_provenance.start_operation.return_value = "op125"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.85,
                "quality_tier": "MEDIUM"
            }
            
            request = ToolRequest(
                tool_id="T05",
                operation="load",
                input_data={"file_path": "data_with_nulls.csv"},
                parameters={"handle_missing": "keep"}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert result.data["dataset"]["missing_values"]["value"] == 1
            assert result.data["dataset"]["missing_values"]["status"] == 1
            assert result.data["dataset"]["data_quality"]["completeness"] < 1.0
    
    def test_edge_case_empty_csv(self):
        """Tool handles empty CSV files gracefully"""
        csv_content = """col1,col2,col3"""  # Headers only, no data
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=csv_content)), \
             patch('pandas.read_csv') as mock_read_csv:
            
            mock_stat.return_value.st_size = 50
            
            # Empty DataFrame
            mock_df = pd.DataFrame(columns=['col1', 'col2', 'col3'])
            mock_read_csv.return_value = mock_df
            
            self.mock_provenance.start_operation.return_value = "op126"
            
            request = ToolRequest(
                tool_id="T05",
                operation="load",
                input_data={"file_path": "empty.csv"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Should handle gracefully
            assert result.status in ["success", "error"]
            if result.status == "success":
                assert result.data["dataset"]["rows"] == 0
                assert result.data["dataset"]["columns"] == 3
    
    def test_edge_case_large_csv(self):
        """Tool handles large CSV files efficiently"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True), \
             patch('pandas.read_csv') as mock_read_csv:
            
            # 100MB file
            mock_stat.return_value.st_size = 100 * 1024 * 1024
            
            # Create large DataFrame
            large_data = {
                f'col_{i}': list(range(100000)) for i in range(20)
            }
            mock_df = pd.DataFrame(large_data)
            mock_read_csv.return_value = mock_df
            
            self.mock_provenance.start_operation.return_value = "op127"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.95,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T05",
                operation="load",
                input_data={"file_path": "large.csv"},
                parameters={"memory_limit_mb": 1000}
            )
            
            start_time = time.time()
            result = self.tool.execute(request)
            execution_time = time.time() - start_time
            
            assert result.status == "success"
            assert result.data["dataset"]["rows"] == 100000
            assert result.data["dataset"]["columns"] == 20
            assert execution_time < 15.0  # Performance requirement
    
    def test_csv_type_inference(self):
        """Tool correctly infers column data types"""
        csv_content = """int_col,float_col,str_col,bool_col,date_col
1,1.5,hello,true,2023-01-01
2,2.7,world,false,2023-01-02
3,3.14,test,true,2023-01-03"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=csv_content)), \
             patch('pandas.read_csv') as mock_read_csv:
            
            mock_stat.return_value.st_size = 512
            
            # Mock DataFrame with proper types
            mock_df = pd.DataFrame({
                'int_col': [1, 2, 3],
                'float_col': [1.5, 2.7, 3.14],
                'str_col': ['hello', 'world', 'test'],
                'bool_col': [True, False, True],
                'date_col': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03'])
            })
            mock_read_csv.return_value = mock_df
            
            self.mock_provenance.start_operation.return_value = "op128"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.94,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T05",
                operation="load",
                input_data={"file_path": "typed_data.csv"},
                parameters={"infer_types": True}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            column_types = result.data["dataset"]["column_types"]
            assert column_types["int_col"] == "integer"
            assert column_types["float_col"] == "float"
            assert column_types["str_col"] == "string"
            assert column_types["bool_col"] == "boolean"
            assert column_types["date_col"] == "datetime"
    
    # ===== INTEGRATION TESTS (MANDATORY) =====
    
    def test_identity_service_integration(self):
        """Tool integrates with IdentityService correctly"""
        csv_content = """id,name\n1,Test"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=csv_content)), \
             patch('pandas.read_csv') as mock_read_csv:
            
            mock_stat.return_value.st_size = 100
            mock_df = pd.DataFrame({'id': [1], 'name': ['Test']})
            mock_read_csv.return_value = mock_df
            
            self.mock_provenance.start_operation.return_value = "op129"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.90,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T05",
                operation="load",
                input_data={"file_path": "test.csv", "workflow_id": "wf_123"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            # Verify dataset ID follows pattern
            assert result.data["dataset"]["dataset_id"].startswith("wf_123_")
    
    def test_provenance_tracking(self):
        """Tool tracks provenance correctly"""
        csv_content = """col1\nvalue1"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=csv_content)), \
             patch('pandas.read_csv') as mock_read_csv:
            
            mock_stat.return_value.st_size = 50
            mock_df = pd.DataFrame({'col1': ['value1']})
            mock_read_csv.return_value = mock_df
            
            # Setup provenance mock
            self.mock_provenance.start_operation.return_value = "op130"
            self.mock_provenance.complete_operation.return_value = {
                "status": "success",
                "operation_id": "op130"
            }
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.85,
                "quality_tier": "MEDIUM"
            }
            
            request = ToolRequest(
                tool_id="T05",
                operation="load",
                input_data={"file_path": "test.csv"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Verify provenance was tracked
            self.mock_provenance.start_operation.assert_called_once()
            call_args = self.mock_provenance.start_operation.call_args[1]
            assert call_args["tool_id"] == "T05"
            assert call_args["operation_type"] == "load_dataset"
            
            self.mock_provenance.complete_operation.assert_called_once()
            complete_args = self.mock_provenance.complete_operation.call_args[1]
            assert complete_args["operation_id"] == "op130"
            assert complete_args["success"] == True
    
    def test_quality_service_integration(self):
        """Tool integrates with quality service for confidence scoring"""
        csv_content = "col1,col2,col3\n" + "\n".join([f"val{i},val{i+1},val{i+2}" for i in range(50)])
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=csv_content)), \
             patch('pandas.read_csv') as mock_read_csv:
            
            mock_stat.return_value.st_size = 2048
            
            # Create DataFrame with many rows
            data = {
                'col1': [f'val{i}' for i in range(50)],
                'col2': [f'val{i+1}' for i in range(50)],
                'col3': [f'val{i+2}' for i in range(50)]
            }
            mock_df = pd.DataFrame(data)
            mock_read_csv.return_value = mock_df
            
            self.mock_provenance.start_operation.return_value = "op131"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            
            # Mock quality assessment
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.96,
                "quality_tier": "HIGH",
                "factors": {
                    "row_count": 1.0,
                    "completeness": 1.0,
                    "consistency": 0.95
                }
            }
            
            request = ToolRequest(
                tool_id="T05",
                operation="load",
                input_data={"file_path": "quality_test.csv"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Verify quality service was used
            self.mock_quality.assess_confidence.assert_called_once()
            quality_args = self.mock_quality.assess_confidence.call_args[1]
            assert quality_args["base_confidence"] > 0.8
            assert "factors" in quality_args
            
            # Result should have quality-adjusted confidence
            assert result.data["dataset"]["confidence"] == 0.96
            assert result.data["dataset"]["quality_tier"] == "HIGH"
    
    # ===== PERFORMANCE TESTS (MANDATORY) =====
    
    @pytest.mark.performance
    def test_performance_requirements(self):
        """Tool meets performance benchmarks"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True), \
             patch('pandas.read_csv') as mock_read_csv:
            
            # Standard test file
            mock_stat.return_value.st_size = 10 * 1024 * 1024  # 10MB
            
            # Create DataFrame with many rows and columns
            data = {
                f'col_{i}': list(range(10000)) for i in range(30)
            }
            mock_df = pd.DataFrame(data)
            mock_read_csv.return_value = mock_df
            
            self.mock_provenance.start_operation.return_value = "op132"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.93,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T05",
                operation="load",
                input_data={"file_path": "performance_test.csv"},
                parameters={}
            )
            
            # Measure performance
            start_time = time.time()
            result = self.tool.execute(request)
            execution_time = time.time() - start_time
            
            # Performance assertions
            assert result.status == "success"
            assert execution_time < 15.0  # Max 15 seconds
            assert result.execution_time < 15.0
            assert result.memory_used < 2048 * 1024 * 1024  # Max 2GB
    
    # ===== ERROR HANDLING TESTS =====
    
    def test_handles_malformed_csv(self):
        """Tool handles malformed CSV files gracefully"""
        csv_content = """col1,col2,col3
val1,val2
val3,val4,val5,val6
val7"""  # Inconsistent columns
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=csv_content)), \
             patch('pandas.read_csv') as mock_read_csv:
            
            mock_stat.return_value.st_size = 100
            # Simulate pandas error
            mock_read_csv.side_effect = pd.errors.ParserError("Error tokenizing data")
            
            self.mock_provenance.start_operation.return_value = "op133"
            
            request = ToolRequest(
                tool_id="T05",
                operation="load",
                input_data={"file_path": "malformed.csv"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code in ["CSV_MALFORMED", "PARSING_FAILED"]
            assert "tokenizing" in result.error_message.lower() or "malformed" in result.error_message.lower()
    
    def test_handles_encoding_errors(self):
        """Tool handles encoding errors appropriately"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')), \
             patch('pandas.read_csv') as mock_read_csv:
            
            mock_stat.return_value.st_size = 100
            mock_read_csv.side_effect = UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid start byte')
            
            self.mock_provenance.start_operation.return_value = "op134"
            
            request = ToolRequest(
                tool_id="T05",
                operation="load",
                input_data={"file_path": "bad_encoding.csv"},
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
                tool_id="T05",
                operation="load",
                input_data={"file_path": "nonexistent.csv"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code == "FILE_NOT_FOUND"
            assert "not found" in result.error_message.lower()
    
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
        assert result.tool_id == "T05"
        assert result.status in ["success", "error"]
        
        if result.status == "success":
            assert result.data["healthy"] == True
            assert "supported_formats" in result.data
            assert ".csv" in result.data["supported_formats"]
    
    def test_cleanup(self):
        """Tool cleans up resources properly"""
        # Setup some mock resources
        self.tool._temp_files = ["temp1.csv", "temp2.csv"]
        
        success = self.tool.cleanup()
        
        assert success == True
        assert len(self.tool._temp_files) == 0