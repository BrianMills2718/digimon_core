"""T55: Temporal Analysis Tool - Advanced Graph Analytics

Real temporal graph analysis using NetworkX with time-series evolution and change detection.
Part of Phase 2.1 Graph Analytics tools providing advanced temporal network analysis capabilities.
"""

import time
import psutil
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import networkx as nx
import numpy as np
from dataclasses import dataclass
from enum import Enum
import json
from collections import defaultdict

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


class TemporalAnalysisType(Enum):
    """Supported temporal analysis types"""
    EVOLUTION = "evolution"
    CHANGE_DETECTION = "change_detection"
    TREND_ANALYSIS = "trend_analysis"
    SNAPSHOT_COMPARISON = "snapshot_comparison"
    DYNAMIC_CENTRALITY = "dynamic_centrality"
    TEMPORAL_PATHS = "temporal_paths"
    COMMUNITY_EVOLUTION = "community_evolution"
    ALL = "all"


class ChangeType(Enum):
    """Types of changes in temporal networks"""
    NODE_ADDITION = "node_addition"
    NODE_REMOVAL = "node_removal"
    EDGE_ADDITION = "edge_addition"
    EDGE_REMOVAL = "edge_removal"
    WEIGHT_CHANGE = "weight_change"
    ATTRIBUTE_CHANGE = "attribute_change"
    COMMUNITY_CHANGE = "community_change"


@dataclass
class TemporalSnapshot:
    """Temporal graph snapshot"""
    timestamp: str
    graph: nx.Graph
    metrics: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class ChangeEvent:
    """Graph change event"""
    timestamp: str
    change_type: ChangeType
    affected_elements: List[str]
    magnitude: float
    details: Dict[str, Any]


@dataclass
class TemporalTrend:
    """Temporal trend in graph metrics"""
    metric_name: str
    values: List[float]
    timestamps: List[str]
    trend_direction: str  # "increasing", "decreasing", "stable", "volatile"
    trend_strength: float
    change_points: List[str]


