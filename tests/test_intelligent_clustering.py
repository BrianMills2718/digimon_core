"""
Test suite for intelligent document clustering functionality.

This module tests the intelligent clustering of documents based on content,
temporal patterns, authorship, and citation networks.
"""

import pytest
import asyncio
from typing import List, Dict, Any
from pathlib import Path

from src.clustering.intelligent_clusterer import IntelligentClusterer
from src.clustering.similarity_calculator import SimilarityCalculator
from src.clustering.cluster_optimizer import ClusterOptimizer
from src.clustering.cluster_evaluator import ClusterEvaluator


@pytest.fixture
def sample_documents():
    """Sample documents for clustering tests"""
    return [
        {
            "path": "doc1.txt",
            "content": "Machine learning and artificial intelligence are revolutionizing healthcare. Deep learning models can diagnose diseases with high accuracy.",
            "metadata": {
                "authors": ["Dr. Smith", "Dr. Johnson"],
                "date": "2024-01-15",
                "keywords": ["AI", "healthcare", "machine learning"],
                "references": ["research_paper.txt", "ai_study.pdf"]
            }
        },
        {
            "path": "doc2.txt", 
            "content": "Climate change impacts are accelerating. Rising temperatures and sea levels threaten coastal communities worldwide.",
            "metadata": {
                "authors": ["Prof. Green", "Dr. Ocean"],
                "date": "2024-02-10",
                "keywords": ["climate", "environment", "sustainability"],
                "references": ["climate_report.pdf", "ocean_study.txt"]
            }
        },
        {
            "path": "doc3.txt",
            "content": "Neural networks and deep learning continue to advance AI capabilities. Computer vision applications are particularly promising.",
            "metadata": {
                "authors": ["Dr. Smith", "Prof. Tech"],
                "date": "2024-03-05",
                "keywords": ["AI", "neural networks", "computer vision"],
                "references": ["research_paper.txt", "vision_analysis.pdf"]
            }
        },
        {
            "path": "doc4.txt",
            "content": "Renewable energy solutions are crucial for combating climate change. Solar and wind power technologies are advancing rapidly.",
            "metadata": {
                "authors": ["Prof. Green", "Dr. Solar"],
                "date": "2024-02-20",
                "keywords": ["renewable energy", "climate", "sustainability"],
                "references": ["energy_report.pdf", "climate_report.pdf"]
            }
        },
        {
            "path": "doc5.txt",
            "content": "Blockchain technology applications extend beyond cryptocurrency. Supply chain management and smart contracts show promise.",
            "metadata": {
                "authors": ["Dr. Chain", "Prof. Crypto"],
                "date": "2024-01-30",
                "keywords": ["blockchain", "cryptocurrency", "smart contracts"],
                "references": ["crypto_study.pdf", "blockchain_analysis.txt"]
            }
        }
    ]


@pytest.fixture
def clusterer():
    """Create intelligent clusterer instance"""
    return IntelligentClusterer()


@pytest.fixture
def similarity_calculator():
    """Create similarity calculator instance"""
    return SimilarityCalculator()


@pytest.fixture
def cluster_optimizer():
    """Create cluster optimizer instance"""
    return ClusterOptimizer()


@pytest.fixture
def cluster_evaluator():
    """Create cluster evaluator instance"""
    return ClusterEvaluator()


@pytest.mark.asyncio
async def test_content_similarity_clustering(clusterer, sample_documents):
    """Test clustering by textual content similarity"""
    result = await clusterer.cluster_by_content_similarity(sample_documents)
    
    # Should create meaningful clusters
    assert len(result.clusters) >= 2, f"Expected at least 2 clusters, got {len(result.clusters)}"
    assert len(result.clusters) <= 4, f"Expected at most 4 clusters, got {len(result.clusters)}"
    
    # Check cluster quality
    assert result.silhouette_score > 0.3, f"Silhouette score too low: {result.silhouette_score}"
    
    # AI-related documents should cluster together
    ai_docs = ["doc1.txt", "doc3.txt"]  # Both have AI/ML content
    ai_cluster_found = False
    for cluster in result.clusters:
        cluster_docs = [doc["path"] for doc in cluster.documents]
        if all(doc in cluster_docs for doc in ai_docs):
            ai_cluster_found = True
            break
    
    assert ai_cluster_found, "AI-related documents should be clustered together"
    
    # Climate-related documents should cluster together
    climate_docs = ["doc2.txt", "doc4.txt"]  # Both have climate content
    climate_cluster_found = False
    for cluster in result.clusters:
        cluster_docs = [doc["path"] for doc in cluster.documents]
        if all(doc in cluster_docs for doc in climate_docs):
            climate_cluster_found = True
            break
    
    assert climate_cluster_found, "Climate-related documents should be clustered together"


