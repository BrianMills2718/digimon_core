"""Graph Clustering Algorithms Coordinator

Streamlined coordinator that delegates to specialized algorithm implementations.
"""

from typing import Dict, List, Any, Optional, Set
import networkx as nx
import time

from .clustering_data_models import ClusteringResult, ClusteringAlgorithm
from .spectral_clustering import SpectralClustering
from .community_clustering import CommunityDetection
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class ClusteringAlgorithms:
    """Coordinator for graph clustering algorithms"""
    
    def __init__(self):
        # Initialize specialized algorithm implementations
        self.spectral = SpectralClustering()
        self.community_detection = CommunityDetection()
        
        # Algorithm routing
        self.algorithm_registry = {
            ClusteringAlgorithm.SPECTRAL: self.spectral.run,
            ClusteringAlgorithm.LOUVAIN: self.community_detection.louvain_clustering,
            ClusteringAlgorithm.LEIDEN: self.community_detection.leiden_clustering,
            ClusteringAlgorithm.LABEL_PROPAGATION: self.community_detection.label_propagation_clustering,
            ClusteringAlgorithm.GREEDY_MODULARITY: self.community_detection.greedy_modularity_clustering,
            ClusteringAlgorithm.KMEANS: self._kmeans_clustering,
            ClusteringAlgorithm.HIERARCHICAL: self._hierarchical_clustering,
            ClusteringAlgorithm.DBSCAN: self._dbscan_clustering
        }
    
    def run_clustering(self, graph: nx.Graph, algorithm: ClusteringAlgorithm, 
                      config: Dict[str, Any]) -> ClusteringResult:
        """Run specified clustering algorithm"""
        try:
            start_time = time.time()
            
            if algorithm in self.algorithm_registry:
                result = self.algorithm_registry[algorithm](graph, config)
                result.execution_time = time.time() - start_time
                return result
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
                
        except Exception as e:
            logger.error(f"Clustering failed with {algorithm}: {e}")
            return self._create_error_result(algorithm.value, str(e), time.time() - start_time)
    
    def _kmeans_clustering(self, graph: nx.Graph, config: Dict[str, Any]) -> ClusteringResult:
        """K-means clustering fallback"""
        try:
            from sklearn.cluster import KMeans
            import numpy as np
            
            # Extract simple node features
            nodes = list(graph.nodes())
            features = [[graph.degree(node)] for node in nodes]
            features = np.array(features)
            
            num_clusters = config.get("num_clusters", 3)
            kmeans = KMeans(n_clusters=num_clusters, random_state=42)
            labels = kmeans.fit_predict(features)
            
            # Convert to clusters
            clusters = []
            for i in range(num_clusters):
                cluster = set(node for node, label in zip(nodes, labels) if label == i)
                if cluster:
                    clusters.append(cluster)
            
            cluster_assignments = dict(zip(nodes, labels))
            
            return ClusteringResult(
                algorithm="kmeans",
                clusters=clusters,
                cluster_assignments=cluster_assignments,
                num_clusters=len(clusters),
                modularity=0.0,
                silhouette_score=None,
                execution_time=0,
                parameters=config,
                quality_metrics={},
                metadata={}
            )
        except Exception as e:
            return self._create_error_result("kmeans", str(e), 0)
    
    def _hierarchical_clustering(self, graph: nx.Graph, config: Dict[str, Any]) -> ClusteringResult:
        """Hierarchical clustering fallback"""
        try:
            # Simple fallback: connected components
            clusters = [set(component) for component in nx.connected_components(graph)]
            
            cluster_assignments = {}
            for i, cluster in enumerate(clusters):
                for node in cluster:
                    cluster_assignments[node] = i
            
            return ClusteringResult(
                algorithm="hierarchical",
                clusters=clusters,
                cluster_assignments=cluster_assignments,
                num_clusters=len(clusters),
                modularity=0.0,
                silhouette_score=None,
                execution_time=0,
                parameters=config,
                quality_metrics={},
                metadata={}
            )
        except Exception as e:
            return self._create_error_result("hierarchical", str(e), 0)
    
    def _dbscan_clustering(self, graph: nx.Graph, config: Dict[str, Any]) -> ClusteringResult:
        """DBSCAN clustering fallback"""
        try:
            # Simple fallback: connected components
            clusters = [set(component) for component in nx.connected_components(graph)]
            
            cluster_assignments = {}
            for i, cluster in enumerate(clusters):
                for node in cluster:
                    cluster_assignments[node] = i
            
            return ClusteringResult(
                algorithm="dbscan",
                clusters=clusters,
                cluster_assignments=cluster_assignments,
                num_clusters=len(clusters),
                modularity=0.0,
                silhouette_score=None,
                execution_time=0,
                parameters=config,
                quality_metrics={},
                metadata={}
            )
        except Exception as e:
            return self._create_error_result("dbscan", str(e), 0)
    
    def _create_error_result(self, algorithm: str, error_msg: str, execution_time: float) -> ClusteringResult:
        """Create error result"""
        return ClusteringResult(
            algorithm=algorithm,
            clusters=[],
            cluster_assignments={},
            num_clusters=0,
            modularity=0.0,
            silhouette_score=None,
            execution_time=execution_time,
            parameters={},
            quality_metrics={},
            metadata={"error": error_msg}
        )