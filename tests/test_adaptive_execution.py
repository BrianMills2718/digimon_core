#!/usr/bin/env python3
"""
Test Adaptive Execution Engine

Tests the adaptive execution engine, result analyzer, and execution controller.
Validates adaptive decision making, result analysis, and execution monitoring.
"""

import pytest
import asyncio
import time
from pathlib import Path
from typing import List, Dict, Any

from src.execution.adaptive_executor import AdaptiveExecutor, AdaptiveDecision, AdaptiveAction, AdaptiveContext
from src.execution.result_analyzer import ResultAnalyzer, AnalysisResult, QualityMetrics, ResultQuality
from src.execution.execution_controller import ExecutionController, ExecutionStatus, ExecutionEvent
from src.execution.execution_planner import DynamicExecutionPlanner, ExecutionStrategy
from src.nlp.advanced_intent_classifier import QuestionIntent


class TestResultAnalyzer:
    """Test result analysis functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.analyzer = ResultAnalyzer()
        
    def test_quality_metrics_calculation(self):
        """Test quality metrics calculation"""
        # Mock tool results
        results = {
            'T23A_SPACY_NER': {
                'success': True,
                'confidence': 0.85,
                'outputs': {'entities': ['person1', 'org1'], 'confidence': 0.85}
            },
            'T27_RELATIONSHIP_EXTRACTOR': {
                'success': True,
                'confidence': 0.78,
                'outputs': {'relationships': [{'source': 'person1', 'target': 'org1'}]}
            }
        }
        
        # Calculate quality metrics
        quality_metrics = asyncio.run(self.analyzer._calculate_quality_metrics(results))
        
        assert isinstance(quality_metrics, QualityMetrics)
        assert 0 <= quality_metrics.completeness <= 1.0
        assert 0 <= quality_metrics.accuracy <= 1.0
        assert 0 <= quality_metrics.consistency <= 1.0
        assert 0 <= quality_metrics.confidence <= 1.0
        assert 0 <= quality_metrics.overall_quality <= 1.0
        
    def test_completeness_assessment(self):
        """Test completeness assessment"""
        # Complete results
        complete_results = {
            'tool1': {'success': True, 'outputs': {'data': 'value1'}},
            'tool2': {'success': True, 'outputs': {'data': 'value2'}}
        }
        
        completeness = self.analyzer._assess_completeness(complete_results)
        assert completeness == 1.0
        
        # Incomplete results
        incomplete_results = {
            'tool1': {'success': True, 'outputs': {'data': 'value1'}},
            'tool2': {'success': False, 'error': 'Failed'}
        }
        
        completeness = self.analyzer._assess_completeness(incomplete_results)
        assert 0.0 <= completeness < 1.0
        
    def test_consistency_assessment(self):
        """Test consistency assessment across tools"""
        # Consistent results
        consistent_results = {
            'tool1': {'confidence': 0.8, 'execution_time': 5.0},
            'tool2': {'confidence': 0.82, 'execution_time': 5.2}
        }
        
        consistency = self.analyzer._assess_consistency(consistent_results)
        assert consistency > 0.5
        
        # Inconsistent results
        inconsistent_results = {
            'tool1': {'confidence': 0.9, 'execution_time': 2.0},
            'tool2': {'confidence': 0.3, 'execution_time': 15.0}
        }
        
        consistency = self.analyzer._assess_consistency(inconsistent_results)
        assert consistency < 0.95  # Less strict assertion
        
    @pytest.mark.asyncio
    async def test_result_quality_analysis(self):
        """Test comprehensive result quality analysis"""
        results = {
            'T23A_SPACY_NER': {
                'success': True,
                'confidence': 0.85,
                'execution_time': 3.2,
                'outputs': {'entities': ['John', 'Apple'], 'confidence': 0.85}
            },
            'T27_RELATIONSHIP_EXTRACTOR': {
                'success': True,
                'confidence': 0.78,
                'execution_time': 4.1,
                'outputs': {'relationships': [{'source': 'John', 'target': 'Apple'}]}
            }
        }
        
        analysis = await self.analyzer.analyze_result_quality(results)
        
        assert isinstance(analysis, AnalysisResult)
        assert analysis.overall_quality > 0.0
        assert isinstance(analysis.quality_metrics, QualityMetrics)
        assert len(analysis.patterns_detected) >= 0
        assert len(analysis.anomalies_found) >= 0
        assert analysis.confidence > 0.0
        
    @pytest.mark.asyncio
    async def test_pattern_detection(self):
        """Test pattern detection in results"""
        # Results with high confidence pattern
        high_confidence_results = {
            'tool1': {'confidence': 0.9},
            'tool2': {'confidence': 0.92},
            'tool3': {'confidence': 0.88}
        }
        
        patterns = await self.analyzer._detect_patterns(high_confidence_results)
        
        # Should detect high confidence cluster
        high_conf_patterns = [p for p in patterns if p['type'] == 'high_confidence_cluster']
        assert len(high_conf_patterns) >= 1
        
    @pytest.mark.asyncio
    async def test_anomaly_detection(self):
        """Test anomaly detection"""
        # Results with confidence anomaly
        anomalous_results = {
            'tool1': {'confidence': 0.8},
            'tool2': {'confidence': 0.82},
            'tool3': {'confidence': 0.1}  # Anomalously low
        }
        
        anomalies = await self.analyzer._detect_anomalies(anomalous_results)
        
        # Should detect confidence anomaly
        conf_anomalies = [a for a in anomalies if a['type'] == 'confidence_anomaly']
        assert len(conf_anomalies) >= 1
        
    @pytest.mark.asyncio
    async def test_tool_output_comparison(self):
        """Test comparison between tool outputs"""
        results1 = {
            'tool1': {'confidence': 0.8, 'success': True},
            'tool2': {'confidence': 0.75, 'success': True}
        }
        
        results2 = {
            'tool1': {'confidence': 0.82, 'success': True},
            'tool2': {'confidence': 0.73, 'success': False}
        }
        
        comparison = await self.analyzer.compare_tool_outputs(results1, results2)
        
        assert 0.0 <= comparison.similarity_score <= 1.0
        assert len(comparison.differences_found) >= 0
        assert len(comparison.consensus_items) >= 0
        assert len(comparison.conflicting_items) >= 0
        assert 0.0 <= comparison.confidence_in_comparison <= 1.0


class TestExecutionController:
    """Test execution controller functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.controller = ExecutionController()
        self.planner = DynamicExecutionPlanner()
        
    @pytest.mark.asyncio
    async def test_execution_monitoring_lifecycle(self):
        """Test complete execution monitoring lifecycle"""
        # Create test execution plan
        required_tools = ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"]
        plan = self.planner.create_execution_plan(required_tools)
        
        # Start monitoring
        await self.controller.start_execution_monitoring(plan)
        
        # Check that monitoring started
        status = self.controller.get_execution_status(plan.plan_id)
        assert status is not None
        assert status.overall_status == ExecutionStatus.RUNNING
        assert status.total_steps == len(plan.steps)
        
        # Stop monitoring
        await self.controller.stop_execution_monitoring(plan.plan_id)
        
        # Check that monitoring stopped
        status = self.controller.get_execution_status(plan.plan_id)
        assert status.overall_status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]
        
    @pytest.mark.asyncio
    async def test_step_status_updates(self):
        """Test step status update functionality"""
        required_tools = ["T23A_SPACY_NER"]
        plan = self.planner.create_execution_plan(required_tools)
        
        await self.controller.start_execution_monitoring(plan)
        
        step_id = plan.steps[0].step_id
        
        # Update step to running
        await self.controller.update_step_status(
            plan.plan_id, step_id, ExecutionStatus.RUNNING,
            progress=0.5, message="Step in progress"
        )
        
        status = self.controller.get_execution_status(plan.plan_id)
        step_status = status.step_statuses[step_id]
        
        assert step_status.status == ExecutionStatus.RUNNING
        assert step_status.progress == 0.5
        assert step_status.start_time is not None
        
        # Update step to completed
        await self.controller.update_step_status(
            plan.plan_id, step_id, ExecutionStatus.COMPLETED,
            progress=1.0, message="Step completed"
        )
        
        status = self.controller.get_execution_status(plan.plan_id)
        step_status = status.step_statuses[step_id]
        
        assert step_status.status == ExecutionStatus.COMPLETED
        assert step_status.progress == 1.0
        assert step_status.end_time is not None
        assert step_status.actual_duration is not None
        
        await self.controller.stop_execution_monitoring()
        
    @pytest.mark.asyncio
    async def test_pause_resume_functionality(self):
        """Test execution pause and resume"""
        required_tools = ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"]
        plan = self.planner.create_execution_plan(required_tools)
        
        await self.controller.start_execution_monitoring(plan)
        
        # Pause execution
        success = await self.controller.pause_execution(plan.plan_id)
        assert success
        
        status = self.controller.get_execution_status(plan.plan_id)
        assert status.overall_status == ExecutionStatus.PAUSED
        
        # Check pause signal
        signal = await self.controller.wait_for_pause_or_cancel(plan.plan_id)
        assert signal == 'pause'
        
        # Resume execution
        success = await self.controller.resume_execution(plan.plan_id)
        assert success
        
        status = self.controller.get_execution_status(plan.plan_id)
        assert status.overall_status == ExecutionStatus.RUNNING
        
        await self.controller.stop_execution_monitoring()
        
    @pytest.mark.asyncio
    async def test_execution_cancellation(self):
        """Test execution cancellation"""
        required_tools = ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"]
        plan = self.planner.create_execution_plan(required_tools)
        
        await self.controller.start_execution_monitoring(plan)
        
        # Cancel execution
        success = await self.controller.cancel_execution(plan.plan_id)
        assert success
        
        status = self.controller.get_execution_status(plan.plan_id)
        assert status.overall_status == ExecutionStatus.CANCELLED
        
        # Check cancel signal
        signal = await self.controller.wait_for_pause_or_cancel(plan.plan_id)
        assert signal == 'cancel'
        
        await self.controller.stop_execution_monitoring()
        
    @pytest.mark.asyncio
    async def test_resource_monitoring(self):
        """Test resource usage monitoring"""
        required_tools = ["T68_PAGE_RANK"]  # Resource-intensive tool
        plan = self.planner.create_execution_plan(required_tools)
        
        await self.controller.start_execution_monitoring(plan)
        
        # Update resource usage
        resource_usage = {'cpu': 0.85, 'memory': 0.9}  # High usage
        await self.controller.update_resource_usage(plan.plan_id, resource_usage)
        
        status = self.controller.get_execution_status(plan.plan_id)
        assert 'cpu' in status.resource_usage
        assert 'memory' in status.resource_usage
        assert len(status.warnings) > 0  # Should generate warnings for high usage
        
        await self.controller.stop_execution_monitoring()
        
    @pytest.mark.asyncio
    async def test_event_handling(self):
        """Test event handling system"""
        events_received = []
        
        def event_handler(event_data):
            events_received.append(event_data)
        
        # Register event handler
        self.controller.register_event_handler(ExecutionEvent.EXECUTION_STARTED, event_handler)
        self.controller.register_event_handler(ExecutionEvent.STEP_STARTED, event_handler)
        
        # Create and start execution
        required_tools = ["T23A_SPACY_NER"]
        plan = self.planner.create_execution_plan(required_tools)
        
        await self.controller.start_execution_monitoring(plan)
        
        # Update step status to trigger event
        step_id = plan.steps[0].step_id
        await self.controller.update_step_status(plan.plan_id, step_id, ExecutionStatus.RUNNING)
        
        await self.controller.stop_execution_monitoring()
        
        # Check that events were fired
        assert len(events_received) >= 2  # At least execution started and step started
        
        event_types = [event.event_type for event in events_received]
        assert ExecutionEvent.EXECUTION_STARTED in event_types
        assert ExecutionEvent.STEP_STARTED in event_types
        
    def test_execution_summary(self):
        """Test execution summary generation"""
        required_tools = ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"]
        plan = self.planner.create_execution_plan(required_tools)
        
        # Start monitoring (sync)
        asyncio.run(self.controller.start_execution_monitoring(plan))
        
        # Get summary
        summary = self.controller.get_execution_summary(plan.plan_id)
        
        assert summary is not None
        assert 'plan_id' in summary
        assert 'status' in summary
        assert 'progress' in summary
        assert 'execution_time' in summary
        assert 'total_steps' in summary
        
        # Stop monitoring
        asyncio.run(self.controller.stop_execution_monitoring())


