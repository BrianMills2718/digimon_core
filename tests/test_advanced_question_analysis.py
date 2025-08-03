#!/usr/bin/env python3
"""
Test Advanced Question Analysis & Intent Classification
Tests multi-dimensional question classification for dynamic tool selection
"""
import pytest
from src.nlp.advanced_intent_classifier import AdvancedIntentClassifier, QuestionIntent
from src.nlp.question_complexity_analyzer import QuestionComplexityAnalyzer, ComplexityLevel
from src.nlp.context_extractor import ContextExtractor, QuestionContext

class TestAdvancedIntentClassifier:
    """Test advanced intent classification with 10+ intent categories"""
    
    def test_basic_intent_categories(self):
        """Test classification of basic single-intent questions"""
        classifier = AdvancedIntentClassifier()
        
        test_cases = [
            # Basic intents from Phase A
            ("What is this document about?", QuestionIntent.DOCUMENT_SUMMARY),
            ("What companies are mentioned?", QuestionIntent.ENTITY_EXTRACTION),
            ("How do they relate?", QuestionIntent.RELATIONSHIP_ANALYSIS),
            ("What are the main themes?", QuestionIntent.THEME_ANALYSIS),
            ("Find information about Microsoft", QuestionIntent.SPECIFIC_SEARCH),
            
            # New advanced intents
            ("Compare Microsoft and Google's AI strategies", QuestionIntent.COMPARATIVE_ANALYSIS),
            ("What patterns emerge from the data?", QuestionIntent.PATTERN_DISCOVERY),
            ("Predict future trends based on this analysis", QuestionIntent.PREDICTIVE_ANALYSIS),
            ("What are the causal relationships?", QuestionIntent.CAUSAL_ANALYSIS),
            ("Summarize the timeline of events", QuestionIntent.TEMPORAL_ANALYSIS),
            ("What are the statistical correlations?", QuestionIntent.STATISTICAL_ANALYSIS),
            ("Identify anomalies or outliers", QuestionIntent.ANOMALY_DETECTION),
            ("What is the sentiment across entities?", QuestionIntent.SENTIMENT_ANALYSIS),
            ("Create a hierarchical view of concepts", QuestionIntent.HIERARCHICAL_ANALYSIS),
            ("What are the network effects?", QuestionIntent.NETWORK_ANALYSIS)
        ]
        
        for question, expected_intent in test_cases:
            result = classifier.classify(question)
            assert result.primary_intent == expected_intent, \
                f"Failed to classify '{question}' as {expected_intent.value}"
            assert result.confidence >= 0.7, \
                f"Low confidence {result.confidence} for '{question}'"
    
    def test_multi_intent_questions(self):
        """Test classification of questions with multiple intents"""
        classifier = AdvancedIntentClassifier()
        
        # Complex multi-part questions
        question = "Compare Microsoft and Google's AI strategies and predict future trends"
        result = classifier.classify(question)
        
        assert result.primary_intent in [QuestionIntent.COMPARATIVE_ANALYSIS, 
                                        QuestionIntent.PREDICTIVE_ANALYSIS]
        assert len(result.secondary_intents) >= 1
        assert any(intent in [QuestionIntent.COMPARATIVE_ANALYSIS, 
                             QuestionIntent.PREDICTIVE_ANALYSIS] 
                  for intent in result.secondary_intents)
    
    def test_confidence_scores(self):
        """Test confidence scoring for intent classification"""
        classifier = AdvancedIntentClassifier()
        
        # Clear, unambiguous question should have high confidence
        clear_result = classifier.classify("What companies are mentioned in this document?")
        assert clear_result.confidence >= 0.9
        
        # Ambiguous question should have lower confidence
        ambiguous_result = classifier.classify("Tell me about the stuff in here")
        assert ambiguous_result.confidence < 0.7
    
    def test_tool_chain_recommendations(self):
        """Test that classifier recommends appropriate tool chains"""
        classifier = AdvancedIntentClassifier()
        
        # Entity extraction should recommend NER tools
        result = classifier.classify("What companies are mentioned?")
        assert "T23A_SPACY_NER" in result.recommended_tools
        
        # Relationship analysis should recommend relationship tools
        result = classifier.classify("How do these entities relate?")
        assert "T27_RELATIONSHIP_EXTRACTOR" in result.recommended_tools
        
        # Complex analysis should recommend multiple tools
        result = classifier.classify("Compare companies and analyze their relationships")
        assert len(result.recommended_tools) >= 3


