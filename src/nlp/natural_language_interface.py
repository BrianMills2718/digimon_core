"""
Natural Language Interface for KGAS
Provides high-level interface for natural language question answering
"""
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from .question_parser import QuestionParser, QuestionIntent
from .response_generator import ResponseGenerator
from ..execution.mcp_executor import MCPExecutor, PipelineManager
from ..execution.dynamic_executor import DynamicExecutor
from .advanced_intent_classifier import AdvancedIntentClassifier
from .question_complexity_analyzer import QuestionComplexityAnalyzer
from .context_extractor import ContextExtractor
from .tool_chain_generator import ToolChainGenerator

logger = logging.getLogger(__name__)

class NaturalLanguageInterface:
    """
    High-level natural language interface for KGAS
    Connects question parsing, tool execution, and response generation
    """
    
    def __init__(self, service_manager):
        self.service_manager = service_manager
        self.question_parser = QuestionParser()
        self.response_generator = ResponseGenerator()
        self.mcp_executor = MCPExecutor()
        self.pipeline_manager = PipelineManager(self.mcp_executor)
        self.current_document_path = None
        
        # Phase B components
        self.use_advanced_analysis = True  # Flag to enable/disable Phase B
        self.advanced_intent_classifier = AdvancedIntentClassifier()
        self.complexity_analyzer = QuestionComplexityAnalyzer()
        self.context_extractor = ContextExtractor()
        self.tool_chain_generator = ToolChainGenerator()
        self.dynamic_executor = DynamicExecutor(self.mcp_executor)
        
        # Store last result for testing/debugging
        self.last_result = None
    
    async def initialize(self):
        """Initialize the interface components"""
        try:
            logger.info("Initializing Natural Language Interface")
            
            # Components are already initialized in constructors
            # Just verify MCP executor is ready
            stats = self.mcp_executor.get_execution_stats()
            
            if not stats.get('mcp_client_available'):
                raise RuntimeError("MCP client not available")
            
            logger.info("Natural Language Interface initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Natural Language Interface: {e}")
            raise
    
    async def load_document(self, file_path: str) -> bool:
        """
        Load a document for processing
        Returns True if successful, False otherwise
        """
        try:
            # Verify file exists
            if not Path(file_path).exists():
                logger.error(f"Document not found: {file_path}")
                return False
            
            # Store current document path
            self.current_document_path = file_path
            logger.info(f"Document loaded: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load document {file_path}: {e}")
            return False
    
    async def ask_question(self, question: str) -> str:
        """
        Process a natural language question and return an answer
        Enhanced with Phase B advanced analysis when enabled
        """
        try:
            logger.info(f"Processing question: {question}")
            
            # Phase B: Advanced Analysis (if enabled)
            advanced_analysis = None
            context_result = None  # Initialize for later use
            if self.use_advanced_analysis:
                try:
                    # Perform advanced analysis
                    intent_result = self.advanced_intent_classifier.classify(question)
                    complexity_result = self.complexity_analyzer.analyze(question, intent_result)
                    context_result = self.context_extractor.extract(question)
                    
                    # Generate optimized tool chain
                    tool_chain = self.tool_chain_generator.generate_chain(
                        intent_result, complexity_result, context_result, question
                    )
                    
                    # Store analysis results
                    advanced_analysis = {
                        'intent': intent_result.primary_intent,
                        'complexity': complexity_result.level,
                        'confidence': intent_result.confidence,
                        'ambiguity_level': context_result.ambiguity_level,
                        'missing_context': context_result.missing_context,
                        'has_temporal_context': context_result.has_temporal_context,
                        'temporal_constraints': context_result.temporal_constraints,
                        'parallelizable_components': complexity_result.parallelizable_components,
                        'execution_strategy': complexity_result.execution_strategy,
                        'tool_chain': tool_chain,
                        'secondary_intents': intent_result.secondary_intents,
                        'context_result': context_result  # Store for dynamic execution
                    }
                    
                    logger.info(f"Advanced analysis complete: {intent_result.primary_intent.value}, "
                               f"complexity: {complexity_result.level.value}, "
                               f"confidence: {intent_result.confidence:.2f}")
                    
                except Exception as e:
                    logger.warning(f"Advanced analysis failed, falling back to basic: {e}")
                    self.last_result = type('Result', (), {
                        'status': 'success',
                        'fallback_used': True,
                        'warning': 'Advanced analysis unavailable, using basic analysis'
                    })()
            
            # Phase A: Basic parsing (fallback or when advanced disabled)
            parsed = self.question_parser.parse_question(question)
            logger.info(f"Question parsed with intent: {parsed.intent.value}")
            
            # Execute with dynamic executor if advanced analysis is available
            if advanced_analysis and advanced_analysis['tool_chain']:
                # Use dynamic execution for Phase B
                execution_result = await self.dynamic_executor.execute_dynamic_chain(
                    tool_chain=advanced_analysis['tool_chain'],
                    question=question,
                    context=advanced_analysis.get('context_result'),
                    current_document_path=self.current_document_path
                )
            else:
                # Fall back to Phase A execution
                execution_plan = parsed.execution_plan
                
                # Update execution plan with current document if needed
                if self.current_document_path and execution_plan.steps:
                    # Update first step (usually T01_PDF_LOADER) with current document
                    first_step = execution_plan.steps[0]
                    if first_step.tool_id == "T01_PDF_LOADER":
                        first_step.arguments["input_data"]["file_path"] = self.current_document_path
                
                # Execute the plan
                execution_result = await self.pipeline_manager.execute_pipeline(
                    execution_plan, 
                    question
                )
            
            # Enhanced result object for testing
            self.last_result = type('Result', (), {
                'status': 'success',
                'advanced_analysis': type('AdvancedAnalysis', (), advanced_analysis or {})() if advanced_analysis else None,
                'tools_executed': list(execution_result.tool_outputs.keys()) if hasattr(execution_result, 'tool_outputs') else [],
                'entities': self._extract_entities_from_results(execution_result.tool_outputs) if hasattr(execution_result, 'tool_outputs') else [],
                'response': '',  # Will be set below
                'execution_metadata': execution_result.execution_metadata if hasattr(execution_result, 'execution_metadata') else {
                    'parallelized': advanced_analysis.get('parallelizable_components', 0) > 0 if advanced_analysis else False,
                    'execution_strategy': advanced_analysis.get('execution_strategy', 'sequential') if advanced_analysis else 'sequential',
                    'execution_time': execution_result.total_execution_time if hasattr(execution_result, 'total_execution_time') else 0,
                    'sequential_estimate': len(execution_result.tool_outputs) * 1.0 if hasattr(execution_result, 'tool_outputs') else 3.0
                },
                'confidence_disclaimer': self._get_confidence_disclaimer(advanced_analysis) if advanced_analysis else None,
                'tool_parameters': {'time_filter': advanced_analysis.get('temporal_constraints', [None])[0] if advanced_analysis and advanced_analysis.get('temporal_constraints') else None},
                'fallback_used': False,
                'warning': None
            })()
            
            # Generate response
            response = self.response_generator.generate_response(
                question=question,
                tool_results=execution_result.tool_outputs,
                intent=parsed.intent,
                provenance_data=execution_result.execution_metadata
            )
            
            # Store response in result object
            self.last_result.response = response
            
            logger.info(f"Generated response of {len(response)} characters")
            return response
            
        except Exception as e:
            logger.error(f"Error processing question '{question}': {e}")
            # Set a basic error result for testing
            self.last_result = type('Result', (), {
                'status': 'error',
                'error': str(e),
                'advanced_analysis': None,
                'tools_executed': [],
                'entities': [],
                'response': f"I encountered an error while processing your question: {str(e)}",
                'execution_metadata': {},
                'confidence_disclaimer': None,
                'tool_parameters': {},
                'fallback_used': True,
                'warning': str(e)
            })()
            return f"I encountered an error while processing your question: {str(e)}"
    
    def _convert_tool_chain_to_execution_plan(self, tool_chain, fallback_plan):
        """Convert Phase B tool chain to Phase A execution plan format"""
        from ..execution.mcp_executor import ExecutionPlan, ExecutionStep
        
        steps = []
        for tool_step in tool_chain.steps:
            step = ExecutionStep(
                tool_id=tool_step.tool_id,
                arguments={
                    "input_data": {},
                    "parameters": tool_step.parameters
                },
                depends_on=tool_step.depends_on
            )
            steps.append(step)
        
        return ExecutionPlan(
            steps=steps,
            parallel_execution_possible=tool_chain.can_parallelize,
            estimated_duration=tool_chain.estimated_time
        )
    
    def _extract_entities_from_results(self, tool_outputs):
        """Extract entities from tool execution results"""
        entities = []
        for tool_id, output in tool_outputs.items():
            if tool_id == "T23A_SPACY_NER" and isinstance(output, dict):
                if "entities" in output:
                    entities.extend(output["entities"])
                elif "data" in output and isinstance(output["data"], dict) and "entities" in output["data"]:
                    entities.extend(output["data"]["entities"])
        return entities
    
    def _get_confidence_disclaimer(self, advanced_analysis):
        """Generate confidence disclaimer for low-confidence responses"""
        if advanced_analysis and advanced_analysis.get('confidence', 1.0) < 0.7:
            return "Note: I'm less confident about this answer due to ambiguity in the question."
        return None
    
    async def ask_questions_batch(self, questions: list[str]) -> list[str]:
        """
        Process multiple questions in batch
        """
        responses = []
        
        for question in questions:
            response = await self.ask_question(question)
            responses.append(response)
        
        return responses
    
    def get_supported_intents(self) -> list[str]:
        """Get list of supported question intents"""
        return [intent.value for intent in QuestionIntent]
    
    def get_interface_stats(self) -> Dict[str, Any]:
        """Get interface statistics"""
        return {
            "current_document": self.current_document_path,
            "supported_intents": self.get_supported_intents(),
            "mcp_executor_stats": self.mcp_executor.get_execution_stats()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of all components"""
        health = {
            "overall": "healthy",
            "components": {}
        }
        
        try:
            # Check question parser
            test_question = "What is this about?"
            parsed = self.question_parser.parse_question(test_question)
            health["components"]["question_parser"] = "healthy" if parsed else "failed"
            
            # Check MCP executor
            executor_stats = self.mcp_executor.get_execution_stats()
            health["components"]["mcp_executor"] = "healthy" if executor_stats.get("mcp_client_available") else "failed"
            
            # Check response generator
            test_response = self.response_generator.generate_response(
                question="test",
                tool_results={},
                intent=QuestionIntent.DOCUMENT_SUMMARY
            )
            health["components"]["response_generator"] = "healthy" if test_response else "failed"
            
            # Overall health
            if any(status == "failed" for status in health["components"].values()):
                health["overall"] = "unhealthy"
            
        except Exception as e:
            health["overall"] = "unhealthy"
            health["error"] = str(e)
        
        return health