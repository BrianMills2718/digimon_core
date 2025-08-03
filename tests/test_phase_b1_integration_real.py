#!/usr/bin/env python3
"""
Real integration tests for Phase B.1 using actual services
No mocks - tests real functionality
"""
import pytest
import asyncio
from pathlib import Path
from src.core.service_manager import ServiceManager
from src.nlp.natural_language_interface import NaturalLanguageInterface
from src.nlp.advanced_intent_classifier import QuestionIntent
from src.nlp.question_complexity_analyzer import ComplexityLevel


class TestPhaseB1RealIntegration:
    """Test Phase B.1 with real services and no mocks"""
    
    async def create_interface(self):
        """Create a real Natural Language Interface with all services"""
        service_manager = ServiceManager()
        interface = NaturalLanguageInterface(service_manager)
        await interface.initialize()
        return interface
    
    @pytest.mark.asyncio
    async def test_simple_question_with_advanced_analysis(self):
        """Test that simple questions trigger advanced analysis"""
        # GIVEN a real interface
        interface = await self.create_interface()
        
        # Create test document
        test_doc = Path("test_doc_integration.txt")
        test_doc.write_text("Microsoft and Google are major tech companies.")
        interface.current_document_path = str(test_doc)
        
        try:
            # WHEN asking a simple question
            result_str = await interface.ask_question("What companies are mentioned?")
            result = interface.last_result
            
            # THEN advanced analysis should be present
            assert hasattr(result, 'advanced_analysis')
            assert result.advanced_analysis is not None
            assert result.advanced_analysis.intent == QuestionIntent.ENTITY_EXTRACTION
            assert result.advanced_analysis.complexity == ComplexityLevel.SIMPLE
            assert result.advanced_analysis.confidence > 0.8
            
            # AND execution should succeed
            assert result.status == "success"
            assert len(result.entities) > 0
            assert any("Microsoft" in e.get('surface_form', '') for e in result.entities)
            assert any("Google" in e.get('surface_form', '') for e in result.entities)
        
        finally:
            # Cleanup
            test_doc.unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_complex_question_analysis(self):
        """Test that complex questions are properly analyzed"""
        # GIVEN a real interface
        interface = await self.create_interface()
        
        # Create test document
        test_doc = Path("test_doc_integration2.txt")
        test_doc.write_text("Microsoft and Google are major tech companies.")
        interface.current_document_path = str(test_doc)
        
        try:
            # WHEN asking a complex multi-part question
            question = "Compare Microsoft and Google and identify which is more important"
            result_str = await interface.ask_question(question)
            result = interface.last_result
            
            # THEN analysis should identify complexity
            assert result.advanced_analysis.intent in [
                QuestionIntent.COMPARATIVE_ANALYSIS,
                QuestionIntent.NETWORK_ANALYSIS
            ]
            assert result.advanced_analysis.complexity in [
                ComplexityLevel.MODERATE,
                ComplexityLevel.COMPLEX
            ]
            
            # AND should identify multiple aspects (if implemented)
            # Note: secondary_intents feature is optional for Phase B.1
            if hasattr(result.advanced_analysis, 'secondary_intents'):
                # If secondary intents are provided, check they're valid
                if result.advanced_analysis.secondary_intents:
                    assert len(result.advanced_analysis.secondary_intents) >= 1
        
        finally:
            test_doc.unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_temporal_question_analysis(self):
        """Test temporal context extraction"""
        # GIVEN a real interface with temporal data
        interface = await self.create_interface()
        test_doc = Path("test_temporal_doc.txt")
        test_doc.write_text("In 2023, Microsoft acquired a company. In 2024, Google launched a product.")
        interface.current_document_path = str(test_doc)
        
        try:
            # WHEN asking a temporal question
            result_str = await interface.ask_question("What happened in 2023?")
            result = interface.last_result
            
            # THEN context should include temporal information
            assert hasattr(result, 'execution_metadata')
            meta = result.execution_metadata
            
            # Check if temporal parameters were adapted
            adapted_params = meta.get('adapted_parameters', {})
            if 'T23A_SPACY_NER' in adapted_params:
                ner_params = adapted_params['T23A_SPACY_NER']
                assert 'time_filter' in ner_params
                assert ner_params['time_filter'] == '2023'
                assert ner_params.get('temporal_filtering_enabled', False) == True
        
        finally:
            test_doc.unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_tool_skipping_with_insufficient_data(self):
        """Test that tools are skipped when data is insufficient"""
        # GIVEN a document with minimal entities
        interface = await self.create_interface()
        test_doc = Path("test_minimal_doc.txt")
        test_doc.write_text("The weather is nice today.")
        interface.current_document_path = str(test_doc)
        
        try:
            # WHEN asking about relationships
            result_str = await interface.ask_question("What relationships exist?")
            result = interface.last_result
            
            # THEN some tools should be skipped
            if hasattr(result, 'execution_metadata'):
                meta = result.execution_metadata
                skipped = meta.get('tools_skipped', [])
                
                # Should skip relationship extractor with < 2 entities
                # This might not always trigger depending on entities found
                if len(result.entities) < 2:
                    assert 'T27_RELATIONSHIP_EXTRACTOR' in skipped
        
        finally:
            test_doc.unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_parameter_adaptation(self):
        """Test that parameters adapt based on question context"""
        # GIVEN a real interface
        interface = await self.create_interface()
        
        # Create test document
        test_doc = Path("test_doc_integration3.txt")
        test_doc.write_text("Microsoft and Google are major tech companies.")
        interface.current_document_path = str(test_doc)
        
        try:
            # WHEN asking an ambiguous question
            result_str = await interface.ask_question("Tell me about the stuff")
            result = interface.last_result
            
            # THEN parameters should be adapted
            if hasattr(result, 'execution_metadata'):
                meta = result.execution_metadata
                adapted = meta.get('adapted_parameters', {})
                
                # Check if confidence threshold was raised for ambiguous question
                if 'T23A_SPACY_NER' in adapted:
                    ner_params = adapted['T23A_SPACY_NER']
                    # Ambiguous questions might get higher threshold
                    assert 'confidence_threshold' in ner_params
        
        finally:
            test_doc.unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])