"""
TDD tests for T03 Text Loader - Unified Interface Migration

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


class TestT03TextLoaderUnified:
    """Test-driven development for T03 Text Loader unified interface"""
    
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
        from src.tools.phase1.t03_text_loader_unified import T03TextLoaderUnified
        self.tool = T03TextLoaderUnified(self.mock_services)
    
    # ===== CONTRACT TESTS (MANDATORY) =====
    
    def test_tool_initialization(self):
        """Tool initializes with required services"""
        assert self.tool is not None
        assert self.tool.tool_id == "T03"
        assert self.tool.services == self.mock_services
        assert isinstance(self.tool, BaseTool)
    
    def test_get_contract(self):
        """Tool provides complete contract specification"""
        contract = self.tool.get_contract()
        
        assert isinstance(contract, ToolContract)
        assert contract.tool_id == "T03"
        assert contract.name == "Text Document Loader"
        assert contract.category == "document_processing"
        assert contract.description == "Load plain text documents with encoding detection"
        
        # Verify input schema
        assert "file_path" in contract.input_schema["properties"]
        assert "workflow_id" in contract.input_schema["properties"]
        assert contract.input_schema["required"] == ["file_path"]
        
        # Verify output schema
        assert "document" in contract.output_schema["properties"]
        assert "text" in contract.output_schema["properties"]["document"]["properties"]
        assert "encoding" in contract.output_schema["properties"]["document"]["properties"]
        assert "confidence" in contract.output_schema["properties"]["document"]["properties"]
        
        # Verify dependencies
        assert "identity_service" in contract.dependencies
        assert "provenance_service" in contract.dependencies
        assert "quality_service" in contract.dependencies
        
        # Verify performance requirements
        assert contract.performance_requirements["max_execution_time"] == 5.0
        assert contract.performance_requirements["max_memory_mb"] == 512
    
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
            {"file_path": "test.docx"},  # Not text
        ]
        
        for invalid_input in invalid_inputs:
            request = ToolRequest(
                tool_id="T03",
                operation="load",
                input_data=invalid_input,
                parameters={}
            )
            result = self.tool.execute(request)
            assert result.status == "error"
            assert result.error_code in ["INVALID_INPUT", "VALIDATION_FAILED", "INVALID_FILE_TYPE", "FILE_NOT_FOUND"]
    
    def test_output_contract_compliance(self):
        """Tool output matches contract specification"""
        # Mock text content
        text_content = "This is a sample text document.\nIt has multiple lines.\nAnd some special characters: é à ñ"
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=text_content)):
            
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
                "file_path": "test.txt",
                "workflow_id": "wf_123"
            }
            
            request = ToolRequest(
                tool_id="T03",
                operation="load",
                input_data=valid_input,
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Verify output structure
            assert result.status == "success"
            assert result.tool_id == "T03"
            assert "document" in result.data
            
            # Verify document structure
            document = result.data["document"]
            assert "document_id" in document
            assert "text" in document
            assert "encoding" in document
            assert "confidence" in document
            assert "file_path" in document
            assert "file_size" in document
            assert "line_count" in document
            
            # Verify metadata
            assert result.execution_time > 0
            assert result.memory_used >= 0
            assert "operation_id" in result.metadata
    
    # ===== FUNCTIONALITY TESTS (MANDATORY) =====
    
    def test_simple_text_loading(self):
        """Tool loads simple text files correctly"""
        text_content = """Hello World
