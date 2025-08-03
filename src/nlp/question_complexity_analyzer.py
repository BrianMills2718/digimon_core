"""
Question Complexity Analyzer for Phase B
Analyzes question complexity to determine execution strategy
"""
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional
import re
import logging

logger = logging.getLogger(__name__)


class ComplexityLevel(Enum):
    """Question complexity levels"""
    SIMPLE = "simple"      # Single intent, <3 tools
    MODERATE = "moderate"  # 1-2 intents, 3-6 tools
    COMPLEX = "complex"    # Multiple intents, >6 tools


@dataclass
class ComplexityAnalysisResult:
    """Result of question complexity analysis"""
    level: ComplexityLevel
    estimated_tools: int
    parallelizable_components: int
    estimated_time_seconds: float
    estimated_memory_mb: int
    requires_gpu: bool
    complexity_factors: Dict[str, float]
    execution_strategy: str


class QuestionComplexityAnalyzer:
    """Analyzes question complexity for execution planning"""
    
    def __init__(self):
        # Complexity indicators and their weights
        self.complexity_weights = {
            'word_count': 0.1,          # More words = more complex
            'entity_mentions': 0.2,     # More entities = more analysis
            'multi_part': 0.3,          # Multiple parts = higher complexity
            'comparison': 0.2,          # Comparisons add complexity
            'aggregation': 0.2,         # Aggregations require more processing
            'temporal': 0.15,           # Temporal analysis adds complexity
            'inference': 0.25,          # Inference/prediction is complex
            'nested_clauses': 0.2       # Nested structure = complex
        }
        
        # Tool execution time estimates (seconds)
        self.tool_time_estimates = {
            "T01_PDF_LOADER": 0.5,
            "T15A_TEXT_CHUNKER": 0.3,
            "T23A_SPACY_NER": 1.0,
            "T27_RELATIONSHIP_EXTRACTOR": 1.5,
            "T31_ENTITY_BUILDER": 0.8,
            "T34_EDGE_BUILDER": 1.0,
            "T68_PAGE_RANK": 2.0,
            "T49_MULTI_HOP_QUERY": 1.5
        }
        
        # Tool memory estimates (MB)
        self.tool_memory_estimates = {
            "T01_PDF_LOADER": 50,
            "T15A_TEXT_CHUNKER": 30,
            "T23A_SPACY_NER": 200,
            "T27_RELATIONSHIP_EXTRACTOR": 150,
            "T31_ENTITY_BUILDER": 100,
            "T34_EDGE_BUILDER": 100,
            "T68_PAGE_RANK": 300,
            "T49_MULTI_HOP_QUERY": 200
        }
    
    def analyze_complexity(self, question: str, intent_result=None) -> ComplexityAnalysisResult:
        """Analyze question complexity for execution planning"""
        # Calculate complexity factors
        complexity_factors = self._calculate_complexity_factors(question)
        
        # Calculate overall complexity score
        complexity_score = sum(
            factor_value * self.complexity_weights.get(factor_name, 0.1)
            for factor_name, factor_value in complexity_factors.items()
        )
        
        # Determine complexity level
        if complexity_score < 0.3:
            level = ComplexityLevel.SIMPLE
        elif complexity_score < 0.7:
            level = ComplexityLevel.MODERATE
        else:
            level = ComplexityLevel.COMPLEX
        
        # Estimate tools needed
        estimated_tools = self._estimate_tool_count(complexity_factors, intent_result)
        
        # Identify parallelizable components
        parallelizable = self._identify_parallelizable_components(question, complexity_factors)
        
        # Estimate execution time
        estimated_time = self._estimate_execution_time(estimated_tools, parallelizable)
        
        # Estimate memory requirements
        estimated_memory = self._estimate_memory_requirements(estimated_tools)
        
        # Determine execution strategy
        execution_strategy = self._determine_execution_strategy(
            level, parallelizable, estimated_tools
        )
        
        return ComplexityAnalysisResult(
            level=level,
            estimated_tools=estimated_tools,
            parallelizable_components=parallelizable,
            estimated_time_seconds=estimated_time,
            estimated_memory_mb=estimated_memory,
            requires_gpu=False,  # Currently no GPU tools
            complexity_factors=complexity_factors,
            execution_strategy=execution_strategy
        )
    
    def analyze(self, question: str, intent_result=None) -> ComplexityAnalysisResult:
        """Alias for analyze_complexity for backwards compatibility"""
        return self.analyze_complexity(question, intent_result)
    
    def _calculate_complexity_factors(self, question: str) -> Dict[str, float]:
        """Calculate various complexity factors"""
        question_lower = question.lower()
        words = question.split()
        
        factors = {
            'word_count': min(len(words) / 20.0, 1.0),  # Normalize to 0-1
            'entity_mentions': self._count_entity_mentions(question) / 5.0,
            'multi_part': 1.0 if any(sep in question for sep in [' and ', ', ', ';']) else 0.0,
            'comparison': 1.0 if any(word in question_lower for word in ['compare', 'versus', 'difference']) else 0.0,
            'aggregation': 1.0 if any(word in question_lower for word in ['all', 'total', 'average', 'every']) else 0.0,
            'temporal': 1.0 if any(word in question_lower for word in ['when', 'timeline', 'history', 'year', 'temporal', 'patterns', 'chronological', 'evolution', 'trend']) else 0.0,
            'inference': 1.0 if any(word in question_lower for word in ['why', 'predict', 'cause', 'will', 'causal', 'mechanisms', 'explain', 'reasoning']) else 0.0,
            'nested_clauses': self._count_nested_clauses(question) / 3.0
        }
        
        # Normalize all factors to 0-1 range
        return {k: min(v, 1.0) for k, v in factors.items()}
    
    def _count_entity_mentions(self, question: str) -> int:
        """Count potential entity mentions in question"""
        # Look for capitalized words (potential entities)
        capitalized = re.findall(r'\b[A-Z][a-z]+\b', question)
        
        # Look for quoted strings
        quoted = re.findall(r'"[^"]*"', question) + re.findall(r"'[^']*'", question)
        
        return len(capitalized) + len(quoted)
    
    def _count_nested_clauses(self, question: str) -> int:
        """Count nested clauses in question"""
        # Count subordinating conjunctions and relative pronouns
        nested_indicators = ['which', 'that', 'who', 'where', 'when', 'if', 'unless', 'because', 'although']
        count = sum(1 for word in question.lower().split() if word in nested_indicators)
        
        # Count parentheses and commas (indication of complex structure)
        count += question.count('(') + question.count(',')
        
        return count
    
    def _estimate_tool_count(self, complexity_factors: Dict[str, float], intent_result=None) -> int:
        """Estimate number of tools needed"""
        base_tools = 3  # Minimum tools (loader, chunker, NER)
        
        # Add tools based on complexity
        additional_tools = 0
        
        if complexity_factors['entity_mentions'] > 0.5:
            additional_tools += 2  # Entity builder, relationship extractor
        
        if complexity_factors['comparison'] > 0:
            additional_tools += 1  # Additional analysis tools
        
        if complexity_factors['aggregation'] > 0:
            additional_tools += 1  # Aggregation tools
        
        if complexity_factors['inference'] > 0:
            additional_tools += 1  # Advanced analysis tools
        
        if complexity_factors['temporal'] > 0:
            additional_tools += 1  # Temporal analysis
        
        # Additional tool for multi-part questions
        if complexity_factors['multi_part'] > 0:
            additional_tools += 1
        
        # Consider intent-based tools if available
        if intent_result and hasattr(intent_result, 'recommended_tools'):
            additional_tools = max(additional_tools, len(intent_result.recommended_tools) - base_tools)
        
        return base_tools + additional_tools
    
    def _identify_parallelizable_components(self, question: str, complexity_factors: Dict[str, float]) -> int:
        """Identify components that can be executed in parallel"""
        parallelizable = 0
        
        # Multiple independent analyses mentioned
        if ' and ' in question:
            # Count independent clauses
            clauses = question.split(' and ')
            
            # Check if clauses are independent (don't reference each other)
            independent_clauses = 0
            for i, clause in enumerate(clauses):
                is_independent = True
                for j, other_clause in enumerate(clauses):
                    if i != j and any(word in clause.lower() for word in ['their', 'these', 'those', 'it']):
                        is_independent = False
                        break
                if is_independent:
                    independent_clauses += 1
            
            if independent_clauses > 1:
                parallelizable = independent_clauses - 1
        
        # Different types of analysis that can run in parallel
        parallel_analyses = []
        if 'sentiment' in question.lower():
            parallel_analyses.append('sentiment')
        if 'theme' in question.lower() or 'topic' in question.lower():
            parallel_analyses.append('theme')
        if 'pattern' in question.lower():
            parallel_analyses.append('pattern')
        if 'statistic' in question.lower():
            parallel_analyses.append('statistics')
        
        if len(parallel_analyses) > 1:
            parallelizable = max(parallelizable, len(parallel_analyses) - 1)
        
        return parallelizable
    
    def _estimate_execution_time(self, tool_count: int, parallelizable: int) -> float:
        """Estimate total execution time"""
        # Base time for sequential execution
        avg_tool_time = 1.0  # Average 1 second per tool
        sequential_time = tool_count * avg_tool_time
        
        # Reduce time based on parallelization
        if parallelizable > 0:
            # Assume we can reduce time by running some tools in parallel
            time_reduction = min(parallelizable * 0.5, sequential_time * 0.4)
            return sequential_time - time_reduction
        
        return sequential_time
    
    def _estimate_memory_requirements(self, tool_count: int) -> int:
        """Estimate memory requirements"""
        # Base memory
        base_memory = 200  # MB
        
        # Additional memory per tool
        memory_per_tool = 100  # MB average
        
        # Some tools require more memory
        high_memory_tools = ['T23A_SPACY_NER', 'T68_PAGE_RANK']
        high_memory_count = min(2, tool_count // 3)  # Assume some high-memory tools
        
        total_memory = base_memory + (tool_count * memory_per_tool) + (high_memory_count * 200)
        
        return int(total_memory)
    
    def _determine_execution_strategy(self, level: ComplexityLevel, 
                                    parallelizable: int, tool_count: int) -> str:
        """Determine optimal execution strategy"""
        if level == ComplexityLevel.SIMPLE:
            return "sequential"
        elif level == ComplexityLevel.MODERATE:
            if parallelizable > 0:
                return "parallel_simple"
            else:
                return "sequential_optimized"
        else:  # COMPLEX
            if parallelizable >= 2:
                return "parallel_advanced"
            elif parallelizable > 0:
                return "hybrid"
            else:
                return "sequential_chunked"