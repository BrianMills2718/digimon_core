"""Spectral Clustering Implementation

Spectral clustering algorithm with Laplacian computation.
"""

from typing import Dict, List, Any, Set
import networkx as nx
import numpy as np
from collections import defaultdict

from .clustering_data_models import ClusteringResult
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class SpectralClustering:
    """Spectral clustering implementation"""
    
    def run(self, graph: nx.Graph, config: Dict[str, Any]) -> ClusteringResult:
        """Perform spectral clustering"""
        try:
            num_clusters = config.get("num_clusters")
            laplacian_type = config.get("laplacian_type", "normalized")
            
            # Get adjacency matrix
            adj_matrix = nx.adjacency_matrix(graph).toarray().astype(float)
            
            # Compute Laplacian
            laplacian = self._compute_graph_laplacian(adj_matrix, laplacian_type)
            
            # Estimate number of clusters if not provided
            if num_clusters is None:
                num_clusters = self._estimate_num_clusters(laplacian, config)
            
            # Compute eigenvalues and eigenvectors
            try:
                eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
            except np.linalg.LinAlgError:
                return self._fallback_clustering(graph, config)
            
            # Select k smallest eigenvectors
            k_eigenvectors = eigenvectors[:, :num_clusters]
            
            # Normalize rows
            row_norms = np.linalg.norm(k_eigenvectors, axis=1)
            row_norms[row_norms == 0] = 1  # Avoid division by zero
            k_eigenvectors = k_eigenvectors / row_norms[:, np.newaxis]
            
            # Apply k-means to eigenvectors
            try:
                from sklearn.cluster import KMeans
                kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
                labels = kmeans.fit_predict(k_eigenvectors)
            except ImportError:
                # Fallback clustering without sklearn
                labels = self._simple_kmeans(k_eigenvectors, num_clusters)
            
            # Convert labels to clusters
            clusters = self._labels_to_clusters(graph.nodes(), labels)
            cluster_assignments = dict(zip(graph.nodes(), labels))
            
            # Calculate quality metrics
            modularity = self._calculate_modularity(graph, clusters)
            quality_metrics = self._calculate_quality_metrics(graph, clusters)
            
            return ClusteringResult(
                algorithm="spectral",
                clusters=clusters,
                cluster_assignments=cluster_assignments,
                num_clusters=len(clusters),
                modularity=modularity,
                silhouette_score=quality_metrics.get("silhouette_score"),
                execution_time=0,  # Will be set by caller
                parameters=config,
                quality_metrics=quality_metrics,
                metadata={
                    "laplacian_type": laplacian_type,
                    "eigenvalues": eigenvalues[:num_clusters].tolist()
                }
            )
            
        except Exception as e:
            logger.error(f"Spectral clustering failed: {e}")
            return self._fallback_clustering(graph, config)
    
    def _compute_graph_laplacian(self, adj_matrix: np.ndarray, laplacian_type: str) -> np.ndarray:
        """Compute graph Laplacian matrix"""
        try:
            # Degree matrix
            degrees = np.sum(adj_matrix, axis=1)
            
            if laplacian_type == "combinatorial":
                # L = D - A
                degree_matrix = np.diag(degrees)
                return degree_matrix - adj_matrix
            
            elif laplacian_type == "normalized":
                # L = D^(-1/2) * (D - A) * D^(-1/2)
                degrees_inv_sqrt = np.zeros_like(degrees)
                nonzero_mask = degrees > 0
                degrees_inv_sqrt[nonzero_mask] = 1.0 / np.sqrt(degrees[nonzero_mask])
                
                degree_inv_sqrt_matrix = np.diag(degrees_inv_sqrt)
                degree_matrix = np.diag(degrees)
                
                return degree_inv_sqrt_matrix @ (degree_matrix - adj_matrix) @ degree_inv_sqrt_matrix
            
            elif laplacian_type == "random_walk":
                # L = D^(-1) * (D - A)
                degrees_inv = np.zeros_like(degrees)
                nonzero_mask = degrees > 0
                degrees_inv[nonzero_mask] = 1.0 / degrees[nonzero_mask]
                
                degree_inv_matrix = np.diag(degrees_inv)
                degree_matrix = np.diag(degrees)
                
                return degree_inv_matrix @ (degree_matrix - adj_matrix)
            
            else:
                raise ValueError(f"Unknown laplacian type: {laplacian_type}")
                
        except Exception as e:
            logger.error(f"Laplacian computation failed: {e}")
            # Fallback to combinatorial Laplacian
            degree_matrix = np.diag(np.sum(adj_matrix, axis=1))
            return degree_matrix - adj_matrix
    
    def _estimate_num_clusters(self, laplacian: np.ndarray, config: Dict[str, Any]) -> int:
        """Estimate optimal number of clusters using eigengap heuristic"""
        try:
            max_clusters = config.get("max_clusters", min(10, laplacian.shape[0] // 2))
            
            # Compute eigenvalues
            eigenvalues = np.linalg.eigvals(laplacian)
            eigenvalues = np.sort(eigenvalues)
            
            # Find largest eigengap in first max_clusters eigenvalues
            if len(eigenvalues) < 2:
                return 1
            
            gaps = []
            for i in range(1, min(max_clusters, len(eigenvalues))):
                gap = eigenvalues[i] - eigenvalues[i-1]
                gaps.append(gap)
            
            if gaps:
                optimal_k = np.argmax(gaps) + 2  # +2 because we start from index 1 and want cluster count
                return min(optimal_k, max_clusters)
            else:
                return 2
                
        except Exception as e:
            logger.error(f"Cluster estimation failed: {e}")
            return 2  # Default fallback
    
    def _fallback_clustering(self, graph: nx.Graph, config: Dict[str, Any]) -> ClusteringResult:
        """Fallback clustering using connected components"""
        try:
            # Use connected components as fallback
            clusters = [set(component) for component in nx.connected_components(graph)]
            
            if len(clusters) == 1 and len(graph.nodes) > 10:
                # If graph is connected, use simple degree-based clustering
                num_clusters = config.get("num_clusters", 3)
                clusters = self._degree_based_clustering(graph, num_clusters)
            
            cluster_assignments = {}
            for i, cluster in enumerate(clusters):
                for node in cluster:
                    cluster_assignments[node] = i
            
            modularity = self._calculate_modularity(graph, clusters)
            quality_metrics = self._calculate_quality_metrics(graph, clusters)
            
            return ClusteringResult(
                algorithm="spectral_fallback",
                clusters=clusters,
                cluster_assignments=cluster_assignments,
                num_clusters=len(clusters),
                modularity=modularity,
                silhouette_score=quality_metrics.get("silhouette_score"),
                execution_time=0,
                parameters=config,
                quality_metrics=quality_metrics,
                metadata={"fallback_method": "degree_based"}
            )
            
        except Exception as e:
            logger.error(f"Fallback clustering failed: {e}")
            return self._create_error_result(str(e))
    
    def _degree_based_clustering(self, graph: nx.Graph, num_clusters: int) -> List[Set[str]]:
        """Simple degree-based clustering"""
        nodes_by_degree = sorted(graph.nodes(), key=lambda x: graph.degree(x), reverse=True)
        
        clusters = [set() for _ in range(num_clusters)]
        
        for i, node in enumerate(nodes_by_degree):
            clusters[i % num_clusters].add(node)
        
        return clusters
    
    def _labels_to_clusters(self, nodes: List[str], labels: np.ndarray) -> List[Set[str]]:
        """Convert cluster labels to cluster sets"""
        cluster_dict = defaultdict(set)
        
        for node, label in zip(nodes, labels):
            if label >= 0:  # Ignore noise points (label -1)
                cluster_dict[label].add(node)
        
        return [cluster for cluster in cluster_dict.values() if cluster]
    
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
    
    def _simple_kmeans(self, features: np.ndarray, k: int) -> np.ndarray:
        """Simple k-means implementation"""
        n_samples, n_features = features.shape
        
        # Initialize centroids randomly
        centroids = features[np.random.choice(n_samples, k, replace=False)]
        labels = np.zeros(n_samples, dtype=int)
        
        for _ in range(100):  # Max iterations
            # Assign points to nearest centroid
            distances = np.sqrt(((features - centroids[:, np.newaxis])**2).sum(axis=2))
            new_labels = np.argmin(distances, axis=0)
            
            # Update centroids
            for i in range(k):
                if np.sum(new_labels == i) > 0:
                    centroids[i] = features[new_labels == i].mean(axis=0)
            
            # Check for convergence
            if np.array_equal(labels, new_labels):
                break
            
            labels = new_labels
        
        return labels
    
    def _create_error_result(self, error_msg: str) -> ClusteringResult:
        """Create error result"""
        return ClusteringResult(
            algorithm="spectral_error",
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