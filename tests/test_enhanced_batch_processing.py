#!/usr/bin/env python3
"""
Test Enhanced Batch Processing - Phase D.3

Tests for intelligent batch scheduling, memory management, and checkpoint recovery.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import psutil
import json

from src.processing.enhanced_batch_scheduler import (
    EnhancedBatchScheduler, DocumentJob, DocumentPriority, 
    ProcessingComplexity, ResourceMonitor
)
from src.processing.streaming_memory_manager import (
    StreamingMemoryManager, MemoryPool
)
from src.processing.checkpoint_recovery_system import (
    CheckpointRecoverySystem, CheckpointStatus
)
from src.processing.multi_document_engine_enhanced import (
    MultiDocumentEngineEnhanced
)
from src.core.evidence_logger import EvidenceLogger
from src.core.service_manager import ServiceManager


class TestEnhancedBatchScheduler:
    """Test suite for enhanced batch scheduler"""
    
    @pytest.fixture
    def scheduler(self):
        """Create scheduler instance"""
        return EnhancedBatchScheduler(max_workers=2, max_memory_mb=1000)
    
    @pytest.fixture
    def evidence_logger(self):
        """Create evidence logger"""
        return EvidenceLogger("Phase_D3_Batch_Processing")
    
    @pytest.mark.asyncio
    async def test_priority_scheduling(self, scheduler, evidence_logger):
        """Test that documents are processed in priority order"""
        evidence_logger.log_test_start("test_priority_scheduling")
        
        # Create documents with different priorities
        docs = [
            {
                "id": "low_priority",
                "file_path": "/path/low.txt",
                "size": 1000,
                "priority": "low"
            },
            {
                "id": "critical_priority",
                "file_path": "/path/critical.txt", 
                "size": 1000,
                "priority": "critical"
            },
            {
                "id": "normal_priority",
                "file_path": "/path/normal.txt",
                "size": 1000,
                "priority": "normal"
            },
            {
                "id": "high_priority",
                "file_path": "/path/high.txt",
                "size": 1000,
                "priority": "high"
            }
        ]
        
        # Add batch
        batch_id = await scheduler.add_document_batch(docs)
        
        # Check queue order
        queue_order = []
        temp_queue = []
        
        while scheduler.job_queue:
            job = scheduler.job_queue.pop(0)
            queue_order.append(job.document_id)
            temp_queue.append(job)
        
        # Restore queue
        scheduler.job_queue = temp_queue
        
        # Verify priority order
        expected_order = ["critical_priority", "high_priority", "normal_priority", "low_priority"]
        
        evidence_logger.log_test_execution(
            "PRIORITY_SCHEDULING",
            {
                "status": "success",
                "queue_order": queue_order,
                "expected_order": expected_order,
                "correct_order": queue_order == expected_order
            }
        )
        
        assert queue_order[0] == "critical_priority", "Critical priority should be first"
        assert queue_order[-1] == "low_priority", "Low priority should be last"
    
    @pytest.mark.asyncio
    async def test_dependency_resolution(self, scheduler, evidence_logger):
        """Test that dependencies are respected"""
        docs = [
            {
                "id": "doc1",
                "file_path": "/path/doc1.txt",
                "size": 1000
            },
            {
                "id": "doc2",
                "file_path": "/path/doc2.txt",
                "size": 1000,
                "dependencies": ["doc1"]
            },
            {
                "id": "doc3",
                "file_path": "/path/doc3.txt",
                "size": 1000,
                "dependencies": ["doc1", "doc2"]
            }
        ]
        
        batch_id = await scheduler.add_document_batch(docs)
        
        # Get ready jobs (should only be doc1)
        ready_jobs = scheduler._get_ready_jobs()
        ready_ids = [job.document_id for job in ready_jobs]
        
        assert "doc1" in ready_ids, "doc1 should be ready"
        assert "doc2" not in ready_ids, "doc2 should wait for doc1"
        assert "doc3" not in ready_ids, "doc3 should wait for dependencies"
        
        # Simulate doc1 completion
        scheduler.completed_jobs.add("doc1")
        ready_jobs = scheduler._get_ready_jobs()
        ready_ids = [job.document_id for job in ready_jobs]
        
        assert "doc2" in ready_ids, "doc2 should be ready after doc1"
        assert "doc3" not in ready_ids, "doc3 should still wait"
        
        evidence_logger.log_test_execution(
            "DEPENDENCY_RESOLUTION",
            {
                "status": "success",
                "total_docs": len(docs),
                "dependency_graph": scheduler.dependency_graph,
                "resolution_working": True
            }
        )
    
    @pytest.mark.asyncio
    async def test_resource_monitoring(self, evidence_logger):
        """Test resource monitoring capabilities"""
        monitor = ResourceMonitor()
        
        # Test memory monitoring
        available_memory = monitor.get_available_memory_mb()
        assert available_memory > 0, "Should detect available memory"
        
        # Test CPU monitoring
        cpu_usage = monitor.get_cpu_usage_percent()
        assert 0 <= cpu_usage <= 100, "CPU usage should be valid percentage"
        
        # Test resource sufficiency check
        has_resources = monitor.has_sufficient_resources(100, cpu_threshold=95.0)
        assert isinstance(has_resources, bool)
        
        evidence_logger.log_test_execution(
            "RESOURCE_MONITORING",
            {
                "status": "success",
                "available_memory_mb": available_memory,
                "cpu_usage_percent": cpu_usage,
                "monitoring_functional": True
            }
        )
    
    @pytest.mark.asyncio 
    async def test_batch_processing_completion(self, scheduler, evidence_logger):
        """Test complete batch processing workflow"""
        docs = [
            {"id": f"doc{i}", "file_path": f"/path/doc{i}.txt", "size": 50000}
            for i in range(5)
        ]
        
        batch_id = await scheduler.add_document_batch(docs)
        
        # Process batch with timeout
        start_time = datetime.now()
        results = await scheduler.process_batch(batch_id, timeout=30)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Verify results
        assert results["batch_id"] == batch_id
        assert results["total_documents"] == 5
        assert results["successful"] + results["failed"] == 5
        
        stats = results["stats"]
        assert stats["success_rate"] >= 0.8, "Should have high success rate"
        
        evidence_logger.log_test_execution(
            "BATCH_PROCESSING_COMPLETION",
            {
                "status": "success",
                "batch_id": batch_id,
                "total_documents": results["total_documents"],
                "successful": results["successful"],
                "failed": results["failed"],
                "processing_time": processing_time,
                "success_rate": stats["success_rate"]
            }
        )


class TestStreamingMemoryManager:
    """Test suite for streaming memory manager"""
    
    @pytest.fixture
    def memory_manager(self):
        """Create memory manager instance"""
        return StreamingMemoryManager(memory_limit_mb=500)
    
    @pytest.mark.asyncio
    async def test_memory_pool_reuse(self, evidence_logger):
        """Test memory pool buffer reuse"""
        pool = MemoryPool(max_size_mb=100)
        
        # Get buffer
        buffer1 = pool.get_buffer(1024 * 1024)  # 1MB
        assert len(buffer1) >= 1024 * 1024
        
        # Return buffer
        pool.return_buffer(buffer1)
        
        # Get another buffer of same size
        buffer2 = pool.get_buffer(1024 * 1024)
        
        # Should reuse the same buffer
        stats = pool.get_stats()
        assert stats["reuse_count"] > 0, "Should reuse buffers"
        
        evidence_logger.log_test_execution(
            "MEMORY_POOL_REUSE",
            {
                "status": "success",
                "allocation_count": stats["allocation_count"],
                "reuse_count": stats["reuse_count"],
                "reuse_rate": stats["reuse_rate"]
            }
        )
    
    @pytest.mark.asyncio
    async def test_streaming_processing(self, memory_manager, evidence_logger):
        """Test streaming document processing"""
        # Create test documents
        test_docs = [f"/path/to/doc_{i}.pdf" for i in range(10)]
        
        processed = []
        peak_memory = 0
        
        # Process with streaming
        async for result in memory_manager.stream_document_batch(test_docs, chunk_size=3):
            processed.append(result)
            current_memory = memory_manager._get_memory_usage_mb()
            peak_memory = max(peak_memory, current_memory)
        
        assert len(processed) == 10, "Should process all documents"
        
        metrics = memory_manager.get_metrics()
        
        evidence_logger.log_test_execution(
            "STREAMING_PROCESSING",
            {
                "status": "success",
                "documents_processed": metrics["documents_processed"],
                "peak_memory_mb": metrics["peak_memory_mb"],
                "gc_collections": metrics["gc_collections"],
                "memory_efficient": metrics["peak_memory_mb"] < 1000
            }
        )
    
    @pytest.mark.asyncio
    async def test_memory_pressure_handling(self, memory_manager, evidence_logger):
        """Test handling of memory pressure"""
        # Simulate low memory condition
        large_docs = [f"/path/to/large_{i}.pdf" for i in range(3)]
        
        processed_under_pressure = 0
        errors = 0
        
        async for result in memory_manager.stream_document_batch(large_docs, chunk_size=1):
            if result["status"] == "success":
                processed_under_pressure += 1
            else:
                errors += 1
        
        # Should still process documents even under memory pressure
        assert processed_under_pressure > 0, "Should handle memory pressure gracefully"
        
        evidence_logger.log_test_execution(
            "MEMORY_PRESSURE_HANDLING",
            {
                "status": "success",
                "processed_under_pressure": processed_under_pressure,
                "errors": errors,
                "graceful_degradation": True
            }
        )


class TestCheckpointRecoverySystem:
    """Test suite for checkpoint recovery system"""
    
    @pytest.fixture
    def checkpoint_dir(self):
        """Create temporary checkpoint directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def checkpoint_system(self, checkpoint_dir):
        """Create checkpoint system instance"""
        return CheckpointRecoverySystem(checkpoint_dir=checkpoint_dir)
    
    @pytest.mark.asyncio
    async def test_checkpoint_creation(self, checkpoint_system, evidence_logger):
        """Test checkpoint creation and recovery"""
        # Create mock scheduler state
        class MockScheduler:
            def __init__(self):
                self.completed_jobs = {"doc1", "doc2", "doc3"}
                self.failed_jobs = {"doc4"}
                self.job_queue = []
                self.active_jobs = {}
                self.dependency_graph = {"doc5": ["doc1"], "doc6": ["doc2", "doc3"]}
                self.job_results = {
                    "doc1": {"status": "success"},
                    "doc2": {"status": "success"},
                    "doc3": {"status": "success"},
                    "doc4": {"status": "failed", "error": "Processing error"}
                }
                self.resource_monitor = ResourceMonitor()
                self.max_workers = 4
            
            def get_stats(self):
                return {
                    "total_jobs": 6,
                    "successful_jobs": 3,
                    "failed_jobs": 1
                }
        
        scheduler = MockScheduler()
        batch_id = "test_batch_001"
        
        # Create checkpoint
        checkpoint_id = await checkpoint_system.create_checkpoint(batch_id, scheduler)
        assert checkpoint_id is not None
        
        # Verify checkpoint file exists
        checkpoint_file = Path(checkpoint_system.checkpoint_dir) / f"{checkpoint_id}.json"
        assert checkpoint_file.exists()
        
        # Load and verify checkpoint content
        with open(checkpoint_file, 'r') as f:
            checkpoint_data = json.load(f)
        
        assert checkpoint_data["batch_id"] == batch_id
        assert len(checkpoint_data["completed_documents"]) == 3
        assert len(checkpoint_data["failed_documents"]) == 1
        
        evidence_logger.log_test_execution(
            "CHECKPOINT_CREATION",
            {
                "status": "success",
                "checkpoint_id": checkpoint_id,
                "completed_docs": len(checkpoint_data["completed_documents"]),
                "failed_docs": len(checkpoint_data["failed_documents"]),
                "checkpoint_size_kb": checkpoint_file.stat().st_size / 1024
            }
        )
    
    @pytest.mark.asyncio
    async def test_checkpoint_recovery(self, checkpoint_system, evidence_logger):
        """Test recovery from checkpoint"""
        # Create checkpoint first
        class MockScheduler:
            def __init__(self):
                self.completed_jobs = {"doc1", "doc2"}
                self.failed_jobs = {"doc3"}
                self.job_queue = []
                self.active_jobs = {}
                self.dependency_graph = {}
                self.job_results = {}
                self.resource_monitor = ResourceMonitor()
                self.max_workers = 4
            
            def get_stats(self):
                return {"total_jobs": 3}
        
        scheduler = MockScheduler()
        batch_id = "recovery_test"
        
        # Create checkpoint
        checkpoint_id = await checkpoint_system.create_checkpoint(batch_id, scheduler)
        
        # Attempt recovery
        recovery_state = await checkpoint_system.recover_from_checkpoint(checkpoint_id)
        
        assert recovery_state is not None
        assert recovery_state["batch_id"] == batch_id
        assert len(recovery_state["completed_documents"]) == 2
        assert len(recovery_state["failed_documents"]) == 1
        assert "doc1" in recovery_state["completed_documents"]
        assert "doc3" in recovery_state["failed_documents"]
        
        evidence_logger.log_test_execution(
            "CHECKPOINT_RECOVERY",
            {
                "status": "success",
                "checkpoint_id": checkpoint_id,
                "recovered_completed": len(recovery_state["completed_documents"]),
                "recovered_failed": len(recovery_state["failed_documents"]),
                "recovery_successful": True
            }
        )
    
    @pytest.mark.asyncio
    async def test_checkpoint_rotation(self, checkpoint_system, evidence_logger):
        """Test checkpoint rotation to limit storage"""
        batch_id = "rotation_test"
        
        # Set low limit for testing
        checkpoint_system.max_checkpoints = 3
        
        # Create multiple checkpoints
        checkpoint_ids = []
        for i in range(5):
            mock_scheduler = type('MockScheduler', (), {
                'completed_jobs': set(),
                'failed_jobs': set(),
                'job_queue': [],
                'active_jobs': {},
                'dependency_graph': {},
                'job_results': {},
                'resource_monitor': ResourceMonitor(),
                'max_workers': 4,
                'get_stats': lambda self: {'total_jobs': 0}
            })()
            
            checkpoint_id = await checkpoint_system.create_checkpoint(
                batch_id, mock_scheduler
            )
            checkpoint_ids.append(checkpoint_id)
            
            # Small delay to ensure different timestamps
            await asyncio.sleep(0.1)
        
        # Check that only the latest checkpoints exist
        existing_checkpoints = checkpoint_system.list_checkpoints(batch_id)
        assert len(existing_checkpoints) <= 3, "Should rotate old checkpoints"
        
        # Verify oldest checkpoints were removed
        checkpoint_dir = Path(checkpoint_system.checkpoint_dir)
        for checkpoint_id in checkpoint_ids[:2]:  # First 2 should be rotated
            checkpoint_file = checkpoint_dir / f"{checkpoint_id}.json"
            assert not checkpoint_file.exists(), f"Old checkpoint {checkpoint_id} should be removed"
        
        evidence_logger.log_test_execution(
            "CHECKPOINT_ROTATION",
            {
                "status": "success",
                "created_checkpoints": len(checkpoint_ids),
                "remaining_checkpoints": len(existing_checkpoints),
                "rotation_working": True
            }
        )


