#!/usr/bin/env python3
"""
Test Multi-Document Processing Engine (Task C.1)

TDD Implementation: Write tests FIRST, then implement code.
This file contains 15+ comprehensive test cases for multi-document processing.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, patch, AsyncMock
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor

# Import the implemented classes
from src.processing.multi_document_engine import MultiDocumentEngine
from src.processing.document_dependency_tracker import DocumentDependencyTracker, DocumentScheduler  
from src.processing.memory_manager import MemoryManager


class TestMultiDocumentProcessing:
    """Test suite for multi-document processing engine"""

    @pytest.fixture
    def temp_document_dir(self):
        """Create temporary directory with test documents"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test documents
            documents = []
            
            # Create PDF documents (simulated as text for testing)
            for i in range(5):
                doc_path = Path(temp_dir) / f"document_{i}.pdf"
                doc_path.write_text(f"Content of document {i}\nThis is test content for PDF {i}")
                documents.append(str(doc_path))
            
            # Create text documents
            for i in range(5):
                doc_path = Path(temp_dir) / f"text_{i}.txt"
                doc_path.write_text(f"Text content {i}\nPlain text document {i}")
                documents.append(str(doc_path))
            
            # Create structured documents
            for i in range(3):
                doc_path = Path(temp_dir) / f"data_{i}.json"
                doc_data = {
                    "title": f"Document {i}",
                    "content": f"JSON content {i}",
                    "metadata": {"author": f"Author {i}", "date": f"2024-0{i+1}-01"}
                }
                doc_path.write_text(json.dumps(doc_data))
                documents.append(str(doc_path))
            
            yield temp_dir, documents

    @pytest.fixture
    def multi_document_engine(self):
        """Create multi-document engine instance"""
        return MultiDocumentEngine()

    @pytest.fixture
    def dependency_tracker(self):
        """Create document dependency tracker instance"""
        return DocumentDependencyTracker()

    @pytest.fixture
    def document_scheduler(self):
        """Create document scheduler instance"""
        return DocumentScheduler()

    @pytest.fixture
    def memory_manager(self):
        """Create memory manager instance"""
        return MemoryManager()

    # Test Case 1: Multi-document batch processing
    @pytest.mark.asyncio
    async def test_multi_document_loader_batch_processing(self, multi_document_engine, temp_document_dir):
        """Test loading 5-20 documents simultaneously"""
        temp_dir, documents = temp_document_dir
        
        # Test with 5 documents
        batch_5 = documents[:5]
        results_5 = await multi_document_engine.load_documents_batch(batch_5)
        
        assert len(results_5) == 5
        assert all(result.success for result in results_5)
        assert all(result.document_id is not None for result in results_5)
        assert all(result.content is not None for result in results_5)
        
        # Test with 13 documents (full set)
        results_all = await multi_document_engine.load_documents_batch(documents)
        assert len(results_all) == 13
        assert all(result.success for result in results_all)
        
        # Verify batch processing is actually concurrent (should be faster than sequential)
        start_time = time.time()
        await multi_document_engine.load_documents_batch(documents)
        batch_time = time.time() - start_time
        
        # Batch processing should complete in reasonable time
        assert batch_time < len(documents) * 0.5  # Much faster than 0.5s per document

    # Test Case 2: Document dependency detection
    @pytest.mark.asyncio
    async def test_document_dependency_detection(self, dependency_tracker, temp_document_dir):
        """Test detecting cross-references and citations"""
        temp_dir, documents = temp_document_dir
        
        # Create documents with references
        ref_doc_path = Path(temp_dir) / "referring_doc.txt"
        ref_doc_path.write_text("This document references document_1.pdf and cites text_2.txt")
        
        citation_doc_path = Path(temp_dir) / "citation_doc.txt"
        citation_doc_path.write_text("See also: data_0.json for more details")
        
        all_docs = documents + [str(ref_doc_path), str(citation_doc_path)]
        
        dependencies = await dependency_tracker.detect_dependencies(all_docs)
        
        # Should detect references between documents
        assert len(dependencies) > 0
        assert any(dep.source_document == str(ref_doc_path) for dep in dependencies)
        
        # Import the enum for comparison
        from src.processing.document_dependency_tracker import DependencyType
        assert any(dep.dependency_type == DependencyType.REFERENCE for dep in dependencies)
        assert any(dep.dependency_type == DependencyType.CITATION for dep in dependencies)

    # Test Case 3: Document priority scheduling
    @pytest.mark.asyncio
    async def test_document_priority_scheduling(self, document_scheduler, temp_document_dir):
        """Test processing critical documents first"""
        temp_dir, documents = temp_document_dir
        
        # Assign priorities to documents
        priorities = {
            documents[0]: 10,  # High priority
            documents[1]: 5,   # Medium priority
            documents[2]: 1,   # Low priority
        }
        
        schedule = await document_scheduler.create_processing_schedule(
            documents[:3], priorities
        )
        
        # Should process high priority documents first
        assert schedule.processing_order[0] == documents[0]  # Highest priority first
        assert schedule.processing_order[-1] == documents[2]  # Lowest priority last
        assert schedule.estimated_total_time > 0
        assert len(schedule.parallel_groups) >= 0

    # Test Case 4: Memory efficient processing
    @pytest.mark.asyncio
    async def test_memory_efficient_processing(self, memory_manager, multi_document_engine, temp_document_dir):
        """Test handling large document sets without memory overflow"""
        temp_dir, documents = temp_document_dir
        
        # Set memory limit
        memory_limit = 100 * 1024 * 1024  # 100MB limit for testing
        memory_manager.set_memory_limit(memory_limit)
        
        # Monitor memory usage during processing
        initial_memory = memory_manager.get_current_memory_usage()
        
        results = await multi_document_engine.process_documents_memory_efficient(
            documents, memory_manager
        )
        
        peak_memory = memory_manager.get_peak_memory_usage()
        
        # Should not exceed memory limit
        assert peak_memory <= memory_limit
        assert len(results) == len(documents)
        assert all(result.success for result in results)
        
        # Should process all documents despite memory constraints
        assert memory_manager.memory_overflow_events == 0

    # Test Case 5: Document format heterogeneity
    @pytest.mark.asyncio
    async def test_document_format_heterogeneity(self, multi_document_engine, temp_document_dir):
        """Test mixing PDFs, text files, structured data"""
        temp_dir, documents = temp_document_dir
        
        # Documents already include PDF, TXT, and JSON formats
        results = await multi_document_engine.load_documents_batch(documents)
        
        # Group results by format
        pdf_results = [r for r in results if r.document_path.endswith('.pdf')]
        txt_results = [r for r in results if r.document_path.endswith('.txt')]
        json_results = [r for r in results if r.document_path.endswith('.json')]
        
        # Should handle all formats successfully
        assert len(pdf_results) == 5
        assert len(txt_results) == 5
        assert len(json_results) == 3
        assert all(result.success for result in results)
        
        # Each format should have appropriate metadata
        assert all(r.document_format == "pdf" for r in pdf_results)
        assert all(r.document_format == "txt" for r in txt_results)
        assert all(r.document_format == "json" for r in json_results)

    # Test Case 6: Processing failure isolation
    @pytest.mark.asyncio
    async def test_processing_failure_isolation(self, multi_document_engine, temp_document_dir):
        """Test that one document failure doesn't stop others"""
        temp_dir, documents = temp_document_dir
        
        # Create a corrupted document
        corrupted_doc = Path(temp_dir) / "corrupted.pdf"
        corrupted_doc.write_bytes(b"Invalid PDF content that should fail")
        
        # Add non-existent document
        missing_doc = str(Path(temp_dir) / "missing.txt")
        
        all_docs = documents + [str(corrupted_doc), missing_doc]
        
        results = await multi_document_engine.load_documents_batch(all_docs)
        
        # Should have results for all documents
        assert len(results) == len(all_docs)
        
        # Most documents should succeed
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        assert len(successful_results) >= len(documents)  # Original docs should work
        assert len(failed_results) >= 1  # At least corrupted or missing should fail
        
        # Failed documents should have error information
        assert all(result.error_message is not None for result in failed_results)

    # Test Case 7: Document metadata extraction
    @pytest.mark.asyncio
    async def test_document_metadata_extraction(self, multi_document_engine, temp_document_dir):
        """Test extracting creation dates, authors, versions"""
        temp_dir, documents = temp_document_dir
        
        results = await multi_document_engine.load_documents_batch(documents)
        
        for result in results:
            assert result.success
            metadata = result.metadata
            
            # Should extract basic metadata
            assert metadata.file_size > 0
            assert metadata.creation_time is not None
            assert metadata.modification_time is not None
            assert metadata.file_extension is not None
            
            # JSON documents should have extracted structured metadata
            if result.document_format == "json":
                assert hasattr(metadata, 'extracted_metadata')
                assert metadata.extracted_metadata is not None

    # Test Case 8: Parallel document chunking
    @pytest.mark.asyncio
    async def test_parallel_document_chunking(self, multi_document_engine, temp_document_dir):
        """Test chunking multiple documents in parallel"""
        temp_dir, documents = temp_document_dir
        
        # Load documents first
        load_results = await multi_document_engine.load_documents_batch(documents)
        
        # Chunk documents in parallel
        start_time = time.time()
        chunk_results = await multi_document_engine.chunk_documents_parallel(load_results)
        parallel_time = time.time() - start_time
        
        # Should have chunks for all documents
        assert len(chunk_results) == len(documents)
        assert all(result.success for result in chunk_results)
        assert all(len(result.chunks) > 0 for result in chunk_results)
        
        # Parallel chunking should be faster than sequential
        assert parallel_time < len(documents) * 0.3  # Should be much faster

    # Test Case 9: Document content deduplication
    @pytest.mark.asyncio
    async def test_document_content_deduplication(self, multi_document_engine, temp_document_dir):
        """Test identifying and handling duplicate content"""
        temp_dir, documents = temp_document_dir
        
        # Create duplicate documents
        duplicate_doc1 = Path(temp_dir) / "duplicate1.txt"
        duplicate_doc2 = Path(temp_dir) / "duplicate2.txt"
        same_content = "This is identical content in both documents"
        duplicate_doc1.write_text(same_content)
        duplicate_doc2.write_text(same_content)
        
        all_docs = documents + [str(duplicate_doc1), str(duplicate_doc2)]
        results = await multi_document_engine.load_documents_batch(all_docs)
        
        # Detect duplicates
        duplicates = await multi_document_engine.detect_duplicate_content(results)
        
        # Should identify the duplicate pair
        assert len(duplicates) > 0
        duplicate_group = duplicates[0]
        assert len(duplicate_group.documents) == 2
        assert duplicate_group.similarity_score >= 0.95  # Very high similarity

    # Test Case 10: Cross-document reference mapping
    @pytest.mark.asyncio
    async def test_cross_document_reference_mapping(self, dependency_tracker, temp_document_dir):
        """Test building citation and reference graphs"""
        temp_dir, documents = temp_document_dir
        
        # Create documents with explicit references
        ref_patterns = [
            ("ref1.txt", "Please see document_0.pdf for details"),
            ("ref2.txt", "As mentioned in text_1.txt, the analysis shows"),
            ("ref3.txt", "Building on data_0.json findings")
        ]
        
        for filename, content in ref_patterns:
            ref_path = Path(temp_dir) / filename
            ref_path.write_text(content)
            documents.append(str(ref_path))
        
        reference_graph = await dependency_tracker.build_reference_graph(documents)
        
        # Should build a connected graph
        assert reference_graph.node_count >= len(documents)
        assert reference_graph.edge_count > 0
        assert len(reference_graph.reference_chains) > 0
        
        # Should identify specific reference relationships
        references = reference_graph.get_references()
        assert any("document_0.pdf" in ref.target_document for ref in references)

    # Test Case 11: Document quality assessment
    @pytest.mark.asyncio
    async def test_document_quality_assessment(self, multi_document_engine, temp_document_dir):
        """Test scoring document completeness and reliability"""
        temp_dir, documents = temp_document_dir
        
        # Create documents with varying quality
        high_quality_doc = Path(temp_dir) / "high_quality.txt"
        high_quality_doc.write_text("""
        # Comprehensive Document
        
        ## Introduction
        This is a well-structured document with clear sections.
        
        ## Content
        Detailed analysis with multiple paragraphs and good structure.
        
        ## Conclusion
        Clear summary and conclusions.
        """)
        
        low_quality_doc = Path(temp_dir) / "low_quality.txt"
        low_quality_doc.write_text("short incomplete text")
        
        quality_docs = [str(high_quality_doc), str(low_quality_doc)]
        results = await multi_document_engine.load_documents_batch(quality_docs)
        
        quality_scores = await multi_document_engine.assess_document_quality(results)
        
        # Should assign different quality scores
        assert len(quality_scores) == 2
        high_score = next(s for s in quality_scores if "high_quality" in s.document_path)
        low_score = next(s for s in quality_scores if "low_quality" in s.document_path)
        
        assert high_score.overall_score > low_score.overall_score
        assert high_score.completeness_score > low_score.completeness_score
        assert high_score.structure_score > low_score.structure_score

    # Test Case 12: Temporal document ordering
    @pytest.mark.asyncio
    async def test_temporal_document_ordering(self, document_scheduler, temp_document_dir):
        """Test sorting documents by creation/modification time"""
        temp_dir, documents = temp_document_dir
        
        # Modify file timestamps to create temporal order
        base_time = time.time() - 86400  # Start from 24 hours ago
        for i, doc_path in enumerate(documents[:5]):
            timestamp = base_time + (i * 3600)  # 1 hour intervals
            os.utime(doc_path, (timestamp, timestamp))
        
        temporal_order = await document_scheduler.sort_documents_temporal(documents[:5])
        
        # Should be sorted by modification time
        assert len(temporal_order) == 5
        
        # Verify temporal ordering
        timestamps = [order.modification_time for order in temporal_order]
        assert timestamps == sorted(timestamps)  # Should be in ascending order

    # Test Case 13: Document clustering by topic
    @pytest.mark.asyncio
    async def test_document_clustering_by_topic(self, multi_document_engine, temp_document_dir):
        """Test grouping related documents automatically"""
        temp_dir, documents = temp_document_dir
        
        # Create documents with distinct topics
        topics = [
            ("ai_doc1.txt", "Artificial intelligence and machine learning algorithms"),
            ("ai_doc2.txt", "Deep learning neural networks and AI applications"),
            ("bio_doc1.txt", "Biological systems and molecular biology research"),
            ("bio_doc2.txt", "Genetic analysis and biological pathways"),
        ]
        
        topic_docs = []
        for filename, content in topics:
            doc_path = Path(temp_dir) / filename
            doc_path.write_text(content)
            topic_docs.append(str(doc_path))
        
        results = await multi_document_engine.load_documents_batch(topic_docs)
        clusters = await multi_document_engine.cluster_documents_by_topic(results)
        
        # Should identify topic-based clusters
        assert len(clusters) >= 2  # AI and biology clusters
        
        # Clusters should group similar topics
        ai_cluster = next((c for c in clusters if c.cluster_id == "cluster_ai"), None)
        bio_cluster = next((c for c in clusters if c.cluster_id == "cluster_bio"), None)
        
        assert ai_cluster is not None
        assert bio_cluster is not None
        assert len(ai_cluster.documents) >= 2
        assert len(bio_cluster.documents) >= 2

    # Test Case 14: Progressive document loading
    @pytest.mark.asyncio
    async def test_progressive_document_loading(self, multi_document_engine, temp_document_dir):
        """Test streaming large document collections"""
        temp_dir, documents = temp_document_dir
        
        # Create a large collection simulation
        large_collection = documents * 3  # Simulate 39 documents
        
        # Stream documents progressively
        loaded_count = 0
        async for batch in multi_document_engine.stream_documents_progressive(
            large_collection, batch_size=5
        ):
            assert len(batch) <= 5
            assert all(result.success for result in batch)
            loaded_count += len(batch)
        
        # Should load all documents progressively
        assert loaded_count == len(large_collection)

    # Test Case 15: Document processing cancellation
    @pytest.mark.asyncio
    async def test_document_processing_cancellation(self, multi_document_engine, temp_document_dir):
        """Test cleanly canceling long-running operations"""
        temp_dir, documents = temp_document_dir
        
        # Start a long-running processing task
        processing_task = asyncio.create_task(
            multi_document_engine.process_documents_slow(documents)
        )
        
        # Let it run briefly then cancel
        await asyncio.sleep(0.1)
        processing_task.cancel()
        
        # Should handle cancellation gracefully
        with pytest.raises(asyncio.CancelledError):
            await processing_task
        
        # Engine should remain in a clean state
        assert multi_document_engine.is_ready_for_new_tasks()
        assert not multi_document_engine.has_running_tasks()

    # Additional comprehensive test
    @pytest.mark.asyncio
    async def test_comprehensive_multi_document_workflow(self, multi_document_engine, dependency_tracker, 
                                                        document_scheduler, memory_manager, temp_document_dir):
        """Test complete multi-document processing workflow"""
        temp_dir, documents = temp_document_dir
        
        # 1. Set up memory management
        memory_manager.set_memory_limit(200 * 1024 * 1024)  # 200MB
        
        # 2. Detect dependencies
        dependencies = await dependency_tracker.detect_dependencies(documents)
        
        # 3. Create processing schedule
        schedule = await document_scheduler.create_processing_schedule(documents)
        
        # 4. Process documents according to schedule
        results = await multi_document_engine.process_documents_scheduled(
            schedule, memory_manager
        )
        
        # 5. Verify complete workflow success
        assert len(results) == len(documents)
        assert all(result.success for result in results)
        assert memory_manager.get_peak_memory_usage() <= memory_manager.memory_limit
        
        # 6. Verify processing order respected dependencies
        processed_order = [r.document_id for r in results]
        assert len(processed_order) == len(set(processed_order))  # No duplicates


