"""
Unit tests for T15A Text Chunker with unified interface.

Tests follow TDD principles - written before implementation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
from datetime import datetime

from src.tools.base_tool import ToolRequest, ToolResult, ToolContract
from src.core.service_manager import ServiceManager


class TestT15ATextChunkerUnified:
    """Test suite for T15A Text Chunker with unified interface"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Mock service manager
        self.service_manager = Mock()
        
        # Mock services
        self.mock_identity = Mock()
        self.mock_provenance = Mock()
        self.mock_quality = Mock()
        
        self.service_manager.identity_service = self.mock_identity
        self.service_manager.provenance_service = self.mock_provenance
        self.service_manager.quality_service = self.mock_quality
        
        # Configure mock returns
        self.mock_provenance.start_operation.return_value = "op123"
        self.mock_provenance.complete_operation.return_value = {"status": "success"}
        self.mock_quality.assess_confidence.return_value = {
            "status": "success",
            "confidence": 0.85,
            "quality_tier": "HIGH"
        }
        self.mock_quality.propagate_confidence.return_value = 0.8
        
        # Import will fail until implementation exists
        try:
            from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
            self.tool = T15ATextChunkerUnified(self.service_manager)
        except ImportError:
            pytest.skip("T15A Text Chunker Unified not implemented yet")
    
    def test_tool_initialization(self):
        """Tool initializes with correct tool ID and services"""
        assert self.tool.tool_id == "T15A"
        assert self.tool.identity_service == self.mock_identity
        assert self.tool.provenance_service == self.mock_provenance
        assert self.tool.quality_service == self.mock_quality
    
    def test_get_contract(self):
        """Tool returns proper contract specification"""
        contract = self.tool.get_contract()
        
        assert isinstance(contract, ToolContract)
        assert contract.tool_id == "T15A"
        assert contract.name == "Text Chunker"
        assert contract.description == "Split text into overlapping chunks for processing"
        assert contract.category == "document_processing"
        
        # Verify input schema
        assert "text" in contract.input_schema["properties"]
        assert "document_ref" in contract.input_schema["properties"]
        assert "text" in contract.input_schema["required"]
        
        # Verify output schema
        assert "chunks" in contract.output_schema["properties"]
        assert "total_chunks" in contract.output_schema["properties"]
        
        # Verify dependencies
        assert "identity_service" in contract.dependencies
        assert "provenance_service" in contract.dependencies
        assert "quality_service" in contract.dependencies
    
    def test_input_contract_validation(self):
        """Tool validates input against contract"""
        # Valid input
        valid_input = {
            "text": "This is some text to chunk",
            "document_ref": "storage://document/doc123"
        }
        assert self.tool.validate_input(valid_input) == True
        
        # Missing required field
        invalid_input = {
            "document_ref": "storage://document/doc123"
        }
        assert self.tool.validate_input(invalid_input) == False
        
        # Empty text
        empty_text = {
            "text": "",
            "document_ref": "storage://document/doc123"
        }
        assert self.tool.validate_input(empty_text) == False
    
    def test_output_contract_compliance(self):
        """Tool output complies with contract schema"""
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "text": "This is a test document with enough content to create multiple chunks.",
                "document_ref": "storage://document/doc123"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert "chunks" in result.data
        assert "total_chunks" in result.data
        assert "total_tokens" in result.data
        
        # Verify chunk structure
        chunks = result.data["chunks"]
        assert len(chunks) > 0
        
        for chunk in chunks:
            assert "chunk_id" in chunk
            assert "chunk_ref" in chunk
            assert "text" in chunk
            assert "token_count" in chunk
            assert "char_start" in chunk
            assert "char_end" in chunk
            assert "confidence" in chunk
    
    def test_simple_text_chunking(self):
        """Tool chunks simple text correctly"""
        text = "The quick brown fox jumps over the lazy dog. " * 20  # Repeat to ensure multiple chunks
        
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "text": text,
                "document_ref": "storage://document/doc123"
            },
            parameters={
                "chunk_size": 10,  # Small chunks for testing
                "overlap_size": 2
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        chunks = result.data["chunks"]
        assert len(chunks) > 1  # Should have multiple chunks
        
        # Verify chunk properties
        for i, chunk in enumerate(chunks):
            assert chunk["chunk_index"] == i
            assert chunk["source_document"] == "storage://document/doc123"
            assert len(chunk["text"]) > 0
            assert chunk["token_count"] > 0
    
    def test_overlapping_chunks(self):
        """Tool creates proper overlapping chunks"""
        # Use numbered tokens to verify overlap
        tokens = [f"token{i}" for i in range(30)]
        text = " ".join(tokens)
        
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "text": text,
                "document_ref": "storage://document/doc123"
            },
            parameters={
                "chunk_size": 10,
                "overlap_size": 3
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        chunks = result.data["chunks"]
        
        # Verify overlap between consecutive chunks
        for i in range(1, len(chunks)):
            prev_tokens = chunks[i-1]["text"].split()
            curr_tokens = chunks[i]["text"].split()
            
            # Last tokens of previous chunk should match first tokens of current
            overlap_count = 0
            for j in range(min(3, len(prev_tokens), len(curr_tokens))):
                if prev_tokens[-(3-j)] == curr_tokens[j]:
                    overlap_count += 1
            
            assert overlap_count >= 2  # At least some overlap
    
    def test_short_text_single_chunk(self):
        """Tool returns single chunk for short text"""
        short_text = "This is a short text."
        
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "text": short_text,
                "document_ref": "storage://document/doc123"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert result.data["total_chunks"] == 1
        chunks = result.data["chunks"]
        assert len(chunks) == 1
        assert chunks[0]["text"] == short_text.strip()
        assert chunks[0]["chunking_method"] == "single_chunk"
    
    def test_chunk_position_tracking(self):
        """Tool tracks character positions correctly"""
        text = "First sentence. Second sentence. Third sentence."
        
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "text": text,
                "document_ref": "storage://document/doc123"
            },
            parameters={
                "chunk_size": 3,  # Small chunks to test positions
                "overlap_size": 0  # No overlap for easier testing
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        chunks = result.data["chunks"]
        
        # Verify character positions
        for chunk in chunks:
            extracted = text[chunk["char_start"]:chunk["char_end"]]
            # Allow for whitespace differences
            assert chunk["text"].strip() in extracted.strip()
    
    def test_unicode_text_handling(self):
        """Tool handles unicode text correctly"""
        unicode_text = "Hello 世界! This contains émojis 🌍 and spëcial characters."
        
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "text": unicode_text,
                "document_ref": "storage://document/doc123"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        chunks = result.data["chunks"]
        assert len(chunks) >= 1
        
        # Verify unicode preserved
        full_text = " ".join(chunk["text"] for chunk in chunks)
        assert "世界" in full_text
        assert "🌍" in full_text
        assert "émojis" in full_text
    
    def test_custom_chunk_parameters(self):
        """Tool respects custom chunking parameters"""
        text = " ".join([f"word{i}" for i in range(100)])
        
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "text": text,
                "document_ref": "storage://document/doc123"
            },
            parameters={
                "chunk_size": 20,
                "overlap_size": 5,
                "min_chunk_size": 10
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        chunks = result.data["chunks"]
        
        # Verify chunk sizes respect parameters
        for chunk in chunks[:-1]:  # Exclude last chunk which may be smaller
            assert chunk["token_count"] <= 20
            assert chunk["token_count"] >= 10
    
    def test_identity_service_integration(self):
        """Tool integrates with identity service for chunk tracking"""
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "text": "Test text for identity service integration.",
                "document_ref": "storage://document/doc123"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Identity service should not be called for text chunking
        # (chunks are not entities)
        self.mock_identity.create_mention.assert_not_called()
    
    def test_provenance_tracking(self):
        """Tool tracks provenance correctly"""
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "text": "Test text for provenance tracking.",
                "document_ref": "storage://document/doc123"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Verify provenance tracking
        self.mock_provenance.start_operation.assert_called_once()
        start_call = self.mock_provenance.start_operation.call_args
        assert start_call[1]["tool_id"] == "T15A"
        assert start_call[1]["operation_type"] == "chunk_text"
        assert start_call[1]["used"]["document"] == "storage://document/doc123"
        
        self.mock_provenance.complete_operation.assert_called_once()
        complete_call = self.mock_provenance.complete_operation.call_args
        assert complete_call[1]["success"] == True
        assert len(complete_call[1]["outputs"]) > 0
    
    def test_quality_service_integration(self):
        """Tool integrates with quality service for confidence"""
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "text": "Test text for quality assessment.",
                "document_ref": "storage://document/doc123",
                "document_confidence": 0.9
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        
        # Verify quality assessment
        self.mock_quality.propagate_confidence.assert_called()
        self.mock_quality.assess_confidence.assert_called()
        
        # Check chunks have confidence scores
        chunks = result.data["chunks"]
        for chunk in chunks:
            assert "confidence" in chunk
            assert chunk["confidence"] > 0
            assert chunk["confidence"] <= 1.0
    
    @pytest.mark.performance
    def test_performance_requirements(self):
        """Tool meets performance requirements"""
        # Generate large text
        large_text = " ".join([f"word{i}" for i in range(10000)])
        
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "text": large_text,
                "document_ref": "storage://document/doc123"
            },
            parameters={}
        )
        
        import time
        start_time = time.time()
        result = self.tool.execute(request)
        execution_time = time.time() - start_time
        
        assert result.status == "success"
        assert execution_time < 5.0  # Should complete within 5 seconds
        assert result.execution_time < 5.0
    
    def test_handles_empty_text(self):
        """Tool handles empty text gracefully"""
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "text": "",
                "document_ref": "storage://document/doc123"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "error"
        assert result.error_code == "EMPTY_TEXT"
        assert "empty" in result.error_message.lower()
    
    def test_handles_missing_document_ref(self):
        """Tool handles missing document reference"""
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "text": "Some text to chunk"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "error"
        assert result.error_code == "INVALID_INPUT"
        assert "document_ref" in result.error_message
    
    def test_handles_whitespace_only_text(self):
        """Tool handles whitespace-only text"""
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "text": "   \n\t   ",
                "document_ref": "storage://document/doc123"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "error"
        assert result.error_code == "EMPTY_TEXT"
    
    def test_chunk_statistics(self):
        """Tool provides accurate chunk statistics"""
        text = " ".join([f"word{i}" for i in range(100)])
        
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "text": text,
                "document_ref": "storage://document/doc123"
            },
            parameters={
                "chunk_size": 10,
                "overlap_size": 2
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert "chunk_statistics" in result.data
        
        stats = result.data["chunk_statistics"]
        assert stats["total_chunks"] == len(result.data["chunks"])
        assert stats["average_tokens_per_chunk"] > 0
        assert stats["min_tokens"] > 0
        assert stats["max_tokens"] >= stats["min_tokens"]
    
    def test_tool_status_management(self):
        """Tool manages status correctly during execution"""
        from src.tools.base_tool import ToolStatus
        
        assert self.tool.status == ToolStatus.READY
        
        # Create a request
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "text": "Test text",
                "document_ref": "storage://document/doc123"
            },
            parameters={}
        )
        
        # Status should change during execution
        # (This would require mocking internal methods to verify)
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert self.tool.status == ToolStatus.READY
    
    def test_health_check(self):
        """Tool health check works correctly"""
        health_result = self.tool.health_check()
        
        assert health_result.status == "success"
        assert health_result.data["healthy"] == True
        assert "chunk_size" in health_result.data
        assert "overlap_size" in health_result.data
        assert "status" in health_result.data
    
    def test_cleanup(self):
        """Tool cleanup works correctly"""
        # Execute a request first
        request = ToolRequest(
            tool_id="T15A",
            operation="chunk",
            input_data={
                "text": "Test text",
                "document_ref": "storage://document/doc123"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        assert result.status == "success"
        
        # Cleanup should succeed
        cleanup_success = self.tool.cleanup()
        assert cleanup_success == True