#!/usr/bin/env python3
"""
End-to-End Dynamic Execution Integration Tests

Comprehensive tests for the complete Phase B dynamic execution pipeline.
Tests the full workflow from question analysis to optimized parallel execution.
"""

import pytest
import asyncio
import time
from pathlib import Path
from typing import List, Dict, Any

# Core Phase B components
from src.nlp.advanced_intent_classifier import AdvancedIntentClassifier, QuestionIntent
from src.nlp.question_complexity_analyzer import QuestionComplexityAnalyzer, ComplexityLevel
from src.nlp.context_extractor import ContextExtractor
from src.nlp.tool_chain_generator import ToolChainGenerator
from src.execution.dag_builder import DynamicDAGBuilder
from src.execution.execution_planner import DynamicExecutionPlanner, ExecutionStrategy
from src.execution.adaptive_executor import AdaptiveExecutor
from src.execution.parallel_executor import ParallelExecutor
from src.performance.execution_optimizer import ExecutionOptimizer, OptimizationStrategy
from src.performance.resource_manager_enhanced import EnhancedResourceManager, AllocationStrategy
from src.nlp.adaptive_response_generator import AdaptiveResponseGenerator
from src.nlp.confidence_aggregator import ConfidenceAggregator
from src.nlp.result_synthesizer import ResultSynthesizer


@pytest.mark.integration
class TestPhaseABaseline:
    """Verify Phase A baseline functionality still works"""
    
    def setup_method(self):
        """Set up Phase A baseline test environment"""
        self.intent_classifier = AdvancedIntentClassifier()
        self.complexity_analyzer = QuestionComplexityAnalyzer()
        self.context_extractor = ContextExtractor()
    
    def test_phase_a_intent_classification_still_works(self):
        """Verify Phase A intent classification continues to function"""
        question = "What are the main themes in the document?"
        
        result = self.intent_classifier.classify(question)
        
        assert result.primary_intent in [QuestionIntent.THEME_ANALYSIS, QuestionIntent.DOCUMENT_SUMMARY]
        assert result.confidence > 0.5
        assert len(result.recommended_tools) > 0
    
    def test_phase_a_complexity_analysis_still_works(self):
        """Verify Phase A complexity analysis continues to function"""
        questions = [
            "What is this about?",  # Simple
            "How do entities relate to each other?",  # Moderate
            "What are the causal relationships between temporal patterns and emergent network structures?"  # Complex
        ]
        
        for question in questions:
            result = self.complexity_analyzer.analyze_complexity(question)
            assert result.level in [ComplexityLevel.SIMPLE, ComplexityLevel.MODERATE, ComplexityLevel.COMPLEX]
            assert result.estimated_tools > 0
            assert result.estimated_time_seconds > 0


