"""Centrality and Network Analysis

Analyzes dynamic centrality, temporal paths, and community evolution.
"""

from typing import Dict, List, Any
import networkx as nx
import numpy as np
from collections import defaultdict

from .temporal_data_models import TemporalSnapshot
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class CentralityAnalyzer:
    """Analyzes centrality and network structure evolution"""
    
    def analyze_dynamic_centrality(self, snapshots: List[TemporalSnapshot]) -> Dict[str, Any]:
        """Analyze how node centrality changes over time"""
        try:
            centrality_results = {
                "centrality_evolution": {},
                "stability_ranking": {},
                "emerging_nodes": [],
                "declining_nodes": []
            }
            
            # Track centrality for each node across time
            node_centrality = defaultdict(list)
            timestamps = []
            
            for snapshot in snapshots:
                timestamps.append(snapshot.timestamp)
                
                if len(snapshot.graph.nodes) > 0:
                    # Calculate degree centrality
                    centrality = nx.degree_centrality(snapshot.graph)
                    
                    for node_id, cent_value in centrality.items():
                        node_centrality[node_id].append(cent_value)
                    
                    # Pad missing nodes with 0
                    all_nodes = set()
                    for s in snapshots:
                        all_nodes.update(s.graph.nodes)
                    
                    for node_id in all_nodes:
                        if node_id not in centrality:
                            node_centrality[node_id].append(0.0)
            
            # Analyze centrality evolution for each node
            for node_id, centrality_values in node_centrality.items():
                centrality_results["centrality_evolution"][node_id] = {
                    "values": centrality_values,
                    "timestamps": timestamps[:len(centrality_values)],
                    "trend": self._calculate_trend(centrality_values),
                    "volatility": np.std(centrality_values) if len(centrality_values) > 1 else 0,
                    "peak_centrality": max(centrality_values),
                    "average_centrality": np.mean(centrality_values)
                }
            
            # Identify emerging and declining nodes
            centrality_results["emerging_nodes"] = self._identify_emerging_nodes(
                centrality_results["centrality_evolution"]
            )
            centrality_results["declining_nodes"] = self._identify_declining_nodes(
                centrality_results["centrality_evolution"]
            )
            
            # Calculate stability ranking
            centrality_results["stability_ranking"] = self._calculate_stability_ranking(
                centrality_results["centrality_evolution"]
            )
            
            return centrality_results
            
        except Exception as e:
            logger.error(f"Dynamic centrality analysis failed: {e}")
            raise
    
    def analyze_temporal_paths(self, snapshots: List[TemporalSnapshot]) -> Dict[str, Any]:
        """Analyze temporal paths and connectivity evolution"""
        try:
            path_results = {
                "connectivity_evolution": {},
                "path_stability": {},
                "temporal_reachability": {}
            }
            
            # Analyze connectivity for each snapshot
            connectivity_metrics = []
            
            for snapshot in snapshots:
                if len(snapshot.graph.nodes) > 0:
                    # Calculate connectivity metrics
                    connectivity = {
                        "timestamp": snapshot.timestamp,
                        "average_path_length": 0,
                        "diameter": 0,
                        "connectivity": nx.is_connected(snapshot.graph)
                    }
                    
                    if nx.is_connected(snapshot.graph):
                        connectivity["average_path_length"] = nx.average_shortest_path_length(snapshot.graph)
                        connectivity["diameter"] = nx.diameter(snapshot.graph)
                    
                    connectivity_metrics.append(connectivity)
            
            path_results["connectivity_evolution"] = connectivity_metrics
            
            # Analyze path stability between consecutive snapshots
            path_stability = []
            for i in range(1, len(snapshots)):
                stability = self._calculate_path_stability(snapshots[i-1], snapshots[i])
                path_stability.append({
                    "from_timestamp": snapshots[i-1].timestamp,
                    "to_timestamp": snapshots[i].timestamp,
                    "stability_score": stability
                })
            
            path_results["path_stability"] = path_stability
            
            return path_results
            
        except Exception as e:
            logger.error(f"Temporal path analysis failed: {e}")
            raise
    
    def analyze_community_evolution(self, snapshots: List[TemporalSnapshot]) -> Dict[str, Any]:
        """Analyze how communities evolve over time"""
        try:
            community_results = {
                "community_evolution": [],
                "stability_scores": [],
                "community_events": []
            }
            
            # Detect communities in each snapshot
            snapshot_communities = []
            
            for snapshot in snapshots:
                if len(snapshot.graph.nodes) > 0:
                    try:
                        # Use Louvain algorithm for community detection
                        communities = nx.community.louvain_communities(snapshot.graph)
                        snapshot_communities.append({
                            "timestamp": snapshot.timestamp,
                            "communities": [list(community) for community in communities],
                            "num_communities": len(communities)
                        })
                    except:
                        # Fallback to connected components
                        communities = list(nx.connected_components(snapshot.graph))
                        snapshot_communities.append({
                            "timestamp": snapshot.timestamp,
                            "communities": [list(community) for community in communities],
                            "num_communities": len(communities)
                        })
                else:
                    snapshot_communities.append({
                        "timestamp": snapshot.timestamp,
                        "communities": [],
                        "num_communities": 0
                    })
            
            community_results["community_evolution"] = snapshot_communities
            
            # Calculate community stability between consecutive snapshots
            for i in range(1, len(snapshot_communities)):
                prev_communities = snapshot_communities[i-1]["communities"]
                curr_communities = snapshot_communities[i]["communities"]
                
                stability_score = self._calculate_community_stability(
                    prev_communities, curr_communities
                )
                
                community_results["stability_scores"].append({
                    "from_timestamp": snapshot_communities[i-1]["timestamp"],
                    "to_timestamp": snapshot_communities[i]["timestamp"],
                    "stability_score": stability_score
                })
            
            return community_results
            
        except Exception as e:
            logger.error(f"Community evolution analysis failed: {e}")
            raise
    
    # Helper methods
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear trend
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if abs(slope) < 0.01:
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"
    
    def _identify_emerging_nodes(self, centrality_evolution: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Identify nodes with increasing centrality"""
        emerging = []
        
        for node_id, evolution in centrality_evolution.items():
            if evolution["trend"] == "increasing" and evolution["volatility"] < 0.5:
                emerging.append({
                    "node_id": node_id,
                    "centrality_increase": evolution["values"][-1] - evolution["values"][0],
                    "peak_centrality": evolution["peak_centrality"],
                    "trend_strength": evolution.get("trend_strength", 0)
                })
        
        # Sort by centrality increase
        emerging.sort(key=lambda x: x["centrality_increase"], reverse=True)
        return emerging[:10]  # Top 10
    
    def _identify_declining_nodes(self, centrality_evolution: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Identify nodes with decreasing centrality"""
        declining = []
        
        for node_id, evolution in centrality_evolution.items():
            if evolution["trend"] == "decreasing" and evolution["volatility"] < 0.5:
                declining.append({
                    "node_id": node_id,
                    "centrality_decrease": evolution["values"][0] - evolution["values"][-1],
                    "peak_centrality": evolution["peak_centrality"],
                    "trend_strength": evolution.get("trend_strength", 0)
                })
        
        # Sort by centrality decrease
        declining.sort(key=lambda x: x["centrality_decrease"], reverse=True)
        return declining[:10]  # Top 10
    
    def _calculate_stability_ranking(self, centrality_evolution: Dict[str, Dict]) -> Dict[str, float]:
        """Calculate stability ranking for nodes"""
        stability_scores = {}
        
        for node_id, evolution in centrality_evolution.items():
            # Stability is inverse of volatility
            stability = 1.0 / (1.0 + evolution["volatility"])
            stability_scores[node_id] = stability
        
        return stability_scores
    
    def _calculate_path_stability(self, prev_snapshot: TemporalSnapshot, 
                                curr_snapshot: TemporalSnapshot) -> float:
        """Calculate path stability between two snapshots"""
        # Simple measure: fraction of common edges
        prev_edges = set(prev_snapshot.graph.edges)
        curr_edges = set(curr_snapshot.graph.edges)
        
        if not prev_edges and not curr_edges:
            return 1.0
        
        common_edges = prev_edges & curr_edges
        total_edges = prev_edges | curr_edges
        
        return len(common_edges) / len(total_edges) if total_edges else 1.0
    
    def _calculate_community_stability(self, prev_communities: List[List[str]], 
                                     curr_communities: List[List[str]]) -> float:
        """Calculate community stability using Jaccard similarity"""
        if not prev_communities and not curr_communities:
            return 1.0
        
        # Convert to sets for easier comparison
        prev_sets = [set(community) for community in prev_communities]
        curr_sets = [set(community) for community in curr_communities]
        
        # Calculate maximum Jaccard similarity between community pairs
        max_similarities = []
        
        for prev_comm in prev_sets:
            max_sim = 0
            for curr_comm in curr_sets:
                intersection = len(prev_comm & curr_comm)
                union = len(prev_comm | curr_comm)
                jaccard = intersection / union if union > 0 else 0
                max_sim = max(max_sim, jaccard)
            max_similarities.append(max_sim)
        
        return np.mean(max_similarities) if max_similarities else 0.0