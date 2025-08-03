"""
Path Finder for Multi-hop Query Tool

Finds multi-hop paths between entities and related entities in the Neo4j graph.
Handles 1-hop, 2-hop, and 3-hop path discovery with confidence scoring.
"""

import logging
from typing import Dict, Any, List
from .connection_manager import Neo4jConnectionManager

logger = logging.getLogger(__name__)


class PathFinder:
    """Finds multi-hop paths between entities in the graph"""
    
    def __init__(self, connection_manager: Neo4jConnectionManager):
        self.connection_manager = connection_manager
        self.logger = logging.getLogger("multihop_query.path_finder")
        
        # Path finding statistics
        self.path_stats = {
            "path_queries_executed": 0,
            "paths_found": 0,
            "unique_paths": 0,
            "average_path_length": 0.0
        }
    
    def find_multihop_paths(
        self, 
        query_entities: List[Dict[str, Any]], 
        max_hops: int,
        result_limit: int
    ) -> List[Dict[str, Any]]:
        """Find multi-hop paths between and around query entities"""
        all_paths = []
        
        try:
            # Find paths between entity pairs if we have multiple entities
            if len(query_entities) >= 2:
                inter_entity_paths = self._find_paths_between_entity_pairs(
                    query_entities, max_hops
                )
                all_paths.extend(inter_entity_paths)
            
            # Find related entities for each query entity
            for entity in query_entities:
                related_paths = self._find_related_entity_paths(
                    entity, max_hops, result_limit // len(query_entities) if len(query_entities) > 0 else result_limit
                )
                all_paths.extend(related_paths)
            
            # Update statistics
            self.path_stats["paths_found"] = len(all_paths)
            self.path_stats["unique_paths"] = len(set(self._get_path_signature(path) for path in all_paths))
            
            if all_paths:
                path_lengths = [path.get("path_length", 1) for path in all_paths if "path_length" in path]
                if path_lengths:
                    self.path_stats["average_path_length"] = sum(path_lengths) / len(path_lengths)
            
            return all_paths
            
        except Exception as e:
            self.logger.error(f"Multi-hop path finding failed: {e}")
            return []
    
    def _find_paths_between_entity_pairs(
        self, 
        query_entities: List[Dict[str, Any]], 
        max_hops: int
    ) -> List[Dict[str, Any]]:
        """Find paths between pairs of query entities"""
        paths = []
        
        for i, source_entity in enumerate(query_entities):
            for target_entity in query_entities[i+1:]:
                try:
                    entity_pair_paths = self._find_paths_between_entities(
                        source_entity, target_entity, max_hops
                    )
                    paths.extend(entity_pair_paths)
                    self.path_stats["path_queries_executed"] += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to find paths between {source_entity['canonical_name']} and {target_entity['canonical_name']}: {e}")
                    continue
        
        return paths
    
    def _find_paths_between_entities(
        self, 
        source_entity: Dict[str, Any], 
        target_entity: Dict[str, Any], 
        max_hops: int
    ) -> List[Dict[str, Any]]:
        """Find paths between two specific entities"""
        paths = []
        
        try:
            # Use connection manager to find paths
            path_results = self.connection_manager.find_paths_between_entities(
                source_entity["entity_id"],
                target_entity["entity_id"],
                max_hops,
                limit_per_hop=5
            )
            
            for path_data in path_results:
                path_info = {
                    "result_type": "path",
                    "source_entity": source_entity["canonical_name"],
                    "target_entity": target_entity["canonical_name"],
                    "source_entity_id": source_entity["entity_id"],
                    "target_entity_id": target_entity["entity_id"],
                    "path": path_data["path_names"],
                    "relationship_types": path_data["relationship_types"],
                    "path_length": path_data["path_length"],
                    "path_weight": path_data["path_weight"],
                    "hop_count": path_data["hop_count"],
                    "confidence": self._calculate_path_confidence(
                        path_data["path_weight"], 
                        path_data["path_length"]
                    ),
                    "explanation": self._generate_path_explanation(
                        path_data["path_names"], 
                        path_data["relationship_types"]
                    )
                }
                paths.append(path_info)
                
        except Exception as e:
            self.logger.error(f"Path finding between entities failed: {e}")
        
        return paths
    
    def _find_related_entity_paths(
        self, 
        entity: Dict[str, Any], 
        max_hops: int,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Find entities related to a query entity"""
        related_paths = []
        
        try:
            # Use connection manager to find related entities
            related_results = self.connection_manager.find_related_entities(
                entity["entity_id"], max_hops, limit
            )
            
            for related_data in related_results:
                related_info = {
                    "result_type": "related_entity",
                    "query_entity": entity["canonical_name"],
                    "query_entity_id": entity["entity_id"],
                    "related_entity": related_data["canonical_name"],
                    "related_entity_id": related_data["entity_id"],
                    "entity_type": related_data["entity_type"],
                    "pagerank_score": related_data["pagerank_score"] or 0.0001,
                    "connection_count": related_data["connection_count"],
                    "confidence": self._calculate_related_confidence(
                        related_data["pagerank_score"] or 0.0001,
                        related_data["connection_count"],
                        related_data["confidence"] or 0.5
                    ),
                    "explanation": f"{related_data['canonical_name']} is connected to {entity['canonical_name']} through {related_data['connection_count']} path(s)"
                }
                related_paths.append(related_info)
                
        except Exception as e:
            self.logger.error(f"Related entity search failed for {entity['canonical_name']}: {e}")
        
        return related_paths
    
    def _calculate_path_confidence(self, path_weight: float, path_length: int) -> float:
        """Calculate confidence score for a path"""
        # Base confidence from path weight
        weight_confidence = min(path_weight * 10.0, 1.0)  # Scale up small weights
        
        # Length penalty (longer paths are less confident)
        length_penalty = 1.0 / (1.0 + (path_length - 1) * 0.2)
        
        confidence = weight_confidence * length_penalty
        return max(0.1, min(1.0, confidence))
    
    def _calculate_related_confidence(
        self, 
        pagerank_score: float, 
        connection_count: int, 
        base_confidence: float
    ) -> float:
        """Calculate confidence for a related entity result"""
        # Combine PageRank, connection count, and base confidence
        pagerank_factor = min(pagerank_score * 1000, 1.0)  # Scale up small PageRank scores
        connection_factor = min(connection_count / 5.0, 1.0)  # Scale connection count
        
        confidence = (pagerank_factor * 0.4) + (connection_factor * 0.3) + (base_confidence * 0.3)
        return max(0.1, min(1.0, confidence))
    
    def _generate_path_explanation(self, path_names: List[str], relationship_types: List[str]) -> str:
        """Generate human-readable explanation for a path"""
        if not path_names or len(path_names) < 2:
            return "No path found"
        
        if not relationship_types or len(relationship_types) != len(path_names) - 1:
            return f"Path: {' -> '.join(path_names)}"
        
        explanation_parts = []
        for i in range(len(relationship_types)):
            source = path_names[i]
            target = path_names[i + 1]
            relation = relationship_types[i].replace("_", " ").lower()
            explanation_parts.append(f"{source} {relation} {target}")
        
        return "; ".join(explanation_parts)
    
    def _get_path_signature(self, path: Dict[str, Any]) -> str:
        """Get a unique signature for a path for deduplication"""
        if path.get("result_type") == "path":
            return f"path:{path.get('source_entity_id', '')}:{path.get('target_entity_id', '')}:{path.get('path_length', 0)}"
        elif path.get("result_type") == "related_entity":
            return f"related:{path.get('query_entity_id', '')}:{path.get('related_entity_id', '')}"
        else:
            return f"unknown:{path.get('entity_id', '')}"
    
    def analyze_path_distribution(self, paths: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze distribution of path lengths and types"""
        if not paths:
            return {}
        
        result_types = {}
        path_lengths = []
        confidence_ranges = {"high": 0, "medium": 0, "low": 0}
        hop_distribution = {}
        
        for path in paths:
            # Count result types
            result_type = path.get("result_type", "unknown")
            result_types[result_type] = result_types.get(result_type, 0) + 1
            
            # Collect path lengths
            if "path_length" in path:
                path_lengths.append(path["path_length"])
            
            # Count hop distribution
            if "hop_count" in path:
                hop_count = path["hop_count"]
                hop_distribution[hop_count] = hop_distribution.get(hop_count, 0) + 1
            
            # Count confidence ranges
            confidence = path.get("confidence", 0.5)
            if confidence >= 0.8:
                confidence_ranges["high"] += 1
            elif confidence >= 0.5:
                confidence_ranges["medium"] += 1
            else:
                confidence_ranges["low"] += 1
        
        analysis = {
            "total_paths": len(paths),
            "result_type_distribution": result_types,
            "confidence_distribution": confidence_ranges,
            "hop_distribution": hop_distribution
        }
        
        if path_lengths:
            analysis["path_length_stats"] = {
                "min_length": min(path_lengths),
                "max_length": max(path_lengths),
                "avg_length": sum(path_lengths) / len(path_lengths),
                "unique_lengths": len(set(path_lengths))
            }
        
        return analysis
    
    def filter_paths_by_quality(
        self, 
        paths: List[Dict[str, Any]], 
        min_confidence: float = 0.3,
        min_path_weight: float = 0.01
    ) -> List[Dict[str, Any]]:
        """Filter paths by quality criteria"""
        filtered_paths = []
        
        for path in paths:
            # Check confidence threshold
            if path.get("confidence", 0.0) < min_confidence:
                continue
            
            # Check path weight for path results
            if path.get("result_type") == "path":
                if path.get("path_weight", 0.0) < min_path_weight:
                    continue
            
            # Check PageRank score for related entities
            if path.get("result_type") == "related_entity":
                if path.get("pagerank_score", 0.0) <= 0.0:
                    continue
            
            filtered_paths.append(path)
        
        return filtered_paths
    
    def get_path_finding_stats(self) -> Dict[str, Any]:
        """Get path finding statistics"""
        return {
            **self.path_stats,
            "connection_manager_available": self.connection_manager.driver is not None
        }
    
    def find_shortest_paths(
        self, 
        source_entity: Dict[str, Any], 
        target_entity: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find shortest paths between two entities (optimized for speed)"""
        try:
            # Use a more targeted query for shortest paths
            shortest_paths = self.connection_manager.find_paths_between_entities(
                source_entity["entity_id"],
                target_entity["entity_id"],
                max_hops=2,  # Limit to 2 hops for shortest paths
                limit_per_hop=3
            )
            
            # Sort by path length and weight
            sorted_paths = sorted(shortest_paths, key=lambda p: (p["path_length"], -p["path_weight"]))
            
            # Convert to standard format
            result_paths = []
            for path_data in sorted_paths:
                path_info = {
                    "result_type": "shortest_path",
                    "source_entity": source_entity["canonical_name"],
                    "target_entity": target_entity["canonical_name"],
                    "path": path_data["path_names"],
                    "relationship_types": path_data["relationship_types"],
                    "path_length": path_data["path_length"],
                    "path_weight": path_data["path_weight"],
                    "confidence": self._calculate_path_confidence(
                        path_data["path_weight"], 
                        path_data["path_length"]
                    ),
                    "explanation": self._generate_path_explanation(
                        path_data["path_names"], 
                        path_data["relationship_types"]
                    )
                }
                result_paths.append(path_info)
            
            return result_paths
            
        except Exception as e:
            self.logger.error(f"Shortest path finding failed: {e}")
            return []