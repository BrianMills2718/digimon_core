#!/usr/bin/env python3
"""
Integration Tests for Phase 2.1 Analytics Pipeline

Tests real end-to-end analytics workflows with NO MOCKS.
Validates that all Phase 2.1 tools work together correctly.
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
import networkx as nx
import json
import time
from typing import Dict, List, Any

# Import all Phase 2.1 tools
from src.tools.phase2.t50_community_detection_unified import CommunityDetectionTool
from src.tools.phase2.t51_centrality_analysis_unified import CentralityAnalysisTool
from src.tools.phase2.t52_graph_clustering_unified import T52GraphClusteringTool
from src.tools.phase2.t53_network_motifs_unified import NetworkMotifsDetectionTool
from src.tools.phase2.t54_graph_visualization_unified import GraphVisualizationTool
from src.tools.phase2.t55_temporal_analysis_unified import TemporalAnalysisTool
from src.tools.phase2.t56_graph_metrics_unified import GraphMetricsTool
from src.tools.phase2.t57_path_analysis_unified import PathAnalysisTool
from src.tools.phase2.t58_graph_comparison_unified import T58GraphComparisonTool
from src.tools.phase2.t59_scale_free_analysis_unified import ScaleFreeAnalyzer
from src.tools.phase2.t60_graph_export_unified import GraphExportTool

from src.core.service_manager import ServiceManager
from src.core.neo4j_manager import Neo4jManager


class TestPhase21AnalyticsPipeline:
    """Integration tests for complete Phase 2.1 analytics pipeline"""
    
    def setup_method(self):
        """Setup real services and tools"""
        self.service_manager = ServiceManager()
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize all Phase 2.1 tools
        self.tools = {
            "community_detection": CommunityDetectionTool(self.service_manager),
            "centrality_analysis": CentralityAnalysisTool(self.service_manager),
            "graph_clustering": T52GraphClusteringTool(self.service_manager),
            "network_motifs": NetworkMotifsDetectionTool(self.service_manager),
            "graph_visualization": GraphVisualizationTool(self.service_manager),
            "temporal_analysis": TemporalAnalysisTool(self.service_manager),
            "graph_metrics": GraphMetricsTool(self.service_manager),
            "path_analysis": PathAnalysisTool(self.service_manager),
            "graph_comparison": T58GraphComparisonTool(self.service_manager),
            "scale_free_analysis": ScaleFreeAnalyzer(self.service_manager),
            "graph_export": GraphExportTool(self.service_manager)
        }
    
    def teardown_method(self):
        """Clean up resources"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_academic_graph(self) -> Dict[str, Any]:
        """Create realistic academic collaboration graph"""
        # Create a graph representing academic collaborations
        nodes = []
        edges = []
        
        # Universities
        universities = [
            {"id": "MIT", "label": "Organization", "type": "University"},
            {"id": "Stanford", "label": "Organization", "type": "University"},
            {"id": "Berkeley", "label": "Organization", "type": "University"}
        ]
        
        # Researchers
        researchers = [
            {"id": "alice_smith", "label": "Person", "name": "Alice Smith", 
             "affiliation": "MIT", "h_index": 25},
            {"id": "bob_johnson", "label": "Person", "name": "Bob Johnson",
             "affiliation": "MIT", "h_index": 30},
            {"id": "carol_williams", "label": "Person", "name": "Carol Williams",
             "affiliation": "Stanford", "h_index": 35},
            {"id": "david_brown", "label": "Person", "name": "David Brown",
             "affiliation": "Stanford", "h_index": 20},
            {"id": "eve_davis", "label": "Person", "name": "Eve Davis",
             "affiliation": "Berkeley", "h_index": 40}
        ]
        
        # Papers
        papers = [
            {"id": "paper1", "label": "Paper", "title": "Deep Learning Advances",
             "year": 2023, "citations": 150},
            {"id": "paper2", "label": "Paper", "title": "Graph Neural Networks",
             "year": 2023, "citations": 200},
            {"id": "paper3", "label": "Paper", "title": "NLP Transformers",
             "year": 2022, "citations": 300}
        ]
        
        nodes.extend(universities)
        nodes.extend(researchers)
        nodes.extend(papers)
        
        # Affiliations
        for researcher in researchers:
            edges.append({
                "source": researcher["id"],
                "target": researcher["affiliation"],
                "type": "AFFILIATED_WITH"
            })
        
        # Authorships
        edges.extend([
            {"source": "alice_smith", "target": "paper1", "type": "AUTHORED"},
            {"source": "bob_johnson", "target": "paper1", "type": "AUTHORED"},
            {"source": "carol_williams", "target": "paper2", "type": "AUTHORED"},
            {"source": "david_brown", "target": "paper2", "type": "AUTHORED"},
            {"source": "eve_davis", "target": "paper3", "type": "AUTHORED"},
            {"source": "alice_smith", "target": "paper3", "type": "AUTHORED"}
        ])
        
        # Collaborations (derived from co-authorship)
        edges.extend([
            {"source": "alice_smith", "target": "bob_johnson", 
             "type": "COLLABORATES_WITH", "weight": 0.8},
            {"source": "carol_williams", "target": "david_brown",
             "type": "COLLABORATES_WITH", "weight": 0.9},
            {"source": "eve_davis", "target": "alice_smith",
             "type": "COLLABORATES_WITH", "weight": 0.7}
        ])
        
        return {"nodes": nodes, "edges": edges}
    
    @pytest.mark.asyncio
    async def test_complete_analytics_pipeline(self):
        """Test complete analytics pipeline from graph to insights"""
        # Create test graph
        graph_data = self._create_academic_graph()
        
        # Step 1: Analyze graph structure
        metrics_result = await self.tools["graph_metrics"].execute({
            "graph_data": graph_data,
            "calculate_all": True
        })
        
        assert metrics_result.basic_metrics["num_nodes"] == 11
        assert metrics_result.basic_metrics["num_edges"] > 10
        assert metrics_result.basic_metrics["density"] > 0
        
        # Step 2: Detect communities
        community_result = await self.tools["community_detection"].execute({
            "graph_data": graph_data,
            "algorithm": "louvain",
            "resolution": 1.0
        })
        
        assert community_result.num_communities >= 2
        assert community_result.modularity_score > 0
        
        # Step 3: Analyze centrality
        centrality_result = await self.tools["centrality_analysis"].execute({
            "graph_data": graph_data,
            "centrality_types": ["degree", "betweenness", "closeness"],
            "normalize": True
        })
        
        # Alice Smith should be central (connected to multiple papers)
        alice_centrality = next(
            n for n in centrality_result.node_centralities 
            if n["node_id"] == "alice_smith"
        )
        assert alice_centrality["degree_centrality"] > 0.2
        
        # Step 4: Check scale-free properties
        scale_free_result = await self.tools["scale_free_analysis"].execute({
            "graph_data": graph_data,
            "min_degree": 1,
            "temporal_analysis": False,
            "hub_threshold_percentile": 80.0
        })
        
        # Academic networks often show scale-free properties
        assert scale_free_result.power_law_alpha > 0
        assert len(scale_free_result.hub_nodes) > 0
        
        # Step 5: Export results
        export_path = str(Path(self.temp_dir) / "academic_network.graphml")
        export_result = await self.tools["graph_export"].execute({
            "graph_data": graph_data,
            "export_format": "graphml",
            "output_path": export_path,
            "compression": "none",
            "include_metadata": True
        })
        
        assert Path(export_path).exists()
        assert export_result.num_nodes_exported == 11
    
    @pytest.mark.asyncio
    async def test_cross_tool_data_flow(self):
        """Test data flows correctly between tools"""
        graph_data = self._create_academic_graph()
        
        # Community detection → Clustering comparison
        community_result = await self.tools["community_detection"].execute({
            "graph_data": graph_data,
            "algorithm": "louvain"
        })
        
        clustering_result = await self.tools["graph_clustering"].execute({
            "graph_data": graph_data,
            "algorithm": "spectral",
            "n_clusters": community_result.num_communities
        })
        
        # Results should be somewhat consistent
        assert abs(clustering_result.num_clusters - community_result.num_communities) <= 2
        
        # Path analysis using centrality results
        centrality_result = await self.tools["centrality_analysis"].execute({
            "graph_data": graph_data,
            "centrality_types": ["betweenness"]
        })
        
        # Find most central nodes
        top_nodes = sorted(
            centrality_result.node_centralities,
            key=lambda x: x["betweenness_centrality"],
            reverse=True
        )[:2]
        
        # Analyze paths between top nodes
        if len(top_nodes) >= 2:
            path_result = await self.tools["path_analysis"].execute({
                "graph_data": graph_data,
                "source_node": top_nodes[0]["node_id"],
                "target_node": top_nodes[1]["node_id"],
                "analysis_type": "shortest_path"
            })
            
            assert path_result.path_exists
            assert len(path_result.shortest_path) > 0
    
    @pytest.mark.asyncio
    async def test_temporal_evolution_analysis(self):
        """Test temporal analysis capabilities"""
        # Create graphs at different time points
        graph_t1 = {
            "nodes": [
                {"id": 1, "timestamp": "2022-01-01"},
                {"id": 2, "timestamp": "2022-01-01"},
                {"id": 3, "timestamp": "2022-01-01"}
            ],
            "edges": [
                {"source": 1, "target": 2, "timestamp": "2022-01-01"},
                {"source": 2, "target": 3, "timestamp": "2022-01-01"}
            ]
        }
        
        graph_t2 = {
            "nodes": [
                {"id": 1, "timestamp": "2023-01-01"},
                {"id": 2, "timestamp": "2023-01-01"},
                {"id": 3, "timestamp": "2023-01-01"},
                {"id": 4, "timestamp": "2023-01-01"}
            ],
            "edges": [
                {"source": 1, "target": 2, "timestamp": "2023-01-01"},
                {"source": 2, "target": 3, "timestamp": "2023-01-01"},
                {"source": 3, "target": 4, "timestamp": "2023-01-01"},
                {"source": 4, "target": 1, "timestamp": "2023-01-01"}
            ]
        }
        
        # Analyze temporal evolution
        temporal_result = await self.tools["temporal_analysis"].execute({
            "graph_snapshots": [graph_t1, graph_t2],
            "time_labels": ["2022", "2023"],
            "analysis_types": ["growth_rate", "stability"]
        })
        
        assert temporal_result.temporal_metrics["node_growth_rate"] > 0
        assert temporal_result.temporal_metrics["edge_growth_rate"] > 0
        
        # Compare graphs
        comparison_result = await self.tools["graph_comparison"].execute({
            "graph1": graph_t1,
            "graph2": graph_t2,
            "comparison_metrics": ["structural", "node_overlap"]
        })
        
        assert comparison_result.similarity_scores["node_overlap"] > 0.5
        assert comparison_result.differences["nodes_added"] == 1
        assert comparison_result.differences["edges_added"] == 2
    
    @pytest.mark.asyncio
    async def test_motif_analysis_integration(self):
        """Test network motif analysis integration"""
        # Create graph with known motifs
        graph_data = {
            "nodes": [{"id": i} for i in range(10)],
            "edges": [
                # Triangle motif
                {"source": 0, "target": 1},
                {"source": 1, "target": 2},
                {"source": 2, "target": 0},
                # Another triangle
                {"source": 3, "target": 4},
                {"source": 4, "target": 5},
                {"source": 5, "target": 3},
                # Chain
                {"source": 6, "target": 7},
                {"source": 7, "target": 8},
                {"source": 8, "target": 9}
            ]
        }
        
        motif_result = await self.tools["network_motifs"].execute({
            "graph_data": graph_data,
            "motif_size": 3,
            "include_counts": True
        })
        
        # Should find triangles
        triangle_motifs = [m for m in motif_result.motifs if m["motif_type"] == "triangle"]
        assert len(triangle_motifs) > 0
        
        # Export motif analysis
        export_result = await self.tools["graph_export"].execute({
            "graph_data": {
                "nodes": graph_data["nodes"],
                "edges": graph_data["edges"],
                "metadata": {"motifs": motif_result.motif_statistics}
            },
            "export_format": "json-ld",
            "output_path": str(Path(self.temp_dir) / "motifs.jsonld"),
            "include_metadata": True
        })
        
        assert Path(export_result.export_path).exists()
    
    @pytest.mark.asyncio
    async def test_performance_with_large_graph(self):
        """Test pipeline performance with larger graph"""
        # Create larger graph
        G = nx.barabasi_albert_graph(500, 3, seed=42)
        large_graph = {
            "nodes": [{"id": n, "label": f"Node_{n}"} for n in G.nodes()],
            "edges": [{"source": s, "target": t, "type": "CONNECTED"} 
                     for s, t in G.edges()]
        }
        
        start_time = time.time()
        
        # Run multiple analyses
        tasks = [
            self.tools["graph_metrics"].execute({
                "graph_data": large_graph,
                "calculate_all": True
            }),
            self.tools["community_detection"].execute({
                "graph_data": large_graph,
                "algorithm": "louvain"
            }),
            self.tools["scale_free_analysis"].execute({
                "graph_data": large_graph,
                "min_degree": 1
            })
        ]
        
        results = await asyncio.gather(*tasks)
        execution_time = time.time() - start_time
        
        # Should complete within reasonable time
        assert execution_time < 30.0  # 30 seconds for 500 nodes
        
        # Verify results
        metrics_result, community_result, scale_free_result = results
        assert metrics_result.basic_metrics["num_nodes"] == 500
        assert community_result.num_communities > 1
        assert scale_free_result.is_scale_free == True
    
    @pytest.mark.asyncio
    async def test_error_handling_across_tools(self):
        """Test error handling when tools receive invalid data"""
        # Invalid graph (no nodes)
        invalid_graph = {"nodes": [], "edges": [{"source": 1, "target": 2}]}
        
        # Tools should handle gracefully
        metrics_result = await self.tools["graph_metrics"].execute({
            "graph_data": invalid_graph,
            "calculate_all": True
        })
        
        assert metrics_result.basic_metrics["num_nodes"] == 0
        assert metrics_result.basic_metrics["num_edges"] == 0
        
        # Invalid export path
        with pytest.raises(Exception):
            await self.tools["graph_export"].execute({
                "graph_data": self._create_academic_graph(),
                "export_format": "graphml",
                "output_path": "/invalid/path/that/does/not/exist.graphml"
            })


