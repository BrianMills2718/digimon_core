"""
TDD tests for T01 PDF Loader - Unified Interface Migration

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


class TestT01PDFLoaderUnified:
    """Test-driven development for T01 PDF Loader unified interface"""
    
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
        from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
        self.tool = T01PDFLoaderUnified(self.mock_services)
    
    # ===== CONTRACT TESTS (MANDATORY) =====
    
    def test_tool_initialization(self):
        """Tool initializes with required services"""
        assert self.tool is not None
        assert self.tool.tool_id == "T01"
        assert self.tool.services == self.mock_services
        assert isinstance(self.tool, BaseTool)
    
    def test_get_contract(self):
        """Tool provides complete contract specification"""
        contract = self.tool.get_contract()
        
        assert isinstance(contract, ToolContract)
        assert contract.tool_id == "T01"
        assert contract.name == "PDF Document Loader"
        assert contract.category == "document_processing"
        assert contract.description == "Load and extract text from PDF documents with confidence scoring"
        
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
        assert contract.performance_requirements["max_execution_time"] == 30.0
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
            {"file_path": "test.exe"},  # Wrong extension
        ]
        
        for invalid_input in invalid_inputs:
            request = ToolRequest(
                tool_id="T01",
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
             patch('builtins.open', create=True) as mock_open, \
             patch('pypdf.PdfReader') as mock_pdf:
            
            # Setup mocks
            mock_stat.return_value.st_size = 1024 * 1024  # 1MB
            mock_pdf_instance = MagicMock()
            mock_pdf_instance.is_encrypted = False
            mock_pdf_instance.pages = [MagicMock(extract_text=lambda: "Test content")]
            mock_pdf.return_value = mock_pdf_instance
            
            # Mock service responses
            self.mock_provenance.start_operation.return_value = "op123"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.95,
                "quality_tier": "HIGH"
            }
            
            valid_input = {
                "file_path": "test.pdf",
                "workflow_id": "wf_123"
            }
            
            request = ToolRequest(
                tool_id="T01",
                operation="load",
                input_data=valid_input,
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Verify output structure
            assert result.status == "success"
            assert result.tool_id == "T01"
            assert "document" in result.data
            
            # Verify document structure
            document = result.data["document"]
            assert "document_id" in document
            assert "text" in document
            assert "confidence" in document
            assert "page_count" in document
            assert "file_path" in document
            assert "file_size" in document
            
            # Verify metadata
            assert result.execution_time > 0
            assert result.memory_used >= 0
            assert "operation_id" in result.metadata
    
    # ===== FUNCTIONALITY TESTS (MANDATORY) =====
    
    def test_pdf_loading_functionality(self):
        """Tool loads PDF files correctly"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_open, \
             patch('pypdf.PdfReader') as mock_pdf:
            
            # Setup test data
            test_text = "This is a test PDF content with multiple words."
            mock_stat.return_value.st_size = 2 * 1024 * 1024  # 2MB
            
            mock_pdf_instance = MagicMock()
            mock_pdf_instance.is_encrypted = False
            mock_pdf_instance.pages = [
                MagicMock(extract_text=lambda: test_text),
                MagicMock(extract_text=lambda: "Page 2 content")
            ]
            mock_pdf.return_value = mock_pdf_instance
            
            # Mock services
            self.mock_provenance.start_operation.return_value = "op123"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.92,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T01",
                operation="load",
                input_data={"file_path": "test.pdf"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert len(result.data["document"]["text"]) > 0
            assert result.data["document"]["page_count"] == 2
            assert result.data["document"]["confidence"] >= 0.9
    
    def test_text_file_loading(self):
        """Tool loads text files correctly"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data="Simple text content")):
            
            mock_stat.return_value.st_size = 1024  # 1KB
            
            # Mock services
            self.mock_provenance.start_operation.return_value = "op124"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.90,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T01",
                operation="load",
                input_data={"file_path": "test.txt"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert result.data["document"]["text"] == "Simple text content"
            assert result.data["document"]["page_count"] == 1
    
    def test_edge_case_empty_pdf(self):
        """Tool handles empty PDFs gracefully"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_open, \
             patch('pypdf.PdfReader') as mock_pdf:
            
            mock_stat.return_value.st_size = 1024
            mock_pdf_instance = MagicMock()
            mock_pdf_instance.is_encrypted = False
            mock_pdf_instance.pages = []  # Empty PDF
            mock_pdf.return_value = mock_pdf_instance
            
            self.mock_provenance.start_operation.return_value = "op125"
            
            request = ToolRequest(
                tool_id="T01",
                operation="load",
                input_data={"file_path": "empty.pdf"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Should handle gracefully
            assert result.status in ["success", "error"]
            if result.status == "success":
                assert result.data["document"]["page_count"] == 0
                assert result.data["document"]["text"] == ""
    
    def test_edge_case_large_pdf(self):
        """Tool handles large PDFs efficiently"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_open, \
             patch('pypdf.PdfReader') as mock_pdf:
            
            # 100MB file
            mock_stat.return_value.st_size = 100 * 1024 * 1024
            
            # Create many pages
            mock_pdf_instance = MagicMock()
            mock_pdf_instance.is_encrypted = False
            mock_pdf_instance.pages = [
                MagicMock(extract_text=lambda: f"Page {i} content")
                for i in range(1000)
            ]
            mock_pdf.return_value = mock_pdf_instance
            
            self.mock_provenance.start_operation.return_value = "op126"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.95,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T01",
                operation="load",
                input_data={"file_path": "large.pdf"},
                parameters={"memory_limit_mb": 500}
            )
            
            start_time = time.time()
            result = self.tool.execute(request)
            execution_time = time.time() - start_time
            
            assert result.status == "success"
            assert result.data["document"]["page_count"] == 1000
            assert execution_time < 30.0  # Performance requirement
    
    # ===== INTEGRATION TESTS (MANDATORY) =====
    
    def test_identity_service_integration(self):
        """Tool integrates with IdentityService correctly"""
        # This test verifies that the tool properly uses identity service
        # For PDF loader, this might be creating document identity
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data="Test content")):
            
            mock_stat.return_value.st_size = 1024
            
            self.mock_provenance.start_operation.return_value = "op127"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.90,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T01",
                operation="load",
                input_data={"file_path": "test.txt", "workflow_id": "wf_123"},
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
             patch('builtins.open', mock_open(read_data="Test")):
            
            mock_stat.return_value.st_size = 100
            
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
                tool_id="T01",
                operation="load",
                input_data={"file_path": "test.txt"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Verify provenance was tracked
            self.mock_provenance.start_operation.assert_called_once()
            call_args = self.mock_provenance.start_operation.call_args[1]
            assert call_args["tool_id"] == "T01"
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
             patch('builtins.open', mock_open(read_data="High quality content " * 100)):
            
            mock_stat.return_value.st_size = 2048
            
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
                tool_id="T01",
                operation="load",
                input_data={"file_path": "quality_test.txt"},
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
             patch('builtins.open', create=True) as mock_open, \
             patch('pypdf.PdfReader') as mock_pdf:
            
            # Standard test file
            mock_stat.return_value.st_size = 5 * 1024 * 1024  # 5MB
            
            mock_pdf_instance = MagicMock()
            mock_pdf_instance.is_encrypted = False
            mock_pdf_instance.pages = [
                MagicMock(extract_text=lambda: f"Page {i} " * 1000)
                for i in range(50)
            ]
            mock_pdf.return_value = mock_pdf_instance
            
            self.mock_provenance.start_operation.return_value = "op130"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.93,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T01",
                operation="load",
                input_data={"file_path": "performance_test.pdf"},
                parameters={}
            )
            
            # Measure performance
            start_time = time.time()
            result = self.tool.execute(request)
            execution_time = time.time() - start_time
            
            # Performance assertions
            assert result.status == "success"
            assert execution_time < 30.0  # Max 30 seconds
            assert result.execution_time < 30.0
            assert result.memory_used < 2048 * 1024 * 1024  # Max 2GB
    
    # ===== ERROR HANDLING TESTS =====
    
    def test_handles_corrupted_pdf(self):
        """Tool handles corrupted PDF files gracefully"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_open, \
             patch('pypdf.PdfReader') as mock_pdf:
            
            mock_stat.return_value.st_size = 1024
            # Simulate corrupted PDF
            mock_pdf.side_effect = Exception("PDF file is corrupted")
            
            self.mock_provenance.start_operation.return_value = "op131"
            
            request = ToolRequest(
                tool_id="T01",
                operation="load",
                input_data={"file_path": "corrupted.pdf"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code in ["PDF_CORRUPTED", "EXTRACTION_FAILED"]
            assert "corrupted" in result.error_message.lower()
    
    def test_handles_encrypted_pdf(self):
        """Tool handles encrypted PDFs appropriately"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', create=True) as mock_open, \
             patch('pypdf.PdfReader') as mock_pdf:
            
            mock_stat.return_value.st_size = 1024
            mock_pdf_instance = MagicMock()
            mock_pdf_instance.is_encrypted = True
            mock_pdf.return_value = mock_pdf_instance
            
            self.mock_provenance.start_operation.return_value = "op132"
            
            request = ToolRequest(
                tool_id="T01",
                operation="load",
                input_data={"file_path": "encrypted.pdf"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code == "PDF_ENCRYPTED"
            assert "encrypted" in result.error_message.lower()
    
    def test_handles_file_not_found(self):
        """Tool handles missing files appropriately"""
        with patch('pathlib.Path.exists', return_value=False):
            
            request = ToolRequest(
                tool_id="T01",
                operation="load",
                input_data={"file_path": "nonexistent.pdf"},
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
        assert result.tool_id == "T01"
        assert result.status in ["success", "error"]
        
        if result.status == "success":
            assert result.data["healthy"] == True
            assert "supported_formats" in result.data
            assert ".pdf" in result.data["supported_formats"]
            assert ".txt" in result.data["supported_formats"]
    
    def test_cleanup(self):
        """Tool cleans up resources properly"""
        # Setup some mock resources
        self.tool._temp_files = ["temp1.txt", "temp2.txt"]
        
        success = self.tool.cleanup()
        
        assert success == True
        assert len(self.tool._temp_files) == 0