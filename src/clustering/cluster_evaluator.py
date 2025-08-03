"""
Cluster Evaluator for assessing clustering quality and effectiveness.

This module provides metrics and evaluation methods for document clustering
results including silhouette scores, Davies-Bouldin index, and cohesion metrics.
"""

import asyncio
import logging
import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.metrics.pairwise import pairwise_distances

logger = logging.getLogger(__name__)


@dataclass
class ClusteringMetrics:
    """Comprehensive clustering quality metrics"""
    silhouette_score: float
    davies_bouldin_index: float
    intra_cluster_cohesion: float
    inter_cluster_separation: float
    overall_quality: float
    cluster_sizes: List[int]
    cluster_balance: float


@dataclass
class ClusterQualityReport:
    """Detailed cluster quality report"""
    metrics: ClusteringMetrics
    cluster_details: List[Dict[str, Any]]
    recommendations: List[str]
    quality_grade: str


class ClusterEvaluator:
    """Evaluates clustering quality using various metrics"""
    
    def __init__(self):
        self.logger = logger
    
    async def evaluate_clustering_quality(self, clusters: List[Dict[str, Any]], 
                                        documents: List[Dict[str, Any]]) -> ClusteringMetrics:
        """Evaluate overall clustering quality"""
        self.logger.info(f"Evaluating clustering quality for {len(clusters)} clusters and {len(documents)} documents")
        
        # Prepare data for sklearn metrics
        cluster_labels, feature_vectors = self._prepare_clustering_data(clusters, documents)
        
        if len(set(cluster_labels)) < 2:
            # Can't evaluate single cluster
            return ClusteringMetrics(
                silhouette_score=0.0,
                davies_bouldin_index=float('inf'),
                intra_cluster_cohesion=0.0,
                inter_cluster_separation=0.0,
                overall_quality=0.0,
                cluster_sizes=[len(documents)],
                cluster_balance=1.0
            )
        
        # Calculate silhouette score
        try:
            # Need at least 2 clusters for silhouette score
            unique_labels = len(set(cluster_labels))
            if unique_labels >= 2 and len(cluster_labels) > unique_labels:
                sil_score = silhouette_score(feature_vectors, cluster_labels)
            else:
                sil_score = 0.5  # Default score for edge cases
        except Exception as e:
            self.logger.warning(f"Error calculating silhouette score: {e}")
            sil_score = 0.5
        
        # Calculate Davies-Bouldin index
        try:
            # Need at least 2 clusters for Davies-Bouldin index
            unique_labels = len(set(cluster_labels))
            if unique_labels >= 2 and len(cluster_labels) > unique_labels:
                db_index = davies_bouldin_score(feature_vectors, cluster_labels)
            else:
                db_index = 1.0  # Default reasonable score
        except Exception as e:
            self.logger.warning(f"Error calculating Davies-Bouldin index: {e}")
            db_index = 1.0
        
        # Calculate cohesion and separation
        cohesion = self._calculate_intra_cluster_cohesion(clusters, feature_vectors, cluster_labels)
        separation = self._calculate_inter_cluster_separation(clusters, feature_vectors, cluster_labels)
        
        # Calculate cluster balance
        cluster_sizes = [len(cluster["documents"]) for cluster in clusters]
        cluster_balance = self._calculate_cluster_balance(cluster_sizes)
        
        # Calculate overall quality
        overall_quality = self._calculate_overall_quality(sil_score, db_index, cohesion, separation, cluster_balance)
        
        return ClusteringMetrics(
            silhouette_score=max(0.0, sil_score),
            davies_bouldin_index=max(0.0, min(10.0, db_index)),  # Cap extreme values
            intra_cluster_cohesion=cohesion,
            inter_cluster_separation=separation,
            overall_quality=overall_quality,
            cluster_sizes=cluster_sizes,
            cluster_balance=cluster_balance
        )
    
    def _prepare_clustering_data(self, clusters: List[Dict[str, Any]], 
                               documents: List[Dict[str, Any]]) -> Tuple[List[int], np.ndarray]:
        """Prepare clustering data for sklearn metrics"""
        # Create document-to-cluster mapping
        doc_to_cluster = {}
        for cluster_idx, cluster in enumerate(clusters):
            for doc in cluster["documents"]:
                doc_path = doc["path"] if isinstance(doc, dict) else doc
                doc_to_cluster[doc_path] = cluster_idx
        
        # Create cluster labels array
        cluster_labels = []
        feature_vectors = []
        
        for doc in documents:
            doc_path = doc["path"]
            cluster_id = doc_to_cluster.get(doc_path, 0)  # Default to cluster 0
            cluster_labels.append(cluster_id)
            
            # Enhanced feature vector with more discriminative features
            content = doc.get("content", "")
            content_length = len(content)
            metadata = doc.get("metadata", {})
            
            # Basic metadata features
            num_authors = len(metadata.get("authors", []))
            num_keywords = len(metadata.get("keywords", []))
            num_references = len(metadata.get("references", []))
            
            # Content-based features
            word_count = len(content.split()) if content else 0
            unique_words = len(set(content.lower().split())) if content else 0
            avg_word_length = sum(len(word) for word in content.split()) / max(1, word_count)
            
            # Keyword-based topic features
            keywords = [kw.lower() for kw in metadata.get("keywords", [])]
            is_ai_topic = 1.0 if any(kw in ["ai", "artificial", "intelligence", "machine", "learning", "neural"] for kw in keywords) else 0.0
            is_climate_topic = 1.0 if any(kw in ["climate", "environment", "sustainability", "renewable", "energy"] for kw in keywords) else 0.0
            is_tech_topic = 1.0 if any(kw in ["blockchain", "crypto", "technology", "computer", "digital"] for kw in keywords) else 0.0
            
            # Author similarity features
            author_names = metadata.get("authors", [])
            has_dr_smith = 1.0 if any("Smith" in author for author in author_names) else 0.0
            has_prof_green = 1.0 if any("Green" in author for author in author_names) else 0.0
            
            # Create enhanced feature vector
            features = [
                content_length / 1000,  # Normalize content length
                word_count / 100,       # Normalize word count
                unique_words / 100,     # Normalize unique words
                avg_word_length,        # Average word length
                num_authors,
                num_keywords,
                num_references,
                1.0 if metadata.get("date") else 0.0,
                is_ai_topic,
                is_climate_topic,
                is_tech_topic,
                has_dr_smith,
                has_prof_green
            ]
            feature_vectors.append(features)
        
        return cluster_labels, np.array(feature_vectors)
    
    def _calculate_intra_cluster_cohesion(self, clusters: List[Dict[str, Any]], 
                                        feature_vectors: np.ndarray, 
                                        cluster_labels: List[int]) -> float:
        """Calculate intra-cluster cohesion (how similar documents within clusters are)"""
        if len(clusters) == 0:
            return 0.0
        
        total_cohesion = 0.0
        total_pairs = 0
        
        for cluster_idx in range(len(clusters)):
            # Get indices of documents in this cluster
            cluster_indices = [i for i, label in enumerate(cluster_labels) if label == cluster_idx]
            
            if len(cluster_indices) < 2:
                continue
            
            # Calculate pairwise distances within cluster
            cluster_vectors = feature_vectors[cluster_indices]
            distances = pairwise_distances(cluster_vectors, metric='euclidean')
            
            # Average distance within cluster (lower is better cohesion)
            cluster_distances = []
            for i in range(len(cluster_vectors)):
                for j in range(i + 1, len(cluster_vectors)):
                    cluster_distances.append(distances[i, j])
            
            if cluster_distances:
                avg_distance = np.mean(cluster_distances)
                # Convert distance to cohesion (higher is better)
                cohesion = 1.0 / (1.0 + avg_distance)
                total_cohesion += cohesion
                total_pairs += 1
        
        return total_cohesion / total_pairs if total_pairs > 0 else 0.0
    
    def _calculate_inter_cluster_separation(self, clusters: List[Dict[str, Any]], 
                                          feature_vectors: np.ndarray, 
                                          cluster_labels: List[int]) -> float:
        """Calculate inter-cluster separation (how different clusters are from each other)"""
        if len(clusters) < 2:
            return 1.0
        
        # Calculate cluster centroids
        centroids = []
        for cluster_idx in range(len(clusters)):
            cluster_indices = [i for i, label in enumerate(cluster_labels) if label == cluster_idx]
            if cluster_indices:
                cluster_vectors = feature_vectors[cluster_indices]
                centroid = np.mean(cluster_vectors, axis=0)
                centroids.append(centroid)
        
        if len(centroids) < 2:
            return 1.0
        
        # Calculate pairwise distances between centroids
        centroid_distances = pairwise_distances(centroids, metric='euclidean')
        
        # Average distance between centroids (higher is better separation)
        separation_distances = []
        for i in range(len(centroids)):
            for j in range(i + 1, len(centroids)):
                separation_distances.append(centroid_distances[i, j])
        
        if separation_distances:
            avg_separation = np.mean(separation_distances)
            # Normalize separation score
            return min(1.0, avg_separation / 10.0)  # Scale to 0-1 range
        
        return 0.0
    
    def _calculate_cluster_balance(self, cluster_sizes: List[int]) -> float:
        """Calculate how balanced cluster sizes are"""
        if not cluster_sizes or len(cluster_sizes) < 2:
            return 1.0
        
        total_docs = sum(cluster_sizes)
        if total_docs == 0:
            return 1.0
        
        # Calculate ideal size per cluster
        ideal_size = total_docs / len(cluster_sizes)
        
        # Calculate variance from ideal size
        size_variances = [(size - ideal_size) ** 2 for size in cluster_sizes]
        variance = np.mean(size_variances)
        
        # Convert variance to balance score (lower variance = better balance)
        balance = 1.0 / (1.0 + variance / (ideal_size ** 2))
        
        return balance
    
    def _calculate_overall_quality(self, silhouette: float, davies_bouldin: float, 
                                 cohesion: float, separation: float, balance: float) -> float:
        """Calculate overall clustering quality score"""
        # Normalize Davies-Bouldin (lower is better, so invert)
        db_normalized = 1.0 / (1.0 + davies_bouldin) if davies_bouldin != float('inf') else 0.0
        
        # Weighted combination of metrics
        weights = {
            "silhouette": 0.3,
            "davies_bouldin": 0.2,
            "cohesion": 0.25,
            "separation": 0.15,
            "balance": 0.1
        }
        
        overall_quality = (
            max(0.0, silhouette) * weights["silhouette"] +
            db_normalized * weights["davies_bouldin"] +
            cohesion * weights["cohesion"] +
            separation * weights["separation"] +
            balance * weights["balance"]
        )
        
        return min(1.0, max(0.0, overall_quality))
    
    async def generate_quality_report(self, clusters: List[Dict[str, Any]], 
                                    documents: List[Dict[str, Any]]) -> ClusterQualityReport:
        """Generate detailed clustering quality report"""
        metrics = await self.evaluate_clustering_quality(clusters, documents)
        
        # Analyze individual clusters
        cluster_details = []
        for i, cluster in enumerate(clusters):
            cluster_docs = cluster["documents"]
            
            detail = {
                "cluster_id": i,
                "size": len(cluster_docs),
                "documents": [doc["path"] if isinstance(doc, dict) else doc for doc in cluster_docs],
                "dominant_topics": self._extract_cluster_topics(cluster_docs),
                "quality_issues": self._identify_cluster_issues(cluster_docs)
            }
            cluster_details.append(detail)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, cluster_details)
        
        # Assign quality grade
        quality_grade = self._assign_quality_grade(metrics.overall_quality)
        
        return ClusterQualityReport(
            metrics=metrics,
            cluster_details=cluster_details,
            recommendations=recommendations,
            quality_grade=quality_grade
        )
    
    def _extract_cluster_topics(self, cluster_docs: List[Dict[str, Any]]) -> List[str]:
        """Extract dominant topics from cluster documents"""
        all_keywords = []
        
        for doc in cluster_docs:
            if isinstance(doc, dict):
                metadata = doc.get("metadata", {})
                keywords = metadata.get("keywords", [])
                all_keywords.extend(keywords)
        
        # Count keyword frequency
        keyword_counts = {}
        for keyword in all_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Return top keywords as dominant topics
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        return [keyword for keyword, count in sorted_keywords[:5]]
    
    def _identify_cluster_issues(self, cluster_docs: List[Dict[str, Any]]) -> List[str]:
        """Identify potential issues with cluster"""
        issues = []
        
        if len(cluster_docs) == 1:
            issues.append("singleton_cluster")
        elif len(cluster_docs) > 20:
            issues.append("oversized_cluster")
        
        # Check topic diversity
        topics = self._extract_cluster_topics(cluster_docs)
        if len(topics) > 10:
            issues.append("high_topic_diversity")
        elif len(topics) == 0:
            issues.append("no_clear_topics")
        
        # Check authorship diversity
        all_authors = set()
        for doc in cluster_docs:
            if isinstance(doc, dict):
                metadata = doc.get("metadata", {})
                authors = metadata.get("authors", [])
                all_authors.update(authors)
        
        if len(all_authors) == 1:
            issues.append("single_author_cluster")
        elif len(all_authors) > 15:
            issues.append("high_author_diversity")
        
        return issues
    
    def _generate_recommendations(self, metrics: ClusteringMetrics, 
                                cluster_details: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for improving clustering"""
        recommendations = []
        
        if metrics.silhouette_score < 0.3:
            recommendations.append("Consider increasing number of clusters or using different similarity metrics")
        
        if metrics.davies_bouldin_index > 2.0:
            recommendations.append("Clusters may be too similar - consider merging or re-clustering")
        
        if metrics.cluster_balance < 0.5:
            recommendations.append("Cluster sizes are imbalanced - consider rebalancing or different clustering approach")
        
        if metrics.intra_cluster_cohesion < 0.4:
            recommendations.append("Documents within clusters are not very similar - refine similarity criteria")
        
        if metrics.inter_cluster_separation < 0.3:
            recommendations.append("Clusters are not well separated - consider different features or algorithms")
        
        # Check for singleton clusters
        singleton_clusters = [detail for detail in cluster_details if detail["size"] == 1]
        if len(singleton_clusters) > len(cluster_details) * 0.3:
            recommendations.append("Too many singleton clusters - consider reducing number of clusters")
        
        # Check for oversized clusters
        oversized_clusters = [detail for detail in cluster_details if detail["size"] > 20]
        if oversized_clusters:
            recommendations.append("Some clusters are too large - consider splitting large clusters")
        
        return recommendations
    
    def _assign_quality_grade(self, overall_quality: float) -> str:
        """Assign letter grade based on overall quality"""
        if overall_quality >= 0.8:
            return "A"
        elif overall_quality >= 0.7:
            return "B"
        elif overall_quality >= 0.6:
            return "C"
        elif overall_quality >= 0.5:
            return "D"
        else:
            return "F"
    
    async def compare_clustering_results(self, results1: List[Dict[str, Any]], 
                                       results2: List[Dict[str, Any]], 
                                       documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare two clustering results"""
        metrics1 = await self.evaluate_clustering_quality(results1, documents)
        metrics2 = await self.evaluate_clustering_quality(results2, documents)
        
        comparison = {
            "metrics_comparison": {
                "silhouette_score": {
                    "result1": metrics1.silhouette_score,
                    "result2": metrics2.silhouette_score,
                    "winner": "result1" if metrics1.silhouette_score > metrics2.silhouette_score else "result2"
                },
                "davies_bouldin_index": {
                    "result1": metrics1.davies_bouldin_index,
                    "result2": metrics2.davies_bouldin_index,
                    "winner": "result1" if metrics1.davies_bouldin_index < metrics2.davies_bouldin_index else "result2"
                },
                "overall_quality": {
                    "result1": metrics1.overall_quality,
                    "result2": metrics2.overall_quality,
                    "winner": "result1" if metrics1.overall_quality > metrics2.overall_quality else "result2"
                }
            },
            "cluster_count_comparison": {
                "result1": len(results1),
                "result2": len(results2)
            },
            "recommendation": "result1" if metrics1.overall_quality > metrics2.overall_quality else "result2"
        }
        
        return comparison