@pytest.mark.benchmark
class TestPhase21PerformanceBenchmarks:
    """Performance benchmarks for Phase 2.1 tools"""
    
    def setup_method(self):
        self.service_manager = ServiceManager()
        self.tools = {
            "community_detection": CommunityDetectionTool(self.service_manager),
            "scale_free_analysis": ScaleFreeAnalyzer(self.service_manager),
            "graph_export": GraphExportTool(self.service_manager)
        }
    
    @pytest.mark.asyncio
    async def test_benchmark_tool_scaling(self):
        """Benchmark tool performance with increasing graph sizes"""
        sizes = [100, 500, 1000, 2000]
        results = []
        
        for size in sizes:
            # Create graph
            G = nx.barabasi_albert_graph(size, 3, seed=42)
            graph_data = {
                "nodes": [{"id": n} for n in G.nodes()],
                "edges": [{"source": s, "target": t} for s, t in G.edges()]
            }
            
            # Benchmark community detection
            start = time.time()
            community_result = await self.tools["community_detection"].execute({
                "graph_data": graph_data,
                "algorithm": "louvain"
            })
            community_time = time.time() - start
            
            # Benchmark scale-free analysis
            start = time.time()
            scale_free_result = await self.tools["scale_free_analysis"].execute({
                "graph_data": graph_data,
                "min_degree": 1
            })
            scale_free_time = time.time() - start
            
            results.append({
                "size": size,
                "community_detection_time": community_time,
                "scale_free_analysis_time": scale_free_time,
                "num_communities": community_result.num_communities,
                "is_scale_free": scale_free_result.is_scale_free
            })
            
            # Performance requirements
            if size <= 1000:
                assert community_time < 5.0
                assert scale_free_time < 5.0
        
        # Print results
        print("\nPerformance Benchmark Results:")
        for r in results:
            print(f"Size: {r['size']}, Community: {r['community_detection_time']:.2f}s, "
                  f"Scale-free: {r['scale_free_analysis_time']:.2f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])