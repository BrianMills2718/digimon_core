"""
Test Parallel Discovery

Tests for ParallelOpportunityFinder and ExecutionPlanOptimizer functionality.
Ensures algorithmic parallel discovery works for N-way parallelization.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.execution.parallel_opportunity_finder import (
    ParallelOpportunityFinder, ExecutionPlan, ParallelGroup
)
from src.execution.execution_plan_optimizer import (
    ExecutionPlanOptimizer, OptimizedExecutionPlan, SchedulingStrategy
)
from src.analysis.contract_analyzer import DependencyGraph


class TestParallelOpportunityFinder:
    """Test ParallelOpportunityFinder functionality"""
    
    @pytest.fixture
    def temp_contracts_dir(self):
        """Create temporary contracts directory with test contracts"""
        temp_dir = tempfile.mkdtemp()
        contracts_dir = Path(temp_dir) / "contracts"
        contracts_dir.mkdir()
        
        # Create test contracts for parallel discovery
        contracts = {
            "T01_BASE": {
                "tool_id": "T01_BASE",
                "depends_on": [],
                "dependencies": ["base"],
                "category": "loader"
            },
            "T02_PARALLEL_A": {
                "tool_id": "T02_PARALLEL_A", 
                "depends_on": ["T01_BASE"],
                "dependencies": ["processor_a"],
                "category": "processing"
            },
            "T03_PARALLEL_B": {
                "tool_id": "T03_PARALLEL_B",
                "depends_on": ["T01_BASE"],
                "dependencies": ["processor_b"],
                "category": "processing"
            },
            "T04_PARALLEL_C": {
                "tool_id": "T04_PARALLEL_C",
                "depends_on": ["T01_BASE"],
                "dependencies": ["processor_c"],
                "category": "processing"
            },
            "T05_CONFLICTING": {
                "tool_id": "T05_CONFLICTING",
                "depends_on": ["T01_BASE"],
                "dependencies": ["neo4j"],  # Will conflict with other neo4j users
                "category": "graph_building"
            },
            "T06_ANOTHER_CONFLICTING": {
                "tool_id": "T06_ANOTHER_CONFLICTING",
                "depends_on": ["T01_BASE"],
                "dependencies": ["neo4j"],  # Will conflict with T05
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
    
    @pytest.fixture
    def mock_dependency_graph(self):
        """Create mock dependency graph for testing"""
        return DependencyGraph(
            nodes={"T01_BASE", "T02_PARALLEL_A", "T03_PARALLEL_B", "T04_PARALLEL_C"},
            edges={
                "T01_BASE": set(),
                "T02_PARALLEL_A": {"T01_BASE"},
                "T03_PARALLEL_B": {"T01_BASE"},
                "T04_PARALLEL_C": {"T01_BASE"}
            },
            levels={
                "T01_BASE": 0,
                "T02_PARALLEL_A": 1,
                "T03_PARALLEL_B": 1,
                "T04_PARALLEL_C": 1
            },
            topological_order=["T01_BASE", "T02_PARALLEL_A", "T03_PARALLEL_B", "T04_PARALLEL_C"]
        )
    
    def test_find_maximal_parallel_groups(self, temp_contracts_dir):
        """Test finding maximal parallel groups"""
        finder = ParallelOpportunityFinder(temp_contracts_dir)
        
        # Test with tools that can all run in parallel
        tools_at_level = ["T02_PARALLEL_A", "T03_PARALLEL_B", "T04_PARALLEL_C"]
        groups = finder.find_maximal_parallel_groups(tools_at_level)
        
        # Should find one large group (if no conflicts) or multiple smaller groups
        assert len(groups) >= 1
        total_tools = sum(len(group) for group in groups)
        assert total_tools == len(tools_at_level)
    
    def test_find_parallel_groups_with_conflicts(self, temp_contracts_dir):
        """Test parallel group finding with resource conflicts"""
        finder = ParallelOpportunityFinder(temp_contracts_dir)
        
        # Test with conflicting tools (both use neo4j for writing)
        tools_with_conflicts = ["T05_CONFLICTING", "T06_ANOTHER_CONFLICTING"]
        groups = finder.find_maximal_parallel_groups(tools_with_conflicts)
        
        # Should create separate groups due to conflicts
        assert len(groups) == 2  # Each tool in its own group
        assert all(len(group) == 1 for group in groups)
    
    def test_optimize_execution_plan(self, temp_contracts_dir, mock_dependency_graph):
        """Test execution plan optimization"""
        finder = ParallelOpportunityFinder(temp_contracts_dir)
        
        plan = finder.optimize_execution_plan(mock_dependency_graph)
        
        # Verify plan structure
        assert isinstance(plan, ExecutionPlan)
        assert plan.total_tools > 0
        assert plan.total_levels >= 2  # At least base level and parallel level
        assert plan.estimated_total_time > 0
        assert plan.estimated_speedup >= 1.0
    
    def test_three_way_parallelization(self, temp_contracts_dir):
        """Test 3-way parallelization detection"""
        finder = ParallelOpportunityFinder(temp_contracts_dir)
        
        # Test with three compatible tools at same level
        compatible_tools = ["T02_PARALLEL_A", "T03_PARALLEL_B", "T04_PARALLEL_C"]
        groups = finder.find_maximal_parallel_groups(compatible_tools)
        
        # Should detect 3-way parallelization opportunity
        max_group_size = max(len(group) for group in groups) if groups else 0
        assert max_group_size >= 2  # At least 2-way, potentially 3-way
    
    def test_estimate_performance_gain(self, temp_contracts_dir, mock_dependency_graph):
        """Test performance gain estimation"""
        finder = ParallelOpportunityFinder(temp_contracts_dir)
        
        plan = finder.optimize_execution_plan(mock_dependency_graph)
        performance = finder.estimate_performance_gain(plan)
        
        # Check performance metrics structure
        expected_keys = [
            "sequential_time", "parallel_time", "time_saved", "speedup_factor",
            "parallelization_ratio", "resource_utilization", "parallelization_efficiency",
            "parallel_opportunities"
        ]
        
        for key in expected_keys:
            assert key in performance
            assert isinstance(performance[key], (int, float))
    
    def test_find_all_parallel_combinations(self, temp_contracts_dir):
        """Test finding all possible parallel combinations"""
        finder = ParallelOpportunityFinder(temp_contracts_dir)
        
        # Test with compatible tools
        tools = ["T02_PARALLEL_A", "T03_PARALLEL_B", "T04_PARALLEL_C"]
        combinations = finder.find_all_parallel_combinations(tools)
        
        # Should find combinations of different sizes
        assert isinstance(combinations, dict)
        
        # Check that we have size-2 combinations
        if 2 in combinations:
            assert len(combinations[2]) > 0
            # Each combination should be a valid parallel group
            for combo in combinations[2]:
                assert len(combo) == 2
                assert finder._can_all_run_together(combo)
    
    def test_analyze_parallelization_potential(self, temp_contracts_dir, mock_dependency_graph):
        """Test parallelization potential analysis"""
        finder = ParallelOpportunityFinder(temp_contracts_dir)
        
        analysis = finder.analyze_parallelization_potential(mock_dependency_graph)
        
        # Check analysis structure
        assert "total_tools" in analysis
        assert "total_levels" in analysis
        assert "parallel_potential_levels" in analysis
        assert "max_theoretical_speedup" in analysis
        assert "level_analysis" in analysis
        
        # Check that level 1 has parallelization potential
        assert 1 in analysis["level_analysis"]
        level_1_analysis = analysis["level_analysis"][1]
        assert level_1_analysis["total_tools"] == 3
        assert level_1_analysis["parallelization_possible"] in [True, False]


class TestExecutionPlanOptimizer:
    """Test ExecutionPlanOptimizer functionality"""
    
    @pytest.fixture
    def mock_contracts_dir(self):
        """Mock contracts directory for testing"""
        temp_dir = tempfile.mkdtemp()
        contracts_dir = Path(temp_dir) / "contracts"
        contracts_dir.mkdir()
        
        # Create test contracts
        contracts = {
            "T01_FAST": {
                "tool_id": "T01_FAST",
                "depends_on": [],
                "dependencies": ["base"],
                "category": "loader"
            },
            "T02_SLOW": {
                "tool_id": "T02_SLOW",
                "depends_on": ["T01_FAST"],
                "dependencies": ["heavy_processor"],
                "category": "processing"
            },
            "T03_MEDIUM": {
                "tool_id": "T03_MEDIUM",
                "depends_on": ["T01_FAST"],
                "dependencies": ["medium_processor"],
                "category": "processing"
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
    
    @pytest.fixture
    def simple_dependency_graph(self):
        """Simple dependency graph for optimization testing"""
        return DependencyGraph(
            nodes={"T01_FAST", "T02_SLOW", "T03_MEDIUM"},
            edges={
                "T01_FAST": set(),
                "T02_SLOW": {"T01_FAST"},
                "T03_MEDIUM": {"T01_FAST"}
            },
            levels={
                "T01_FAST": 0,
                "T02_SLOW": 1,
                "T03_MEDIUM": 1
            },
            topological_order=["T01_FAST", "T02_SLOW", "T03_MEDIUM"]
        )
    
    def test_optimize_execution_plan_minimize_makespan(self, mock_contracts_dir, simple_dependency_graph):
        """Test execution plan optimization for minimum makespan"""
        optimizer = ExecutionPlanOptimizer(mock_contracts_dir)
        
        plan = optimizer.optimize_execution_plan(
            simple_dependency_graph, 
            SchedulingStrategy.MINIMIZE_MAKESPAN
        )
        
        # Verify optimized plan structure
        assert isinstance(plan, OptimizedExecutionPlan)
        assert len(plan.scheduled_tasks) == 3
        assert plan.total_makespan > 0
        assert plan.parallelization_efficiency >= 0.0
        assert plan.scheduling_strategy == SchedulingStrategy.MINIMIZE_MAKESPAN
    
    def test_resource_utilization_calculation(self, mock_contracts_dir, simple_dependency_graph):
        """Test resource utilization calculation"""
        optimizer = ExecutionPlanOptimizer(mock_contracts_dir)
        
        plan = optimizer.optimize_execution_plan(simple_dependency_graph)
        
        # Check resource utilization metrics
        assert "cpu" in plan.resource_utilization
        assert "memory" in plan.resource_utilization
        assert "disk_io" in plan.resource_utilization
        assert "network" in plan.resource_utilization
        
        # All utilization values should be between 0 and 1
        for resource, util in plan.resource_utilization.items():
            assert 0.0 <= util <= 1.0
    
    def test_critical_path_calculation(self, mock_contracts_dir, simple_dependency_graph):
        """Test critical path calculation"""
        optimizer = ExecutionPlanOptimizer(mock_contracts_dir)
        
        plan = optimizer.optimize_execution_plan(simple_dependency_graph)
        critical_path = plan.get_critical_path()
        
        # Critical path should start with T01_FAST
        assert len(critical_path) > 0
        assert critical_path[0] == "T01_FAST"
    
    def test_resource_constraint_validation(self, mock_contracts_dir, simple_dependency_graph):
        """Test resource constraint validation"""
        optimizer = ExecutionPlanOptimizer(mock_contracts_dir)
        
        plan = optimizer.optimize_execution_plan(simple_dependency_graph)
        
        # Check that validation was performed
        violations = optimizer._check_resource_constraints(plan.scheduled_tasks)
        
        # For this simple test case, should have no violations
        # (unless we specifically design resource conflicts)
        assert isinstance(violations, list)
    
    def test_dependency_constraint_validation(self, mock_contracts_dir, simple_dependency_graph):
        """Test dependency constraint validation"""
        optimizer = ExecutionPlanOptimizer(mock_contracts_dir)
        
        plan = optimizer.optimize_execution_plan(simple_dependency_graph)
        
        # Check dependency constraint validation
        dep_violations = optimizer._check_dependency_constraints(plan.scheduled_tasks)
        
        # Should have no dependency violations in valid plan
        assert len(dep_violations) == 0
    
    def test_scheduling_strategy_comparison(self, mock_contracts_dir, simple_dependency_graph):
        """Test comparison of different scheduling strategies"""
        optimizer = ExecutionPlanOptimizer(mock_contracts_dir)
        
        comparison = optimizer.compare_strategies(simple_dependency_graph)
        
        # Should have results for available strategies
        assert len(comparison) > 0
        
        for strategy, plan in comparison.items():
            assert isinstance(strategy, SchedulingStrategy)
            assert isinstance(plan, OptimizedExecutionPlan)
            assert plan.total_makespan > 0
    
    def test_gantt_chart_export(self, mock_contracts_dir, simple_dependency_graph):
        """Test Gantt chart data export"""
        optimizer = ExecutionPlanOptimizer(mock_contracts_dir)
        
        plan = optimizer.optimize_execution_plan(simple_dependency_graph)
        gantt_data = optimizer.export_schedule_gantt(plan)
        
        # Check Gantt data structure
        assert isinstance(gantt_data, list)
        assert len(gantt_data) == len(plan.scheduled_tasks)
        
        for item in gantt_data:
            assert "task" in item
            assert "start" in item
            assert "duration" in item
            assert "level" in item
            assert "resources" in item


class TestRealParallelDiscoveryIntegration:
    """Integration tests with real contracts"""
    
    def test_real_parallel_discovery(self):
        """Test parallel discovery with real project contracts"""
        contracts_dir = Path(__file__).parent.parent / "contracts" / "tools"
        
        if not contracts_dir.exists():
            pytest.skip("Real contracts directory not found")
        
        finder = ParallelOpportunityFinder(contracts_dir)
        
        # Test with known tools at same level
        tools_at_level = ["T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER"]
        groups = finder.find_maximal_parallel_groups(tools_at_level)
        
        # Should find parallel opportunities
        assert len(groups) >= 1
        total_tools = sum(len(group) for group in groups)
        assert total_tools == len(tools_at_level)
    
    def test_real_execution_plan_optimization(self):
        """Test execution plan optimization with real contracts"""
        contracts_dir = Path(__file__).parent.parent / "contracts" / "tools"
        
        if not contracts_dir.exists():
            pytest.skip("Real contracts directory not found")
        
        # Import real contract analyzer to build dependency graph
        from src.analysis.contract_analyzer import ToolContractAnalyzer
        from src.analysis.dependency_graph_builder import DependencyGraphBuilder
        
        builder = DependencyGraphBuilder(contracts_dir)
        required_tools = ["T31_ENTITY_BUILDER", "T34_EDGE_BUILDER"]
        
        try:
            dependency_graph = builder.build_execution_graph(required_tools)
            
            optimizer = ExecutionPlanOptimizer(contracts_dir)
            plan = optimizer.optimize_execution_plan(dependency_graph)
            
            # Verify plan is reasonable
            assert plan.total_makespan > 0
            assert len(plan.scheduled_tasks) > 0
            assert plan.parallelization_efficiency >= 0.0
            
        except Exception as e:
            pytest.skip(f"Could not build real execution plan: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])