"""
Graph Layout Calculator

Calculates node positions for graph visualization using various layout algorithms.
"""

import logging
import numpy as np
import networkx as nx
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .visualization_data_models import (
    NodeData, EdgeData, LayoutAlgorithm, LayoutQualityMetrics
)

logger = logging.getLogger(__name__)


class GraphLayoutCalculator:
    """Calculate layout positions for graph visualization nodes"""
    
    def __init__(self):
        """Initialize layout calculator"""
        self.layout_cache = {}
        self.quality_metrics = {}
    
    def calculate_layout(self, nodes: List[NodeData], edges: List[EdgeData], 
                        algorithm: LayoutAlgorithm = LayoutAlgorithm.SPRING,
                        **kwargs) -> Dict[str, Tuple[float, float]]:
        """
        Calculate layout positions for nodes using specified algorithm.
        
        Args:
            nodes: List of node data
            edges: List of edge data
            algorithm: Layout algorithm to use
            **kwargs: Additional algorithm-specific parameters
            
        Returns:
            Dictionary mapping node IDs to (x, y) positions
        """
        if not nodes:
            return {}
        
        try:
            # Create NetworkX graph
            graph = self._create_networkx_graph(nodes, edges)
            
            # Calculate positions based on algorithm
            if algorithm == LayoutAlgorithm.SPRING:
                positions = self._spring_layout(graph, **kwargs)
            elif algorithm == LayoutAlgorithm.CIRCULAR:
                positions = self._circular_layout(graph, **kwargs)
            elif algorithm == LayoutAlgorithm.KAMADA_KAWAI:
                positions = self._kamada_kawai_layout(graph, **kwargs)
            else:
                logger.warning(f"Unknown layout algorithm: {algorithm}, using spring layout")
                positions = self._spring_layout(graph, **kwargs)
            
            # Calculate layout quality metrics
            quality_metrics = self._calculate_layout_quality(graph, positions)
            self.quality_metrics[algorithm.value] = quality_metrics
            
            # Convert positions to required format
            layout_positions = {
                node_id: (float(coords[0]), float(coords[1])) 
                for node_id, coords in positions.items()
            }
            
            logger.info(f"Calculated {algorithm.value} layout for {len(nodes)} nodes")
            return layout_positions
            
        except Exception as e:
            logger.error(f"Layout calculation failed: {e}")
            return self._fallback_layout(nodes)
    
    def _create_networkx_graph(self, nodes: List[NodeData], edges: List[EdgeData]) -> nx.Graph:
        """Create NetworkX graph from node and edge data"""
        graph = nx.Graph()
        
        # Add nodes with attributes
        for node in nodes:
            if node.id:  # Filter out None ids
                graph.add_node(node.id, 
                             name=node.name,
                             type=node.type,
                             confidence=node.confidence,
                             size=node.size or 10)
        
        # Add edges with attributes
        for edge in edges:
            source_id = edge.source
            target_id = edge.target
            
            # Only add edges between existing nodes
            if (source_id and target_id and 
                graph.has_node(source_id) and graph.has_node(target_id)):
                graph.add_edge(source_id, target_id,
                             type=edge.type,
                             confidence=edge.confidence,
                             weight=edge.confidence)  # Use confidence as edge weight
        
        logger.debug(f"Created NetworkX graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
        return graph
    
    def _spring_layout(self, graph: nx.Graph, **kwargs) -> Dict[str, Tuple[float, float]]:
        """Calculate spring layout positions"""
        # Extract parameters with defaults
        k = kwargs.get('k', 1.0)  # Optimal distance between nodes
        iterations = kwargs.get('iterations', 50)
        threshold = kwargs.get('threshold', 1e-4)
        weight = kwargs.get('weight', 'weight')
        scale = kwargs.get('scale', 1.0)
        center = kwargs.get('center', None)
        dim = kwargs.get('dim', 2)
        
        try:
            pos = nx.spring_layout(
                graph,
                k=k,
                iterations=iterations,
                threshold=threshold,
                weight=weight,
                scale=scale,
                center=center,
                dim=dim,
                seed=42  # For reproducible layouts
            )
            return pos
        except Exception as e:
            logger.warning(f"Spring layout failed: {e}, using fallback")
            return self._simple_circular_layout(graph)
    
    def _circular_layout(self, graph: nx.Graph, **kwargs) -> Dict[str, Tuple[float, float]]:
        """Calculate circular layout positions"""
        scale = kwargs.get('scale', 1.0)
        center = kwargs.get('center', None)
        
        try:
            pos = nx.circular_layout(graph, scale=scale, center=center)
            return pos
        except Exception as e:
            logger.warning(f"Circular layout failed: {e}, using fallback")
            return self._simple_circular_layout(graph)
    
    def _kamada_kawai_layout(self, graph: nx.Graph, **kwargs) -> Dict[str, Tuple[float, float]]:
        """Calculate Kamada-Kawai layout positions"""
        dist = kwargs.get('dist', None)
        pos = kwargs.get('pos', None)
        weight = kwargs.get('weight', 'weight')
        scale = kwargs.get('scale', 1.0)
        center = kwargs.get('center', None)
        
        try:
            # Only use Kamada-Kawai for connected graphs
            if nx.is_connected(graph):
                pos = nx.kamada_kawai_layout(
                    graph,
                    dist=dist,
                    pos=pos,
                    weight=weight,
                    scale=scale,
                    center=center
                )
                return pos
            else:
                logger.info("Graph not connected, using spring layout instead of Kamada-Kawai")
                return self._spring_layout(graph, **kwargs)
                
        except Exception as e:
            logger.warning(f"Kamada-Kawai layout failed: {e}, using spring layout")
            return self._spring_layout(graph, **kwargs)
    
    def _simple_circular_layout(self, graph: nx.Graph) -> Dict[str, Tuple[float, float]]:
        """Simple circular layout as fallback"""
        nodes = list(graph.nodes())
        if not nodes:
            return {}
        
        positions = {}
        n = len(nodes)
        
        for i, node_id in enumerate(nodes):
            angle = 2 * np.pi * i / n
            x = np.cos(angle)
            y = np.sin(angle)
            positions[node_id] = (x, y)
        
        return positions
    
    def _fallback_layout(self, nodes: List[NodeData]) -> Dict[str, Tuple[float, float]]:
        """Fallback layout when all algorithms fail"""
        valid_nodes = [node for node in nodes if node.id]
        if not valid_nodes:
            return {}
        
        positions = {}
        n = len(valid_nodes)
        
        for i, node in enumerate(valid_nodes):
            # Simple grid layout
            cols = int(np.ceil(np.sqrt(n)))
            row = i // cols
            col = i % cols
            
            x = col * 2.0 - cols
            y = row * 2.0 - (n // cols)
            
            positions[node.id] = (float(x), float(y))
        
        logger.info(f"Used fallback grid layout for {len(valid_nodes)} nodes")
        return positions
    
    def _calculate_layout_quality(self, graph: nx.Graph, 
                                 positions: Dict[str, Tuple[float, float]]) -> LayoutQualityMetrics:
        """Calculate quality metrics for layout"""
        try:
            # Edge crossing count (simplified estimation)
            edge_crossing_count = self._estimate_edge_crossings(graph, positions)
            
            # Node overlap count
            node_overlap_count = self._count_node_overlaps(positions)
            
            # Edge length variance
            edge_length_variance = self._calculate_edge_length_variance(graph, positions)
            
            # Angular resolution (average minimum angle between edges)
            angular_resolution = self._calculate_angular_resolution(graph, positions)
            
            # Aspect ratio of bounding box
            aspect_ratio = self._calculate_aspect_ratio(positions)
            
            # Node distribution uniformity
            node_distribution_uniformity = self._calculate_distribution_uniformity(positions)
            
            return LayoutQualityMetrics(
                edge_crossing_count=edge_crossing_count,
                node_overlap_count=node_overlap_count,
                edge_length_variance=edge_length_variance,
                angular_resolution=angular_resolution,
                aspect_ratio=aspect_ratio,
                node_distribution_uniformity=node_distribution_uniformity
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate layout quality: {e}")
            return LayoutQualityMetrics(
                edge_crossing_count=0,
                node_overlap_count=0,
                edge_length_variance=0.0,
                angular_resolution=0.0,
                aspect_ratio=1.0,
                node_distribution_uniformity=0.0
            )
    
    def _estimate_edge_crossings(self, graph: nx.Graph, 
                                positions: Dict[str, Tuple[float, float]]) -> int:
        """Estimate number of edge crossings (simplified)"""
        edges = list(graph.edges())
        crossings = 0
        
        # Compare each pair of edges for intersections
        for i, (u1, v1) in enumerate(edges):
            if u1 not in positions or v1 not in positions:
                continue
                
            for j, (u2, v2) in enumerate(edges[i+1:], i+1):
                if u2 not in positions or v2 not in positions:
                    continue
                
                # Skip if edges share a node
                if u1 in (u2, v2) or v1 in (u2, v2):
                    continue
                
                # Check if line segments intersect
                if self._lines_intersect(positions[u1], positions[v1], 
                                       positions[u2], positions[v2]):
                    crossings += 1
        
        return crossings
    
    def _lines_intersect(self, p1: Tuple[float, float], p2: Tuple[float, float],
                        p3: Tuple[float, float], p4: Tuple[float, float]) -> bool:
        """Check if two line segments intersect"""
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
        
        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)
    
    def _count_node_overlaps(self, positions: Dict[str, Tuple[float, float]], 
                           min_distance: float = 0.1) -> int:
        """Count nodes that are too close together"""
        pos_list = list(positions.values())
        overlaps = 0
        
        for i, (x1, y1) in enumerate(pos_list):
            for x2, y2 in pos_list[i+1:]:
                distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                if distance < min_distance:
                    overlaps += 1
        
        return overlaps
    
    def _calculate_edge_length_variance(self, graph: nx.Graph,
                                      positions: Dict[str, Tuple[float, float]]) -> float:
        """Calculate variance in edge lengths"""
        edge_lengths = []
        
        for u, v in graph.edges():
            if u in positions and v in positions:
                x1, y1 = positions[u]
                x2, y2 = positions[v]
                length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                edge_lengths.append(length)
        
        if not edge_lengths:
            return 0.0
        
        return float(np.var(edge_lengths))
    
    def _calculate_angular_resolution(self, graph: nx.Graph,
                                    positions: Dict[str, Tuple[float, float]]) -> float:
        """Calculate average angular resolution between edges"""
        total_min_angles = []
        
        for node in graph.nodes():
            if node not in positions:
                continue
                
            neighbors = list(graph.neighbors(node))
            if len(neighbors) < 2:
                continue
            
            # Calculate angles between all pairs of edges from this node
            angles = []
            node_pos = positions[node]
            
            for neighbor in neighbors:
                if neighbor in positions:
                    neighbor_pos = positions[neighbor]
                    angle = np.arctan2(neighbor_pos[1] - node_pos[1],
                                     neighbor_pos[0] - node_pos[0])
                    angles.append(angle)
            
            if len(angles) >= 2:
                # Sort angles and find minimum angle between adjacent edges
                angles.sort()
                min_angle = 2 * np.pi
                
                for i in range(len(angles)):
                    next_i = (i + 1) % len(angles)
                    angle_diff = abs(angles[next_i] - angles[i])
                    if angle_diff > np.pi:
                        angle_diff = 2 * np.pi - angle_diff
                    min_angle = min(min_angle, angle_diff)
                
                total_min_angles.append(min_angle)
        
        if not total_min_angles:
            return 0.0
        
        # Normalize to 0-1 scale (higher is better)
        avg_min_angle = np.mean(total_min_angles)
        return float(avg_min_angle / (np.pi / 3))  # Normalize by 60 degrees
    
    def _calculate_aspect_ratio(self, positions: Dict[str, Tuple[float, float]]) -> float:
        """Calculate aspect ratio of layout bounding box"""
        if not positions:
            return 1.0
        
        pos_list = list(positions.values())
        x_coords = [pos[0] for pos in pos_list]
        y_coords = [pos[1] for pos in pos_list]
        
        x_range = max(x_coords) - min(x_coords)
        y_range = max(y_coords) - min(y_coords)
        
        if y_range == 0:
            return float('inf') if x_range > 0 else 1.0
        
        return float(x_range / y_range)
    
    def _calculate_distribution_uniformity(self, positions: Dict[str, Tuple[float, float]]) -> float:
        """Calculate uniformity of node distribution"""
        if len(positions) < 3:
            return 1.0
        
        pos_list = list(positions.values())
        
        # Calculate pairwise distances
        distances = []
        for i, pos1 in enumerate(pos_list):
            for pos2 in pos_list[i+1:]:
                dist = np.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)
                distances.append(dist)
        
        if not distances:
            return 1.0
        
        # Uniformity is inverse of coefficient of variation
        mean_dist = np.mean(distances)
        std_dist = np.std(distances)
        
        if mean_dist == 0:
            return 1.0
        
        cv = std_dist / mean_dist
        uniformity = 1.0 / (1.0 + cv)  # Higher values = more uniform
        
        return float(uniformity)
    
    def get_layout_quality_report(self, algorithm: LayoutAlgorithm) -> Dict[str, Any]:
        """Get quality report for a layout algorithm"""
        if algorithm.value not in self.quality_metrics:
            return {"error": "No quality metrics available for this algorithm"}
        
        metrics = self.quality_metrics[algorithm.value]
        overall_quality = metrics.calculate_overall_quality()
        
        return {
            "algorithm": algorithm.value,
            "overall_quality": overall_quality,
            "metrics": {
                "edge_crossings": metrics.edge_crossing_count,
                "node_overlaps": metrics.node_overlap_count,
                "edge_length_variance": metrics.edge_length_variance,
                "angular_resolution": metrics.angular_resolution,
                "aspect_ratio": metrics.aspect_ratio,
                "distribution_uniformity": metrics.node_distribution_uniformity
            },
            "quality_assessment": self._assess_quality(overall_quality)
        }
    
    def _assess_quality(self, quality_score: float) -> str:
        """Assess layout quality based on score"""
        if quality_score >= 0.8:
            return "Excellent"
        elif quality_score >= 0.6:
            return "Good"
        elif quality_score >= 0.4:
            return "Fair"
        else:
            return "Poor"
    
    def compare_layouts(self, nodes: List[NodeData], edges: List[EdgeData]) -> Dict[str, Any]:
        """Compare quality of different layout algorithms"""
        algorithms = [LayoutAlgorithm.SPRING, LayoutAlgorithm.CIRCULAR, LayoutAlgorithm.KAMADA_KAWAI]
        comparison = {}
        
        for algorithm in algorithms:
            try:
                # Calculate layout
                self.calculate_layout(nodes, edges, algorithm)
                
                # Get quality report
                quality_report = self.get_layout_quality_report(algorithm)
                comparison[algorithm.value] = quality_report
                
            except Exception as e:
                comparison[algorithm.value] = {"error": str(e)}
        
        # Find best algorithm
        best_algorithm = None
        best_quality = -1
        
        for alg, report in comparison.items():
            if "overall_quality" in report and report["overall_quality"] > best_quality:
                best_quality = report["overall_quality"]
                best_algorithm = alg
        
        comparison["recommendation"] = {
            "best_algorithm": best_algorithm,
            "best_quality": best_quality,
            "comparison_timestamp": datetime.now().isoformat()
        }
        
        return comparison