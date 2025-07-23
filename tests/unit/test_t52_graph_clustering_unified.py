#!/usr/bin/env python3
"""
Unit Tests for T52 Graph Clustering Tool - Mock-Free Implementation

This test suite validates T52 Graph Clustering functionality using real graph data
and algorithms. No mocking is used - all tests use actual NetworkX graphs,
real clustering algorithms, and genuine statistical calculations.

Test Coverage:
- Real spectral clustering with scikit-learn
- Multiple clustering algorithms (K-means, hierarchical, DBSCAN, Louvain)
- Graph Laplacian computation variants
- Academic quality metrics and confidence scoring
- Multiple data source loading (edge lists, adjacency matrices, NetworkX data)
- Error handling and algorithm fallbacks

Author: KGAS Development Team
Version: 1.0.0
"""

import pytest
import numpy as np
import networkx as nx
from typing import Dict, Any, List

# Import the tool under test
from src.tools.phase2.t52_graph_clustering_unified import (
    T52GraphClusteringTool, 
    ClusteringAlgorithm, 
    LaplacianType,
    ClusteringResult
)
from src.core.base_tool import ToolRequest, ToolResult
from src.core.service_manager import ServiceManager


class TestT52GraphClusteringMockFree:
    """Mock-free test suite for T52 Graph Clustering Tool"""
    
    def setup_method(self):
        """Set up test environment with real components"""
        # Create real ServiceManager - NO mocks
        self.service_manager = ServiceManager()
        self.tool = T52GraphClusteringTool(service_manager=self.service_manager)
        
        # Create real test graphs with known cluster structures
        self.test_graphs = self._create_test_graphs()
        
    def _create_test_graphs(self) -> Dict[str, nx.Graph]:
        """Create various test graphs with known clustering properties"""
        graphs = {}
        
        # Graph 1: Two clear clusters connected by a bridge
        graphs["two_clusters"] = nx.Graph()
        # Cluster 1: Complete graph K5
        for i in range(5):
            for j in range(i+1, 5):
                graphs["two_clusters"].add_edge(f"c1_{i}", f"c1_{j}")
        # Cluster 2: Complete graph K4
        for i in range(4):
            for j in range(i+1, 4):
                graphs["two_clusters"].add_edge(f"c2_{i}", f"c2_{j}")
        # Bridge between clusters
        graphs["two_clusters"].add_edge("c1_0", "c2_0")
        
        # Graph 2: Three star structures (clear cluster centers)
        graphs["three_stars"] = nx.Graph()
        for star_id in range(3):
            center = f"center_{star_id}"
            for i in range(5):
                graphs["three_stars"].add_edge(center, f"s{star_id}_node_{i}")
        
        # Graph 3: Path graph (should form linear clusters)
        graphs["path"] = nx.path_graph(20)
        
        # Graph 4: Karate club graph (classic clustering benchmark)
        graphs["karate"] = nx.karate_club_graph()
        
        # Graph 5: Small complete graph (single cluster)
        graphs["complete"] = nx.complete_graph(8)
        
        # Graph 6: Disconnected components (natural clusters)
        graphs["disconnected"] = nx.Graph()
        # Component 1
        graphs["disconnected"].add_edges_from([(0, 1), (1, 2), (2, 0)])
        # Component 2  
        graphs["disconnected"].add_edges_from([(3, 4), (4, 5), (5, 3)])
        # Component 3
        graphs["disconnected"].add_edges_from([(6, 7), (7, 8), (8, 6)])
        
        return graphs
    
    def test_tool_initialization_real(self):
        """Test T52 tool initialization with real components"""
        assert self.tool.tool_id == "T52"
        assert self.tool.name == "Graph Clustering"
        assert self.tool.category == "graph_analytics"
        assert self.tool.service_manager is not None
        assert hasattr(self.tool, 'default_config')
        assert ClusteringAlgorithm.SPECTRAL.value in self.tool.default_config['algorithm']
    
    def test_spectral_clustering_real_two_clusters(self):
        """Test real spectral clustering on graph with two clear clusters"""
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "networkx_data",
                "graph_data": {
                    "nodes": list(self.test_graphs["two_clusters"].nodes()),
                    "edges": [(u, v) for u, v in self.test_graphs["two_clusters"].edges()]
                }
            },
            parameters={
                "algorithm": ClusteringAlgorithm.SPECTRAL.value,
                "num_clusters": 2,
                "laplacian_type": LaplacianType.SYMMETRIC.value
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert "clustering_results" in result.data
        assert "quality_metrics" in result.data
        assert "academic_assessment" in result.data
        
        clustering_results = result.data["clustering_results"]
        assert clustering_results["num_clusters"] == 2
        assert "cluster_assignments" in clustering_results
        assert clustering_results["algorithm"] == ClusteringAlgorithm.SPECTRAL.value
        
        # Verify quality metrics
        quality_metrics = result.data["quality_metrics"]
        assert "modularity_score" in quality_metrics
        assert "silhouette_score" in quality_metrics
        assert isinstance(quality_metrics["modularity_score"], (int, float))
        
        # Academic assessment should show reasonable confidence
        academic = result.data["academic_assessment"]
        assert "confidence_score" in academic
        assert 0.0 <= academic["confidence_score"] <= 1.0
        assert "quality_grade" in academic
        assert "recommendations" in academic
    
    def test_spectral_clustering_real_three_stars(self):
        """Test spectral clustering on three star graphs (clear centers)"""
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "networkx_data",
                "graph_data": {
                    "nodes": list(self.test_graphs["three_stars"].nodes()),
                    "edges": [(u, v) for u, v in self.test_graphs["three_stars"].edges()]
                }
            },
            parameters={
                "algorithm": ClusteringAlgorithm.SPECTRAL.value,
                "num_clusters": 3
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        clustering_results = result.data["clustering_results"]
        assert clustering_results["num_clusters"] == 3
        
        # Check that clusters are reasonably sized
        cluster_sizes = clustering_results["cluster_sizes"]
        assert len(cluster_sizes) == 3
        assert all(size > 0 for size in cluster_sizes)
    
    def test_kmeans_clustering_real(self):
        """Test real K-means clustering on karate club graph"""
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "networkx_data", 
                "graph_data": {
                    "nodes": list(self.test_graphs["karate"].nodes()),
                    "edges": [(u, v) for u, v in self.test_graphs["karate"].edges()]
                }
            },
            parameters={
                "algorithm": ClusteringAlgorithm.K_MEANS.value,
                "num_clusters": 2
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        clustering_results = result.data["clustering_results"]
        assert clustering_results["algorithm"] == ClusteringAlgorithm.K_MEANS.value
        assert clustering_results["num_clusters"] == 2
        
        # Verify that all nodes are assigned to clusters
        cluster_assignments = clustering_results["cluster_assignments"]
        assert len(cluster_assignments) == self.test_graphs["karate"].number_of_nodes()
    
    def test_hierarchical_clustering_real(self):
        """Test real hierarchical clustering"""
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "networkx_data",
                "graph_data": {
                    "nodes": list(self.test_graphs["path"].nodes()),
                    "edges": [(u, v) for u, v in self.test_graphs["path"].edges()]
                }
            },
            parameters={
                "algorithm": ClusteringAlgorithm.HIERARCHICAL.value,
                "num_clusters": 4,
                "linkage": "ward"
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        clustering_results = result.data["clustering_results"]
        assert clustering_results["algorithm"] == ClusteringAlgorithm.HIERARCHICAL.value
        assert clustering_results["num_clusters"] == 4
    
    def test_dbscan_clustering_real(self):
        """Test real DBSCAN clustering"""
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "networkx_data",
                "graph_data": {
                    "nodes": list(self.test_graphs["complete"].nodes()),
                    "edges": [(u, v) for u, v in self.test_graphs["complete"].edges()]
                }
            },
            parameters={
                "algorithm": ClusteringAlgorithm.DBSCAN.value,
                "eps": 0.5,
                "min_samples": 3
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        clustering_results = result.data["clustering_results"]
        assert clustering_results["algorithm"] == ClusteringAlgorithm.DBSCAN.value
        # DBSCAN may find different number of clusters including noise points
        assert clustering_results["num_clusters"] >= 1
    
    def test_louvain_clustering_real(self):
        """Test real Louvain community detection"""
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "networkx_data",
                "graph_data": {
                    "nodes": list(self.test_graphs["karate"].nodes()),
                    "edges": [(u, v) for u, v in self.test_graphs["karate"].edges()]
                }
            },
            parameters={
                "algorithm": ClusteringAlgorithm.LOUVAIN.value
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        clustering_results = result.data["clustering_results"]
        assert clustering_results["algorithm"] == ClusteringAlgorithm.LOUVAIN.value
        
        # Louvain should find reasonable community structure in karate club
        assert clustering_results["num_clusters"] >= 2
        assert clustering_results["num_clusters"] <= 10  # Reasonable upper bound
        
        # Modularity should be positive for good community structure
        quality_metrics = result.data["quality_metrics"]
        assert quality_metrics["modularity_score"] > 0.0
    
    def test_leiden_clustering_with_fallback_real(self):
        """Test Leiden clustering with fallback to Louvain"""
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "networkx_data",
                "graph_data": {
                    "nodes": list(self.test_graphs["two_clusters"].nodes()),
                    "edges": [(u, v) for u, v in self.test_graphs["two_clusters"].edges()]
                }
            },
            parameters={
                "algorithm": ClusteringAlgorithm.LEIDEN.value
            }
        )
        
        result = self.tool.execute(request)
        
        # Should succeed either with Leiden or Louvain fallback
        assert result.status == "success"
        clustering_results = result.data["clustering_results"]
        # Algorithm might be "leiden" or "louvain" depending on availability
        assert "leiden" in clustering_results["algorithm"] or "louvain" in clustering_results["algorithm"]
    
    def test_auto_cluster_detection_real(self):
        """Test automatic cluster number detection"""
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "networkx_data",
                "graph_data": {
                    "nodes": list(self.test_graphs["disconnected"].nodes()),
                    "edges": [(u, v) for u, v in self.test_graphs["disconnected"].edges()]
                }
            },
            parameters={
                "algorithm": ClusteringAlgorithm.SPECTRAL.value,
                "num_clusters": None  # Auto-detect
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        clustering_results = result.data["clustering_results"]
        
        # Should detect approximately 3 clusters (3 disconnected components)
        detected_clusters = clustering_results["num_clusters"]
        assert 2 <= detected_clusters <= 5  # Reasonable range
    
    def test_laplacian_variants_real(self):
        """Test different graph Laplacian matrix variants"""
        laplacian_types = [
            LaplacianType.UNNORMALIZED.value,
            LaplacianType.SYMMETRIC.value,
            LaplacianType.RANDOM_WALK.value
        ]
        
        for laplacian_type in laplacian_types:
            request = ToolRequest(
                tool_id="T52",
                input_data={
                    "graph_source": "networkx_data",
                    "graph_data": {
                        "nodes": list(self.test_graphs["two_clusters"].nodes()),
                        "edges": [(u, v) for u, v in self.test_graphs["two_clusters"].edges()]
                    }
                },
                parameters={
                    "algorithm": ClusteringAlgorithm.SPECTRAL.value,
                    "num_clusters": 2,
                    "laplacian_type": laplacian_type
                }
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success", f"Failed for Laplacian type: {laplacian_type}"
            clustering_results = result.data["clustering_results"]
            assert clustering_results["num_clusters"] == 2
    
    def test_edge_list_loading_real(self):
        """Test loading graph from edge list"""
        edges = [
            ("A", "B"), ("B", "C"), ("C", "A"),  # Triangle 1
            ("D", "E"), ("E", "F"), ("F", "D"),  # Triangle 2
            ("A", "D")  # Bridge
        ]
        
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "edge_list",
                "edges": edges
            },
            parameters={
                "algorithm": ClusteringAlgorithm.SPECTRAL.value,
                "num_clusters": 2
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        clustering_results = result.data["clustering_results"]
        assert clustering_results["num_clusters"] == 2
        assert len(clustering_results["cluster_assignments"]) == 6  # 6 nodes
    
    def test_adjacency_matrix_loading_real(self):
        """Test loading graph from adjacency matrix"""
        # 4x4 adjacency matrix for a simple graph
        adj_matrix = [
            [0, 1, 1, 0],
            [1, 0, 1, 0], 
            [1, 1, 0, 1],
            [0, 0, 1, 0]
        ]
        
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "adjacency_matrix",
                "adjacency_matrix": adj_matrix
            },
            parameters={
                "algorithm": ClusteringAlgorithm.SPECTRAL.value,
                "num_clusters": 2
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        clustering_results = result.data["clustering_results"]
        assert clustering_results["num_clusters"] == 2
        assert len(clustering_results["cluster_assignments"]) == 4  # 4 nodes
    
    def test_weighted_edges_real(self):
        """Test clustering with weighted edges"""
        weighted_edges = [
            {"source": "A", "target": "B", "weight": 2.0},
            {"source": "B", "target": "C", "weight": 1.5},
            {"source": "C", "target": "A", "weight": 2.5},
            {"source": "D", "target": "E", "weight": 3.0},
            {"source": "E", "target": "F", "weight": 1.0},
            {"source": "F", "target": "D", "weight": 2.0},
            {"source": "A", "target": "D", "weight": 0.1}  # Weak bridge
        ]
        
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "edge_list",
                "edges": weighted_edges
            },
            parameters={
                "algorithm": ClusteringAlgorithm.SPECTRAL.value,
                "num_clusters": 2
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        clustering_results = result.data["clustering_results"]
        assert clustering_results["num_clusters"] == 2
    
    def test_quality_metrics_calculation_real(self):
        """Test comprehensive quality metrics calculation"""
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "networkx_data",
                "graph_data": {
                    "nodes": list(self.test_graphs["karate"].nodes()),
                    "edges": [(u, v) for u, v in self.test_graphs["karate"].edges()]
                }
            },
            parameters={
                "algorithm": ClusteringAlgorithm.LOUVAIN.value
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        quality_metrics = result.data["quality_metrics"]
        
        # Check all expected quality metrics are present
        expected_metrics = [
            "modularity_score", "silhouette_score", "num_clusters",
            "cluster_balance", "node_coverage", "internal_edge_ratio"
        ]
        for metric in expected_metrics:
            assert metric in quality_metrics
            assert isinstance(quality_metrics[metric], (int, float))
        
        # Modularity should be reasonable for karate club graph
        assert quality_metrics["modularity_score"] > 0.1
        
        # Node coverage should be 1.0 (all nodes clustered)
        assert abs(quality_metrics["node_coverage"] - 1.0) < 0.01
    
    def test_academic_confidence_scoring_real(self):
        """Test academic confidence scoring with real metrics"""
        # Test with high-quality clustering (two clear clusters)
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "networkx_data",
                "graph_data": {
                    "nodes": list(self.test_graphs["two_clusters"].nodes()),
                    "edges": [(u, v) for u, v in self.test_graphs["two_clusters"].edges()]
                }
            },
            parameters={
                "algorithm": ClusteringAlgorithm.SPECTRAL.value,
                "num_clusters": 2
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        academic = result.data["academic_assessment"]
        
        assert "confidence_score" in academic
        assert 0.0 <= academic["confidence_score"] <= 1.0
        
        assert "quality_grade" in academic
        assert academic["quality_grade"] in [
            "A+ (Excellent)", "A (Very Good)", "B+ (Good)", 
            "B (Satisfactory)", "C+ (Fair)", "C (Acceptable)", "D (Poor)"
        ]
        
        assert "recommendations" in academic
        assert isinstance(academic["recommendations"], list)
        assert len(academic["recommendations"]) > 0
    
    def test_large_graph_performance_real(self):
        """Test performance with larger graph"""
        # Create a larger graph (100 nodes, random structure)
        large_graph = nx.erdos_renyi_graph(100, 0.05, seed=42)
        
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "networkx_data",
                "graph_data": {
                    "nodes": list(large_graph.nodes()),
                    "edges": [(u, v) for u, v in large_graph.edges()]
                }
            },
            parameters={
                "algorithm": ClusteringAlgorithm.LOUVAIN.value  # Efficient for large graphs
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        assert result.execution_time < 10.0  # Should complete within 10 seconds
        
        clustering_results = result.data["clustering_results"]
        assert clustering_results["num_clusters"] >= 2
        assert len(clustering_results["cluster_assignments"]) == 100
    
    def test_error_handling_invalid_graph_source_real(self):
        """Test error handling for invalid graph source"""
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "invalid_source"
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "error"
        assert "error" in result.data
        assert "Invalid graph source" in result.data["error"]
    
    def test_error_handling_missing_data_real(self):
        """Test error handling for missing required data"""
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "edge_list"
                # Missing "edges" key
            },
            parameters={}
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "error"
        assert "error" in result.data
        assert "Edge list required" in result.data["error"]
    
    def test_algorithm_fallback_handling_real(self):
        """Test algorithm fallback when preferred algorithm fails"""
        # Test with a very small graph that might cause issues for some algorithms
        tiny_graph = nx.Graph()
        tiny_graph.add_edge("A", "B")
        
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "networkx_data",
                "graph_data": {
                    "nodes": list(tiny_graph.nodes()),
                    "edges": [(u, v) for u, v in tiny_graph.edges()]
                }
            },
            parameters={
                "algorithm": ClusteringAlgorithm.SPECTRAL.value,
                "num_clusters": 5  # More clusters than nodes - should trigger fallback
            }
        )
        
        result = self.tool.execute(request)
        
        # Should handle gracefully and produce a result
        assert result.status == "success"
        clustering_results = result.data["clustering_results"]
        assert clustering_results["num_clusters"] <= 2  # Should be limited by node count
    
    def test_cluster_statistics_calculation_real(self):
        """Test detailed cluster statistics calculation"""
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "networkx_data",
                "graph_data": {
                    "nodes": list(self.test_graphs["three_stars"].nodes()),
                    "edges": [(u, v) for u, v in self.test_graphs["three_stars"].edges()]
                }
            },
            parameters={
                "algorithm": ClusteringAlgorithm.SPECTRAL.value,
                "num_clusters": 3
            }
        )
        
        result = self.tool.execute(request)
        
        assert result.status == "success"
        cluster_stats = result.data["cluster_statistics"]
        
        # Check all expected statistics
        expected_stats = [
            "cluster_sizes", "average_cluster_size", "cluster_size_std",
            "largest_cluster_size", "smallest_cluster_size", "cluster_size_balance"
        ]
        for stat in expected_stats:
            assert stat in cluster_stats
            assert isinstance(cluster_stats[stat], (int, float, list))
        
        # Verify cluster size balance is meaningful
        assert 0.0 <= cluster_stats["cluster_size_balance"] <= 1.0
    
    def test_all_clustering_algorithms_produce_results_real(self):
        """Test that all supported algorithms produce valid results"""
        algorithms = [
            ClusteringAlgorithm.SPECTRAL.value,
            ClusteringAlgorithm.K_MEANS.value,
            ClusteringAlgorithm.HIERARCHICAL.value,
            ClusteringAlgorithm.DBSCAN.value,
            ClusteringAlgorithm.LOUVAIN.value,
            ClusteringAlgorithm.LEIDEN.value
        ]
        
        test_graph = self.test_graphs["karate"]
        
        for algorithm in algorithms:
            request = ToolRequest(
                tool_id="T52",
                input_data={
                    "graph_source": "networkx_data",
                    "graph_data": {
                        "nodes": list(test_graph.nodes()),
                        "edges": [(u, v) for u, v in test_graph.edges()]
                    }
                },
                parameters={
                    "algorithm": algorithm,
                    "num_clusters": 3 if algorithm != ClusteringAlgorithm.DBSCAN.value else None
                }
            )
            
            result = self.tool.execute(request)
            
            assert result.status == "success", f"Algorithm {algorithm} failed"
            assert "clustering_results" in result.data
            assert result.data["clustering_results"]["num_clusters"] >= 1
    
    def test_neo4j_loading_fallback_real(self):
        """Test Neo4j loading with fallback to mock data"""
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "neo4j",
                "neo4j_config": {
                    "uri": "bolt://localhost:7687",
                    "username": "neo4j",
                    "password": "password"
                }
            },
            parameters={
                "algorithm": ClusteringAlgorithm.SPECTRAL.value,
                "num_clusters": 3
            }
        )
        
        result = self.tool.execute(request)
        
        # Should succeed with either real Neo4j data or mock data fallback
        assert result.status == "success"
        clustering_results = result.data["clustering_results"]
        assert clustering_results["num_clusters"] >= 1
        assert len(clustering_results["cluster_assignments"]) > 0


