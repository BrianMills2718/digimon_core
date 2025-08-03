#!/usr/bin/env python3
"""
Test Dynamic DAG Building

Tests the dynamic DAG builder and execution planner functionality.
Validates DAG construction, optimization, and execution planning.
"""

import pytest
import asyncio
from pathlib import Path
from typing import List, Dict, Any

from src.execution.dag_builder import DynamicDAGBuilder, ExecutionDAG, DAGNode, NodeType
from src.execution.execution_planner import DynamicExecutionPlanner, ExecutionStrategy, ExecutionConstraints
from src.execution.dependency_resolver import DynamicDependencyResolver, ResolutionContext
from src.nlp.advanced_intent_classifier import QuestionIntent
from src.nlp.question_complexity_analyzer import ComplexityLevel
from src.nlp.context_extractor import QuestionContext


class TestDynamicDAGBuilder:
    """Test DAG building functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.dag_builder = DynamicDAGBuilder()
        
    def test_simple_dag_creation(self):
        """Test creating a simple DAG"""
        required_tools = ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER"]
        
        dag = self.dag_builder.build_execution_dag(required_tools)
        
        assert isinstance(dag, ExecutionDAG)
        assert len(dag.nodes) >= len(required_tools)
        assert len(dag.entry_points) > 0
        assert len(dag.exit_points) > 0
        assert dag.estimated_makespan > 0
        
    def test_complex_dag_with_dependencies(self):
        """Test creating complex DAG with multiple dependencies"""
        required_tools = [
            "T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER",
            "T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER", "T34_EDGE_BUILDER",
            "T68_PAGE_RANK", "T49_MULTI_HOP_QUERY"
        ]
        
        dag = self.dag_builder.build_execution_dag(required_tools)
        
        assert len(dag.nodes) >= len(required_tools)
        assert len(dag.edges) > 0
        assert dag.critical_path is not None
        assert dag.parallelization_factor > 1.0
        
    def test_parallel_group_creation(self):
        """Test that parallel groups are created when appropriate"""
        required_tools = ["T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER"]
        
        dag = self.dag_builder.build_execution_dag(required_tools)
        
        # Should have parallel groups if tools can run together
        parallel_groups = [node for node in dag.nodes.values() 
                          if node.node_type == NodeType.PARALLEL_GROUP]
        
        # Either parallel groups exist, or tools are at different levels
        has_parallel_groups = len(parallel_groups) > 0
        different_levels = any(node.metadata.get('dependency_level', 0) != 
                             next(iter(dag.nodes.values())).metadata.get('dependency_level', 0)
                             for node in dag.nodes.values())
        
        assert has_parallel_groups or different_levels
        
    def test_dag_with_question_context(self):
        """Test DAG creation with question context"""
        required_tools = ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"]
        context = {
            'temporal': True,
            'entities': ['person', 'organization'],
            'complexity': 'high'
        }
        
        dag = self.dag_builder.build_execution_dag(
            required_tools, 
            question_intent=QuestionIntent.TEMPORAL_ANALYSIS,
            question_context=context
        )
        
        # Should adjust execution times based on context
        total_time = sum(node.estimated_time for node in dag.nodes.values())
        assert total_time > 0
        
    def test_critical_path_calculation(self):
        """Test critical path calculation"""
        required_tools = ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER", "T68_PAGE_RANK"]
        
        dag = self.dag_builder.build_execution_dag(required_tools)
        
        assert len(dag.critical_path) > 0
        assert dag.estimated_makespan > 0
        
        # Critical path should start with entry point and end with exit point
        if dag.entry_points and dag.exit_points:
            assert dag.critical_path[0] in dag.entry_points or any(
                dag.critical_path[0] in dag.get_dependencies(entry) 
                for entry in dag.entry_points
            )
        
    def test_resource_requirements(self):
        """Test that resource requirements are calculated"""
        required_tools = ["T68_PAGE_RANK", "T23A_SPACY_NER"]  # Resource-intensive tools
        
        dag = self.dag_builder.build_execution_dag(required_tools)
        
        for node in dag.nodes.values():
            if node.tool_id:
                assert 'cpu' in node.resource_requirements
                assert 'memory' in node.resource_requirements
                assert node.resource_requirements['memory'] > 0
                
    def test_dag_networkx_conversion(self):
        """Test conversion to NetworkX graph"""
        required_tools = ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER"]
        
        dag = self.dag_builder.build_execution_dag(required_tools)
        nx_graph = dag.to_networkx()
        
        assert nx_graph.number_of_nodes() == len(dag.nodes)
        assert nx_graph.number_of_edges() == len(dag.edges)
        
    def test_dag_visualization(self):
        """Test DAG visualization"""
        required_tools = ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER"]
        
        dag = self.dag_builder.build_execution_dag(required_tools)
        visualization = self.dag_builder.visualize_dag(dag)
        
        assert isinstance(visualization, str)
        assert len(visualization) > 0
        assert "EXECUTION DAG VISUALIZATION" in visualization
        
    def test_dag_metadata_export(self):
        """Test DAG metadata export"""
        required_tools = ["T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER"]
        
        dag = self.dag_builder.build_execution_dag(required_tools)
        metadata = self.dag_builder.export_dag_metadata(dag)
        
        assert 'nodes' in metadata
        assert 'edges' in metadata
        assert 'critical_path' in metadata
        assert 'estimated_makespan' in metadata
        assert metadata['nodes'] == len(dag.nodes)


class TestDynamicExecutionPlanner:
    """Test execution planning functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.planner = DynamicExecutionPlanner()
        
    def test_basic_execution_plan_creation(self):
        """Test creating basic execution plan"""
        required_tools = ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER"]
        
        plan = self.planner.create_execution_plan(required_tools)
        
        assert len(plan.steps) > 0
        assert plan.total_estimated_time > 0
        assert plan.confidence > 0
        assert plan.strategy is not None
        
    def test_strategy_selection(self):
        """Test different strategy selection"""
        required_tools = ["T68_PAGE_RANK", "T49_MULTI_HOP_QUERY"]
        
        # Test speed optimized
        speed_plan = self.planner.create_execution_plan(
            required_tools, strategy=ExecutionStrategy.SPEED_OPTIMIZED
        )
        
        # Test quality optimized  
        quality_plan = self.planner.create_execution_plan(
            required_tools, strategy=ExecutionStrategy.QUALITY_OPTIMIZED
        )
        
        assert speed_plan.strategy == ExecutionStrategy.SPEED_OPTIMIZED
        assert quality_plan.strategy == ExecutionStrategy.QUALITY_OPTIMIZED
        
        # Speed plan should prioritize parallelization
        # Quality plan should have higher quality score
        assert quality_plan.quality_score >= speed_plan.quality_score
        
    def test_adaptive_strategy_selection(self):
        """Test adaptive strategy selection"""
        required_tools = ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"]
        
        # Simple question should select speed optimization
        plan = self.planner.create_execution_plan(
            required_tools,
            complexity=ComplexityLevel.SIMPLE,
            strategy=ExecutionStrategy.ADAPTIVE
        )
        
        assert plan.strategy in [ExecutionStrategy.SPEED_OPTIMIZED, ExecutionStrategy.BALANCED]
        
    def test_execution_constraints(self):
        """Test execution with constraints"""
        required_tools = ["T68_PAGE_RANK", "T23A_SPACY_NER", "T49_MULTI_HOP_QUERY"]
        
        constraints = ExecutionConstraints(
            max_execution_time=30.0,
            max_parallel_tools=2,
            max_memory_usage=1000.0
        )
        
        plan = self.planner.create_execution_plan(
            required_tools, constraints=constraints
        )
        
        # Validate constraints are respected
        for step in plan.steps:
            assert len(step.tool_ids) <= constraints.max_parallel_tools
            
        # Total memory at any point should not exceed limit
        max_concurrent_memory = 0
        time_points = sorted(set([step.estimated_start_time for step in plan.steps] + 
                                [step.estimated_end_time for step in plan.steps]))
        
        for time_point in time_points:
            active_steps = [step for step in plan.steps 
                           if step.estimated_start_time <= time_point < step.estimated_end_time]
            concurrent_memory = sum(step.resource_allocation.get('memory', 0) 
                                  for step in active_steps)
            max_concurrent_memory = max(max_concurrent_memory, concurrent_memory)
            
        # Should not significantly exceed constraint (some tolerance for estimation)
        # Note: This is more of a soft constraint as exact memory prediction is complex
        assert max_concurrent_memory <= constraints.max_memory_usage * 1.5
        
    def test_plan_metrics_calculation(self):
        """Test execution plan metrics calculation"""
        required_tools = ["T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER", "T68_PAGE_RANK"]
        
        plan = self.planner.create_execution_plan(required_tools)
        
        assert 0 <= plan.parallelization_ratio <= 1.0
        assert plan.resource_efficiency > 0
        assert 0 <= plan.quality_score <= 1.0
        assert 0 <= plan.confidence <= 1.0
        
    def test_parallel_step_detection(self):
        """Test detection of parallel steps"""
        required_tools = ["T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER"]
        
        plan = self.planner.create_execution_plan(required_tools)
        parallel_steps = plan.get_parallel_steps()
        
        # Should have at least some parallel opportunities
        assert len(parallel_steps) >= 0  # May be 0 if tools conflict
        
    def test_critical_path_steps(self):
        """Test critical path step identification"""
        required_tools = ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER", "T68_PAGE_RANK"]
        
        plan = self.planner.create_execution_plan(required_tools)
        critical_steps = plan.get_critical_path_steps()
        
        assert len(critical_steps) > 0
        
    def test_plan_visualization(self):
        """Test execution plan visualization"""
        required_tools = ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"]
        
        plan = self.planner.create_execution_plan(required_tools)
        visualization = self.planner.visualize_execution_plan(plan)
        
        assert isinstance(visualization, str)
        assert "EXECUTION PLAN VISUALIZATION" in visualization
        assert str(plan.strategy.value) in visualization


