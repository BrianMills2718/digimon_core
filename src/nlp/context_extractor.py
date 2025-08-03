"""
Context Extractor for Phase B
Extracts contextual information from questions to guide tool selection
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class QuestionContext:
    """Extracted context from a question"""
    # Temporal context
    has_temporal_context: bool = False
    temporal_constraints: List[str] = field(default_factory=list)
    requires_temporal_analysis: bool = False
    
    # Entity context
    mentioned_entities: List[str] = field(default_factory=list)
    entity_constraints: Dict[str, str] = field(default_factory=dict)
    
    # Comparison context
    requires_comparison: bool = False
    comparison_type: Optional[str] = None  # 'versus', 'ranking', 'similarity'
    comparison_count: Optional[int] = None
    comparison_entities: List[str] = field(default_factory=list)
    
    # Aggregation context
    requires_aggregation: bool = False
    aggregation_type: Optional[str] = None  # 'average', 'sum', 'count', 'max', 'min'
    aggregation_scope: Optional[str] = None  # 'all', 'filtered', 'grouped'
    
    # Filtering context
    has_filters: bool = False
    filter_conditions: List[str] = field(default_factory=list)
    
    # Output format hints
    output_format_hints: List[str] = field(default_factory=list)
    requires_visualization: bool = False
    
    # Scope and boundaries
    scope_modifiers: List[str] = field(default_factory=list)  # 'all', 'only', 'except'
    has_negation: bool = False
    
    # Confidence and ambiguity
    ambiguity_level: float = 0.0  # 0-1 scale
    missing_context: List[str] = field(default_factory=list)


class ContextExtractor:
    """Extracts contextual information from questions"""
    
    def __init__(self):
        # Temporal patterns
        self.temporal_patterns = {
            'year': r'\b((19|20)\d{2})\b',
            'month': r'\b(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b',
            'relative': r'\b(last|next|previous|recent|current|this|past)\s+(year|month|week|quarter)',
            'range': r'(from|between)\s+.*\s+(to|and)\s+',
            'specific_date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        }
        
        # Comparison keywords
        self.comparison_keywords = {
            'versus': ['vs', 'versus', 'compared to', 'against', 'compare'],
            'ranking': ['top', 'best', 'worst', 'highest', 'lowest', 'most', 'least'],
            'similarity': ['similar', 'like', 'same as', 'different from', 'differ']
        }
        
        # Aggregation patterns
        self.aggregation_patterns = {
            'average': ['average', 'mean', 'avg'],
            'sum': ['total', 'sum', 'combined', 'altogether'],
            'count': ['count', 'number of', 'how many'],
            'max': ['maximum', 'max', 'highest', 'most'],
            'min': ['minimum', 'min', 'lowest', 'least']
        }
        
        # Scope modifiers
        self.scope_patterns = {
            'all': ['all', 'every', 'each', 'entire', 'whole'],
            'only': ['only', 'just', 'solely', 'exclusively'],
            'except': ['except', 'excluding', 'but not', 'without']
        }
    
    def extract(self, question: str) -> QuestionContext:
        """Extract comprehensive context from question"""
        context = QuestionContext()
        question_lower = question.lower()
        
        # Extract temporal context
        self._extract_temporal_context(question, context)
        
        # Extract entity mentions
        self._extract_entities(question, context)
        
        # Extract comparison requirements
        self._extract_comparison_context(question_lower, context)
        
        # Extract aggregation requirements
        self._extract_aggregation_context(question_lower, context)
        
        # Extract filters
        self._extract_filters(question, context)
        
        # Extract output format hints
        self._extract_output_hints(question_lower, context)
        
        # Extract scope modifiers
        self._extract_scope_modifiers(question_lower, context)
        
        # Assess ambiguity
        self._assess_ambiguity(question, context)
        
        return context
    
    def _extract_temporal_context(self, question: str, context: QuestionContext):
        """Extract temporal information from question"""
        temporal_found = []
        
        for pattern_name, pattern in self.temporal_patterns.items():
            matches = re.findall(pattern, question, re.IGNORECASE)
            if matches:
                context.has_temporal_context = True
                temporal_found.extend(matches)
                
                if pattern_name in ['year', 'month', 'specific_date']:
                    if pattern_name == 'year':
                        # Extract the full year from regex groups
                        context.temporal_constraints.extend([m[0] if isinstance(m, tuple) else m for m in matches])
                    else:
                        context.temporal_constraints.extend(matches)
                elif pattern_name == 'relative':
                    context.requires_temporal_analysis = True
                    context.temporal_constraints.extend([m[0] + ' ' + m[1] for m in matches])
                elif pattern_name == 'range':
                    context.requires_temporal_analysis = True
        
        # Check for temporal keywords
        temporal_keywords = ['when', 'timeline', 'chronological', 'evolution', 'history', 'trend']
        if any(keyword in question.lower() for keyword in temporal_keywords):
            context.has_temporal_context = True
            context.requires_temporal_analysis = True
    
    def _extract_entities(self, question: str, context: QuestionContext):
        """Extract entity mentions from question"""
        # Extract capitalized words (potential entities)
        # Don't count question words as entities
        question_words = ['What', 'How', 'When', 'Where', 'Why', 'Which', 'Who', 'Compare']
        
        # More precise pattern for multi-word entities
        # Match single capitalized words or sequences of capitalized words
        entity_matches = []
        
        # Find all sequences of capitalized words
        # First, handle possessive forms properly
        clean_question = question.replace("'s", " ")
        words = clean_question.split()
        
        for i, word in enumerate(words):
            # Skip question words and non-capitalized words
            if word and word[0].isupper() and word not in question_words:
                # Check if it's a valid entity (not just punctuation)
                clean_word = word.rstrip('?.,!:;')
                if clean_word and clean_word not in question_words:
                    entity_matches.append(clean_word)
        
        context.mentioned_entities.extend(entity_matches)
        
        # Extract quoted entities (but not possessives)
        # Double quotes
        quoted = re.findall(r'"([^"]*)"', question)
        context.mentioned_entities.extend(quoted)
        
        # Single quotes - but avoid possessives
        # Match single quoted strings that don't end with 's
        single_quoted = re.findall(r"'([^']+)'(?!s)", question)
        context.mentioned_entities.extend(single_quoted)
        
        # Extract entities with possessive (avoiding fragments)
        # Don't extract possessive patterns that would duplicate entities we already have
        
        # Remove duplicates while preserving order
        seen = set()
        unique_entities = []
        for entity in context.mentioned_entities:
            if entity not in seen:
                seen.add(entity)
                unique_entities.append(entity)
        context.mentioned_entities = unique_entities
        
        # Extract entity constraints (e.g., "Microsoft's AI strategy") 
        # But also check if we should add any entities mentioned with possessives
        possessive_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'s\s+(\w+)"
        possessive_matches = re.findall(possessive_pattern, question)
        
        for entity_name, constraint in possessive_matches:
            # Add constraint for existing entities
            if entity_name in context.mentioned_entities:
                context.entity_constraints[entity_name] = constraint
            # Don't add "s strategy differ from Google" as an entity
            elif constraint not in ['strategy', 'AI', 'revenue', 'performance']:
                # This is likely a parsing error, don't add it
                pass
    
    def _extract_comparison_context(self, question_lower: str, context: QuestionContext):
        """Extract comparison requirements"""
        # Check for ranking first (more specific)
        if any(keyword in question_lower for keyword in self.comparison_keywords['ranking']):
            context.requires_comparison = True
            context.comparison_type = 'ranking'
        else:
            # Then check other comparison types
            for comp_type, keywords in self.comparison_keywords.items():
                if any(keyword in question_lower for keyword in keywords):
                    context.requires_comparison = True
                    context.comparison_type = comp_type
                    break
        
        # Extract comparison count (e.g., "top 3")
        count_match = re.search(r'top\s+(\d+)|best\s+(\d+)|(\d+)\s+most', question_lower)
        if count_match:
            context.comparison_count = int(next(g for g in count_match.groups() if g))
        
        # Extract entities being compared
        if context.requires_comparison and len(context.mentioned_entities) >= 2:
            context.comparison_entities = context.mentioned_entities[:2]  # First two entities
            
            # Look for explicit comparison pattern
            versus_pattern = r'(\w+)\s+(?:vs|versus|compared to)\s+(\w+)'
            versus_match = re.search(versus_pattern, question_lower)
            if versus_match:
                context.comparison_entities = [versus_match.group(1), versus_match.group(2)]
    
    def _extract_aggregation_context(self, question_lower: str, context: QuestionContext):
        """Extract aggregation requirements"""
        for agg_type, keywords in self.aggregation_patterns.items():
            if any(keyword in question_lower for keyword in keywords):
                context.requires_aggregation = True
                context.aggregation_type = agg_type
                break
        
        # Determine aggregation scope
        if context.requires_aggregation:
            # Check for explicit entity mentions in aggregation
            if 'entities' in question_lower:
                context.aggregation_scope = 'all entities'
            elif any(word in question_lower for word in ['all', 'every', 'total']):
                context.aggregation_scope = 'all'
            elif any(word in question_lower for word in ['filtered', 'selected', 'specific']):
                context.aggregation_scope = 'filtered'
            elif any(word in question_lower for word in ['by', 'per', 'grouped']):
                context.aggregation_scope = 'grouped'
            else:
                context.aggregation_scope = 'all'  # Default
    
    def _extract_filters(self, question: str, context: QuestionContext):
        """Extract filter conditions"""
        # Look for conditional words
        filter_keywords = ['where', 'with', 'having', 'that have', 'which have', 'containing']
        
        for keyword in filter_keywords:
            pattern = f"{keyword}\\s+([^,\\.]+)"
            matches = re.findall(pattern, question, re.IGNORECASE)
            if matches:
                context.has_filters = True
                context.filter_conditions.extend(matches)
        
        # Look for exclusion patterns
        exclusion_patterns = [r'except\s+([^,\.]+)', r'excluding\s+([^,\.]+)', r'but not\s+([^,\.]+)']
        for pattern in exclusion_patterns:
            matches = re.findall(pattern, question, re.IGNORECASE)
            if matches:
                context.has_filters = True
                context.filter_conditions.extend([f"NOT {match}" for match in matches])
    
    def _extract_output_hints(self, question_lower: str, context: QuestionContext):
        """Extract hints about desired output format"""
        # Visualization keywords
        viz_keywords = ['visualize', 'graph', 'chart', 'diagram', 'plot', 'tree', 'network']
        if any(keyword in question_lower for keyword in viz_keywords):
            context.requires_visualization = True
            context.output_format_hints.append('visualization')
        
        # Format keywords
        if 'list' in question_lower:
            context.output_format_hints.append('list')
        if 'table' in question_lower:
            context.output_format_hints.append('table')
        if 'summary' in question_lower:
            context.output_format_hints.append('summary')
        if 'detailed' in question_lower or 'detail' in question_lower:
            context.output_format_hints.append('detailed')
        if 'brief' in question_lower or 'concise' in question_lower:
            context.output_format_hints.append('brief')
    
    def _extract_scope_modifiers(self, question_lower: str, context: QuestionContext):
        """Extract scope modifiers"""
        for scope_type, keywords in self.scope_patterns.items():
            if any(keyword in question_lower for keyword in keywords):
                context.scope_modifiers.append(scope_type)
        
        # Check for negation
        negation_words = ['not', 'no', "don't", "doesn't", "isn't", "aren't", 'without']
        if any(word in question_lower for word in negation_words):
            context.has_negation = True
    
    def _assess_ambiguity(self, question: str, context: QuestionContext):
        """Assess question ambiguity and missing context"""
        ambiguity_score = 0.0
        
        # Vague pronouns without clear antecedents
        vague_pronouns = ['it', 'they', 'them', 'these', 'those', 'this', 'that']
        for pronoun in vague_pronouns:
            if f' {pronoun} ' in question.lower() and not context.mentioned_entities:
                ambiguity_score += 0.2
                context.missing_context.append('entity_reference')
        
        # Questions without specific entities
        if not context.mentioned_entities and 'document' not in question.lower():
            ambiguity_score += 0.3
            context.missing_context.append('specific_entities')
        
        # Temporal questions without time constraints
        if context.requires_temporal_analysis and not context.temporal_constraints:
            ambiguity_score += 0.2
            context.missing_context.append('time_period')
        
        # Comparison without clear targets
        if context.requires_comparison and len(context.comparison_entities) < 2:
            ambiguity_score += 0.2
            context.missing_context.append('comparison_targets')
        
        context.ambiguity_level = min(ambiguity_score, 1.0)
    
    def extract_context(self, question: str) -> QuestionContext:
        """Alias for extract() method for backwards compatibility"""
        return self.extract(question)