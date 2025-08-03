"""
Question Parsing Tests
Tests for natural language question parsing and intent classification
"""
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.nlp.question_parser import QuestionParser, QuestionIntent, IntentClassifier, ToolMapper

class TestIntentClassifier:
    """Test question intent classification"""
    
    def setup_method(self):
        """Setup for each test"""
        self.classifier = IntentClassifier()
    
    def test_document_summary_classification(self):
        """Test document summary intent classification"""
        test_questions = [
            "What is this document about?",
            "Summarize the main points",
            "Give me an overview",
            "What are the key findings?"
        ]
        
        for question in test_questions:
            intent, confidence = self.classifier.classify(question)
            assert intent == QuestionIntent.DOCUMENT_SUMMARY, f"Failed for: {question}"
            assert confidence > 0.3, f"Low confidence for: {question}"
    
    def test_entity_analysis_classification(self):
        """Test entity analysis intent classification"""
        test_questions = [
            "Who are the key people mentioned?",
            "What organizations are discussed?",
            "List the entities",
            "What are the key players?"
        ]
        
        for question in test_questions:
            intent, confidence = self.classifier.classify(question)
            assert intent == QuestionIntent.ENTITY_ANALYSIS, f"Failed for: {question}"
            assert confidence > 0.3, f"Low confidence for: {question}"
    
    def test_relationship_analysis_classification(self):
        """Test relationship analysis intent classification"""
        test_questions = [
            "How do X and Y relate?",
            "What connections exist?",
            "Show me the relationships",
            "How are these entities connected?"
        ]
        
        for question in test_questions:
            intent, confidence = self.classifier.classify(question)
            assert intent == QuestionIntent.RELATIONSHIP_ANALYSIS, f"Failed for: {question}"
            assert confidence > 0.3, f"Low confidence for: {question}"
    
    def test_theme_analysis_classification(self):
        """Test theme analysis intent classification"""
        test_questions = [
            "What are the main themes?",
            "What topics are discussed?",
            "What subjects are covered?",
            "What are the central ideas?"
        ]
        
        for question in test_questions:
            intent, confidence = self.classifier.classify(question)
            assert intent == QuestionIntent.THEME_ANALYSIS, f"Failed for: {question}"
            assert confidence > 0.3, f"Low confidence for: {question}"
    
    def test_specific_search_classification(self):
        """Test specific search intent classification"""
        test_questions = [
            "Find information about Microsoft",
            "What does the document say about AI?",
            "Search for details about the merger",
            "Tell me about blockchain"
        ]
        
        for question in test_questions:
            intent, confidence = self.classifier.classify(question)
            assert intent == QuestionIntent.SPECIFIC_SEARCH, f"Failed for: {question}"
            assert confidence > 0.3, f"Low confidence for: {question}"
    
    def test_pagerank_analysis_classification(self):
        """Test PageRank analysis intent classification"""
        test_questions = [
            "What are the most important entities?",
            "Rank the key players by importance",
            "Which entities have the most influence?",
            "Show entity significance"
        ]
        
        for question in test_questions:
            intent, confidence = self.classifier.classify(question)
            assert intent == QuestionIntent.PAGERANK_ANALYSIS, f"Failed for: {question}"
            assert confidence > 0.3, f"Low confidence for: {question}"

class TestToolMapper:
    """Test intent to tool mapping"""
    
    def setup_method(self):
        """Setup for each test"""
        self.mapper = ToolMapper()
    
    def test_document_summary_tools(self):
        """Test tools for document summary"""
        tools = self.mapper.get_tools_for_intent(QuestionIntent.DOCUMENT_SUMMARY)
        
        expected_tools = ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER"]
        assert tools == expected_tools
    
    def test_entity_analysis_tools(self):
        """Test tools for entity analysis"""
        tools = self.mapper.get_tools_for_intent(QuestionIntent.ENTITY_ANALYSIS)
        
        expected_tools = [
            "T01_PDF_LOADER", "T15A_TEXT_CHUNKER", 
            "T23A_SPACY_NER", "T31_ENTITY_BUILDER"
        ]
        assert tools == expected_tools
    
    def test_relationship_analysis_tools(self):
        """Test tools for relationship analysis"""
        tools = self.mapper.get_tools_for_intent(QuestionIntent.RELATIONSHIP_ANALYSIS)
        
        expected_tools = [
            "T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER",
            "T27_RELATIONSHIP_EXTRACTOR", "T34_EDGE_BUILDER"
        ]
        assert tools == expected_tools
    
    def test_pagerank_analysis_tools(self):
        """Test tools for PageRank analysis"""
        tools = self.mapper.get_tools_for_intent(QuestionIntent.PAGERANK_ANALYSIS)
        
        expected_tools = [
            "T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER",
            "T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER", 
            "T34_EDGE_BUILDER", "T68_PAGE_RANK"
        ]
        assert tools == expected_tools
    
    def test_multi_hop_query_tools(self):
        """Test tools for multi-hop queries"""
        tools = self.mapper.get_tools_for_intent(QuestionIntent.MULTI_HOP_QUERY)
        
        expected_tools = [
            "T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER",
            "T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER",
            "T34_EDGE_BUILDER", "T49_MULTI_HOP_QUERY"
        ]
        assert tools == expected_tools