class TemporalAnalysisTool(BaseTool):
    """T55: Advanced Temporal Analysis Tool
    
    Implements real temporal graph analysis including time-series evolution,
    change detection, and trend analysis for academic research networks.
    """
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize temporal analysis tool with advanced capabilities"""
        if service_manager is None:
            service_manager = ServiceManager()
        
        super().__init__(service_manager)
        self.tool_id = "T55_TEMPORAL_ANALYSIS"
        self.name = "Advanced Temporal Analysis"
        self.category = "advanced_analytics"
        self.requires_large_data = True
        self.supports_batch_processing = True
        self.academic_output_ready = True
        
        # Initialize Neo4j connection for graph data
        self.neo4j_tool = None
        self._initialize_neo4j_connection()
        
        # Temporal analysis configurations
        self.analysis_configs = {
            TemporalAnalysisType.EVOLUTION: {
                "min_snapshots": 2,
                "max_snapshots": 100,
                "compute_metrics": True
            },
            TemporalAnalysisType.CHANGE_DETECTION: {
                "sensitivity": 0.1,
                "min_change_magnitude": 0.05,
                "change_types": ["all"]
            },
            TemporalAnalysisType.TREND_ANALYSIS: {
                "min_data_points": 3,
                "trend_window": 5,
                "significance_threshold": 0.05
            },
            TemporalAnalysisType.SNAPSHOT_COMPARISON: {
                "comparison_metrics": ["density", "clustering", "centrality"],
                "statistical_tests": True
            },
            TemporalAnalysisType.DYNAMIC_CENTRALITY: {
                "centrality_measures": ["degree", "betweenness", "closeness", "pagerank"],
                "normalize": True
            },
            TemporalAnalysisType.TEMPORAL_PATHS: {
                "max_path_length": 10,
                "time_window": None  # Auto-calculate
            },
            TemporalAnalysisType.COMMUNITY_EVOLUTION: {
                "community_algorithm": "louvain",
                "stability_threshold": 0.8
            }
        }
        
        # Default graph metrics to track
        self.default_metrics = [
            "node_count", "edge_count", "density", "average_clustering", 
            "average_degree", "diameter", "radius", "transitivity"
        ]
    
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
            description="Advanced temporal graph analysis with evolution tracking and change detection",
            category=self.category,
            input_schema={
                "type": "object",
                "properties": {
                    "temporal_data_source": {
                        "type": "string",
                        "enum": ["neo4j_temporal", "graph_snapshots", "edge_sequence", "event_stream"],
                        "description": "Source of temporal graph data"
                    },
                    "temporal_data": {
                        "type": "object",
                        "description": "Temporal graph data"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["evolution", "change_detection", "trend_analysis", 
                               "snapshot_comparison", "dynamic_centrality", "temporal_paths",
                               "community_evolution", "all"],
                        "default": "evolution"
                    },
                    "time_range": {
                        "type": "object",
                        "properties": {
                            "start_time": {"type": "string"},
                            "end_time": {"type": "string"},
                            "time_unit": {"type": "string", "enum": ["second", "minute", "hour", "day", "week", "month"]}
                        }
                    },
                    "temporal_resolution": {
                        "type": "string",
                        "enum": ["high", "medium", "low", "auto"],
                        "default": "auto"
                    },
                    "metrics_to_track": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["node_count", "edge_count", "density", "clustering"]
                    },
                    "change_detection_params": {
                        "type": "object",
                        "properties": {
                            "sensitivity": {"type": "number", "minimum": 0.01, "maximum": 1.0},
                            "min_change_magnitude": {"type": "number", "minimum": 0.001, "maximum": 1.0},
                            "change_types": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "trend_analysis_params": {
                        "type": "object",
                        "properties": {
                            "trend_window": {"type": "integer", "minimum": 3, "maximum": 50},
                            "significance_threshold": {"type": "number", "minimum": 0.01, "maximum": 0.2},
                            "detrend": {"type": "boolean", "default": False}
                        }
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["detailed", "summary", "time_series", "changes_only"],
                        "default": "detailed"
                    },
                    "include_visualizations": {
                        "type": "boolean",
                        "default": True
                    },
                    "store_results": {
                        "type": "boolean",
                        "default": False
                    }
                },
                "required": ["temporal_data_source"],
                "additionalProperties": False
            },
            output_schema={
                "type": "object",
                "properties": {
                    "temporal_evolution": {
                        "type": "object",
                        "properties": {
                            "snapshots": {"type": "array"},
                            "metrics_evolution": {"type": "object"},
                            "summary_statistics": {"type": "object"}
                        }
                    },
                    "change_events": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "timestamp": {"type": "string"},
                                "change_type": {"type": "string"},
                                "affected_elements": {"type": "array"},
                                "magnitude": {"type": "number"},
                                "details": {"type": "object"}
                            }
                        }
                    },
                    "temporal_trends": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "metric_name": {"type": "string"},
                                "values": {"type": "array"},
                                "timestamps": {"type": "array"},
                                "trend_direction": {"type": "string"},
                                "trend_strength": {"type": "number"},
                                "change_points": {"type": "array"}
                            }
                        }
                    },
                    "analysis_summary": {
                        "type": "object",
                        "properties": {
                            "time_span": {"type": "string"},
                            "total_snapshots": {"type": "integer"},
                            "major_changes": {"type": "integer"},
                            "stability_index": {"type": "number"},
                            "growth_rate": {"type": "number"}
                        }
                    }
                },
                "required": ["temporal_evolution", "change_events", "temporal_trends", "analysis_summary"]
            },
            dependencies=["networkx", "numpy", "neo4j_service"],
            performance_requirements={
                "max_execution_time": 600.0,  # 10 minutes for large temporal datasets
                "max_memory_mb": 6000,  # 6GB for temporal analysis
                "min_accuracy": 0.90  # Temporal analysis accuracy
            },
            error_conditions=[
                "INVALID_TEMPORAL_DATA",
                "ANALYSIS_TYPE_NOT_SUPPORTED",
                "INSUFFICIENT_TEMPORAL_DATA",
                "TIME_RANGE_INVALID",
                "TEMPORAL_ANALYSIS_FAILED",
                "NEO4J_CONNECTION_ERROR",
                "MEMORY_LIMIT_EXCEEDED",
                "CHANGE_DETECTION_FAILED"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute temporal analysis with real algorithms"""
        self._start_execution()
        
        try:
            # Validate input against contract
            validation_result = self._validate_advanced_input(request.input_data)
            if not validation_result["valid"]:
                return self._create_error_result(request, "INVALID_INPUT", validation_result["error"])
            
            # Extract parameters
            temporal_data_source = request.input_data["temporal_data_source"]
            analysis_type = TemporalAnalysisType(request.input_data.get("analysis_type", "evolution"))
            time_range = request.input_data.get("time_range", {})
            temporal_resolution = request.input_data.get("temporal_resolution", "auto")
            metrics_to_track = request.input_data.get("metrics_to_track", self.default_metrics)
            change_detection_params = request.input_data.get("change_detection_params", {})
            trend_analysis_params = request.input_data.get("trend_analysis_params", {})
            output_format = request.input_data.get("output_format", "detailed")
            include_visualizations = request.input_data.get("include_visualizations", True)
            store_results = request.input_data.get("store_results", False)
            
            # Load temporal data
            temporal_snapshots = self._load_temporal_data(
                temporal_data_source, request.input_data.get("temporal_data"), time_range
            )
            if not temporal_snapshots:
                return self._create_error_result(
                    request, "INVALID_TEMPORAL_DATA", "Failed to load temporal data"
                )
            
            # Validate temporal data sufficiency
            if len(temporal_snapshots) < 2:
                return self._create_error_result(
                    request, "INSUFFICIENT_TEMPORAL_DATA", 
                    f"At least 2 temporal snapshots required, got {len(temporal_snapshots)}"
                )
            
            # Perform temporal analysis
            analysis_results = {}
            
            if analysis_type == TemporalAnalysisType.ALL:
                # Perform all analysis types
                for specific_type in TemporalAnalysisType:
                    if specific_type != TemporalAnalysisType.ALL:
                        result = self._perform_temporal_analysis(
                            temporal_snapshots, specific_type, metrics_to_track,
                            change_detection_params, trend_analysis_params
                        )
                        analysis_results[specific_type.value] = result
            else:
                # Perform specific analysis
                analysis_results[analysis_type.value] = self._perform_temporal_analysis(
                    temporal_snapshots, analysis_type, metrics_to_track,
                    change_detection_params, trend_analysis_params
                )
            
            # Extract results for standardized output
            temporal_evolution = self._extract_temporal_evolution(analysis_results, temporal_snapshots)
            change_events = self._extract_change_events(analysis_results)
            temporal_trends = self._extract_temporal_trends(analysis_results)
            analysis_summary = self._calculate_analysis_summary(temporal_snapshots, analysis_results)
            
            # Store results to Neo4j if requested
            storage_info = {}
            if store_results and self.neo4j_tool:
                storage_info = self._store_temporal_results(analysis_results, temporal_snapshots)
            
            # Calculate academic confidence
            confidence = self._calculate_academic_confidence(analysis_summary, temporal_snapshots)
            
            # Performance monitoring
            execution_time, memory_used = self._end_execution()
            
            # Prepare result data based on output format
            result_data = self._format_output(
                temporal_evolution, change_events, temporal_trends, analysis_summary, output_format
            )
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data=result_data,
                execution_time=execution_time,
                memory_used=memory_used,
                metadata={
                    "academic_ready": True,
                    "analysis_type": analysis_type.value,
                    "statistical_significance": confidence,
                    "batch_processed": len(temporal_snapshots) > 10,
                    "temporal_span": len(temporal_snapshots),
                    "metrics_tracked": len(metrics_to_track),
                    "change_events_detected": len(change_events),
                    "trends_analyzed": len(temporal_trends),
                    "storage_info": storage_info,
                    "publication_ready": True
                }
            )
            
        except Exception as e:
            return self._handle_advanced_error(e, request)
    
    def _validate_advanced_input(self, input_data: Any) -> Dict[str, Any]:
        """Advanced validation for temporal analysis input"""
        try:
            # Basic type checking
            if not isinstance(input_data, dict):
                return {"valid": False, "error": "Input must be a dictionary"}
            
            # Required fields
            if "temporal_data_source" not in input_data:
                return {"valid": False, "error": "temporal_data_source is required"}
            
            # Validate temporal data source
            valid_sources = ["neo4j_temporal", "graph_snapshots", "edge_sequence", "event_stream"]
            if input_data["temporal_data_source"] not in valid_sources:
                return {"valid": False, "error": f"temporal_data_source must be one of {valid_sources}"}
            
            # Validate analysis type
            if "analysis_type" in input_data:
                try:
                    TemporalAnalysisType(input_data["analysis_type"])
                except ValueError:
                    valid_types = [at.value for at in TemporalAnalysisType]
                    return {"valid": False, "error": f"analysis_type must be one of {valid_types}"}
            
            # Validate time range
            if "time_range" in input_data:
                time_range = input_data["time_range"]
                if not isinstance(time_range, dict):
                    return {"valid": False, "error": "time_range must be a dictionary"}
                
                # Check required time range fields
                if "start_time" in time_range and "end_time" in time_range:
                    try:
                        # Try to parse timestamps
                        datetime.fromisoformat(time_range["start_time"].replace('Z', '+00:00'))
                        datetime.fromisoformat(time_range["end_time"].replace('Z', '+00:00'))
                    except ValueError:
                        return {"valid": False, "error": "Invalid timestamp format in time_range"}
            
            # Validate change detection parameters
            if "change_detection_params" in input_data:
                params = input_data["change_detection_params"]
                if not isinstance(params, dict):
                    return {"valid": False, "error": "change_detection_params must be a dictionary"}
                
                if "sensitivity" in params:
                    if not (0.01 <= params["sensitivity"] <= 1.0):
                        return {"valid": False, "error": "sensitivity must be between 0.01 and 1.0"}
            
            return {"valid": True, "error": None}
            
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}
    
    def _load_temporal_data(self, data_source: str, temporal_data: Optional[Dict] = None,
                           time_range: Dict[str, Any] = None) -> List[TemporalSnapshot]:
        """Load temporal graph data from various sources"""
        try:
            if data_source == "neo4j_temporal":
                return self._load_from_neo4j_temporal(time_range)
            elif data_source == "graph_snapshots":
                return self._load_from_graph_snapshots(temporal_data)
            elif data_source == "edge_sequence":
                return self._load_from_edge_sequence(temporal_data)
            elif data_source == "event_stream":
                return self._load_from_event_stream(temporal_data)
            else:
                return []
                
        except Exception as e:
            print(f"Error loading temporal data: {e}")
            return []
    
    def _load_from_neo4j_temporal(self, time_range: Dict[str, Any] = None) -> List[TemporalSnapshot]:
        """Load temporal data from Neo4j with timestamp information"""
        if not self.neo4j_tool or not self.neo4j_tool.driver:
            return []
        
        try:
            snapshots = []
            with self.neo4j_tool.driver.session() as session:
                # Query for temporal data with timestamps
                query = """
                MATCH (n:Entity)-[r]->(m:Entity)
                WHERE r.timestamp IS NOT NULL
                """
                
                # Add time range filters if provided
                if time_range and "start_time" in time_range and "end_time" in time_range:
                    query += """
                    AND datetime(r.timestamp) >= datetime($start_time)
                    AND datetime(r.timestamp) <= datetime($end_time)
                    """
                
                query += """
                RETURN r.timestamp as timestamp, 
                       n.entity_id as source, m.entity_id as target,
                       r.weight as weight, r.confidence as confidence,
                       n.canonical_name as source_name, m.canonical_name as target_name,
                       n.entity_type as source_type, m.entity_type as target_type
                ORDER BY r.timestamp
                """
                
                params = {}
                if time_range and "start_time" in time_range and "end_time" in time_range:
                    params["start_time"] = time_range["start_time"]
                    params["end_time"] = time_range["end_time"]
                
                result = session.run(query, params)
                
                # Group edges by timestamp
                edges_by_time = defaultdict(list)
                for record in result:
                    timestamp = record["timestamp"]
                    edges_by_time[timestamp].append({
                        "source": record["source"],
                        "target": record["target"],
                        "weight": record["weight"] or 1.0,
                        "confidence": record["confidence"] or 0.8,
                        "source_name": record["source_name"],
                        "target_name": record["target_name"],
                        "source_type": record["source_type"],
                        "target_type": record["target_type"]
                    })
                
                # Create snapshots for each timestamp
                for timestamp in sorted(edges_by_time.keys()):
                    graph = nx.Graph()
                    edges = edges_by_time[timestamp]
                    
                    # Add edges and infer nodes
                    for edge in edges:
                        graph.add_node(edge["source"], 
                                     name=edge["source_name"], 
                                     type=edge["source_type"])
                        graph.add_node(edge["target"], 
                                     name=edge["target_name"], 
                                     type=edge["target_type"])
                        graph.add_edge(edge["source"], edge["target"],
                                     weight=edge["weight"], 
                                     confidence=edge["confidence"])
                    
                    # Calculate metrics for this snapshot
                    metrics = self._calculate_snapshot_metrics(graph)
                    
                    snapshots.append(TemporalSnapshot(
                        timestamp=timestamp,
                        graph=graph,
                        metrics=metrics,
                        metadata={"source": "neo4j_temporal", "edge_count": len(edges)}
                    ))
                
                return snapshots
                
        except Exception as e:
            print(f"Error loading from Neo4j temporal: {e}")
            return []
    
    def _load_from_graph_snapshots(self, temporal_data: Dict) -> List[TemporalSnapshot]:
        """Load temporal data from graph snapshots format"""
        if not temporal_data or "snapshots" not in temporal_data:
            return []
        
        try:
            snapshots = []
            for snapshot_data in temporal_data["snapshots"]:
                timestamp = snapshot_data.get("timestamp")
                graph_data = snapshot_data.get("graph")
                
                if not timestamp or not graph_data:
                    continue
                
                # Create NetworkX graph
                graph = nx.Graph()
                
                # Add nodes
                if "nodes" in graph_data:
                    for node_data in graph_data["nodes"]:
                        if isinstance(node_data, dict):
                            node_id = node_data.get("id")
                            attributes = {k: v for k, v in node_data.items() if k != "id"}
                            graph.add_node(node_id, **attributes)
                        else:
                            graph.add_node(node_data)
                
                # Add edges
                if "edges" in graph_data:
                    for edge_data in graph_data["edges"]:
                        if isinstance(edge_data, dict):
                            source = edge_data.get("source")
                            target = edge_data.get("target")
                            attributes = {k: v for k, v in edge_data.items() 
                                        if k not in ["source", "target"]}
                            graph.add_edge(source, target, **attributes)
                        elif isinstance(edge_data, (list, tuple)) and len(edge_data) >= 2:
                            graph.add_edge(edge_data[0], edge_data[1])
                
                # Calculate metrics
                metrics = self._calculate_snapshot_metrics(graph)
                
                snapshots.append(TemporalSnapshot(
                    timestamp=timestamp,
                    graph=graph,
                    metrics=metrics,
                    metadata={"source": "graph_snapshots"}
                ))
            
            # Sort by timestamp
            snapshots.sort(key=lambda x: x.timestamp)
            return snapshots
            
        except Exception as e:
            print(f"Error loading graph snapshots: {e}")
            return []
    
    def _load_from_edge_sequence(self, temporal_data: Dict) -> List[TemporalSnapshot]:
        """Load temporal data from edge sequence format"""
        if not temporal_data or "edge_sequence" not in temporal_data:
            return []
        
        try:
            edge_sequence = temporal_data["edge_sequence"]
            graph = nx.Graph()
            snapshots = []
            
            # Track unique timestamps
            timestamps = set()
            for edge_event in edge_sequence:
                timestamps.add(edge_event.get("timestamp"))
            
            # Create snapshots for each timestamp
            for timestamp in sorted(timestamps):
                current_graph = graph.copy()
                
                # Apply all changes up to this timestamp
                for edge_event in edge_sequence:
                    if edge_event.get("timestamp") <= timestamp:
                        event_type = edge_event.get("type", "add")
                        source = edge_event.get("source")
                        target = edge_event.get("target")
                        
                        if event_type == "add" and source and target:
                            weight = edge_event.get("weight", 1.0)
                            current_graph.add_edge(source, target, weight=weight)
                        elif event_type == "remove" and source and target:
                            if current_graph.has_edge(source, target):
                                current_graph.remove_edge(source, target)
                
                # Calculate metrics
                metrics = self._calculate_snapshot_metrics(current_graph)
                
                snapshots.append(TemporalSnapshot(
                    timestamp=timestamp,
                    graph=current_graph.copy(),
                    metrics=metrics,
                    metadata={"source": "edge_sequence"}
                ))
            
            return snapshots
            
        except Exception as e:
            print(f"Error loading edge sequence: {e}")
            return []
    
    def _load_from_event_stream(self, temporal_data: Dict) -> List[TemporalSnapshot]:
        """Load temporal data from event stream format"""
        if not temporal_data or "events" not in temporal_data:
            return []
        
        try:
            events = temporal_data["events"]
            graph = nx.Graph()
            snapshots = []
            
            # Group events by timestamp
            events_by_time = defaultdict(list)
            for event in events:
                timestamp = event.get("timestamp")
                events_by_time[timestamp].append(event)
            
            # Create snapshots for each timestamp
            for timestamp in sorted(events_by_time.keys()):
                # Apply events at this timestamp
                for event in events_by_time[timestamp]:
                    event_type = event.get("type")
                    
                    if event_type == "node_add":
                        node_id = event.get("node_id")
                        attributes = event.get("attributes", {})
                        if node_id:
                            graph.add_node(node_id, **attributes)
                    
                    elif event_type == "node_remove":
                        node_id = event.get("node_id")
                        if node_id and graph.has_node(node_id):
                            graph.remove_node(node_id)
                    
                    elif event_type == "edge_add":
                        source = event.get("source")
                        target = event.get("target")
                        attributes = event.get("attributes", {})
                        if source and target:
                            graph.add_edge(source, target, **attributes)
                    
                    elif event_type == "edge_remove":
                        source = event.get("source")
                        target = event.get("target")
                        if source and target and graph.has_edge(source, target):
                            graph.remove_edge(source, target)
                
                # Calculate metrics
                metrics = self._calculate_snapshot_metrics(graph)
                
                snapshots.append(TemporalSnapshot(
                    timestamp=timestamp,
                    graph=graph.copy(),
                    metrics=metrics,
                    metadata={"source": "event_stream", "events_count": len(events_by_time[timestamp])}
                ))
            
            return snapshots
            
        except Exception as e:
            print(f"Error loading event stream: {e}")
            return []
    
    def _calculate_snapshot_metrics(self, graph: nx.Graph) -> Dict[str, Any]:
        """Calculate metrics for a graph snapshot"""
        try:
            metrics = {}
            
            # Basic metrics
            metrics["node_count"] = len(graph.nodes())
            metrics["edge_count"] = len(graph.edges())
            
            if len(graph.nodes()) > 0:
                metrics["density"] = nx.density(graph)
                
                if len(graph.nodes()) > 1:
                    metrics["average_degree"] = sum(dict(graph.degree()).values()) / len(graph.nodes())
                else:
                    metrics["average_degree"] = 0.0
                
                # Clustering coefficient
                try:
                    metrics["average_clustering"] = nx.average_clustering(graph)
                except:
                    metrics["average_clustering"] = 0.0
                
                # Transitivity
                try:
                    metrics["transitivity"] = nx.transitivity(graph)
                except:
                    metrics["transitivity"] = 0.0
                
                # Connected components
                metrics["connected_components"] = nx.number_connected_components(graph)
                
                # Diameter and radius (for connected graphs)
                if nx.is_connected(graph) and len(graph.nodes()) > 1:
                    try:
                        metrics["diameter"] = nx.diameter(graph)
                        metrics["radius"] = nx.radius(graph)
                    except:
                        metrics["diameter"] = 0
                        metrics["radius"] = 0
                else:
                    metrics["diameter"] = 0
                    metrics["radius"] = 0
            else:
                # Empty graph
                metrics["density"] = 0.0
                metrics["average_degree"] = 0.0
                metrics["average_clustering"] = 0.0
                metrics["transitivity"] = 0.0
                metrics["connected_components"] = 0
                metrics["diameter"] = 0
                metrics["radius"] = 0
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating snapshot metrics: {e}")
            return {"node_count": 0, "edge_count": 0, "density": 0.0}
    
    def _perform_temporal_analysis(self, snapshots: List[TemporalSnapshot], 
                                 analysis_type: TemporalAnalysisType,
                                 metrics_to_track: List[str],
                                 change_detection_params: Dict[str, Any],
                                 trend_analysis_params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform specific temporal analysis"""
        try:
            if analysis_type == TemporalAnalysisType.EVOLUTION:
                return self._analyze_evolution(snapshots, metrics_to_track)
            elif analysis_type == TemporalAnalysisType.CHANGE_DETECTION:
                return self._detect_changes(snapshots, change_detection_params)
            elif analysis_type == TemporalAnalysisType.TREND_ANALYSIS:
                return self._analyze_trends(snapshots, metrics_to_track, trend_analysis_params)
            elif analysis_type == TemporalAnalysisType.SNAPSHOT_COMPARISON:
                return self._compare_snapshots(snapshots, metrics_to_track)
            elif analysis_type == TemporalAnalysisType.DYNAMIC_CENTRALITY:
                return self._analyze_dynamic_centrality(snapshots)
            elif analysis_type == TemporalAnalysisType.TEMPORAL_PATHS:
                return self._analyze_temporal_paths(snapshots)
            elif analysis_type == TemporalAnalysisType.COMMUNITY_EVOLUTION:
                return self._analyze_community_evolution(snapshots)
            else:
                return {}
                
        except Exception as e:
            print(f"Error performing temporal analysis {analysis_type}: {e}")
            return {}
    
    def _analyze_evolution(self, snapshots: List[TemporalSnapshot], 
                         metrics_to_track: List[str]) -> Dict[str, Any]:
        """Analyze temporal evolution of graph metrics"""
        evolution_data = {}
        
        # Extract metric values over time
        for metric in metrics_to_track:
            values = []
            timestamps = []
            
            for snapshot in snapshots:
                if metric in snapshot.metrics:
                    values.append(snapshot.metrics[metric])
                    timestamps.append(snapshot.timestamp)
            
            if values:
                evolution_data[metric] = {
                    "values": values,
                    "timestamps": timestamps,
                    "min": min(values),
                    "max": max(values),
                    "mean": np.mean(values),
                    "std": np.std(values) if len(values) > 1 else 0.0,
                    "growth_rate": (values[-1] - values[0]) / values[0] if values[0] != 0 else 0.0
                }
        
        return {"evolution": evolution_data}
    
    def _detect_changes(self, snapshots: List[TemporalSnapshot], 
                       params: Dict[str, Any]) -> Dict[str, Any]:
        """Detect significant changes between consecutive snapshots"""
        changes = []
        sensitivity = params.get("sensitivity", 0.1)
        min_magnitude = params.get("min_change_magnitude", 0.05)
        
        for i in range(1, len(snapshots)):
            prev_snapshot = snapshots[i-1]
            curr_snapshot = snapshots[i]
            
            # Detect node changes
            prev_nodes = set(prev_snapshot.graph.nodes())
            curr_nodes = set(curr_snapshot.graph.nodes())
            
            added_nodes = curr_nodes - prev_nodes
            removed_nodes = prev_nodes - curr_nodes
            
            if added_nodes:
                changes.append(ChangeEvent(
                    timestamp=curr_snapshot.timestamp,
                    change_type=ChangeType.NODE_ADDITION,
                    affected_elements=list(added_nodes),
                    magnitude=len(added_nodes) / max(len(prev_nodes), 1),
                    details={"added_nodes": list(added_nodes)}
                ))
            
            if removed_nodes:
                changes.append(ChangeEvent(
                    timestamp=curr_snapshot.timestamp,
                    change_type=ChangeType.NODE_REMOVAL,
                    affected_elements=list(removed_nodes),
                    magnitude=len(removed_nodes) / max(len(prev_nodes), 1),
                    details={"removed_nodes": list(removed_nodes)}
                ))
            
            # Detect edge changes
            prev_edges = set(prev_snapshot.graph.edges())
            curr_edges = set(curr_snapshot.graph.edges())
            
            added_edges = curr_edges - prev_edges
            removed_edges = prev_edges - curr_edges
            
            if added_edges:
                changes.append(ChangeEvent(
                    timestamp=curr_snapshot.timestamp,
                    change_type=ChangeType.EDGE_ADDITION,
                    affected_elements=[f"{u}-{v}" for u, v in added_edges],
                    magnitude=len(added_edges) / max(len(prev_edges), 1),
                    details={"added_edges": list(added_edges)}
                ))
            
            if removed_edges:
                changes.append(ChangeEvent(
                    timestamp=curr_snapshot.timestamp,
                    change_type=ChangeType.EDGE_REMOVAL,
                    affected_elements=[f"{u}-{v}" for u, v in removed_edges],
                    magnitude=len(removed_edges) / max(len(prev_edges), 1),
                    details={"removed_edges": list(removed_edges)}
                ))
            
            # Detect metric changes
            for metric in prev_snapshot.metrics:
                if metric in curr_snapshot.metrics:
                    prev_value = prev_snapshot.metrics[metric]
                    curr_value = curr_snapshot.metrics[metric]
                    
                    if prev_value != 0:
                        relative_change = abs(curr_value - prev_value) / abs(prev_value)
                        if relative_change > min_magnitude:
                            changes.append(ChangeEvent(
                                timestamp=curr_snapshot.timestamp,
                                change_type=ChangeType.ATTRIBUTE_CHANGE,
                                affected_elements=[metric],
                                magnitude=relative_change,
                                details={
                                    "metric": metric,
                                    "previous_value": prev_value,
                                    "current_value": curr_value,
                                    "relative_change": relative_change
                                }
                            ))
        
        # Filter changes by magnitude threshold
        significant_changes = [c for c in changes if c.magnitude >= min_magnitude]
        
        return {"changes": significant_changes}
    
    def _analyze_trends(self, snapshots: List[TemporalSnapshot], 
                       metrics_to_track: List[str],
                       params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends in temporal metrics"""
        trends = []
        trend_window = params.get("trend_window", 5)
        
        for metric in metrics_to_track:
            values = []
            timestamps = []
            
            for snapshot in snapshots:
                if metric in snapshot.metrics:
                    values.append(snapshot.metrics[metric])
                    timestamps.append(snapshot.timestamp)
            
            if len(values) >= 3:  # Minimum for trend analysis
                # Calculate trend direction
                if len(values) >= trend_window:
                    # Use recent window for trend
                    recent_values = values[-trend_window:]
                    slope = np.polyfit(range(len(recent_values)), recent_values, 1)[0]
                else:
                    # Use all values
                    slope = np.polyfit(range(len(values)), values, 1)[0]
                
                # Determine trend direction
                if abs(slope) < 0.01 * np.mean(values):
                    direction = "stable"
                elif slope > 0:
                    direction = "increasing"
                else:
                    direction = "decreasing"
                
                # Calculate trend strength
                if len(values) > 1:
                    trend_strength = abs(slope) / np.std(values) if np.std(values) > 0 else 0
                else:
                    trend_strength = 0
                
                # Detect change points (simplified)
                change_points = []
                if len(values) > 4:
                    for i in range(2, len(values) - 2):
                        # Look for significant changes in slope
                        before_slope = np.polyfit(range(i), values[:i], 1)[0]
                        after_slope = np.polyfit(range(len(values) - i), values[i:], 1)[0]
                        
                        if abs(after_slope - before_slope) > 0.1 * abs(before_slope):
                            change_points.append(timestamps[i])
                
                trends.append(TemporalTrend(
                    metric_name=metric,
                    values=values,
                    timestamps=timestamps,
                    trend_direction=direction,
                    trend_strength=trend_strength,
                    change_points=change_points
                ))
        
        return {"trends": trends}
    
    def _compare_snapshots(self, snapshots: List[TemporalSnapshot], 
                          metrics_to_track: List[str]) -> Dict[str, Any]:
        """Compare snapshots statistically"""
        comparisons = {}
        
        # Compare consecutive snapshots
        for i in range(1, len(snapshots)):
            prev_snapshot = snapshots[i-1]
            curr_snapshot = snapshots[i]
            
            comparison = {
                "timestamp_pair": (prev_snapshot.timestamp, curr_snapshot.timestamp),
                "metric_changes": {}
            }
            
            for metric in metrics_to_track:
                if metric in prev_snapshot.metrics and metric in curr_snapshot.metrics:
                    prev_val = prev_snapshot.metrics[metric]
                    curr_val = curr_snapshot.metrics[metric]
                    
                    comparison["metric_changes"][metric] = {
                        "previous": prev_val,
                        "current": curr_val,
                        "absolute_change": curr_val - prev_val,
                        "relative_change": (curr_val - prev_val) / prev_val if prev_val != 0 else 0,
                        "percentage_change": ((curr_val - prev_val) / prev_val * 100) if prev_val != 0 else 0
                    }
            
            comparisons[f"comparison_{i}"] = comparison
        
        return {"comparisons": comparisons}
    
    def _analyze_dynamic_centrality(self, snapshots: List[TemporalSnapshot]) -> Dict[str, Any]:
        """Analyze how centrality measures change over time"""
        centrality_evolution = {}
        
        # Track centrality for all nodes across time
        all_nodes = set()
        for snapshot in snapshots:
            all_nodes.update(snapshot.graph.nodes())
        
        for node in all_nodes:
            node_centrality = {
                "timestamps": [],
                "degree": [],
                "betweenness": [],
                "closeness": []
            }
            
            for snapshot in snapshots:
                if node in snapshot.graph.nodes():
                    node_centrality["timestamps"].append(snapshot.timestamp)
                    
                    # Degree centrality
                    degree_cent = snapshot.graph.degree(node) / max(len(snapshot.graph.nodes()) - 1, 1)
                    node_centrality["degree"].append(degree_cent)
                    
                    # Betweenness centrality (simplified calculation for performance)
                    try:
                        if len(snapshot.graph.nodes()) > 2:
                            betweenness = nx.betweenness_centrality(snapshot.graph)
                            node_centrality["betweenness"].append(betweenness.get(node, 0))
                        else:
                            node_centrality["betweenness"].append(0)
                    except:
                        node_centrality["betweenness"].append(0)
                    
                    # Closeness centrality
                    try:
                        if len(snapshot.graph.nodes()) > 1 and nx.is_connected(snapshot.graph):
                            closeness = nx.closeness_centrality(snapshot.graph)
                            node_centrality["closeness"].append(closeness.get(node, 0))
                        else:
                            node_centrality["closeness"].append(0)
                    except:
                        node_centrality["closeness"].append(0)
            
            if node_centrality["timestamps"]:
                centrality_evolution[node] = node_centrality
        
        return {"dynamic_centrality": centrality_evolution}
    
    def _analyze_temporal_paths(self, snapshots: List[TemporalSnapshot]) -> Dict[str, Any]:
        """Analyze temporal paths through the network"""
        # Simplified temporal path analysis
        path_analysis = {
            "connectivity_evolution": [],
            "path_length_evolution": []
        }
        
        for snapshot in snapshots:
            graph = snapshot.graph
            
            if len(graph.nodes()) > 1:
                # Average path length for connected components
                if nx.is_connected(graph):
                    avg_path_length = nx.average_shortest_path_length(graph)
                else:
                    # Calculate for largest connected component
                    largest_cc = max(nx.connected_components(graph), key=len)
                    subgraph = graph.subgraph(largest_cc)
                    if len(subgraph.nodes()) > 1:
                        avg_path_length = nx.average_shortest_path_length(subgraph)
                    else:
                        avg_path_length = 0
                
                path_analysis["connectivity_evolution"].append({
                    "timestamp": snapshot.timestamp,
                    "connectivity": nx.is_connected(graph),
                    "largest_component_size": len(max(nx.connected_components(graph), key=len))
                })
                
                path_analysis["path_length_evolution"].append({
                    "timestamp": snapshot.timestamp,
                    "average_path_length": avg_path_length
                })
        
        return {"temporal_paths": path_analysis}
    
    def _analyze_community_evolution(self, snapshots: List[TemporalSnapshot]) -> Dict[str, Any]:
        """Analyze how communities evolve over time"""
        community_evolution = {
            "community_counts": [],
            "stability_metrics": []
        }
        
        prev_communities = None
        
        for snapshot in snapshots:
            graph = snapshot.graph
            
            try:
                # Simple community detection using connected components as fallback
                if len(graph.edges()) > 0:
                    # Try Louvain if available, otherwise use connected components
                    try:
                        import networkx.algorithms.community as nx_community
                        communities = list(nx_community.louvain_communities(graph))
                    except:
                        communities = list(nx.connected_components(graph))
                else:
                    communities = [{node} for node in graph.nodes()]
                
                community_counts = {
                    "timestamp": snapshot.timestamp,
                    "num_communities": len(communities),
                    "largest_community": len(max(communities, key=len)) if communities else 0,
                    "smallest_community": len(min(communities, key=len)) if communities else 0
                }
                community_evolution["community_counts"].append(community_counts)
                
                # Calculate stability if we have previous communities
                if prev_communities is not None:
                    stability = self._calculate_community_stability(prev_communities, communities)
                    community_evolution["stability_metrics"].append({
                        "timestamp": snapshot.timestamp,
                        "stability": stability
                    })
                
                prev_communities = communities
                
            except Exception as e:
                print(f"Error in community analysis for timestamp {snapshot.timestamp}: {e}")
        
        return {"community_evolution": community_evolution}
    
    def _calculate_community_stability(self, prev_communities: List[set], 
                                     curr_communities: List[set]) -> float:
        """Calculate stability between community structures"""
        try:
            # Simplified stability metric based on Jaccard similarity
            max_similarities = []
            
            for curr_comm in curr_communities:
                best_similarity = 0
                for prev_comm in prev_communities:
                    intersection = len(curr_comm.intersection(prev_comm))
                    union = len(curr_comm.union(prev_comm))
                    similarity = intersection / union if union > 0 else 0
                    best_similarity = max(best_similarity, similarity)
                max_similarities.append(best_similarity)
            
            return np.mean(max_similarities) if max_similarities else 0.0
            
        except Exception as e:
            print(f"Error calculating community stability: {e}")
            return 0.0
    
    def _extract_temporal_evolution(self, analysis_results: Dict[str, Any],
                                  snapshots: List[TemporalSnapshot]) -> Dict[str, Any]:
        """Extract temporal evolution data from analysis results"""
        evolution_data = {}
        
        # Get evolution analysis if available
        for analysis_type, results in analysis_results.items():
            if "evolution" in results:
                evolution_data.update(results["evolution"])
        
        # Add snapshot summary
        evolution_data["snapshots_summary"] = [
            {
                "timestamp": snapshot.timestamp,
                "node_count": snapshot.metrics.get("node_count", 0),
                "edge_count": snapshot.metrics.get("edge_count", 0),
                "density": snapshot.metrics.get("density", 0.0)
            }
            for snapshot in snapshots
        ]
        
        return evolution_data
    
    def _extract_change_events(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract change events from analysis results"""
        all_changes = []
        
        for analysis_type, results in analysis_results.items():
            if "changes" in results:
                for change in results["changes"]:
                    all_changes.append({
                        "timestamp": change.timestamp,
                        "change_type": change.change_type.value,
                        "affected_elements": change.affected_elements,
                        "magnitude": change.magnitude,
                        "details": change.details
                    })
        
        # Sort by timestamp
        all_changes.sort(key=lambda x: x["timestamp"])
        return all_changes
    
    def _extract_temporal_trends(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract temporal trends from analysis results"""
        all_trends = []
        
        for analysis_type, results in analysis_results.items():
            if "trends" in results:
                for trend in results["trends"]:
                    all_trends.append({
                        "metric_name": trend.metric_name,
                        "values": trend.values,
                        "timestamps": trend.timestamps,
                        "trend_direction": trend.trend_direction,
                        "trend_strength": trend.trend_strength,
                        "change_points": trend.change_points
                    })
        
        return all_trends
    
    def _calculate_analysis_summary(self, snapshots: List[TemporalSnapshot],
                                  analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall analysis summary"""
        if not snapshots:
            return {}
        
        # Time span
        start_time = snapshots[0].timestamp
        end_time = snapshots[-1].timestamp
        
        # Count major changes
        total_changes = 0
        for analysis_type, results in analysis_results.items():
            if "changes" in results:
                total_changes += len(results["changes"])
        
        # Calculate stability index (simplified)
        node_count_values = [s.metrics.get("node_count", 0) for s in snapshots]
        edge_count_values = [s.metrics.get("edge_count", 0) for s in snapshots]
        
        node_stability = 1.0 - (np.std(node_count_values) / np.mean(node_count_values)) if np.mean(node_count_values) > 0 else 0
        edge_stability = 1.0 - (np.std(edge_count_values) / np.mean(edge_count_values)) if np.mean(edge_count_values) > 0 else 0
        stability_index = (node_stability + edge_stability) / 2
        
        # Calculate growth rate
        if len(snapshots) > 1:
            initial_nodes = snapshots[0].metrics.get("node_count", 0)
            final_nodes = snapshots[-1].metrics.get("node_count", 0)
            growth_rate = (final_nodes - initial_nodes) / initial_nodes if initial_nodes > 0 else 0
        else:
            growth_rate = 0
        
        return {
            "time_span": f"{start_time} to {end_time}",
            "total_snapshots": len(snapshots),
            "major_changes": total_changes,
            "stability_index": max(0.0, min(1.0, stability_index)),
            "growth_rate": growth_rate
        }
    
    def _store_temporal_results(self, analysis_results: Dict[str, Any],
                              snapshots: List[TemporalSnapshot]) -> Dict[str, Any]:
        """Store temporal analysis results to Neo4j"""
        if not self.neo4j_tool or not self.neo4j_tool.driver:
            return {"status": "failed", "reason": "Neo4j not available"}
        
        try:
            with self.neo4j_tool.driver.session() as session:
                stored_count = 0
                
                # Store temporal snapshots metadata
                for snapshot in snapshots:
                    session.run("""
                    CREATE (ts:TemporalSnapshot {
                        timestamp: $timestamp,
                        node_count: $node_count,
                        edge_count: $edge_count,
                        density: $density,
                        created_at: $created_at
                    })
                    """, {
                        "timestamp": snapshot.timestamp,
                        "node_count": snapshot.metrics.get("node_count", 0),
                        "edge_count": snapshot.metrics.get("edge_count", 0),
                        "density": snapshot.metrics.get("density", 0.0),
                        "created_at": datetime.now().isoformat()
                    })
                    stored_count += 1
                
                return {
                    "status": "success",
                    "snapshots_stored": stored_count,
                    "analysis_types": list(analysis_results.keys())
                }
                
        except Exception as e:
            return {"status": "failed", "reason": str(e)}
    
    def _calculate_academic_confidence(self, analysis_summary: Dict[str, Any],
                                     snapshots: List[TemporalSnapshot]) -> float:
        """Calculate academic-quality confidence for temporal analysis"""
        try:
            # Base confidence from temporal data quantity
            snapshot_count = len(snapshots)
            quantity_factor = min(1.0, snapshot_count / 10.0)  # Normalize to 10 snapshots
            
            # Stability factor
            stability_index = analysis_summary.get("stability_index", 0.5)
            stability_factor = 0.5 + 0.5 * stability_index  # Convert to confidence factor
            
            # Time span factor (more time points generally better)
            time_span_factor = min(1.0, snapshot_count / 20.0)  # Up to 20 snapshots
            
            # Data quality factor
            avg_node_count = np.mean([s.metrics.get("node_count", 0) for s in snapshots])
            quality_factor = min(1.0, avg_node_count / 50.0)  # Normalize to 50 nodes
            
            # Combine factors
            combined_confidence = (
                quantity_factor * 0.3 +
                stability_factor * 0.3 +
                time_span_factor * 0.2 +
                quality_factor * 0.2
            )
            
            return max(0.1, min(1.0, combined_confidence))
            
        except Exception as e:
            print(f"Error calculating academic confidence: {e}")
            return 0.5
    
    def _format_output(self, temporal_evolution: Dict[str, Any], change_events: List[Dict[str, Any]],
                      temporal_trends: List[Dict[str, Any]], analysis_summary: Dict[str, Any],
                      output_format: str) -> Dict[str, Any]:
        """Format output based on requested format"""
        base_data = {
            "temporal_evolution": temporal_evolution,
            "change_events": change_events,
            "temporal_trends": temporal_trends,
            "analysis_summary": analysis_summary
        }
        
        if output_format == "summary":
            # Simplified summary
            base_data["temporal_evolution"] = {
                "snapshots_summary": temporal_evolution.get("snapshots_summary", [])
            }
            base_data["change_events"] = change_events[:10]  # Limit to top 10 changes
        
        elif output_format == "time_series":
            # Focus on time series data
            base_data = {
                "temporal_evolution": temporal_evolution,
                "temporal_trends": temporal_trends,
                "analysis_summary": analysis_summary
            }
        
        elif output_format == "changes_only":
            # Focus on changes
            base_data = {
                "change_events": change_events,
                "analysis_summary": analysis_summary
            }
        
        # detailed format returns everything
        return base_data
    
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
        elif "temporal" in error_message.lower():
            error_code = "TEMPORAL_ANALYSIS_FAILED"
        elif "change" in error_message.lower():
            error_code = "CHANGE_DETECTION_FAILED"
        elif "time" in error_message.lower():
            error_code = "TIME_RANGE_INVALID"
        elif "neo4j" in error_message.lower():
            error_code = "NEO4J_CONNECTION_ERROR"
        elif "analysis" in error_message.lower():
            error_code = "ANALYSIS_TYPE_NOT_SUPPORTED"
        
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
    tool = TemporalAnalysisTool()
    contract = tool.get_contract()
    print(f"Tool {tool.tool_id} initialized successfully")
    print(f"Contract: {contract.name}")
    print(f"Supported analysis types: {[at.value for at in TemporalAnalysisType]}")