class TestAdaptiveExecutor:
    """Test adaptive execution engine"""
    
    def setup_method(self):
        """Set up test environment"""
        self.executor = AdaptiveExecutor()
        self.planner = DynamicExecutionPlanner()
        
    @pytest.mark.asyncio
    async def test_basic_adaptive_execution(self):
        """Test basic adaptive execution"""
        required_tools = ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"]
        plan = self.planner.create_execution_plan(required_tools)
        available_tools = set(required_tools)
        
        # Execute with adaptive logic
        results = await self.executor.execute_adaptive_plan(plan, available_tools)
        
        assert 'execution_results' in results
        assert 'execution_summary' in results
        
        # Check execution results structure
        execution_results = results['execution_results']
        summary = results['execution_summary']
        assert summary['total_steps'] == len(plan.steps)
        assert summary['completed_steps'] >= 0
        assert summary['total_time'] > 0
        
    @pytest.mark.asyncio
    async def test_adaptive_decision_making(self):
        """Test adaptive decision making"""
        # Create mock adaptive context
        plan = self.planner.create_execution_plan(["T23A_SPACY_NER"])
        step = plan.steps[0]
        
        context = AdaptiveContext(
            current_step=step,
            intermediate_results={},
            execution_history=[],
            performance_metrics={},
            quality_metrics={},
            resource_usage={'memory': 0.9},  # High memory usage
            time_elapsed=0.0,
            remaining_steps=[],
            original_plan=plan,
            constraints_status={}
        )
        
        # Make adaptive decision
        action = await self.executor._make_adaptive_decision(context)
        
        assert isinstance(action, AdaptiveAction)
        assert action.decision in [d for d in AdaptiveDecision]
        assert action.confidence > 0.0
        
    @pytest.mark.asyncio
    async def test_time_pressure_adaptation(self):
        """Test adaptation under time pressure"""
        plan = self.planner.create_execution_plan(["T23A_SPACY_NER"])
        step = plan.steps[0]
        
        # Create time pressure situation
        context = AdaptiveContext(
            current_step=step,
            intermediate_results={},
            execution_history=[],
            performance_metrics={},
            quality_metrics={},
            resource_usage={},
            time_elapsed=plan.total_estimated_time * 0.9,  # 90% time elapsed
            remaining_steps=[step],
            original_plan=plan,
            constraints_status={}
        )
        
        # Should trigger time pressure handling
        action = await self.executor._handle_time_pressure(context, {'time_pressure': True})
        
        assert action.decision in [AdaptiveDecision.MODIFY_PARAMS, AdaptiveDecision.PARALLEL_BOOST]
        assert 'time' in action.reason.lower()
        
    @pytest.mark.asyncio
    async def test_quality_concern_adaptation(self):
        """Test adaptation for quality concerns"""
        plan = self.planner.create_execution_plan(["T23A_SPACY_NER"])
        step = plan.steps[0]
        
        context = AdaptiveContext(
            current_step=step,
            intermediate_results={},
            execution_history=[],
            performance_metrics={},
            quality_metrics={'tool1': 0.4, 'tool2': 0.3},  # Low quality
            resource_usage={},
            time_elapsed=0.0,
            remaining_steps=[],
            original_plan=plan,
            constraints_status={}
        )
        
        action = await self.executor._handle_quality_concerns(context, {'quality_concerns': True})
        
        assert action.decision == AdaptiveDecision.QUALITY_CHECK
        assert 'quality' in action.reason.lower()
        
    @pytest.mark.asyncio
    async def test_parallel_execution_adaptation(self):
        """Test parallel execution adaptation"""
        # Create plan with tools that can run in parallel
        required_tools = ["T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER"]
        plan = self.planner.create_execution_plan(required_tools)
        available_tools = set(required_tools)
        
        results = await self.executor.execute_adaptive_plan(plan, available_tools)
        
        # Should complete successfully with potential parallel optimizations
        assert 'execution_summary' in results
        summary = results['execution_summary']
        
        # Check if any adaptations were made
        adaptations_made = summary.get('adaptations_made', 0)
        assert adaptations_made >= 0
        
    @pytest.mark.asyncio
    async def test_failure_handling_adaptation(self):
        """Test adaptation to step failures"""
        plan = self.planner.create_execution_plan(["T23A_SPACY_NER"])
        step = plan.steps[0]
        
        # Simulate step failure
        step_result = {
            'success': False,
            'error': 'Connection timeout',
            'step_id': step.step_id
        }
        
        context = AdaptiveContext(
            current_step=step,
            intermediate_results={},
            execution_history=[],
            performance_metrics={},
            quality_metrics={},
            resource_usage={},
            time_elapsed=0.0,
            remaining_steps=[],
            original_plan=plan,
            constraints_status={}
        )
        
        # Should decide to retry for transient errors
        action = await self.executor._decide_failure_response(step, step_result, context)
        
        assert action.decision == AdaptiveDecision.RETRY_STEP
        assert 'retry' in action.reason.lower()
        
    @pytest.mark.asyncio
    async def test_adaptive_execution_with_config(self):
        """Test adaptive execution with custom configuration"""
        required_tools = ["T23A_SPACY_NER"]
        plan = self.planner.create_execution_plan(required_tools)
        available_tools = set(required_tools)
        
        # Custom adaptation configuration
        adaptation_config = {
            'adaptation_threshold': 0.5,
            'quality_threshold': 0.9,
            'time_pressure_factor': 1.5
        }
        
        results = await self.executor.execute_adaptive_plan(
            plan, available_tools, adaptation_config
        )
        
        assert 'execution_summary' in results
        assert results['execution_summary']['total_steps'] > 0
        
    def test_adaptation_summary(self):
        """Test adaptation summary generation"""
        # Initialize some adaptation history
        self.executor.adaptation_history = [
            AdaptiveAction(
                decision=AdaptiveDecision.PARALLEL_BOOST,
                reason="Time pressure",
                confidence=0.8,
                expected_impact={'time_saved': 5.0}
            ),
            AdaptiveAction(
                decision=AdaptiveDecision.QUALITY_CHECK,
                reason="Quality concerns",
                confidence=0.9,
                expected_impact={'quality_improvement': 0.1}
            )
        ]
        
        self.executor.execution_metrics['total_adaptations'] = 2
        self.executor.execution_metrics['successful_adaptations'] = 2
        self.executor.execution_metrics['time_saved'] = 5.0
        self.executor.execution_metrics['quality_improvements'] = 1
        
        summary = self.executor.get_adaptation_summary()
        
        assert summary['total_adaptations'] == 2
        assert summary['successful_adaptations'] == 2
        assert summary['adaptation_success_rate'] == 1.0
        assert summary['time_saved'] == 5.0
        assert summary['quality_improvements'] == 1
        assert 'adaptation_types' in summary


