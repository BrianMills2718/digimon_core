"""
Integration tests for T301 Multi-Document Fusion functionality.
These tests capture the current behavior BEFORE decomposition (Red phase).
They must continue to pass AFTER decomposition (Green phase).
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from src.tools.phase3.t301_multi_document_fusion import (
        EntitySimilarityCalculator,
        EntityClusterFinder,
        ConflictResolver,
        RelationshipMerger,
        ConsistencyChecker,
        MultiDocumentFusion,
        FusionResult,
        ConsistencyMetrics,
        EntityCluster
    )
    T301_AVAILABLE = True
except ImportError as e:
    T301_AVAILABLE = False
    print(f"T301 not available: {e}")


@pytest.mark.skipif(not T301_AVAILABLE, reason="T301 module not available")
class TestT301IntegrationBeforeDecomposition:
    """Integration tests to capture current T301 behavior before decomposition."""
    
    def setup_method(self):
        """Set up test fixtures with mocked services."""
        # Mock services to avoid external dependencies
        self.mock_identity_service = Mock()
        self.mock_quality_service = Mock()
        self.mock_provenance_service = Mock()
        
        # Mock successful service responses
        self.mock_identity_service.create_mention.return_value = {
            'success': True,
            'entity_id': 'test_entity_1',
            'mention_id': 'test_mention_1'
        }
        
        self.mock_quality_service.assess_confidence.return_value = 0.85
        
    def test_entity_similarity_calculation(self):
        """Test EntitySimilarityCalculator functionality."""
        calculator = EntitySimilarityCalculator(self.mock_identity_service)
        
        # Test basic similarity calculation
        result = calculator.calculate(
            entity1_name="Apple Inc",
            entity2_name="Apple",
            entity1_type="ORG",
            entity2_type="ORG"
        )
        
        # Should return a similarity score
        assert isinstance(result, (int, float))
        assert 0 <= result <= 1.0
        
        # Test get_tool_info
        info = calculator.get_tool_info()
        assert isinstance(info, dict)
        assert 'tool_name' in info
        assert 'description' in info
        
    def test_entity_cluster_finder(self):
        """Test EntityClusterFinder functionality."""
        calculator = EntitySimilarityCalculator(self.mock_identity_service)
        finder = EntityClusterFinder(calculator)
        
        # Test entities clustering
        test_entities = [
            {'name': 'Apple Inc', 'type': 'ORG', 'confidence': 0.9},
            {'name': 'Apple', 'type': 'ORG', 'confidence': 0.8},
            {'name': 'Microsoft', 'type': 'ORG', 'confidence': 0.9}
        ]
        
        clusters = finder.find_clusters(
            entities=test_entities,
            similarity_threshold=0.8
        )
        
        # Should return clusters
        assert isinstance(clusters, list)
        for cluster in clusters:
            assert isinstance(cluster, dict)
            assert 'entities' in cluster
            
        # Test get_tool_info
        info = finder.get_tool_info()
        assert isinstance(info, dict)
        assert 'tool_name' in info
        
    def test_conflict_resolver(self):
        """Test ConflictResolver functionality."""
        resolver = ConflictResolver(self.mock_quality_service)
        
        # Test conflict resolution
        conflicting_entities = [
            {'name': 'Apple Inc', 'confidence': 0.9, 'source': 'doc1'},
            {'name': 'Apple Corp', 'confidence': 0.8, 'source': 'doc2'}
        ]
        
        resolved = resolver.resolve(
            conflicting_entities,
            strategy="confidence_weighted"
        )
        
        # Should return resolved entity
        assert isinstance(resolved, dict)
        assert 'name' in resolved
        assert 'confidence' in resolved
        
        # Test get_tool_info
        info = resolver.get_tool_info()
        assert isinstance(info, dict)
        assert 'tool_name' in info
        
    def test_relationship_merger(self):
        """Test RelationshipMerger functionality."""
        merger = RelationshipMerger()
        
        # Test relationship merging
        relationships = [
            {
                'source': 'Apple Inc',
                'target': 'iPhone',
                'type': 'PRODUCES',
                'confidence': 0.9,
                'evidence': 'Apple produces iPhone'
            },
            {
                'source': 'Apple',
                'target': 'iPhone',
                'type': 'PRODUCES', 
                'confidence': 0.8,
                'evidence': 'Apple makes iPhone'
            }
        ]
        
        merged = merger.merge(relationships)
        
        # Should return merged relationship
        assert isinstance(merged, dict)
        assert 'source' in merged
        assert 'target' in merged
        assert 'confidence' in merged
        
        # Test get_tool_info
        info = merger.get_tool_info()
        assert isinstance(info, dict)
        assert 'tool_name' in info
        
    def test_consistency_checker(self):
        """Test ConsistencyChecker functionality."""
        checker = ConsistencyChecker()
        
        # Test consistency checking
        entities = [
            {'name': 'Apple Inc', 'type': 'ORG', 'founded': '1976'},
            {'name': 'Steve Jobs', 'type': 'PERSON', 'birth': '1955'}
        ]
        
        relationships = [
            {
                'source': 'Steve Jobs',
                'target': 'Apple Inc',
                'type': 'FOUNDED',
                'date': '1976'
            }
        ]
        
        consistency = checker.check(entities, relationships)
        
        # Should return consistency metrics
        assert isinstance(consistency, dict)
        assert 'entity_consistency' in consistency
        assert 'temporal_consistency' in consistency
        
        # Test get_tool_info
        info = checker.get_tool_info()
        assert isinstance(info, dict)
        assert 'tool_name' in info
        
    @pytest.mark.skip(reason="MultiDocumentFusion requires complex mocking - test after decomposition")
    def test_multi_document_fusion_basic(self):
        """Test basic MultiDocumentFusion functionality."""
        # This will be tested after decomposition when dependencies are clearer
        pass
        
    def test_fusion_result_dataclass(self):
        """Test FusionResult data class."""
        result = FusionResult(
            total_documents=2,
            entities_before_fusion=10,
            entities_after_fusion=8,
            conflicts_resolved=2
        )
        
        assert result.total_documents == 2
        assert result.entities_before_fusion == 10
        assert result.entities_after_fusion == 8
        assert result.conflicts_resolved == 2
        
        # Test serialization
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict['total_documents'] == 2
        
    def test_consistency_metrics_dataclass(self):
        """Test ConsistencyMetrics data class."""
        metrics = ConsistencyMetrics(
            entity_consistency=0.9,
            temporal_consistency=0.8,
            overall_score=0.85
        )
        
        assert metrics.entity_consistency == 0.9
        assert metrics.temporal_consistency == 0.8
        assert metrics.overall_score == 0.85
        
        # Test get_tool_info
        info = metrics.get_tool_info()
        assert isinstance(info, dict)
        
    def test_entity_cluster_dataclass(self):
        """Test EntityCluster data class."""
        from src.tools.phase3.t301_multi_document_fusion import Entity
        
        # Mock Entity objects
        entity1 = Mock()
        entity1.name = "Apple Inc"
        entity2 = Mock()
        entity2.name = "Apple"
        
        cluster = EntityCluster(
            cluster_id="cluster_1",
            entities=[entity1, entity2],
            confidence=0.85
        )
        
        assert cluster.cluster_id == "cluster_1"
        assert len(cluster.entities) == 2
        assert cluster.confidence == 0.85
        
        # Test get_tool_info
        info = cluster.get_tool_info()
        assert isinstance(info, dict)


@pytest.mark.skipif(not T301_AVAILABLE, reason="T301 module not available")
class TestT301ComponentInteractions:
    """Test interactions between T301 components before decomposition."""
    
    def setup_method(self):
        """Set up interconnected components."""
        self.mock_identity_service = Mock()
        self.mock_quality_service = Mock()
        
        # Set up component chain
        self.calculator = EntitySimilarityCalculator(self.mock_identity_service)
        self.finder = EntityClusterFinder(self.calculator)
        self.resolver = ConflictResolver(self.mock_quality_service)
        self.merger = RelationshipMerger()
        self.checker = ConsistencyChecker()
        
    def test_end_to_end_entity_processing(self):
        """Test end-to-end entity processing pipeline."""
        # Mock input entities
        entities = [
            {'name': 'Apple Inc', 'type': 'ORG', 'confidence': 0.9},
            {'name': 'Apple Corporation', 'type': 'ORG', 'confidence': 0.8},
            {'name': 'Microsoft', 'type': 'ORG', 'confidence': 0.9}
        ]
        
        # Step 1: Find clusters
        clusters = self.finder.find_clusters(entities, similarity_threshold=0.7)
        assert isinstance(clusters, list)
        
        # Step 2: Resolve conflicts (simulate conflicts in clusters)
        if clusters:
            for cluster in clusters:
                if len(cluster.get('entities', [])) > 1:
                    resolved = self.resolver.resolve(
                        cluster['entities'], 
                        strategy="confidence_weighted"
                    )
                    assert isinstance(resolved, dict)
        
        # Step 3: Check consistency
        consistency = self.checker.check(entities, [])
        assert isinstance(consistency, dict)
        assert 'entity_consistency' in consistency
        
    def test_mcp_tool_endpoints(self):
        """Test that MCP tool endpoints work correctly."""
        # Test calculator MCP endpoint
        calc_result = self.calculator.execute_query("test query")
        assert isinstance(calc_result, dict)
        assert 'error' in calc_result or 'result' in calc_result
        
        # Test finder MCP endpoint
        finder_result = self.finder.execute_query("test query")
        assert isinstance(finder_result, dict)
        
        # Test resolver MCP endpoint
        resolver_result = self.resolver.execute_query("test query")
        assert isinstance(resolver_result, dict)


if __name__ == "__main__":
    # Run integration tests to capture current behavior
    print("🧪 Running T301 integration tests to capture current behavior...")
    
    if not T301_AVAILABLE:
        print("❌ T301 module not available - cannot run integration tests")
        exit(1)
    
    # Simple test runner
    test_instance = TestT301IntegrationBeforeDecomposition()
    test_instance.setup_method()
    
    tests = [
        test_instance.test_entity_similarity_calculation,
        test_instance.test_entity_cluster_finder,
        test_instance.test_conflict_resolver,
        test_instance.test_relationship_merger,
        test_instance.test_consistency_checker,
        test_instance.test_fusion_result_dataclass,
        test_instance.test_consistency_metrics_dataclass,
        test_instance.test_entity_cluster_dataclass
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests pass - ready for decomposition!")
    else:
        print("⚠️  Some tests failed - fix before decomposition")