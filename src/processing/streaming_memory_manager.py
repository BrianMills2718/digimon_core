#!/usr/bin/env python3
"""
Streaming Memory Manager - Phase D.3 Implementation

Memory-efficient streaming processor for large document batches with
intelligent memory management and garbage collection.
"""

import asyncio
import gc
import psutil
import os
import uuid
from typing import AsyncGenerator, Dict, Any, Optional, List, Callable
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import time
from dataclasses import dataclass
import weakref

logger = logging.getLogger(__name__)


class MemoryPool:
    """
    Efficient memory pool for document processing.
    
    Reuses buffers to minimize allocation overhead and fragmentation.
    """
    
    def __init__(self, max_size_mb: int = 500):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.allocated_bytes = 0
        self.free_buffers = {}  # size -> list of buffers
        self.in_use_buffers = set()  # Track buffer IDs since bytearray is unhashable
        self.allocation_count = 0
        self.reuse_count = 0
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def get_buffer(self, size_bytes: int) -> bytearray:
        """
        Get a buffer of specified size from pool.
        
        Args:
            size_bytes: Required buffer size
            
        Returns:
            Buffer object
            
        Raises:
            MemoryError: If requested size exceeds pool limit
        """
        if size_bytes > self.max_size_bytes:
            raise MemoryError(
                f"Requested buffer size {size_bytes} exceeds pool limit {self.max_size_bytes}"
            )
        
        # Round up to nearest power of 2 for better reuse
        actual_size = 1 << (size_bytes - 1).bit_length()
        
        # Try to reuse existing buffer
        if actual_size in self.free_buffers and self.free_buffers[actual_size]:
            buffer = self.free_buffers[actual_size].pop()
            self.reuse_count += 1
            self.logger.debug(f"Reused buffer of size {actual_size} bytes")
        else:
            # Check if we have space for new allocation
            if self.allocated_bytes + actual_size > self.max_size_bytes:
                # Try to free some memory
                self._cleanup_unused()
                
                if self.allocated_bytes + actual_size > self.max_size_bytes:
                    raise MemoryError(
                        f"Memory pool exhausted: {self.allocated_bytes}/{self.max_size_bytes} bytes used"
                    )
            
            # Create new buffer
            buffer = bytearray(actual_size)
            self.allocated_bytes += actual_size
            self.allocation_count += 1
            self.logger.debug(f"Allocated new buffer of size {actual_size} bytes")
        
        # Track buffer in use
        self.in_use_buffers.add(id(buffer))
        return buffer
    
    def return_buffer(self, buffer: bytearray):
        """Return buffer to pool for reuse"""
        if id(buffer) not in self.in_use_buffers:
            self.logger.warning("Attempting to return buffer not from this pool")
            return
        
        size = len(buffer)
        
        # Clear buffer contents for security
        buffer[:] = b'\0' * size
        
        # Add to free list
        if size not in self.free_buffers:
            self.free_buffers[size] = []
        
        self.free_buffers[size].append(buffer)
        self.in_use_buffers.discard(id(buffer))
        
        self.logger.debug(f"Returned buffer of size {size} bytes to pool")
    
    def _cleanup_unused(self):
        """Clean up unused buffers to free memory"""
        freed_bytes = 0
        
        for size, buffers in list(self.free_buffers.items()):
            if buffers:
                # Keep at most 2 buffers of each size
                to_remove = len(buffers) - 2
                if to_remove > 0:
                    for _ in range(to_remove):
                        buffers.pop()
                        freed_bytes += size
                        self.allocated_bytes -= size
        
        gc.collect()
        
        self.logger.info(f"Freed {freed_bytes} bytes from memory pool")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        free_count = sum(len(buffers) for buffers in self.free_buffers.values())
        
        return {
            "max_size_mb": self.max_size_bytes // (1024 * 1024),
            "allocated_mb": self.allocated_bytes // (1024 * 1024),
            "in_use_buffers": len(self.in_use_buffers),
            "free_buffers": free_count,
            "allocation_count": self.allocation_count,
            "reuse_count": self.reuse_count,
            "reuse_rate": self.reuse_count / (self.allocation_count + self.reuse_count) 
                         if (self.allocation_count + self.reuse_count) > 0 else 0.0
        }