class TestQuestionParser:
    """Test complete question parsing functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.parser = QuestionParser()
    
    def test_basic_question_parsing(self):
        """Test basic question parsing"""
        question = "What is this document about?"
        
        parsed = self.parser.parse_question(question)
        
        assert parsed.original_question == question
        assert parsed.intent == QuestionIntent.DOCUMENT_SUMMARY
        assert parsed.confidence > 0.3
        assert len(parsed.required_tools) > 0
        assert parsed.execution_plan is not None
    
    def test_entity_mention_extraction(self):
        """Test extraction of mentioned entities"""
        question = "What does the document say about Microsoft and Google?"
        
        parsed = self.parser.parse_question(question)
        
        # Should extract proper nouns
        assert "Microsoft" in parsed.entities_mentioned
        assert "Google" in parsed.entities_mentioned
    
    def test_execution_plan_creation(self):
        """Test execution plan creation"""
        question = "How do the entities relate to each other?"
        
        parsed = self.parser.parse_question(question)
        
        assert parsed.execution_plan is not None
        assert len(parsed.execution_plan.steps) > 0
        
        # Check step dependencies
        for i, step in enumerate(parsed.execution_plan.steps):
            if i > 0:
                # Each step should depend on the previous one
                assert step.depends_on is not None
                assert len(step.depends_on) > 0
    
    def test_tool_arguments_creation(self):
        """Test tool argument creation"""
        question = "Analyze the relationships in this document"
        document_path = "/path/to/test.pdf"
        
        parsed = self.parser.parse_question(question, document_path)
        
        # Check that T01 gets file path
        t01_step = None
        for step in parsed.execution_plan.steps:
            if step.tool_id == "T01_PDF_LOADER":
                t01_step = step
                break
        
        assert t01_step is not None
        assert "input_data" in t01_step.arguments
        assert t01_step.arguments["input_data"]["file_path"] == document_path
    
    def test_complex_question_parsing(self):
        """Test parsing of complex questions"""
        complex_questions = [
            "What are the key entities and how do they relate to the main themes?",
            "Find the most important players and show their relationships",
            "Analyze the document structure and extract key connections"
        ]
        
        for question in complex_questions:
            parsed = self.parser.parse_question(question)
            
            assert parsed.original_question == question
            assert parsed.intent is not None
            assert parsed.confidence > 0.0
            assert len(parsed.required_tools) >= 3  # Complex questions need multiple tools
    
    def test_question_variations(self):
        """Test handling of question variations"""
        # Same intent, different phrasing
        variations = [
            ("What is this about?", "Summarize this document", QuestionIntent.DOCUMENT_SUMMARY),
            ("Who is mentioned?", "List the people", QuestionIntent.ENTITY_ANALYSIS),
            ("How do they connect?", "Show relationships", QuestionIntent.RELATIONSHIP_ANALYSIS)
        ]
        
        for q1, q2, expected_intent in variations:
            parsed1 = self.parser.parse_question(q1)
            parsed2 = self.parser.parse_question(q2)
            
            assert parsed1.intent == expected_intent
            assert parsed2.intent == expected_intent
            # Should use same tools for same intent
            assert parsed1.required_tools == parsed2.required_tools

# Main test execution
if __name__ == "__main__":
    print("🔧 Running Question Parsing Tests")
    print("=" * 50)
    
    # Test intent classifier
    print("\n1. Testing Intent Classifier...")
    test_classifier = TestIntentClassifier()
    test_classifier.setup_method()
    
    try:
        test_classifier.test_document_summary_classification()
        print("   ✅ Document summary classification")
        
        test_classifier.test_entity_analysis_classification()
        print("   ✅ Entity analysis classification")
        
        test_classifier.test_relationship_analysis_classification()
        print("   ✅ Relationship analysis classification")
        
        test_classifier.test_theme_analysis_classification()
        print("   ✅ Theme analysis classification")
        
        test_classifier.test_specific_search_classification()
        print("   ✅ Specific search classification")
        
        test_classifier.test_pagerank_analysis_classification()
        print("   ✅ PageRank analysis classification")
        
    except Exception as e:
        print(f"   ❌ Intent classifier test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test tool mapper
    print("\n2. Testing Tool Mapper...")
    test_mapper = TestToolMapper()
    test_mapper.setup_method()
    
    try:
        test_mapper.test_document_summary_tools()
        print("   ✅ Document summary tool mapping")
        
        test_mapper.test_entity_analysis_tools()
        print("   ✅ Entity analysis tool mapping")
        
        test_mapper.test_relationship_analysis_tools()
        print("   ✅ Relationship analysis tool mapping")
        
        test_mapper.test_pagerank_analysis_tools()
        print("   ✅ PageRank analysis tool mapping")
        
        test_mapper.test_multi_hop_query_tools()
        print("   ✅ Multi-hop query tool mapping")
        
    except Exception as e:
        print(f"   ❌ Tool mapper test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test question parser
    print("\n3. Testing Question Parser...")
    test_parser = TestQuestionParser()
    test_parser.setup_method()
    
    try:
        test_parser.test_basic_question_parsing()
        print("   ✅ Basic question parsing")
        
        test_parser.test_entity_mention_extraction()
        print("   ✅ Entity mention extraction")
        
        test_parser.test_execution_plan_creation()
        print("   ✅ Execution plan creation")
        
        test_parser.test_tool_arguments_creation()
        print("   ✅ Tool arguments creation")
        
        test_parser.test_complex_question_parsing()
        print("   ✅ Complex question parsing")
        
        test_parser.test_question_variations()
        print("   ✅ Question variations handling")
        
    except Exception as e:
        print(f"   ❌ Question parser test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Question Parsing Tests completed")