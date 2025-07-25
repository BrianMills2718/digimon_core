"""Temporal Data Loader

Load temporal graph data from various sources including Neo4j, 
graph snapshots, edge sequences, and event streams.
"""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import networkx as nx
import json
from collections import defaultdict

from .temporal_data_models import TemporalSnapshot
from src.tools.phase1.base_neo4j_tool import BaseNeo4jTool
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class TemporalDataLoader(BaseNeo4jTool):
    """Load temporal graph data from various sources"""
    
    def __init__(self, service_manager=None):
        super().__init__(service_manager)
        self.tool_id = "TEMPORAL_DATA_LOADER"
    
    def load_temporal_data(self, data_source: str, temporal_data: Optional[Dict] = None,
                          time_range: Optional[Dict[str, Any]] = None) -> List[TemporalSnapshot]:
        """Load temporal data from specified source
        
        Args:
            data_source: Source type ("neo4j", "snapshots", "edges", "events")
            temporal_data: Data for non-Neo4j sources
            time_range: Time range for Neo4j queries
            
        Returns:
            List of temporal snapshots
        """
        try:
            if data_source == "neo4j":
                return self._load_from_neo4j_temporal(time_range)
            elif data_source == "snapshots":
                return self._load_from_graph_snapshots(temporal_data)
            elif data_source == "edges":
                return self._load_from_edge_sequence(temporal_data)
            elif data_source == "events":
                return self._load_from_event_stream(temporal_data)
            else:
                raise ValueError(f"Unsupported data source: {data_source}")
                
        except Exception as e:
            logger.error(f"Failed to load temporal data from {data_source}: {e}")
            raise
    
    def _load_from_neo4j_temporal(self, time_range: Dict[str, Any] = None) -> List[TemporalSnapshot]:
        """Load temporal snapshots from Neo4j with time-based queries"""
        snapshots = []
        
        try:
            # Determine time range
            if time_range:
                start_time = time_range.get("start", "2020-01-01")
                end_time = time_range.get("end", datetime.now().strftime("%Y-%m-%d"))
                interval = time_range.get("interval", "1d")
            else:
                # Default: last 30 days, daily snapshots
                end_time = datetime.now().strftime("%Y-%m-%d")
                start_time = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
                interval = "1d"
            
            # Generate time points
            time_points = self._generate_time_points(start_time, end_time, interval)
            
            for timestamp in time_points:
                # Query Neo4j for entities and relationships at this time
                entities_query = f"""
                MATCH (e:Entity)
                WHERE e.created_at <= datetime('{timestamp}T23:59:59') 
                AND (e.updated_at IS NULL OR e.updated_at <= datetime('{timestamp}T23:59:59'))
                RETURN e
                """
                
                relationships_query = f"""
                MATCH (e1:Entity)-[r:RELATIONSHIP]->(e2:Entity)
                WHERE r.created_at <= datetime('{timestamp}T23:59:59')
                AND (r.updated_at IS NULL OR r.updated_at <= datetime('{timestamp}T23:59:59'))
                RETURN e1, r, e2
                """
                
                # Execute queries
                entities = self.neo4j_manager.execute_query(entities_query)
                relationships = self.neo4j_manager.execute_query(relationships_query)
                
                # Build NetworkX graph
                graph = nx.Graph()
                
                # Add nodes
                for entity in entities:
                    entity_data = dict(entity['e'])
                    node_id = entity_data.get('entity_id', entity_data.get('name'))
                    graph.add_node(node_id, **entity_data)
                
                # Add edges
                for rel in relationships:
                    source = dict(rel['e1'])
                    target = dict(rel['e2'])
                    edge_data = dict(rel['r'])
                    
                    source_id = source.get('entity_id', source.get('name'))
                    target_id = target.get('entity_id', target.get('name'))
                    
                    graph.add_edge(source_id, target_id, **edge_data)
                
                # Calculate basic metrics
                metrics = self._calculate_snapshot_metrics(graph)
                
                # Create snapshot
                snapshot = TemporalSnapshot(
                    timestamp=timestamp,
                    graph=graph,
                    metrics=metrics,
                    metadata={
                        "source": "neo4j",
                        "query_time": datetime.now().isoformat(),
                        "entities_count": len(entities),
                        "relationships_count": len(relationships)
                    }
                )
                
                snapshots.append(snapshot)
                logger.info(f"Loaded snapshot for {timestamp}: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            
            return snapshots
            
        except Exception as e:
            logger.error(f"Failed to load temporal data from Neo4j: {e}")
            raise
    
    def _load_from_graph_snapshots(self, temporal_data: Dict) -> List[TemporalSnapshot]:
        """Load from pre-computed graph snapshots"""
        snapshots = []
        
        try:
            snapshot_data = temporal_data.get("snapshots", [])
            
            for snapshot_info in snapshot_data:
                timestamp = snapshot_info["timestamp"]
                graph_data = snapshot_info["graph"]
                
                # Create NetworkX graph
                graph = nx.Graph()
                
                # Add nodes
                for node_info in graph_data.get("nodes", []):
                    graph.add_node(node_info["id"], **node_info.get("attributes", {}))
                
                # Add edges
                for edge_info in graph_data.get("edges", []):
                    graph.add_edge(
                        edge_info["source"],
                        edge_info["target"],
                        **edge_info.get("attributes", {})
                    )
                
                # Calculate metrics
                metrics = self._calculate_snapshot_metrics(graph)
                
                snapshot = TemporalSnapshot(
                    timestamp=timestamp,
                    graph=graph,
                    metrics=metrics,
                    metadata={
                        "source": "snapshots",
                        "original_data": snapshot_info
                    }
                )
                
                snapshots.append(snapshot)
            
            return snapshots
            
        except Exception as e:
            logger.error(f"Failed to load from graph snapshots: {e}")
            raise
    
    def _load_from_edge_sequence(self, temporal_data: Dict) -> List[TemporalSnapshot]:
        """Load from sequence of edge additions/removals"""
        snapshots = []
        
        try:
            edge_sequence = temporal_data.get("edge_sequence", [])
            nodes = temporal_data.get("nodes", [])
            time_points = temporal_data.get("time_points", [])
            
            # Create base graph with nodes
            base_graph = nx.Graph()
            for node_info in nodes:
                base_graph.add_node(node_info["id"], **node_info.get("attributes", {}))
            
            # Build snapshots by applying edge changes
            current_graph = base_graph.copy()
            edge_index = 0
            
            for timestamp in time_points:
                # Apply edge changes up to this timestamp
                while edge_index < len(edge_sequence):
                    edge_event = edge_sequence[edge_index]
                    if edge_event["timestamp"] > timestamp:
                        break
                    
                    if edge_event["action"] == "add":
                        current_graph.add_edge(
                            edge_event["source"],
                            edge_event["target"],
                            **edge_event.get("attributes", {})
                        )
                    elif edge_event["action"] == "remove":
                        if current_graph.has_edge(edge_event["source"], edge_event["target"]):
                            current_graph.remove_edge(edge_event["source"], edge_event["target"])
                    
                    edge_index += 1
                
                # Calculate metrics
                metrics = self._calculate_snapshot_metrics(current_graph)
                
                snapshot = TemporalSnapshot(
                    timestamp=timestamp,
                    graph=current_graph.copy(),
                    metrics=metrics,
                    metadata={
                        "source": "edge_sequence",
                        "edges_applied": edge_index
                    }
                )
                
                snapshots.append(snapshot)
            
            return snapshots
            
        except Exception as e:
            logger.error(f"Failed to load from edge sequence: {e}")
            raise
    
    def _load_from_event_stream(self, temporal_data: Dict) -> List[TemporalSnapshot]:
        """Load from stream of graph events"""
        snapshots = []
        
        try:
            events = temporal_data.get("events", [])
            time_points = temporal_data.get("time_points", [])
            
            # Build snapshots by applying events
            current_graph = nx.Graph()
            event_index = 0
            
            for timestamp in time_points:
                # Apply events up to this timestamp
                while event_index < len(events):
                    event = events[event_index]
                    if event["timestamp"] > timestamp:
                        break
                    
                    self._apply_event_to_graph(current_graph, event)
                    event_index += 1
                
                # Calculate metrics
                metrics = self._calculate_snapshot_metrics(current_graph)
                
                snapshot = TemporalSnapshot(
                    timestamp=timestamp,
                    graph=current_graph.copy(),
                    metrics=metrics,
                    metadata={
                        "source": "event_stream",
                        "events_applied": event_index
                    }
                )
                
                snapshots.append(snapshot)
            
            return snapshots
            
        except Exception as e:
            logger.error(f"Failed to load from event stream: {e}")
            raise
    
    def _apply_event_to_graph(self, graph: nx.Graph, event: Dict[str, Any]):
        """Apply a single event to the graph"""
        event_type = event.get("type")
        
        if event_type == "node_add":
            graph.add_node(event["node_id"], **event.get("attributes", {}))
        elif event_type == "node_remove":
            if graph.has_node(event["node_id"]):
                graph.remove_node(event["node_id"])
        elif event_type == "edge_add":
            graph.add_edge(
                event["source"],
                event["target"],
                **event.get("attributes", {})
            )
        elif event_type == "edge_remove":
            if graph.has_edge(event["source"], event["target"]):
                graph.remove_edge(event["source"], event["target"])
        elif event_type == "attribute_update":
            if event.get("element_type") == "node" and graph.has_node(event["element_id"]):
                graph.nodes[event["element_id"]].update(event.get("attributes", {}))
            elif event.get("element_type") == "edge":
                source, target = event["element_id"].split("-")
                if graph.has_edge(source, target):
                    graph.edges[source, target].update(event.get("attributes", {}))
    
    def _calculate_snapshot_metrics(self, graph: nx.Graph) -> Dict[str, Any]:
        """Calculate basic metrics for a graph snapshot"""
        if len(graph.nodes) == 0:
            return {
                "node_count": 0,
                "edge_count": 0,
                "density": 0.0,
                "avg_degree": 0.0,
                "connected_components": 0
            }
        
        metrics = {
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "density": nx.density(graph),
            "avg_degree": sum(dict(graph.degree()).values()) / len(graph.nodes),
            "connected_components": nx.number_connected_components(graph)
        }
        
        # Add centrality measures if graph is not too large
        if len(graph.nodes) <= 1000:
            try:
                centrality = nx.degree_centrality(graph)
                metrics["max_degree_centrality"] = max(centrality.values()) if centrality else 0
                metrics["avg_degree_centrality"] = sum(centrality.values()) / len(centrality) if centrality else 0
            except:
                pass
        
        return metrics
    
    def _generate_time_points(self, start_time: str, end_time: str, interval: str) -> List[str]:
        """Generate time points for temporal analysis"""
        time_points = []
        
        start_dt = datetime.strptime(start_time, "%Y-%m-%d")
        end_dt = datetime.strptime(end_time, "%Y-%m-%d")
        
        # Parse interval
        if interval.endswith("d"):
            delta = timedelta(days=int(interval[:-1]))
        elif interval.endswith("h"):
            delta = timedelta(hours=int(interval[:-1]))
        elif interval.endswith("w"):
            delta = timedelta(weeks=int(interval[:-1]))
        else:
            delta = timedelta(days=1)  # Default to daily
        
        current_dt = start_dt
        while current_dt <= end_dt:
            time_points.append(current_dt.strftime("%Y-%m-%d"))
            current_dt += delta
        
        return time_points