# Integration test for real workflow
class TestT52IntegrationMockFree:
    """Integration tests for T52 with real workflow scenarios"""
    
    def setup_method(self):
        """Set up integration test environment"""
        self.service_manager = ServiceManager()
        self.tool = T52GraphClusteringTool(service_manager=self.service_manager)
    
    def test_complete_clustering_workflow_real(self):
        """Test complete clustering workflow from data to insights"""
        # Create a realistic academic collaboration network
        collab_network = nx.Graph()
        
        # Research group 1: AI researchers
        ai_researchers = ["Alice", "Bob", "Charlie", "Diana"]
        for i, researcher1 in enumerate(ai_researchers):
            for researcher2 in ai_researchers[i+1:]:
                collab_network.add_edge(researcher1, researcher2, weight=2.0)
        
        # Research group 2: Biology researchers
        bio_researchers = ["Eve", "Frank", "Grace"]
        for i, researcher1 in enumerate(bio_researchers):
            for researcher2 in bio_researchers[i+1:]:
                collab_network.add_edge(researcher1, researcher2, weight=1.5)
        
        # Cross-disciplinary collaborations (weaker connections)
        collab_network.add_edge("Alice", "Eve", weight=0.5)
        collab_network.add_edge("Charlie", "Frank", weight=0.3)
        
        # Execute clustering
        request = ToolRequest(
            tool_id="T52",
            input_data={
                "graph_source": "networkx_data",
                "graph_data": {
                    "nodes": list(collab_network.nodes()),
                    "edges": [
                        {"source": u, "target": v, "weight": d.get("weight", 1.0)}
                        for u, v, d in collab_network.edges(data=True)
                    ]
                }
            },
            parameters={
                "algorithm": ClusteringAlgorithm.LOUVAIN.value
            }
        )
        
        result = self.tool.execute(request)
        
        # Verify successful execution
        assert result.status == "success"
        
        # Verify clustering identifies the two research groups
        clustering_results = result.data["clustering_results"]
        assert clustering_results["num_clusters"] >= 2
        
        # Verify quality metrics indicate good clustering
        quality_metrics = result.data["quality_metrics"]
        assert quality_metrics["modularity_score"] > 0.2  # Should find community structure
        
        # Verify academic assessment provides actionable insights
        academic = result.data["academic_assessment"]
        assert academic["confidence_score"] > 0.4  # Should be reasonably confident
        assert len(academic["recommendations"]) > 0
        
        # Verify metadata is complete
        metadata = result.data["metadata"]
        assert metadata["tool_id"] == "T52"
        assert metadata["academic_quality"] in ["low", "medium", "high"]
    
    def test_clustering_comparison_workflow_real(self):
        """Test workflow comparing different clustering algorithms"""
        test_graph = nx.karate_club_graph()
        algorithms_to_test = [
            ClusteringAlgorithm.SPECTRAL.value,
            ClusteringAlgorithm.LOUVAIN.value,
            ClusteringAlgorithm.K_MEANS.value
        ]
        
        results = {}
        
        for algorithm in algorithms_to_test:
            request = ToolRequest(
                tool_id="T52",
                input_data={
                    "graph_source": "networkx_data",
                    "graph_data": {
                        "nodes": list(test_graph.nodes()),
                        "edges": [(u, v) for u, v in test_graph.edges()]
                    }
                },
                parameters={
                    "algorithm": algorithm,
                    "num_clusters": 2
                }
            )
            
            result = self.tool.execute(request)
            assert result.status == "success"
            results[algorithm] = result.data
        
        # Compare results across algorithms
        for algorithm, data in results.items():
            assert data["clustering_results"]["num_clusters"] == 2
            assert "modularity_score" in data["quality_metrics"]
            assert data["academic_assessment"]["confidence_score"] > 0.0
        
        # Verify different algorithms can produce different but valid results
        modularities = [
            data["quality_metrics"]["modularity_score"] 
            for data in results.values()
        ]
        # At least one algorithm should find reasonable community structure
        assert any(mod > 0.1 for mod in modularities)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])