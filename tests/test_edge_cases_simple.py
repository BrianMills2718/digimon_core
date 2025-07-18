"""Simplified edge case testing for core functionality

Tests tools with malformed inputs to ensure proper error handling.
"""

import pytest
import json
import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.evidence_logger import EvidenceLogger


class TestEdgeCasesSimple:
    """Simplified edge case testing"""
    
    def test_evidence_logger_methods(self):
        """Test that new evidence logger methods work correctly"""
        evidence_logger = EvidenceLogger("test_evidence.md")
        
        # Test log_error_scenario_test
        evidence_logger.log_error_scenario_test(
            test_name="Test Error Scenario",
            error_scenario="Testing error logging",
            expected_behavior="Should log without error",
            actual_behavior="Logged successfully",
            error_handled_correctly=True
        )
        
        # Test log_performance_boundary_test
        evidence_logger.log_performance_boundary_test(
            component="Test Component",
            test_type="Boundary Test",
            input_size=1000,
            processing_time=1.5,
            memory_usage=100.0,
            success=True,
            failure_reason=None
        )
        
        # Verify file was created and has content
        assert os.path.exists("test_evidence.md")
        
        with open("test_evidence.md", "r") as f:
            content = f.read()
            assert "ERROR SCENARIO TEST" in content
            assert "PERFORMANCE BOUNDARY TEST" in content
        
        # Cleanup
        os.remove("test_evidence.md")
    
    def test_malformed_input_handling_basic(self):
        """Basic test for malformed input handling"""
        from src.tools.phase1.t01_pdf_loader import PDFLoader
        
        evidence_logger = EvidenceLogger()
        pdf_loader = PDFLoader()
        
        # Test with nonexistent file
        result = pdf_loader.load_pdf("nonexistent.pdf")
        
        # Log the result
        evidence_logger.log_error_scenario_test(
            test_name="PDF Loader - Nonexistent File",
            error_scenario="Loading nonexistent PDF file",
            expected_behavior="Should return error result",
            actual_behavior=json.dumps(result, indent=2),
            error_handled_correctly="error" in result or result.get("status") == "error"
        )
        
        # Verify error was handled
        assert "error" in result or result.get("status") == "error", "PDFLoader should handle nonexistent file gracefully"
    
    def test_boundary_condition_basic(self):
        """Basic boundary condition test"""
        from src.tools.phase1.t15a_text_chunker import TextChunker
        
        evidence_logger = EvidenceLogger()
        text_chunker = TextChunker()
        
        # Test with empty document
        result = text_chunker.chunk_text(
            document_ref="doc_ref_1",
            text=""
        )
        
        # Log the result
        evidence_logger.log_performance_boundary_test(
            component="TextChunker",
            test_type="Empty Input",
            input_size=0,
            processing_time=0.001,
            memory_usage=0.0,
            success="error" in result or result.get("status") == "error",
            failure_reason=None if "error" in result else "Should have error for empty input"
        )
        
        # Verify it handled empty input with error
        assert "error" in result or result.get("status") == "error", "TextChunker should return error for empty input"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])