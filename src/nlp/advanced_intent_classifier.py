"""
Advanced Intent Classifier for Phase B
Multi-dimensional question classification with 10+ intent categories
"""
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Set, Optional
import re
import logging

logger = logging.getLogger(__name__)


class QuestionIntent(Enum):
    """Extended intent categories for advanced question analysis"""
    # Basic intents from Phase A
    DOCUMENT_SUMMARY = "document_summary"
    ENTITY_EXTRACTION = "entity_extraction"
    RELATIONSHIP_ANALYSIS = "relationship_analysis"
    THEME_ANALYSIS = "theme_analysis"
    SPECIFIC_SEARCH = "specific_search"
    
    # New advanced intents for Phase B
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    PATTERN_DISCOVERY = "pattern_discovery"
    PREDICTIVE_ANALYSIS = "predictive_analysis"
    CAUSAL_ANALYSIS = "causal_analysis"
    TEMPORAL_ANALYSIS = "temporal_analysis"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    HIERARCHICAL_ANALYSIS = "hierarchical_analysis"
    NETWORK_ANALYSIS = "network_analysis"


@dataclass
class IntentClassificationResult:
    """Result of advanced intent classification"""
    primary_intent: QuestionIntent
    secondary_intents: List[QuestionIntent]
    confidence: float
    recommended_tools: List[str]
    intent_scores: Dict[QuestionIntent, float]
    requires_multi_step: bool
    complexity_indicators: Dict[str, bool]


