"""
Result Ranker for Multi-hop Query Tool

Ranks and scores query results based on confidence, PageRank scores,
path weights, and other relevance factors.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ResultRanker:
    """Ranks and scores multi-hop query results"""
    
    def __init__(self, pagerank_boost_factor: float = 2.0):
        self.pagerank_boost_factor = pagerank_boost_factor
        self.logger = logging.getLogger("multihop_query.result_ranker")
        
        # Ranking statistics
        self.ranking_stats = {
            "results_ranked": 0,
            "high_confidence_results": 0,
            "medium_confidence_results": 0,
            "low_confidence_results": 0,
            "filtered_out_results": 0
        }
    
    def rank_query_results(
        self, 
        results: List[Dict[str, Any]], 
        query_text: str,
        min_path_weight: float = 0.01,
        min_confidence: float = 0.1
    ) -> List[Dict[str, Any]]:
        """Rank query results by relevance and confidence"""
        if not results:
            return []
        
        # Calculate ranking scores for all results
        scored_results = self._calculate_ranking_scores(results, query_text, min_path_weight)
        
        # Filter out very low scoring results
        filtered_results = self._filter_low_quality_results(scored_results, min_confidence)
        
        # Sort by ranking score descending
        ranked_results = sorted(filtered_results, key=lambda x: x.get("ranking_score", 0), reverse=True)
        
        # Add final rankings
        for i, result in enumerate(ranked_results, 1):
            result["rank"] = i
        
        # Update statistics
        self._update_ranking_stats(results, ranked_results)
        
        return ranked_results
    
    def _calculate_ranking_scores(
        self, 
        results: List[Dict[str, Any]], 
        query_text: str,
        min_path_weight: float
    ) -> List[Dict[str, Any]]:
        """Calculate ranking scores for all results"""
        scored_results = []
        
        for result in results:
            ranking_score = self._calculate_individual_ranking_score(result, query_text, min_path_weight)
            
            # Add ranking score to result
            result_with_score = result.copy()
            result_with_score["ranking_score"] = ranking_score
            scored_results.append(result_with_score)
        
        return scored_results
    
    def _calculate_individual_ranking_score(
        self, 
        result: Dict[str, Any], 
        query_text: str,
        min_path_weight: float
    ) -> float:
        """Calculate ranking score for a single result"""
        ranking_score = 0.0
        
        # Base score from confidence (40% weight)
        confidence = result.get("confidence", 0.5)
        ranking_score += confidence * 0.4
        
        # PageRank boost (30% weight)
        pagerank_score = result.get("pagerank_score", 0.0001)
        ranking_score += pagerank_score * self.pagerank_boost_factor * 0.3
        
        # Result type specific scoring
        result_type = result.get("result_type", "unknown")
        
        if result_type == "path":
            # Path weight boost (20% weight)
            path_weight = result.get("path_weight", 0.0)
            if path_weight >= min_path_weight:
                ranking_score += path_weight * 0.2
            else:
                ranking_score *= 0.5  # Penalize low-weight paths
            
            # Prefer shorter paths (10% weight)
            path_length = result.get("path_length", 1)
            ranking_score += (1.0 / path_length) * 0.1
            
        elif result_type == "related_entity":
            # Connection count boost (20% weight)
            connection_count = result.get("connection_count", 1)
            ranking_score += min(connection_count / 10.0, 0.2) * 0.2
            
            # Entity type relevance (10% weight)
            entity_type_boost = self._calculate_entity_type_relevance(result, query_text)
            ranking_score += entity_type_boost * 0.1
        
        # Query relevance boost (additional scoring)
        query_relevance = self._calculate_query_relevance(result, query_text)
        ranking_score += query_relevance * 0.1
        
        return max(0.0, ranking_score)
    
    def _calculate_entity_type_relevance(self, result: Dict[str, Any], query_text: str) -> float:
        """Calculate relevance based on entity type and query content"""
        entity_type = result.get("entity_type", "").lower()
        query_lower = query_text.lower()
        
        # Entity type relevance mapping
        type_relevance = {
            "person": 0.8 if any(word in query_lower for word in ["who", "person", "people", "individual"]) else 0.3,
            "organization": 0.8 if any(word in query_lower for word in ["company", "organization", "business"]) else 0.3,
            "location": 0.8 if any(word in query_lower for word in ["where", "location", "place", "city"]) else 0.3,
            "event": 0.8 if any(word in query_lower for word in ["when", "event", "happened"]) else 0.3,
            "product": 0.6 if any(word in query_lower for word in ["what", "product", "item"]) else 0.2
        }
        
        return type_relevance.get(entity_type, 0.5)
    
    def _calculate_query_relevance(self, result: Dict[str, Any], query_text: str) -> float:
        """Calculate relevance based on text matching with query"""
        query_words = set(query_text.lower().split())
        
        # Check for word matches in result text fields
        result_text_fields = [
            result.get("canonical_name", ""),
            result.get("related_entity", ""),
            result.get("source_entity", ""),
            result.get("target_entity", ""),
            result.get("explanation", "")
        ]
        
        result_words = set()
        for field in result_text_fields:
            if field:
                result_words.update(field.lower().split())
        
        # Calculate word overlap
        common_words = query_words.intersection(result_words)
        if query_words:
            relevance_score = len(common_words) / len(query_words)
        else:
            relevance_score = 0.0
        
        return min(relevance_score, 1.0)
    
    def _filter_low_quality_results(
        self, 
        results: List[Dict[str, Any]], 
        min_confidence: float
    ) -> List[Dict[str, Any]]:
        """Filter out low quality results"""
        filtered_results = []
        
        for result in results:
            # Check minimum confidence
            if result.get("confidence", 0.0) < min_confidence:
                self.ranking_stats["filtered_out_results"] += 1
                continue
            
            # Check minimum ranking score
            if result.get("ranking_score", 0.0) < 0.1:
                self.ranking_stats["filtered_out_results"] += 1
                continue
            
            # Additional quality checks for specific result types
            result_type = result.get("result_type", "unknown")
            
            if result_type == "path":
                # Require valid path data
                if not result.get("path") or not result.get("relationship_types"):
                    self.ranking_stats["filtered_out_results"] += 1
                    continue
                
                # Require reasonable path weight
                if result.get("path_weight", 0.0) <= 0.0:
                    self.ranking_stats["filtered_out_results"] += 1
                    continue
            
            elif result_type == "related_entity":
                # Require valid entity data
                if not result.get("related_entity_id"):
                    self.ranking_stats["filtered_out_results"] += 1
                    continue
                
                # Require some PageRank score
                if result.get("pagerank_score", 0.0) <= 0.0:
                    self.ranking_stats["filtered_out_results"] += 1
                    continue
            
            filtered_results.append(result)
        
        return filtered_results
    
    def _update_ranking_stats(self, original_results: List[Dict[str, Any]], ranked_results: List[Dict[str, Any]]):
        """Update ranking statistics"""
        self.ranking_stats["results_ranked"] = len(ranked_results)
        
        # Count confidence ranges
        for result in ranked_results:
            confidence = result.get("confidence", 0.5)
            if confidence >= 0.8:
                self.ranking_stats["high_confidence_results"] += 1
            elif confidence >= 0.5:
                self.ranking_stats["medium_confidence_results"] += 1
            else:
                self.ranking_stats["low_confidence_results"] += 1
    
    def calculate_overall_confidence(self, results: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence for a set of results"""
        if not results:
            return 0.0
        
        # Weight confidence by ranking (higher ranked results get more weight)
        weighted_confidence = 0.0
        total_weight = 0.0
        
        for result in results:
            rank = result.get("rank", 1)
            rank_weight = 1.0 / rank  # Higher rank = higher weight
            confidence = result.get("confidence", 0.5)
            
            weighted_confidence += confidence * rank_weight
            total_weight += rank_weight
        
        return weighted_confidence / total_weight if total_weight > 0 else 0.0
    
    def get_top_results_by_type(
        self, 
        results: List[Dict[str, Any]], 
        result_type: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get top results of a specific type"""
        type_results = [r for r in results if r.get("result_type") == result_type]
        return type_results[:limit]
    
    def analyze_ranking_distribution(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze distribution of ranking scores"""
        if not results:
            return {}
        
        ranking_scores = [r.get("ranking_score", 0.0) for r in results]
        confidence_scores = [r.get("confidence", 0.5) for r in results]
        
        analysis = {
            "total_results": len(results),
            "ranking_score_stats": {
                "min": min(ranking_scores),
                "max": max(ranking_scores),
                "average": sum(ranking_scores) / len(ranking_scores),
                "median": sorted(ranking_scores)[len(ranking_scores) // 2]
            },
            "confidence_score_stats": {
                "min": min(confidence_scores),
                "max": max(confidence_scores),
                "average": sum(confidence_scores) / len(confidence_scores),
                "median": sorted(confidence_scores)[len(confidence_scores) // 2]
            },
            "score_distribution": self._get_score_distribution(ranking_scores),
            "result_type_performance": self._analyze_result_type_performance(results)
        }
        
        return analysis
    
    def _get_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Get distribution of scores in ranges"""
        distribution = {
            "excellent": 0,     # 0.8-1.0
            "good": 0,          # 0.6-0.8
            "acceptable": 0,    # 0.4-0.6
            "poor": 0,          # 0.2-0.4
            "very_poor": 0      # 0.0-0.2
        }
        
        for score in scores:
            if score >= 0.8:
                distribution["excellent"] += 1
            elif score >= 0.6:
                distribution["good"] += 1
            elif score >= 0.4:
                distribution["acceptable"] += 1
            elif score >= 0.2:
                distribution["poor"] += 1
            else:
                distribution["very_poor"] += 1
        
        return distribution
    
    def _analyze_result_type_performance(self, results: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Analyze average performance by result type"""
        type_stats = {}
        
        for result in results:
            result_type = result.get("result_type", "unknown")
            
            if result_type not in type_stats:
                type_stats[result_type] = {
                    "count": 0,
                    "total_ranking_score": 0.0,
                    "total_confidence": 0.0
                }
            
            type_stats[result_type]["count"] += 1
            type_stats[result_type]["total_ranking_score"] += result.get("ranking_score", 0.0)
            type_stats[result_type]["total_confidence"] += result.get("confidence", 0.5)
        
        # Calculate averages
        performance = {}
        for result_type, stats in type_stats.items():
            if stats["count"] > 0:
                performance[result_type] = {
                    "count": stats["count"],
                    "avg_ranking_score": stats["total_ranking_score"] / stats["count"],
                    "avg_confidence": stats["total_confidence"] / stats["count"]
                }
        
        return performance
    
    def get_ranking_stats(self) -> Dict[str, Any]:
        """Get ranking statistics"""
        return {
            **self.ranking_stats,
            "pagerank_boost_factor": self.pagerank_boost_factor
        }
    
    def update_ranking_parameters(self, **kwargs):
        """Update ranking parameters"""
        if "pagerank_boost_factor" in kwargs:
            self.pagerank_boost_factor = kwargs["pagerank_boost_factor"]
            self.logger.info(f"Updated PageRank boost factor to {self.pagerank_boost_factor}")
    
    def get_ranking_criteria(self) -> Dict[str, str]:
        """Get description of ranking criteria used"""
        return {
            "confidence_weight": "40% - Base confidence from extraction/calculation",
            "pagerank_weight": "30% - PageRank score boost for entity importance",
            "path_weight": "20% - Path weight for path results, connection count for related entities",
            "path_length_bonus": "10% - Shorter paths get higher scores",
            "query_relevance": "10% - Text matching with query terms",
            "entity_type_relevance": "Variable - Based on query context and entity type",
            "quality_filters": "Minimum confidence and ranking score thresholds"
        }