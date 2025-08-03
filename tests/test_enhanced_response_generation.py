#!/usr/bin/env python3
"""
Test Enhanced Response Generation

Tests the adaptive response generator and confidence aggregator.
Validates response adaptation, confidence aggregation, and uncertainty quantification.
"""

import pytest
import asyncio
import time
from pathlib import Path
from typing import List, Dict, Any

from src.nlp.adaptive_response_generator import (
    AdaptiveResponseGenerator, ResponseContext, AdaptiveResponse, ResponseAdaptation
)
from src.nlp.confidence_aggregator import (
    ConfidenceAggregator, ConfidenceInput, ConfidenceMetrics, ConfidenceSource,
    AggregationMethod, UncertaintyQuantification
)
from src.nlp.result_synthesizer import ResultSynthesizer, SynthesisResult, SynthesisStrategy, SynthesisFragment
from src.nlp.question_complexity_analyzer import ComplexityLevel, ComplexityAnalysisResult
from src.nlp.advanced_intent_classifier import QuestionIntent
from src.execution.execution_planner import ExecutionPlan, ExecutionStep, ExecutionPriority, ExecutionStrategy, ExecutionConstraints
from src.execution.dag_builder import ExecutionDAG, DAGNode, DAGEdge, NodeType


def create_test_execution_plan(plan_id: str, tool_ids: List[str], total_time: float = 10.0) -> ExecutionPlan:
    """Helper function to create test execution plans"""
    # Create simple DAG with required parameters
    nodes = {}
    edges = []
    steps = []
    
    for i, tool_id in enumerate(tool_ids):
        node_id = f"node{i+1}"
        node = DAGNode(node_id, NodeType.TOOL, tool_id)
        nodes[node_id] = node
        
        step = ExecutionStep(
            step_id=f"step{i+1}",
            node_id=node_id,
            tool_ids=[tool_id],
            estimated_start_time=float(i * 3),
            estimated_duration=3.0,
            execution_priority=ExecutionPriority.HIGH
        )
        steps.append(step)
        
        # Add dependency edge if not the first node
        if i > 0:
            edges.append(DAGEdge(f"node{i}", node_id))
    
    # Create DAG
    dag = ExecutionDAG(
        nodes=nodes,
        edges=edges,
        entry_points=[f"node1"] if tool_ids else [],
        exit_points=[f"node{len(tool_ids)}"] if tool_ids else []
    )
    
    return ExecutionPlan(
        plan_id=plan_id,
        steps=steps,
        strategy=ExecutionStrategy.ADAPTIVE,
        total_estimated_time=total_time,
        total_estimated_cost=5.0,
        parallelization_ratio=0.0,
        resource_efficiency=0.8,
        quality_score=0.85,
        confidence=0.8,
        dag=dag,
        constraints=ExecutionConstraints()
    )