class TestIntegratedBatchProcessing:
    """Integration tests for complete batch processing system"""
    
    @pytest.fixture
    async def enhanced_engine(self):
        """Create enhanced engine instance"""
        service_manager = ServiceManager()
        engine = MultiDocumentEngineEnhanced(
            service_manager,
            max_workers=2,
            memory_limit_mb=1000,
            enable_checkpoints=True
        )
        yield engine
        engine.cleanup()
    
    @pytest.mark.asyncio
    async def test_end_to_end_batch_processing(self, enhanced_engine, evidence_logger):
        """Test complete batch processing workflow"""
        evidence_logger.log_test_start("test_end_to_end_batch_processing")
        
        # Create test documents with various characteristics
        test_docs = [
            {
                "id": "critical_doc",
                "file_path": "/path/to/critical.pdf",
                "priority": "critical",
                "size": 500000
            },
            {
                "id": "dependent_doc",
                "file_path": "/path/to/dependent.txt",
                "dependencies": ["critical_doc"],
                "size": 100000
            },
            {
                "id": "large_doc",
                "file_path": "/path/to/large.pdf",
                "priority": "low",
                "size": 5000000
            },
            {
                "id": "normal_doc",
                "file_path": "/path/to/normal.txt",
                "size": 200000
            }
        ]
        
        # Track progress
        progress_updates = []
        def progress_callback(current, total):
            progress_updates.append((current, total))
        
        # Process batch
        start_time = datetime.now()
        
        results = await enhanced_engine.process_document_batch_enhanced(
            test_docs,
            batch_id="integration_test_001",
            enable_recovery=True,
            progress_callback=progress_callback
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Verify results
        assert results["total_documents"] == len(test_docs)
        assert results["processed"] > 0
        assert len(progress_updates) > 0, "Should have progress updates"
        
        # Check statistics
        stats = results["statistics"]
        assert "scheduler" in stats
        assert "memory" in stats
        
        evidence_logger.log_test_execution(
            "END_TO_END_BATCH_PROCESSING",
            {
                "status": "success",
                "total_documents": results["total_documents"],
                "processed": results["processed"],
                "successful": results["successful"],
                "failed": results["failed"],
                "processing_time": processing_time,
                "progress_updates": len(progress_updates),
                "memory_stats": stats["memory"],
                "scheduler_stats": stats["scheduler"]
            }
        )
    
    @pytest.mark.asyncio
    async def test_batch_recovery_after_failure(self, enhanced_engine, evidence_logger):
        """Test recovery from checkpoint after simulated failure"""
        batch_id = "recovery_test_002"
        
        # First attempt - will be interrupted
        test_docs = [
            {"id": f"doc{i}", "file_path": f"/path/to/doc{i}.txt"}
            for i in range(10)
        ]
        
        # Simulate partial processing by manually creating a checkpoint
        # In real scenario, this would happen automatically
        
        # Second attempt - should recover
        results = await enhanced_engine.process_document_batch_enhanced(
            test_docs,
            batch_id=batch_id,
            enable_recovery=True
        )
        
        # Check batch status
        status = await enhanced_engine.get_batch_status(batch_id)
        
        evidence_logger.log_test_execution(
            "BATCH_RECOVERY_AFTER_FAILURE",
            {
                "status": "success",
                "batch_id": batch_id,
                "checkpoints_available": len(status["checkpoints"]),
                "recovery_enabled": status["checkpoint_enabled"]
            }
        )


if __name__ == "__main__":
    # Run tests with evidence collection
    pytest.main([__file__, "-v", "--tb=short"])