@dataclass
class ProcessingMetrics:
    """Metrics for document processing"""
    documents_processed: int = 0
    total_bytes_processed: int = 0
    peak_memory_mb: int = 0
    processing_time: float = 0.0
    gc_collections: int = 0


class DocumentProcessor:
    """
    Process documents with memory management.
    
    Handles individual document processing with memory tracking.
    """
    
    def __init__(self, documents: List[str], memory_pool: MemoryPool):
        self.documents = documents
        self.memory_pool = memory_pool
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._processing_buffers = []
    
    async def process_documents(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Process documents and yield results"""
        for doc_path in self.documents:
            try:
                result = await self._process_single_document(doc_path)
                yield result
            except Exception as e:
                self.logger.error(f"Failed to process document {doc_path}: {e}")
                yield {
                    "document": doc_path,
                    "status": "error",
                    "error": str(e)
                }
    
    async def _process_single_document(self, doc_path: str) -> Dict[str, Any]:
        """Process a single document with REAL tool integration"""
        start_time = time.time()
        
        # Determine document size
        try:
            if os.path.exists(doc_path):
                doc_size = os.path.getsize(doc_path)
            else:
                # For test documents without real files, fail fast
                raise FileNotFoundError(f"Document file not found: {doc_path}")
        except Exception as e:
            return {
                "document": doc_path,
                "status": "error",
                "error": f"File access error: {str(e)}",
                "processing_time": time.time() - start_time
            }
        
        # Allocate buffer for document processing
        buffer_size = max(doc_size, 64 * 1024)  # At least 64KB
        buffer = self.memory_pool.get_buffer(buffer_size)
        self._processing_buffers.append(buffer)
        
        try:
            # Import real tools
            from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
            from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
            from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
            from src.core.service_manager import ServiceManager
            
            # Initialize real tools
            service_manager = ServiceManager()
            pdf_loader = T01PDFLoaderUnified(service_manager)
            chunker = T15ATextChunkerUnified(service_manager)
            ner = T23ASpacyNERUnified(service_manager)
            
            # Generate workflow ID for document processing
            workflow_id = f"streaming_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Step 1: Load document content using real T01 tool
            from src.tools.base_tool import ToolRequest
            
            load_request = ToolRequest(
                tool_id="T01",
                operation="load_document",
                input_data={"file_path": doc_path, "workflow_id": workflow_id},
                parameters={}
            )
            load_result = pdf_loader.execute(load_request)
            
            if load_result.status != "success":
                return {
                    "document": doc_path,
                    "status": "error",
                    "error": f"PDF loading failed: {load_result.error_message or 'Unknown error'}",
                    "processing_time": time.time() - start_time
                }
            
            document_content = load_result.data["document"]["text"]
            document_ref = load_result.data["document"]["document_ref"]
            
            # Step 2: Chunk text using real T15A tool
            chunk_request = ToolRequest(
                tool_id="T15A",
                operation="chunk_text",
                input_data={
                    "document_ref": document_ref,
                    "text": document_content,
                    "confidence": 0.8
                },
                parameters={}
            )
            chunk_result = chunker.execute(chunk_request)
            
            if chunk_result.status != "success":
                return {
                    "document": doc_path,
                    "status": "error", 
                    "error": f"Text chunking failed: {chunk_result.error_message or 'Unknown error'}",
                    "processing_time": time.time() - start_time
                }
            
            chunks = chunk_result.data["chunks"]
            
            # Step 3: Extract entities from chunks using real T23A tool
            total_entities = []
            for chunk in chunks:
                chunk_ref = chunk["chunk_ref"]
                chunk_text = chunk["text"]
                
                entity_request = ToolRequest(
                    tool_id="T23A",
                    operation="extract_entities",
                    input_data={
                        "chunk_ref": chunk_ref,
                        "text": chunk_text,
                        "confidence": 0.8
                    },
                    parameters={}
                )
                entity_result = ner.execute(entity_request)
                
                if entity_result.status == "success":
                    total_entities.extend(entity_result.data.get("entities", []))
            
            # Step 4: Create comprehensive processing result
            result = {
                "document": doc_path,
                "status": "success",
                "document_ref": document_ref,
                "chunks_created": len(chunks),
                "entities_extracted": len(total_entities),
                "entity_types": self._count_entity_types(total_entities),
                "text_length": len(document_content),
                "processing_time": time.time() - start_time,
                "memory_used_mb": len(buffer) // (1024 * 1024),
                "document_size": doc_size,
                "workflow_id": workflow_id,
                "tools_used": ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER"]
            }
            
            self.logger.info(
                f"Real document processing complete: {doc_path} -> "
                f"{len(chunks)} chunks, {len(total_entities)} entities in "
                f"{result['processing_time']:.2f}s"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Real document processing failed for {doc_path}: {e}")
            return {
                "document": doc_path,
                "status": "error",
                "error": f"Processing pipeline error: {str(e)}",
                "processing_time": time.time() - start_time
            }
            
        finally:
            # Return buffer to pool
            self.memory_pool.return_buffer(buffer)
            self._processing_buffers.remove(buffer)
    
    def _count_entity_types(self, entities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count entities by type"""
        type_counts = {}
        for entity in entities:
            entity_type = entity.get("entity_type", "UNKNOWN")
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        return type_counts
    
    async def cleanup(self):
        """Clean up processor resources"""
        for buffer in self._processing_buffers:
            self.memory_pool.return_buffer(buffer)
        self._processing_buffers.clear()


class StreamingMemoryManager:
    """
    Memory-efficient streaming processor for large document batches.
    
    Features:
    - Streaming processing with controlled memory usage
    - Automatic garbage collection
    - Memory pressure monitoring
    - Adaptive batch sizing
    """
    
    def __init__(self, memory_limit_mb: int = 1500):
        self.memory_limit_mb = memory_limit_mb
        self.memory_limit_bytes = memory_limit_mb * 1024 * 1024
        self.memory_pool = MemoryPool(max_size_mb=memory_limit_mb // 2)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.metrics = ProcessingMetrics()
        self._process = psutil.Process()
        self._gc_enabled = gc.isenabled()
    
    async def stream_document_batch(
        self, 
        documents: List[str], 
        chunk_size: int = 5,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream process documents in memory-efficient chunks.
        
        Args:
            documents: List of document paths to process
            chunk_size: Number of documents per chunk
            progress_callback: Optional callback for progress updates
            
        Yields:
            Processing results for each document
        """
        total_docs = len(documents)
        total_chunks = (total_docs + chunk_size - 1) // chunk_size
        
        self.logger.info(
            f"Starting streaming processing of {total_docs} documents "
            f"in {total_chunks} chunks of size {chunk_size}"
        )
        
        start_time = time.time()
        initial_memory = self._get_memory_usage_mb()
        
        for i in range(0, total_docs, chunk_size):
            chunk = documents[i:i + chunk_size]
            chunk_num = i // chunk_size + 1
            
            self.logger.info(
                f"Processing chunk {chunk_num}/{total_chunks} with {len(chunk)} documents"
            )
            
            # Wait for sufficient memory
            await self._wait_for_memory_availability()
            
            # Process chunk with memory management
            async with self._memory_managed_processing(chunk) as processor:
                async for result in processor.process_documents():
                    self.metrics.documents_processed += 1
                    
                    # Update progress
                    if progress_callback:
                        progress_callback(self.metrics.documents_processed, total_docs)
                    
                    yield result
            
            # Force garbage collection between chunks
            self._force_cleanup()
            
            # Check memory usage
            current_memory = self._get_memory_usage_mb()
            self.metrics.peak_memory_mb = max(self.metrics.peak_memory_mb, current_memory)
            
            self.logger.debug(
                f"Chunk {chunk_num} complete. Memory: {current_memory}MB "
                f"(peak: {self.metrics.peak_memory_mb}MB)"
            )
        
        # Final metrics
        self.metrics.processing_time = time.time() - start_time
        
        self.logger.info(
            f"Streaming processing complete: {self.metrics.documents_processed} documents "
            f"in {self.metrics.processing_time:.2f}s, peak memory: {self.metrics.peak_memory_mb}MB"
        )
    
    @asynccontextmanager
    async def _memory_managed_processing(self, documents: List[str]):
        """Context manager for memory-managed document processing"""
        processor = None
        
        try:
            # Check memory before starting
            if not await self._has_sufficient_memory():
                await self._free_memory()
            
            # Create processor
            processor = DocumentProcessor(documents, self.memory_pool)
            yield processor
            
        finally:
            # Cleanup
            if processor:
                await processor.cleanup()
            
            # Aggressive cleanup
            self._cleanup_memory()
    
    async def _wait_for_memory_availability(self, timeout: float = 30.0):
        """Wait for sufficient memory to become available"""
        start_time = time.time()
        
        while not await self._has_sufficient_memory():
            if time.time() - start_time > timeout:
                raise TimeoutError(
                    f"Timeout waiting for memory availability after {timeout}s"
                )
            
            self.logger.warning(
                f"Insufficient memory, waiting... "
                f"(current: {self._get_memory_usage_mb()}MB, "
                f"limit: {self.memory_limit_mb}MB)"
            )
            
            # Try to free memory
            await self._free_memory()
            
            # Wait before retrying
            await asyncio.sleep(1.0)
    
    async def _has_sufficient_memory(self) -> bool:
        """Check if sufficient memory is available"""
        current_memory = self._get_memory_usage_mb()
        available_memory = psutil.virtual_memory().available // (1024 * 1024)
        
        # Check both process memory and system available memory
        has_process_headroom = current_memory < self.memory_limit_mb * 0.8
        has_system_headroom = available_memory > self.memory_limit_mb * 0.2
        
        return has_process_headroom and has_system_headroom
    
    async def _free_memory(self):
        """Attempt to free memory"""
        self.logger.info("Attempting to free memory")
        
        # Clean up memory pool
        self.memory_pool._cleanup_unused()
        
        # Force garbage collection
        self._force_cleanup()
        
        # Give system time to reclaim memory
        await asyncio.sleep(0.1)
    
    def _cleanup_memory(self):
        """Aggressive memory cleanup"""
        # Clear any circular references
        gc.collect()
        
        # Clean up memory pool
        self.memory_pool._cleanup_unused()
    
    def _force_cleanup(self):
        """Force garbage collection with metrics"""
        before_gc = gc.get_count()
        collected = gc.collect()
        after_gc = gc.get_count()
        
        self.metrics.gc_collections += 1
        
        self.logger.debug(
            f"GC: collected {collected} objects "
            f"(before: {before_gc}, after: {after_gc})"
        )
    
    def _get_memory_usage_mb(self) -> int:
        """Get current process memory usage in MB"""
        return self._process.memory_info().rss // (1024 * 1024)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get processing metrics"""
        return {
            "documents_processed": self.metrics.documents_processed,
            "total_bytes_processed": self.metrics.total_bytes_processed,
            "peak_memory_mb": self.metrics.peak_memory_mb,
            "processing_time": self.metrics.processing_time,
            "gc_collections": self.metrics.gc_collections,
            "avg_time_per_doc": (
                self.metrics.processing_time / self.metrics.documents_processed
                if self.metrics.documents_processed > 0 else 0.0
            ),
            "memory_pool_stats": self.memory_pool.get_stats()
        }


if __name__ == "__main__":
    # Test streaming memory manager
    async def test_streaming():
        manager = StreamingMemoryManager(memory_limit_mb=500)
        
        # Create test document list
        test_docs = [f"/path/to/doc_{i}.pdf" for i in range(20)]
        
        # Progress callback
        def progress(current, total):
            print(f"Progress: {current}/{total} ({current/total*100:.1f}%)")
        
        try:
            results = []
            async for result in manager.stream_document_batch(
                test_docs, 
                chunk_size=5,
                progress_callback=progress
            ):
                results.append(result)
                print(f"Processed: {result['document']} - {result['status']}")
            
            print(f"\nProcessing complete:")
            print(f"Results: {len(results)} documents")
            print(f"Metrics: {manager.get_metrics()}")
            
        except Exception as e:
            print(f"Test failed: {e}")
    
    asyncio.run(test_streaming())