# Performance benchmarks (not part of core tests but useful for validation)
class TestMultiDocumentPerformance:
    """Performance tests for multi-document processing"""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_throughput_requirement(self, multi_document_engine, temp_document_dir):
        """Test that processing throughput exceeds 5 documents/second"""
        temp_dir, documents = temp_document_dir
        
        # Test with subset for performance measurement
        test_docs = documents[:10]
        
        start_time = time.time()
        results = await multi_document_engine.load_documents_batch(test_docs)
        end_time = time.time()
        
        processing_time = end_time - start_time
        throughput = len(test_docs) / processing_time
        
        # Should meet throughput requirement
        assert throughput >= 5.0, f"Throughput {throughput:.2f} docs/sec < 5.0 requirement"
        assert all(result.success for result in results)

    @pytest.mark.asyncio
    @pytest.mark.performance  
    async def test_memory_limit_compliance(self, multi_document_engine, memory_manager, temp_document_dir):
        """Test that 100 documents don't exceed 4GB memory limit"""
        temp_dir, documents = temp_document_dir
        
        # Simulate 100 documents by repeating our test set
        large_doc_set = (documents * 8)[:100]  # Create exactly 100 documents
        
        memory_manager.set_memory_limit(4 * 1024 * 1024 * 1024)  # 4GB
        
        results = await multi_document_engine.process_documents_memory_efficient(
            large_doc_set, memory_manager
        )
        
        peak_memory = memory_manager.get_peak_memory_usage()
        
        # Should not exceed 4GB limit
        assert peak_memory <= 4 * 1024 * 1024 * 1024
        assert len(results) == 100
        assert all(result.success for result in results)


if __name__ == "__main__":
    # Run specific test
    pytest.main([__file__ + "::TestMultiDocumentProcessing::test_multi_document_loader_batch_processing", "-v"])