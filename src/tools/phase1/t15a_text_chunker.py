"""T15a: Sliding Window Text Chunker - Minimal Implementation

Splits text into overlapping chunks for processing.
Essential for managing large documents in the vertical slice workflow.

Minimal implementation focusing on:
- Fixed 512-token chunks with 50-token overlap
- Simple position tracking for provenance
- Quality inheritance from document
- Integration with core services

Deferred features:
- Semantic chunking
- Dynamic chunk sizing
- Advanced boundary detection
- Content-aware splitting
"""

from typing import Dict, List, Optional, Any, Tuple
import uuid
from datetime import datetime
import re

# Import core services
from src.core.identity_service import IdentityService
from src.core.provenance_service import ProvenanceService
from src.core.quality_service import QualityService


class TextChunker:
    """T15a: Sliding Window Text Chunker."""
    
    def __init__(
        self,
        identity_service: IdentityService,
        provenance_service: ProvenanceService,
        quality_service: QualityService
    ):
        self.identity_service = identity_service
        self.provenance_service = provenance_service
        self.quality_service = quality_service
        self.tool_id = "T15A_TEXT_CHUNKER"
        
        # Chunking parameters (minimal implementation)
        self.chunk_size = 512      # tokens per chunk
        self.overlap_size = 50     # tokens overlap between chunks
        self.min_chunk_size = 100  # minimum chunk size
    
    def chunk_text(
        self,
        document_ref: str,
        text: str,
        document_confidence: float = 0.8
    ) -> Dict[str, Any]:
        """Split text into overlapping chunks.
        
        Args:
            document_ref: Reference to source document
            text: Text to chunk
            document_confidence: Confidence score from document
            
        Returns:
            List of text chunks with metadata
        """
        # Start operation tracking
        operation_id = self.provenance_service.start_operation(
            tool_id=self.tool_id,
            operation_type="chunk_text",
            inputs=[document_ref],
            parameters={
                "chunk_size": self.chunk_size,
                "overlap_size": self.overlap_size,
                "text_length": len(text)
            }
        )
        
        try:
            # Input validation
            if not text or not text.strip():
                return self._complete_with_error(
                    operation_id,
                    "Text cannot be empty"
                )
            
            if not document_ref:
                return self._complete_with_error(
                    operation_id,
                    "document_ref is required"
                )
            
            # Simple tokenization (split by whitespace)
            tokens = self._tokenize_text(text)
            
            if len(tokens) < self.min_chunk_size:
                # Text too short, return as single chunk
                chunks = self._create_single_chunk(
                    document_ref, text, tokens, document_confidence
                )
            else:
                # Split into overlapping chunks
                chunks = self._create_overlapping_chunks(
                    document_ref, text, tokens, document_confidence
                )
            
            # Track quality for each chunk
            chunk_refs = []
            for chunk in chunks:
                chunk_ref = chunk["chunk_ref"]
                chunk_refs.append(chunk_ref)
                
                # Propagate confidence from document with slight degradation
                propagated_confidence = self.quality_service.propagate_confidence(
                    input_refs=[document_ref],
                    operation_type="text_chunking",
                    boost_factor=0.98  # Small degradation for chunking
                )
                
                # Assess chunk quality
                quality_result = self.quality_service.assess_confidence(
                    object_ref=chunk_ref,
                    base_confidence=propagated_confidence,
                    factors={
                        "chunk_length": min(1.0, len(chunk["text"]) / 1000),  # Longer chunks better
                        "token_count": min(1.0, chunk["token_count"] / self.chunk_size),  # Target size
                        "position_factor": 1.0 - (chunk["chunk_index"] * 0.01)  # Early chunks slightly better
                    },
                    metadata={
                        "source_document": document_ref,
                        "chunk_method": "sliding_window"
                    }
                )
                
                if quality_result["status"] == "success":
                    chunk["confidence"] = quality_result["confidence"]
                    chunk["quality_tier"] = quality_result["quality_tier"]
            
            # Complete operation
            completion_result = self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=chunk_refs,
                success=True,
                metadata={
                    "total_chunks": len(chunks),
                    "total_tokens": len(tokens),
                    "average_chunk_size": sum(c["token_count"] for c in chunks) / len(chunks) if chunks else 0
                }
            )
            
            return {
                "status": "success",
                "chunks": chunks,
                "total_chunks": len(chunks),
                "total_tokens": len(tokens),
                "operation_id": operation_id,
                "provenance": completion_result
            }
            
        except Exception as e:
            return self._complete_with_error(
                operation_id,
                f"Unexpected error during text chunking: {str(e)}"
            )
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Simple tokenization by whitespace and punctuation."""
        # Split by whitespace and common punctuation
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    def _create_single_chunk(
        self, 
        document_ref: str, 
        text: str, 
        tokens: List[str], 
        document_confidence: float
    ) -> List[Dict[str, Any]]:
        """Create a single chunk for short text."""
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
            "confidence": document_confidence * 0.98,  # Slight degradation
            "created_at": datetime.now().isoformat(),
            "chunking_method": "single_chunk"
        }
        
        return [chunk]
    
    def _create_overlapping_chunks(
        self, 
        document_ref: str, 
        text: str, 
        tokens: List[str], 
        document_confidence: float
    ) -> List[Dict[str, Any]]:
        """Create overlapping chunks using sliding window."""
        chunks = []
        chunk_index = 0
        
        # Calculate character positions for each token
        token_positions = self._calculate_token_positions(text, tokens)
        
        start_token = 0
        while start_token < len(tokens):
            # Calculate end token for this chunk
            end_token = min(start_token + self.chunk_size, len(tokens))
            
            # Skip if chunk would be too small
            if end_token - start_token < self.min_chunk_size and start_token > 0:
                break
            
            # Extract chunk tokens and text
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
                "confidence": document_confidence * 0.98,  # Slight degradation
                "created_at": datetime.now().isoformat(),
                "chunking_method": "sliding_window",
                "overlap_with_previous": min(self.overlap_size, start_token) if start_token > 0 else 0,
                "tokens": chunk_tokens  # Include for debugging
            }
            
            chunks.append(chunk)
            chunk_index += 1
            
            # Move to next chunk position
            next_start = start_token + self.chunk_size - self.overlap_size
            
            # Ensure we make progress
            if next_start <= start_token:
                next_start = start_token + 1
            
            start_token = next_start
            
            # Safety check to prevent infinite loops
            if chunk_index > 1000:  # Max 1000 chunks
                break
        
        return chunks
    
    def _calculate_token_positions(self, text: str, tokens: List[str]) -> List[Tuple[int, int]]:
        """Calculate character positions for each token in the text."""
        positions = []
        current_pos = 0
        
        for token in tokens:
            # Find token in remaining text
            token_start = text.find(token, current_pos)
            if token_start == -1:
                # Token not found, approximate position
                token_start = current_pos
                token_end = current_pos + len(token)
            else:
                token_end = token_start + len(token)
            
            positions.append((token_start, token_end))
            current_pos = token_end
        
        return positions
    
    def _complete_with_error(self, operation_id: str, error_message: str) -> Dict[str, Any]:
        """Complete operation with error."""
        self.provenance_service.complete_operation(
            operation_id=operation_id,
            outputs=[],
            success=False,
            error_message=error_message
        )
        
        return {
            "status": "error",
            "error": error_message,
            "operation_id": operation_id
        }
    
    def get_chunking_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics for a set of chunks."""
        if not chunks:
            return {"total_chunks": 0}
        
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
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get tool information."""
        return {
            "tool_id": self.tool_id,
            "name": "Sliding Window Text Chunker",
            "version": "1.0.0",
            "description": "Splits text into overlapping chunks for processing",
            "parameters": {
                "chunk_size": self.chunk_size,
                "overlap_size": self.overlap_size,
                "min_chunk_size": self.min_chunk_size
            },
            "input_type": "document",
            "output_type": "chunks"
        }