class TestQuestionComplexityAnalyzer:
    """Test question complexity analysis for execution planning"""
    
    def test_complexity_levels(self):
        """Test classification of question complexity"""
        analyzer = QuestionComplexityAnalyzer()
        
        # Simple questions
        simple = analyzer.analyze("What is this document about?")
        assert simple.level == ComplexityLevel.SIMPLE
        assert simple.estimated_tools <= 3
        
        # Moderate questions
        moderate = analyzer.analyze("What companies are mentioned and how do they compete?")
        assert moderate.level == ComplexityLevel.MODERATE
        assert 3 < moderate.estimated_tools <= 6
        
        # Complex questions
        complex_q = analyzer.analyze(
            "Compare all companies' AI strategies, identify patterns, "
            "predict future trends, and analyze causal relationships"
        )
        assert complex_q.level == ComplexityLevel.COMPLEX
        assert complex_q.estimated_tools > 6
    
    def test_parallelization_opportunities(self):
        """Test identification of parallel execution opportunities"""
        analyzer = QuestionComplexityAnalyzer()
        
        # Sequential question - no parallelization
        seq_result = analyzer.analyze("Extract entities then analyze their relationships")
        assert seq_result.parallelizable_components == 0
        
        # Parallel question - multiple independent analyses
        par_result = analyzer.analyze(
            "Analyze sentiment, extract themes, and identify patterns"
        )
        assert par_result.parallelizable_components >= 2
    
    def test_resource_estimation(self):
        """Test resource requirement estimation"""
        analyzer = QuestionComplexityAnalyzer()
        
        result = analyzer.analyze("Perform comprehensive analysis of all entities and relationships")
        assert result.estimated_memory_mb > 0
        assert result.estimated_time_seconds > 0
        assert result.requires_gpu is False  # Unless we add GPU tools


class TestContextExtractor:
    """Test context extraction from questions"""
    
    def test_temporal_context(self):
        """Test extraction of temporal context"""
        extractor = ContextExtractor()
        
        # Questions with time references
        result = extractor.extract("What happened in 2023?")
        assert result.has_temporal_context
        assert "2023" in result.temporal_constraints
        
        result = extractor.extract("Compare last year's performance with this year")
        assert result.has_temporal_context
        assert result.requires_temporal_analysis
    
    def test_entity_context(self):
        """Test extraction of entity-specific context"""
        extractor = ContextExtractor()
        
        result = extractor.extract("How does Microsoft's strategy differ from Google's?")
        assert len(result.mentioned_entities) == 2
        assert "Microsoft" in result.mentioned_entities
        assert "Google" in result.mentioned_entities
    
    def test_comparison_context(self):
        """Test extraction of comparison requirements"""
        extractor = ContextExtractor()
        
        result = extractor.extract("Compare the top 3 companies by revenue")
        assert result.requires_comparison
        assert result.comparison_type == "ranking"
        assert result.comparison_count == 3
    
    def test_aggregation_context(self):
        """Test extraction of aggregation requirements"""
        extractor = ContextExtractor()
        
        result = extractor.extract("What is the average sentiment across all entities?")
        assert result.requires_aggregation
        assert result.aggregation_type == "average"
        assert result.aggregation_scope == "all entities"


class TestIntegration:
    """Test integration of all question analysis components"""
    
    def test_complete_question_analysis(self):
        """Test complete analysis pipeline"""
        classifier = AdvancedIntentClassifier()
        complexity = QuestionComplexityAnalyzer()
        context = ContextExtractor()
        
        question = "Compare Microsoft and Google's AI strategies from 2020 to 2024 and predict future trends"
        
        # Classify intent
        intent_result = classifier.classify(question)
        # Either could be primary with the other as secondary
        valid_primary = [QuestionIntent.COMPARATIVE_ANALYSIS, QuestionIntent.PREDICTIVE_ANALYSIS]
        assert intent_result.primary_intent in valid_primary
        
        # Check that both intents are recognized
        all_intents = [intent_result.primary_intent] + intent_result.secondary_intents
        assert QuestionIntent.COMPARATIVE_ANALYSIS in all_intents
        assert QuestionIntent.PREDICTIVE_ANALYSIS in all_intents
        
        # Analyze complexity
        complexity_result = complexity.analyze(question)
        assert complexity_result.level == ComplexityLevel.COMPLEX
        assert complexity_result.parallelizable_components > 0
        
        # Extract context
        context_result = context.extract(question)
        assert context_result.has_temporal_context
        assert "Microsoft" in context_result.mentioned_entities
        assert "Google" in context_result.mentioned_entities
        assert context_result.requires_comparison
    
    def test_tool_chain_generation(self):
        """Test generation of optimal tool chains based on analysis"""
        from src.nlp.tool_chain_generator import ToolChainGenerator
        
        generator = ToolChainGenerator()
        classifier = AdvancedIntentClassifier()
        complexity = QuestionComplexityAnalyzer()
        context = ContextExtractor()
        
        question = "What are the main entities and their relationships?"
        
        # Analyze question
        intent = classifier.classify(question)
        complexity_info = complexity.analyze(question)
        context_info = context.extract(question)
        
        # Generate tool chain
        tool_chain = generator.generate_chain(intent, complexity_info, context_info, question)
        
        assert len(tool_chain.steps) >= 3
        # This specific question might not parallelize
        assert isinstance(tool_chain.can_parallelize, bool)
        assert tool_chain.estimated_time > 0
        
        # Should include entity extraction and relationship analysis
        tool_ids = [step.tool_id for step in tool_chain.steps]
        assert "T23A_SPACY_NER" in tool_ids
        assert "T27_RELATIONSHIP_EXTRACTOR" in tool_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v"])