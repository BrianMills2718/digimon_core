"""
End-to-End Natural Language Interface Testing
Tests the complete natural language workflow: question → tool execution → response
"""
import pytest
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.interface.nl_interface import NaturalLanguageInterface, create_test_interface
from src.interface.session_manager import SessionManager

class TestNLEndToEnd:
    """Test complete natural language workflow"""
    
    def setup_method(self):
        """Setup for each test"""
        self.interface = None
    
    async def _get_interface(self):
        """Get initialized interface"""
        if not self.interface:
            self.interface = await create_test_interface()
        return self.interface
    
    @pytest.mark.asyncio
    async def test_interface_initialization(self):
        """Test interface can be initialized"""
        interface = await self._get_interface()
        
        assert interface.initialization_complete == True
        
        capabilities = interface.list_capabilities()
        assert capabilities["initialization_complete"] == True
        assert capabilities["mcp_status"]["mcp_client_available"] == True
    
    @pytest.mark.asyncio
    async def test_document_loading(self):
        """Test document loading functionality"""
        interface = await self._get_interface()
        
        # Test with non-existent document
        success = await interface.load_document("nonexistent.pdf")
        assert success == False
        
        # Test with valid file path (create a test file)
        test_file = Path("test_document.txt")
        test_file.write_text("This is a test document with sample content.")
        
        try:
            success = await interface.load_document(str(test_file))
            assert success == True
            
            # Check document context
            assert interface.current_document is not None
            assert interface.current_document.title == "test_document"
            assert interface.current_document.file_path.endswith("test_document.txt")
            
        finally:
            # Clean up
            if test_file.exists():
                test_file.unlink()
    
    @pytest.mark.asyncio
    async def test_question_without_document(self):
        """Test question handling without loaded document"""
        interface = await self._get_interface()
        
        # Ensure no document is loaded
        interface.current_document = None
        
        response = await interface.ask_question("What is this about?")
        assert "load a document first" in response.lower()
    
    @pytest.mark.asyncio
    async def test_basic_question_workflow(self):
        """Test basic question processing workflow"""
        interface = await self._get_interface()
        
        # Create test document
        test_file = Path("test_workflow.txt")
        test_content = """
        This is a test document about Microsoft and Google.
        Microsoft develops software while Google focuses on search.
        Both companies are leaders in technology.
        """
        test_file.write_text(test_content)
        
        try:
            # Load document
            await interface.load_document(str(test_file))
            
            # Ask a basic question
            response = await interface.ask_question("What is this document about?")
            
            # Verify response structure
            assert isinstance(response, str)
            assert len(response) > 50  # Should be a substantial response
            assert "error" not in response.lower()  # No error messages
            
            # Response should contain some analysis
            assert any(word in response.lower() for word in ['document', 'analysis', 'entities', 'microsoft', 'google'])
            
        finally:
            if test_file.exists():
                test_file.unlink()
    
    @pytest.mark.asyncio
    async def test_different_question_types(self):
        """Test different types of questions"""
        interface = await self._get_interface()
        
        # Create test document
        test_file = Path("test_questions.txt")
        test_content = """
        Apple Inc. is a technology company founded by Steve Jobs.
        The company is located in Cupertino, California.
        Apple develops the iPhone and works with suppliers worldwide.
        Tim Cook is the current CEO who succeeded Steve Jobs.
        """
        test_file.write_text(test_content)
        
        try:
            await interface.load_document(str(test_file))
            
            # Test different question types
            question_types = [
                ("What is this document about?", "summary"),
                ("Who are the key people mentioned?", "entities"),
                ("How do Apple and Steve Jobs relate?", "relationships"),
                ("What are the main themes?", "themes")
            ]
            
            session_id = "test_session"
            
            for question, expected_content in question_types:
                response = await interface.ask_question(question, session_id)
                
                assert isinstance(response, str)
                assert len(response) > 30
                assert "error" not in response.lower()
                
                # Check that response contains relevant content
                if expected_content == "entities":
                    assert any(name in response for name in ["Apple", "Steve Jobs", "Tim Cook"])
                elif expected_content == "relationships":
                    assert any(word in response.lower() for word in ["relationship", "connection", "relate"])
            
        finally:
            if test_file.exists():
                test_file.unlink()
    
    @pytest.mark.asyncio
    async def test_session_management(self):
        """Test session management and context"""
        interface = await self._get_interface()
        
        # Create test document
        test_file = Path("test_session.txt")
        test_file.write_text("This is a test document for session management.")
        
        try:
            await interface.load_document(str(test_file))
            
            session_id = "session_test"
            
            # Ask multiple questions in same session
            question1 = "What is this document about?"
            response1 = await interface.ask_question(question1, session_id)
            
            question2 = "What are the key entities?"
            response2 = await interface.ask_question(question2, session_id)
            
            # Check session context
            context = interface.get_session_context(session_id)
            
            assert "interaction_count" in context
            assert context["interaction_count"] == 2
            assert len(context["interactions"]) == 2
            
            # Check interaction details
            interactions = context["interactions"]
            assert interactions[0].question == question1
            assert interactions[1].question == question2
            
        finally:
            if test_file.exists():
                test_file.unlink()
    
    @pytest.mark.asyncio
    async def test_advanced_response_details(self):
        """Test advanced response with detailed metadata"""
        interface = await self._get_interface()
        
        # Create test document
        test_file = Path("test_advanced.txt")
        test_file.write_text("Microsoft and Google are technology companies that compete in cloud services.")
        
        try:
            await interface.load_document(str(test_file))
            
            # Get advanced response
            nl_response = await interface.ask_question_advanced(
                "What are the relationships between entities?",
                "advanced_session"
            )
            
            # Check response structure
            assert hasattr(nl_response, 'answer')
            assert hasattr(nl_response, 'confidence')
            assert hasattr(nl_response, 'execution_time')
            assert hasattr(nl_response, 'tools_used')
            assert hasattr(nl_response, 'provenance_info')
            
            # Check values
            assert isinstance(nl_response.answer, str)
            assert len(nl_response.answer) > 30
            assert nl_response.confidence >= 0.0
            assert nl_response.execution_time >= 0.0
            assert isinstance(nl_response.tools_used, list)
            
        finally:
            if test_file.exists():
                test_file.unlink()
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test graceful error handling"""
        interface = await self._get_interface()
        
        # Create test document
        test_file = Path("test_errors.txt")
        test_file.write_text("Simple test content.")
        
        try:
            await interface.load_document(str(test_file))
            
            # Test with malformed question
            response = await interface.ask_question("")
            assert isinstance(response, str)
            # Should handle gracefully, not crash
            
            # Test with very long question
            long_question = "What about " + "test " * 200 + "?"
            response = await interface.ask_question(long_question)
            assert isinstance(response, str)
            # Should handle gracefully
            
        finally:
            if test_file.exists():
                test_file.unlink()
    
    def test_capabilities_listing(self):
        """Test capabilities listing"""
        # This can be synchronous
        interface = NaturalLanguageInterface()
        capabilities = interface.list_capabilities()
        
        assert "supported_question_types" in capabilities
        assert "supported_document_types" in capabilities
        assert "current_document" in capabilities
        assert "mcp_status" in capabilities
        assert "initialization_complete" in capabilities
        
        # Check question types
        question_types = capabilities["supported_question_types"]
        assert len(question_types) >= 8  # Should support multiple types
        
        # Check document types
        doc_types = capabilities["supported_document_types"]
        assert ".pdf" in doc_types
        assert ".txt" in doc_types
    
    def test_help_system(self):
        """Test help system"""
        interface = NaturalLanguageInterface()
        help_text = interface.get_help()
        
        assert isinstance(help_text, str)
        assert len(help_text) > 200  # Should be comprehensive
        assert "Getting Started" in help_text
        assert "Supported Question Types" in help_text
        assert "Example Session" in help_text
    
    @pytest.mark.asyncio
    async def test_concurrent_questions(self):
        """Test handling concurrent questions"""
        interface = await self._get_interface()
        
        # Create test document
        test_file = Path("test_concurrent.txt")
        test_file.write_text("Test document for concurrent processing with multiple entities and relationships.")
        
        try:
            await interface.load_document(str(test_file))
            
            # Create multiple questions
            questions = [
                "What is this about?",
                "What entities are mentioned?",
                "What are the themes?"
            ]
            
            # Execute concurrently
            tasks = [
                interface.ask_question(q, f"session_{i}")
                for i, q in enumerate(questions)
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should complete successfully
            for i, response in enumerate(responses):
                assert not isinstance(response, Exception), f"Question {i} failed: {response}"
                assert isinstance(response, str)
                assert len(response) > 20
            
        finally:
            if test_file.exists():
                test_file.unlink()

class TestSessionManager:
    """Test session manager functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.session_manager = SessionManager()
    
    def test_session_creation(self):
        """Test session creation"""
        session_id = self.session_manager.create_session()
        
        assert session_id is not None
        assert len(session_id) > 0
        assert session_id in self.session_manager.sessions
    
    def test_interaction_tracking(self):
        """Test interaction tracking"""
        session_id = self.session_manager.create_session("test_interactions")
        
        # Add interactions
        question1 = "What is this about?"
        response1 = "This is a test response"
        
        self.session_manager.add_interaction(session_id, question1, response1)
        
        interactions = self.session_manager.get_session_interactions(session_id)
        assert len(interactions) == 1
        assert interactions[0].question == question1
    
    def test_session_context(self):
        """Test session context retrieval"""
        session_id = self.session_manager.create_session("test_context")
        
        # Add some interactions
        self.session_manager.add_interaction(session_id, "Q1", "A1")
        self.session_manager.add_interaction(session_id, "Q2", "A2")
        
        context = self.session_manager.get_session_context(session_id)
        
        assert context["session_id"] == session_id
        assert context["interaction_count"] == 2
        assert len(context["interactions"]) == 2
        assert context["active"] == True
    
    def test_session_summary(self):
        """Test session summarization"""
        session_id = self.session_manager.create_session("test_summary")
        
        # Add interaction with keywords
        self.session_manager.add_interaction(session_id, "Who are the entities?", "Response")
        self.session_manager.add_interaction(session_id, "How do they relate?", "Response")
        
        summary = self.session_manager.get_session_summary(session_id)
        
        assert summary["session_id"] == session_id
        assert summary["interaction_count"] == 2
        assert "entities" in summary["topics_discussed"]
        assert "relationships" in summary["topics_discussed"]
    
    def test_session_cleanup(self):
        """Test session cleanup"""
        # Create session manager with short timeout
        sm = SessionManager(session_timeout=1)  # 1 second timeout
        
        session_id = sm.create_session("test_cleanup")
        assert session_id in sm.sessions
        
        # Wait for timeout
        import time
        time.sleep(2)
        
        # Trigger cleanup
        sm._cleanup_sessions()
        
        # Session should be removed
        assert session_id not in sm.sessions

