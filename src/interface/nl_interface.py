"""
Natural Language Interface for KGAS
Main interface for natural language document analysis
"""
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
import time
from pathlib import Path

# Local imports
from ..nlp.question_parser import QuestionParser, ParsedQuestion
from ..nlp.response_generator import ResponseGenerator
from ..execution.mcp_executor import MCPExecutor, PipelineManager
from ..mcp.mcp_server import MCPServer
from .session_manager import SessionManager

logger = logging.getLogger(__name__)

@dataclass
class DocumentContext:
    """Context about loaded document"""
    file_path: str
    title: str
    loaded_at: float
    metadata: Dict[str, Any]

@dataclass
class NLResponse:
    """Natural language response with metadata"""
    answer: str
    confidence: float
    execution_time: float
    tools_used: List[str]
    provenance_info: Dict[str, Any]
    session_id: Optional[str] = None

class NaturalLanguageInterface:
    """Main interface for natural language document analysis"""
    
    def __init__(self, service_manager=None):
        # Initialize components
        self.question_parser = QuestionParser()
        self.response_generator = ResponseGenerator()
        
        # Initialize MCP components
        if service_manager:
            self.mcp_executor = MCPExecutor()
            self.pipeline_manager = PipelineManager(self.mcp_executor)
        else:
            # Initialize service manager if not provided
            from ..core.service_manager import ServiceManager
            service_manager = ServiceManager()
            self.mcp_executor = MCPExecutor()
            self.pipeline_manager = PipelineManager(self.mcp_executor)
        
        self.session_manager = SessionManager()
        
        # Document context
        self.current_document: Optional[DocumentContext] = None
        self.initialization_complete = False
        
        logger.info("Natural Language Interface initialized")
    
    async def initialize(self):
        """Initialize the interface and all components"""
        try:
            logger.info("Initializing Natural Language Interface...")
            
            # Test MCP connectivity
            stats = self.mcp_executor.get_execution_stats()
            if stats['mcp_client_available']:
                logger.info(f"MCP client available: {stats['mcp_client_type']}")
            else:
                logger.warning("MCP client not available")
            
            self.initialization_complete = True
            logger.info("Natural Language Interface initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Natural Language Interface: {e}")
            raise
    
    async def load_document(self, file_path: str) -> bool:
        """Load a document for analysis"""
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                raise FileNotFoundError(f"Document not found: {file_path}")
            
            # Create document context
            self.current_document = DocumentContext(
                file_path=str(file_path_obj.absolute()),
                title=file_path_obj.stem,
                loaded_at=time.time(),
                metadata={
                    'file_size': file_path_obj.stat().st_size,
                    'file_type': file_path_obj.suffix
                }
            )
            
            logger.info(f"Document loaded: {self.current_document.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load document {file_path}: {e}")
            return False
    
    async def ask_question(self, question: str, session_id: str = None) -> str:
        """Process natural language question and return answer"""
        
        if not self.initialization_complete:
            await self.initialize()
        
        if not self.current_document:
            return "Please load a document first using load_document() method."
        
        start_time = time.time()
        
        try:
            logger.info(f"Processing question: {question}")
            
            # 1. Parse the question
            parsed_question = self.question_parser.parse_question(
                question, 
                self.current_document.file_path
            )
            
            logger.info(f"Question intent: {parsed_question.intent.value} "
                       f"(confidence: {parsed_question.confidence:.2f})")
            
            # 2. Validate execution plan
            plan_issues = self.pipeline_manager.validate_execution_plan(parsed_question.execution_plan)
            if plan_issues:
                logger.warning(f"Execution plan issues: {plan_issues}")
            
            # 3. Execute the required tools via MCP
            execution_result = await self.pipeline_manager.execute_pipeline(
                parsed_question.execution_plan,
                question
            )
            
            # 4. Check for execution errors
            if execution_result.failure_count > 0:
                logger.error(f"Execution had {execution_result.failure_count} failures: {execution_result.errors}")
                
                if execution_result.success_count == 0:
                    return f"I encountered errors processing your question: {'; '.join(execution_result.errors)}"
            
            # 5. Generate natural language response
            response_text = self.response_generator.generate_response(
                question=question,
                tool_results=execution_result.tool_outputs,
                intent=parsed_question.intent,
                provenance_data=execution_result.execution_metadata
            )
            
            execution_time = time.time() - start_time
            
            # 6. Store in session for context
            if session_id:
                nl_response = NLResponse(
                    answer=response_text,
                    confidence=parsed_question.confidence,
                    execution_time=execution_time,
                    tools_used=list(execution_result.tool_outputs.keys()),
                    provenance_info=execution_result.execution_metadata,
                    session_id=session_id
                )
                
                self.session_manager.add_interaction(session_id, question, nl_response)
            
            logger.info(f"Question processed successfully in {execution_time:.2f}s")
            return response_text
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"I encountered an error processing your question: {str(e)}"
            logger.error(f"Question processing failed after {execution_time:.2f}s: {e}")
            return error_msg
    
    async def ask_question_advanced(self, question: str, session_id: str = None) -> NLResponse:
        """Process question and return detailed response object"""
        
        response_text = await self.ask_question(question, session_id)
        
        # Get the stored response if available
        if session_id:
            interactions = self.session_manager.get_session_interactions(session_id)
            if interactions:
                return interactions[-1].response
        
        # Create basic response if not stored
        return NLResponse(
            answer=response_text,
            confidence=0.5,
            execution_time=0.0,
            tools_used=[],
            provenance_info={},
            session_id=session_id
        )
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get context for a session"""
        return self.session_manager.get_session_context(session_id)
    
    def list_capabilities(self) -> Dict[str, Any]:
        """List current interface capabilities"""
        return {
            "supported_question_types": [
                "Document summary (What is this document about?)",
                "Entity analysis (Who are the key players?)", 
                "Relationship analysis (How do entities relate?)",
                "Theme analysis (What are the main themes?)",
                "Specific search (Find information about X)",
                "Graph analysis (Show network structure)",
                "PageRank analysis (Rank entities by importance)",
                "Multi-hop queries (Complex relationship paths)"
            ],
            "supported_document_types": [".pdf", ".txt", ".docx"],
            "current_document": {
                "loaded": self.current_document is not None,
                "title": self.current_document.title if self.current_document else None,
                "file_path": self.current_document.file_path if self.current_document else None
            },
            "mcp_status": self.mcp_executor.get_execution_stats(),
            "initialization_complete": self.initialization_complete
        }
    
    def get_help(self) -> str:
        """Get help text for using the interface"""
        return """
