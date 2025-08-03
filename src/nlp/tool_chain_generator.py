"""
Tool Chain Generator for Phase B
Generates optimal tool execution chains based on question analysis
"""
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from enum import Enum
import logging

from .advanced_intent_classifier import IntentClassificationResult, QuestionIntent
from .question_complexity_analyzer import ComplexityAnalysisResult, ComplexityLevel
from .context_extractor import QuestionContext

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """Tool execution modes"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


@dataclass
class ToolStep:
    """Single step in tool execution chain"""
    tool_id: str
    input_mapping: Dict[str, str]  # Maps inputs from previous tools
    parameters: Dict[str, any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)  # Tool IDs this depends on
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    optional: bool = False
    condition: Optional[str] = None  # Condition for execution


@dataclass
class ToolChain:
    """Complete tool execution chain"""
    steps: List[ToolStep]
    can_parallelize: bool
    estimated_time: float
    estimated_memory: int
    optimization_notes: List[str] = field(default_factory=list)
    execution_graph: Dict[str, List[str]] = field(default_factory=dict)  # DAG representation
    
    @property
    def required_tools(self) -> List[str]:
        """Get list of required tool IDs for backwards compatibility"""
        return [step.tool_id for step in self.steps]
    
    @property
    def estimated_execution_time(self) -> float:
        """Get estimated execution time for backwards compatibility"""
        return self.estimated_time
    
    @property
    def execution_strategy(self) -> str:
        """Get execution strategy description for backwards compatibility"""
        if self.can_parallelize:
            return "parallel_optimized"
        elif len(self.steps) > 5:
            return "sequential_chunked"
        else:
            return "sequential"


class ToolChainGenerator:
    """Generates optimal tool chains based on question analysis"""
    
    def __init__(self):
        # Load tool dependencies from contracts (no hardcoded rules)
        from ..analysis.contract_analyzer import ToolContractAnalyzer
        self.contract_analyzer = ToolContractAnalyzer()
        
        # Build dependency graph from contracts
        try:
            dependency_graph = self.contract_analyzer.build_dependency_graph()
            self.tool_dependencies = dependency_graph.edges
            logger.info("✅ Loaded tool dependencies from contracts (zero hardcoded rules)")
        except Exception as e:
            logger.error(f"Failed to load dependencies from contracts: {e}")
            # Fallback to empty dependencies - will be handled by error processing
            self.tool_dependencies = {}
        
        # Tool capabilities
        self.tool_capabilities = {
            "T01_PDF_LOADER": ["document_loading"],
            "T15A_TEXT_CHUNKER": ["text_segmentation"],
            "T23A_SPACY_NER": ["entity_extraction", "basic_analysis"],
            "T27_RELATIONSHIP_EXTRACTOR": ["relationship_analysis"],
            "T31_ENTITY_BUILDER": ["graph_creation", "entity_storage"],
            "T34_EDGE_BUILDER": ["relationship_storage", "graph_edges"],
            "T68_PAGE_RANK": ["importance_ranking", "network_analysis"],
            "T49_MULTI_HOP_QUERY": ["complex_queries", "path_finding"]
        }
        
        # Parallel execution groups (tools that can run together)
        self.parallel_groups = {
            "analysis": ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"],
            "graph_build": ["T31_ENTITY_BUILDER", "T34_EDGE_BUILDER"],
            "advanced": ["T68_PAGE_RANK", "T49_MULTI_HOP_QUERY"]
        }
    
    def generate_chain(self, 
                      intent_result: IntentClassificationResult,
                      complexity_result: ComplexityAnalysisResult,
                      context_result: QuestionContext,
                      question: str = "") -> ToolChain:
        """Generate optimal tool chain based on comprehensive analysis"""
        
        # Start with basic document processing
        steps = []
        required_tools = set()
        
        # Always start with document loading and chunking
        steps.extend(self._create_basic_pipeline())
        required_tools.update(["T01_PDF_LOADER", "T15A_TEXT_CHUNKER"])
        
        # Add tools based on primary intent
        intent_tools = self._get_tools_for_intent(intent_result.primary_intent)
        required_tools.update(intent_tools)
        
        # Add tools for secondary intents
        for secondary_intent in intent_result.secondary_intents:
            intent_tools = self._get_tools_for_intent(secondary_intent)
            required_tools.update(intent_tools)
        
        # Add tools based on context requirements
        context_tools = self._get_tools_for_context(context_result)
        required_tools.update(context_tools)
        
        # Add relationship extractor for certain intents
        if "T23A_SPACY_NER" in required_tools:
            if (intent_result.primary_intent in [QuestionIntent.RELATIONSHIP_ANALYSIS, 
                                               QuestionIntent.NETWORK_ANALYSIS,
                                               QuestionIntent.COMPARATIVE_ANALYSIS] or
                "relationships" in question.lower() or
                "relate" in question.lower()):
                required_tools.add("T27_RELATIONSHIP_EXTRACTOR")
        
        # Add graph builders for questions that need graph analysis
        if ("T27_RELATIONSHIP_EXTRACTOR" in required_tools or 
            intent_result.primary_intent == QuestionIntent.NETWORK_ANALYSIS):
            required_tools.add("T31_ENTITY_BUILDER")
            required_tools.add("T34_EDGE_BUILDER")
        
        # Optimize tool selection based on complexity
        if complexity_result.level == ComplexityLevel.SIMPLE:
            # Remove redundant tools for simple questions
            required_tools = self._optimize_simple_chain(required_tools)
        elif complexity_result.level == ComplexityLevel.COMPLEX:
            # Ensure all necessary tools for complex analysis
            required_tools = self._ensure_complex_chain(required_tools)
        
        # Build execution steps
        for tool_id in self._topological_sort(required_tools):
            if tool_id not in ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER"]:  # Already added
                step = self._create_tool_step(tool_id, steps)
                steps.append(step)
        
        # Identify parallelization opportunities
        can_parallelize, parallel_groups = self._identify_parallel_opportunities(steps)
        
        # Create execution graph
        execution_graph = self._build_execution_graph(steps)
        
        # Calculate estimates
        estimated_time = self._calculate_estimated_time(steps, can_parallelize)
        estimated_memory = self._calculate_estimated_memory(steps)
        
        # Generate optimization notes
        optimization_notes = self._generate_optimization_notes(
            steps, can_parallelize, complexity_result
        )
        
        return ToolChain(
            steps=steps,
            can_parallelize=can_parallelize,
            estimated_time=estimated_time,
            estimated_memory=estimated_memory,
            optimization_notes=optimization_notes,
            execution_graph=execution_graph
        )
    
    def _create_basic_pipeline(self) -> List[ToolStep]:
        """Create basic document processing pipeline"""
        return [
            ToolStep(
                tool_id="T01_PDF_LOADER",
                input_mapping={"file_path": "document_path"},
                parameters={},
                depends_on=[],
                execution_mode=ExecutionMode.SEQUENTIAL
            ),
            ToolStep(
                tool_id="T15A_TEXT_CHUNKER",
                input_mapping={
                    "text": "T01_PDF_LOADER.document.text",
                    "document_ref": "T01_PDF_LOADER.document.document_ref"
                },
                parameters={"chunk_size": 1000},
                depends_on=["T01_PDF_LOADER"],
                execution_mode=ExecutionMode.SEQUENTIAL
            )
        ]
    
    def _get_tools_for_intent(self, intent: QuestionIntent) -> Set[str]:
        """Get required tools for a specific intent"""
        intent_tool_mapping = {
            QuestionIntent.ENTITY_EXTRACTION: {"T23A_SPACY_NER", "T31_ENTITY_BUILDER"},
            QuestionIntent.RELATIONSHIP_ANALYSIS: {"T27_RELATIONSHIP_EXTRACTOR", "T34_EDGE_BUILDER"},
            QuestionIntent.PATTERN_DISCOVERY: {"T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR", "T68_PAGE_RANK"},
            QuestionIntent.NETWORK_ANALYSIS: {"T31_ENTITY_BUILDER", "T34_EDGE_BUILDER", "T68_PAGE_RANK"},
            QuestionIntent.COMPARATIVE_ANALYSIS: {"T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR", "T49_MULTI_HOP_QUERY"},
            QuestionIntent.PREDICTIVE_ANALYSIS: {"T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR", "T68_PAGE_RANK"},
            QuestionIntent.TEMPORAL_ANALYSIS: {"T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"},
            QuestionIntent.SENTIMENT_ANALYSIS: {"T23A_SPACY_NER"},
            QuestionIntent.ANOMALY_DETECTION: {"T23A_SPACY_NER", "T68_PAGE_RANK"},
            QuestionIntent.CAUSAL_ANALYSIS: {"T27_RELATIONSHIP_EXTRACTOR", "T49_MULTI_HOP_QUERY"},
            QuestionIntent.HIERARCHICAL_ANALYSIS: {"T23A_SPACY_NER", "T31_ENTITY_BUILDER", "T27_RELATIONSHIP_EXTRACTOR"},
            QuestionIntent.STATISTICAL_ANALYSIS: {"T23A_SPACY_NER", "T68_PAGE_RANK"}
        }
        
        return intent_tool_mapping.get(intent, {"T23A_SPACY_NER"})
    
    def _get_tools_for_context(self, context: QuestionContext) -> Set[str]:
        """Get required tools based on context"""
        tools = set()
        
        if context.mentioned_entities:
            tools.add("T23A_SPACY_NER")
            tools.add("T31_ENTITY_BUILDER")
        
        if context.requires_comparison:
            tools.add("T27_RELATIONSHIP_EXTRACTOR")
            tools.add("T49_MULTI_HOP_QUERY")
        
        if context.requires_aggregation:
            tools.add("T68_PAGE_RANK")
        
        if context.has_temporal_context:
            tools.add("T27_RELATIONSHIP_EXTRACTOR")
        
        return tools
    
    def _optimize_simple_chain(self, tools: Set[str]) -> Set[str]:
        """Optimize tool selection for simple questions"""
        # For simple questions, we might not need all tools
        essential_tools = {"T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER"}
        
        # Add only necessary tools based on what's really needed
        if "T27_RELATIONSHIP_EXTRACTOR" in tools and "T34_EDGE_BUILDER" in tools:
            essential_tools.update(["T27_RELATIONSHIP_EXTRACTOR", "T34_EDGE_BUILDER"])
        
        return essential_tools
    
    def _ensure_complex_chain(self, tools: Set[str]) -> Set[str]:
        """Ensure all necessary tools for complex analysis"""
        # For complex questions, ensure we have complete pipelines
        if "T27_RELATIONSHIP_EXTRACTOR" in tools:
            tools.add("T34_EDGE_BUILDER")
        
        if "T31_ENTITY_BUILDER" in tools or "T34_EDGE_BUILDER" in tools:
            # If building graph, might need PageRank
            tools.add("T68_PAGE_RANK")
        
        return tools
    
    def _topological_sort(self, tools: Set[str]) -> List[str]:
        """Sort tools based on dependencies"""
        # Build dependency graph
        graph = {}
        in_degree = {}
        
        for tool in tools:
            graph[tool] = []
            in_degree[tool] = 0
        
        for tool in tools:
            deps = self.tool_dependencies.get(tool, [])
            for dep in deps:
                if dep in tools:
                    graph[dep].append(tool)
                    in_degree[tool] += 1
        
        # Topological sort
        queue = [tool for tool in tools if in_degree[tool] == 0]
        result = []
        
        while queue:
            tool = queue.pop(0)
            result.append(tool)
            
            for neighbor in graph[tool]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def _create_tool_step(self, tool_id: str, existing_steps: List[ToolStep]) -> ToolStep:
        """Create a tool step with proper input mapping"""
        dependencies = self.tool_dependencies.get(tool_id, [])
        
        # Build input mapping based on tool requirements
        input_mapping = {}
        
        if tool_id == "T23A_SPACY_NER":
            input_mapping = {
                "text": "T15A_TEXT_CHUNKER.aggregated_text",
                "chunk_ref": "T15A_TEXT_CHUNKER.first_chunk_ref"
            }
        elif tool_id == "T27_RELATIONSHIP_EXTRACTOR":
            input_mapping = {
                "chunks": "T15A_TEXT_CHUNKER.chunks",
                "entities": "T23A_SPACY_NER.entities"
            }
        elif tool_id == "T31_ENTITY_BUILDER":
            input_mapping = {
                "entities": "T23A_SPACY_NER.entities"
            }
        elif tool_id == "T34_EDGE_BUILDER":
            input_mapping = {
                "relationships": "T27_RELATIONSHIP_EXTRACTOR.relationships"
            }
        elif tool_id in ["T68_PAGE_RANK", "T49_MULTI_HOP_QUERY"]:
            input_mapping = {
                "graph_ready": "T31_ENTITY_BUILDER.success AND T34_EDGE_BUILDER.success"
            }
        
        return ToolStep(
            tool_id=tool_id,
            input_mapping=input_mapping,
            parameters={},
            depends_on=dependencies,
            execution_mode=ExecutionMode.SEQUENTIAL
        )
    
    def _identify_parallel_opportunities(self, steps: List[ToolStep]) -> Tuple[bool, List[List[str]]]:
        """Identify which tools can run in parallel"""
        parallel_groups = []
        
        # Build dependency levels first
        levels = {}
        for step in steps:
            if not step.depends_on:
                levels[step.tool_id] = 0
            else:
                max_dep_level = max(levels.get(dep, -1) for dep in step.depends_on)
                levels[step.tool_id] = max_dep_level + 1
        
        # Group tools by level - tools at same level might be parallelizable
        level_groups = {}
        for step in steps:
            level = levels.get(step.tool_id, 0)
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(step)
        
        # Check each level for parallel opportunities
        for level, level_steps in level_groups.items():
            if len(level_steps) > 1:
                # These tools are at the same dependency level
                # Check if they can actually run in parallel
                for i in range(len(level_steps)):
                    for j in range(i + 1, len(level_steps)):
                        tool1 = level_steps[i]
                        tool2 = level_steps[j]
                        
                        # Check if they don't depend on each other
                        if (tool1.tool_id not in tool2.depends_on and 
                            tool2.tool_id not in tool1.depends_on):
                            
                            # Check known parallel-safe combinations
                            if self._are_tools_parallel_safe(tool1.tool_id, tool2.tool_id):
                                parallel_groups.append([tool1.tool_id, tool2.tool_id])
        
        # Also check predefined parallel groups
        for group_name, group_tools in self.parallel_groups.items():
            group_in_chain = [tool for tool in group_tools if any(step.tool_id == tool for step in steps)]
            if len(group_in_chain) > 1:
                # Verify they don't have inter-dependencies
                can_parallel = True
                for i, tool1 in enumerate(group_in_chain):
                    step1 = next(s for s in steps if s.tool_id == tool1)
                    for j, tool2 in enumerate(group_in_chain):
                        if i != j:
                            if tool2 in step1.depends_on:
                                can_parallel = False
                                break
                
                if can_parallel and group_in_chain not in parallel_groups:
                    parallel_groups.append(group_in_chain)
        
        # Mark steps that can be parallelized
        for group in parallel_groups:
            for tool_id in group:
                step = next(s for s in steps if s.tool_id == tool_id)
                step.execution_mode = ExecutionMode.PARALLEL
        
        return len(parallel_groups) > 0, parallel_groups
    
    def _are_tools_parallel_safe(self, tool1: str, tool2: str) -> bool:
        """Check if two specific tools can run in parallel"""
        # Define specific parallel-safe pairs
        parallel_safe_pairs = {
            # T31 and T27 both depend on T23A, can run in parallel
            ("T27_RELATIONSHIP_EXTRACTOR", "T31_ENTITY_BUILDER"),
            # These both run at the end of the pipeline
            ("T68_PAGE_RANK", "T49_MULTI_HOP_QUERY"),
            # Original pair kept for compatibility
            ("T31_ENTITY_BUILDER", "T34_EDGE_BUILDER"),
        }
        
        # Check both orderings
        tool_pair = tuple(sorted([tool1, tool2]))
        return tool_pair in parallel_safe_pairs
    
    def _build_execution_graph(self, steps: List[ToolStep]) -> Dict[str, List[str]]:
        """Build execution graph (DAG) from steps"""
        graph = {}
        
        for step in steps:
            graph[step.tool_id] = step.depends_on.copy()
        
        return graph
    
    def _calculate_estimated_time(self, steps: List[ToolStep], can_parallelize: bool) -> float:
        """Calculate estimated execution time"""
        tool_times = {
            "T01_PDF_LOADER": 0.5,
            "T15A_TEXT_CHUNKER": 0.3,
            "T23A_SPACY_NER": 1.0,
            "T27_RELATIONSHIP_EXTRACTOR": 1.5,
            "T31_ENTITY_BUILDER": 0.8,
            "T34_EDGE_BUILDER": 1.0,
            "T68_PAGE_RANK": 2.0,
            "T49_MULTI_HOP_QUERY": 1.5
        }
        
        total_time = sum(tool_times.get(step.tool_id, 1.0) for step in steps)
        
        if can_parallelize:
            # Assume 30% time reduction with parallelization
            total_time *= 0.7
        
        return round(total_time, 1)
    
    def _calculate_estimated_memory(self, steps: List[ToolStep]) -> int:
        """Calculate estimated memory requirements"""
        tool_memory = {
            "T01_PDF_LOADER": 50,
            "T15A_TEXT_CHUNKER": 30,
            "T23A_SPACY_NER": 200,
            "T27_RELATIONSHIP_EXTRACTOR": 150,
            "T31_ENTITY_BUILDER": 100,
            "T34_EDGE_BUILDER": 100,
            "T68_PAGE_RANK": 300,
            "T49_MULTI_HOP_QUERY": 200
        }
        
        # Peak memory is max of individual tools plus overhead
        peak_memory = max(tool_memory.get(step.tool_id, 100) for step in steps)
        overhead = 200  # Base system overhead
        
        return peak_memory + overhead
    
    def _generate_optimization_notes(self, steps: List[ToolStep], 
                                   can_parallelize: bool,
                                   complexity: ComplexityAnalysisResult) -> List[str]:
        """Generate optimization recommendations"""
        notes = []
        
        if can_parallelize:
            notes.append("Parallel execution possible - consider using async processing")
        
        if complexity.level == ComplexityLevel.SIMPLE and len(steps) > 5:
            notes.append("Consider simplifying chain for better performance")
        
        if any(step.tool_id == "T68_PAGE_RANK" for step in steps):
            notes.append("PageRank computation may be slow for large graphs - consider caching")
        
        if len(steps) > 8:
            notes.append("Long execution chain - monitor memory usage")
        
        return notes
    
    def generate_tool_chain(self, 
                            intent_result: IntentClassificationResult,
                            complexity_result: ComplexityAnalysisResult,
                            context_result: QuestionContext,
                            question: str = "") -> ToolChain:
        """Alias for generate_chain() method for backwards compatibility"""
        return self.generate_chain(intent_result, complexity_result, context_result, question)