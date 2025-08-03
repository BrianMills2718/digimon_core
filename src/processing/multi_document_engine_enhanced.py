#!/usr/bin/env python3
"""
Enhanced Multi-Document Processing Engine - Phase D.3 Integration

Integrates enhanced batch processing, streaming memory management, and
checkpoint recovery into the existing multi-document engine.
"""

import asyncio
import logging
import os
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import uuid

from src.processing.multi_document_engine import (
    MultiDocumentEngine as BaseMultiDocumentEngine,
    ProcessingResult, DocumentMetadata, ProcessingStatus
)
from src.processing.enhanced_batch_scheduler import EnhancedBatchScheduler, DocumentPriority
from src.processing.streaming_memory_manager import StreamingMemoryManager
from src.processing.checkpoint_recovery_system import CheckpointRecoverySystem, CheckpointStatus
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class MultiDocumentEngineEnhanced(BaseMultiDocumentEngine):
    """
    Enhanced multi-document engine with Phase D.3 capabilities.
    
    Adds:
    - Intelligent batch scheduling
    - Streaming memory management
    - Checkpoint recovery
    - Resource-aware processing
    """
    
    def __init__(
        self,
        service_manager: ServiceManager,
        max_workers: int = 4,
        memory_limit_mb: int = 2000,
        enable_checkpoints: bool = True
    ):
        """Initialize enhanced engine with advanced capabilities"""
        # Initialize base engine with max_workers
        super().__init__(max_workers=max_workers)
        
        # Store service manager for enhanced features
        self.service_manager = service_manager
        
        # Add enhanced capabilities
        self.batch_scheduler = EnhancedBatchScheduler(
            max_workers=max_workers,
            max_memory_mb=memory_limit_mb
        )
        self.memory_manager = StreamingMemoryManager(
            memory_limit_mb=memory_limit_mb
        )
        self.checkpoint_system = CheckpointRecoverySystem()
        
        self.enable_checkpoints = enable_checkpoints
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Track active batch processing
        self._active_batches = {}
        self._checkpoint_tasks = {}
    
    async def process_document_batch_enhanced(
        self,
        documents: List[Dict[str, Any]],
        batch_id: Optional[str] = None,
        enable_recovery: bool = True,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Enhanced batch processing with intelligent scheduling.
        
        Args:
            documents: List of document dictionaries with metadata
            batch_id: Optional batch identifier (generated if not provided)
            enable_recovery: Enable checkpoint recovery
            progress_callback: Optional progress callback function
            
        Returns:
            Batch processing results with statistics
        """
        if not batch_id:
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        try:
            # Check for existing checkpoint
            if enable_recovery:
                recovery_state = await self._attempt_recovery(batch_id)
                if recovery_state:
                    documents = self._filter_recovered_documents(documents, recovery_state)
                    self.logger.info(
                        f"Recovered batch {batch_id}: "
                        f"{len(recovery_state['completed_documents'])} already completed"
                    )
            
            # Analyze and prioritize documents
            enhanced_documents = await self._analyze_documents(documents)
            
            # Add batch to scheduler with intelligent scheduling
            await self.batch_scheduler.add_document_batch(enhanced_documents)
            
            # Set up automatic checkpointing
            checkpoint_task = None
            if self.enable_checkpoints:
                checkpoint_task = asyncio.create_task(
                    self.checkpoint_system.auto_checkpoint_monitor(
                        batch_id, self.batch_scheduler
                    )
                )
                self._checkpoint_tasks[batch_id] = checkpoint_task
            
            # Process batch with streaming memory management
            results = await self._process_with_streaming(
                batch_id, enhanced_documents, progress_callback
            )
            
            # Create final checkpoint
            if self.enable_checkpoints:
                await self.checkpoint_system.create_checkpoint(
                    batch_id, self.batch_scheduler, CheckpointStatus.COMPLETED
                )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Enhanced batch processing failed: {e}")
            
            # Create emergency checkpoint before failing
            if self.enable_checkpoints:
                try:
                    await self.checkpoint_system.create_checkpoint(
                        batch_id, self.batch_scheduler, CheckpointStatus.FAILED
                    )
                except Exception as cp_error:
                    self.logger.error(f"Emergency checkpoint failed: {cp_error}")
            
            raise
            
        finally:
            # Clean up checkpoint task
            if batch_id in self._checkpoint_tasks:
                self._checkpoint_tasks[batch_id].cancel()
                del self._checkpoint_tasks[batch_id]
    
    async def _analyze_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze documents and add metadata for intelligent scheduling"""
        enhanced_docs = []
        
        for doc in documents:
            # Determine document size
            file_path = doc.get("file_path", doc.get("path", ""))
            file_size = 0
            
            try:
                if file_path and os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
            except Exception:
                pass
            
            # Determine priority based on metadata
            priority = "normal"
            if doc.get("priority"):
                priority = doc["priority"]
            elif doc.get("urgent", False):
                priority = "high"
            elif file_size > 10 * 1024 * 1024:  # Large files
                priority = "low"
            
            # Add enhanced metadata
            enhanced_doc = doc.copy()
            enhanced_doc.update({
                "size": file_size,
                "priority": priority,
                "type": self._determine_doc_type(file_path),
                "dependencies": doc.get("dependencies", [])
            })
            
            enhanced_docs.append(enhanced_doc)
        
        return enhanced_docs
    
    async def _process_with_streaming(
        self,
        batch_id: str,
        documents: List[Dict[str, Any]],
        progress_callback: Optional[callable]
    ) -> Dict[str, Any]:
        """Process documents with streaming memory management"""
        results = {}
        start_time = datetime.now()
        
        # Create document paths list
        doc_paths = [doc.get("file_path", doc.get("path", "")) for doc in documents]
        
        # Process with streaming memory manager
        processed_count = 0
        async for result in self.memory_manager.stream_document_batch(
            doc_paths,
            chunk_size=5,
            progress_callback=progress_callback
        ):
            # Convert streaming result to ProcessingResult
            doc_path = result["document"]
            doc_id = self._get_doc_id(doc_path, documents)
            
            if result["status"] == "success":
                processing_result = ProcessingResult(
                    document_id=doc_id,
                    document_path=doc_path,
                    document_format=self._determine_doc_type(doc_path),
                    success=True,
                    processing_time=result.get("processing_time", 0),
                    status=ProcessingStatus.COMPLETED
                )
            else:
                processing_result = ProcessingResult(
                    document_id=doc_id,
                    document_path=doc_path,
                    document_format=self._determine_doc_type(doc_path),
                    success=False,
                    error_message=result.get("error", "Unknown error"),
                    status=ProcessingStatus.FAILED
                )
            
            results[doc_id] = processing_result
            processed_count += 1
        
        # Get final statistics
        scheduler_stats = self.batch_scheduler.get_stats()
        memory_stats = self.memory_manager.get_metrics()
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "batch_id": batch_id,
            "total_documents": len(documents),
            "processed": processed_count,
            "successful": scheduler_stats["successful_jobs"],
            "failed": scheduler_stats["failed_jobs"],
            "processing_time": processing_time,
            "results": results,
            "statistics": {
                "scheduler": scheduler_stats,
                "memory": memory_stats,
                "avg_time_per_doc": processing_time / processed_count if processed_count > 0 else 0
            }
        }
    
    async def _attempt_recovery(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Attempt to recover from existing checkpoint"""
        checkpoints = self.checkpoint_system.list_checkpoints(batch_id)
        
        if not checkpoints:
            return None
        
        # Use most recent checkpoint
        latest_checkpoint = checkpoints[0]
        
        try:
            recovery_state = await self.checkpoint_system.recover_from_checkpoint(
                latest_checkpoint["checkpoint_id"]
            )
            return recovery_state
            
        except Exception as e:
            self.logger.error(f"Checkpoint recovery failed: {e}")
            return None
    
    def _filter_recovered_documents(
        self,
        documents: List[Dict[str, Any]],
        recovery_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter out already processed documents"""
        completed = recovery_state.get("completed_documents", set())
        failed = recovery_state.get("failed_documents", set())
        
        # Only reprocess failed and pending documents
        filtered = []
        for doc in documents:
            doc_id = doc.get("id", doc.get("file_path", ""))
            if doc_id not in completed:
                # Add retry flag for failed documents
                if doc_id in failed:
                    doc["retry"] = True
                filtered.append(doc)
        
        return filtered
    
    def _determine_doc_type(self, file_path: str) -> str:
        """Determine document type from file path"""
        if not file_path:
            return "unknown"
        
        ext = os.path.splitext(file_path)[1].lower()
        type_map = {
            ".pdf": "pdf",
            ".txt": "text",
            ".md": "markdown",
            ".json": "json",
            ".xml": "xml",
            ".doc": "word",
            ".docx": "word"
        }
        
        return type_map.get(ext, "unknown")
    
    def _get_doc_id(self, doc_path: str, documents: List[Dict[str, Any]]) -> str:
        """Get document ID from path"""
        for doc in documents:
            if doc.get("file_path") == doc_path or doc.get("path") == doc_path:
                return doc.get("id", doc_path)
        return doc_path
    
    async def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Get current status of a batch"""
        scheduler_stats = self.batch_scheduler.get_stats()
        
        # Check for checkpoints
        checkpoints = self.checkpoint_system.list_checkpoints(batch_id)
        
        return {
            "batch_id": batch_id,
            "active": batch_id in self._active_batches,
            "scheduler_stats": scheduler_stats,
            "checkpoints": checkpoints,
            "checkpoint_enabled": self.enable_checkpoints
        }
    
    async def cancel_batch(self, batch_id: str) -> bool:
        """Cancel batch processing"""
        try:
            # Cancel checkpoint task
            if batch_id in self._checkpoint_tasks:
                self._checkpoint_tasks[batch_id].cancel()
            
            # Create cancellation checkpoint
            if self.enable_checkpoints:
                await self.checkpoint_system.create_checkpoint(
                    batch_id, self.batch_scheduler, CheckpointStatus.FAILED
                )
            
            # Mark batch as cancelled
            if batch_id in self._active_batches:
                self._active_batches[batch_id]["status"] = "cancelled"
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cancel batch {batch_id}: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        try:
            # Shutdown scheduler
            self.batch_scheduler.shutdown()
            
            # Cancel all checkpoint tasks
            for task in self._checkpoint_tasks.values():
                task.cancel()
            
            # Clean up old checkpoints
            self.checkpoint_system.cleanup_old_checkpoints(days=7)
            
            # Base cleanup
            super().cleanup()
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")


# Convenience function
def create_enhanced_engine(
    service_manager: ServiceManager,
    **kwargs
) -> MultiDocumentEngineEnhanced:
    """Create enhanced multi-document engine instance"""
    return MultiDocumentEngineEnhanced(service_manager, **kwargs)


if __name__ == "__main__":
    # Test enhanced engine
    import asyncio
    from src.core.service_manager import ServiceManager
    
    async def test_enhanced_engine():
        service_manager = ServiceManager()
        engine = create_enhanced_engine(service_manager, max_workers=2)
        
        # Test documents
        test_docs = [
            {
                "id": "doc1",
                "file_path": "/path/to/important.pdf",
                "priority": "high"
            },
            {
                "id": "doc2", 
                "file_path": "/path/to/report.txt",
                "dependencies": ["doc1"]
            },
            {
                "id": "doc3",
                "file_path": "/path/to/large_file.pdf",
                "priority": "low"
            }
        ]
        
        try:
            # Process with progress tracking
            def progress(current, total):
                print(f"Progress: {current}/{total} ({current/total*100:.1f}%)")
            
            results = await engine.process_document_batch_enhanced(
                test_docs,
                batch_id="test_batch_001",
                progress_callback=progress
            )
            
            print(f"\nProcessing complete:")
            print(f"- Total: {results['total_documents']}")
            print(f"- Successful: {results['successful']}")
            print(f"- Failed: {results['failed']}")
            print(f"- Time: {results['processing_time']:.2f}s")
            
            # Check batch status
            status = await engine.get_batch_status("test_batch_001")
            print(f"\nBatch status: {status}")
            
        finally:
            engine.cleanup()
    
    asyncio.run(test_enhanced_engine())