class AdvancedIntentClassifier:
    """Advanced classifier for multi-dimensional question intent analysis"""
    
    def __init__(self):
        # Intent patterns with keywords and phrases
        self.intent_patterns = {
            QuestionIntent.DOCUMENT_SUMMARY: {
                'keywords': ['about', 'summary', 'overview', 'describe', 'main points', 'gist'],
                'patterns': [r'what.*document.*about', r'summarize', r'give.*overview'],
                'weight': 1.0
            },
            QuestionIntent.ENTITY_EXTRACTION: {
                'keywords': ['entities', 'mentions', 'names', 'companies', 'people', 'organizations', 'who'],
                'patterns': [r'what.*mentioned', r'which.*entities', r'list.*companies', r'^what\s+\w+\s+are\s+mentioned'],
                'weight': 1.0
            },
            QuestionIntent.RELATIONSHIP_ANALYSIS: {
                'keywords': ['relate', 'relationship', 'connection', 'between', 'interact', 'associated'],
                'patterns': [r'how.*relate', r'relationship.*between', r'connections?'],
                'weight': 1.0
            },
            QuestionIntent.THEME_ANALYSIS: {
                'keywords': ['themes', 'topics', 'subjects', 'main ideas', 'concepts'],
                'patterns': [r'main.*themes?', r'key.*topics?', r'central.*ideas?'],
                'weight': 1.0
            },
            QuestionIntent.SPECIFIC_SEARCH: {
                'keywords': ['find', 'search', 'locate', 'information about', 'details on'],
                'patterns': [r'find.*about', r'search.*for', r'information.*(?:about|on)'],
                'weight': 0.9
            },
            QuestionIntent.COMPARATIVE_ANALYSIS: {
                'keywords': ['compare', 'contrast', 'versus', 'vs', 'difference', 'similar', 'differ'],
                'patterns': [r'compare.*(?:and|with)', r'difference.*between', r'contrast'],
                'weight': 1.2
            },
            QuestionIntent.PATTERN_DISCOVERY: {
                'keywords': ['pattern', 'trend', 'recurring', 'common', 'emerge', 'identify patterns'],
                'patterns': [r'what.*patterns?', r'identify.*trends?', r'recurring.*themes?'],
                'weight': 1.1
            },
            QuestionIntent.PREDICTIVE_ANALYSIS: {
                'keywords': ['predict', 'forecast', 'future', 'will', 'expect', 'anticipate', 'projection'],
                'patterns': [r'predict.*future', r'what.*will', r'forecast'],
                'weight': 1.3
            },
            QuestionIntent.CAUSAL_ANALYSIS: {
                'keywords': ['cause', 'effect', 'because', 'why', 'reason', 'lead to', 'result'],
                'patterns': [r'what.*caused?', r'why.*happen', r'causal.*relationship'],
                'weight': 1.2
            },
            QuestionIntent.TEMPORAL_ANALYSIS: {
                'keywords': ['timeline', 'when', 'chronological', 'sequence', 'history', 'evolution', 'over time'],
                'patterns': [r'timeline', r'chronological.*order', r'when.*happen'],
                'weight': 1.1
            },
            QuestionIntent.STATISTICAL_ANALYSIS: {
                'keywords': ['statistics', 'correlation', 'average', 'mean', 'median', 'distribution', 'percentage'],
                'patterns': [r'statistical.*analysis', r'correlation', r'average'],
                'weight': 1.2
            },
            QuestionIntent.ANOMALY_DETECTION: {
                'keywords': ['anomaly', 'outlier', 'unusual', 'abnormal', 'exception', 'irregular'],
                'patterns': [r'identify.*anomal', r'find.*outliers?', r'unusual.*patterns?'],
                'weight': 1.1
            },
            QuestionIntent.SENTIMENT_ANALYSIS: {
                'keywords': ['sentiment', 'opinion', 'feeling', 'positive', 'negative', 'emotion', 'attitude'],
                'patterns': [r'sentiment.*analysis', r'what.*opinion', r'positive.*negative', r'what.*sentiment'],
                'weight': 1.3
            },
            QuestionIntent.HIERARCHICAL_ANALYSIS: {
                'keywords': ['hierarchy', 'structure', 'organize', 'categorize', 'taxonomy', 'tree', 'levels'],
                'patterns': [r'hierarchical.*(?:view|structure)', r'organize.*categories'],
                'weight': 1.0
            },
            QuestionIntent.NETWORK_ANALYSIS: {
                'keywords': ['network', 'graph', 'connections', 'nodes', 'centrality', 'cluster'],
                'patterns': [r'network.*(?:analysis|effect)', r'graph.*structure'],
                'weight': 1.1
            }
        }
        
        # Tool mapping for each intent
        self.intent_to_tools = {
            QuestionIntent.DOCUMENT_SUMMARY: ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_SPACY_NER"],
            QuestionIntent.ENTITY_EXTRACTION: ["T23A_SPACY_NER", "T31_ENTITY_BUILDER"],
            QuestionIntent.RELATIONSHIP_ANALYSIS: ["T27_RELATIONSHIP_EXTRACTOR", "T34_EDGE_BUILDER"],
            QuestionIntent.THEME_ANALYSIS: ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"],
            QuestionIntent.SPECIFIC_SEARCH: ["T49_MULTI_HOP_QUERY"],
            QuestionIntent.COMPARATIVE_ANALYSIS: ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR", "T49_MULTI_HOP_QUERY"],
            QuestionIntent.PATTERN_DISCOVERY: ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR", "T68_PAGE_RANK"],
            QuestionIntent.PREDICTIVE_ANALYSIS: ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR", "T68_PAGE_RANK"],
            QuestionIntent.CAUSAL_ANALYSIS: ["T27_RELATIONSHIP_EXTRACTOR", "T49_MULTI_HOP_QUERY"],
            QuestionIntent.TEMPORAL_ANALYSIS: ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"],
            QuestionIntent.STATISTICAL_ANALYSIS: ["T23A_SPACY_NER", "T68_PAGE_RANK"],
            QuestionIntent.ANOMALY_DETECTION: ["T23A_SPACY_NER", "T68_PAGE_RANK"],
            QuestionIntent.SENTIMENT_ANALYSIS: ["T23A_SPACY_NER"],
            QuestionIntent.HIERARCHICAL_ANALYSIS: ["T23A_SPACY_NER", "T31_ENTITY_BUILDER", "T27_RELATIONSHIP_EXTRACTOR"],
            QuestionIntent.NETWORK_ANALYSIS: ["T27_RELATIONSHIP_EXTRACTOR", "T34_EDGE_BUILDER", "T68_PAGE_RANK"]
        }
    
    def classify(self, question: str) -> IntentClassificationResult:
        """Classify question intent with multi-dimensional analysis"""
        question_lower = question.lower()
        intent_scores = {}
        
        # Score each intent based on keywords and patterns
        for intent, config in self.intent_patterns.items():
            score = 0.0
            
            # Check keywords
            for keyword in config['keywords']:
                if keyword in question_lower:
                    score += 0.4 * config['weight']
            
            # Check patterns
            for pattern in config['patterns']:
                if re.search(pattern, question_lower):
                    score += 0.6 * config['weight']
            
            intent_scores[intent] = score
        
        # Sort intents by score
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Determine primary and secondary intents
        primary_intent = sorted_intents[0][0]
        primary_score = sorted_intents[0][1]
        
        # Get secondary intents (those with significant scores)
        secondary_intents = []
        for intent, score in sorted_intents[1:]:
            if score > 0.3 and score >= primary_score * 0.5:
                secondary_intents.append(intent)
        
        # Calculate confidence
        confidence = self._calculate_confidence(primary_score, intent_scores)
        
        # Get recommended tools
        recommended_tools = self._get_recommended_tools(primary_intent, secondary_intents)
        
        # Check complexity indicators
        complexity_indicators = self._analyze_complexity_indicators(question)
        
        # Determine if multi-step processing is required
        requires_multi_step = len(secondary_intents) > 0 or complexity_indicators['has_multiple_parts']
        
        return IntentClassificationResult(
            primary_intent=primary_intent,
            secondary_intents=secondary_intents,
            confidence=confidence,
            recommended_tools=recommended_tools,
            intent_scores=intent_scores,
            requires_multi_step=requires_multi_step,
            complexity_indicators=complexity_indicators
        )
    
    def _calculate_confidence(self, primary_score: float, all_scores: Dict[QuestionIntent, float]) -> float:
        """Calculate confidence score for classification"""
        if primary_score == 0:
            return 0.0
        
        # High score = high confidence
        base_confidence = min(primary_score, 1.0)
        
        # Adjust based on score distribution
        total_score = sum(all_scores.values())
        if total_score > 0:
            score_ratio = primary_score / total_score
            # If primary intent dominates, increase confidence
            if score_ratio > 0.5:
                base_confidence = min(base_confidence * 1.2, 1.0)
            elif score_ratio < 0.3:
                # If scores are distributed, decrease confidence
                base_confidence *= 0.8
        
        return round(base_confidence, 2)
    
    def _get_recommended_tools(self, primary: QuestionIntent, secondary: List[QuestionIntent]) -> List[str]:
        """Get recommended tools based on intents"""
        tools = set()
        
        # Add tools for primary intent
        if primary in self.intent_to_tools:
            tools.update(self.intent_to_tools[primary])
        
        # Add tools for secondary intents
        for intent in secondary:
            if intent in self.intent_to_tools:
                tools.update(self.intent_to_tools[intent])
        
        # Always include basic document processing
        tools.add("T01_PDF_LOADER")
        tools.add("T15A_TEXT_CHUNKER")
        
        return sorted(list(tools))
    
    def _analyze_complexity_indicators(self, question: str) -> Dict[str, bool]:
        """Analyze various complexity indicators in the question"""
        return {
            'has_multiple_parts': ' and ' in question.lower() or ',' in question,
            'has_comparison': any(word in question.lower() for word in ['compare', 'versus', 'vs', 'difference']),
            'has_temporal': any(word in question.lower() for word in ['when', 'timeline', 'history', 'evolution']),
            'has_aggregation': any(word in question.lower() for word in ['all', 'total', 'average', 'sum']),
            'has_conditional': any(word in question.lower() for word in ['if', 'when', 'unless', 'except']),
            'requires_inference': any(word in question.lower() for word in ['why', 'predict', 'cause', 'reason'])
        }