"""
Resource Manager - Optimize spaCy Model Sharing

Addresses PRIORITY ISSUE 3.1: Implement resource manager to optimize spaCy model sharing.
This fixes the spaCy model loading bottleneck identified in stress tests.

Key Optimizations:
- Shared spaCy model instances across tools
- Proper lifecycle management
- Memory-efficient model loading
- Thread-safe access patterns

This addresses the Gemini AI finding: "Resource sharing bottlenecks and execution monitoring gaps"
"""

import threading
import logging
import time
import weakref
from typing import Dict, Any, Optional, Set, List
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import psutil

# Optional imports with fallbacks
try:
    import spacy
    from spacy.lang.en import English
    SPACY_AVAILABLE = True
except ImportError:
    spacy = None
    English = None
    SPACY_AVAILABLE = False

from .memory_manager import MemoryManager, MemoryConfiguration

logger = logging.getLogger(__name__)

@dataclass
class ModelStats:
    """Statistics for a shared model"""
    model_name: str
    load_time: float
    memory_usage_mb: float
    reference_count: int
    last_accessed: datetime
    total_accesses: int
    created_at: datetime

@dataclass
class ResourceConfiguration:
    """Configuration for resource management"""
    max_models_cached: int = 3
    model_timeout_minutes: int = 30
    memory_threshold_mb: int = 500
    enable_model_sharing: bool = True
    spacy_model_name: str = "en_core_web_sm"
    preload_models: bool = True

class SharedSpacyModel:
    """Thread-safe wrapper for shared spaCy models"""
    
    def __init__(self, model_name: str, nlp_instance):
        self.model_name = model_name
        self.nlp = nlp_instance
        self._lock = threading.RLock()
        self._reference_count = 0
        self._created_at = datetime.now()
        self._last_accessed = datetime.now()
        self._total_accesses = 0
        self._memory_usage = self._calculate_memory_usage()
        
        logger.info(f"Created shared spaCy model: {model_name} ({self._memory_usage:.1f}MB)")
    
    def _calculate_memory_usage(self) -> float:
        """Calculate approximate memory usage of the model"""
        try:
            # Rough estimate based on model size
            if hasattr(self.nlp, 'meta'):
                # Use model metadata if available
                vocab_size = len(self.nlp.vocab)
                # Rough calculation: vocab + vectors + components
                return (vocab_size * 0.001) + 50  # Base overhead
            else:
                return 100  # Default estimate
        except Exception:
            return 100  # Fallback estimate
    
    @contextmanager
    def get_model(self):
        """Get model instance with reference counting"""
        with self._lock:
            self._reference_count += 1
            self._last_accessed = datetime.now()
            self._total_accesses += 1
            
        try:
            yield self.nlp
        finally:
            with self._lock:
                self._reference_count -= 1
    
    @property
    def stats(self) -> ModelStats:
        """Get model statistics"""
        with self._lock:
            return ModelStats(
                model_name=self.model_name,
                load_time=0.0,  # Historical load time not tracked
                memory_usage_mb=self._memory_usage,
                reference_count=self._reference_count,
                last_accessed=self._last_accessed,
                total_accesses=self._total_accesses,
                created_at=self._created_at
            )
    
    @property
    def in_use(self) -> bool:
        """Check if model is currently in use"""
        with self._lock:
            return self._reference_count > 0
    
    @property
    def idle_time(self) -> timedelta:
        """Get idle time since last access"""
        with self._lock:
            return datetime.now() - self._last_accessed

