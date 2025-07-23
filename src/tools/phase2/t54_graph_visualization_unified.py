"""T54: Graph Visualization Tool - Advanced Graph Analytics

Real graph visualization using Plotly and NetworkX with advanced layouts and interactivity.
Part of Phase 2.1 Graph Analytics tools providing advanced network visualization capabilities.
"""

import time
import psutil
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
import networkx as nx
import numpy as np
from dataclasses import dataclass
from enum import Enum
import json
import tempfile
import os

# Import base tool
from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract

# Import core services
try:
    from src.core.service_manager import ServiceManager
    from src.core.confidence_score import ConfidenceScore
except ImportError:
    from core.service_manager import ServiceManager
    from core.confidence_score import ConfidenceScore

# Import Neo4j integration
from src.tools.phase1.base_neo4j_tool import BaseNeo4jTool
from src.tools.phase1.neo4j_error_handler import Neo4jErrorHandler

# Import visualization libraries
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class LayoutType(Enum):
    """Supported graph layout algorithms"""
    SPRING = "spring"
    CIRCULAR = "circular"
    KAMADA_KAWAI = "kamada_kawai"
    FRUCHTERMAN_REINGOLD = "fruchterman_reingold"
    SPECTRAL = "spectral"
    PLANAR = "planar"
    SHELL = "shell"
    SPIRAL = "spiral"
    RANDOM = "random"


class ColorScheme(Enum):
    """Supported color schemes for visualization"""
    ENTITY_TYPE = "entity_type"
    CONFIDENCE = "confidence"
    CENTRALITY = "centrality"
    COMMUNITY = "community"
    DEGREE = "degree"
    PAGERANK = "pagerank"
    CUSTOM = "custom"


@dataclass
class VisualizationConfig:
    """Configuration for graph visualization"""
    layout: LayoutType
    color_scheme: ColorScheme
    max_nodes: int
    max_edges: int
    node_size_metric: str
    edge_width_metric: str
    show_labels: bool
    interactive: bool
    output_format: str


@dataclass
class VisualizationResult:
    """Result of graph visualization"""
    visualization_data: Dict[str, Any]
    layout_info: Dict[str, Any]
    statistics: Dict[str, Any]
    file_paths: List[str]
    metadata: Dict[str, Any]


