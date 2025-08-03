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
    
    async def create_mock_mcp_executor(self):
        """Create a properly mocked MCP executor"""
        mock_executor = MagicMock()
        
        # Tool outputs that will be returned
        tool_outputs = {
            "T01_PDF_LOADER": {
                "status": "success",
                "data": {"document": {"text": "Sample document text", "document_ref": "doc123"}}
            },
            "T15A_TEXT_CHUNKER": {
                "status": "success",
                "data": {"chunks": [{"text": "Sample chunk with Microsoft, Google and Amazon", "chunk_ref": "chunk123"}]}
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
            },
            "T27_RELATIONSHIP_EXTRACTOR": {
                "status": "success",
                "data": {
                    "relationships": [
                        {"source": "Microsoft", "target": "Google", "type": "competes_with"},
                        {"source": "Google", "target": "Amazon", "type": "competes_with"}
                    ]
                }
            }
        }
        
        # Mock the _execute_single_tool method
        async def mock_execute_single_tool(tool_id, args):
            await asyncio.sleep(0.01)  # Simulate some execution time
            return tool_outputs.get(tool_id, {"status": "error", "error": "Tool not found", "data": None})
        
        # Create a MagicMock that returns a coroutine when called
        mock_executor._execute_single_tool = MagicMock(side_effect=mock_execute_single_tool)
        mock_executor.get_execution_stats = Mock(return_value={'mcp_client_available': True})
        
        return mock_executor
    
    @pytest.mark.asyncio
    async def test_phase_b_enhances_phase_a_simple_question(self, mock_service_manager):
        """Simple questions should use Phase B analysis but maintain Phase A functionality"""
        # Create mock MCP executor
        mock_mcp_executor = await self.create_mock_mcp_executor()
        
        # GIVEN a Natural Language Interface with mocked MCP executor
        interface = NaturalLanguageInterface(mock_service_manager)
        interface.mcp_executor = mock_mcp_executor
        interface.dynamic_executor.mcp_executor = mock_mcp_executor
        
        await interface.initialize()
        
        # AND load a test document
        interface.current_document_path = "test.pdf"
        
        # AND a simple question
        question = "What companies are mentioned in this document?"
        
        # WHEN processed through the pipeline
        result_str = await interface.ask_question(question)
        
        # Parse the result to check advanced analysis
        result = interface.last_result
        
        # THEN it should use advanced analysis
        assert hasattr(result, 'advanced_analysis'), "Result should include advanced analysis"
        assert result.advanced_analysis is not None, "Advanced analysis should not be None"
        assert result.advanced_analysis.intent == QuestionIntent.ENTITY_EXTRACTION
        assert result.advanced_analysis.complexity == ComplexityLevel.SIMPLE
        
        # AND still execute tools via MCP
        assert result.status == "success"
        assert "T23A_SPACY_NER" in result.tools_executed
        assert len(result.entities) > 0, "Should extract entities"
        assert any("Microsoft" in str(e) for e in result.entities), "Should find Microsoft"
        assert any("Google" in str(e) for e in result.entities), "Should find Google"
        assert any("Amazon" in str(e) for e in result.entities), "Should find Amazon"
    
    @pytest.mark.asyncio
    async def test_phase_b_handles_complex_multi_intent_questions(self, mock_service_manager):
        """Complex questions should trigger advanced analysis and dynamic execution"""
        # Create mock MCP executor with additional tools
        mock_mcp_executor = await self.create_mock_mcp_executor()
        
        # GIVEN a Natural Language Interface
        interface = NaturalLanguageInterface(mock_service_manager)
        interface.mcp_executor = mock_mcp_executor
        interface.dynamic_executor.mcp_executor = mock_mcp_executor
        
        await interface.initialize()
        
        # AND a complex multi-part question
        question = "Compare Microsoft and Google's AI strategies from 2020 to 2024 and predict future trends"
        
        # WHEN processed
        result_str = await interface.ask_question(question)
        result = interface.last_result
        
        # THEN advanced analysis should identify multiple intents
        assert result.advanced_analysis.intent in [
            QuestionIntent.COMPARATIVE_ANALYSIS,
            QuestionIntent.PREDICTIVE_ANALYSIS
        ]
        assert len(result.advanced_analysis.secondary_intents) >= 1
        assert result.advanced_analysis.complexity == ComplexityLevel.COMPLEX
        
        # AND should have temporal context
        assert result.advanced_analysis.has_temporal_context == True
        assert "2020" in result.advanced_analysis.temporal_constraints or "2024" in result.advanced_analysis.temporal_constraints
        
        # AND should execute multiple tools
        assert len(result.tools_executed) >= 3
        assert "T27_RELATIONSHIP_EXTRACTOR" in result.tools_executed
        
        # AND execution should be marked as potentially parallelizable
        assert result.execution_metadata.get("execution_strategy") in ["parallel_simple", "parallel_advanced", "sequential"]
    
    @pytest.mark.asyncio
    async def test_phase_b_adapts_parameters_based_on_context(self, mock_service_manager):
        """Tool parameters should be adapted based on question context"""
        # Create mock MCP executor
        mock_mcp_executor = await self.create_mock_mcp_executor()
        
        # GIVEN a Natural Language Interface
        interface = NaturalLanguageInterface(mock_service_manager)
        interface.mcp_executor = mock_mcp_executor
        interface.dynamic_executor.mcp_executor = mock_mcp_executor
        
        await interface.initialize()
        
        # AND a question with temporal context
        question = "What happened to Microsoft's stock price in 2023?"
        
        # WHEN processed
        result_str = await interface.ask_question(question)
        result = interface.last_result
        
        # THEN temporal context should be extracted
        assert result.advanced_analysis.has_temporal_context == True
        assert "2023" in result.advanced_analysis.temporal_constraints
        
        # AND tool parameters should include temporal filter
        assert result.tool_parameters.get("time_filter") == "2023"
        
        # AND adapted parameters should be recorded
        if 'adapted_parameters' in result.execution_metadata:
            adapted = result.execution_metadata['adapted_parameters']
            if 'T23A_SPACY_NER' in adapted:
                assert adapted['T23A_SPACY_NER'].get('temporal_filtering_enabled') == True
    
    @pytest.mark.asyncio
    async def test_phase_b_skips_tools_dynamically(self, mock_service_manager):
        """Tools should be skipped based on intermediate results"""
        # Create mock MCP executor with limited entities
        mock_mcp_executor = await self.create_mock_mcp_executor()
        
        # Override NER to return only one entity (not enough for relationships)
        original_execute = mock_mcp_executor._execute_single_tool
        
        async def limited_execute(tool_id, args):
            if tool_id == "T23A_SPACY_NER":
                return {
                    "status": "success",
                    "data": {"entities": [{"text": "Microsoft", "type": "ORG"}]}  # Only one entity
                }
            return await original_execute(tool_id, args)
        
        mock_mcp_executor._execute_single_tool = limited_execute
        
        # GIVEN a Natural Language Interface
        interface = NaturalLanguageInterface(mock_service_manager)
        interface.mcp_executor = mock_mcp_executor
        interface.dynamic_executor.mcp_executor = mock_mcp_executor
        
        await interface.initialize()
        
        # AND a question that would normally trigger relationship extraction
        question = "What relationships exist between companies?"
        
        # WHEN processed
        result_str = await interface.ask_question(question)
        result = interface.last_result
        
        # THEN relationship extractor should be skipped (not enough entities)
        if 'tools_skipped' in result.execution_metadata:
            assert "T27_RELATIONSHIP_EXTRACTOR" in result.execution_metadata['tools_skipped']
    
    @pytest.mark.asyncio
    async def test_phase_b_handles_ambiguous_questions(self, mock_service_manager):
        """Ambiguous questions should be detected and confidence reported"""
        # Create mock MCP executor
        mock_mcp_executor = await self.create_mock_mcp_executor()
        
        # GIVEN a Natural Language Interface
        interface = NaturalLanguageInterface(mock_service_manager)
        interface.mcp_executor = mock_mcp_executor
        interface.dynamic_executor.mcp_executor = mock_mcp_executor
        
        await interface.initialize()
        
        # AND an ambiguous question
        question = "Tell me about the stuff in here"
        
        # WHEN processed
        result_str = await interface.ask_question(question)
        result = interface.last_result
        
        # THEN it should detect ambiguity
        assert result.advanced_analysis.confidence < 0.7
        assert result.advanced_analysis.ambiguity_level > 0.5
        assert len(result.advanced_analysis.missing_context) > 0
        
        # AND should still attempt to provide a response
        assert result.status == "success"
        assert result.confidence_disclaimer is not None
    
    @pytest.mark.asyncio 
    async def test_phase_b_maintains_backward_compatibility(self, mock_service_manager):
        """Phase A functionality should still work when Phase B is disabled"""
        # Create mock for PipelineManager (Phase A)
        with patch('src.nlp.natural_language_interface.PipelineManager') as mock_pm:
            mock_result = Mock()
            mock_result.tool_outputs = {
                "T23A_SPACY_NER": {
                    "status": "success",
                    "data": {"entities": [{"text": "TestCompany", "type": "ORG"}]}
                }
            }
            mock_result.execution_metadata = {"provenance": {}}
            
            async def mock_execute(*args, **kwargs):
                return mock_result
            
            mock_pm.return_value.execute_pipeline = mock_execute
            
            # GIVEN a Natural Language Interface
            interface = NaturalLanguageInterface(mock_service_manager)
            
            # AND we disable advanced analysis
            interface.use_advanced_analysis = False
            
            await interface.initialize()
            
            # WHEN processing a question the old way
            question = "What is this document about?"
            result_str = await interface.ask_question(question)
            result = interface.last_result
            
            # THEN it should work exactly like Phase A
            assert result.status == "success"
            assert not hasattr(result, 'advanced_analysis') or result.advanced_analysis is None
            # Phase A uses fixed 3-tool pipeline
            assert len(result.tools_executed) == 1  # Only NER in mock

if __name__ == "__main__":
    pytest.main([__file__, "-v"])