@pytest.mark.asyncio
async def test_temporal_clustering_analysis(clusterer, sample_documents):
    """Test grouping documents by time periods"""
    result = await clusterer.cluster_by_temporal_patterns(sample_documents)
    
    # Should group documents by time periods
    assert len(result.temporal_clusters) > 0, "Should create temporal clusters"
    
    # Check that documents from similar time periods are grouped
    january_docs = ["doc1.txt", "doc5.txt"]  # Both from January 2024
    february_docs = ["doc2.txt", "doc4.txt"]  # Both from February 2024
    
    # Find temporal clusters and verify grouping
    temporal_groupings = {}
    for cluster in result.temporal_clusters:
        cluster_docs = [doc["path"] for doc in cluster.documents]
        cluster_period = cluster.time_period
        temporal_groupings[cluster_period] = cluster_docs
    
    # Should have reasonable temporal grouping
    assert len(temporal_groupings) >= 2, f"Expected at least 2 temporal periods, got {len(temporal_groupings)}"
    
    # Verify overall confidence
    assert result.overall_confidence > 0.6, f"Temporal clustering confidence too low: {result.overall_confidence}"


@pytest.mark.asyncio
async def test_author_based_clustering(clusterer, sample_documents):
    """Test clustering by authorship patterns"""
    result = await clusterer.cluster_by_authorship(sample_documents)
    
    # Should cluster documents by shared authors
    assert len(result.author_clusters) > 0, "Should create author-based clusters"
    
    # Dr. Smith appears in doc1 and doc3
    smith_docs = ["doc1.txt", "doc3.txt"]
    smith_cluster_found = False
    for cluster in result.author_clusters:
        cluster_docs = [doc["path"] for doc in cluster.documents]
        if all(doc in cluster_docs for doc in smith_docs):
            smith_cluster_found = True
            assert "Dr. Smith" in cluster.shared_authors
            break
    
    assert smith_cluster_found, "Documents by Dr. Smith should be clustered together"
    
    # Prof. Green appears in doc2 and doc4
    green_docs = ["doc2.txt", "doc4.txt"]
    green_cluster_found = False
    for cluster in result.author_clusters:
        cluster_docs = [doc["path"] for doc in cluster.documents]
        if all(doc in cluster_docs for doc in green_docs):
            green_cluster_found = True
            assert "Prof. Green" in cluster.shared_authors
            break
    
    assert green_cluster_found, "Documents by Prof. Green should be clustered together"
    
    # Check cluster quality metrics
    assert result.collaboration_strength > 0.5, f"Collaboration strength too low: {result.collaboration_strength}"


@pytest.mark.asyncio
async def test_topic_coherence_clustering(clusterer, sample_documents):
    """Test grouping by topic similarity"""
    result = await clusterer.cluster_by_topic_coherence(sample_documents)
    
    # Should create topically coherent clusters
    assert len(result.topic_clusters) >= 2, f"Expected at least 2 topic clusters, got {len(result.topic_clusters)}"
    
    # Check that AI/ML topics cluster together
    ai_keywords = set(["AI", "machine learning", "neural networks", "computer vision"])
    ai_cluster_found = False
    for cluster in result.topic_clusters:
        cluster_keywords = set()
        for topic in cluster.dominant_topics:
            cluster_keywords.update(topic.keywords)
        
        if len(ai_keywords.intersection(cluster_keywords)) >= 2:
            ai_cluster_found = True
            break
    
    assert ai_cluster_found, "AI/ML topics should form a coherent cluster"
    
    # Check that climate topics cluster together
    climate_keywords = set(["climate", "environment", "sustainability", "renewable energy"])
    climate_cluster_found = False
    for cluster in result.topic_clusters:
        cluster_keywords = set()
        for topic in cluster.dominant_topics:
            cluster_keywords.update(topic.keywords)
        
        if len(climate_keywords.intersection(cluster_keywords)) >= 2:
            climate_cluster_found = True
            break
    
    assert climate_cluster_found, "Climate topics should form a coherent cluster"
    
    # Check coherence scores
    for cluster in result.topic_clusters:
        assert cluster.coherence_score > 0.5, f"Topic coherence too low: {cluster.coherence_score}"


