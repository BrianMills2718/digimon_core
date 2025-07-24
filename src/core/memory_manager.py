"""Memory Management Service - Core Infrastructure

Provides centralized memory management for large document processing, vector operations,
and multi-document fusion to prevent memory exhaustion and optimize performance.

Part of Phase 5B: Security & Reliability Enhancement - Memory Management Improvements
"""

import gc
import psutil
import logging
import threading
import time
from typing import Dict, Any, Optional, List, Iterator, Callable, TypeVar
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import weakref

T = TypeVar('T')

@dataclass
class MemoryStats:
    """Memory usage statistics"""
    current_memory_mb: float
    peak_memory_mb: float
    available_memory_mb: float
    memory_usage_percent: float
    swap_usage_mb: float
    gc_collections: int
    timestamp: datetime

@dataclass
class MemoryConfiguration:
    """Memory management configuration"""
    max_memory_mb: int = 1024  # 1GB default
    warning_threshold: float = 0.8  # 80% warning
    critical_threshold: float = 0.9  # 90% critical
    cleanup_threshold: float = 0.85  # 85% cleanup trigger
    gc_frequency: int = 100  # operations between GC
    chunk_size_mb: int = 50  # Default chunk size for streaming
    max_cache_size_mb: int = 256  # Maximum cache size

