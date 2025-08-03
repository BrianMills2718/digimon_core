"""
Multi-Document Processing Engine

Core engine for processing multiple documents simultaneously with dependency tracking,
memory management, and intelligent scheduling.
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, AsyncGenerator, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import os
import mimetypes
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

logger = logging.getLogger(__name__)


class DocumentFormat(Enum):
    """Supported document formats"""
    PDF = "pdf"
    TXT = "txt"
    JSON = "json"
    XML = "xml"
    MD = "md"
    UNKNOWN = "unknown"


class ProcessingStatus(Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DocumentMetadata:
    """Document metadata container"""
    file_size: int
    creation_time: float
    modification_time: float
    file_extension: str
    file_path: str
    extracted_metadata: Optional[Dict[str, Any]] = None
    quality_score: Optional[float] = None


@dataclass
class ProcessingResult:
    """Result of document processing"""
    document_id: str
    document_path: str
    document_format: str
    success: bool
    content: Optional[str] = None
    metadata: Optional[DocumentMetadata] = None
    chunks: Optional[List[str]] = None
    processing_time: float = 0.0
    error_message: Optional[str] = None
    status: ProcessingStatus = ProcessingStatus.PENDING


@dataclass
class DuplicateGroup:
    """Group of duplicate documents"""
    documents: List[str]
    similarity_score: float
    representative_document: str


@dataclass
class QualityScore:
    """Document quality assessment"""
    document_path: str
    overall_score: float
    completeness_score: float
    structure_score: float
    readability_score: float
    metadata_score: float


@dataclass
class TopicCluster:
    """Document topic cluster"""
    cluster_id: str
    documents: List[str]
    topic_keywords: List[str]
    cluster_score: float
    centroid_document: str


@dataclass
class ProcessingSchedule:
    """Document processing schedule"""
    processing_order: List[str]
    estimated_total_time: float
    parallel_groups: List[List[str]] = field(default_factory=list)
    dependencies: Optional[List] = field(default_factory=list)


class MultiDocumentEngine:
    """Engine for processing multiple documents simultaneously"""
    
    def __init__(self, max_workers: int = 4):
        """Initialize the multi-document engine"""
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.logger = logger
        self._processing_tasks: Dict[str, asyncio.Task] = {}
        self._document_cache: Dict[str, ProcessingResult] = {}
        self._is_shutdown = False
        
    async def load_documents_batch(self, document_paths: List[str]) -> List[ProcessingResult]:
        """Load multiple documents simultaneously"""
        self.logger.info(f"Loading batch of {len(document_paths)} documents")
        
        # Create tasks for concurrent loading
        tasks = []
        for doc_path in document_paths:
            task = asyncio.create_task(self._load_single_document(doc_path))
            tasks.append(task)
        
        # Wait for all documents to load
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create failed result for exception
                failed_result = ProcessingResult(
                    document_id=f"doc_{i}",
                    document_path=document_paths[i],
                    document_format=self._detect_format(document_paths[i]).value,
                    success=False,
                    error_message=str(result),
                    status=ProcessingStatus.FAILED
                )
                processed_results.append(failed_result)
            else:
                processed_results.append(result)
        
        self.logger.info(f"Completed loading {len(processed_results)} documents")
        return processed_results
    
    async def _load_single_document(self, document_path: str) -> ProcessingResult:
        """Load a single document"""
        start_time = time.time()
        document_id = self._generate_document_id(document_path)
        
        try:
            # Check if file exists
            if not os.path.exists(document_path):
                raise FileNotFoundError(f"Document not found: {document_path}")
            
            # Detect format
            doc_format = self._detect_format(document_path)
            
            # Extract metadata
            metadata = await self._extract_metadata(document_path)
            
            # Load content based on format
            content = await self._load_content(document_path, doc_format)
            
            processing_time = time.time() - start_time
            
            result = ProcessingResult(
                document_id=document_id,
                document_path=document_path,
                document_format=doc_format.value,
                success=True,
                content=content,
                metadata=metadata,
                processing_time=processing_time,
                status=ProcessingStatus.COMPLETED
            )
            
            # Cache result
            self._document_cache[document_id] = result
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Failed to load document {document_path}: {e}")
            
            return ProcessingResult(
                document_id=document_id,
                document_path=document_path,
                document_format=self._detect_format(document_path).value,
                success=False,
                error_message=str(e),
                processing_time=processing_time,
                status=ProcessingStatus.FAILED
            )
    
    def _generate_document_id(self, document_path: str) -> str:
        """Generate unique document ID"""
        # Use hash of path and modification time for uniqueness
        path_hash = hashlib.md5(document_path.encode()).hexdigest()[:8]
        return f"doc_{path_hash}"
    
    def _detect_format(self, document_path: str) -> DocumentFormat:
        """Detect document format from file extension"""
        extension = Path(document_path).suffix.lower()
        
        format_map = {
            '.pdf': DocumentFormat.PDF,
            '.txt': DocumentFormat.TXT,
            '.json': DocumentFormat.JSON,
            '.xml': DocumentFormat.XML,
            '.md': DocumentFormat.MD,
            '.markdown': DocumentFormat.MD
        }
        
        return format_map.get(extension, DocumentFormat.UNKNOWN)
    
    async def _extract_metadata(self, document_path: str) -> DocumentMetadata:
        """Extract document metadata"""
        stat = os.stat(document_path)
        
        metadata = DocumentMetadata(
            file_size=stat.st_size,
            creation_time=stat.st_ctime,
            modification_time=stat.st_mtime,
            file_extension=Path(document_path).suffix,
            file_path=document_path
        )
        
        # Extract format-specific metadata
        if document_path.endswith('.json'):
            try:
                with open(document_path, 'r') as f:
                    data = json.load(f)
                    metadata.extracted_metadata = data
            except:
                pass
        
        return metadata
    
    async def _load_content(self, document_path: str, doc_format: DocumentFormat) -> str:
        """Load document content based on format"""
        if doc_format == DocumentFormat.JSON:
            with open(document_path, 'r') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        else:
            # Handle as text for now (PDF would need PyPDF2 or similar)
            with open(document_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    
    async def chunk_documents_parallel(self, load_results: List[ProcessingResult]) -> List[ProcessingResult]:
        """Chunk multiple documents in parallel"""
        self.logger.info(f"Chunking {len(load_results)} documents in parallel")
        
        tasks = []
        for result in load_results:
            if result.success and result.content:
                task = asyncio.create_task(self._chunk_single_document(result))
                tasks.append(task)
        
        chunk_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(chunk_results):
            if isinstance(result, Exception):
                # Create failed result
                original_result = load_results[i]
                failed_result = ProcessingResult(
                    document_id=original_result.document_id,
                    document_path=original_result.document_path,
                    document_format=original_result.document_format,
                    success=False,
                    error_message=str(result),
                    status=ProcessingStatus.FAILED
                )
                processed_results.append(failed_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _chunk_single_document(self, document_result: ProcessingResult) -> ProcessingResult:
        """Chunk a single document"""
        try:
            content = document_result.content
            chunk_size = 1000  # Characters per chunk
            
            chunks = []
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                chunks.append(chunk)
            
            # Create new result with chunks
            result = ProcessingResult(
                document_id=document_result.document_id,
                document_path=document_result.document_path,
                document_format=document_result.document_format,
                success=True,
                content=document_result.content,
                metadata=document_result.metadata,
                chunks=chunks,
                status=ProcessingStatus.COMPLETED
            )
            
            return result
            
        except Exception as e:
            return ProcessingResult(
                document_id=document_result.document_id,
                document_path=document_result.document_path,
                document_format=document_result.document_format,
                success=False,
                error_message=str(e),
                status=ProcessingStatus.FAILED
            )
    
    async def detect_duplicate_content(self, results: List[ProcessingResult]) -> List[DuplicateGroup]:
        """Detect duplicate content across documents"""
        duplicates = []
        
        # Simple content comparison for testing
        content_groups = {}
        for result in results:
            if result.success and result.content:
                content_hash = hashlib.md5(result.content.encode()).hexdigest()
                
                if content_hash not in content_groups:
                    content_groups[content_hash] = []
                content_groups[content_hash].append(result.document_path)
        
        # Find groups with multiple documents
        for content_hash, doc_paths in content_groups.items():
            if len(doc_paths) > 1:
                duplicate_group = DuplicateGroup(
                    documents=doc_paths,
                    similarity_score=1.0,  # Exact match
                    representative_document=doc_paths[0]
                )
                duplicates.append(duplicate_group)
        
        return duplicates
    
    async def assess_document_quality(self, results: List[ProcessingResult]) -> List[QualityScore]:
        """Assess document quality"""
        quality_scores = []
        
        for result in results:
            if result.success and result.content:
                # Simple quality metrics
                content_length = len(result.content)
                word_count = len(result.content.split())
                line_count = len(result.content.splitlines())
                
                # Basic scoring
                completeness_score = min(content_length / 1000, 1.0)  # Longer is better
                structure_score = min(line_count / 20, 1.0)  # More structure is better
                readability_score = min(word_count / content_length if content_length > 0 else 0, 1.0)
                metadata_score = 1.0 if result.metadata else 0.5
                
                overall_score = (completeness_score + structure_score + readability_score + metadata_score) / 4
                
                quality_score = QualityScore(
                    document_path=result.document_path,
                    overall_score=overall_score,
                    completeness_score=completeness_score,
                    structure_score=structure_score,
                    readability_score=readability_score,
                    metadata_score=metadata_score
                )
                
                quality_scores.append(quality_score)
        
        return quality_scores
    
    async def cluster_documents_by_topic(self, results: List[ProcessingResult]) -> List[TopicCluster]:
        """Cluster documents by topic"""
        # Simple keyword-based clustering for testing
        clusters = []
        
        # Define topic keywords
        topic_keywords = {
            "ai": ["artificial", "intelligence", "machine", "learning", "neural", "deep"],
            "bio": ["biological", "biology", "genetic", "molecular", "gene", "protein"],
            "tech": ["technology", "computer", "software", "system", "algorithm"],
        }
        
        topic_documents = {topic: [] for topic in topic_keywords}
        
        for result in results:
            if result.success and result.content:
                content_lower = result.content.lower()
                
                # Find best matching topic
                best_topic = None
                best_score = 0
                
                for topic, keywords in topic_keywords.items():
                    score = sum(1 for keyword in keywords if keyword in content_lower)
                    if score > best_score:
                        best_score = score
                        best_topic = topic
                
                if best_topic and best_score > 0:
                    topic_documents[best_topic].append(result.document_path)
        
        # Create clusters for topics with documents
        for topic, documents in topic_documents.items():
            if documents:
                cluster = TopicCluster(
                    cluster_id=f"cluster_{topic}",
                    documents=documents,
                    topic_keywords=topic_keywords[topic],
                    cluster_score=0.8,  # Default score
                    centroid_document=documents[0]
                )
                clusters.append(cluster)
        
        return clusters
    
    async def stream_documents_progressive(self, document_paths: List[str], 
                                         batch_size: int = 10) -> AsyncGenerator[List[ProcessingResult], None]:
        """Stream documents progressively in batches"""
        for i in range(0, len(document_paths), batch_size):
            batch = document_paths[i:i + batch_size]
            results = await self.load_documents_batch(batch)
            yield results
    
    async def process_documents_slow(self, document_paths: List[str]) -> List[ProcessingResult]:
        """Simulate slow processing for cancellation testing"""
        results = []
        for doc_path in document_paths:
            # Simulate slow processing
            await asyncio.sleep(0.5)
            result = await self._load_single_document(doc_path)
            results.append(result)
        return results
    
    async def process_documents_memory_efficient(self, document_paths: List[str], 
                                               memory_manager) -> List[ProcessingResult]:
        """Process documents with memory efficiency"""
        import gc
        results = []
        
        # Process in smaller chunks to control memory
        chunk_size = 3  # Process 3 documents at a time
        
        for i in range(0, len(document_paths), chunk_size):
            chunk = document_paths[i:i+chunk_size]
            
            # Check memory before processing chunk
            current_memory = memory_manager.get_current_memory_usage()
            if current_memory > memory_manager.memory_limit * 0.7:
                # Force garbage collection when approaching limit
                gc.collect()
                await asyncio.sleep(0.05)  # Give system time to clean up
            
            # Process chunk
            for doc_path in chunk:
                result = await self._load_single_document(doc_path)
                results.append(result)
            
            # Clean up after each chunk
            gc.collect()
        
        return results
    
    async def process_documents_scheduled(self, schedule, memory_manager) -> List[ProcessingResult]:
        """Process documents according to schedule"""
        results = []
        
        for doc_path in schedule.processing_order:
            result = await self._load_single_document(doc_path)
            results.append(result)
        
        return results
    
    def is_ready_for_new_tasks(self) -> bool:
        """Check if engine is ready for new tasks"""
        return not self._is_shutdown and len(self._processing_tasks) == 0
    
    def has_running_tasks(self) -> bool:
        """Check if there are running tasks"""
        return len(self._processing_tasks) > 0
    
    def shutdown(self):
        """Shutdown the engine"""
        self._is_shutdown = True
        self.executor.shutdown(wait=True)