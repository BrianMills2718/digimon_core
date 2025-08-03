"""
Memory Manager for Multi-Document Processing

Manages memory usage during large-scale document processing with monitoring,
limits, and efficient resource allocation.
"""

import logging
import psutil
import asyncio
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import gc
import threading

logger = logging.getLogger(__name__)


class MemoryStatus(Enum):
    """Memory usage status"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    OVERFLOW = "overflow"


@dataclass
class MemorySnapshot:
    """Snapshot of memory usage at a point in time"""
    timestamp: float
    total_memory: int
    available_memory: int
    used_memory: int
    memory_percent: float
    process_memory: int


class MemoryManager:
    """Manages memory during document processing"""
    
    def __init__(self, warning_threshold: float = 0.8, critical_threshold: float = 0.9):
        """Initialize memory manager
        
        Args:
            warning_threshold: Memory usage threshold for warnings (0.0-1.0)
            critical_threshold: Memory usage threshold for critical alerts (0.0-1.0)
        """
        self.logger = logger
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        
        # Memory tracking
        self.memory_limit: Optional[int] = None
        self.memory_overflow_events = 0
        self._peak_memory_usage = 0
        self._memory_snapshots: List[MemorySnapshot] = []
        self._monitoring_active = False
        
        # Process monitoring
        self.process = psutil.Process()
        
        # Lock for thread safety
        self._lock = threading.Lock()
    
    def set_memory_limit(self, limit_bytes: int):
        """Set memory limit in bytes"""
        self.memory_limit = limit_bytes
        self.logger.info(f"Set memory limit to {limit_bytes / (1024**3):.2f} GB")
    
    def get_current_memory_usage(self) -> int:
        """Get current memory usage in bytes"""
        try:
            # Force garbage collection before measuring
            gc.collect()
            
            # Get process memory info
            memory_info = self.process.memory_info()
            current_usage = memory_info.rss  # Resident Set Size
            
            # Account for Python baseline memory (approximately 100MB for imports/libraries)
            # This helps get a more accurate measure of actual document processing memory
            python_baseline = 100 * 1024 * 1024  # 100MB baseline for Python + libraries
            adjusted_usage = max(0, current_usage - python_baseline)
            
            # Update peak usage
            with self._lock:
                if adjusted_usage > self._peak_memory_usage:
                    self._peak_memory_usage = adjusted_usage
            
            return adjusted_usage
            
        except Exception as e:
            self.logger.warning(f"Failed to get memory usage: {e}")
            return 0
    
    def get_peak_memory_usage(self) -> int:
        """Get peak memory usage since initialization"""
        with self._lock:
            return self._peak_memory_usage
    
    def get_system_memory_info(self) -> Dict[str, float]:
        """Get system memory information"""
        try:
            memory = psutil.virtual_memory()
            return {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            }
        except Exception as e:
            self.logger.warning(f"Failed to get system memory info: {e}")
            return {
                'total': 0,
                'available': 0,
                'used': 0,
                'percent': 0
            }
    
    def get_memory_status(self) -> MemoryStatus:
        """Get current memory status"""
        if self.memory_limit is None:
            # No limit set, use system memory
            system_info = self.get_system_memory_info()
            usage_percent = system_info['percent'] / 100.0
        else:
            # Use set limit
            current_usage = self.get_current_memory_usage()
            usage_percent = current_usage / self.memory_limit
        
        if usage_percent >= 1.0:
            return MemoryStatus.OVERFLOW
        elif usage_percent >= self.critical_threshold:
            return MemoryStatus.CRITICAL
        elif usage_percent >= self.warning_threshold:
            return MemoryStatus.WARNING
        else:
            return MemoryStatus.NORMAL
    
    async def monitor_memory_continuous(self, interval: float = 1.0):
        """Continuously monitor memory usage"""
        self._monitoring_active = True
        self.logger.info("Started continuous memory monitoring")
        
        while self._monitoring_active:
            try:
                snapshot = self._take_memory_snapshot()
                
                with self._lock:
                    self._memory_snapshots.append(snapshot)
                    
                    # Keep only last 1000 snapshots
                    if len(self._memory_snapshots) > 1000:
                        self._memory_snapshots = self._memory_snapshots[-1000:]
                
                # Check for memory issues
                status = self.get_memory_status()
                if status == MemoryStatus.OVERFLOW:
                    self.memory_overflow_events += 1
                    self.logger.error("Memory overflow detected!")
                    await self._handle_memory_overflow()
                elif status == MemoryStatus.CRITICAL:
                    self.logger.warning("Critical memory usage detected")
                    await self._handle_critical_memory()
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in memory monitoring: {e}")
                await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """Stop continuous memory monitoring"""
        self._monitoring_active = False
        self.logger.info("Stopped memory monitoring")
    
    def _take_memory_snapshot(self) -> MemorySnapshot:
        """Take a snapshot of current memory usage"""
        system_info = self.get_system_memory_info()
        process_memory = self.get_current_memory_usage()
        
        return MemorySnapshot(
            timestamp=time.time(),
            total_memory=int(system_info['total']),
            available_memory=int(system_info['available']),
            used_memory=int(system_info['used']),
            memory_percent=system_info['percent'],
            process_memory=process_memory
        )
    
    async def _handle_memory_overflow(self):
        """Handle memory overflow situation"""
        self.logger.warning("Handling memory overflow - triggering garbage collection")
        
        # Force garbage collection
        gc.collect()
        
        # Small delay to allow cleanup
        await asyncio.sleep(0.1)
    
    async def _handle_critical_memory(self):
        """Handle critical memory situation"""
        self.logger.warning("Handling critical memory usage")
        
        # Trigger garbage collection
        gc.collect()
        
        # Small delay
        await asyncio.sleep(0.05)
    
    def check_memory_available(self, required_bytes: int) -> bool:
        """Check if required memory is available"""
        current_usage = self.get_current_memory_usage()
        
        if self.memory_limit is None:
            # Use system available memory
            system_info = self.get_system_memory_info()
            available = system_info['available']
        else:
            # Use limit
            available = self.memory_limit - current_usage
        
        return available >= required_bytes
    
    async def wait_for_memory_available(self, required_bytes: int, timeout: float = 30.0):
        """Wait until required memory becomes available"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.check_memory_available(required_bytes):
                return True
            
            # Trigger cleanup
            gc.collect()
            await asyncio.sleep(0.1)
        
        return False
    
    def get_memory_statistics(self) -> Dict[str, float]:
        """Get memory usage statistics"""
        with self._lock:
            if not self._memory_snapshots:
                return {}
            
            # Calculate statistics
            memory_values = [s.process_memory for s in self._memory_snapshots]
            
            return {
                'current': self.get_current_memory_usage(),
                'peak': self._peak_memory_usage,
                'average': sum(memory_values) / len(memory_values),
                'min': min(memory_values),
                'max': max(memory_values),
                'overflow_events': self.memory_overflow_events,
                'snapshots_count': len(self._memory_snapshots)
            }
    
    def estimate_document_memory_usage(self, document_size: int) -> int:
        """Estimate memory usage for processing a document of given size"""
        # Rule of thumb: processing uses 2-3x document size in memory
        # Plus overhead for data structures
        base_multiplier = 2.5
        overhead = 50 * 1024 * 1024  # 50MB overhead
        
        return int(document_size * base_multiplier + overhead)
    
    def can_process_documents(self, document_sizes: List[int]) -> bool:
        """Check if multiple documents can be processed simultaneously"""
        total_estimated = sum(self.estimate_document_memory_usage(size) for size in document_sizes)
        return self.check_memory_available(total_estimated)
    
    def optimize_batch_size(self, document_sizes: List[int], max_batch_size: int = 10) -> int:
        """Optimize batch size based on available memory"""
        if not document_sizes:
            return 0
        
        # Start with maximum and work down
        for batch_size in range(min(max_batch_size, len(document_sizes)), 0, -1):
            batch_sizes = document_sizes[:batch_size]
            if self.can_process_documents(batch_sizes):
                return batch_size
        
        return 1  # At minimum, try to process one document
    
    def cleanup_memory(self):
        """Perform memory cleanup"""
        self.logger.info("Performing memory cleanup")
        
        # Clear snapshots older than 1 hour
        cutoff_time = time.time() - 3600
        with self._lock:
            self._memory_snapshots = [
                s for s in self._memory_snapshots 
                if s.timestamp > cutoff_time
            ]
        
        # Force garbage collection
        gc.collect()
    
    def reset_statistics(self):
        """Reset memory statistics"""
        with self._lock:
            self._memory_snapshots.clear()
            self._peak_memory_usage = self.get_current_memory_usage()
            self.memory_overflow_events = 0
        
        self.logger.info("Reset memory statistics")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_monitoring()
        self.cleanup_memory()