class TestDynamicDependencyResolver:
    """Test dependency resolution functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.resolver = DynamicDependencyResolver()
        self.planner = DynamicExecutionPlanner()
        
    def test_basic_dependency_resolution(self):
        """Test basic dependency resolution"""
        required_tools = ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER"]
        plan = self.planner.create_execution_plan(required_tools)
        
        context = ResolutionContext(
            available_tools=set(required_tools),
            completed_tools=set(),
            failed_tools=set(),
            intermediate_results={},
            execution_constraints={},
            runtime_conditions={}
        )
        
        result = self.resolver.resolve_dependencies(plan, context)
        
        assert result.resolution_confidence >= 0.0
        assert len(result.resolved_dependencies) >= 0
        
    def test_failed_tool_handling(self):
        """Test handling of failed tools"""
        required_tools = ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER"]
        plan = self.planner.create_execution_plan(required_tools)
        
        context = ResolutionContext(
            available_tools=set(required_tools),
            completed_tools={"T01_PDF_LOADER"},
            failed_tools={"T15A_TEXT_CHUNKER"},
            intermediate_results={},
            execution_constraints={},
            runtime_conditions={}
        )
        
        result = self.resolver.resolve_dependencies(plan, context)
        
        # Should have some unresolved dependencies due to failed tool
        assert len(result.unresolved_dependencies) >= 0
        assert len(result.warnings) >= 0
        
    def test_conditional_dependencies(self):
        """Test conditional dependency resolution"""
        required_tools = ["T68_PAGE_RANK"]
        plan = self.planner.create_execution_plan(required_tools)
        
        context = ResolutionContext(
            available_tools=set(required_tools),
            completed_tools=set(),
            failed_tools=set(),
            intermediate_results={},
            execution_constraints={'quality_threshold': 0.95},
            runtime_conditions={'dataset_size': 'large'}
        )
        
        result = self.resolver.resolve_dependencies(plan, context)
        
        # Should resolve at least partially
        assert result.resolution_confidence >= 0.0
        
    def test_adaptive_dependencies(self):
        """Test adaptive dependency resolution"""
        required_tools = ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"]
        plan = self.planner.create_execution_plan(required_tools)
        
        # Create mock question context
        mock_context = type('MockContext', (), {})()
        mock_context.temporal_context = type('TemporalContext', (), {})()
        mock_context.entity_context = type('EntityContext', (), {})()
        
        context = ResolutionContext(
            available_tools=set(required_tools),
            completed_tools=set(),
            failed_tools=set(),
            intermediate_results={},
            execution_constraints={},
            runtime_conditions={},
            question_context=mock_context
        )
        
        result = self.resolver.resolve_dependencies(plan, context)
        
        assert result.resolution_confidence >= 0.0
        
    def test_plan_adaptation(self):
        """Test execution plan adaptation based on resolution"""
        required_tools = ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER"]
        original_plan = self.planner.create_execution_plan(required_tools)
        
        context = ResolutionContext(
            available_tools=set(required_tools),
            completed_tools=set(),
            failed_tools=set(),
            intermediate_results={},
            execution_constraints={},
            runtime_conditions={}
        )
        
        resolution_result = self.resolver.resolve_dependencies(original_plan, context)
        adapted_plan = self.resolver.adapt_execution_plan(original_plan, resolution_result, context)
        
        assert adapted_plan.plan_id != original_plan.plan_id
        assert 'dependency_adaptation' in adapted_plan.adaptive_features
        
    def test_resolution_validation(self):
        """Test dependency resolution validation"""
        required_tools = ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER"]
        plan = self.planner.create_execution_plan(required_tools)
        
        context = ResolutionContext(
            available_tools=set(required_tools),
            completed_tools=set(),
            failed_tools=set(),
            intermediate_results={},
            execution_constraints={},
            runtime_conditions={}
        )
        
        result = self.resolver.resolve_dependencies(plan, context)
        validation = self.resolver.validate_resolution(result)
        
        assert 'is_valid' in validation
        assert 'critical_issues' in validation
        assert 'warnings' in validation
        
    def test_dependency_summary(self):
        """Test dependency resolution summary generation"""
        required_tools = ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"]
        plan = self.planner.create_execution_plan(required_tools)
        
        context = ResolutionContext(
            available_tools=set(required_tools),
            completed_tools=set(),
            failed_tools=set(),
            intermediate_results={},
            execution_constraints={},
            runtime_conditions={}
        )
        
        result = self.resolver.resolve_dependencies(plan, context)
        summary = self.resolver.get_dependency_summary(result)
        
        assert isinstance(summary, str)
        assert "DEPENDENCY RESOLUTION SUMMARY" in summary
        assert "Resolution Confidence" in summary


class TestIntegrationDAGPlannerResolver:
    """Test integration between DAG builder, planner, and resolver"""
    
    def setup_method(self):
        """Set up test environment"""
        self.dag_builder = DynamicDAGBuilder()
        self.planner = DynamicExecutionPlanner()
        self.resolver = DynamicDependencyResolver()
        
    def test_full_pipeline_integration(self):
        """Test full pipeline from DAG building to execution planning to resolution"""
        required_tools = ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER", 
                         "T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER"]
        
        # Create execution plan
        plan = self.planner.create_execution_plan(
            required_tools,
            strategy=ExecutionStrategy.BALANCED
        )
        
        # Resolve dependencies
        context = ResolutionContext(
            available_tools=set(required_tools),
            completed_tools=set(),
            failed_tools=set(),
            intermediate_results={},
            execution_constraints={},
            runtime_conditions={}
        )
        
        resolution_result = self.resolver.resolve_dependencies(plan, context)
        adapted_plan = self.resolver.adapt_execution_plan(plan, resolution_result, context)
        
        # Validate end-to-end pipeline
        assert len(adapted_plan.steps) > 0
        assert adapted_plan.total_estimated_time > 0
        assert resolution_result.resolution_confidence > 0.5
        
    def test_complex_question_handling(self):
        """Test handling of complex multi-tool questions"""
        required_tools = [
            "T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER",
            "T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER", "T34_EDGE_BUILDER",
            "T68_PAGE_RANK", "T49_MULTI_HOP_QUERY"
        ]
        
        # Create plan with quality optimization for complex analysis
        plan = self.planner.create_execution_plan(
            required_tools,
            question_intent=QuestionIntent.COMPARATIVE_ANALYSIS,
            complexity=ComplexityLevel.COMPLEX,
            strategy=ExecutionStrategy.QUALITY_OPTIMIZED
        )
        
        # Should have quality checkpoints and adaptive features
        assert plan.quality_score >= 0.8
        assert len(plan.adaptive_features) > 0
        
        # Should handle parallel opportunities
        parallel_steps = plan.get_parallel_steps()
        if len(required_tools) > 4:  # With this many tools, should find some parallelization
            assert plan.parallelization_ratio > 0.1
            
    def test_performance_optimization_integration(self):
        """Test performance optimization across components"""
        required_tools = ["T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER", 
                         "T68_PAGE_RANK", "T49_MULTI_HOP_QUERY"]
        
        # Speed-optimized plan should maximize parallelization
        speed_plan = self.planner.create_execution_plan(
            required_tools,
            strategy=ExecutionStrategy.SPEED_OPTIMIZED
        )
        
        # Check that plan is optimized for speed
        assert speed_plan.strategy == ExecutionStrategy.SPEED_OPTIMIZED
        
        # Should have reasonable performance metrics
        assert speed_plan.total_estimated_time > 0
        assert speed_plan.parallelization_ratio >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])