@pytest.mark.asyncio
async def test_citation_network_clustering(clusterer, sample_documents):
    """Test clustering based on citation patterns"""
    result = await clusterer.cluster_by_citation_network(sample_documents)
    
    # Should create clusters based on citation relationships
    assert len(result.citation_clusters) > 0, "Should create citation-based clusters"
    
    # Documents that cite the same sources should cluster together
    # doc1 and doc3 both reference "research_paper.txt"
    shared_citation_docs = ["doc1.txt", "doc3.txt"]
    citation_cluster_found = False
    for cluster in result.citation_clusters:
        cluster_docs = [doc["path"] for doc in cluster.documents]
        if all(doc in cluster_docs for doc in shared_citation_docs):
            citation_cluster_found = True
            assert "research_paper.txt" in cluster.shared_citations
            break
    
    assert citation_cluster_found, "Documents with shared citations should cluster together"
    
    # doc2 and doc4 both reference "climate_report.pdf"
    climate_citation_docs = ["doc2.txt", "doc4.txt"]
    climate_citation_cluster_found = False
    for cluster in result.citation_clusters:
        cluster_docs = [doc["path"] for doc in cluster.documents]
        if all(doc in cluster_docs for doc in climate_citation_docs):
            climate_citation_cluster_found = True
            assert "climate_report.pdf" in cluster.shared_citations
            break
    
    assert climate_citation_cluster_found, "Documents citing climate sources should cluster together"
    
    # Check citation network metrics
    assert result.network_density > 0.1, f"Citation network density too low: {result.network_density}"


@pytest.mark.asyncio
async def test_hierarchical_cluster_formation(clusterer, sample_documents):
    """Test building multi-level clustering"""
    result = await clusterer.create_hierarchical_clusters(sample_documents)
    
    # Should create hierarchical structure
    assert result.hierarchy_levels >= 2, f"Expected at least 2 hierarchy levels, got {result.hierarchy_levels}"
    assert result.hierarchy_levels <= 4, f"Too many hierarchy levels: {result.hierarchy_levels}"
    
    # Check root level clusters
    assert len(result.root_clusters) >= 2, "Should have multiple root clusters"
    assert len(result.root_clusters) <= 5, "Too many root clusters"
    
    # Check that some clusters have subclusters
    has_subclusters = any(len(cluster.subclusters) > 0 for cluster in result.root_clusters)
    assert has_subclusters, "At least one cluster should have subclusters"
    
    # Verify hierarchy quality
    assert result.hierarchy_quality > 0.6, f"Hierarchy quality too low: {result.hierarchy_quality}"
    
    # Check that leaf nodes contain actual documents
    total_docs_in_leaves = 0
    for cluster in result.root_clusters:
        total_docs_in_leaves += cluster.count_documents_recursive()
    
    assert total_docs_in_leaves == len(sample_documents), "All documents should be in leaf nodes"


