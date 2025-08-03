"""
Natural Language Question Parser
Converts natural language questions into structured tool execution plans
"""
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class QuestionIntent(Enum):
    """Types of question intents"""
    DOCUMENT_SUMMARY = "document_summary"
    ENTITY_ANALYSIS = "entity_analysis" 
    RELATIONSHIP_ANALYSIS = "relationship_analysis"
    THEME_ANALYSIS = "theme_analysis"
    SPECIFIC_SEARCH = "specific_search"
    GRAPH_ANALYSIS = "graph_analysis"
    PAGERANK_ANALYSIS = "pagerank_analysis"
    MULTI_HOP_QUERY = "multi_hop_query"

@dataclass
class ParsedQuestion:
    """Parsed question with execution plan"""
    original_question: str
    intent: QuestionIntent
    entities_mentioned: List[str]
    required_tools: List[str]
    execution_plan: 'ExecutionPlan'
    confidence: float

@dataclass 
class ExecutionPlan:
    """Execution plan for tools"""
    steps: List['ExecutionStep']
    parallel_execution_possible: bool = False
    estimated_duration: float = 0.0

@dataclass
class ExecutionStep:
    """Individual execution step"""
    tool_id: str
    arguments: Dict[str, Any]
    depends_on: List[str] = None
    optional: bool = False

class IntentClassifier:
    """Classify question intent based on keywords and patterns"""
    
    def __init__(self):
        self.intent_patterns = {
            QuestionIntent.DOCUMENT_SUMMARY: [
                r'\b(what.*about|summarize|summary|main points?|overview|gist)\b',
                r'\b(document.*about|paper.*about|content.*summary)\b',
                r'\b(key findings?|main ideas?)\b'
            ],
            QuestionIntent.ENTITY_ANALYSIS: [
                r'\b(who|what entities?|people mentioned|organizations?|companies?)\b',
                r'\b(key players?|main actors?|stakeholders?)\b',
                r'\b(names?.*mentioned|persons?.*involved)\b'
            ],
            QuestionIntent.RELATIONSHIP_ANALYSIS: [
                r'\b(how.*relate|relationships?|connections?|linked)\b',
                r'\b(interact|associated|connected|tied)\b',
                r'\b(between.*and|relate.*to)\b'
            ],
            QuestionIntent.THEME_ANALYSIS: [
                r'\b(themes?|topics?|subjects?|categories)\b',
                r'\b(main.*themes?|key.*topics?|central.*ideas?)\b',
                r'\b(what.*discussed|areas?.*covered)\b'
            ],
            QuestionIntent.SPECIFIC_SEARCH: [
                r'\b(find.*about|information.*about|details.*about)\b',
                r'\b(what.*say.*about|mentions?.*of)\b',
                r'\b(search.*for|look.*for)\b'
            ],
            QuestionIntent.GRAPH_ANALYSIS: [
                r'\b(network|graph|structure|hierarchy)\b',
                r'\b(connected.*how|paths?.*between|degrees?.*separation)\b',
                r'\b(centrality|importance.*network)\b'
            ],
            QuestionIntent.PAGERANK_ANALYSIS: [
                r'\b(most.*important|ranking|significance|influence)\b',
                r'\b(key.*entities?|central.*figures?|important.*players?)\b',
                r'\b(priority|weight|prominence)\b'
            ],
            QuestionIntent.MULTI_HOP_QUERY: [
                r'\b(through.*via|indirect.*connection|chain.*of)\b',
                r'\b(path.*from.*to|how.*reach|steps?.*between)\b',
                r'\b(multi.*step|complex.*relationship)\b'
            ]
        }
    
    def classify(self, question: str) -> tuple[QuestionIntent, float]:
        """Classify question intent with confidence score"""
        question_lower = question.lower()
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            for pattern in patterns:
                matches = len(re.findall(pattern, question_lower))
                score += matches * 0.3  # Each match adds confidence
            
            # Boost score for exact keyword matches
            if intent == QuestionIntent.DOCUMENT_SUMMARY and any(
                word in question_lower for word in ['summary', 'summarize', 'about']
            ):
                score += 0.4
            elif intent == QuestionIntent.ENTITY_ANALYSIS and any(
                word in question_lower for word in ['who', 'entities', 'people']
            ):
                score += 0.4
            elif intent == QuestionIntent.RELATIONSHIP_ANALYSIS and any(
                word in question_lower for word in ['relate', 'relationship', 'connect']
            ):
                score += 0.4
            
            intent_scores[intent] = min(score, 1.0)  # Cap at 1.0
        
        # Find best intent
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            return best_intent[0], best_intent[1]
        else:
            # Default to document summary
            return QuestionIntent.DOCUMENT_SUMMARY, 0.3

