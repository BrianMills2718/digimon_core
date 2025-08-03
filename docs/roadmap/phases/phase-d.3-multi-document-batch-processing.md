# Phase D.3: Multi-Document Batch Processing Enhancements

## Overview

**Phase**: D.3 - Production Optimization  
**Focus**: Multi-Document Batch Processing Enhancements  
**Timeline**: 3-5 days  
**Priority**: High  
**Prerequisites**: D.1 (Structured Output Migration), D.2 (LLM Entity Resolution)

## Mission Statement

Enhance the existing multi-document processing capabilities to support efficient batch processing of large document collections with advanced scheduling, memory management, and error recovery for research workflows.

## Current State Assessment

### Existing Multi-Document Infrastructure ✅
- **MultiDocumentEngine** (`src/processing/multi_document_engine.py`) - Core batch processing engine
- **MultiDocumentTool** (`src/tools/phase_c/multi_document_tool.py`) - MCP tool wrapper
- **Document Dependency Tracker** (`src/processing/document_dependency_tracker.py`) - Dependency management
- **Memory Manager** (`src/processing/memory_manager.py`) - Resource management
- **Intelligent Clusterer** (`src/clustering/intelligent_clusterer.py`) - Document clustering

### Phase C Accomplishments ✅
- Multi-document processing: 15/15 tests passing
- Cross-modal analysis: 12/12 tests passing  
- Document clustering: 11/11 tests passing
- 93.8% overall test success rate

## Enhancement Objectives

### 1. **Advanced Batch Scheduling**
- **Smart Queue Management**: Intelligent document prioritization based on size, dependencies, and processing complexity
- **Resource-Aware Scheduling**: Dynamic worker allocation based on system resources and document characteristics
- **Dependency-Aware Processing**: Automated dependency resolution and parallel execution of independent documents

### 2. **Enhanced Memory Management**
- **Streaming Processing**: Process large documents without loading entire collections into memory
- **Memory Pool Management**: Efficient memory allocation and cleanup for batch operations
- **Garbage Collection Optimization**: Proactive cleanup during long-running batch jobs

### 3. **Robust Error Recovery**
- **Checkpoint System**: Save processing state to resume interrupted batch jobs
- **Retry Logic**: Intelligent retry mechanisms for transient failures
- **Error Isolation**: Prevent single document failures from stopping entire batch

### 4. **Research Workflow Integration**
- **Citation Tracking**: Enhanced provenance tracking for research citations
- **Cross-Document Entity Resolution**: Leverage Phase D.2 LLM entity resolution for better cross-document linking
- **Batch Result Aggregation**: Intelligent aggregation of results across document collections

## Implementation Plan

### Task D.3.1: Advanced Batch Scheduling Engine

**Deliverable**: Enhanced scheduling system with intelligent prioritization

