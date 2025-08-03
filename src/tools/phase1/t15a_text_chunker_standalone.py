"""
T15A: Text Chunker - Standalone Version
Splits text into overlapping chunks for processing
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import logging

# Import the fixed base tool
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from base_tool_fixed import BaseTool, ToolRequest, ToolResult, ToolContract, ToolStatus

logger = logging.getLogger(__name__)


class T15ATextChunkerStandalone(BaseTool):
    """T15A: Text Chunker - works standalone without service_manager"""
    
    def __init__(self, service_manager=None, chunk_size=512, overlap_size=50):
        """Initialize with optional service manager"""
        super().__init__(service_manager)
        self.tool_id = "T15A_TEXT_CHUNKER"
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.min_chunk_size = 100
    
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
                        "description": "Text to chunk"
                    },
                    "document_id": {
                        "type": "string",
                        "description": "Source document ID"
                    },
                    "chunk_size": {
                        "type": "integer",
                        "description": "Number of tokens per chunk (default: 512)"
                    },
                    "overlap_size": {
                        "type": "integer",
                        "description": "Number of overlapping tokens (default: 50)"
                    }
                },
                "required": ["text"]
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
                                "text": {"type": "string"},
                                "start_pos": {"type": "integer"},
                                "end_pos": {"type": "integer"},
                                "chunk_index": {"type": "integer"},
                                "token_count": {"type": "integer"}
                            }
                        }
                    },
                    "total_chunks": {"type": "integer"},
                    "total_tokens": {"type": "integer"}
                }
            },
            dependencies=[],
            performance_requirements={
                "max_execution_time": 10.0,
                "max_memory_mb": 1024
            },
            error_conditions=[
                "INVALID_INPUT",
                "TEXT_TOO_SHORT",
                "CHUNKING_FAILED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute text chunking"""
        self._start_execution()
        
        try:
            # Extract parameters
            text = request.input_data.get("text")
            document_id = request.input_data.get("document_id", str(uuid.uuid4()))
            chunk_size = request.input_data.get("chunk_size", self.chunk_size)
            overlap_size = request.input_data.get("overlap_size", self.overlap_size)
            
            # Validate input
            if not text:
                return self._create_error_result(
                    "INVALID_INPUT",
                    "No text provided for chunking"
                )
            
            if len(text.strip()) < self.min_chunk_size:
                return self._create_error_result(
                    "TEXT_TOO_SHORT",
                    f"Text too short for chunking (min: {self.min_chunk_size} chars)"
                )
            
            # Tokenize (simple whitespace tokenization)
            tokens = text.split()
            total_tokens = len(tokens)
            
            # Create chunks
            chunks = []
            chunk_index = 0
            position = 0
            
            while position < total_tokens:
                # Calculate chunk boundaries
                chunk_start = position
                chunk_end = min(position + chunk_size, total_tokens)
                
                # Extract chunk tokens
                chunk_tokens = tokens[chunk_start:chunk_end]
                
                if len(chunk_tokens) >= self.min_chunk_size or position == 0:
                    # Find character positions in original text
                    # This is approximate but good enough for our purposes
                    char_start = len(' '.join(tokens[:chunk_start]))
                    if chunk_start > 0:
                        char_start += 1  # Account for space
                    char_end = len(' '.join(tokens[:chunk_end]))
                    
                    chunk_text = ' '.join(chunk_tokens)
                    
                    chunk = {
                        "chunk_id": f"chunk_{document_id}_{chunk_index:04d}",
                        "text": chunk_text,
                        "start_pos": char_start,
                        "end_pos": char_end,
                        "chunk_index": chunk_index,
                        "token_count": len(chunk_tokens),
                        "document_id": document_id
                    }
                    
                    chunks.append(chunk)
                    chunk_index += 1
                
                # Move position forward (with overlap)
                position += chunk_size - overlap_size
                
                # Ensure we don't create tiny final chunks
                if total_tokens - position < self.min_chunk_size and position < total_tokens:
                    # Include remaining tokens in the last chunk
                    if chunks:
                        last_chunk = chunks[-1]
                        remaining_tokens = tokens[position:]
                        last_chunk["text"] += " " + " ".join(remaining_tokens)
                        last_chunk["token_count"] += len(remaining_tokens)
                        last_chunk["end_pos"] = len(text)
                    break
            
            # Log with provenance service
            operation_id = self.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="chunk_text",
                inputs=[document_id],
                parameters={
                    "chunk_size": chunk_size,
                    "overlap_size": overlap_size
                }
            )
            
            chunk_ids = [c["chunk_id"] for c in chunks]
            self.provenance_service.complete_operation(
                operation_id=operation_id,
                outputs=chunk_ids,
                success=True,
                metadata={"chunk_count": len(chunks)}
            )
            
            return self._create_success_result(
                data={
                    "chunks": chunks,
                    "total_chunks": len(chunks),
                    "total_tokens": total_tokens
                },
                metadata={
                    "operation_id": operation_id,
                    "document_id": document_id,
                    "chunk_size": chunk_size,
                    "overlap_size": overlap_size,
                    "standalone_mode": getattr(self, 'is_standalone', False)
                }
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in text chunker: {e}", exc_info=True)
            return self._create_error_result(
                "CHUNKING_FAILED",
                f"Chunking failed: {str(e)}"
            )


# Test function
def test_standalone_chunker():
    """Test the standalone chunker"""
    chunker = T15ATextChunkerStandalone()
    print(f"✅ Text Chunker initialized: {chunker.tool_id}")
    
    # Test text
    test_text = """
    The United States and the Soviet Union were allies in World War II.
    However, after the war ended, tensions arose between the two superpowers.
    This led to the Cold War, a period of geopolitical tension that lasted
    for nearly half a century. The competition involved military, economic,
    and ideological dimensions, shaping global politics for decades.
    """ * 5  # Repeat to make it longer
    
    request = ToolRequest(
        tool_id="T15A",
        operation="chunk",
        input_data={
            "text": test_text,
            "document_id": "test_doc",
            "chunk_size": 50,
            "overlap_size": 10
        }
    )
    
    result = chunker.execute(request)
    print(f"Status: {result.status}")
    
    if result.status == "success":
        data = result.data
        print(f"Created {data['total_chunks']} chunks from {data['total_tokens']} tokens")
        for i, chunk in enumerate(data['chunks'][:3]):  # Show first 3
            print(f"\nChunk {i}: {chunk['chunk_id']}")
            print(f"  Tokens: {chunk['token_count']}")
            print(f"  Text preview: {chunk['text'][:100]}...")
    else:
        print(f"Error: {result.error_message}")
    
    return chunker


if __name__ == "__main__":
    test_standalone_chunker()