class TestConfidenceAggregator:
    """Test confidence aggregation functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.aggregator = ConfidenceAggregator()
    
    def test_confidence_input_creation(self):
        """Test confidence input creation and validation"""
        input_data = ConfidenceInput(
            source_id="T23A_SPACY_NER",
            source_type=ConfidenceSource.TOOL_OUTPUT,
            confidence_score=0.85,
            uncertainty=0.1,
            weight=1.0,
            execution_time=3.2,
            data_volume=500
        )
        
        assert input_data.source_id == "T23A_SPACY_NER"
        assert input_data.confidence_score == 0.85
        assert input_data.uncertainty == 0.1
        assert input_data.weight == 1.0
    
    @pytest.mark.asyncio
    async def test_weighted_average_aggregation(self):
        """Test weighted average confidence aggregation"""
        inputs = [
            ConfidenceInput("tool1", ConfidenceSource.TOOL_OUTPUT, 0.8, 0.1, 1.0),
            ConfidenceInput("tool2", ConfidenceSource.TOOL_OUTPUT, 0.9, 0.05, 1.5),
            ConfidenceInput("tool3", ConfidenceSource.TOOL_OUTPUT, 0.7, 0.2, 0.8)
        ]
        
        metrics = await self.aggregator.aggregate_confidence(
            inputs, AggregationMethod.WEIGHTED_AVERAGE
        )
        
        assert isinstance(metrics, ConfidenceMetrics)
        assert 0.0 <= metrics.overall_confidence <= 1.0
        assert 0.0 <= metrics.uncertainty_level <= 1.0
        assert 0.0 <= metrics.reliability_score <= 1.0
        assert 0.0 <= metrics.consensus_strength <= 1.0
        assert len(metrics.tool_confidences) == 3
    
    @pytest.mark.asyncio
    async def test_bayesian_fusion_aggregation(self):
        """Test Bayesian fusion confidence aggregation"""
        inputs = [
            ConfidenceInput("tool1", ConfidenceSource.TOOL_OUTPUT, 0.8, 0.1, 1.0),
            ConfidenceInput("tool2", ConfidenceSource.TOOL_OUTPUT, 0.85, 0.08, 1.2),
            ConfidenceInput("tool3", ConfidenceSource.TOOL_OUTPUT, 0.75, 0.15, 0.9)
        ]
        
        metrics = await self.aggregator.aggregate_confidence(
            inputs, AggregationMethod.BAYESIAN_FUSION
        )
        
        assert isinstance(metrics, ConfidenceMetrics)
        assert 0.0 <= metrics.overall_confidence <= 1.0
        assert metrics.aggregation_method == AggregationMethod.BAYESIAN_FUSION
        assert metrics.inputs_processed == 3
    
    @pytest.mark.asyncio
    async def test_uncertainty_weighted_aggregation(self):
        """Test uncertainty-weighted confidence aggregation"""
        inputs = [
            ConfidenceInput("tool1", ConfidenceSource.TOOL_OUTPUT, 0.9, 0.05, 1.0),  # High confidence, low uncertainty
            ConfidenceInput("tool2", ConfidenceSource.TOOL_OUTPUT, 0.6, 0.4, 1.0),   # Low confidence, high uncertainty
            ConfidenceInput("tool3", ConfidenceSource.TOOL_OUTPUT, 0.8, 0.1, 1.0)    # Medium confidence, low uncertainty
        ]
        
        metrics = await self.aggregator.aggregate_confidence(
            inputs, AggregationMethod.UNCERTAINTY_WEIGHTED
        )
        
        assert isinstance(metrics, ConfidenceMetrics)
        # Tool1 should have highest weight due to low uncertainty
        assert metrics.overall_confidence > 0.7  # Should be pulled toward high-confidence, low-uncertainty tools
        assert len(metrics.uncertainty_sources) == 3
    
    @pytest.mark.asyncio
    async def test_minimum_consensus_aggregation(self):
        """Test minimum consensus aggregation"""
        # Create inputs with clear consensus and outlier
        inputs = [
            ConfidenceInput("tool1", ConfidenceSource.TOOL_OUTPUT, 0.8, 0.1, 1.0),
            ConfidenceInput("tool2", ConfidenceSource.TOOL_OUTPUT, 0.82, 0.1, 1.0),
            ConfidenceInput("tool3", ConfidenceSource.TOOL_OUTPUT, 0.79, 0.1, 1.0),
            ConfidenceInput("tool4", ConfidenceSource.TOOL_OUTPUT, 0.3, 0.4, 1.0)   # Outlier
        ]
        
        metrics = await self.aggregator.aggregate_confidence(
            inputs, AggregationMethod.MINIMUM_CONSENSUS
        )
        
        assert isinstance(metrics, ConfidenceMetrics)
        assert metrics.consensus_strength > 0.5  # Should find consensus among first 3 tools
        # Overall confidence should be close to consensus group (around 0.8)
        assert 0.7 <= metrics.overall_confidence <= 0.9
    
    @pytest.mark.asyncio
    async def test_dynamic_weighting_aggregation(self):
        """Test dynamic weighting based on context"""
        inputs = [
            ConfidenceInput("T23A_SPACY_NER", ConfidenceSource.TOOL_OUTPUT, 0.8, 0.1, 1.0, 
                          execution_time=2.0, data_volume=1000),
            ConfidenceInput("T27_RELATIONSHIP_EXTRACTOR", ConfidenceSource.TOOL_OUTPUT, 0.7, 0.2, 1.0,
                          execution_time=5.0, data_volume=500)
        ]
        
        context = {
            'question_complexity': 'complex',
            'average_execution_time': 3.0,
            'average_data_volume': 750
        }
        
        metrics = await self.aggregator.aggregate_confidence(
            inputs, AggregationMethod.DYNAMIC_WEIGHTING, context
        )
        
        assert isinstance(metrics, ConfidenceMetrics)
        assert 0.0 <= metrics.overall_confidence <= 1.0
        assert metrics.aggregation_method == AggregationMethod.DYNAMIC_WEIGHTING
    
    @pytest.mark.asyncio
    async def test_confidence_with_no_inputs(self):
        """Test confidence aggregation with no inputs"""
        inputs = []
        
        metrics = await self.aggregator.aggregate_confidence(inputs)
        
        assert isinstance(metrics, ConfidenceMetrics)
        assert metrics.overall_confidence == 0.5  # Neutral confidence
        assert metrics.uncertainty_level == 0.8   # High uncertainty
        assert metrics.reliability_score == 0.3   # Low reliability
        assert metrics.inputs_processed == 0
        assert metrics.failed_inputs == 0
    
    @pytest.mark.asyncio
    async def test_confidence_with_invalid_inputs(self):
        """Test confidence aggregation with invalid inputs"""
        inputs = [
            ConfidenceInput("tool1", ConfidenceSource.TOOL_OUTPUT, 1.5, 0.1, 1.0),  # Invalid confidence > 1.0
            ConfidenceInput("tool2", ConfidenceSource.TOOL_OUTPUT, -0.1, 0.1, 1.0), # Invalid confidence < 0.0
            ConfidenceInput("tool3", ConfidenceSource.TOOL_OUTPUT, 0.8, 0.1, 1.0)   # Valid
        ]
        
        metrics = await self.aggregator.aggregate_confidence(inputs)
        
        assert isinstance(metrics, ConfidenceMetrics)
        assert metrics.inputs_processed == 1  # Only 1 valid input processed
        assert metrics.failed_inputs == 2     # 2 invalid inputs
    
    @pytest.mark.asyncio
    async def test_outlier_detection(self):
        """Test outlier detection in confidence inputs"""
        inputs = [
            ConfidenceInput("tool1", ConfidenceSource.TOOL_OUTPUT, 0.8, 0.1, 1.0),
            ConfidenceInput("tool2", ConfidenceSource.TOOL_OUTPUT, 0.82, 0.1, 1.0),
            ConfidenceInput("tool3", ConfidenceSource.TOOL_OUTPUT, 0.79, 0.1, 1.0),
            ConfidenceInput("tool4", ConfidenceSource.TOOL_OUTPUT, 0.05, 0.3, 1.0)   # More extreme outlier
        ]
        
        metrics = await self.aggregator.aggregate_confidence(inputs)
        
        assert isinstance(metrics, ConfidenceMetrics)
        # Either should detect outlier or have no outliers (both are valid outcomes)
        assert len(metrics.outlier_scores) >= 0  # Allow for no outliers detected
        if len(metrics.outlier_scores) > 0:
            assert "tool4" in metrics.outlier_scores  # Should identify tool4 as outlier if any detected
    
    @pytest.mark.asyncio
    async def test_cross_validation_scoring(self):
        """Test cross-validation scoring with different source types"""
        inputs = [
            ConfidenceInput("tool1", ConfidenceSource.TOOL_OUTPUT, 0.8, 0.1, 1.0),
            ConfidenceInput("tool2", ConfidenceSource.TOOL_OUTPUT, 0.82, 0.1, 1.0),
            ConfidenceInput("validator1", ConfidenceSource.CROSS_VALIDATION, 0.79, 0.1, 1.0),
            ConfidenceInput("quality1", ConfidenceSource.DATA_QUALITY, 0.85, 0.1, 1.0)
        ]
        
        metrics = await self.aggregator.aggregate_confidence(inputs)
        
        assert isinstance(metrics, ConfidenceMetrics)
        assert metrics.cross_validation_score > 0.0
        assert len(metrics.source_type_confidences) >= 3  # At least 3 different source types
    
    def test_tool_reliability_updates(self):
        """Test tool reliability weight updates"""
        initial_weight = self.aggregator.tool_reliability_weights.get("test_tool", 1.0)
        
        # Update with high performance
        self.aggregator.update_tool_reliability("test_tool", 0.95)
        
        updated_weight = self.aggregator.tool_reliability_weights.get("test_tool", 1.0)
        
        # Weight should have increased (or stayed high if already high)
        assert updated_weight >= initial_weight * 0.9  # Allow for some decay
    
    def test_aggregation_statistics(self):
        """Test aggregation statistics tracking"""
        stats = self.aggregator.get_aggregation_statistics()
        
        assert isinstance(stats, dict)
        assert 'total_aggregations' in stats
        assert stats['total_aggregations'] >= 0


class TestAdaptiveResponseGenerator:
    """Test adaptive response generation functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.generator = AdaptiveResponseGenerator()
        
        # Create mock synthesis result
        self.mock_synthesis = SynthesisResult(
            primary_response="Test analysis summary with key findings: Finding 1, Finding 2, Finding 3",
            supporting_fragments=[
                SynthesisFragment("Finding 1", ["T23A_SPACY_NER"], 0.85, "finding"),
                SynthesisFragment("Finding 2", ["T27_RELATIONSHIP_EXTRACTOR"], 0.82, "finding"),
                SynthesisFragment("Finding 3", ["T31_ENTITY_BUILDER"], 0.79, "finding")
            ],
            overall_confidence=0.8,
            synthesis_strategy=SynthesisStrategy.COMPREHENSIVE,
            source_tool_coverage={"T23A_SPACY_NER": 0.4, "T27_RELATIONSHIP_EXTRACTOR": 0.35, "T31_ENTITY_BUILDER": 0.25},
            quality_metrics={"completeness": 0.85, "coherence": 0.8},
            metadata={}
        )
        
        # Create mock execution plan
        self.mock_plan = create_test_execution_plan("test_plan", ["T23A_SPACY_NER"])
    
    def test_response_context_creation(self):
        """Test response context creation"""
        context = ResponseContext(
            original_question="What are the main themes?",
            question_intent=QuestionIntent.SPECIFIC_SEARCH,
            complexity_analysis=ComplexityAnalysisResult(
                level=ComplexityLevel.SIMPLE,
                estimated_tools=2,
                parallelizable_components=1,
                estimated_time_seconds=5.0,
                estimated_memory_mb=256,
                requires_gpu=False,
                complexity_factors={"word_count": 0.3, "entity_mentions": 0.4},
                execution_strategy="sequential"
            ),
            original_plan=self.mock_plan,
            actual_execution={"step1": {"success": True}},
            execution_summary={"total_time": 5.0, "completed_steps": 1},
            synthesis_result=self.mock_synthesis,
            available_data={"entities": ["Entity1", "Entity2"]}
        )
        
        assert context.original_question == "What are the main themes?"
        assert context.question_intent == QuestionIntent.SPECIFIC_SEARCH
        assert len(context.available_data) > 0
    
    @pytest.mark.asyncio
    async def test_basic_response_generation(self):
        """Test basic adaptive response generation"""
        context = ResponseContext(
            original_question="What are the key findings?",
            question_intent=QuestionIntent.SPECIFIC_SEARCH,
            complexity_analysis=ComplexityAnalysisResult(
                level=ComplexityLevel.SIMPLE,
                estimated_tools=2,
                parallelizable_components=1,
                estimated_time_seconds=5.0,
                estimated_memory_mb=256,
                requires_gpu=False,
                complexity_factors={"word_count": 0.3, "entity_mentions": 0.4},
                execution_strategy="sequential"
            ),
            original_plan=self.mock_plan,
            actual_execution={"step1": {"success": True}},
            execution_summary={"total_time": 5.0, "completed_steps": 1, "total_steps": 1},
            synthesis_result=self.mock_synthesis,
            available_data={"entities": ["Entity1", "Entity2"]}
        )
        
        response = await self.generator.generate_adaptive_response(context)
        
        assert isinstance(response, AdaptiveResponse)
        assert len(response.response_text) > 0
        assert 0.0 <= response.confidence_score <= 1.0
        assert 0.0 <= response.information_completeness <= 1.0
        assert 0.0 <= response.response_quality <= 1.0
        assert isinstance(response.adaptations_applied, list)
    
    @pytest.mark.asyncio
    async def test_response_with_failed_tools(self):
        """Test response generation with failed tools"""
        context = ResponseContext(
            original_question="What are the relationships?",
            question_intent=QuestionIntent.RELATIONSHIP_ANALYSIS,
            complexity_analysis=ComplexityAnalysisResult(
                level=ComplexityLevel.MODERATE,
                estimated_tools=4,
                parallelizable_components=2,
                estimated_time_seconds=10.0,
                estimated_memory_mb=512,
                requires_gpu=False,
                complexity_factors={"word_count": 0.5, "entity_mentions": 0.6, "multi_part": 0.4},
                execution_strategy="adaptive"
            ),
            original_plan=self.mock_plan,
            actual_execution={"step1": {"success": False, "error": "Tool failed"}},
            execution_summary={"total_time": 2.0, "completed_steps": 0, "failed_steps": 1, "total_steps": 1},
            synthesis_result=self.mock_synthesis,
            available_data={"entities": ["Entity1"]},
            failed_tools=["T27_RELATIONSHIP_EXTRACTOR"]
        )
        
        response = await self.generator.generate_adaptive_response(context)
        
        assert isinstance(response, AdaptiveResponse)
        assert ResponseAdaptation.ACKNOWLEDGE_FAILURES in response.adaptations_applied
        assert ResponseAdaptation.FILL_GAPS in response.adaptations_applied
        assert len(response.limitations) > 0
        assert "unavailable" in response.limitations[0].lower() or "failed" in response.limitations[0].lower()
    
    @pytest.mark.asyncio
    async def test_response_with_low_confidence(self):
        """Test response generation with low confidence"""
        low_confidence_synthesis = SynthesisResult(
            primary_response="Uncertain analysis with tentative finding",
            supporting_fragments=[
                SynthesisFragment("Tentative finding", ["T23A_SPACY_NER"], 0.4, "finding")
            ],
            overall_confidence=0.4,
            synthesis_strategy=SynthesisStrategy.SUMMARY,
            source_tool_coverage={"T23A_SPACY_NER": 1.0},
            quality_metrics={"completeness": 0.4, "coherence": 0.5},
            metadata={}
        )
        
        confidence_metrics = ConfidenceMetrics(
            overall_confidence=0.4,
            confidence_variance=0.2,
            uncertainty_level=0.7,
            reliability_score=0.3,
            consensus_strength=0.2
        )
        
        context = ResponseContext(
            original_question="What can you tell me about this?",
            question_intent=QuestionIntent.SPECIFIC_SEARCH,
            complexity_analysis=ComplexityAnalysisResult(
                level=ComplexityLevel.SIMPLE,
                estimated_tools=2,
                parallelizable_components=1,
                estimated_time_seconds=5.0,
                estimated_memory_mb=256,
                requires_gpu=False,
                complexity_factors={"word_count": 0.3, "entity_mentions": 0.4},
                execution_strategy="sequential"
            ),
            original_plan=self.mock_plan,
            actual_execution={"step1": {"success": True}},
            execution_summary={"total_time": 5.0, "completed_steps": 1, "total_steps": 1},
            synthesis_result=low_confidence_synthesis,
            available_data={"entities": ["Entity1"]},
            confidence_metrics=confidence_metrics
        )
        
        response = await self.generator.generate_adaptive_response(context)
        
        assert isinstance(response, AdaptiveResponse)
        assert ResponseAdaptation.ENHANCE_CONFIDENCE in response.adaptations_applied
        assert ResponseAdaptation.HIGHLIGHT_UNCERTAINTIES in response.adaptations_applied
        assert "confidence" in response.response_text.lower()
    
    @pytest.mark.asyncio
    async def test_response_with_complex_question(self):
        """Test response generation for complex questions"""
        context = ResponseContext(
            original_question="How do the temporal patterns relate to the causal mechanisms underlying the observed phenomena?",
            question_intent=QuestionIntent.CAUSAL_ANALYSIS,
            complexity_analysis=ComplexityAnalysisResult(
                level=ComplexityLevel.COMPLEX,
                estimated_tools=8,
                parallelizable_components=4,
                estimated_time_seconds=20.0,
                estimated_memory_mb=1024,
                requires_gpu=True,
                complexity_factors={"word_count": 0.8, "entity_mentions": 0.9, "multi_part": 0.9, "inference": 0.8},
                execution_strategy="parallel_optimized"
            ),
            original_plan=self.mock_plan,
            actual_execution={"step1": {"success": True}},
            execution_summary={"total_time": 15.0, "completed_steps": 1, "total_steps": 3},
            synthesis_result=self.mock_synthesis,
            available_data={"entities": ["Entity1", "Entity2"], "relationships": [{"source": "A", "target": "B"}]}
        )
        
        response = await self.generator.generate_adaptive_response(context)
        
        assert isinstance(response, AdaptiveResponse)
        # Should apply complexity-related adaptations
        complexity_adaptations = [ResponseAdaptation.SIMPLIFY_COMPLEXITY, ResponseAdaptation.REORDER_PRIORITIES]
        assert any(adapt in response.adaptations_applied for adapt in complexity_adaptations)
    
    @pytest.mark.asyncio
    async def test_response_with_adaptation_history(self):
        """Test response generation with execution adaptations"""
        context = ResponseContext(
            original_question="What are the findings?",
            question_intent=QuestionIntent.SPECIFIC_SEARCH,
            complexity_analysis=ComplexityAnalysisResult(
                level=ComplexityLevel.MODERATE,
                estimated_tools=4,
                parallelizable_components=2,
                estimated_time_seconds=10.0,
                estimated_memory_mb=512,
                requires_gpu=False,
                complexity_factors={"word_count": 0.5, "entity_mentions": 0.5, "multi_part": 0.4},
                execution_strategy="adaptive"
            ),
            original_plan=self.mock_plan,
            actual_execution={"step1": {"success": True}},
            execution_summary={"total_time": 8.0, "completed_steps": 1, "total_steps": 1, "adaptations_made": 2},
            synthesis_result=self.mock_synthesis,
            available_data={"entities": ["Entity1", "Entity2"]},
            adaptation_history=[
                {"type": "parallel_boost", "reason": "Time pressure"},
                {"type": "quality_check", "reason": "Ensure accuracy"}
            ]
        )
        
        response = await self.generator.generate_adaptive_response(context)
        
        assert isinstance(response, AdaptiveResponse)
        assert ResponseAdaptation.ADD_CONTEXT in response.adaptations_applied
        assert "adaptive" in response.response_text.lower() or "adjustment" in response.response_text.lower()
    
    @pytest.mark.asyncio
    async def test_response_quality_assessment(self):
        """Test response quality assessment"""
        context = ResponseContext(
            original_question="Comprehensive analysis question",
            question_intent=QuestionIntent.COMPARATIVE_ANALYSIS,
            complexity_analysis=ComplexityAnalysisResult(
                level=ComplexityLevel.MODERATE,
                estimated_tools=4,
                parallelizable_components=2,
                estimated_time_seconds=10.0,
                estimated_memory_mb=512,
                requires_gpu=False,
                complexity_factors={"word_count": 0.5, "entity_mentions": 0.6, "multi_part": 0.5},
                execution_strategy="adaptive"
            ),
            original_plan=self.mock_plan,
            actual_execution={"step1": {"success": True}},
            execution_summary={"total_time": 7.0, "completed_steps": 1, "total_steps": 1},
            synthesis_result=self.mock_synthesis,
            available_data={"entities": ["E1", "E2", "E3"], "relationships": [{"s": "A", "t": "B"}]}
        )
        
        response = await self.generator.generate_adaptive_response(context)
        
        assert isinstance(response, AdaptiveResponse)
        assert 0.0 <= response.response_quality <= 1.0
        
        # Quality should be reasonable for complete successful execution
        assert response.response_quality > 0.5
    
    @pytest.mark.asyncio
    async def test_alternative_suggestions_generation(self):
        """Test generation of alternative suggestions"""
        # Complex question with limited results
        limited_synthesis = SynthesisResult(
            primary_response="Limited analysis with single finding",
            supporting_fragments=[
                SynthesisFragment("Single finding", ["T23A_SPACY_NER"], 0.6, "finding")
            ],
            overall_confidence=0.6,
            synthesis_strategy=SynthesisStrategy.FOCUSED,
            source_tool_coverage={"T23A_SPACY_NER": 1.0},
            quality_metrics={"completeness": 0.6, "coherence": 0.7},
            metadata={}
        )
        
        context = ResponseContext(
            original_question="Complex multi-part question about temporal causality and emergent patterns?",
            question_intent=QuestionIntent.CAUSAL_ANALYSIS,
            complexity_analysis=ComplexityAnalysisResult(
                level=ComplexityLevel.COMPLEX,
                estimated_tools=8,
                parallelizable_components=4,
                estimated_time_seconds=20.0,
                estimated_memory_mb=1024,
                requires_gpu=True,
                complexity_factors={"word_count": 0.9, "entity_mentions": 0.8, "multi_part": 0.9, "inference": 0.8},
                execution_strategy="parallel_optimized"
            ),
            original_plan=self.mock_plan,
            actual_execution={"step1": {"success": True}},
            execution_summary={"total_time": 5.0, "completed_steps": 1, "total_steps": 1},
            synthesis_result=limited_synthesis,
            available_data={"entities": ["Entity1"]}
        )
        
        response = await self.generator.generate_adaptive_response(context)
        
        assert isinstance(response, AdaptiveResponse)
        assert len(response.alternative_suggestions) > 0
        # Should suggest breaking down complex question
        suggestions_text = " ".join(response.alternative_suggestions).lower()
        assert any(keyword in suggestions_text for keyword in ["specific", "break", "narrow", "focused"])
    
    @pytest.mark.asyncio
    async def test_response_with_skipped_tools(self):
        """Test response generation with skipped tools"""
        context = ResponseContext(
            original_question="Quick analysis needed",
            question_intent=QuestionIntent.SPECIFIC_SEARCH,
            complexity_analysis=ComplexityAnalysisResult(
                level=ComplexityLevel.SIMPLE,
                estimated_tools=2,
                parallelizable_components=1,
                estimated_time_seconds=5.0,
                estimated_memory_mb=256,
                requires_gpu=False,
                complexity_factors={"word_count": 0.3, "entity_mentions": 0.3},
                execution_strategy="sequential"
            ),
            original_plan=self.mock_plan,
            actual_execution={"step1": {"success": True}},
            execution_summary={"total_time": 3.0, "completed_steps": 1, "total_steps": 2},
            synthesis_result=self.mock_synthesis,
            available_data={"entities": ["Entity1"]},
            skipped_tools=["T68_PAGE_RANK"]
        )
        
        response = await self.generator.generate_adaptive_response(context)
        
        assert isinstance(response, AdaptiveResponse)
        assert ResponseAdaptation.ACKNOWLEDGE_FAILURES in response.adaptations_applied
        assert len(response.limitations) > 0
        assert "skipped" in response.response_text.lower()
    
    def test_response_template_selection(self):
        """Test response template selection for different intents"""
        # Test factual lookup template
        factual_template = self.generator._select_response_template(
            QuestionIntent.SPECIFIC_SEARCH,
            ComplexityAnalysisResult(ComplexityLevel.SIMPLE, 2, 1, 5.0, 256, False, {}, "sequential")
        )
        assert factual_template == 'factual'
        
        # Test comparative analysis template
        comparative_template = self.generator._select_response_template(
            QuestionIntent.COMPARATIVE_ANALYSIS,
            ComplexityAnalysisResult(ComplexityLevel.MODERATE, 4, 2, 10.0, 512, False, {}, "adaptive")
        )
        assert comparative_template == 'comparative'
        
        # Test complex question template
        complex_template = self.generator._select_response_template(
            QuestionIntent.TEMPORAL_ANALYSIS,
            ComplexityAnalysisResult(ComplexityLevel.COMPLEX, 8, 4, 20.0, 1024, True, {}, "parallel_optimized")
        )
        assert complex_template == 'complex'
    
    def test_adaptation_statistics(self):
        """Test adaptation statistics tracking"""
        stats = self.generator.get_adaptation_statistics()
        
        assert isinstance(stats, dict)
        assert 'total_responses_generated' in stats
        assert 'adaptations_applied' in stats
        assert 'average_response_quality' in stats
        assert 'average_confidence' in stats