**Implementation Details**:
```python
# src/processing/enhanced_batch_scheduler.py
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import heapq
import asyncio
from concurrent.futures import ThreadPoolExecutor

class DocumentPriority(Enum):
    CRITICAL = 1    # Dependencies blocking other documents
    HIGH = 2        # Large impact documents  
    NORMAL = 3      # Standard processing
    LOW = 4         # Background processing

class ProcessingComplexity(Enum):
    SIMPLE = 1      # Text-only, < 100KB
    MODERATE = 2    # Mixed content, < 1MB
    COMPLEX = 3     # Large documents, > 1MB
    INTENSIVE = 4   # Very large or complex documents

@dataclass
class DocumentJob:
    document_id: str
    file_path: str
    priority: DocumentPriority
    complexity: ProcessingComplexity
    dependencies: List[str] = field(default_factory=list)
    estimated_processing_time: float = 0.0
    memory_requirement: int = 0
    retry_count: int = 0
    max_retries: int = 3
    
    def __lt__(self, other):
        # Priority queue ordering
        return (self.priority.value, self.estimated_processing_time) < \
               (other.priority.value, other.estimated_processing_time)

class EnhancedBatchScheduler:
    """Advanced batch scheduler with intelligent prioritization"""
    
    def __init__(self, max_workers: int = 4, max_memory_mb: int = 2000):
        self.max_workers = max_workers
        self.max_memory_mb = max_memory_mb
        self.job_queue = []  # Priority queue
        self.dependency_graph = {}
        self.completed_jobs = set()
        self.failed_jobs = set()
        self.active_jobs = {}
        self.resource_monitor = ResourceMonitor()
        
    async def add_document_batch(self, documents: List[Dict[str, Any]]) -> str:
        """Add batch of documents for processing"""
        batch_id = self._generate_batch_id()
        
        # Analyze documents and create jobs
        jobs = []
        for doc in documents:
            job = await self._analyze_document_requirements(doc)
            jobs.append(job)
            heapq.heappush(self.job_queue, job)
        
        # Build dependency graph
        self._build_dependency_graph(jobs)
        
        return batch_id
    
    async def process_batch(self, batch_id: str) -> Dict[str, Any]:
        """Process entire batch with intelligent scheduling"""
        results = {}
        
        while self.job_queue or self.active_jobs:
            # Check for completed dependencies
            ready_jobs = self._get_ready_jobs()
            
            # Start new jobs if resources available
            for job in ready_jobs[:self._available_worker_slots()]:
                if self._has_sufficient_resources(job):
                    asyncio.create_task(self._process_job(job))
                    self.active_jobs[job.document_id] = job
            
            # Wait for job completion
            await asyncio.sleep(0.1)
        
        return {
            "batch_id": batch_id,
            "total_documents": len(self.completed_jobs) + len(self.failed_jobs),
            "successful": len(self.completed_jobs),
            "failed": len(self.failed_jobs),
            "results": results
        }
    
    async def _analyze_document_requirements(self, doc: Dict[str, Any]) -> DocumentJob:
        """Analyze document to determine processing requirements"""
        file_path = doc.get("path", "")
        file_size = doc.get("metadata", {}).get("file_size", 0)
        
        # Determine complexity
        if file_size < 100_000:  # < 100KB
            complexity = ProcessingComplexity.SIMPLE
            estimated_time = 5.0
            memory_req = 50_000_000  # 50MB
        elif file_size < 1_000_000:  # < 1MB
            complexity = ProcessingComplexity.MODERATE  
            estimated_time = 15.0
            memory_req = 200_000_000  # 200MB
        elif file_size < 10_000_000:  # < 10MB
            complexity = ProcessingComplexity.COMPLEX
            estimated_time = 60.0
            memory_req = 500_000_000  # 500MB
        else:
            complexity = ProcessingComplexity.INTENSIVE
            estimated_time = 180.0
            memory_req = 1_000_000_000  # 1GB
        
        # Determine priority
        priority = DocumentPriority.NORMAL
        if doc.get("metadata", {}).get("critical", False):
            priority = DocumentPriority.CRITICAL
        elif file_size > 5_000_000:  # Large documents get high priority
            priority = DocumentPriority.HIGH
        
        return DocumentJob(
            document_id=doc["id"],
            file_path=file_path,
            priority=priority,
            complexity=complexity,
            estimated_processing_time=estimated_time,
            memory_requirement=memory_req
        )
```

### Task D.3.2: Streaming Memory Management

**Deliverable**: Memory-efficient processing for large document collections