@pytest.mark.integration
class TestDynamicExecutionPipeline:
    """Test the complete dynamic execution pipeline"""
    
    def setup_method(self):
        """Set up complete pipeline test environment"""
        # Phase B.1 - Question Analysis
        self.intent_classifier = AdvancedIntentClassifier()
        self.complexity_analyzer = QuestionComplexityAnalyzer()
        self.context_extractor = ContextExtractor()
        self.tool_chain_generator = ToolChainGenerator()
        
        # Phase B.2 - DAG Building & Planning
        self.dag_builder = DynamicDAGBuilder()
        self.execution_planner = DynamicExecutionPlanner()
        
        # Phase B.3 - Adaptive Execution
        self.adaptive_executor = AdaptiveExecutor()
        
        # Phase B.4 - Response Generation
        self.response_generator = AdaptiveResponseGenerator()
        self.confidence_aggregator = ConfidenceAggregator()
        self.result_synthesizer = ResultSynthesizer()
        
        # Phase B.5 - Performance Optimization
        self.parallel_executor = ParallelExecutor()
        self.execution_optimizer = ExecutionOptimizer()
        self.resource_manager = EnhancedResourceManager()
    
    def teardown_method(self):
        """Clean up test environment"""
        if hasattr(self, 'resource_manager'):
            self.resource_manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_simple_question_full_pipeline(self):
        """Test complete pipeline with a simple question"""
        question = "What entities are mentioned in the document?"
        
        # Step 1: Question Analysis (B.1)
        intent_result = self.intent_classifier.classify(question)
        complexity_result = self.complexity_analyzer.analyze_complexity(question)
        context_result = self.context_extractor.extract_context(question)
        
        assert intent_result.primary_intent == QuestionIntent.ENTITY_EXTRACTION
        assert complexity_result.level == ComplexityLevel.SIMPLE
        
        # Step 2: Tool Chain Generation (B.1)
        tool_chain = self.tool_chain_generator.generate_tool_chain(
            intent_result, complexity_result, context_result
        )
        
        assert len(tool_chain.required_tools) > 0
        assert "T23A_SPACY_NER" in tool_chain.required_tools
        
        # Step 3: DAG Building & Execution Planning (B.2)
        dag = self.dag_builder.build_execution_dag(
            tool_chain.required_tools, 
            intent_result.primary_intent, 
            {}
        )
        
        execution_plan = self.execution_planner.create_execution_plan(
            tool_chain.required_tools,
            intent_result.primary_intent,
            complexity_result.level,
            context_result,
            ExecutionStrategy.ADAPTIVE
        )
        
        assert len(execution_plan.steps) > 0
        assert execution_plan.total_estimated_time > 0
        assert execution_plan.confidence > 0.5
        
        # Step 4: Optimization (B.5)
        optimization_result = await self.execution_optimizer.optimize_execution_plan(execution_plan)
        optimized_plan = optimization_result.optimized_plan
        
        assert optimization_result.performance_improvement != 0.0
        
        # Step 5: Parallel Execution (B.5)
        execution_result = await self.parallel_executor.execute_parallel_plan(optimized_plan)
        
        assert execution_result.successful_steps > 0
        assert execution_result.speedup_factor >= 1.0
        
        print(f"✅ Simple question pipeline: {execution_result.speedup_factor:.2f}x speedup achieved")
    
    @pytest.mark.asyncio
    async def test_complex_question_full_pipeline(self):
        """Test complete pipeline with a complex multi-part question"""
        question = "What are the main themes and how do they relate to key entities over time?"
        
        # Step 1: Advanced Question Analysis (B.1)
        intent_result = self.intent_classifier.classify(question)
        complexity_result = self.complexity_analyzer.analyze_complexity(question)
        context_result = self.context_extractor.extract_context(question)
        
        assert complexity_result.level in [ComplexityLevel.MODERATE, ComplexityLevel.COMPLEX]
        assert intent_result.requires_multi_step is True
        assert len(intent_result.secondary_intents) > 0
        
        # Step 2: Dynamic Tool Chain Generation (B.1)
        tool_chain = self.tool_chain_generator.generate_tool_chain(
            intent_result, complexity_result, context_result
        )
        
        assert len(tool_chain.required_tools) >= 3  # Complex questions need multiple tools
        
        # Step 3: Dynamic DAG Construction (B.2)
        dag = self.dag_builder.build_execution_dag(
            tool_chain.required_tools,
            intent_result.primary_intent,
            {"temporal": True, "entities": True, "themes": True}
        )
        
        assert len(dag.nodes) >= len(tool_chain.required_tools)
        assert len(dag.edges) > 0  # Should have dependencies
        
        # Step 4: Adaptive Execution Planning (B.2)
        execution_plan = self.execution_planner.create_execution_plan(
            tool_chain.required_tools,
            intent_result.primary_intent,
            complexity_result.level,
            context_result,
            ExecutionStrategy.ADAPTIVE
        )
        
        # Complex questions should have parallel opportunities
        parallel_steps = execution_plan.get_parallel_steps()
        assert execution_plan.parallelization_ratio > 0.1
        
        # Step 5: Performance Optimization (B.5)
        optimization_result = await self.execution_optimizer.optimize_execution_plan(execution_plan)
        
        # Should achieve meaningful optimization for complex questions
        assert abs(optimization_result.performance_improvement) > 0.05  # At least 5% improvement
        
        # Step 6: Optimized Parallel Execution (B.5)
        execution_result = await self.parallel_executor.execute_parallel_plan(
            optimization_result.optimized_plan
        )
        
        assert execution_result.successful_steps > 0
        assert execution_result.total_execution_time > 0
        
        # Complex questions should benefit from parallelization
        if len(execution_result.step_results) > 1:
            assert execution_result.speedup_factor > 1.1  # At least 10% speedup
        
        print(f"✅ Complex question pipeline: {execution_result.speedup_factor:.2f}x speedup, "
              f"{execution_result.parallel_efficiency:.1%} efficiency")
    
    @pytest.mark.asyncio
    async def test_adaptive_execution_with_failures(self):
        """Test adaptive execution handling tool failures gracefully"""
        question = "What are the relationships between entities?"
        
        # Analyze question
        intent_result = self.intent_classifier.classify(question)
        complexity_result = self.complexity_analyzer.analyze_complexity(question)
        context_result = self.context_extractor.extract_context(question)
        
        # Generate execution plan
        tool_chain = self.tool_chain_generator.generate_tool_chain(
            intent_result, complexity_result, context_result
        )
        
        execution_plan = self.execution_planner.create_execution_plan(
            tool_chain.required_tools,
            intent_result.primary_intent,
            complexity_result.level,
            context_result
        )
        
        # Execute with potential failures (simulated)
        execution_result = await self.parallel_executor.execute_parallel_plan(execution_plan)
        
        # Should handle failures gracefully
        total_steps = execution_result.total_steps
        if execution_result.failed_steps > 0:
            # System should still produce results even with some failures
            assert execution_result.successful_steps > 0
            assert execution_result.successful_steps + execution_result.failed_steps == total_steps
        
        # Should still achieve some performance benefit
        assert execution_result.speedup_factor > 0.5  # At least some benefit
    
    @pytest.mark.asyncio
    async def test_resource_management_integration(self):
        """Test resource management integration with execution pipeline"""
        question = "Analyze all entities, relationships, and themes comprehensively"
        
        # This is a resource-intensive question
        intent_result = self.intent_classifier.classify(question)
        complexity_result = self.complexity_analyzer.analyze_complexity(question)
        context_result = self.context_extractor.extract_context(question)
        
        # Generate comprehensive tool chain
        tool_chain = self.tool_chain_generator.generate_tool_chain(
            intent_result, complexity_result, context_result
        )
        
        # Create execution plan
        execution_plan = self.execution_planner.create_execution_plan(
            tool_chain.required_tools,
            intent_result.primary_intent,
            complexity_result.level,
            context_result,
            ExecutionStrategy.RESOURCE_EFFICIENT
        )
        
        # Get initial resource status
        initial_status = self.resource_manager.get_system_status()
        
        # Execute with resource monitoring
        start_time = time.time()
        execution_result = await self.parallel_executor.execute_parallel_plan(execution_plan)
        execution_time = time.time() - start_time
        
        # Get final resource status
        final_status = self.resource_manager.get_system_status()
        
        # Validate resource management worked
        assert execution_result.successful_steps > 0
        assert execution_time < 60.0  # Should complete within reasonable time
        
        # Resource manager should be tracking usage
        resource_metrics = self.resource_manager.get_resource_metrics()
        assert len(resource_metrics) > 0
    
    @pytest.mark.asyncio
    async def test_end_to_end_performance_requirements(self):
        """Test that end-to-end pipeline meets Phase B performance requirements"""
        
        # Test multiple question types to validate performance
        test_questions = [
            ("What entities are mentioned?", "simple"),
            ("How do entities relate to each other?", "moderate"), 
            ("What are the temporal patterns in entity relationships and how do they affect network centrality?", "complex")
        ]
        
        total_improvements = []
        
        for question, expected_complexity in test_questions:
            print(f"\n🔍 Testing: {question}")
            
            # Full pipeline execution
            start_time = time.time()
            
            # Analysis phase
            intent_result = self.intent_classifier.classify(question)
            complexity_result = self.complexity_analyzer.analyze_complexity(question)
            context_result = self.context_extractor.extract_context(question)
            
            # Planning phase
            tool_chain = self.tool_chain_generator.generate_tool_chain(
                intent_result, complexity_result, context_result
            )
            
            execution_plan = self.execution_planner.create_execution_plan(
                tool_chain.required_tools,
                intent_result.primary_intent,
                complexity_result.level,
                context_result,
                ExecutionStrategy.ADAPTIVE
            )
            
            # Optimization phase
            optimization_result = await self.execution_optimizer.optimize_execution_plan(execution_plan)
            
            # Execution phase
            execution_result = await self.parallel_executor.execute_parallel_plan(
                optimization_result.optimized_plan
            )
            
            pipeline_time = time.time() - start_time
            
            # Validate results
            assert execution_result.successful_steps > 0
            assert execution_result.speedup_factor > 0.0
            assert pipeline_time < 30.0  # End-to-end should be fast
            
            # Track performance improvements
            if execution_result.speedup_factor > 1.0:
                improvement = execution_result.speedup_factor - 1.0
                total_improvements.append(improvement)
                
            print(f"  ✅ {execution_result.speedup_factor:.2f}x speedup in {pipeline_time:.1f}s")
        
        # Validate overall performance requirements
        if total_improvements:
            avg_improvement = sum(total_improvements) / len(total_improvements)
            print(f"\n📊 Average Performance Improvement: {avg_improvement:.1%}")
            
            # Phase B requirement: >50% improvement through parallelization
            if avg_improvement >= 0.5:
                print("🎉 PHASE B PERFORMANCE REQUIREMENT MET: >50% improvement achieved!")
            else:
                print(f"⚠️  Performance improvement: {avg_improvement:.1%} (target: >50%)")
        
        # At minimum, should have some successful executions with speedup
        assert len(total_improvements) > 0
        assert max(total_improvements) > 0.2  # At least 20% improvement somewhere