This is a simple text file.
It contains plain text content."""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=text_content)):
            
            mock_stat.return_value.st_size = len(text_content)
            
            # Mock services
            self.mock_provenance.start_operation.return_value = "op123"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.95,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T03",
                operation="load",
                input_data={"file_path": "simple.txt"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert result.data["document"]["text"] == text_content
            assert result.data["document"]["line_count"] == 3
            assert result.data["document"]["encoding"] == "utf-8"
            assert result.data["document"]["confidence"] >= 0.9
    
    def test_encoding_detection(self):
        """Tool detects and handles different encodings"""
        # Test UTF-8 with BOM
        utf8_bom = b'\xef\xbb\xbfHello UTF-8 with BOM'
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=utf8_bom)) as mock_file:
            
            # Mock chardet for encoding detection
            with patch('chardet.detect') as mock_chardet:
                mock_chardet.return_value = {'encoding': 'utf-8-sig', 'confidence': 0.99}
                
                mock_stat.return_value.st_size = len(utf8_bom)
                
                self.mock_provenance.start_operation.return_value = "op124"
                self.mock_provenance.complete_operation.return_value = {"status": "success"}
                self.mock_quality.assess_confidence.return_value = {
                    "status": "success",
                    "confidence": 0.92,
                    "quality_tier": "HIGH"
                }
                
                request = ToolRequest(
                    tool_id="T03",
                    operation="load",
                    input_data={"file_path": "utf8_bom.txt"},
                    parameters={"detect_encoding": True}
                )
                
                result = self.tool.execute(request)
                
                assert result.status == "success"
                assert result.data["document"]["encoding"] in ["utf-8-sig", "utf-8"]
                assert "encoding_confidence" in result.data["document"]
    
    def test_large_text_file(self):
        """Tool handles large text files efficiently"""
        # Create large text content
        large_text = "\n".join([f"Line {i}: " + "x" * 100 for i in range(10000)])
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=large_text)):
            
            # 1MB file
            mock_stat.return_value.st_size = 1024 * 1024
            
            self.mock_provenance.start_operation.return_value = "op125"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.95,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T03",
                operation="load",
                input_data={"file_path": "large.txt"},
                parameters={}
            )
            
            start_time = time.time()
            result = self.tool.execute(request)
            execution_time = time.time() - start_time
            
            assert result.status == "success"
            assert result.data["document"]["line_count"] == 10000
            assert execution_time < 5.0  # Performance requirement
    
    def test_special_characters_and_unicode(self):
        """Tool handles special characters and unicode correctly"""
        unicode_text = """Unicode Test File
