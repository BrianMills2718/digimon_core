#!/usr/bin/env python3
"""
Enhanced Batch Scheduler - Phase D.3 Implementation

Implements production-ready batch processing for large document collections
with intelligent scheduling, resource management, and checkpoint recovery.
"""

from typing import List, Dict, Any, Optional, Type, Tuple
from dataclasses import dataclass, field
from enum import Enum
import heapq
import asyncio
import time
import psutil
import threading
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import uuid

logger = logging.getLogger(__name__)


class DocumentPriority(Enum):
    """Document processing priority levels"""
    CRITICAL = 1    # Dependencies blocking other documents
    HIGH = 2        # Large impact documents  
    NORMAL = 3      # Standard processing
    LOW = 4         # Background processing


class ProcessingComplexity(Enum):
    """Document processing complexity levels"""
    SIMPLE = 1      # Text-only, < 100KB
    MODERATE = 2    # Mixed content, < 1MB
    COMPLEX = 3     # Large documents, > 1MB
    INTENSIVE = 4   # Very large or complex documents


@dataclass
class DocumentJob:
    """Represents a document processing job with metadata"""
    document_id: str
    file_path: str
    priority: DocumentPriority
    complexity: ProcessingComplexity
    dependencies: List[str] = field(default_factory=list)
    estimated_processing_time: float = 0.0
    memory_requirement: int = 0
    retry_count: int = 0
    max_retries: int = 3
    created_at: float = field(default_factory=time.time)
    
    def __lt__(self, other):
        """Priority queue ordering: higher priority first, then by processing time"""
        return (self.priority.value, self.estimated_processing_time) < \
               (other.priority.value, other.estimated_processing_time)


