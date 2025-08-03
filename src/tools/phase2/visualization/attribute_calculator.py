"""Attribute Calculator for Graph Visualization

Calculates node and edge attributes for visualization styling.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from .visualization_data_models import ColorScheme
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class AttributeCalculator:
    """Calculate node and edge attributes for visualization"""
    
    def __init__(self):
        self.color_palettes = {
            ColorScheme.ENTITY_TYPE: px.colors.qualitative.Set1 if PLOTLY_AVAILABLE else [],
            ColorScheme.CONFIDENCE: px.colors.sequential.Viridis if PLOTLY_AVAILABLE else [],
            ColorScheme.CENTRALITY: px.colors.sequential.Plasma if PLOTLY_AVAILABLE else [],
            ColorScheme.COMMUNITY: px.colors.qualitative.Set3 if PLOTLY_AVAILABLE else [],
            ColorScheme.DEGREE: px.colors.sequential.Blues if PLOTLY_AVAILABLE else [],
            ColorScheme.PAGERANK: px.colors.sequential.Reds if PLOTLY_AVAILABLE else []
        }
    
    def calculate_node_attributes(self, graph: nx.Graph, size_metric: str) -> Dict[str, Any]:
        """Calculate node attributes for visualization"""
        try:
            node_attributes = {}
            
            # Calculate size values
            size_values = self._calculate_node_sizes(graph, size_metric)
            
            # Calculate positions (if not provided separately)
            positions = self._get_node_positions(graph)
            
            for node in graph.nodes():
                node_data = graph.nodes[node]
                
                attributes = {
                    "id": str(node),
                    "size": size_values.get(node, 10),
                    "label": str(node),
                    "entity_type": node_data.get("entity_type", "UNKNOWN"),
                    "confidence": node_data.get("confidence", 0.5),
                    "degree": graph.degree(node),
                    "properties": node_data
                }
                
                # Add position if available
                if node in positions:
                    attributes["x"] = positions[node][0]
                    attributes["y"] = positions[node][1]
                
                node_attributes[str(node)] = attributes
            
            return {
                "attributes": node_attributes,
                "size_metric": size_metric,
                "size_range": self._get_value_range(size_values),
                "statistics": self._calculate_node_statistics(node_attributes)
            }
            
        except Exception as e:
            logger.error(f"Error calculating node attributes: {e}")
            return {"attributes": {}, "size_metric": size_metric, "error": str(e)}
    
    def calculate_edge_attributes(self, graph: nx.Graph, width_metric: str) -> List[Dict[str, Any]]:
        """Calculate edge attributes for visualization"""
        try:
            edge_attributes = []
            
            # Calculate width values
            width_values = self._calculate_edge_widths(graph, width_metric)
            
            for source, target, edge_data in graph.edges(data=True):
                attributes = {
                    "source": str(source),
                    "target": str(target),
                    "width": width_values.get((source, target), 1.0),
                    "relationship_type": edge_data.get("relationship_type", "RELATED"),
                    "confidence": edge_data.get("confidence", 0.5),
                    "weight": edge_data.get("weight", 1.0),
                    "properties": edge_data
                }
                
                edge_attributes.append(attributes)
            
            return edge_attributes
            
        except Exception as e:
            logger.error(f"Error calculating edge attributes: {e}")
            return []
    
    def generate_color_mapping(self, graph: nx.Graph, color_scheme: ColorScheme, 
                             node_attributes: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate color mapping for nodes based on color scheme"""
        try:
            if color_scheme == ColorScheme.ENTITY_TYPE:
                return self._color_by_entity_type(graph)
            elif color_scheme == ColorScheme.CONFIDENCE:
                return self._color_by_confidence(graph)
            elif color_scheme == ColorScheme.CENTRALITY:
                return self._color_by_centrality(graph)
            elif color_scheme == ColorScheme.COMMUNITY:
                return self._color_by_community(graph)
            elif color_scheme == ColorScheme.DEGREE:
                return self._color_by_degree(graph)
            elif color_scheme == ColorScheme.PAGERANK:
                return self._color_by_pagerank(graph)
            else:
                # Default color scheme
                return self._color_by_entity_type(graph)
                
        except Exception as e:
            logger.error(f"Error generating color mapping: {e}")
            return {"colors": {}, "scheme": color_scheme.value, "error": str(e)}
    
    def _calculate_node_sizes(self, graph: nx.Graph, size_metric: str) -> Dict[str, float]:
        """Calculate node sizes based on specified metric"""
        try:
            if size_metric == "degree":
                values = dict(graph.degree())
            elif size_metric == "betweenness":
                values = nx.betweenness_centrality(graph)
            elif size_metric == "closeness":
                values = nx.closeness_centrality(graph)
            elif size_metric == "eigenvector":
                try:
                    values = nx.eigenvector_centrality(graph, max_iter=1000)
                except:
                    values = dict(graph.degree())  # Fallback
            elif size_metric == "pagerank":
                values = nx.pagerank(graph)
            elif size_metric == "confidence":
                values = {node: data.get("confidence", 0.5) 
                         for node, data in graph.nodes(data=True)}
            else:
                # Default to degree
                values = dict(graph.degree())
            
            # Normalize to reasonable size range (5-30)
            if values:
                min_val = min(values.values())
                max_val = max(values.values())
                if max_val > min_val:
                    normalized = {node: 5 + 25 * (val - min_val) / (max_val - min_val) 
                                for node, val in values.items()}
                else:
                    normalized = {node: 15 for node in values.keys()}
            else:
                normalized = {}
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error calculating node sizes: {e}")
            return {node: 10 for node in graph.nodes()}
    
    def _calculate_edge_widths(self, graph: nx.Graph, width_metric: str) -> Dict[tuple, float]:
        """Calculate edge widths based on specified metric"""
        try:
            if width_metric == "weight":
                values = {(u, v): data.get("weight", 1.0) 
                         for u, v, data in graph.edges(data=True)}
            elif width_metric == "confidence":
                values = {(u, v): data.get("confidence", 0.5) 
                         for u, v, data in graph.edges(data=True)}
            elif width_metric == "betweenness":
                edge_betweenness = nx.edge_betweenness_centrality(graph)
                values = edge_betweenness
            else:
                # Default to weight
                values = {(u, v): data.get("weight", 1.0) 
                         for u, v, data in graph.edges(data=True)}
            
            # Normalize to reasonable width range (0.5-5.0)
            if values:
                min_val = min(values.values())
                max_val = max(values.values())
                if max_val > min_val:
                    normalized = {edge: 0.5 + 4.5 * (val - min_val) / (max_val - min_val) 
                                for edge, val in values.items()}
                else:
                    normalized = {edge: 2.0 for edge in values.keys()}
            else:
                normalized = {}
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error calculating edge widths: {e}")
            return {(u, v): 1.0 for u, v in graph.edges()}
    
    def _get_node_positions(self, graph: nx.Graph) -> Dict[str, tuple]:
        """Get node positions if available in node data"""
        positions = {}
        for node, data in graph.nodes(data=True):
            if "x" in data and "y" in data:
                positions[node] = (data["x"], data["y"])
        return positions
    
    def _color_by_entity_type(self, graph: nx.Graph) -> Dict[str, Any]:
        """Color nodes by entity type"""
        try:
            entity_types = set()
            for node, data in graph.nodes(data=True):
                entity_type = data.get("entity_type", "UNKNOWN")
                entity_types.add(entity_type)
            
            entity_types = sorted(list(entity_types))
            color_palette = self.color_palettes.get(ColorScheme.ENTITY_TYPE, [])
            
            if color_palette:
                type_colors = {entity_type: color_palette[i % len(color_palette)] 
                              for i, entity_type in enumerate(entity_types)}
            else:
                # Fallback color generation
                type_colors = {entity_type: f"hsl({i * 360 / len(entity_types)}, 70%, 50%)" 
                              for i, entity_type in enumerate(entity_types)}
            
            node_colors = {str(node): type_colors.get(data.get("entity_type", "UNKNOWN"), "#gray") 
                          for node, data in graph.nodes(data=True)}
            
            return {
                "colors": node_colors,
                "scheme": "entity_type",
                "legend": type_colors,
                "categories": entity_types
            }
            
        except Exception as e:
            logger.error(f"Error coloring by entity type: {e}")
            return {"colors": {}, "scheme": "entity_type", "error": str(e)}
    
    def _color_by_confidence(self, graph: nx.Graph) -> Dict[str, Any]:
        """Color nodes by confidence score"""
        try:
            confidences = {node: data.get("confidence", 0.5) 
                          for node, data in graph.nodes(data=True)}
            
            color_palette = self.color_palettes.get(ColorScheme.CONFIDENCE, [])
            
            if color_palette:
                # Map confidence values to color palette
                min_conf = min(confidences.values())
                max_conf = max(confidences.values())
                
                if max_conf > min_conf:
                    node_colors = {}
                    for node, conf in confidences.items():
                        normalized = (conf - min_conf) / (max_conf - min_conf)
                        color_idx = int(normalized * (len(color_palette) - 1))
                        node_colors[str(node)] = color_palette[color_idx]
                else:
                    node_colors = {str(node): color_palette[0] for node in confidences.keys()}
            else:
                # Fallback: grayscale based on confidence
                node_colors = {str(node): f"rgb({int(conf * 255)}, {int(conf * 255)}, {int(conf * 255)})" 
                              for node, conf in confidences.items()}
            
            return {
                "colors": node_colors,
                "scheme": "confidence",
                "range": [min(confidences.values()), max(confidences.values())],
                "palette": color_palette[:10] if color_palette else []
            }
            
        except Exception as e:
            logger.error(f"Error coloring by confidence: {e}")
            return {"colors": {}, "scheme": "confidence", "error": str(e)}
    
    def _color_by_centrality(self, graph: nx.Graph) -> Dict[str, Any]:
        """Color nodes by betweenness centrality"""
        try:
            centralities = nx.betweenness_centrality(graph)
            color_palette = self.color_palettes.get(ColorScheme.CENTRALITY, [])
            
            if color_palette and centralities:
                min_cent = min(centralities.values())
                max_cent = max(centralities.values())
                
                if max_cent > min_cent:
                    node_colors = {}
                    for node, cent in centralities.items():
                        normalized = (cent - min_cent) / (max_cent - min_cent)
                        color_idx = int(normalized * (len(color_palette) - 1))
                        node_colors[str(node)] = color_palette[color_idx]
                else:
                    node_colors = {str(node): color_palette[0] for node in centralities.keys()}
            else:
                # Fallback
                node_colors = {str(node): "#gray" for node in graph.nodes()}
            
            return {
                "colors": node_colors,
                "scheme": "centrality",
                "values": centralities,
                "range": [min(centralities.values()), max(centralities.values())] if centralities else [0, 0]
            }
            
        except Exception as e:
            logger.error(f"Error coloring by centrality: {e}")
            return {"colors": {}, "scheme": "centrality", "error": str(e)}
    
    def _color_by_community(self, graph: nx.Graph) -> Dict[str, Any]:
        """Color nodes by community detection"""
        try:
            communities = nx.community.louvain_communities(graph)
            color_palette = self.color_palettes.get(ColorScheme.COMMUNITY, [])
            
            # Create node to community mapping
            node_community = {}
            for i, community in enumerate(communities):
                for node in community:
                    node_community[node] = i
            
            # Assign colors
            if color_palette:
                node_colors = {str(node): color_palette[comm_id % len(color_palette)] 
                              for node, comm_id in node_community.items()}
            else:
                # Fallback color generation
                num_communities = len(communities)
                node_colors = {str(node): f"hsl({comm_id * 360 / num_communities}, 70%, 50%)" 
                              for node, comm_id in node_community.items()}
            
            return {
                "colors": node_colors,
                "scheme": "community",
                "communities": len(communities),
                "community_sizes": [len(comm) for comm in communities]
            }
            
        except Exception as e:
            logger.error(f"Error coloring by community: {e}")
            return {"colors": {}, "scheme": "community", "error": str(e)}
    
    def _color_by_degree(self, graph: nx.Graph) -> Dict[str, Any]:
        """Color nodes by degree"""
        try:
            degrees = dict(graph.degree())
            color_palette = self.color_palettes.get(ColorScheme.DEGREE, [])
            
            if color_palette and degrees:
                min_deg = min(degrees.values())
                max_deg = max(degrees.values())
                
                if max_deg > min_deg:
                    node_colors = {}
                    for node, deg in degrees.items():
                        normalized = (deg - min_deg) / (max_deg - min_deg)
                        color_idx = int(normalized * (len(color_palette) - 1))
                        node_colors[str(node)] = color_palette[color_idx]
                else:
                    node_colors = {str(node): color_palette[0] for node in degrees.keys()}
            else:
                # Fallback
                node_colors = {str(node): "#gray" for node in graph.nodes()}
            
            return {
                "colors": node_colors,
                "scheme": "degree",
                "values": degrees,
                "range": [min(degrees.values()), max(degrees.values())] if degrees else [0, 0]
            }
            
        except Exception as e:
            logger.error(f"Error coloring by degree: {e}")
            return {"colors": {}, "scheme": "degree", "error": str(e)}
    
    def _color_by_pagerank(self, graph: nx.Graph) -> Dict[str, Any]:
        """Color nodes by PageRank scores"""
        try:
            pagerank_scores = nx.pagerank(graph)
            color_palette = self.color_palettes.get(ColorScheme.PAGERANK, [])
            
            if color_palette and pagerank_scores:
                min_pr = min(pagerank_scores.values())
                max_pr = max(pagerank_scores.values())
                
                if max_pr > min_pr:
                    node_colors = {}
                    for node, pr in pagerank_scores.items():
                        normalized = (pr - min_pr) / (max_pr - min_pr)
                        color_idx = int(normalized * (len(color_palette) - 1))
                        node_colors[str(node)] = color_palette[color_idx]
                else:
                    node_colors = {str(node): color_palette[0] for node in pagerank_scores.keys()}
            else:
                # Fallback
                node_colors = {str(node): "#gray" for node in graph.nodes()}
            
            return {
                "colors": node_colors,
                "scheme": "pagerank",
                "values": pagerank_scores,
                "range": [min(pagerank_scores.values()), max(pagerank_scores.values())] if pagerank_scores else [0, 0]
            }
            
        except Exception as e:
            logger.error(f"Error coloring by PageRank: {e}")
            return {"colors": {}, "scheme": "pagerank", "error": str(e)}
    
    def _get_value_range(self, values: Dict) -> Dict[str, float]:
        """Get min/max range of values"""
        if not values:
            return {"min": 0, "max": 0}
        
        vals = list(values.values()) 
        return {"min": min(vals), "max": max(vals)}
    
    def _calculate_node_statistics(self, node_attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistics about node attributes"""
        try:
            if not node_attributes:
                return {}
            
            sizes = [attr.get("size", 10) for attr in node_attributes.values()]
            confidences = [attr.get("confidence", 0.5) for attr in node_attributes.values()]
            degrees = [attr.get("degree", 0) for attr in node_attributes.values()]
            
            entity_types = {}
            for attr in node_attributes.values():
                entity_type = attr.get("entity_type", "UNKNOWN")
                entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
            
            return {
                "total_nodes": len(node_attributes),
                "size_stats": {
                    "min": min(sizes),
                    "max": max(sizes),
                    "mean": np.mean(sizes),
                    "std": np.std(sizes)
                },
                "confidence_stats": {
                    "min": min(confidences),
                    "max": max(confidences),
                    "mean": np.mean(confidences),
                    "std": np.std(confidences)
                },
                "degree_stats": {
                    "min": min(degrees),
                    "max": max(degrees),
                    "mean": np.mean(degrees),
                    "std": np.std(degrees)
                },
                "entity_type_distribution": entity_types
            }
            
        except Exception as e:
            logger.error(f"Error calculating node statistics: {e}")
            return {}