@pytest.mark.asyncio
async def test_cluster_quality_metrics(cluster_evaluator, sample_documents):
    """Test measuring clustering effectiveness"""
    # Create some test clusters for evaluation
    test_clusters = [
        {
            "documents": [sample_documents[0], sample_documents[2]],  # AI docs
            "cluster_id": "ai_cluster",
            "centroid": [0.8, 0.2, 0.1]
        },
        {
            "documents": [sample_documents[1], sample_documents[3]],  # Climate docs
            "cluster_id": "climate_cluster", 
            "centroid": [0.1, 0.9, 0.1]
        },
        {
            "documents": [sample_documents[4]],  # Blockchain doc
            "cluster_id": "blockchain_cluster",
            "centroid": [0.1, 0.1, 0.8]
        }
    ]
    
    metrics = await cluster_evaluator.evaluate_clustering_quality(test_clusters, sample_documents)
    
    # Check silhouette score
    assert metrics.silhouette_score >= 0.3, f"Silhouette score too low: {metrics.silhouette_score}"
    assert metrics.silhouette_score <= 1.0, f"Invalid silhouette score: {metrics.silhouette_score}"
    
    # Check Davies-Bouldin index (lower is better)
    assert metrics.davies_bouldin_index >= 0.0, f"Invalid Davies-Bouldin index: {metrics.davies_bouldin_index}"
    assert metrics.davies_bouldin_index <= 5.0, f"Davies-Bouldin index too high: {metrics.davies_bouldin_index}"
    
    # Check intra-cluster cohesion (higher is better)
    assert metrics.intra_cluster_cohesion >= 0.0, f"Invalid cohesion: {metrics.intra_cluster_cohesion}"
    assert metrics.intra_cluster_cohesion <= 1.0, f"Invalid cohesion: {metrics.intra_cluster_cohesion}"
    
    # Check inter-cluster separation (higher is better)
    assert metrics.inter_cluster_separation >= 0.0, f"Invalid separation: {metrics.inter_cluster_separation}"
    assert metrics.inter_cluster_separation <= 1.0, f"Invalid separation: {metrics.inter_cluster_separation}"
    
    # Overall quality should be reasonable
    assert metrics.overall_quality > 0.4, f"Overall clustering quality too low: {metrics.overall_quality}"


@pytest.mark.asyncio
async def test_dynamic_cluster_adjustment(clusterer, sample_documents):
    """Test adapting clusters as documents are added"""
    # Start with initial documents
    initial_docs = sample_documents[:3]
    initial_result = await clusterer.cluster_by_content_similarity(initial_docs)
    
    # Add new documents dynamically
    new_docs = sample_documents[3:]
    updated_result = await clusterer.adjust_clusters_dynamically(
        initial_result, new_docs
    )
    
    # Should handle dynamic updates
    assert len(updated_result.clusters) >= len(initial_result.clusters), "Should maintain or increase cluster count"
    
    # Total documents should be preserved
    total_docs_updated = sum(len(cluster.documents) for cluster in updated_result.clusters)
    assert total_docs_updated == len(sample_documents), "All documents should be in updated clusters"
    
    # Quality should remain reasonable
    assert updated_result.silhouette_score > 0.2, f"Updated clustering quality degraded: {updated_result.silhouette_score}"
    
    # Check that adjustment was incremental (not full re-clustering)
    assert updated_result.was_incremental, "Update should be incremental, not full re-clustering"
    assert updated_result.adjustment_time < 1.0, f"Dynamic adjustment too slow: {updated_result.adjustment_time}s"


@pytest.mark.asyncio
async def test_outlier_document_detection(clusterer, sample_documents):
    """Test identifying documents that don't fit clusters"""
    # Add an outlier document
    outlier_doc = {
        "path": "outlier.txt",
        "content": "Ancient Egyptian hieroglyphics and pyramid construction techniques from the Old Kingdom period.",
        "metadata": {
            "authors": ["Dr. Ancient"],
            "date": "2024-04-01",
            "keywords": ["history", "archaeology", "Egypt"],
            "references": ["archaeology_journal.pdf"]
        }
    }
    
    docs_with_outlier = sample_documents + [outlier_doc]
    
    result = await clusterer.detect_outliers(docs_with_outlier)
    
    # Should identify the outlier
    assert len(result.outliers) > 0, "Should detect outlier documents"
    
    # The archaeology document should be flagged as outlier
    outlier_paths = [doc["path"] for doc in result.outliers]
    assert "outlier.txt" in outlier_paths, "Archaeology document should be detected as outlier"
    
    # Check outlier scores
    for outlier in result.outlier_details:
        assert outlier.outlier_score > 0.5, f"Outlier score too low: {outlier.outlier_score}"
        assert outlier.distance_to_nearest_cluster > 0.3, "Outlier should be distant from clusters"
    
    # Main clusters should still be coherent
    assert len(result.main_clusters) >= 2, "Should maintain main clusters after outlier detection"
    assert result.cluster_stability > 0.6, f"Cluster stability reduced by outliers: {result.cluster_stability}"


