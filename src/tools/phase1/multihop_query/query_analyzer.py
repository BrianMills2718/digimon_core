"""
Query Analyzer for Multi-hop Query Tool

Analyzes query complexity, extracts query features, and provides insights
into query processing requirements and expected performance.
"""

import logging
import re
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class QueryAnalyzer:
    """Analyzes queries for complexity, patterns, and processing requirements"""
    
    def __init__(self):
        self.logger = logging.getLogger("multihop_query.query_analyzer")
        
        # Analysis statistics
        self.analysis_stats = {
            "queries_analyzed": 0,
            "complex_queries": 0,
            "simple_queries": 0,
            "multi_entity_queries": 0,
            "single_entity_queries": 0
        }
        
        # Query pattern definitions
        self.query_patterns = self._initialize_query_patterns()
    
    def _initialize_query_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize query pattern definitions"""
        return {
            "who_questions": {
                "patterns": [r'\bwho\b', r'\bwhich\s+person\b', r'\bwhat\s+person\b'],
                "entity_types": ["PERSON"],
                "complexity_factor": 0.6
            },
            "what_questions": {
                "patterns": [r'\bwhat\b', r'\bwhich\b'],
                "entity_types": ["ORGANIZATION", "PRODUCT", "CONCEPT"],
                "complexity_factor": 0.7
            },
            "where_questions": {
                "patterns": [r'\bwhere\b', r'\bwhich\s+location\b'],
                "entity_types": ["LOCATION", "FACILITY"],
                "complexity_factor": 0.5
            },
            "when_questions": {
                "patterns": [r'\bwhen\b', r'\bwhat\s+time\b'],
                "entity_types": ["DATE", "TIME", "EVENT"],
                "complexity_factor": 0.8
            },
            "how_questions": {
                "patterns": [r'\bhow\b'],
                "entity_types": ["PROCESS", "METHOD"],
                "complexity_factor": 0.9
            },
            "relationship_queries": {
                "patterns": [r'\bconnected\s+to\b', r'\brelated\s+to\b', r'\bworked?\s+(?:with|for|at)\b', r'\bassociated\s+with\b'],
                "entity_types": ["PERSON", "ORGANIZATION"],
                "complexity_factor": 0.8
            },
            "comparison_queries": {
                "patterns": [r'\bcompare\b', r'\bdifference\b', r'\bsimilar\b', r'\bversus\b', r'\bvs\b'],
                "entity_types": ["ORGANIZATION", "PRODUCT", "CONCEPT"],
                "complexity_factor": 0.9
            }
        }
    
    def analyze_query(self, query_text: str, extracted_entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive query analysis"""
        self.analysis_stats["queries_analyzed"] += 1
        
        analysis = {
            "query_text": query_text,
            "timestamp": datetime.now().isoformat(),
            "basic_features": self._analyze_basic_features(query_text),
            "entity_analysis": self._analyze_entities(extracted_entities),
            "pattern_analysis": self._analyze_query_patterns(query_text),
            "complexity_analysis": self._analyze_complexity(query_text, extracted_entities),
            "processing_requirements": self._estimate_processing_requirements(query_text, extracted_entities),
            "expected_performance": self._estimate_expected_performance(query_text, extracted_entities)
        }
        
        # Update statistics
        self._update_analysis_stats(analysis)
        
        return analysis
    
    def _analyze_basic_features(self, query_text: str) -> Dict[str, Any]:
        """Analyze basic textual features of the query"""
        words = query_text.split()
        sentences = query_text.split('.')
        
        return {
            "character_count": len(query_text),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "average_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "has_question_marks": "?" in query_text,
            "has_punctuation": bool(re.search(r'[.!?;,:]', query_text)),
            "has_capitalized_words": bool(re.search(r'\b[A-Z][a-zA-Z]+\b', query_text)),
            "unique_words": len(set(word.lower() for word in words)),
            "vocabulary_richness": len(set(word.lower() for word in words)) / len(words) if words else 0
        }
    
    def _analyze_entities(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze extracted entities from the query"""
        if not entities:
            return {
                "entity_count": 0,
                "unique_entity_types": 0,
                "entity_types": [],
                "avg_confidence": 0.0,
                "has_high_confidence_entities": False,
                "entity_type_distribution": {}
            }
        
        entity_types = [e.get("entity_type", "UNKNOWN") for e in entities]
        confidences = [e.get("confidence", 0.5) for e in entities]
        
        # Count entity type distribution
        type_distribution = {}
        for entity_type in entity_types:
            type_distribution[entity_type] = type_distribution.get(entity_type, 0) + 1
        
        return {
            "entity_count": len(entities),
            "unique_entity_types": len(set(entity_types)),
            "entity_types": list(set(entity_types)),
            "avg_confidence": sum(confidences) / len(confidences),
            "max_confidence": max(confidences),
            "min_confidence": min(confidences),
            "has_high_confidence_entities": any(c >= 0.8 for c in confidences),
            "entity_type_distribution": type_distribution,
            "dominant_entity_type": max(type_distribution.items(), key=lambda x: x[1])[0] if type_distribution else None
        }
    
    def _analyze_query_patterns(self, query_text: str) -> Dict[str, Any]:
        """Analyze query patterns and types"""
        query_lower = query_text.lower()
        matched_patterns = {}
        pattern_scores = {}
        
        for pattern_name, pattern_info in self.query_patterns.items():
            matches = []
            for pattern in pattern_info["patterns"]:
                if re.search(pattern, query_lower):
                    matches.append(pattern)
            
            if matches:
                matched_patterns[pattern_name] = {
                    "matched_patterns": matches,
                    "expected_entity_types": pattern_info["entity_types"],
                    "complexity_factor": pattern_info["complexity_factor"]
                }
                pattern_scores[pattern_name] = pattern_info["complexity_factor"]
        
        # Determine primary query type
        primary_pattern = None
        if pattern_scores:
            primary_pattern = max(pattern_scores.items(), key=lambda x: x[1])[0]
        
        return {
            "matched_patterns": matched_patterns,
            "primary_query_pattern": primary_pattern,
            "pattern_complexity_score": max(pattern_scores.values()) if pattern_scores else 0.5,
            "is_question": bool(re.search(r'\b(who|what|where|when|why|how)\b', query_lower)),
            "is_comparative": bool(re.search(r'\b(compare|versus|vs|difference|similar)\b', query_lower)),
            "is_relational": bool(re.search(r'\b(connected|related|associated|worked|partner)\b', query_lower))
        }
    
    def _analyze_complexity(self, query_text: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall query complexity"""
        # Base complexity factors
        entity_complexity = min(len(entities) / 5.0, 1.0)  # More entities = more complex
        length_complexity = min(len(query_text) / 100.0, 1.0)  # Longer queries = more complex
        
        # Entity type diversity
        entity_types = [e.get("entity_type", "UNKNOWN") for e in entities]
        type_diversity = len(set(entity_types)) / max(len(entities), 1) if entities else 0
        
        # Pattern complexity
        pattern_analysis = self._analyze_query_patterns(query_text)
        pattern_complexity = pattern_analysis.get("pattern_complexity_score", 0.5)
        
        # Relationship indicators
        relationship_indicators = len(re.findall(r'\b(connected|related|worked|partner|associate|collaborate|between|among)\b', query_text.lower()))
        relationship_complexity = min(relationship_indicators / 3.0, 1.0)
        
        # Combined complexity score
        overall_complexity = (
            entity_complexity * 0.3 +
            length_complexity * 0.2 +
            type_diversity * 0.2 +
            pattern_complexity * 0.2 +
            relationship_complexity * 0.1
        )
        
        complexity_level = "simple"
        if overall_complexity >= 0.7:
            complexity_level = "complex"
        elif overall_complexity >= 0.4:
            complexity_level = "moderate"
        
        return {
            "overall_complexity_score": overall_complexity,
            "complexity_level": complexity_level,
            "entity_complexity": entity_complexity,
            "length_complexity": length_complexity,
            "type_diversity": type_diversity,
            "pattern_complexity": pattern_complexity,
            "relationship_complexity": relationship_complexity,
            "complexity_factors": {
                "multiple_entities": len(entities) > 1,
                "diverse_entity_types": len(set(entity_types)) > 2,
                "long_query": len(query_text) > 50,
                "relationship_seeking": relationship_indicators > 0,
                "comparison_query": pattern_analysis.get("is_comparative", False)
            }
        }
    
    def _estimate_processing_requirements(self, query_text: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate processing requirements for the query"""
        complexity = self._analyze_complexity(query_text, entities)
        
        # Base estimates (in seconds and MB)
        base_time = 1.0
        base_memory = 10.0
        
        # Adjust based on complexity
        complexity_multiplier = 1.0 + complexity["overall_complexity_score"]
        
        # Entity count factor
        entity_factor = 1.0 + (len(entities) * 0.2)
        
        # Estimate hop requirements
        estimated_hops = 1
        if len(entities) > 1:
            estimated_hops = 2
        if complexity["relationship_complexity"] > 0.5:
            estimated_hops = 3
        
        return {
            "estimated_execution_time": base_time * complexity_multiplier * entity_factor,
            "estimated_memory_usage": base_memory * complexity_multiplier,
            "recommended_max_hops": estimated_hops,
            "recommended_result_limit": max(10, min(50, 20 + len(entities) * 5)),
            "suggested_timeout": max(30, int(base_time * complexity_multiplier * entity_factor * 10)),
            "neo4j_query_complexity": "high" if complexity["overall_complexity_score"] > 0.7 else "medium" if complexity["overall_complexity_score"] > 0.4 else "low"
        }
    
    def _estimate_expected_performance(self, query_text: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate expected performance and result quality"""
        complexity = self._analyze_complexity(query_text, entities)
        
        # Base success probability
        base_success = 0.8
        
        # Adjust based on entity confidence
        if entities:
            avg_confidence = sum(e.get("confidence", 0.5) for e in entities) / len(entities)
            confidence_factor = avg_confidence
        else:
            confidence_factor = 0.3  # Low success if no entities found
        
        # Adjust based on complexity
        complexity_penalty = complexity["overall_complexity_score"] * 0.2
        
        success_probability = max(0.1, base_success * confidence_factor - complexity_penalty)
        
        return {
            "estimated_success_probability": success_probability,
            "expected_result_count": max(1, int(20 * success_probability)),
            "expected_confidence_range": {
                "min": max(0.1, success_probability - 0.3),
                "max": min(1.0, success_probability + 0.2),
                "average": success_probability
            },
            "likely_result_types": self._predict_result_types(query_text, entities),
            "performance_concerns": self._identify_performance_concerns(query_text, entities, complexity)
        }
    
    def _predict_result_types(self, query_text: str, entities: List[Dict[str, Any]]) -> List[str]:
        """Predict likely result types based on query analysis"""
        result_types = []
        
        if len(entities) >= 2:
            result_types.append("path")
        
        if len(entities) >= 1:
            result_types.append("related_entity")
        
        # Add specific predictions based on query patterns
        query_lower = query_text.lower()
        
        if re.search(r'\b(connected|related|between)\b', query_lower):
            result_types.insert(0, "path")  # Prioritize paths for relationship queries
        
        if re.search(r'\b(who|what|which)\b', query_lower):
            result_types.append("entity_info")
        
        return result_types or ["related_entity"]
    
    def _identify_performance_concerns(
        self, 
        query_text: str, 
        entities: List[Dict[str, Any]], 
        complexity: Dict[str, Any]
    ) -> List[str]:
        """Identify potential performance concerns"""
        concerns = []
        
        if not entities:
            concerns.append("No entities extracted - may result in empty results")
        
        if len(entities) > 5:
            concerns.append("Many entities may lead to combinatorial explosion")
        
        if complexity["overall_complexity_score"] > 0.8:
            concerns.append("High complexity query may require extended processing time")
        
        if len(query_text) > 200:
            concerns.append("Very long query may have parsing difficulties")
        
        if complexity["relationship_complexity"] > 0.8:
            concerns.append("Complex relationship queries may require multiple hops")
        
        # Check for low-confidence entities
        if entities:
            low_confidence_entities = [e for e in entities if e.get("confidence", 0.5) < 0.6]
            if len(low_confidence_entities) > len(entities) * 0.5:
                concerns.append("Many low-confidence entities may affect result quality")
        
        return concerns
    
    def _update_analysis_stats(self, analysis: Dict[str, Any]):
        """Update analysis statistics"""
        complexity_level = analysis["complexity_analysis"]["complexity_level"]
        
        if complexity_level == "complex":
            self.analysis_stats["complex_queries"] += 1
        else:
            self.analysis_stats["simple_queries"] += 1
        
        entity_count = analysis["entity_analysis"]["entity_count"]
        if entity_count > 1:
            self.analysis_stats["multi_entity_queries"] += 1
        else:
            self.analysis_stats["single_entity_queries"] += 1
    
    def get_query_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate human-readable insights about the query"""
        insights = []
        
        complexity = analysis["complexity_analysis"]
        entities = analysis["entity_analysis"]
        patterns = analysis["pattern_analysis"]
        
        # Complexity insights
        if complexity["complexity_level"] == "complex":
            insights.append("This is a complex query that may require extended processing time.")
        elif complexity["complexity_level"] == "moderate":
            insights.append("This is a moderately complex query with good prospects for meaningful results.")
        else:
            insights.append("This is a simple query that should process quickly.")
        
        # Entity insights
        if entities["entity_count"] == 0:
            insights.append("No entities were detected in the query, which may limit result quality.")
        elif entities["entity_count"] == 1:
            insights.append("Single entity detected - will search for related entities.")
        else:
            insights.append(f"Multiple entities detected ({entities['entity_count']}) - will search for paths between them.")
        
        # Pattern insights
        if patterns["primary_query_pattern"]:
            pattern_name = patterns["primary_query_pattern"].replace("_", " ").title()
            insights.append(f"Query appears to be a {pattern_name} type.")
        
        if patterns["is_relational"]:
            insights.append("Query seeks relationship information - multi-hop paths will be prioritized.")
        
        return insights
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get query analysis statistics"""
        return {
            **self.analysis_stats,
            "pattern_types_supported": len(self.query_patterns)
        }