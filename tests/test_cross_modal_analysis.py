#!/usr/bin/env python3
"""
Test Cross-Modal Content Analysis (Task C.2)

TDD Implementation: Write tests FIRST, then implement code.
This file contains 12+ comprehensive test cases for cross-modal analysis.
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock

# Import the classes to implement
from src.analysis.cross_modal_analyzer import CrossModalAnalyzer
from src.analysis.structural_analyzer import StructuralAnalyzer
from src.analysis.metadata_correlator import MetadataCorrelator
from src.analysis.citation_network_builder import CitationNetworkBuilder


class TestCrossModalAnalysis:
    """Test suite for cross-modal content analysis"""

    @pytest.fixture
    def cross_modal_analyzer(self):
        """Create cross-modal analyzer instance"""
        return CrossModalAnalyzer()

    @pytest.fixture
    def structural_analyzer(self):
        """Create structural analyzer instance"""
        return StructuralAnalyzer()

    @pytest.fixture
    def metadata_correlator(self):
        """Create metadata correlator instance"""
        return MetadataCorrelator()

    @pytest.fixture
    def citation_network_builder(self):
        """Create citation network builder instance"""
        return CitationNetworkBuilder()

    @pytest.fixture
    def multi_modal_documents(self):
        """Create test documents with multiple modalities"""
        with tempfile.TemporaryDirectory() as temp_dir:
            documents = []
            
            # Document 1: Structured research paper
            doc1_path = Path(temp_dir) / "research_paper.txt"
            doc1_content = """
# AI Safety Research Paper

## Abstract
This paper explores artificial intelligence safety mechanisms.

## Introduction
AI safety is critical for deployment of autonomous systems.

## Methodology
We employed reinforcement learning with human feedback.

## Results
Our approach achieved 95% safety compliance.

## Conclusion
RLHF shows promise for AI alignment.

## References
- Smith et al. (2023) "AI Alignment"
- Jones (2024) "Safety Measures"
"""
            doc1_path.write_text(doc1_content)
            
            # Create metadata for doc1
            doc1_meta = {
                "title": "AI Safety Research Paper",
                "authors": ["Dr. Alice Smith", "Dr. Bob Jones"],
                "date": "2024-01-15",
                "journal": "AI Safety Journal",
                "keywords": ["AI", "safety", "alignment"],
                "citations": ["Smith2023", "Jones2024"]
            }
            
            documents.append({
                "path": str(doc1_path),
                "content": doc1_content,
                "metadata": doc1_meta,
                "format": "structured_text"
            })
            
            # Document 2: JSON structured data
            doc2_path = Path(temp_dir) / "experiment_data.json"
            doc2_data = {
                "experiment_id": "EXP_001",
                "title": "RLHF Safety Evaluation",
                "researchers": ["Dr. Alice Smith", "Dr. Carol Brown"],
                "date": "2024-02-01",
                "data": {
                    "safety_scores": [0.92, 0.94, 0.96, 0.93, 0.95],
                    "test_cases": 500,
                    "success_rate": 0.95
                },
                "references": ["Smith2023"],
                "related_papers": ["research_paper.txt"]
            }
            doc2_path.write_text(json.dumps(doc2_data, indent=2))
            
            documents.append({
                "path": str(doc2_path),
                "content": json.dumps(doc2_data, indent=2),
                "metadata": doc2_data,
                "format": "json"
            })
            
            # Document 3: Citation-heavy paper
            doc3_path = Path(temp_dir) / "literature_review.txt"
            doc3_content = """
# Literature Review on AI Safety

## Overview
This review synthesizes research from Smith et al. (2023) and Jones (2024).

According to Smith2023, AI alignment requires careful consideration.
The work by Jones2024 demonstrates practical safety measures.

## Analysis
Building on research_paper.txt findings, we observe convergent evidence.
The experiment_data.json results support these theoretical frameworks.

