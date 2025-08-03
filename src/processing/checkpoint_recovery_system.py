#!/usr/bin/env python3
"""
Checkpoint Recovery System - Phase D.3 Implementation

System for saving and recovering batch processing state to handle
failures and enable resumable processing.
"""

import json
import pickle
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime
import logging
import asyncio
import shutil
from enum import Enum

logger = logging.getLogger(__name__)


class CheckpointStatus(Enum):
    """Checkpoint status states"""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RECOVERED = "recovered"


@dataclass
class ProcessingCheckpoint:
    """Processing checkpoint for batch recovery"""
    batch_id: str
    checkpoint_id: str
    timestamp: str
    status: str
    completed_documents: List[str]
    failed_documents: List[str]
    pending_documents: List[str]
    processing_state: Dict[str, Any]
    resource_state: Dict[str, Any]
    error_log: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert checkpoint to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingCheckpoint':
        """Create checkpoint from dictionary"""
        return cls(**data)


class CheckpointRecoverySystem:
    """
    System for saving and recovering batch processing state.
    
    Features:
    - Atomic checkpoint creation
    - Automatic checkpoint intervals
    - State recovery with validation
    - Checkpoint compression and rotation
    """
    
    def __init__(self, checkpoint_dir: str = "data/checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.auto_checkpoint_interval = 300  # 5 minutes
        self.max_checkpoints = 10  # Keep last 10 checkpoints per batch
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Active monitoring tasks
        self._monitor_tasks = {}
        
        # Checkpoint statistics
        self.stats = {
            "checkpoints_created": 0,
            "checkpoints_recovered": 0,
            "recovery_failures": 0,
            "total_size_mb": 0.0
        }
    
    async def create_checkpoint(
        self, 
        batch_id: str,
        scheduler: Any,  # EnhancedBatchScheduler
        status: CheckpointStatus = CheckpointStatus.IN_PROGRESS
    ) -> str:
        """
        Create processing checkpoint for recovery.
        
        Args:
            batch_id: Batch identifier
            scheduler: Batch scheduler instance
            status: Checkpoint status
            
        Returns:
            Checkpoint ID
        """
        checkpoint_id = self._generate_checkpoint_id(batch_id)
        timestamp = datetime.now().isoformat()
        
        try:
            # Capture current state
            checkpoint = ProcessingCheckpoint(
                batch_id=batch_id,
                checkpoint_id=checkpoint_id,
                timestamp=timestamp,
                status=status.value,
                completed_documents=list(scheduler.completed_jobs),
                failed_documents=list(scheduler.failed_jobs),
                pending_documents=self._get_pending_documents(scheduler),
                processing_state=self._capture_processing_state(scheduler),
                resource_state=self._capture_resource_state(scheduler),
                error_log=self._capture_error_log(scheduler),
                metadata={
                    "scheduler_stats": scheduler.get_stats(),
                    "checkpoint_version": "1.0"
                }
            )
            
            # Save checkpoint atomically
            await self._save_checkpoint_atomic(checkpoint)
            
            self.stats["checkpoints_created"] += 1
            
            self.logger.info(
                f"Created checkpoint {checkpoint_id} for batch {batch_id} "
                f"({len(checkpoint.completed_documents)} completed, "
                f"{len(checkpoint.pending_documents)} pending)"
            )
            
            # Rotate old checkpoints
            await self._rotate_checkpoints(batch_id)
            
            return checkpoint_id
            
        except Exception as e:
            self.logger.error(f"Failed to create checkpoint: {e}")
            raise
    
    async def recover_from_checkpoint(
        self, 
        checkpoint_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Recover batch processing from checkpoint.
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Returns:
            Recovery state dictionary or None if recovery fails
        """
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
        
        if not checkpoint_file.exists():
            self.logger.error(f"Checkpoint file not found: {checkpoint_id}")
            return None
        
        try:
            # Load checkpoint
            checkpoint = await self._load_checkpoint(checkpoint_file)
            
            # Validate checkpoint integrity
            if not self._validate_checkpoint(checkpoint):
                self.logger.error(f"Checkpoint validation failed: {checkpoint_id}")
                self.stats["recovery_failures"] += 1
                return None
            
            # Create recovery state
            recovery_state = self._create_recovery_state(checkpoint)
            
            # Update checkpoint status
            checkpoint.status = CheckpointStatus.RECOVERED.value
            await self._save_checkpoint_atomic(checkpoint)
            
            self.stats["checkpoints_recovered"] += 1
            
            self.logger.info(
                f"Successfully recovered from checkpoint {checkpoint_id} "
                f"(batch: {checkpoint.batch_id}, "
                f"completed: {len(checkpoint.completed_documents)}, "
                f"pending: {len(checkpoint.pending_documents)})"
            )
            
            return recovery_state
            
        except Exception as e:
            self.logger.error(f"Failed to recover from checkpoint {checkpoint_id}: {e}")
            self.stats["recovery_failures"] += 1
            raise
    
    async def auto_checkpoint_monitor(
        self, 
        batch_id: str,
        scheduler: Any
    ) -> None:
        """
        Monitor batch processing and create automatic checkpoints.
        
        Args:
            batch_id: Batch identifier
            scheduler: Batch scheduler instance
        """
        monitor_id = f"monitor_{batch_id}"
        
        try:
            self.logger.info(
                f"Starting auto-checkpoint monitor for batch {batch_id} "
                f"(interval: {self.auto_checkpoint_interval}s)"
            )
            
            while True:
                await asyncio.sleep(self.auto_checkpoint_interval)
                
                # Check if processing is still active
                stats = scheduler.get_stats()
                if stats["active_jobs"] == 0 and stats["queued_jobs"] == 0:
                    self.logger.info(f"Batch {batch_id} complete, stopping monitor")
                    break
                
                # Create checkpoint
                try:
                    checkpoint_id = await self.create_checkpoint(
                        batch_id, scheduler, CheckpointStatus.IN_PROGRESS
                    )
                    self.logger.debug(f"Auto-checkpoint created: {checkpoint_id}")
                    
                except Exception as e:
                    self.logger.error(f"Auto-checkpoint failed: {e}")
                    
        except asyncio.CancelledError:
            self.logger.info(f"Auto-checkpoint monitor cancelled for batch {batch_id}")
            raise
        
        finally:
            self._monitor_tasks.pop(monitor_id, None)
    
    def _generate_checkpoint_id(self, batch_id: str) -> str:
        """Generate unique checkpoint ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        content = f"{batch_id}_{timestamp}"
        hash_suffix = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"checkpoint_{batch_id}_{timestamp}_{hash_suffix}"
    
    def _get_pending_documents(self, scheduler: Any) -> List[str]:
        """Extract pending documents from scheduler"""
        pending = []
        
        # Documents in queue
        for job in scheduler.job_queue:
            pending.append(job.document_id)
        
        # Documents being processed
        for doc_id in scheduler.active_jobs:
            pending.append(doc_id)
        
        return pending
    
    def _capture_processing_state(self, scheduler: Any) -> Dict[str, Any]:
        """Capture scheduler processing state"""
        return {
            "job_queue": [
                {
                    "document_id": job.document_id,
                    "priority": job.priority.name,
                    "complexity": job.complexity.name,
                    "retry_count": job.retry_count,
                    "dependencies": job.dependencies
                }
                for job in scheduler.job_queue
            ],
            "dependency_graph": {
                doc_id: list(deps)
                for doc_id, deps in scheduler.dependency_graph.items()
            },
            "job_results": dict(scheduler.job_results)
        }
    
    def _capture_resource_state(self, scheduler: Any) -> Dict[str, Any]:
        """Capture resource utilization state"""
        monitor = scheduler.resource_monitor
        
        return {
            "available_memory_mb": monitor.get_available_memory_mb(),
            "cpu_usage_percent": monitor.get_cpu_usage_percent(),
            "max_workers": scheduler.max_workers,
            "active_workers": len(scheduler.active_jobs)
        }
    
    def _capture_error_log(self, scheduler: Any) -> List[Dict[str, Any]]:
        """Capture error information from failed jobs"""
        errors = []
        
        for doc_id in scheduler.failed_jobs:
            result = scheduler.job_results.get(doc_id, {})
            if result.get("status") == "failed":
                errors.append({
                    "document_id": doc_id,
                    "error": result.get("error", "Unknown error"),
                    "retry_count": result.get("retry_count", 0),
                    "timestamp": datetime.now().isoformat()
                })
        
        return errors
    
    async def _save_checkpoint_atomic(self, checkpoint: ProcessingCheckpoint):
        """Save checkpoint atomically to prevent corruption"""
        checkpoint_file = self.checkpoint_dir / f"{checkpoint.checkpoint_id}.json"
        temp_file = checkpoint_file.with_suffix(".tmp")
        
        try:
            # Write to temporary file
            with open(temp_file, 'w') as f:
                json.dump(checkpoint.to_dict(), f, indent=2)
            
            # Atomic rename
            temp_file.replace(checkpoint_file)
            
            # Update size statistics
            file_size_mb = checkpoint_file.stat().st_size / (1024 * 1024)
            self.stats["total_size_mb"] += file_size_mb
            
        except Exception as e:
            # Clean up temp file on error
            if temp_file.exists():
                temp_file.unlink()
            raise
    
    async def _load_checkpoint(self, checkpoint_file: Path) -> ProcessingCheckpoint:
        """Load checkpoint from file"""
        with open(checkpoint_file, 'r') as f:
            data = json.load(f)
        
        return ProcessingCheckpoint.from_dict(data)
    
    def _validate_checkpoint(self, checkpoint: ProcessingCheckpoint) -> bool:
        """Validate checkpoint integrity"""
        # Check required fields
        if not checkpoint.batch_id or not checkpoint.checkpoint_id:
            return False
        
        # Check for data consistency
        all_docs = set(checkpoint.completed_documents + 
                      checkpoint.failed_documents + 
                      checkpoint.pending_documents)
        
        if len(all_docs) == 0:
            self.logger.warning("Checkpoint has no documents")
            return False
        
        # Check for duplicate documents
        total_count = (len(checkpoint.completed_documents) + 
                      len(checkpoint.failed_documents) + 
                      len(checkpoint.pending_documents))
        
        if len(all_docs) != total_count:
            self.logger.warning("Checkpoint has duplicate documents")
            return False
        
        return True
    
    def _create_recovery_state(self, checkpoint: ProcessingCheckpoint) -> Dict[str, Any]:
        """Create recovery state from checkpoint"""
        return {
            "batch_id": checkpoint.batch_id,
            "checkpoint_id": checkpoint.checkpoint_id,
            "completed_documents": set(checkpoint.completed_documents),
            "failed_documents": set(checkpoint.failed_documents),
            "pending_documents": checkpoint.pending_documents,
            "processing_state": checkpoint.processing_state,
            "resource_state": checkpoint.resource_state,
            "error_log": checkpoint.error_log,
            "metadata": checkpoint.metadata,
            "recovery_timestamp": datetime.now().isoformat()
        }
    
    async def _rotate_checkpoints(self, batch_id: str):
        """Rotate old checkpoints to maintain size limits"""
        # Find all checkpoints for this batch
        batch_checkpoints = []
        
        for checkpoint_file in self.checkpoint_dir.glob(f"checkpoint_{batch_id}_*.json"):
            try:
                # Extract timestamp from filename
                parts = checkpoint_file.stem.split('_')
                timestamp_str = f"{parts[2]}_{parts[3]}"
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                batch_checkpoints.append((timestamp, checkpoint_file))
            except Exception as e:
                self.logger.warning(f"Skipping malformed checkpoint file: {checkpoint_file}")
        
        # Sort by timestamp (newest first)
        batch_checkpoints.sort(reverse=True)
        
        # Remove old checkpoints
        if len(batch_checkpoints) > self.max_checkpoints:
            for _, checkpoint_file in batch_checkpoints[self.max_checkpoints:]:
                try:
                    file_size_mb = checkpoint_file.stat().st_size / (1024 * 1024)
                    checkpoint_file.unlink()
                    self.stats["total_size_mb"] -= file_size_mb
                    self.logger.debug(f"Rotated old checkpoint: {checkpoint_file.name}")
                except Exception as e:
                    self.logger.error(f"Failed to rotate checkpoint: {e}")
    
    def list_checkpoints(self, batch_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available checkpoints"""
        checkpoints = []
        
        pattern = f"checkpoint_{batch_id}_*.json" if batch_id else "checkpoint_*.json"
        
        for checkpoint_file in self.checkpoint_dir.glob(pattern):
            try:
                # Load checkpoint metadata
                with open(checkpoint_file, 'r') as f:
                    data = json.load(f)
                
                checkpoints.append({
                    "checkpoint_id": data["checkpoint_id"],
                    "batch_id": data["batch_id"],
                    "timestamp": data["timestamp"],
                    "status": data["status"],
                    "completed": len(data["completed_documents"]),
                    "failed": len(data["failed_documents"]),
                    "pending": len(data["pending_documents"]),
                    "file_size_mb": checkpoint_file.stat().st_size / (1024 * 1024)
                })
                
            except Exception as e:
                self.logger.error(f"Failed to read checkpoint {checkpoint_file}: {e}")
        
        # Sort by timestamp
        checkpoints.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return checkpoints
    
    def cleanup_old_checkpoints(self, days: int = 7):
        """Clean up checkpoints older than specified days"""
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        removed_count = 0
        removed_size_mb = 0.0
        
        for checkpoint_file in self.checkpoint_dir.glob("checkpoint_*.json"):
            try:
                if checkpoint_file.stat().st_mtime < cutoff_time:
                    file_size_mb = checkpoint_file.stat().st_size / (1024 * 1024)
                    checkpoint_file.unlink()
                    removed_count += 1
                    removed_size_mb += file_size_mb
                    
            except Exception as e:
                self.logger.error(f"Failed to clean up checkpoint {checkpoint_file}: {e}")
        
        if removed_count > 0:
            self.logger.info(
                f"Cleaned up {removed_count} old checkpoints "
                f"({removed_size_mb:.2f}MB freed)"
            )
            self.stats["total_size_mb"] -= removed_size_mb
    
    def get_stats(self) -> Dict[str, Any]:
        """Get checkpoint system statistics"""
        checkpoint_count = len(list(self.checkpoint_dir.glob("checkpoint_*.json")))
        
        return {
            "checkpoints_created": self.stats["checkpoints_created"],
            "checkpoints_recovered": self.stats["checkpoints_recovered"],
            "recovery_failures": self.stats["recovery_failures"],
            "current_checkpoints": checkpoint_count,
            "total_size_mb": self.stats["total_size_mb"],
            "checkpoint_dir": str(self.checkpoint_dir),
            "auto_interval_seconds": self.auto_checkpoint_interval
        }


if __name__ == "__main__":
    # Test checkpoint system
    import asyncio
    from src.processing.enhanced_batch_scheduler import EnhancedBatchScheduler
    
    async def test_checkpoint_system():
        checkpoint_system = CheckpointRecoverySystem()
        scheduler = EnhancedBatchScheduler()
        
        # Simulate batch processing
        batch_id = "test_batch_001"
        
        # Add some test state
        scheduler.completed_jobs = {"doc1", "doc2", "doc3"}
        scheduler.failed_jobs = {"doc4"}
        scheduler.job_queue = []  # Would have actual jobs
        
        try:
            # Create checkpoint
            checkpoint_id = await checkpoint_system.create_checkpoint(batch_id, scheduler)
            print(f"Created checkpoint: {checkpoint_id}")
            
            # List checkpoints
            checkpoints = checkpoint_system.list_checkpoints(batch_id)
            print(f"\nAvailable checkpoints: {len(checkpoints)}")
            for cp in checkpoints:
                print(f"- {cp['checkpoint_id']}: {cp['completed']} completed, {cp['pending']} pending")
            
            # Simulate recovery
            recovery_state = await checkpoint_system.recover_from_checkpoint(checkpoint_id)
            if recovery_state:
                print(f"\nRecovered state:")
                print(f"- Completed: {len(recovery_state['completed_documents'])}")
                print(f"- Failed: {len(recovery_state['failed_documents'])}")
                print(f"- Pending: {len(recovery_state['pending_documents'])}")
            
            # Get stats
            print(f"\nCheckpoint system stats: {checkpoint_system.get_stats()}")
            
        except Exception as e:
            print(f"Test failed: {e}")
    
    asyncio.run(test_checkpoint_system())