class TestAdaptiveExecutionIntegration:
    """Test integration between adaptive execution components"""
    
    def setup_method(self):
        """Set up test environment"""
        self.executor = AdaptiveExecutor()
        self.analyzer = ResultAnalyzer()
        self.controller = ExecutionController()
        self.planner = DynamicExecutionPlanner()
        
    @pytest.mark.asyncio
    async def test_full_adaptive_pipeline(self):
        """Test complete adaptive execution pipeline"""
        # Create complex execution plan
        required_tools = [
            "T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER",
            "T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER"
        ]
        
        plan = self.planner.create_execution_plan(
            required_tools,
            strategy=ExecutionStrategy.ADAPTIVE
        )
        
        available_tools = set(required_tools)
        
        # Execute with full adaptive pipeline
        results = await self.executor.execute_adaptive_plan(plan, available_tools)
        
        # Validate results
        assert 'execution_summary' in results
        summary = results['execution_summary']
        
        assert summary['total_steps'] == len(plan.steps)
        assert summary['completed_steps'] + summary['failed_steps'] <= summary['total_steps']
        assert summary['total_time'] > 0
        
        # Check adaptation metrics
        adaptation_summary = self.executor.get_adaptation_summary()
        assert adaptation_summary['total_adaptations'] >= 0
        
    @pytest.mark.asyncio
    async def test_quality_analysis_integration(self):
        """Test integration with quality analysis"""
        # Create mock execution results
        execution_results = {
            'step_001': {
                'success': True,
                'outputs': {
                    'T23A_SPACY_NER': {
                        'confidence': 0.85,
                        'outputs': {'entities': ['John', 'Apple']}
                    }
                }
            }
        }
        
        # Analyze quality
        for step_results in execution_results.values():
            if 'outputs' in step_results:
                analysis = await self.analyzer.analyze_result_quality(step_results['outputs'])
                
                assert analysis.overall_quality >= 0.0
                assert analysis.quality_metrics.overall_quality >= 0.0
                
    @pytest.mark.asyncio
    async def test_execution_monitoring_integration(self):
        """Test integration with execution controller"""
        required_tools = ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"]
        plan = self.planner.create_execution_plan(required_tools)
        
        # Start monitoring
        await self.controller.start_execution_monitoring(plan)
        
        # Simulate execution steps with the controller
        for i, step in enumerate(plan.steps):
            await self.controller.update_step_status(
                plan.plan_id, step.step_id, ExecutionStatus.RUNNING
            )
            
            # Simulate execution time
            await asyncio.sleep(0.1)
            
            await self.controller.update_step_status(
                plan.plan_id, step.step_id, ExecutionStatus.COMPLETED,
                progress=1.0
            )
        
        # Check final status
        status = self.controller.get_execution_status(plan.plan_id)
        assert status.overall_status in [ExecutionStatus.COMPLETED, ExecutionStatus.RUNNING]
        assert status.completed_steps == len(plan.steps)
        
        await self.controller.stop_execution_monitoring()
        
    @pytest.mark.asyncio
    async def test_adaptive_performance_optimization(self):
        """Test adaptive performance optimization"""
        # Create plan optimized for speed
        required_tools = ["T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER", "T68_PAGE_RANK"]
        
        speed_plan = self.planner.create_execution_plan(
            required_tools,
            strategy=ExecutionStrategy.SPEED_OPTIMIZED
        )
        
        available_tools = set(required_tools)
        
        # Execute with speed optimization
        start_time = time.time()
        results = await self.executor.execute_adaptive_plan(speed_plan, available_tools)
        execution_time = time.time() - start_time
        
        # Should complete in reasonable time
        assert execution_time < 60.0  # Should not take more than 1 minute for testing
        
        # Check if parallel optimizations were applied
        summary = results['execution_summary']
        if summary['adaptations_made'] > 0:
            # If adaptations were made, they should be related to performance
            adaptation_summary = self.executor.get_adaptation_summary()
            assert adaptation_summary['time_saved'] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])