class ToolMapper:
    """Map intents to required tool sequences"""
    
    def __init__(self):
        self.tool_sequences = {
            QuestionIntent.DOCUMENT_SUMMARY: [
                "T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER"
            ],
            QuestionIntent.ENTITY_ANALYSIS: [
                "T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER", "T31_ENTITY_BUILDER"
            ],
            QuestionIntent.RELATIONSHIP_ANALYSIS: [
                "T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER", 
                "T27_RELATIONSHIP_EXTRACTOR", "T34_EDGE_BUILDER"
            ],
            QuestionIntent.THEME_ANALYSIS: [
                "T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER", 
                "T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER", "T34_EDGE_BUILDER"
            ],
            QuestionIntent.SPECIFIC_SEARCH: [
                "T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER", "T49_MULTI_HOP_QUERY"
            ],
            QuestionIntent.GRAPH_ANALYSIS: [
                "T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER",
                "T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER", "T34_EDGE_BUILDER", "T49_MULTI_HOP_QUERY"
            ],
            QuestionIntent.PAGERANK_ANALYSIS: [
                "T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER",
                "T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER", "T34_EDGE_BUILDER", "T68_PAGE_RANK"
            ],
            QuestionIntent.MULTI_HOP_QUERY: [
                "T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER",
                "T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER", "T34_EDGE_BUILDER", "T49_MULTI_HOP_QUERY"
            ]
        }
    
    def get_tools_for_intent(self, intent: QuestionIntent) -> List[str]:
        """Get required tools for intent"""
        return self.tool_sequences.get(intent, self.tool_sequences[QuestionIntent.DOCUMENT_SUMMARY])

