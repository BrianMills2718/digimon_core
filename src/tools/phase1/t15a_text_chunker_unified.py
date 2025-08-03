"""
T15A: Text Chunker - Unified Interface Implementation

Splits text into overlapping chunks for processing.
"""

from typing import Dict, Any, Optional, List, Tuple
import uuid
from datetime import datetime
import re
import logging
import time
import psutil

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class T15ATextChunkerUnified(BaseTool):
    """T15A: Text Chunker with unified interface"""
    
    def __init__(self, service_manager: ServiceManager):
        """Initialize with service manager"""
        super().__init__(service_manager)
        self.tool_id = "T15A_TEXT_CHUNKER"
        self.identity_service = service_manager.identity_service
        self.provenance_service = service_manager.provenance_service
        self.quality_service = service_manager.quality_service
        
        # Default chunking parameters
        self.default_chunk_size = 512      # tokens per chunk
        self.default_overlap_size = 50     # tokens overlap between chunks
        self.default_min_chunk_size = 100  # minimum chunk size
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name="Text Chunker",
            description="Split text into overlapping chunks for processing",
            category="document_processing",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to chunk",
                        "minLength": 1
                    },
                    "document_ref": {
                        "type": "string",
                        "description": "Reference to source document"
                    },
                    "document_confidence": {
                        "type": "number",
                        "description": "Confidence score from document",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.8
                    }
                },
                "required": ["text", "document_ref"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "chunks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "chunk_id": {"type": "string"},
                                "chunk_ref": {"type": "string"},
                                "chunk_index": {"type": "integer"},
                                "text": {"type": "string"},
                                "token_count": {"type": "integer"},
                                "char_start": {"type": "integer"},
                                "char_end": {"type": "integer"},
                                "source_document": {"type": "string"},
                                "confidence": {"type": "number"},
                                "quality_tier": {"type": "string"},
                                "created_at": {"type": "string"},
                                "chunking_method": {"type": "string"}
                            },
                            "required": ["chunk_id", "chunk_ref", "text", "token_count", "confidence"]
                        }
                    },
                    "total_chunks": {"type": "integer"},
                    "total_tokens": {"type": "integer"},
                    "chunk_statistics": {"type": "object"}
                },
                "required": ["chunks", "total_chunks", "total_tokens"]
            },
            dependencies=["identity_service", "provenance_service", "quality_service"],
            performance_requirements={
                "max_execution_time": 5.0,  # 5 seconds for large texts
                "max_memory_mb": 512,       # 512MB for processing
                "min_confidence": 0.7       # Minimum confidence threshold
            },
            error_conditions=[
                "EMPTY_TEXT",
                "INVALID_INPUT",
                "CHUNKING_FAILED",
                "MEMORY_LIMIT_EXCEEDED"
            ]
        )
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input against tool contract"""
        try:
            # First check with base validation
            if not super().validate_input(input_data):
                return False
            
            # Additional validation: text must not be empty
            text = input_data.get("text", "")
            if not text or not text.strip():
                return False
            
            return True
        except Exception:
            return False
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute text chunking with unified interface"""
        self._start_execution()
        
        try:
            # Extract parameters first
            text = request.input_data.get("text", "").strip()
            document_ref = request.input_data.get("document_ref")
            document_confidence = request.input_data.get("document_confidence", 0.8)
            
            # Check for empty text first
            if not text:
                return self._create_error_result(
                    request,
                    "EMPTY_TEXT",
                    "Text cannot be empty"
                )
            
            # Validate input
            if not self.validate_input(request.input_data):
                return self._create_error_result(
                    request,
                    "INVALID_INPUT",
                    "Input validation failed. Required: text and document_ref"
                )
            
            # Extract chunking parameters
            chunk_size = request.parameters.get("chunk_size", self.default_chunk_size)
            overlap_size = request.parameters.get("overlap_size", self.default_overlap_size)
            min_chunk_size = request.parameters.get("min_chunk_size", self.default_min_chunk_size)
            
            # For small chunk sizes, adjust min_chunk_size accordingly
            if chunk_size < self.default_min_chunk_size:
                min_chunk_size = min(chunk_size, min_chunk_size)
            
            # Start provenance tracking
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="chunk_text",
                inputs=[document_ref],
                parameters={
                    "chunk_size": chunk_size,
                    "overlap_size": overlap_size,
                    "text_length": len(text)
                }
            )
            
            # Tokenize text
            tokens = self._tokenize_text(text)
            
            # Create chunks
            if len(tokens) < min_chunk_size:
                # Text too short, return as single chunk
                chunks = self._create_single_chunk(
                    document_ref, text, tokens, document_confidence
                )
            else:
                # Split into overlapping chunks
                chunks = self._create_overlapping_chunks(
                    document_ref, text, tokens, document_confidence,
                    chunk_size, overlap_size, min_chunk_size
                )
            
            # Track quality for each chunk
            chunk_refs = []
            for chunk in chunks:
                chunk_ref = chunk["chunk_ref"]
                chunk_refs.append(chunk_ref)
                
                # Propagate confidence from document
                propagated_confidence = self.quality_service.propagate_confidence(
                    source_confidence=document_confidence,
                    operation_type="chunk_text",
                    degradation_factor=0.98  # Small degradation for chunking
                )
                
                # Assess chunk quality
                quality_result = self.quality_service.assess_confidence(
                    object_ref=chunk_ref,
                    base_confidence=propagated_confidence,
                    factors={
                        "chunk_length": min(1.0, len(chunk["text"]) / 1000),
                        "token_count": min(1.0, chunk["token_count"] / chunk_size),
                        "position_factor": 1.0 - (chunk["chunk_index"] * 0.01)
                    },
                    metadata={
                        "source_document": document_ref,
                        "chunk_method": chunk["chunking_method"]
                    }
                )
                
                if quality_result["status"] == "success":
                    chunk["confidence"] = quality_result["confidence"]
                    chunk["quality_tier"] = quality_result["quality_tier"]
            
            # Calculate chunk statistics
            chunk_statistics = self._calculate_chunk_statistics(chunks)
            
            # Complete provenance
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=chunk_refs,
                success=True,
                metadata={
                    "total_chunks": len(chunks),
                    "total_tokens": len(tokens),
                    "average_chunk_size": chunk_statistics["average_tokens_per_chunk"]
                }
            )
            
            # Get execution metrics
            execution_time, memory_used = self._end_execution()
            
            # Create success result
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "chunks": chunks,
                    "total_chunks": len(chunks),
                    "total_tokens": len(tokens),
                    "chunk_statistics": chunk_statistics
                },
                metadata={
                    "operation_id": operation_id,
                    "chunking_parameters": {
                        "chunk_size": chunk_size,
                        "overlap_size": overlap_size,
                        "min_chunk_size": min_chunk_size
                    }
                },
                execution_time=execution_time,
                memory_used=memory_used
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in {self.tool_id}: {e}", exc_info=True)
            return self._create_error_result(
                request,
                "UNEXPECTED_ERROR",
                f"Unexpected error during text chunking: {str(e)}"
            )
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Simple tokenization by whitespace and punctuation"""
        # Split by word boundaries to get individual words
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    def _create_single_chunk(
        self, 
        document_ref: str, 
        text: str, 
        tokens: List[str], 
        document_confidence: float
    ) -> List[Dict[str, Any]]:
        """Create a single chunk for short text"""
        chunk_id = f"chunk_{uuid.uuid4().hex[:8]}"
        chunk_ref = f"storage://chunk/{chunk_id}"
        
        chunk = {
            "chunk_id": chunk_id,
            "chunk_ref": chunk_ref,
            "chunk_index": 0,
            "text": text.strip(),
            "token_count": len(tokens),
            "char_start": 0,
            "char_end": len(text),
            "source_document": document_ref,
            "confidence": document_confidence * 0.98,
            "created_at": datetime.now().isoformat(),
            "chunking_method": "single_chunk"
        }
        
        return [chunk]
    
    def _create_overlapping_chunks(
        self, 
        document_ref: str, 
        text: str, 
        tokens: List[str], 
        document_confidence: float,
        chunk_size: int,
        overlap_size: int,
        min_chunk_size: int
    ) -> List[Dict[str, Any]]:
        """Create overlapping chunks using sliding window"""
        chunks = []
        chunk_index = 0
        
        # Calculate character positions for each token
        token_positions = self._calculate_token_positions(text, tokens)
        
        start_token = 0
        while start_token < len(tokens):
            # Calculate end token for this chunk
            end_token = min(start_token + chunk_size, len(tokens))
            
            # Skip if chunk would be too small
            if end_token - start_token < min_chunk_size and start_token > 0:
                break
            
            # Extract chunk tokens
            chunk_tokens = tokens[start_token:end_token]
            
            # Get character positions
            if start_token < len(token_positions):
                char_start = token_positions[start_token][0]
            else:
                char_start = len(text)
            
            if end_token - 1 < len(token_positions):
                char_end = token_positions[end_token - 1][1]
            else:
                char_end = len(text)
            
            chunk_text = text[char_start:char_end].strip()
            
            # Create chunk metadata
            chunk_id = f"chunk_{uuid.uuid4().hex[:8]}"
            chunk_ref = f"storage://chunk/{chunk_id}"
            
            chunk = {
                "chunk_id": chunk_id,
                "chunk_ref": chunk_ref,
                "chunk_index": chunk_index,
                "text": chunk_text,
                "token_count": len(chunk_tokens),
                "char_start": char_start,
                "char_end": char_end,
                "source_document": document_ref,
                "confidence": document_confidence * 0.98,
                "created_at": datetime.now().isoformat(),
                "chunking_method": "sliding_window",
                "overlap_with_previous": min(overlap_size, start_token) if start_token > 0 else 0
            }
            
            chunks.append(chunk)
            chunk_index += 1
            
            # Move to next chunk position
            next_start = start_token + chunk_size - overlap_size
            
            # Ensure we make progress
            if next_start <= start_token:
                next_start = start_token + 1
            
            start_token = next_start
            
            # Safety check
            if chunk_index > 1000:
                logger.warning("Maximum chunk limit reached")
                break
        
        return chunks
    
    def _calculate_token_positions(self, text: str, tokens: List[str]) -> List[Tuple[int, int]]:
        """Calculate character positions for each token in the text"""
        positions = []
        current_pos = 0
        
        for token in tokens:
            # Find token in remaining text
            token_start = text.find(token, current_pos)
            if token_start == -1:
                # Token not found, use current position
                token_start = current_pos
                token_end = current_pos + len(token)
            else:
                token_end = token_start + len(token)
            
            positions.append((token_start, token_end))
            current_pos = token_end
        
        return positions
    
    def _calculate_chunk_statistics(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics for a set of chunks"""
        if not chunks:
            return {
                "total_chunks": 0,
                "total_tokens": 0,
                "average_tokens_per_chunk": 0,
                "min_tokens": 0,
                "max_tokens": 0,
                "average_text_length": 0,
                "total_text_length": 0
            }
        
        token_counts = [chunk["token_count"] for chunk in chunks]
        text_lengths = [len(chunk["text"]) for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "total_tokens": sum(token_counts),
            "average_tokens_per_chunk": sum(token_counts) / len(chunks),
            "min_tokens": min(token_counts),
            "max_tokens": max(token_counts),
            "average_text_length": sum(text_lengths) / len(chunks),
            "total_text_length": sum(text_lengths)
        }
    
    def health_check(self) -> ToolResult:
        """Check tool health and readiness"""
        try:
            # Check service dependencies
            services_healthy = True
            if self.services:
                try:
                    _ = self.identity_service
                    _ = self.provenance_service
                    _ = self.quality_service
                except:
                    services_healthy = False
            
            healthy = services_healthy
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success" if healthy else "error",
                data={
                    "healthy": healthy,
                    "services_healthy": services_healthy,
                    "chunk_size": self.default_chunk_size,
                    "overlap_size": self.default_overlap_size,
                    "min_chunk_size": self.default_min_chunk_size,
                    "status": self.status.value
                },
                metadata={
                    "timestamp": datetime.now().isoformat()
                },
                execution_time=0.0,
                memory_used=0
            )
            
        except Exception as e:
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={"healthy": False},
                metadata={"error": str(e)},
                execution_time=0.0,
                memory_used=0,
                error_code="HEALTH_CHECK_FAILED",
                error_message=str(e)
            )
    
    def cleanup(self) -> bool:
        """Clean up any resources"""
        try:
            self.status = ToolStatus.READY
            return True
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False