class MemoryManager:
    """Centralized memory management service with streaming and optimization capabilities"""
    
    def __init__(self, config: MemoryConfiguration = None):
        self.config = config or MemoryConfiguration()
        self.logger = logging.getLogger(__name__)
        self._lock = threading.RLock()
        self._operation_count = 0
        self._peak_memory = 0.0
        self._gc_collections = 0
        self._memory_cache = weakref.WeakValueDictionary()
        self._monitoring_active = False
        self._monitor_thread = None
        
        # Initialize memory monitoring
        self._start_monitoring()
        
        self.logger.info(f"MemoryManager initialized with max_memory={self.config.max_memory_mb}MB")
    
    def _start_monitoring(self):
        """Start background memory monitoring"""
        if not self._monitoring_active:
            self._monitoring_active = True
            self._monitor_thread = threading.Thread(target=self._monitor_memory, daemon=True)
            self._monitor_thread.start()
    
    def _monitor_memory(self):
        """Background memory monitoring thread"""
        while self._monitoring_active:
            try:
                stats = self.get_memory_stats()
                
                # Check thresholds and trigger cleanup if needed
                if stats.memory_usage_percent > self.config.cleanup_threshold:
                    self.logger.warning(f"Memory usage {stats.memory_usage_percent:.1f}% exceeds cleanup threshold")
                    self._perform_cleanup()
                
                if stats.memory_usage_percent > self.config.critical_threshold:
                    self.logger.error(f"Critical memory usage: {stats.memory_usage_percent:.1f}%")
                
                # Update peak memory
                with self._lock:
                    if stats.current_memory_mb > self._peak_memory:
                        self._peak_memory = stats.current_memory_mb
                
            except Exception as e:
                self.logger.error(f"Memory monitoring error: {e}")
            
            # Use event-based monitoring instead of blocking sleep
            # In async context, this would be: await asyncio.sleep(30)
            import asyncio
            try:
                asyncio.create_task(asyncio.sleep(30))
            except RuntimeError:
                # Non-async fallback - use shorter intervals to reduce blocking
                import time
                # Use async sleep if possible to avoid blocking
                try:
                    import asyncio
                    loop = asyncio.get_running_loop()
                    if loop:
                        asyncio.create_task(asyncio.sleep(1.0))
                    else:
                        import time
                        time.sleep(0.1)  # Reduced to 100ms for better responsiveness
                except RuntimeError:
                    import time
                    time.sleep(0.1)  # Minimal blocking fallback
    
    def get_memory_stats(self) -> MemoryStats:
        """Get current memory statistics"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            virtual_memory = psutil.virtual_memory()
            
            current_memory_mb = memory_info.rss / (1024 * 1024)
            available_memory_mb = virtual_memory.available / (1024 * 1024)
            memory_usage_percent = (current_memory_mb / self.config.max_memory_mb) * 100
            swap_usage_mb = getattr(memory_info, 'vms', 0) / (1024 * 1024)
            
            with self._lock:
                peak_memory_mb = max(self._peak_memory, current_memory_mb)
                self._peak_memory = peak_memory_mb
                gc_collections = self._gc_collections
            
            return MemoryStats(
                current_memory_mb=current_memory_mb,
                peak_memory_mb=peak_memory_mb,
                available_memory_mb=available_memory_mb,
                memory_usage_percent=memory_usage_percent,
                swap_usage_mb=swap_usage_mb,
                gc_collections=gc_collections,
                timestamp=datetime.now()
            )
        
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}")
            return MemoryStats(0, 0, 0, 0, 0, 0, datetime.now())
    
    @contextmanager
    def memory_context(self, operation_name: str, max_memory_mb: Optional[int] = None):
        """Context manager for memory-monitored operations"""
        start_stats = self.get_memory_stats()
        operation_max = max_memory_mb or self.config.max_memory_mb
        
        try:
            self.logger.debug(f"Starting memory context for {operation_name}")
            yield self
            
        finally:
            end_stats = self.get_memory_stats()
            memory_used = end_stats.current_memory_mb - start_stats.current_memory_mb
            
            if memory_used > operation_max:
                self.logger.warning(f"Operation {operation_name} exceeded memory limit: {memory_used:.1f}MB > {operation_max}MB")
            
            self.logger.debug(f"Memory context {operation_name}: used {memory_used:.1f}MB")
            
            # Increment operation count and trigger GC if needed
            with self._lock:
                self._operation_count += 1
                if self._operation_count % self.config.gc_frequency == 0:
                    self._perform_gc()
    
    def stream_large_file(self, file_path: str, chunk_size_mb: Optional[int] = None) -> Iterator[bytes]:
        """Stream large files in memory-efficient chunks"""
        chunk_size = (chunk_size_mb or self.config.chunk_size_mb) * 1024 * 1024
        
        try:
            file_path = Path(file_path)
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            
            self.logger.info(f"Streaming file {file_path.name} ({file_size_mb:.1f}MB) in {chunk_size_mb}MB chunks")
            
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    
                    # Check memory before yielding chunk
                    stats = self.get_memory_stats()
                    if stats.memory_usage_percent > self.config.warning_threshold:
                        self.logger.warning(f"High memory usage during file streaming: {stats.memory_usage_percent:.1f}%")
                        self._perform_cleanup()
                    
                    yield chunk
                    
        except Exception as e:
            self.logger.error(f"Error streaming file {file_path}: {e}")
            raise
    
    def process_in_batches(self, items: List[T], batch_size: Optional[int] = None, 
                          processor: Optional[Callable[[List[T]], Any]] = None) -> Iterator[Any]:
        """Process items in memory-efficient batches"""
        if not items:
            return
            
        # Calculate optimal batch size based on memory
        if batch_size is None:
            stats = self.get_memory_stats()
            available_memory_ratio = 1.0 - (stats.memory_usage_percent / 100)
            base_batch_size = 100
            batch_size = max(10, int(base_batch_size * available_memory_ratio))
        
        self.logger.info(f"Processing {len(items)} items in batches of {batch_size}")
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            # Monitor memory before processing batch
            stats = self.get_memory_stats()
            if stats.memory_usage_percent > self.config.warning_threshold:
                self.logger.warning(f"High memory before batch {i//batch_size + 1}: {stats.memory_usage_percent:.1f}%")
                self._perform_cleanup()
            
            if processor:
                try:
                    result = processor(batch)
                    yield result
                except Exception as e:
                    self.logger.error(f"Error processing batch {i//batch_size + 1}: {e}")
                    continue
            else:
                yield batch
            
            # Trigger GC after each batch if memory is high
            if stats.memory_usage_percent > self.config.cleanup_threshold:
                self._perform_gc()
    
    def cache_with_memory_limit(self, key: str, value: Any, size_hint_mb: float = 0):
        """Cache data with automatic memory management"""
        try:
            stats = self.get_memory_stats()
            cache_usage = len(self._memory_cache) * 10  # Rough estimate
            
            # Check if we can add to cache
            if (cache_usage + size_hint_mb) > self.config.max_cache_size_mb:
                self.logger.warning("Cache size limit reached, clearing oldest entries")
                self._clear_cache_lru()
            
            if stats.memory_usage_percent < self.config.warning_threshold:
                self._memory_cache[key] = value
                self.logger.debug(f"Cached item {key} (~{size_hint_mb:.1f}MB)")
            else:
                self.logger.warning(f"Skipping cache due to high memory usage: {stats.memory_usage_percent:.1f}%")
                
        except Exception as e:
            self.logger.error(f"Error caching item {key}: {e}")
    
    def get_from_cache(self, key: str) -> Any:
        """Retrieve item from memory cache"""
        return self._memory_cache.get(key)
    
    def optimize_for_large_operation(self) -> Dict[str, Any]:
        """Prepare memory for large operation"""
        initial_stats = self.get_memory_stats()
        
        # Perform aggressive cleanup
        self._clear_cache_lru()
        self._perform_gc()
        
        final_stats = self.get_memory_stats()
        memory_freed = initial_stats.current_memory_mb - final_stats.current_memory_mb
        
        optimization_info = {
            "memory_freed_mb": memory_freed,
            "initial_usage_percent": initial_stats.memory_usage_percent,
            "final_usage_percent": final_stats.memory_usage_percent,
            "available_memory_mb": final_stats.available_memory_mb,
            "recommended_batch_size": self._calculate_recommended_batch_size(final_stats)
        }
        
        self.logger.info(f"Memory optimization freed {memory_freed:.1f}MB, usage: {final_stats.memory_usage_percent:.1f}%")
        
        return optimization_info
    
    def _perform_cleanup(self):
        """Perform memory cleanup operations"""
        try:
            # Clear cache if needed
            if len(self._memory_cache) > 100:
                self._clear_cache_lru()
            
            # Force garbage collection
            self._perform_gc()
            
            self.logger.debug("Memory cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during memory cleanup: {e}")
    
    def _perform_gc(self):
        """Perform garbage collection"""
        try:
            collected = gc.collect()
            with self._lock:
                self._gc_collections += 1
            
            self.logger.debug(f"GC collected {collected} objects (total collections: {self._gc_collections})")
            
        except Exception as e:
            self.logger.error(f"Error during garbage collection: {e}")
    
    def _clear_cache_lru(self):
        """Clear least recently used cache entries"""
        try:
            # Clear half of the cache (simple LRU approximation)
            if len(self._memory_cache) > 50:
                keys_to_remove = list(self._memory_cache.keys())[:len(self._memory_cache) // 2]
                for key in keys_to_remove:
                    self._memory_cache.pop(key, None)
                
                self.logger.debug(f"Cleared {len(keys_to_remove)} cache entries")
                
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
    
    def _calculate_recommended_batch_size(self, stats: MemoryStats) -> int:
        """Calculate recommended batch size based on available memory"""
        available_ratio = 1.0 - (stats.memory_usage_percent / 100)
        base_size = 100
        return max(10, int(base_size * available_ratio))
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get memory manager service information"""
        stats = self.get_memory_stats()
        
        return {
            "service_name": "MemoryManager",
            "version": "1.0.0",
            "current_memory_mb": stats.current_memory_mb,
            "peak_memory_mb": stats.peak_memory_mb,
            "memory_usage_percent": stats.memory_usage_percent,
            "max_memory_mb": self.config.max_memory_mb,
            "cache_entries": len(self._memory_cache),
            "gc_collections": stats.gc_collections,
            "operations_processed": self._operation_count,
            "monitoring_active": self._monitoring_active
        }
    
    def shutdown(self):
        """Shutdown memory manager and cleanup resources"""
        self._monitoring_active = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)
        
        self._memory_cache.clear()
        self._perform_gc()
        
        self.logger.info("MemoryManager shutdown completed")

# Singleton instance for global access
_memory_manager_instance = None
_memory_manager_lock = threading.Lock()

def get_memory_manager(config: MemoryConfiguration = None) -> MemoryManager:
    """Get singleton MemoryManager instance"""
    global _memory_manager_instance
    
    if _memory_manager_instance is None:
        with _memory_manager_lock:
            if _memory_manager_instance is None:
                _memory_manager_instance = MemoryManager(config)
    
    return _memory_manager_instance