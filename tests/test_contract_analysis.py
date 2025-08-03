"""
Test Contract Analysis

Tests for ToolContractAnalyzer and DependencyGraphBuilder functionality.
Ensures programmatic dependency analysis works correctly.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.analysis.contract_analyzer import ToolContractAnalyzer, ResourceUsage, DependencyGraph
from src.analysis.dependency_graph_builder import DependencyGraphBuilder, ExecutionPlan


class TestToolContractAnalyzer:
    """Test ToolContractAnalyzer functionality"""
    
    @pytest.fixture
    def temp_contracts_dir(self):
        """Create temporary contracts directory with test contracts"""
        temp_dir = tempfile.mkdtemp()
        contracts_dir = Path(temp_dir) / "contracts"
        contracts_dir.mkdir()
        
        # Create test contracts
        contracts = {
            "T01_TEST": {
                "tool_id": "T01_TEST",
                "depends_on": [],
                "dependencies": ["base"],
                "category": "loader"
            },
            "T02_TEST": {
                "tool_id": "T02_TEST", 
                "depends_on": ["T01_TEST"],
                "dependencies": ["processor"],
                "category": "processing"
            },
            "T03_TEST": {
                "tool_id": "T03_TEST",
                "depends_on": ["T01_TEST", "T02_TEST"],
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
    
    def test_extract_dependencies(self, temp_contracts_dir):
        """Test dependency extraction from contracts"""
        analyzer = ToolContractAnalyzer(temp_contracts_dir)
        
        # Test T01 - no dependencies
        deps = analyzer.extract_dependencies(str(temp_contracts_dir / "T01_TEST.yaml"))
        assert deps == []
        
        # Test T02 - depends on T01
        deps = analyzer.extract_dependencies(str(temp_contracts_dir / "T02_TEST.yaml"))
        assert deps == ["T01_TEST"]
        
        # Test T03 - depends on T01 and T02
        deps = analyzer.extract_dependencies(str(temp_contracts_dir / "T03_TEST.yaml"))
        assert set(deps) == {"T01_TEST", "T02_TEST"}
    
    def test_extract_resources(self, temp_contracts_dir):
        """Test resource extraction from contracts"""
        analyzer = ToolContractAnalyzer(temp_contracts_dir)
        
        # Test T01 - loader category
        resources = analyzer.extract_resources(str(temp_contracts_dir / "T01_TEST.yaml"))
        assert 'read_input' in resources.file_access
        assert 'read_file' in resources.file_access
        assert 'write_output' in resources.file_access
        
        # Test T03 - neo4j dependency
        resources = analyzer.extract_resources(str(temp_contracts_dir / "T03_TEST.yaml"))
        assert 'read_neo4j' in resources.database_access
        assert 'write_neo4j' in resources.database_access
    
    def test_build_dependency_graph(self, temp_contracts_dir):
        """Test building complete dependency graph"""
        analyzer = ToolContractAnalyzer(temp_contracts_dir)
        
        graph = analyzer.build_dependency_graph()
        
        # Check nodes
        expected_nodes = {"T01_TEST", "T02_TEST", "T03_TEST"}
        assert graph.nodes == expected_nodes
        
        # Check edges
        assert graph.edges["T01_TEST"] == set()
        assert graph.edges["T02_TEST"] == {"T01_TEST"}
        assert graph.edges["T03_TEST"] == {"T01_TEST", "T02_TEST"}
        
        # Check levels
        assert graph.levels["T01_TEST"] == 0
        assert graph.levels["T02_TEST"] == 1
        assert graph.levels["T03_TEST"] == 2
        
        # Check topological order
        t01_pos = graph.topological_order.index("T01_TEST")
        t02_pos = graph.topological_order.index("T02_TEST")
        t03_pos = graph.topological_order.index("T03_TEST")
        
        assert t01_pos < t02_pos < t03_pos
    
    def test_circular_dependency_detection(self, temp_contracts_dir):
        """Test detection of circular dependencies"""
        # Create circular dependency
        circular_contract = {
            "tool_id": "T04_TEST",
            "depends_on": ["T02_TEST"],
            "dependencies": []
        }
        
        contract_path = temp_contracts_dir / "T04_TEST.yaml"
        with open(contract_path, 'w') as f:
            yaml.dump(circular_contract, f)
        
        # Modify T02 to depend on T04, creating cycle
        t02_path = temp_contracts_dir / "T02_TEST.yaml"
        with open(t02_path, 'r') as f:
            t02_contract = yaml.safe_load(f)
        
        t02_contract["depends_on"] = ["T01_TEST", "T04_TEST"]
        
        with open(t02_path, 'w') as f:
            yaml.dump(t02_contract, f)
        
        analyzer = ToolContractAnalyzer(temp_contracts_dir)
        
        # Should raise ValueError for circular dependency
        with pytest.raises(ValueError, match="Circular dependency detected"):
            analyzer.build_dependency_graph()
    
    def test_validate_contract(self, temp_contracts_dir):
        """Test contract validation"""
        analyzer = ToolContractAnalyzer(temp_contracts_dir)
        
        # Valid contract
        assert analyzer.validate_contract(str(temp_contracts_dir / "T01_TEST.yaml"))
        
        # Create invalid contract - missing depends_on
        invalid_contract = {
            "tool_id": "INVALID_TEST",
            "dependencies": []
        }
        
        invalid_path = temp_contracts_dir / "INVALID_TEST.yaml"
        with open(invalid_path, 'w') as f:
            yaml.dump(invalid_contract, f)
        
        assert not analyzer.validate_contract(str(invalid_path))


class TestDependencyGraphBuilder:
    """Test DependencyGraphBuilder functionality"""
    
    @pytest.fixture
    def mock_contracts_dir(self):
        """Mock contracts directory for testing"""
        temp_dir = tempfile.mkdtemp()
        contracts_dir = Path(temp_dir) / "contracts"
        contracts_dir.mkdir()
        
        # Create realistic test contracts matching actual tool structure
        contracts = {
            "T01_PDF_LOADER": {
                "tool_id": "T01_PDF_LOADER",
                "depends_on": [],
                "dependencies": ["pypdf"],
                "category": "document_processing"
            },
            "T15A_TEXT_CHUNKER": {
                "tool_id": "T15A_TEXT_CHUNKER",
                "depends_on": ["T01_PDF_LOADER"],
                "dependencies": [],
                "category": "processing"
            },
            "T23A_SPACY_NER": {
                "tool_id": "T23A_SPACY_NER",
                "depends_on": ["T15A_TEXT_CHUNKER"],
                "dependencies": ["spacy"],
                "category": "entity_extraction"
            },
            "T31_ENTITY_BUILDER": {
                "tool_id": "T31_ENTITY_BUILDER",
                "depends_on": ["T23A_SPACY_NER"],
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
    
    def test_build_execution_graph(self, mock_contracts_dir):
        """Test building execution graph for specific tools"""
        builder = DependencyGraphBuilder(mock_contracts_dir)
        
        required_tools = ["T31_ENTITY_BUILDER"]
        graph = builder.build_execution_graph(required_tools)
        
        # Should include all dependencies
        expected_nodes = {"T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER", "T31_ENTITY_BUILDER"}
        assert graph.nodes == expected_nodes
        
        # Check dependency levels
        assert graph.levels["T01_PDF_LOADER"] == 0
        assert graph.levels["T15A_TEXT_CHUNKER"] == 1
        assert graph.levels["T23A_SPACY_NER"] == 2
        assert graph.levels["T31_ENTITY_BUILDER"] == 3
    
    def test_create_execution_plan(self, mock_contracts_dir):
        """Test creating complete execution plan"""
        builder = DependencyGraphBuilder(mock_contracts_dir)
        
        required_tools = ["T31_ENTITY_BUILDER"]
        plan = builder.create_execution_plan(required_tools)
        
        # Check plan structure
        assert len(plan.levels) == 4  # 4 dependency levels
        assert plan.total_tools == 4
        assert plan.parallelization_opportunities == 0  # Linear chain
        
        # Check each level has correct tools
        assert plan.get_tools_at_level(0) == ["T01_PDF_LOADER"]
        assert plan.get_tools_at_level(1) == ["T15A_TEXT_CHUNKER"]
        assert plan.get_tools_at_level(2) == ["T23A_SPACY_NER"]
        assert plan.get_tools_at_level(3) == ["T31_ENTITY_BUILDER"]
    
    def test_validate_execution_plan(self, mock_contracts_dir):
        """Test execution plan validation"""
        builder = DependencyGraphBuilder(mock_contracts_dir)
        
        required_tools = ["T31_ENTITY_BUILDER"]
        plan = builder.create_execution_plan(required_tools)
        
        # Should validate successfully
        assert builder.validate_execution_plan(plan)
    
    def test_multiple_parallel_tools(self, mock_contracts_dir):
        """Test execution plan with parallel opportunities"""
        # Add parallel tools at same level
        parallel_contracts = {
            "T32_PARALLEL_TOOL": {
                "tool_id": "T32_PARALLEL_TOOL",
                "depends_on": ["T23A_SPACY_NER"],
                "dependencies": [],
                "category": "processing"
            },
            "T33_ANOTHER_PARALLEL": {
                "tool_id": "T33_ANOTHER_PARALLEL", 
                "depends_on": ["T23A_SPACY_NER"],
                "dependencies": [],
                "category": "processing"
            }
        }
        
        for tool_id, contract in parallel_contracts.items():
            contract_path = mock_contracts_dir / f"{tool_id}.yaml"
            with open(contract_path, 'w') as f:
                yaml.dump(contract, f)
        
        builder = DependencyGraphBuilder(mock_contracts_dir)
        
        required_tools = ["T31_ENTITY_BUILDER", "T32_PARALLEL_TOOL", "T33_ANOTHER_PARALLEL"]
        plan = builder.create_execution_plan(required_tools)
        
        # Should detect parallelization opportunity
        level_3_tools = plan.get_tools_at_level(3)
        assert len(level_3_tools) == 3  # All three tools at same level
        assert plan.parallelization_opportunities > 0


class TestRealContractIntegration:
    """Integration tests with real contract files"""
    
    def test_analyze_real_contracts(self):
        """Test analysis of actual project contracts"""
        # Use real contracts directory
        contracts_dir = Path(__file__).parent.parent / "contracts" / "tools"
        
        if not contracts_dir.exists():
            pytest.skip("Real contracts directory not found")
        
        analyzer = ToolContractAnalyzer(contracts_dir)
        
        # Test with real contracts
        graph = analyzer.build_dependency_graph()
        
        # Basic sanity checks
        assert len(graph.nodes) > 0
        assert len(graph.levels) > 0
        
        # Check specific known dependencies
        if "T15A_TEXT_CHUNKER" in graph.edges:
            assert "T01_PDF_LOADER" in graph.edges["T15A_TEXT_CHUNKER"]
        
        if "T23A_SPACY_NER" in graph.edges:
            assert "T15A_TEXT_CHUNKER" in graph.edges["T23A_SPACY_NER"]
    
    def test_build_execution_plan_real_tools(self):
        """Test execution plan with real tools"""
        contracts_dir = Path(__file__).parent.parent / "contracts" / "tools"
        
        if not contracts_dir.exists():
            pytest.skip("Real contracts directory not found")
        
        builder = DependencyGraphBuilder(contracts_dir)
        
        # Test with realistic tool set
        required_tools = ["T31_ENTITY_BUILDER", "T34_EDGE_BUILDER"]
        plan = builder.create_execution_plan(required_tools)
        
        # Should build valid plan
        assert len(plan.levels) > 0
        assert plan.total_tools > 0
        assert builder.validate_execution_plan(plan)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])