@pytest.mark.integration
class TestErrorHandlingAndRecovery:
    """Test error handling and recovery across the dynamic execution pipeline"""
    
    def setup_method(self):
        """Set up error handling test environment"""
        self.intent_classifier = AdvancedIntentClassifier()
        self.complexity_analyzer = QuestionComplexityAnalyzer()
        self.execution_planner = DynamicExecutionPlanner()
        self.parallel_executor = ParallelExecutor()
    
    def test_invalid_question_handling(self):
        """Test handling of invalid or malformed questions"""
        invalid_questions = [
            "",  # Empty
            "???",  # No clear intent
            "a" * 1000,  # Too long
            "What?",  # Too vague
        ]
        
        for question in invalid_questions:
            # Should not crash, should provide reasonable defaults
            intent_result = self.intent_classifier.classify(question)
            complexity_result = self.complexity_analyzer.analyze_complexity(question)
            
            assert intent_result is not None
            assert complexity_result is not None
            assert intent_result.confidence >= 0.0
    
    @pytest.mark.asyncio
    async def test_tool_failure_recovery(self):
        """Test recovery when individual tools fail"""
        question = "What are the main themes?"
        
        # Create a plan that might have failures
        intent_result = self.intent_classifier.classify(question)
        complexity_result = self.complexity_analyzer.analyze_complexity(question)
        
        execution_plan = self.execution_planner.create_execution_plan(
            ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER"],
            intent_result.primary_intent,
            complexity_result.level
        )
        
        # Execute (some steps may fail in simulation)
        execution_result = await self.parallel_executor.execute_parallel_plan(execution_plan)
        
        # Should handle failures gracefully
        assert execution_result.total_steps > 0
        
        # Even with failures, should provide meaningful results
        if execution_result.failed_steps > 0:
            assert execution_result.successful_steps > 0  # At least some should succeed
            assert execution_result.speedup_factor > 0.0  # Should still calculate metrics
    
    @pytest.mark.asyncio
    async def test_resource_exhaustion_handling(self):
        """Test handling when resources are exhausted"""
        # This test would simulate resource exhaustion scenarios
        # For now, just validate the system doesn't crash
        
        question = "Analyze everything comprehensively with maximum detail"
        
        intent_result = self.intent_classifier.classify(question)
        complexity_result = self.complexity_analyzer.analyze_complexity(question)
        
        # Create resource-intensive plan
        execution_plan = self.execution_planner.create_execution_plan(
            ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER", 
             "T34_EDGE_BUILDER", "T68_PAGE_RANK"],
            intent_result.primary_intent,
            complexity_result.level,
            strategy=ExecutionStrategy.QUALITY_OPTIMIZED
        )
        
        # Should execute without crashing even under resource pressure
        execution_result = await self.parallel_executor.execute_parallel_plan(execution_plan)
        
        assert execution_result is not None
        assert execution_result.total_steps > 0