class ResourceManager:
    """
    Resource manager for optimizing spaCy model sharing and other resource bottlenecks.
    
    This addresses the performance bottleneck identified in stress tests where spaCy models
    were loaded separately for each tool execution, causing memory and initialization overhead.
    """
    
    def __init__(self, config: ResourceConfiguration = None):
        self.config = config or ResourceConfiguration()
        self.memory_manager = MemoryManager()
        
        # Thread-safe storage for shared resources
        self._models: Dict[str, SharedSpacyModel] = {}
        self._models_lock = threading.RLock()
        
        # Resource monitoring
        self._resource_stats = {}
        self._cleanup_thread = None
        self._cleanup_active = False
        
        # Track tool instances using resources
        self._tool_references: Dict[str, Set[weakref.ref]] = {}
        
        logger.info(f"ResourceManager initialized with {self.config.max_models_cached} model cache slots")
        
        # Start background cleanup if enabled
        if self.config.model_timeout_minutes > 0:
            self._start_cleanup_thread()
        
        # Preload models if enabled
        if self.config.preload_models and SPACY_AVAILABLE:
            self._preload_default_models()
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread for unused models"""
        if not self._cleanup_active:
            self._cleanup_active = True
            self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
            self._cleanup_thread.start()
            logger.info("Resource cleanup thread started")
    
    def _cleanup_worker(self):
        """Background worker to cleanup unused models"""
        while self._cleanup_active:
            try:
                self._cleanup_unused_models()
                
                # Sleep for cleanup interval
                time.sleep(min(self.config.model_timeout_minutes * 60 // 4, 300))  # Max 5 minutes
                
            except Exception as e:
                logger.error(f"Error in resource cleanup worker: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _preload_default_models(self):
        """Preload commonly used models"""
        try:
            default_models = [self.config.spacy_model_name]
            
            for model_name in default_models:
                logger.info(f"Preloading spaCy model: {model_name}")
                self.get_spacy_model(model_name)
                
        except Exception as e:
            logger.warning(f"Failed to preload models: {e}")
    
    def get_spacy_model(self, model_name: str = None) -> Optional['SharedSpacyModel']:
        """
        Get a shared spaCy model instance with optimized loading and sharing.
        
        Args:
            model_name: Name of the spaCy model to load (defaults to configured model)
            
        Returns:
            SharedSpacyModel wrapper or None if spaCy not available
        """
        if not SPACY_AVAILABLE:
            logger.error("spaCy not available. Install with: pip install spacy && python -m spacy download en_core_web_sm")
            return None
        
        model_name = model_name or self.config.spacy_model_name
        
        with self._models_lock:
            # Return existing model if available
            if model_name in self._models:
                model = self._models[model_name]
                logger.debug(f"Reusing cached spaCy model: {model_name}")
                return model
            
            # Check memory before loading new model
            memory_stats = self.memory_manager.get_memory_stats()
            if memory_stats.current_memory_mb > self.config.memory_threshold_mb:
                logger.warning(f"High memory usage ({memory_stats.current_memory_mb:.1f}MB), cleaning up before loading model")
                self._cleanup_unused_models()
            
            # Check cache limit
            if len(self._models) >= self.config.max_models_cached:
                logger.info(f"Model cache full ({len(self._models)}/{self.config.max_models_cached}), cleaning up least used models")
                self._evict_least_used_model()
            
            # Load new model
            try:
                logger.info(f"Loading spaCy model: {model_name}")
                start_time = time.time()
                
                nlp = spacy.load(model_name)
                load_time = time.time() - start_time
                
                # Create shared model wrapper
                shared_model = SharedSpacyModel(model_name, nlp)
                self._models[model_name] = shared_model
                
                logger.info(f"Successfully loaded spaCy model {model_name} in {load_time:.2f}s")
                return shared_model
                
            except OSError as e:
                logger.error(f"Failed to load spaCy model {model_name}: {e}")
                logger.error(f"Install with: python -m spacy download {model_name}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error loading spaCy model {model_name}: {e}")
                return None
    
    @contextmanager
    def get_spacy_nlp(self, model_name: str = None):
        """
        Context manager to get spaCy nlp instance with proper resource management.
        
        Usage:
            with resource_manager.get_spacy_nlp() as nlp:
                if nlp:
                    doc = nlp("Some text to process")
        """
        shared_model = self.get_spacy_model(model_name)
        if shared_model:
            with shared_model.get_model() as nlp:
                yield nlp
        else:
            yield None
    
    def _cleanup_unused_models(self):
        """Remove unused models that have exceeded timeout"""
        if not self.config.model_timeout_minutes:
            return
        
        timeout = timedelta(minutes=self.config.model_timeout_minutes)
        models_to_remove = []
        
        with self._models_lock:
            for model_name, model in self._models.items():
                if not model.in_use and model.idle_time > timeout:
                    models_to_remove.append(model_name)
            
            for model_name in models_to_remove:
                logger.info(f"Removing unused spaCy model: {model_name} (idle for {self._models[model_name].idle_time})")
                del self._models[model_name]
        
        if models_to_remove:
            # Force garbage collection after removing models
            self.memory_manager._perform_gc()
    
    def _evict_least_used_model(self):
        """Evict the least recently used model to make space"""
        if not self._models:
            return
        
        with self._models_lock:
            # Find model that's not in use with oldest last_accessed time
            unused_models = [
                (name, model) for name, model in self._models.items() 
                if not model.in_use
            ]
            
            if unused_models:
                # Sort by last accessed time (oldest first)
                unused_models.sort(key=lambda x: x[1].stats.last_accessed)
                model_name_to_evict = unused_models[0][0]
                
                logger.info(f"Evicting least used spaCy model: {model_name_to_evict}")
                del self._models[model_name_to_evict]
                
                # Force garbage collection
                self.memory_manager._perform_gc()
            else:
                logger.warning("All cached models are in use, cannot evict")
    
    def register_tool_reference(self, tool_id: str, tool_instance):
        """Register a tool instance that may use shared resources"""
        if tool_id not in self._tool_references:
            self._tool_references[tool_id] = set()
        
        # Use weak reference to avoid preventing garbage collection
        self._tool_references[tool_id].add(weakref.ref(tool_instance))
        
        # Clean up dead references
        self._tool_references[tool_id] = {
            ref for ref in self._tool_references[tool_id] 
            if ref() is not None
        }
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """Get comprehensive resource usage statistics"""
        model_stats = {}
        total_memory = 0
        
        with self._models_lock:
            for model_name, model in self._models.items():
                stats = model.stats
                model_stats[model_name] = {
                    "memory_usage_mb": stats.memory_usage_mb,
                    "reference_count": stats.reference_count,
                    "total_accesses": stats.total_accesses,
                    "last_accessed": stats.last_accessed.isoformat(),
                    "idle_time_minutes": stats.last_accessed and (datetime.now() - stats.last_accessed).total_seconds() / 60,
                    "in_use": model.in_use
                }
                total_memory += stats.memory_usage_mb
        
        memory_stats = self.memory_manager.get_memory_stats()
        
        return {
            "resource_manager": {
                "models_cached": len(self._models),
                "max_models_cached": self.config.max_models_cached,
                "total_model_memory_mb": total_memory,
                "cleanup_active": self._cleanup_active,
                "spacy_available": SPACY_AVAILABLE
            },
            "model_stats": model_stats,
            "memory_stats": {
                "current_memory_mb": memory_stats.current_memory_mb,
                "memory_usage_percent": memory_stats.memory_usage_percent,
                "peak_memory_mb": memory_stats.peak_memory_mb
            },
            "tool_references": {
                tool_id: len(refs) for tool_id, refs in self._tool_references.items()
            }
        }
    
    def optimize_for_processing(self) -> Dict[str, Any]:
        """Optimize resources for intensive processing workload"""
        logger.info("Optimizing resources for processing workload")
        
        # Get baseline stats
        initial_stats = self.get_resource_stats()
        
        # Optimize memory
        memory_optimization = self.memory_manager.optimize_for_large_operation()
        
        # Preload commonly used models if not already loaded
        if SPACY_AVAILABLE and self.config.preload_models:
            self.get_spacy_model(self.config.spacy_model_name)
        
        # Clean up unused models
        self._cleanup_unused_models()
        
        final_stats = self.get_resource_stats()
        
        optimization_result = {
            "memory_optimization": memory_optimization,
            "models_before": initial_stats["resource_manager"]["models_cached"],
            "models_after": final_stats["resource_manager"]["models_cached"],
            "memory_freed_mb": (
                initial_stats["memory_stats"]["current_memory_mb"] - 
                final_stats["memory_stats"]["current_memory_mb"]
            ),
            "spacy_models_ready": list(self._models.keys()),
            "optimization_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Resource optimization completed: {optimization_result['memory_freed_mb']:.1f}MB freed")
        
        return optimization_result
    
    def force_cleanup(self):
        """Force cleanup of all unused resources"""
        logger.info("Forcing cleanup of all unused resources")
        
        with self._models_lock:
            models_to_remove = [
                name for name, model in self._models.items() 
                if not model.in_use
            ]
            
            for model_name in models_to_remove:
                logger.info(f"Force removing model: {model_name}")
                del self._models[model_name]
        
        # Force memory cleanup
        self.memory_manager._perform_cleanup()
        
        logger.info(f"Force cleanup completed, {len(models_to_remove)} models removed")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on resource management"""
        health_status = {
            "healthy": True,
            "issues": [],
            "checks": {}
        }
        
        # Check spaCy availability
        health_status["checks"]["spacy_available"] = SPACY_AVAILABLE
        if not SPACY_AVAILABLE:
            health_status["healthy"] = False
            health_status["issues"].append("spaCy not available")
        
        # Check memory usage
        memory_stats = self.memory_manager.get_memory_stats()
        health_status["checks"]["memory_usage_ok"] = memory_stats.memory_usage_percent < 90
        if memory_stats.memory_usage_percent >= 90:
            health_status["healthy"] = False
            health_status["issues"].append(f"High memory usage: {memory_stats.memory_usage_percent:.1f}%")
        
        # Check model cache status
        with self._models_lock:
            health_status["checks"]["models_cached"] = len(self._models)
            health_status["checks"]["cache_utilization"] = len(self._models) / self.config.max_models_cached
            
            # Check for models in use
            models_in_use = sum(1 for model in self._models.values() if model.in_use)
            health_status["checks"]["models_in_use"] = models_in_use
        
        # Check cleanup thread
        health_status["checks"]["cleanup_thread_active"] = self._cleanup_active
        if self.config.model_timeout_minutes > 0 and not self._cleanup_active:
            health_status["issues"].append("Cleanup thread not active")
        
        return health_status
    
    def shutdown(self):
        """Shutdown resource manager and cleanup all resources"""
        logger.info("Shutting down ResourceManager")
        
        # Stop cleanup thread
        self._cleanup_active = False
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)
        
        # Clear all models
        with self._models_lock:
            model_count = len(self._models)
            self._models.clear()
            logger.info(f"Cleared {model_count} cached models")
        
        # Clear tool references
        self._tool_references.clear()
        
        # Shutdown memory manager
        self.memory_manager.shutdown()
        
        logger.info("ResourceManager shutdown completed")

# Singleton instance for global access
_resource_manager_instance: Optional[ResourceManager] = None
_resource_manager_lock = threading.Lock()

def get_resource_manager(config: ResourceConfiguration = None) -> ResourceManager:
    """Get singleton ResourceManager instance"""
    global _resource_manager_instance
    
    if _resource_manager_instance is None:
        with _resource_manager_lock:
            if _resource_manager_instance is None:
                _resource_manager_instance = ResourceManager(config)
    
    return _resource_manager_instance

def shutdown_resource_manager():
    """Shutdown the global resource manager instance"""
    global _resource_manager_instance
    
    if _resource_manager_instance:
        with _resource_manager_lock:
            if _resource_manager_instance:
                _resource_manager_instance.shutdown()
                _resource_manager_instance = None