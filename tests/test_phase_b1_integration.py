#!/usr/bin/env python3
"""
Integration tests for Phase B.1: Advanced Question Analysis
These tests verify that Phase B analysis enhances Phase A's pipeline
Written FIRST before implementation (proper TDD)
"""
import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch
from src.nlp.natural_language_interface import NaturalLanguageInterface
from src.nlp.advanced_intent_classifier import QuestionIntent
from src.nlp.question_complexity_analyzer import ComplexityLevel

class TestPhaseB1Integration:
    """Test that Phase B.1 analysis integrates with and enhances Phase A"""
    
    @pytest.fixture
    def mock_service_manager(self):
        """Create a mock service manager for testing"""
        manager = Mock()
        manager.provenance_service = Mock()
        manager.provenance_service.start_operation = Mock(return_value="op-123")
        manager.provenance_service.complete_operation = Mock()
        manager.provenance_service.record_tool_execution = Mock()
        return manager
    
    @pytest.fixture
    def mock_mcp_executor(self):
        """Mock the MCP executor to return test data"""
        # We need to patch both PipelineManager and MCPExecutor since dynamic executor uses MCPExecutor directly
        with patch('src.nlp.natural_language_interface.PipelineManager') as mock_pm:
            with patch('src.nlp.natural_language_interface.MCPExecutor') as mock_mcp:
                with patch('src.execution.dynamic_executor.MCPExecutor') as mock_mcp2:
                    # Mock execution result with entities
                    mock_result = Mock()
                    mock_result.tool_outputs = {
                        "T01_PDF_LOADER": {
                            "status": "success",
                            "data": {"document": {"text": "Sample document text", "document_ref": "doc123"}}
                        },
                        "T15A_TEXT_CHUNKER": {
                            "status": "success",
                            "data": {"chunks": [{"text": "Sample chunk", "chunk_ref": "chunk123"}]}
                        },
                        "T23A_SPACY_NER": {
                            "status": "success",
                            "data": {
                                "entities": [
                                    {"text": "Microsoft", "type": "ORG"},
                                    {"text": "Google", "type": "ORG"},
                                    {"text": "Amazon", "type": "ORG"}
                                ]
                            }
                        }
                    }
                    mock_result.execution_metadata = {
                        "provenance": {},
                        "execution_time": 1.5,
                        "tools_executed": ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER"]
                    }
                    mock_result.total_execution_time = 1.5
                    mock_result.success_count = 3
                    mock_result.failure_count = 0
                    mock_result.errors = []
                    
                    # Mock the _execute_single_tool method for dynamic executor
                    async def mock_execute_single_tool(tool_id, args):
                        if tool_id in mock_result.tool_outputs:
                            return mock_result.tool_outputs[tool_id]
                        return {"status": "error", "error": "Tool not found", "data": None}
                    
                    # Make execute_pipeline return our mock result (async)
                    async def mock_execute_pipeline(*args, **kwargs):
                        return mock_result
                
                    # Configure mocks
                    mock_mcp.return_value._execute_single_tool = mock_execute_single_tool
                    mock_mcp.return_value.get_execution_stats.return_value = {'mcp_client_available': True}
                    mock_mcp2.return_value._execute_single_tool = mock_execute_single_tool
                    mock_mcp2.return_value.get_execution_stats.return_value = {'mcp_client_available': True}
                    mock_pm.return_value.execute_pipeline = mock_execute_pipeline
                    
                    yield mock_pm
    
    @pytest.mark.asyncio
    async def test_phase_b_enhances_phase_a_simple_question(self, mock_service_manager, mock_mcp_executor):
        """Simple questions should use Phase B analysis but maintain Phase A functionality"""
        # GIVEN a Natural Language Interface (Phase A component)
        interface = NaturalLanguageInterface(mock_service_manager)
        await interface.initialize()
        
        # AND a simple question
        question = "What companies are mentioned in this document?"
        
        # WHEN processed through the pipeline
        result_str = await interface.ask_question(question)
        
        # Parse the result to check advanced analysis
        result = interface.last_result  # We'll add this to track the detailed result
        
        # THEN it should use advanced analysis
        assert hasattr(result, 'advanced_analysis'), "Result should include advanced analysis"
        assert result.advanced_analysis.intent == QuestionIntent.ENTITY_EXTRACTION
        assert result.advanced_analysis.complexity == ComplexityLevel.SIMPLE
        
        # AND still execute tools via MCP
        assert result.status == "success"
        assert "T23A_SPACY_NER" in result.tools_executed
        assert len(result.entities) > 0, "Should extract entities"
    
    @pytest.mark.asyncio
    async def test_phase_b_handles_complex_multi_intent_questions(self, mock_service_manager, mock_mcp_executor):
        """Complex questions should trigger advanced analysis and dynamic execution"""
        # GIVEN a Natural Language Interface
        interface = NaturalLanguageInterface(mock_service_manager)
        
        # AND a complex multi-part question
        question = "Compare Microsoft and Google's AI strategies from 2020 to 2024 and predict future trends"
        
        # WHEN processed
        await interface.initialize()
        result_str = await interface.ask_question(question)
        result = interface.last_result
        
        # THEN advanced analysis should identify multiple intents
        assert result.advanced_analysis.intent in [
            QuestionIntent.COMPARATIVE_ANALYSIS,
            QuestionIntent.PREDICTIVE_ANALYSIS
        ]
        assert len(result.advanced_analysis.secondary_intents) >= 1
        assert result.advanced_analysis.complexity == ComplexityLevel.COMPLEX
        
        # AND should execute a complex tool chain
        assert len(result.tools_executed) >= 3  # Adjusted for mocked test
        assert "T27_RELATIONSHIP_EXTRACTOR" in result.tools_executed
        assert result.execution_metadata.get("parallelized", False) == True
        
        # AND should produce comparison results
        assert "Microsoft" in result.response
        assert "Google" in result.response
        assert any(word in result.response.lower() for word in ["compare", "comparison", "versus"])
    
    @pytest.mark.asyncio
    async def test_phase_b_optimizes_execution_for_parallelizable_questions(self, mock_service_manager, mock_mcp_executor):
        """Questions with independent analyses should execute in parallel"""
        # GIVEN a Natural Language Interface
        interface = NaturalLanguageInterface(mock_service_manager)
        
        # AND a question with parallelizable components
        question = "Analyze sentiment, extract themes, and identify patterns in the document"
        
        # WHEN processed
        await interface.initialize()
        result_str = await interface.ask_question(question)
        result = interface.last_result
        
        # THEN it should identify parallelization opportunities
        assert result.advanced_analysis.parallelizable_components > 0
        
        # AND execution should be optimized
        assert result.execution_metadata["execution_strategy"] in ["parallel_simple", "parallel_advanced"]
        assert result.execution_metadata["execution_time"] < result.execution_metadata.get("sequential_estimate", float('inf'))
    
    @pytest.mark.asyncio
    async def test_phase_b_provides_confidence_and_ambiguity_detection(self, mock_service_manager, mock_mcp_executor):
        """Ambiguous questions should be detected and confidence reported"""
        # GIVEN a Natural Language Interface
        interface = NaturalLanguageInterface(mock_service_manager)
        
        # AND an ambiguous question
        question = "Tell me about the stuff in here"
        
        # WHEN processed
        await interface.initialize()
        result_str = await interface.ask_question(question)
        result = interface.last_result
        
        # THEN it should detect ambiguity
        assert result.advanced_analysis.confidence < 0.7
        assert result.advanced_analysis.ambiguity_level > 0.5
        assert len(result.advanced_analysis.missing_context) > 0
        
        # AND should still attempt to provide a response
        assert result.status == "success"
        assert "document" in result.response.lower()
        assert result.confidence_disclaimer is not None
    
    @pytest.mark.asyncio
    async def test_phase_b_maintains_backward_compatibility(self, mock_service_manager, mock_mcp_executor):
        """Phase A functionality should still work exactly as before"""
        # GIVEN a Natural Language Interface
        interface = NaturalLanguageInterface(mock_service_manager)
        
        # AND we disable advanced analysis
        interface.use_advanced_analysis = False
        
        # WHEN processing a question the old way
        await interface.initialize()
        question = "What is this document about?"
        result_str = await interface.ask_question(question)
        result = interface.last_result
        
        # THEN it should work exactly like Phase A
        assert result.status == "success"
        assert not hasattr(result, 'advanced_analysis')
        assert len(result.tools_executed) == 3  # T01, T15A, T23A
    
    @pytest.mark.asyncio
    async def test_phase_b_handles_temporal_context_intelligently(self, mock_service_manager, mock_mcp_executor):
        """Questions with temporal context should extract and use time constraints"""
        # GIVEN a Natural Language Interface
        interface = NaturalLanguageInterface(mock_service_manager)
        
        # AND a question with temporal context
        question = "What happened to Microsoft's stock price in 2023?"
        
        # WHEN processed
        await interface.initialize()
        result_str = await interface.ask_question(question)
        result = interface.last_result
        
        # THEN temporal context should be extracted
        assert result.advanced_analysis.has_temporal_context == True
        assert "2023" in result.advanced_analysis.temporal_constraints
        
        # AND the response should be time-aware
        assert "2023" in result.response
        assert result.tool_parameters.get("time_filter") == "2023"
    
    @pytest.mark.asyncio
    async def test_phase_b_gracefully_handles_analysis_failures(self, mock_service_manager, mock_mcp_executor):
        """If advanced analysis fails, should fall back to Phase A behavior"""
        # GIVEN a Natural Language Interface
        interface = NaturalLanguageInterface(mock_service_manager)
        
        # AND we simulate an analysis failure
        question = "What companies are mentioned?"
        
        # WHEN advanced analysis fails (simulated)
        await interface.initialize()
        with patch('src.nlp.advanced_intent_classifier.AdvancedIntentClassifier.classify',
                   side_effect=Exception("Analysis failed")):
            result_str = await interface.ask_question(question)
            result = interface.last_result
        
        # THEN it should fall back gracefully
        assert result.status == "success"
        assert result.fallback_used == True
        assert result.warning == "Advanced analysis unavailable, using basic analysis"
        assert len(result.entities) > 0  # Should still extract entities

if __name__ == "__main__":
    pytest.main([__file__, "-v"])