@pytest.mark.asyncio
async def test_cluster_summary_generation(clusterer, sample_documents):
    """Test generating summaries for each cluster"""
    clustering_result = await clusterer.cluster_by_content_similarity(sample_documents)
    
    summary_result = await clusterer.generate_cluster_summaries(clustering_result)
    
    # Should generate summaries for all clusters
    assert len(summary_result.cluster_summaries) == len(clustering_result.clusters), "Should have summary for each cluster"
    
    for summary in summary_result.cluster_summaries:
        # Each summary should have key components
        assert len(summary.key_topics) > 0, "Summary should identify key topics"
        assert len(summary.representative_documents) > 0, "Summary should identify representative docs"
        assert len(summary.cluster_description) > 20, "Summary description should be substantial"
        
        # Check topic relevance
        assert summary.topic_coherence > 0.5, f"Topic coherence too low: {summary.topic_coherence}"
        
        # Check summary quality
        assert summary.summary_quality > 0.6, f"Summary quality too low: {summary.summary_quality}"
        
        # Should identify common themes
        assert len(summary.common_themes) > 0, "Should identify common themes in cluster"
        
        # Should have reasonable document coverage
        assert len(summary.representative_documents) <= len(clustering_result.clusters[0].documents), "Too many representative docs"
    
    # Overall summary quality
    assert summary_result.overall_summary_quality > 0.6, f"Overall summary quality low: {summary_result.overall_summary_quality}"


@pytest.mark.asyncio
async def test_similarity_calculator_features(similarity_calculator):
    """Test multi-modal similarity computation"""
    doc1 = {
        "content": "Machine learning applications in healthcare diagnosis",
        "metadata": {"keywords": ["AI", "healthcare"], "authors": ["Dr. Smith"]}
    }
    doc2 = {
        "content": "Artificial intelligence for medical image analysis", 
        "metadata": {"keywords": ["AI", "medical"], "authors": ["Dr. Johnson"]}
    }
    doc3 = {
        "content": "Climate change impacts on Arctic ice",
        "metadata": {"keywords": ["climate", "environment"], "authors": ["Prof. Green"]}
    }
    
    # Test content similarity
    content_sim = await similarity_calculator.calculate_content_similarity(doc1, doc2)
    assert content_sim > 0.5, f"Content similarity too low for related docs: {content_sim}"
    
    content_sim_unrelated = await similarity_calculator.calculate_content_similarity(doc1, doc3)
    assert content_sim_unrelated < 0.3, f"Content similarity too high for unrelated docs: {content_sim_unrelated}"
    
    # Test metadata similarity
    metadata_sim = await similarity_calculator.calculate_metadata_similarity(doc1, doc2)
    assert metadata_sim > 0.3, f"Metadata similarity too low: {metadata_sim}"
    
    # Test combined similarity
    combined_sim = await similarity_calculator.calculate_combined_similarity(doc1, doc2)
    assert combined_sim > 0.4, f"Combined similarity too low: {combined_sim}"
    assert combined_sim <= 1.0, f"Invalid combined similarity: {combined_sim}"
    
    # Test similarity matrix
    documents = [doc1, doc2, doc3]
    similarity_matrix = await similarity_calculator.compute_similarity_matrix(documents)
    
    assert similarity_matrix.shape == (3, 3), f"Wrong similarity matrix shape: {similarity_matrix.shape}"
    assert similarity_matrix[0, 1] > 0.4, "Similar documents should have high similarity"
    assert similarity_matrix[0, 2] < 0.4, "Dissimilar documents should have low similarity"


if __name__ == "__main__":
    pytest.main([__file__])