**Implementation Details**:
```python
# src/processing/streaming_memory_manager.py
import asyncio
import gc
import psutil
from typing import AsyncGenerator, Dict, Any, Optional
from contextlib import asynccontextmanager

class StreamingMemoryManager:
    """Memory-efficient streaming processor for large document batches"""
    
    def __init__(self, memory_limit_mb: int = 1500):
        self.memory_limit_mb = memory_limit_mb
        self.memory_limit_bytes = memory_limit_mb * 1024 * 1024
        self.active_documents = {}
        self.memory_pool = MemoryPool()
        
    async def stream_document_batch(self, 
                                   documents: List[str], 
                                   chunk_size: int = 5) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream process documents in memory-efficient chunks"""
        
        for i in range(0, len(documents), chunk_size):
            chunk = documents[i:i + chunk_size]
            
            # Wait for sufficient memory
            await self._wait_for_memory_availability()
            
            # Process chunk
            async with self._memory_managed_processing(chunk) as processor:
                async for result in processor.process_documents():
                    yield result
            
            # Force garbage collection between chunks
            gc.collect()
    
    @asynccontextmanager
    async def _memory_managed_processing(self, documents: List[str]):
        """Context manager for memory-managed document processing"""
        processor = None
        try:
            # Check memory before starting
            if not self._has_sufficient_memory():
                await self._free_memory()
            
            processor = DocumentProcessor(documents, self.memory_pool)
            yield processor
            
        finally:
            if processor:
                await processor.cleanup()
            
            # Aggressive cleanup
            self._cleanup_memory()
    
    async def _wait_for_memory_availability(self):
        """Wait until sufficient memory is available"""
        max_wait_time = 300  # 5 minutes
        wait_start = time.time()
        
        while not self._has_sufficient_memory():
            if time.time() - wait_start > max_wait_time:
                raise MemoryError("Insufficient memory available after waiting")
            
            await self._free_memory()
            await asyncio.sleep(1)
    
    def _has_sufficient_memory(self) -> bool:
        """Check if sufficient memory is available"""
        process = psutil.Process()
        current_memory = process.memory_info().rss
        available_memory = psutil.virtual_memory().available
        
        return (current_memory < self.memory_limit_bytes and 
                available_memory > self.memory_limit_bytes)
    
    async def _free_memory(self):
        """Free memory by cleaning up old documents"""
        # Remove old documents from memory
        cleanup_count = 0
        for doc_id in list(self.active_documents.keys()):
            del self.active_documents[doc_id]
            cleanup_count += 1
            if cleanup_count >= 5:  # Cleanup in batches
                break
        
        # Force garbage collection
        gc.collect()
        
        # Pool cleanup
        self.memory_pool.cleanup_unused()
```

### Task D.3.3: Checkpoint and Recovery System

**Deliverable**: Robust error recovery with checkpoint system

**Implementation Details**:
```python
# src/processing/checkpoint_recovery_system.py
import json
import pickle
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class ProcessingCheckpoint:
    """Processing checkpoint for batch recovery"""
    batch_id: str
    checkpoint_id: str
    timestamp: str
    completed_documents: List[str]
    failed_documents: List[str]
    pending_documents: List[str]
    processing_state: Dict[str, Any]
    resource_state: Dict[str, Any]
    error_log: List[Dict[str, Any]]

class CheckpointRecoverySystem:
    """System for saving and recovering batch processing state"""
    
    def __init__(self, checkpoint_dir: str = "data/checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.auto_checkpoint_interval = 300  # 5 minutes
        
    async def create_checkpoint(self, 
                               batch_id: str,
                               scheduler: 'EnhancedBatchScheduler') -> str:
        """Create processing checkpoint"""
        checkpoint_id = self._generate_checkpoint_id(batch_id)
        
        checkpoint = ProcessingCheckpoint(
            batch_id=batch_id,
            checkpoint_id=checkpoint_id,
            timestamp=datetime.now().isoformat(),
            completed_documents=list(scheduler.completed_jobs),
            failed_documents=list(scheduler.failed_jobs),
            pending_documents=[job.document_id for job in scheduler.job_queue],
            processing_state=self._capture_processing_state(scheduler),
            resource_state=self._capture_resource_state(),
            error_log=[]  # Add error logging here
        )
        
        # Save checkpoint to disk
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(asdict(checkpoint), f, indent=2)
        
        logger.info(f"Created checkpoint {checkpoint_id} for batch {batch_id}")
        return checkpoint_id
    
    async def recover_from_checkpoint(self, 
                                     checkpoint_id: str) -> Optional['EnhancedBatchScheduler']:
        """Recover batch processing from checkpoint"""
        checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"
        
        if not checkpoint_file.exists():
            logger.error(f"Checkpoint file not found: {checkpoint_id}")
            return None
        
        try:
            with open(checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
            
            checkpoint = ProcessingCheckpoint(**checkpoint_data)
            
            # Recreate scheduler state
            scheduler = self._restore_scheduler_state(checkpoint)
            
            logger.info(f"Successfully recovered from checkpoint {checkpoint_id}")
            return scheduler
            
        except Exception as e:
            logger.error(f"Failed to recover from checkpoint {checkpoint_id}: {e}")
            return None
    
    async def auto_checkpoint_monitor(self, 
                                     batch_id: str, 
                                     scheduler: 'EnhancedBatchScheduler'):
        """Monitor and create automatic checkpoints"""
        last_checkpoint = time.time()
        
        while not scheduler.is_complete():
            current_time = time.time()
            
            if current_time - last_checkpoint > self.auto_checkpoint_interval:
                await self.create_checkpoint(batch_id, scheduler)
                last_checkpoint = current_time
            
            await asyncio.sleep(30)  # Check every 30 seconds
```

