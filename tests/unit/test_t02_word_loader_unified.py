"""
TDD tests for T02 Word Loader - Unified Interface Migration

Write these tests FIRST before implementing the unified interface.
These tests MUST fail initially (Red phase).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from typing import Dict, Any
import time
from pathlib import Path

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus
from src.core.service_manager import ServiceManager


class TestT02WordLoaderUnified:
    """Test-driven development for T02 Word Loader unified interface"""
    
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
        from src.tools.phase1.t02_word_loader_unified import T02WordLoaderUnified
        self.tool = T02WordLoaderUnified(self.mock_services)
    
    # ===== CONTRACT TESTS (MANDATORY) =====
    
    def test_tool_initialization(self):
        """Tool initializes with required services"""
        assert self.tool is not None
        assert self.tool.tool_id == "T02"
        assert self.tool.services == self.mock_services
        assert isinstance(self.tool, BaseTool)
    
    def test_get_contract(self):
        """Tool provides complete contract specification"""
        contract = self.tool.get_contract()
        
        assert isinstance(contract, ToolContract)
        assert contract.tool_id == "T02"
        assert contract.name == "Word Document Loader"
        assert contract.category == "document_processing"
        assert contract.description == "Load and extract text from Word documents (.docx)"
        
        # Verify input schema
        assert "file_path" in contract.input_schema["properties"]
        assert "workflow_id" in contract.input_schema["properties"]
        assert contract.input_schema["required"] == ["file_path"]
        
        # Verify output schema
        assert "document" in contract.output_schema["properties"]
        assert "text" in contract.output_schema["properties"]["document"]["properties"]
        assert "confidence" in contract.output_schema["properties"]["document"]["properties"]
        
        # Verify dependencies
        assert "identity_service" in contract.dependencies
        assert "provenance_service" in contract.dependencies
        assert "quality_service" in contract.dependencies
        
        # Verify performance requirements
        assert contract.performance_requirements["max_execution_time"] == 20.0
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
            {"file_path": "test.doc"},  # Old Word format not supported
        ]
        
        for invalid_input in invalid_inputs:
            request = ToolRequest(
                tool_id="T02",
                operation="load",
                input_data=invalid_input,
                parameters={}
            )
            result = self.tool.execute(request)
            assert result.status == "error"
            assert result.error_code in ["INVALID_INPUT", "VALIDATION_FAILED", "INVALID_FILE_TYPE", "FILE_NOT_FOUND"]
    
    def test_output_contract_compliance(self):
        """Tool output matches contract specification"""
        # Mock file operations
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_file_open:
            
            # Mock docx operations
            with patch('docx.Document') as mock_doc:
                # Setup mocks
                mock_stat.return_value.st_size = 1024 * 1024  # 1MB
                
                # Mock document structure
                mock_para1 = MagicMock()
                mock_para1.text = "First paragraph text"
                mock_para2 = MagicMock()
                mock_para2.text = "Second paragraph text"
                
                mock_doc_instance = MagicMock()
                mock_doc_instance.paragraphs = [mock_para1, mock_para2]
                mock_doc_instance.tables = []  # No tables for now
                mock_doc.return_value = mock_doc_instance
                
                # Mock service responses
                self.mock_provenance.start_operation.return_value = "op123"
                self.mock_provenance.complete_operation.return_value = {"status": "success"}
                self.mock_quality.assess_confidence.return_value = {
                    "status": "success",
                    "confidence": 0.95,
                    "quality_tier": "HIGH"
                }
                
                valid_input = {
                    "file_path": "test.docx",
                    "workflow_id": "wf_123"
                }
                
                request = ToolRequest(
                    tool_id="T02",
                    operation="load",
                    input_data=valid_input,
                    parameters={}
                )
                
                result = self.tool.execute(request)
                
                # Verify output structure
                assert result.status == "success"
                assert result.tool_id == "T02"
                assert "document" in result.data
                
                # Verify document structure
                document = result.data["document"]
                assert "document_id" in document
                assert "text" in document
                assert "confidence" in document
                assert "paragraph_count" in document
                assert "file_path" in document
                assert "file_size" in document
                
                # Verify metadata
                assert result.execution_time > 0
                assert result.memory_used >= 0
                assert "operation_id" in result.metadata
    
    # ===== FUNCTIONALITY TESTS (MANDATORY) =====
    
    def test_docx_loading_functionality(self):
        """Tool loads DOCX files correctly"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_file_open, \
             patch('docx.Document') as mock_doc:
            
            # Setup test data
            test_paragraphs = [
                "This is the first paragraph with some content.",
                "This is the second paragraph with more content.",
                "",  # Empty paragraph
                "Final paragraph with conclusion."
            ]
            
            mock_stat.return_value.st_size = 2 * 1024 * 1024  # 2MB
            
            # Create mock paragraphs
            mock_paragraphs = []
            for text in test_paragraphs:
                para = MagicMock()
                para.text = text
                mock_paragraphs.append(para)
            
            # Create mock table
            mock_table = MagicMock()
            mock_row1 = MagicMock()
            mock_cell1 = MagicMock()
            mock_cell1.text = "Cell 1"
            mock_cell2 = MagicMock()
            mock_cell2.text = "Cell 2"
            mock_row1.cells = [mock_cell1, mock_cell2]
            mock_table.rows = [mock_row1]
            
            mock_doc_instance = MagicMock()
            mock_doc_instance.paragraphs = mock_paragraphs
            mock_doc_instance.tables = [mock_table]
            mock_doc.return_value = mock_doc_instance
            
            # Mock services
            self.mock_provenance.start_operation.return_value = "op123"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.92,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T02",
                operation="load",
                input_data={"file_path": "test.docx"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert len(result.data["document"]["text"]) > 0
            assert result.data["document"]["paragraph_count"] == 3  # Empty paragraphs excluded
            assert result.data["document"]["table_count"] == 1
            assert result.data["document"]["confidence"] >= 0.9
    
    def test_docx_with_complex_formatting(self):
        """Tool handles complex formatting in Word documents"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_file_open, \
             patch('docx.Document') as mock_doc:
            
            mock_stat.return_value.st_size = 1024 * 500  # 500KB
            
            # Mock paragraphs with runs (formatted text)
            mock_para = MagicMock()
            run1 = MagicMock()
            run1.text = "Bold text "
            run1.bold = True
            run2 = MagicMock()
            run2.text = "and italic text"
            run2.italic = True
            mock_para.runs = [run1, run2]
            mock_para.text = "Bold text and italic text"
            
            mock_doc_instance = MagicMock()
            mock_doc_instance.paragraphs = [mock_para]
            mock_doc_instance.tables = []
            mock_doc.return_value = mock_doc_instance
            
            # Mock services
            self.mock_provenance.start_operation.return_value = "op124"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.90,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T02",
                operation="load",
                input_data={"file_path": "formatted.docx"},
                parameters={"preserve_formatting": False}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert "Bold text and italic text" in result.data["document"]["text"]
    
    def test_edge_case_empty_docx(self):
        """Tool handles empty DOCX files gracefully"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_file_open, \
             patch('docx.Document') as mock_doc:
            
            mock_stat.return_value.st_size = 1024
            
            mock_doc_instance = MagicMock()
            mock_doc_instance.paragraphs = []
            mock_doc_instance.tables = []
            mock_doc.return_value = mock_doc_instance
            
            self.mock_provenance.start_operation.return_value = "op125"
            
            request = ToolRequest(
                tool_id="T02",
                operation="load",
                input_data={"file_path": "empty.docx"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Should handle gracefully
            assert result.status in ["success", "error"]
            if result.status == "success":
                assert result.data["document"]["paragraph_count"] == 0
                assert result.data["document"]["text"] == ""
    
    def test_edge_case_large_docx(self):
        """Tool handles large DOCX files efficiently"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_file_open, \
             patch('docx.Document') as mock_doc:
            
            # 50MB file
            mock_stat.return_value.st_size = 50 * 1024 * 1024
            
            # Create many paragraphs
            mock_paragraphs = []
            for i in range(5000):
                para = MagicMock()
                para.text = f"Paragraph {i} with some content to make it realistic."
                mock_paragraphs.append(para)
            
            mock_doc_instance = MagicMock()
            mock_doc_instance.paragraphs = mock_paragraphs
            mock_doc_instance.tables = []
            mock_doc.return_value = mock_doc_instance
            
            self.mock_provenance.start_operation.return_value = "op126"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.95,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T02",
                operation="load",
                input_data={"file_path": "large.docx"},
                parameters={"memory_limit_mb": 500}
            )
            
            start_time = time.time()
            result = self.tool.execute(request)
            execution_time = time.time() - start_time
            
            assert result.status == "success"
            assert result.data["document"]["paragraph_count"] == 5000
            assert execution_time < 20.0  # Performance requirement
    
    def test_tables_extraction(self):
        """Tool extracts table content from Word documents"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_file_open, \
             patch('docx.Document') as mock_doc:
            
            mock_stat.return_value.st_size = 1024 * 200
            
            # Create mock table with 2x3 structure
            mock_table = MagicMock()
            mock_rows = []
            table_data = [
                ["Header 1", "Header 2", "Header 3"],
                ["Data 1", "Data 2", "Data 3"],
            ]
            
            for row_data in table_data:
                mock_row = MagicMock()
                mock_cells = []
                for cell_text in row_data:
                    mock_cell = MagicMock()
                    mock_cell.text = cell_text
                    mock_cells.append(mock_cell)
                mock_row.cells = mock_cells
                mock_rows.append(mock_row)
            
            mock_table.rows = mock_rows
            
            # Also add regular paragraph
            mock_para = MagicMock()
            mock_para.text = "Regular paragraph before table"
            
            mock_doc_instance = MagicMock()
            mock_doc_instance.paragraphs = [mock_para]
            mock_doc_instance.tables = [mock_table]
            mock_doc.return_value = mock_doc_instance
            
            self.mock_provenance.start_operation.return_value = "op127"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.93,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T02",
                operation="load",
                input_data={"file_path": "table_test.docx"},
                parameters={"extract_tables": True}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert result.data["document"]["table_count"] == 1
            assert "Header 1" in result.data["document"]["text"]
            assert "Data 1" in result.data["document"]["text"]
    
    # ===== INTEGRATION TESTS (MANDATORY) =====
    
    def test_identity_service_integration(self):
        """Tool integrates with IdentityService correctly"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_file_open, \
             patch('docx.Document') as mock_doc:
            
            mock_stat.return_value.st_size = 1024
            
            mock_para = MagicMock()
            mock_para.text = "Test content"
            mock_doc_instance = MagicMock()
            mock_doc_instance.paragraphs = [mock_para]
            mock_doc_instance.tables = []
            mock_doc.return_value = mock_doc_instance
            
            self.mock_provenance.start_operation.return_value = "op127"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.90,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T02",
                operation="load",
                input_data={"file_path": "test.docx", "workflow_id": "wf_123"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            # Verify document ID follows pattern
            assert result.data["document"]["document_id"].startswith("wf_123_")
    
    def test_provenance_tracking(self):
        """Tool tracks provenance correctly"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_file_open, \
             patch('docx.Document') as mock_doc:
            
            mock_stat.return_value.st_size = 100
            
            mock_para = MagicMock()
            mock_para.text = "Test"
            mock_doc_instance = MagicMock()
            mock_doc_instance.paragraphs = [mock_para]
            mock_doc_instance.tables = []
            mock_doc.return_value = mock_doc_instance
            
            # Setup provenance mock
            self.mock_provenance.start_operation.return_value = "op128"
            self.mock_provenance.complete_operation.return_value = {
                "status": "success",
                "operation_id": "op128"
            }
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.85,
                "quality_tier": "MEDIUM"
            }
            
            request = ToolRequest(
                tool_id="T02",
                operation="load",
                input_data={"file_path": "test.docx"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Verify provenance was tracked
            self.mock_provenance.start_operation.assert_called_once()
            call_args = self.mock_provenance.start_operation.call_args[1]
            assert call_args["tool_id"] == "T02"
            assert call_args["operation_type"] == "load_document"
            
            self.mock_provenance.complete_operation.assert_called_once()
            complete_args = self.mock_provenance.complete_operation.call_args[1]
            assert complete_args["operation_id"] == "op128"
            assert complete_args["success"] == True
    
    def test_quality_service_integration(self):
        """Tool integrates with quality service for confidence scoring"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_file_open, \
             patch('docx.Document') as mock_doc:
            
            mock_stat.return_value.st_size = 2048
            
            # Create multiple paragraphs
            mock_paragraphs = []
            for i in range(10):
                para = MagicMock()
                para.text = f"High quality content paragraph {i} " * 10
                mock_paragraphs.append(para)
            
            mock_doc_instance = MagicMock()
            mock_doc_instance.paragraphs = mock_paragraphs
            mock_doc_instance.tables = []
            mock_doc.return_value = mock_doc_instance
            
            self.mock_provenance.start_operation.return_value = "op129"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            
            # Mock quality assessment
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.96,
                "quality_tier": "HIGH",
                "factors": {
                    "text_length": 1.0,
                    "structure": 0.95
                }
            }
            
            request = ToolRequest(
                tool_id="T02",
                operation="load",
                input_data={"file_path": "quality_test.docx"},
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
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_file_open, \
             patch('docx.Document') as mock_doc:
            
            # Standard test file
            mock_stat.return_value.st_size = 5 * 1024 * 1024  # 5MB
            
            # Create realistic document
            mock_paragraphs = []
            for i in range(500):
                para = MagicMock()
                para.text = f"Paragraph {i} " * 100  # ~500 chars per paragraph
                mock_paragraphs.append(para)
            
            mock_doc_instance = MagicMock()
            mock_doc_instance.paragraphs = mock_paragraphs
            mock_doc_instance.tables = []
            mock_doc.return_value = mock_doc_instance
            
            self.mock_provenance.start_operation.return_value = "op130"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.93,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T02",
                operation="load",
                input_data={"file_path": "performance_test.docx"},
                parameters={}
            )
            
            # Measure performance
            start_time = time.time()
            result = self.tool.execute(request)
            execution_time = time.time() - start_time
            
            # Performance assertions
            assert result.status == "success"
            assert execution_time < 20.0  # Max 20 seconds
            assert result.execution_time < 20.0
            assert result.memory_used < 1024 * 1024 * 1024  # Max 1GB
    
    # ===== ERROR HANDLING TESTS =====
    
    def test_handles_corrupted_docx(self):
        """Tool handles corrupted DOCX files gracefully"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_file_open, \
             patch('docx.Document') as mock_doc:
            
            mock_stat.return_value.st_size = 1024
            # Simulate corrupted DOCX
            mock_doc.side_effect = Exception("Package not found")
            
            self.mock_provenance.start_operation.return_value = "op131"
            
            request = ToolRequest(
                tool_id="T02",
                operation="load",
                input_data={"file_path": "corrupted.docx"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code in ["DOCX_CORRUPTED", "EXTRACTION_FAILED"]
            assert "corrupted" in result.error_message.lower() or "package" in result.error_message.lower()
    
    def test_handles_password_protected_docx(self):
        """Tool handles password-protected DOCX appropriately"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_file_open, \
             patch('docx.Document') as mock_doc:
            
            mock_stat.return_value.st_size = 1024
            # Simulate password-protected file
            mock_doc.side_effect = Exception("File is password-protected")
            
            self.mock_provenance.start_operation.return_value = "op132"
            
            request = ToolRequest(
                tool_id="T02",
                operation="load",
                input_data={"file_path": "protected.docx"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code in ["DOCX_PROTECTED", "EXTRACTION_FAILED"]
            assert "password" in result.error_message.lower() or "protected" in result.error_message.lower()
    
    def test_handles_file_not_found(self):
        """Tool handles missing files appropriately"""
        with patch('pathlib.Path.exists', return_value=False):
            
            request = ToolRequest(
                tool_id="T02",
                operation="load",
                input_data={"file_path": "nonexistent.docx"},
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
        assert result.tool_id == "T02"
        assert result.status in ["success", "error"]
        
        if result.status == "success":
            assert result.data["healthy"] == True
            assert "supported_formats" in result.data
            assert ".docx" in result.data["supported_formats"]
    
    def test_cleanup(self):
        """Tool cleans up resources properly"""
        # Setup some mock resources
        self.tool._temp_files = ["temp1.docx", "temp2.docx"]
        
        success = self.tool.cleanup()
        
        assert success == True
        assert len(self.tool._temp_files) == 0