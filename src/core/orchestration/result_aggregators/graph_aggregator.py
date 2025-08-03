"""Graph Aggregator (<150 lines)

Graph-based aggregation for complex relationship analysis.
Provides advanced aggregation for graph-structured data.
"""

from typing import Dict, Any, List, Set
from collections import defaultdict
from ...logging_config import get_logger

logger = get_logger("core.orchestration.graph_aggregator")


class GraphAggregator:
    """Graph-based aggregator for complex relationship analysis"""
    
    def __init__(self):
        self.logger = get_logger("core.orchestration.graph_aggregator")
        
    def aggregate(self, execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate execution results with graph-based analysis
        
        Args:
            execution_results: Results from pipeline execution
            
        Returns:
            Aggregated results with graph analysis
        """
        if not execution_results:
            return self._create_empty_result()
            
        try:
            # Extract final data from execution results
            final_data = execution_results.get("final_data", {})
            execution_result_list = execution_results.get("execution_results", [])
            
            # Perform graph-based aggregation
            graph_analysis = self._analyze_graph_structure(final_data)
            entity_analysis = self._analyze_entity_patterns(final_data)
            relationship_analysis = self._analyze_relationship_patterns(final_data)
            
            # Create comprehensive result
            unified_result = {
                "status": execution_results.get("status", "unknown"),
                "data": {
                    "entities": self._aggregate_entities_with_analysis(final_data, entity_analysis),
                    "relationships": self._aggregate_relationships_with_analysis(final_data, relationship_analysis),
                    "graph_structure": graph_analysis,
                    "documents": final_data.get("documents", []),
                    "chunks": final_data.get("chunks", []),
                    "query_results": final_data.get("query_results", [])
                },
                "analysis": {
                    "entity_analysis": entity_analysis,
                    "relationship_analysis": relationship_analysis,
                    "graph_metrics": self._calculate_graph_metrics(graph_analysis),
                    "centrality_analysis": self._analyze_centrality(final_data)
                },
                "summary": self._calculate_graph_summary(graph_analysis, entity_analysis, relationship_analysis),
                "execution_metadata": execution_results.get("execution_metadata", {}),
                "tool_results": self._summarize_tool_results(execution_result_list)
            }
            
            self.logger.info(f"Graph aggregation complete: {unified_result['summary']['total_entities']} entities, {unified_result['summary']['total_relationships']} relationships")
            
            return unified_result
            
        except Exception as e:
            self.logger.error(f"Error in graph aggregation: {e}")
            return self._create_error_result(str(e))
            
    def _analyze_graph_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall graph structure"""
        entities = data.get("entities", [])
        relationships = data.get("relationships", [])
        
        # Build adjacency structure
        adjacency = defaultdict(set)
        entity_types = defaultdict(int)
        relationship_types = defaultdict(int)
        
        # Process entities
        entity_ids = set()
        for entity in entities:
            if isinstance(entity, dict):
                entity_id = entity.get("entity_id")
                entity_type = entity.get("entity_type", "UNKNOWN")
                if entity_id:
                    entity_ids.add(entity_id)
                    entity_types[entity_type] += 1
        
        # Process relationships
        for rel in relationships:
            if isinstance(rel, dict):
                subject_id = rel.get("subject_entity_id")
                object_id = rel.get("object_entity_id")
                rel_type = rel.get("relationship_type", "UNKNOWN")
                
                if subject_id and object_id:
                    adjacency[subject_id].add(object_id)
                    adjacency[object_id].add(subject_id)  # Undirected for analysis
                    relationship_types[rel_type] += 1
        
        # Calculate graph metrics
        connected_components = self._find_connected_components(adjacency, entity_ids)
        
        return {
            "total_nodes": len(entity_ids),
            "total_edges": len(relationships),
            "entity_type_distribution": dict(entity_types),
            "relationship_type_distribution": dict(relationship_types),
            "connected_components": len(connected_components),
            "largest_component_size": max(len(comp) for comp in connected_components) if connected_components else 0,
            "adjacency_data": {node: list(neighbors) for node, neighbors in adjacency.items()},
            "density": self._calculate_graph_density(len(entity_ids), len(relationships))
        }
        
    def _analyze_entity_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze entity patterns and characteristics"""
        entities = data.get("entities", [])
        
        type_confidence = defaultdict(list)
        source_distribution = defaultdict(int)
        mention_counts = defaultdict(int)
        
        for entity in entities:
            if isinstance(entity, dict):
                entity_type = entity.get("entity_type", "UNKNOWN")
                confidence = entity.get("confidence", 0.0)
                source_chunks = entity.get("source_chunks", [])
                
                type_confidence[entity_type].append(confidence)
                source_distribution[len(source_chunks)] += 1
                mention_counts[entity.get("entity_id")] = len(source_chunks)
        
        # Calculate average confidence by type
        avg_confidence_by_type = {}
        for entity_type, confidences in type_confidence.items():
            avg_confidence_by_type[entity_type] = sum(confidences) / len(confidences)
        
        return {
            "total_entities": len(entities),
            "entity_types": list(type_confidence.keys()),
            "average_confidence_by_type": avg_confidence_by_type,
            "source_chunk_distribution": dict(source_distribution),
            "high_confidence_entities": len([e for e in entities if e.get("confidence", 0) > 0.8]),
            "most_mentioned_entities": sorted(mention_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        }
        
    def _analyze_relationship_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze relationship patterns and characteristics"""
        relationships = data.get("relationships", [])
        
        type_confidence = defaultdict(list)
        entity_connections = defaultdict(int)
        
        for rel in relationships:
            if isinstance(rel, dict):
                rel_type = rel.get("relationship_type", "UNKNOWN")
                confidence = rel.get("confidence", 0.0)
                subject_id = rel.get("subject_entity_id")
                object_id = rel.get("object_entity_id")
                
                type_confidence[rel_type].append(confidence)
                if subject_id:
                    entity_connections[subject_id] += 1
                if object_id:
                    entity_connections[object_id] += 1
        
        # Calculate average confidence by relationship type
        avg_confidence_by_type = {}
        for rel_type, confidences in type_confidence.items():
            avg_confidence_by_type[rel_type] = sum(confidences) / len(confidences)
        
        return {
            "total_relationships": len(relationships),
            "relationship_types": list(type_confidence.keys()),
            "average_confidence_by_type": avg_confidence_by_type,
            "high_confidence_relationships": len([r for r in relationships if r.get("confidence", 0) > 0.8]),
            "most_connected_entities": sorted(entity_connections.items(), key=lambda x: x[1], reverse=True)[:10]
        }
        
    def _find_connected_components(self, adjacency: Dict[str, Set[str]], all_nodes: Set[str]) -> List[List[str]]:
        """Find connected components in the graph"""
        visited = set()
        components = []
        
        def dfs(node, component):
            if node in visited:
                return
            visited.add(node)
            component.append(node)
            for neighbor in adjacency.get(node, []):
                dfs(neighbor, component)
        
        for node in all_nodes:
            if node not in visited:
                component = []
                dfs(node, component)
                components.append(component)
                
        return components
        
    def _calculate_graph_density(self, num_nodes: int, num_edges: int) -> float:
        """Calculate graph density"""
        if num_nodes <= 1:
            return 0.0
        max_edges = num_nodes * (num_nodes - 1) / 2  # Undirected graph
        return num_edges / max_edges if max_edges > 0 else 0.0
        
    def _calculate_graph_metrics(self, graph_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate advanced graph metrics"""
        return {
            "clustering_coefficient": self._estimate_clustering_coefficient(graph_structure),
            "average_degree": (2 * graph_structure["total_edges"]) / graph_structure["total_nodes"] if graph_structure["total_nodes"] > 0 else 0,
            "component_ratio": graph_structure["connected_components"] / graph_structure["total_nodes"] if graph_structure["total_nodes"] > 0 else 0
        }
        
    def _estimate_clustering_coefficient(self, graph_structure: Dict[str, Any]) -> float:
        """Estimate clustering coefficient"""
        # Simplified estimation based on graph structure
        if graph_structure["total_nodes"] == 0:
            return 0.0
        return min(1.0, graph_structure["density"] * 2)  # Rough estimation
        
    def _analyze_centrality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze centrality measures from PageRank if available"""
        pagerank_scores = data.get("pagerank_scores", [])
        
        if not pagerank_scores:
            return {"pagerank_available": False}
            
        # Analyze PageRank distribution
        scores = [score.get("pagerank_score", 0.0) for score in pagerank_scores if isinstance(score, dict)]
        
        if not scores:
            return {"pagerank_available": False}
            
        return {
            "pagerank_available": True,
            "top_entities": sorted(pagerank_scores, key=lambda x: x.get("pagerank_score", 0), reverse=True)[:10],
            "average_pagerank": sum(scores) / len(scores),
            "max_pagerank": max(scores),
            "min_pagerank": min(scores)
        }
        
    def _aggregate_entities_with_analysis(self, data: Dict[str, Any], entity_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aggregate entities with additional analysis data"""
        entities = data.get("entities", [])
        
        # Add analysis metadata to entities
        enhanced_entities = []
        for entity in entities:
            if isinstance(entity, dict):
                enhanced_entity = entity.copy()
                entity_type = entity.get("entity_type", "UNKNOWN")
                
                # Add type-specific analysis
                enhanced_entity["type_avg_confidence"] = entity_analysis.get("average_confidence_by_type", {}).get(entity_type, 0.0)
                enhanced_entity["is_high_confidence"] = entity.get("confidence", 0.0) > 0.8
                
                enhanced_entities.append(enhanced_entity)
                
        return enhanced_entities
        
    def _aggregate_relationships_with_analysis(self, data: Dict[str, Any], relationship_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aggregate relationships with additional analysis data"""
        relationships = data.get("relationships", [])
        
        # Add analysis metadata to relationships
        enhanced_relationships = []
        for rel in relationships:
            if isinstance(rel, dict):
                enhanced_rel = rel.copy()
                rel_type = rel.get("relationship_type", "UNKNOWN")
                
                # Add type-specific analysis
                enhanced_rel["type_avg_confidence"] = relationship_analysis.get("average_confidence_by_type", {}).get(rel_type, 0.0)
                enhanced_rel["is_high_confidence"] = rel.get("confidence", 0.0) > 0.8
                
                enhanced_relationships.append(enhanced_rel)
                
        return enhanced_relationships
        
    def _calculate_graph_summary(self, graph_analysis: Dict[str, Any], 
                                entity_analysis: Dict[str, Any], 
                                relationship_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive graph summary"""
        return {
            "total_entities": entity_analysis.get("total_entities", 0),
            "total_relationships": relationship_analysis.get("total_relationships", 0),
            "connected_components": graph_analysis.get("connected_components", 0),
            "graph_density": graph_analysis.get("density", 0.0),
            "high_confidence_entities": entity_analysis.get("high_confidence_entities", 0),
            "high_confidence_relationships": relationship_analysis.get("high_confidence_relationships", 0),
            "entity_types": len(entity_analysis.get("entity_types", [])),
            "relationship_types": len(relationship_analysis.get("relationship_types", []))
        }
        
    def _summarize_tool_results(self, execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize tool execution results"""
        return {tool.get("tool_name", "unknown"): tool.get("status", "unknown") for tool in execution_results}
        
    def _create_empty_result(self) -> Dict[str, Any]:
        """Create empty result structure"""
        return {
            "status": "empty",
            "data": {"entities": [], "relationships": [], "graph_structure": {}, "documents": [], "chunks": [], "query_results": []},
            "analysis": {"entity_analysis": {}, "relationship_analysis": {}, "graph_metrics": {}, "centrality_analysis": {}},
            "summary": {"total_entities": 0, "total_relationships": 0, "connected_components": 0, "graph_density": 0.0},
            "execution_metadata": {},
            "tool_results": {}
        }
        
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result structure"""
        result = self._create_empty_result()
        result["status"] = "error"
        result["error"] = error_message
        return result