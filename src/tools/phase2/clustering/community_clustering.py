"""Community Detection Algorithms

NetworkX-based community detection algorithms.
"""

from typing import Dict, List, Any, Set
import networkx as nx
import numpy as np
from collections import defaultdict

from .clustering_data_models import ClusteringResult
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class CommunityDetection:
    """Community detection algorithms"""
    
    def louvain_clustering(self, graph: nx.Graph, config: Dict[str, Any]) -> ClusteringResult:
        """Louvain community detection"""
        try:
            communities = nx.community.louvain_communities(graph, resolution=config.get("resolution", 1.0))
            clusters = [set(community) for community in communities]
            
            cluster_assignments = {}
            for i, cluster in enumerate(clusters):
                for node in cluster:
                    cluster_assignments[node] = i
            
            modularity = self._calculate_modularity(graph, clusters)
            quality_metrics = self._calculate_quality_metrics(graph, clusters)
            
            return ClusteringResult(
                algorithm="louvain",
                clusters=clusters,
                cluster_assignments=cluster_assignments,
                num_clusters=len(clusters),
                modularity=modularity,
                silhouette_score=quality_metrics.get("silhouette_score"),
                execution_time=0,
                parameters=config,
                quality_metrics=quality_metrics,
                metadata={"resolution": config.get("resolution", 1.0)}
            )
            
        except Exception as e:
            logger.error(f"Louvain clustering failed: {e}")
            return self._create_error_result("louvain", str(e))
    
    def leiden_clustering(self, graph: nx.Graph, config: Dict[str, Any]) -> ClusteringResult:
        """Leiden community detection (fallback to Louvain if not available)"""
        try:
            # Try to use Leiden if available
            try:
                import leidenalg
                import igraph as ig
                
                # Convert to igraph
                edge_list = list(graph.edges())
                ig_graph = ig.Graph(edges=edge_list)
                
                # Run Leiden
                partition = leidenalg.find_partition(ig_graph, leidenalg.ModularityVertexPartition)
                
                # Convert back to NetworkX format
                clusters = []
                for cluster_nodes in partition:
                    cluster = set(graph.nodes()[i] for i in cluster_nodes)
                    clusters.append(cluster)
                
            except ImportError:
                # Fallback to Louvain
                logger.warning("Leiden algorithm not available, falling back to Louvain")
                return self.louvain_clustering(graph, config)
            
            cluster_assignments = {}
            for i, cluster in enumerate(clusters):
                for node in cluster:
                    cluster_assignments[node] = i
            
            modularity = self._calculate_modularity(graph, clusters)
            quality_metrics = self._calculate_quality_metrics(graph, clusters)
            
            return ClusteringResult(
                algorithm="leiden",
                clusters=clusters,
                cluster_assignments=cluster_assignments,
                num_clusters=len(clusters),
                modularity=modularity,
                silhouette_score=quality_metrics.get("silhouette_score"),
                execution_time=0,
                parameters=config,
                quality_metrics=quality_metrics,
                metadata={"resolution": config.get("resolution", 1.0)}
            )
            
        except Exception as e:
            logger.error(f"Leiden clustering failed: {e}")
            return self.louvain_clustering(graph, config)  # Fallback
    
    def label_propagation_clustering(self, graph: nx.Graph, config: Dict[str, Any]) -> ClusteringResult:
        """Label propagation clustering"""
        try:
            communities = nx.community.label_propagation_communities(graph)
            clusters = [set(community) for community in communities]
            
            cluster_assignments = {}
            for i, cluster in enumerate(clusters):
                for node in cluster:
                    cluster_assignments[node] = i
            
            modularity = self._calculate_modularity(graph, clusters)
            quality_metrics = self._calculate_quality_metrics(graph, clusters)
            
            return ClusteringResult(
                algorithm="label_propagation",
                clusters=clusters,
                cluster_assignments=cluster_assignments,
                num_clusters=len(clusters),
                modularity=modularity,
                silhouette_score=quality_metrics.get("silhouette_score"),
                execution_time=0,
                parameters=config,
                quality_metrics=quality_metrics,
                metadata={}
            )
            
        except Exception as e:
            logger.error(f"Label propagation clustering failed: {e}")
            return self._create_error_result("label_propagation", str(e))
    
    def greedy_modularity_clustering(self, graph: nx.Graph, config: Dict[str, Any]) -> ClusteringResult:
        """Greedy modularity optimization"""
        try:
            communities = nx.community.greedy_modularity_communities(graph)
            clusters = [set(community) for community in communities]
            
            cluster_assignments = {}
            for i, cluster in enumerate(clusters):
                for node in cluster:
                    cluster_assignments[node] = i
            
            modularity = self._calculate_modularity(graph, clusters)
            quality_metrics = self._calculate_quality_metrics(graph, clusters)
            
            return ClusteringResult(
                algorithm="greedy_modularity",
                clusters=clusters,
                cluster_assignments=cluster_assignments,
                num_clusters=len(clusters),
                modularity=modularity,
                silhouette_score=quality_metrics.get("silhouette_score"),
                execution_time=0,
                parameters=config,
                quality_metrics=quality_metrics,
                metadata={}
            )
            
        except Exception as e:
            logger.error(f"Greedy modularity clustering failed: {e}")
            return self._create_error_result("greedy_modularity", str(e))
    
    def _calculate_modularity(self, graph: nx.Graph, clusters: List[Set[str]]) -> float:
        """Calculate modularity of clustering"""
        try:
            return nx.community.modularity(graph, clusters)
        except:
            return 0.0
    
    def _calculate_quality_metrics(self, graph: nx.Graph, clusters: List[Set[str]]) -> Dict[str, float]:
        """Calculate clustering quality metrics"""
        metrics = {}
        
        try:
            # Modularity
            metrics["modularity"] = self._calculate_modularity(graph, clusters)
            
            # Conductance (average over all clusters)
            conductances = []
            for cluster in clusters:
                if len(cluster) > 0:
                    conductance = nx.conductance(graph, cluster)
                    conductances.append(conductance)
            metrics["conductance"] = np.mean(conductances) if conductances else 0.0
            
        except Exception as e:
            logger.error(f"Quality metrics calculation failed: {e}")
        
        return metrics
    
    def _create_error_result(self, algorithm: str, error_msg: str) -> ClusteringResult:
        """Create error result"""
        return ClusteringResult(
            algorithm=algorithm,
            clusters=[],
            cluster_assignments={},
            num_clusters=0,
            modularity=0.0,
            silhouette_score=None,
            execution_time=0,
            parameters={},
            quality_metrics={},
            metadata={"error": error_msg}
        )