🤖 KGAS Natural Language Interface Help

**Getting Started:**
1. Load a document: interface.load_document("path/to/document.pdf")
2. Ask questions: interface.ask_question("What is this document about?")

**Supported Question Types:**
• Document Summary: "What is this document about?", "Summarize the main points"
• Entity Analysis: "Who are the key people?", "What organizations are mentioned?"
• Relationship Analysis: "How do X and Y relate?", "What connections exist?"
• Theme Analysis: "What are the main themes?", "What topics are discussed?"
• Specific Search: "Find information about X", "What does it say about Y?"
• Graph Analysis: "Show the network structure", "How are entities connected?"
• PageRank Analysis: "What are the most important entities?", "Rank by importance"
• Multi-hop Queries: "How is X connected to Y?", "Show indirect connections"

**Session Management:**
• Use session_id parameter to maintain conversation context
• Get session context: interface.get_session_context(session_id)

**Advanced Usage:**
• Detailed responses: interface.ask_question_advanced(question, session_id)
• List capabilities: interface.list_capabilities()
• Check status: interface.get_help()

**Example Session:**
```python
interface = NaturalLanguageInterface()
await interface.initialize()
await interface.load_document("research_paper.pdf")

response = await interface.ask_question("What are the main findings?", "session_1")
print(response)

follow_up = await interface.ask_question("Who are the key researchers?", "session_1")
print(follow_up)
```
"""

# Convenience functions for testing and demos
async def create_test_interface():
    """Create a test interface for development"""
    interface = NaturalLanguageInterface()
    await interface.initialize()
    return interface

async def demo_natural_language_interface():
    """Demonstrate the natural language interface"""
    print("🤖 KGAS Natural Language Interface Demo")
    print("=" * 50)
    
    try:
        # Create interface
        interface = await create_test_interface()
        
        # Show capabilities
        capabilities = interface.list_capabilities()
        print(f"\n📋 Interface Status:")
        print(f"   Initialization: {'✅' if capabilities['initialization_complete'] else '❌'}")
        print(f"   MCP Client: {'✅' if capabilities['mcp_status']['mcp_client_available'] else '❌'}")
        
        # Test document loading (if test document exists)
        test_doc_path = "tests/fixtures/sample_document.pdf"
        if Path(test_doc_path).exists():
            print(f"\n📄 Loading test document...")
            success = await interface.load_document(test_doc_path)
            print(f"   Document loading: {'✅' if success else '❌'}")
            
            if success:
                # Test questions
                test_questions = [
                    "What is this document about?",
                    "Who are the key entities mentioned?",
                    "What are the main themes?"
                ]
                
                session_id = "demo_session"
                
                for i, question in enumerate(test_questions, 1):
                    print(f"\n🤔 Question {i}: {question}")
                    
                    try:
                        response = await interface.ask_question(question, session_id)
                        print(f"🤖 Response: {response[:200]}...")
                        
                    except Exception as e:
                        print(f"❌ Error: {e}")
                
                # Show session context
                context = interface.get_session_context(session_id)
                print(f"\n📊 Session Context: {len(context.get('interactions', []))} interactions")
        
        else:
            print(f"\n⚠️  Test document not found: {test_doc_path}")
            print("   Create a test document to run full demo")
        
        print("\n✅ Natural Language Interface demo completed")
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(demo_natural_language_interface())