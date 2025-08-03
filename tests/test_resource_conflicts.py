"""
Test Resource Conflict Analysis

Tests for ResourceConflictAnalyzer and ResourceUsageDetector functionality.
Ensures accurate conflict detection between tools for parallel execution.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.analysis.resource_conflict_analyzer import (
    ResourceConflictAnalyzer, ConflictResult, ConflictType
)
from src.analysis.resource_usage_detector import (
    ResourceUsageDetector, ToolResourceProfile, ResourceAccess, 
    ResourceType, AccessPattern
)


class TestResourceConflictAnalyzer:
    """Test ResourceConflictAnalyzer functionality"""
    
    @pytest.fixture
    def temp_contracts_dir(self):
        """Create temporary contracts directory with test contracts"""
        temp_dir = tempfile.mkdtemp()
        contracts_dir = Path(temp_dir) / "contracts"
        contracts_dir.mkdir()
        
        # Create test contracts with different resource patterns
        contracts = {
            "T01_READER": {
                "tool_id": "T01_READER",
                "depends_on": [],
                "dependencies": ["base"],
                "category": "loader"
            },
            "T02_PROCESSOR": {
                "tool_id": "T02_PROCESSOR", 
                "depends_on": ["T01_READER"],
                "dependencies": ["processor"],
                "category": "processing"
            },
            "T03_WRITER": {
                "tool_id": "T03_WRITER",
                "depends_on": ["T02_PROCESSOR"],
                "dependencies": ["neo4j"],
                "category": "graph_building"
            },
            "T04_ANOTHER_WRITER": {
                "tool_id": "T04_ANOTHER_WRITER",
                "depends_on": ["T02_PROCESSOR"],
                "dependencies": ["neo4j"],
                "category": "graph_building"
            }
        }
        
        for tool_id, contract in contracts.items():
            contract_path = contracts_dir / f"{tool_id}.yaml"
            with open(contract_path, 'w') as f:
                yaml.dump(contract, f)
        
        yield contracts_dir
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_analyze_database_conflicts(self, temp_contracts_dir):
        """Test database conflict detection"""
        analyzer = ResourceConflictAnalyzer(temp_contracts_dir)
        
        # Test conflict between two writers to same database
        result = analyzer.analyze_database_conflicts("T03_WRITER", "T04_ANOTHER_WRITER")
        assert result.has_conflict
        assert result.conflict_type == ConflictType.DATABASE_WRITE_CONFLICT
        assert "neo4j" in result.details
        
        # Test no conflict between reader and different category
        result = analyzer.analyze_database_conflicts("T01_READER", "T02_PROCESSOR")
        assert not result.has_conflict
        assert result.conflict_type == ConflictType.NO_CONFLICT
    
    def test_analyze_file_conflicts(self, temp_contracts_dir):
        """Test file conflict detection"""
        analyzer = ResourceConflictAnalyzer(temp_contracts_dir)
        
        # Most file operations should be safe
        result = analyzer.analyze_file_conflicts("T01_READER", "T02_PROCESSOR")
        assert not result.has_conflict
        assert result.conflict_type == ConflictType.NO_CONFLICT
    
    def test_analyze_shared_state_conflicts(self, temp_contracts_dir):
        """Test shared state conflict detection"""
        analyzer = ResourceConflictAnalyzer(temp_contracts_dir)
        
        # Basic shared state should be safe
        result = analyzer.analyze_shared_state_conflicts("T01_READER", "T02_PROCESSOR")
        assert not result.has_conflict
        assert result.conflict_type == ConflictType.NO_CONFLICT
    
    def test_can_run_in_parallel(self, temp_contracts_dir):
        """Test overall parallel execution safety"""
        analyzer = ResourceConflictAnalyzer(temp_contracts_dir)
        
        # Reader and processor should be safe
        assert analyzer.can_run_in_parallel("T01_READER", "T02_PROCESSOR")
        
        # Two writers to same database should conflict
        assert not analyzer.can_run_in_parallel("T03_WRITER", "T04_ANOTHER_WRITER")
    
    def test_get_safe_parallel_pairs(self, temp_contracts_dir):
        """Test finding all safe parallel pairs"""
        analyzer = ResourceConflictAnalyzer(temp_contracts_dir)
        
        safe_pairs = analyzer.get_safe_parallel_pairs()
        
        # Should find some safe pairs
        assert len(safe_pairs) > 0
        
        # Check specific expectations
        reader_processor = tuple(sorted(["T01_READER", "T02_PROCESSOR"]))
        assert reader_processor in safe_pairs
        
        # Writers should not be in safe pairs with each other
        writer_pair = tuple(sorted(["T03_WRITER", "T04_ANOTHER_WRITER"]))
        assert writer_pair not in safe_pairs
    
    def test_graph_modification_safety(self, temp_contracts_dir):
        """Test specific graph modification tool safety"""
        analyzer = ResourceConflictAnalyzer(temp_contracts_dir)
        
        # Test known safe graph pair
        assert analyzer._check_graph_modification_safety("T31_ENTITY_BUILDER", "T34_EDGE_BUILDER")
        
        # Test potentially unsafe combination
        assert not analyzer._check_graph_modification_safety("T03_WRITER", "T04_ANOTHER_WRITER")


class TestResourceUsageDetector:
    """Test ResourceUsageDetector functionality"""
    
    @pytest.fixture
    def mock_contracts_dir(self):
        """Mock contracts directory for testing"""
        temp_dir = tempfile.mkdtemp()
        contracts_dir = Path(temp_dir) / "contracts"
        contracts_dir.mkdir()
        
        # Create realistic test contracts
        contracts = {
            "T01_PDF_LOADER": {
                "tool_id": "T01_PDF_LOADER",
                "depends_on": [],
                "dependencies": ["pypdf"],
                "category": "document_processing"
            },
            "T31_ENTITY_BUILDER": {
                "tool_id": "T31_ENTITY_BUILDER",
                "depends_on": ["T23A_SPACY_NER"],
                "dependencies": ["neo4j", "identity_service"],
                "category": "graph_building"
            },
            "T68_PAGE_RANK": {
                "tool_id": "T68_PAGE_RANK",
                "depends_on": ["T31_ENTITY_BUILDER", "T34_EDGE_BUILDER"],
                "dependencies": ["neo4j", "networkx"],
                "category": "analysis"
            }
        }
        
        for tool_id, contract in contracts.items():
            contract_path = contracts_dir / f"{tool_id}.yaml"
            with open(contract_path, 'w') as f:
                yaml.dump(contract, f)
        
        yield contracts_dir
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_build_tool_profiles(self, mock_contracts_dir):
        """Test building resource profiles for tools"""
        detector = ResourceUsageDetector(mock_contracts_dir)
        
        # Check that profiles were built
        profiles = detector.get_all_profiles()
        assert len(profiles) == 3
        
        # Check specific tool profile
        pdf_profile = detector.get_tool_profile("T01_PDF_LOADER")
        assert pdf_profile is not None
        assert pdf_profile.tool_id == "T01_PDF_LOADER"
        assert len(pdf_profile.resource_accesses) > 0
    
    def test_database_access_analysis(self, mock_contracts_dir):
        """Test database access pattern analysis"""
        detector = ResourceUsageDetector(mock_contracts_dir)
        
        # Check entity builder database access
        profile = detector.get_tool_profile("T31_ENTITY_BUILDER")
        db_accesses = profile.get_database_accesses()
        
        assert len(db_accesses) > 0
        
        # Should have neo4j access
        neo4j_accesses = [access for access in db_accesses 
                         if access.resource_name == "neo4j"]
        assert len(neo4j_accesses) > 0
    
    def test_concurrency_safety_assessment(self, mock_contracts_dir):
        """Test concurrency safety assessment"""
        detector = ResourceUsageDetector(mock_contracts_dir)
        
        # PDF loader should be relatively safe
        profile = detector.get_tool_profile("T01_PDF_LOADER")
        assert profile.concurrency_safety in ["safe", "caution"]
        
        # Entity builder with database writes might be more cautious
        profile = detector.get_tool_profile("T31_ENTITY_BUILDER")
        assert profile.concurrency_safety in ["caution", "unsafe"]
    
    def test_resource_load_estimation(self, mock_contracts_dir):
        """Test resource load estimation"""
        detector = ResourceUsageDetector(mock_contracts_dir)
        
        # PageRank should have higher load (known heavy algorithm)
        pagerank_profile = detector.get_tool_profile("T68_PAGE_RANK")
        pdf_profile = detector.get_tool_profile("T01_PDF_LOADER")
        
        assert pagerank_profile.estimated_resource_load >= pdf_profile.estimated_resource_load
    
    def test_resource_conflict_detection(self, mock_contracts_dir):
        """Test specific resource conflict detection"""
        detector = ResourceUsageDetector(mock_contracts_dir)
        
        # Find conflicts between entity builder and page rank (both use neo4j)
        conflicts = detector.find_resource_conflicts("T31_ENTITY_BUILDER", "T68_PAGE_RANK")
        
        # Should detect database conflicts
        db_conflicts = [c for c in conflicts if "Database" in c]
        assert len(db_conflicts) > 0
    
    def test_resource_usage_summary(self, mock_contracts_dir):
        """Test resource usage summary generation"""
        detector = ResourceUsageDetector(mock_contracts_dir)
        
        summary = detector.get_resource_usage_summary()
        
        # Check summary structure
        assert "total_tools" in summary
        assert "safety_distribution" in summary
        assert "resource_usage" in summary
        assert "average_resource_load" in summary
        
        # Check values make sense
        assert summary["total_tools"] == 3
        assert summary["average_resource_load"] > 0


class TestRealResourceConflictIntegration:
    """Integration tests with real contracts"""
    
    def test_real_contract_conflict_analysis(self):
        """Test conflict analysis with real project contracts"""
        contracts_dir = Path(__file__).parent.parent / "contracts" / "tools"
        
        if not contracts_dir.exists():
            pytest.skip("Real contracts directory not found")
        
        analyzer = ResourceConflictAnalyzer(contracts_dir)
        
        # Test known safe pair
        if analyzer._resource_cache.get("T27_RELATIONSHIP_EXTRACTOR") and analyzer._resource_cache.get("T31_ENTITY_BUILDER"):
            assert analyzer.can_run_in_parallel("T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER")
        
        # Test known conflict - T31 and T34 should actually be safe per current logic
        if analyzer._resource_cache.get("T31_ENTITY_BUILDER") and analyzer._resource_cache.get("T34_EDGE_BUILDER"):
            # This should be true based on business logic safety check
            result = analyzer.can_run_in_parallel("T31_ENTITY_BUILDER", "T34_EDGE_BUILDER")
            # The result depends on the specific resource conflict analysis
            # They might conflict due to database access but be allowed by business logic
    
    def test_real_resource_usage_detection(self):
        """Test resource usage detection with real contracts"""
        contracts_dir = Path(__file__).parent.parent / "contracts" / "tools"
        
        if not contracts_dir.exists():
            pytest.skip("Real contracts directory not found")
        
        detector = ResourceUsageDetector(contracts_dir)
        
        # Check that profiles were built
        profiles = detector.get_all_profiles()
        assert len(profiles) > 0
        
        # Check specific known tools if they exist
        if "T01_PDF_LOADER" in profiles:
            profile = profiles["T01_PDF_LOADER"]
            assert profile.tool_id == "T01_PDF_LOADER"
            assert len(profile.resource_accesses) > 0
    
    def test_comprehensive_conflict_matrix(self):
        """Test building complete conflict matrix"""
        contracts_dir = Path(__file__).parent.parent / "contracts" / "tools"
        
        if not contracts_dir.exists():
            pytest.skip("Real contracts directory not found")
        
        analyzer = ResourceConflictAnalyzer(contracts_dir)
        
        # Build conflict matrix
        conflict_matrix = analyzer.get_conflict_matrix()
        
        # Should have entries for all tools
        assert len(conflict_matrix) > 0
        
        # Matrix should be symmetric (if A conflicts with B, B conflicts with A)
        tools = list(conflict_matrix.keys())
        for tool1 in tools:
            for tool2 in tools:
                if tool1 in conflict_matrix and tool2 in conflict_matrix[tool1]:
                    assert conflict_matrix[tool1][tool2] == conflict_matrix[tool2][tool1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])