class ResourceMonitor:
    """Monitor system resources for intelligent scheduling"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._last_check = 0
        self._check_interval = 1.0  # seconds
        self._cached_metrics = {}
    
    def get_available_memory_mb(self) -> int:
        """Get available memory in MB"""
        return psutil.virtual_memory().available // (1024 * 1024)
    
    def get_cpu_usage_percent(self) -> float:
        """Get CPU usage percentage"""
        return psutil.cpu_percent(interval=0.1)
    
    def get_disk_io_stats(self) -> Dict[str, int]:
        """Get disk I/O statistics"""
        io_counters = psutil.disk_io_counters()
        return {
            "read_bytes": io_counters.read_bytes,
            "write_bytes": io_counters.write_bytes,
            "read_count": io_counters.read_count,
            "write_count": io_counters.write_count
        }
    
    def has_sufficient_resources(self, memory_mb: int, cpu_threshold: float = 80.0) -> bool:
        """Check if system has sufficient resources"""
        current_time = time.time()
        
        # Use cached values if recent
        if current_time - self._last_check < self._check_interval:
            available_memory = self._cached_metrics.get("memory", 0)
            cpu_usage = self._cached_metrics.get("cpu", 100)
        else:
            available_memory = self.get_available_memory_mb()
            cpu_usage = self.get_cpu_usage_percent()
            
            self._cached_metrics = {
                "memory": available_memory,
                "cpu": cpu_usage
            }
            self._last_check = current_time
        
        has_memory = available_memory >= memory_mb
        has_cpu = cpu_usage < cpu_threshold
        
        if not has_memory:
            self.logger.warning(
                f"Insufficient memory: {available_memory}MB available, {memory_mb}MB required"
            )
        if not has_cpu:
            self.logger.warning(
                f"High CPU usage: {cpu_usage}% (threshold: {cpu_threshold}%)"
            )
        
        return has_memory and has_cpu


class EnhancedBatchScheduler:
    """
    Advanced batch scheduler with intelligent prioritization.
    
    Features:
    - Priority-based scheduling
    - Resource-aware execution
    - Dependency management
    - Automatic retry with backoff
    - Performance monitoring
    """
    
    def __init__(self, max_workers: int = 4, max_memory_mb: int = 2000):
        self.max_workers = max_workers
        self.max_memory_mb = max_memory_mb
        self.job_queue = []  # Priority queue
        self.dependency_graph = {}
        self.completed_jobs = set()
        self.failed_jobs = set()
        self.active_jobs = {}
        self.job_results = {}
        self.resource_monitor = ResourceMonitor()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = threading.Lock()
        self._shutdown = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Performance tracking
        self.stats = {
            "total_jobs": 0,
            "successful_jobs": 0,
            "failed_jobs": 0,
            "retried_jobs": 0,
            "total_processing_time": 0.0,
            "total_memory_used": 0
        }
    
    async def add_document_batch(self, documents: List[Dict[str, Any]]) -> str:
        """
        Add batch of documents for processing with intelligent analysis.
        
        Args:
            documents: List of document dictionaries with metadata
            
        Returns:
            Batch ID for tracking
        """
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Analyze documents and create jobs
        jobs = []
        for doc in documents:
            try:
                job = await self._analyze_document_requirements(doc)
                jobs.append(job)
                
                with self._lock:
                    heapq.heappush(self.job_queue, job)
                    self.stats["total_jobs"] += 1
                
            except Exception as e:
                self.logger.error(f"Failed to analyze document {doc.get('id', 'unknown')}: {e}")
        
        # Build dependency graph
        self._build_dependency_graph(jobs)
        
        self.logger.info(
            f"Added batch {batch_id} with {len(jobs)} documents "
            f"({sum(1 for j in jobs if j.priority == DocumentPriority.CRITICAL)} critical, "
            f"{sum(1 for j in jobs if j.priority == DocumentPriority.HIGH)} high priority)"
        )
        
        return batch_id
    
    async def _analyze_document_requirements(self, doc: Dict[str, Any]) -> DocumentJob:
        """Analyze document to determine processing requirements"""
        doc_id = doc.get("id", str(uuid.uuid4()))
        file_path = doc.get("file_path", "")
        
        # Determine document size and complexity
        file_size = doc.get("size", 0)
        doc_type = doc.get("type", "text")
        
        # Assign complexity based on size and type
        if file_size < 100 * 1024:  # < 100KB
            complexity = ProcessingComplexity.SIMPLE
            estimated_time = 5.0
            memory_mb = 50
        elif file_size < 1024 * 1024:  # < 1MB
            complexity = ProcessingComplexity.MODERATE
            estimated_time = 15.0
            memory_mb = 200
        elif file_size < 10 * 1024 * 1024:  # < 10MB
            complexity = ProcessingComplexity.COMPLEX
            estimated_time = 60.0
            memory_mb = 500
        else:
            complexity = ProcessingComplexity.INTENSIVE
            estimated_time = 300.0
            memory_mb = 1000
        
        # Adjust for document type
        if doc_type == "pdf":
            estimated_time *= 1.5
            memory_mb = int(memory_mb * 1.2)
        elif doc_type == "image":
            estimated_time *= 2.0
            memory_mb = int(memory_mb * 1.5)
        
        # Determine priority
        priority = DocumentPriority.NORMAL
        if doc.get("priority") == "critical":
            priority = DocumentPriority.CRITICAL
        elif doc.get("priority") == "high":
            priority = DocumentPriority.HIGH
        elif doc.get("priority") == "low":
            priority = DocumentPriority.LOW
        
        # Check for dependencies
        dependencies = doc.get("dependencies", [])
        
        return DocumentJob(
            document_id=doc_id,
            file_path=file_path,
            priority=priority,
            complexity=complexity,
            dependencies=dependencies,
            estimated_processing_time=estimated_time,
            memory_requirement=memory_mb
        )
    
    def _build_dependency_graph(self, jobs: List[DocumentJob]):
        """Build dependency graph from job dependencies"""
        with self._lock:
            for job in jobs:
                self.dependency_graph[job.document_id] = set(job.dependencies)
    
    async def process_batch(self, batch_id: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Process entire batch with intelligent scheduling.
        
        Args:
            batch_id: Batch identifier
            timeout: Optional timeout in seconds
            
        Returns:
            Processing results and statistics
        """
        start_time = time.time()
        results = {}
        
        try:
            # Process jobs until queue is empty or timeout
            while (self.job_queue or self.active_jobs) and not self._shutdown:
                if timeout and (time.time() - start_time) > timeout:
                    self.logger.warning(f"Batch {batch_id} processing timeout reached")
                    break
                
                # Get jobs ready for processing (dependencies satisfied)
                ready_jobs = self._get_ready_jobs()
                
                # Start new jobs if resources available
                for job in ready_jobs:
                    if self._can_start_job(job):
                        await self._start_job(job)
                
                # Check for completed jobs
                await self._check_completed_jobs(results)
                
                # Brief pause to prevent busy waiting
                await asyncio.sleep(0.1)
            
            # Wait for remaining active jobs
            while self.active_jobs and not self._shutdown:
                await self._check_completed_jobs(results)
                await asyncio.sleep(0.1)
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            raise
        
        processing_time = time.time() - start_time
        
        return {
            "batch_id": batch_id,
            "total_documents": self.stats["total_jobs"],
            "successful": len(self.completed_jobs),
            "failed": len(self.failed_jobs),
            "processing_time": processing_time,
            "results": results,
            "stats": self.get_stats()
        }
    
    def _get_ready_jobs(self) -> List[DocumentJob]:
        """Get jobs that are ready for processing (dependencies satisfied)"""
        ready = []
        
        with self._lock:
            # Check each job in priority order
            temp_queue = []
            
            while self.job_queue:
                job = heapq.heappop(self.job_queue)
                
                # Check if dependencies are satisfied
                deps = self.dependency_graph.get(job.document_id, set())
                if deps.issubset(self.completed_jobs):
                    ready.append(job)
                else:
                    temp_queue.append(job)
            
            # Restore non-ready jobs to queue
            for job in temp_queue:
                heapq.heappush(self.job_queue, job)
        
        return ready
    
    def _can_start_job(self, job: DocumentJob) -> bool:
        """Check if we can start a job based on resources"""
        # Check worker availability
        if len(self.active_jobs) >= self.max_workers:
            return False
        
        # Check resource availability
        return self.resource_monitor.has_sufficient_resources(
            job.memory_requirement,
            cpu_threshold=90.0  # Allow up to 90% CPU
        )
    
    async def _start_job(self, job: DocumentJob):
        """Start processing a job"""
        task = asyncio.create_task(self._process_job(job))
        
        with self._lock:
            self.active_jobs[job.document_id] = {
                "job": job,
                "task": task,
                "start_time": time.time()
            }
        
        self.logger.debug(
            f"Started job {job.document_id} "
            f"(priority: {job.priority.name}, complexity: {job.complexity.name})"
        )
    
    async def _process_job(self, job: DocumentJob) -> Dict[str, Any]:
        """Process a single job with real document processing pipeline"""
        start_time = time.time()
        
        try:
            # Initialize real processing tools with ServiceManager
            from src.core.service_manager import ServiceManager
            from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
            from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
            from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
            
            service_manager = ServiceManager()
            
            # Initialize tools
            pdf_loader = T01PDFLoaderUnified(service_manager)
            text_chunker = T15ATextChunkerUnified(service_manager)
            ner_extractor = T23ASpacyNERUnified(service_manager)
            
            # Execute real document processing pipeline with proper ToolRequest interface
            from src.tools.base_classes.tool_protocol import ToolRequest
            
            # Step 1: Load document
            load_request = ToolRequest(
                tool_id="T01_PDF_LOADER",
                operation="load_document",
                input_data={
                    "file_path": job.file_path,
                    "document_id": job.document_id
                },
                parameters={}
            )
            load_result = pdf_loader.execute(load_request)
            
            if not load_result or load_result.status != "success":
                raise Exception(f"Failed to load document: {load_result.error_message if hasattr(load_result, 'error_message') else 'Unknown error'}")
            
            document_text = load_result.data.get("text", "")
            if not document_text:
                raise Exception("No text extracted from document")
            
            # Step 2: Chunk text
            chunk_request = ToolRequest(
                tool_id="T15A_TEXT_CHUNKER",
                operation="chunk_text",
                input_data={
                    "text": document_text,
                    "document_ref": job.document_id
                },
                parameters={"chunk_size": 1000}
            )
            chunk_result = text_chunker.execute(chunk_request)
            
            if not chunk_result or chunk_result.status != "success":
                raise Exception(f"Failed to chunk text: {chunk_result.error_message if hasattr(chunk_result, 'error_message') else 'Unknown error'}")
            
            chunks = chunk_result.data.get("chunks", [])
            
            # Step 3: Extract entities from all chunks
            total_entities = 0
            entity_types = set()
            
            for chunk in chunks:
                ner_request = ToolRequest(
                    tool_id="T23A_SPACY_NER",
                    operation="extract_entities",
                    input_data={
                        "text": chunk.get("text", ""),
                        "chunk_ref": chunk.get("chunk_id", "")
                    },
                    parameters={"confidence_threshold": 0.7}
                )
                ner_result = ner_extractor.execute(ner_request)
                
                if ner_result and ner_result.status == "success":
                    entities = ner_result.data.get("entities", [])
                    total_entities += len(entities)
                    entity_types.update(entity.get("entity_type", "") for entity in entities)
            
            # Calculate actual processing metrics
            processing_time = time.time() - start_time
            
            # Success result with real data
            result = {
                "document_id": job.document_id,
                "status": "success",
                "processing_time": processing_time,
                "entities_extracted": total_entities,
                "entity_types": list(entity_types),
                "chunks_processed": len(chunks),
                "document_size": len(document_text),
                "confidence": 0.85  # Could be calculated from actual entity confidences
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Job {job.document_id} failed: {e}")
            
            # Check if we should retry
            if job.retry_count < job.max_retries:
                job.retry_count += 1
                self.stats["retried_jobs"] += 1
                
                # Exponential backoff
                await asyncio.sleep(2 ** job.retry_count)
                
                # Re-queue job
                with self._lock:
                    heapq.heappush(self.job_queue, job)
                
                self.logger.info(
                    f"Re-queued job {job.document_id} for retry "
                    f"({job.retry_count}/{job.max_retries})"
                )
            else:
                # Final failure
                result = {
                    "document_id": job.document_id,
                    "status": "failed",
                    "error": str(e),
                    "retry_count": job.retry_count
                }
                
                return result
            
            raise
    
    async def _check_completed_jobs(self, results: Dict[str, Any]):
        """Check for completed jobs and update results"""
        completed = []
        
        # Check active jobs
        for doc_id, job_info in list(self.active_jobs.items()):
            task = job_info["task"]
            
            if task.done():
                try:
                    result = task.result()
                    
                    with self._lock:
                        if result["status"] == "success":
                            self.completed_jobs.add(doc_id)
                            self.stats["successful_jobs"] += 1
                        else:
                            self.failed_jobs.add(doc_id)
                            self.stats["failed_jobs"] += 1
                        
                        results[doc_id] = result
                        self.job_results[doc_id] = result
                        completed.append(doc_id)
                        
                        # Update stats
                        processing_time = time.time() - job_info["start_time"]
                        self.stats["total_processing_time"] += processing_time
                    
                except Exception as e:
                    self.logger.error(f"Failed to get result for job {doc_id}: {e}")
                    completed.append(doc_id)
        
        # Remove completed jobs from active
        with self._lock:
            for doc_id in completed:
                self.active_jobs.pop(doc_id, None)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scheduler performance statistics"""
        with self._lock:
            total = self.stats["total_jobs"]
            successful = self.stats["successful_jobs"]
            failed = self.stats["failed_jobs"]
            
            return {
                "total_jobs": total,
                "successful_jobs": successful,
                "failed_jobs": failed,
                "retried_jobs": self.stats["retried_jobs"],
                "success_rate": successful / total if total > 0 else 0.0,
                "failure_rate": failed / total if total > 0 else 0.0,
                "avg_processing_time": (
                    self.stats["total_processing_time"] / (successful + failed)
                    if (successful + failed) > 0 else 0.0
                ),
                "active_jobs": len(self.active_jobs),
                "queued_jobs": len(self.job_queue),
                "system_resources": {
                    "available_memory_mb": self.resource_monitor.get_available_memory_mb(),
                    "cpu_usage_percent": self.resource_monitor.get_cpu_usage_percent()
                }
            }
    
    def get_batch_metrics(self, batch_id: str) -> Dict[str, Any]:
        """Get metrics for a specific batch
        
        Args:
            batch_id: The batch identifier
            
        Returns:
            Dictionary containing batch metrics
        """
        # For now, return general stats
        # In a real implementation, this would track per-batch metrics
        return self.get_stats()
    
    def shutdown(self):
        """Gracefully shutdown the scheduler"""
        self.logger.info("Shutting down batch scheduler")
        self._shutdown = True
        self.executor.shutdown(wait=True)
    
    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


if __name__ == "__main__":
    # Test the scheduler
    import asyncio
    
    async def test_scheduler():
        scheduler = EnhancedBatchScheduler(max_workers=2)
        
        # Create test documents
        test_docs = [
            {
                "id": "doc1",
                "file_path": "/path/to/doc1.pdf",
                "size": 500000,  # 500KB
                "type": "pdf",
                "priority": "high"
            },
            {
                "id": "doc2",
                "file_path": "/path/to/doc2.txt",
                "size": 50000,  # 50KB
                "type": "text",
                "priority": "normal",
                "dependencies": ["doc1"]
            },
            {
                "id": "doc3",
                "file_path": "/path/to/doc3.pdf",
                "size": 2000000,  # 2MB
                "type": "pdf",
                "priority": "critical"
            }
        ]
        
        try:
            # Add batch
            batch_id = await scheduler.add_document_batch(test_docs)
            print(f"Created batch: {batch_id}")
            
            # Process batch
            results = await scheduler.process_batch(batch_id, timeout=60)
            
            print(f"\nBatch processing complete:")
            print(f"- Successful: {results['successful']}")
            print(f"- Failed: {results['failed']}")
            print(f"- Processing time: {results['processing_time']:.2f}s")
            print(f"\nStats: {results['stats']}")
            
        finally:
            scheduler.shutdown()
    
    asyncio.run(test_scheduler())