class GraphVisualizationTool(BaseTool):
    """T54: Advanced Graph Visualization Tool
    
    Implements real graph visualization using Plotly with advanced layouts,
    interactive features, and multiple output formats for academic research.
    """
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize graph visualization tool with advanced capabilities"""
        if service_manager is None:
            service_manager = ServiceManager()
        
        super().__init__(service_manager)
        self.tool_id = "T54_GRAPH_VISUALIZATION"
        self.name = "Advanced Graph Visualization"
        self.category = "advanced_analytics"
        self.requires_large_data = True
        self.supports_batch_processing = True
        self.academic_output_ready = True
        
        # Initialize Neo4j connection for graph data
        self.neo4j_tool = None
        self._initialize_neo4j_connection()
        
        # Visualization configurations
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
        
        # Color palettes for different schemes
        self.color_palettes = {
            ColorScheme.ENTITY_TYPE: px.colors.qualitative.Set1,
            ColorScheme.CONFIDENCE: px.colors.sequential.Viridis,
            ColorScheme.CENTRALITY: px.colors.sequential.Plasma,
            ColorScheme.COMMUNITY: px.colors.qualitative.Set3,
            ColorScheme.DEGREE: px.colors.sequential.Blues,
            ColorScheme.PAGERANK: px.colors.sequential.Reds
        }
        
        # Check dependencies
        self.plotly_available = PLOTLY_AVAILABLE
        if not self.plotly_available:
            print("Warning: Plotly not available. Visualization features will be limited.")
    
    def _initialize_neo4j_connection(self):
        """Initialize Neo4j connection for graph data access"""
        try:
            self.neo4j_tool = BaseNeo4jTool()
        except Exception as e:
            print(f"Warning: Could not initialize Neo4j connection: {e}")
            self.neo4j_tool = None
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification"""
        return ToolContract(
            tool_id=self.tool_id,
            name=self.name,
            description="Advanced graph visualization with interactive layouts and multiple output formats",
            category=self.category,
            input_schema={
                "type": "object",
                "properties": {
                    "graph_source": {
                        "type": "string",
                        "enum": ["neo4j", "networkx", "edge_list", "adjacency_matrix"],
                        "description": "Source of graph data"
                    },
                    "graph_data": {
                        "type": "object",
                        "description": "Graph data when not using Neo4j"
                    },
                    "layout": {
                        "type": "string",
                        "enum": ["spring", "circular", "kamada_kawai", "fruchterman_reingold", 
                               "spectral", "planar", "shell", "spiral", "random"],
                        "default": "spring"
                    },
                    "color_scheme": {
                        "type": "string",
                        "enum": ["entity_type", "confidence", "centrality", "community", 
                               "degree", "pagerank", "custom"],
                        "default": "entity_type"
                    },
                    "max_nodes": {
                        "type": "integer",
                        "minimum": 10,
                        "maximum": 10000,
                        "default": 1000
                    },
                    "max_edges": {
                        "type": "integer",
                        "minimum": 10,
                        "maximum": 50000,
                        "default": 5000
                    },
                    "node_size_metric": {
                        "type": "string",
                        "enum": ["degree", "pagerank", "centrality", "confidence", "uniform"],
                        "default": "degree"
                    },
                    "edge_width_metric": {
                        "type": "string",
                        "enum": ["weight", "confidence", "uniform"],
                        "default": "weight"
                    },
                    "show_labels": {
                        "type": "boolean",
                        "default": True
                    },
                    "interactive": {
                        "type": "boolean",
                        "default": True
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["html", "json", "png", "svg", "pdf", "all"],
                        "default": "html"
                    },
                    "custom_colors": {
                        "type": "object",
                        "description": "Custom color mapping for nodes/edges"
                    },
                    "filter_criteria": {
                        "type": "object",
                        "properties": {
                            "min_degree": {"type": "integer", "minimum": 0},
                            "min_confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                            "entity_types": {"type": "array", "items": {"type": "string"}},
                            "communities": {"type": "array", "items": {"type": "integer"}}
                        }
                    },
                    "save_to_file": {
                        "type": "boolean",
                        "default": True
                    }
                },
                "required": ["graph_source"],
                "additionalProperties": False
            },
            output_schema={
                "type": "object",
                "properties": {
                    "visualization_data": {
                        "type": "object",
                        "properties": {
                            "plotly_figure": {"type": "object"},
                            "node_positions": {"type": "object"},
                            "edge_data": {"type": "array"},
                            "color_mapping": {"type": "object"}
                        }
                    },
                    "layout_info": {
                        "type": "object",
                        "properties": {
                            "layout_type": {"type": "string"},
                            "parameters": {"type": "object"},
                            "computation_time": {"type": "number"},
                            "node_count": {"type": "integer"},
                            "edge_count": {"type": "integer"}
                        }
                    },
                    "statistics": {
                        "type": "object",
                        "properties": {
                            "graph_metrics": {"type": "object"},
                            "layout_quality": {"type": "object"},
                            "color_distribution": {"type": "object"},
                            "performance_metrics": {"type": "object"}
                        }
                    },
                    "file_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Paths to generated visualization files"
                    }
                },
                "required": ["visualization_data", "layout_info", "statistics", "file_paths"]
            },
            dependencies=["networkx", "plotly", "numpy", "neo4j_service"],
            performance_requirements={
                "max_execution_time": 300.0,  # 5 minutes for large visualizations
                "max_memory_mb": 8000,  # 8GB for large graphs
                "min_accuracy": 0.95  # Layout quality
            },
            error_conditions=[
                "INVALID_GRAPH_DATA",
                "LAYOUT_NOT_SUPPORTED",
                "GRAPH_TOO_LARGE",
                "VISUALIZATION_FAILED",
                "NEO4J_CONNECTION_ERROR",
                "INSUFFICIENT_NODES",
                "MEMORY_LIMIT_EXCEEDED",
                "PLOTLY_NOT_AVAILABLE",
                "FILE_WRITE_ERROR"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute graph visualization with real algorithms"""
        self._start_execution()
        
        try:
            # Check Plotly availability
            if not self.plotly_available:
                return self._create_error_result(
                    request, "PLOTLY_NOT_AVAILABLE", 
                    "Plotly library not available. Install with: pip install plotly"
                )
            
            # Validate input against contract
            validation_result = self._validate_advanced_input(request.input_data)
            if not validation_result["valid"]:
                return self._create_error_result(request, "INVALID_INPUT", validation_result["error"])
            
            # Extract parameters
            graph_source = request.input_data["graph_source"]
            layout = LayoutType(request.input_data.get("layout", "spring"))
            color_scheme = ColorScheme(request.input_data.get("color_scheme", "entity_type"))
            max_nodes = request.input_data.get("max_nodes", 1000)
            max_edges = request.input_data.get("max_edges", 5000)
            node_size_metric = request.input_data.get("node_size_metric", "degree")
            edge_width_metric = request.input_data.get("edge_width_metric", "weight")
            show_labels = request.input_data.get("show_labels", True)
            interactive = request.input_data.get("interactive", True)
            output_format = request.input_data.get("output_format", "html")
            custom_colors = request.input_data.get("custom_colors", {})
            filter_criteria = request.input_data.get("filter_criteria", {})
            save_to_file = request.input_data.get("save_to_file", True)
            
            # Load graph data
            graph = self._load_graph_data(graph_source, request.input_data.get("graph_data"))
            if graph is None:
                return self._create_error_result(request, "INVALID_GRAPH_DATA", "Failed to load graph data")
            
            # Validate graph size
            if len(graph.nodes()) < 1:
                return self._create_error_result(request, "INSUFFICIENT_NODES", "Graph must have at least 1 node")
            
            if len(graph.nodes()) > max_nodes:
                return self._create_error_result(
                    request, "GRAPH_TOO_LARGE", 
                    f"Graph has {len(graph.nodes())} nodes, exceeding maximum of {max_nodes}"
                )
            
            # Apply filters
            filtered_graph = self._apply_filters(graph, filter_criteria)
            
            # Calculate layout
            layout_data = self._calculate_layout(filtered_graph, layout)
            
            # Calculate node attributes
            node_attributes = self._calculate_node_attributes(filtered_graph, node_size_metric)
            
            # Calculate edge attributes
            edge_attributes = self._calculate_edge_attributes(filtered_graph, edge_width_metric)
            
            # Generate colors
            color_mapping = self._generate_color_mapping(
                filtered_graph, color_scheme, custom_colors, node_attributes
            )
            
            # Create visualization
            viz_result = self._create_visualization(
                filtered_graph, layout_data, node_attributes, edge_attributes,
                color_mapping, show_labels, interactive
            )
            
            # Save to files if requested
            file_paths = []
            if save_to_file:
                file_paths = self._save_visualization(viz_result, output_format)
            
            # Calculate statistics
            statistics = self._calculate_visualization_statistics(
                filtered_graph, layout_data, color_mapping, node_attributes
            )
            
            # Calculate academic confidence
            confidence = self._calculate_academic_confidence(statistics, layout_data)
            
            # Performance monitoring
            execution_time, memory_used = self._end_execution()
            
            # Prepare result data
            result_data = {
                "visualization_data": {
                    "plotly_figure": viz_result.get("figure_json") if interactive else None,
                    "node_positions": layout_data["positions"],
                    "edge_data": edge_attributes,
                    "color_mapping": color_mapping
                },
                "layout_info": {
                    "layout_type": layout.value,
                    "parameters": self.layout_configs[layout],
                    "computation_time": layout_data["computation_time"],
                    "node_count": len(filtered_graph.nodes()),
                    "edge_count": len(filtered_graph.edges())
                },
                "statistics": statistics,
                "file_paths": file_paths
            }
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data=result_data,
                execution_time=execution_time,
                memory_used=memory_used,
                metadata={
                    "academic_ready": True,
                    "layout_used": layout.value,
                    "color_scheme": color_scheme.value,
                    "statistical_significance": confidence,
                    "batch_processed": len(filtered_graph.nodes()) > 100,
                    "graph_size": len(filtered_graph.nodes()),
                    "edge_count": len(filtered_graph.edges()),
                    "interactive": interactive,
                    "output_formats": [output_format] if output_format != "all" else ["html", "json", "png"],
                    "publication_ready": True
                }
            )
            
        except Exception as e:
            return self._handle_advanced_error(e, request)
    
    def _validate_advanced_input(self, input_data: Any) -> Dict[str, Any]:
        """Advanced validation for visualization input"""
        try:
            # Basic type checking
            if not isinstance(input_data, dict):
                return {"valid": False, "error": "Input must be a dictionary"}
            
            # Required fields
            if "graph_source" not in input_data:
                return {"valid": False, "error": "graph_source is required"}
            
            # Validate graph source
            valid_sources = ["neo4j", "networkx", "edge_list", "adjacency_matrix"]
            if input_data["graph_source"] not in valid_sources:
                return {"valid": False, "error": f"graph_source must be one of {valid_sources}"}
            
            # Validate layout type
            if "layout" in input_data:
                try:
                    LayoutType(input_data["layout"])
                except ValueError:
                    valid_layouts = [lt.value for lt in LayoutType]
                    return {"valid": False, "error": f"layout must be one of {valid_layouts}"}
            
            # Validate color scheme
            if "color_scheme" in input_data:
                try:
                    ColorScheme(input_data["color_scheme"])
                except ValueError:
                    valid_schemes = [cs.value for cs in ColorScheme]
                    return {"valid": False, "error": f"color_scheme must be one of {valid_schemes}"}
            
            # Validate numeric parameters
            if "max_nodes" in input_data:
                max_nodes = input_data["max_nodes"]
                if not isinstance(max_nodes, int) or not (10 <= max_nodes <= 10000):
                    return {"valid": False, "error": "max_nodes must be an integer between 10 and 10000"}
            
            if "max_edges" in input_data:
                max_edges = input_data["max_edges"]
                if not isinstance(max_edges, int) or not (10 <= max_edges <= 50000):
                    return {"valid": False, "error": "max_edges must be an integer between 10 and 50000"}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}
    
    def _load_graph_data(self, graph_source: str, graph_data: Optional[Dict] = None) -> Optional[nx.Graph]:
        """Load graph data from various sources"""
        try:
            if graph_source == "neo4j":
                return self._load_from_neo4j()
            elif graph_source == "networkx":
                return self._load_from_networkx_data(graph_data)
            elif graph_source == "edge_list":
                return self._load_from_edge_list(graph_data)
            elif graph_source == "adjacency_matrix":
                return self._load_from_adjacency_matrix(graph_data)
            else:
                return None
                
        except Exception as e:
            print(f"Error loading graph data: {e}")
            return None
    
    def _load_from_neo4j(self) -> Optional[nx.Graph]:
        """Load graph from Neo4j database"""
        if not self.neo4j_tool or not self.neo4j_tool.driver:
            return None
        
        try:
            with self.neo4j_tool.driver.session() as session:
                # Load nodes with all available attributes
                nodes_result = session.run("""
                MATCH (n:Entity)
                RETURN n.entity_id as id, n.canonical_name as name, 
                       n.entity_type as type, n.pagerank_score as pagerank,
                       n.confidence as confidence, n.community_id as community
                """)
                
                # Load edges with attributes
                edges_result = session.run("""
                MATCH (a:Entity)-[r]->(b:Entity)
                RETURN a.entity_id as source, b.entity_id as target, 
                       r.weight as weight, r.confidence as confidence,
                       type(r) as relationship_type
                """)
                
                # Create NetworkX graph
                G = nx.Graph()
                
                # Add nodes with attributes
                for record in nodes_result:
                    G.add_node(
                        record["id"],
                        name=record["name"] or record["id"],
                        type=record["type"] or "unknown",
                        pagerank=record["pagerank"] or 0.0,
                        confidence=record["confidence"] or 0.8,
                        community=record["community"] or 0
                    )
                
                # Add edges with attributes
                for record in edges_result:
                    G.add_edge(
                        record["source"],
                        record["target"],
                        weight=record["weight"] or 1.0,
                        confidence=record["confidence"] or 0.8,
                        relationship_type=record["relationship_type"] or "related"
                    )
                
                return G
                
        except Exception as e:
            print(f"Error loading from Neo4j: {e}")
            return None
    
    def _load_from_networkx_data(self, graph_data: Dict) -> Optional[nx.Graph]:
        """Load graph from NetworkX data format"""
        if not graph_data or "nodes" not in graph_data or "edges" not in graph_data:
            return None
        
        try:
            G = nx.Graph()
            
            # Add nodes with attributes
            for node_data in graph_data["nodes"]:
                if isinstance(node_data, dict):
                    node_id = node_data.get("id")
                    attributes = {k: v for k, v in node_data.items() if k != "id"}
                    # Set default attributes
                    attributes.setdefault("name", str(node_id))
                    attributes.setdefault("type", "unknown")
                    attributes.setdefault("confidence", 0.8)
                    G.add_node(node_id, **attributes)
                else:
                    G.add_node(node_data, name=str(node_data), type="unknown", confidence=0.8)
            
            # Add edges with attributes
            for edge_data in graph_data["edges"]:
                if isinstance(edge_data, dict):
                    source = edge_data.get("source")
                    target = edge_data.get("target")
                    attributes = {k: v for k, v in edge_data.items() if k not in ["source", "target"]}
                    attributes.setdefault("weight", 1.0)
                    attributes.setdefault("confidence", 0.8)
                    G.add_edge(source, target, **attributes)
                elif isinstance(edge_data, (list, tuple)) and len(edge_data) >= 2:
                    G.add_edge(edge_data[0], edge_data[1], weight=1.0, confidence=0.8)
            
            return G
            
        except Exception as e:
            print(f"Error loading NetworkX data: {e}")
            return None
    
    def _load_from_edge_list(self, graph_data: Dict) -> Optional[nx.Graph]:
        """Load graph from edge list format"""
        if not graph_data or "edges" not in graph_data:
            return None
        
        try:
            G = nx.Graph()
            
            for edge in graph_data["edges"]:
                if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                    source, target = edge[0], edge[1]
                    weight = edge[2] if len(edge) > 2 else 1.0
                    G.add_edge(source, target, weight=weight, confidence=0.8)
                elif isinstance(edge, dict):
                    source = edge.get("source")
                    target = edge.get("target")
                    weight = edge.get("weight", 1.0)
                    confidence = edge.get("confidence", 0.8)
                    if source and target:
                        G.add_edge(source, target, weight=weight, confidence=confidence)
            
            # Add default node attributes
            for node in G.nodes():
                G.nodes[node].setdefault("name", str(node))
                G.nodes[node].setdefault("type", "unknown")
                G.nodes[node].setdefault("confidence", 0.8)
            
            return G
            
        except Exception as e:
            print(f"Error loading edge list: {e}")
            return None
    
    def _load_from_adjacency_matrix(self, graph_data: Dict) -> Optional[nx.Graph]:
        """Load graph from adjacency matrix format"""
        if not graph_data or "matrix" not in graph_data:
            return None
        
        try:
            matrix = np.array(graph_data["matrix"])
            node_labels = graph_data.get("node_labels", list(range(len(matrix))))
            
            G = nx.from_numpy_array(matrix)
            
            # Relabel nodes if labels provided
            if len(node_labels) == len(matrix):
                mapping = {i: label for i, label in enumerate(node_labels)}
                G = nx.relabel_nodes(G, mapping)
            
            # Add default attributes
            for node in G.nodes():
                G.nodes[node].setdefault("name", str(node))
                G.nodes[node].setdefault("type", "unknown")
                G.nodes[node].setdefault("confidence", 0.8)
            
            for edge in G.edges():
                G.edges[edge].setdefault("confidence", 0.8)
            
            return G
            
        except Exception as e:
            print(f"Error loading adjacency matrix: {e}")
            return None
    
    def _apply_filters(self, graph: nx.Graph, filter_criteria: Dict[str, Any]) -> nx.Graph:
        """Apply filtering criteria to graph"""
        filtered_graph = graph.copy()
        
        try:
            # Filter by minimum degree
            if "min_degree" in filter_criteria:
                min_degree = filter_criteria["min_degree"]
                nodes_to_remove = [node for node, degree in graph.degree() if degree < min_degree]
                filtered_graph.remove_nodes_from(nodes_to_remove)
            
            # Filter by minimum confidence
            if "min_confidence" in filter_criteria:
                min_confidence = filter_criteria["min_confidence"]
                nodes_to_remove = [
                    node for node in filtered_graph.nodes() 
                    if filtered_graph.nodes[node].get("confidence", 0.0) < min_confidence
                ]
                filtered_graph.remove_nodes_from(nodes_to_remove)
            
            # Filter by entity types
            if "entity_types" in filter_criteria:
                allowed_types = set(filter_criteria["entity_types"])
                nodes_to_remove = [
                    node for node in filtered_graph.nodes()
                    if filtered_graph.nodes[node].get("type", "unknown") not in allowed_types
                ]
                filtered_graph.remove_nodes_from(nodes_to_remove)
            
            # Filter by communities
            if "communities" in filter_criteria:
                allowed_communities = set(filter_criteria["communities"])
                nodes_to_remove = [
                    node for node in filtered_graph.nodes()
                    if filtered_graph.nodes[node].get("community", 0) not in allowed_communities
                ]
                filtered_graph.remove_nodes_from(nodes_to_remove)
            
            return filtered_graph
            
        except Exception as e:
            print(f"Error applying filters: {e}")
            return graph
    
    def _calculate_layout(self, graph: nx.Graph, layout_type: LayoutType) -> Dict[str, Any]:
        """Calculate graph layout using specified algorithm"""
        start_time = time.time()
        
        try:
            config = self.layout_configs[layout_type].copy()
            
            if layout_type == LayoutType.SPRING:
                pos = nx.spring_layout(graph, **config)
            elif layout_type == LayoutType.CIRCULAR:
                pos = nx.circular_layout(graph, **config)
            elif layout_type == LayoutType.KAMADA_KAWAI:
                pos = nx.kamada_kawai_layout(graph, **config)
            elif layout_type == LayoutType.FRUCHTERMAN_REINGOLD:
                pos = nx.fruchterman_reingold_layout(graph, **config)
            elif layout_type == LayoutType.SPECTRAL:
                pos = nx.spectral_layout(graph, **config)
            elif layout_type == LayoutType.PLANAR:
                if nx.is_planar(graph):
                    pos = nx.planar_layout(graph, **config)
                else:
                    # Fallback to spring layout
                    pos = nx.spring_layout(graph)
            elif layout_type == LayoutType.SHELL:
                pos = nx.shell_layout(graph, **config)
            elif layout_type == LayoutType.SPIRAL:
                pos = nx.spiral_layout(graph, **config)
            elif layout_type == LayoutType.RANDOM:
                pos = nx.random_layout(graph, **config)
            else:
                pos = nx.spring_layout(graph)  # Default fallback
            
            computation_time = time.time() - start_time
            
            return {
                "positions": pos,
                "computation_time": computation_time,
                "layout_type": layout_type.value,
                "config": config
            }
            
        except Exception as e:
            print(f"Error calculating layout: {e}")
            # Fallback to random layout
            pos = nx.random_layout(graph)
            return {
                "positions": pos,
                "computation_time": time.time() - start_time,
                "layout_type": "random",
                "config": {}
            }
    
    def _calculate_node_attributes(self, graph: nx.Graph, size_metric: str) -> Dict[str, Any]:
        """Calculate node attributes for visualization"""
        attributes = {}
        
        try:
            # Calculate node sizes based on metric
            if size_metric == "degree":
                degrees = dict(graph.degree())
                max_degree = max(degrees.values()) if degrees else 1
                attributes["sizes"] = {node: 10 + 40 * (degree / max_degree) for node, degree in degrees.items()}
            
            elif size_metric == "pagerank":
                pagerank = nx.pagerank(graph)
                max_pr = max(pagerank.values()) if pagerank else 1
                attributes["sizes"] = {node: 10 + 40 * (pr / max_pr) for node, pr in pagerank.items()}
            
            elif size_metric == "centrality":
                centrality = nx.betweenness_centrality(graph)
                max_cent = max(centrality.values()) if centrality else 1
                if max_cent > 0:
                    attributes["sizes"] = {node: 10 + 40 * (cent / max_cent) for node, cent in centrality.items()}
                else:
                    attributes["sizes"] = {node: 25 for node in graph.nodes()}
            
            elif size_metric == "confidence":
                confidences = {node: graph.nodes[node].get("confidence", 0.8) for node in graph.nodes()}
                max_conf = max(confidences.values()) if confidences else 1
                attributes["sizes"] = {node: 10 + 40 * (conf / max_conf) for node, conf in confidences.items()}
            
            else:  # uniform
                attributes["sizes"] = {node: 25 for node in graph.nodes()}
            
            # Calculate other attributes with error handling
            attributes["degrees"] = dict(graph.degree())
            
            try:
                attributes["pagerank"] = nx.pagerank(graph)
            except Exception as e:
                print(f"PageRank calculation failed: {e}")
                # Fallback: uniform PageRank values
                num_nodes = len(graph.nodes())
                attributes["pagerank"] = {node: 1.0/num_nodes for node in graph.nodes()}
            
            try:
                attributes["centrality"] = nx.betweenness_centrality(graph)
            except Exception as e:
                print(f"Centrality calculation failed: {e}")
                # Fallback: zero centrality
                attributes["centrality"] = {node: 0.0 for node in graph.nodes()}
            
            return attributes
            
        except Exception as e:
            print(f"Error calculating node attributes: {e}")
            return {"sizes": {node: 25 for node in graph.nodes()}}
    
    def _calculate_edge_attributes(self, graph: nx.Graph, width_metric: str) -> List[Dict[str, Any]]:
        """Calculate edge attributes for visualization"""
        edge_data = []
        
        try:
            # Get edge widths based on metric
            if width_metric == "weight":
                weights = [graph.edges[edge].get("weight", 1.0) for edge in graph.edges()]
                max_weight = max(weights) if weights else 1
                widths = [1 + 9 * (w / max_weight) for w in weights]
            
            elif width_metric == "confidence":
                confidences = [graph.edges[edge].get("confidence", 0.8) for edge in graph.edges()]
                max_conf = max(confidences) if confidences else 1
                widths = [1 + 9 * (c / max_conf) for c in confidences]
            
            else:  # uniform
                widths = [2.0] * len(graph.edges())
            
            # Create edge data
            for i, (source, target) in enumerate(graph.edges()):
                edge_data.append({
                    "source": source,
                    "target": target,
                    "width": widths[i] if i < len(widths) else 2.0,
                    "weight": graph.edges[(source, target)].get("weight", 1.0),
                    "confidence": graph.edges[(source, target)].get("confidence", 0.8),
                    "type": graph.edges[(source, target)].get("relationship_type", "related")
                })
            
            return edge_data
            
        except Exception as e:
            print(f"Error calculating edge attributes: {e}")
            return [{"source": s, "target": t, "width": 2.0} for s, t in graph.edges()]
    
    def _generate_color_mapping(self, graph: nx.Graph, color_scheme: ColorScheme, 
                              custom_colors: Dict[str, Any], node_attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Generate color mapping for nodes and edges"""
        color_mapping = {"nodes": {}, "edges": {}, "legend": {}}
        
        try:
            if color_scheme == ColorScheme.CUSTOM and custom_colors:
                color_mapping["nodes"] = custom_colors.get("nodes", {})
                color_mapping["edges"] = custom_colors.get("edges", {})
            
            elif color_scheme == ColorScheme.ENTITY_TYPE:
                entity_types = list(set(graph.nodes[node].get("type", "unknown") for node in graph.nodes()))
                palette = self.color_palettes[color_scheme]
                type_colors = {etype: palette[i % len(palette)] for i, etype in enumerate(entity_types)}
                color_mapping["nodes"] = {node: type_colors[graph.nodes[node].get("type", "unknown")] 
                                        for node in graph.nodes()}
                color_mapping["legend"] = type_colors
            
            elif color_scheme == ColorScheme.CONFIDENCE:
                confidences = {node: graph.nodes[node].get("confidence", 0.8) for node in graph.nodes()}
                min_conf = min(confidences.values())
                max_conf = max(confidences.values())
                palette = self.color_palettes[color_scheme]
                
                for node in graph.nodes():
                    conf = confidences[node]
                    if max_conf > min_conf:
                        norm_conf = (conf - min_conf) / (max_conf - min_conf)
                    else:
                        norm_conf = 0.5
                    color_idx = int(norm_conf * (len(palette) - 1))
                    color_mapping["nodes"][node] = palette[color_idx]
            
            elif color_scheme == ColorScheme.DEGREE:
                degrees = node_attributes.get("degrees", {})
                max_degree = max(degrees.values()) if degrees else 1
                palette = self.color_palettes[color_scheme]
                
                for node in graph.nodes():
                    degree = degrees.get(node, 0)
                    norm_degree = degree / max_degree if max_degree > 0 else 0
                    color_idx = int(norm_degree * (len(palette) - 1))
                    color_mapping["nodes"][node] = palette[color_idx]
            
            elif color_scheme == ColorScheme.PAGERANK:
                pagerank = node_attributes.get("pagerank", {})
                max_pr = max(pagerank.values()) if pagerank else 1
                palette = self.color_palettes[color_scheme]
                
                for node in graph.nodes():
                    pr = pagerank.get(node, 0)
                    norm_pr = pr / max_pr if max_pr > 0 else 0
                    color_idx = int(norm_pr * (len(palette) - 1))
                    color_mapping["nodes"][node] = palette[color_idx]
            
            elif color_scheme == ColorScheme.COMMUNITY:
                communities = list(set(graph.nodes[node].get("community", 0) for node in graph.nodes()))
                palette = self.color_palettes[color_scheme]
                comm_colors = {comm: palette[i % len(palette)] for i, comm in enumerate(communities)}
                color_mapping["nodes"] = {node: comm_colors[graph.nodes[node].get("community", 0)] 
                                        for node in graph.nodes()}
                color_mapping["legend"] = comm_colors
            
            else:
                # Default color
                default_color = "#1f77b4"
                color_mapping["nodes"] = {node: default_color for node in graph.nodes()}
            
            # Default edge colors
            if not color_mapping["edges"]:
                color_mapping["edges"] = {edge: "#888888" for edge in graph.edges()}
            
            return color_mapping
            
        except Exception as e:
            print(f"Error generating color mapping: {e}")
            default_color = "#1f77b4"
            return {
                "nodes": {node: default_color for node in graph.nodes()},
                "edges": {edge: "#888888" for edge in graph.edges()},
                "legend": {}
            }
    
    def _create_visualization(self, graph: nx.Graph, layout_data: Dict[str, Any], 
                            node_attributes: Dict[str, Any], edge_attributes: List[Dict[str, Any]],
                            color_mapping: Dict[str, Any], show_labels: bool, 
                            interactive: bool) -> Dict[str, Any]:
        """Create Plotly visualization"""
        try:
            pos = layout_data["positions"]
            
            # Create edge traces
            edge_x = []
            edge_y = []
            for edge_data in edge_attributes:
                source = edge_data["source"]
                target = edge_data["target"]
                if source in pos and target in pos:
                    x0, y0 = pos[source]
                    x1, y1 = pos[target]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
            
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=2, color='#888'),
                hoverinfo='none',
                mode='lines'
            )
            
            # Create node traces
            node_x = []
            node_y = []
            node_colors = []
            node_sizes = []
            node_text = []
            node_hovertext = []
            
            for node in graph.nodes():
                if node in pos:
                    x, y = pos[node]
                    node_x.append(x)
                    node_y.append(y)
                    node_colors.append(color_mapping["nodes"].get(node, "#1f77b4"))
                    node_sizes.append(node_attributes["sizes"].get(node, 25))
                    
                    if show_labels:
                        node_text.append(graph.nodes[node].get("name", str(node)))
                    else:
                        node_text.append("")
                    
                    # Create hover text
                    hover_info = [
                        f"Node: {graph.nodes[node].get('name', str(node))}",
                        f"Type: {graph.nodes[node].get('type', 'unknown')}",
                        f"Degree: {node_attributes.get('degrees', {}).get(node, 0)}",
                        f"PageRank: {node_attributes.get('pagerank', {}).get(node, 0):.4f}",
                        f"Confidence: {graph.nodes[node].get('confidence', 0.8):.2f}"
                    ]
                    node_hovertext.append("<br>".join(hover_info))
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text' if show_labels else 'markers',
                hoverinfo='text',
                hovertext=node_hovertext,
                text=node_text,
                textposition="middle center",
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    line=dict(width=2, color='white')
                )
            )
            
            # Create figure
            fig = go.Figure(data=[edge_trace, node_trace],
                          layout=go.Layout(
                              title=dict(
                                  text=f'Graph Visualization - {layout_data["layout_type"].title()} Layout',
                                  font=dict(size=16)
                              ),
                              showlegend=False,
                              hovermode='closest',
                              margin=dict(b=20,l=5,r=5,t=40),
                              annotations=[ dict(
                                  text=f"Nodes: {len(graph.nodes())}, Edges: {len(graph.edges())}",
                                  showarrow=False,
                                  xref="paper", yref="paper",
                                  x=0.005, y=-0.002,
                                  xanchor='left', yanchor='bottom',
                                  font=dict(size=12)
                              )],
                              xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                              yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                          )
            
            result = {
                "figure": fig,
                "figure_json": fig.to_json() if interactive else None
            }
            
            return result
            
        except Exception as e:
            print(f"Error creating visualization: {e}")
            # Return minimal figure
            fig = go.Figure()
            fig.add_annotation(text=f"Visualization error: {str(e)}", 
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return {"figure": fig, "figure_json": None}
    
    def _save_visualization(self, viz_result: Dict[str, Any], output_format: str) -> List[str]:
        """Save visualization to files"""
        file_paths = []
        
        try:
            # Create temporary directory for output files
            temp_dir = tempfile.mkdtemp(prefix="graph_viz_")
            base_filename = "graph_visualization"
            
            fig = viz_result["figure"]
            
            if output_format == "all" or output_format == "html":
                html_path = os.path.join(temp_dir, f"{base_filename}.html")
                fig.write_html(html_path)
                file_paths.append(html_path)
            
            if output_format == "all" or output_format == "json":
                json_path = os.path.join(temp_dir, f"{base_filename}.json")
                with open(json_path, 'w') as f:
                    json.dump(viz_result["figure_json"], f, indent=2)
                file_paths.append(json_path)
            
            if output_format == "all" or output_format == "png":
                try:
                    png_path = os.path.join(temp_dir, f"{base_filename}.png")
                    fig.write_image(png_path, format="png", width=1200, height=800)
                    file_paths.append(png_path)
                except Exception as e:
                    print(f"Could not save PNG: {e}")
            
            if output_format == "all" or output_format == "svg":
                try:
                    svg_path = os.path.join(temp_dir, f"{base_filename}.svg")
                    fig.write_image(svg_path, format="svg", width=1200, height=800)
                    file_paths.append(svg_path)
                except Exception as e:
                    print(f"Could not save SVG: {e}")
            
            return file_paths
            
        except Exception as e:
            print(f"Error saving visualization: {e}")
            return []
    
    def _calculate_visualization_statistics(self, graph: nx.Graph, layout_data: Dict[str, Any],
                                          color_mapping: Dict[str, Any], 
                                          node_attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive visualization statistics"""
        try:
            # Graph metrics
            graph_metrics = {
                "node_count": len(graph.nodes()),
                "edge_count": len(graph.edges()),
                "density": nx.density(graph),
                "average_degree": sum(dict(graph.degree()).values()) / len(graph.nodes()) if graph.nodes() else 0,
                "connected_components": nx.number_connected_components(graph),
                "average_clustering": nx.average_clustering(graph)
            }
            
            # Layout quality metrics
            pos = layout_data["positions"]
            if pos:
                # Calculate edge crossing (simplified)
                edge_lengths = []
                for edge in graph.edges():
                    if edge[0] in pos and edge[1] in pos:
                        x1, y1 = pos[edge[0]]
                        x2, y2 = pos[edge[1]]
                        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                        edge_lengths.append(length)
                
                layout_quality = {
                    "computation_time": layout_data["computation_time"],
                    "average_edge_length": np.mean(edge_lengths) if edge_lengths else 0,
                    "edge_length_variance": np.var(edge_lengths) if edge_lengths else 0,
                    "layout_type": layout_data["layout_type"]
                }
            else:
                layout_quality = {"computation_time": layout_data["computation_time"]}
            
            # Color distribution
            node_colors = list(color_mapping["nodes"].values())
            unique_colors = list(set(node_colors))
            color_distribution = {
                "unique_colors": len(unique_colors),
                "color_counts": {color: node_colors.count(color) for color in unique_colors}
            }
            
            # Performance metrics
            performance_metrics = {
                "layout_computation_time": layout_data["computation_time"],
                "nodes_processed": len(graph.nodes()),
                "edges_processed": len(graph.edges())
            }
            
            return {
                "graph_metrics": graph_metrics,
                "layout_quality": layout_quality,
                "color_distribution": color_distribution,
                "performance_metrics": performance_metrics
            }
            
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return {
                "graph_metrics": {"node_count": len(graph.nodes()), "edge_count": len(graph.edges())},
                "layout_quality": {},
                "color_distribution": {},
                "performance_metrics": {}
            }
    
    def _calculate_academic_confidence(self, statistics: Dict[str, Any], 
                                     layout_data: Dict[str, Any]) -> float:
        """Calculate academic-quality confidence for visualization"""
        try:
            # Base confidence from graph size and connectivity
            graph_metrics = statistics.get("graph_metrics", {})
            node_count = graph_metrics.get("node_count", 0)
            edge_count = graph_metrics.get("edge_count", 0)
            density = graph_metrics.get("density", 0)
            
            # Size factor (more nodes generally better for academic visualization)
            size_factor = min(1.0, node_count / 100.0)  # Normalize to 100 nodes
            
            # Connectivity factor
            connectivity_factor = min(1.0, density * 10)  # Moderate density is good
            
            # Layout quality factor
            layout_quality = statistics.get("layout_quality", {})
            computation_time = layout_quality.get("computation_time", 0)
            layout_factor = 0.8 if computation_time > 0 and computation_time < 30 else 0.5
            
            # Color diversity factor
            color_dist = statistics.get("color_distribution", {})
            unique_colors = color_dist.get("unique_colors", 1)
            color_factor = min(1.0, unique_colors / 10.0)  # Good color diversity
            
            # Combine factors
            combined_confidence = (
                size_factor * 0.3 +
                connectivity_factor * 0.25 +
                layout_factor * 0.25 +
                color_factor * 0.2
            )
            
            return max(0.1, min(1.0, combined_confidence))
            
        except Exception as e:
            print(f"Error calculating academic confidence: {e}")
            return 0.5
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input against tool contract - override base implementation"""
        validation_result = self._validate_advanced_input(input_data)
        return validation_result["valid"]
    
    def _handle_advanced_error(self, error: Exception, request: ToolRequest) -> ToolResult:
        """Handle advanced analytics errors"""
        execution_time, memory_used = self._end_execution()
        
        error_message = str(error)
        error_code = "UNEXPECTED_ERROR"
        
        # Categorize specific errors
        if "memory" in error_message.lower():
            error_code = "MEMORY_LIMIT_EXCEEDED"
        elif "plotly" in error_message.lower():
            error_code = "PLOTLY_NOT_AVAILABLE"
        elif "layout" in error_message.lower():
            error_code = "LAYOUT_NOT_SUPPORTED"
        elif "visualization" in error_message.lower():
            error_code = "VISUALIZATION_FAILED"
        elif "neo4j" in error_message.lower():
            error_code = "NEO4J_CONNECTION_ERROR"
        elif "file" in error_message.lower() or "write" in error_message.lower():
            error_code = "FILE_WRITE_ERROR"
        
        return ToolResult(
            tool_id=self.tool_id,
            status="error",
            data=None,
            execution_time=execution_time,
            memory_used=memory_used,
            error_code=error_code,
            error_message=error_message,
            metadata={
                "operation": request.operation,
                "timestamp": datetime.now().isoformat(),
                "academic_ready": False
            }
        )


# Example usage and validation
if __name__ == "__main__":
    # Quick validation test
    tool = GraphVisualizationTool()
    contract = tool.get_contract()
    print(f"Tool {tool.tool_id} initialized successfully")
    print(f"Contract: {contract.name}")
    print(f"Supported layouts: {[lt.value for lt in LayoutType]}")
    print(f"Plotly available: {tool.plotly_available}")