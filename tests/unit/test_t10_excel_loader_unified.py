"""
Mock-free unit tests for T10 Excel Loader Unified

Tests the unified Excel loader tool with real Excel processing using pandas and openpyxl.
No mocking is used - all functionality is tested with real data and real processing.
"""

import pytest
import tempfile
import pandas as pd
import openpyxl
from pathlib import Path
import os

from src.tools.phase1.t10_excel_loader_unified import T10ExcelLoaderUnified
from src.core.service_manager import ServiceManager
from src.tools.base_tool import ToolRequest


class TestT10ExcelLoaderUnifiedMockFree:
    def setup_method(self):
        """Set up test fixtures with real ServiceManager - NO mocks"""
        # Real ServiceManager - NO mocking
        self.service_manager = ServiceManager()
        self.tool = T10ExcelLoaderUnified(service_manager=self.service_manager)
        
        # Create real test Excel files
        self.test_files = self._create_real_test_excel_files()
    
    def teardown_method(self):
        """Clean up real test files"""
        for file_path in self.test_files.values():
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except:
                pass
    
    def _create_real_test_excel_files(self) -> dict:
        """Create real Excel test files for testing"""
        test_files = {}
        
        # Simple Excel file with one sheet
        simple_data = {
            'Name': ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson'],
            'Age': [25, 30, 35, 40],
            'Department': ['Engineering', 'Marketing', 'Sales', 'HR'],
            'Salary': [75000, 65000, 55000, 60000],
            'Start_Date': ['2020-01-15', '2019-06-01', '2021-03-10', '2018-11-20']
        }
        df_simple = pd.DataFrame(simple_data)
        
        simple_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        df_simple.to_excel(simple_file.name, index=False, sheet_name='Employees')
        simple_file.close()
        test_files['simple'] = simple_file.name
        
        # Complex Excel file with multiple sheets
        complex_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        
        with pd.ExcelWriter(complex_file.name, engine='openpyxl') as writer:
            # Sales data sheet
            sales_data = {
                'Product': ['Widget A', 'Widget B', 'Widget C', 'Widget D', 'Widget E'],
                'Q1_Sales': [12000, 15000, 8000, 20000, 5000],
                'Q2_Sales': [13000, 14000, 9000, 22000, 6000],
                'Q3_Sales': [14000, 16000, 7000, 21000, 7000],
                'Q4_Sales': [15000, 17000, 10000, 23000, 8000],
                'Total': [54000, 62000, 34000, 86000, 26000]
            }
            pd.DataFrame(sales_data).to_excel(writer, sheet_name='Sales', index=False)
            
            # Employee data sheet
            employee_data = {
                'ID': [1001, 1002, 1003, 1004, 1005, 1006],
                'Name': ['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson', 'Tom Brown', 'Lisa Garcia'],
                'Position': ['Manager', 'Developer', 'Designer', 'Analyst', 'Developer', 'Tester'],
                'Team': ['Alpha', 'Beta', 'Alpha', 'Gamma', 'Beta', 'Gamma'],
                'Salary': [85000, 70000, 65000, 60000, 72000, 58000],
                'Performance': [4.5, 4.2, 4.8, 4.0, 4.3, 4.1]
            }
            pd.DataFrame(employee_data).to_excel(writer, sheet_name='Employees', index=False)
            
            # Financial data sheet
            financial_data = {
                'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'Revenue': [120000, 135000, 128000, 142000, 156000, 148000],
                'Expenses': [85000, 92000, 88000, 95000, 102000, 98000],
                'Profit': [35000, 43000, 40000, 47000, 54000, 50000],
                'Growth_%': [5.2, 8.1, 6.3, 9.2, 12.4, 7.8]
            }
            pd.DataFrame(financial_data).to_excel(writer, sheet_name='Financials', index=False)
        
        complex_file.close()
        test_files['complex'] = complex_file.name
        
        # Large Excel file for performance testing
        large_data = {
            f'Column_{i}': [f'Value_{i}_{j}' for j in range(500)]
            for i in range(20)
        }
        df_large = pd.DataFrame(large_data)
        
        large_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        df_large.to_excel(large_file.name, index=False, sheet_name='LargeData')
        large_file.close()
        test_files['large'] = large_file.name
        
        # Excel file with mixed data types
        mixed_data = {
            'String_Col': ['Text1', 'Text2', 'Text3', None, 'Text5'],
            'Integer_Col': [1, 2, 3, 4, 5],
            'Float_Col': [1.1, 2.2, 3.3, 4.4, 5.5],
            'Boolean_Col': [True, False, True, False, True],
            'Date_Col': pd.date_range('2024-01-01', periods=5),
            'Mixed_Col': ['A', 123, 45.6, True, None]
        }
        df_mixed = pd.DataFrame(mixed_data)
        
        mixed_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        df_mixed.to_excel(mixed_file.name, index=False, sheet_name='MixedTypes')
        mixed_file.close()
        test_files['mixed'] = mixed_file.name
        
        # Empty Excel file
        empty_data = pd.DataFrame()
        empty_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        empty_data.to_excel(empty_file.name, index=False, sheet_name='Empty')
        empty_file.close()
        test_files['empty'] = empty_file.name
        
        return test_files
    
    def test_tool_contract_real(self):
        """Test tool contract with REAL contract validation"""
        contract = self.tool.get_contract()
        
        # Verify contract structure
        assert contract.tool_id == "T10"
        assert contract.name == "Excel Document Loader"
        assert contract.category == "document_processing"
        assert "file_path" in contract.input_schema["required"]
        assert "document" in contract.output_schema["required"]
        assert len(contract.dependencies) > 0
        
        # Verify performance requirements
        assert "max_execution_time" in contract.performance_requirements
        assert "max_memory_mb" in contract.performance_requirements
        assert "min_confidence" in contract.performance_requirements
        
        # Verify error conditions
        assert "EXCEL_CORRUPTED" in contract.error_conditions
        assert "FILE_NOT_FOUND" in contract.error_conditions
    
    def test_simple_excel_loading_real(self):
        """Test loading simple Excel with REAL processing"""
        request = ToolRequest(
            tool_id="T10",
            operation="load_excel",
            input_data={
                "file_path": self.test_files['simple'],
                "workflow_id": "test_workflow_simple"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify successful execution
        assert result.status == "success"
        assert result.tool_id == "T10"
        assert result.execution_time > 0
        
        # Verify document data
        doc = result.data["document"]
        assert doc["document_id"] == "test_workflow_simple_" + Path(self.test_files['simple']).stem
        assert doc["file_name"] == Path(self.test_files['simple']).name
        assert doc["sheet_count"] == 1
        assert doc["total_rows"] == 4  # 4 employees
        assert doc["total_columns"] == 5  # Name, Age, Department, Salary, Start_Date
        assert doc["confidence"] > 0.5
        assert len(doc["text_content"]) > 0
        
        # Verify Excel data structure
        excel_data = doc["excel_data"]
        assert "Employees" in excel_data
        employee_sheet = excel_data["Employees"]
        assert employee_sheet["row_count"] == 4
        assert employee_sheet["column_count"] == 5
        assert "Name" in employee_sheet["headers"]
        assert "Salary" in employee_sheet["headers"]
        
        # Verify specific content
        assert "Alice Johnson" in doc["text_content"]
        assert "Engineering" in doc["text_content"]
    
    def test_complex_excel_multiple_sheets_real(self):
        """Test loading complex Excel with multiple sheets with REAL processing"""
        request = ToolRequest(
            tool_id="T10",
            operation="load_excel",
            input_data={
                "file_path": self.test_files['complex'],
                "workflow_id": "test_workflow_complex"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify successful execution
        assert result.status == "success"
        
        # Verify document data
        doc = result.data["document"]
        assert doc["sheet_count"] == 3  # Sales, Employees, Financials
        assert doc["total_rows"] > 10   # Combined rows from all sheets
        assert doc["confidence"] > 0.5
        
        # Verify all sheets are loaded
        excel_data = doc["excel_data"]
        assert "Sales" in excel_data
        assert "Employees" in excel_data
        assert "Financials" in excel_data
        
        # Verify sheet data
        sales_sheet = excel_data["Sales"]
        assert sales_sheet["row_count"] == 5  # 5 products
        assert "Product" in sales_sheet["headers"]
        assert "Q1_Sales" in sales_sheet["headers"]
        
        # Verify content from all sheets
        assert "Widget A" in doc["text_content"]  # From Sales sheet
        assert "John Doe" in doc["text_content"]  # From Employees sheet
        assert "Revenue" in doc["text_content"]   # From Financials sheet
    
    def test_specific_sheet_loading_real(self):
        """Test loading specific sheet with REAL processing"""
        request = ToolRequest(
            tool_id="T10",
            operation="load_excel",
            input_data={
                "file_path": self.test_files['complex'],
                "parse_options": {
                    "sheet_name": "Sales"
                }
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify successful execution
        assert result.status == "success"
        
        # Verify only Sales sheet is loaded
        doc = result.data["document"]
        excel_data = doc["excel_data"]
        assert len(excel_data) == 1
        assert "Sales" in excel_data
        assert "Employees" not in excel_data
        assert "Financials" not in excel_data
        
        # Verify Sales sheet data
        sales_sheet = excel_data["Sales"]
        assert sales_sheet["row_count"] == 5
        assert "Widget A" in doc["text_content"]
        assert "John Doe" not in doc["text_content"]  # Not from Sales sheet
    
    def test_sheet_by_index_real(self):
        """Test loading sheet by index with REAL processing"""
        request = ToolRequest(
            tool_id="T10",
            operation="load_excel",
            input_data={
                "file_path": self.test_files['complex'],
                "parse_options": {
                    "sheet_name": 1  # Second sheet (Employees)
                }
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify successful execution
        assert result.status == "success"
        
        # Verify only Employees sheet is loaded (index 1)
        doc = result.data["document"]
        excel_data = doc["excel_data"]
        assert len(excel_data) == 1
        
        # Should contain the second sheet (Employees)
        sheet_name = list(excel_data.keys())[0]
        sheet_data = excel_data[sheet_name]
        assert "Name" in sheet_data["headers"]
        assert "Position" in sheet_data["headers"]
        assert "John Doe" in doc["text_content"]
    
    def test_parse_options_functionality_real(self):
        """Test different parse options with REAL processing"""
        # Test with custom header row
        request_header = ToolRequest(
            tool_id="T10",
            operation="load_excel",
            input_data={
                "file_path": self.test_files['simple'],
                "parse_options": {
                    "header_row": 0  # First row as header
                }
            },
            parameters={}
        )
        
        result_header = self.tool.execute(request_header)
        assert result_header.status == "success"
        
        # Test with max rows limit
        request_max_rows = ToolRequest(
            tool_id="T10",
            operation="load_excel",
            input_data={
                "file_path": self.test_files['large'],
                "parse_options": {
                    "max_rows": 10
                }
            },
            parameters={}
        )
        
        result_max_rows = self.tool.execute(request_max_rows)
        assert result_max_rows.status == "success"
        
        # Should only load 10 rows
        doc = result_max_rows.data["document"]
        excel_data = doc["excel_data"]
        sheet_data = list(excel_data.values())[0]
        assert sheet_data["row_count"] <= 10
    
    def test_mixed_data_types_real(self):
        """Test Excel with mixed data types with REAL processing"""
        request = ToolRequest(
            tool_id="T10",
            operation="load_excel",
            input_data={
                "file_path": self.test_files['mixed']
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify successful execution
        assert result.status == "success"
        
        # Verify mixed data types are handled
        doc = result.data["document"]
        excel_data = doc["excel_data"]
        sheet_data = list(excel_data.values())[0]
        
        # Verify different column types
        assert "String_Col" in sheet_data["headers"]
        assert "Integer_Col" in sheet_data["headers"]
        assert "Float_Col" in sheet_data["headers"]
        assert "Boolean_Col" in sheet_data["headers"]
        
        # Verify data was processed correctly
        assert sheet_data["row_count"] == 5
        assert len(sheet_data["data"]) == 5
        
        # Check data types information
        assert "data_types" in sheet_data
        data_types = sheet_data["data_types"]
        assert len(data_types) > 0
    
    def test_empty_excel_file_real(self):
        """Test empty Excel file with REAL processing"""
        request = ToolRequest(
            tool_id="T10",
            operation="load_excel",
            input_data={
                "file_path": self.test_files['empty']
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify successful execution even with empty file
        assert result.status == "success"
        
        # Verify empty data handling
        doc = result.data["document"]
        assert doc["sheet_count"] == 1
        assert doc["total_rows"] == 0
        assert doc["confidence"] > 0.1  # Should still have some confidence
    
    def test_file_not_found_error_real(self):
        """Test file not found error with REAL missing file"""
        request = ToolRequest(
            tool_id="T10",
            operation="load_excel",
            input_data={
                "file_path": "/path/to/nonexistent/file.xlsx"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify error handling
        assert result.status == "error"
        assert result.error_code == "FILE_NOT_FOUND"
        assert "File not found" in result.error_message
    
    def test_invalid_file_type_error_real(self):
        """Test invalid file type error with REAL non-Excel file"""
        # Create a non-Excel file
        txt_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        txt_file.write("This is not an Excel file")
        txt_file.close()
        
        try:
            request = ToolRequest(
                tool_id="T10",
                operation="load_excel",
                input_data={
                    "file_path": txt_file.name
                },
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Verify error handling
            assert result.status == "error"
            assert result.error_code == "INVALID_FILE_TYPE"
            assert "Invalid file extension" in result.error_message
        finally:
            os.unlink(txt_file.name)
    
    def test_sheet_not_found_error_real(self):
        """Test sheet not found error with REAL sheet name"""
        request = ToolRequest(
            tool_id="T10",
            operation="load_excel",
            input_data={
                "file_path": self.test_files['simple'],
                "parse_options": {
                    "sheet_name": "NonexistentSheet"
                }
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify error handling
        assert result.status == "error"
        assert result.error_code == "SHEET_NOT_FOUND"
        assert "NonexistentSheet" in result.error_message
    
    def test_input_validation_real(self):
        """Test input validation with REAL validation logic"""
        # Test missing file_path
        result = self.tool.validate_input({})
        assert result == False
        
        result = self.tool.validate_input({"file_path": ""})
        assert result == False
        
        # Test valid input
        result = self.tool.validate_input({"file_path": "/some/path.xlsx"})
        assert result == True
    
    def test_health_check_real(self):
        """Test health check with REAL service verification"""
        result = self.tool.health_check()
        
        # Verify health check structure
        assert isinstance(result.data, dict)
        assert "healthy" in result.data
        assert "pandas_available" in result.data
        assert "pandas_version" in result.data
        assert "openpyxl_available" in result.data
        assert "openpyxl_version" in result.data
        assert "services_healthy" in result.data
        assert "supported_formats" in result.data
        
        # Verify pandas and openpyxl are available
        assert result.data["pandas_available"] == True
        assert result.data["openpyxl_available"] == True
        
        # Verify supported formats
        supported_formats = result.data["supported_formats"]
        assert ".xlsx" in supported_formats
        assert ".xls" in supported_formats
        assert ".xlsm" in supported_formats
    
    def test_cleanup_functionality_real(self):
        """Test cleanup functionality with REAL resource management"""
        # Add some temp files to the tool
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        self.tool._temp_files.append(temp_file.name)
        
        # Verify cleanup works
        cleanup_result = self.tool.cleanup()
        assert cleanup_result == True
        assert len(self.tool._temp_files) == 0
        assert not os.path.exists(temp_file.name)
    
    def test_confidence_calculation_real(self):
        """Test confidence calculation with REAL Excel parsing metrics"""
        # Test with simple Excel
        request_simple = ToolRequest(
            tool_id="T10",
            operation="load_excel",
            input_data={"file_path": self.test_files['simple']},
            parameters={}
        )
        
        result_simple = self.tool.execute(request_simple)
        confidence_simple = result_simple.data["document"]["confidence"]
        
        # Test with complex Excel
        request_complex = ToolRequest(
            tool_id="T10",
            operation="load_excel",
            input_data={"file_path": self.test_files['complex']},
            parameters={}
        )
        
        result_complex = self.tool.execute(request_complex)
        confidence_complex = result_complex.data["document"]["confidence"]
        
        # Both should have reasonable confidence
        assert confidence_simple > 0.5
        assert confidence_complex > 0.5
        # Complex Excel should have higher confidence due to more data
        assert confidence_complex >= confidence_simple - 0.1
    
    def test_performance_metrics_real(self):
        """Test performance metrics with REAL execution measurement"""
        request = ToolRequest(
            tool_id="T10",
            operation="load_excel",
            input_data={"file_path": self.test_files['large']},
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify performance metrics are captured
        assert result.execution_time > 0
        assert result.memory_used >= 0
        
        # Verify reasonable execution time for large file
        assert result.execution_time < 10.0  # Should be under 10 seconds
    
    def test_service_integration_real(self):
        """Test service integration with REAL services"""
        request = ToolRequest(
            tool_id="T10",
            operation="load_excel",
            input_data={
                "file_path": self.test_files['simple'],
                "workflow_id": "test_service_integration"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify service integration
        assert result.status == "success"
        assert "operation_id" in result.metadata
        
        # Verify provenance tracking
        operation_id = result.metadata["operation_id"]
        assert operation_id is not None
        
        # Verify quality assessment
        doc = result.data["document"]
        assert "quality_tier" in doc
        assert doc["confidence"] > 0
    
    def test_data_extraction_accuracy_real(self):
        """Test data extraction accuracy with REAL Excel content"""
        request = ToolRequest(
            tool_id="T10",
            operation="load_excel",
            input_data={"file_path": self.test_files['simple']},
            parameters={}
        )
        
        result = self.tool.execute(request)
        doc = result.data["document"]
        excel_data = doc["excel_data"]
        employee_sheet = excel_data["Employees"]
        
        # Verify extracted data accuracy
        data = employee_sheet["data"]
        assert len(data) == 4  # 4 employees
        
        # Check first employee data
        first_employee = data[0]
        assert first_employee[0] == "Alice Johnson"  # Name
        assert first_employee[1] == 25               # Age
        assert first_employee[2] == "Engineering"    # Department
        assert first_employee[3] == 75000           # Salary
        
        # Verify headers
        headers = employee_sheet["headers"]
        assert headers == ['Name', 'Age', 'Department', 'Salary', 'Start_Date']
    
    def test_text_content_extraction_real(self):
        """Test text content extraction with REAL text processing"""
        request = ToolRequest(
            tool_id="T10",
            operation="load_excel",
            input_data={"file_path": self.test_files['complex']},
            parameters={}
        )
        
        result = self.tool.execute(request)
        text_content = result.data["document"]["text_content"]
        
        # Verify all expected content is extracted from all sheets
        assert "Sheet: Sales" in text_content
        assert "Sheet: Employees" in text_content
        assert "Sheet: Financials" in text_content
        
        assert "Widget A" in text_content      # From Sales sheet
        assert "John Doe" in text_content      # From Employees sheet
        assert "Revenue" in text_content       # From Financials sheet
        
        # Verify text is properly formatted
        assert len(text_content.strip()) > 0
        lines = text_content.split('\n')
        assert len(lines) > 10  # Should have multiple lines of content
    
    def test_large_file_handling_real(self):
        """Test large Excel file handling with REAL performance measurement"""
        request = ToolRequest(
            tool_id="T10",
            operation="load_excel",
            input_data={"file_path": self.test_files['large']},
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify successful processing of large file
        assert result.status == "success"
        
        doc = result.data["document"]
        assert doc["total_rows"] == 500    # 500 rows
        assert doc["total_columns"] == 20  # 20 columns
        
        # Verify reasonable performance
        assert result.execution_time < 10.0  # Under 10 seconds
        
        # Verify data integrity
        excel_data = doc["excel_data"]
        sheet_data = list(excel_data.values())[0]
        assert len(sheet_data["data"]) == 500
        assert len(sheet_data["headers"]) == 20