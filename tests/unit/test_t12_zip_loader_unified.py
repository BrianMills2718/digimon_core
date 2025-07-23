"""
Mock-Free Tests for T12 Zip Archive Loader Unified
Tests real ZIP archive processing with zipfile module
No mocking - uses real ZIP files and actual zipfile operations
"""

import pytest
import tempfile
import zipfile
import os
from pathlib import Path
from src.tools.phase1.t12_zip_loader_unified import T12ZipLoaderUnified
from src.core.service_manager import ServiceManager
from src.tools.base_tool import ToolRequest, ToolErrorCode


class TestT12ZipLoaderUnifiedMockFree:
    """Mock-free tests using real ZIP archive processing"""
    
    def setup_method(self):
        """Setup with real ServiceManager and test data - NO mocks"""
        self.service_manager = ServiceManager()
        self.tool = T12ZipLoaderUnified(service_manager=self.service_manager)
        
        # Create real test ZIP files
        self.test_files = self._create_real_test_zip_files()
    
    def _create_real_test_zip_files(self) -> dict:
        """Create actual ZIP files for testing - NO synthetic data"""
        test_files = {}
        
        # Create simple ZIP with text files
        simple_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        with zipfile.ZipFile(simple_zip.name, 'w') as zf:
            zf.writestr("document1.txt", "This is the content of document 1.\nLine 2 of document 1.")
            zf.writestr("document2.txt", "Content of document 2\nAnother line\nThird line")
            zf.writestr("readme.md", "# README\nThis is a markdown file\n## Section")
        test_files['simple'] = simple_zip.name
        
        # Create ZIP with mixed file types
        mixed_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        with zipfile.ZipFile(mixed_zip.name, 'w') as zf:
            zf.writestr("data.csv", "name,age,city\nJohn,25,NYC\nJane,30,LA")
            zf.writestr("config.json", '{"setting1": true, "setting2": "value"}')
            zf.writestr("script.py", "print('Hello World')\nfor i in range(5):\n    print(i)")
            zf.writestr("binary.dat", b"\x00\x01\x02\x03\x04\x05")  # Binary data
        test_files['mixed'] = mixed_zip.name
        
        # Create ZIP with directory structure
        structured_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        with zipfile.ZipFile(structured_zip.name, 'w') as zf:
            zf.writestr("folder1/file1.txt", "File in folder 1")
            zf.writestr("folder1/subfolder/nested.txt", "Nested file content")
            zf.writestr("folder2/file2.txt", "File in folder 2")
            zf.writestr("root.txt", "File in root directory")
        test_files['structured'] = structured_zip.name
        
        # Create large ZIP for performance testing
        large_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        with zipfile.ZipFile(large_zip.name, 'w') as zf:
            for i in range(50):
                content = f"This is file {i}\n" + "Content line\n" * 20
                zf.writestr(f"file_{i:03d}.txt", content)
        test_files['large'] = large_zip.name
        
        # Create compressed ZIP to test compression ratios
        compressed_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        with zipfile.ZipFile(compressed_zip.name, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            # Highly compressible content
            repeated_content = "This line repeats many times.\n" * 1000
            zf.writestr("repeated.txt", repeated_content)
            # Less compressible content
            zf.writestr("random.txt", "Random content with varied text patterns and numbers 123456789")
        test_files['compressed'] = compressed_zip.name
        
        # Create empty ZIP
        empty_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        with zipfile.ZipFile(empty_zip.name, 'w') as zf:
            pass  # Empty ZIP
        test_files['empty'] = empty_zip.name
        
        return test_files
    
    def teardown_method(self):
        """Clean up real test files"""
        for zip_path in self.test_files.values():
            if os.path.exists(zip_path):
                os.unlink(zip_path)
    
    def test_simple_zip_extraction_real(self):
        """Test basic ZIP extraction with real zipfile processing"""
        request = ToolRequest(
            tool_id="T12",
            operation="extract", 
            input_data={
                "zip_path": self.test_files['simple'],
                "extract_all": True
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        # Verify successful extraction
        assert result.status == "success"
        assert result.data["file_count"] == 3
        assert result.data["total_files_in_archive"] == 3
        assert result.metadata["confidence"] > 0.7
        assert result.execution_time > 0
        
        # Verify file details
        extracted_files = result.data["extracted_files"]
        assert len(extracted_files) == 3
        
        # Check specific files were extracted
        file_names = [f["name"] for f in extracted_files]
        assert "document1.txt" in file_names
        assert "document2.txt" in file_names
        assert "readme.md" in file_names
        
        # Verify content previews exist
        for file_info in extracted_files:
            assert "content_preview" in file_info
            assert file_info["content_preview"] != ""
            assert file_info["size"] > 0
    
    def test_mixed_file_types_real(self):
        """Test ZIP with mixed file types using real processing"""
        request = ToolRequest(
            tool_id="T12",
            operation="extract",
            input_data={
                "zip_path": self.test_files['mixed'],
                "extract_all": True
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert result.data["file_count"] == 4
        
        # Verify different file types handled
        extracted_files = result.data["extracted_files"]
        file_extensions = [Path(f["name"]).suffix for f in extracted_files]
        assert ".csv" in file_extensions
        assert ".json" in file_extensions  
        assert ".py" in file_extensions
        assert ".dat" in file_extensions
        
        # Check binary file detection
        binary_files = [f for f in extracted_files if f["content_preview"] == "<binary_content>"]
        assert len(binary_files) == 1  # binary.dat should be detected as binary
    
    def test_directory_structure_handling_real(self):
        """Test ZIP with directory structure using real zipfile operations"""
        request = ToolRequest(
            tool_id="T12",
            operation="extract",
            input_data={"zip_path": self.test_files['structured']}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert result.data["file_count"] == 4
        
        # Verify directory paths preserved
        extracted_files = result.data["extracted_files"]
        file_paths = [f["name"] for f in extracted_files]
        
        assert "folder1/file1.txt" in file_paths
        assert "folder1/subfolder/nested.txt" in file_paths
        assert "folder2/file2.txt" in file_paths
        assert "root.txt" in file_paths
    
    def test_file_extension_filtering_real(self):
        """Test filtering by file extensions with real ZIP processing"""
        request = ToolRequest(
            tool_id="T12",
            operation="extract",
            input_data={
                "zip_path": self.test_files['mixed'],
                "allowed_extensions": [".txt", ".py"]
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Should only extract files with allowed extensions
        extracted_files = result.data["extracted_files"]
        for file_info in extracted_files:
            file_ext = Path(file_info["name"]).suffix
            assert file_ext in [".py"]  # Only .py in mixed zip, .txt files not present
    
    def test_max_files_limit_real(self):
        """Test file count limiting with real large ZIP"""
        request = ToolRequest(
            tool_id="T12", 
            operation="extract",
            input_data={
                "zip_path": self.test_files['large'],
                "max_files": 10
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert result.data["file_count"] == 10  # Limited to 10
        assert result.data["total_files_in_archive"] == 50  # Original count
        
        # Verify only first 10 files processed
        extracted_files = result.data["extracted_files"]
        assert len(extracted_files) == 10
    
    def test_compression_ratio_calculation_real(self):
        """Test compression ratio calculation with real compressed ZIP"""
        request = ToolRequest(
            tool_id="T12",
            operation="extract", 
            input_data={"zip_path": self.test_files['compressed']}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Verify compression metrics
        assert "compression_ratio" in result.data
        assert result.data["compression_ratio"] > 0  # Should have some compression
        assert result.data["total_size"] > result.data["compressed_size"]
        
        # Check individual file compression ratios
        extracted_files = result.data["extracted_files"]
        for file_info in extracted_files:
            assert "compression_ratio" in file_info
            assert file_info["compression_ratio"] >= 0
    
    def test_extract_all_false_real(self):
        """Test listing files without extraction using real ZIP operations"""
        request = ToolRequest(
            tool_id="T12",
            operation="list",
            input_data={
                "zip_path": self.test_files['simple'],
                "extract_all": False
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert result.data["file_count"] == 3
        
        # Content should not be extracted, only listed
        extracted_files = result.data["extracted_files"]
        for file_info in extracted_files:
            assert file_info["content_preview"] == "<not_extracted>"
    
    def test_empty_zip_handling_real(self):
        """Test empty ZIP file handling with real zipfile operations"""
        request = ToolRequest(
            tool_id="T12",
            operation="extract",
            input_data={"zip_path": self.test_files['empty']}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert result.data["file_count"] == 0
        assert result.data["total_files_in_archive"] == 0
        assert len(result.data["extracted_files"]) == 0
        assert result.metadata["confidence"] > 0.4  # Should still have some confidence
    
    def test_invalid_zip_path_real(self):
        """Test handling of non-existent ZIP file with real error conditions"""
        request = ToolRequest(
            tool_id="T12",
            operation="extract",
            input_data={"zip_path": "/nonexistent/path/file.zip"}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "error"
        assert result.error_code == ToolErrorCode.FILE_NOT_FOUND
        assert result.execution_time > 0
    
    def test_corrupted_zip_file_real(self):
        """Test handling of corrupted ZIP file with real error conditions"""
        # Create a fake ZIP file (not actually ZIP format)
        fake_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        fake_zip.write(b"This is not a ZIP file content")
        fake_zip.close()
        
        try:
            request = ToolRequest(
                tool_id="T12",
                operation="extract",
                input_data={"zip_path": fake_zip.name}
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "error" 
            assert result.error_code == ToolErrorCode.ZIP_CORRUPTED
            
        finally:
            os.unlink(fake_zip.name)
    
    def test_missing_input_data_real(self):
        """Test handling of missing input data with real validation"""
        request = ToolRequest(
            tool_id="T12",
            operation="extract",
            input_data={}  # Missing zip_path
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "error"
        assert result.error_code == ToolErrorCode.INVALID_INPUT
    
    def test_service_integration_real(self):
        """Test ServiceManager integration with real services"""
        request = ToolRequest(
            tool_id="T12",
            operation="extract",
            input_data={"zip_path": self.test_files['simple']}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Verify service integration occurred
        metadata = result.metadata
        assert "identity_tracked" in metadata
        assert "provenance_logged" in metadata  
        assert "quality_assessed" in metadata
        
        # Services should have attempted tracking (success depends on service implementation)
        assert isinstance(metadata["identity_tracked"], bool)
        assert isinstance(metadata["provenance_logged"], bool)
        assert isinstance(metadata["quality_assessed"], bool)
    
    def test_performance_tracking_real(self):
        """Test performance tracking with real execution metrics"""
        request = ToolRequest(
            tool_id="T12",
            operation="extract",
            input_data={"zip_path": self.test_files['large']}  # Use large file for measurable performance
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert result.execution_time > 0
        assert hasattr(result, 'memory_used')
        
        # Large file should take measurable time
        assert result.execution_time > 0.001  # At least 1ms
    
    def test_tool_contract_real(self):
        """Test tool contract specification with real implementation"""
        contract = self.tool.get_contract()
        
        # Verify contract structure
        assert contract["tool_id"] == "T12"
        assert contract["name"] == "Zip Archive Loader"
        assert contract["category"] == "document_processing"
        assert "input_specification" in contract
        assert "output_specification" in contract
        assert "error_codes" in contract
        
        # Verify input specification
        input_spec = contract["input_specification"]
        assert "zip_path" in input_spec
        assert input_spec["zip_path"]["required"] is True
        assert "extract_all" in input_spec
        assert "max_files" in input_spec
        
        # Verify error codes
        error_codes = contract["error_codes"]
        assert ToolErrorCode.INVALID_INPUT in error_codes
        assert ToolErrorCode.FILE_NOT_FOUND in error_codes
        assert ToolErrorCode.ZIP_CORRUPTED in error_codes
    
    def test_health_check_real(self):
        """Test health check functionality with real zipfile operations"""
        health_result = self.tool.health_check()
        
        assert "status" in health_result
        assert health_result["status"] in ["healthy", "unhealthy"]
        assert "zipfile_available" in health_result
        assert health_result["zipfile_available"] is True
        assert "test_extraction" in health_result
        assert health_result["test_extraction"] is True
    
    def test_cleanup_functionality_real(self):
        """Test cleanup functionality with real resource management"""
        # Cleanup should not raise exceptions
        try:
            self.tool.cleanup()
            cleanup_success = True
        except Exception:
            cleanup_success = False
        
        assert cleanup_success is True
    
    def test_confidence_calculation_real(self):
        """Test confidence calculation with different ZIP scenarios"""
        # Test high confidence with good content
        request_good = ToolRequest(
            tool_id="T12",
            operation="extract",
            input_data={"zip_path": self.test_files['mixed']}
        )
        result_good = self.tool.execute(request_good)
        
        # Test lower confidence with empty ZIP
        request_empty = ToolRequest(
            tool_id="T12", 
            operation="extract",
            input_data={"zip_path": self.test_files['empty']}
        )
        result_empty = self.tool.execute(request_empty)
        
        assert result_good.status == "success"
        assert result_empty.status == "success"
        
        # Good content should have higher confidence than empty
        assert result_good.metadata["confidence"] > result_empty.metadata["confidence"]
        assert result_good.metadata["confidence"] > 0.7
        assert result_empty.metadata["confidence"] > 0.4
    
    def test_large_file_handling_real(self):
        """Test handling of ZIP with many files using real processing"""
        request = ToolRequest(
            tool_id="T12",
            operation="extract",
            input_data={
                "zip_path": self.test_files['large'],
                "max_files": 25  # Process moderate number
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert result.data["file_count"] == 25
        assert result.data["total_files_in_archive"] == 50
        
        # Verify extraction summary
        summary = result.data["extraction_summary"]
        assert summary["total_files"] == 25
        assert summary["text_files"] > 0  # Should detect text files
        assert "average_compression" in summary