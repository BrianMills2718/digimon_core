"""
Cluster Optimizer for optimizing cluster assignments and parameters.

This module provides optimization algorithms for improving clustering results
including parameter tuning, cluster refinement, and assignment optimization.
"""

import asyncio
import logging
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from scipy.optimize import minimize
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

logger = logging.getLogger(__name__)


@dataclass
class OptimizationParameters:
    """Parameters for cluster optimization"""
    min_clusters: int = 2
    max_clusters: int = 10
    similarity_threshold: float = 0.5
    balance_weight: float = 0.2
    quality_weight: float = 0.8
    max_iterations: int = 100


@dataclass
class OptimizationResult:
    """Result of cluster optimization"""
    optimized_clusters: List[Dict[str, Any]]
    optimal_parameters: Dict[str, Any]
    quality_improvement: float
    optimization_score: float
    iterations_used: int


class ClusterOptimizer:
    """Optimizes clustering parameters and assignments"""
    
    def __init__(self):
        self.logger = logger
    
    async def optimize_cluster_assignments(self, initial_clusters: List[Dict[str, Any]], 
                                         documents: List[Dict[str, Any]], 
                                         parameters: OptimizationParameters) -> OptimizationResult:
        """Optimize cluster assignments using iterative improvement"""
        self.logger.info(f"Optimizing cluster assignments for {len(initial_clusters)} clusters")
        
        current_clusters = [cluster.copy() for cluster in initial_clusters]
        best_clusters = current_clusters.copy()
        best_score = await self._calculate_clustering_score(current_clusters, documents)
        
        for iteration in range(parameters.max_iterations):
            # Try different optimization strategies
            improved_clusters = await self._try_optimization_strategies(
                current_clusters, documents, parameters
            )
            
            # Evaluate improvement
            new_score = await self._calculate_clustering_score(improved_clusters, documents)
            
            if new_score > best_score:
                best_clusters = improved_clusters.copy()
                best_score = new_score
                current_clusters = improved_clusters
            else:
                # Apply small random perturbation to escape local optima
                current_clusters = await self._apply_perturbation(current_clusters, documents)
            
            # Early stopping if improvement is minimal
            if iteration > 10 and (new_score - best_score) < 0.001:
                break
        
        # Calculate quality improvement
        initial_score = await self._calculate_clustering_score(initial_clusters, documents)
        quality_improvement = best_score - initial_score
        
        # Extract optimal parameters
        optimal_parameters = await self._extract_optimal_parameters(best_clusters, documents)
        
        return OptimizationResult(
            optimized_clusters=best_clusters,
            optimal_parameters=optimal_parameters,
            quality_improvement=quality_improvement,
            optimization_score=best_score,
            iterations_used=iteration + 1
        )
    
    async def _try_optimization_strategies(self, clusters: List[Dict[str, Any]], 
                                         documents: List[Dict[str, Any]], 
                                         parameters: OptimizationParameters) -> List[Dict[str, Any]]:
        """Try different optimization strategies"""
        strategies = [
            self._reassign_outliers,
            self._merge_similar_clusters,
            self._split_large_clusters,
            self._balance_cluster_sizes
        ]
        
        best_clusters = clusters.copy()
        best_score = await self._calculate_clustering_score(clusters, documents)
        
        for strategy in strategies:
            try:
                improved_clusters = await strategy(clusters, documents, parameters)
                score = await self._calculate_clustering_score(improved_clusters, documents)
                
                if score > best_score:
                    best_clusters = improved_clusters
                    best_score = score
            except Exception as e:
                self.logger.warning(f"Strategy failed: {e}")
                continue
        
        return best_clusters
    
    async def _reassign_outliers(self, clusters: List[Dict[str, Any]], 
                               documents: List[Dict[str, Any]], 
                               parameters: OptimizationParameters) -> List[Dict[str, Any]]:
        """Reassign outlier documents to better clusters"""
        optimized_clusters = [cluster.copy() for cluster in clusters]
        
        # Import similarity calculator
        from .similarity_calculator import SimilarityCalculator
        sim_calc = SimilarityCalculator()
        
        # Identify outliers in each cluster
        for cluster_idx, cluster in enumerate(optimized_clusters):
            cluster_docs = cluster["documents"]
            
            if len(cluster_docs) <= 1:
                continue
            
            # Calculate average similarity of each document to others in cluster
            outliers = []
            for i, doc in enumerate(cluster_docs):
                similarities = []
                for j, other_doc in enumerate(cluster_docs):
                    if i != j:
                        sim = await sim_calc.calculate_combined_similarity(doc, other_doc)
                        similarities.append(sim)
                
                avg_similarity = np.mean(similarities) if similarities else 0.0
                
                # If similarity is below threshold, consider as outlier
                if avg_similarity < parameters.similarity_threshold:
                    outliers.append((i, doc, avg_similarity))
            
            # Reassign outliers to better clusters
            for outlier_idx, outlier_doc, _ in outliers:
                best_cluster_idx = cluster_idx
                best_avg_similarity = 0.0
                
                # Find best cluster for this outlier
                for other_cluster_idx, other_cluster in enumerate(optimized_clusters):
                    if other_cluster_idx == cluster_idx:
                        continue
                    
                    other_docs = other_cluster["documents"]
                    if not other_docs:
                        continue
                    
                    # Calculate average similarity to other cluster
                    similarities = []
                    for other_doc in other_docs:
                        sim = await sim_calc.calculate_combined_similarity(outlier_doc, other_doc)
                        similarities.append(sim)
                    
                    avg_sim = np.mean(similarities)
                    if avg_sim > best_avg_similarity:
                        best_avg_similarity = avg_sim
                        best_cluster_idx = other_cluster_idx
                
                # Reassign if better cluster found
                if best_cluster_idx != cluster_idx and best_avg_similarity > parameters.similarity_threshold:
                    optimized_clusters[cluster_idx]["documents"].remove(outlier_doc)
                    optimized_clusters[best_cluster_idx]["documents"].append(outlier_doc)
        
        return optimized_clusters
    
    async def _merge_similar_clusters(self, clusters: List[Dict[str, Any]], 
                                    documents: List[Dict[str, Any]], 
                                    parameters: OptimizationParameters) -> List[Dict[str, Any]]:
        """Merge clusters that are too similar"""
        from .similarity_calculator import SimilarityCalculator
        sim_calc = SimilarityCalculator()
        
        optimized_clusters = clusters.copy()
        merge_threshold = 0.8  # High similarity threshold for merging
        
        merged = True
        while merged and len(optimized_clusters) > parameters.min_clusters:
            merged = False
            
            for i in range(len(optimized_clusters)):
                for j in range(i + 1, len(optimized_clusters)):
                    cluster1 = optimized_clusters[i]
                    cluster2 = optimized_clusters[j]
                    
                    # Calculate inter-cluster similarity
                    inter_similarity = await self._calculate_inter_cluster_similarity(
                        cluster1, cluster2, sim_calc
                    )
                    
                    if inter_similarity > merge_threshold:
                        # Merge clusters
                        merged_cluster = {
                            "cluster_id": f"merged_{cluster1.get('cluster_id', i)}_{cluster2.get('cluster_id', j)}",
                            "documents": cluster1["documents"] + cluster2["documents"],
                            "centroid": self._calculate_merged_centroid(cluster1, cluster2)
                        }
                        
                        # Remove original clusters and add merged cluster
                        optimized_clusters = [
                            cluster for k, cluster in enumerate(optimized_clusters) 
                            if k != i and k != j
                        ] + [merged_cluster]
                        
                        merged = True
                        break
                
                if merged:
                    break
        
        return optimized_clusters
    
    async def _split_large_clusters(self, clusters: List[Dict[str, Any]], 
                                  documents: List[Dict[str, Any]], 
                                  parameters: OptimizationParameters) -> List[Dict[str, Any]]:
        """Split clusters that are too large or diverse"""
        optimized_clusters = clusters.copy()
        max_cluster_size = max(10, len(documents) // parameters.max_clusters)
        
        clusters_to_split = []
        for i, cluster in enumerate(optimized_clusters):
            if len(cluster["documents"]) > max_cluster_size:
                clusters_to_split.append(i)
        
        # Split large clusters
        for cluster_idx in reversed(clusters_to_split):  # Reverse to maintain indices
            cluster = optimized_clusters[cluster_idx]
            split_clusters = await self._split_cluster(cluster, parameters)
            
            if len(split_clusters) > 1:
                # Remove original cluster and add split clusters
                optimized_clusters.pop(cluster_idx)
                optimized_clusters.extend(split_clusters)
        
        return optimized_clusters
    
    async def _split_cluster(self, cluster: Dict[str, Any], 
                           parameters: OptimizationParameters) -> List[Dict[str, Any]]:
        """Split a single cluster into multiple clusters"""
        cluster_docs = cluster["documents"]
        
        if len(cluster_docs) < 4:  # Don't split small clusters
            return [cluster]
        
        # Use K-means to split cluster
        try:
            # Prepare feature vectors
            feature_vectors = []
            for doc in cluster_docs:
                content_length = len(doc.get("content", ""))
                metadata = doc.get("metadata", {})
                features = [
                    content_length / 1000,
                    len(metadata.get("authors", [])),
                    len(metadata.get("keywords", [])),
                    len(metadata.get("references", []))
                ]
                feature_vectors.append(features)
            
            feature_matrix = np.array(feature_vectors)
            
            # Determine optimal number of subclusters (2-3)
            n_subclusters = min(3, max(2, len(cluster_docs) // 5))
            
            kmeans = KMeans(n_clusters=n_subclusters, random_state=42, n_init=10)
            subcluster_labels = kmeans.fit_predict(feature_matrix)
            
            # Create new clusters
            split_clusters = []
            for subcluster_id in range(n_subclusters):
                subcluster_docs = [
                    doc for i, doc in enumerate(cluster_docs) 
                    if subcluster_labels[i] == subcluster_id
                ]
                
                if subcluster_docs:  # Only create non-empty clusters
                    split_cluster = {
                        "cluster_id": f"{cluster.get('cluster_id', 'cluster')}_split_{subcluster_id}",
                        "documents": subcluster_docs,
                        "centroid": kmeans.cluster_centers_[subcluster_id].tolist()
                    }
                    split_clusters.append(split_cluster)
            
            return split_clusters if len(split_clusters) > 1 else [cluster]
            
        except Exception as e:
            self.logger.warning(f"Failed to split cluster: {e}")
            return [cluster]
    
    async def _balance_cluster_sizes(self, clusters: List[Dict[str, Any]], 
                                   documents: List[Dict[str, Any]], 
                                   parameters: OptimizationParameters) -> List[Dict[str, Any]]:
        """Balance cluster sizes by redistributing documents"""
        optimized_clusters = [cluster.copy() for cluster in clusters]
        
        total_docs = len(documents)
        ideal_size = total_docs / len(clusters)
        
        # Identify oversized and undersized clusters
        oversized = []
        undersized = []
        
        for i, cluster in enumerate(optimized_clusters):
            size = len(cluster["documents"])
            if size > ideal_size * 1.5:
                oversized.append(i)
            elif size < ideal_size * 0.5:
                undersized.append(i)
        
        # Move documents from oversized to undersized clusters
        from .similarity_calculator import SimilarityCalculator
        sim_calc = SimilarityCalculator()
        
        for oversized_idx in oversized:
            for undersized_idx in undersized:
                oversized_cluster = optimized_clusters[oversized_idx]
                undersized_cluster = optimized_clusters[undersized_idx]
                
                if len(oversized_cluster["documents"]) <= ideal_size:
                    break
                
                # Find best document to move
                best_doc = None
                best_similarity = 0.0
                
                for doc in oversized_cluster["documents"]:
                    # Calculate similarity to undersized cluster
                    if undersized_cluster["documents"]:
                        similarities = []
                        for target_doc in undersized_cluster["documents"]:
                            sim = await sim_calc.calculate_combined_similarity(doc, target_doc)
                            similarities.append(sim)
                        avg_similarity = np.mean(similarities)
                        
                        if avg_similarity > best_similarity:
                            best_similarity = avg_similarity
                            best_doc = doc
                
                # Move document if similarity is reasonable
                if best_doc and best_similarity > 0.3:
                    oversized_cluster["documents"].remove(best_doc)
                    undersized_cluster["documents"].append(best_doc)
        
        return optimized_clusters
    
    async def _apply_perturbation(self, clusters: List[Dict[str, Any]], 
                                documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply small random perturbation to escape local optima"""
        perturbed_clusters = [cluster.copy() for cluster in clusters]
        
        # Randomly move 1-2 documents between clusters
        num_moves = min(2, len(documents) // 10)
        
        for _ in range(num_moves):
            if len(perturbed_clusters) < 2:
                break
            
            # Select random source and target clusters
            source_idx = np.random.randint(0, len(perturbed_clusters))
            target_idx = np.random.randint(0, len(perturbed_clusters))
            
            if source_idx == target_idx or len(perturbed_clusters[source_idx]["documents"]) <= 1:
                continue
            
            # Move random document
            source_cluster = perturbed_clusters[source_idx]
            target_cluster = perturbed_clusters[target_idx]
            
            if source_cluster["documents"]:
                doc_idx = np.random.randint(0, len(source_cluster["documents"]))
                doc_to_move = source_cluster["documents"].pop(doc_idx)
                target_cluster["documents"].append(doc_to_move)
        
        return perturbed_clusters
    
    async def _calculate_clustering_score(self, clusters: List[Dict[str, Any]], 
                                        documents: List[Dict[str, Any]]) -> float:
        """Calculate overall clustering quality score"""
        try:
            from .cluster_evaluator import ClusterEvaluator
            evaluator = ClusterEvaluator()
            metrics = await evaluator.evaluate_clustering_quality(clusters, documents)
            return metrics.overall_quality
        except Exception as e:
            self.logger.warning(f"Error calculating clustering score: {e}")
            return 0.0
    
    async def _calculate_inter_cluster_similarity(self, cluster1: Dict[str, Any], 
                                                cluster2: Dict[str, Any], 
                                                sim_calc) -> float:
        """Calculate similarity between two clusters"""
        docs1 = cluster1["documents"]
        docs2 = cluster2["documents"]
        
        if not docs1 or not docs2:
            return 0.0
        
        similarities = []
        for doc1 in docs1:
            for doc2 in docs2:
                sim = await sim_calc.calculate_combined_similarity(doc1, doc2)
                similarities.append(sim)
        
        return np.mean(similarities) if similarities else 0.0
    
    def _calculate_merged_centroid(self, cluster1: Dict[str, Any], 
                                 cluster2: Dict[str, Any]) -> List[float]:
        """Calculate centroid for merged cluster"""
        centroid1 = cluster1.get("centroid", [0.0, 0.0, 0.0])
        centroid2 = cluster2.get("centroid", [0.0, 0.0, 0.0])
        
        size1 = len(cluster1["documents"])
        size2 = len(cluster2["documents"])
        total_size = size1 + size2
        
        if total_size == 0:
            return [0.0, 0.0, 0.0]
        
        # Weighted average of centroids
        merged_centroid = []
        for i in range(max(len(centroid1), len(centroid2))):
            val1 = centroid1[i] if i < len(centroid1) else 0.0
            val2 = centroid2[i] if i < len(centroid2) else 0.0
            merged_val = (val1 * size1 + val2 * size2) / total_size
            merged_centroid.append(merged_val)
        
        return merged_centroid
    
    async def _extract_optimal_parameters(self, clusters: List[Dict[str, Any]], 
                                        documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract optimal parameters from final clustering"""
        cluster_sizes = [len(cluster["documents"]) for cluster in clusters]
        
        optimal_params = {
            "num_clusters": len(clusters),
            "average_cluster_size": np.mean(cluster_sizes),
            "cluster_size_variance": np.var(cluster_sizes),
            "total_documents": len(documents),
            "clustering_density": len(clusters) / len(documents) if documents else 0.0
        }
        
        return optimal_params
    
    async def find_optimal_cluster_count(self, documents: List[Dict[str, Any]], 
                                       min_clusters: int = 2, 
                                       max_clusters: int = 10) -> int:
        """Find optimal number of clusters using elbow method and silhouette analysis"""
        if len(documents) < min_clusters:
            return min(len(documents), max_clusters)
        
        # Prepare feature vectors
        feature_vectors = []
        for doc in documents:
            content_length = len(doc.get("content", ""))
            metadata = doc.get("metadata", {})
            features = [
                content_length / 1000,
                len(metadata.get("authors", [])),
                len(metadata.get("keywords", [])),
                len(metadata.get("references", []))
            ]
            feature_vectors.append(features)
        
        feature_matrix = np.array(feature_vectors)
        
        # Calculate scores for different cluster counts
        cluster_scores = {}
        
        for k in range(min_clusters, min(max_clusters + 1, len(documents))):
            try:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(feature_matrix)
                
                # Calculate silhouette score
                sil_score = silhouette_score(feature_matrix, cluster_labels)
                
                # Calculate inertia (within-cluster sum of squares)
                inertia = kmeans.inertia_
                
                # Combined score (higher silhouette, lower inertia)
                combined_score = sil_score - (inertia / 10000)  # Normalize inertia
                
                cluster_scores[k] = {
                    "silhouette": sil_score,
                    "inertia": inertia,
                    "combined": combined_score
                }
                
            except Exception as e:
                self.logger.warning(f"Error evaluating {k} clusters: {e}")
                cluster_scores[k] = {"silhouette": 0.0, "inertia": float('inf'), "combined": 0.0}
        
        # Find optimal k based on combined score
        if cluster_scores:
            optimal_k = max(cluster_scores.keys(), key=lambda k: cluster_scores[k]["combined"])
            self.logger.info(f"Optimal cluster count: {optimal_k} (score: {cluster_scores[optimal_k]['combined']:.3f})")
            return optimal_k
        
        return min_clusters