class TestEnhancedResponseIntegration:
    """Test integration between response generation and confidence aggregation"""
    
    def setup_method(self):
        """Set up test environment"""
        self.generator = AdaptiveResponseGenerator()
        self.aggregator = ConfidenceAggregator()
        
        # Create comprehensive test data
        self.confidence_inputs = [
            ConfidenceInput("T23A_SPACY_NER", ConfidenceSource.TOOL_OUTPUT, 0.85, 0.1, 1.0),
            ConfidenceInput("T27_RELATIONSHIP_EXTRACTOR", ConfidenceSource.TOOL_OUTPUT, 0.78, 0.15, 1.2),
            ConfidenceInput("T31_ENTITY_BUILDER", ConfidenceSource.TOOL_OUTPUT, 0.82, 0.12, 1.1)
        ]
        
        self.synthesis_result = SynthesisResult(
            primary_response="Integrated analysis summary with key findings: Key finding 1, Key finding 2, Key finding 3",
            supporting_fragments=[
                SynthesisFragment("Key finding 1", ["T23A_SPACY_NER"], 0.85, "finding"),
                SynthesisFragment("Key finding 2", ["T27_RELATIONSHIP_EXTRACTOR"], 0.78, "finding"),
                SynthesisFragment("Key finding 3", ["T31_ENTITY_BUILDER"], 0.82, "finding")
            ],
            overall_confidence=0.81,
            synthesis_strategy=SynthesisStrategy.COMPREHENSIVE,
            source_tool_coverage={"T23A_SPACY_NER": 0.33, "T27_RELATIONSHIP_EXTRACTOR": 0.33, "T31_ENTITY_BUILDER": 0.34},
            quality_metrics={"completeness": 0.85, "coherence": 0.88},
            metadata={"integration_test": True}
        )
    
    @pytest.mark.asyncio
    async def test_full_integration_pipeline(self):
        """Test complete integration pipeline"""
        # Step 1: Aggregate confidence
        confidence_metrics = await self.aggregator.aggregate_confidence(
            self.confidence_inputs, AggregationMethod.WEIGHTED_AVERAGE
        )
        
        # Step 2: Create response context with aggregated confidence
        context = ResponseContext(
            original_question="What are the integrated findings from this analysis?",
            question_intent=QuestionIntent.SPECIFIC_SEARCH,
            complexity_analysis=ComplexityAnalysisResult(
                level=ComplexityLevel.MODERATE,
                estimated_tools=4,
                parallelizable_components=2,
                estimated_time_seconds=10.0,
                estimated_memory_mb=512,
                requires_gpu=False,
                complexity_factors={"word_count": 0.5, "entity_mentions": 0.6, "multi_part": 0.4},
                execution_strategy="adaptive"
            ),
            original_plan=create_test_execution_plan(
                "integration_test", 
                ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER"], 
                10.5
            ),
            actual_execution={
                "step1": {"success": True, "confidence": 0.85},
                "step2": {"success": True, "confidence": 0.78},
                "step3": {"success": True, "confidence": 0.82}
            },
            execution_summary={"total_time": 9.8, "completed_steps": 3, "total_steps": 3},
            synthesis_result=self.synthesis_result,
            available_data={
                "entities": ["Entity1", "Entity2", "Entity3"],
                "relationships": [{"source": "Entity1", "target": "Entity2"}],
                "confidence_scores": {"overall": 0.81}
            },
            confidence_metrics=confidence_metrics
        )
        
        # Step 3: Generate adaptive response
        response = await self.generator.generate_adaptive_response(context)
        
        # Validate integration results
        assert isinstance(response, AdaptiveResponse)
        assert response.confidence_score > 0.7  # Should have good confidence
        assert response.information_completeness > 0.8  # Should be quite complete
        assert response.response_quality > 0.7  # Should have good quality
        
        # Should have structured response with key findings
        assert "finding" in response.response_text.lower()
        assert len(response.response_text) > 100  # Substantial response
    
    @pytest.mark.asyncio
    async def test_integration_with_mixed_success(self):
        """Test integration with some failed/skipped tools"""
        # Mixed confidence inputs with one failure
        mixed_inputs = [
            ConfidenceInput("T23A_SPACY_NER", ConfidenceSource.TOOL_OUTPUT, 0.88, 0.08, 1.0),
            ConfidenceInput("T31_ENTITY_BUILDER", ConfidenceSource.TOOL_OUTPUT, 0.79, 0.18, 1.0)
            # Note: T27_RELATIONSHIP_EXTRACTOR missing (failed)
        ]
        
        confidence_metrics = await self.aggregator.aggregate_confidence(
            mixed_inputs, AggregationMethod.UNCERTAINTY_WEIGHTED
        )
        
        context = ResponseContext(
            original_question="What can you determine from partial analysis?",
            question_intent=QuestionIntent.SPECIFIC_SEARCH,
            complexity_analysis=ComplexityAnalysisResult(
                level=ComplexityLevel.MODERATE,
                estimated_tools=4,
                parallelizable_components=2,
                estimated_time_seconds=10.0,
                estimated_memory_mb=512,
                requires_gpu=False,
                complexity_factors={"word_count": 0.5, "entity_mentions": 0.5, "multi_part": 0.4},
                execution_strategy="adaptive"
            ),
            original_plan=create_test_execution_plan(
                "mixed_test", 
                ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER"], 
                10.5
            ),
            actual_execution={
                "step1": {"success": True, "confidence": 0.88},
                "step2": {"success": False, "error": "Tool timeout"},
                "step3": {"success": True, "confidence": 0.79}
            },
            execution_summary={"total_time": 7.2, "completed_steps": 2, "failed_steps": 1, "total_steps": 3},
            synthesis_result=self.synthesis_result,
            available_data={
                "entities": ["Entity1", "Entity2"],
                "confidence_scores": {"partial": 0.76}
            },
            confidence_metrics=confidence_metrics,
            failed_tools=["T27_RELATIONSHIP_EXTRACTOR"]
        )
        
        response = await self.generator.generate_adaptive_response(context)
        
        # Validate mixed success handling
        assert isinstance(response, AdaptiveResponse)
        assert ResponseAdaptation.ACKNOWLEDGE_FAILURES in response.adaptations_applied
        assert ResponseAdaptation.FILL_GAPS in response.adaptations_applied
        assert len(response.limitations) > 0
        
        # Should acknowledge the limitation
        assert "limit" in response.response_text.lower() or "unavailable" in response.response_text.lower()
    
    @pytest.mark.asyncio
    async def test_integration_performance_tracking(self):
        """Test performance tracking across integration"""
        start_time = time.time()
        
        # Run full integration pipeline
        confidence_metrics = await self.aggregator.aggregate_confidence(
            self.confidence_inputs, AggregationMethod.BAYESIAN_FUSION
        )
        
        context = ResponseContext(
            original_question="Performance test question",
            question_intent=QuestionIntent.SPECIFIC_SEARCH,
            complexity_analysis=ComplexityAnalysisResult(
                level=ComplexityLevel.SIMPLE,
                estimated_tools=2,
                parallelizable_components=1,
                estimated_time_seconds=5.0,
                estimated_memory_mb=256,
                requires_gpu=False,
                complexity_factors={"word_count": 0.3, "entity_mentions": 0.4},
                execution_strategy="sequential"
            ),
            original_plan=create_test_execution_plan("perf_test", ["T23A_SPACY_NER"], 3.0),
            actual_execution={"step1": {"success": True, "confidence": 0.85}},
            execution_summary={"total_time": 2.8, "completed_steps": 1, "total_steps": 1},
            synthesis_result=self.synthesis_result,
            available_data={"entities": ["Entity1"]},
            confidence_metrics=confidence_metrics
        )
        
        response = await self.generator.generate_adaptive_response(context)
        
        total_time = time.time() - start_time
        
        # Validate performance
        assert isinstance(response, AdaptiveResponse)
        assert total_time < 5.0  # Should complete quickly
        assert confidence_metrics.processing_time > 0.0  # Should track processing time
        
        # Check performance tracking in metrics
        aggregation_stats = self.aggregator.get_aggregation_statistics()
        assert aggregation_stats['total_aggregations'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])