# Main test execution
if __name__ == "__main__":
    print("🔧 Running End-to-End Natural Language Interface Tests")
    print("=" * 60)
    
    # Test session manager first (synchronous)
    print("\n1. Testing Session Manager...")
    test_session = TestSessionManager()
    
    try:
        test_session.setup_method()
        test_session.test_session_creation()
        print("   ✅ Session creation")
        
        test_session.setup_method()
        test_session.test_interaction_tracking()
        print("   ✅ Interaction tracking")
        
        test_session.setup_method()
        test_session.test_session_context()
        print("   ✅ Session context")
        
        test_session.setup_method()
        test_session.test_session_summary()
        print("   ✅ Session summary")
        
    except Exception as e:
        print(f"   ❌ Session manager test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test natural language interface (async)
    print("\n2. Testing Natural Language Interface...")
    
    async def run_nl_tests():
        test_nl = TestNLEndToEnd()
        
        try:
            # Test initialization
            await test_nl.test_interface_initialization()
            print("   ✅ Interface initialization")
            
            # Test document loading
            await test_nl.test_document_loading()
            print("   ✅ Document loading")
            
            # Test question without document
            await test_nl.test_question_without_document()
            print("   ✅ Question handling without document")
            
            # Test basic workflow
            await test_nl.test_basic_question_workflow()
            print("   ✅ Basic question workflow")
            
            # Test error handling
            await test_nl.test_error_handling()
            print("   ✅ Error handling")
            
            # Test capabilities
            test_nl.test_capabilities_listing()
            print("   ✅ Capabilities listing")
            
            # Test help
            test_nl.test_help_system()
            print("   ✅ Help system")
            
        except Exception as e:
            print(f"   ❌ Natural language interface test failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Run async tests
    asyncio.run(run_nl_tests())
    
    print("\n✅ End-to-End Natural Language Interface Tests completed")