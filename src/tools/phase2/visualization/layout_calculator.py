"""Layout Calculator for Graph Visualization

Calculates various graph layout algorithms for visualization.
"""

import networkx as nx
import numpy as np
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from .visualization_data_models import LayoutType
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class LayoutCalculator:
    """Calculate graph layouts for visualization"""
    
    def __init__(self):
        self.layout_configs = {
            LayoutType.SPRING: {
                "iterations": 50,
                "k": None,  # Auto-calculated
                "pos": None
            },
            LayoutType.CIRCULAR: {
                "scale": 1.0
            },
            LayoutType.KAMADA_KAWAI: {
                "scale": 1.0,
                "center": None
            },
            LayoutType.FRUCHTERMAN_REINGOLD: {
                "iterations": 50,
                "threshold": 1e-4,
                "k": None
            },
            LayoutType.SPECTRAL: {
                "weight": "weight"
            },
            LayoutType.PLANAR: {
                "scale": 1.0
            },
            LayoutType.SHELL: {
                "nlist": None
            },
            LayoutType.SPIRAL: {
                "equidistant": False
            },
            LayoutType.RANDOM: {
                "center": None,
                "dim": 2
            }
        }
    
    def calculate_layout(self, graph: nx.Graph, layout_type: LayoutType) -> Dict[str, Any]:
        """Calculate node positions using specified layout algorithm"""
        try:
            if len(graph.nodes) == 0:
                return {"positions": {}, "layout_type": layout_type.value, "success": False}
            
            layout_config = self.layout_configs.get(layout_type, {})
            
            if layout_type == LayoutType.SPRING:
                pos = self._calculate_spring_layout(graph, layout_config)
            elif layout_type == LayoutType.CIRCULAR:
                pos = self._calculate_circular_layout(graph, layout_config)
            elif layout_type == LayoutType.KAMADA_KAWAI:
                pos = self._calculate_kamada_kawai_layout(graph, layout_config)
            elif layout_type == LayoutType.FRUCHTERMAN_REINGOLD:
                pos = self._calculate_fruchterman_reingold_layout(graph, layout_config)
            elif layout_type == LayoutType.SPECTRAL:
                pos = self._calculate_spectral_layout(graph, layout_config)
            elif layout_type == LayoutType.PLANAR:
                pos = self._calculate_planar_layout(graph, layout_config)
            elif layout_type == LayoutType.SHELL:
                pos = self._calculate_shell_layout(graph, layout_config)
            elif layout_type == LayoutType.SPIRAL:
                pos = self._calculate_spiral_layout(graph, layout_config)
            elif layout_type == LayoutType.RANDOM:
                pos = self._calculate_random_layout(graph, layout_config)
            else:
                logger.warning(f"Unknown layout type: {layout_type}. Using spring layout.")
                pos = self._calculate_spring_layout(graph, self.layout_configs[LayoutType.SPRING])
            
            if pos is None:
                logger.error(f"Failed to calculate {layout_type.value} layout")
                return {"positions": {}, "layout_type": layout_type.value, "success": False}
            
            # Convert positions to serializable format
            positions = {str(node): {"x": float(coords[0]), "y": float(coords[1])} 
                        for node, coords in pos.items()}
            
            # Calculate layout statistics
            layout_stats = self._calculate_layout_statistics(positions)
            
            return {
                "positions": positions,
                "layout_type": layout_type.value,
                "success": True,
                "statistics": layout_stats,
                "metadata": {
                    "algorithm": layout_type.value,
                    "node_count": len(positions),
                    "config": layout_config,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating {layout_type.value} layout: {e}")
            return {"positions": {}, "layout_type": layout_type.value, "success": False, "error": str(e)}
    
    def _calculate_spring_layout(self, graph: nx.Graph, config: Dict[str, Any]) -> Optional[Dict]:
        """Calculate spring layout (Fruchterman-Reingold)"""
        try:
            return nx.spring_layout(graph, 
                                   iterations=config.get("iterations", 50),
                                   k=config.get("k"),
                                   pos=config.get("pos"))
        except Exception as e:
            logger.error(f"Spring layout calculation failed: {e}")
            return None
    
    def _calculate_circular_layout(self, graph: nx.Graph, config: Dict[str, Any]) -> Optional[Dict]:
        """Calculate circular layout"""
        try:
            return nx.circular_layout(graph, scale=config.get("scale", 1.0))
        except Exception as e:
            logger.error(f"Circular layout calculation failed: {e}")
            return None
    
    def _calculate_kamada_kawai_layout(self, graph: nx.Graph, config: Dict[str, Any]) -> Optional[Dict]:
        """Calculate Kamada-Kawai layout"""
        try:
            if len(graph.nodes) < 2:
                return self._calculate_random_layout(graph, {})
            return nx.kamada_kawai_layout(graph, 
                                        scale=config.get("scale", 1.0),
                                        center=config.get("center"))
        except Exception as e:
            logger.warning(f"Kamada-Kawai layout failed, using spring layout: {e}")
            return self._calculate_spring_layout(graph, self.layout_configs[LayoutType.SPRING])
    
    def _calculate_fruchterman_reingold_layout(self, graph: nx.Graph, config: Dict[str, Any]) -> Optional[Dict]:
        """Calculate Fruchterman-Reingold layout"""
        try:
            return nx.fruchterman_reingold_layout(graph,
                                                iterations=config.get("iterations", 50),
                                                threshold=config.get("threshold", 1e-4),
                                                k=config.get("k"))
        except Exception as e:
            logger.error(f"Fruchterman-Reingold layout calculation failed: {e}")
            return None
    
    def _calculate_spectral_layout(self, graph: nx.Graph, config: Dict[str, Any]) -> Optional[Dict]:
        """Calculate spectral layout"""
        try:
            if len(graph.nodes) < 2:
                return self._calculate_random_layout(graph, {})
            return nx.spectral_layout(graph, weight=config.get("weight"))
        except Exception as e:
            logger.warning(f"Spectral layout failed, using spring layout: {e}")
            return self._calculate_spring_layout(graph, self.layout_configs[LayoutType.SPRING])
    
    def _calculate_planar_layout(self, graph: nx.Graph, config: Dict[str, Any]) -> Optional[Dict]:
        """Calculate planar layout (if graph is planar)"""
        try:
            if nx.is_planar(graph):
                return nx.planar_layout(graph, scale=config.get("scale", 1.0))
            else:
                logger.warning("Graph is not planar, using spring layout")
                return self._calculate_spring_layout(graph, self.layout_configs[LayoutType.SPRING])
        except Exception as e:
            logger.warning(f"Planar layout failed, using spring layout: {e}")
            return self._calculate_spring_layout(graph, self.layout_configs[LayoutType.SPRING])
    
    def _calculate_shell_layout(self, graph: nx.Graph, config: Dict[str, Any]) -> Optional[Dict]:
        """Calculate shell layout"""
        try:
            nlist = config.get("nlist")
            if nlist is None:
                # Create default shell arrangement based on degree
                degrees = dict(graph.degree())
                nodes_by_degree = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
                
                # Create shells based on degree quartiles
                n_nodes = len(nodes_by_degree)
                if n_nodes <= 4:
                    nlist = [[node for node, _ in nodes_by_degree]]
                else:
                    shell_size = max(1, n_nodes // 4)
                    nlist = []
                    for i in range(0, n_nodes, shell_size):
                        shell = [node for node, _ in nodes_by_degree[i:i+shell_size]]
                        if shell:
                            nlist.append(shell)
            
            return nx.shell_layout(graph, nlist=nlist)
        except Exception as e:
            logger.warning(f"Shell layout failed, using circular layout: {e}")
            return self._calculate_circular_layout(graph, self.layout_configs[LayoutType.CIRCULAR])
    
    def _calculate_spiral_layout(self, graph: nx.Graph, config: Dict[str, Any]) -> Optional[Dict]:
        """Calculate spiral layout"""
        try:
            # NetworkX doesn't have built-in spiral layout, so create custom one
            nodes = list(graph.nodes())
            n_nodes = len(nodes)
            
            if n_nodes == 0:
                return {}
            
            pos = {}
            equidistant = config.get("equidistant", False)
            
            for i, node in enumerate(nodes):
                if equidistant:
                    # Equal angular spacing
                    angle = 2 * np.pi * i / n_nodes
                    radius = 0.1 + (i / n_nodes) * 0.9
                else:
                    # Logarithmic spiral
                    angle = i * 0.5  # Spiral parameter
                    radius = 0.1 * np.exp(angle * 0.1)
                
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                pos[node] = (x, y)
            
            return pos
        except Exception as e:
            logger.error(f"Spiral layout calculation failed: {e}")
            return None
    
    def _calculate_random_layout(self, graph: nx.Graph, config: Dict[str, Any]) -> Optional[Dict]:
        """Calculate random layout"""
        try:
            return nx.random_layout(graph, 
                                  center=config.get("center"),
                                  dim=config.get("dim", 2))
        except Exception as e:
            logger.error(f"Random layout calculation failed: {e}")
            return None
    
    def _calculate_layout_statistics(self, positions: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Calculate statistics about the layout"""
        try:
            if not positions:
                return {}
            
            x_coords = [pos["x"] for pos in positions.values()]
            y_coords = [pos["y"] for pos in positions.values()]
            
            return {
                "bounds": {
                    "x_min": min(x_coords),
                    "x_max": max(x_coords),
                    "y_min": min(y_coords),
                    "y_max": max(y_coords)
                },
                "center": {
                    "x": np.mean(x_coords),
                    "y": np.mean(y_coords)
                },
                "spread": {
                    "x_std": np.std(x_coords),
                    "y_std": np.std(y_coords)
                },
                "node_count": len(positions)
            }
        except Exception as e:
            logger.error(f"Error calculating layout statistics: {e}")
            return {}