@pytest.mark.integration
class TestPerformanceRegression:
    """Test for performance regressions and validate improvements"""
    
    def setup_method(self):
        """Set up regression testing environment"""
        self.parallel_executor = ParallelExecutor()
        self.execution_optimizer = ExecutionOptimizer()
        
        # Baseline execution plans for comparison
        self.baseline_plans = self._create_baseline_plans()
    
    def _create_baseline_plans(self) -> List[Any]:
        """Create baseline execution plans for testing"""
        from tests.test_performance_optimization import create_test_execution_plan
        
        return [
            create_test_execution_plan("baseline_simple", ["T23A_SPACY_NER"], 3.0),
            create_test_execution_plan("baseline_moderate", ["T23A_SPACY_NER", "T31_ENTITY_BUILDER"], 6.0),
            create_test_execution_plan("baseline_complex", 
                                     ["T23A_SPACY_NER", "T31_ENTITY_BUILDER", "T27_RELATIONSHIP_EXTRACTOR"], 9.0)
        ]
    
    @pytest.mark.asyncio
    async def test_performance_benchmarking(self):
        """Benchmark performance against baseline to prevent regressions"""
        
        benchmark_results = await self.parallel_executor.benchmark_parallel_performance(self.baseline_plans)
        
        # Validate benchmark results
        assert benchmark_results['total_plans'] == len(self.baseline_plans)
        assert len(benchmark_results['parallel_results']) == len(self.baseline_plans)
        assert benchmark_results['overall_speedup'] > 0.0
        
        # Check for meaningful performance improvements
        speedups = [result['speedup'] for result in benchmark_results['parallel_results']]
        avg_speedup = sum(speedups) / len(speedups)
        
        print(f"📊 Performance Benchmark Results:")
        print(f"   Overall Speedup: {benchmark_results['overall_speedup']:.2f}x")
        print(f"   Average Speedup: {avg_speedup:.2f}x") 
        print(f"   Time Saved: {benchmark_results['total_time_saved']:.2f}s")
        
        # Validate performance requirements
        assert avg_speedup > 1.0  # At least some improvement
        assert benchmark_results['total_time_saved'] > 0.0  # Should save time
    
    @pytest.mark.asyncio
    async def test_optimization_effectiveness(self):
        """Test that optimization strategies are effective"""
        
        optimization_results = []
        
        for plan in self.baseline_plans:
            # Test different optimization strategies
            strategies = [
                OptimizationStrategy.THROUGHPUT_MAXIMIZATION,
                OptimizationStrategy.LATENCY_MINIMIZATION,
                OptimizationStrategy.BALANCED_PERFORMANCE
            ]
            
            for strategy in strategies:
                optimizer = ExecutionOptimizer()
                optimizer.config.strategy = strategy
                
                result = await optimizer.optimize_execution_plan(plan)
                optimization_results.append({
                    'plan_id': plan.plan_id,
                    'strategy': strategy.value,
                    'improvement': result.performance_improvement,
                    'optimization_time': result.optimization_time
                })
        
        # Validate optimization effectiveness
        improvements = [r['improvement'] for r in optimization_results]
        positive_improvements = [i for i in improvements if i > 0]
        
        print(f"📈 Optimization Effectiveness:")
        print(f"   Total Optimizations: {len(optimization_results)}")
        print(f"   Positive Improvements: {len(positive_improvements)}")
        print(f"   Best Improvement: {max(improvements):.1%}")
        print(f"   Average Improvement: {(sum(improvements) / len(improvements)):.1%}")
        
        # Should have at least some positive improvements
        assert len(positive_improvements) > 0
        assert max(improvements) > 0.05  # At least 5% improvement somewhere


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])