### Task D.3.4: Research Workflow Integration

**Deliverable**: Enhanced research-specific features and citation tracking

**Implementation Details**:
```python
# src/processing/research_workflow_integration.py
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import asyncio

@dataclass
class ResearchDocument:
    """Research document with enhanced metadata"""
    document_id: str
    title: str
    authors: List[str]
    publication_date: Optional[str]
    journal: Optional[str]
    doi: Optional[str]
    citations: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    research_domain: Optional[str] = None
    keywords: List[str] = field(default_factory=list)

@dataclass
class CrossDocumentEntityCluster:
    """Entity cluster across multiple documents"""
    cluster_id: str
    canonical_name: str
    entity_type: str
    member_entities: List[Dict[str, Any]]
    confidence_score: float
    source_documents: List[str]
    resolution_method: str  # "llm", "similarity", "manual"

class ResearchWorkflowIntegration:
    """Enhanced research workflow features"""
    
    def __init__(self, llm_entity_resolver=None):
        self.llm_entity_resolver = llm_entity_resolver
        self.citation_tracker = CitationTracker()
        self.cross_document_resolver = CrossDocumentEntityResolver()
        
    async def process_research_batch(self, 
                                   documents: List[ResearchDocument]) -> Dict[str, Any]:
        """Process batch with research-specific enhancements"""
        
        # Phase 1: Standard document processing
        processed_docs = await self._process_documents_standard(documents)
        
        # Phase 2: Cross-document entity resolution using LLM
        entity_clusters = await self._resolve_cross_document_entities(processed_docs)
        
        # Phase 3: Citation network analysis
        citation_network = await self._build_citation_network(documents)
        
        # Phase 4: Research domain clustering
        domain_clusters = await self._cluster_by_research_domain(documents)
        
        # Phase 5: Generate research insights
        insights = await self._generate_research_insights(
            processed_docs, entity_clusters, citation_network, domain_clusters
        )
        
        return {
            "processed_documents": processed_docs,
            "entity_clusters": entity_clusters,
            "citation_network": citation_network,
            "domain_clusters": domain_clusters,
            "research_insights": insights,
            "processing_metadata": {
                "total_documents": len(documents),
                "total_entities": sum(len(doc.get("entities", [])) for doc in processed_docs),
                "total_citations": len(citation_network.get("edges", [])),
                "processing_timestamp": datetime.now().isoformat()
            }
        }
    
    async def _resolve_cross_document_entities(self, 
                                             documents: List[Dict[str, Any]]) -> List[CrossDocumentEntityCluster]:
        """Use LLM-based entity resolution for cross-document linking"""
        
        if not self.llm_entity_resolver:
            logger.warning("LLM entity resolver not available, falling back to similarity-based resolution")
            return await self._similarity_based_resolution(documents)
        
        entity_clusters = []
        
        # Collect all entities across documents
        all_entities = []
        for doc in documents:
            for entity in doc.get("entities", []):
                entity["source_document"] = doc["document_id"]
                all_entities.append(entity)
        
        # Group entities by type for efficient LLM processing
        entities_by_type = defaultdict(list)
        for entity in all_entities:
            entities_by_type[entity["entity_type"]].append(entity)
        
        # Process each entity type
        for entity_type, entities in entities_by_type.items():
            if len(entities) < 2:
                continue  # Skip if only one entity of this type
            
            # Use LLM to resolve entity clusters
            llm_clusters = await self.llm_entity_resolver.resolve_entity_clusters(
                entities, entity_type
            )
            
            # Convert LLM results to our format
            for cluster_data in llm_clusters:
                cluster = CrossDocumentEntityCluster(
                    cluster_id=cluster_data["cluster_id"],
                    canonical_name=cluster_data["canonical_name"],
                    entity_type=entity_type,
                    member_entities=cluster_data["members"],
                    confidence_score=cluster_data["confidence"],
                    source_documents=list(set(e["source_document"] for e in cluster_data["members"])),
                    resolution_method="llm"
                )
                entity_clusters.append(cluster)
        
        return entity_clusters
    
    async def _build_citation_network(self, 
                                    documents: List[ResearchDocument]) -> Dict[str, Any]:
        """Build citation network from research documents"""
        
        nodes = []
        edges = []
        
        # Create nodes for each document
        for doc in documents:
            nodes.append({
                "id": doc.document_id,
                "title": doc.title,
                "authors": doc.authors,
                "publication_date": doc.publication_date,
                "journal": doc.journal,
                "doi": doc.doi
            })
        
        # Create edges for citations
        for doc in documents:
            for cited_doc_id in doc.citations:
                edges.append({
                    "source": doc.document_id,
                    "target": cited_doc_id,
                    "type": "cites",
                    "weight": 1.0
                })
        
        # Calculate network metrics
        network_metrics = {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "average_citations_per_document": len(edges) / len(nodes) if nodes else 0,
            "most_cited_documents": self._find_most_cited(nodes, edges)
        }
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metrics": network_metrics
        }
```