class QuestionParser:
    """Parse natural language questions into structured requests"""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.tool_mapper = ToolMapper()
    
    def parse_question(self, question: str, document_path: str = None) -> ParsedQuestion:
        """Convert natural language question to tool execution plan"""
        
        # 1. Classify question type
        intent, confidence = self.intent_classifier.classify(question)
        
        # 2. Extract mentioned entities (simple keyword extraction)
        entities_mentioned = self._extract_mentioned_entities(question)
        
        # 3. Determine required tools based on intent
        required_tools = self.tool_mapper.get_tools_for_intent(intent)
        
        # 4. Create execution plan
        execution_plan = self._create_execution_plan(intent, required_tools, document_path, entities_mentioned)
        
        return ParsedQuestion(
            original_question=question,
            intent=intent,
            entities_mentioned=entities_mentioned,
            required_tools=required_tools,
            execution_plan=execution_plan,
            confidence=confidence
        )
    
    def _extract_mentioned_entities(self, question: str) -> List[str]:
        """Extract entity names mentioned in question"""
        # Simple extraction - look for capitalized words/phrases
        entities = []
        
        # Pattern for proper nouns (capitalized words)
        proper_noun_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        matches = re.findall(proper_noun_pattern, question)
        
        # Filter out common question words
        question_words = {
            'What', 'Who', 'Where', 'When', 'Why', 'How', 'Which', 'This', 'That',
            'The', 'These', 'Those', 'Are', 'Is', 'Was', 'Were', 'Do', 'Does', 'Did'
        }
        
        for match in matches:
            if match not in question_words and len(match) > 2:
                entities.append(match)
        
        return entities
    
    def _create_execution_plan(self, intent: QuestionIntent, required_tools: List[str], 
                             document_path: str = None, entities_mentioned: List[str] = None) -> ExecutionPlan:
        """Create execution plan with proper tool sequencing"""
        
        steps = []
        
        for i, tool_id in enumerate(required_tools):
            # Determine dependencies
            depends_on = []
            if i > 0:
                depends_on = [required_tools[i-1]]
            
            # Create tool arguments
            arguments = self._create_tool_arguments(tool_id, intent, document_path, entities_mentioned)
            
            step = ExecutionStep(
                tool_id=tool_id,
                arguments=arguments,
                depends_on=depends_on,
                optional=False
            )
            steps.append(step)
        
        # Determine if parallel execution is possible
        parallel_possible = len(steps) <= 3  # Simple heuristic
        
        # Estimate duration (simple heuristic)
        estimated_duration = len(steps) * 2.0  # 2 seconds per tool average
        
        return ExecutionPlan(
            steps=steps,
            parallel_execution_possible=parallel_possible,
            estimated_duration=estimated_duration
        )
    
    def _create_tool_arguments(self, tool_id: str, intent: QuestionIntent, 
                             document_path: str = None, entities_mentioned: List[str] = None) -> Dict[str, Any]:
        """Create appropriate arguments for each tool"""
        
        base_args = {
            "input_data": {},
            "parameters": {}
        }
        
        if tool_id == "T01_PDF_LOADER" and document_path:
            base_args["input_data"]["file_path"] = document_path
        elif tool_id == "T23A_SPACY_NER":
            base_args["parameters"]["confidence_threshold"] = 0.0  # Use current setting
        elif tool_id == "T27_RELATIONSHIP_EXTRACTOR":
            base_args["parameters"]["pattern_count"] = 24  # Use enhanced patterns
        elif tool_id == "T49_MULTI_HOP_QUERY" and entities_mentioned:
            # Add specific search terms for multi-hop queries
            base_args["parameters"]["search_entities"] = entities_mentioned
        elif tool_id == "T68_PAGE_RANK":
            base_args["parameters"]["max_iterations"] = 20
            base_args["parameters"]["damping_factor"] = 0.85
        
        return base_args

# Supported question types for reference
SUPPORTED_QUESTION_TYPES = {
    "document_summary": [
        "What is this document about?",
        "Summarize the main points",
        "Give me an overview of this paper",
        "What are the key findings?"
    ],
    "entity_analysis": [
        "What are the key entities?", 
        "Who are the main people mentioned?",
        "What organizations are discussed?",
        "List the key players"
    ],
    "relationship_analysis": [
        "How do X and Y relate?",
        "What connections exist?",
        "How are these entities connected?",
        "What relationships are described?"
    ],
    "theme_analysis": [
        "What are the main themes?",
        "What topics are discussed?",
        "What subjects are covered?",
        "What are the central ideas?"
    ],
    "specific_search": [
        "Find information about X",
        "What does the document say about Y?",
        "Search for details about Z",
        "Tell me about [specific topic]"
    ],
    "graph_analysis": [
        "Show me the network structure",
        "How are entities connected in the graph?",
        "What's the network hierarchy?",
        "Display the relationship graph"
    ],
    "pagerank_analysis": [
        "What are the most important entities?",
        "Rank the key players by importance",
        "Which entities have the most influence?",
        "Show entity significance scores"
    ],
    "multi_hop_query": [
        "How is X connected to Y through other entities?",
        "What's the path from A to B?",
        "Show indirect connections between entities",
        "Find multi-step relationships"
    ]
}