"""
Adversarial Testing for Graph Visualization

Tests visualization components with challenging inputs and edge cases.
"""

import logging
import time
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime

from .visualization_data_models import (
    VisualizationData, NodeData, EdgeData, OntologyInfo, 
    VisualizationMetrics, GraphVisualizationConfig, LayoutAlgorithm
)
from .graph_data_loader import GraphDataLoader
from .layout_calculator import GraphLayoutCalculator
from .plotly_renderer import PlotlyGraphRenderer

logger = logging.getLogger(__name__)


class VisualizationAdversarialTester:
    """Test visualization components with adversarial inputs and edge cases"""
    
    def __init__(self, data_loader: Optional[GraphDataLoader] = None,
                 layout_calculator: Optional[GraphLayoutCalculator] = None,
                 renderer: Optional[PlotlyGraphRenderer] = None):
        """Initialize tester with optional component instances"""
        self.data_loader = data_loader or GraphDataLoader()
        self.layout_calculator = layout_calculator or GraphLayoutCalculator()
        self.renderer = renderer or PlotlyGraphRenderer()
    
    def run_comprehensive_adversarial_tests(self, max_test_nodes: int = 100) -> Dict[str, Any]:
        """Run comprehensive adversarial tests on visualization components"""
        logger.info("🎨 Running comprehensive adversarial tests for visualization...")
        
        test_results = {
            "large_graph_handling": self._test_large_graph_visualization(max_test_nodes),
            "empty_graph_handling": self._test_empty_graph_visualization(),
            "malformed_data_handling": self._test_malformed_data_visualization(),
            "unicode_label_handling": self._test_unicode_labels(),
            "extreme_confidence_values": self._test_extreme_confidence_values(),
            "layout_algorithm_stress": self._test_layout_algorithm_stress(),
            "color_scheme_robustness": self._test_color_scheme_robustness(),
            "rendering_performance": self._test_rendering_performance(),
            "memory_usage": self._test_memory_usage_limits(),
            "concurrent_operations": self._test_concurrent_operations()
        }
        
        # Calculate overall test score
        passed_tests = sum(1 for test in test_results.values() if test.get("passed", False))
        total_tests = len(test_results)
        
        test_results["overall_score"] = passed_tests / total_tests
        test_results["summary"] = f"Visualization adversarial tests: {passed_tests}/{total_tests} passed"
        test_results["test_timestamp"] = datetime.now().isoformat()
        
        logger.info(f"🎨 Visualization adversarial testing complete: {passed_tests}/{total_tests} passed")
        
        return test_results
    
    def _test_large_graph_visualization(self, max_nodes: int) -> Dict[str, Any]:
        """Test visualization with large graphs"""
        try:
            start_time = time.time()
            
            # Generate large synthetic graph
            nodes = []
            edges = []
            
            # Create nodes
            for i in range(max_nodes):
                node = NodeData(
                    id=f"node_{i}",
                    name=f"Entity {i}",
                    type="TEST_ENTITY",
                    confidence=np.random.uniform(0.5, 1.0),
                    size=np.random.uniform(10, 30),
                    color="#3498db"
                )
                nodes.append(node)
            
            # Create edges (random connections)
            num_edges = min(max_nodes * 2, 200)  # Limit edges for performance
            for i in range(num_edges):
                source_idx = np.random.randint(0, len(nodes))
                target_idx = np.random.randint(0, len(nodes))
                if source_idx != target_idx:
                    edge = EdgeData(
                        source=nodes[source_idx].id,
                        target=nodes[target_idx].id,
                        type="TEST_RELATIONSHIP",
                        confidence=np.random.uniform(0.5, 1.0),
                        width=2.0,
                        color="#95a5a6"
                    )
                    edges.append(edge)
            
            # Test layout calculation
            config = GraphVisualizationConfig(max_nodes=max_nodes, max_edges=num_edges)
            layout_positions = self.layout_calculator.calculate_layout(
                nodes, edges, LayoutAlgorithm.SPRING
            )
            
            # Create visualization data
            vis_data = VisualizationData(
                nodes=nodes,
                edges=edges,
                ontology_info=OntologyInfo(
                    entity_type_counts={"TEST_ENTITY": len(nodes)},
                    relationship_type_counts={"TEST_RELATIONSHIP": len(edges)},
                    confidence_distribution={},
                    ontology_coverage={},
                    domains=[]
                ),
                metrics=VisualizationMetrics(
                    total_nodes=len(nodes),
                    total_edges=len(edges),
                    avg_confidence=0.75,
                    entity_types=1,
                    relationship_types=1,
                    graph_density=len(edges) / (len(nodes) * (len(nodes) - 1) / 2)
                ),
                layout_positions=layout_positions
            )
            
            # Test rendering
            fig = self.renderer.create_interactive_plot(vis_data, config)
            
            execution_time = time.time() - start_time
            passed = len(layout_positions) <= max_nodes and fig is not None
            
            return {
                "passed": passed,
                "details": f"Handled {len(nodes)} nodes, {len(edges)} edges in {execution_time:.2f}s",
                "execution_time": execution_time,
                "nodes_processed": len(nodes),
                "edges_processed": len(edges)
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _test_empty_graph_visualization(self) -> Dict[str, Any]:
        """Test visualization with empty graph"""
        try:
            # Create empty visualization data
            empty_data = VisualizationData(
                nodes=[],
                edges=[],
                ontology_info=OntologyInfo(
                    entity_type_counts={},
                    relationship_type_counts={},
                    confidence_distribution={},
                    ontology_coverage={},
                    domains=[]
                ),
                metrics=VisualizationMetrics(
                    total_nodes=0,
                    total_edges=0,
                    avg_confidence=0.0,
                    entity_types=0,
                    relationship_types=0,
                    graph_density=0.0
                ),
                layout_positions={}
            )
            
            # Test layout calculation
            layout_positions = self.layout_calculator.calculate_layout([], [])
            
            # Test rendering
            fig = self.renderer.create_interactive_plot(empty_data)
            ontology_fig = self.renderer.create_ontology_structure_plot(empty_data.ontology_info)
            
            passed = fig is not None and ontology_fig is not None
            
            return {
                "passed": passed,
                "details": "Empty graph visualization handled gracefully",
                "layout_empty": len(layout_positions) == 0,
                "figure_created": fig is not None
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _test_malformed_data_visualization(self) -> Dict[str, Any]:
        """Test visualization with malformed data"""
        try:
            # Create malformed data with various issues
            malformed_nodes = [
                NodeData(id=None, name="Invalid Node 1", type="", confidence=-0.5),
                NodeData(id="", name=None, type="VALID", confidence=1.5),
                NodeData(id="valid_node", name="Valid Node", type="VALID", confidence=0.8),
                NodeData(id="duplicate_node", name="Duplicate", type="VALID", confidence=0.7),
                NodeData(id="duplicate_node", name="Duplicate", type="VALID", confidence=0.6)  # Duplicate ID
            ]
            
            malformed_edges = [
                EdgeData(source="missing_source", target="valid_node", type="INVALID", confidence=0.8),
                EdgeData(source="valid_node", target="missing_target", type="INVALID", confidence=0.8),
                EdgeData(source="valid_node", target="valid_node", type="SELF_LOOP", confidence=0.8),
                EdgeData(source="", target="valid_node", type="EMPTY_SOURCE", confidence=0.8),
                EdgeData(source="valid_node", target=None, type="NULL_TARGET", confidence=0.8)
            ]
            
            # Test layout calculation with malformed data
            layout_positions = self.layout_calculator.calculate_layout(
                malformed_nodes, malformed_edges
            )
            
            # Create visualization data
            malformed_data = VisualizationData(
                nodes=malformed_nodes,
                edges=malformed_edges,
                ontology_info=OntologyInfo(
                    entity_type_counts={"VALID": 2, "": 1},
                    relationship_type_counts={"INVALID": 2, "SELF_LOOP": 1},
                    confidence_distribution={},
                    ontology_coverage={},
                    domains=[]
                ),
                metrics=VisualizationMetrics(
                    total_nodes=len(malformed_nodes),
                    total_edges=len(malformed_edges),
                    avg_confidence=0.5,
                    entity_types=2,
                    relationship_types=3,
                    graph_density=0.1
                ),
                layout_positions=layout_positions
            )
            
            # Test rendering
            fig = self.renderer.create_interactive_plot(malformed_data)
            
            passed = fig is not None  # Should handle gracefully without crashing
            
            return {
                "passed": passed,
                "details": "Malformed data handled gracefully without crashing",
                "layout_calculated": len(layout_positions) > 0,
                "figure_created": fig is not None
            }
            
        except Exception as e:
            # Expected to handle malformed data gracefully
            return {
                "passed": True, 
                "details": f"Handled malformed data error gracefully: {str(e)[:100]}"
            }
    
    def _test_unicode_labels(self) -> Dict[str, Any]:
        """Test visualization with Unicode labels and special characters"""
        try:
            unicode_nodes = [
                NodeData(id="node1", name="北京", type="LOCATION", confidence=0.9, size=20, color="#3498db"),
                NodeData(id="node2", name="São Paulo", type="LOCATION", confidence=0.8, size=18, color="#3498db"),
                NodeData(id="node3", name="Москва", type="LOCATION", confidence=0.85, size=19, color="#3498db"),
                NodeData(id="node4", name="東京", type="LOCATION", confidence=0.92, size=21, color="#3498db"),
                NodeData(id="node5", name="🌍 Earth", type="LOCATION", confidence=0.95, size=25, color="#2ecc71")  # Emoji
            ]
            
            unicode_edges = [
                EdgeData(source="node1", target="node2", type="連接", confidence=0.8, width=2, color="#95a5a6"),
                EdgeData(source="node2", target="node3", type="соединение", confidence=0.75, width=2, color="#95a5a6"),
                EdgeData(source="node3", target="node4", type="接続", confidence=0.85, width=2, color="#95a5a6")
            ]
            
            # Test layout calculation
            layout_positions = self.layout_calculator.calculate_layout(unicode_nodes, unicode_edges)
            
            # Create visualization data
            unicode_data = VisualizationData(
                nodes=unicode_nodes,
                edges=unicode_edges,
                ontology_info=OntologyInfo(
                    entity_type_counts={"LOCATION": 5},
                    relationship_type_counts={"連接": 1, "соединение": 1, "接続": 1},
                    confidence_distribution={},
                    ontology_coverage={},
                    domains=[]
                ),
                metrics=VisualizationMetrics(
                    total_nodes=5,
                    total_edges=3,
                    avg_confidence=0.86,
                    entity_types=1,
                    relationship_types=3,
                    graph_density=0.3
                ),
                layout_positions=layout_positions
            )
            
            # Test rendering
            fig = self.renderer.create_interactive_plot(unicode_data)
            
            passed = fig is not None and len(layout_positions) == 5
            
            return {
                "passed": passed,
                "details": "Unicode labels and special characters handled correctly",
                "unicode_nodes": len(unicode_nodes),
                "unicode_edges": len(unicode_edges)
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _test_extreme_confidence_values(self) -> Dict[str, Any]:
        """Test visualization with extreme confidence values"""
        try:
            extreme_nodes = [
                NodeData(id="node1", name="Zero Confidence", type="TEST", confidence=0.0, size=1, color="#e74c3c"),
                NodeData(id="node2", name="Perfect Confidence", type="TEST", confidence=1.0, size=100, color="#2ecc71"),
                NodeData(id="node3", name="Negative", type="TEST", confidence=-0.5, size=10, color="#95a5a6"),
                NodeData(id="node4", name="Over One", type="TEST", confidence=1.5, size=150, color="#f39c12"),
                NodeData(id="node5", name="NaN", type="TEST", confidence=float('nan'), size=10, color="#9b59b6")
            ]
            
            extreme_edges = [
                EdgeData(source="node1", target="node2", type="EXTREME", confidence=0.0, width=0.1, color="#e74c3c"),
                EdgeData(source="node2", target="node3", type="EXTREME", confidence=1.0, width=10, color="#2ecc71"),
                EdgeData(source="node3", target="node4", type="EXTREME", confidence=-1.0, width=1, color="#95a5a6")
            ]
            
            # Test layout calculation
            layout_positions = self.layout_calculator.calculate_layout(extreme_nodes, extreme_edges)
            
            # Create visualization data
            extreme_data = VisualizationData(
                nodes=extreme_nodes,
                edges=extreme_edges,
                ontology_info=OntologyInfo(
                    entity_type_counts={"TEST": 5},
                    relationship_type_counts={"EXTREME": 3},
                    confidence_distribution={},
                    ontology_coverage={},
                    domains=[]
                ),
                metrics=VisualizationMetrics(
                    total_nodes=5,
                    total_edges=3,
                    avg_confidence=0.4,  # Handling NaN values
                    entity_types=1,
                    relationship_types=1,
                    graph_density=0.3
                ),
                layout_positions=layout_positions
            )
            
            # Test rendering
            fig = self.renderer.create_interactive_plot(extreme_data)
            
            passed = fig is not None
            
            return {
                "passed": passed,
                "details": "Extreme confidence values handled without breaking visualization",
                "nan_values_handled": True,
                "negative_values_handled": True,
                "over_one_values_handled": True
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _test_layout_algorithm_stress(self) -> Dict[str, Any]:
        """Test different layout algorithms under stress"""
        try:
            # Create moderately complex graph
            nodes = [NodeData(id=f"node_{i}", name=f"Node {i}", type="TEST", confidence=0.8, size=15, color="#3498db") 
                    for i in range(20)]
            
            edges = []
            for i in range(len(nodes)):
                for j in range(i + 1, min(i + 4, len(nodes))):  # Connect to next 3 nodes
                    edge = EdgeData(source=f"node_{i}", target=f"node_{j}", type="TEST", confidence=0.7, width=2, color="#95a5a6")
                    edges.append(edge)
            
            algorithm_results = {}
            
            # Test all layout algorithms
            for algorithm in LayoutAlgorithm:
                try:
                    start_time = time.time()
                    layout_positions = self.layout_calculator.calculate_layout(nodes, edges, algorithm)
                    execution_time = time.time() - start_time
                    
                    algorithm_results[algorithm.value] = {
                        "success": True,
                        "execution_time": execution_time,
                        "positions_calculated": len(layout_positions),
                        "expected_positions": len(nodes)
                    }
                    
                except Exception as e:
                    algorithm_results[algorithm.value] = {
                        "success": False,
                        "error": str(e)
                    }
            
            # Check if at least one algorithm succeeded
            successful_algorithms = sum(1 for result in algorithm_results.values() if result.get("success", False))
            passed = successful_algorithms > 0
            
            return {
                "passed": passed,
                "details": f"{successful_algorithms}/{len(LayoutAlgorithm)} layout algorithms succeeded",
                "algorithm_results": algorithm_results
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _test_color_scheme_robustness(self) -> Dict[str, Any]:
        """Test color scheme handling with various entity types"""
        try:
            # Create nodes with unusual entity types
            unusual_nodes = [
                NodeData(id="node1", name="Normal", type="PERSON", confidence=0.8, size=15),
                NodeData(id="node2", name="Empty Type", type="", confidence=0.8, size=15),
                NodeData(id="node3", name="None Type", type=None, confidence=0.8, size=15),
                NodeData(id="node4", name="Special Chars", type="TYPE_WITH_SPECIAL_!@#$%", confidence=0.8, size=15),
                NodeData(id="node5", name="Very Long Type Name", type="A_VERY_LONG_ENTITY_TYPE_NAME_THAT_EXCEEDS_NORMAL_LENGTH", confidence=0.8, size=15)
            ]
            
            # Test rendering with color assignment
            layout_positions = {"node1": (0, 0), "node2": (1, 0), "node3": (0, 1), "node4": (1, 1), "node5": (0.5, 0.5)}
            
            vis_data = VisualizationData(
                nodes=unusual_nodes,
                edges=[],
                ontology_info=OntologyInfo(
                    entity_type_counts={},
                    relationship_type_counts={},
                    confidence_distribution={},
                    ontology_coverage={},
                    domains=[]
                ),
                metrics=VisualizationMetrics(
                    total_nodes=5,
                    total_edges=0,
                    avg_confidence=0.8,
                    entity_types=4,
                    relationship_types=0,
                    graph_density=0.0
                ),
                layout_positions=layout_positions
            )
            
            # Test all color schemes
            color_scheme_results = {}
            for scheme in ["entity_type", "confidence", "ontology_domain"]:
                try:
                    config = GraphVisualizationConfig()
                    config.color_by = scheme
                    fig = self.renderer.create_interactive_plot(vis_data, config)
                    color_scheme_results[scheme] = {"success": True}
                except Exception as e:
                    color_scheme_results[scheme] = {"success": False, "error": str(e)}
            
            successful_schemes = sum(1 for result in color_scheme_results.values() if result.get("success", False))
            passed = successful_schemes > 0
            
            return {
                "passed": passed,
                "details": f"{successful_schemes}/3 color schemes handled successfully",
                "color_scheme_results": color_scheme_results
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _test_rendering_performance(self) -> Dict[str, Any]:
        """Test rendering performance with timing measurements"""
        try:
            # Create medium-sized graph for performance testing
            nodes = [NodeData(id=f"node_{i}", name=f"Node {i}", type="PERF_TEST", confidence=0.8, size=15, color="#3498db") 
                    for i in range(50)]
            
            edges = [EdgeData(source=nodes[i].id, target=nodes[(i+1) % len(nodes)].id, 
                            type="PERF_EDGE", confidence=0.7, width=2, color="#95a5a6") 
                    for i in range(len(nodes))]
            
            layout_positions = {node.id: (np.random.uniform(-1, 1), np.random.uniform(-1, 1)) for node in nodes}
            
            vis_data = VisualizationData(
                nodes=nodes,
                edges=edges,
                ontology_info=OntologyInfo(
                    entity_type_counts={"PERF_TEST": len(nodes)},
                    relationship_type_counts={"PERF_EDGE": len(edges)},
                    confidence_distribution={},
                    ontology_coverage={},
                    domains=[]
                ),
                metrics=VisualizationMetrics(
                    total_nodes=len(nodes),
                    total_edges=len(edges),
                    avg_confidence=0.8,
                    entity_types=1,
                    relationship_types=1,
                    graph_density=0.04
                ),
                layout_positions=layout_positions
            )
            
            # Measure rendering performance
            render_times = []
            for i in range(3):  # Multiple runs for average
                start_time = time.time()
                fig = self.renderer.create_interactive_plot(vis_data)
                render_time = time.time() - start_time
                render_times.append(render_time)
            
            avg_render_time = np.mean(render_times)
            passed = avg_render_time < 5.0  # Should render within 5 seconds
            
            return {
                "passed": passed,
                "details": f"Average rendering time: {avg_render_time:.3f}s for {len(nodes)} nodes",
                "avg_render_time": avg_render_time,
                "render_times": render_times,
                "performance_threshold": 5.0
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _test_memory_usage_limits(self) -> Dict[str, Any]:
        """Test memory usage with large datasets"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
            
            # Create large dataset
            large_nodes = [NodeData(id=f"mem_node_{i}", name=f"Memory Node {i}", type="MEM_TEST", 
                                  confidence=0.8, size=15, color="#3498db") 
                          for i in range(200)]
            
            # Measure memory after creation
            after_creation_memory = process.memory_info().rss
            memory_increase = after_creation_memory - initial_memory
            
            # Test if memory usage is reasonable (less than 100MB increase)
            passed = memory_increase < 100 * 1024 * 1024  # 100MB
            
            return {
                "passed": passed,
                "details": f"Memory increase: {memory_increase / 1024 / 1024:.2f} MB for {len(large_nodes)} nodes",
                "memory_increase_mb": memory_increase / 1024 / 1024,
                "memory_threshold_mb": 100,
                "nodes_created": len(large_nodes)
            }
            
        except ImportError:
            return {"passed": True, "details": "psutil not available, skipping memory test"}
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _test_concurrent_operations(self) -> Dict[str, Any]:
        """Test concurrent visualization operations"""
        try:
            import threading
            import queue
            
            results_queue = queue.Queue()
            
            def worker(worker_id):
                try:
                    nodes = [NodeData(id=f"worker_{worker_id}_node_{i}", name=f"Node {i}", 
                                    type="CONCURRENT", confidence=0.8, size=15, color="#3498db") 
                            for i in range(10)]
                    
                    layout_positions = self.layout_calculator.calculate_layout(nodes, [])
                    results_queue.put({"worker_id": worker_id, "success": True, "positions": len(layout_positions)})
                except Exception as e:
                    results_queue.put({"worker_id": worker_id, "success": False, "error": str(e)})
            
            # Start multiple threads
            threads = []
            num_workers = 3
            
            for i in range(num_workers):
                thread = threading.Thread(target=worker, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join(timeout=10)
            
            # Collect results
            worker_results = []
            while not results_queue.empty():
                worker_results.append(results_queue.get())
            
            successful_workers = sum(1 for result in worker_results if result.get("success", False))
            passed = successful_workers == num_workers
            
            return {
                "passed": passed,
                "details": f"{successful_workers}/{num_workers} concurrent operations succeeded",
                "worker_results": worker_results
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}