## Success Criteria

Phase D.3 is complete when:

1. **✅ Enhanced Batch Scheduler**: Intelligent document prioritization and resource-aware scheduling implemented
2. **✅ Streaming Memory Management**: Large document collections processable within memory constraints  
3. **✅ Checkpoint Recovery**: Robust error recovery with automatic checkpoint system
4. **✅ Research Integration**: Enhanced citation tracking and cross-document entity resolution
5. **✅ Performance Validation**: Batch processing improvements demonstrated with evidence

## Evidence Requirements

Create `Evidence_Phase_D3_Multi_Document_Batch.md` with:

### 1. Batch Scheduling Performance
- Document prioritization algorithm testing
- Resource utilization measurements  
- Processing time comparisons (before/after)
- Concurrent processing efficiency metrics

### 2. Memory Management Validation
- Large document batch processing (>1GB total)
- Memory usage patterns during streaming
- Garbage collection effectiveness metrics
- Out-of-memory prevention demonstration

### 3. Recovery System Testing
- Checkpoint creation and restoration testing
- Interrupted batch recovery demonstration
- Error isolation and retry logic validation
- Data integrity after recovery verification

### 4. Research Workflow Benefits
- Cross-document entity resolution accuracy improvements
- Citation network analysis results
- Research domain clustering effectiveness
- Processing time improvements for research collections

## Integration Points

### Dependencies
- **Phase D.1**: Structured output migration for reliable LLM processing
- **Phase D.2**: LLM entity resolution for cross-document entity linking
- **Existing Infrastructure**: MultiDocumentEngine, memory management systems

### Provides Foundation For
- **Phase D.4**: Visualization dashboard can display batch processing results
- **Phase D.5**: Research workflow improvements build on enhanced batch processing
- **Phase D.6**: Web deployment benefits from robust batch processing backend

## Implementation Timeline

**Day 1**: Enhanced Batch Scheduler implementation and testing  
**Day 2**: Streaming Memory Management system development  
**Day 3**: Checkpoint Recovery System implementation  
**Day 4**: Research Workflow Integration features  
**Day 5**: Integration testing, performance validation, and evidence collection

---

**Status**: Ready for Implementation  
**Next Phase**: D.4 - Visualization Dashboard  
**Owner**: Development Team  
**Review Date**: Upon completion of implementation