## Future Work
Integration with EXP_001 data suggests promising directions.
"""
            doc3_path.write_text(doc3_content)
            
            doc3_meta = {
                "title": "Literature Review on AI Safety",
                "authors": ["Dr. David Wilson"],
                "date": "2024-03-01",
                "type": "review",
                "cited_works": ["Smith2023", "Jones2024", "EXP_001"],
                "references_to": ["research_paper.txt", "experiment_data.json"]
            }
            
            documents.append({
                "path": str(doc3_path),
                "content": doc3_content,
                "metadata": doc3_meta,
                "format": "citation_text"
            })
            
            yield documents

    # Test Case 1: Text content analysis integration
    @pytest.mark.asyncio
    async def test_text_content_analysis_integration(self, cross_modal_analyzer, multi_modal_documents):
        """Test extracting and correlating textual content"""
        
        analysis_result = await cross_modal_analyzer.analyze_text_content(multi_modal_documents)
        
        # Should extract key concepts from all documents
        assert len(analysis_result.extracted_concepts) > 0
        concept_names = [concept.name.lower() for concept in analysis_result.extracted_concepts]
        assert "ai safety" in concept_names
        assert "alignment" in concept_names
        
        # Should identify relationships between concepts
        assert len(analysis_result.concept_relationships) > 0
        
        # Should correlate content across documents
        assert len(analysis_result.cross_document_correlations) > 0
        
        # Should maintain high confidence scores
        assert analysis_result.overall_confidence > 0.8

    # Test Case 2: Document structure analysis
    @pytest.mark.asyncio
    async def test_document_structure_analysis(self, structural_analyzer, multi_modal_documents):
        """Test analyzing headings, sections, formatting"""
        
        # Debug: Print first document content
        print(f"DEBUG: First document content: {multi_modal_documents[0]['content'][:200]}")
        
        structure_results = await structural_analyzer.analyze_document_structures(multi_modal_documents)
        
        # Should identify structural elements
        assert len(structure_results) == len(multi_modal_documents)
        
        # At least one document should have headings (the markdown ones)
        total_headings = sum(len(result.headings) for result in structure_results)
        assert total_headings > 0
        
        # Check that structured documents have expected properties
        structured_docs = [result for result in structure_results if len(result.headings) > 0]
        assert len(structured_docs) > 0
        
        for result in structured_docs:
            # Should detect headings in structured documents
            assert len(result.headings) > 0
            
            # Should analyze document hierarchy
            assert result.max_heading_level >= 1
            assert len(result.sections) > 0
        
        # At least one document should be an academic paper (with abstract/introduction)
        academic_docs = [result for result in structure_results 
                        if result.has_abstract or result.has_introduction]
        assert len(academic_docs) > 0
            
        # All documents should have a determined structure type
        for result in structure_results:
            assert result.structure_type in ["academic_paper", "data_document", "review_article"]

    # Test Case 3: Metadata correlation analysis
    @pytest.mark.asyncio
    async def test_metadata_correlation_analysis(self, metadata_correlator, multi_modal_documents):
        """Test linking authors, dates, topics across documents"""
        
        correlations = await metadata_correlator.correlate_metadata(multi_modal_documents)
        
        # Should identify author collaborations
        assert len(correlations.author_networks) > 0
        
        # Should identify shared authors
        shared_authors = correlations.get_shared_authors()
        assert "Dr. Alice Smith" in shared_authors
        
        # Should identify temporal relationships
        assert len(correlations.temporal_relationships) > 0
        
        # Should identify topic overlaps
        topic_overlaps = correlations.get_topic_overlaps()
        assert len(topic_overlaps) > 0
        assert any("AI safety" in overlap.topics for overlap in topic_overlaps)

    # Test Case 4: Citation network construction
    @pytest.mark.asyncio
    async def test_citation_network_construction(self, citation_network_builder, multi_modal_documents):
        """Test building citation graphs and networks"""
        
        citation_network = await citation_network_builder.build_citation_network(multi_modal_documents)
        
        # Should build connected network
        assert citation_network.node_count >= len(multi_modal_documents)
        assert citation_network.edge_count > 0
        
        # Should identify citation relationships
        citations = citation_network.get_all_citations()
        assert len(citations) > 0
        
        # Should identify most cited works
        most_cited = citation_network.get_most_cited_works(top_n=2)
        assert len(most_cited) > 0
        
        # Should calculate network metrics
        metrics = citation_network.calculate_network_metrics()
        assert metrics.density > 0
        assert metrics.clustering_coefficient >= 0

    # Test Case 5: Cross-modal entity alignment
    @pytest.mark.asyncio
    async def test_cross_modal_entity_alignment(self, cross_modal_analyzer, multi_modal_documents):
        """Test matching entities across different modalities"""
        
        alignment_result = await cross_modal_analyzer.align_entities_cross_modal(multi_modal_documents)
        
        # Should align entities across modalities
        assert len(alignment_result.aligned_entities) > 0
        
        # Should identify "Dr. Alice Smith" across text and metadata
        smith_alignments = [e for e in alignment_result.aligned_entities 
                          if "Alice Smith" in e.canonical_name]
        assert len(smith_alignments) > 0
        
        # Should achieve high alignment accuracy
        assert alignment_result.alignment_accuracy > 0.85
        
        # Should handle entity variations
        entity_variations = alignment_result.get_entity_variations()
        assert len(entity_variations) > 0

    # Test Case 6: Structural pattern detection
    @pytest.mark.asyncio
    async def test_structural_pattern_detection(self, structural_analyzer, multi_modal_documents):
        """Test finding common document structures"""
        
        patterns = await structural_analyzer.detect_structural_patterns(multi_modal_documents)
        
        # Should identify common patterns
        assert len(patterns.common_patterns) > 0
        
        # Should identify academic paper pattern
        academic_pattern = next((p for p in patterns.common_patterns 
                               if p.pattern_type == "academic_paper"), None)
        assert academic_pattern is not None
        assert academic_pattern.frequency >= 1
        
        # Should identify pattern variations
        assert len(patterns.pattern_variations) > 0
        
        # Should provide pattern confidence scores
        assert all(p.confidence > 0.7 for p in patterns.common_patterns)

    # Test Case 7: Reference resolution engine
    @pytest.mark.asyncio
    async def test_reference_resolution_engine(self, citation_network_builder, multi_modal_documents):
        """Test resolving citations to actual documents"""
        
        resolution_results = await citation_network_builder.resolve_references(multi_modal_documents)
        
        # Should resolve internal references
        internal_refs = resolution_results.get_internal_references()
        assert len(internal_refs) > 0
        
        # Should resolve cross-document references
        cross_refs = resolution_results.get_cross_document_references()
        assert len(cross_refs) > 0
        
        # Should identify unresolved references
        unresolved = resolution_results.get_unresolved_references()
        assert isinstance(unresolved, list)  # May be empty if all resolved
        
        # Should achieve high resolution rate
        assert resolution_results.resolution_rate > 0.8

    # Test Case 8: Temporal metadata analysis
    @pytest.mark.asyncio
    async def test_temporal_metadata_analysis(self, metadata_correlator, multi_modal_documents):
        """Test analyzing creation and modification patterns"""
        
        temporal_analysis = await metadata_correlator.analyze_temporal_patterns(multi_modal_documents)
        
        # Should identify temporal sequence
        assert len(temporal_analysis.document_timeline) == len(multi_modal_documents)
        
        # Should identify research progression
        progression = temporal_analysis.get_research_progression()
        assert len(progression.research_phases) > 0
        
        # Should identify temporal gaps
        temporal_gaps = temporal_analysis.identify_temporal_gaps()
        assert isinstance(temporal_gaps, list)
        
        # Should calculate temporal metrics
        metrics = temporal_analysis.get_temporal_metrics()
        assert metrics.average_time_between_publications > 0

    # Test Case 9: Author collaboration networks
    @pytest.mark.asyncio
    async def test_author_collaboration_networks(self, metadata_correlator, multi_modal_documents):
        """Test mapping co-authorship and collaboration"""
        
        collaboration_network = await metadata_correlator.build_collaboration_network(multi_modal_documents)
        
        # Should identify collaborations
        assert collaboration_network.collaboration_count > 0
        
        # Should identify key collaborators
        key_collaborators = collaboration_network.get_key_collaborators()
        assert "Dr. Alice Smith" in [c.name for c in key_collaborators]
        
        # Should calculate collaboration metrics
        metrics = collaboration_network.get_collaboration_metrics()
        assert metrics.network_density > 0
        assert metrics.average_collaborations_per_author > 0

    # Test Case 10: Topic evolution tracking
    @pytest.mark.asyncio
    async def test_topic_evolution_tracking(self, cross_modal_analyzer, multi_modal_documents):
        """Test tracking how topics change across documents"""
        
        evolution_analysis = await cross_modal_analyzer.track_topic_evolution(multi_modal_documents)
        
        # Should identify topic evolution
        assert len(evolution_analysis.topic_trajectories) > 0
        
        # Should track "AI safety" evolution
        ai_safety_trajectory = next((t for t in evolution_analysis.topic_trajectories 
                                   if "AI safety" in t.topic_name), None)
        assert ai_safety_trajectory is not None
        
        # Should identify topic emergence and decline
        topic_changes = evolution_analysis.get_topic_changes()
        assert len(topic_changes.emerging_topics) >= 0
        assert len(topic_changes.declining_topics) >= 0
        
        # Should provide evolution confidence
        assert evolution_analysis.overall_confidence > 0.7

    # Test Case 11: Cross-modal confidence scoring
    @pytest.mark.asyncio
    async def test_cross_modal_confidence_scoring(self, cross_modal_analyzer, multi_modal_documents):
        """Test aggregating confidence across modalities"""
        
        confidence_results = await cross_modal_analyzer.calculate_cross_modal_confidence(multi_modal_documents)
        
        # Should provide confidence for each modality
        assert len(confidence_results.modality_confidences) > 0
        modalities = [conf.modality for conf in confidence_results.modality_confidences]
        assert "text" in modalities
        assert "metadata" in modalities
        assert "structure" in modalities
        
        # Should aggregate overall confidence
        assert 0.0 <= confidence_results.overall_confidence <= 1.0
        
        # Should identify confidence variations
        conf_variance = confidence_results.calculate_confidence_variance()
        assert conf_variance >= 0
        
        # Should provide confidence breakdown
        breakdown = confidence_results.get_confidence_breakdown()
        assert len(breakdown) > 0

    # Test Case 12: Modality conflict resolution
    @pytest.mark.asyncio
    async def test_modality_conflict_resolution(self, cross_modal_analyzer, multi_modal_documents):
        """Test handling contradictions between modalities"""
        
        # Add conflicting information to test conflict resolution
        modified_docs = multi_modal_documents.copy()
        
        # Create a document with conflicting metadata
        conflict_doc = modified_docs[0].copy()
        conflict_doc["metadata"]["authors"] = ["Dr. Different Author"]  # Conflicts with content
        
        conflict_results = await cross_modal_analyzer.resolve_modality_conflicts(
            [conflict_doc] + modified_docs[1:]
        )
        
        # Should identify conflicts
        assert len(conflict_results.detected_conflicts) > 0
        
        # Should provide conflict resolution strategies
        assert len(conflict_results.resolution_strategies) > 0
        
        # Should resolve conflicts with confidence scores
        resolved_conflicts = conflict_results.get_resolved_conflicts()
        assert len(resolved_conflicts) >= 0  # May resolve all or some
        
        # Should maintain data integrity
        assert conflict_results.data_integrity_score > 0.7


# Performance and integration tests
class TestCrossModalPerformance:
    """Performance tests for cross-modal analysis"""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_analysis_time_requirement(self, cross_modal_analyzer, multi_modal_documents):
        """Test that analysis completes within 500ms per document"""
        import time
        
        start_time = time.time()
        result = await cross_modal_analyzer.analyze_text_content(multi_modal_documents)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        time_per_document = analysis_time / len(multi_modal_documents)
        
        # Should meet performance requirement
        assert time_per_document < 0.5, f"Analysis time {time_per_document:.3f}s > 0.5s requirement"
        assert result.overall_confidence > 0.8

    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_entity_alignment_accuracy_requirement(self, cross_modal_analyzer, multi_modal_documents):
        """Test that entity alignment achieves >85% accuracy"""
        
        alignment_result = await cross_modal_analyzer.align_entities_cross_modal(multi_modal_documents)
        
        # Should meet accuracy requirement
        assert alignment_result.alignment_accuracy > 0.85, \
            f"Alignment accuracy {alignment_result.alignment_accuracy:.3f} < 0.85 requirement"


if __name__ == "__main__":
    # Run specific test
    pytest.main([__file__ + "::TestCrossModalAnalysis::test_text_content_analysis_integration", "-v"])