Contains various characters:
- Emojis: 😀 🌟 🚀
- Accents: café, naïve, résumé
- Asian: 你好 こんにちは 안녕하세요
- Symbols: ™ © ® € £ ¥
- Math: ∑ ∏ √ ∞ ≈ ≠"""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=unicode_text)):
            
            mock_stat.return_value.st_size = len(unicode_text.encode('utf-8'))
            
            self.mock_provenance.start_operation.return_value = "op126"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.93,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T03",
                operation="load",
                input_data={"file_path": "unicode.txt"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            assert "😀" in result.data["document"]["text"]
            assert "café" in result.data["document"]["text"]
            assert "你好" in result.data["document"]["text"]
            assert result.data["document"]["has_unicode"] == True
    
    def test_empty_file_handling(self):
        """Tool handles empty files gracefully"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data="")):
            
            mock_stat.return_value.st_size = 0
            
            self.mock_provenance.start_operation.return_value = "op127"
            
            request = ToolRequest(
                tool_id="T03",
                operation="load",
                input_data={"file_path": "empty.txt"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Should handle gracefully
            assert result.status in ["success", "error"]
            if result.status == "success":
                assert result.data["document"]["text"] == ""
                assert result.data["document"]["line_count"] == 0
                assert result.data["document"]["confidence"] < 0.5  # Low confidence for empty
    
    def test_line_ending_normalization(self):
        """Tool normalizes different line endings"""
        # Test Windows (CRLF), Unix (LF), and old Mac (CR) line endings
        mixed_endings = "Line 1\r\nLine 2\nLine 3\rLine 4"
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=mixed_endings)):
            
            mock_stat.return_value.st_size = len(mixed_endings)
            
            self.mock_provenance.start_operation.return_value = "op128"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.91,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T03",
                operation="load",
                input_data={"file_path": "mixed_endings.txt"},
                parameters={"normalize_line_endings": True}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success"
            # Should normalize to consistent line endings
            text = result.data["document"]["text"]
            assert "\r\n" not in text or "\n" not in text  # One or the other, not mixed
            assert result.data["document"]["line_count"] == 4
    
    # ===== INTEGRATION TESTS (MANDATORY) =====
    
    def test_identity_service_integration(self):
        """Tool integrates with IdentityService correctly"""
        text_content = "Test document for identity service."
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=text_content)):
            
            mock_stat.return_value.st_size = len(text_content)
            
            self.mock_provenance.start_operation.return_value = "op129"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.90,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T03",
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
        text_content = "Provenance test content"
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=text_content)):
            
            mock_stat.return_value.st_size = len(text_content)
            
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
                tool_id="T03",
                operation="load",
                input_data={"file_path": "test.txt"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Verify provenance was tracked
            self.mock_provenance.start_operation.assert_called_once()
            call_args = self.mock_provenance.start_operation.call_args[1]
            assert call_args["tool_id"] == "T03"
            assert call_args["operation_type"] == "load_document"
            
            self.mock_provenance.complete_operation.assert_called_once()
            complete_args = self.mock_provenance.complete_operation.call_args[1]
            assert complete_args["operation_id"] == "op130"
            assert complete_args["success"] == True
    
    def test_quality_service_integration(self):
        """Tool integrates with quality service for confidence scoring"""
        text_content = """High quality document with substantial content.
        Multiple paragraphs of text.
        Clear structure and formatting.
        Good encoding and no errors."""
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=text_content)):
            
            mock_stat.return_value.st_size = len(text_content)
            
            self.mock_provenance.start_operation.return_value = "op131"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            
            # Mock quality assessment
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.96,
                "quality_tier": "HIGH",
                "factors": {
                    "text_quality": 0.95,
                    "encoding_confidence": 0.98
                }
            }
            
            request = ToolRequest(
                tool_id="T03",
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
        # Create moderately large text
        test_text = "\n".join([f"Line {i}: " + "x" * 200 for i in range(5000)])
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data=test_text)):
            
            # 1MB file
            mock_stat.return_value.st_size = 1024 * 1024
            
            self.mock_provenance.start_operation.return_value = "op132"
            self.mock_provenance.complete_operation.return_value = {"status": "success"}
            self.mock_quality.assess_confidence.return_value = {
                "status": "success",
                "confidence": 0.93,
                "quality_tier": "HIGH"
            }
            
            request = ToolRequest(
                tool_id="T03",
                operation="load",
                input_data={"file_path": "performance_test.txt"},
                parameters={}
            )
            
            # Measure performance
            start_time = time.time()
            result = self.tool.execute(request)
            execution_time = time.time() - start_time
            
            # Performance assertions
            assert result.status == "success"
            assert execution_time < 5.0  # Max 5 seconds
            assert result.execution_time < 5.0
            assert result.memory_used < 512 * 1024 * 1024  # Max 512MB
    
    # ===== ERROR HANDLING TESTS =====
    
    def test_handles_file_not_found(self):
        """Tool handles missing files appropriately"""
        with patch('pathlib.Path.exists', return_value=False):
            
            request = ToolRequest(
                tool_id="T03",
                operation="load",
                input_data={"file_path": "nonexistent.txt"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code == "FILE_NOT_FOUND"
            assert "not found" in result.error_message.lower()
    
    def test_handles_permission_error(self):
        """Tool handles permission errors gracefully"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', side_effect=PermissionError("Permission denied")):
            
            mock_stat.return_value.st_size = 1024
            
            self.mock_provenance.start_operation.return_value = "op133"
            
            request = ToolRequest(
                tool_id="T03",
                operation="load",
                input_data={"file_path": "protected.txt"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "error"
            assert result.error_code in ["PERMISSION_DENIED", "FILE_ACCESS_ERROR"]
            assert "permission" in result.error_message.lower()
    
    def test_handles_encoding_errors(self):
        """Tool handles encoding errors appropriately"""
        # Binary data that can't be decoded as text
        binary_data = b'\x80\x81\x82\x83\x84\x85'
        
        def mock_open_binary(*args, **kwargs):
            # Simulate opening a file with binary data that fails to decode
            if 'r' in args[1]:
                raise UnicodeDecodeError('utf-8', binary_data, 0, len(binary_data), 'invalid start byte')
            else:
                m = MagicMock()
                m.read.return_value = binary_data
                m.__enter__.return_value = m
                return m
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open_binary):
            
            mock_stat.return_value.st_size = len(binary_data)
            
            self.mock_provenance.start_operation.return_value = "op134"
            
            request = ToolRequest(
                tool_id="T03",
                operation="load",
                input_data={"file_path": "binary.txt"},
                parameters={}
            )
            
            result = self.tool.execute(request)
            
            # Should handle encoding error gracefully
            assert result.status == "error"
            assert result.error_code in ["ENCODING_ERROR", "DECODING_FAILED"]
            assert "encoding" in result.error_message.lower() or "decode" in result.error_message.lower()
    
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
        assert result.tool_id == "T03"
        assert result.status in ["success", "error"]
        
        if result.status == "success":
            assert result.data["healthy"] == True
            assert "supported_formats" in result.data
            assert ".txt" in result.data["supported_formats"]
    
    def test_cleanup(self):
        """Tool cleans up resources properly"""
        # Setup some mock resources
        self.tool._temp_files = ["temp1.txt", "temp2.txt"]
        
        success = self.tool.cleanup()
        
        assert success == True
        assert len(self.tool._temp_files) == 0